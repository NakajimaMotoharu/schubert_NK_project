package dev.codex.schubert.nk.api.storage;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.storage.DirectoryCalls;
import dev.codex.schubert.nk.storage.LinuxDirectoryCalls;
import dev.codex.schubert.nk.storage.OwnedTransferDirectory;
import dev.codex.schubert.nk.storage.StorageIdentity;
import dev.codex.schubert.nk.storage.StorageIoException;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.NoSuchFileException;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.nio.file.attribute.PosixFilePermissions;
import java.security.NoSuchAlgorithmException;
import java.time.Instant;
import java.time.LocalDate;
import java.time.ZoneId;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import java.util.UUID;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** Exclusive diagnostic ownership and failure postconditions on real ext4; P01..P03. */
class TransferStartupProbeTest {
  private static final UUID ID = UUID.fromString("00000000-0000-4000-8000-000000000001");
  private static final Instant NOW = Instant.parse("2026-09-07T15:00:00Z");

  @TempDir(factory = TransferRootInspectionTest.Ext4Fixture.class)
  Path fixture;

  @Test
  void p01ColdAndExistingDateUseActualPatternsGroupsNoReplaceAndLeaveOnlyEmptyDates()
      throws Exception {
    Path root = root("normal");
    var identity = identity(root);
    var calls = new Calls(root, Fault.NONE);
    try (var held = OwnedTransferDirectory.open(calls, root)) {
      var probe = new TransferStartupProbe(held, identity);
      probe.verify(NOW.minusNanos(1));
      probe.verify(NOW);
      probe.verify(NOW.plusSeconds(1));
      assertEquals(6, calls.creates);
      assertEquals(6, calls.publishes);
      assertEquals(3, calls.collisions);
      assertEquals(3, calls.unlinks);
      assertEquals(10, calls.syncs); // Two fresh dates * 2, three publication+cleanup pairs.
      assertEquals(1, calls.live.size());
      for (String name : calls.createdNames) {
        UUID id = UUID.fromString(name.substring(0, 36));
        assertEquals(4, id.version());
        assertEquals(2, id.variant());
      }
      for (String date : new String[] {"20260907", "20260908"}) {
        Path day = root.resolve(date);
        assertEquals(040750, Files.getAttribute(day, "unix:mode"));
        assertEquals(
            "users",
            Files.readAttributes(day, java.nio.file.attribute.PosixFileAttributes.class)
                .group()
                .getName());
        try (var names = Files.list(day)) {
          assertEquals(0, names.count());
        }
      }
      assertEquals(0, new TransferUsageScanner().scan(held, identity).files());
    }
    assertTrue(calls.live.isEmpty());
    noArtifactHandles(root);
  }

