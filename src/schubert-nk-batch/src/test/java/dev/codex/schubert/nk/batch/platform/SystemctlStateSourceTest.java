package dev.codex.schubert.nk.batch.platform;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.nio.charset.StandardCharsets;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Test;

/** NK-OPS-001/PT-OPS-STOP-009..016; SS341/343; real readonly tool and fault-controlled Process. */
final class SystemctlStateSourceTest {
  @Test
  void fixedCommandAndSuccess() {
    for (var unit : ApplicationUnit.values()) {
      var child = new Child("public byte vector".getBytes(StandardCharsets.US_ASCII));
      var source =
          new SystemctlStateSource(
              command -> {
                assertEquals(
                    List.of(
                        "/usr/bin/systemctl",
                        "--system",
                        "--no-pager",
                        "--no-ask-password",
                        "show",
                        "--property=Id,LoadState,ActiveState,SubState,Job,MainPID,ControlPID",
                        unit == ApplicationUnit.API
                            ? "schubert-nk-api.service"
                            : "schubert-nk-web.service"),
                    command);
                return child;
              });
      assertArrayEquals(
          "public byte vector".getBytes(StandardCharsets.US_ASCII), source.read(unit));
      closed(child);
      assertEquals(0, child.destroyed);
      assertEquals(1, child.output.reads);
    }
  }

  @Test
  void commandFailure() {
    failed(
        StopGateFailure.COMMAND_FAILURE,
        () ->
            new SystemctlStateSource(
                    command -> {
                      throw new IOException("SECRET_CANARY");
                    })
                .read(ApplicationUnit.API));
    for (int code : List.of(1, 20, 50, 255, -1)) {
      var child = new Child(new byte[] {1});
      child.code = code;
      failed(StopGateFailure.COMMAND_FAILURE, () -> source(child).read(ApplicationUnit.API));
      closed(child);
      assertEquals(0, child.output.reads);
      assertEquals(0, child.destroyed);
    }
  }

  @Test
  void timeoutAndTermination() {
    var child = new Child(new byte[0]);
    child.completed = false;
    failed(StopGateFailure.TIMEOUT, () -> source(child).read(ApplicationUnit.API));
    closed(child);
    assertEquals(1, child.destroyed);
    assertEquals(0, child.output.reads);
  }

  @Test
  void interruptedWait() {
    var child = new Child(new byte[0]);
    child.interrupted = true;
    try {
      failed(StopGateFailure.INTERRUPTED, () -> source(child).read(ApplicationUnit.API));
      assertTrue(Thread.currentThread().isInterrupted());
      closed(child);
      assertEquals(1, child.destroyed);
    } finally {
      Thread.interrupted();
    }
  }

  @Test
  void outputBoundaries() {
    for (int size : List.of(0, 1, 1024)) {
      var bytes = new byte[size];
      Arrays.fill(bytes, (byte) 'x');
      var child = new Child(bytes);
      assertArrayEquals(bytes, source(child).read(ApplicationUnit.API));
      closed(child);
    }
    for (int size : List.of(1025, 20000)) {
      var child = new Child(new byte[size]);
      failed(StopGateFailure.MALFORMED_STATE, () -> source(child).read(ApplicationUnit.API));
      closed(child);
      assertEquals(1025, child.output.maximumRequested);
    }
    var child = new Child(new byte[0]);
    child.output.failRead = true;
    failed(StopGateFailure.COMMAND_FAILURE, () -> source(child).read(ApplicationUnit.API));
    closed(child);
  }

