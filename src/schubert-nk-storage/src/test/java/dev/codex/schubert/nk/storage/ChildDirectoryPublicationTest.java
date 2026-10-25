package dev.codex.schubert.nk.storage;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.io.IOException;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Proxy;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** NK-OPS-001; BAK/BKO/OPS009/UI251/SS333 7.5/341 6.9; SSC065/PG176; PDIR001..008. */
final class ChildDirectoryPublicationTest {
  @TempDir Path temporary;
  private static final byte[] CONTENT = {65, 10};

  @Test
  void nativeDirectoryPublication() throws Exception {
    try (var f = new Fixture(temporary)) {
      f.seed("pending", CONTENT);
      Object inode = Files.getAttribute(f.path.resolve("pending"), "unix:ino");
      Object device = Files.getAttribute(f.path.resolve("pending"), "unix:dev");
      f.root.publishChild("pending", "ready");
      assertEquals(List.of("openDirectory", "publish", "sync", "close"), f.events);
      assertEquals(inode, Files.getAttribute(f.path.resolve("ready"), "unix:ino"));
      assertEquals(device, Files.getAttribute(f.path.resolve("ready"), "unix:dev"));
      assertArrayEquals(CONTENT, Files.readAllBytes(f.path.resolve("ready/content")));
      assertFalse(Files.exists(f.path.resolve("pending")));
      f.released();
    }
  }

  @Test
  void noReplaceAndSourceType() throws Exception {
    for (String type : List.of("directory", "file", "symlink")) {
      try (var f = new Fixture(temporary)) {
        f.seed("pending", CONTENT);
        Path ready = f.path.resolve("ready");
        if (type.equals("directory")) f.seed("ready", new byte[] {9});
        else if (type.equals("file")) Files.write(ready, new byte[] {9});
        else {
          Files.write(f.path.resolve("outside"), new byte[] {9});
          Files.createSymbolicLink(ready, f.path.resolve("outside"));
        }
        failure(StorageIoException.Reason.COLLISION, () -> f.root.publishChild("pending", "ready"));
        assertArrayEquals(CONTENT, Files.readAllBytes(f.path.resolve("pending/content")));
        assertArrayEquals(
            new byte[] {9},
            Files.readAllBytes(type.equals("directory") ? ready.resolve("content") : ready));
        if (type.equals("symlink")) assertTrue(Files.isSymbolicLink(ready));
        f.released();
      }
    }
    for (String type : List.of("missing", "file", "symlink")) {
      try (var f = new Fixture(temporary)) {
        if (type.equals("file")) Files.write(f.path.resolve("pending"), CONTENT);
        if (type.equals("symlink")) {
          f.seed("outside", CONTENT);
          Files.createSymbolicLink(f.path.resolve("pending"), f.path.resolve("outside"));
        }
        failure(
            type.equals("missing")
                ? StorageIoException.Reason.MISSING
                : StorageIoException.Reason.UNAVAILABLE,
            () -> f.root.publishChild("pending", "ready"));
        assertFalse(Files.exists(f.path.resolve("ready")));
        if (type.equals("file"))
          assertArrayEquals(CONTENT, Files.readAllBytes(f.path.resolve("pending")));
        if (type.equals("symlink"))
          assertArrayEquals(CONTENT, Files.readAllBytes(f.path.resolve("outside/content")));
        f.released();
      }
    }
  }

  @Test
  void nameNullAndClosed() throws Exception {
    var f = new Fixture(temporary);
    try {
      for (String name : new String[] {"", ".", "..", "a/b", "a\0b"}) {
        assertThrows(IllegalArgumentException.class, () -> f.root.publishChild(name, "ready"));
        assertThrows(IllegalArgumentException.class, () -> f.root.publishChild("pending", name));
      }
      assertThrows(IllegalArgumentException.class, () -> f.root.publishChild("same", "same"));
      assertThrows(NullPointerException.class, () -> f.root.publishChild(null, "ready"));
      assertThrows(NullPointerException.class, () -> f.root.publishChild("pending", null));
      assertTrue(f.events.isEmpty());
      f.root.close();
      f.events.clear();
      failure(StorageIoException.Reason.UNAVAILABLE, () -> f.root.publishChild("pending", "ready"));
      assertTrue(f.events.isEmpty());
    } finally {
      f.close();
    }
  }

