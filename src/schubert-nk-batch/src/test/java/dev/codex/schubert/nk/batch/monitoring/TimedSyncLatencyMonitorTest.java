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
import java.util.OptionalDouble;
import java.util.concurrent.Callable;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Test;

/**
 * SS351 literal strict boundaries and independent elapsed time, no actual percentile calculation.
 */
class TimedSyncLatencyMonitorTest {
  private static final Instant OBSERVED_AT = Instant.parse("2026-10-23T00:00:00Z");

  private static ObservationContext at(long seconds, CauseClearance cause) {
    return new ObservationContext(
        cause, OBSERVED_AT.plusSeconds(seconds), Duration.ofSeconds(seconds));
  }

  private static TimedSyncLatencyMonitor.Evaluation sample(
      TimedSyncLatencyMonitor monitor, double seconds, long elapsed) {
    return monitor.observe(OptionalDouble.of(seconds), true, at(elapsed, CauseClearance.CONFIRMED));
  }

  @Test
  void syncTime001StrictTwoSecondWarningNeedsFiveMinutes() {
    var monitor = new TimedSyncLatencyMonitor(Service.API);
    assertTrue(monitor.snapshot().isEmpty());
    assertTrue(sample(monitor, 2.0, 0).event().isEmpty());
    assertTrue(sample(monitor, 2.0, 300).event().isEmpty());
    assertTrue(sample(monitor, 2.0001, 301).event().isEmpty());
    assertTrue(
        monitor
            .observe(
                OptionalDouble.of(2.0001),
                true,
                new ObservationContext(
                    CauseClearance.CONFIRMED,
                    OBSERVED_AT.plusSeconds(600),
                    Duration.ofSeconds(600, 999_999_999)))
            .event()
            .isEmpty());
    var warning = sample(monitor, 2.0001, 601).event().orElseThrow();
    assertEquals(Severity.WARNING, warning.severity());
    assertEquals(Condition.SYNC_P95, warning.condition());
    assertEquals(OBSERVED_AT.plusSeconds(601), warning.firstSeen());
    assertEquals(BigInteger.ONE, warning.count());
  }

  @Test
  void syncTime002StrictTwoPointFiveNeedsFiveMinutesBeforeCriticalPromotion() {
    var monitor = new TimedSyncLatencyMonitor(Service.API);
    assertTrue(sample(monitor, 2.5, 0).event().isEmpty());
    var warning = sample(monitor, 2.5, 300).event().orElseThrow();
    assertEquals(Severity.WARNING, warning.severity());
    assertEquals(Severity.WARNING, sample(monitor, 2.5001, 301).event().orElseThrow().severity());
    assertEquals(
        Severity.WARNING,
        monitor
            .observe(
                OptionalDouble.of(2.5001),
                true,
                new ObservationContext(
                    CauseClearance.CONFIRMED,
                    OBSERVED_AT.plusSeconds(600),
                    Duration.ofSeconds(600, 999_999_999)))
            .event()
            .orElseThrow()
            .severity());
    var critical = sample(monitor, 2.5001, 601).event().orElseThrow();
    assertEquals(Severity.CRITICAL, critical.severity());
    assertEquals(warning.firstSeen(), critical.firstSeen());
    assertEquals(BigInteger.valueOf(4), critical.count());
    assertEquals(BigInteger.ONE, warning.count());
  }

  @Test
  void syncTime003UnknownCutsBothViolationWindowsRatherThanBecomingZero() {
    var monitor = new TimedSyncLatencyMonitor(Service.WEB);
    var unknown = monitor.observe(OptionalDouble.empty(), true, at(0, CauseClearance.CONFIRMED));
    assertFalse(unknown.suppliedValuePresent());
    assertTrue(unknown.event().isEmpty());
    assertTrue(sample(monitor, 3.0, 1).event().isEmpty());
    assertTrue(sample(monitor, 3.0, 300).event().isEmpty());
    monitor.observe(OptionalDouble.empty(), true, at(301, CauseClearance.CONFIRMED));
    assertTrue(sample(monitor, 3.0, 302).event().isEmpty());
    assertTrue(sample(monitor, 3.0, 601).event().isEmpty());
    var result = sample(monitor, 3.0, 602);
    assertTrue(result.suppliedValuePresent());
    assertEquals(Severity.CRITICAL, result.event().orElseThrow().severity());
  }

  @Test
  void syncTime004UnknownCutsCriticalRecoveryAndCauseMustBeConfirmed() {
    var monitor = new TimedSyncLatencyMonitor(Service.BATCH);
    sample(monitor, 3.0, 0);
    var critical = sample(monitor, 3.0, 300).event().orElseThrow();
    sample(monitor, 0, 301);
    var unknown = monitor.observe(OptionalDouble.empty(), true, at(901, CauseClearance.CONFIRMED));
    assertEquals(critical.count(), unknown.event().orElseThrow().count());
    assertTrue(unknown.event().orElseThrow().isOpen());
    assertTrue(sample(monitor, 0, 902).event().orElseThrow().isOpen());
    assertTrue(sample(monitor, 0, 1501).event().orElseThrow().isOpen());
    assertTrue(
        monitor
            .observe(OptionalDouble.of(0), true, at(1502, CauseClearance.UNCONFIRMED))
            .event()
            .orElseThrow()
            .isOpen());
    assertFalse(sample(monitor, 0, 1502).event().orElseThrow().isOpen());
    assertTrue(monitor.snapshot().isEmpty());
  }

