package dev.codex.schubert.nk.storage;

import java.nio.file.attribute.GroupPrincipal;
import java.nio.file.attribute.UserPrincipal;
import java.util.Map;
import java.util.Objects;

/**
 * Strict Linux Unix-attribute contract, applied to held inode capabilities, not user paths.
 * NK-SCN-001; RD FIL-001..009; UI237/243; SS333 §2/7 and 343 §2; PT-SCN-008-A02/A03. A valid
 * attribute map is not root admission, authorization, descriptor/hash verification or I/O.
 */
public final class StorageAttributeGuard {
  private StorageAttributeGuard() {}

  public static void directory(Map<String, Object> attributes, StorageIdentity identity)
      throws StorageIoException {
    requireOwnership(attributes, identity);
    require(integer(attributes, "mode") == 040750);
    require(integer(attributes, "nlink") >= 1);
  }

  public static void file(
      Map<String, Object> attributes, StorageIdentity identity, long expectedSize)
      throws StorageIoException {
    Objects.requireNonNull(attributes, "attributes");
    Objects.requireNonNull(identity, "identity");
    if (expectedSize < 1 || expectedSize > 48_000_000L) {
      throw new IllegalArgumentException("invalid transfer file size");
    }
    requireRegularFile(attributes, identity);
    Object size = attributes.get("size");
    require(size instanceof Long value && value == expectedSize);
  }

  /**
   * Startup accounting includes incomplete/empty parts; never grants read/use of their content.
   * U01/U02.
   */
  public static long transferSize(
      Map<String, Object> attributes, StorageIdentity identity, boolean ready)
      throws StorageIoException {
    requireRegularFile(attributes, identity);
    Object size = attributes.get("size");
    if (!(size instanceof Long bytes) || bytes < 0 || bytes > 48_000_000L) {
      throw new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
    }
    if (ready && (bytes == 0 || bytes % 4800 != 0)) {
      throw new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
    }
    return bytes;
  }

  private static void requireRegularFile(Map<String, Object> attributes, StorageIdentity identity)
      throws StorageIoException {
    requireOwnership(attributes, identity);
    require(integer(attributes, "mode") == 0100640);
    require(integer(attributes, "nlink") == 1);
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
