package dev.codex.schubert.nk.api.storage;

import static org.junit.jupiter.api.Assertions.*;

import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.channels.FileChannel;
import java.nio.file.Files;
import java.nio.file.LinkOption;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.nio.file.attribute.PosixFilePermissions;
import java.time.LocalDate;
import java.util.HashSet;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicBoolean;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** Native FD ownership and path replacement tests. NK-SCN-001; SSC-019; PT-SCN-008-F02. */
class OwnedTransferDirectoryTest {
  private static final UUID ID = UUID.fromString("00000000-0000-4000-8000-000000000123");
  private static final LocalDate DATE = LocalDate.of(2026, 9, 8);
  @TempDir Path root;

  @Test
  void bug036CallerMonitorCannotBlockAnyDirectoryOperation() throws Exception {
    FaultCalls calls = new FaultCalls();
    try (var parent = OwnedTransferDirectory.open(calls, root);
        var executor = Executors.newVirtualThreadPerTaskExecutor()) {
      OwnedTransferDirectory child;
      synchronized (parent) {
        child = executor.submit(() -> parent.openDate(DATE)).get(5, TimeUnit.SECONDS);
      }
      synchronized (child) {
        executor
            .submit(
                () -> {
                  assertEquals(3L, child.atPart(ID, OwnedTransferDirectoryTest::write));
                  child.publish(ID);
                  assertArrayEquals(
                      new byte[] {1, 2, 3}, child.atReady(ID, OwnedTransferDirectoryTest::read));
                  child.atPart(ID, OwnedTransferDirectoryTest::write);
                  child.deletePart(ID);
                  child.close();
                  return 0;
                })
            .get(5, TimeUnit.SECONDS);
      }
    }
    assertTrue(calls.live.isEmpty());
  }

  @Test
  void f02RootAndDateReplacementCannotRedirectWritePublishOrCleanup() throws Exception {
    FaultCalls calls = new FaultCalls();
    Path trusted = Files.createDirectory(root.resolve("trusted"));
    Path outside = Files.createDirectory(root.resolve("outside"));
    try (var capability = OwnedTransferDirectory.open(calls, trusted)) {
      Files.move(trusted, root.resolve("anchored"));
      Files.createSymbolicLink(trusted, outside);
      try (var date = capability.openDate(DATE)) {
        Files.move(root.resolve("anchored/20260908"), root.resolve("anchored/retained"));
        Files.createSymbolicLink(root.resolve("anchored/20260908"), outside);
        assertEquals(3L, date.atPart(ID, OwnedTransferDirectoryTest::write));
        Path part = root.resolve("anchored/retained/" + ID + ".part");
        assertEquals(
            PosixFilePermissions.fromString("rw-r-----"), Files.getPosixFilePermissions(part));
        date.publish(ID);
        assertArrayEquals(new byte[] {1, 2, 3}, date.atReady(ID, OwnedTransferDirectoryTest::read));
        assertFalse(Files.exists(part));
        assertArrayEquals(
            new byte[] {1, 2, 3},
            Files.readAllBytes(root.resolve("anchored/retained/" + ID + ".ready")));
        assertEquals(3L, date.atPart(ID, OwnedTransferDirectoryTest::write));
        failure(StorageIoException.Reason.COLLISION, () -> date.publish(ID));
        assertArrayEquals(new byte[] {1, 2, 3}, date.atReady(ID, OwnedTransferDirectoryTest::read));
        date.deletePart(ID);
        assertFalse(Files.exists(part));
        failure(StorageIoException.Reason.MISSING, () -> date.deletePart(ID));
      }
      failure(StorageIoException.Reason.UNAVAILABLE, () -> capability.openDate(DATE));
    }
    assertTrue(calls.live.isEmpty());
    try (var entries = Files.list(outside)) {
      assertEquals(0L, entries.count());
    }
  }

  @Test
  void f02ExistingDateIndependentChildLifetimeAndSafeIoFailures() throws Exception {
    FaultCalls calls = new FaultCalls();
    var parent = OwnedTransferDirectory.open(calls, root);
    var child = parent.openDate(DATE);
    try (var second = parent.openDate(DATE)) {
      assertEquals(3L, second.atPart(ID, OwnedTransferDirectoryTest::write));
      failure(
          StorageIoException.Reason.COLLISION,
          () -> child.atPart(ID, OwnedTransferDirectoryTest::write));
    }
    parent.close();
    parent.close();
    child.publish(ID);
    assertArrayEquals(new byte[] {1, 2, 3}, child.atReady(ID, OwnedTransferDirectoryTest::read));
    failure(
        StorageIoException.Reason.MISSING,
        () -> child.atPart(ID, OwnedTransferDirectoryTest::read));
    failure(
        StorageIoException.Reason.UNAVAILABLE,
        () ->
            child.atReady(
                ID,
                path -> {
                  IOException ex = new IOException("SYNTHETIC_PRIVATE_PATH");
                  ex.addSuppressed(new IOException("SYNTHETIC_PRIVATE_CAUSE"));
                  throw ex;
                }));
    child.close();
    child.close();
    assertTrue(calls.live.isEmpty());
    failure(StorageIoException.Reason.UNAVAILABLE, () -> child.openDate(DATE));
    failure(
        StorageIoException.Reason.UNAVAILABLE,
        () -> child.atPart(ID, OwnedTransferDirectoryTest::read));
    failure(
        StorageIoException.Reason.UNAVAILABLE,
        () -> child.atReady(ID, OwnedTransferDirectoryTest::read));
    failure(StorageIoException.Reason.UNAVAILABLE, () -> child.publish(ID));
    failure(StorageIoException.Reason.UNAVAILABLE, () -> child.deletePart(ID));
  }

