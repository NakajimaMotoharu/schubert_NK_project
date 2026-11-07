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
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.function.Executable;
import org.junit.jupiter.api.io.TempDir;

/** NK-OPS-001; OPS-009/UI251/SS333/343 §6.10; PG-D-153; PT-OPS-PFILE-001..008. */
class PrivateDirectoryEntryTest {
  private static final int UNCHECKED_BODY_VARIANT = 2;

  private static final String FIXTURE_UNIX_MODE_18F40B0C = "unix:mode";
  private static final String FIXTURE_RETAINED_EXEC_1FEFDEDD = "retained.exec";
  private static final String FIXTURE_CLOSE_97959247 = "close";
  private static final UUID ID = UUID.fromString("00000000-0000-4000-8000-000000000001");
  private static final String TARGET = "inbox-inspector.env";
  private static final byte[] CONTENT = {65, 61, 49, 10};
  @TempDir Path root;

  @Test
  void nativePrivateCreation() throws Exception {
    Calls calls = new Calls();
    try (var directory = OwnedTransferDirectory.open(calls, root)) {
      byte[] actual =
          directory.createPrivatePart(
              ID,
              path -> {
                assertEquals(
                    0x8180 /* POSIX 0100600 */,
                    Files.getAttribute(path, FIXTURE_UNIX_MODE_18F40B0C));
                assertEquals(1, Files.getAttribute(path, "unix:nlink"));
                assertEquals(2, calls.live.size());
                write(path, CONTENT);
                return Files.readAllBytes(path);
              });
      assertArrayEquals(CONTENT, actual);
      failure(
          StorageIoException.Reason.COLLISION,
          () -> directory.createPrivatePart(ID, path -> fail("existing inode callback")));
      assertArrayEquals(CONTENT, Files.readAllBytes(part(ID)));
      UUID regular = new UUID(1, 2);
      directory.createPart(
          regular,
          path -> {
            assertEquals(
                0x81a0 /* POSIX 0100640 */, Files.getAttribute(path, FIXTURE_UNIX_MODE_18F40B0C));
            write(path, CONTENT);
            return true;
          });
      Path outside = root.resolve("outside");
      Files.write(outside, new byte[] {9});
      UUID linked = new UUID(1, 3);
      Files.createSymbolicLink(part(linked), outside);
      failure(
          StorageIoException.Reason.COLLISION,
          () -> directory.createPrivatePart(linked, path -> fail("symlink callback")));
      assertArrayEquals(new byte[] {9}, Files.readAllBytes(outside));
      assertTrue(Files.isSymbolicLink(part(linked)));
      assertEquals(1, calls.live.size());
    }
    assertTrue(calls.live.isEmpty());
  }

  @Test
  void nfile193001NamedEntryHasHeldPrivateInodeAndNeverReopensReplacement() throws Exception {
    Calls calls = new Calls();
    String name = "1234567890abcdef1234567890abcdef.terminal.exec";
    try (var directory = OwnedTransferDirectory.open(calls, root)) {
      int before = calls.closes;
      directory.createPrivateEntry(
          name,
          held -> {
            assertEquals(
                0x8180 /* POSIX 0100600 */, Files.getAttribute(held, FIXTURE_UNIX_MODE_18F40B0C));
            assertEquals(1, Files.getAttribute(held, "unix:nlink"));
            assertEquals(2, calls.live.size());
            Files.move(root.resolve(name), root.resolve(FIXTURE_RETAINED_EXEC_1FEFDEDD));
            Files.write(root.resolve(name), new byte[] {9});
            write(held, CONTENT);
            return true;
          });
      directory.sync();
      assertEquals(before + 1, calls.closes);
      assertArrayEquals(CONTENT, Files.readAllBytes(root.resolve(FIXTURE_RETAINED_EXEC_1FEFDEDD)));
      assertArrayEquals(new byte[] {9}, Files.readAllBytes(root.resolve(name)));
      failure(
          StorageIoException.Reason.COLLISION,
          () -> directory.createPrivateEntry(name, p -> fail("existing callback")));
      Files.createSymbolicLink(
          root.resolve("linked.exec"), root.resolve(FIXTURE_RETAINED_EXEC_1FEFDEDD));
      failure(
          StorageIoException.Reason.COLLISION,
          () -> directory.createPrivateEntry("linked.exec", p -> fail("symlink callback")));
      assertArrayEquals(CONTENT, Files.readAllBytes(root.resolve(FIXTURE_RETAINED_EXEC_1FEFDEDD)));
    }
    assertTrue(calls.live.isEmpty());
  }