  @Test
  void everyNativeFailure() throws Exception {
    for (String point : List.of("openDirectory", "publish", "sync", "close")) {
      for (int kind = 0; kind < 3; kind++) {
        try (var f = new Fixture(temporary)) {
          f.seed("pending", CONTENT);
          Throwable expected =
              kind == 0
                  ? new StorageIoException(StorageIoException.Reason.UNAVAILABLE)
                  : kind == 1
                      ? new IllegalStateException("public synthetic fault")
                      : new AssertionError("public synthetic fault");
          f.faults.put(point, expected);
          if (kind == 0)
            failure(
                StorageIoException.Reason.UNAVAILABLE,
                () -> f.root.publishChild("pending", "ready"));
          else
            assertSame(
                expected,
                assertThrows(expected.getClass(), () -> f.root.publishChild("pending", "ready")));
          assertEquals(
              point.equals("openDirectory") ? 0 : 1, Collections.frequency(f.events, "close"));
          boolean renamed = point.equals("sync") || point.equals("close");
          assertArrayEquals(
              CONTENT,
              Files.readAllBytes(f.path.resolve(renamed ? "ready/content" : "pending/content")));
          f.released();
        }
      }
    }
  }

  @Test
  void uncertainPublication() throws Exception {
    for (String point : List.of("sync", "close")) {
      try (var f = new Fixture(temporary)) {
        f.seed("pending", CONTENT);
        f.faults.put(point, new StorageIoException(StorageIoException.Reason.UNAVAILABLE));
        failure(
            StorageIoException.Reason.UNAVAILABLE, () -> f.root.publishChild("pending", "ready"));
        assertFalse(Files.exists(f.path.resolve("pending")));
        assertArrayEquals(CONTENT, Files.readAllBytes(f.path.resolve("ready/content")));
        f.faults.clear();
        failure(StorageIoException.Reason.MISSING, () -> f.root.publishChild("pending", "ready"));
        assertArrayEquals(CONTENT, Files.readAllBytes(f.path.resolve("ready/content")));
        f.released();
      }
    }
  }

  @Test
  void compoundFailures() throws Exception {
    for (int primaryKind = 0; primaryKind < 3; primaryKind++) {
      for (int closeKind = 0; closeKind < 4; closeKind++) {
        try (var f = new Fixture(temporary)) {
          f.seed("pending", CONTENT);
          Throwable primary =
              primaryKind == 0
                  ? new StorageIoException(StorageIoException.Reason.UNAVAILABLE)
                  : primaryKind == 1
                      ? new IllegalStateException("public body")
                      : new AssertionError("public body");
          Throwable secondary =
              closeKind == 0
                  ? new StorageIoException(StorageIoException.Reason.UNAVAILABLE)
                  : closeKind == 1
                      ? new IllegalStateException("public close")
                      : closeKind == 2 ? new AssertionError("public close") : primary;
          f.faults.put("publish", primary);
          f.faults.put("close", secondary);
          if (primaryKind == 0 && (closeKind == 0 || closeKind == 3))
            failure(
                StorageIoException.Reason.UNAVAILABLE,
                () -> f.root.publishChild("pending", "ready"));
          else {
            Throwable expected = primaryKind == 0 ? secondary : primary;
            Throwable actual =
                assertThrows(expected.getClass(), () -> f.root.publishChild("pending", "ready"));
            assertSame(expected, actual);
            assertEquals(primaryKind == 0 ? 0 : 1, actual.getSuppressed().length);
            if (primaryKind != 0)
              assertInstanceOf(StorageIoException.class, actual.getSuppressed()[0]);
          }
          assertArrayEquals(CONTENT, Files.readAllBytes(f.path.resolve("pending/content")));
          assertEquals(1, Collections.frequency(f.events, "close"));
          f.released();
        }
      }
    }
  }