  @Test
  void closeFailures() {
    // PG173/SSC063/BUG195/YKT154: independent 4 x 3 x 7 compound matrix.
    for (String scope : List.of("output", "input", "error", "term"))
      for (String primary :
          List.of("runtime", "io", "timeout", "interrupt", "exit", "oversize", "success"))
        for (Throwable unknown :
            List.of(
                new IllegalStateException("synthetic compound"),
                new NullPointerException("synthetic compound"),
                new AssertionError("synthetic compound"))) {
          byte[] vector = new byte[primary.equals("oversize") ? 1025 : 3];
          java.util.Arrays.fill(vector, (byte) 7);
          var compound = new Child(vector);
          compound.cleanupAlive = true;
          int[] injected = {0};
          Runnable cleanup =
              () -> {
                injected[0]++;
                throwUnknown(unknown);
              };
          switch (scope) {
            case "output" -> compound.output.ending = cleanup;
            case "input" -> compound.input.ending = cleanup;
            case "error" -> compound.error.ending = cleanup;
            case "term" -> compound.ending = cleanup;
            default -> throw new AssertionError(scope);
          }
          if (primary.equals("runtime")) compound.waiting = () -> throwUnknown(unknown);
          if (primary.equals("io")) compound.output.failRead = true;
          if (primary.equals("timeout")) compound.completed = false;
          if (primary.equals("interrupt")) compound.interrupted = true;
          if (primary.equals("exit")) compound.code = 1;
          try {
            Throwable actual =
                assertThrows(unknown.getClass(), () -> source(compound).read(ApplicationUnit.API));
            assertSame(unknown, actual);
            assertEquals(primary.equals("runtime") ? 1 : 0, actual.getSuppressed().length);
            if (primary.equals("runtime")) {
              var fixed = assertInstanceOf(StopGateException.class, actual.getSuppressed()[0]);
              assertEquals(StopGateFailure.COMMAND_FAILURE, fixed.reason());
              assertNull(fixed.getCause());
              assertEquals(0, fixed.getSuppressed().length);
            }
            assertEquals(1, injected[0]);
            closed(compound);
            assertEquals(1, compound.destroyed);
            assertEquals(primary.equals("interrupt"), Thread.currentThread().isInterrupted());
            assertEquals(
                primary.equals("oversize") ? 1025 : primary.equals("success") ? 3 : 0,
                compound.output.delivered.length);
            assertArrayEquals(
                new byte[compound.output.delivered.length], compound.output.delivered);
          } finally {
            Thread.interrupted();
          }
        }
    for (String stream : List.of("output", "input", "error"))
      for (String primary : List.of("success", "exit", "timeout", "oversize", "io", "interrupt")) {
        var child = new Child(new byte[primary.equals("oversize") ? 1025 : 0]);
        child.output.failClose = stream.equals("output");
        child.input.failClose = stream.equals("input");
        child.error.failClose = stream.equals("error");
        if (primary.equals("exit")) child.code = 1;
        if (primary.equals("timeout")) child.completed = false;
        if (primary.equals("io")) child.output.failRead = true;
        if (primary.equals("interrupt")) child.interrupted = true;
        var expected =
            switch (primary) {
              case "timeout" -> StopGateFailure.TIMEOUT;
              case "oversize" -> StopGateFailure.MALFORMED_STATE;
              case "interrupt" -> StopGateFailure.INTERRUPTED;
              default -> StopGateFailure.COMMAND_FAILURE;
            };
        try {
          failed(expected, () -> source(child).read(ApplicationUnit.API));
          closed(child);
          assertEquals(primary.equals("interrupt"), Thread.currentThread().isInterrupted());
        } finally {
          Thread.interrupted();
        }
      }
    var child = new Child(new byte[0]);
    child.output.failClose = true;
    child.input.failClose = true;
    child.error.failClose = true;
    failed(StopGateFailure.COMMAND_FAILURE, () -> source(child).read(ApplicationUnit.API));
    closed(child);
  }

  @Test
  void nativeEnvironmentAndRead() {
    var command = List.of("/usr/bin/systemctl", "--version");
    var builder = SystemctlStateSource.NativeProcess.builder(command);
    assertEquals(command, builder.command());
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
    for (var unit : ApplicationUnit.values()) {
      var result = new SystemctlStateSource().read(unit);
      assertTrue(result.length > 0 && result.length <= 1024);
      var fields = new HashMap<String, String>();
      for (String line :
          new String(result, StandardCharsets.US_ASCII).stripTrailing().split("\n")) {
        int equals = line.indexOf('=');
        assertTrue(equals > 0);
        assertNull(fields.put(line.substring(0, equals), line.substring(equals + 1)));
      }
      assertEquals(
          Set.of("Id", "LoadState", "ActiveState", "SubState", "Job", "MainPID", "ControlPID"),
          fields.keySet());
      assertEquals(
          unit == ApplicationUnit.API ? "schubert-nk-api.service" : "schubert-nk-web.service",
          fields.get("Id"));
      assertEquals(
          "not-found",
          fields.get("LoadState"),
          "unprovisioned PG/PT host only; not a deployment acceptance test");
    }
  }

  @Test
  void nullAndRuntimeContracts() {
    // BUG-157: register each acquisition before the next getter may fail.
    for (String getter : List.of("output", "input", "error")) {
      var failed = new Child(new byte[0]);
      failed.getFailure = getter;
      assertSame(
          failed.getterFailure,
          assertThrows(
              IllegalStateException.class, () -> source(failed).read(ApplicationUnit.API)));
      assertEquals(getter.equals("output") ? 0 : 1, failed.output.closed);
      assertEquals(getter.equals("error") ? 1 : 0, failed.input.closed);
      assertEquals(0, failed.error.closed);
      assertEquals(0, failed.waits);
      assertEquals(0, failed.output.reads);
      assertEquals(1, failed.destroyed);
    }
    for (String getter : List.of("output", "input", "error")) {
      var missing = new Child(new byte[0]);
      missing.nullGetter = getter;
      assertThrows(NullPointerException.class, () -> source(missing).read(ApplicationUnit.API));
      assertEquals(getter.equals("output") ? 0 : 1, missing.output.closed);
      assertEquals(getter.equals("input") ? 0 : 1, missing.input.closed);
      assertEquals(getter.equals("error") ? 0 : 1, missing.error.closed);
      assertEquals(0, missing.waits);
      assertEquals(0, missing.output.reads);
      assertEquals(1, missing.destroyed);
    }
    assertThrows(
        NullPointerException.class,
        () -> new SystemctlStateSource(command -> null).read(ApplicationUnit.API));
    assertThrows(NullPointerException.class, () -> new SystemctlStateSource(null));
    var child = new Child(new byte[0]);
    assertThrows(NullPointerException.class, () -> source(child).read(null));
    assertEquals(0, child.output.closed);
    var runtime = new IllegalStateException("programming failure");
    child.runtime = runtime;
    assertSame(
        runtime,
        assertThrows(IllegalStateException.class, () -> source(child).read(ApplicationUnit.API)));
    closed(child);
    assertEquals(1, child.destroyed);
    assertSame(
        runtime,
        assertThrows(
            IllegalStateException.class,
            () ->
                new SystemctlStateSource(
                        command -> {
                          throw runtime;
                        })
                    .read(ApplicationUnit.API)));
  }

