package dev.codex.schubert.nk.api.file;

import dev.codex.schubert.nk.api.maintenance.InspectionExecution;
import dev.codex.schubert.nk.api.maintenance.InspectionRun;
import dev.codex.schubert.nk.api.maintenance.InspectorDatabaseConnections;
import dev.codex.schubert.nk.api.maintenance.InspectorProcess;
import dev.codex.schubert.nk.api.maintenance.InspectorSettings;
import dev.codex.schubert.nk.storage.DirectoryCalls;
import dev.codex.schubert.nk.storage.InodeSecurityCalls;
import dev.codex.schubert.nk.storage.LinuxDirectoryCalls;
import dev.codex.schubert.nk.storage.LinuxInodeSecurity;
import dev.codex.schubert.nk.storage.OwnedTransferDirectory;
import dev.codex.schubert.nk.storage.StorageIoException;
import java.security.NoSuchAlgorithmException;
import java.util.Objects;
import java.util.Optional;
import org.jspecify.annotations.NullMarked;

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
    Objects.requireNonNull(run, "inspection run");
    // BUG-134/YKT-105: no interruptible credential IO before the outer startup gate.
    if (Thread.currentThread().isInterrupted())
      return new InspectionExecution(InspectionExecution.Status.INTERRUPTED, Optional.empty());
    InspectionExecution result;
    try (var root = OwnedTransferDirectory.open(directories, settings.credentialRoot())) {
      var reader = new InspectorCredentialLoader(root, security, io);
      try (var password = reader.loadDatabasePassword();
          var connections = new InspectorDatabaseConnections(settings.databaseUrl(), password)) {
        result =
            new InspectorProcess(reader, connections, settings.fingerprintVersions()).execute(run);
      }
    }
    return result;
  }
}
