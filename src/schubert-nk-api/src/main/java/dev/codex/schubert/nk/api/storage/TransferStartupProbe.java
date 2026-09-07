package dev.codex.schubert.nk.api.storage;

import dev.codex.schubert.nk.storage.OwnedTransferDirectory;
import dev.codex.schubert.nk.storage.StorageAttributeGuard;
import dev.codex.schubert.nk.storage.StorageIdentity;
import dev.codex.schubert.nk.storage.StorageIoException;
import java.nio.file.Files;
import java.time.Instant;
import java.time.LocalDate;
import java.time.ZoneId;
import java.util.Objects;
import java.util.UUID;
import java.util.function.Supplier;

/**
 * Exclusive startup only; never register before single-instance/producer-stop/root admission gates.
 * NK-SCN-001; RD FIL-001..009; UI237/243; SS333 §7.4/342; SSC-022; PT-SCN-008-P01..P03. Removes
 * only its CREATE_NEW diagnostic artifacts; never issues a business descriptor.
 */
final class TransferStartupProbe {
  private final OwnedTransferDirectory root;
  private final StorageIdentity identity;
  private final Supplier<UUID> ids;
  private final ProbeFileIo files;

  TransferStartupProbe(OwnedTransferDirectory root, StorageIdentity identity) {
    this(root, identity, UUID::randomUUID, new HeldProbeFileIo(identity));
  }

  TransferStartupProbe(
      OwnedTransferDirectory root,
      StorageIdentity identity,
      Supplier<UUID> ids,
      ProbeFileIo files) {
    this.root = Objects.requireNonNull(root, "root");
    this.identity = Objects.requireNonNull(identity, "identity");
    this.ids = Objects.requireNonNull(ids, "ids");
    this.files = Objects.requireNonNull(files, "files");
  }

  void verify(Instant now) throws StorageIoException {
    Objects.requireNonNull(now, "now");
    LocalDate date = LocalDate.ofInstant(now, ZoneId.of("Asia/Tokyo"));
    if (date.getYear() < 1 || date.getYear() > 9999) {
      throw new IllegalArgumentException("invalid probe date");
    }
    UUID id = Objects.requireNonNull(ids.get(), "probe ID");
    TransferRootInspection.inspect(root, identity);
    try (var day =
        root.openDate(
            date,
            handle -> {
              files.initializeDirectory(handle);
              return Boolean.TRUE;
            })) {
      day.atDirectory(
          handle -> {
            StorageAttributeGuard.directory(
                Files.readAttributes(handle, "unix:owner,group,mode,nlink"), identity);
            return Boolean.TRUE;
          });
      var ownership = new Ownership();
      try {
        write(day, id, false, ownership);
        day.publish(id);
        ownership.part = false;
        ownership.ready = true;
        write(day, id, true, ownership);
        requireCollision(day, id, ownership);
        day.atReadyHandle(
            id,
            handle -> {
              files.verify(handle, false);
              return Boolean.TRUE;
            });
        day.atPartHandle(
            id,
            handle -> {
              files.verify(handle, true);
              return Boolean.TRUE;
            });
      } finally {
        cleanup(day, id, ownership);
      }
    } catch (StorageIoException | RuntimeException failure) {
      throw new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
    }
  }

  private void write(OwnedTransferDirectory day, UUID id, boolean second, Ownership ownership)
      throws StorageIoException {
    day.createPart(
        id,
        handle -> {
          ownership.part = true;
          files.write(handle, second);
          return Boolean.TRUE;
        });
  }

  private static void requireCollision(OwnedTransferDirectory day, UUID id, Ownership ownership)
      throws StorageIoException {
    try {
      day.publish(id);
      ownership.part = false;
    } catch (StorageIoException failure) {
      if (failure.reason() == StorageIoException.Reason.COLLISION) return;
      throw failure;
    }
    throw new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
  }

  private void cleanup(OwnedTransferDirectory day, UUID id, Ownership ownership)
      throws StorageIoException {
    boolean failed = false;
    if (ownership.part) {
      try {
        day.deletePart(id);
      } catch (StorageIoException | RuntimeException failure) {
        failed = true;
      }
    }
    if (ownership.ready) {
      try {
        // Changed/unreadable evidence is preserved, even if the attempt originally owned the name.
        day.atReadyHandle(
            id,
            handle -> {
              files.verify(handle, false);
              return Boolean.TRUE;
            });
        // SSC-022: diagnostic UUID created by this exclusive attempt, never a business file.
        day.atReady(
            id,
            path -> {
              Files.delete(path);
              return Boolean.TRUE;
            });
      } catch (StorageIoException | RuntimeException failure) {
        failed = true;
      }
    }
    try {
      day.sync();
    } catch (StorageIoException | RuntimeException failure) {
      failed = true;
    }
    if (failed) throw new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
  }

  private static final class Ownership {
    private boolean part;
    private boolean ready;
  }
}
