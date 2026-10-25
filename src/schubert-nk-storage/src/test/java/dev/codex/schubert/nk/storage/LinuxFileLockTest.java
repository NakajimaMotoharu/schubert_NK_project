package dev.codex.schubert.nk.storage;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.io.IOException;
import java.lang.foreign.Linker;
import java.lang.foreign.MemoryLayout;
import java.lang.foreign.StructLayout;
import java.lang.foreign.ValueLayout;
import java.nio.channels.FileChannel;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.concurrent.Callable;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.CyclicBarrier;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** NK-OPS-001/PT-OPS-FLOCK-001..008; SS311/341/343; actual isolated Linux flock interop. */
final class LinuxFileLockTest {
  @TempDir Path root;
  private static final StructLayout STATE = Linker.Option.captureStateLayout();
  private static final long ERRNO =
      STATE.byteOffset(MemoryLayout.PathElement.groupElement("errno"));

  @BeforeEach
  void fixture() throws IOException {
    Files.write(root.resolve("lock"), new byte[] {3, 5, 8});
  }

  @Test
  void nativeRoundTrip() throws Exception {
    var lock = LinuxFileLock.create();
    held(
        path -> {
          assertEquals(Optional.of(42), lock.tryExclusive(path, () -> 42));
          assertEquals(Optional.of(43), lock.tryExclusive(path, () -> 43));
          assertArrayEquals(new byte[] {3, 5, 8}, Files.readAllBytes(path));
          assertTrue(Files.exists(path));
          return true;
        });
    assertArrayEquals(new byte[] {3, 5, 8}, Files.readAllBytes(root.resolve("lock")));
  }

  @Test
  void externalFlockInteroperability() throws Exception {
    var lock = LinuxFileLock.create();
    held(
        path -> {
          assertEquals(
              Optional.of(7),
              lock.tryExclusive(
                  path,
                  () -> {
                    assertEquals(20, assertDoesNotThrow(() -> external(root.resolve("lock"))));
                    return 7;
                  }));
          assertEquals(0, external(root.resolve("lock")));
          try (var executor = Executors.newSingleThreadExecutor()) {
            var child =
                new ProcessBuilder(
                        "/usr/bin/flock",
                        "-x",
                        "-n",
                        "-E",
                        "20",
                        root.resolve("lock").toString(),
                        "/bin/sh",
                        "-c",
                        "printf 'READY\\n'; read -r ignored || :")
                    .start();
            try (var reader = child.inputReader();
                var writer = child.getOutputStream()) {
              try {
                assertEquals("READY", executor.submit(reader::readLine).get(5, TimeUnit.SECONDS));
                var calls = new AtomicInteger();
                assertEquals(
                    Optional.empty(), lock.tryExclusive(path, () -> calls.incrementAndGet()));
                assertEquals(0, calls.get());
                writer.write('\n');
                writer.flush();
                assertTrue(child.waitFor(5, TimeUnit.SECONDS));
                assertEquals(0, child.exitValue());
              } finally {
                if (child.isAlive()) child.destroy();
              }
            }
          }
          assertEquals(Optional.of(9), lock.tryExclusive(path, () -> 9));
          return true;
        });
  }

  @Test
  void fcntlIsNotFlock() throws Exception {
    try (var channel = FileChannel.open(root.resolve("lock"), StandardOpenOption.WRITE);
        var fcntl = channel.lock()) {
      assertTrue(fcntl.isValid());
      assertEquals(
          0, external(root.resolve("lock"))); // Native Linux flock and fcntl do not interact.
      held(
          path -> {
            assertEquals(Optional.of(1), LinuxFileLock.create().tryExclusive(path, () -> 1));
            return true;
          });
      assertTrue(fcntl.isValid());
    }
  }

