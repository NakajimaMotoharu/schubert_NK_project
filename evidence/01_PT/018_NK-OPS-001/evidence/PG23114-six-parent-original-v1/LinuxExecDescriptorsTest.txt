package dev.codex.schubert.nk.storage;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assertions.fail;

import java.io.IOException;
import java.lang.foreign.Linker;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.concurrent.Callable;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** Independent syscall order oracle; borrowed ownership and actual exec/flock interop. */
final class LinuxExecDescriptorsTest {
  private static final String FIXTURE_BODY_BFD4D039 = "body";
  private static final String FIXTURE_128_1_0_31CFFFFA = "128:1:0";
  private static final String FIXTURE_128_2_0_F22A3178 = "128:2:0";
  private static final String FIXTURE_129_1_0_F3574D87 = "129:1:0";
  private static final String FIXTURE_129_2_0_AE3E5612 = "129:2:0";
  private static final String FIXTURE_129_2_1_81F75D1D = "129:2:1";
  private static final String FIXTURE_128_2_1_FBB8F1D8 = "128:2:1";
  private static final String FIXTURE_PUBLIC_UNKNOWN_5B451478 = "public unknown";
  private static final String FIXTURE_AMD64_58D0BD71 = "amd64";
  private static final String FIXTURE_LINUX_1CA133AF = "Linux";
  @TempDir Path root;

  @Test
  void opsXfd001ExactlyTwoFlagsRestoredInReverseOrder() {
    var calls = new ArrayList<String>();
    var descriptor = fixture(calls);
    assertDoesNotThrow(
        () -> descriptor.withInherited(128, 129, () -> calls.add(FIXTURE_BODY_BFD4D039)));
    assertEquals(
        List.of(
            FIXTURE_128_1_0_31CFFFFA,
            FIXTURE_128_2_0_F22A3178,
            FIXTURE_129_1_0_F3574D87,
            FIXTURE_129_2_0_AE3E5612,
            FIXTURE_BODY_BFD4D039,
            FIXTURE_129_2_1_81F75D1D,
            FIXTURE_128_2_1_FBB8F1D8),
        calls);
  }

  @Test
  void opsXfd002EveryNativeFailureAndPartialTransition() {
    var expected =
        List.of(
            FIXTURE_128_1_0_31CFFFFA,
            FIXTURE_128_2_0_F22A3178,
            FIXTURE_129_1_0_F3574D87,
            FIXTURE_129_2_0_AE3E5612,
            FIXTURE_BODY_BFD4D039,
            FIXTURE_129_2_1_81F75D1D,
            FIXTURE_128_2_1_FBB8F1D8);
    for (String failed :
        List.of(
            FIXTURE_128_1_0_31CFFFFA,
            FIXTURE_128_2_0_F22A3178,
            FIXTURE_129_1_0_F3574D87,
            FIXTURE_129_2_0_AE3E5612,
            FIXTURE_129_2_1_81F75D1D,
            FIXTURE_128_2_1_FBB8F1D8)) {
      for (int returned : List.of(-1, 2)) {
        var calls = new ArrayList<String>();
        var descriptor =
            new LinuxExecDescriptors(
                (fd, cmd, arg) -> {
                  String name = fd + ":" + cmd + ":" + arg;
                  calls.add(name);
                  return name.equals(failed) ? returned : cmd == 1 ? 1 : 0;
                });
        unavailable(
            assertThrows(
                StorageIoException.class,
                () -> descriptor.withInherited(128, 129, () -> calls.add(FIXTURE_BODY_BFD4D039))));
        var oracle = new ArrayList<>(expected.subList(0, expected.indexOf(failed) + 1));
        if (failed.equals(FIXTURE_128_2_0_F22A3178)) oracle.add(FIXTURE_128_2_1_FBB8F1D8);
        if (failed.equals(FIXTURE_129_1_0_F3574D87)) oracle.add(FIXTURE_128_2_1_FBB8F1D8);
        if (failed.equals(FIXTURE_129_2_0_AE3E5612)) {
          oracle.add(FIXTURE_129_2_1_81F75D1D);
          oracle.add(FIXTURE_128_2_1_FBB8F1D8);
        }
        if (failed.equals(FIXTURE_129_2_1_81F75D1D)) oracle.add(FIXTURE_128_2_1_FBB8F1D8);
        assertEquals(oracle, calls);
      }
    }
    var calls = new ArrayList<String>();
    var missingCloexec =
        new LinuxExecDescriptors(
            (fd, cmd, arg) -> {
              calls.add(fd + ":" + cmd + ":" + arg);
              return 0;
            });
    unavailable(
        assertThrows(
            StorageIoException.class,
            () -> missingCloexec.withInherited(128, 129, () -> fail("no replacement"))));
    assertEquals(List.of(FIXTURE_128_1_0_31CFFFFA), calls);
  }

