package dev.codex.schubert.nk.storage;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.lang.reflect.InvocationHandler;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Proxy;
import java.nio.file.Files;
import java.nio.file.LinkOption;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.function.Executable;
import org.junit.jupiter.api.io.TempDir;

/** NK-OPS-001/BAK/BKO/UI251/SS333 7.6/341 6.1/343; SSC068/PG186; CDIR001..008. */
final class PrivateChildDirectoryTest {
  private static final String FIXTURE_CREATEPRIVATEDIRECTORY_589F758D = "createPrivateDirectory";
  private static final String FIXTURE_OPENDIRECTORY_9E885716 = "openDirectory";
  private static final String FIXTURE_SYNC_CHILD_D71164AB = "sync-child";
  private static final String FIXTURE_SYNC_PARENT_02AB780D = "sync-parent";
  private static final String FIXTURE_UNIX_INO_19AF1B90 = "unix:ino";
  private static final String FIXTURE_CLOSE_97959247 = "close";
  private static final String FIXTURE_PARTIAL_8AC24611 = "partial";
  private static final String FIXTURE_NEW_80270E39 = "new";
  @TempDir Path temporary;

  @Test
  void nativePrivateCreation() throws Exception {
    try (var f = new Fixture(temporary)) {
      Object inode;
      try (var child = f.root.createPrivateChild("new.part")) {
        assertEquals(
            List.of(
                FIXTURE_CREATEPRIVATEDIRECTORY_589F758D,
                FIXTURE_OPENDIRECTORY_9E885716,
                FIXTURE_SYNC_CHILD_D71164AB,
                FIXTURE_SYNC_PARENT_02AB780D),
            f.events);
        Path created = f.path.resolve("new.part");
        assertEquals(0700, ((Integer) Files.getAttribute(created, "unix:mode")) & 0777);
        assertEquals(
            Files.getAttribute(f.path, "unix:uid"), Files.getAttribute(created, "unix:uid"));
        assertEquals(
            Files.getAttribute(f.path, "unix:dev"), Files.getAttribute(created, "unix:dev"));
        try (var entries = Files.list(created)) {
          assertEquals(0, entries.count());
        }
        inode = Files.getAttribute(created, FIXTURE_UNIX_INO_19AF1B90);
        Object held = child.atDirectory(p -> Files.getAttribute(p, FIXTURE_UNIX_INO_19AF1B90));
        assertEquals(inode, held);
        assertEquals(2, f.live.size());
        child.atDirectory(
            p -> {
              Files.write(p.resolve("public.txt"), new byte[] {65, 10});
              return true;
            });
        assertArrayEquals(new byte[] {65, 10}, Files.readAllBytes(created.resolve("public.txt")));
      }
      assertEquals(
          inode, Files.getAttribute(f.path.resolve("new.part"), FIXTURE_UNIX_INO_19AF1B90));
      assertEquals(1, Collections.frequency(f.events, FIXTURE_CLOSE_97959247));
      f.released();
      // The child remains usable after the borrowed parent's owner closes its own FD.
      try (var child = f.root.createPrivateChild("independent.part")) {
        f.tracking = false;
        f.root.close();
        assertTrue(child.<Boolean>atDirectory(Files::isDirectory));
      }
      assertTrue(f.live.isEmpty());
    }
  }

  @Test
  void existingEntriesPreserved() throws Exception {
    for (String kind : List.of("directory", "file", "symlink")) {
      try (var f = new Fixture(temporary)) {
        Path entry = f.path.resolve("existing");
        Path target = f.path.resolve("outside");
        Files.write(target, new byte[] {9, 10});
        if (kind.equals("directory")) Files.createDirectory(entry);
        else if (kind.equals("file")) Files.write(entry, new byte[] {65, 10});
        else Files.createSymbolicLink(entry, target);
        var before =
            Files.readAttributes(entry, "unix:ino,mode,uid,gid", LinkOption.NOFOLLOW_LINKS);
        fail(StorageIoException.Reason.COLLISION, () -> f.root.createPrivateChild("existing"));
        assertEquals(List.of(FIXTURE_CREATEPRIVATEDIRECTORY_589F758D), f.events);
        assertEquals(
            before,
            Files.readAttributes(entry, "unix:ino,mode,uid,gid", LinkOption.NOFOLLOW_LINKS));
        assertArrayEquals(new byte[] {9, 10}, Files.readAllBytes(target));
        if (kind.equals("file")) assertArrayEquals(new byte[] {65, 10}, Files.readAllBytes(entry));
        if (kind.equals("directory"))
          try (var entries = Files.list(entry)) {
            assertEquals(0, entries.count());
          }
        if (kind.equals("symlink")) assertEquals(target, Files.readSymbolicLink(entry));
        f.released();
      }
    }
  }

