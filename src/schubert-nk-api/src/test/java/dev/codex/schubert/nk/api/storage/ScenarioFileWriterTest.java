package dev.codex.schubert.nk.api.storage;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.api.error.CapacityExceededException;
import dev.codex.schubert.nk.protocol.file.LargeResultContent;
import dev.codex.schubert.nk.protocol.file.LargeResultDescriptor;
import dev.codex.schubert.nk.protocol.layout.scenario.ScenarioEntryRecord;
import dev.codex.schubert.nk.protocol.layout.semantic.EntryId;
import dev.codex.schubert.nk.protocol.layout.semantic.EntryType;
import dev.codex.schubert.nk.storage.DirectoryCalls;
import dev.codex.schubert.nk.storage.LinuxDirectoryCalls;
import dev.codex.schubert.nk.storage.OwnedTransferDirectory;
import dev.codex.schubert.nk.storage.StorageIdentity;
import dev.codex.schubert.nk.storage.StorageIoException;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.nio.file.attribute.PosixFileAttributes;
import java.nio.file.attribute.PosixFilePermissions;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.EnumSet;
import java.util.HashSet;
import java.util.HexFormat;
import java.util.List;
import java.util.Locale;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.Executors;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** Real held-inode publication with independent wire/hash/FS/accounting oracle. W07..W10. */
class ScenarioFileWriterTest {
  private static final String FIXTURE_USERS_774733B7 = "users";
  private static final String FIXTURE_20260908_771C782C = "20260908/";
  private static final String FIXTURE_READY_6630F9C3 = ".ready";
  private static final String FIXTURE_20260908_520314A3 = "20260908";
  private static final String FIXTURE_UNIX_MODE_18F40B0C = "unix:mode";
  private static final String FIXTURE_PART_92B0D5FC = ".part";
  private static final String FIXTURE_SYNTHETIC_PRIVATE_PATH_6CBCF6F9 = "SYNTHETIC_PRIVATE_PATH";
  private static final Instant NOW = Instant.parse("2026-09-07T15:00:00Z");
  private static final UUID ID = UUID.fromString("00000000-0000-4000-8000-000000000123");

  @TempDir(factory = TransferRootInspectionTest.Ext4Fixture.class)
  Path fixture;

  @Test
  void w07GoldenFilesHaveJstDateExactDescriptorAndNewOnlySharedGroupPermissions() throws Exception {
    for (int count : new int[] {1, 200, 201, 10000}) {
      Path root = root("count-" + count, FIXTURE_USERS_774733B7);
      StorageIdentity identity = identity(root);
      var capacity = new TransferCapacity(0, 0);
      var calls = new Calls();
      try (var owned = OwnedTransferDirectory.open(calls, root)) {
        var writer = new ScenarioFileWriter(owned, identity, capacity, () -> ID);
        LargeResultDescriptor result = writer.publish(records(count), NOW);
        assertEquals(ID, result.fileId());
        assertEquals(
            FIXTURE_20260908_771C782C + ID + FIXTURE_READY_6630F9C3, result.relativePath());
        assertEquals(4800, result.recordLength());
        assertEquals(count, result.recordCount());
        assertEquals(4800L * count, result.byteLength());
        Path ready = root.resolve(result.relativePath());
        assertEquals(goldenFile(ready, count), result.sha256());
        assertEquals(
            040750,
            Files.getAttribute(
                root.resolve(FIXTURE_20260908_520314A3), FIXTURE_UNIX_MODE_18F40B0C));
        assertEquals(0100640, Files.getAttribute(ready, FIXTURE_UNIX_MODE_18F40B0C));
        assertEquals(
            FIXTURE_USERS_774733B7,
            Files.readAttributes(ready, PosixFileAttributes.class).group().getName());
        assertEquals(
            FIXTURE_USERS_774733B7, identity(root.resolve(FIXTURE_20260908_520314A3)).group());
        assertFalse(
            Files.exists(root.resolve(FIXTURE_20260908_771C782C + ID + FIXTURE_PART_92B0D5FC)));
        usage(capacity, 4800L * count, 1);
      }
      assertTrue(calls.live.isEmpty());
    }
  }

