package dev.codex.schubert.nk.storage;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.nio.file.DirectoryStream;
import java.nio.file.Files;
import java.nio.file.NoSuchFileException;
import java.nio.file.Path;
import java.nio.file.attribute.GroupPrincipal;
import java.nio.file.attribute.PosixFilePermission;
import java.nio.file.attribute.UserPrincipal;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** PT-SCN-008-A07: real Linux six-root, no-follow and read-only startup prerequisite. */
class StorageRootInspectionTest {
  @TempDir Path temporary;

  @Test
  void a08DeviceAndInodeBothDefinePhysicalRootIdentity() throws Exception {
    var same = StorageRootInspection.inode(Map.of("dev", 8L, "ino", 200L));
    var otherDevice = StorageRootInspection.inode(Map.of("dev", 9L, "ino", 200L));
    var otherInode = StorageRootInspection.inode(Map.of("dev", 8L, "ino", 201L));
    var seen = new HashSet<StorageRootInspection.Inode>();
    StorageRootInspection.requireDistinct(seen, same);
    StorageRootInspection.requireDistinct(seen, otherDevice);
    StorageRootInspection.requireDistinct(seen, otherInode);
    assertEquals(3, seen.size());
    assertThrows(StorageIoException.class, () -> StorageRootInspection.requireDistinct(seen, same));
    for (Map<String, Object> bad :
        java.util.List.of(
            Map.<String, Object>of("ino", 200L),
            Map.<String, Object>of("dev", 8L),
            Map.<String, Object>of("dev", "8", "ino", 200L),
            Map.<String, Object>of("dev", 8L, "ino", "200"),
            Map.<String, Object>of("dev", -1L, "ino", 200L),
            Map.<String, Object>of("dev", 8L, "ino", 0L))) {
      assertThrows(StorageIoException.class, () -> StorageRootInspection.inode(bad));
    }
    assertThrows(NullPointerException.class, () -> StorageRootInspection.inode(null));
    assertThrows(
        NullPointerException.class, () -> StorageRootInspection.requireDistinct(null, same));
    assertThrows(
        NullPointerException.class, () -> StorageRootInspection.requireDistinct(seen, null));
  }

  @Test
  void a07MetadataAndProviderNegativeMatrix() throws Exception {
    StorageIdentity expected = new StorageIdentity("owner", "group");
    Map<String, Object> valid = new HashMap<>();
    valid.put("mode", 040700);
    valid.put("nlink", 2);
    valid.put("owner", (UserPrincipal) () -> "owner");
    valid.put("group", (GroupPrincipal) () -> "group");
    StorageRootInspection.requireBackup(valid, expected);
    StorageRootInspection.requireDirectory(valid);
    for (String key : new String[] {"mode", "nlink", "owner", "group"}) {
      Map<String, Object> missing = new HashMap<>(valid);
      missing.remove(key);
      assertThrows(
          StorageIoException.class, () -> StorageRootInspection.requireBackup(missing, expected));
    }
    for (Object wrong : new Object[] {"bad", 0100700, 040750}) {
      Map<String, Object> changed = new HashMap<>(valid);
      changed.put("mode", wrong);
      assertThrows(
          StorageIoException.class, () -> StorageRootInspection.requireBackup(changed, expected));
    }
    Map<String, Object> zeroLinks = new HashMap<>(valid);
    zeroLinks.put("nlink", 0);
    assertThrows(StorageIoException.class, () -> StorageRootInspection.requireDirectory(zeroLinks));
    Map<String, Object> wrongLinks = new HashMap<>(valid);
    wrongLinks.put("nlink", "two");
    assertThrows(
        StorageIoException.class, () -> StorageRootInspection.requireDirectory(wrongLinks));
    Map<String, Object> wrongOwner = new HashMap<>(valid);
    wrongOwner.put("owner", (UserPrincipal) () -> "wrong");
    assertThrows(
        StorageIoException.class, () -> StorageRootInspection.requireBackup(wrongOwner, expected));
    Map<String, Object> wrongGroup = new HashMap<>(valid);
    wrongGroup.put("group", (GroupPrincipal) () -> "wrong");
    assertThrows(
        StorageIoException.class, () -> StorageRootInspection.requireBackup(wrongGroup, expected));
    try (DirectoryStream<Path> secure = Files.newDirectoryStream(temporary)) {
      StorageRootInspection.requireSecureStream(secure);
    }
    DirectoryStream<Path> ordinary =
        new DirectoryStream<>() {
          @Override
          public java.util.Iterator<Path> iterator() {
            return java.util.List.<Path>of().iterator();
          }

          @Override
          public void close() {}
        };
    assertThrows(
        StorageIoException.class, () -> StorageRootInspection.requireSecureStream(ordinary));
    assertThrows(NullPointerException.class, () -> StorageRootInspection.requireSecureStream(null));
  }