  @Test
  void nameNullAndClosed() throws Exception {
    try (var f = new Fixture(temporary)) {
      assertThrows(NullPointerException.class, () -> f.root.createPrivateChild(null));
      for (String name : List.of("", ".", "..", "a/b", "a\0b"))
        assertThrows(IllegalArgumentException.class, () -> f.root.createPrivateChild(name));
      assertEquals(List.of(), f.events);
      f.root.close();
      f.events.clear();
      fail(StorageIoException.Reason.UNAVAILABLE, () -> f.root.createPrivateChild("closed"));
      assertEquals(List.of(), f.events);
    }
    var nativeCalls = LinuxDirectoryCalls.create();
    assertThrows(NullPointerException.class, () -> nativeCalls.createPrivateDirectory(-1, null));
    for (String name : List.of("", ".", "..", "a/b", "a\0b"))
      assertThrows(
          IllegalArgumentException.class, () -> nativeCalls.createPrivateDirectory(-1, name));
    fail(
        StorageIoException.Reason.UNAVAILABLE,
        () -> nativeCalls.createPrivateDirectory(-1, "valid"));
    try (var f = new Fixture(temporary)) {
      fail(
          StorageIoException.Reason.UNAVAILABLE,
          () -> nativeCalls.createPrivateDirectory(f.rootFd, "x".repeat(256)));
      try (var entries = Files.list(f.path)) {
        assertEquals(0, entries.count());
      }
      f.released();
    }
  }

  @Test
  void everyNativeFailure() throws Exception {
    for (String point :
        List.of(
            FIXTURE_CREATEPRIVATEDIRECTORY_589F758D,
            FIXTURE_OPENDIRECTORY_9E885716,
            FIXTURE_SYNC_CHILD_D71164AB,
            FIXTURE_SYNC_PARENT_02AB780D))
      for (int kind = 0; kind < 4; kind++) {
        try (var f = new Fixture(temporary)) {
          Throwable expected = fault(kind);
          f.faults.put(point, expected);
          if (kind == 0)
            fail(
                StorageIoException.Reason.UNAVAILABLE,
                () -> f.root.createPrivateChild(FIXTURE_PARTIAL_8AC24611));
          else
            assertSame(
                expected,
                assertThrows(
                    expected.getClass(),
                    () -> f.root.createPrivateChild(FIXTURE_PARTIAL_8AC24611)));
          boolean acquired = point.startsWith("sync-");
          assertEquals(acquired ? 1 : 0, Collections.frequency(f.events, FIXTURE_CLOSE_97959247));
          assertEquals(
              !point.equals(FIXTURE_CREATEPRIVATEDIRECTORY_589F758D),
              Files.exists(f.path.resolve(FIXTURE_PARTIAL_8AC24611)));
          if (Files.exists(f.path.resolve(FIXTURE_PARTIAL_8AC24611))) {
            assertEquals(
                0700,
                ((Integer)
                        Files.getAttribute(f.path.resolve(FIXTURE_PARTIAL_8AC24611), "unix:mode"))
                    & 0777);
            try (var entries = Files.list(f.path.resolve(FIXTURE_PARTIAL_8AC24611))) {
              assertEquals(0, entries.count());
            }
          }
          f.released();
        }
      }
  }

  @Test
  void compoundFailures() throws Exception {
    for (String point : List.of(FIXTURE_SYNC_CHILD_D71164AB, FIXTURE_SYNC_PARENT_02AB780D))
      for (int primaryKind = 0; primaryKind < 4; primaryKind++)
        for (int closeKind = 0; closeKind < 5; closeKind++) {
          try (var f = new Fixture(temporary)) {
            Throwable primary = fault(primaryKind);
            Throwable secondary = closeKind == 4 ? primary : fault(closeKind);
            f.faults.put(point, primary);
            f.faults.put(FIXTURE_CLOSE_97959247, secondary);
            if (primaryKind == 0 && (closeKind == 0 || closeKind == 4))
              fail(
                  StorageIoException.Reason.UNAVAILABLE,
                  () -> f.root.createPrivateChild(FIXTURE_PARTIAL_8AC24611));
            else {
              Throwable expected = primaryKind == 0 ? secondary : primary;
              Throwable actual =
                  assertThrows(
                      expected.getClass(),
                      () -> f.root.createPrivateChild(FIXTURE_PARTIAL_8AC24611));
              assertSame(expected, actual);
              assertEquals(primaryKind == 0 ? 0 : 1, actual.getSuppressed().length);
              if (primaryKind != 0) {
                var safe = assertInstanceOf(StorageIoException.class, actual.getSuppressed()[0]);
                assertNull(safe.getCause());
                assertEquals(0, safe.getSuppressed().length);
              }
            }
            assertEquals(1, Collections.frequency(f.events, FIXTURE_CLOSE_97959247));
            assertTrue(Files.isDirectory(f.path.resolve(FIXTURE_PARTIAL_8AC24611)));
            f.released();
          }
        }
  }