  @Test
  void syncTime005NullInvalidAndBackwardsInputsCannotMutateExistingState() {
    assertThrows(NullPointerException.class, () -> new TimedSyncLatencyMonitor(null));
    assertThrows(
        NullPointerException.class, () -> new TimedSyncLatencyMonitor.Evaluation(false, null));
    var monitor = new TimedSyncLatencyMonitor(Service.API);
    sample(monitor, 3.0, 0);
    var before = sample(monitor, 3.0, 300).event().orElseThrow();
    assertThrows(
        NullPointerException.class,
        () -> monitor.observe(null, true, at(301, CauseClearance.CONFIRMED)));
    assertThrows(
        NullPointerException.class, () -> monitor.observe(OptionalDouble.empty(), true, null));
    for (double invalid :
        new double[] {Double.NaN, Double.NEGATIVE_INFINITY, Double.POSITIVE_INFINITY, -0.1})
      assertThrows(IllegalArgumentException.class, () -> sample(monitor, invalid, 301));
    assertThrows(IllegalArgumentException.class, () -> sample(monitor, 3.0, 299));
    assertEquals(before, monitor.snapshot().orElseThrow());
    assertEquals(BigInteger.TWO, sample(monitor, 3.0, 301).event().orElseThrow().count());
  }

  @Test
  void syncTime006ExplicitGapRestartsViolationAndRecoveryWithStickyCritical() {
    var monitor = new TimedSyncLatencyMonitor(Service.WEB);
    sample(monitor, 3.0, 0);
    assertTrue(
        monitor
            .observe(OptionalDouble.of(3.0), false, at(300, CauseClearance.CONFIRMED))
            .event()
            .isEmpty());
    assertEquals(Severity.CRITICAL, sample(monitor, 3.0, 600).event().orElseThrow().severity());
    assertEquals(Severity.CRITICAL, sample(monitor, 2.1, 601).event().orElseThrow().severity());
    sample(monitor, 0, 602);
    assertTrue(
        monitor
            .observe(OptionalDouble.of(0), false, at(1202, CauseClearance.CONFIRMED))
            .event()
            .orElseThrow()
            .isOpen());
    assertTrue(sample(monitor, 0, 1801).event().orElseThrow().isOpen());
    assertFalse(sample(monitor, 0, 1802).event().orElseThrow().isOpen());
  }

  @Test
  void syncTime007ConcurrentSameEpochMaintainsExactImmutableEventCounts() throws Exception {
    var monitor = new TimedSyncLatencyMonitor(Service.API);
    sample(monitor, 3.0, 0);
    var first = sample(monitor, 3.0, 300).event().orElseThrow();
    var pool = Executors.newFixedThreadPool(8);
    try {
      var jobs =
          java.util.stream.IntStream.range(0, 64)
              .<Callable<Severity>>mapToObj(
                  i -> () -> sample(monitor, 3.0, 301).event().orElseThrow().severity())
              .toList();
      for (var result : pool.invokeAll(jobs, 10, TimeUnit.SECONDS))
        assertEquals(Severity.CRITICAL, result.get());
    } finally {
      pool.shutdownNow();
      assertTrue(pool.awaitTermination(10, TimeUnit.SECONDS));
    }
    assertEquals(BigInteger.ONE, first.count());
    assertEquals(OBSERVED_AT.plusSeconds(300), first.lastSeen());
    assertEquals(BigInteger.valueOf(65), monitor.snapshot().orElseThrow().count());
  }

  @Test
  void syncTime008FiniteMaximumAndWarningRecoveryDoNotMixSeparateOwners() {
    var web = new TimedSyncLatencyMonitor(Service.WEB);
    var api = new TimedSyncLatencyMonitor(Service.API);
    assertTrue(sample(web, 0, 0).event().isEmpty());
    assertTrue(sample(web, Double.MAX_VALUE, 1).event().isEmpty());
    assertTrue(sample(web, Double.MAX_VALUE, 300).event().isEmpty());
    assertEquals(
        Severity.CRITICAL, sample(web, Double.MAX_VALUE, 301).event().orElseThrow().severity());
    sample(api, 2.5, 0);
    assertEquals(Severity.WARNING, sample(api, 2.5, 300).event().orElseThrow().severity());
    sample(api, 2.0, 301);
    assertTrue(sample(api, 0, 600).event().orElseThrow().isOpen());
    assertFalse(sample(api, 0, 601).event().orElseThrow().isOpen());
    assertEquals(Service.WEB, web.snapshot().orElseThrow().service());
    assertTrue(api.snapshot().isEmpty());
  }
}
