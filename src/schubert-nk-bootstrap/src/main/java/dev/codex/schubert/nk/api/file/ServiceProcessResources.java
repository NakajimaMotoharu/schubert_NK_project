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
    var root = OwnedTransferDirectory.open(directories, inputs.credentials().directory());
    ResourceScope.use(
        release(root::close, retainUnknown),
        () -> {
          var reader = new ServiceCredentialReader(root, security, inputs.service(), io);
          var credentials = ServiceCredentialSet.load(reader, inputs.service());
          return ResourceScope.use(
              release(credentials::close, retainUnknown),
              () -> withDatabase(credentials, operation, retainUnknown));
        });
  }

  private Boolean withDatabase(
      ServiceCredentialSet credentials, Operation operation, boolean retainUnknown)
      throws StorageIoException {
    char[] password =
        credentials.copyPassword(ServiceCredentialId.forService(inputs.service()).getFirst());
    ServiceDatabaseSource source;
    try {
      source =
          Objects.requireNonNull(sources.open(inputs.databaseUrl(), password), "database source");
    } finally {
      Arrays.fill(password, '\0');
    }
    return ResourceScope.use(
        release(source::close, retainUnknown),
        () -> {
          HikariDataSource pool = Objects.requireNonNull(pools.open(source), "database pool");
          return ResourceScope.use(
              release(pool::close, retainUnknown),
              () -> {
                operation.run(pool, credentials);
                return Boolean.TRUE;
              });
        });
  }

  // The native owner holds this exact release frame, including the original failure graph.
  // No raw provider text, clean marker, automatic retry or downstream cleanup after UNKNOWN.
  static Closeable release(Closeable resource, boolean retainUnknown) {
    Objects.requireNonNull(resource, "service resource release");
    if (!retainUnknown) return resource;
    return () -> {
      try {
        resource.close();
      } catch (IOException | RuntimeException | Error unconfirmed) {
        System.err.println("service resource release unconfirmed");
        while (true) {
          try {
            // Periodic observation wakeup, never a release/automatic retry/termination proof.
            Thread.sleep(1000);
          } catch (InterruptedException notification) {
            /* UNKNOWN still owns the full outer frame. */
          }
        }
      }
    };
  }
}
