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
  private static final String FIXTURE_PENDING_12ADAC54 = "pending";
  private static final String FIXTURE_READY_40EC7F71 = "ready";
  private static final String FIXTURE_OPENDIRECTORY_9E885716 = "openDirectory";
  private static final String FIXTURE_PUBLISH_69201707 = "publish";
  private static final String FIXTURE_SYNC_5CFA1A73 = "sync";
  private static final String FIXTURE_CLOSE_97959247 = "close";
  private static final String FIXTURE_READY_CONTENT_F3A9BB35 = "ready/content";
  private static final String FIXTURE_FILE_BFDDE6F5 = "file";
  private static final String FIXTURE_SYMLINK_36F374CF = "symlink";
  private static final String FIXTURE_OUTSIDE_F78EA721 = "outside";
  private static final String FIXTURE_PENDING_CONTENT_83FC1E31 = "pending/content";
  @TempDir Path temporary;
  private static final byte[] CONTENT = {65, 10};

  @Test
  void nativeDirectoryPublication() throws Exception {
    try (var f = new Fixture(temporary)) {
      f.seed(FIXTURE_PENDING_12ADAC54, CONTENT);
      Object inode = Files.getAttribute(f.path.resolve(FIXTURE_PENDING_12ADAC54), "unix:ino");
      Object device = Files.getAttribute(f.path.resolve(FIXTURE_PENDING_12ADAC54), "unix:dev");
      f.root.publishChild(FIXTURE_PENDING_12ADAC54, FIXTURE_READY_40EC7F71);
      assertEquals(
          List.of(
              FIXTURE_OPENDIRECTORY_9E885716,
              FIXTURE_PUBLISH_69201707,
              FIXTURE_SYNC_5CFA1A73,
              FIXTURE_CLOSE_97959247),
          f.events);
      assertEquals(inode, Files.getAttribute(f.path.resolve(FIXTURE_READY_40EC7F71), "unix:ino"));
      assertEquals(device, Files.getAttribute(f.path.resolve(FIXTURE_READY_40EC7F71), "unix:dev"));
      assertArrayEquals(
          CONTENT, Files.readAllBytes(f.path.resolve(FIXTURE_READY_CONTENT_F3A9BB35)));
      assertFalse(Files.exists(f.path.resolve(FIXTURE_PENDING_12ADAC54)));
      f.released();
    }
  }

  @Test
  void noReplaceAndSourceType() throws Exception {
    for (String type : List.of("directory", FIXTURE_FILE_BFDDE6F5, FIXTURE_SYMLINK_36F374CF)) {
      try (var f = new Fixture(temporary)) {
        f.seed(FIXTURE_PENDING_12ADAC54, CONTENT);
        Path ready = f.path.resolve(FIXTURE_READY_40EC7F71);
        if (type.equals("directory")) f.seed(FIXTURE_READY_40EC7F71, new byte[] {9});
        else if (type.equals(FIXTURE_FILE_BFDDE6F5)) Files.write(ready, new byte[] {9});
        else {
          Files.write(f.path.resolve(FIXTURE_OUTSIDE_F78EA721), new byte[] {9});
          Files.createSymbolicLink(ready, f.path.resolve(FIXTURE_OUTSIDE_F78EA721));
        }
        failure(
            StorageIoException.Reason.COLLISION,
            () -> f.root.publishChild(FIXTURE_PENDING_12ADAC54, FIXTURE_READY_40EC7F71));
        assertArrayEquals(
            CONTENT, Files.readAllBytes(f.path.resolve(FIXTURE_PENDING_CONTENT_83FC1E31)));
        assertArrayEquals(
            new byte[] {9},
            Files.readAllBytes(type.equals("directory") ? ready.resolve("content") : ready));
        if (type.equals(FIXTURE_SYMLINK_36F374CF)) assertTrue(Files.isSymbolicLink(ready));
        f.released();
      }
    }
    for (String type : List.of("missing", FIXTURE_FILE_BFDDE6F5, FIXTURE_SYMLINK_36F374CF)) {
      try (var f = new Fixture(temporary)) {
        if (type.equals(FIXTURE_FILE_BFDDE6F5))
          Files.write(f.path.resolve(FIXTURE_PENDING_12ADAC54), CONTENT);
        if (type.equals(FIXTURE_SYMLINK_36F374CF)) {
          f.seed(FIXTURE_OUTSIDE_F78EA721, CONTENT);
          Files.createSymbolicLink(
              f.path.resolve(FIXTURE_PENDING_12ADAC54), f.path.resolve(FIXTURE_OUTSIDE_F78EA721));
        }
        failure(
            type.equals("missing")
                ? StorageIoException.Reason.MISSING
                : StorageIoException.Reason.UNAVAILABLE,
            () -> f.root.publishChild(FIXTURE_PENDING_12ADAC54, FIXTURE_READY_40EC7F71));
        assertFalse(Files.exists(f.path.resolve(FIXTURE_READY_40EC7F71)));
        if (type.equals(FIXTURE_FILE_BFDDE6F5))
          assertArrayEquals(CONTENT, Files.readAllBytes(f.path.resolve(FIXTURE_PENDING_12ADAC54)));
        if (type.equals(FIXTURE_SYMLINK_36F374CF))
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
        assertThrows(
            IllegalArgumentException.class,
            () -> f.root.publishChild(name, FIXTURE_READY_40EC7F71));
        assertThrows(
            IllegalArgumentException.class,
            () -> f.root.publishChild(FIXTURE_PENDING_12ADAC54, name));
      }
      assertThrows(IllegalArgumentException.class, () -> f.root.publishChild("same", "same"));
      assertThrows(
          NullPointerException.class, () -> f.root.publishChild(null, FIXTURE_READY_40EC7F71));
      assertThrows(
          NullPointerException.class, () -> f.root.publishChild(FIXTURE_PENDING_12ADAC54, null));
      assertTrue(f.events.isEmpty());
      f.root.close();
      f.events.clear();
      failure(
          StorageIoException.Reason.UNAVAILABLE,
          () -> f.root.publishChild(FIXTURE_PENDING_12ADAC54, FIXTURE_READY_40EC7F71));
      assertTrue(f.events.isEmpty());
    } finally {
      f.close();
    }
  }

  @Test
  void everyNativeFailure() throws Exception {
    for (String point :
        List.of(
            FIXTURE_OPENDIRECTORY_9E885716,
            FIXTURE_PUBLISH_69201707,
            FIXTURE_SYNC_5CFA1A73,
            FIXTURE_CLOSE_97959247)) {
      for (int kind = 0; kind < 3; kind++) {
        try (var f = new Fixture(temporary)) {
          f.seed(FIXTURE_PENDING_12ADAC54, CONTENT);
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
                () -> f.root.publishChild(FIXTURE_PENDING_12ADAC54, FIXTURE_READY_40EC7F71));
          else
            assertSame(
                expected,
                assertThrows(
                    expected.getClass(),
                    () -> f.root.publishChild(FIXTURE_PENDING_12ADAC54, FIXTURE_READY_40EC7F71)));
          assertEquals(
              point.equals(FIXTURE_OPENDIRECTORY_9E885716) ? 0 : 1,
              Collections.frequency(f.events, FIXTURE_CLOSE_97959247));
          boolean renamed =
              point.equals(FIXTURE_SYNC_5CFA1A73) || point.equals(FIXTURE_CLOSE_97959247);
          assertArrayEquals(
              CONTENT,
              Files.readAllBytes(
                  f.path.resolve(
                      renamed
                          ? FIXTURE_READY_CONTENT_F3A9BB35
                          : FIXTURE_PENDING_CONTENT_83FC1E31)));
          f.released();
        }
      }
    }
  }

  @Test
  void uncertainPublication() throws Exception {
    for (String point : List.of(FIXTURE_SYNC_5CFA1A73, FIXTURE_CLOSE_97959247)) {
      try (var f = new Fixture(temporary)) {
        f.seed(FIXTURE_PENDING_12ADAC54, CONTENT);
        f.faults.put(point, new StorageIoException(StorageIoException.Reason.UNAVAILABLE));
        failure(
            StorageIoException.Reason.UNAVAILABLE,
            () -> f.root.publishChild(FIXTURE_PENDING_12ADAC54, FIXTURE_READY_40EC7F71));
        assertFalse(Files.exists(f.path.resolve(FIXTURE_PENDING_12ADAC54)));
        assertArrayEquals(
            CONTENT, Files.readAllBytes(f.path.resolve(FIXTURE_READY_CONTENT_F3A9BB35)));
        f.faults.clear();
        failure(
            StorageIoException.Reason.MISSING,
            () -> f.root.publishChild(FIXTURE_PENDING_12ADAC54, FIXTURE_READY_40EC7F71));
        assertArrayEquals(
            CONTENT, Files.readAllBytes(f.path.resolve(FIXTURE_READY_CONTENT_F3A9BB35)));
        f.released();
      }
    }
  }

  @Test
  void compoundFailures() throws Exception {
    for (int primaryKind = 0; primaryKind < 3; primaryKind++) {
      for (int closeKind = 0; closeKind < 4; closeKind++) {
        try (var f = new Fixture(temporary)) {
          f.seed(FIXTURE_PENDING_12ADAC54, CONTENT);
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
          f.faults.put(FIXTURE_PUBLISH_69201707, primary);
          f.faults.put(FIXTURE_CLOSE_97959247, secondary);
          if (primaryKind == 0 && (closeKind == 0 || closeKind == 3))
            failure(
                StorageIoException.Reason.UNAVAILABLE,
                () -> f.root.publishChild(FIXTURE_PENDING_12ADAC54, FIXTURE_READY_40EC7F71));
          else {
            Throwable expected = primaryKind == 0 ? secondary : primary;
            Throwable actual =
                assertThrows(
                    expected.getClass(),
                    () -> f.root.publishChild(FIXTURE_PENDING_12ADAC54, FIXTURE_READY_40EC7F71));
            assertSame(expected, actual);
            assertEquals(primaryKind == 0 ? 0 : 1, actual.getSuppressed().length);
            if (primaryKind != 0)
              assertInstanceOf(StorageIoException.class, actual.getSuppressed()[0]);
          }
          assertArrayEquals(
              CONTENT, Files.readAllBytes(f.path.resolve(FIXTURE_PENDING_CONTENT_83FC1E31)));
          assertEquals(1, Collections.frequency(f.events, FIXTURE_CLOSE_97959247));
          f.released();
        }
      }
    }
  }

  @Test
  void retainedParentCapability() throws Exception {
    try (var f = new Fixture(temporary)) {
      f.seed(FIXTURE_PENDING_12ADAC54, CONTENT);
      Path saved = f.path.resolveSibling("saved");
      Files.move(f.path, saved);
      Files.createDirectory(f.path);
      f.seed(FIXTURE_PENDING_12ADAC54, new byte[] {9});
      f.root.publishChild(FIXTURE_PENDING_12ADAC54, FIXTURE_READY_40EC7F71);
      assertArrayEquals(CONTENT, Files.readAllBytes(saved.resolve(FIXTURE_READY_CONTENT_F3A9BB35)));
      assertArrayEquals(
          new byte[] {9}, Files.readAllBytes(f.path.resolve(FIXTURE_PENDING_CONTENT_83FC1E31)));
      assertFalse(Files.exists(f.path.resolve(FIXTURE_READY_40EC7F71)));
      f.released();
    }
  }

  @Test
  void concurrentNoReplace() throws Exception {
    try (var f = new Fixture(temporary);
        var executor = Executors.newVirtualThreadPerTaskExecutor()) {
      for (int i = 0; i < 8; i++) f.seed(FIXTURE_PENDING_12ADAC54 + i, new byte[] {(byte) i});
      List<Future<Boolean>> results = new ArrayList<>();
      for (int i = 0; i < 8; i++) {
        String source = FIXTURE_PENDING_12ADAC54 + i;
        results.add(
            executor.submit(
                () -> {
                  try {
                    f.root.publishChild(source, FIXTURE_READY_40EC7F71);
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
      int winner = Files.readAllBytes(f.path.resolve(FIXTURE_READY_CONTENT_F3A9BB35))[0];
      for (int i = 0; i < 8; i++) {
        if (i == winner) assertFalse(Files.exists(f.path.resolve(FIXTURE_PENDING_12ADAC54 + i)));
        else
          assertArrayEquals(
              new byte[] {(byte) i},
              Files.readAllBytes(f.path.resolve(FIXTURE_PENDING_12ADAC54 + i + "/content")));
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
                    if (!Set.of(
                            "openRoot",
                            FIXTURE_OPENDIRECTORY_9E885716,
                            FIXTURE_PUBLISH_69201707,
                            FIXTURE_SYNC_5CFA1A73,
                            FIXTURE_CLOSE_97959247)
                        .contains(name))
                      throw new AssertionError("unapproved directory mutation " + name);
                    if (!name.equals(FIXTURE_CLOSE_97959247)) point(name);
                    Object result;
                    try {
                      result = method.invoke(nativeCalls, args);
                    } catch (InvocationTargetException failure) {
                      throw failure.getCause();
                    }
                    if (name.equals(FIXTURE_CLOSE_97959247)) {
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
