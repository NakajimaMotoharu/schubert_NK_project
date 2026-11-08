package dev.codex.schubert.nk.batch.monitoring;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.CauseClearance;
import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.Service;
import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.Severity;
import java.lang.management.MemoryUsage;
import java.math.BigInteger;
import java.time.Duration;
import java.time.Instant;
import java.util.List;
import java.util.Optional;
import java.util.concurrent.Callable;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicLong;
import org.junit.jupiter.api.Test;

/**
 * Owned synthetic providers only: independent SS351 times, values, calls and failure identities.
 */
class JvmHeapHealthMonitorTest {
  private static final Instant AT = Instant.parse("2026-10-23T00:00:00Z");

  private static ObservationContext context(long seconds) {
    return new ObservationContext(
        CauseClearance.CONFIRMED, AT.plusSeconds(seconds), Duration.ofSeconds(seconds));
  }

  private static void usage(JvmHeapHealthObservationTest.Fixture fixture, long used) {
    fixture.usage = Optional.of(new MemoryUsage(-1, used, 1000, 1000));
  }

  @Test
  void heapConn001BeanClockAndKernelNeedExactlyTenWarningMinutes() {
    var fixture = new JvmHeapHealthObservationTest.Fixture();
    var wall = new MonitoringObservationClockTest.FixtureClock();
    var ticks = new AtomicLong();
    var clock = new MonitoringObservationClock(wall, ticks::get);
    var monitor = new JvmHeapHealthMonitor(fixture.bean, Service.WEB);
    assertTrue(monitor.snapshot().isEmpty());
    assertTrue(
        monitor.observeNow(true, false, CauseClearance.UNCONFIRMED, clock).event().isEmpty());
    ticks.set(599_999_999_999L);
    assertTrue(
        monitor.observeNow(true, false, CauseClearance.UNCONFIRMED, clock).event().isEmpty());
    ticks.set(600_000_000_000L);
    wall.at = Optional.of(AT.plusSeconds(600));
    var result = monitor.observeNow(true, false, CauseClearance.UNCONFIRMED, clock);
    assertTrue(result.suppliedValuePresent());
    assertEquals(Severity.WARNING, result.event().orElseThrow().severity());
    assertEquals(AT.plusSeconds(600), result.event().orElseThrow().firstSeen());
    assertEquals(3, fixture.reads.get());
    assertEquals(3, wall.reads.get());
  }

  @Test
  void heapConn002UnknownMaximumBreaksCriticalNormalRecovery() {
    var fixture = new JvmHeapHealthObservationTest.Fixture();
    usage(fixture, 900);
    var monitor = new JvmHeapHealthMonitor(fixture.bean, Service.API);
    assertEquals(
        Severity.CRITICAL,
        monitor.observe(true, false, context(0)).event().orElseThrow().severity());
    usage(fixture, 0);
    assertTrue(monitor.observe(true, false, context(1)).event().orElseThrow().isOpen());
    fixture.usage = Optional.of(new MemoryUsage(-1, 100, 1000, -1));
    var unknown = monitor.observe(true, false, context(601));
    assertFalse(unknown.suppliedValuePresent());
    assertTrue(unknown.event().orElseThrow().isOpen());
    usage(fixture, 0);
    assertTrue(monitor.observe(true, false, context(602)).event().orElseThrow().isOpen());
    assertTrue(monitor.observe(true, false, context(1201)).event().orElseThrow().isOpen());
    assertFalse(monitor.observe(true, false, context(1202)).event().orElseThrow().isOpen());
    assertTrue(monitor.snapshot().isEmpty());
    assertEquals(6, fixture.reads.get());
  }

  @Test
  void heapConn003GetterFailureIsNotRetriedOrConvertedAndBreaksRecovery() {
    for (Throwable failure :
        List.of(
            new IllegalStateException(),
            new NullPointerException(),
            new AssertionError(),
            new OutOfMemoryError("synthetic-test-only-no-allocation"))) {
      var fixture = new JvmHeapHealthObservationTest.Fixture();
      usage(fixture, 900);
      var monitor = new JvmHeapHealthMonitor(fixture.bean, Service.BATCH);
      monitor.observe(true, false, context(0));
      usage(fixture, 0);
      monitor.observe(true, false, context(1));
      fixture.failure = Optional.of(failure);
      assertSame(
          failure,
          assertThrows(failure.getClass(), () -> monitor.observe(true, false, context(601))));
      assertEquals(3, fixture.reads.get());
      fixture.failure = Optional.empty();
      assertTrue(monitor.observe(true, false, context(602)).event().orElseThrow().isOpen());
      assertTrue(monitor.observe(true, false, context(1201)).event().orElseThrow().isOpen());
      assertFalse(monitor.observe(true, false, context(1202)).event().orElseThrow().isOpen());
      assertEquals(6, fixture.reads.get());
    }
  }

