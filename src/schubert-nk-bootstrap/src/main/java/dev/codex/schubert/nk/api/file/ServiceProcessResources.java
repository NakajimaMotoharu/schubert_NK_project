package dev.codex.schubert.nk.api.file;

import com.zaxxer.hikari.HikariDataSource;
import dev.codex.schubert.nk.api.bootstrap.ServiceDatabaseSource;
import dev.codex.schubert.nk.storage.DirectoryCalls;
import dev.codex.schubert.nk.storage.InodeSecurityCalls;
import dev.codex.schubert.nk.storage.LinuxDirectoryCalls;
import dev.codex.schubert.nk.storage.LinuxInodeSecurity;
import dev.codex.schubert.nk.storage.OwnedTransferDirectory;
import dev.codex.schubert.nk.storage.ResourceScope;
import dev.codex.schubert.nk.storage.ServiceConfigFiles;
import dev.codex.schubert.nk.storage.ServiceCredentialId;
import dev.codex.schubert.nk.storage.ServiceCredentialLocation;
import dev.codex.schubert.nk.storage.StorageIoException;
import java.io.Closeable;
import java.io.IOException;
import java.util.Arrays;
import java.util.Objects;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.locks.LockSupport;
import java.util.function.Consumer;
import javax.sql.DataSource;
import org.jspecify.annotations.NullMarked;

/**
 * Operation-owned Web/API credential root/material/source/pool, not full process readiness. All
 * dependencies passed to the operation are borrowed only until it returns. Startup/DB/JMS/root
 * admission must still precede receive groups; no fixture/management credential is selected here.
 * NK-OPS-001; SYS-002/004,DAT-001; UI212/243/253; SS311/342/343/SSC081/082/084;
 * PG288/290/PT-OPS-API-RES-001..006,PT-OPS-WEB-RES-001; 471 D01/02/05.
 */
@NullMarked
public final class ServiceProcessResources {
  private static final long OBSERVATION_MILLIS = 1000;
  private static final long OBSERVATION_NANOS = TimeUnit.MILLISECONDS.toNanos(OBSERVATION_MILLIS);
  private static final Runnable UNKNOWN_OBSERVATION = ServiceProcessResources::observeUnconfirmed;
  private static final Runnable UNKNOWN_FALLBACK = ServiceProcessResources::waitUnknownInterval;

  static {
    // Resolve this standard wait implementation before any native resource acquisition.
    LockSupport.parkNanos(0);
  }

  public record Inputs(
      ServiceConfigFiles.Service service,
      ServiceCredentialLocation credentials,
      String databaseUrl) {
    public Inputs {
      Objects.requireNonNull(service, "service");
      Objects.requireNonNull(credentials, "credential location");
      Objects.requireNonNull(databaseUrl, "database URL");
    }
  }

  private final Inputs inputs;
  private final DirectoryCalls directories;
  private final InodeSecurityCalls security;
  private final InspectorCredentialLoader.Io io;
  private final SourceFactory sources;
  private final PoolFactory pools;

  @FunctionalInterface
  interface SourceFactory {
    ServiceDatabaseSource open(String url, char[] ownedPassword);
  }

  @FunctionalInterface
  public interface PoolFactory {
    HikariDataSource open(DataSource source);
  }

  @FunctionalInterface
  public interface Operation {
    void run(DataSource pool, ServiceCredentialSet credentials) throws IOException;
  }

  /** Safe interim production state: all owned acquisitions must still close on this refusal. */
  public static Operation unassembledStartup() {
    return (pool, credentials) -> {
      Objects.requireNonNull(pool, "database pool");
      Objects.requireNonNull(credentials, "service credentials");
      throw new IOException("mandatory startup assembly unavailable");
    };
  }

  public ServiceProcessResources(Inputs inputs, PoolFactory pools) {
    this(
        Objects.requireNonNull(inputs, "startup inputs"),
        LinuxDirectoryCalls.create(),
        LinuxInodeSecurity.create(),
        new InspectorCredentialLoader.NioIo(),
        pools);
  }

  ServiceProcessResources(
      Inputs inputs,
      DirectoryCalls directories,
      InodeSecurityCalls security,
      InspectorCredentialLoader.Io io,
      PoolFactory pools) {
    this(
        inputs,
        directories,
        security,
        io,
        (url, password) -> new ServiceDatabaseSource(inputs.service(), url, password),
        pools);
  }

  ServiceProcessResources(
      Inputs inputs,
      DirectoryCalls directories,
      InodeSecurityCalls security,
      InspectorCredentialLoader.Io io,
      SourceFactory sources,
      PoolFactory pools) {
    this.inputs = Objects.requireNonNull(inputs, "startup inputs");
    this.directories = Objects.requireNonNull(directories, "directory calls");
    this.security = Objects.requireNonNull(security, "inode security");
    this.io = Objects.requireNonNull(io, "credential IO");
    this.sources = Objects.requireNonNull(sources, "database source factory");
    this.pools = Objects.requireNonNull(pools, "database pool factory");
  }

  public void execute(Operation operation) throws StorageIoException {
    execute(operation, false);
  }

  /** Native callback: an unconfirmed release must not unwind downstream key/root owners. */
  public void executeRetainingUnknown(Operation operation) throws StorageIoException {
    execute(operation, true);
  }

