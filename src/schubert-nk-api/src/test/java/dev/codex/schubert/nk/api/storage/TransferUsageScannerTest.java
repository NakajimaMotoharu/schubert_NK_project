package dev.codex.schubert.nk.api.storage;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.api.error.CapacityExceededException;
import dev.codex.schubert.nk.storage.DirectoryCalls;
import dev.codex.schubert.nk.storage.LinuxDirectoryCalls;
import dev.codex.schubert.nk.storage.OwnedTransferDirectory;
import dev.codex.schubert.nk.storage.StorageIdentity;
import dev.codex.schubert.nk.storage.StorageIoException;
import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.channels.FileChannel;
import java.nio.file.DirectoryIteratorException;
import java.nio.file.DirectoryStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.nio.file.attribute.PosixFileAttributes;
import java.nio.file.attribute.PosixFilePermissions;
import java.util.HashSet;
import java.util.Iterator;
import java.util.Set;
import java.util.UUID;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** Actual ext4 metadata, independent size/count and bounded startup failures. U01..U03. */
class TransferUsageScannerTest {
  @TempDir(factory = TransferRootInspectionTest.Ext4Fixture.class)
  Path fixture;

  @Test
  void u01LiteralSizesAcrossDatesAndReplacedRootInitializeCapacityWithoutWriting()
      throws Exception {
    Path root = directory(fixture.resolve("root"));
    Path first = directory(root.resolve("20260907"));
    Path second = directory(root.resolve("20260908"));
    directory(root.resolve("20260909"));
    file(first, 1, "part", 0);
    file(first, 2, "part", 1);
    file(second, 3, "part", 4799);
    file(second, 4, "ready", 4800);
    file(second, 5, "ready", 48_000_000);
    var calls = new ReadCalls();
    StorageIdentity identity = identity(root);
    try (var held = OwnedTransferDirectory.open(calls, root)) {
      var scanner = new TransferUsageScanner();
      var usage = scanner.scan(held, identity);
      assertEquals(48_009_600, usage.bytes());
      assertEquals(5, usage.files());
      var capacity = new TransferCapacity(usage.bytes(), usage.files());
      assertEquals(48_009_600, capacity.snapshot().bytes());
      assertEquals(5, capacity.snapshot().files());
      assertEquals(TransferCapacity.Level.NORMAL, capacity.snapshot().level());
      Path retained = fixture.resolve("retained");
      Files.move(root, retained);
      Files.createSymbolicLink(root, directory(fixture.resolve("outside")));
      assertEquals(usage, scanner.scan(held, identity));
      assertEquals(1, calls.live.size());
      assertEquals(0, Files.size(retained.resolve("20260907/" + new UUID(0, 1) + ".part")));
    }
    assertTrue(calls.live.isEmpty());
  }

  @Test
  void u01EmptyAnd9000And10000AreCompleteBut10001NeverReturnsPartialCounts() throws Exception {
    Path root = directory(fixture.resolve("root"));
    var calls = new ReadCalls();
    try (var held = OwnedTransferDirectory.open(calls, root)) {
      var scanner = new TransferUsageScanner();
      var identity = identity(root);
      assertEquals(new TransferUsageScanner.Usage(0, 0), scanner.scan(held, identity));
      Path day = directory(root.resolve("20260908"));
      Path nextDay = directory(root.resolve("20260909"));
      for (int index = 1; index <= 10001; index++) {
        file(index <= 9000 ? day : nextDay, index, "part", 0);
        if (index == 9000 || index == 10000) {
          var usage = scanner.scan(held, identity);
          assertEquals(0, usage.bytes());
          assertEquals(index, usage.files());
          var capacity = new TransferCapacity(usage.bytes(), usage.files());
          assertEquals(TransferCapacity.Level.CRITICAL, capacity.snapshot().level());
          assertThrows(CapacityExceededException.class, () -> capacity.reserve(4800));
        }
      }
      reject(() -> scanner.scan(held, identity));
      assertEquals(1, calls.live.size());
      try (var files = Files.walk(root)) {
        assertEquals(10001, files.filter(Files::isRegularFile).count());
      }
    }
    assertTrue(calls.live.isEmpty());
    for (long[] invalid : new long[][] {{0, -1}, {0, 10001}, {-1, 1}, {1, 0}, {48_000_001, 1}}) {
      assertThrows(
          IllegalArgumentException.class,
          () -> new TransferUsageScanner.Usage(invalid[0], invalid[1]));
    }
    assertEquals(480_000_000_000L, new TransferUsageScanner.Usage(480_000_000_000L, 10000).bytes());
  }

