package dev.codex.schubert.nk.batch.platform;

import static dev.codex.schubert.nk.batch.platform.InspectorUnitProbeFixture.Child;
import static dev.codex.schubert.nk.batch.platform.InspectorUnitProbeFixture.Script;
import static dev.codex.schubert.nk.batch.platform.InspectorUnitSnapshotTest.GOLDEN;
import static dev.codex.schubert.nk.batch.platform.InspectorUnitSnapshotTest.ID;
import static dev.codex.schubert.nk.batch.platform.InspectorUnitSnapshotTest.with;
import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.io.FilterInputStream;
import java.io.FilterOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.OptionalInt;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.Test;

/** NK-OPS-001/OPS009/UI251/SS341 7.4; PG167/SSC060; UNIT009..016, 018/023. */
final class InspectorUnitProbeTest {
  private static final List<String> OPERATIONS =
      List.of(
          "start",
          "get.stdout",
          "get.stdin",
          "get.stderr",
          "stdin.close",
          "stderr.close",
          "wait",
          "exit",
          "stdout.read",
          "stdout.close",
          "alive");

  @Test
  void fixedCommands() {
    assertThrows(NullPointerException.class, () -> InspectorUnitProbe.forTarget(null));
    assertThrows(NullPointerException.class, () -> InspectorUnitProbe.NativeReader.forTarget(null));
    assertThrows(NullPointerException.class, () -> new InspectorUnitProbe(new Script(), null));
    for (boolean processes : List.of(false, true)) {
      byte[] bytes =
          (processes
                  ? "a(sus) 0\n"
                  : GOLDEN
                      .replace(
                          InspectorUnitSnapshot.UNIT, InspectorUnitSnapshot.Target.BACKUP.unit())
                      .replace("RemainAfterExit=no", "RemainAfterExit=yes"))
              .getBytes(StandardCharsets.US_ASCII);
      var child = new Child(bytes);
      var reader =
          new InspectorUnitProbe.NativeReader(
              command -> {
                var expected = new ArrayList<>(processes ? processCommand() : stateCommand());
                expected.set(expected.size() - 1, "schubert-nk-backup.service");
                assertEquals(expected, command);
                child.event("start");
                return child;
              },
              InspectorUnitSnapshot.Target.BACKUP);
      assertArrayEquals(bytes, processes ? reader.readProcesses() : reader.readState());
      child.allClosed();
    }
    var backupScript = new Script();
    backupScript.states =
        List.of(
            GOLDEN
                .replace(InspectorUnitSnapshot.UNIT, InspectorUnitSnapshot.Target.BACKUP.unit())
                .replace("RemainAfterExit=no", "RemainAfterExit=yes"));
    assertTrue(
        new InspectorUnitProbe(backupScript, InspectorUnitSnapshot.Target.BACKUP)
            .completionAfter(Optional.empty())
            .isEmpty());
    backupScript.wiped();
    assertThrows(
        StopGateException.class,
        () -> InspectorUnitProbe.forTarget(InspectorUnitSnapshot.Target.BACKUP).read());
    for (boolean processes : new boolean[] {false, true}) {
      byte[] bytes = (processes ? "a(sus) 0\n" : GOLDEN).getBytes(StandardCharsets.US_ASCII);
      var child = new Child(bytes);
      var reader =
          new InspectorUnitProbe.NativeReader(
              command -> {
                child.event("start");
                assertEquals(processes ? processCommand() : stateCommand(), command);
                assertThrows(UnsupportedOperationException.class, () -> command.add("unsafe"));
                return child;
              });
      byte[] actual = processes ? reader.readProcesses() : reader.readState();
      assertArrayEquals(bytes, actual);
      assertEquals(OPERATIONS, child.order);
      assertEquals(11, child.counts.size());
      assertTrue(child.counts.values().stream().allMatch(n -> n == 1));
      assertEquals(processes ? 10 : 2049, child.output.maximum);
      child.allClosed();
      assertEquals(0, child.destroyed);
      Arrays.fill(actual, (byte) 0);
      child.wiped();
    }
    var s = new Script();
    assertTrue(new InspectorUnitProbe(s).read().quiescent());
    assertEquals(List.of("state"), s.calls);
    s.wiped();
  }

