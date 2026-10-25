package dev.codex.schubert.nk.web.storage;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.protocol.file.LargeResultDescriptor;
import dev.codex.schubert.nk.storage.DirectoryCalls;
import dev.codex.schubert.nk.storage.LinuxDirectoryCalls;
import dev.codex.schubert.nk.storage.OwnedTransferDirectory;
import dev.codex.schubert.nk.storage.StorageIdentity;
import dev.codex.schubert.nk.storage.StorageIoException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.attribute.PosixFileAttributes;
import java.nio.file.attribute.PosixFilePermissions;
import java.util.ArrayList;
import java.util.Set;
import java.util.concurrent.Callable;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** Real native inode + read-only channel, independent bytes/attributes; PT-SCN-008-RD05. */
class LargeResultReaderTest {
  @TempDir Path root;

  @Test
  void rd05OneHundredConcurrentReadersHaveIndependentChannelsAndNeverModifyTheSharedReadyFile()
      throws Exception {
    var descriptor = prepare();
    var calls = new ReadOnlyCalls();
    try (var parent = OwnedTransferDirectory.open(calls, root);
        var executor = Executors.newFixedThreadPool(16)) {
      var reader = new LargeResultReader(parent, identity());
      var jobs = new ArrayList<Callable<Integer>>();
      for (int index = 0; index < 100; index++) {
        jobs.add(
            () -> {
              var records = reader.readScenario(descriptor);
              assertEquals(50000, records.getFirst().entryId().value());
              assertEquals("本文", records.getFirst().bodyText());
              return records.size();
            });
      }
      for (var result : executor.invokeAll(jobs, 20, TimeUnit.SECONDS)) {
        assertFalse(result.isCancelled());
        assertEquals(1, result.get());
      }
      assertEquals(1, calls.live.size());
      assertArrayEquals(
          ScenarioFileFixture.golden(1),
          Files.readAllBytes(root.resolve(descriptor.relativePath())));
    }
    assertTrue(calls.live.isEmpty());
  }

  @Test
  void rd05ReadOnlyFileAdapterReturnsVerifiedRecordsWithoutChangingFileOrOwningRoot()
      throws Exception {
    mode(root, "rwxr-x---");
    Path day = Files.createDirectory(root.resolve("20260908"));
    mode(day, "rwxr-x---");
    Path file = day.resolve(ScenarioFileFixture.ID + ".ready");
    var descriptor = ScenarioFileFixture.write(file, 201);
    var before = Files.readAttributes(file, "unix:owner,group,mode,nlink,size,lastModifiedTime");
    var calls = new ReadOnlyCalls();
    try (var parent = OwnedTransferDirectory.open(calls, root)) {
      var reader = new LargeResultReader(parent, identity());
      var records = reader.readScenario(descriptor);
      assertEquals(201, records.size());
      assertEquals(50000, records.getFirst().entryId().value());
      assertEquals(49800, records.getLast().entryId().value());
      assertEquals(201, records.getLast().entrySequence());
      assertEquals("本文", records.getLast().bodyText());
      assertThrows(UnsupportedOperationException.class, records::clear);
      assertEquals(
          before, Files.readAttributes(file, "unix:owner,group,mode,nlink,size,lastModifiedTime"));
      assertEquals(1, calls.live.size());
      assertEquals(201, reader.readScenario(descriptor).size());
    }
    assertTrue(calls.live.isEmpty());
    assertTrue(Files.exists(file));
  }

  @Test
  void rd05NullClosedAndWrongOwnershipModeAndSizeAreDeniedWithoutRepair() throws Exception {
    var descriptor = prepare();
    Path day = root.resolve("20260908");
    Path file = day.resolve(ScenarioFileFixture.ID + ".ready");
    var calls = new ReadOnlyCalls();
    var parent = OwnedTransferDirectory.open(calls, root);
    try (parent) {
      var identity = identity();
      assertThrows(NullPointerException.class, () -> new LargeResultReader(null, identity));
      assertThrows(NullPointerException.class, () -> new LargeResultReader(parent, null));
      var reader = new LargeResultReader(parent, identity);
      assertThrows(NullPointerException.class, () -> reader.readScenario(null));
      failure(
          () ->
              new LargeResultReader(parent, new StorageIdentity("wrong-owner", identity.group()))
                  .readScenario(descriptor));
      failure(
          () ->
              new LargeResultReader(parent, new StorageIdentity(identity.owner(), "wrong-group"))
                  .readScenario(descriptor));
      for (Path target : new Path[] {root, day, file}) {
        mode(target, "rwx------");
        failure(() -> reader.readScenario(descriptor));
        assertEquals(
            PosixFilePermissions.fromString("rwx------"), Files.getPosixFilePermissions(target));
        mode(target, target.equals(file) ? "rw-r-----" : "rwxr-x---");
        assertEquals(1, calls.live.size());
      }
      Files.write(file, new byte[] {9});
      failure(() -> reader.readScenario(descriptor));
      assertArrayEquals(new byte[] {9}, Files.readAllBytes(file));
      var badDate =
          new LargeResultDescriptor(
              ScenarioFileFixture.ID,
              "00000101/" + ScenarioFileFixture.ID + ".ready",
              4800,
              descriptor.sha256(),
              1);
      failure(() -> reader.readScenario(badDate));
    }
    failure(() -> new LargeResultReader(parent, identity()).readScenario(descriptor));
    assertTrue(calls.live.isEmpty());
  }

