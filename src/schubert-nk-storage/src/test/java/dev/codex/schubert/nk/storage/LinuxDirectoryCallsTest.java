package dev.codex.schubert.nk.storage;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.lang.foreign.Linker;
import java.lang.foreign.SymbolLookup;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.nio.file.attribute.PosixFilePermissions;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.concurrent.Callable;
import java.util.concurrent.Executors;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** Actual Linux syscalls against synthetic files only. SS333/SSC-019; PT-SCN-008-F01/F03. */
class LinuxDirectoryCallsTest {
  @TempDir Path root;

  @Test
  void transfer003EmptyDirectoryOnlyNeverRecursesOrFollowsSymlink() throws Exception {
    var calls = LinuxDirectoryCalls.create();
    try (var parent = OwnedTransferDirectory.open(calls, root)) {
      Files.createDirectory(root.resolve("empty"));
      parent.removeEmptyChild("empty");
      assertFalse(Files.exists(root.resolve("empty")));
      Files.createDirectory(root.resolve("nonempty"));
      Files.write(root.resolve("nonempty/file"), new byte[] {1, 2});
      assertThrows(StorageIoException.class, () -> parent.removeEmptyChild("nonempty"));
      assertArrayEquals(new byte[] {1, 2}, Files.readAllBytes(root.resolve("nonempty/file")));
      Files.createSymbolicLink(root.resolve("link"), root.resolve("nonempty"));
      assertThrows(StorageIoException.class, () -> parent.removeEmptyChild("link"));
      assertTrue(Files.isSymbolicLink(root.resolve("link")));
      for (String bad : List.of("", ".", "..", "a/b", "a\0b"))
        assertThrows(IllegalArgumentException.class, () -> parent.removeEmptyChild(bad));
      assertThrows(NullPointerException.class, () -> parent.removeEmptyChild(null));
      assertThrows(
          StorageIoException.class,
          () -> LinuxHostDirectoryCalls.create().removeEmptyDirectory(-1, "empty"));
    }
  }

  @Test
  void w01CreateNewHasOneWinnerAndPreservesExistingFileAndSymlinkTargets() throws Exception {
    DirectoryCalls calls = LinuxDirectoryCalls.create();
    int parent = open(calls, root);
    try (var executor = Executors.newFixedThreadPool(16)) {
      List<Callable<Integer>> tasks = new ArrayList<>();
      for (int i = 0; i < 100; i++) {
        int contender = i;
        tasks.add(
            () -> {
              int fd;
              try {
                fd = calls.createFile(parent, "same.part");
              } catch (StorageIoException failure) {
                assertEquals(StorageIoException.Reason.COLLISION, failure.reason());
                return -1;
              }
              try {
                Path handle = Path.of("/proc/self/fd", Integer.toString(fd));
                assertEquals(0100640, Files.getAttribute(handle, "unix:mode"));
                try (var stream =
                    java.nio.channels.FileChannel.open(handle, StandardOpenOption.WRITE)) {
                  assertEquals(
                      1, stream.write(java.nio.ByteBuffer.wrap(new byte[] {(byte) contender})));
                  stream.force(true);
                }
              } finally {
                calls.close(fd);
              }
              return contender;
            });
      }
      int winner = -1;
      int count = 0;
      for (var result : executor.invokeAll(tasks)) {
        int contender = result.get();
        if (contender >= 0) {
          winner = contender;
          count++;
        }
      }
      assertEquals(1, count);
      assertArrayEquals(new byte[] {(byte) winner}, Files.readAllBytes(root.resolve("same.part")));
      Files.createSymbolicLink(root.resolve("link.part"), root.resolve("same.part"));
      assertFailure(
          StorageIoException.Reason.COLLISION, () -> calls.createFile(parent, "link.part"));
      assertTrue(Files.isSymbolicLink(root.resolve("link.part")));
      assertArrayEquals(new byte[] {(byte) winner}, Files.readAllBytes(root.resolve("same.part")));
      for (String name : List.of("", ".", "..", "a/b", "a\0b", "/")) {
        assertThrows(IllegalArgumentException.class, () -> calls.createFile(parent, name));
      }
      assertThrows(NullPointerException.class, () -> calls.createFile(parent, null));
      assertFailure(StorageIoException.Reason.UNAVAILABLE, () -> calls.createFile(-1, "new.part"));
    } finally {
      calls.close(parent);
    }
  }

