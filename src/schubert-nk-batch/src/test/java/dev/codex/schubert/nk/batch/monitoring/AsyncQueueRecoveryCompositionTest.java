package dev.codex.schubert.nk.batch.monitoring;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.CauseClearance;
import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.Severity;
import dev.codex.schubert.nk.batch.monitoring.AsyncQueueMonitor.ByteUsage;
import java.math.BigInteger;
import java.time.Duration;
import java.time.Instant;
import java.util.Optional;
import java.util.OptionalLong;
import org.junit.jupiter.api.Test;

/** UI252 §6, SS321 §5.2, SS351 §7, PT-ASYNC-RECOVERY-001/002. */
final class AsyncQueueRecoveryCompositionTest {
  private static final Instant EPOCH = Instant.parse("2026-10-23T00:00:00Z");
  private static final long FIRST_CRITICAL_BYTE = 8_301_034_833_169_298_227L;
  private static final OptionalLong ZERO_QUEUED = OptionalLong.of(0);
  private static final Optional<ByteUsage> ZERO_USED =
      Optional.of(new ByteUsage(0, Long.MAX_VALUE));

  @Test
  void partialByteCriticalRequiresFreshContinuousRecoveryAndCauseConfirmation() {
    var monitor = new AsyncQueueMonitor();
    var warning =
        monitor
            .observe(OptionalLong.empty(), bytes(FIRST_CRITICAL_BYTE - 1), true, at(0, true))
            .event()
            .orElseThrow();
    assertEquals(Severity.WARNING, warning.severity());
    var critical =
        monitor.observe(OptionalLong.empty(), bytes(FIRST_CRITICAL_BYTE), true, at(1, true));
    assertFalse(critical.queuedPresent());
    assertTrue(critical.byteUsagePresent());
    var event = critical.event().orElseThrow();
    assertEquals(Severity.CRITICAL, event.severity());
    assertEquals(BigInteger.TWO, event.count());
    assertEquals(EPOCH, event.firstSeen());
    assertEquals(EPOCH.plusSeconds(1), event.lastSeen());

    monitor.observe(ZERO_QUEUED, ZERO_USED, true, at(2, true));
    var partialNormal = monitor.observe(ZERO_QUEUED, Optional.empty(), true, at(602, true));
    assertSame(event, partialNormal.event().orElseThrow());
    monitor.observe(ZERO_QUEUED, ZERO_USED, true, at(603, true));
    var tooEarly = monitor.observe(ZERO_QUEUED, ZERO_USED, true, at(1202, true));
    assertSame(event, tooEarly.event().orElseThrow());
    var unconfirmed = monitor.observe(ZERO_QUEUED, ZERO_USED, true, at(1203, false));
    assertSame(event, unconfirmed.event().orElseThrow());
    var closed =
        monitor.observe(ZERO_QUEUED, ZERO_USED, true, at(1204, true)).event().orElseThrow();
    assertFalse(closed.isOpen());
    assertEquals(Severity.CRITICAL, closed.severity());
    assertEquals(BigInteger.TWO, closed.count());
    assertEquals(EPOCH, closed.firstSeen());
    assertEquals(EPOCH.plusSeconds(1), closed.lastSeen());
    assertTrue(monitor.snapshot().isEmpty());
  }

  @Test
  void simultaneousCriticalCountAndBytesCountAsOneObservation() {
    var monitor = new AsyncQueueMonitor();
    var evaluated =
        monitor.observe(OptionalLong.of(9_000), bytes(FIRST_CRITICAL_BYTE), true, at(0, true));
    assertTrue(evaluated.queuedPresent());
    assertTrue(evaluated.byteUsagePresent());
    var event = evaluated.event().orElseThrow();
    assertTrue(event.isOpen());
    assertEquals(Severity.CRITICAL, event.severity());
    assertEquals(BigInteger.ONE, event.count());
    assertEquals(EPOCH, event.lastSeen());
    assertSame(event, monitor.snapshot().orElseThrow());
  }

  private static Optional<ByteUsage> bytes(long used) {
    return Optional.of(new ByteUsage(used, Long.MAX_VALUE));
  }

  private static ObservationContext at(long second, boolean confirmed) {
    return new ObservationContext(
        confirmed ? CauseClearance.CONFIRMED : CauseClearance.UNCONFIRMED,
        EPOCH.plusSeconds(second),
        Duration.ofSeconds(second));
  }
}