  @Test
  void stableTerminalAndReceipt() throws Exception {
    for (int status : new int[] {0, 10}) {
      var s = new Script();
      s.states = List.of(with("ExecMainStatus", Integer.toString(status)));
      var probe = new InspectorUnitProbe(s);
      OptionalInt actual = probe.completionAfter(Optional.empty());
      assertEquals(OptionalInt.of(status), actual);
      assertEquals(List.of("state", "processes", "state"), s.calls);
      s.wiped();
      Path target = Path.of("target", "inspector-unit-traces");
      Files.createDirectories(target);
      Files.writeString(
          target.resolve("PT-OPS-UNIT-010-receipt-" + status + ".txt"),
          "receipt=" + actual.orElseThrow() + "\ncommands=" + s.calls.size() + "\n");
    }
    var s = new Script();
    assertTrue(new InspectorUnitProbe(s).completionAfter(Optional.of(ID)).isEmpty());
    s.wiped();
    s = new Script();
    s.states = List.of(with("InvocationID", ""));
    assertTrue(new InspectorUnitProbe(s).completionAfter(Optional.empty()).isEmpty());
    s.wiped();
    s = new Script();
    s.states = List.of(with("MainPID", "1"));
    assertTrue(new InspectorUnitProbe(s).completionAfter(Optional.empty()).isEmpty());
    assertEquals(List.of("state"), s.calls);
    s.wiped();
    s = new Script();
    assertEquals(
        OptionalInt.of(10), new InspectorUnitProbe(s).completionAfter(Optional.of(new UUID(0, 1))));
    s.wiped();
  }

  @Test
  void unstableAndNonempty() {
    // Every variable property can change to another valid observation; fixed properties must
    // reject.
    Map<String, String> changes =
        Map.ofEntries(
            Map.entry("ActiveState", "inactive"),
            Map.entry("SubState", "dead"),
            Map.entry("Job", "1"),
            Map.entry("MainPID", "1"),
            Map.entry("ControlPID", "1"),
            Map.entry("InvocationID", "f".repeat(32)),
            Map.entry("ExecMainCode", "2"),
            Map.entry("ExecMainStatus", "0"),
            Map.entry("ExecMainStartTimestampMonotonic", "1234568"),
            Map.entry("ExecMainExitTimestampMonotonic", "2345679"),
            Map.entry("Result", "timeout"),
            Map.entry("RemainAfterExit", "yes"));
    assertEquals(12, changes.size());
    for (var entry : changes.entrySet()) {
      var s = new Script();
      s.states = List.of(GOLDEN, with(entry.getKey(), entry.getValue()));
      assertTrue(new InspectorUnitProbe(s).quiescent().isEmpty(), entry.getKey());
      assertEquals(List.of("state", "processes", "state"), s.calls);
      s.wiped();
    }
    for (String key : List.of("Id", "LoadState", "Type", "Restart", "KillMode", "SendSIGKILL")) {
      var s = new Script();
      s.states = List.of(GOLDEN, with(key, "unknown"));
      failed(StopGateFailure.MALFORMED_STATE, () -> new InspectorUnitProbe(s).quiescent());
      s.wiped();
    }
    for (String wrong :
        List.of("", "a(sus) 1", "a(sus) 0\n\n", "a(sus) 0", "garbage", "a(sus) 1 public")) {
      var s = new Script();
      s.processes = wrong.getBytes(StandardCharsets.US_ASCII);
      assertTrue(new InspectorUnitProbe(s).quiescent().isEmpty());
      assertEquals(List.of("state", "processes"), s.calls);
      s.wiped();
    }
    var s = new Script();
    s.states = List.of(with("Job", "1"));
    assertTrue(new InspectorUnitProbe(s).quiescent().isEmpty());
    assertEquals(List.of("state"), s.calls);
    s.wiped();
  }

