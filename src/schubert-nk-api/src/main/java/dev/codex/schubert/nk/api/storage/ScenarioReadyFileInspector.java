package dev.codex.schubert.nk.api.storage;

import dev.codex.schubert.nk.api.file.ScenarioFileInspector;
import dev.codex.schubert.nk.protocol.file.LargeResultContent;
import dev.codex.schubert.nk.protocol.file.LargeResultDescriptor;
import dev.codex.schubert.nk.storage.OwnedTransferDirectory;
import dev.codex.schubert.nk.storage.StorageAttributeGuard;
import dev.codex.schubert.nk.storage.StorageIdentity;
import dev.codex.schubert.nk.storage.StorageIoException;
import java.nio.file.Files;
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.util.Objects;

/**
 * API-internal existing-ready integrity check on held inodes, no file mutation or DB access.
 * NK-SCN-001; FIL-001..009/MQ-006..010; UI237/241; SS324 §7.1/333 §6;
 * SSC-027/PG-D-069/PT-SCN-009-V01..V03. Full startup registration remains a separate gate.
 */
final class ScenarioReadyFileInspector implements ScenarioFileInspector {
  private final OwnedTransferDirectory root;
  private final StorageIdentity identity;
  private final TransferFileIo files;

  ScenarioReadyFileInspector(OwnedTransferDirectory root, StorageIdentity identity) {
    this(root, identity, new HeldTransferFileIo(identity));
  }

  ScenarioReadyFileInspector(
      OwnedTransferDirectory root, StorageIdentity identity, TransferFileIo files) {
    this.root = Objects.requireNonNull(root, "root");
    this.identity = Objects.requireNonNull(identity, "identity");
    this.files = Objects.requireNonNull(files, "files");
  }

  @Override
  public Availability inspect(LargeResultDescriptor descriptor) throws StorageIoException {
    Objects.requireNonNull(descriptor, "descriptor");
    try {
      TransferRootInspection.inspect(root, identity);
      return inspectDate(descriptor);
    } catch (StorageIoException | RuntimeException failure) {
      // Missing held root capabilities or close failures are not proof of file absence.
      throw new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
    }
  }

  private Availability inspectDate(LargeResultDescriptor descriptor) throws StorageIoException {
    boolean dateOpened = false;
    try (var date =
        root.openExistingDate(
            LocalDate.parse(
                descriptor.relativePath().substring(0, 8), DateTimeFormatter.BASIC_ISO_DATE))) {
      dateOpened = true;
      date.atDirectory(
          handle -> {
            StorageAttributeGuard.directory(
                Files.readAttributes(handle, "unix:owner,group,mode,nlink"), identity);
            return Boolean.TRUE;
          });
      return inspectEntry(date, descriptor);
    } catch (StorageIoException failure) {
      if (failure.reason() == StorageIoException.Reason.MISSING && !dateOpened)
        return Availability.MISSING;
      throw failure;
    }
  }

  private Availability inspectEntry(OwnedTransferDirectory date, LargeResultDescriptor descriptor)
      throws StorageIoException {
    boolean[] entered = {false};
    try {
      return date.atReadyHandle(
          descriptor.fileId(),
          handle -> {
            entered[0] = true;
            files.verify(
                handle,
                new LargeResultContent(
                    descriptor.recordCount(), descriptor.byteLength(), descriptor.sha256()));
            StorageAttributeGuard.file(
                Files.readAttributes(handle, "unix:owner,group,mode,nlink,size"),
                identity,
                descriptor.byteLength());
            return Availability.PRESENT;
          });
    } catch (StorageIoException failure) {
      if (failure.reason() == StorageIoException.Reason.MISSING && !entered[0])
        return Availability.MISSING;
      throw failure;
    }
  }
}