  @Test
  void callbackFailureAndClose() throws Exception {
    var lock = LinuxFileLock.create();
    held(
        path -> {
          assertUnavailable(
              assertThrows(
                  StorageIoException.class,
                  () ->
                      lock.tryExclusive(
                          path,
                          () -> {
                            throw new IOException("SECRET_CANARY");
                          })));
          var runtime = new IllegalStateException("programming canary");
          assertSame(
              runtime,
              assertThrows(
                  IllegalStateException.class,
                  () ->
                      lock.tryExclusive(
                          path,
                          () -> {
                            throw runtime;
                          })));
          assertThrows(NullPointerException.class, () -> lock.tryExclusive(path, () -> null));
          assertEquals(0, external(root.resolve("lock")));
          assertEquals(Optional.of(1), lock.tryExclusive(path, () -> 1));
          return true;
        });
    for (boolean failOperation : List.of(false, true)) {
      var calls = new ArrayList<String>();
      var broken = fake(17, 0, 0, -1, calls);
      assertUnavailable(
          assertThrows(
              StorageIoException.class,
              () ->
                  broken.tryExclusive(
                      Path.of("/proc/self/fd/9"),
                      () -> {
                        calls.add("operation");
                        if (failOperation) throw new IOException("SECRET_CANARY");
                        return 1;
                      })));
      assertEquals(List.of("open", "flock:17", "operation", "close:17"), calls);
    }
    var calls = new ArrayList<String>();
    assertUnavailable(
        assertThrows(
            StorageIoException.class,
            () ->
                fake(17, -1, 11, -1, calls)
                    .tryExclusive(
                        Path.of("/proc/self/fd/9"),
                        () -> {
                          throw new AssertionError("not acquired");
                        })));
    assertEquals(List.of("open", "flock:17", "close:17"), calls);
  }

  @Test
  void nativeErrorsAndFlags() throws Exception {
    // BUG195: owned descriptor cleanup preserves unknown identity, even self-rethrow.
    for (boolean known : new boolean[] {false, true})
      for (Throwable unknown :
          List.of(
              new IllegalStateException("public unknown"),
              new NullPointerException("public unknown"),
              new AssertionError("public unknown"))) {
        var order = new ArrayList<String>();
        var scoped =
            new LinuxFileLock(
                (state, path, flags, mode) -> {
                  assertEquals(0x80000, flags);
                  assertEquals(0, mode);
                  order.add("open");
                  return 17;
                },
                (state, descriptor, flags) -> {
                  assertEquals(17, descriptor);
                  assertEquals(6, flags);
                  order.add("flock");
                  return 0;
                },
                (state, descriptor) -> {
                  assertEquals(17, descriptor);
                  order.add("close");
                  if (unknown instanceof RuntimeException failure) throw failure;
                  throw (Error) unknown;
                });
        assertSame(
            unknown,
            assertThrows(
                unknown.getClass(),
                () ->
                    scoped.tryExclusive(
                        Path.of("/proc/self/fd/9"),
                        () -> {
                          order.add("body");
                          if (known) throw new IOException("public I/O");
                          if (unknown instanceof RuntimeException failure) throw failure;
                          throw (Error) unknown;
                        })));
        assertEquals(List.of("open", "flock", "body", "close"), order);
        assertEquals(known ? 0 : 1, unknown.getSuppressed().length);
        for (Throwable secondary : unknown.getSuppressed())
          assertUnavailable(assertInstanceOf(StorageIoException.class, secondary));
      }
    for (int error : List.of(11, 4, 9, 22, 37)) {
      var calls = new ArrayList<String>();
      var lock = fake(17, -1, error, 0, calls);
      if (error == 11)
        assertEquals(
            Optional.empty(),
            lock.tryExclusive(
                Path.of("/proc/self/fd/9"),
                () -> {
                  throw new AssertionError("no operation");
                }));
      else
        assertUnavailable(
            assertThrows(
                StorageIoException.class,
                () ->
                    lock.tryExclusive(
                        Path.of("/proc/self/fd/9"),
                        () -> {
                          throw new AssertionError("no operation");
                        })));
      assertEquals(List.of("open", "flock:17", "close:17"), calls);
    }
    var calls = new ArrayList<String>();
    assertUnavailable(
        assertThrows(
            StorageIoException.class,
            () -> fake(-1, 0, 0, 0, calls).tryExclusive(Path.of("/proc/self/fd/9"), () -> 1)));
    assertEquals(List.of("open"), calls);
    calls.clear();
    assertUnavailable(
        assertThrows(
            StorageIoException.class,
            () -> fake(17, 1, 11, 0, calls).tryExclusive(Path.of("/proc/self/fd/9"), () -> 1)));
    assertEquals(List.of("open", "flock:17", "close:17"), calls);
    calls.clear();
    assertEquals(
        Optional.of(2), fake(0, 0, 0, 0, calls).tryExclusive(Path.of("/proc/self/fd/0"), () -> 2));
    assertEquals(List.of("open", "flock:0", "close:0"), calls);
    assertUnavailable(
        assertThrows(
            StorageIoException.class,
            () ->
                LinuxFileLock.create().tryExclusive(Path.of("/proc/self/fd/2147483647"), () -> 1)));
  }