  @Test
  void commandFailures() {
    for (int position = 1; position <= 3; position++) {
      var s = new Script();
      s.failAt = position;
      failed(StopGateFailure.COMMAND_FAILURE, () -> new InspectorUnitProbe(s).quiescent());
      s.wiped();
      var absent = new Script();
      absent.nullAt = position;
      assertThrows(NullPointerException.class, () -> new InspectorUnitProbe(absent).quiescent());
      absent.wiped();
      var runtime = new Script();
      runtime.failAt = position;
      runtime.runtime = new IllegalStateException("public primary");
      assertSame(
          runtime.runtime,
          assertThrows(
              IllegalStateException.class, () -> new InspectorUnitProbe(runtime).quiescent()));
      runtime.wiped();
    }
    for (int code : new int[] {-1, 1, 20, 50, 70, 255}) {
      var child = child();
      child.code = code;
      failed(StopGateFailure.COMMAND_FAILURE, () -> reader(child).readState());
      child.allClosed();
      child.wiped();
      assertFalse(child.counts.containsKey("stdout.read"));
    }
    failed(
        StopGateFailure.COMMAND_FAILURE,
        () ->
            new InspectorUnitProbe.NativeReader(
                    command -> {
                      throw new IOException("PUBLIC_DIAGNOSTIC_CANARY");
                    })
                .readState());
    assertThrows(
        NullPointerException.class,
        () -> new InspectorUnitProbe.NativeReader(command -> null).readState());
    assertThrows(NullPointerException.class, () -> new InspectorUnitProbe.NativeReader(null));
    assertThrows(NullPointerException.class, () -> new InspectorUnitProbe(null));
    assertThrows(
        NullPointerException.class,
        () -> new InspectorUnitProbe(new Script()).completionAfter(null));
  }

  @Test
  void boundedOutputAndTimeout() {
    for (boolean processes : new boolean[] {false, true}) {
      int limit = processes ? 9 : 2048;
      for (int size : new int[] {0, 1, limit, limit + 1, 65536}) {
        var child = new Child(new byte[size]);
        var reader = reader(child);
        if (size > limit)
          failed(
              StopGateFailure.MALFORMED_STATE,
              () -> {
                if (processes) reader.readProcesses();
                else reader.readState();
              });
        else {
          byte[] actual = processes ? reader.readProcesses() : reader.readState();
          assertEquals(size, actual.length);
          Arrays.fill(actual, (byte) 0);
        }
        child.allClosed();
        child.wiped();
        assertEquals(limit + 1, child.output.maximum);
      }
    }
    var child = child();
    child.completed = false;
    final var timeoutChild = child;
    failed(StopGateFailure.TIMEOUT, () -> reader(timeoutChild).readState());
    child.allClosed();
    assertEquals(1, child.destroyed);
    assertFalse(child.alive);
    child = child();
    child.output.nullRead = true;
    final var missing = child;
    assertThrows(NullPointerException.class, () -> reader(missing).readState());
    missing.allClosed();
    child = child();
    child.ioFailures.add("stdout.read");
    final var broken = child;
    failed(StopGateFailure.COMMAND_FAILURE, () -> reader(broken).readState());
    broken.allClosed();
  }