  @Test
  void retainedParentCapability() throws Exception {
    try (var f = new Fixture(temporary)) {
      f.seed("pending", CONTENT);
      Path saved = f.path.resolveSibling("saved");
      Files.move(f.path, saved);
      Files.createDirectory(f.path);
      f.seed("pending", new byte[] {9});
      f.root.publishChild("pending", "ready");
      assertArrayEquals(CONTENT, Files.readAllBytes(saved.resolve("ready/content")));
      assertArrayEquals(new byte[] {9}, Files.readAllBytes(f.path.resolve("pending/content")));
      assertFalse(Files.exists(f.path.resolve("ready")));
      f.released();
    }
  }

  @Test
  void concurrentNoReplace() throws Exception {
    try (var f = new Fixture(temporary);
        var executor = Executors.newVirtualThreadPerTaskExecutor()) {
      for (int i = 0; i < 8; i++) f.seed("pending" + i, new byte[] {(byte) i});
      List<Future<Boolean>> results = new ArrayList<>();
      for (int i = 0; i < 8; i++) {
        String source = "pending" + i;
        results.add(
            executor.submit(
                () -> {
                  try {
                    f.root.publishChild(source, "ready");
                    return true;
                  } catch (StorageIoException failure) {
                    assertEquals(StorageIoException.Reason.COLLISION, failure.reason());
                    return false;
                  }
                }));
      }
      int successes = 0;
      for (var result : results) if (result.get()) successes++;
      assertEquals(1, successes);
      int winner = Files.readAllBytes(f.path.resolve("ready/content"))[0];
      for (int i = 0; i < 8; i++) {
        if (i == winner) assertFalse(Files.exists(f.path.resolve("pending" + i)));
        else
          assertArrayEquals(
              new byte[] {(byte) i},
              Files.readAllBytes(f.path.resolve("pending" + i + "/content")));
      }
      f.released();
    }
  }

  @FunctionalInterface
  interface Operation {
    void run() throws StorageIoException;
  }

  private static void failure(StorageIoException.Reason reason, Operation operation) {
    var failure = assertThrows(StorageIoException.class, operation::run);
    assertEquals(reason, failure.reason());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
  }

  private static final class Fixture implements AutoCloseable {
    final Path path;
    final OwnedTransferDirectory root;
    final Set<Integer> live = new HashSet<>();
    final List<String> events = new ArrayList<>();
    final Map<String, Throwable> faults = new HashMap<>();
    final int rootFd;
    boolean tracking;

    Fixture(Path temporary) throws Exception {
      path =
          Files.createDirectory(Files.createTempDirectory(temporary, "directory-").resolve("root"));
      DirectoryCalls nativeCalls = LinuxDirectoryCalls.create();
      DirectoryCalls calls =
          (DirectoryCalls)
              Proxy.newProxyInstance(
                  getClass().getClassLoader(),
                  new Class<?>[] {DirectoryCalls.class},
                  (proxy, method, args) -> {
                    String name = method.getName();
                    if (!Set.of("openRoot", "openDirectory", "publish", "sync", "close")
                        .contains(name))
                      throw new AssertionError("unapproved directory mutation " + name);
                    if (!name.equals("close")) point(name);
                    Object result;
                    try {
                      result = method.invoke(nativeCalls, args);
                    } catch (InvocationTargetException failure) {
                      throw failure.getCause();
                    }
                    if (name.equals("close")) {
                      live.remove((Integer) args[0]);
                      point(name);
                    } else if (name.startsWith("open")) live.add((Integer) result);
                    return result;
                  });
      root = OwnedTransferDirectory.open(calls, path);
      assertEquals(1, live.size());
      rootFd = live.iterator().next();
      tracking = true;
    }

    void point(String name) throws Throwable {
      if (!tracking) return;
      events.add(name);
      Throwable failure = faults.get(name);
      if (failure != null) throw failure;
    }

    void seed(String name, byte[] content) throws IOException {
      Files.createDirectory(path.resolve(name));
      Files.write(path.resolve(name).resolve("content"), content);
    }

    void released() {
      assertEquals(Set.of(rootFd), live);
    }

    @Override
    public void close() throws StorageIoException {
      tracking = false;
      faults.clear();
      root.close();
      assertTrue(live.isEmpty());
    }
  }
}
