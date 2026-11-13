package dev.codex.schubert.nk.api.file;

import dev.codex.schubert.nk.api.error.TemporaryInfrastructureException;
import dev.codex.schubert.nk.api.maintenance.InspectionExecution;
import dev.codex.schubert.nk.api.maintenance.InspectionRun;
import dev.codex.schubert.nk.api.maintenance.InspectorDatabaseConnections;
import dev.codex.schubert.nk.api.maintenance.InspectorProcess;
import dev.codex.schubert.nk.api.maintenance.InspectorSettings;
import dev.codex.schubert.nk.bootstrap.ChildStartupContext;
import dev.codex.schubert.nk.bootstrap.FixedServiceIdentity;
import dev.codex.schubert.nk.bootstrap.MaintenanceOwnerFrame;
import dev.codex.schubert.nk.storage.DirectoryCalls;
import dev.codex.schubert.nk.storage.InodeSecurityCalls;
import dev.codex.schubert.nk.storage.LinuxDirectoryCalls;
import dev.codex.schubert.nk.storage.LinuxInodeSecurity;
import dev.codex.schubert.nk.storage.OwnedTransferDirectory;
import dev.codex.schubert.nk.storage.StorageIoException;
import java.io.IOException;
import java.security.NoSuchAlgorithmException;
import java.util.Objects;
import java.util.Optional;
import java.util.UUID;
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;

/**
 * Operation-owned file adapter; no main, unit or parent safety authority. NK-DAT-001;
 * DAT-009/OPS-009/FIL-006; UI212/241/251; SS343 6.7/324/341/352; QA-046/SSC-049/PG-D-143;
 * PT-DB-INBOX-212..220.
 */
@NullMarked
public final class InspectorApplication {
  private final InspectorSettings settings;
  private final DirectoryCalls directories;
  private final InodeSecurityCalls security;
  private final InspectorCredentialLoader.Io io;

  public InspectorApplication(InspectorSettings settings) {
    this(
        Objects.requireNonNull(settings, "inspector settings"),
        LinuxDirectoryCalls.create(),
        LinuxInodeSecurity.create(),
        new InspectorCredentialLoader.NioIo());
  }

  InspectorApplication(
      InspectorSettings settings,
      DirectoryCalls directories,
      InodeSecurityCalls security,
      InspectorCredentialLoader.Io io) {
    this.settings = Objects.requireNonNull(settings, "inspector settings");
    this.directories = Objects.requireNonNull(directories, "directory calls");
    this.security = Objects.requireNonNull(security, "inode security");
    this.io = Objects.requireNonNull(io, "credential IO");
  }

  /** Every invocation owns independent resources; no result is returned before final root close. */
  public InspectionExecution execute(InspectionRun run)
      throws StorageIoException, InspectorCredentialException, NoSuchAlgorithmException {
    return execute(run, Optional.empty());
  }

  /** SSC119: the external Unit entry, never an alternate admission from fixture claims. */
  public InspectionExecution executeNative(InspectionRun run)
      throws IOException, NoSuchAlgorithmException {
    Objects.requireNonNull(run, "inspection run");
    var context = new ChildStartupContext();
    var fixed = new FixedServiceIdentity().resolveInspector();
    var initial = context.capture();
    String invocation = System.getenv().getOrDefault("INVOCATION_ID", "");
    var expected = context.verifyInspector(UUID.fromString(initial.boot()), invocation, fixed);
    MaintenanceOwnerFrame owner;
    try (var root = OwnedTransferDirectory.open(directories, settings.credentialRoot())) {
      var reader = new InspectorCredentialLoader(root, security, io);
      owner = readMaintenanceOwner(reader);
    }
    validateOwner(run, initial.boot(), owner);
    return executeGuarded(
        run,
        owner.parentsGuard(),
        () -> expected.equals(context.verifyInspector(owner.boot(), invocation, fixed)),
        this::execute);
  }

  /** PG-D402 data-only equality; never grants an OS admission. */
  static void validateOwner(
      @Nullable InspectionRun run, @Nullable String boot, @Nullable MaintenanceOwnerFrame owner)
      throws IOException {
    if (run == null || boot == null || owner == null)
      throw new IllegalArgumentException("inspector owner contract required");
    if (!owner.boot().toString().equals(boot)
        || !owner.run().equals(run.id())
        || !owner.cutoff().equals(run.cutoff())
        || owner.cleanup().isEmpty()) throw new IOException("maintenance owner unavailable");
  }

  @FunctionalInterface
  interface InspectorProbe {
    boolean same() throws IOException;
  }

  @FunctionalInterface
  interface OwnedOperation {
    InspectionExecution execute(InspectionRun run, Optional<MaintenanceOwnerFrame.Guard> guard)
        throws IOException, NoSuchAlgorithmException;
  }

  /** PT-INSP-OWN676001..006: internal order/budget contract, not live ownership proof. */
  static InspectionExecution executeGuarded(
      @Nullable InspectionRun run,
      MaintenanceOwnerFrame.@Nullable Guard parents,
      @Nullable InspectorProbe probe,
      @Nullable OwnedOperation operation)
      throws IOException, NoSuchAlgorithmException {
    if (run == null || parents == null || probe == null || operation == null)
      throw new IllegalArgumentException("inspector guard contract required");
    MaintenanceOwnerFrame.Guard guard =
        () -> {
          parents.check();
          if (!probe.same()) throw new IOException("maintenance owner unavailable");
          return parents.remainingNanos();
        };
    guard.check();
    var result = operation.execute(run, Optional.of(guard));
    guard.check();
    return result;
  }

  /** PG-D408: private claim data only, never Unit/Root admission; PT-APP-925002..003. */
  static MaintenanceOwnerFrame readMaintenanceOwner(InspectorCredentialLoader reader)
      throws IOException {
    Objects.requireNonNull(reader, "private owner reader");
    try {
      return MaintenanceOwnerFrame.consume(reader.readMaintenanceOwner());
    } catch (IllegalArgumentException invalid) {
      throw new IOException("maintenance owner unavailable");
    }
  }

  /** PG-D408: operation body port, native entry still owns all admission; PT-APP-925001. */
  InspectionExecution execute(InspectionRun run, Optional<MaintenanceOwnerFrame.Guard> guard)
      throws StorageIoException, InspectorCredentialException, NoSuchAlgorithmException {
    Objects.requireNonNull(run, "inspection run");
    // BUG-134/YKT-105: no interruptible credential IO before the outer startup gate.
    if (Thread.currentThread().isInterrupted())
      return new InspectionExecution(InspectionExecution.Status.INTERRUPTED, Optional.empty());
    InspectionExecution result;
    try (var root = OwnedTransferDirectory.open(directories, settings.credentialRoot())) {
      var reader = new InspectorCredentialLoader(root, security, io);
      if (guard.isPresent())
        try {
          guard.orElseThrow().check();
        } catch (IOException unavailable) {
          // BUG2826: preserve fatal graph identity before the ordinary fixed outcome.
          TemporaryInfrastructureException.preserveFatal(unavailable);
          throw new InspectorCredentialException();
        }
      try (var password = reader.loadDatabasePassword();
          var connections = new InspectorDatabaseConnections(settings.databaseUrl(), password)) {
        result =
            (guard.isPresent()
                    ? InspectorProcess.withParent(
                        reader, connections, settings.fingerprintVersions(), guard.orElseThrow())
                    : new InspectorProcess(reader, connections, settings.fingerprintVersions()))
                .execute(run);
      }
    }
    return result;
  }
}