  @Test
  void interruptions() {
    for (int position = 1; position <= 3; position++) {
      var s = new Script();
      s.interruptAt = position;
      try {
        failed(StopGateFailure.INTERRUPTED, () -> new InspectorUnitProbe(s).quiescent());
        assertTrue(Thread.currentThread().isInterrupted());
        assertEquals(position, s.calls.size());
        s.wiped();
      } finally {
        Thread.interrupted();
      }
    }
    var before = new Script();
    Thread.currentThread().interrupt();
    try {
      failed(StopGateFailure.INTERRUPTED, () -> new InspectorUnitProbe(before).read());
      assertTrue(before.calls.isEmpty());
      assertTrue(Thread.currentThread().isInterrupted());
    } finally {
      Thread.interrupted();
    }
    for (String position : OPERATIONS) {
      var child = child();
      child.hook =
          (name, count) -> {
            if (name.equals(position)) Thread.currentThread().interrupt();
          };
      try {
        failed(StopGateFailure.INTERRUPTED, () -> new InspectorUnitProbe(reader(child)).read());
        assertTrue(Thread.currentThread().isInterrupted());
        child.allClosed();
        child.wiped();
      } finally {
        Thread.interrupted();
      }
    }
    var child = child();
    child.waitInterrupt = true;
    final var interruptedChild = child;
    try {
      failed(StopGateFailure.INTERRUPTED, () -> reader(interruptedChild).readState());
      assertTrue(Thread.currentThread().isInterrupted());
      child.allClosed();
      assertEquals(1, child.destroyed);
    } finally {
      Thread.interrupted();
    }
    child = child();
    final var notStarted = child;
    Thread.currentThread().interrupt();
    try {
      failed(StopGateFailure.INTERRUPTED, () -> reader(notStarted).readState());
      assertTrue(notStarted.order.isEmpty());
    } finally {
      Thread.interrupted();
    }
    child = child();
    child.completed = false;
    child.hook =
        (name, count) -> {
          if (name.equals("destroy")) Thread.currentThread().interrupt();
        };
    final var timed = child;
    try {
      failed(StopGateFailure.TIMEOUT, () -> reader(timed).readState());
      assertTrue(Thread.currentThread().isInterrupted());
      timed.allClosed();
    } finally {
      Thread.interrupted();
    }
  }

  @Test
  void allResourceFailures() {
    for (String stream : List.of("stdout", "stdin", "stderr")) {
      var child = child();
      child.missing = stream;
      assertThrows(NullPointerException.class, () -> reader(child).readState());
      assertEquals(stream.equals("stdout") ? 0 : 1, child.output.closed);
      assertEquals(stream.equals("stderr") ? 1 : 0, child.input.closed);
      assertEquals(0, child.error.closed);
      assertEquals(1, child.destroyed);
    }
    for (String point : OPERATIONS) {
      var child = child();
      var primary = new IllegalStateException("public primary");
      child.hook =
          (name, count) -> {
            if (name.equals(point) && count == 1) throw primary;
          };
      assertSame(
          primary, assertThrows(IllegalStateException.class, () -> reader(child).readState()));
      if (!Set.of("start", "get.stdout", "get.stdin", "get.stderr").contains(point))
        child.allClosed();
      child.wiped();
    }
    for (String failing : List.of("stdout.read", "stdout.close", "stdin.close", "stderr.close")) {
      var child = child();
      child.ioFailures.add(failing);
      failed(StopGateFailure.COMMAND_FAILURE, () -> reader(child).readState());
      child.allClosed();
      child.wiped();
    }
    for (String cleanup : List.of("stdout.close", "stdin.close", "stderr.close"))
      for (Throwable primary :
          List.of(
              new IllegalStateException("public primary"),
              new NullPointerException("public primary"),
              new AssertionError("public primary"))) {
        var child = child();
        child.ioFailures.add(cleanup);
        // BUG190: stderr must already be owned when the primary failure occurs.
        String point =
            switch (cleanup) {
              case "stdout.close" -> "stdout.read";
              case "stdin.close" -> "get.stderr";
              default -> "stdin.close";
            };
        child.hook =
            (name, count) -> {
              if (name.equals(point)) {
                if (primary instanceof RuntimeException failure) throw failure;
                throw (Error) primary;
              }
            };
        assertSame(primary, assertThrows(primary.getClass(), () -> reader(child).readState()));
        assertEquals(1, child.counts.get(cleanup));
        assertEquals(1, primary.getSuppressed().length);
        assertEquals(1, child.output.closed);
        assertEquals(1, child.input.closed);
        assertEquals(cleanup.equals("stdin.close") ? 0 : 1, child.error.closed);
        for (Throwable suppressed : primary.getSuppressed()) {
          assertInstanceOf(StopGateException.class, suppressed);
          assertEquals("application stop check failed", suppressed.getMessage());
          assertNull(suppressed.getCause());
        }
        child.wiped();
      }
    // BUG195/YKT154: repeated unknown throwable must not trigger TWR self-suppression.
    for (String cleanup : List.of("stdout.close", "stdin.close", "stderr.close"))
      for (Throwable primary :
          List.of(
              new IllegalStateException("public primary"),
              new NullPointerException("public primary"),
              new AssertionError("public primary"))) {
        var repeated = child();
        String point =
            switch (cleanup) {
              case "stdout.close" -> "stdout.read";
              case "stdin.close" -> "get.stderr";
              default -> "stdin.close";
            };
        repeated.hook =
            (name, count) -> {
              if (name.equals(point) || name.equals(cleanup)) {
                if (primary instanceof RuntimeException failure) throw failure;
                throw (Error) primary;
              }
            };
        assertSame(primary, assertThrows(primary.getClass(), () -> reader(repeated).readState()));
        assertEquals(1, repeated.counts.get(cleanup));
        assertEquals(1, primary.getSuppressed().length);
        var secondary = assertInstanceOf(StopGateException.class, primary.getSuppressed()[0]);
        assertEquals(StopGateFailure.COMMAND_FAILURE, secondary.reason());
        assertNull(secondary.getCause());
        assertEquals(1, repeated.output.closed);
        assertEquals(1, repeated.input.closed);
        assertEquals(cleanup.equals("stdin.close") ? 0 : 1, repeated.error.closed);
        repeated.wiped();
      }
    // I/O, timeout and interrupted known primaries cannot hide unknown/fatal cleanup.
    for (int known = 0; known < 3; known++)
      for (Throwable cleanup :
          List.of(
              new IllegalStateException("public cleanup"),
              new NullPointerException("public cleanup"),
              new AssertionError("public cleanup"))) {
        var compound = child();
        if (known == 0) compound.ioFailures.add("stdout.read");
        if (known == 1) compound.completed = false;
        if (known == 2) compound.waitInterrupt = true;
        compound.hook =
            (name, count) -> {
              if (name.equals("stdout.close")) {
                if (cleanup instanceof RuntimeException failure) throw failure;
                throw (Error) cleanup;
              }
            };
        try {
          assertSame(cleanup, assertThrows(cleanup.getClass(), () -> reader(compound).readState()));
          assertEquals(known == 2, Thread.currentThread().isInterrupted());
          assertEquals(0, cleanup.getSuppressed().length);
          compound.allClosed();
          compound.wiped();
        } finally {
          Thread.interrupted();
        }
      }
    var child = child();
    child.ioFailures.addAll(Set.of("stdout.close", "stdin.close", "stderr.close"));
    failed(StopGateFailure.COMMAND_FAILURE, () -> reader(child).readState());
    child.allClosed();
  }

