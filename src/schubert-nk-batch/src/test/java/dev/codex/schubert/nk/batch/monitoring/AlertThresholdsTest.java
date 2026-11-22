package dev.codex.schubert.nk.batch.monitoring;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.Severity;
import java.time.Duration;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.Callable;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.function.Executable;

/** Independent SS351 numbers/time boundaries; PT-OPS-THRESH-001..015/spec1547. */
class AlertThresholdsTest {
  private final AlertThresholds thresholds = new AlertThresholds();
  private static final Duration ZERO = Duration.ZERO;
  private static final Duration MINUTE = Duration.ofSeconds(60);
  private static final Duration FIVE = Duration.ofSeconds(300);
  private static final Duration TEN = Duration.ofSeconds(600);
  private static final Duration THIRTY = Duration.ofSeconds(1800);

  @Test
  void threshold001FilesystemPercentAndDwellBoundaries() {
    assertEquals(Severity.NORMAL, thresholds.filesystem(0, ZERO, ZERO));
    assertEquals(Severity.NORMAL, thresholds.filesystem(Math.nextDown(80.0), FIVE, ZERO));
    assertEquals(Severity.NORMAL, thresholds.filesystem(80, FIVE.minusNanos(1), ZERO));
    assertEquals(Severity.WARNING, thresholds.filesystem(80, FIVE, ZERO));
    assertEquals(Severity.WARNING, thresholds.filesystem(Math.nextDown(90.0), FIVE, MINUTE));
    assertEquals(Severity.WARNING, thresholds.filesystem(90, FIVE, MINUTE.minusNanos(1)));
    assertEquals(Severity.CRITICAL, thresholds.filesystem(90, FIVE, MINUTE));
    assertEquals(Severity.CRITICAL, thresholds.filesystem(100, MINUTE, MINUTE));
  }

  @Test
  void threshold002TransferBytesFilesAndOrBoundaries() {
    assertEquals(Severity.NORMAL, thresholds.transfer(0, 0));
    assertEquals(Severity.NORMAL, thresholds.transfer(3_499_999_999L, 4_999));
    assertEquals(Severity.WARNING, thresholds.transfer(3_500_000_000L, 0));
    assertEquals(Severity.WARNING, thresholds.transfer(0, 5_000));
    assertEquals(Severity.WARNING, thresholds.transfer(4_499_999_999L, 8_999));
    assertEquals(Severity.CRITICAL, thresholds.transfer(4_500_000_000L, 0));
    assertEquals(Severity.CRITICAL, thresholds.transfer(0, 9_000));
    assertEquals(Severity.CRITICAL, thresholds.transfer(Long.MAX_VALUE, Long.MAX_VALUE));
  }

  @Test
  void threshold003AsyncCountRatioAndNoOverflow() {
    assertEquals(Severity.NORMAL, thresholds.asyncQueue(0, 0, 10_000));
    assertEquals(Severity.NORMAL, thresholds.asyncQueue(4_999, 0, 100_000));
    assertEquals(Severity.WARNING, thresholds.asyncQueue(5_000, 0, 100_000));
    assertEquals(Severity.WARNING, thresholds.asyncQueue(8_999, 0, 100_000));
    assertEquals(Severity.CRITICAL, thresholds.asyncQueue(9_000, 0, 100_000));
    assertEquals(Severity.NORMAL, thresholds.asyncQueue(1, 699, 1_000));
    assertEquals(Severity.WARNING, thresholds.asyncQueue(1, 700, 1_000));
    assertEquals(Severity.WARNING, thresholds.asyncQueue(1, 899, 1_000));
    assertEquals(Severity.CRITICAL, thresholds.asyncQueue(1, 900, 1_000));
    assertEquals(Severity.CRITICAL, thresholds.asyncQueue(Long.MAX_VALUE, 0, Long.MAX_VALUE));
    assertEquals(Severity.CRITICAL, thresholds.asyncQueue(0, 1, 1));
    assertEquals(Severity.NORMAL, thresholds.asyncQueue(4999, 0, 1));
    assertEquals(Severity.CRITICAL, thresholds.asyncQueue(0, Long.MAX_VALUE, Long.MAX_VALUE));
    assertEquals(Severity.CRITICAL, thresholds.asyncQueue(0, 100, 99));
  }