  @Test
  void p02NullInvalidDateClosedAndWrongAttributesNeverRepairConfiguredRoots() throws Exception {
    Path root = root("contracts");
    var identity = identity(root);
    var calls = new Calls(root, Fault.NONE);
    var held = OwnedTransferDirectory.open(calls, root);
    var io = new HeldProbeFileIo(identity);
    try (held) {
      assertThrows(NullPointerException.class, () -> new TransferStartupProbe(null, identity));
      assertThrows(NullPointerException.class, () -> new TransferStartupProbe(held, null));
      assertThrows(
          NullPointerException.class, () -> new TransferStartupProbe(held, identity, null, io));
      assertThrows(
          NullPointerException.class,
          () -> new TransferStartupProbe(held, identity, () -> ID, null));
      assertThrows(
          NullPointerException.class, () -> new TransferStartupProbe(held, null, () -> ID, io));
      assertThrows(
          NullPointerException.class, () -> new TransferStartupProbe(null, identity, () -> ID, io));
      var probe = new TransferStartupProbe(held, identity, () -> ID, io);
      assertThrows(NullPointerException.class, () -> probe.verify(null));
      assertThrows(
          NullPointerException.class,
          () -> new TransferStartupProbe(held, identity, () -> null, io).verify(NOW));
      for (int year : new int[] {0, 10000}) {
        Instant invalid =
            LocalDate.of(year, 1, 1).atStartOfDay(ZoneId.of("Asia/Tokyo")).toInstant();
        assertThrows(IllegalArgumentException.class, () -> probe.verify(invalid));
      }
      assertThrows(java.time.DateTimeException.class, () -> probe.verify(Instant.MAX));
      assertThrows(NullPointerException.class, () -> new HeldProbeFileIo(null));
      assertThrows(NullPointerException.class, () -> io.initializeDirectory(null));
      assertThrows(NullPointerException.class, () -> io.write(null, false));
      assertThrows(NullPointerException.class, () -> io.verify(null, false));
      reject(
          () ->
              new TransferStartupProbe(held, new StorageIdentity("wrong-owner", "users"))
                  .verify(NOW));
      reject(
          () ->
              new TransferStartupProbe(held, new StorageIdentity(identity.owner(), "wrong-group"))
                  .verify(NOW));
      mode(root, "rwx------");
      reject(() -> probe.verify(NOW));
      assertEquals(040700, Files.getAttribute(root, "unix:mode"));
      mode(root, "rwxr-x---");
      Path day = day(root);
      mode(day, "rwx------");
      reject(() -> probe.verify(NOW));
      assertEquals(040700, Files.getAttribute(day, "unix:mode"));
      mode(day, "rwxr-x---");
      assertEquals(0, calls.creates);
    }
    reject(() -> new TransferStartupProbe(held, identity).verify(NOW));
    assertTrue(calls.live.isEmpty());
  }

  @Test
  void p02ExistingPartReadyAndUnexpectedSecondPartAreNeverDeletedAsProbeOwnership()
      throws Exception {
    for (String suffix : new String[] {"part", "ready"}) {
      Path root = root("existing-" + suffix);
      Path day = day(root);
      Path existing = day.resolve(ID + "." + suffix);
      Files.write(existing, new byte[] {9}, StandardOpenOption.CREATE_NEW);
      mode(existing, "rw-r-----");
      var calls = new Calls(root, Fault.NONE);
      var identity = identity(root);
      try (var held = OwnedTransferDirectory.open(calls, root)) {
        reject(
            () ->
                new TransferStartupProbe(held, identity, () -> ID, new HeldProbeFileIo(identity))
                    .verify(NOW));
        assertArrayEquals(new byte[] {9}, Files.readAllBytes(existing));
        try (var names = Files.list(day)) {
          assertEquals(1, names.count());
        }
      }
      assertTrue(calls.live.isEmpty());
      noArtifactHandles(root);
    }
    Path root = root("foreign-second");
    Path day = day(root);
    var identity = identity(root);
    var calls = new Calls(root, Fault.FOREIGN_SECOND_PART);
    try (var held = OwnedTransferDirectory.open(calls, root)) {
      reject(
          () ->
              new TransferStartupProbe(held, identity, () -> ID, new HeldProbeFileIo(identity))
                  .verify(NOW));
      assertArrayEquals(new byte[] {9}, Files.readAllBytes(day.resolve(ID + ".part")));
      assertFalse(Files.exists(day.resolve(ID + ".ready")));
    }
    assertTrue(calls.live.isEmpty());
  }

  @Test
  void p03CreateWritePublishVerifyAndCloseFaultsFailEvenWhenOwnedFilesCanBeCleaned()
      throws Exception {
    for (Fault fault :
        new Fault[] {
          Fault.CREATE_FIRST,
          Fault.CREATE_SECOND,
          Fault.WRITE_FIRST,
          Fault.WRITE_SECOND,
          Fault.WRITE_SECURITY,
          Fault.WRITE_RUNTIME,
          Fault.CLOSE_FIRST,
          Fault.CLOSE_SECOND,
          Fault.PUBLISH_FIRST,
          Fault.PUBLISH_SECOND,
          Fault.READY_OPEN,
          Fault.READY_CLOSE,
          Fault.PART_HASH,
          Fault.UNLINK_AFTER,
          Fault.READY_MISSING,
          Fault.CLEANUP_SYNC,
          Fault.DAY_CLOSE
        }) {
      Path root = root(fault.name());
      Path day = day(root);
      var identity = identity(root);
      var calls = new Calls(root, fault);
      var io = new FaultIo(identity, day, fault);
      try (var held = OwnedTransferDirectory.open(calls, root)) {
        reject(() -> new TransferStartupProbe(held, identity, () -> ID, io).verify(NOW));
        assertEquals(1, calls.live.size(), fault.name());
        try (var names = Files.list(day)) {
          assertEquals(0, names.count(), fault.name());
        }
      }
      assertTrue(calls.live.isEmpty(), fault.name());
      noArtifactHandles(root);
    }
  }