  @Test
  void w07ExistingDateIsValidatedNotRepairedAndDateBoundaryUsesJst() throws Exception {
    Path root = root("existing", FIXTURE_USERS_774733B7);
    StorageIdentity identity = identity(root);
    Path day = Files.createDirectory(root.resolve(FIXTURE_20260908_520314A3));
    Files.setPosixFilePermissions(day, PosixFilePermissions.fromString("rwxr-x---"));
    var capacity = new TransferCapacity(0, 0);
    try (var owned = OwnedTransferDirectory.open(LinuxDirectoryCalls.create(), root)) {
      var writer = new ScenarioFileWriter(owned, identity, capacity, () -> ID);
      reject(
          () ->
              writer.publish(
                  records(1), NOW)); // Existing child still belongs to primary mini group.
      assertNotEquals(FIXTURE_USERS_774733B7, identity(day).group());
      Files.setAttribute(
          day,
          "posix:group",
          day.getFileSystem()
              .getUserPrincipalLookupService()
              .lookupPrincipalByGroupName(FIXTURE_USERS_774733B7));
      Files.setPosixFilePermissions(day, PosixFilePermissions.fromString("rwx------"));
      reject(() -> writer.publish(records(1), NOW));
      assertEquals(040700, Files.getAttribute(day, FIXTURE_UNIX_MODE_18F40B0C));
      Files.setPosixFilePermissions(day, PosixFilePermissions.fromString("rwxr-x---"));
      assertEquals(
          FIXTURE_20260908_771C782C + ID + FIXTURE_READY_6630F9C3,
          writer.publish(records(1), NOW).relativePath());
      assertEquals(
          "20260907/" + ID + FIXTURE_READY_6630F9C3,
          writer.publish(records(1), NOW.minusNanos(1)).relativePath());
      usage(capacity, 9600, 2);
      var wrong =
          new ScenarioFileWriter(
              owned, new StorageIdentity("unknown-owner", FIXTURE_USERS_774733B7), capacity);
      reject(() -> wrong.publish(records(1), NOW));
      usage(capacity, 9600, 2);
    }
  }

  @Test
  void w08PartAndReadyCollisionsRetryThreeTimesWithoutDeletingExistingBytes() throws Exception {
    for (boolean readyCollision : new boolean[] {false, true}) {
      Path root = root("retry-" + readyCollision, currentGroup());
      var capacity = new TransferCapacity(0, 0);
      var calls = new Calls();
      try (var owned = OwnedTransferDirectory.open(calls, root);
          var day = owned.openDate(java.time.LocalDate.of(2026, 9, 8))) {
        for (int i = 0; i < 3; i++) {
          Files.write(
              root.resolve(
                  FIXTURE_20260908_771C782C
                      + id(i)
                      + (readyCollision ? FIXTURE_READY_6630F9C3 : FIXTURE_PART_92B0D5FC)),
              new byte[] {(byte) i},
              StandardOpenOption.CREATE_NEW);
        }
        AtomicInteger ids = new AtomicInteger();
        var writer =
            new ScenarioFileWriter(
                owned,
                identity(root),
                capacity,
                () -> {
                  assertEquals(2, calls.live.size()); // Only root and this test's fixture date.
                  return id(ids.getAndIncrement());
                });
        assertEquals(id(3), writer.publish(records(1), NOW).fileId());
        assertEquals(4, ids.get());
        usage(capacity, 4800, 1);
        for (int i = 0; i < 3; i++) {
          assertArrayEquals(
              new byte[] {(byte) i},
              Files.readAllBytes(
                  root.resolve(
                      FIXTURE_20260908_771C782C
                          + id(i)
                          + (readyCollision ? FIXTURE_READY_6630F9C3 : FIXTURE_PART_92B0D5FC))));
          if (readyCollision)
            assertFalse(
                Files.exists(
                    root.resolve(FIXTURE_20260908_771C782C + id(i) + FIXTURE_PART_92B0D5FC)));
        }
        AtomicInteger exhausted = new AtomicInteger();
        var failure =
            new ScenarioFileWriter(
                owned,
                identity(root),
                capacity,
                () -> {
                  assertEquals(2, calls.live.size());
                  exhausted.incrementAndGet();
                  return id(0);
                });
        reject(() -> failure.publish(records(1), NOW));
        assertEquals(4, exhausted.get());
        usage(capacity, 4800, 1);
        Object mode =
            day.atDirectory(handle -> Files.getAttribute(handle, FIXTURE_UNIX_MODE_18F40B0C));
        assertEquals(040750, mode);
      }
      assertTrue(calls.live.isEmpty());
    }
  }

