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

/**
 * Supplied count/percent/context vectors, not a real pool, counter source or database operation.
 */
class TimedDbPoolMonitorTest {
  private static final Instant OBSERVED_AT = Instant.parse("2026-10-23T00:00:00Z");

  private static ObservationContext at(long seconds, CauseClearance cause) {
    return new ObservationContext(
        cause, OBSERVED_AT.plusSeconds(seconds), Duration.ofSeconds(seconds));
  }

  private static TimedDbPoolMonitor.Evaluation sample(
      TimedDbPoolMonitor monitor, double percent, long seconds) {
    return monitor.observe(
        OptionalDouble.of(percent), 0, 0, true, at(seconds, CauseClearance.CONFIRMED));
  }

  @Test
  void dbTime001EightyNeedsFiveMinutesAndWarningNeedsFiveNormalMinutes() {
    var monitor = new TimedDbPoolMonitor(Service.WEB);
    assertTrue(monitor.snapshot().isEmpty());
    assertTrue(sample(monitor, 80, 0).event().isEmpty());
    assertTrue(
        monitor
            .observe(
                OptionalDouble.of(80),
                0,
                0,
                true,
                new ObservationContext(
                    CauseClearance.UNCONFIRMED,
                    OBSERVED_AT.plusSeconds(299),
                    Duration.ofSeconds(299, 999_999_999)))
            .event()
            .isEmpty());
    var warning = sample(monitor, 80, 300).event().orElseThrow();
    assertEquals(Severity.WARNING, warning.severity());
    assertEquals(Condition.DB_POOL, warning.condition());
    assertEquals(OBSERVED_AT.plusSeconds(300), warning.firstSeen());
    assertEquals(BigInteger.ONE, warning.count());
    assertTrue(sample(monitor, 0, 301).event().orElseThrow().isOpen());
    assertTrue(sample(monitor, 0, 600).event().orElseThrow().isOpen());
    assertFalse(sample(monitor, 0, 601).event().orElseThrow().isOpen());
    assertTrue(monitor.snapshot().isEmpty());
  }

  @Test
  void dbTime002PendingOrTimeoutIsImmediateAndNeedsCauseAndTenNormalMinutes() {
    for (long[] counts : List.of(new long[] {1, 0}, new long[] {0, 1})) {
      var monitor = new TimedDbPoolMonitor(Service.API);
      var critical =
          monitor
              .observe(
                  OptionalDouble.of(0),
                  counts[0],
                  counts[1],
                  true,
                  at(0, CauseClearance.UNCONFIRMED))
              .event()
              .orElseThrow();
      assertEquals(Severity.CRITICAL, critical.severity());
      assertEquals(Service.API, critical.service());
      assertEquals(OBSERVED_AT, critical.firstSeen());
      monitor.observe(OptionalDouble.of(0), 0, 0, true, at(1, CauseClearance.UNCONFIRMED));
      assertTrue(
          monitor
              .observe(OptionalDouble.of(0), 0, 0, true, at(600, CauseClearance.CONFIRMED))
              .event()
              .orElseThrow()
              .isOpen());
      assertTrue(
          monitor
              .observe(OptionalDouble.of(0), 0, 0, true, at(601, CauseClearance.UNCONFIRMED))
              .event()
              .orElseThrow()
              .isOpen());
      assertFalse(sample(monitor, 0, 601).event().orElseThrow().isOpen());
    }
  }

  @Test
  void dbTime003UnknownCutsViolationAndNormalRecoveryWithoutInventingZero() {
    var monitor = new TimedDbPoolMonitor(Service.BATCH);
    assertTrue(
        monitor
            .observe(OptionalDouble.empty(), 0, 0, true, at(0, CauseClearance.CONFIRMED))
            .event()
            .isEmpty());
    assertTrue(sample(monitor, 80, 1).event().isEmpty());
    assertTrue(sample(monitor, 80, 300).event().isEmpty());
    assertFalse(
        monitor
            .observe(OptionalDouble.empty(), 0, 0, true, at(301, CauseClearance.CONFIRMED))
            .suppliedValuePresent());
    assertTrue(sample(monitor, 80, 302).event().isEmpty());
    assertTrue(sample(monitor, 80, 601).event().isEmpty());
    var warning = sample(monitor, 80, 602).event().orElseThrow();
    assertEquals(Severity.WARNING, warning.severity());
    sample(monitor, 0, 603);
    var unknown =
        monitor.observe(OptionalDouble.empty(), 0, 0, true, at(903, CauseClearance.CONFIRMED));
    assertEquals(warning.count(), unknown.event().orElseThrow().count());
    assertTrue(unknown.event().orElseThrow().isOpen());
    assertTrue(sample(monitor, 0, 904).event().orElseThrow().isOpen());
    assertTrue(sample(monitor, 0, 1203).event().orElseThrow().isOpen());
    assertFalse(sample(monitor, 0, 1204).event().orElseThrow().isOpen());
  }

  @Test
  void dbTime004KnownCountsAreIndependentOfUnknownPercent() {
    for (long[] counts : List.of(new long[] {1, 0}, new long[] {0, 1})) {
      var monitor = new TimedDbPoolMonitor(Service.WEB);
      var result =
          monitor.observe(
              OptionalDouble.empty(), counts[0], counts[1], true, at(0, CauseClearance.CONFIRMED));
      assertFalse(result.suppliedValuePresent());
      assertEquals(Severity.CRITICAL, result.event().orElseThrow().severity());
      var unknown =
          monitor.observe(OptionalDouble.empty(), 0, 0, true, at(600, CauseClearance.CONFIRMED));
      assertEquals(result.event(), unknown.event());
      assertTrue(unknown.event().orElseThrow().isOpen());
    }
  }

