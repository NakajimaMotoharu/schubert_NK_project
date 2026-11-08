package dev.codex.schubert.nk.batch.monitoring;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.CauseClearance;
import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.Condition;
import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.Service;
import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.Severity;
import dev.codex.schubert.nk.batch.monitoring.ExpiryBacklogMonitor.Evaluation;
import java.math.BigInteger;
import java.time.Duration;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Optional;
import java.util.OptionalLong;
import java.util.concurrent.Callable;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Test;

/**
 * EXPIRYMON001..008/1676: supplied count and memory context only, no actual queue/purge/control.
 */
class ExpiryBacklogMonitorTest {
  private static final Instant OBSERVED_AT = Instant.parse("2026-10-24T00:00:00Z");

  private static ObservationContext at(long seconds, CauseClearance cause) {
    return new ObservationContext(
        cause, OBSERVED_AT.plusSeconds(seconds), Duration.ofSeconds(seconds));
  }

  private static Evaluation sample(ExpiryBacklogMonitor monitor, long count, long seconds) {
    return monitor.observe(OptionalLong.of(count), true, at(seconds, CauseClearance.CONFIRMED));
  }

  @Test
  void expiryMon001KnownNormalAndUnknownDoNotInventAnEvent() {
    var monitor = new ExpiryBacklogMonitor();
    assertTrue(monitor.snapshot().isEmpty());
    var normal = sample(monitor, 0, 0);
    assertTrue(normal.suppliedValuePresent());
    assertTrue(normal.event().isEmpty());
    var unknown = monitor.observe(OptionalLong.empty(), true, at(1, CauseClearance.CONFIRMED));
    assertFalse(unknown.suppliedValuePresent());
    assertTrue(unknown.event().isEmpty());
    assertTrue(monitor.snapshot().isEmpty());
  }

  @Test
  void expiryMon002ExactCountBoundariesHaveFixedSeverityAndKey() {
    long[] counts = {999, 1000, 4999, 5000, Long.MAX_VALUE};
    Severity[] expected = {
      Severity.NORMAL, Severity.WARNING, Severity.WARNING, Severity.CRITICAL, Severity.CRITICAL
    };
    for (int i = 0; i < counts.length; i++) {
      var monitor = new ExpiryBacklogMonitor();
      var actual = sample(monitor, counts[i], 0);
      assertTrue(actual.suppliedValuePresent());
      if (expected[i] == Severity.NORMAL) assertTrue(actual.event().isEmpty());
      else {
        var event = actual.event().orElseThrow();
        assertEquals(expected[i], event.severity());
        assertEquals(Condition.EXPIRY, event.condition());
        assertEquals(Service.BROKER, event.service());
        assertEquals(BigInteger.ONE, event.count());
        assertEquals(OBSERVED_AT, event.firstSeen());
        assertEquals(OBSERVED_AT, event.lastSeen());
        assertTrue(event.isOpen());
      }
    }
  }

  @Test
  void expiryMon003MissingBreaksWarningRecoveryWithoutErasingOldEvent() {
    var monitor = new ExpiryBacklogMonitor();
    var first = sample(monitor, 1000, 0).event().orElseThrow();
    sample(monitor, 0, 1);
    var missing = monitor.observe(OptionalLong.empty(), true, at(180, CauseClearance.CONFIRMED));
    assertFalse(missing.suppliedValuePresent());
    assertSame(first, missing.event().orElseThrow());
    sample(monitor, 0, 200);
    assertTrue(sample(monitor, 0, 499).event().orElseThrow().isOpen());
    var closed = sample(monitor, 0, 500).event().orElseThrow();
    assertFalse(closed.isOpen());
    assertEquals(BigInteger.ONE, closed.count());
    assertEquals(OBSERVED_AT, closed.firstSeen());
    assertEquals(OBSERVED_AT, closed.lastSeen());
    assertTrue(first.isOpen());
    assertTrue(monitor.snapshot().isEmpty());
  }

  @Test
  void expiryMon004CriticalStaysStickyUntilTenNormalMinutesAndCauseConfirmed() {
    var monitor = new ExpiryBacklogMonitor();
    var first = sample(monitor, 5000, 0).event().orElseThrow();
    var lower = sample(monitor, 1000, 1).event().orElseThrow();
    assertEquals(Severity.CRITICAL, lower.severity());
    assertEquals(BigInteger.TWO, lower.count());
    sample(monitor, 0, 2);
    var unconfirmed =
        monitor.observe(OptionalLong.of(0), true, at(602, CauseClearance.UNCONFIRMED));
    assertTrue(unconfirmed.event().orElseThrow().isOpen());
    var closed = sample(monitor, 0, 603).event().orElseThrow();
    assertFalse(closed.isOpen());
    assertEquals(Severity.CRITICAL, closed.severity());
    assertEquals(OBSERVED_AT, closed.firstSeen());
    assertEquals(OBSERVED_AT.plusSeconds(1), closed.lastSeen());
    assertEquals(BigInteger.TWO, closed.count());
    assertEquals(BigInteger.ONE, first.count());
    assertTrue(monitor.snapshot().isEmpty());
  }

