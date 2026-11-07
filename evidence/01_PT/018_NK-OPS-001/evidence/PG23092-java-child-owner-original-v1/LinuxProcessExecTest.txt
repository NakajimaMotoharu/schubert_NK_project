package dev.codex.schubert.nk.storage;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.lang.foreign.Linker;
import java.lang.foreign.MemorySegment;
import java.lang.foreign.ValueLayout;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.concurrent.Callable;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.Test;

/** Independent literal pointer vectors/native same PID oracle; SS342/343; SSC086. */
final class LinuxProcessExecTest {
  private static final String FIXTURE_JAVA_4108EFE1 = "java";
  private static final String FIXTURE_AMD64_58D0BD71 = "amd64";
  private static final String FIXTURE_LINUX_1CA133AF = "Linux";
  private static final Path HELD = Path.of("/proc/self/fd/17");

  @Test
  void opsExec001LiteralVectorsAndArenaLifetime() {
    var captures = new ArrayList<MemorySegment>();
    var replacement =
        new LinuxProcessExec(
            (file, argv, env) -> {
              assertEquals("/proc/self/fd/17", file.getString(0));
              assertEquals(List.of("setpriv", "--no-new-privs", "日本語", ""), strings(argv));
              assertEquals(
                  List.of(
                      "CREDENTIALS_DIRECTORY=/run/credentials/unit",
                      "INVOCATION_ID=public_fixture"),
                  strings(env));
              captures.add(file);
              captures.add(argv);
              captures.add(env);
              return -1;
            });
    unavailable(
        assertThrows(
            StorageIoException.class,
            () ->
                replacement.replace(
                    HELD,
                    List.of("setpriv", "--no-new-privs", "日本語", ""),
                    Map.of(
                        "INVOCATION_ID",
                        "public_fixture",
                        "CREDENTIALS_DIRECTORY",
                        "/run/credentials/unit"))));
    assertEquals(3, captures.size());
    for (var segment : captures) assertFalse(segment.scope().isAlive());
  }

  @Test
  void opsExec002EveryNativeReturnIsRedactedFailure() {
    for (int returned : List.of(-1, 0, 1, Integer.MIN_VALUE, Integer.MAX_VALUE)) {
      var calls = new AtomicInteger();
      var replacement =
          new LinuxProcessExec(
              (file, argv, env) -> {
                assertEquals(List.of(FIXTURE_JAVA_4108EFE1), strings(argv));
                assertEquals(List.of(), strings(env));
                calls.incrementAndGet();
                return returned;
              });
      unavailable(
          assertThrows(
              StorageIoException.class,
              () -> replacement.replace(HELD, List.of(FIXTURE_JAVA_4108EFE1), Map.of())));
      assertEquals(1, calls.get());
    }
    // Real execve ENOENT, never a raw native diagnostic.
    unavailable(
        assertThrows(
            StorageIoException.class,
            () ->
                LinuxProcessExec.create()
                    .replace(
                        Path.of("/proc/self/fd/2147483647"),
                        List.of(FIXTURE_JAVA_4108EFE1),
                        Map.of())));
  }

  @Test
  void opsExec003InputNullAndPathContracts() {
    var calls = new AtomicInteger();
    var replacement = new LinuxProcessExec((p, a, e) -> calls.incrementAndGet());
    for (String path :
        List.of(
            "/tmp/exec",
            "/proc/1/fd/17",
            "/proc/self/fd/-1",
            "/proc/self/fd/+1",
            "/proc/self/fd/01",
            "/proc/self/fd/99999999999",
            "/proc/self/fd/2147483648",
            "/proc/self/fd/17/child"))
      invalid(
          assertThrows(
              IllegalArgumentException.class,
              () -> replacement.replace(Path.of(path), List.of(FIXTURE_JAVA_4108EFE1), Map.of())));
    assertThrows(
        NullPointerException.class,
        () -> replacement.replace(null, List.of(FIXTURE_JAVA_4108EFE1), Map.of()));
    assertThrows(NullPointerException.class, () -> replacement.replace(HELD, null, Map.of()));
    assertThrows(
        NullPointerException.class,
        () -> replacement.replace(HELD, List.of(FIXTURE_JAVA_4108EFE1), null));
    assertThrows(
        NullPointerException.class,
        () -> replacement.replace(HELD, Arrays.asList(FIXTURE_JAVA_4108EFE1, null), Map.of()));
    var bad = new HashMap<String, String>();
    bad.put(null, "x");
    assertThrows(
        NullPointerException.class,
        () -> replacement.replace(HELD, List.of(FIXTURE_JAVA_4108EFE1), bad));
    bad.clear();
    bad.put("X", null);
    assertThrows(
        NullPointerException.class,
        () -> replacement.replace(HELD, List.of(FIXTURE_JAVA_4108EFE1), bad));
    assertThrows(NullPointerException.class, () -> new LinuxProcessExec(null));
    assertEquals(0, calls.get());
  }

