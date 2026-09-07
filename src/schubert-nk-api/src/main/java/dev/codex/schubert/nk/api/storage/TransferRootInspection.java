package dev.codex.schubert.nk.api.storage;

import java.io.IOException;
import java.nio.file.DirectoryStream;
import java.nio.file.Files;
import java.nio.file.SecureDirectoryStream;
import java.util.Objects;

/**
 * Held-directory metadata/provider inspection, not complete startup admission or authorization.
 * NK-SCN-001; RD FIL-001..009; UI237/243; SS333 §2/7; PG-D-058; PT-SCN-008-A06.
 */
final class TransferRootInspection {
  private TransferRootInspection() {}

  static void inspect(OwnedTransferDirectory directory, StorageIdentity identity)
      throws StorageIoException {
    Objects.requireNonNull(directory, "directory");
    Objects.requireNonNull(identity, "identity");
    directory.atDirectory(
        handle -> {
          try {
            StorageAttributeGuard.directory(
                Files.readAttributes(handle, "unix:owner,group,mode,nlink"), identity);
            var store = Files.getFileStore(handle);
            requireFileStore(store.type(), store.isReadOnly());
            try (DirectoryStream<java.nio.file.Path> entries = Files.newDirectoryStream(handle)) {
              requireSecureDirectoryStream(entries);
            }
            return Boolean.TRUE;
          } catch (IOException | UnsupportedOperationException ex) {
            throw new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
          }
        });
  }

  static void requireFileStore(String type, boolean readOnly) throws StorageIoException {
    Objects.requireNonNull(type, "type");
    // Initial proven local filesystem only; add another only after explicit compatibility PT.
    if (!type.equals("ext4") || readOnly) {
      throw new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
    }
  }

  static void requireSecureDirectoryStream(DirectoryStream<?> entries) throws StorageIoException {
    Objects.requireNonNull(entries, "entries");
    if (!(entries instanceof SecureDirectoryStream<?>)) {
      throw new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
    }
  }
}