  @Test
  void expiryMon005ExplicitGapRestartsTheFiveMinuteWarningRecovery() {
    var monitor = new ExpiryBacklogMonitor();
    sample(monitor, 1000, 0);
    sample(monitor, 0, 1);
    monitor.observe(OptionalLong.of(0), false, at(300, CauseClearance.CONFIRMED));
    assertTrue(sample(monitor, 0, 599).event().orElseThrow().isOpen());
    assertFalse(sample(monitor, 0, 600).event().orElseThrow().isOpen());
    assertTrue(monitor.snapshot().isEmpty());
  }

  @Test
  void expiryMon006NullNegativeAndReversedTimeCannotChangeAcceptedEvent() {
    var monitor = new ExpiryBacklogMonitor();
    var first = sample(monitor, 1000, 5).event().orElseThrow();
    assertThrows(
        NullPointerException.class,
        () -> monitor.observe(null, true, at(6, CauseClearance.CONFIRMED)));
    assertThrows(NullPointerException.class, () -> monitor.observe(OptionalLong.of(0), true, null));
    assertThrows(IllegalArgumentException.class, () -> sample(monitor, -1, 6));
    assertThrows(IllegalArgumentException.class, () -> sample(monitor, Long.MIN_VALUE, 6));
    assertThrows(IllegalArgumentException.class, () -> sample(monitor, 0, 4));
    assertSame(first, monitor.snapshot().orElseThrow());
    sample(monitor, 0, 6);
    assertFalse(sample(monitor, 0, 306).event().orElseThrow().isOpen());
    assertTrue(monitor.snapshot().isEmpty());
  }

  @Test
  void expiryMon007ConcurrentSameOwnerAndIndependentOwnerHaveExactCounts() throws Exception {
    var monitor = new ExpiryBacklogMonitor();
    var other = new ExpiryBacklogMonitor();
    var otherEvent = sample(other, 1000, 0).event().orElseThrow();
    var tasks = new ArrayList<Callable<Boolean>>();
    for (int i = 0; i < 64; i++) {
      long count = i % 2 == 0 ? 1000 : 5000;
      tasks.add(
          () -> {
            var actual = sample(monitor, count, 0);
            return actual.suppliedValuePresent() && actual.event().orElseThrow().isOpen();
          });
    }
    var pool = Executors.newFixedThreadPool(8);
    try {
      for (var result : pool.invokeAll(tasks, 10, TimeUnit.SECONDS)) assertTrue(result.get());
    } finally {
      pool.shutdownNow();
      assertTrue(pool.awaitTermination(10, TimeUnit.SECONDS));
    }
    var actual = monitor.snapshot().orElseThrow();
    assertEquals(BigInteger.valueOf(64), actual.count());
    assertEquals(Severity.CRITICAL, actual.severity());
    assertEquals(OBSERVED_AT, actual.firstSeen());
    assertEquals(OBSERVED_AT, actual.lastSeen());
    assertSame(otherEvent, other.snapshot().orElseThrow());
    assertEquals(BigInteger.ONE, otherEvent.count());
    assertEquals(Severity.WARNING, otherEvent.severity());
  }

  @Test
  void expiryMon008GeneratedEvaluationContractsUseIndependentBooleanAndIdentityHashes() {
    var actual = new Evaluation(true, Optional.empty());
    Object self = actual;
    Object absent = null;
    Object otherType = "not evaluation";
    assertTrue(actual.equals(self));
    assertTrue(actual.equals(new Evaluation(true, Optional.empty())));
    assertFalse(actual.equals(absent));
    assertFalse(actual.equals(otherType));
    var missing = new Evaluation(false, Optional.empty());
    assertFalse(actual.equals(missing));
    assertFalse(missing.suppliedValuePresent());
    assertEquals(38347, missing.hashCode());
    assertEquals(
        "Evaluation[suppliedValuePresent=false, event=Optional.empty]", missing.toString());
    var event = sample(new ExpiryBacklogMonitor(), 1000, 0).event().orElseThrow();
    var populated = new Evaluation(true, Optional.of(event));
    assertFalse(actual.equals(populated));
    assertTrue(populated.equals(new Evaluation(true, Optional.of(event))));
    assertTrue(actual.suppliedValuePresent());
    assertEquals(Optional.empty(), actual.event());
    assertSame(event, populated.event().orElseThrow());
    assertEquals(38161, actual.hashCode());
    assertEquals(38161 + System.identityHashCode(event), populated.hashCode());
    assertEquals("Evaluation[suppliedValuePresent=true, event=Optional.empty]", actual.toString());
    assertEquals(
        "Evaluation[suppliedValuePresent=true,"
            + " event=Optional[dev.codex.schubert.nk.batch.monitoring.AlertLifecycle$Event@"
            + Integer.toHexString(System.identityHashCode(event))
            + "]]",
        populated.toString());
    assertThrows(NullPointerException.class, () -> new Evaluation(false, null));
  }
}