  @Test
  void p03UncertainPublicationChangedReadyAndCleanupFailuresPreserveOnlyRequiredEvidence()
      throws Exception {
    for (Fault fault :
        new Fault[] {
          Fault.SYNC_PUBLICATION,
          Fault.REPLACE_SECOND,
          Fault.UNLINK,
          Fault.READY_HASH,
          Fault.READY_CLEANUP_CLOSE,
          Fault.READY_DELETE
        }) {
      Path root = root(fault.name());
      Path day = day(root);
      var identity = identity(root);
      var calls = new Calls(root, fault);
      var io = new FaultIo(identity, day, fault);
      try (var held = OwnedTransferDirectory.open(calls, root)) {
        try {
          reject(() -> new TransferStartupProbe(held, identity, () -> ID, io).verify(NOW));
        } finally {
          mode(day, "rwxr-x---");
        }
        assertEquals(1, calls.live.size(), fault.name());
        boolean part = fault == Fault.UNLINK;
        Path remaining = day.resolve(ID + (part ? ".part" : ".ready"));
        byte[] expected = pattern(part || fault == Fault.REPLACE_SECOND);
        if (fault == Fault.READY_HASH) expected[0] = 'X';
        assertArrayEquals(expected, Files.readAllBytes(remaining), fault.name());
        try (var names = Files.list(day)) {
          assertEquals(1, names.count(), fault.name());
        }
      }
      assertTrue(calls.live.isEmpty(), fault.name());
      noArtifactHandles(root);
    }
  }

  @Test
  void p03NewDateInitializationAndSyncFailureCannotBecomeSuccessfulReadiness() throws Exception {
    for (Fault fault : new Fault[] {Fault.INIT_DIRECTORY, Fault.ROOT_SYNC, Fault.INIT_SYNC}) {
      Path root = root(fault.name());
      var identity = identity(root);
      var calls = new Calls(root, fault);
      try (var held = OwnedTransferDirectory.open(calls, root)) {
        reject(
            () ->
                new TransferStartupProbe(
                        held,
                        identity,
                        () -> ID,
                        new FaultIo(identity, root.resolve("20260908"), fault))
                    .verify(NOW));
        assertEquals(0, calls.creates);
        assertEquals(1, calls.live.size());
        Path day = root.resolve("20260908");
        assertTrue(Files.isDirectory(day));
        try (var names = Files.list(day)) {
          assertEquals(0, names.count());
        }
      }
      assertTrue(calls.live.isEmpty());
    }
  }

  private Path root(String name) throws IOException {
    Path root = Files.createDirectory(fixture.resolve(name));
    mode(root, "rwxr-x---");
    group(root);
    return root;
  }

  private static Path day(Path root) throws IOException {
    Path result = Files.createDirectory(root.resolve("20260908"));
    mode(result, "rwxr-x---");
    group(result);
    return result;
  }

  private static void mode(Path path, String permissions) throws IOException {
    Files.setPosixFilePermissions(path, PosixFilePermissions.fromString(permissions));
  }

  private static void group(Path path) throws IOException {
    Files.setAttribute(
        path,
        "posix:group",
        path.getFileSystem().getUserPrincipalLookupService().lookupPrincipalByGroupName("users"));
  }

  private static StorageIdentity identity(Path root) throws IOException {
    return new StorageIdentity(Files.getOwner(root).getName(), "users");
  }

