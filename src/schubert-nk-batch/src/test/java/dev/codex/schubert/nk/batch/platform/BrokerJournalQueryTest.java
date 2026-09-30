package dev.codex.schubert.nk.batch.platform;

import static org.junit.jupiter.api.Assertions.*;

import java.io.*;
import java.util.*;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Test;

/** NK-OPS-001/OPS009/UI251/SS343 SSC125; BROKERQUERY001..003. Independent process IO. */
final class BrokerJournalQueryTest {
  private static final List<String> COMMAND = List.of("/usr/bin/journalctl", "--output=json");

  @Test
  void concurrentDrainAndOwnedStreams() {
    byte[] golden = new byte[131072];
    Arrays.fill(golden, (byte) 'J');
    var child = new Child(golden);
    assertArrayEquals(
        golden, reader(child).executeStreaming(COMMAND, golden.length, 2_000_000_000L));
    assertEquals(1, child.stdoutClosed);
    assertEquals(1, child.stdinClosed);
    assertEquals(1, child.stderrClosed);
    assertFalse(child.destroyed);
    assertTrue(child.waitBound > 0 && child.waitBound <= 2_000_000_000L);
    assertEquals(TimeUnit.NANOSECONDS, child.waitUnit);
  }

  @Test
  void sizeExitTimeoutAndInterruptedRemainFailures() {
    var large = new Child(new byte[17]);
    assertReason(StopGateFailure.MALFORMED_STATE, large, 16);
    var failed = new Child(new byte[0]);
    failed.exit = 7;
    assertReason(StopGateFailure.COMMAND_FAILURE, failed, 16);
    var timeout = new Child(new byte[0]);
    timeout.completed = false;
    assertReason(StopGateFailure.TIMEOUT, timeout, 16);
    assertTrue(timeout.destroyed);
    var interrupt = new Child(new byte[0]);
    interrupt.interrupt = true;
    try {
      assertReason(StopGateFailure.INTERRUPTED, interrupt, 16);
      assertTrue(Thread.currentThread().isInterrupted());
    } finally {
      Thread.interrupted();
    }
    assertThrows(StopGateException.class, () -> reader(failed).executeStreaming(COMMAND, 0, 1));
    assertThrows(StopGateException.class, () -> reader(failed).executeStreaming(COMMAND, 1, 0));
  }

  @Test
  void declaredReadFailureUnknownFailureAndCloseFailure() {
    var io = new Child(new byte[0]);
    io.readFailure = new IOException("fixture");
    assertReason(StopGateFailure.COMMAND_FAILURE, io, 16);
    for (Throwable unexpected :
        List.of(new IllegalStateException("fixture"), new AssertionError("fixture"))) {
      var child = new Child(new byte[0]);
      child.readFailure = unexpected;
      assertSame(
          unexpected,
          assertThrows(
              unexpected.getClass(),
              () -> reader(child).executeStreaming(COMMAND, 16, 2_000_000_000L)));
      assertEquals(1, child.stdoutClosed);
      assertEquals(1, child.stdinClosed);
      assertEquals(1, child.stderrClosed);
    }
    var close = new Child(new byte[0]);
    close.closeFailure = true;
    assertReason(StopGateFailure.COMMAND_FAILURE, close, 16);
    assertTrue(close.destroyed);
  }

  private static InspectorUnitProbe.NativeReader reader(Child child) {
    return new InspectorUnitProbe.NativeReader(
        command -> {
          assertEquals(COMMAND, command);
          return child;
        });
  }

  private static void assertReason(StopGateFailure reason, Child child, int limit) {
    assertEquals(
        reason,
        assertThrows(
                StopGateException.class,
                () -> reader(child).executeStreaming(COMMAND, limit, 2_000_000_000L))
            .reason());
    assertEquals(1, child.stdoutClosed);
    assertEquals(1, child.stdinClosed);
    assertEquals(1, child.stderrClosed);
  }

  private static final class Child extends Process {
    private final byte[] bytes;
    private int stdoutClosed, stdinClosed, stderrClosed, exit;
    private boolean completed = true, alive = true, destroyed, interrupt, closeFailure;
    private Throwable readFailure;
    private long waitBound;
    private TimeUnit waitUnit;

    Child(byte[] bytes) {
      this.bytes = bytes;
    }

    @Override
    public InputStream getInputStream() {
      return new ByteArrayInputStream(bytes) {
        @Override
        public byte[] readNBytes(int count) throws IOException {
          assertTrue(Thread.currentThread().isVirtual());
          if (readFailure instanceof IOException failure) throw failure;
          if (readFailure instanceof RuntimeException failure) throw failure;
          if (readFailure instanceof Error failure) throw failure;
          return super.readNBytes(count);
        }

        @Override
        public void close() {
          stdoutClosed++;
        }
      };
    }

    @Override
    public OutputStream getOutputStream() {
      return new ByteArrayOutputStream() {
        @Override
        public void close() throws IOException {
          stdinClosed++;
          if (closeFailure) throw new IOException("fixture");
        }
      };
    }

    @Override
    public InputStream getErrorStream() {
      return new ByteArrayInputStream(new byte[0]) {
        @Override
        public void close() {
          stderrClosed++;
        }
      };
    }

    @Override
    public int waitFor() {
      throw new AssertionError("unbounded wait forbidden");
    }

    @Override
    public boolean waitFor(long timeout, TimeUnit unit) throws InterruptedException {
      waitBound = timeout;
      waitUnit = unit;
      if (interrupt) throw new InterruptedException("fixture");
      alive = !completed;
      return completed;
    }

    @Override
    public int exitValue() {
      assertFalse(alive);
      return exit;
    }

    @Override
    public boolean isAlive() {
      return alive;
    }

    @Override
    public void destroy() {
      destroyed = true;
      alive = false;
    }
  }
}