  @Test
  void nfile193002MissingNullAndUnsafeNameDoNotMutate() throws Exception {
    Calls calls = new Calls();
    var directory = OwnedTransferDirectory.open(calls, root);
    try (directory) {
      assertThrows(
          IllegalArgumentException.class, () -> directory.createPrivateEntry(null, p -> true));
      assertThrows(
          IllegalArgumentException.class, () -> directory.createPrivateEntry("fixed.exec", null));
      for (String name : new String[] {"", ".", "..", "a/b", "a\0b"})
        assertThrows(
            IllegalArgumentException.class, () -> directory.createPrivateEntry(name, p -> true));
      assertEquals(0, calls.mutations);
    }
    failure(
        StorageIoException.Reason.UNAVAILABLE,
        () -> directory.createPrivateEntry("fixed.exec", p -> fail("closed callback")));
    assertEquals(0, calls.mutations);
  }

  @Test
  void nfile193003CreateWriteAndCloseFailuresRetainPartialAndConsumeFd() throws Exception {
    Calls calls = new Calls();
    try (var directory = OwnedTransferDirectory.open(calls, root)) {
      calls.fail = "create";
      failure(
          StorageIoException.Reason.UNAVAILABLE,
          () -> directory.createPrivateEntry("create.exec", p -> fail("failed create callback")));
      assertFalse(Files.exists(root.resolve("create.exec")));
      calls.fail = "";
      for (String kind : new String[] {"write", FIXTURE_CLOSE_97959247, "both"}) {
        int before = calls.closes;
        failure(
            StorageIoException.Reason.UNAVAILABLE,
            () ->
                directory.createPrivateEntry(
                    kind + ".exec",
                    held -> {
                      write(held, CONTENT);
                      if (!kind.equals("write")) calls.fail = FIXTURE_CLOSE_97959247;
                      if (!kind.equals(FIXTURE_CLOSE_97959247))
                        throw new IOException("private failure not exported");
                      return true;
                    }));
        calls.fail = "";
        assertEquals(before + 1, calls.closes);
        assertEquals(1, calls.live.size());
        assertArrayEquals(CONTENT, Files.readAllBytes(root.resolve(kind + ".exec")));
        failure(
            StorageIoException.Reason.COLLISION,
            () -> directory.createPrivateEntry(kind + ".exec", p -> fail("partial reused")));
      }
    }
    assertTrue(calls.live.isEmpty());
  }

  @Test
  void nfile193004ConcurrentNamedEntryHasExactlyOneWriter() throws Exception {
    try (var directory = OwnedTransferDirectory.open(LinuxDirectoryCalls.create(), root);
        var executor = Executors.newFixedThreadPool(4)) {
      var results = new ArrayList<java.util.concurrent.Future<Boolean>>();
      for (int i = 0; i < 16; i++)
        results.add(
            executor.submit(
                () -> {
                  try {
                    directory.createPrivateEntry(
                        "one.exec",
                        held -> {
                          write(held, CONTENT);
                          return true;
                        });
                    return true;
                  } catch (StorageIoException failure) {
                    assertEquals(StorageIoException.Reason.COLLISION, failure.reason());
                    return false;
                  }
                }));
      int winners = 0;
      for (var result : results) if (result.get(5, TimeUnit.SECONDS)) winners++;
      assertEquals(1, winners);
      assertArrayEquals(CONTENT, Files.readAllBytes(root.resolve("one.exec")));
      assertEquals(
          0x8180 /* POSIX 0100600 */,
          Files.getAttribute(root.resolve("one.exec"), FIXTURE_UNIX_MODE_18F40B0C));
    }
  }

