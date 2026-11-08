package dev.codex.schubert.nk.batch.monitoring;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.CauseClearance;
import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.Condition;
import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.Service;
import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.Severity;
import java.math.BigInteger;
import java.time.Duration;
import java.time.Instant;
import java.util.List;
import java.util.OptionalDouble;
import java.util.concurrent.Callable;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Test;

/** Pure supplied values/reports, independent fixed SS351 boundaries, no real heap/OOM operation. */
class TimedJvmHeapMonitorTest {
  private static final Instant AT = Instant.parse("2026-10-23T00:00:00Z");

  private static ObservationContext context(long seconds, CauseClearance cause) {
    return new ObservationContext(cause, AT.plusSeconds(seconds), Duration.ofSeconds(seconds));
  }

  private static TimedJvmHeapMonitor.Evaluation sample(
      TimedJvmHeapMonitor monitor, double percent, long seconds) {
    return monitor.observe(
        OptionalDouble.of(percent), false, true, context(seconds, CauseClearance.UNCONFIRMED));
  }

  @Test
  void heapTime001WarningNeedsTenMinutesAndFiveNormalMinutesToClose() {
    var monitor = new TimedJvmHeapMonitor(Service.WEB);
    assertTrue(monitor.snapshot().isEmpty());
    assertTrue(sample(monitor, 75, 0).event().isEmpty());
    assertTrue(
        monitor
            .observe(
                OptionalDouble.of(75),
                false,
                true,
                new ObservationContext(
                    CauseClearance.UNCONFIRMED,
                    AT.plusSeconds(599),
                    Duration.ofSeconds(599, 999_999_999)))
            .event()
            .isEmpty());
    var warning = sample(monitor, 75, 600);
    assertTrue(warning.suppliedValuePresent());
    assertEquals(Severity.WARNING, warning.event().orElseThrow().severity());
    assertEquals(Condition.JVM_HEAP, warning.event().orElseThrow().condition());
    assertEquals(AT.plusSeconds(600), warning.event().orElseThrow().firstSeen());
    assertEquals(BigInteger.ONE, warning.event().orElseThrow().count());
    assertTrue(sample(monitor, 0, 601).event().orElseThrow().isOpen());
    assertTrue(sample(monitor, 0, 900).event().orElseThrow().isOpen());
    assertFalse(sample(monitor, 0, 901).event().orElseThrow().isOpen());
    assertTrue(monitor.snapshot().isEmpty());
  }

  @Test
  void heapTime002NinetyIsImmediateAndCriticalNeedsCauseAndTenMinutes() {
    var monitor = new TimedJvmHeapMonitor(Service.API);
    var critical = sample(monitor, 90, 0).event().orElseThrow();
    assertEquals(Severity.CRITICAL, critical.severity());
    assertEquals(Service.API, critical.service());
    assertEquals(AT, critical.firstSeen());
    assertTrue(sample(monitor, 0, 1).event().orElseThrow().isOpen());
    assertTrue(sample(monitor, 0, 601).event().orElseThrow().isOpen());
    var closed =
        monitor.observe(OptionalDouble.of(0), false, true, context(601, CauseClearance.CONFIRMED));
    assertFalse(closed.event().orElseThrow().isOpen());
    assertTrue(monitor.snapshot().isEmpty());
  }

  @Test
  void heapTime003UnknownBreaksBothViolationAndRecoveryWithoutInventingNormal() {
    var monitor = new TimedJvmHeapMonitor(Service.BATCH);
    var absent =
        monitor.observe(OptionalDouble.empty(), false, true, context(0, CauseClearance.CONFIRMED));
    assertFalse(absent.suppliedValuePresent());
    assertTrue(absent.event().isEmpty());
    assertTrue(sample(monitor, 75, 1).event().isEmpty());
    monitor.observe(OptionalDouble.empty(), false, true, context(600, CauseClearance.CONFIRMED));
    assertTrue(sample(monitor, 75, 601).event().isEmpty());
    assertTrue(sample(monitor, 75, 1200).event().isEmpty());
    var warning = sample(monitor, 75, 1201).event().orElseThrow();
    assertEquals(Severity.WARNING, warning.severity());
    assertTrue(sample(monitor, 0, 1202).event().orElseThrow().isOpen());
    var missing =
        monitor.observe(
            OptionalDouble.empty(), false, true, context(1502, CauseClearance.CONFIRMED));
    assertFalse(missing.suppliedValuePresent());
    assertTrue(missing.event().orElseThrow().isOpen());
    assertEquals(warning.count(), missing.event().orElseThrow().count());
    assertEquals(warning.firstSeen(), missing.event().orElseThrow().firstSeen());
    assertTrue(sample(monitor, 0, 1503).event().orElseThrow().isOpen());
    assertTrue(sample(monitor, 0, 1802).event().orElseThrow().isOpen());
    assertFalse(sample(monitor, 0, 1803).event().orElseThrow().isOpen());
  }

