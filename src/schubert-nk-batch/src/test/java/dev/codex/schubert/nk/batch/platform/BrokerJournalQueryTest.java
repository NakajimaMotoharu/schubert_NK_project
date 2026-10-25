package dev.codex.schubert.nk.batch.platform;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.InterruptedIOException;
import java.io.OutputStream;
import java.util.Arrays;
import java.util.List;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Test;

/** NK-OPS-001/OPS009/UI251/SS343 SSC125; BROKERQUERY001..003. Independent process IO. */
final class BrokerJournalQueryTest {
  private static final List<String> COMMAND = List.of("/usr/bin/journalctl", "--output=json");

  @Test
  void inspector919003StartAndCompletedWaitRespectOriginalQueryBudget() {
    var slowStart = new Child(new byte[0]);
    var reader =
        new InspectorUnitProbe.NativeReader(
            command -> {
              assertEquals(COMMAND, command);
              consumeNanos(100_000_000L);
              return slowStart;
            });
    assertEquals(
        StopGateFailure.TIMEOUT,
        assertThrows(
                StopGateException.class, () -> reader.executeStreaming(COMMAND, 16, 50_000_000L))
            .reason());
    assertEquals(1, slowStart.stdoutClosed);
    assertEquals(1, slowStart.stdinClosed);
    assertEquals(1, slowStart.stderrClosed);
    assertFalse(slowStart.isAlive());
    var slowWait = new Child(new byte[0]);
    slowWait.waitDelayNanos = 100_000_000L;
    assertEquals(
        StopGateFailure.TIMEOUT,
        assertThrows(
                StopGateException.class,
                () -> reader(slowWait).executeStreaming(COMMAND, 16, 50_000_000L))
            .reason());
    assertEquals(1, slowWait.stdoutClosed);
    assertEquals(1, slowWait.stdinClosed);
    assertEquals(1, slowWait.stderrClosed);
    assertFalse(slowWait.isAlive());
  }

  @Test
  void inspector919004ExpiredStdoutDrainCancelsReaderAndClosesEveryStream() throws Exception {
    var blocked = new Child(new byte[0]);
    blocked.readDelayNanos = 5_000_000_000L;
    assertEquals(
        StopGateFailure.TIMEOUT,
        assertThrows(
                StopGateException.class,
                () -> reader(blocked).executeStreaming(COMMAND, 16, 1_000_000_000L))
            .reason());
    assertTrue(blocked.drainFinished.await(5, TimeUnit.SECONDS));
    assertEquals(1, blocked.stdoutClosed);
    assertEquals(1, blocked.stdinClosed);
    assertEquals(1, blocked.stderrClosed);
    assertFalse(blocked.isAlive());
  }

  private static void consumeNanos(long nanos) {
    long end = System.nanoTime() + nanos;
    while (System.nanoTime() < end && !Thread.currentThread().isInterrupted()) {
      java.util.concurrent.locks.LockSupport.parkNanos(
          Math.min(20_000_000L, end - System.nanoTime()));
    }
  }

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
    private int stdoutClosed;
    private int stdinClosed;
    private int stderrClosed;
    private int exit;
    private boolean completed = true;
    private boolean alive = true;
    private boolean destroyed;
    private boolean interrupt;
    private boolean closeFailure;
    private Throwable readFailure;
    private long waitBound;
    private TimeUnit waitUnit;
    private long waitDelayNanos;
    private long readDelayNanos;
    private final CountDownLatch drainStarted = new CountDownLatch(1);
    private final CountDownLatch drainFinished = new CountDownLatch(1);

    Child(byte[] bytes) {
      this.bytes = bytes;
    }

    @Override
    public InputStream getInputStream() {
      return new ByteArrayInputStream(bytes) {
        @Override
        public byte[] readNBytes(int count) throws IOException {
          assertTrue(Thread.currentThread().isVirtual());
          if (readDelayNanos > 0) {
            drainStarted.countDown();
            try {
              consumeNanos(readDelayNanos);
              if (Thread.currentThread().isInterrupted())
                throw new InterruptedIOException("fixture cancelled");
            } finally {
              drainFinished.countDown();
            }
          }
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
      if (readDelayNanos > 0) assertTrue(drainStarted.await(5, TimeUnit.SECONDS));
      if (waitDelayNanos > 0) consumeNanos(waitDelayNanos);
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