  @Test
  void f01NativeOperationsPreserveExistingTargetsAndBoundAllErrors() throws Exception {
    DirectoryCalls calls = LinuxDirectoryCalls.create();
    int fd = open(calls, root);
    try {
      calls.createDirectory(fd, "20260908");
      assertEquals(
          PosixFilePermissions.fromString("rwxr-x---"),
          Files.getPosixFilePermissions(root.resolve("20260908")));
      int child = calls.openDirectory(fd, "20260908");
      calls.sync(child);
      calls.close(child);
      assertFailure(
          StorageIoException.Reason.COLLISION, () -> calls.createDirectory(fd, "20260908"));
      assertFailure(StorageIoException.Reason.MISSING, () -> calls.openDirectory(fd, "missing"));
      Files.write(root.resolve("sample.part"), new byte[] {1, 2, 3}, StandardOpenOption.CREATE_NEW);
      Files.write(root.resolve("sample.ready"), new byte[] {7, 8}, StandardOpenOption.CREATE_NEW);
      assertFailure(
          StorageIoException.Reason.COLLISION,
          () -> calls.publish(fd, "sample.part", "sample.ready"));
      assertArrayEquals(new byte[] {1, 2, 3}, Files.readAllBytes(root.resolve("sample.part")));
      assertArrayEquals(new byte[] {7, 8}, Files.readAllBytes(root.resolve("sample.ready")));
      calls.publish(fd, "sample.part", "new.ready");
      calls.sync(fd);
      assertFalse(Files.exists(root.resolve("sample.part")));
      assertArrayEquals(new byte[] {1, 2, 3}, Files.readAllBytes(root.resolve("new.ready")));
      calls.unlink(fd, "new.ready");
      assertFalse(Files.exists(root.resolve("new.ready")));
      assertFailure(StorageIoException.Reason.MISSING, () -> calls.unlink(fd, "new.ready"));
      assertFailure(
          StorageIoException.Reason.MISSING, () -> calls.publish(fd, "missing", "another"));
      Files.createSymbolicLink(root.resolve("link"), root.resolve("20260908"));
      assertFailure(StorageIoException.Reason.UNAVAILABLE, () -> calls.openDirectory(fd, "link"));
      assertFailure(
          StorageIoException.Reason.UNAVAILABLE, () -> calls.openDirectory(fd, "sample.ready"));
      assertFailure(StorageIoException.Reason.UNAVAILABLE, () -> calls.sync(-1));
      assertFailure(StorageIoException.Reason.UNAVAILABLE, () -> calls.close(-1));
      assertFailure(StorageIoException.Reason.UNAVAILABLE, () -> calls.createDirectory(-1, "date"));
      assertFailure(StorageIoException.Reason.UNAVAILABLE, () -> calls.openDirectory(-1, "date"));
      assertFailure(
          StorageIoException.Reason.UNAVAILABLE, () -> calls.publish(-1, "part", "ready"));
      assertFailure(StorageIoException.Reason.UNAVAILABLE, () -> calls.unlink(-1, "part"));
    } finally {
      calls.close(fd);
    }
  }

