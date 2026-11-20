package dev.codex.schubert.nk.batch.monitoring;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.CauseClearance;
import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.Event;
import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.Service;
import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.Severity;
import java.math.BigInteger;
import java.time.Duration;
import java.time.Instant;
import java.util.OptionalDouble;
import org.junit.jupiter.api.Test;

/** SS351 §7 and YKT-2738, PT-TIMED-RECOVERY-009/010. */
final class TimedAlertCriticalRecoveryTest {
  private static final Instant EPOCH = Instant.parse("2026-10-23T00:00:00Z");

  @Test
  void syncLatencyRequiresFreshNormalTimeAfterPendingWarningOnOpenCritical() {
    var monitor = new TimedSyncLatencyMonitor(Service.API);
    assertTrue(
        monitor
            .observe(OptionalDouble.of(3.0), true, at(0, CauseClearance.CONFIRMED))
            .event()
            .isEmpty());
    var open = sync(monitor, 3.0, true, 300, CauseClearance.CONFIRMED);
    assertEquals(Severity.CRITICAL, open.severity());
    assertSame(open, sync(monitor, 2.0, true, 301, CauseClearance.CONFIRMED));

    assertSame(open, sync(monitor, 2.2, false, 600, CauseClearance.CONFIRMED));
    assertSame(open, sync(monitor, 2.2, true, 899, CauseClearance.CONFIRMED));
    assertSame(open, sync(monitor, 2.0, true, 900, CauseClearance.CONFIRMED));
    assertSame(open, sync(monitor, 2.0, true, 1200, CauseClearance.CONFIRMED));
    assertSame(open, sync(monitor, 2.0, true, 1499, CauseClearance.CONFIRMED));
    assertSame(open, sync(monitor, 2.0, true, 1500, CauseClearance.UNCONFIRMED));
    var closed = sync(monitor, 2.0, true, 1501, CauseClearance.CONFIRMED);
    assertClosedCritical(closed, 300);
    assertTrue(monitor.snapshot().isEmpty());
  }

  @Test
  void policyPoolRequiresFreshNormalTimeAfterPendingUsageOnOpenCritical() {
    var engine = new MonitoringPolicyEngine();
    var open = pool(engine, 79, 1, 0, CauseClearance.CONFIRMED);
    assertTrue(open.isOpen());
    assertEquals(Severity.CRITICAL, open.severity());

    assertSame(open, pool(engine, 80, 0, 10, CauseClearance.CONFIRMED));
    assertSame(open, pool(engine, 79, 0, 310, CauseClearance.CONFIRMED));
    assertSame(open, pool(engine, 79, 0, 610, CauseClearance.CONFIRMED));
    assertSame(open, pool(engine, 79, 0, 909, CauseClearance.CONFIRMED));
    assertSame(open, pool(engine, 79, 0, 910, CauseClearance.UNCONFIRMED));
    assertClosedCritical(pool(engine, 79, 0, 911, CauseClearance.CONFIRMED), 0);
    assertTrue(engine.activeAlerts().isEmpty());
  }

  private static Event sync(
      TimedSyncLatencyMonitor monitor,
      double value,
      boolean consecutive,
      long elapsed,
      CauseClearance clearance) {
    return monitor
        .observe(OptionalDouble.of(value), consecutive, at(elapsed, clearance))
        .event()
        .orElseThrow();
  }

  private static Event pool(
      MonitoringPolicyEngine engine,
      double usage,
      long pending,
      long elapsed,
      CauseClearance clearance) {
    return engine
        .dbPool(Service.API, usage, Duration.ZERO, pending, 0, at(elapsed, clearance))
        .orElseThrow();
  }

  private static ObservationContext at(long elapsed, CauseClearance clearance) {
    return new ObservationContext(
        clearance, EPOCH.plusSeconds(elapsed), Duration.ofSeconds(elapsed));
  }

  private static void assertClosedCritical(Event closed, long openedAt) {
    assertFalse(closed.isOpen());
    assertEquals(Severity.CRITICAL, closed.severity());
    assertEquals(BigInteger.ONE, closed.count());
    assertEquals(EPOCH.plusSeconds(openedAt), closed.firstSeen());
    assertEquals(closed.firstSeen(), closed.lastSeen());
  }
}
