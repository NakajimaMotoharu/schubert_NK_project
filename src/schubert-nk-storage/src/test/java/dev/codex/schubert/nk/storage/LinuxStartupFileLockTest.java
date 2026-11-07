package dev.codex.schubert.nk.storage;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assertions.fail;

import java.io.IOException;
import java.lang.foreign.Linker;
import java.lang.foreign.MemoryLayout;
import java.lang.foreign.StructLayout;
import java.lang.foreign.ValueLayout;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.concurrent.Callable;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.CyclicBarrier;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** PT-OPS-AFD-001..008; A-only borrowed FD, independent syscall/ownership/interop oracles. */
final class LinuxStartupFileLockTest {
  private static final int EAGAIN_ERRNO = 11;

  private static final String FIXTURE_OPEN_35FF74AE = "open";
  private static final String FIXTURE_CLOSE_128_7836A21E = "close:128";
  private static final String FIXTURE_CLOSE_17_F1422F88 = "close:17";
  private static final String FIXTURE_LOCK_E9DEB047 = "lock";
  @TempDir Path root;
  private static final StructLayout STATE = Linker.Option.captureStateLayout();
  private static final long ERRNO =
      STATE.byteOffset(MemoryLayout.PathElement.groupElement("errno"));
  private static final Path HELD = Path.of("/proc/self/fd/9");

  @Test
  void opsAfd001ReservedSameOfdScopeAndReverseClose() throws Exception {
    var f = new Fixture();
    assertEquals(
        Optional.of(42),
        f.calls()
            .tryExclusiveForStartup(
                HELD,
                fd -> {
                  assertEquals(128, fd);
                  f.events.add("body");
                  return 42;
                }));
    assertEquals(
        List.of(
            FIXTURE_OPEN_35FF74AE,
            "dup:17:1030:128",
            "flock:128:6",
            "body",
            FIXTURE_CLOSE_128_7836A21E,
            FIXTURE_CLOSE_17_F1422F88),
        f.events);
  }

  @Test
  void opsAfd002ContentionAndOtherNativeErrors() {
    for (int errno : List.of(11, 4, 9, 22, 37)) {
      var f = new Fixture();
      f.lockResult = -1;
      f.errno = errno;
      if (errno == EAGAIN_ERRNO)
        assertEquals(
            Optional.empty(),
            assertDoesNotThrow(() -> f.calls().tryExclusiveForStartup(HELD, fd -> fail())));
      else
        unavailable(
            assertThrows(
                StorageIoException.class,
                () -> f.calls().tryExclusiveForStartup(HELD, fd -> fail())));
      assertEquals(
          List.of(
              FIXTURE_OPEN_35FF74AE,
              "dup:17:1030:128",
              "flock:128:6",
              FIXTURE_CLOSE_128_7836A21E,
              FIXTURE_CLOSE_17_F1422F88),
          f.events);
    }
    var f = new Fixture();
    f.lockResult = 1;
    f.errno = 11;
    unavailable(
        assertThrows(
            StorageIoException.class, () -> f.calls().tryExclusiveForStartup(HELD, fd -> fail())));
  }

  @Test
  void opsAfd003EveryPartialAcquisitionClosesOnlyOwnedDescriptors() {
    var f = new Fixture();
    f.openResult = -1;
    unavailable(
        assertThrows(
            StorageIoException.class, () -> f.calls().tryExclusiveForStartup(HELD, fd -> fail())));
    assertEquals(List.of(FIXTURE_OPEN_35FF74AE), f.events);
    for (int reserved : List.of(-1, 17, 127, 65536)) {
      var fixture = new Fixture();
      fixture.reserved = reserved;
      unavailable(
          assertThrows(
              StorageIoException.class,
              () -> fixture.calls().tryExclusiveForStartup(HELD, fd -> fail())));
      var expected = new ArrayList<>(List.of(FIXTURE_OPEN_35FF74AE, "dup:17:1030:128"));
      if (reserved == 127 || reserved == 65536) expected.add("close:" + reserved);
      expected.add(FIXTURE_CLOSE_17_F1422F88);
      assertEquals(expected, fixture.events);
    }
    for (int closed : List.of(128, 17)) {
      var fixture = new Fixture();
      fixture.failedClose = closed;
      unavailable(
          assertThrows(
              StorageIoException.class,
              () -> fixture.calls().tryExclusiveForStartup(HELD, fd -> 1)));
      assertEquals(
          List.of(FIXTURE_CLOSE_128_7836A21E, FIXTURE_CLOSE_17_F1422F88),
          fixture.events.subList(fixture.events.size() - 2, fixture.events.size()));
    }
  }

