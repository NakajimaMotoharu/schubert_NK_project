package dev.codex.schubert.nk.api.storage;

import java.nio.file.attribute.GroupPrincipal;
import java.nio.file.attribute.UserPrincipal;
import java.util.Map;
import java.util.Objects;

/**
 * Strict Linux Unix-attribute contract, applied to held inode capabilities, not user paths.
 * NK-SCN-001; RD FIL-001..009; UI237/243; SS333 §2/7 and 343 §2; PT-SCN-008-A02/A03. A valid
 * attribute map is not root admission, authorization, descriptor/hash verification or I/O.
 */
final class StorageAttributeGuard {
  private StorageAttributeGuard() {}

  static void directory(Map<String, Object> attributes, StorageIdentity identity)
      throws StorageIoException {
    requireOwnership(attributes, identity);
    require(integer(attributes, "mode") == 040750);
    require(integer(attributes, "nlink") >= 1);
  }

  static void file(Map<String, Object> attributes, StorageIdentity identity, long expectedSize)
      throws StorageIoException {
    Objects.requireNonNull(attributes, "attributes");
    Objects.requireNonNull(identity, "identity");
    if (expectedSize < 1 || expectedSize > 48_000_000L) {
      throw new IllegalArgumentException("invalid transfer file size");
    }
    requireOwnership(attributes, identity);
    require(integer(attributes, "mode") == 0100640);
    require(integer(attributes, "nlink") == 1);
    Object size = attributes.get("size");
    require(size instanceof Long value && value == expectedSize);
  }

  private static void requireOwnership(Map<String, Object> attributes, StorageIdentity identity)
      throws StorageIoException {
    Objects.requireNonNull(attributes, "attributes");
    Objects.requireNonNull(identity, "identity");
    Object owner = attributes.get("owner");
    Object group = attributes.get("group");
    require(owner instanceof UserPrincipal user && identity.owner().equals(user.getName()));
    require(
        group instanceof GroupPrincipal principal && identity.group().equals(principal.getName()));
  }

  private static int integer(Map<String, Object> attributes, String name)
      throws StorageIoException {
    Object field = attributes.get(name);
    if (!(field instanceof Integer number)) {
      throw new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
    }
    return number;
  }

  private static void require(boolean valid) throws StorageIoException {
    if (!valid) {
      throw new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
    }
  }
}