  @Test
  void opsExec004VectorAndStringBoundaries() {
    var calls = new AtomicInteger();
    var replacement =
        new LinuxProcessExec(
            (p, a, e) -> {
              calls.incrementAndGet();
              return -1;
            });
    invalid(
        assertThrows(
            IllegalArgumentException.class, () -> replacement.replace(HELD, List.of(), Map.of())));
    invalid(
        assertThrows(
            IllegalArgumentException.class,
            () -> replacement.replace(HELD, Collections.nCopies(65, "x"), Map.of())));
    var env = new HashMap<String, String>();
    for (int i = 0; i < 33; i++) env.put("X" + i, "");
    invalid(
        assertThrows(
            IllegalArgumentException.class, () -> replacement.replace(HELD, List.of("x"), env)));
    env.remove("X32");
    unavailable(
        assertThrows(
            StorageIoException.class,
            () -> replacement.replace(HELD, Collections.nCopies(64, "x"), env)));
    unavailable(
        assertThrows(
            StorageIoException.class,
            () ->
                replacement.replace(
                    Path.of("/proc/self/fd/0"),
                    List.of("x".repeat(4096)),
                    Map.of("A".repeat(64), "x".repeat(4096)))));
    for (String value : List.of("x".repeat(4097), "\0", "\n", "\r", "\t", "\u007f")) {
      invalid(
          assertThrows(
              IllegalArgumentException.class,
              () -> replacement.replace(HELD, List.of(value), Map.of())));
      invalid(
          assertThrows(
              IllegalArgumentException.class,
              () -> replacement.replace(HELD, List.of("x"), Map.of("A", value))));
    }
    for (String key : List.of("", "a", "0A", "A=B", "A\n", "A".repeat(65)))
      invalid(
          assertThrows(
              IllegalArgumentException.class,
              () -> replacement.replace(HELD, List.of("x"), Map.of(key, ""))));
    assertEquals(2, calls.get());
  }

  @Test
  void opsExec005PlatformAndSymbolContracts() {
    var symbols = Linker.nativeLinker().defaultLookup();
    assertThrows(
        NullPointerException.class,
        () -> LinuxProcessExec.create(null, FIXTURE_AMD64_58D0BD71, symbols));
    assertThrows(
        NullPointerException.class,
        () -> LinuxProcessExec.create(FIXTURE_LINUX_1CA133AF, null, symbols));
    assertThrows(
        NullPointerException.class,
        () -> LinuxProcessExec.create(FIXTURE_LINUX_1CA133AF, FIXTURE_AMD64_58D0BD71, null));
    for (String os : List.of("Windows", "linux", ""))
      assertThrows(
          IllegalStateException.class,
          () -> LinuxProcessExec.create(os, FIXTURE_AMD64_58D0BD71, symbols));
    assertThrows(
        IllegalStateException.class,
        () -> LinuxProcessExec.create(FIXTURE_LINUX_1CA133AF, "unknown", symbols));
    assertThrows(
        IllegalStateException.class,
        () ->
            LinuxProcessExec.create(
                FIXTURE_LINUX_1CA133AF, FIXTURE_AMD64_58D0BD71, name -> Optional.empty()));
    for (String arch : List.of(FIXTURE_AMD64_58D0BD71, "x86_64", "aarch64"))
      assertNotNull(LinuxProcessExec.create(FIXTURE_LINUX_1CA133AF, arch, symbols));
  }