  @Test
  void opsXfd003IoAndUnknownBodyPreserveOwnership() {
    for (Throwable body :
        List.of(
            new IOException("private fixture diagnostic"),
            new IllegalStateException(FIXTURE_PUBLIC_UNKNOWN_5B451478),
            new AssertionError(FIXTURE_PUBLIC_UNKNOWN_5B451478))) {
      var calls = new ArrayList<String>();
      var descriptor = fixture(calls);
      Class<? extends Throwable> expectedType =
          body instanceof IOException ? StorageIoException.class : body.getClass();
      var actual =
          assertThrows(
              expectedType,
              () ->
                  descriptor.withInherited(
                      128,
                      129,
                      () -> {
                        calls.add(FIXTURE_BODY_BFD4D039);
                        if (body instanceof IOException failure) throw failure;
                        if (body instanceof RuntimeException failure) throw failure;
                        throw (Error) body;
                      }));
      if (body instanceof IOException) unavailable((StorageIoException) actual);
      else assertSame(body, actual);
      assertEquals(
          List.of(
              FIXTURE_128_1_0_31CFFFFA,
              FIXTURE_128_2_0_F22A3178,
              FIXTURE_129_1_0_F3574D87,
              FIXTURE_129_2_0_AE3E5612,
              FIXTURE_BODY_BFD4D039,
              FIXTURE_129_2_1_81F75D1D,
              FIXTURE_128_2_1_FBB8F1D8),
          calls);
    }
  }

  @Test
  void opsXfd004CompoundCleanupUnknownPriority() {
    for (boolean knownBody : List.of(false, true)) {
      for (Throwable unknown :
          List.of(
              new IllegalStateException(FIXTURE_PUBLIC_UNKNOWN_5B451478),
              new AssertionError(FIXTURE_PUBLIC_UNKNOWN_5B451478))) {
        var calls = new ArrayList<String>();
        var descriptor =
            new LinuxExecDescriptors(
                (fd, cmd, arg) -> {
                  calls.add(fd + ":" + cmd + ":" + arg);
                  if (fd == 129 && cmd == 2 && arg == 1) {
                    if (unknown instanceof RuntimeException failure) throw failure;
                    throw (Error) unknown;
                  }
                  return cmd == 1 ? 1 : 0;
                });
        assertSame(
            unknown,
            assertThrows(
                unknown.getClass(),
                () ->
                    descriptor.withInherited(
                        128,
                        129,
                        () -> {
                          if (knownBody) throw new IOException("private fixture diagnostic");
                          if (unknown instanceof RuntimeException failure) throw failure;
                          throw (Error) unknown;
                        })));
        assertEquals(FIXTURE_128_2_1_FBB8F1D8, calls.getLast());
        assertEquals(knownBody ? 0 : 1, unknown.getSuppressed().length);
      }
    }
  }

  @Test
  void opsXfd005NullDescriptorAndBoundaryContracts() {
    var calls = new ArrayList<String>();
    var descriptor = fixture(calls);
    for (int[] pair :
        List.of(
            new int[] {127, 129},
            new int[] {65536, 129},
            new int[] {128, 127},
            new int[] {128, 65536},
            new int[] {128, 128})) {
      var failure =
          assertThrows(
              IllegalArgumentException.class,
              () -> descriptor.withInherited(pair[0], pair[1], () -> fail()));
      assertEquals("invalid descriptor inheritance input", failure.getMessage());
      assertNull(failure.getCause());
    }
    assertThrows(NullPointerException.class, () -> descriptor.withInherited(128, 129, null));
    assertThrows(NullPointerException.class, () -> new LinuxExecDescriptors(null));
    assertEquals(List.of(), calls);
    assertDoesNotThrow(() -> descriptor.withInherited(128, 65535, () -> {}));
    assertEquals(
        List.of(
            FIXTURE_128_1_0_31CFFFFA,
            FIXTURE_128_2_0_F22A3178,
            "65535:1:0",
            "65535:2:0",
            "65535:2:1",
            FIXTURE_128_2_1_FBB8F1D8),
        calls);
    unavailable(
        assertThrows(
            StorageIoException.class,
            () -> LinuxExecDescriptors.create().withInherited(65534, 65535, () -> fail())));
  }