  @Test
  void heapTime004ReportedOomIsIndependentOfMissingUsageAndNeverInventsZero() {
    var monitor = new TimedJvmHeapMonitor(Service.WEB);
    var report =
        monitor.observe(OptionalDouble.empty(), true, true, context(0, CauseClearance.UNCONFIRMED));
    assertFalse(report.suppliedValuePresent());
    var event = report.event().orElseThrow();
    assertEquals(Severity.CRITICAL, event.severity());
    assertEquals(BigInteger.ONE, event.count());
    var unknown =
        monitor.observe(
            OptionalDouble.empty(), false, true, context(100, CauseClearance.CONFIRMED));
    assertEquals(event, unknown.event().orElseThrow());
    var nextReport =
        monitor.observe(OptionalDouble.of(0), true, true, context(1000, CauseClearance.CONFIRMED));
    assertTrue(nextReport.suppliedValuePresent());
    assertEquals(Severity.CRITICAL, nextReport.event().orElseThrow().severity());
    assertEquals(BigInteger.TWO, nextReport.event().orElseThrow().count());
  }

  @Test
  void heapTime005NullInvalidAndBackwardsInputsNeverMutateState() {
    assertThrows(NullPointerException.class, () -> new TimedJvmHeapMonitor(null));
    assertThrows(NullPointerException.class, () -> new TimedJvmHeapMonitor.Evaluation(false, null));
    var monitor = new TimedJvmHeapMonitor(Service.WEB);
    var before = sample(monitor, 90, 5).event().orElseThrow();
    assertThrows(
        NullPointerException.class,
        () -> monitor.observe(null, false, true, context(6, CauseClearance.CONFIRMED)));
    assertThrows(
        NullPointerException.class,
        () -> monitor.observe(OptionalDouble.empty(), true, true, null));
    for (boolean oom : List.of(false, true))
      for (double invalid : new double[] {Double.NaN, Double.POSITIVE_INFINITY, -0.1, 100.1})
        assertThrows(
            IllegalArgumentException.class,
            () ->
                monitor.observe(
                    OptionalDouble.of(invalid), oom, true, context(6, CauseClearance.CONFIRMED)));
    assertThrows(IllegalArgumentException.class, () -> sample(monitor, 90, 4));
    assertEquals(before, monitor.snapshot().orElseThrow());
    assertEquals(BigInteger.TWO, sample(monitor, 90, 6).event().orElseThrow().count());
  }

  @Test
  void heapTime006ExplicitGapRestartsViolationAndNormalRecovery() {
    var monitor = new TimedJvmHeapMonitor(Service.API);
    assertTrue(sample(monitor, 75, 0).event().isEmpty());
    assertTrue(
        monitor
            .observe(OptionalDouble.of(75), false, false, context(600, CauseClearance.UNCONFIRMED))
            .event()
            .isEmpty());
    assertEquals(Severity.WARNING, sample(monitor, 75, 1200).event().orElseThrow().severity());
    sample(monitor, 90, 1201);
    assertTrue(sample(monitor, 0, 1202).event().orElseThrow().isOpen());
    assertTrue(
        monitor
            .observe(OptionalDouble.of(0), false, false, context(1802, CauseClearance.CONFIRMED))
            .event()
            .orElseThrow()
            .isOpen());
    assertTrue(
        monitor
            .observe(OptionalDouble.of(0), false, true, context(2401, CauseClearance.CONFIRMED))
            .event()
            .orElseThrow()
            .isOpen());
    assertFalse(
        monitor
            .observe(OptionalDouble.of(0), false, true, context(2402, CauseClearance.CONFIRMED))
            .event()
            .orElseThrow()
            .isOpen());
  }

  @Test
  void heapTime007ConcurrentSameEpochKeepsOneEventAndImmutableSnapshot() throws Exception {
    var monitor = new TimedJvmHeapMonitor(Service.BATCH);
    var first = sample(monitor, 90, 0).event().orElseThrow();
    var pool = Executors.newFixedThreadPool(8);
    try {
      var jobs =
          java.util.stream.IntStream.range(0, 64)
              .<Callable<Severity>>mapToObj(
                  i -> () -> sample(monitor, 90, 1).event().orElseThrow().severity())
              .toList();
      for (var result : pool.invokeAll(jobs, 10, TimeUnit.SECONDS))
        assertEquals(Severity.CRITICAL, result.get());
    } finally {
      pool.shutdownNow();
      assertTrue(pool.awaitTermination(10, TimeUnit.SECONDS));
    }
    assertEquals(BigInteger.ONE, first.count());
    assertEquals(AT, first.lastSeen());
    var current = monitor.snapshot().orElseThrow();
    assertEquals(BigInteger.valueOf(65), current.count());
    assertEquals(first.firstSeen(), current.firstSeen());
    assertEquals(AT.plusSeconds(1), current.lastSeen());
  }

  @Test
  void heapTime008CriticalIsStickyAcrossWarningAndReportedOomResetsRecovery() {
    var monitor = new TimedJvmHeapMonitor(Service.WEB);
    sample(monitor, 75, 0);
    var warning = sample(monitor, 75, 600).event().orElseThrow();
    assertEquals(Severity.WARNING, warning.severity());
    var critical = sample(monitor, 90, 601).event().orElseThrow();
    assertEquals(Severity.CRITICAL, critical.severity());
    assertEquals(warning.firstSeen(), critical.firstSeen());
    assertEquals(BigInteger.TWO, critical.count());
    assertEquals(Severity.CRITICAL, sample(monitor, 80, 602).event().orElseThrow().severity());
    sample(monitor, 0, 603);
    assertTrue(
        monitor
            .observe(OptionalDouble.of(0), true, true, context(1203, CauseClearance.CONFIRMED))
            .event()
            .orElseThrow()
            .isOpen());
    assertEquals(Severity.WARNING, warning.severity());
    assertEquals(BigInteger.ONE, warning.count());
  }
}