  private static byte[] pattern(boolean second) {
    byte[] bytes = new byte[4800];
    Arrays.fill(bytes, (byte) (second ? 0x4e : 0x53));
    return bytes;
  }

  private static void reject(org.junit.jupiter.api.function.Executable operation) {
    StorageIoException failure = assertThrows(StorageIoException.class, operation);
    assertEquals(StorageIoException.Reason.UNAVAILABLE, failure.reason());
    assertEquals("transfer storage operation failed", failure.getMessage());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
  }

  private static void noArtifactHandles(Path root) throws IOException {
    try (var handles = Files.list(Path.of("/proc/self/fd"))) {
      for (Path handle : handles.toList()) {
        try {
          String target = Files.readSymbolicLink(handle).toString();
          assertFalse(
              target.startsWith(root.toString())
                  && (target.contains(".part") || target.contains(".ready")),
              "diagnostic file channel leaked");
        } catch (NoSuchFileException closedDuringEnumeration) {
          /* Only an already closed FD vanished. */
        }
      }
    }
  }

  private enum Fault {
    NONE,
    INIT_DIRECTORY,
    ROOT_SYNC,
    INIT_SYNC,
    CREATE_FIRST,
    CREATE_SECOND,
    FOREIGN_SECOND_PART,
    WRITE_FIRST,
    WRITE_SECOND,
    WRITE_SECURITY,
    WRITE_RUNTIME,
    CLOSE_FIRST,
    CLOSE_SECOND,
    PUBLISH_FIRST,
    PUBLISH_SECOND,
    SYNC_PUBLICATION,
    REPLACE_SECOND,
    READY_OPEN,
    READY_CLOSE,
    READY_HASH,
    PART_HASH,
    UNLINK,
    UNLINK_AFTER,
    READY_CLEANUP_CLOSE,
    READY_DELETE,
    READY_MISSING,
    CLEANUP_SYNC,
    DAY_CLOSE
  }

  private static final class FaultIo implements ProbeFileIo {
    final HeldProbeFileIo delegate;
    final Path day;
    final Fault fault;
    int readyChecks;

    FaultIo(StorageIdentity identity, Path day, Fault fault) {
      delegate = new HeldProbeFileIo(identity);
      this.day = day;
      this.fault = fault;
    }

    @Override
    public void initializeDirectory(Path path) throws IOException {
      if (fault == Fault.INIT_DIRECTORY) throw new IOException("SYNTHETIC_PRIVATE_PATH");
      delegate.initializeDirectory(path);
    }

    @Override
    public void write(Path path, boolean second) throws IOException, NoSuchAlgorithmException {
      if (!second && fault == Fault.WRITE_FIRST || second && fault == Fault.WRITE_SECOND)
        throw new IOException("SYNTHETIC_PRIVATE_PATH");
      if (fault == Fault.WRITE_SECURITY)
        throw new NoSuchAlgorithmException("SYNTHETIC_PRIVATE_PATH");
      if (fault == Fault.WRITE_RUNTIME) throw new IllegalStateException("SYNTHETIC_PRIVATE_PATH");
      delegate.write(path, second);
      assertArrayEquals(pattern(second), Files.readAllBytes(path));
    }

    @Override
    public void verify(Path path, boolean second) throws IOException, NoSuchAlgorithmException {
      if (!second) readyChecks++;
      if (fault == Fault.READY_HASH && !second && readyChecks == 1
          || fault == Fault.PART_HASH && second) {
        byte[] changed = pattern(second);
        changed[0] = 'X';
        Files.write(path, changed, StandardOpenOption.WRITE);
      }
      delegate.verify(path, second);
      if (!second && readyChecks == 2) {
        if (fault == Fault.READY_DELETE) mode(day, "r-xr-x---");
        if (fault == Fault.READY_MISSING) Files.delete(day.resolve(ID + ".ready"));
      }
    }
  }