  @Test
  void inputAndPlatformContracts() throws Exception {
    var lock = fake(17, 0, 0, 0, new ArrayList<>());
    for (String name :
        List.of(
            "lock",
            "/tmp/lock",
            "/proc/1/fd/9",
            "/proc/self/fd",
            "/proc/self/fd/-1",
            "/proc/self/fd/+1",
            "/proc/self/fd/01",
            "/proc/self/fd/2147483648",
            "/proc/self/fd/99999999999",
            "/proc/self/fd/9/child",
            "/proc/self/fd/../9")) {
      var failure =
          assertThrows(
              IllegalArgumentException.class, () -> lock.tryExclusive(Path.of(name), () -> 1));
      assertEquals("invalid held file capability", failure.getMessage());
      assertNull(failure.getCause());
    }
    assertThrows(NullPointerException.class, () -> lock.tryExclusive(null, () -> 1));
    assertThrows(
        NullPointerException.class, () -> lock.tryExclusive(Path.of("/proc/self/fd/9"), null));
    var symbols = Linker.nativeLinker().defaultLookup();
    assertThrows(NullPointerException.class, () -> LinuxFileLock.create(null, "amd64", symbols));
    assertThrows(NullPointerException.class, () -> LinuxFileLock.create("Linux", null, symbols));
    assertThrows(NullPointerException.class, () -> LinuxFileLock.create("Linux", "amd64", null));
    for (String os : List.of("Windows", "linux", ""))
      assertThrows(IllegalStateException.class, () -> LinuxFileLock.create(os, "amd64", symbols));
    assertThrows(
        IllegalStateException.class, () -> LinuxFileLock.create("Linux", "unknown", symbols));
    for (String missing : List.of("open", "flock", "close")) {
      var failure =
          assertThrows(
              IllegalStateException.class,
              () ->
                  LinuxFileLock.create(
                      "Linux",
                      "amd64",
                      name -> name.equals(missing) ? Optional.empty() : symbols.find(name)));
      assertEquals("native file locking is unavailable", failure.getMessage());
    }
    for (String arch : List.of("amd64", "x86_64", "aarch64"))
      assertNotNull(LinuxFileLock.create("Linux", arch, symbols));
    LinuxFileLock.OpenCall open = (s, p, f, m) -> 1;
    LinuxFileLock.LockCall flock = (s, d, f) -> 0;
    LinuxFileLock.CloseCall close = (s, d) -> 0;
    assertThrows(NullPointerException.class, () -> new LinuxFileLock(null, flock, close));
    assertThrows(NullPointerException.class, () -> new LinuxFileLock(open, null, close));
    assertThrows(NullPointerException.class, () -> new LinuxFileLock(open, flock, null));
  }

