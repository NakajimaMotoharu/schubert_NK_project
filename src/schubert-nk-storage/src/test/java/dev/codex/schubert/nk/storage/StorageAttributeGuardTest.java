package dev.codex.schubert.nk.storage;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.nio.file.Files;
import java.nio.file.LinkOption;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.nio.file.attribute.GroupPrincipal;
import java.nio.file.attribute.PosixFilePermissions;
import java.nio.file.attribute.UserPrincipal;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** Independent Unix mode/attribute matrix and real synthetic files. PT-SCN-008-A01..A03. */
class StorageAttributeGuardTest {
  private static final int TRANSFER_LIMIT_BYTES = 48_000_000;
  private static final String SIZE_FIELD = "size";
  private static final String OWNER_FIELD = "owner";
  private static final String GROUP_FIELD = "group";
  private static final String MODE_FIELD = "mode";
  private static final String LINK_COUNT_FIELD = "nlink";
  private static final StorageIdentity IDENTITY =
      new StorageIdentity("schubert-api", "schubert-web");
  @TempDir Path root;

  @Test
  void med020LargeAssetSizesKeepTransferLimitAndUnixGuards() throws Exception {
    Map<String, Object> attrs = file();
    for (long size : new long[] {1, 48_000_000, 48_000_001, 999_999_999_999L, Long.MAX_VALUE}) {
      attrs.put(SIZE_FIELD, size);
      StorageAttributeGuard.existingFile(attrs, IDENTITY, size);
      reject(() -> StorageAttributeGuard.existingFile(attrs, IDENTITY, size == 1 ? 2 : 1));
      if (size > TRANSFER_LIMIT_BYTES) {
        assertThrows(
            IllegalArgumentException.class,
            () -> StorageAttributeGuard.file(attrs, IDENTITY, size));
      }
    }
    for (long size : new long[] {0, -1, Long.MIN_VALUE}) {
      assertThrows(
          IllegalArgumentException.class,
          () -> StorageAttributeGuard.existingFile(attrs, IDENTITY, size));
    }
    assertThrows(
        NullPointerException.class, () -> StorageAttributeGuard.existingFile(null, IDENTITY, 3));
    assertThrows(
        NullPointerException.class, () -> StorageAttributeGuard.existingFile(attrs, null, 3));
    for (String key : List.of(OWNER_FIELD, GROUP_FIELD, MODE_FIELD, LINK_COUNT_FIELD, SIZE_FIELD)) {
      Map<String, Object> invalid = file();
      invalid.remove(key);
      reject(() -> StorageAttributeGuard.existingFile(invalid, IDENTITY, 3));
      for (Object value : new Object[] {null, "invalid", -1, -1L}) {
        invalid.put(key, value);
        reject(() -> StorageAttributeGuard.existingFile(invalid, IDENTITY, 3));
      }
    }
    // Typed but incorrect fields must not pass the shared guard either.
    Map<String, Object> wrong = file();
    wrong.put(OWNER_FIELD, (UserPrincipal) () -> "other");
    reject(() -> StorageAttributeGuard.existingFile(wrong, IDENTITY, 3));
    wrong.put(OWNER_FIELD, (UserPrincipal) IDENTITY::owner);
    wrong.put(GROUP_FIELD, (GroupPrincipal) () -> "other");
    reject(() -> StorageAttributeGuard.existingFile(wrong, IDENTITY, 3));
    wrong.put(GROUP_FIELD, (GroupPrincipal) IDENTITY::group);
    for (int mode :
        new int[] {
          0b100_000_110_100_000,
          0b001_010_000_110_100_000,
          0b001_000_000_110_100_100,
          0b001_000_100_110_100_000
        }) {
      wrong.put(MODE_FIELD, mode);
      reject(() -> StorageAttributeGuard.existingFile(wrong, IDENTITY, 3));
    }
    wrong.put(MODE_FIELD, 0b001_000_000_110_100_000);
    wrong.put(LINK_COUNT_FIELD, 2);
    reject(() -> StorageAttributeGuard.existingFile(wrong, IDENTITY, 3));
  }

