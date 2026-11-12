package dev.codex.schubert.nk.web.storage;

import dev.codex.schubert.nk.protocol.codec.PermanentProtocolException;
import dev.codex.schubert.nk.protocol.file.LargeResultDescriptor;
import dev.codex.schubert.nk.protocol.layout.scenario.ScenarioEntryRecord;
import dev.codex.schubert.nk.storage.OwnedTransferDirectory;
import dev.codex.schubert.nk.storage.StorageAttributeGuard;
import dev.codex.schubert.nk.storage.StorageIdentity;
import dev.codex.schubert.nk.storage.StorageIoException;
import dev.codex.schubert.nk.web.session.SessionStoreException;
import java.nio.channels.FileChannel;
import java.nio.file.Files;
import java.nio.file.StandardOpenOption;
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.util.List;
import java.util.Objects;

/**
 * Internal read-only adapter; not registered until full root/readiness and authorization wiring.
 * NK-SCN-001; RD FIL-001..009; UI237/243; SS333 §6/7; SSC-021; PT-SCN-008-RD05. Caller owns an
 * admitted root. No physical path/channel leaves this adapter.
 */
public final class LargeResultReader {
  private final OwnedTransferDirectory root;
  private final StorageIdentity identity;

  public LargeResultReader(OwnedTransferDirectory root, StorageIdentity identity) {
    this.root = Objects.requireNonNull(root, "root");
    this.identity = Objects.requireNonNull(identity, "identity");
  }

  public List<ScenarioEntryRecord> readScenario(LargeResultDescriptor descriptor)
      throws FileIntegrityException {
    Objects.requireNonNull(descriptor, "descriptor");
    try {
      verifyDirectory(root);
      LocalDate date =
          LocalDate.parse(
              descriptor.relativePath().substring(0, 8), DateTimeFormatter.BASIC_ISO_DATE);
      try (var day = root.openExistingDate(date)) {
        verifyDirectory(day);
        return day.atReadyHandle(
            descriptor.fileId(),
            handle -> {
              StorageAttributeGuard.file(
                  Files.readAttributes(handle, "unix:owner,group,mode,nlink,size"),
                  identity,
                  descriptor.byteLength());
              try (var channel = FileChannel.open(handle, StandardOpenOption.READ)) {
                List<ScenarioEntryRecord> records = ScenarioRecordReader.read(channel, descriptor);
                StorageAttributeGuard.file(
                    Files.readAttributes(handle, "unix:owner,group,mode,nlink,size"),
                    identity,
                    descriptor.byteLength());
                return records;
              }
            });
      }
    } catch (StorageIoException | PermanentProtocolException | IllegalArgumentException failure) {
      SessionStoreException.preserveFatal(failure);
      throw new FileIntegrityException();
    }
  }

  private void verifyDirectory(OwnedTransferDirectory directory) throws StorageIoException {
    directory.atDirectory(
        handle -> {
          StorageAttributeGuard.directory(
              Files.readAttributes(handle, "unix:owner,group,mode,nlink"), identity);
          return Boolean.TRUE;
        });
  }
}