  @Test
  void threshold015AsyncByteRatiosDistinguishAdjacentValuesAtLongCapacity() {
    // Ceil(capacity * 70 / 100) and ceil(capacity * 90 / 100), computed independently.
    long capacity = Long.MAX_VALUE;
    assertEquals(Severity.NORMAL, thresholds.asyncQueue(0, 6_456_360_425_798_343_064L, capacity));
    assertEquals(Severity.WARNING, thresholds.asyncQueue(0, 6_456_360_425_798_343_065L, capacity));
    assertEquals(Severity.WARNING, thresholds.asyncQueue(0, 8_301_034_833_169_298_226L, capacity));
    assertEquals(Severity.CRITICAL, thresholds.asyncQueue(0, 8_301_034_833_169_298_227L, capacity));
  }

  @Test
  void threshold004WebLogCountAndOldestAge() {
    assertEquals(Severity.NORMAL, thresholds.webLog(0, ZERO));
    assertEquals(Severity.NORMAL, thresholds.webLog(4_999, FIVE.minusNanos(1)));
    assertEquals(Severity.WARNING, thresholds.webLog(5_000, ZERO));
    assertEquals(Severity.WARNING, thresholds.webLog(1, FIVE));
    assertEquals(Severity.WARNING, thresholds.webLog(8_999, THIRTY.minusNanos(1)));
    assertEquals(Severity.CRITICAL, thresholds.webLog(9_000, ZERO));
    assertEquals(Severity.CRITICAL, thresholds.webLog(1, THIRTY));
  }

  @Test
  void threshold005DlqNonemptyInvestigationAndGrowth() {
    for (boolean increasing : new boolean[] {false, true}) {
      for (boolean uninvestigated : new boolean[] {false, true}) {
        assertEquals(Severity.NORMAL, thresholds.dlq(0, increasing, uninvestigated));
        Severity expected = increasing || uninvestigated ? Severity.CRITICAL : Severity.WARNING;
        assertEquals(expected, thresholds.dlq(1, increasing, uninvestigated));
      }
    }
  }

  @Test
  void threshold006ExpiryCountBoundaries() {
    assertEquals(Severity.NORMAL, thresholds.expiry(0));
    assertEquals(Severity.NORMAL, thresholds.expiry(999));
    assertEquals(Severity.WARNING, thresholds.expiry(1_000));
    assertEquals(Severity.WARNING, thresholds.expiry(4_999));
    assertEquals(Severity.CRITICAL, thresholds.expiry(5_000));
  }

  @Test
  void threshold007PoolUtilizationPendingAndTimeout() {
    assertEquals(Severity.NORMAL, thresholds.dbPool(0, ZERO, 0, 0));
    assertEquals(Severity.NORMAL, thresholds.dbPool(Math.nextDown(80.0), FIVE, 0, 0));
    assertEquals(Severity.NORMAL, thresholds.dbPool(80, FIVE.minusNanos(1), 0, 0));
    assertEquals(Severity.WARNING, thresholds.dbPool(80, FIVE, 0, 0));
    assertEquals(Severity.CRITICAL, thresholds.dbPool(0, ZERO, 1, 0));
    assertEquals(Severity.CRITICAL, thresholds.dbPool(0, ZERO, 0, 1));
  }

