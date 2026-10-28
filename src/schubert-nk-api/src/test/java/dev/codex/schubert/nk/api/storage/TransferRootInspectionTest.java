package dev.codex.schubert.nk.api.storage;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.storage.InodeSecurityCalls;
import dev.codex.schubert.nk.storage.LinuxDirectoryCalls;
import dev.codex.schubert.nk.storage.OwnedTransferDirectory;
import dev.codex.schubert.nk.storage.StorageIdentity;
import dev.codex.schubert.nk.storage.StorageIoException;
import java.io.IOException;
import java.nio.file.DirectoryStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.SecureDirectoryStream;
import java.nio.file.attribute.PosixFileAttributes;
import java.nio.file.attribute.PosixFilePermissions;
import java.util.Collections;
import java.util.Iterator;
import java.util.List;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.AnnotatedElementContext;
import org.junit.jupiter.api.extension.ExtensionContext;
import org.junit.jupiter.api.io.TempDir;
import org.junit.jupiter.api.io.TempDirFactory;

/** Held-root real filesystem and independent provider rejection matrix. PT-SCN-008-A06. */
class TransferRootInspectionTest {
  private static final String FIXTURE_RWXR_X_E5EF2357 = "rwxr-x---";
  private static final String FIXTURE_UNIX_MODE_18F40B0C = "unix:mode";

  @TempDir(factory = Ext4Fixture.class)
  Path fixture;

  /** The host /tmp is tmpfs; real accepted fixtures belong to the ext4 project target. */
  static final class Ext4Fixture implements TempDirFactory {
    @Override
    public Path createTempDirectory(AnnotatedElementContext element, ExtensionContext context)
        throws IOException {
      return Files.createTempDirectory(Path.of("target").toAbsolutePath(), "root-inspection-");
    }
  }

  @Test
  void a06HeldRootRemainsOriginalWhenConfiguredPathIsReplacedBySymlink() throws Exception {
    Path root = Files.createDirectory(fixture.resolve("root"));
    Files.setPosixFilePermissions(root, PosixFilePermissions.fromString(FIXTURE_RWXR_X_E5EF2357));
    Path outside = Files.createDirectory(fixture.resolve("outside"));
    Files.setPosixFilePermissions(outside, PosixFilePermissions.fromString("rwx------"));
    StorageIdentity identity = identity(root);
    try (var directory = OwnedTransferDirectory.open(LinuxDirectoryCalls.create(), root)) {
      TransferRootInspection.inspect(directory, identity);
      Files.move(root, fixture.resolve("retained"));
      Files.createSymbolicLink(root, outside);
      TransferRootInspection.inspect(directory, identity);
      Object heldMode =
          directory.atDirectory(handle -> Files.getAttribute(handle, FIXTURE_UNIX_MODE_18F40B0C));
      assertEquals(040750, heldMode);
      assertThrows(NullPointerException.class, () -> directory.atDirectory(null));
      reject(
          () ->
              directory.atDirectory(
                  handle -> {
                    throw new IOException("SYNTHETIC_PRIVATE_PATH");
                  }));
      assertTrue(Files.isSymbolicLink(root));
      assertEquals(040700, Files.getAttribute(outside, FIXTURE_UNIX_MODE_18F40B0C));
      try (var entries = Files.list(outside)) {
        assertEquals(0, entries.count());
      }
    }
  }

  @Test
  void a06NullClosedWrongOwnerGroupAndPermissionNeverModifyRoot() throws Exception {
    Files.setPosixFilePermissions(
        fixture, PosixFilePermissions.fromString(FIXTURE_RWXR_X_E5EF2357));
    StorageIdentity identity = identity(fixture);
    var directory = OwnedTransferDirectory.open(LinuxDirectoryCalls.create(), fixture);
    try (directory) {
      assertThrows(
          NullPointerException.class, () -> TransferRootInspection.inspect(null, identity));
      assertThrows(
          NullPointerException.class, () -> TransferRootInspection.inspect(directory, null));
      reject(
          () ->
              TransferRootInspection.inspect(
                  directory, new StorageIdentity("unknown-service", identity.group())));
      reject(
          () ->
              TransferRootInspection.inspect(
                  directory, new StorageIdentity(identity.owner(), "unknown-group")));
      for (String mode : List.of("rwx------", "rwxrwx---", "rwxr-xr-x")) {
        Files.setPosixFilePermissions(fixture, PosixFilePermissions.fromString(mode));
        reject(() -> TransferRootInspection.inspect(directory, identity));
        assertEquals(PosixFilePermissions.fromString(mode), Files.getPosixFilePermissions(fixture));
      }
      Files.setPosixFilePermissions(
          fixture, PosixFilePermissions.fromString(FIXTURE_RWXR_X_E5EF2357));
      TransferRootInspection.inspect(directory, identity);
    }
    reject(() -> TransferRootInspection.inspect(directory, identity));
    assertEquals(040750, Files.getAttribute(fixture, FIXTURE_UNIX_MODE_18F40B0C));
  }