  @Test
  void nativeEnvironmentAndConcurrency() throws Exception {
    var builder = SystemctlStateSource.NativeProcess.builder(stateCommand());
    assertEquals(stateCommand(), builder.command());
    assertEquals(
        Map.of(
            "PATH",
            "/usr/bin:/bin",
            "LANG",
            "C",
            "LC_ALL",
            "C",
            "SYSTEMD_COLORS",
            "0",
            "TERM",
            "dumb"),
        builder.environment());
    assertEquals(ProcessBuilder.Redirect.DISCARD, builder.redirectError());
    assertEquals(ProcessBuilder.Redirect.PIPE, builder.redirectInput());
    assertEquals(ProcessBuilder.Redirect.PIPE, builder.redirectOutput());
    // Unprovisioned PG/PT host: reject not-found, never claim a deployed Inspector lifecycle.
    var nativeReader = new InspectorUnitProbe.NativeReader();
    byte[] actual = nativeReader.readState();
    try {
      String observed = new String(actual, StandardCharsets.US_ASCII);
      assertTrue(observed.contains("Id=schubert-nk-inbox-inspector.service\n"));
      assertTrue(observed.contains("LoadState=not-found\n"));
    } finally {
      Arrays.fill(actual, (byte) 0);
    }
    failed(StopGateFailure.COMMAND_FAILURE, nativeReader::readProcesses);
    failed(StopGateFailure.MALFORMED_STATE, () -> new InspectorUnitProbe().read());
    AtomicInteger states = new AtomicInteger();
    AtomicInteger processes = new AtomicInteger();
    var shared =
        new InspectorUnitProbe(
            new InspectorUnitProbe.Reader() {
              @Override
              public byte[] readState() {
                states.incrementAndGet();
                return GOLDEN.getBytes(StandardCharsets.US_ASCII);
              }

              @Override
              public byte[] readProcesses() {
                processes.incrementAndGet();
                return "a(sus) 0\n".getBytes(StandardCharsets.US_ASCII);
              }
            });
    try (var pool = Executors.newFixedThreadPool(8)) {
      List<Future<OptionalInt>> futures = new ArrayList<>();
      for (int i = 0; i < 64; i++)
        futures.add(pool.submit(() -> shared.completionAfter(Optional.empty())));
      for (var future : futures) assertEquals(OptionalInt.of(10), future.get(10, TimeUnit.SECONDS));
    }
    assertEquals(128, states.get());
    assertEquals(64, processes.get());
  }