  @Test
  void u01SizeAccountingIncludesEmptyPartialPartsButReadyRequiresWholeRecords() throws Exception {
    Map<String, Object> attrs = file();
    for (long size : new long[] {0, 1, 4799, 4800, 48_000_000}) {
      attrs.put(SIZE_FIELD, size);
      assertEquals(size, StorageAttributeGuard.transferSize(attrs, IDENTITY, false));
    }
    for (long size : new long[] {4800, 9600, 48_000_000}) {
      attrs.put(SIZE_FIELD, size);
      assertEquals(size, StorageAttributeGuard.transferSize(attrs, IDENTITY, true));
    }
    for (long size : new long[] {0, 1, 4799, 4801, 47_999_999}) {
      attrs.put(SIZE_FIELD, size);
      reject(() -> StorageAttributeGuard.transferSize(attrs, IDENTITY, true));
    }
  }

  @Test
  void u02AccountingRejectsUnknownSizeBoundsAndInvalidOwnershipOrLinkAttributes() {
    assertThrows(
        NullPointerException.class,
        () -> StorageAttributeGuard.transferSize(null, IDENTITY, false));
    assertThrows(
        NullPointerException.class, () -> StorageAttributeGuard.transferSize(file(), null, false));
    Map<String, Object> attrs = file();
    attrs.remove(SIZE_FIELD);
    reject(() -> StorageAttributeGuard.transferSize(attrs, IDENTITY, false));
    for (Object invalid : new Object[] {null, "0", 0, -1L, 48_000_001L, Long.MAX_VALUE}) {
      attrs.put(SIZE_FIELD, invalid);
      reject(() -> StorageAttributeGuard.transferSize(attrs, IDENTITY, false));
    }
    for (String name : List.of(OWNER_FIELD, GROUP_FIELD, MODE_FIELD, LINK_COUNT_FIELD)) {
      Map<String, Object> invalid = file();
      invalid.remove(name);
      reject(() -> StorageAttributeGuard.transferSize(invalid, IDENTITY, false));
    }
  }

  @Test
  void a01NullInvalidAndBoundaryOsIdentityNamesAreExplicit() {
    for (String name : List.of("mini", "_service", "a".repeat(32), "service-01", "service_01")) {
      StorageIdentity identity = new StorageIdentity(name, name);
      assertEquals(name, identity.owner());
      assertEquals(name, identity.group());
      assertEquals("StorageIdentity[REDACTED]", identity.toString());
    }
    for (String name :
        List.of("", " ", "Root", "1service", "a".repeat(33), "a/b", "a\0b", "a\nb", "利用者")) {
      assertThrows(IllegalArgumentException.class, () -> new StorageIdentity(name, GROUP_FIELD));
      assertThrows(IllegalArgumentException.class, () -> new StorageIdentity(OWNER_FIELD, name));
    }
    assertThrows(NullPointerException.class, () -> new StorageIdentity(null, GROUP_FIELD));
    assertThrows(NullPointerException.class, () -> new StorageIdentity(OWNER_FIELD, null));
    assertThrows(NullPointerException.class, () -> StorageAttributeGuard.directory(null, IDENTITY));
    assertThrows(
        NullPointerException.class, () -> StorageAttributeGuard.directory(directory(), null));
    assertThrows(NullPointerException.class, () -> StorageAttributeGuard.file(null, IDENTITY, 3));
    assertThrows(NullPointerException.class, () -> StorageAttributeGuard.file(file(), null, 3));
  }