  private static void throwUnknown(Throwable failure) {
    if (failure instanceof RuntimeException runtime) throw runtime;
    throw (Error) failure;
  }

  private static SystemctlStateSource source(Child child) {
    return new SystemctlStateSource(command -> child);
  }

  private static void closed(Child child) {
    assertEquals(1, child.output.closed);
    assertEquals(1, child.input.closed);
    assertEquals(1, child.error.closed);
  }

  private static void failed(StopGateFailure expected, Runnable action) {
    var failure = assertThrows(StopGateException.class, action::run);
    assertEquals(expected, failure.reason());
    assertEquals("application stop check failed", failure.getMessage());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
  }

  private static final class Child extends Process {
    final ReadStream output;
    final ReadStream error = new ReadStream(new byte[0]);
    final WriteStream input = new WriteStream();
    boolean completed = true;
    boolean interrupted;
    boolean alive = true;
    boolean cleanupAlive;
    Runnable waiting = () -> {};
    Runnable ending = () -> {};
    int code;
    int destroyed;
    int waits;
    RuntimeException runtime;
    String getFailure = "";
    String nullGetter = "";
    final IllegalStateException getterFailure =
        new IllegalStateException("synthetic getter failure");

    Child(byte[] bytes) {
      output = new ReadStream(bytes);
    }

    @Override
    public InputStream getInputStream() {
      if (getFailure.equals("output")) throw getterFailure;
      if (nullGetter.equals("output")) return null;
      return output;
    }

    @Override
    public InputStream getErrorStream() {
      if (getFailure.equals("error")) throw getterFailure;
      if (nullGetter.equals("error")) return null;
      return error;
    }

    @Override
    public OutputStream getOutputStream() {
      if (getFailure.equals("input")) throw getterFailure;
      if (nullGetter.equals("input")) return null;
      return input;
    }

    @Override
    public int waitFor() {
      throw new AssertionError("unbounded wait forbidden");
    }

    @Override
    public boolean waitFor(long timeout, TimeUnit unit) throws InterruptedException {
      waits++;
      assertEquals(5, timeout);
      assertEquals(TimeUnit.SECONDS, unit);
      waiting.run();
      if (runtime != null) throw runtime;
      if (interrupted) throw new InterruptedException("SECRET_CANARY");
      alive = !completed;
      return completed;
    }

    @Override
    public int exitValue() {
      assertFalse(alive);
      return code;
    }

    @Override
    public boolean isAlive() {
      return alive || cleanupAlive;
    }

    @Override
    public void destroy() {
      destroyed++;
      alive = false;
      ending.run();
    }

    @Override
    public Process destroyForcibly() {
      throw new AssertionError("SIGKILL forbidden");
    }
  }

  private static final class ReadStream extends InputStream {
    final ByteArrayInputStream bytes;
    boolean failRead;
    boolean failClose;
    int closed;
    int reads;
    int maximumRequested;
    byte[] delivered = new byte[0];
    Runnable ending = () -> {};

    ReadStream(byte[] bytes) {
      this.bytes = new ByteArrayInputStream(bytes);
    }

    @Override
    public int read() {
      throw new AssertionError("bounded read required");
    }

    @Override
    public byte[] readNBytes(int length) throws IOException {
      assertEquals(1025, length);
      maximumRequested = length;
      reads++;
      if (failRead) throw new IOException("SECRET_CANARY");
      delivered = bytes.readNBytes(length);
      return delivered;
    }

    @Override
    public void close() throws IOException {
      closed++;
      ending.run();
      if (failClose) throw new IOException("SECRET_CANARY");
    }
  }

  private static final class WriteStream extends OutputStream {
    boolean failClose;
    int closed;
    Runnable ending = () -> {};

    @Override
    public void write(int value) {
      throw new AssertionError("no command stdin");
    }

    @Override
    public void close() throws IOException {
      closed++;
      ending.run();
      if (failClose) throw new IOException("SECRET_CANARY");
    }
  }
}