  @Test
  void w08NullBoundsAndCapacityRejectBeforeCreatingFiles() throws Exception {
    Path root = root("negative", currentGroup());
    StorageIdentity identity = identity(root);
    var capacity = new TransferCapacity(0, 0);
    try (var owned = OwnedTransferDirectory.open(LinuxDirectoryCalls.create(), root)) {
      assertThrows(
          NullPointerException.class, () -> new ScenarioFileWriter(null, identity, capacity));
      assertThrows(NullPointerException.class, () -> new ScenarioFileWriter(owned, null, capacity));
      assertThrows(NullPointerException.class, () -> new ScenarioFileWriter(owned, identity, null));
      assertThrows(
          NullPointerException.class,
          () -> new ScenarioFileWriter(owned, identity, capacity, null));
      assertThrows(
          NullPointerException.class,
          () -> new ScenarioFileWriter(owned, identity, capacity, () -> ID, null));
      var writer = new ScenarioFileWriter(owned, identity, capacity);
      assertThrows(NullPointerException.class, () -> writer.publish(null, NOW));
      assertThrows(NullPointerException.class, () -> writer.publish(records(1), null));
      assertThrows(IllegalArgumentException.class, () -> writer.publish(List.of(), NOW));
      for (Instant time :
          List.of(Instant.parse("0000-01-01T00:00:00Z"), Instant.parse("+10000-01-01T00:00:00Z"))) {
        assertThrows(IllegalArgumentException.class, () -> writer.publish(records(1), time));
      }
      assertThrows(
          java.time.DateTimeException.class, () -> writer.publish(records(1), Instant.MAX));
      var brokenIds = new ScenarioFileWriter(owned, identity, capacity, () -> null);
      assertThrows(NullPointerException.class, () -> brokenIds.publish(records(1), NOW));
      usage(capacity, 0, 0);
      var full = new ScenarioFileWriter(owned, identity, new TransferCapacity(0, 9000));
      assertThrows(CapacityExceededException.class, () -> full.publish(records(1), NOW));
      try (var entries = Files.list(root)) {
        assertEquals(0, entries.count());
      }
      var io = new HeldTransferFileIo(identity);
      assertThrows(NullPointerException.class, () -> new HeldTransferFileIo(null));
      assertThrows(NullPointerException.class, () -> io.initializeDirectory(null));
      assertThrows(
          NullPointerException.class,
          () -> io.writePart(null, new ScenarioRecordStream(records(1))));
      assertThrows(NullPointerException.class, () -> io.writePart(root, null));
      assertThrows(
          NullPointerException.class,
          () -> io.verify(null, new LargeResultContent(1, 4800, "0".repeat(64))));
      assertThrows(NullPointerException.class, () -> io.verify(root, null));
    }
  }

  @Test
  void w09PrepublicationFailuresCleanOnlyOwnedPartAndReleaseReservation() throws Exception {
    for (Fault fault :
        List.of(
            Fault.DIR_INIT,
            Fault.DIR_INIT_CLOSE,
            Fault.CREATE,
            Fault.WRITE_IO,
            Fault.WRITE_RUNTIME,
            Fault.WRITE_NULL,
            Fault.WRITE_SECURITY,
            Fault.SECURITY_CLOSE,
            Fault.PART_HASH,
            Fault.FILE_CLOSE,
            Fault.PUBLISH)) {
      Path root = root("before-" + fault, currentGroup());
      StorageIdentity identity = identity(root);
      var calls = new Calls(fault);
      var capacity = new TransferCapacity(0, 0);
      try (var owned = OwnedTransferDirectory.open(calls, root)) {
        var writer =
            new ScenarioFileWriter(
                owned, identity, capacity, () -> ID, new FaultIo(identity, fault));
        reject(() -> writer.publish(records(1), NOW));
        usage(capacity, 0, 0);
        assertFalse(
            Files.exists(root.resolve(FIXTURE_20260908_771C782C + ID + FIXTURE_PART_92B0D5FC)));
        assertFalse(
            Files.exists(root.resolve(FIXTURE_20260908_771C782C + ID + FIXTURE_READY_6630F9C3)));
      }
      assertTrue(calls.live.isEmpty(), fault.name());
    }
  }

