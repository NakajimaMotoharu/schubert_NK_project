package dev.codex.schubert.nk.batch.monitoring;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.CauseClearance;
import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.Condition;
import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.Event;
import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.Service;
import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.Severity;
import java.math.BigInteger;
import java.time.Duration;
import java.time.Instant;
import java.util.Optional;
import java.util.OptionalDouble;
import org.junit.jupiter.api.Test;

/** SS351 §7 and BUG-3415/YKT-2738, PT-TIMED-RECOVERY-001..008. */
final class TimedAlertPendingRecoveryTest {
  private static final Instant EPOCH = Instant.parse("2026-10-23T00:00:00Z");

  @FunctionalInterface
  private interface Samples {
    Optional<Event> observe(
        boolean aboveWarning, boolean consecutive, long elapsed, long aboveWarningSeconds);
  }

  @Test
  void timedSyncLatencyDoesNotRecoverWhileLatencyRemainsAboveTwoSeconds() {
    var monitor = new TimedSyncLatencyMonitor(Service.API);
    verifyContinuousRecovery(
        (high, consecutive, elapsed, duration) ->
            monitor.observe(OptionalDouble.of(high ? 2.2 : 2.0), consecutive, at(elapsed)).event(),
        300);
  }

  @Test
  void timedFilesystemDoesNotRecoverWhileUsageRemainsAtEightyPercent() {
    var monitor = new TimedFilesystemMonitor(Service.API);
    verifyContinuousRecovery(
        (high, consecutive, elapsed, duration) ->
            monitor.observe(OptionalDouble.of(high ? 80 : 79), consecutive, at(elapsed)).event(),
        300);
  }

  @Test
  void timedHeapDoesNotRecoverWhileUsageRemainsAtSeventyFivePercent() {
    var monitor = new TimedJvmHeapMonitor(Service.API);
    verifyContinuousRecovery(
        (high, consecutive, elapsed, duration) ->
            monitor
                .observe(OptionalDouble.of(high ? 75 : 74), false, consecutive, at(elapsed))
                .event(),
        600);
  }

  @Test
  void timedDbPoolDoesNotRecoverWhileUsageRemainsAtEightyPercent() {
    var monitor = new TimedDbPoolMonitor(Service.API);
    verifyContinuousRecovery(
        (high, consecutive, elapsed, duration) ->
            monitor
                .observe(OptionalDouble.of(high ? 80 : 79), 0, 0, consecutive, at(elapsed))
                .event(),
        300);
  }

  @Test
  void policySyncLatencyDoesNotCountPendingWarningAsRecovery() {
    var engine = new MonitoringPolicyEngine();
    verifyContinuousRecovery(
        (high, consecutive, elapsed, duration) -> {
          interruptIfNeeded(engine, Condition.SYNC_P95, consecutive, elapsed);
          return engine.syncP95(
              Service.API,
              high ? 2.2 : 2.0,
              Duration.ofSeconds(duration),
              Duration.ZERO,
              at(elapsed));
        },
        300);
  }

  @Test
  void policyFilesystemDoesNotCountPendingWarningAsRecovery() {
    var engine = new MonitoringPolicyEngine();
    verifyContinuousRecovery(
        (high, consecutive, elapsed, duration) -> {
          interruptIfNeeded(engine, Condition.FILESYSTEM, consecutive, elapsed);
          return engine.filesystem(
              Service.API,
              high ? 80 : 79,
              Duration.ofSeconds(duration),
              Duration.ZERO,
              at(elapsed));
        },
        300);
  }

  @Test
  void policyHeapDoesNotCountPendingWarningAsRecovery() {
    var engine = new MonitoringPolicyEngine();
    verifyContinuousRecovery(
        (high, consecutive, elapsed, duration) -> {
          interruptIfNeeded(engine, Condition.JVM_HEAP, consecutive, elapsed);
          return engine.jvmHeap(
              Service.API, high ? 75 : 74, Duration.ofSeconds(duration), false, at(elapsed));
        },
        600);
  }

  @Test
  void policyDbPoolDoesNotCountPendingWarningAsRecovery() {
    var engine = new MonitoringPolicyEngine();
    verifyContinuousRecovery(
        (high, consecutive, elapsed, duration) -> {
          interruptIfNeeded(engine, Condition.DB_POOL, consecutive, elapsed);
          return engine.dbPool(
              Service.API, high ? 80 : 79, Duration.ofSeconds(duration), 0, 0, at(elapsed));
        },
        300);
  }

  private static void verifyContinuousRecovery(Samples samples, long warningDelay) {
    assertTrue(samples.observe(true, true, 0, 0).isEmpty());
    var warning = samples.observe(true, true, warningDelay, warningDelay).orElseThrow();
    assertTrue(warning.isOpen());
    assertEquals(Severity.WARNING, warning.severity());
    assertEquals(BigInteger.ONE, warning.count());

    assertSame(warning, samples.observe(true, false, warningDelay + 100, 0).orElseThrow());
    assertSame(warning, samples.observe(true, true, warningDelay + 399, 299).orElseThrow());

    long firstNormal = warningDelay + 400;
    assertTrue(samples.observe(false, true, firstNormal, 0).orElseThrow().isOpen());
    assertTrue(samples.observe(false, true, firstNormal + 299, 0).orElseThrow().isOpen());
    var closed = samples.observe(false, true, firstNormal + 300, 0).orElseThrow();
    assertFalse(closed.isOpen());
    assertEquals(Severity.WARNING, closed.severity());
    assertEquals(BigInteger.ONE, closed.count());
    assertEquals(EPOCH.plusSeconds(warningDelay), closed.firstSeen());
    assertEquals(warning.firstSeen(), closed.lastSeen());
  }

  private static void interruptIfNeeded(
      MonitoringPolicyEngine engine, Condition condition, boolean consecutive, long elapsed) {
    if (!consecutive)
      engine.observationMissing(condition, Service.API, Duration.ofSeconds(elapsed));
  }

  private static ObservationContext at(long elapsed) {
    return new ObservationContext(
        CauseClearance.CONFIRMED, EPOCH.plusSeconds(elapsed), Duration.ofSeconds(elapsed));
  }
}