  @Test
  void retainedParentCapability() throws Exception {
    try (var f = new Fixture(temporary)) {
      Path old = f.path.resolveSibling("original");
      Files.move(f.path, old);
      Files.createDirectory(f.path);
      try (var child = f.root.createPrivateChild(FIXTURE_NEW_80270E39)) {
        Object held = child.atDirectory(p -> Files.getAttribute(p, FIXTURE_UNIX_INO_19AF1B90));
        assertEquals(
            Files.getAttribute(old.resolve(FIXTURE_NEW_80270E39), FIXTURE_UNIX_INO_19AF1B90), held);
        assertFalse(Files.exists(f.path.resolve(FIXTURE_NEW_80270E39)));
      }
      f.released();
    }
  }

  @Test
  void unsupportedAdapter() throws Exception {
    try (var f = new Fixture(temporary)) {
      f.unsupported = true;
      fail(
          StorageIoException.Reason.UNAVAILABLE,
          () -> f.root.createPrivateChild(FIXTURE_NEW_80270E39));
      assertEquals(List.of(FIXTURE_CREATEPRIVATEDIRECTORY_589F758D), f.events);
      try (var entries = Files.list(f.path)) {
        assertEquals(0, entries.count());
      }
      f.released();
    }
  }

  @Test
  void concurrentNewOnly() throws Exception {
    try (var f = new Fixture(temporary);
        var pool = Executors.newFixedThreadPool(8)) {
      List<Future<Object>> results = new ArrayList<>();
      synchronized (f.root) {
        for (int i = 0; i < 8; i++)
          results.add(
              pool.submit(
                  () -> {
                    try (var child = f.root.createPrivateChild("single")) {
                      return child.atDirectory(
                          p -> Files.getAttribute(p, FIXTURE_UNIX_INO_19AF1B90));
                    } catch (StorageIoException failure) {
                      assertEquals(StorageIoException.Reason.COLLISION, failure.reason());
                      return null;
                    }
                  }));
        int wins = 0;
        for (var result : results) {
          Object inode = result.get(10, TimeUnit.SECONDS);
          if (inode != null) {
            wins++;
            assertEquals(
                Files.getAttribute(f.path.resolve("single"), FIXTURE_UNIX_INO_19AF1B90), inode);
          }
        }
        assertEquals(1, wins);
      }
      assertEquals(8, Collections.frequency(f.events, FIXTURE_CREATEPRIVATEDIRECTORY_589F758D));
      assertEquals(1, Collections.frequency(f.events, FIXTURE_OPENDIRECTORY_9E885716));
      assertEquals(1, Collections.frequency(f.events, FIXTURE_SYNC_CHILD_D71164AB));
      assertEquals(1, Collections.frequency(f.events, FIXTURE_SYNC_PARENT_02AB780D));
      assertEquals(1, Collections.frequency(f.events, FIXTURE_CLOSE_97959247));
      f.released();
    }
  }

  private static Throwable fault(int kind) {
    return switch (kind) {
      case 0 -> new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
      case 1 -> new IllegalStateException("public synthetic fault");
      case 2 -> new NullPointerException("public synthetic fault");
      default -> new AssertionError("public synthetic fault");
    };
  }

  private static void fail(StorageIoException.Reason reason, Executable action) {
    var actual = assertThrows(StorageIoException.class, action);
    assertEquals(reason, actual.reason());
    assertNull(actual.getCause());
    assertEquals(0, actual.getSuppressed().length);
  }

  private static final class Fixture implements AutoCloseable {
    final Path path;
    final OwnedTransferDirectory root;
    final Set<Integer> live = ConcurrentHashMap.newKeySet();
    final List<String> events = Collections.synchronizedList(new ArrayList<>());
    final Map<String, Throwable> faults = new ConcurrentHashMap<>();
    int rootFd = -1;
    boolean tracking;
    boolean unsupported;

    Fixture(Path temporary) throws Exception {
      path =
          Files.createDirectory(
              Files.createTempDirectory(temporary, "private-child-").resolve("root"));
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
                            FIXTURE_CREATEPRIVATEDIRECTORY_589F758D,
                            "sync",
                            FIXTURE_CLOSE_97959247)
                        .contains(name)) throw new AssertionError("unapproved mutation " + name);
                    String point =
                        name.equals("sync")
                            ? ((Integer) args[0] == rootFd
                                ? FIXTURE_SYNC_PARENT_02AB780D
                                : FIXTURE_SYNC_CHILD_D71164AB)
                            : name;
                    if (!name.equals(FIXTURE_CLOSE_97959247)) point(point);
                    // Bookkeeping is atomic with native close/open to avoid numeric FD reuse races.
                    synchronized (live) {
                      Object result;
                      try {
                        result =
                            unsupported && name.equals(FIXTURE_CREATEPRIVATEDIRECTORY_589F758D)
                                ? InvocationHandler.invokeDefault(proxy, method, args)
                                : method.invoke(nativeCalls, args);
                      } catch (InvocationTargetException failure) {
                        throw failure.getCause();
                      }
                      if (name.equals(FIXTURE_CLOSE_97959247)) {
                        assertTrue(live.remove((Integer) args[0]));
                        point(point);
                      } else if (name.startsWith("open")) assertTrue(live.add((Integer) result));
                      return result;
                    }
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