  @Test
  void opsAfd004UnknownAndCompoundFailurePriority() {
    for (boolean knownBody : List.of(false, true))
      for (boolean unknownClose : List.of(false, true))
        for (Throwable unknown :
            List.of(
                new IllegalStateException("public unknown"),
                new AssertionError("public unknown"))) {
          var f = new Fixture();
          f.unknownClose = unknownClose ? unknown : null;
          Class<? extends Throwable> expected =
              knownBody && !unknownClose ? StorageIoException.class : unknown.getClass();
          var actual =
              assertThrows(
                  expected,
                  () ->
                      f.calls()
                          .tryExclusiveForStartup(
                              HELD,
                              fd -> {
                                if (knownBody) throw new IOException("private fixture diagnostic");
                                if (unknown instanceof RuntimeException failure) throw failure;
                                throw (Error) unknown;
                              }));
          if (actual instanceof StorageIoException failure) unavailable(failure);
          else assertSame(unknown, actual);
          assertEquals(
              List.of(FIXTURE_CLOSE_128_7836A21E, FIXTURE_CLOSE_17_F1422F88),
              f.events.subList(f.events.size() - 2, f.events.size()));
        }
  }

  @Test
  void opsAfd005InputNullMissingPortAndBindingContracts() {
    var f = new Fixture();
    var calls = f.calls();
    assertThrows(NullPointerException.class, () -> calls.tryExclusiveForStartup(null, fd -> 1));
    assertThrows(NullPointerException.class, () -> calls.tryExclusiveForStartup(HELD, null));
    assertThrows(
        IllegalArgumentException.class,
        () -> calls.tryExclusiveForStartup(Path.of("/tmp/lock"), fd -> 1));
    assertTrue(f.events.isEmpty());
    LinuxFileLock.OpenCall open = (s, p, flags, m) -> 17;
    LinuxFileLock.LockCall lock = (s, d, flags) -> 0;
    LinuxFileLock.CloseCall close = (s, d) -> 0;
    assertThrows(
        NullPointerException.class,
        () -> new LinuxFileLock(open, lock, close, (LinuxExecDescriptors.FcntlCall) null));
    assertThrows(
        IllegalStateException.class,
        () -> new LinuxFileLock(open, lock, close).tryExclusiveForStartup(HELD, fd -> 1));
    var symbols = Linker.nativeLinker().defaultLookup();
    assertThrows(
        IllegalStateException.class,
        () ->
            LinuxFileLock.create(
                "Linux",
                "amd64",
                name -> name.equals("fcntl") ? Optional.empty() : symbols.find(name)));
    var fixture = new Fixture();
    fixture.reserved = 65535;
    assertEquals(
        Optional.of(65535),
        assertDoesNotThrow(
            () ->
                fixture
                    .calls()
                    .tryExclusiveForStartup(
                        HELD,
                        fd -> {
                          assertEquals(65535, fd);
                          return 65535;
                        })));
  }

  @Test
  void opsAfd006RealNativeFlockAndSeparateImmutableProof() throws Exception {
    Files.write(root.resolve(FIXTURE_LOCK_E9DEB047), new byte[0]);
    try (var directory = OwnedTransferDirectory.open(LinuxDirectoryCalls.create(), root)) {
      boolean result =
          directory.atExistingEntryHandle(
              FIXTURE_LOCK_E9DEB047,
              held ->
                  LinuxFileLock.create()
                      .tryExclusiveForStartup(
                          held,
                          fd -> {
                            assertTrue(fd >= 128 && fd <= 65535);
                            assertEquals(
                                20,
                                assertDoesNotThrow(
                                    () -> external(root.resolve(FIXTURE_LOCK_E9DEB047))));
                            byte[] literal = new byte[] {65, 66, 67};
                            return LinuxSealedProof.create()
                                .withProof(
                                    literal,
                                    proof -> {
                                      assertNotEquals(fd, proof);
                                      assertArrayEquals(
                                          literal, LinuxSealedProof.create().read(proof));
                                      LinuxExecDescriptors.create()
                                          .withInherited(
                                              fd,
                                              proof,
                                              () ->
                                                  assertEquals(
                                                      20,
                                                      assertDoesNotThrow(
                                                          () ->
                                                              external(
                                                                  root.resolve(
                                                                      FIXTURE_LOCK_E9DEB047)))));
                                      return true;
                                    });
                          })
                      .orElseThrow());
      assertTrue(result);
    }
    assertEquals(0, external(root.resolve(FIXTURE_LOCK_E9DEB047)));
  }