  @Test
  void threshold008HeapPercentDwellAndOutOfMemory() {
    assertEquals(Severity.NORMAL, thresholds.jvmHeap(0, ZERO, false));
    assertEquals(Severity.NORMAL, thresholds.jvmHeap(Math.nextDown(75.0), TEN, false));
    assertEquals(Severity.NORMAL, thresholds.jvmHeap(75, TEN.minusNanos(1), false));
    assertEquals(Severity.WARNING, thresholds.jvmHeap(75, TEN, false));
    assertEquals(Severity.WARNING, thresholds.jvmHeap(Math.nextDown(90.0), TEN, false));
    assertEquals(Severity.CRITICAL, thresholds.jvmHeap(90, ZERO, false));
    assertEquals(Severity.CRITICAL, thresholds.jvmHeap(0, ZERO, true));
  }

  @Test
  void threshold009StrictP95AndFiveMinuteDwell() {
    assertEquals(Severity.NORMAL, thresholds.syncP95(0, ZERO, ZERO));
    assertEquals(Severity.NORMAL, thresholds.syncP95(2.0, FIVE, ZERO));
    assertEquals(Severity.NORMAL, thresholds.syncP95(Math.nextUp(2.0), FIVE.minusNanos(1), ZERO));
    assertEquals(Severity.WARNING, thresholds.syncP95(Math.nextUp(2.0), FIVE, ZERO));
    assertEquals(Severity.WARNING, thresholds.syncP95(2.5, FIVE, FIVE));
    assertEquals(Severity.WARNING, thresholds.syncP95(Math.nextUp(2.5), FIVE, FIVE.minusNanos(1)));
    assertEquals(Severity.CRITICAL, thresholds.syncP95(Math.nextUp(2.5), FIVE, FIVE));
  }

  @Test
  void threshold010BackupScheduleSuccessAndConsecutiveFailures() {
    assertEquals(Severity.NORMAL, thresholds.backup(false, false, 0));
    assertEquals(Severity.NORMAL, thresholds.backup(true, true, 0));
    assertEquals(Severity.WARNING, thresholds.backup(true, false, 0));
    assertEquals(Severity.WARNING, thresholds.backup(true, false, 1));
    assertEquals(Severity.CRITICAL, thresholds.backup(true, false, 2));
    assertEquals(Severity.CRITICAL, thresholds.backup(false, true, 2));
  }

  @Test
  void threshold011RestartWindowBoundaries() {
    assertEquals(Severity.NORMAL, thresholds.restarts(0, false));
    assertEquals(Severity.WARNING, thresholds.restarts(1, false));
    assertEquals(Severity.WARNING, thresholds.restarts(4, false));
    assertEquals(Severity.CRITICAL, thresholds.restarts(5, false));
    assertEquals(Severity.CRITICAL, thresholds.restarts(0, true));
    assertEquals(Severity.CRITICAL, thresholds.restarts(4, true));
    assertEquals(Severity.CRITICAL, thresholds.restarts(Long.MAX_VALUE, false));
  }

  @Test
  void threshold012IntegrityNeverWarnsOrAutomaticallyRepairs() {
    assertEquals(Severity.NORMAL, thresholds.integrity(0));
    assertEquals(Severity.CRITICAL, thresholds.integrity(1));
    assertEquals(Severity.CRITICAL, thresholds.integrity(Long.MAX_VALUE));
  }