  private void execute(Operation operation, boolean retainUnknown) throws StorageIoException {
    Objects.requireNonNull(operation, "startup operation");
    ResourceScope.acquire(
        () -> OwnedTransferDirectory.open(directories, inputs.credentials().directory()),
        ownedRelease(OwnedTransferDirectory::close, retainUnknown),
        root -> {
          var reader = new ServiceCredentialReader(root, security, inputs.service(), io);
          return ResourceScope.acquire(
              () -> ServiceCredentialSet.load(reader, inputs.service()),
              ownedRelease(ServiceCredentialSet::close, retainUnknown),
              credentials -> withDatabase(credentials, operation, retainUnknown));
        });
  }

  private Boolean withDatabase(
      ServiceCredentialSet credentials, Operation operation, boolean retainUnknown)
      throws StorageIoException {
    char[] password =
        credentials.copyPassword(ServiceCredentialId.forService(inputs.service()).getFirst());
    try {
      return ResourceScope.<ServiceDatabaseSource, Boolean, StorageIoException>acquire(
          () -> sources.open(inputs.databaseUrl(), password),
          ownedRelease(ServiceDatabaseSource::close, retainUnknown),
          source -> {
            // Clear before any pool operation/release can retain an UNKNOWN outer frame.
            Arrays.fill(password, '\0');
            return ResourceScope.<HikariDataSource, Boolean, StorageIoException>acquire(
                () -> pools.open(source),
                ownedRelease(HikariDataSource::close, retainUnknown),
                pool -> {
                  operation.run(pool, credentials);
                  return Boolean.TRUE;
                });
          });
    } finally {
      // Includes factory failure/null and callback construction failure before acquisition.
      Arrays.fill(password, '\0');
    }
  }

  /** SSC308: this resource-independent port is completely constructed before acquisition. */
  public static <R> ResourceScope.Release<R> ownedRelease(
      ResourceScope.Release<R> release, boolean retainUnknown) {
    Objects.requireNonNull(release, "service resource release");
    if (!retainUnknown) return release;
    return ownedRelease(release, unknownReleasePolicy());
  }

  /** SSC318: invocation initializes this retaining class before the caller's factory runs. */
  public static Consumer<Throwable> unknownReleasePolicy() {
    return ServiceProcessResources::retainUnknownRelease;
  }

  // A finite observer may inspect the failure in component PT; returning still rethrows UNKNOWN.
  static <R> ResourceScope.Release<R> ownedRelease(
      ResourceScope.Release<R> release, Consumer<Throwable> onUnconfirmed) {
    Objects.requireNonNull(release, "service resource release");
    Objects.requireNonNull(onUnconfirmed, "unconfirmed release policy");
    return resource -> {
      try {
        release.close(resource);
      } catch (IOException | RuntimeException | Error unconfirmed) {
        onUnconfirmed.accept(unconfirmed);
        throw unconfirmed;
      }
    };
  }

  // The native owner holds this exact release frame, including the original failure graph.
  // No raw provider text, clean marker, automatic retry or downstream cleanup after UNKNOWN.
  static Closeable release(Closeable resource, boolean retainUnknown) {
    Objects.requireNonNull(resource, "service resource release");
    if (!retainUnknown) return resource;
    var release = ServiceProcessResources.<Closeable>ownedRelease(Closeable::close, true);
    return () -> release.close(resource);
  }

  /**
   * SSC316: fixed native retention only; no retry, release, normal completion or raw diagnostic.
   */
  public static void retainUnknownRelease(Throwable unconfirmed) {
    diagnoseUnknownRelease(unconfirmed);
    while (true) observeUnknownInterval(UNKNOWN_OBSERVATION, UNKNOWN_FALLBACK);
  }

  // Prebuilt fault ports permit finite component observation; native policy always fixes both.
  static void retainUnknownRelease(Throwable unconfirmed, Runnable observation, Runnable fallback) {
    Objects.requireNonNull(unconfirmed, "unconfirmed release");
    Objects.requireNonNull(observation, "unconfirmed observation");
    Objects.requireNonNull(fallback, "unconfirmed fallback");
    diagnoseUnknownRelease(unconfirmed);
    while (true) observeUnknownInterval(observation, fallback);
  }

  // PG-D472/SS318: finite protected actions; each native/test entry owns its non-returning loop.
  private static void diagnoseUnknownRelease(Throwable unconfirmed) {
    Objects.requireNonNull(unconfirmed, "unconfirmed release");
    try {
      System.err.println("service resource release unconfirmed");
    } catch (RuntimeException | Error unavailableDiagnostic) {
      // Diagnostic failure is still UNKNOWN, not permission to unwind or report normal cleanup.
    }
  }

  private static void observeUnknownInterval(Runnable observation, Runnable fallback) {
    try {
      observation.run();
    } catch (RuntimeException | Error unavailableObservation) {
      try {
        fallback.run();
      } catch (RuntimeException | Error unavailableFallback) {
        // A failed tick never releases ownership; the calling loop still cannot return.
      }
    }
  }

  // Fixed monotonic fallback; an interrupt or spurious unpark cannot accelerate retry ticks.
  static void waitUnknownInterval() {
    long deadline = System.nanoTime() + OBSERVATION_NANOS;
    Thread.interrupted();
    while (true) {
      long left = deadline - System.nanoTime();
      if (left <= 0) return;
      LockSupport.parkNanos(left);
      Thread.interrupted();
    }
  }

  private static void observeUnconfirmed() {
    try {
      // Only this single observation tick returns. The original catch frame never returns.
      Thread.sleep(OBSERVATION_MILLIS);
    } catch (InterruptedException notification) {
      /* UNKNOWN still owns the full outer frame, never a release/termination proof. */
    }
  }
}