  @Test
  void dbTime005InvalidNullAndBackwardsInputsCannotMutateState() {
    assertThrows(NullPointerException.class, () -> new TimedDbPoolMonitor(null));
    assertThrows(NullPointerException.class, () -> new TimedDbPoolMonitor.Evaluation(false, null));
    var monitor = new TimedDbPoolMonitor(Service.API);
    var before =
        monitor
            .observe(OptionalDouble.of(0), 1, 0, true, at(5, CauseClearance.CONFIRMED))
            .event()
            .orElseThrow();
    assertThrows(
        NullPointerException.class,
        () -> monitor.observe(null, 0, 0, true, at(6, CauseClearance.CONFIRMED)));
    assertThrows(
        NullPointerException.class,
        () -> monitor.observe(OptionalDouble.empty(), 0, 0, true, null));
    for (double percent : new double[] {Double.NaN, Double.POSITIVE_INFINITY, -0.1, 100.1})
      assertThrows(
          IllegalArgumentException.class,
          () ->
              monitor.observe(
                  OptionalDouble.of(percent), 1, 1, true, at(6, CauseClearance.CONFIRMED)));
    for (long[] counts : List.of(new long[] {-1, 0}, new long[] {0, -1}))
      assertThrows(
          IllegalArgumentException.class,
          () ->
              monitor.observe(
                  OptionalDouble.empty(),
                  counts[0],
                  counts[1],
                  true,
                  at(6, CauseClearance.CONFIRMED)));
    assertThrows(IllegalArgumentException.class, () -> sample(monitor, 80, 4));
    assertEquals(before, monitor.snapshot().orElseThrow());
    assertEquals(
        BigInteger.TWO,
        monitor
            .observe(OptionalDouble.of(0), 1, 0, true, at(6, CauseClearance.CONFIRMED))
            .event()
            .orElseThrow()
            .count());
  }

  @Test
  void dbTime006ExplicitGapRestartsWindowAndCriticalRemainsSticky() {
    var monitor = new TimedDbPoolMonitor(Service.WEB);
    sample(monitor, 80, 0);
    assertTrue(
        monitor
            .observe(OptionalDouble.of(80), 0, 0, false, at(300, CauseClearance.CONFIRMED))
            .event()
            .isEmpty());
    assertEquals(Severity.WARNING, sample(monitor, 80, 600).event().orElseThrow().severity());
    assertEquals(
        Severity.CRITICAL,
        monitor
            .observe(OptionalDouble.of(80), 1, 0, true, at(601, CauseClearance.CONFIRMED))
            .event()
            .orElseThrow()
            .severity());
    assertEquals(Severity.CRITICAL, sample(monitor, 80, 602).event().orElseThrow().severity());
    sample(monitor, 0, 603);
    assertTrue(
        monitor
            .observe(OptionalDouble.of(0), 0, 0, false, at(1203, CauseClearance.CONFIRMED))
            .event()
            .orElseThrow()
            .isOpen());
    assertTrue(sample(monitor, 0, 1802).event().orElseThrow().isOpen());
    assertFalse(sample(monitor, 0, 1803).event().orElseThrow().isOpen());
  }

  @Test
  void dbTime007ConcurrentSameEpochKeepsImmutableExactEventCount() throws Exception {
    var monitor = new TimedDbPoolMonitor(Service.BATCH);
    var first =
        monitor
            .observe(OptionalDouble.of(0), 1, 0, true, at(0, CauseClearance.CONFIRMED))
            .event()
            .orElseThrow();
    var pool = Executors.newFixedThreadPool(8);
    try {
      var jobs =
          java.util.stream.IntStream.range(0, 64)
              .<Callable<Severity>>mapToObj(
                  i ->
                      () ->
                          monitor
                              .observe(
                                  OptionalDouble.of(0), 1, 0, true, at(1, CauseClearance.CONFIRMED))
                              .event()
                              .orElseThrow()
                              .severity())
              .toList();
      for (var result : pool.invokeAll(jobs, 10, TimeUnit.SECONDS))
        assertEquals(Severity.CRITICAL, result.get());
    } finally {
      pool.shutdownNow();
      assertTrue(pool.awaitTermination(10, TimeUnit.SECONDS));
    }
    assertEquals(BigInteger.ONE, first.count());
    assertEquals(OBSERVED_AT, first.lastSeen());
    assertEquals(BigInteger.valueOf(65), monitor.snapshot().orElseThrow().count());
  }

  @Test
  void dbTime008BoundariesMaximumCountsAndOwnersStayIndependent() {
    var web = new TimedDbPoolMonitor(Service.WEB);
    var api = new TimedDbPoolMonitor(Service.API);
    assertTrue(sample(web, 79.999, 0).event().isEmpty());
    assertTrue(sample(web, 79.999, 300).event().isEmpty());
    assertTrue(sample(web, 80, 301).event().isEmpty());
    assertEquals(Severity.WARNING, sample(web, 100, 601).event().orElseThrow().severity());
    assertTrue(api.snapshot().isEmpty());
    var maximum =
        api.observe(
                OptionalDouble.empty(),
                Long.MAX_VALUE,
                Long.MAX_VALUE,
                true,
                at(0, CauseClearance.CONFIRMED))
            .event()
            .orElseThrow();
    assertEquals(Severity.CRITICAL, maximum.severity());
    assertEquals(Service.API, maximum.service());
    assertEquals(BigInteger.ONE, maximum.count());
    assertEquals(Service.WEB, web.snapshot().orElseThrow().service());
  }
}