  @Test
  void w09UnconfirmedCleanupAndPublishedFailuresRetainFullQuotaAndNeverDeleteReady()
      throws Exception {
    for (Fault fault :
        List.of(
            Fault.CLEANUP,
            Fault.SYNC_AFTER_PUBLISH,
            Fault.READY_OPEN,
            Fault.READY_CLOSE,
            Fault.READY_COLLISION,
            Fault.READY_HASH,
            Fault.READY_RUNTIME,
            Fault.DAY_CLOSE)) {
      Path root = root("after-" + fault, currentGroup());
      StorageIdentity identity = identity(root);
      var calls = new Calls(fault);
      var capacity = new TransferCapacity(0, 0);
      AtomicInteger generated = new AtomicInteger();
      try (var owned = OwnedTransferDirectory.open(calls, root)) {
        var writer =
            new ScenarioFileWriter(
                owned,
                identity,
                capacity,
                () -> {
                  generated.incrementAndGet();
                  return ID;
                },
                new FaultIo(identity, fault));
        reject(() -> writer.publish(records(1), NOW));
        assertEquals(1, generated.get());
        usage(capacity, 4800, 1);
        boolean part = fault == Fault.CLEANUP;
        assertEquals(
            part,
            Files.exists(root.resolve(FIXTURE_20260908_771C782C + ID + FIXTURE_PART_92B0D5FC)));
        assertEquals(
            !part,
            Files.exists(root.resolve(FIXTURE_20260908_771C782C + ID + FIXTURE_READY_6630F9C3)));
        if (part)
          assertEquals(
              0, Files.size(root.resolve(FIXTURE_20260908_771C782C + ID + FIXTURE_PART_92B0D5FC)));
        else
          assertEquals(
              4800,
              Files.size(root.resolve(FIXTURE_20260908_771C782C + ID + FIXTURE_READY_6630F9C3)));
      }
      assertTrue(calls.live.isEmpty(), fault.name());
    }
  }

  @Test
  void w10ConcurrentDefaultCsprngPublishersHaveDistinctFilesAndExactSharedAccounting()
      throws Exception {
    Path root = root("parallel", currentGroup());
    var capacity = new TransferCapacity(0, 0);
    var calls = new Calls();
    try (var owned = OwnedTransferDirectory.open(calls, root);
        var executor = Executors.newFixedThreadPool(16)) {
      var writer = new ScenarioFileWriter(owned, identity(root), capacity);
      var tasks = new ArrayList<java.util.concurrent.Callable<LargeResultDescriptor>>();
      for (int i = 0; i < 100; i++) tasks.add(() -> writer.publish(records(1), NOW));
      Set<UUID> ids = new HashSet<>();
      for (var result : executor.invokeAll(tasks)) {
        LargeResultDescriptor descriptor = result.get();
        assertTrue(ids.add(descriptor.fileId()));
        assertEquals(4, descriptor.fileId().version());
        assertEquals(2, descriptor.fileId().variant());
        assertEquals(goldenFile(root.resolve(descriptor.relativePath()), 1), descriptor.sha256());
      }
      assertEquals(100, ids.size());
      usage(capacity, 480000, 100);
      try (var entries = Files.list(root.resolve(FIXTURE_20260908_520314A3))) {
        assertEquals(100, entries.count());
      }
    }
    assertTrue(calls.live.isEmpty());
  }

  private Path root(String name, String group) throws IOException {
    Path result = Files.createDirectory(fixture.resolve(name));
    Files.setAttribute(
        result,
        "posix:group",
        result.getFileSystem().getUserPrincipalLookupService().lookupPrincipalByGroupName(group));
    Files.setPosixFilePermissions(result, PosixFilePermissions.fromString("rwxr-x---"));
    return result;
  }

