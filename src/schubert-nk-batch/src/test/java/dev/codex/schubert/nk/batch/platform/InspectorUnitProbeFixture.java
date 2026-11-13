package dev.codex.schubert.nk.batch.platform;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;

import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.TimeUnit;
import java.util.function.BiConsumer;

/** Public synthetic process/reader fault ports; no private production reflection, UNIT009..016. */
final class InspectorUnitProbeFixture {
  private static final String GOLDEN =
      "Id=schubert-nk-inbox-inspector.service\nLoadState=loaded\nActiveState=active\nSubState=exited\nJob=\nMainPID=0\nControlPID=0\nInvocationID=123456789abcdef08123456789abcdef\nExecMainCode=1\nExecMainStatus=10\nExecMainStartTimestampMonotonic=1234567\nExecMainExitTimestampMonotonic=2345678\nResult=success\nType=oneshot\nRestart=no\nRemainAfterExit=no\nKillMode=control-group\nSendSIGKILL=no\n";

  private InspectorUnitProbeFixture() {}

  static final class Script implements InspectorUnitProbe.Reader {
    final List<String> calls = new ArrayList<>();
    final List<byte[]> delivered = new ArrayList<>();
    List<String> states = List.of(GOLDEN, GOLDEN);
    byte[] processes = "a(sus) 0\n".getBytes(StandardCharsets.US_ASCII);
    int stateAt;
    int failAt;
    int nullAt;
    int interruptAt;
    RuntimeException runtime;

    private byte[] next(String type, byte[] bytes) throws IOException {
      calls.add(type);
      if (calls.size() == interruptAt) Thread.currentThread().interrupt();
      if (calls.size() == failAt) {
        if (runtime != null) throw runtime;
        throw new IOException("PUBLIC_DIAGNOSTIC_CANARY");
      }
      if (calls.size() == nullAt) return null;
      byte[] result = bytes.clone();
      delivered.add(result);
      return result;
    }

    @Override
    public byte[] readState() throws IOException {
      int currentState = stateAt;
      stateAt++;
      return next(
          "state",
          states
              .get(Math.min(currentState, states.size() - 1))
              .getBytes(StandardCharsets.US_ASCII));
    }

    @Override
    public byte[] readProcesses() throws IOException {
      return next("processes", processes);
    }

    void wiped() {
      for (byte[] bytes : delivered) assertArrayEquals(new byte[bytes.length], bytes);
    }
  }

  static final class Child extends Process {
    final ReadStream output;
    final ReadStream error;
    final WriteStream input;
    final Map<String, Integer> counts = new LinkedHashMap<>();
    final List<String> order = new ArrayList<>();
    final Set<String> ioFailures = new HashSet<>();
    BiConsumer<String, Integer> hook = (name, count) -> {};
    boolean completed = true;
    boolean waitInterrupt;
    boolean alive = true;
    long waitSeconds = 5;
    String missing = "";
    int code;
    int destroyed;
    byte[] delivered = new byte[0];

    Child(byte[] bytes) {
      output = new ReadStream("stdout", bytes);
      error = new ReadStream("stderr", new byte[0]);
      input = new WriteStream();
    }

    void event(String name) {
      order.add(name);
      hook.accept(name, counts.merge(name, 1, Integer::sum));
    }

    void io(String name) throws IOException {
      event(name);
      if (ioFailures.contains(name)) throw new IOException("PUBLIC_DIAGNOSTIC_CANARY");
    }

    @Override
    public InputStream getInputStream() {
      event("get.stdout");
      return missing.equals("stdout") ? null : output;
    }

    @Override
    public OutputStream getOutputStream() {
      event("get.stdin");
      return missing.equals("stdin") ? null : input;
    }

    @Override
    public InputStream getErrorStream() {
      event("get.stderr");
      return missing.equals("stderr") ? null : error;
    }

    @Override
    public int waitFor() {
      throw new AssertionError("unbounded wait forbidden");
    }

    @Override
    public boolean waitFor(long timeout, TimeUnit unit) throws InterruptedException {
      assertEquals(waitSeconds, timeout);
      assertEquals(TimeUnit.SECONDS, unit);
      event("wait");
      if (waitInterrupt) throw new InterruptedException("PUBLIC_DIAGNOSTIC_CANARY");
      alive = !completed;
      return completed;
    }

    @Override
    public int exitValue() {
      event("exit");
      assertFalse(alive);
      return code;
    }

    @Override
    public boolean isAlive() {
      event("alive");
      return alive;
    }

    @Override
    public void destroy() {
      destroyed++;
      alive = false;
      event("destroy");
    }

    @Override
    public Process destroyForcibly() {
      throw new AssertionError("SIGKILL forbidden");
    }

    void allClosed() {
      assertEquals(1, output.closed);
      assertEquals(1, input.closed);
      assertEquals(1, error.closed);
    }

    void wiped() {
      assertArrayEquals(new byte[delivered.length], delivered);
    }

    final class ReadStream extends InputStream {
      final String name;
      final byte[] bytes;
      int closed;
      int maximum;
      boolean nullRead;

      ReadStream(String name, byte[] bytes) {
        this.name = name;
        this.bytes = bytes.clone();
      }

      @Override
      public int read() {
        throw new AssertionError("bounded bulk reads only");
      }

      @Override
      public byte[] readNBytes(int limit) throws IOException {
        maximum = limit;
        io(name + ".read");
        if (nullRead) return null;
        delivered = Arrays.copyOf(bytes, Math.min(bytes.length, limit));
        return delivered;
      }

      @Override
      public void close() throws IOException {
        closed++;
        io(name + ".close");
      }
    }

    final class WriteStream extends OutputStream {
      int closed;

      @Override
      public void write(int value) {
        throw new AssertionError("queries accept no input");
      }

      @Override
      public void close() throws IOException {
        closed++;
        io("stdin.close");
      }
    }
  }
}