  @Test
  void atomicNoReplace() throws Exception {
    try (var directory = OwnedTransferDirectory.open(LinuxDirectoryCalls.create(), root)) {
      create(directory, ID, CONTENT);
      Path target = root.resolve(TARGET);
      Files.write(target, new byte[] {8});
      failure(StorageIoException.Reason.COLLISION, () -> directory.publishAs(ID, TARGET));
      assertArrayEquals(new byte[] {8}, Files.readAllBytes(target));
      assertArrayEquals(CONTENT, Files.readAllBytes(part(ID)));
      Files.delete(target);
      Path outside = root.resolve("outside");
      Files.write(outside, new byte[] {9});
      Files.createSymbolicLink(target, outside);
      failure(StorageIoException.Reason.COLLISION, () -> directory.publishAs(ID, TARGET));
      assertTrue(Files.isSymbolicLink(target));
      assertArrayEquals(new byte[] {9}, Files.readAllBytes(outside));
      assertArrayEquals(CONTENT, Files.readAllBytes(part(ID)));
      Files.delete(target);
      directory.publishAs(ID, TARGET);
      assertFalse(Files.exists(part(ID)));
      assertArrayEquals(CONTENT, Files.readAllBytes(target));
      assertEquals(
          0x8180 /* POSIX 0100600 */, Files.getAttribute(target, FIXTURE_UNIX_MODE_18F40B0C));
      failure(StorageIoException.Reason.MISSING, () -> directory.publishAs(ID, "other"));
      assertFalse(Files.exists(root.resolve("other")));
      directory.unlinkEntry(TARGET);
      assertFalse(Files.exists(target));
      failure(StorageIoException.Reason.MISSING, () -> directory.unlinkEntry(TARGET));
    }
  }

  @Test
  void scopedOwnership() throws Exception {
    Calls calls = new Calls();
    try (var directory = OwnedTransferDirectory.open(calls, root)) {
      int before = calls.closes;
      directory.createPrivatePart(
          ID,
          path -> {
            Files.move(part(ID), root.resolve("saved"));
            Files.write(part(ID), new byte[] {9});
            write(path, CONTENT);
            return true;
          });
      assertEquals(before + 1, calls.closes);
      assertArrayEquals(CONTENT, Files.readAllBytes(root.resolve("saved")));
      assertArrayEquals(new byte[] {9}, Files.readAllBytes(part(ID)));
      for (int kind = 0; kind < 3; kind++) {
        int mode = kind;
        UUID id = new UUID(2, kind);
        int closed = calls.closes;
        if (kind == UNCHECKED_BODY_VARIANT) {
          var expected = new IllegalStateException("synthetic unchecked failure");
          assertSame(
              expected,
              assertThrows(
                  IllegalStateException.class,
                  () ->
                      directory.createPrivatePart(
                          id,
                          path -> {
                            throw expected;
                          })));
        } else {
          failure(
              StorageIoException.Reason.UNAVAILABLE,
              () ->
                  directory.createPrivatePart(
                      id,
                      path -> {
                        calls.fail = mode == 1 ? FIXTURE_CLOSE_97959247 : "";
                        throw new IOException("synthetic private path must not escape");
                      }));
        }
        calls.fail = "";
        assertEquals(closed + 1, calls.closes);
        assertEquals(1, calls.live.size());
        assertTrue(Files.exists(part(id)));
      }
      boolean alive = directory.atDirectory(Files::isDirectory);
      assertTrue(alive);
    }
    assertTrue(calls.live.isEmpty());
  }

  @Test
  void nameAndNullContracts() throws Exception {
    Calls calls = new Calls();
    var directory = OwnedTransferDirectory.open(calls, root);
    try (directory) {
      int mutations = calls.mutations;
      for (String name : new String[] {"", ".", "..", "a/b", "a\0b"}) {
        assertThrows(IllegalArgumentException.class, () -> directory.publishAs(ID, name));
        assertThrows(IllegalArgumentException.class, () -> directory.unlinkEntry(name));
      }
      assertThrows(NullPointerException.class, () -> directory.createPrivatePart(null, p -> true));
      assertThrows(NullPointerException.class, () -> directory.createPrivatePart(ID, null));
      assertThrows(NullPointerException.class, () -> directory.publishAs(null, TARGET));
      assertThrows(NullPointerException.class, () -> directory.publishAs(ID, null));
      assertThrows(NullPointerException.class, () -> directory.unlinkEntry(null));
      assertEquals(mutations, calls.mutations);
    }
    failure(
        StorageIoException.Reason.UNAVAILABLE, () -> directory.createPrivatePart(ID, p -> true));
    failure(StorageIoException.Reason.UNAVAILABLE, () -> directory.publishAs(ID, TARGET));
    failure(StorageIoException.Reason.UNAVAILABLE, () -> directory.unlinkEntry(TARGET));
    assertEquals(0, calls.mutations);
    assertTrue(calls.live.isEmpty());
  }