  @Test
  void a02DirectoryTypePermissionsOwnershipAndMissingAttributesFailClosed() throws Exception {
    StorageAttributeGuard.directory(directory(), IDENTITY);
    for (String name : List.of(OWNER_FIELD, GROUP_FIELD, MODE_FIELD, LINK_COUNT_FIELD)) {
      Map<String, Object> missing = directory();
      missing.remove(name);
      reject(() -> StorageAttributeGuard.directory(missing, IDENTITY));
      missing.put(name, null);
      reject(() -> StorageAttributeGuard.directory(missing, IDENTITY));
      missing.put(name, "SYNTHETIC_INVALID_ATTRIBUTE");
      reject(() -> StorageAttributeGuard.directory(missing, IDENTITY));
    }
    Map<String, Object> attrs = directory();
    attrs.put(OWNER_FIELD, (UserPrincipal) () -> "different-owner");
    reject(() -> StorageAttributeGuard.directory(attrs, IDENTITY));
    attrs.put(OWNER_FIELD, (UserPrincipal) IDENTITY::owner);
    attrs.put(GROUP_FIELD, (GroupPrincipal) () -> "different-group");
    reject(() -> StorageAttributeGuard.directory(attrs, IDENTITY));
    attrs.put(GROUP_FIELD, (GroupPrincipal) IDENTITY::group);
    for (int mode :
        new int[] {
          0b100_000_111_000_000,
          0b100_000_111_101_101,
          0b100_010_111_101_000,
          0b100_001_111_101_000,
          0b001_000_000_111_101_000,
          0b001_010_000_111_101_000,
          0b001_100_000_111_101_000,
          0
        }) {
      attrs.put(MODE_FIELD, mode);
      reject(() -> StorageAttributeGuard.directory(attrs, IDENTITY));
    }
    attrs.put(MODE_FIELD, 0b100_000_111_101_000);
    for (int count : new int[] {0, -1}) {
      attrs.put(LINK_COUNT_FIELD, count);
      reject(() -> StorageAttributeGuard.directory(attrs, IDENTITY));
    }
    for (int count : new int[] {1, 2, 10002}) {
      attrs.put(LINK_COUNT_FIELD, count);
      StorageAttributeGuard.directory(attrs, IDENTITY);
    }
  }

  @Test
  void a02FileRequiresOneLinkExactBytesAnd0640WithoutSpecialBits() throws Exception {
    Map<String, Object> attrs = file();
    StorageAttributeGuard.file(attrs, IDENTITY, 3);
    for (long size : new long[] {0, -1, 48_000_001L, Long.MAX_VALUE}) {
      assertThrows(
          IllegalArgumentException.class, () -> StorageAttributeGuard.file(attrs, IDENTITY, size));
    }
    for (long size : new long[] {1, 3, 48_000_000L}) {
      attrs.put(SIZE_FIELD, size);
      StorageAttributeGuard.file(attrs, IDENTITY, size);
      reject(() -> StorageAttributeGuard.file(attrs, IDENTITY, size == 1 ? 2 : 1));
    }
    attrs.put(SIZE_FIELD, 3); // Integer is not the Linux long size contract.
    reject(() -> StorageAttributeGuard.file(attrs, IDENTITY, 3));
    attrs.remove(SIZE_FIELD);
    reject(() -> StorageAttributeGuard.file(attrs, IDENTITY, 3));
    attrs.put(SIZE_FIELD, null);
    reject(() -> StorageAttributeGuard.file(attrs, IDENTITY, 3));
    attrs.put(SIZE_FIELD, 3L);
    for (int links : new int[] {0, -1, 2, Integer.MAX_VALUE}) {
      attrs.put(LINK_COUNT_FIELD, links);
      reject(() -> StorageAttributeGuard.file(attrs, IDENTITY, 3));
    }
    attrs.put(LINK_COUNT_FIELD, 1);
    for (int mode :
        new int[] {
          0b001_000_000_110_000_000,
          0b001_000_000_110_100_100,
          0b001_000_100_110_100_000,
          0b001_000_010_110_100_000,
          0b001_000_001_110_100_000,
          0b100_000_110_100_000,
          0b001_010_000_110_100_000,
          0b001_100_000_110_100_000,
          0b001_000_110_100_000,
          0b110_000_110_100_000,
          0b010_000_110_100_000,
          0
        }) {
      attrs.put(MODE_FIELD, mode);
      reject(() -> StorageAttributeGuard.file(attrs, IDENTITY, 3));
    }
    attrs.put(MODE_FIELD, 0b001_000_000_110_100_000);
    StorageAttributeGuard.file(attrs, IDENTITY, 3);
  }

