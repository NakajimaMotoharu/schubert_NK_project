package dev.codex.schubert.nk.storage;

import java.io.IOException;
import java.nio.file.DirectoryStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.SecureDirectoryStream;
import java.nio.file.attribute.GroupPrincipal;
import java.nio.file.attribute.UserPrincipal;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import org.jspecify.annotations.NullMarked;

/**
 * Read-only, no-follow inspection of six existing deployment roots. This is one startup
 * prerequisite, not an OS singleton, ACL, credential, or complete readiness decision. NK-SCN-001;
 * RD FIL-001..009; UI243; SS333 §2/343 §2; PG260/PT-SCN-008-A07.
 */
@NullMarked
public final class StorageRootInspection {
  private StorageRootInspection() {}

  public static void inspect(
      StorageRootLayout layout,
      StorageIdentity assetIdentity,
      StorageIdentity transferIdentity,
      StorageIdentity backupIdentity)
      throws StorageIoException {
    Objects.requireNonNull(layout, "layout");
    Objects.requireNonNull(assetIdentity, "asset identity");
    Objects.requireNonNull(transferIdentity, "transfer identity");
    Objects.requireNonNull(backupIdentity, "backup identity");
    List<Path> roots =
        List.of(
            layout.asset(),
            layout.transfer(),
            layout.backup(),
            layout.log(),
            layout.artemis(),
            layout.staging());
    for (int index = 0; index < roots.size(); index++) {
      inspectOne(roots.get(index), index, assetIdentity, transferIdentity, backupIdentity);
    }
  }

  private static void inspectOne(
      Path root, int index, StorageIdentity asset, StorageIdentity transfer, StorageIdentity backup)
      throws StorageIoException {
    OwnedTransferDirectory held = OwnedTransferDirectory.open(LinuxDirectoryCalls.create(), root);
    ResourceScope.use(
        held::close,
        () ->
            held.atDirectory(
                path -> {
                  try {
                    Map<String, Object> attributes =
                        Files.readAttributes(path, "unix:owner,group,mode,nlink");
                    if (index == 0) StorageAttributeGuard.directory(attributes, asset);
                    else if (index == 1) StorageAttributeGuard.directory(attributes, transfer);
                    else if (index == 2) requireBackup(attributes, backup);
                    else requireDirectory(attributes);
                    try (DirectoryStream<Path> entries = Files.newDirectoryStream(path)) {
                      requireSecureStream(entries);
                    }
                    return Boolean.TRUE;
                  } catch (IOException | UnsupportedOperationException failure) {
                    throw unavailable();
                  }
                }));
  }

  static void requireBackup(Map<String, Object> attributes, StorageIdentity identity)
      throws StorageIoException {
    requireDirectory(attributes);
    Object owner = attributes.get("owner");
    Object group = attributes.get("group");
    if (!(owner instanceof UserPrincipal user)
        || !identity.owner().equals(user.getName())
        || !(group instanceof GroupPrincipal principal)
        || !identity.group().equals(principal.getName())
        || !Integer.valueOf(040700).equals(attributes.get("mode"))) throw unavailable();
  }

  static void requireDirectory(Map<String, Object> attributes) throws StorageIoException {
    Object mode = attributes.get("mode");
    Object links = attributes.get("nlink");
    if (!(mode instanceof Integer bits)
        || (bits & 0170000) != 040000
        || !(links instanceof Integer count)
        || count < 1) throw unavailable();
  }

  static void requireSecureStream(DirectoryStream<?> entries) throws StorageIoException {
    Objects.requireNonNull(entries, "entries");
    if (!(entries instanceof SecureDirectoryStream<?>)) throw unavailable();
  }

  private static StorageIoException unavailable() {
    return new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
  }
}