  @Test
  void rd05SymlinkHardLinkDirectoryMissingAndUnlinkedHeldInodeAreDeniedAndNeverDeleted()
      throws Exception {
    var descriptor = prepare();
    Path day = root.resolve("20260908");
    Path file = day.resolve(ScenarioFileFixture.ID + ".ready");
    var calls = new ReadOnlyCalls();
    try (var parent = OwnedTransferDirectory.open(calls, root)) {
      var reader = new LargeResultReader(parent, identity());
      Path link = root.resolve("linked");
      Files.createLink(link, file);
      failure(() -> reader.readScenario(descriptor));
      assertEquals(2, Files.getAttribute(file, "unix:nlink"));
      Files.delete(link);
      Path retained = root.resolve("retained");
      Files.move(file, retained);
      failure(() -> reader.readScenario(descriptor));
      assertFalse(Files.exists(file));
      Files.createSymbolicLink(file, retained);
      failure(() -> reader.readScenario(descriptor));
      assertTrue(Files.isSymbolicLink(file));
      Files.delete(file);
      Files.createDirectory(file);
      mode(file, "rwxr-x---");
      failure(() -> reader.readScenario(descriptor));
      assertTrue(Files.isDirectory(file));
      Files.delete(file);
      Files.move(retained, file);
      Path savedDay = root.resolve("saved-day");
      Files.move(day, savedDay);
      Files.createSymbolicLink(day, savedDay);
      failure(() -> reader.readScenario(descriptor));
      assertTrue(Files.isSymbolicLink(day));
      Files.delete(day);
      Files.move(savedDay, day);
      assertEquals(1, reader.readScenario(descriptor).size());
      calls.afterEntry =
          () -> {
            try {
              Files.delete(file);
            } catch (java.io.IOException ex) {
              throw new AssertionError(ex);
            }
          };
      failure(() -> reader.readScenario(descriptor));
      assertEquals(1, calls.live.size());
    }
    assertTrue(calls.live.isEmpty());
  }

  @Test
  void rd05BadHashRecordAndNativeCloseFailuresReturnOnlyFixedClassificationAndReleaseFds()
      throws Exception {
    var descriptor = prepare();
    Path file = root.resolve(descriptor.relativePath());
    var calls = new ReadOnlyCalls();
    try (var parent = OwnedTransferDirectory.open(calls, root)) {
      var reader = new LargeResultReader(parent, identity());
      failure(() -> reader.readScenario(ScenarioFileFixture.descriptor(1, "0".repeat(64))));
      byte[] invalid = ScenarioFileFixture.golden(1);
      invalid[4799] = '#';
      Files.write(file, invalid);
      var invalidDescriptor = ScenarioFileFixture.descriptor(1, ScenarioFileFixture.hash(invalid));
      failure(() -> reader.readScenario(invalidDescriptor));
      calls.failEntryClose = true;
      failure(() -> reader.readScenario(invalidDescriptor));
      Files.write(file, ScenarioFileFixture.golden(1));
      calls.failEntryClose = true;
      failure(() -> reader.readScenario(descriptor));
      calls.failDateClose = true;
      failure(() -> reader.readScenario(descriptor));
      assertEquals(1, calls.live.size());
      assertArrayEquals(ScenarioFileFixture.golden(1), Files.readAllBytes(file));
      assertEquals(1, reader.readScenario(descriptor).size());
    }
    assertTrue(calls.live.isEmpty());
  }

  private LargeResultDescriptor prepare() throws Exception {
    mode(root, "rwxr-x---");
    Path day = Files.createDirectory(root.resolve("20260908"));
    mode(day, "rwxr-x---");
    return ScenarioFileFixture.write(day.resolve(ScenarioFileFixture.ID + ".ready"), 1);
  }

  private StorageIdentity identity() throws Exception {
    var attributes = Files.readAttributes(root, PosixFileAttributes.class);
    return new StorageIdentity(attributes.owner().getName(), attributes.group().getName());
  }

  private static void mode(Path path, String permissions) throws Exception {
    Files.setPosixFilePermissions(path, PosixFilePermissions.fromString(permissions));
  }

  private static void failure(org.junit.jupiter.api.function.Executable action) {
    FileIntegrityException failure = assertThrows(FileIntegrityException.class, action);
    assertEquals("FILE_INTEGRITY_MISMATCH", failure.getMessage());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
  }

  private static final class ReadOnlyCalls implements DirectoryCalls {
    final DirectoryCalls delegate = LinuxDirectoryCalls.create();
    final Set<Integer> live = ConcurrentHashMap.newKeySet();
    final Set<Integer> entries = ConcurrentHashMap.newKeySet();
    final Set<Integer> dates = ConcurrentHashMap.newKeySet();
    boolean failEntryClose;
    boolean failDateClose;
    Runnable afterEntry = () -> {};

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
      entries.add(fd);
      afterEntry.run();
      return fd;
    }

    @Override
    public void close(int fd) throws StorageIoException {
      assertTrue(live.remove(fd));
      boolean entry = entries.remove(fd);
      boolean date = dates.remove(fd);
      delegate.close(fd);
      if (entry && failEntryClose || date && failDateClose) {
        failEntryClose = false;
        failDateClose = false;
        throw new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
      }
    }

    @Override
    public void createDirectory(int parent, String name) {
      throw new AssertionError("reader mkdir");
    }

    @Override
    public int createFile(int parent, String name) {
      throw new AssertionError("reader create");
    }

    @Override
    public void publish(int directory, String part, String ready) {
      throw new AssertionError("reader rename");
    }

    @Override
    public void unlink(int directory, String name) {
      throw new AssertionError("reader delete");
    }

    @Override
    public void sync(int directory) {
      throw new AssertionError("reader fsync");
    }
  }
}