  @Test
  void a03ActualFileSymlinkHardLinkWrongPermissionAndOwnerRemainUntouched() throws Exception {
    Files.setPosixFilePermissions(root, PosixFilePermissions.fromString("rwxr-x---"));
    String owner = Files.getOwner(root).getName();
    String group =
        Files.readAttributes(root, java.nio.file.attribute.PosixFileAttributes.class)
            .group()
            .getName();
    StorageIdentity expected = new StorageIdentity(owner, group);
    StorageAttributeGuard.directory(attributes(root), expected);
    Path regular = root.resolve("synthetic.part");
    Files.write(regular, new byte[] {1, 2, 3}, StandardOpenOption.CREATE_NEW);
    Files.setPosixFilePermissions(regular, PosixFilePermissions.fromString("rw-r-----"));
    StorageAttributeGuard.file(attributes(regular), expected, 3);
    reject(
        () ->
            StorageAttributeGuard.file(
                attributes(regular), new StorageIdentity("not-the-owner", group), 3));
    reject(
        () ->
            StorageAttributeGuard.file(
                attributes(regular), new StorageIdentity(owner, "not-the-group"), 3));
    Path link = Files.createSymbolicLink(root.resolve("symlink.ready"), regular);
    reject(() -> StorageAttributeGuard.file(attributes(link), expected, 3));
    Path hard = Files.createLink(root.resolve("hard.ready"), regular);
    assertEquals(2, attributes(regular).get(LINK_COUNT_FIELD));
    reject(() -> StorageAttributeGuard.file(attributes(regular), expected, 3));
    reject(() -> StorageAttributeGuard.file(attributes(hard), expected, 3));
    assertArrayEquals(new byte[] {1, 2, 3}, Files.readAllBytes(regular));
    assertArrayEquals(new byte[] {1, 2, 3}, Files.readAllBytes(hard));
    assertTrue(Files.isSymbolicLink(link));
    Path other = root.resolve("wrong-mode.part");
    Files.write(other, new byte[] {1, 2, 3}, StandardOpenOption.CREATE_NEW);
    Files.setPosixFilePermissions(other, PosixFilePermissions.fromString("rw-r--r--"));
    reject(() -> StorageAttributeGuard.file(attributes(other), expected, 3));
    assertEquals(
        PosixFilePermissions.fromString("rw-r--r--"), Files.getPosixFilePermissions(other));
  }

  private static Map<String, Object> directory() {
    Map<String, Object> result = new HashMap<>();
    result.put(OWNER_FIELD, (UserPrincipal) IDENTITY::owner);
    result.put(GROUP_FIELD, (GroupPrincipal) IDENTITY::group);
    result.put(MODE_FIELD, 0b100_000_111_101_000);
    result.put(LINK_COUNT_FIELD, 2);
    return result;
  }

  private static Map<String, Object> file() {
    Map<String, Object> result = directory();
    result.put(MODE_FIELD, 0b001_000_000_110_100_000);
    result.put(LINK_COUNT_FIELD, 1);
    result.put(SIZE_FIELD, 3L);
    return result;
  }

  private static Map<String, Object> attributes(Path path) throws java.io.IOException {
    return Files.readAttributes(
        path, "unix:owner,group,mode,nlink,size", LinkOption.NOFOLLOW_LINKS);
  }

  private static void reject(org.junit.jupiter.api.function.Executable operation) {
    StorageIoException ex = assertThrows(StorageIoException.class, operation);
    assertEquals(StorageIoException.Reason.UNAVAILABLE, ex.reason());
    assertEquals("transfer storage operation failed", ex.getMessage());
    assertNull(ex.getCause());
    assertEquals(0, ex.getSuppressed().length);
  }
}