  private static final class Calls implements DirectoryCalls {
    final DirectoryCalls delegate = LinuxDirectoryCalls.create();
    final Path root;
    final Fault fault;
    final Set<Integer> live = new HashSet<>();
    final Map<Integer, String> kinds = new HashMap<>();
    final List<String> createdNames = new ArrayList<>();
    int creates;
    int publishes;
    int collisions;
    int unlinks;
    int syncs;
    int readyOpens;

    Calls(Path root, Fault fault) {
      this.root = root;
      this.fault = fault;
    }

    private int own(int fd, String kind) {
      assertTrue(live.add(fd));
      kinds.put(fd, kind);
      return fd;
    }

    @Override
    public int openRoot() throws StorageIoException {
      return own(delegate.openRoot(), "O");
    }

    @Override
    public int openDirectory(int parent, String name) throws StorageIoException {
      return own(delegate.openDirectory(parent, name), name.matches("[0-9]{8}") ? "D" : "O");
    }

    @Override
    public void createDirectory(int parent, String name) throws StorageIoException {
      delegate.createDirectory(parent, name);
    }

    @Override
    public int createFile(int parent, String name) throws StorageIoException {
      creates++;
      createdNames.add(name);
      if (creates == 1 && fault == Fault.CREATE_FIRST
          || creates == 2 && fault == Fault.CREATE_SECOND) throw unavailable();
      if (creates == 2 && fault == Fault.FOREIGN_SECOND_PART) {
        try {
          Files.write(
              root.resolve("20260908").resolve(name),
              new byte[] {9},
              StandardOpenOption.CREATE_NEW);
        } catch (IOException failure) {
          throw new AssertionError(failure);
        }
      }
      return own(delegate.createFile(parent, name), "C" + creates);
    }

    @Override
    public int openEntry(int parent, String name) throws StorageIoException {
      String kind = "P";
      if (name.endsWith(".ready")) {
        kind = "R" + (++readyOpens);
        if (readyOpens == 1 && fault == Fault.READY_OPEN) throw unavailable();
      }
      return own(delegate.openEntry(parent, name), kind);
    }

    @Override
    public void publish(int directory, String part, String ready) throws StorageIoException {
      publishes++;
      if (publishes == 1 && fault == Fault.PUBLISH_FIRST
          || publishes == 2 && fault == Fault.PUBLISH_SECOND) throw unavailable();
      if (publishes == 2 && fault == Fault.REPLACE_SECOND) delegate.unlink(directory, ready);
      try {
        delegate.publish(directory, part, ready);
      } catch (StorageIoException failure) {
        if (failure.reason() == StorageIoException.Reason.COLLISION) collisions++;
        throw failure;
      }
    }

    @Override
    public void unlink(int directory, String name) throws StorageIoException {
      unlinks++;
      if (fault == Fault.UNLINK) throw unavailable();
      delegate.unlink(directory, name);
      if (fault == Fault.UNLINK_AFTER) throw unavailable();
    }

    @Override
    public void sync(int directory) throws StorageIoException {
      syncs++;
      delegate.sync(directory);
      if (fault == Fault.SYNC_PUBLICATION && syncs == 1
          || fault == Fault.CLEANUP_SYNC && syncs == 2
          || fault == Fault.ROOT_SYNC && kinds.get(directory).equals("O")
          || fault == Fault.INIT_SYNC && publishes == 0 && kinds.get(directory).equals("D"))
        throw unavailable();
    }

    @Override
    public void close(int fd) throws StorageIoException {
      assertTrue(live.remove(fd));
      String kind = Objects.requireNonNull(kinds.remove(fd));
      delegate.close(fd);
      if (fault == Fault.CLOSE_FIRST && kind.equals("C1")
          || fault == Fault.CLOSE_SECOND && kind.equals("C2")
          || fault == Fault.READY_CLOSE && kind.equals("R1")
          || fault == Fault.READY_CLEANUP_CLOSE && kind.equals("R2")
          || fault == Fault.DAY_CLOSE && kind.equals("D")) throw unavailable();
    }

    private static StorageIoException unavailable() {
      return new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
    }
  }
}