  @Test
  void a07AcceptsSixExistingRootsAndRejectsUnsafeExistingRoots() throws Exception {
    Path[] roots = roots();
    StorageIdentity identity = identity(roots[0]);
    inspect(roots, identity, identity, identity);
    int directoryDescriptorsBefore = directoryDescriptors(temporary);
    try (var entries = Files.list(temporary)) {
      assertEquals(6, entries.count());
    }
    assertEquals(directoryDescriptorsBefore, directoryDescriptors(temporary));

    Files.setPosixFilePermissions(roots[0], permissions("rwxrwx---"));
    unavailable(roots, identity, identity, identity);
    Files.setPosixFilePermissions(roots[0], permissions("rwxr-x---"));
    Files.setPosixFilePermissions(roots[1], permissions("rwx------"));
    unavailable(roots, identity, identity, identity);
    Files.setPosixFilePermissions(roots[1], permissions("rwxr-x---"));
    Files.setPosixFilePermissions(roots[2], permissions("rwxr-x---"));
    unavailable(roots, identity, identity, identity);
    Files.setPosixFilePermissions(roots[2], permissions("rwx------"));

    StorageIdentity wrong = new StorageIdentity("not_the_owner", identity.group());
    unavailable(roots, wrong, identity, identity);
    unavailable(roots, identity, wrong, identity);
    unavailable(roots, identity, identity, wrong);
    StorageIdentity wrongGroup = new StorageIdentity(identity.owner(), "not_the_group");
    unavailable(roots, identity, identity, wrongGroup);

    Path alias = temporary.resolve("alias");
    Files.createSymbolicLink(alias, roots[3]);
    Path[] symlink = roots.clone();
    symlink[3] = alias;
    unavailable(symlink, identity, identity, identity);
    Path[] missing = roots.clone();
    missing[4] = temporary.resolve("missing");
    rejected(missing, identity, identity, identity, StorageIoException.Reason.MISSING);
    Path[] regular = roots.clone();
    regular[5] = Files.createFile(temporary.resolve("regular"));
    unavailable(regular, identity, identity, identity);

    assertThrows(
        NullPointerException.class,
        () -> StorageRootInspection.inspect(null, identity, identity, identity));
    assertThrows(NullPointerException.class, () -> inspect(roots, null, identity, identity));
    assertThrows(NullPointerException.class, () -> inspect(roots, identity, null, identity));
    assertThrows(NullPointerException.class, () -> inspect(roots, identity, identity, null));
  }

  private Path[] roots() throws Exception {
    Path[] roots = new Path[6];
    for (int index = 0; index < roots.length; index++) {
      roots[index] = Files.createDirectory(temporary.resolve("root" + index));
      Files.setPosixFilePermissions(
          roots[index], permissions(index == 2 ? "rwx------" : "rwxr-x---"));
    }
    return roots;
  }

  // BUG1289: procfs observes the test fixture's OS handles independently of the list stream.
  private static int directoryDescriptors(Path directory) throws Exception {
    int count = 0;
    try (DirectoryStream<Path> descriptors = Files.newDirectoryStream(Path.of("/proc/self/fd"))) {
      for (Path descriptor : descriptors) {
        try {
          if (Files.readSymbolicLink(descriptor).equals(directory)) count++;
        } catch (NoSuchFileException gone) {
          // Another unrelated descriptor may close during the snapshot; it is not this inode.
        }
      }
    }
    return count;
  }

  private static StorageIdentity identity(Path root) throws Exception {
    return new StorageIdentity(
        Files.getOwner(root).getName(),
        Files.readAttributes(root, java.nio.file.attribute.PosixFileAttributes.class)
            .group()
            .getName());
  }

  private static void inspect(
      Path[] roots, StorageIdentity asset, StorageIdentity transfer, StorageIdentity backup)
      throws Exception {
    StorageRootInspection.inspect(
        new StorageRootLayout(roots[0], roots[1], roots[2], roots[3], roots[4], roots[5]),
        asset,
        transfer,
        backup);
  }

  private static void unavailable(
      Path[] roots, StorageIdentity asset, StorageIdentity transfer, StorageIdentity backup) {
    rejected(roots, asset, transfer, backup, StorageIoException.Reason.UNAVAILABLE);
  }

  private static void rejected(
      Path[] roots,
      StorageIdentity asset,
      StorageIdentity transfer,
      StorageIdentity backup,
      StorageIoException.Reason reason) {
    StorageIoException failure =
        assertThrows(StorageIoException.class, () -> inspect(roots, asset, transfer, backup));
    assertEquals(reason, failure.reason());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
    assertFalse(failure.getMessage().contains("root"));
  }

  private static java.util.Set<PosixFilePermission> permissions(String symbolic) {
    return java.nio.file.attribute.PosixFilePermissions.fromString(symbolic);
  }
}