  @Test
  void concurrentSingleWinner() throws Exception {
    var lock = LinuxFileLock.create();
    held(
        path -> {
          var barrier = new CyclicBarrier(32);
          var rejected = new CountDownLatch(31);
          try (var executor = Executors.newFixedThreadPool(32)) {
            var work = new ArrayList<Callable<Optional<Integer>>>();
            for (int i = 0; i < 32; i++) {
              work.add(
                  () -> {
                    barrier.await(10, TimeUnit.SECONDS);
                    var result =
                        lock.tryExclusive(
                            path,
                            () -> {
                              assertTrue(
                                  assertDoesNotThrow(() -> rejected.await(10, TimeUnit.SECONDS)));
                              return 1;
                            });
                    if (result.isEmpty()) rejected.countDown();
                    return result;
                  });
            }
            int winners = 0;
            for (var done : executor.invokeAll(work))
              if (done.get(10, TimeUnit.SECONDS).isPresent()) winners++;
            assertEquals(1, winners);
            assertEquals(0, rejected.getCount());
          }
          assertEquals(Optional.of(2), lock.tryExclusive(path, () -> 2));
          return true;
        });
  }

  @Test
  void retainedInodeAndDescriptorLifetime() throws Exception {
    var lock = LinuxFileLock.create();
    held(
        path -> {
          Files.move(root.resolve("lock"), root.resolve("original"));
          Files.write(root.resolve("lock"), new byte[] {1});
          assertEquals(
              Optional.of(3),
              lock.tryExclusive(
                  path,
                  () -> {
                    assertEquals(20, assertDoesNotThrow(() -> external(root.resolve("original"))));
                    assertEquals(0, assertDoesNotThrow(() -> external(root.resolve("lock"))));
                    return 3;
                  }));
          assertArrayEquals(new byte[] {3, 5, 8}, Files.readAllBytes(path));
          assertEquals(0, external(root.resolve("original")));
          assertEquals(Optional.of(4), lock.tryExclusive(path, () -> 4));
          return true;
        });
    assertArrayEquals(new byte[] {1}, Files.readAllBytes(root.resolve("lock")));
    assertArrayEquals(new byte[] {3, 5, 8}, Files.readAllBytes(root.resolve("original")));
  }

  private static LinuxFileLock fake(
      int opened, int result, int error, int closed, List<String> calls) {
    return new LinuxFileLock(
        (state, path, flags, mode) -> {
          assertTrue(path.getString(0).matches("/proc/self/fd/[0-9]+"));
          assertEquals(0x80000, flags);
          assertEquals(0, mode);
          calls.add("open");
          return opened;
        },
        (state, descriptor, flags) -> {
          assertEquals(6, flags);
          state.set(ValueLayout.JAVA_INT, ERRNO, error);
          calls.add("flock:" + descriptor);
          return result;
        },
        (state, descriptor) -> {
          calls.add("close:" + descriptor);
          return closed;
        });
  }

  private static void assertUnavailable(StorageIoException failure) {
    assertEquals(StorageIoException.Reason.UNAVAILABLE, failure.reason());
    assertEquals("transfer storage operation failed", failure.getMessage());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
  }

  private int external(Path file) throws Exception {
    var child =
        new ProcessBuilder("/usr/bin/flock", "-x", "-n", "-E", "20", file.toString(), "/bin/true")
            .start();
    try {
      assertTrue(child.waitFor(5, TimeUnit.SECONDS));
      return child.exitValue();
    } finally {
      if (child.isAlive()) child.destroy();
    }
  }

  private <T> T held(Checked<T> operation) throws Exception {
    try (var directory = OwnedTransferDirectory.open(LinuxDirectoryCalls.create(), root)) {
      return directory.atExistingEntryHandle(
          "lock", path -> assertDoesNotThrow(() -> operation.execute(path)));
    }
  }

  private interface Checked<T> {
    T execute(Path path) throws Exception;
  }
}