  @Test
  void opsXfd006PlatformAndSymbolContracts() {
    var symbols = Linker.nativeLinker().defaultLookup();
    assertThrows(
        NullPointerException.class,
        () -> LinuxExecDescriptors.create(null, FIXTURE_AMD64_58D0BD71, symbols));
    assertThrows(
        NullPointerException.class,
        () -> LinuxExecDescriptors.create(FIXTURE_LINUX_1CA133AF, null, symbols));
    assertThrows(
        NullPointerException.class,
        () -> LinuxExecDescriptors.create(FIXTURE_LINUX_1CA133AF, FIXTURE_AMD64_58D0BD71, null));
    for (String os : List.of("Windows", "linux", ""))
      assertThrows(
          IllegalStateException.class,
          () -> LinuxExecDescriptors.create(os, FIXTURE_AMD64_58D0BD71, symbols));
    assertThrows(
        IllegalStateException.class,
        () -> LinuxExecDescriptors.create(FIXTURE_LINUX_1CA133AF, "unknown", symbols));
    assertThrows(
        IllegalStateException.class,
        () ->
            LinuxExecDescriptors.create(
                FIXTURE_LINUX_1CA133AF, FIXTURE_AMD64_58D0BD71, name -> Optional.empty()));
    for (String arch : List.of(FIXTURE_AMD64_58D0BD71, "x86_64", "aarch64"))
      assertNotNull(LinuxExecDescriptors.create(FIXTURE_LINUX_1CA133AF, arch, symbols));
  }

  @Test
  void opsXfd007ConcurrentDisjointCapabilities() throws Exception {
    var calls = new AtomicInteger();
    var descriptor =
        new LinuxExecDescriptors(
            (fd, cmd, arg) -> {
              calls.incrementAndGet();
              return cmd == 1 ? 1 : 0;
            });
    try (var executor = Executors.newFixedThreadPool(8)) {
      var work = new ArrayList<Callable<Boolean>>();
      for (int i = 0; i < 32; i++) {
        int fd = 128 + i * 2;
        work.add(
            () -> {
              assertDoesNotThrow(() -> descriptor.withInherited(fd, fd + 1, () -> {}));
              return true;
            });
      }
      for (var result : executor.invokeAll(work, 30, TimeUnit.SECONDS))
        assertTrue(result.get(5, TimeUnit.SECONDS));
    }
    assertEquals(32 * 6, calls.get());
  }

  @Test
  void opsXfd008RealExecInheritsSameFlockUntilProcessExit() throws Exception {
    Files.write(root.resolve("lock"), new byte[0]);
    try (var executor = Executors.newSingleThreadExecutor();
        var childOwner =
            new OwnedTestProcess(
                new ProcessBuilder(
                        Path.of(System.getProperty("java.home"), "bin/java").toString(),
                        "--enable-native-access=ALL-UNNAMED",
                        "-cp",
                        System.getProperty("java.class.path"),
                        LinuxExecDescriptorsChild.class.getName(),
                        root.toString())
                    .redirectErrorStream(true)
                    .start())) {
      var child = childOwner.process();
      try (var reader = child.inputReader()) {
        try {
          assertEquals(
              "PID=" + child.pid() + " INHERITED=128,129",
              executor.submit(reader::readLine).get(10, TimeUnit.SECONDS));
          var competitor =
              new ProcessBuilder(
                      "/usr/bin/flock",
                      "-x",
                      "-n",
                      "-E",
                      "20",
                      root.resolve("lock").toString(),
                      "/bin/true")
                  .start();
          assertTrue(competitor.waitFor(5, TimeUnit.SECONDS));
          assertEquals(20, competitor.exitValue());
          child.getOutputStream().write('\n');
          child.getOutputStream().flush();
          assertTrue(child.waitFor(5, TimeUnit.SECONDS));
          assertEquals(0, child.exitValue());
          assertNull(reader.readLine());
          var after =
              new ProcessBuilder(
                      "/usr/bin/flock",
                      "-x",
                      "-n",
                      "-E",
                      "20",
                      root.resolve("lock").toString(),
                      "/bin/true")
                  .start();
          assertTrue(after.waitFor(5, TimeUnit.SECONDS));
          assertEquals(0, after.exitValue());
        } finally {
          childOwner.close();
        }
      }
    }
  }

  private static LinuxExecDescriptors fixture(List<String> calls) {
    return new LinuxExecDescriptors(
        (fd, cmd, arg) -> {
          calls.add(fd + ":" + cmd + ":" + arg);
          return cmd == 1 ? 1 : 0;
        });
  }

  private static void unavailable(StorageIoException failure) {
    assertEquals(StorageIoException.Reason.UNAVAILABLE, failure.reason());
    assertEquals("transfer storage operation failed", failure.getMessage());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
  }
}