  @Test
  void u02NullClosedUnknownDateAndNoncanonicalEntriesAreRejectedWithoutRepair() throws Exception {
    Path root = directory(fixture.resolve("root"));
    var calls = new ReadCalls();
    var held = OwnedTransferDirectory.open(calls, root);
    var identity = identity(root);
    var scanner = new TransferUsageScanner();
    try (held) {
      assertThrows(NullPointerException.class, () -> new TransferUsageScanner(null));
      assertThrows(NullPointerException.class, () -> scanner.scan(null, identity));
      assertThrows(NullPointerException.class, () -> scanner.scan(held, null));
      for (String name :
          new String[] {"unexpected", "2026098", "20260230", "00000101", "20260908+0900"}) {
        Path invalid = directory(root.resolve(name));
        reject(() -> scanner.scan(held, identity));
        assertTrue(Files.isDirectory(invalid));
        Files.delete(invalid);
      }
      Path day = directory(root.resolve("20260908"));
      for (String name :
          new String[] {
            "unknown",
            new UUID(0, 1) + ".PART",
            new UUID(0, 1) + ".part.extra",
            "AAAAAAAA-0000-0000-0000-000000000001.ready"
          }) {
        Path invalid = Files.createFile(day.resolve(name));
        reject(() -> scanner.scan(held, identity));
        assertTrue(Files.exists(invalid));
        Files.delete(invalid);
      }
      assertEquals(1, calls.live.size());
    }
    reject(() -> scanner.scan(held, identity));
    assertTrue(calls.live.isEmpty());
  }

  @Test
  void u02HeldMetadataRejectsWrongModesLinksAndInvalidReadySizeWithoutDeleting() throws Exception {
    Path root = directory(fixture.resolve("root"));
    Path day = directory(root.resolve("20260908"));
    Path ready = file(day, 1, "ready", 4800);
    var calls = new ReadCalls();
    try (var held = OwnedTransferDirectory.open(calls, root)) {
      var scanner = new TransferUsageScanner();
      var identity = identity(root);
      Path hard = fixture.resolve("hard");
      Files.createLink(hard, ready);
      reject(() -> scanner.scan(held, identity));
      assertEquals(2, Files.getAttribute(ready, "unix:nlink"));
      Files.delete(hard);
      for (Path target : new Path[] {root, day, ready}) {
        Files.setPosixFilePermissions(target, PosixFilePermissions.fromString("rwx------"));
        reject(() -> scanner.scan(held, identity));
        assertEquals(
            PosixFilePermissions.fromString("rwx------"), Files.getPosixFilePermissions(target));
        Files.setPosixFilePermissions(
            target,
            PosixFilePermissions.fromString(target.equals(ready) ? "rw-r-----" : "rwxr-x---"));
      }
      Files.write(ready, new byte[] {9});
      reject(() -> scanner.scan(held, identity));
      assertArrayEquals(new byte[] {9}, Files.readAllBytes(ready));
      Path retained = fixture.resolve("retained-file");
      Files.move(ready, retained);
      Files.createSymbolicLink(ready, retained);
      reject(() -> scanner.scan(held, identity));
      assertTrue(Files.isSymbolicLink(ready));
      Files.delete(ready);
      directory(ready);
      reject(() -> scanner.scan(held, identity));
      assertTrue(Files.isDirectory(ready));
      assertEquals(1, calls.live.size());
    }
    assertTrue(calls.live.isEmpty());
  }

