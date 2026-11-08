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
import dev.codex.schubert.nk.batch.monitoring.IntegrityHealthMonitor.Evaluation;
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

/** INTEGRITYMON001..008/1687 fixed count/time fixtures, no real file/DB/key/config access. */
class IntegrityHealthMonitorTest {
  private static final Instant OBSERVED_AT = Instant.parse("2026-10-24T00:00:00Z");

  private static ObservationContext at(long seconds, CauseClearance cause) {
    return new ObservationContext(
        cause, OBSERVED_AT.plusSeconds(seconds), Duration.ofSeconds(seconds));
  }

  private static IntegrityHealthMonitor owner() {
    return new IntegrityHealthMonitor(Service.BATCH);
  }

  private static Evaluation sample(IntegrityHealthMonitor owner, long failures, long seconds) {
    return owner.observe(OptionalLong.of(failures), true, at(seconds, CauseClearance.CONFIRMED));
  }

  @Test
  void integrityMon001KnownZeroAndMissingDoNotInventOrConflateEvents() {
    var owner = owner();
    assertTrue(owner.snapshot().isEmpty());
    var normal = sample(owner, 0, 0);
    assertTrue(normal.failureCountPresent());
    assertTrue(normal.event().isEmpty());
    var missing = owner.observe(OptionalLong.empty(), true, at(1, CauseClearance.CONFIRMED));
    assertFalse(missing.failureCountPresent());
    assertTrue(missing.event().isEmpty());
    assertTrue(owner.snapshot().isEmpty());
  }

  @Test
  void integrityMon002OneOrMaximumFailureIsCriticalWithFixedIdentity() {
    for (long count : new long[] {1, Long.MAX_VALUE}) {
      var result = sample(owner(), count, 0);
      assertTrue(result.failureCountPresent());
      var event = result.event().orElseThrow();
      assertEquals(Condition.INTEGRITY_CONFIG, event.condition());
      assertEquals(Service.BATCH, event.service());
      assertEquals(Severity.CRITICAL, event.severity());
      assertEquals(BigInteger.ONE, event.count());
      assertEquals(OBSERVED_AT, event.firstSeen());
      assertEquals(OBSERVED_AT, event.lastSeen());
      assertTrue(event.isOpen());
    }
  }

  @Test
  void integrityMon003NormalEvenConfirmedAndMaximumElapsedCannotAutoClose() {
    var owner = owner();
    var first = sample(owner, 1, 0).event().orElseThrow();
    for (var cause : CauseClearance.values()) {
      for (long seconds : new long[] {1, 601, 86400}) {
        var result = owner.observe(OptionalLong.of(0), true, at(seconds, cause));
        assertSame(first, result.event().orElseThrow());
      }
      // Start a separate owner for the next cause's earlier elapsed vector.
      owner = owner();
      first = sample(owner, 1, 0).event().orElseThrow();
    }
    var maximum =
        new ObservationContext(
            CauseClearance.CONFIRMED, Instant.MAX, Duration.ofSeconds(Long.MAX_VALUE, 999_999_999));
    assertSame(first, owner.observe(OptionalLong.of(0), true, maximum).event().orElseThrow());
    assertSame(first, owner.snapshot().orElseThrow());
    assertTrue(first.isOpen());
    assertEquals(BigInteger.ONE, first.count());
    assertEquals(OBSERVED_AT, first.firstSeen());
    assertEquals(OBSERVED_AT, first.lastSeen());
  }

  @Test
  void integrityMon004UnknownAndExplicitGapKeepOldEventAndNewViolationHistory() {
    var owner = owner();
    var first = sample(owner, 1, 0).event().orElseThrow();
    var missing = owner.observe(OptionalLong.empty(), true, at(1, CauseClearance.CONFIRMED));
    assertFalse(missing.failureCountPresent());
    assertSame(first, missing.event().orElseThrow());
    var gap = owner.observe(OptionalLong.of(0), false, at(2, CauseClearance.CONFIRMED));
    assertSame(first, gap.event().orElseThrow());
    assertSame(first, sample(owner, 0, 602).event().orElseThrow());
    var second = sample(owner, 1, 603).event().orElseThrow();
    assertEquals(Severity.CRITICAL, second.severity());
    assertEquals(BigInteger.TWO, second.count());
    assertEquals(OBSERVED_AT, second.firstSeen());
    assertEquals(OBSERVED_AT.plusSeconds(603), second.lastSeen());
    assertEquals(BigInteger.ONE, first.count());
    assertTrue(first.isOpen());
  }