  private static List<String> stateCommand() {
    return List.of(
        "/usr/bin/systemctl",
        "--system",
        "--no-pager",
        "--no-ask-password",
        "show",
        "--property=Id,LoadState,ActiveState,SubState,Job,MainPID,ControlPID,InvocationID,ExecMainCode,ExecMainStatus,ExecMainStartTimestampMonotonic,ExecMainExitTimestampMonotonic,Result,Type,Restart,RemainAfterExit,KillMode,SendSIGKILL",
        "schubert-nk-inbox-inspector.service");
  }

  /** PT-DEP-1007001: a streaming-query launch failure is sanitized before any child exists. */
  @Test
  void streamingStartIoFailureIsSanitizedWithoutRetry() {
    var calls = new AtomicInteger();
    var expected = List.of("literal-stream-query");
    var reader =
        new InspectorUnitProbe.NativeReader(
            command -> {
              assertEquals(expected, command);
              calls.incrementAndGet();
              throw new IOException("PUBLIC_STREAM_DIAGNOSTIC_CANARY");
            });
    failed(
        StopGateFailure.COMMAND_FAILURE,
        () -> reader.executeStreaming(expected, 4, TimeUnit.SECONDS.toNanos(5)));
    assertEquals(1, calls.get());
  }

  /** PT-DEP-1007002: independent ASCII boundary; output N+1 rejects and closes the real child. */
  @Test
  void streamingLiteralByteLimitAndOverflowCloseActualProcess() throws Exception {
    for (String literal : List.of("ABCD", "ABCDE")) {
      var process =
          new ObservedProcess(new ProcessBuilder("/usr/bin/printf", "%s", literal).start());
      var reader = new InspectorUnitProbe.NativeReader(command -> process);
      if (literal.length() == 4) {
        byte[] actual =
            reader.executeStreaming(
                List.of("literal-stream-query"), 4, TimeUnit.SECONDS.toNanos(5));
        try {
          assertArrayEquals(new byte[] {65, 66, 67, 68}, actual);
        } finally {
          Arrays.fill(actual, (byte) 0);
        }
      } else {
        failed(
            StopGateFailure.MALFORMED_STATE,
            () ->
                reader.executeStreaming(
                    List.of("literal-stream-query"), 4, TimeUnit.SECONDS.toNanos(5)));
      }
      assertFalse(process.isAlive());
      assertEquals(0, process.exitValue());
      assertEquals(1, process.stdoutCloses.get());
      assertEquals(1, process.stdinCloses.get());
      assertEquals(1, process.stderrCloses.get());
    }
  }

