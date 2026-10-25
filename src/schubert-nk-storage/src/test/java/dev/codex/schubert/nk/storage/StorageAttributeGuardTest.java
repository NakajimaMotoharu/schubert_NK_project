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
  private static final StorageIdentity IDENTITY =
      new StorageIdentity("schubert-api", "schubert-web");
  @TempDir Path root;

  @Test
  void med020LargeAssetSizesKeepTransferLimitAndUnixGuards() throws Exception {
    Map<String, Object> attrs = file();
    for (long size : new long[] {1, 48_000_000, 48_000_001, 999_999_999_999L, Long.MAX_VALUE}) {
      attrs.put("size", size);
      StorageAttributeGuard.existingFile(attrs, IDENTITY, size);
      reject(() -> StorageAttributeGuard.existingFile(attrs, IDENTITY, size == 1 ? 2 : 1));
      if (size > 48_000_000) {
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
    for (String key : List.of("owner", "group", "mode", "nlink", "size")) {
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
    wrong.put("owner", (UserPrincipal) () -> "other");
    reject(() -> StorageAttributeGuard.existingFile(wrong, IDENTITY, 3));
    wrong.put("owner", (UserPrincipal) IDENTITY::owner);
    wrong.put("group", (GroupPrincipal) () -> "other");
    reject(() -> StorageAttributeGuard.existingFile(wrong, IDENTITY, 3));
    wrong.put("group", (GroupPrincipal) IDENTITY::group);
    for (int mode : new int[] {040640, 0120640, 0100644, 0104640}) {
      wrong.put("mode", mode);
      reject(() -> StorageAttributeGuard.existingFile(wrong, IDENTITY, 3));
    }
    wrong.put("mode", 0100640);
    wrong.put("nlink", 2);
    reject(() -> StorageAttributeGuard.existingFile(wrong, IDENTITY, 3));
  }

  @Test
  void u01SizeAccountingIncludesEmptyPartialPartsButReadyRequiresWholeRecords() throws Exception {
    Map<String, Object> attrs = file();
    for (long size : new long[] {0, 1, 4799, 4800, 48_000_000}) {
      attrs.put("size", size);
      assertEquals(size, StorageAttributeGuard.transferSize(attrs, IDENTITY, false));
    }
    for (long size : new long[] {4800, 9600, 48_000_000}) {
      attrs.put("size", size);
      assertEquals(size, StorageAttributeGuard.transferSize(attrs, IDENTITY, true));
    }
    for (long size : new long[] {0, 1, 4799, 4801, 47_999_999}) {
      attrs.put("size", size);
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
    attrs.remove("size");
    reject(() -> StorageAttributeGuard.transferSize(attrs, IDENTITY, false));
    for (Object invalid : new Object[] {null, "0", 0, -1L, 48_000_001L, Long.MAX_VALUE}) {
      attrs.put("size", invalid);
      reject(() -> StorageAttributeGuard.transferSize(attrs, IDENTITY, false));
    }
    for (String name : List.of("owner", "group", "mode", "nlink")) {
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
      assertThrows(IllegalArgumentException.class, () -> new StorageIdentity(name, "group"));
      assertThrows(IllegalArgumentException.class, () -> new StorageIdentity("owner", name));
    }
    assertThrows(NullPointerException.class, () -> new StorageIdentity(null, "group"));
    assertThrows(NullPointerException.class, () -> new StorageIdentity("owner", null));
    assertThrows(NullPointerException.class, () -> StorageAttributeGuard.directory(null, IDENTITY));
    assertThrows(
        NullPointerException.class, () -> StorageAttributeGuard.directory(directory(), null));
    assertThrows(NullPointerException.class, () -> StorageAttributeGuard.file(null, IDENTITY, 3));
    assertThrows(NullPointerException.class, () -> StorageAttributeGuard.file(file(), null, 3));
  }

  @Test
  void a02DirectoryTypePermissionsOwnershipAndMissingAttributesFailClosed() throws Exception {
    StorageAttributeGuard.directory(directory(), IDENTITY);
    for (String name : List.of("owner", "group", "mode", "nlink")) {
      Map<String, Object> missing = directory();
      missing.remove(name);
      reject(() -> StorageAttributeGuard.directory(missing, IDENTITY));
      missing.put(name, null);
      reject(() -> StorageAttributeGuard.directory(missing, IDENTITY));
      missing.put(name, "SYNTHETIC_INVALID_ATTRIBUTE");
      reject(() -> StorageAttributeGuard.directory(missing, IDENTITY));
    }
    Map<String, Object> attrs = directory();
    attrs.put("owner", (UserPrincipal) () -> "different-owner");
    reject(() -> StorageAttributeGuard.directory(attrs, IDENTITY));
    attrs.put("owner", (UserPrincipal) IDENTITY::owner);
    attrs.put("group", (GroupPrincipal) () -> "different-group");
    reject(() -> StorageAttributeGuard.directory(attrs, IDENTITY));
    attrs.put("group", (GroupPrincipal) IDENTITY::group);
    for (int mode : new int[] {040700, 040755, 042750, 041750, 0100750, 0120750, 0140750, 0}) {
      attrs.put("mode", mode);
      reject(() -> StorageAttributeGuard.directory(attrs, IDENTITY));
    }
    attrs.put("mode", 040750);
    for (int count : new int[] {0, -1}) {
      attrs.put("nlink", count);
      reject(() -> StorageAttributeGuard.directory(attrs, IDENTITY));
    }
    for (int count : new int[] {1, 2, 10002}) {
      attrs.put("nlink", count);
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
      attrs.put("size", size);
      StorageAttributeGuard.file(attrs, IDENTITY, size);
      reject(() -> StorageAttributeGuard.file(attrs, IDENTITY, size == 1 ? 2 : 1));
    }
    attrs.put("size", 3); // Integer is not the Linux long size contract.
    reject(() -> StorageAttributeGuard.file(attrs, IDENTITY, 3));
    attrs.remove("size");
    reject(() -> StorageAttributeGuard.file(attrs, IDENTITY, 3));
    attrs.put("size", null);
    reject(() -> StorageAttributeGuard.file(attrs, IDENTITY, 3));
    attrs.put("size", 3L);
    for (int links : new int[] {0, -1, 2, Integer.MAX_VALUE}) {
      attrs.put("nlink", links);
      reject(() -> StorageAttributeGuard.file(attrs, IDENTITY, 3));
    }
    attrs.put("nlink", 1);
    for (int mode :
        new int[] {
          0100600, 0100644, 0104640, 0102640, 0101640, 040640, 0120640, 0140640, 010640, 060640,
          020640, 0
        }) {
      attrs.put("mode", mode);
      reject(() -> StorageAttributeGuard.file(attrs, IDENTITY, 3));
    }
    attrs.put("mode", 0100640);
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
    assertEquals(2, attributes(regular).get("nlink"));
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
    result.put("owner", (UserPrincipal) IDENTITY::owner);
    result.put("group", (GroupPrincipal) IDENTITY::group);
    result.put("mode", 040750);
    result.put("nlink", 2);
    return result;
  }

  private static Map<String, Object> file() {
    Map<String, Object> result = directory();
    result.put("mode", 0100640);
    result.put("nlink", 1);
    result.put("size", 3L);
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