  @Test
  void integrityMon005NullNegativeAndReversedTimeRejectWithoutMutatingEvent() {
    assertThrows(NullPointerException.class, () -> new IntegrityHealthMonitor(null));
    var owner = owner();
    var first = sample(owner, 1, 5).event().orElseThrow();
    assertThrows(
        NullPointerException.class,
        () -> owner.observe(null, true, at(6, CauseClearance.CONFIRMED)));
    assertThrows(NullPointerException.class, () -> owner.observe(OptionalLong.empty(), true, null));
    for (long invalid : new long[] {-1, Long.MIN_VALUE})
      assertThrows(IllegalArgumentException.class, () -> sample(owner, invalid, 6));
    assertThrows(IllegalArgumentException.class, () -> sample(owner, 0, 4));
    assertSame(first, owner.snapshot().orElseThrow());
    assertSame(first, sample(owner, 0, 6).event().orElseThrow());
  }

  @Test
  void integrityMon006EveryClosedServiceUsesItsOwnImmutableLogicalKey() {
    for (var service : Service.values()) {
      var owner = new IntegrityHealthMonitor(service);
      var first = sample(owner, 1, 0).event().orElseThrow();
      assertEquals(service, first.service());
      assertEquals(Condition.INTEGRITY_CONFIG, first.condition());
      assertEquals(Severity.CRITICAL, first.severity());
      assertSame(first, sample(owner, 0, 86400).event().orElseThrow());
      assertEquals(BigInteger.ONE, first.count());
    }
  }

  @Test
  void integrityMon007ConcurrentCallersKeepExactCountAndIndependentOwner() throws Exception {
    var owner = owner();
    var other = new IntegrityHealthMonitor(Service.API);
    var otherEvent = sample(other, 1, 0).event().orElseThrow();
    var tasks = new ArrayList<Callable<Boolean>>();
    for (int i = 0; i < 64; i++) {
      long count = i % 2 == 0 ? 1 : Long.MAX_VALUE;
      tasks.add(() -> sample(owner, count, 0).event().orElseThrow().isOpen());
    }
    var pool = Executors.newFixedThreadPool(8);
    try {
      for (var result : pool.invokeAll(tasks, 10, TimeUnit.SECONDS)) assertTrue(result.get());
    } finally {
      pool.shutdownNow();
      assertTrue(pool.awaitTermination(10, TimeUnit.SECONDS));
    }
    var last = owner.snapshot().orElseThrow();
    assertEquals(BigInteger.valueOf(64), last.count());
    assertEquals(Severity.CRITICAL, last.severity());
    assertEquals(Service.BATCH, last.service());
    assertEquals(OBSERVED_AT, last.firstSeen());
    assertEquals(OBSERVED_AT, last.lastSeen());
    assertSame(otherEvent, other.snapshot().orElseThrow());
    assertEquals(Service.API, otherEvent.service());
    assertEquals(BigInteger.ONE, otherEvent.count());
  }

  @Test
  void integrityMon008GeneratedEvaluationUsesIndependentBooleanAndIdentityOracles() {
    var actual = new Evaluation(true, Optional.empty());
    Object self = actual;
    Object absent = null;
    Object other = "evaluation";
    assertTrue(actual.equals(self));
    assertEquals(new Evaluation(true, Optional.empty()), actual);
    assertFalse(actual.equals(absent));
    assertFalse(actual.equals(other));
    assertFalse(actual.equals(new Evaluation(false, Optional.empty())));
    assertFalse(new Evaluation(false, Optional.empty()).failureCountPresent());
    var event = sample(owner(), 1, 0).event().orElseThrow();
    assertFalse(actual.equals(new Evaluation(true, Optional.of(event))));
    assertTrue(actual.failureCountPresent());
    assertEquals(Optional.empty(), actual.event());
    assertEquals(38161, actual.hashCode());
    assertEquals(38347, new Evaluation(false, Optional.empty()).hashCode());
    assertEquals("Evaluation[failureCountPresent=true, event=Optional.empty]", actual.toString());
    var populated = new Evaluation(true, Optional.of(event));
    assertSame(event, populated.event().orElseThrow());
    assertEquals(new Evaluation(true, Optional.of(event)), populated);
    assertEquals(38161 + System.identityHashCode(event), populated.hashCode());
    assertEquals(
        "Evaluation[failureCountPresent=true,"
            + " event=Optional[dev.codex.schubert.nk.batch.monitoring.AlertLifecycle$Event@"
            + Integer.toHexString(System.identityHashCode(event))
            + "]]",
        populated.toString());
    assertThrows(NullPointerException.class, () -> new Evaluation(false, null));
  }
}