  @Test
  void heapConn004ClockFailureOrNullNeverReadsBeanAndCrossApiRecoveryHasGap() {
    for (boolean nullInstant : List.of(false, true)) {
      var fixture = new JvmHeapHealthObservationTest.Fixture();
      usage(fixture, 900);
      var wall = new MonitoringObservationClockTest.FixtureClock();
      var ticks = new AtomicLong();
      var clock = new MonitoringObservationClock(wall, ticks::get);
      var monitor = new JvmHeapHealthMonitor(fixture.bean, Service.WEB);
      monitor.observeNow(true, false, CauseClearance.CONFIRMED, clock);
      usage(fixture, 0);
      monitor.observe(true, false, context(1));
      var failure = new AssertionError();
      if (nullInstant) wall.at = Optional.empty();
      else wall.failure = Optional.of(failure);
      ticks.set(601_000_000_000L);
      if (nullInstant)
        assertThrows(
            NullPointerException.class,
            () -> monitor.observeNow(true, false, CauseClearance.CONFIRMED, clock));
      else
        assertSame(
            failure,
            assertThrows(
                AssertionError.class,
                () -> monitor.observeNow(true, false, CauseClearance.CONFIRMED, clock)));
      assertEquals(2, fixture.reads.get());
      wall.at = Optional.of(AT);
      wall.failure = Optional.empty();
      assertTrue(monitor.observe(true, false, context(602)).event().orElseThrow().isOpen());
      ticks.set(1201_000_000_000L);
      assertTrue(
          monitor
              .observeNow(true, false, CauseClearance.CONFIRMED, clock)
              .event()
              .orElseThrow()
              .isOpen());
      ticks.set(1202_000_000_000L);
      assertFalse(
          monitor
              .observeNow(true, false, CauseClearance.CONFIRMED, clock)
              .event()
              .orElseThrow()
              .isOpen());
    }
  }

  @Test
  void heapConn005ExplicitOomReportWithUnknownUsageIsCriticalNotInventedZero() {
    var fixture = new JvmHeapHealthObservationTest.Fixture();
    fixture.usage = Optional.of(new MemoryUsage(-1, 100, 1000, -1));
    var monitor = new JvmHeapHealthMonitor(fixture.bean, Service.API);
    var result = monitor.observe(true, true, context(0));
    assertFalse(result.suppliedValuePresent());
    assertEquals(Severity.CRITICAL, result.event().orElseThrow().severity());
    assertEquals(BigInteger.ONE, result.event().orElseThrow().count());
    assertEquals(1, fixture.reads.get());
    var wall = new MonitoringObservationClockTest.FixtureClock();
    var clock = new MonitoringObservationClock(wall, () -> 0);
    assertEquals(
        BigInteger.TWO,
        monitor
            .observeNow(true, true, CauseClearance.CONFIRMED, clock)
            .event()
            .orElseThrow()
            .count());
  }

  @Test
  void heapConn006NullAndBackwardsBoundariesHaveNoProviderOrStateMutation() {
    var fixture = new JvmHeapHealthObservationTest.Fixture();
    assertThrows(NullPointerException.class, () -> new JvmHeapHealthMonitor(null, Service.WEB));
    assertThrows(NullPointerException.class, () -> new JvmHeapHealthMonitor(fixture.bean, null));
    var monitor = new JvmHeapHealthMonitor(fixture.bean, Service.WEB);
    var wall = new MonitoringObservationClockTest.FixtureClock();
    var clock = new MonitoringObservationClock(wall, () -> 0);
    assertThrows(NullPointerException.class, () -> monitor.observe(true, false, null));
    assertThrows(NullPointerException.class, () -> monitor.observeNow(true, false, null, clock));
    assertThrows(
        NullPointerException.class,
        () -> monitor.observeNow(true, false, CauseClearance.CONFIRMED, null));
    assertEquals(0, fixture.reads.get());
    assertEquals(0, wall.reads.get());
    usage(fixture, 900);
    var before = monitor.observe(true, false, context(5)).event().orElseThrow();
    assertThrows(IllegalArgumentException.class, () -> monitor.observe(true, false, context(4)));
    assertEquals(before, monitor.snapshot().orElseThrow());
    assertEquals(1, fixture.reads.get());
    assertEquals(
        BigInteger.TWO, monitor.observe(true, false, context(6)).event().orElseThrow().count());
  }

  @Test
  void heapConn007SeparateOwnersDoNotShareBeansOrAlertState() {
    var web = new JvmHeapHealthObservationTest.Fixture();
    usage(web, 900);
    var api = new JvmHeapHealthObservationTest.Fixture();
    usage(api, 0);
    var webMonitor = new JvmHeapHealthMonitor(web.bean, Service.WEB);
    var apiMonitor = new JvmHeapHealthMonitor(api.bean, Service.API);
    assertEquals(
        Service.WEB, webMonitor.observe(true, false, context(0)).event().orElseThrow().service());
    assertTrue(apiMonitor.observe(true, false, context(0)).event().isEmpty());
    assertTrue(apiMonitor.snapshot().isEmpty());
    assertEquals(1, web.reads.get());
    assertEquals(1, api.reads.get());
  }

  @Test
  void heapConn008ConcurrentInputsHaveExactReadsAndImmutableCountSnapshots() throws Exception {
    var fixture = new JvmHeapHealthObservationTest.Fixture();
    usage(fixture, 900);
    var monitor = new JvmHeapHealthMonitor(fixture.bean, Service.BATCH);
    var first = monitor.observe(true, false, context(0)).event().orElseThrow();
    var pool = Executors.newFixedThreadPool(8);
    try {
      var jobs =
          java.util.stream.IntStream.range(0, 64)
              .<Callable<Severity>>mapToObj(
                  i ->
                      () ->
                          monitor.observe(true, false, context(1)).event().orElseThrow().severity())
              .toList();
      for (var result : pool.invokeAll(jobs, 10, TimeUnit.SECONDS))
        assertEquals(Severity.CRITICAL, result.get());
    } finally {
      pool.shutdownNow();
      assertTrue(pool.awaitTermination(10, TimeUnit.SECONDS));
    }
    assertEquals(65, fixture.reads.get());
    assertEquals(BigInteger.ONE, first.count());
    assertEquals(BigInteger.valueOf(65), monitor.snapshot().orElseThrow().count());
  }
}