  @Test
  void faultAndUncertainOutcomes() throws Exception {
    Calls calls = new Calls();
    for (String point : new String[] {"openRoot", "openDirectory"}) {
      calls.fail = point;
      failure(
          StorageIoException.Reason.UNAVAILABLE, () -> OwnedTransferDirectory.open(calls, root));
      assertTrue(calls.live.isEmpty());
    }
    calls.fail = "";
    try (var directory = OwnedTransferDirectory.open(calls, root)) {
      calls.fail = "create";
      failure(
          StorageIoException.Reason.UNAVAILABLE,
          () -> directory.createPrivatePart(ID, p -> fail("failed create callback")));
      assertFalse(Files.exists(part(ID)));
      calls.fail = FIXTURE_CLOSE_97959247;
      failure(StorageIoException.Reason.UNAVAILABLE, () -> create(directory, ID, CONTENT));
      assertArrayEquals(CONTENT, Files.readAllBytes(part(ID)));
      assertEquals(1, calls.live.size());
      calls.fail = "publish";
      failure(StorageIoException.Reason.UNAVAILABLE, () -> directory.publishAs(ID, TARGET));
      assertTrue(Files.exists(part(ID)));
      assertFalse(Files.exists(root.resolve(TARGET)));
      calls.fail = "sync";
      failure(StorageIoException.Reason.UNAVAILABLE, () -> directory.publishAs(ID, TARGET));
      assertFalse(Files.exists(part(ID)));
      assertArrayEquals(CONTENT, Files.readAllBytes(root.resolve(TARGET)));
      calls.fail = "unlink";
      failure(StorageIoException.Reason.UNAVAILABLE, () -> directory.unlinkEntry(TARGET));
      assertArrayEquals(CONTENT, Files.readAllBytes(root.resolve(TARGET)));
      calls.fail = "sync";
      failure(StorageIoException.Reason.UNAVAILABLE, () -> directory.unlinkEntry(TARGET));
      assertFalse(Files.exists(root.resolve(TARGET)));
      assertEquals(1, calls.live.size());
      calls.fail = "";
    }
    assertTrue(calls.live.isEmpty());
  }

  @Test
  void retainedNamespace() throws Exception {
    Path configured = Files.createDirectory(root.resolve("configured"));
    Path retained = root.resolve("retained");
    Path outside = Files.createDirectory(root.resolve("outside"));
    Files.write(outside.resolve(TARGET), new byte[] {9});
    try (var directory = OwnedTransferDirectory.open(LinuxDirectoryCalls.create(), configured)) {
      Files.move(configured, retained);
      Files.createSymbolicLink(configured, outside);
      create(directory, ID, CONTENT);
      assertTrue(Files.exists(retained.resolve(ID + ".part")));
      assertFalse(Files.exists(outside.resolve(ID + ".part")));
      directory.publishAs(ID, TARGET);
      assertArrayEquals(CONTENT, Files.readAllBytes(retained.resolve(TARGET)));
      assertArrayEquals(new byte[] {9}, Files.readAllBytes(outside.resolve(TARGET)));
      directory.unlinkEntry(TARGET);
      assertFalse(Files.exists(retained.resolve(TARGET)));
      assertArrayEquals(new byte[] {9}, Files.readAllBytes(outside.resolve(TARGET)));
    }
  }

  @Test
  void concurrentSinglePublication() throws Exception {
    try (var directory = OwnedTransferDirectory.open(LinuxDirectoryCalls.create(), root);
        var executor = Executors.newFixedThreadPool(8)) {
      var results = new ArrayList<java.util.concurrent.Future<Integer>>();
      for (int i = 0; i < 32; i++) {
        int index = i;
        results.add(
            executor.submit(
                () -> {
                  UUID id = new UUID(3, index);
                  create(directory, id, new byte[] {(byte) index});
                  try {
                    directory.publishAs(id, TARGET);
                    return index;
                  } catch (StorageIoException ex) {
                    assertEquals(StorageIoException.Reason.COLLISION, ex.reason());
                    return -1;
                  }
                }));
      }
      int winners = 0;
      for (int i = 0; i < results.size(); i++) {
        int winner = results.get(i).get(10, TimeUnit.SECONDS);
        if (winner >= 0) {
          winners++;
          assertEquals(i, winner);
          assertFalse(Files.exists(part(new UUID(3, i))));
          assertArrayEquals(new byte[] {(byte) i}, Files.readAllBytes(root.resolve(TARGET)));
        } else {
          assertArrayEquals(new byte[] {(byte) i}, Files.readAllBytes(part(new UUID(3, i))));
        }
      }
      assertEquals(1, winners);
      try (var entries = Files.list(root)) {
        assertEquals(32, entries.count());
      }
    }
  }