  @Test
  void u03EnumerationOpenIteratorCloseAndNativeCloseFaultsNeverReturnPartialUsage()
      throws Exception {
    Path root = directory(fixture.resolve("root"));
    Path day = directory(root.resolve("20260908"));
    file(day, 1, "part", 1);
    var calls = new ReadCalls();
    try (var held = OwnedTransferDirectory.open(calls, root)) {
      var identity = identity(root);
      for (int level : new int[] {1, 2}) {
        for (String kind : new String[] {"OPEN", "ITERATOR", "AFTER_ONE", "CLOSE", "COMPOUND"}) {
          var fault = new FaultEntries(level, kind);
          reject(() -> new TransferUsageScanner(fault).scan(held, identity));
          assertEquals(fault.opened, fault.closed);
          assertEquals(1, calls.live.size());
        }
      }
      calls.failDateClose = true;
      reject(() -> new TransferUsageScanner().scan(held, identity));
      assertEquals(1, calls.live.size());
      var removed = new FaultEntries(2, "REMOVE_ENTRY");
      reject(() -> new TransferUsageScanner(removed).scan(held, identity));
      assertEquals(removed.opened, removed.closed);
      assertFalse(Files.exists(day.resolve(new UUID(0, 1) + ".part")));
      file(day, 1, "part", 1); // Restore only the synthetic file removed by the fault injector.
      assertEquals(
          new TransferUsageScanner.Usage(1, 1), new TransferUsageScanner().scan(held, identity));
    }
    assertTrue(calls.live.isEmpty());
  }

  @Test
  void u03RetainedDateSurvivesReplacementDuringEnumerationWithoutFollowingTheNewSymlink()
      throws Exception {
    Path root = directory(fixture.resolve("root"));
    Path day = directory(root.resolve("20260908"));
    file(day, 1, "part", 1);
    Path outside = directory(fixture.resolve("outside"));
    file(outside, 2, "ready", 4800);
    var calls = new ReadCalls();
    int[] opened = {0};
    var scanner =
        new TransferUsageScanner(
            path -> {
              if (++opened[0] == 2) {
                Files.move(day, fixture.resolve("retained-day"));
                Files.createSymbolicLink(day, outside);
              }
              return Files.newDirectoryStream(path);
            });
    try (var held = OwnedTransferDirectory.open(calls, root)) {
      assertEquals(new TransferUsageScanner.Usage(1, 1), scanner.scan(held, identity(root)));
      assertTrue(Files.isSymbolicLink(day));
      assertEquals(4800, Files.size(outside.resolve(new UUID(0, 2) + ".ready")));
      assertEquals(1, calls.live.size());
    }
    assertTrue(calls.live.isEmpty());
  }

  private static Path directory(Path path) throws IOException {
    return Files.createDirectory(
        path, PosixFilePermissions.asFileAttribute(PosixFilePermissions.fromString("rwxr-x---")));
  }

  private static Path file(Path day, long id, String suffix, long size) throws IOException {
    Path path = day.resolve(new UUID(0, id) + "." + suffix);
    try (var channel =
        FileChannel.open(
            path,
            Set.of(StandardOpenOption.CREATE_NEW, StandardOpenOption.WRITE),
            PosixFilePermissions.asFileAttribute(PosixFilePermissions.fromString("rw-r-----")))) {
      if (size > 0) {
        channel.position(size - 1);
        assertEquals(1, channel.write(ByteBuffer.wrap(new byte[] {0})));
      }
    }
    return path;
  }

  private static StorageIdentity identity(Path root) throws IOException {
    var attrs = Files.readAttributes(root, PosixFileAttributes.class);
    return new StorageIdentity(attrs.owner().getName(), attrs.group().getName());
  }