  private String currentGroup() throws IOException {
    return identity(fixture).group();
  }

  private static StorageIdentity identity(Path path) throws IOException {
    var attrs = Files.readAttributes(path, PosixFileAttributes.class);
    return new StorageIdentity(attrs.owner().getName(), attrs.group().getName());
  }

  private static UUID id(int index) {
    return new UUID(0x4000, 0x8000000000000000L + index);
  }

  private static void usage(TransferCapacity capacity, long bytes, long files) {
    assertEquals(bytes, capacity.snapshot().bytes());
    assertEquals(files, capacity.snapshot().files());
  }

  private static void reject(org.junit.jupiter.api.function.Executable action) {
    StorageIoException failure = assertThrows(StorageIoException.class, action);
    assertEquals(StorageIoException.Reason.UNAVAILABLE, failure.reason());
    assertEquals("transfer storage operation failed", failure.getMessage());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
  }

  private static List<ScenarioEntryRecord> records(int count) {
    var result = new ArrayList<ScenarioEntryRecord>();
    for (int i = 0; i < count; i++)
      result.add(
          new ScenarioEntryRecord(
              new EntryId(71 + i),
              i + 1,
              42 + i,
              EntryType.NARRATION,
              Optional.empty(),
              "本文 " + i,
              0,
              Optional.empty(),
              Optional.empty()));
    return result;
  }

  private static String goldenFile(Path file, int count) throws Exception {
    MessageDigest digest = MessageDigest.getInstance("SHA-256");
    try (var input = Files.newInputStream(file)) {
      for (int i = 0; i < count; i++) {
        byte[] golden = new byte[4800];
        Arrays.fill(golden, (byte) ' ');
        put(golden, 0, String.format(Locale.ROOT, "%012d", 71 + i));
        put(golden, 12, String.format(Locale.ROOT, "%06d", i + 1));
        put(golden, 18, String.format(Locale.ROOT, "%08d", 42 + i));
        put(golden, 26, "narration");
        put(golden, 164, "本文 " + i);
        put(golden, 4260, "000");
        assertArrayEquals(golden, input.readNBytes(4800));
        digest.update(golden);
      }
      assertEquals(-1, input.read());
    }
    return HexFormat.of().formatHex(digest.digest());
  }

  private static void put(byte[] target, int offset, String value) {
    byte[] bytes = value.getBytes(java.nio.charset.StandardCharsets.UTF_8);
    System.arraycopy(bytes, 0, target, offset, bytes.length);
  }

  enum Fault {
    DIR_INIT,
    DIR_INIT_CLOSE,
    CREATE,
    WRITE_IO,
    WRITE_RUNTIME,
    WRITE_NULL,
    WRITE_SECURITY,
    SECURITY_CLOSE,
    PART_HASH,
    FILE_CLOSE,
    PUBLISH,
    CLEANUP,
    SYNC_AFTER_PUBLISH,
    READY_OPEN,
    READY_CLOSE,
    READY_COLLISION,
    READY_HASH,
    READY_RUNTIME,
    DAY_CLOSE
  }

  private static final class FaultIo implements TransferFileIo {
    final HeldTransferFileIo actual;
    final Fault fault;

    FaultIo(StorageIdentity identity, Fault fault) {
      actual = new HeldTransferFileIo(identity);
      this.fault = fault;
    }

    @Override
    public void initializeDirectory(Path handle) throws IOException {
      if (fault == Fault.DIR_INIT || fault == Fault.DIR_INIT_CLOSE)
        throw new IOException(FIXTURE_SYNTHETIC_PRIVATE_PATH_6CBCF6F9);
      actual.initializeDirectory(handle);
    }

    @Override
    public LargeResultContent writePart(Path handle, ScenarioRecordStream records)
        throws IOException, NoSuchAlgorithmException {
      if (fault == Fault.WRITE_IO || fault == Fault.CLEANUP)
        throw new IOException(FIXTURE_SYNTHETIC_PRIVATE_PATH_6CBCF6F9);
      if (fault == Fault.WRITE_RUNTIME)
        throw new IllegalStateException(FIXTURE_SYNTHETIC_PRIVATE_PATH_6CBCF6F9);
      if (fault == Fault.WRITE_NULL) return null;
      if (fault == Fault.WRITE_SECURITY || fault == Fault.SECURITY_CLOSE)
        throw new NoSuchAlgorithmException(FIXTURE_SYNTHETIC_PRIVATE_PATH_6CBCF6F9);
      var content = actual.writePart(handle, records);
      if (fault == Fault.PART_HASH) {
        Files.write(handle, new byte[] {'9'}, StandardOpenOption.WRITE);
        actual.verify(handle, content);
      }
      return content;
    }