  @Test
  void a06OnlyProvenWritableExt4AndSecureDirectoryProviderAreAccepted() throws Exception {
    TransferRootInspection.requireFileStore("ext4", false);
    reject(() -> TransferRootInspection.requireFileStore("ext4", true));
    for (String type :
        List.of("", "EXT4", "ext3", "nfs", "cifs", "tmpfs", "xfs", "btrfs", "overlay")) {
      reject(() -> TransferRootInspection.requireFileStore(type, false));
      reject(() -> TransferRootInspection.requireFileStore(type, true));
    }
    assertThrows(
        NullPointerException.class, () -> TransferRootInspection.requireFileStore(null, false));
    assertThrows(
        NullPointerException.class,
        () -> TransferRootInspection.requireSecureDirectoryStream(null));
    try (DirectoryStream<Path> entries = Files.newDirectoryStream(fixture)) {
      assertInstanceOf(SecureDirectoryStream.class, entries);
      TransferRootInspection.requireSecureDirectoryStream(entries);
    }
    try (DirectoryStream<Path> plain =
        new DirectoryStream<>() {
          @Override
          public Iterator<Path> iterator() {
            return Collections.emptyIterator();
          }

          @Override
          public void close() {}
        }) {
      reject(() -> TransferRootInspection.requireSecureDirectoryStream(plain));
      assertFalse(plain.iterator().hasNext());
    }
  }

  private static StorageIdentity identity(Path root) throws IOException {
    PosixFileAttributes attributes = Files.readAttributes(root, PosixFileAttributes.class);
    return new StorageIdentity(attributes.owner().getName(), attributes.group().getName());
  }

  @Test
  void a06Mount001CurrentHeldMountFlagsAreMandatoryAndReadOnlyIsRejected() throws Exception {
    Files.setPosixFilePermissions(
        fixture, PosixFilePermissions.fromString(FIXTURE_RWXR_X_E5EF2357));
    var identity = identity(fixture);
    var calls = new AtomicInteger();
    try (var root = OwnedTransferDirectory.open(LinuxDirectoryCalls.create(), fixture)) {
      reject(() -> TransferRootInspection.inspect(root, identity, mount(true, false, calls)));
      assertEquals(1, calls.get());
      TransferRootInspection.inspect(root, identity, mount(false, false, calls));
      assertEquals(2, calls.get());
      assertEquals(040750, Files.getAttribute(fixture, FIXTURE_UNIX_MODE_18F40B0C));
      try (var entries = Files.list(fixture)) {
        assertEquals(0, entries.count());
      }
    }
  }

  @Test
  void a06Mount002UnknownMountAndNullNeverFallBackToWritablePath() throws Exception {
    Files.setPosixFilePermissions(
        fixture, PosixFilePermissions.fromString(FIXTURE_RWXR_X_E5EF2357));
    var identity = identity(fixture);
    var calls = new AtomicInteger();
    try (var root = OwnedTransferDirectory.open(LinuxDirectoryCalls.create(), fixture)) {
      reject(() -> TransferRootInspection.inspect(root, identity, mount(false, true, calls)));
      assertEquals(1, calls.get());
      assertThrows(
          NullPointerException.class, () -> TransferRootInspection.inspect(root, identity, null));
      assertEquals(1, calls.get());
      assertEquals(040750, Files.getAttribute(fixture, FIXTURE_UNIX_MODE_18F40B0C));
      try (var entries = Files.list(fixture)) {
        assertEquals(0, entries.count());
      }
    }
  }

  private static InodeSecurityCalls mount(boolean readOnly, boolean fail, AtomicInteger calls) {
    return new InodeSecurityCalls() {
      @Override
      public boolean readOnlyFilesystem(Path held) throws StorageIoException {
        assertTrue(held.toString().matches("/proc/self/fd/[1-9][0-9]*"));
        calls.incrementAndGet();
        if (fail) throw new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
        return readOnly;
      }

      @Override
      public byte[] accessAcl(Path held, int maximumBytes) {
        throw new AssertionError("not an ACL probe");
      }

      @Override
      public long effectiveUid() {
        throw new AssertionError("not an identity probe");
      }
    };
  }

  private static void reject(org.junit.jupiter.api.function.Executable action) {
    StorageIoException failure = assertThrows(StorageIoException.class, action);
    assertEquals(StorageIoException.Reason.UNAVAILABLE, failure.reason());
    assertEquals("transfer storage operation failed", failure.getMessage());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
  }
}