  /** Transparent actual-process delegation; closure is observed independently of EOF behavior. */
  @Test
  void streamingReadFaultPreservesUnknownFailureAndSanitizesIo() throws Exception {
    // PT-DEP-1015001: independent provider faults, actual process exit, all resources closed.
    for (Throwable fault :
        List.of(
            new IOException("public IO"),
            new IllegalStateException("public unknown"),
            new NullPointerException("public unknown null contract"),
            new AssertionError("public fatal"))) {
      Process actual = new ProcessBuilder("/usr/bin/printf", "%s", "ABCD").start();
      var stream =
          new FilterInputStream(actual.getInputStream()) {
            @Override
            public int read(byte[] bytes, int offset, int length) throws IOException {
              if (fault instanceof IOException io) throw io;
              if (fault instanceof RuntimeException unknown) throw unknown;
              throw (Error) fault;
            }
          };
      var process = new ObservedProcess(actual, stream);
      var reader = new InspectorUnitProbe.NativeReader(command -> process);
      if (fault instanceof IOException) {
        failed(
            StopGateFailure.COMMAND_FAILURE,
            () ->
                reader.executeStreaming(
                    List.of("literal-read-fault"), 4, TimeUnit.SECONDS.toNanos(5)));
      } else {
        assertSame(
            fault,
            assertThrows(
                fault.getClass(),
                () ->
                    reader.executeStreaming(
                        List.of("literal-read-fault"), 4, TimeUnit.SECONDS.toNanos(5))));
      }
      assertFalse(process.isAlive());
      assertEquals(0, process.exitValue());
      assertEquals(1, process.stdoutCloses.get());
      assertEquals(1, process.stdinCloses.get());
      assertEquals(1, process.stderrCloses.get());
    }
  }

  /** Transparent actual-process delegation; closure is observed independently of EOF behavior. */
  private static final class ObservedProcess extends Process {
    private final Process delegate;
    final AtomicInteger stdoutCloses = new AtomicInteger();
    final AtomicInteger stdinCloses = new AtomicInteger();
    final AtomicInteger stderrCloses = new AtomicInteger();
    private final InputStream output;
    private final OutputStream input;
    private final InputStream error;

    ObservedProcess(Process delegate) {
      this(delegate, delegate.getInputStream());
    }

    ObservedProcess(Process delegate, InputStream stdout) {
      this.delegate = delegate;
      output = observed(stdout, stdoutCloses);
      error = observed(delegate.getErrorStream(), stderrCloses);
      input =
          new FilterOutputStream(delegate.getOutputStream()) {
            @Override
            public void close() throws IOException {
              stdinCloses.incrementAndGet();
              super.close();
            }
          };
    }

    private static InputStream observed(InputStream stream, AtomicInteger closes) {
      return new FilterInputStream(stream) {
        @Override
        public void close() throws IOException {
          closes.incrementAndGet();
          super.close();
        }
      };
    }

    @Override
    public InputStream getInputStream() {
      return output;
    }

    @Override
    public OutputStream getOutputStream() {
      return input;
    }

    @Override
    public InputStream getErrorStream() {
      return error;
    }

    @Override
    public int waitFor() throws InterruptedException {
      return delegate.waitFor();
    }

    @Override
    public boolean waitFor(long timeout, TimeUnit unit) throws InterruptedException {
      return delegate.waitFor(timeout, unit);
    }

    @Override
    public int exitValue() {
      return delegate.exitValue();
    }

    @Override
    public boolean isAlive() {
      return delegate.isAlive();
    }

    @Override
    public void destroy() {
      delegate.destroy();
    }

    @Override
    public Process destroyForcibly() {
      delegate.destroyForcibly();
      return this;
    }
  }

  private static List<String> processCommand() {
    return List.of(
        "/usr/bin/busctl",
        "--system",
        "--timeout=5s",
        "--no-pager",
        "call",
        "org.freedesktop.systemd1",
        "/org/freedesktop/systemd1",
        "org.freedesktop.systemd1.Manager",
        "GetUnitProcesses",
        "s",
        "schubert-nk-inbox-inspector.service");
  }

  private static Child child() {
    return new Child(GOLDEN.getBytes(StandardCharsets.US_ASCII));
  }

  private static InspectorUnitProbe.NativeReader reader(Child child) {
    return new InspectorUnitProbe.NativeReader(
        command -> {
          child.event("start");
          return child;
        });
  }

  private static void failed(
      StopGateFailure reason, org.junit.jupiter.api.function.Executable action) {
    var failure = assertThrows(StopGateException.class, action);
    assertEquals(reason, failure.reason());
    assertEquals("application stop check failed", failure.getMessage());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
  }
}