  @Test
  void f02RejectsNullRelativeRootDotSegmentsAndInvalidDates() throws Exception {
    FaultCalls calls = new FaultCalls();
    assertThrows(NullPointerException.class, () -> OwnedTransferDirectory.open(null, root));
    assertThrows(NullPointerException.class, () -> OwnedTransferDirectory.open(calls, null));
    for (Path invalid :
        new Path[] {
          Path.of("relative"), Path.of("/"), root.resolve("../other"), root.resolve(".")
        }) {
      assertThrows(
          IllegalArgumentException.class, () -> OwnedTransferDirectory.open(calls, invalid));
      assertTrue(calls.live.isEmpty());
    }
    try (var parent = OwnedTransferDirectory.open(calls, root)) {
      assertThrows(NullPointerException.class, () -> parent.openDate(null));
      assertThrows(IllegalArgumentException.class, () -> parent.openDate(LocalDate.of(0, 1, 1)));
      assertThrows(
          IllegalArgumentException.class, () -> parent.openDate(LocalDate.of(10000, 1, 1)));
      assertThrows(
          NullPointerException.class, () -> parent.atPart(null, OwnedTransferDirectoryTest::read));
      assertThrows(NullPointerException.class, () -> parent.atReady(ID, null));
      assertThrows(NullPointerException.class, () -> parent.publish(null));
      assertThrows(NullPointerException.class, () -> parent.deletePart(null));
      try (var first = parent.openDate(LocalDate.of(1, 1, 1));
          var last = parent.openDate(LocalDate.of(9999, 12, 31))) {
        assertTrue(Files.isDirectory(root.resolve("00010101")));
        assertTrue(Files.isDirectory(root.resolve("99991231")));
        assertEquals(3L, first.atPart(ID, OwnedTransferDirectoryTest::write));
        assertEquals(3L, last.atPart(ID, OwnedTransferDirectoryTest::write));
        assertArrayEquals(
            new byte[] {1, 2, 3}, Files.readAllBytes(root.resolve("00010101/" + ID + ".part")));
        assertArrayEquals(
            new byte[] {1, 2, 3}, Files.readAllBytes(root.resolve("99991231/" + ID + ".part")));
      }
    }
    assertTrue(calls.live.isEmpty());
  }

  @Test
  void f02SymlinkAtAnyRootSegmentAndFailedTraversalReleaseEveryOwnedFd() throws Exception {
    FaultCalls calls = new FaultCalls();
    Path outside = Files.createDirectory(root.resolve("outside"));
    Files.createDirectory(outside.resolve("child"));
    Files.createSymbolicLink(root.resolve("link"), outside);
    failure(
        StorageIoException.Reason.UNAVAILABLE,
        () -> OwnedTransferDirectory.open(calls, root.resolve("link")));
    assertTrue(calls.live.isEmpty());
    failure(
        StorageIoException.Reason.UNAVAILABLE,
        () -> OwnedTransferDirectory.open(calls, root.resolve("link/child")));
    assertTrue(calls.live.isEmpty());
    failure(
        StorageIoException.Reason.MISSING,
        () -> OwnedTransferDirectory.open(calls, root.resolve("missing")));
    assertTrue(calls.live.isEmpty());
    calls.failClose = true;
    failure(StorageIoException.Reason.UNAVAILABLE, () -> OwnedTransferDirectory.open(calls, root));
    assertTrue(calls.live.isEmpty());
    try (var parent = OwnedTransferDirectory.open(calls, root)) {
      Files.write(root.resolve("20260908"), new byte[] {9}, StandardOpenOption.CREATE_NEW);
      failure(StorageIoException.Reason.UNAVAILABLE, () -> parent.openDate(DATE));
      calls.failCreate = true;
      failure(StorageIoException.Reason.UNAVAILABLE, () -> parent.openDate(DATE.plusDays(1)));
      calls.failCreate = false;
      calls.failSync = true;
      failure(StorageIoException.Reason.UNAVAILABLE, () -> parent.openDate(DATE.plusDays(1)));
      calls.failSync = false;
    }
    assertTrue(calls.live.isEmpty());
  }