  @Test
  void f01RejectsNullNamesTraversalUnknownAbiAndMissingSymbols() throws Exception {
    DirectoryCalls calls = LinuxDirectoryCalls.create();
    for (String name : List.of("", ".", "..", "a/b", "a\0b", "/")) {
      assertThrows(IllegalArgumentException.class, () -> calls.openDirectory(-1, name));
      assertThrows(IllegalArgumentException.class, () -> calls.openEntry(-1, name));
      assertThrows(IllegalArgumentException.class, () -> calls.createDirectory(-1, name));
      assertThrows(IllegalArgumentException.class, () -> calls.publish(-1, name, "ready"));
      assertThrows(IllegalArgumentException.class, () -> calls.publish(-1, "part", name));
      assertThrows(IllegalArgumentException.class, () -> calls.unlink(-1, name));
    }
    assertThrows(NullPointerException.class, () -> calls.openDirectory(-1, null));
    assertThrows(NullPointerException.class, () -> calls.openEntry(-1, null));
    assertFailure(StorageIoException.Reason.UNAVAILABLE, () -> calls.openEntry(-1, "entry"));
    assertThrows(NullPointerException.class, () -> calls.createDirectory(-1, null));
    assertThrows(NullPointerException.class, () -> calls.publish(-1, null, "ready"));
    assertThrows(NullPointerException.class, () -> calls.publish(-1, "part", null));
    assertThrows(NullPointerException.class, () -> calls.unlink(-1, null));
    assertThrows(NullPointerException.class, () -> new StorageIoException(null));
    SymbolLookup symbols = Linker.nativeLinker().defaultLookup();
    assertThrows(
        NullPointerException.class, () -> LinuxDirectoryCalls.create(null, "amd64", symbols));
    assertThrows(
        NullPointerException.class, () -> LinuxDirectoryCalls.create("Linux", null, symbols));
    assertThrows(
        NullPointerException.class, () -> LinuxDirectoryCalls.create("Linux", "amd64", null));
    assertThrows(
        IllegalStateException.class, () -> LinuxDirectoryCalls.create("Windows", "amd64", symbols));
    assertThrows(
        IllegalStateException.class, () -> LinuxDirectoryCalls.create("Linux", "unknown", symbols));
    assertEquals(
        "native storage is unavailable",
        assertThrows(
                IllegalStateException.class,
                () -> LinuxDirectoryCalls.create("Linux", "amd64", name -> Optional.empty()))
            .getMessage());
  }

  @Test
  void f03OneOf100ConcurrentPublishersWinsWithoutReplacingWinner() throws Exception {
    DirectoryCalls calls = LinuxDirectoryCalls.create();
    int fd = open(calls, root);
    try (var executor = Executors.newFixedThreadPool(16)) {
      List<Callable<Integer>> tasks = new ArrayList<>();
      for (int i = 0; i < 100; i++) {
        int id = i;
        Files.write(
            root.resolve(id + ".part"), new byte[] {(byte) id}, StandardOpenOption.CREATE_NEW);
        tasks.add(
            () -> {
              try {
                calls.publish(fd, id + ".part", "winner.ready");
                return id;
              } catch (StorageIoException ex) {
                assertEquals(StorageIoException.Reason.COLLISION, ex.reason());
                return -1;
              }
            });
      }
      int wins = 0;
      for (var future : executor.invokeAll(tasks)) {
        int id = future.get();
        if (id >= 0) {
          wins++;
          assertArrayEquals(
              new byte[] {(byte) id}, Files.readAllBytes(root.resolve("winner.ready")));
          assertFalse(Files.exists(root.resolve(id + ".part")));
        }
      }
      assertEquals(1, wins);
      byte winner = Files.readAllBytes(root.resolve("winner.ready"))[0];
      for (int i = 0; i < 100; i++) {
        if (i != winner)
          assertArrayEquals(new byte[] {(byte) i}, Files.readAllBytes(root.resolve(i + ".part")));
      }
      try (var entries = Files.list(root)) {
        assertEquals(100L, entries.count());
      }
    } finally {
      calls.close(fd);
    }
  }

  private static int open(DirectoryCalls calls, Path path) throws StorageIoException {
    int fd = calls.openRoot();
    for (Path component : path) {
      int child = calls.openDirectory(fd, component.toString());
      calls.close(fd);
      fd = child;
    }
    return fd;
  }

  private static void assertFailure(
      StorageIoException.Reason reason, org.junit.jupiter.api.function.Executable action) {
    StorageIoException ex = assertThrows(StorageIoException.class, action);
    assertEquals(reason, ex.reason());
    assertEquals("transfer storage operation failed", ex.getMessage());
    assertNull(ex.getCause());
    assertEquals(0, ex.getSuppressed().length);
  }
}
