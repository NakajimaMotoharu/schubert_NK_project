package dev.codex.schubert.nk.storage;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assertions.fail;

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
  private static final String ASSET_ENTRY_NAME = "音源 name.ogg";
  private static final String FIXTURE_UNIX_OWNER_GROUP_MODE_NLINK_SIZE_69F67BAF =
      "unix:owner,group,mode,nlink,size";
  private static final String FIXTURE_OUTSIDE_F78EA721 = "outside";
  private static final String FIXTURE_ASSET_9D9381A7 = "asset";
  private static final String FIXTURE_MISSING_4B62D186 = "missing";
  private static final String FIXTURE_LINK_6EFEC986 = "link";
  private static final String FIXTURE_SYNTHETIC_PRIVATE_PATH_6CBCF6F9 = "SYNTHETIC_PRIVATE_PATH";
  private static final String FIXTURE_READY_6630F9C3 = ".ready";
  private static final String FIXTURE_20260908_771C782C = "20260908/";
  private static final String FIXTURE_PART_92B0D5FC = ".part";
  private static final UUID ID = UUID.fromString("00000000-0000-4000-8000-000000000123");
  private static final LocalDate DATE = LocalDate.of(2026, 9, 8);
  @TempDir Path root;

  @Test
  void med018ExistingAssetChildrenAndEntriesRetainReadOnlyInodes() throws Exception {
    Path directory = Files.createDirectory(root.resolve("音楽 folder"));
    Path asset = directory.resolve(ASSET_ENTRY_NAME);
    write(asset);
    Path outside = Files.createDirectory(root.resolve(FIXTURE_OUTSIDE_F78EA721));
    Files.write(outside.resolve(ASSET_ENTRY_NAME), new byte[] {9});
    FaultCalls calls = new FaultCalls();
    calls.readOnly = true;
    var parent = OwnedTransferDirectory.open(calls, root);
    StorageIdentity expected = identity(root);
    try (var child = parent.openExistingChild("音楽 folder")) {
      parent.close();
      assertEquals(1, calls.live.size());
      Path retained = root.resolve("retained");
      Files.move(directory, retained);
      Files.createSymbolicLink(directory, outside);
      assertArrayEquals(
          new byte[] {1, 2, 3},
          child.atExistingEntryHandle(
              ASSET_ENTRY_NAME,
              handle -> {
                assertEquals(2, calls.live.size());
                Files.move(retained.resolve(ASSET_ENTRY_NAME), retained.resolve("saved.ogg"));
                Files.createSymbolicLink(
                    retained.resolve(ASSET_ENTRY_NAME), outside.resolve(ASSET_ENTRY_NAME));
                StorageAttributeGuard.existingFile(
                    Files.readAttributes(handle, FIXTURE_UNIX_OWNER_GROUP_MODE_NLINK_SIZE_69F67BAF),
                    expected,
                    3);
                return readHeld(handle);
              }));
      assertEquals(1, calls.live.size());
      assertArrayEquals(new byte[] {9}, Files.readAllBytes(outside.resolve(ASSET_ENTRY_NAME)));
      assertArrayEquals(new byte[] {1, 2, 3}, Files.readAllBytes(retained.resolve("saved.ogg")));
    } finally {
      parent.close();
    }
    assertTrue(calls.live.isEmpty());
  }

  @Test
  void med019AssetNameNullOpenAndCloseFaultsNeverEscapeOwnership() throws Exception {
    compoundOwnership();
    FaultCalls calls = new FaultCalls();
    calls.readOnly = true;
    var parent = OwnedTransferDirectory.open(calls, root);
    try (parent) {
      assertThrows(NullPointerException.class, () -> parent.openExistingChild(null));
      assertThrows(
          NullPointerException.class,
          () -> parent.atExistingEntryHandle(null, OwnedTransferDirectoryTest::readHeld));
      assertThrows(
          NullPointerException.class,
          () -> parent.atExistingEntryHandle(FIXTURE_ASSET_9D9381A7, null));
      for (String name : new String[] {"", ".", "..", "a/b", "a\0b"}) {
        assertThrows(IllegalArgumentException.class, () -> parent.openExistingChild(name));
        assertThrows(
            IllegalArgumentException.class,
            () -> parent.atExistingEntryHandle(name, OwnedTransferDirectoryTest::readHeld));
      }
      failure(
          StorageIoException.Reason.MISSING,
          () -> parent.openExistingChild(FIXTURE_MISSING_4B62D186));
      failure(
          StorageIoException.Reason.MISSING,
          () ->
              parent.atExistingEntryHandle(
                  FIXTURE_MISSING_4B62D186, p -> fail("missing entry callback")));
      assertFalse(Files.exists(root.resolve(FIXTURE_MISSING_4B62D186)));
      write(root.resolve(FIXTURE_ASSET_9D9381A7));
      failure(
          StorageIoException.Reason.UNAVAILABLE,
          () -> parent.openExistingChild(FIXTURE_ASSET_9D9381A7));
      Files.createSymbolicLink(
          root.resolve(FIXTURE_LINK_6EFEC986), root.resolve(FIXTURE_ASSET_9D9381A7));
      failure(
          StorageIoException.Reason.UNAVAILABLE,
          () -> parent.openExistingChild(FIXTURE_LINK_6EFEC986));
      StorageIdentity expected = identity(root);
      failure(
          StorageIoException.Reason.UNAVAILABLE,
          () ->
              parent.atExistingEntryHandle(
                  FIXTURE_LINK_6EFEC986,
                  p -> {
                    StorageAttributeGuard.existingFile(
                        Files.readAttributes(p, FIXTURE_UNIX_OWNER_GROUP_MODE_NLINK_SIZE_69F67BAF),
                        expected,
                        3);
                    return fail("symlink content read");
                  }));
      for (boolean closeFailure : new boolean[] {false, true}) {
        int before = calls.closes;
        failure(
            StorageIoException.Reason.UNAVAILABLE,
            () ->
                parent.atExistingEntryHandle(
                    FIXTURE_ASSET_9D9381A7,
                    p -> {
                      calls.failClose = closeFailure;
                      throw new IOException(FIXTURE_SYNTHETIC_PRIVATE_PATH_6CBCF6F9);
                    }));
        assertEquals(before + 1, calls.closes);
        assertEquals(1, calls.live.size());
      }
      int before = calls.closes;
      failure(
          StorageIoException.Reason.UNAVAILABLE,
          () ->
              parent.atExistingEntryHandle(
                  FIXTURE_ASSET_9D9381A7,
                  p -> {
                    calls.failClose = true;
                    return readHeld(p);
                  }));
      assertEquals(before + 1, calls.closes);
      assertEquals(1, calls.live.size());
      assertArrayEquals(
          new byte[] {1, 2, 3}, Files.readAllBytes(root.resolve(FIXTURE_ASSET_9D9381A7)));
      assertTrue(Files.isSymbolicLink(root.resolve(FIXTURE_LINK_6EFEC986)));
    }
    failure(
        StorageIoException.Reason.UNAVAILABLE,
        () -> parent.openExistingChild(FIXTURE_ASSET_9D9381A7));
    failure(
        StorageIoException.Reason.UNAVAILABLE,
        () ->
            parent.atExistingEntryHandle(
                FIXTURE_ASSET_9D9381A7, OwnedTransferDirectoryTest::readHeld));
    assertTrue(calls.live.isEmpty());
  }

  @Test
  void rd01ExistingDateRetainsReadOnlyInodeAndOutlivesRootWithoutAnyMutation() throws Exception {
    Path date = Files.createDirectory(root.resolve("20260908"));
    write(date.resolve(ID + FIXTURE_READY_6630F9C3));
    Path outside = Files.createDirectory(root.resolve(FIXTURE_OUTSIDE_F78EA721));
    Files.write(outside.resolve(ID + FIXTURE_READY_6630F9C3), new byte[] {9});
    var before = Files.readAttributes(date, "unix:owner,group,mode,nlink");
    FaultCalls calls = new FaultCalls();
    calls.readOnly = true;
    var parent = OwnedTransferDirectory.open(calls, root);
    try (var child = parent.openExistingDate(DATE)) {
      parent.close();
      assertEquals(1, calls.live.size());
      Files.move(date, root.resolve("retained-date"));
      Files.createSymbolicLink(date, outside);
      assertEquals(
          before, child.atDirectory(p -> Files.readAttributes(p, "unix:owner,group,mode,nlink")));
      assertArrayEquals(
          new byte[] {1, 2, 3}, child.atReadyHandle(ID, OwnedTransferDirectoryTest::readHeld));
      assertArrayEquals(
          new byte[] {9}, Files.readAllBytes(outside.resolve(ID + FIXTURE_READY_6630F9C3)));
      assertTrue(Files.isSymbolicLink(date));
    } finally {
      parent.close();
    }
    assertTrue(calls.live.isEmpty());
  }

  @Test
  void rd01MissingNullInvalidAndNonDirectoryDatesNeverCreateOrRepairAnything() throws Exception {
    FaultCalls calls = new FaultCalls();
    calls.readOnly = true;
    var parent = OwnedTransferDirectory.open(calls, root);
    try (parent) {
      assertThrows(NullPointerException.class, () -> parent.openExistingDate(null));
      for (int year : new int[] {0, 10000}) {
        assertThrows(
            IllegalArgumentException.class,
            () -> parent.openExistingDate(LocalDate.of(year, 1, 1)));
      }
      failure(StorageIoException.Reason.MISSING, () -> parent.openExistingDate(DATE));
      Path date = root.resolve("20260908");
      assertFalse(Files.exists(date));
      Files.write(date, new byte[] {9});
      failure(StorageIoException.Reason.UNAVAILABLE, () -> parent.openExistingDate(DATE));
      assertArrayEquals(new byte[] {9}, Files.readAllBytes(date));
      Files.delete(date);
      Files.createSymbolicLink(date, root);
      failure(StorageIoException.Reason.UNAVAILABLE, () -> parent.openExistingDate(DATE));
      assertTrue(Files.isSymbolicLink(date));
      assertEquals(1, calls.live.size());
    }
    failure(StorageIoException.Reason.UNAVAILABLE, () -> parent.openExistingDate(DATE));
    assertTrue(calls.live.isEmpty());
  }

  @Test
  void w02CreateOwnsInodeBeforeCallbackAndNameReplacementCannotRedirectWrite() throws Exception {
    FaultCalls calls = new FaultCalls();
    try (var parent = OwnedTransferDirectory.open(calls, root);
        var child = parent.openDate(DATE)) {
      Path part = root.resolve(FIXTURE_20260908_771C782C + ID + FIXTURE_PART_92B0D5FC);
      Path retained = root.resolve("retained");
      StorageIdentity expected = identity(root);
      assertEquals(
          Boolean.TRUE,
          child.createPart(
              ID,
              handle -> {
                assertEquals(3, calls.live.size());
                assertEquals(0100640, Files.getAttribute(handle, "unix:mode"));
                assertEquals(0L, Files.getAttribute(handle, "unix:size"));
                Files.move(part, retained);
                Files.write(part, new byte[] {9}, StandardOpenOption.CREATE_NEW);
                Files.setPosixFilePermissions(handle, PosixFilePermissions.fromString("rw-r-----"));
                Files.setAttribute(
                    handle,
                    "posix:group",
                    Files.readAttributes(root, java.nio.file.attribute.PosixFileAttributes.class)
                        .group());
                try (var stream = FileChannel.open(handle, StandardOpenOption.WRITE)) {
                  assertEquals(3, stream.write(ByteBuffer.wrap(new byte[] {1, 2, 3})));
                  stream.force(true);
                }
                StorageAttributeGuard.file(
                    Files.readAttributes(handle, FIXTURE_UNIX_OWNER_GROUP_MODE_NLINK_SIZE_69F67BAF),
                    expected,
                    3);
                return Boolean.TRUE;
              }));
      assertEquals(2, calls.live.size());
      assertArrayEquals(new byte[] {1, 2, 3}, Files.readAllBytes(retained));
      assertArrayEquals(new byte[] {9}, Files.readAllBytes(part));
      AtomicBoolean callback = new AtomicBoolean();
      failure(
          StorageIoException.Reason.COLLISION,
          () -> child.createPart(ID, handle -> callback.getAndSet(true)));
      assertFalse(callback.get());
      assertArrayEquals(new byte[] {9}, Files.readAllBytes(part));
    }
    assertTrue(calls.live.isEmpty());
  }

  @Test
  void w02NullCallbackAndCloseFaultsReleaseFdButNeverDeletePartImplicitly() throws Exception {
    FaultCalls calls = new FaultCalls();
    var parent = OwnedTransferDirectory.open(calls, root);
    try (parent) {
      assertThrows(NullPointerException.class, () -> parent.createPart(null, path -> Boolean.TRUE));
      assertThrows(NullPointerException.class, () -> parent.createPart(ID, null));
      assertThrows(NullPointerException.class, () -> parent.openDate(DATE, null));
      for (int mode = 0; mode < 3; mode++) {
        int fault = mode;
        failure(
            StorageIoException.Reason.UNAVAILABLE,
            () ->
                parent.createPart(
                    ID,
                    handle -> {
                      calls.failClose = fault != 0;
                      if (fault != 1)
                        throw new IOException(FIXTURE_SYNTHETIC_PRIVATE_PATH_6CBCF6F9);
                      return Boolean.TRUE;
                    }));
        assertEquals(1, calls.live.size());
        assertTrue(Files.exists(root.resolve(ID + FIXTURE_PART_92B0D5FC)));
        assertEquals(0L, Files.size(root.resolve(ID + FIXTURE_PART_92B0D5FC)));
        parent.deletePart(ID);
      }
    }
    failure(
        StorageIoException.Reason.UNAVAILABLE, () -> parent.createPart(ID, path -> Boolean.TRUE));
    assertTrue(calls.live.isEmpty());
  }

  @Test
  void a04HeldPartAndReadyInodesSurviveNameReplacementWithDifferentBytes() throws Exception {
    FaultCalls calls = new FaultCalls();
    try (var parent = OwnedTransferDirectory.open(calls, root);
        var child = parent.openDate(DATE)) {
      StorageIdentity identity = identity(root);
      child.atPart(ID, OwnedTransferDirectoryTest::write);
      Path part = root.resolve(FIXTURE_20260908_771C782C + ID + FIXTURE_PART_92B0D5FC);
      assertArrayEquals(
          new byte[] {1, 2, 3},
          child.atPartHandle(
              ID,
              handle -> {
                assertEquals(3, calls.live.size());
                Files.move(part, root.resolve("retained-part"));
                Files.write(part, new byte[] {9}, StandardOpenOption.CREATE_NEW);
                StorageAttributeGuard.file(
                    Files.readAttributes(handle, FIXTURE_UNIX_OWNER_GROUP_MODE_NLINK_SIZE_69F67BAF),
                    identity,
                    3);
                return readHeld(handle);
              }));
      assertEquals(2, calls.live.size());
      assertArrayEquals(new byte[] {9}, Files.readAllBytes(part));
      child.deletePart(ID);
      child.atPart(ID, OwnedTransferDirectoryTest::write);
      child.publish(ID);
      Path ready = root.resolve(FIXTURE_20260908_771C782C + ID + FIXTURE_READY_6630F9C3);
      Path outside =
          Files.write(
              root.resolve(FIXTURE_OUTSIDE_F78EA721),
              new byte[] {8},
              StandardOpenOption.CREATE_NEW);
      assertArrayEquals(
          new byte[] {1, 2, 3},
          child.atReadyHandle(
              ID,
              handle -> {
                Files.move(ready, root.resolve("retained-ready"));
                Files.createSymbolicLink(ready, outside);
                StorageAttributeGuard.file(
                    Files.readAttributes(handle, FIXTURE_UNIX_OWNER_GROUP_MODE_NLINK_SIZE_69F67BAF),
                    identity,
                    3);
                return readHeld(handle);
              }));
      assertEquals(2, calls.live.size());
      assertTrue(Files.isSymbolicLink(ready));
      assertArrayEquals(new byte[] {8}, Files.readAllBytes(outside));
    }
    assertTrue(calls.live.isEmpty());
  }

  @Test
  void a04SymlinkAndHardLinkAreRejectedBeforeOpeningAReadChannel() throws Exception {
    FaultCalls calls = new FaultCalls();
    try (var parent = OwnedTransferDirectory.open(calls, root);
        var child = parent.openDate(DATE)) {
      StorageIdentity identity = identity(root);
      Path outside = root.resolve(FIXTURE_OUTSIDE_F78EA721);
      write(outside);
      Path ready = root.resolve(FIXTURE_20260908_771C782C + ID + FIXTURE_READY_6630F9C3);
      Files.createSymbolicLink(ready, outside);
      AtomicBoolean readAttempted = new AtomicBoolean();
      failure(
          StorageIoException.Reason.UNAVAILABLE,
          () ->
              child.atReadyHandle(
                  ID,
                  handle -> {
                    assertEquals(
                        0120000, ((Integer) Files.getAttribute(handle, "unix:mode")) & 0170000);
                    StorageAttributeGuard.file(
                        Files.readAttributes(
                            handle, FIXTURE_UNIX_OWNER_GROUP_MODE_NLINK_SIZE_69F67BAF),
                        identity,
                        3);
                    readAttempted.set(true);
                    return readHeld(handle);
                  }));
      assertFalse(readAttempted.get());
      Files.createLink(
          root.resolve(FIXTURE_20260908_771C782C + ID + FIXTURE_PART_92B0D5FC), outside);
      failure(
          StorageIoException.Reason.UNAVAILABLE,
          () ->
              child.atPartHandle(
                  ID,
                  handle -> {
                    assertEquals(2, Files.getAttribute(handle, "unix:nlink"));
                    StorageAttributeGuard.file(
                        Files.readAttributes(
                            handle, FIXTURE_UNIX_OWNER_GROUP_MODE_NLINK_SIZE_69F67BAF),
                        identity,
                        3);
                    readAttempted.set(true);
                    return readHeld(handle);
                  }));
      assertFalse(readAttempted.get());
      assertEquals(2, calls.live.size());
      assertArrayEquals(new byte[] {1, 2, 3}, Files.readAllBytes(outside));
    }
    assertTrue(calls.live.isEmpty());
  }

  @Test
  void a04MissingNullCloseAndCompoundFailuresLeaveNoEntryFdOrExceptionPaths() throws Exception {
    FaultCalls calls = new FaultCalls();
    var parent = OwnedTransferDirectory.open(calls, root);
    try (var child = parent.openDate(DATE)) {
      assertThrows(
          NullPointerException.class,
          () -> child.atPartHandle(null, OwnedTransferDirectoryTest::readHeld));
      assertThrows(NullPointerException.class, () -> child.atReadyHandle(ID, null));
      failure(
          StorageIoException.Reason.MISSING,
          () -> child.atReadyHandle(ID, OwnedTransferDirectoryTest::readHeld));
      child.atPart(ID, OwnedTransferDirectoryTest::write);
      failure(
          StorageIoException.Reason.COLLISION,
          () ->
              child.atPartHandle(
                  ID,
                  path -> {
                    throw new java.nio.file.FileAlreadyExistsException(
                        FIXTURE_SYNTHETIC_PRIVATE_PATH_6CBCF6F9);
                  }));
      failure(
          StorageIoException.Reason.UNAVAILABLE,
          () ->
              child.atPartHandle(
                  ID,
                  path -> {
                    calls.failClose = true;
                    throw new java.nio.file.FileAlreadyExistsException(
                        FIXTURE_SYNTHETIC_PRIVATE_PATH_6CBCF6F9);
                  }));
      assertEquals(2, calls.live.size());
      failure(
          StorageIoException.Reason.UNAVAILABLE,
          () ->
              child.atPartHandle(
                  ID,
                  path -> {
                    calls.failClose = true;
                    return readHeld(path);
                  }));
      assertEquals(2, calls.live.size());
      failure(
          StorageIoException.Reason.UNAVAILABLE,
          () ->
              child.atPartHandle(
                  ID,
                  path -> {
                    throw new IOException(FIXTURE_SYNTHETIC_PRIVATE_PATH_6CBCF6F9);
                  }));
      assertEquals(2, calls.live.size());
    } finally {
      parent.close();
    }
    failure(
        StorageIoException.Reason.UNAVAILABLE,
        () -> parent.atPartHandle(ID, OwnedTransferDirectoryTest::readHeld));
    failure(
        StorageIoException.Reason.UNAVAILABLE,
        () -> parent.atReadyHandle(ID, OwnedTransferDirectoryTest::readHeld));
    assertTrue(calls.live.isEmpty());
  }

  private static StorageIdentity identity(Path directory) throws IOException {
    var attrs = Files.readAttributes(directory, java.nio.file.attribute.PosixFileAttributes.class);
    return new StorageIdentity(attrs.owner().getName(), attrs.group().getName());
  }

  /** Intentional follow of kernel-owned O_PATH FD, never a caller-supplied symlink. */
  private static byte[] readHeld(Path handle) throws IOException {
    try (FileChannel channel = FileChannel.open(handle, StandardOpenOption.READ)) {
      ByteBuffer bytes = ByteBuffer.allocate(3);
      while (bytes.hasRemaining()) assertTrue(channel.read(bytes) > 0);
      assertEquals(3L, channel.size());
      return bytes.array();
    }
  }

  @Test
  void bug036CallerMonitorCannotBlockAnyDirectoryOperation() throws Exception {
    FaultCalls calls = new FaultCalls();
    try (var parent = OwnedTransferDirectory.open(calls, root);
        var executor = Executors.newVirtualThreadPerTaskExecutor()) {
      OwnedTransferDirectory child;
      synchronized (parent) {
        child = executor.submit(() -> parent.openDate(DATE)).get(5, TimeUnit.SECONDS);
        assertEquals(
            Boolean.TRUE,
            executor
                .submit(
                    () -> {
                      try (var existing = parent.openExistingDate(DATE)) {
                        return existing.atDirectory(path -> Files.isDirectory(path));
                      }
                    })
                .get(5, TimeUnit.SECONDS));
      }
      synchronized (child) {
        executor
            .submit(
                () -> {
                  assertEquals(3L, child.atPart(ID, OwnedTransferDirectoryTest::write));
                  child.publish(ID);
                  assertArrayEquals(
                      new byte[] {1, 2, 3},
                      child.atReadyHandle(ID, OwnedTransferDirectoryTest::readHeld));
                  assertArrayEquals(
                      new byte[] {1, 2, 3}, child.atReady(ID, OwnedTransferDirectoryTest::read));
                  child.atPart(ID, OwnedTransferDirectoryTest::write);
                  assertArrayEquals(
                      new byte[] {1, 2, 3},
                      child.atPartHandle(ID, OwnedTransferDirectoryTest::readHeld));
                  child.deletePart(ID);
                  assertEquals(Boolean.TRUE, child.createPart(ID, handle -> Boolean.TRUE));
                  child.deletePart(ID);
                  child.sync();
                  child.close();
                  failure(StorageIoException.Reason.UNAVAILABLE, child::sync);
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
    Path outside = Files.createDirectory(root.resolve(FIXTURE_OUTSIDE_F78EA721));
    try (var capability = OwnedTransferDirectory.open(calls, trusted)) {
      Files.move(trusted, root.resolve("anchored"));
      Files.createSymbolicLink(trusted, outside);
      try (var date = capability.openDate(DATE)) {
        Files.move(root.resolve("anchored/20260908"), root.resolve("anchored/retained"));
        Files.createSymbolicLink(root.resolve("anchored/20260908"), outside);
        assertEquals(3L, date.atPart(ID, OwnedTransferDirectoryTest::write));
        Path part = root.resolve("anchored/retained/" + ID + FIXTURE_PART_92B0D5FC);
        assertEquals(
            PosixFilePermissions.fromString("rw-r-----"), Files.getPosixFilePermissions(part));
        date.publish(ID);
        assertArrayEquals(new byte[] {1, 2, 3}, date.atReady(ID, OwnedTransferDirectoryTest::read));
        assertFalse(Files.exists(part));
        assertArrayEquals(
            new byte[] {1, 2, 3},
            Files.readAllBytes(root.resolve("anchored/retained/" + ID + FIXTURE_READY_6630F9C3)));
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
                  IOException ex = new IOException(FIXTURE_SYNTHETIC_PRIVATE_PATH_6CBCF6F9);
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
            new byte[] {1, 2, 3},
            Files.readAllBytes(root.resolve("00010101/" + ID + FIXTURE_PART_92B0D5FC)));
        assertArrayEquals(
            new byte[] {1, 2, 3},
            Files.readAllBytes(root.resolve("99991231/" + ID + FIXTURE_PART_92B0D5FC)));
      }
    }
    assertTrue(calls.live.isEmpty());
  }

  @Test
  void f02SymlinkAtAnyRootSegmentAndFailedTraversalReleaseEveryOwnedFd() throws Exception {
    FaultCalls calls = new FaultCalls();
    Path outside = Files.createDirectory(root.resolve(FIXTURE_OUTSIDE_F78EA721));
    Files.createDirectory(outside.resolve("child"));
    Files.createSymbolicLink(root.resolve(FIXTURE_LINK_6EFEC986), outside);
    failure(
        StorageIoException.Reason.UNAVAILABLE,
        () -> OwnedTransferDirectory.open(calls, root.resolve(FIXTURE_LINK_6EFEC986)));
    assertTrue(calls.live.isEmpty());
    failure(
        StorageIoException.Reason.UNAVAILABLE,
        () -> OwnedTransferDirectory.open(calls, root.resolve("link/child")));
    assertTrue(calls.live.isEmpty());
    failure(
        StorageIoException.Reason.MISSING,
        () -> OwnedTransferDirectory.open(calls, root.resolve(FIXTURE_MISSING_4B62D186)));
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
      assertFalse(
          Files.exists(root.resolve(FIXTURE_20260908_771C782C + ID + FIXTURE_PART_92B0D5FC)));
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
      CountDownLatch entered = new CountDownLatch(1);
      CountDownLatch release = new CountDownLatch(1);
      CountDownLatch closing = new CountDownLatch(1);
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
          new byte[] {1, 2, 3},
          Files.readAllBytes(root.resolve(FIXTURE_20260908_771C782C + ID + FIXTURE_PART_92B0D5FC)));
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
  private void compoundOwnership() throws Exception {
    int sequence = 0;
    for (int scope = 0; scope < 3; scope++)
      for (Throwable primary :
          new Throwable[] {
            new IllegalStateException("public primary"),
            new NullPointerException("public primary"),
            new AssertionError("public primary"),
            new StorageIoException(StorageIoException.Reason.MISSING)
          }) {
        var calls = new FaultCalls();
        Throwable cleanup =
            primary instanceof StorageIoException ? new AssertionError("public cleanup") : primary;
        if (scope == 0) {
          calls.openFailure = primary;
          calls.closeFailure = cleanup;
          assertSame(
              cleanup,
              assertThrows(cleanup.getClass(), () -> OwnedTransferDirectory.open(calls, root)));
          assertEquals(1, calls.closes);
        } else {
          try (var parent = OwnedTransferDirectory.open(calls, root)) {
            int before = calls.closes;
            calls.closeFailure = cleanup;
            if (scope == 1) {
              int sequenceValue = sequence;
              sequence++;
              LocalDate date = DATE.plusDays(sequenceValue);
              assertSame(
                  cleanup,
                  assertThrows(
                      cleanup.getClass(),
                      () ->
                          parent.openDate(
                              date,
                              path -> {
                                raise(primary);
                                return true;
                              })));
            } else {
              int sequenceValue = sequence;
              sequence++;
              String name = "compound-" + sequenceValue;
              write(root.resolve(name));
              assertSame(
                  cleanup,
                  assertThrows(
                      cleanup.getClass(),
                      () ->
                          parent.atExistingEntryHandle(
                              name,
                              path -> {
                                raise(primary);
                                return true;
                              })));
            }
            assertEquals(before + 1, calls.closes);
            assertEquals(1, calls.live.size());
          }
        }
        assertTrue(calls.live.isEmpty());
        assertEquals(primary instanceof StorageIoException ? 0 : 1, cleanup.getSuppressed().length);
        for (Throwable secondary : cleanup.getSuppressed()) {
          failure(
              StorageIoException.Reason.UNAVAILABLE,
              () -> {
                throw secondary;
              });
        }
      }
  }

  private static void raise(Throwable failure) throws StorageIoException {
    if (failure instanceof StorageIoException known) throw known;
    if (failure instanceof RuntimeException unknown) throw unknown;
    throw (Error) failure;
  }

  private static final class FaultCalls implements DirectoryCalls {
    final DirectoryCalls delegate = LinuxDirectoryCalls.create();
    final Set<Integer> live = new HashSet<>();
    int closes;
    boolean failClose;
    boolean failCreate;
    boolean failSync;
    boolean readOnly;
    Throwable openFailure;
    Throwable closeFailure;

    @Override
    public int openRoot() throws StorageIoException {
      int fd = delegate.openRoot();
      assertTrue(live.add(fd));
      return fd;
    }

    @Override
    public int openDirectory(int parent, String name) throws StorageIoException {
      if (openFailure != null) raise(openFailure);
      int fd = delegate.openDirectory(parent, name);
      assertTrue(live.add(fd));
      return fd;
    }

    @Override
    public void createDirectory(int parent, String name) throws StorageIoException {
      assertFalse(readOnly, "reader attempted mkdir");
      if (failCreate) throw new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
      delegate.createDirectory(parent, name);
    }

    @Override
    public int openEntry(int parent, String name) throws StorageIoException {
      int fd = delegate.openEntry(parent, name);
      assertTrue(live.add(fd));
      return fd;
    }

    @Override
    public int createFile(int parent, String name) throws StorageIoException {
      assertFalse(readOnly, "reader attempted create");
      int fd = delegate.createFile(parent, name);
      assertTrue(live.add(fd));
      return fd;
    }

    @Override
    public void publish(int directory, String part, String ready) throws StorageIoException {
      assertFalse(readOnly, "reader attempted rename");
      delegate.publish(directory, part, ready);
    }

    @Override
    public void unlink(int directory, String name) throws StorageIoException {
      assertFalse(readOnly, "reader attempted unlink");
      delegate.unlink(directory, name);
    }

    @Override
    public void sync(int directory) throws StorageIoException {
      assertFalse(readOnly, "reader attempted fsync");
      if (failSync) throw new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
      delegate.sync(directory);
    }

    @Override
    public void close(int directory) throws StorageIoException {
      assertTrue(live.remove(directory));
      closes++;
      delegate.close(directory);
      if (closeFailure != null) {
        Throwable failure = closeFailure;
        closeFailure = null;
        raise(failure);
      }
      if (failClose) {
        failClose = false;
        throw new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
      }
    }
  }
}