  private static void reject(org.junit.jupiter.api.function.Executable operation) {
    var error = assertThrows(StorageIoException.class, operation);
    assertEquals(StorageIoException.Reason.UNAVAILABLE, error.reason());
    assertEquals("transfer storage operation failed", error.getMessage());
    assertNull(error.getCause());
    assertEquals(0, error.getSuppressed().length);
  }

  private static final class FaultEntries implements TransferUsageScanner.DirectoryEntries {
    final int target;
    final String kind;
    int calls;
    int opened;
    int closed;

    FaultEntries(int target, String kind) {
      this.target = target;
      this.kind = kind;
    }

    @Override
    public DirectoryStream<Path> open(Path path) throws IOException {
      boolean fail = ++calls == target;
      if (fail && kind.equals("OPEN")) throw new IOException("SYNTHETIC_PRIVATE_PATH");
      var real = Files.newDirectoryStream(path);
      opened++;
      return new DirectoryStream<>() {
        @Override
        public Iterator<Path> iterator() {
          if (fail && (kind.equals("ITERATOR") || kind.equals("COMPOUND")))
            throw new DirectoryIteratorException(new IOException("SYNTHETIC_PRIVATE_PATH"));
          Iterator<Path> delegate = real.iterator();
          if (fail && (kind.equals("AFTER_ONE") || kind.equals("REMOVE_ENTRY"))) {
            return new Iterator<>() {
              int returned;

              @Override
              public boolean hasNext() {
                if (returned > 0 && kind.equals("AFTER_ONE"))
                  throw new DirectoryIteratorException(new IOException("SYNTHETIC_PRIVATE_PATH"));
                return delegate.hasNext();
              }

              @Override
              public Path next() {
                returned++;
                Path entry = delegate.next();
                if (kind.equals("REMOVE_ENTRY")) {
                  try {
                    Files.delete(entry);
                  } catch (IOException failure) {
                    throw new DirectoryIteratorException(failure);
                  }
                }
                return entry;
              }
            };
          }
          return delegate;
        }

        @Override
        public void close() throws IOException {
          real.close();
          closed++;
          if (fail && (kind.equals("CLOSE") || kind.equals("COMPOUND")))
            throw new IOException("SYNTHETIC_PRIVATE_PATH");
        }
      };
    }
  }

  private static final class ReadCalls implements DirectoryCalls {
    final DirectoryCalls delegate = LinuxDirectoryCalls.create();
    final Set<Integer> live = new HashSet<>();
    final Set<Integer> dates = new HashSet<>();
    boolean failDateClose;

    @Override
    public int openRoot() throws StorageIoException {
      int fd = delegate.openRoot();
      assertTrue(live.add(fd));
      return fd;
    }

    @Override
    public int openDirectory(int parent, String name) throws StorageIoException {
      int fd = delegate.openDirectory(parent, name);
      assertTrue(live.add(fd));
      if (name.equals("20260908")) dates.add(fd);
      return fd;
    }

    @Override
    public int openEntry(int parent, String name) throws StorageIoException {
      int fd = delegate.openEntry(parent, name);
      assertTrue(live.add(fd));
      return fd;
    }

    @Override
    public void close(int fd) throws StorageIoException {
      assertTrue(live.remove(fd));
      boolean date = dates.remove(fd);
      delegate.close(fd);
      if (date && failDateClose) {
        failDateClose = false;
        throw new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
      }
    }

    @Override
    public void createDirectory(int parent, String name) {
      throw new AssertionError("scanner mkdir");
    }

    @Override
    public int createFile(int parent, String name) {
      throw new AssertionError("scanner create");
    }

    @Override
    public void publish(int directory, String part, String ready) {
      throw new AssertionError("scanner rename");
    }

    @Override
    public void unlink(int directory, String name) {
      throw new AssertionError("scanner delete");
    }

    @Override
    public void sync(int directory) {
      throw new AssertionError("scanner fsync");
    }
  }
}