  @Test
  void threshold013InvalidInputsNeverBecomeNormal() {
    for (double value :
        new double[] {
          -1, Double.NaN, Double.NEGATIVE_INFINITY, Double.POSITIVE_INFINITY, 100.00001
        }) {
      assertEquals(
          "invalid alert observation",
          assertThrows(
                  IllegalArgumentException.class, () -> thresholds.filesystem(value, ZERO, ZERO))
              .getMessage());
    }
    for (double value : new double[] {-1, Double.NaN, Double.POSITIVE_INFINITY})
      assertThrows(IllegalArgumentException.class, () -> thresholds.syncP95(value, ZERO, ZERO));
    List<Executable> negativeCounts =
        List.of(
            () -> thresholds.transfer(-1, 0),
            () -> thresholds.transfer(0, -1),
            () -> thresholds.asyncQueue(-1, 0, 1),
            () -> thresholds.asyncQueue(0, 0, 0),
            () -> thresholds.asyncQueue(0, 0, -1),
            () -> thresholds.asyncQueue(0, -1, 1),
            () -> thresholds.webLog(-1, ZERO),
            () -> thresholds.dlq(-1, false, false),
            () -> thresholds.expiry(-1),
            () -> thresholds.dbPool(0, ZERO, -1, 0),
            () -> thresholds.dbPool(0, ZERO, 0, -1),
            () -> thresholds.backup(false, false, -1),
            () -> thresholds.restarts(-1, false),
            () -> thresholds.restarts(-1, true),
            () -> thresholds.integrity(-1));
    for (var operation : negativeCounts)
      assertEquals(
          "invalid alert observation",
          assertThrows(IllegalArgumentException.class, operation).getMessage());
    List<Executable> nullDurations =
        List.of(
            () -> thresholds.filesystem(0, null, ZERO),
            () -> thresholds.filesystem(0, ZERO, null),
            () -> thresholds.webLog(0, null),
            () -> thresholds.dbPool(0, null, 0, 0),
            () -> thresholds.jvmHeap(0, null, false),
            () -> thresholds.syncP95(0, null, ZERO),
            () -> thresholds.syncP95(0, ZERO, null));
    for (var operation : nullDurations) assertThrows(NullPointerException.class, operation);
    Duration negative = Duration.ofNanos(-1);
    List<Executable> invalidDurations =
        List.of(
            () -> thresholds.filesystem(0, negative, ZERO),
            () -> thresholds.filesystem(0, ZERO, negative),
            () -> thresholds.filesystem(90, ZERO, MINUTE),
            () -> thresholds.webLog(0, negative),
            () -> thresholds.dbPool(0, negative, 0, 0),
            () -> thresholds.jvmHeap(0, negative, false),
            () -> thresholds.syncP95(0, negative, ZERO),
            () -> thresholds.syncP95(0, ZERO, negative),
            () -> thresholds.syncP95(3, ZERO, FIVE));
    for (var operation : invalidDurations)
      assertEquals(
          "invalid alert observation",
          assertThrows(IllegalArgumentException.class, operation).getMessage());
  }

  @Test
  void threshold014ConcurrentStatelessEvaluations()
      throws InterruptedException, ExecutionException {
    var executor = Executors.newFixedThreadPool(4);
    var expected =
        List.of(
            Severity.WARNING,
            Severity.WARNING,
            Severity.WARNING,
            Severity.WARNING,
            Severity.WARNING,
            Severity.WARNING,
            Severity.WARNING,
            Severity.WARNING,
            Severity.WARNING,
            Severity.WARNING,
            Severity.WARNING,
            Severity.CRITICAL);
    try {
      var tasks = new ArrayList<Callable<List<Severity>>>();
      for (int index = 0; index < 64; index++)
        tasks.add(
            () ->
                List.of(
                    thresholds.filesystem(80, FIVE, ZERO),
                    thresholds.transfer(3_500_000_000L, 0),
                    thresholds.asyncQueue(1, 700, 1000),
                    thresholds.webLog(1, FIVE),
                    thresholds.dlq(1, false, false),
                    thresholds.expiry(1000),
                    thresholds.dbPool(80, FIVE, 0, 0),
                    thresholds.jvmHeap(75, TEN, false),
                    thresholds.syncP95(2.1, FIVE, ZERO),
                    thresholds.backup(true, false, 1),
                    thresholds.restarts(1, false),
                    thresholds.integrity(1)));
      for (var future : executor.invokeAll(tasks, 10, TimeUnit.SECONDS))
        assertEquals(expected, future.get());
    } finally {
      executor.shutdownNow();
      assertTrue(executor.awaitTermination(10, TimeUnit.SECONDS));
    }
  }
}