  @Test
  void opsExec006UnknownFailureIdentityAndArenaClose() {
    for (Throwable unknown :
        List.of(
            new IllegalStateException("public unknown"), new AssertionError("public unknown"))) {
      var captures = new ArrayList<MemorySegment>();
      var replacement =
          new LinuxProcessExec(
              (p, a, e) -> {
                captures.add(a);
                if (unknown instanceof RuntimeException runtime) throw runtime;
                throw (Error) unknown;
              });
      assertSame(
          unknown,
          assertThrows(
              unknown.getClass(), () -> replacement.replace(HELD, List.of("x"), Map.of())));
      assertFalse(captures.getFirst().scope().isAlive());
      assertEquals(0, unknown.getSuppressed().length);
    }
  }

  @Test
  void opsExec007ConcurrentInputsRemainIndependent() throws Exception {
    var calls = new AtomicInteger();
    var expectedInput = new ThreadLocal<String>();
    var replacement =
        new LinuxProcessExec(
            (p, a, e) -> {
              String expected = expectedInput.get();
              assertNotNull(expected, "independent task fixture must be bound");
              assertEquals(List.of(expected), strings(a));
              assertEquals(List.of("X=" + expected), strings(e));
              calls.incrementAndGet();
              return -1;
            });
    try (var executor = Executors.newFixedThreadPool(8)) {
      var work = new ArrayList<Callable<Boolean>>();
      for (int i = 0; i < 32; i++) {
        String value = "fixture" + i;
        work.add(
            () -> {
              expectedInput.set(value);
              try {
                unavailable(
                    assertThrows(
                        StorageIoException.class,
                        () -> replacement.replace(HELD, List.of(value), Map.of("X", value))));
                return true;
              } finally {
                expectedInput.remove();
              }
            });
      }
      for (var result : executor.invokeAll(work, 30, TimeUnit.SECONDS))
        assertTrue(result.get(5, TimeUnit.SECONDS));
    }
    assertEquals(32, calls.get());
  }

  @Test
  void opsExec008ActualReplacementKeepsPidAndOnlyPreparedEnvironment() throws Exception {
    var builder =
        new ProcessBuilder(
                Path.of(System.getProperty("java.home"), "bin/java").toString(),
                "--enable-native-access=ALL-UNNAMED",
                "-cp",
                System.getProperty("java.class.path"),
                LinuxProcessExecChild.class.getName())
            .redirectErrorStream(true);
    builder.environment().put("PGPT_EXEC_UNEXPECTED", "public_fixture");
    var child = builder.start();
    try {
      assertTrue(child.waitFor(10, TimeUnit.SECONDS));
      assertEquals(0, child.exitValue());
      assertEquals(
          "PID=" + child.pid() + " ENV=fixture_only\n", child.inputReader().readLine() + "\n");
      assertEquals(-1, child.getInputStream().read());
    } finally {
      if (child.isAlive()) child.destroy();
    }
  }

  // Every pointed string is freshly allocated by the tested confined arena; bounded fixture only.
  @SuppressWarnings("restricted")
  private static List<String> strings(MemorySegment vector) {
    var result = new ArrayList<String>();
    for (int index = 0; ; index++) {
      var pointer = vector.getAtIndex(ValueLayout.ADDRESS, index);
      if (pointer.equals(MemorySegment.NULL)) return result;
      result.add(pointer.reinterpret(8192).getString(0));
    }
  }

  private static void unavailable(StorageIoException failure) {
    assertEquals(StorageIoException.Reason.UNAVAILABLE, failure.reason());
    assertEquals("transfer storage operation failed", failure.getMessage());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
  }

  private static void invalid(IllegalArgumentException failure) {
    assertEquals("invalid process replacement input", failure.getMessage());
    assertNull(failure.getCause());
  }
}