  @Test
  void opsAfd007ConcurrentOnlyOneCallbackOwnsA() throws Exception {
    Files.write(root.resolve(FIXTURE_LOCK_E9DEB047), new byte[0]);
    try (var directory = OwnedTransferDirectory.open(LinuxDirectoryCalls.create(), root)) {
      directory.atExistingEntryHandle(
          FIXTURE_LOCK_E9DEB047,
          held -> {
            var barrier = new CyclicBarrier(16);
            var losers = new CountDownLatch(15);
            try (var executor = Executors.newFixedThreadPool(16)) {
              var work = new ArrayList<Callable<Optional<Boolean>>>();
              for (int i = 0; i < 16; i++)
                work.add(
                    () -> {
                      barrier.await(10, TimeUnit.SECONDS);
                      var result =
                          LinuxFileLock.create()
                              .tryExclusiveForStartup(
                                  held,
                                  fd -> {
                                    assertTrue(
                                        assertDoesNotThrow(
                                            () -> losers.await(10, TimeUnit.SECONDS)));
                                    return true;
                                  });
                      if (result.isEmpty()) losers.countDown();
                      return result;
                    });
              int winners = 0;
              for (var result : executor.invokeAll(work, 30, TimeUnit.SECONDS))
                if (result.get(15, TimeUnit.SECONDS).isPresent()) winners++;
              assertEquals(1, winners);
              assertEquals(0L, losers.getCount());
            } catch (InterruptedException | ExecutionException | TimeoutException failure) {
              throw new AssertionError("public parallel fixture failed", failure);
            }
            return true;
          });
    }
    assertEquals(0, external(root.resolve(FIXTURE_LOCK_E9DEB047)));
  }

  @Test
  void opsAfd008ExistingOrdinaryMaintenanceScopeNeverExportsFd() throws Exception {
    var f = new Fixture();
    assertEquals(Optional.of(7), f.calls().tryExclusive(HELD, () -> 7));
    assertEquals(List.of(FIXTURE_OPEN_35FF74AE, "flock:17:6", FIXTURE_CLOSE_17_F1422F88), f.events);
    assertFalse(f.events.stream().anyMatch(event -> event.startsWith("dup:")));
  }

  private int external(Path file) throws Exception {
    try (var childOwner =
        new OwnedTestProcess(
            new ProcessBuilder(
                "/usr/bin/flock",
                "--no-fork", // BUG2468: keep the command in this PID.
                "-x",
                "-n",
                "-E",
                "20",
                file.toString(),
                "/bin/true"))) {
      var child = childOwner.process();
      assertTrue(child.waitFor(5, TimeUnit.SECONDS));
      return child.exitValue();
    }
  }

  private static void unavailable(StorageIoException failure) {
    assertEquals(StorageIoException.Reason.UNAVAILABLE, failure.reason());
    assertEquals("transfer storage operation failed", failure.getMessage());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
  }

  private static final class Fixture {
    final List<String> events = new ArrayList<>();
    int openResult = 17;
    int reserved = 128;
    int lockResult = 0;
    int errno = 0;
    int failedClose = -1;
    Throwable unknownClose;

    LinuxFileLock calls() {
      return new LinuxFileLock(
          (state, path, flags, mode) -> {
            assertEquals("/proc/self/fd/9", path.getString(0));
            assertEquals(0x80000, flags);
            assertEquals(0, mode);
            events.add(FIXTURE_OPEN_35FF74AE);
            return openResult;
          },
          (state, fd, flags) -> {
            events.add("flock:" + fd + ":" + flags);
            state.set(ValueLayout.JAVA_INT, ERRNO, errno);
            return lockResult;
          },
          (state, fd) -> {
            events.add("close:" + fd);
            if (fd == reserved && unknownClose instanceof RuntimeException failure) throw failure;
            if (fd == reserved && unknownClose instanceof Error failure) throw failure;
            return fd == failedClose ? -1 : 0;
          },
          (fd, cmd, arg) -> {
            events.add("dup:" + fd + ":" + cmd + ":" + arg);
            return reserved;
          });
    }
  }
}