  @Test
  void f02CloseFailureIsNotRetriedAndSyncFailureKeepsPublishedReady() throws Exception {
    FaultCalls calls = new FaultCalls();
    var parent = OwnedTransferDirectory.open(calls, root);
    try (var child = parent.openDate(DATE)) {
      child.atPart(ID, OwnedTransferDirectoryTest::write);
      calls.failSync = true;
      failure(StorageIoException.Reason.UNAVAILABLE, () -> child.publish(ID));
      assertFalse(Files.exists(root.resolve("20260908/" + ID + ".part")));
      assertArrayEquals(new byte[] {1, 2, 3}, child.atReady(ID, OwnedTransferDirectoryTest::read));
      calls.failSync = false;
    }
    int before = calls.closes;
    calls.failClose = true;
    failure(StorageIoException.Reason.UNAVAILABLE, parent::close);
    parent.close();
    assertEquals(before + 1, calls.closes);
    assertTrue(calls.live.isEmpty());
  }

  @Test
  void f02CloseCannotReuseDescriptorWhileFileCallbackIsInFlight() throws Exception {
    FaultCalls calls = new FaultCalls();
    try (var parent = OwnedTransferDirectory.open(calls, root);
        var executor = Executors.newFixedThreadPool(2)) {
      var child = parent.openDate(DATE);
      CountDownLatch entered = new CountDownLatch(1),
          release = new CountDownLatch(1),
          closing = new CountDownLatch(1);
      AtomicBoolean closed = new AtomicBoolean();
      var file =
          executor.submit(
              () ->
                  child.atPart(
                      ID,
                      path -> {
                        entered.countDown();
                        try {
                          assertTrue(release.await(10, TimeUnit.SECONDS));
                        } catch (InterruptedException ex) {
                          Thread.currentThread().interrupt();
                          throw new IOException("interrupted");
                        }
                        return write(path);
                      }));
      assertTrue(entered.await(10, TimeUnit.SECONDS));
      var close =
          executor.submit(
              () -> {
                closing.countDown();
                child.close();
                closed.set(true);
                return 0;
              });
      assertTrue(closing.await(10, TimeUnit.SECONDS));
      try {
        assertFalse(closed.get());
      } finally {
        release.countDown();
      }
      assertEquals(3L, file.get(10, TimeUnit.SECONDS));
      assertEquals(0, close.get(10, TimeUnit.SECONDS));
      assertTrue(closed.get());
      assertArrayEquals(
          new byte[] {1, 2, 3}, Files.readAllBytes(root.resolve("20260908/" + ID + ".part")));
    }
    assertTrue(calls.live.isEmpty());
  }

  private static long write(Path path) throws IOException {
    try (FileChannel channel =
        FileChannel.open(
            path,
            Set.of(
                StandardOpenOption.WRITE, StandardOpenOption.CREATE_NEW, LinkOption.NOFOLLOW_LINKS),
            PosixFilePermissions.asFileAttribute(PosixFilePermissions.fromString("rw-r-----")))) {
      ByteBuffer bytes = ByteBuffer.wrap(new byte[] {1, 2, 3});
      while (bytes.hasRemaining()) channel.write(bytes);
      channel.force(true);
      return channel.size();
    }
  }

  private static byte[] read(Path path) throws IOException {
    try (FileChannel channel =
        FileChannel.open(path, StandardOpenOption.READ, LinkOption.NOFOLLOW_LINKS)) {
      ByteBuffer bytes = ByteBuffer.allocate(3);
      while (bytes.hasRemaining()) assertTrue(channel.read(bytes) > 0);
      assertEquals(3L, channel.size());
      return bytes.array();
    }
  }

  private static void failure(
      StorageIoException.Reason reason, org.junit.jupiter.api.function.Executable action) {
    StorageIoException ex = assertThrows(StorageIoException.class, action);
    assertEquals(reason, ex.reason());
    assertEquals("transfer storage operation failed", ex.getMessage());
    assertNull(ex.getCause());
    assertEquals(0, ex.getSuppressed().length);
  }

  /**
   * Test fault port still performs actual open/close; tracks every live FD, never guesses numbers.
   */
  private static final class FaultCalls implements DirectoryCalls {
    final DirectoryCalls delegate = LinuxDirectoryCalls.create();
    final Set<Integer> live = new HashSet<>();
    int closes;
    boolean failClose, failCreate, failSync;

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
      return fd;
    }

    @Override
    public void createDirectory(int parent, String name) throws StorageIoException {
      if (failCreate) throw new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
      delegate.createDirectory(parent, name);
    }

    @Override
    public void publish(int directory, String part, String ready) throws StorageIoException {
      delegate.publish(directory, part, ready);
    }

    @Override
    public void unlink(int directory, String name) throws StorageIoException {
      delegate.unlink(directory, name);
    }

    @Override
    public void sync(int directory) throws StorageIoException {
      if (failSync) throw new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
      delegate.sync(directory);
    }

    @Override
    public void close(int directory) throws StorageIoException {
      assertTrue(live.remove(directory));
      closes++;
      delegate.close(directory);
      if (failClose) {
        failClose = false;
        throw new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
      }
    }
  }
}