  @Test
  void unsupportedAndNativeArguments() throws Exception {
    Calls calls = new Calls();
    calls.unsupported = true;
    try (var directory = OwnedTransferDirectory.open(calls, root)) {
      int closed = calls.closes;
      failure(
          StorageIoException.Reason.UNAVAILABLE,
          () -> directory.createPrivatePart(ID, p -> fail("unsupported callback")));
      assertEquals(closed, calls.closes);
      assertEquals(0, calls.mutations);
      assertFalse(Files.exists(part(ID)));
      assertEquals(1, calls.live.size());
    }
    assertTrue(calls.live.isEmpty());
    LinuxDirectoryCalls nativeCalls = LinuxDirectoryCalls.create();
    assertThrows(NullPointerException.class, () -> nativeCalls.createPrivateFile(-1, null));
    for (String name : new String[] {"", ".", "..", "a/b", "a\0b"}) {
      assertThrows(IllegalArgumentException.class, () -> nativeCalls.createPrivateFile(-1, name));
    }
    failure(
        StorageIoException.Reason.UNAVAILABLE, () -> nativeCalls.createPrivateFile(-1, "entry"));
    int fd = nativeCalls.openRoot();
    try {
      failure(
          StorageIoException.Reason.UNAVAILABLE,
          () -> nativeCalls.createPrivateFile(fd, "x".repeat(256)));
    } finally {
      nativeCalls.close(fd);
    }
  }

  private Path part(UUID id) {
    return root.resolve(id + ".part");
  }

  private static void create(OwnedTransferDirectory directory, UUID id, byte[] content)
      throws StorageIoException {
    directory.createPrivatePart(
        id,
        path -> {
          write(path, content);
          return true;
        });
  }

  private static void write(Path path, byte[] bytes) throws IOException {
    try (var channel = FileChannel.open(path, StandardOpenOption.WRITE)) {
      var buffer = ByteBuffer.wrap(bytes);
      while (buffer.hasRemaining()) {
        assertTrue(channel.write(buffer) > 0);
      }
      channel.force(true);
    }
  }

  private static void failure(StorageIoException.Reason reason, Executable operation) {
    var ex = assertThrows(StorageIoException.class, operation);
    assertEquals(reason, ex.reason());
    assertNull(ex.getCause());
    assertEquals(0, ex.getSuppressed().length);
    assertFalse(ex.getMessage().contains("synthetic"));
  }

  /** Public SPI fault port; every native descriptor is accounted for, including failed close. */
  private static final class Calls implements DirectoryCalls {
    final LinuxDirectoryCalls nativeCalls = LinuxDirectoryCalls.create();
    final Set<Integer> live = new HashSet<>();
    String fail = "";
    boolean unsupported;
    int closes;
    int mutations;

    private void point(String name) throws StorageIoException {
      if (fail.equals(name)) {
        throw new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
      }
    }

    private int own(int fd) {
      assertTrue(live.add(fd));
      return fd;
    }

    @Override
    public int openRoot() throws StorageIoException {
      point("openRoot");
      return own(nativeCalls.openRoot());
    }

    @Override
    public int openDirectory(int parent, String name) throws StorageIoException {
      point("openDirectory");
      return own(nativeCalls.openDirectory(parent, name));
    }

    @Override
    public int openEntry(int parent, String name) throws StorageIoException {
      return own(nativeCalls.openEntry(parent, name));
    }

    @Override
    public int createFile(int parent, String name) throws StorageIoException {
      mutations++;
      return own(nativeCalls.createFile(parent, name));
    }

    @Override
    public int createPrivateFile(int parent, String name) throws StorageIoException {
      if (unsupported) {
        return DirectoryCalls.super.createPrivateFile(parent, name);
      }
      point("create");
      mutations++;
      return own(nativeCalls.createPrivateFile(parent, name));
    }

    @Override
    public void createDirectory(int parent, String name) throws StorageIoException {
      mutations++;
      nativeCalls.createDirectory(parent, name);
    }

    @Override
    public void publish(int parent, String source, String target) throws StorageIoException {
      point("publish");
      mutations++;
      nativeCalls.publish(parent, source, target);
    }

    @Override
    public void unlink(int parent, String name) throws StorageIoException {
      point("unlink");
      mutations++;
      nativeCalls.unlink(parent, name);
    }

    @Override
    public void sync(int fd) throws StorageIoException {
      point("sync");
      nativeCalls.sync(fd);
    }

    @Override
    public void close(int fd) throws StorageIoException {
      assertTrue(live.remove(fd));
      closes++;
      nativeCalls.close(fd);
      point(FIXTURE_CLOSE_97959247);
    }
  }
}