    @Override
    public void verify(Path handle, LargeResultContent content)
        throws IOException, NoSuchAlgorithmException {
      if (fault == Fault.READY_RUNTIME)
        throw new IllegalStateException(FIXTURE_SYNTHETIC_PRIVATE_PATH_6CBCF6F9);
      actual.verify(handle, content);
    }
  }

  private static final class Calls implements DirectoryCalls {
    final DirectoryCalls actual = LinuxDirectoryCalls.create();
    final Set<Integer> live = ConcurrentHashMap.newKeySet();
    final Set<Integer> parts = ConcurrentHashMap.newKeySet();
    final Set<Integer> entries = ConcurrentHashMap.newKeySet();
    final Set<Integer> dates = ConcurrentHashMap.newKeySet();
    final Set<Fault> faults;
    volatile boolean published;

    Calls(Fault... faults) {
      this.faults =
          faults.length == 0 ? EnumSet.noneOf(Fault.class) : EnumSet.copyOf(List.of(faults));
    }

    int own(int fd) {
      assertTrue(live.add(fd));
      return fd;
    }

    @Override
    public int openRoot() throws StorageIoException {
      return own(actual.openRoot());
    }

    @Override
    public int openDirectory(int parent, String name) throws StorageIoException {
      int fd = own(actual.openDirectory(parent, name));
      if (name.matches("[0-9]{8}")) dates.add(fd);
      return fd;
    }

    @Override
    public int openEntry(int parent, String name) throws StorageIoException {
      if (faults.contains(Fault.READY_OPEN))
        throw new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
      if (faults.contains(Fault.READY_COLLISION))
        throw new StorageIoException(StorageIoException.Reason.COLLISION);
      int fd = own(actual.openEntry(parent, name));
      entries.add(fd);
      return fd;
    }

    @Override
    public int createFile(int parent, String name) throws StorageIoException {
      if (faults.contains(Fault.CREATE))
        throw new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
      int fd = own(actual.createFile(parent, name));
      parts.add(fd);
      return fd;
    }

    @Override
    public void createDirectory(int parent, String name) throws StorageIoException {
      actual.createDirectory(parent, name);
    }

    @Override
    public void publish(int directory, String part, String ready) throws StorageIoException {
      if (faults.contains(Fault.PUBLISH))
        throw new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
      actual.publish(directory, part, ready);
      published = true;
      if (faults.contains(Fault.READY_HASH)) {
        try {
          Files.write(
              Path.of("/proc/self/fd", Integer.toString(directory), ready),
              new byte[] {'9'},
              StandardOpenOption.WRITE);
        } catch (IOException failure) {
          throw new AssertionError("fault fixture failed", failure);
        }
      }
    }

    @Override
    public void unlink(int directory, String name) throws StorageIoException {
      if (faults.contains(Fault.CLEANUP))
        throw new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
      actual.unlink(directory, name);
    }

    @Override
    public void sync(int directory) throws StorageIoException {
      if (published && faults.contains(Fault.SYNC_AFTER_PUBLISH))
        throw new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
      actual.sync(directory);
    }

    @Override
    public void close(int fd) throws StorageIoException {
      assertTrue(live.remove(fd));
      boolean part = parts.remove(fd);
      boolean entry = entries.remove(fd);
      boolean date = dates.remove(fd);
      actual.close(fd);
      if ((part && (faults.contains(Fault.FILE_CLOSE) || faults.contains(Fault.SECURITY_CLOSE)))
          || (date && (faults.contains(Fault.DAY_CLOSE) || faults.contains(Fault.DIR_INIT_CLOSE)))
          || (entry && faults.contains(Fault.READY_CLOSE)))
        throw new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
    }
  }
}
