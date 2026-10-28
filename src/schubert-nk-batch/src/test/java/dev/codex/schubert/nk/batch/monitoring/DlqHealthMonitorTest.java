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
import dev.codex.schubert.nk.batch.monitoring.DlqHealthMonitor.Evaluation;
import dev.codex.schubert.nk.batch.monitoring.DlqHealthMonitor.Observation;
import java.math.BigInteger;
import java.time.Duration;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Optional;
import java.util.concurrent.Callable;
import java.util.concurrent.Executors;
import org.junit.jupiter.api.Test;

/**
 * DLQMON001..008/1689 current-entry count/flags only, no broker/incident/body/DB/control access.
 */
class DlqHealthMonitorTest {
  private static final Instant OBSERVED_AT = Instant.parse("2026-10-24T00:00:00Z");

  private static ObservationContext at(long seconds, CauseClearance cause) {
    return new ObservationContext(
        cause, OBSERVED_AT.plusSeconds(seconds), Duration.ofSeconds(seconds));
  }

  private static DlqHealthMonitor owner() {
    return new DlqHealthMonitor(Service.BROKER);
  }

  private static Evaluation sample(
      DlqHealthMonitor owner, long count, boolean growing, boolean uninvestigated, long seconds) {
    return owner.observe(
        Optional.of(new Observation(count, growing, uninvestigated)),
        true,
        at(seconds, CauseClearance.CONFIRMED));
  }

  @Test
  void dlqMon001KnownEmptyAndUnknownRemainDistinctWithoutInventingEvents() {
    var owner = owner();
    assertTrue(owner.snapshot().isEmpty());
    var normal = sample(owner, 0, false, false, 0);
    assertTrue(normal.observationPresent());
    assertTrue(normal.event().isEmpty());
    var missing = owner.observe(Optional.empty(), true, at(1, CauseClearance.CONFIRMED));
    assertFalse(missing.observationPresent());
    assertTrue(missing.event().isEmpty());
    assertTrue(owner.snapshot().isEmpty());
  }

  @Test
  void dlqMon002CoherentEntryMatrixUsesIndependentSeverityAndAllServiceKeys() {
    for (var service : Service.values()) {
      for (long count : new long[] {1, Long.MAX_VALUE}) {
        for (boolean growing : new boolean[] {false, true}) {
          for (boolean pending : new boolean[] {false, true}) {
            var event =
                sample(new DlqHealthMonitor(service), count, growing, pending, 0)
                    .event()
                    .orElseThrow();
            assertEquals(
                growing || pending ? Severity.CRITICAL : Severity.WARNING, event.severity());
            assertEquals(Condition.DLQ, event.condition());
            assertEquals(service, event.service());
            assertEquals(BigInteger.ONE, event.count());
            assertEquals(OBSERVED_AT, event.firstSeen());
            assertEquals(OBSERVED_AT, event.lastSeen());
            assertTrue(event.isOpen());
          }
        }
      }
    }
  }

  @Test
  void dlqMon003NormalEvenConfirmedCannotAutoCloseWarningOrCritical() {
    for (boolean critical : new boolean[] {false, true}) {
      for (var cause : CauseClearance.values()) {
        var owner = owner();
        var first = sample(owner, 1, critical, false, 0).event().orElseThrow();
        for (long seconds : new long[] {1, 601, 86400})
          assertSame(
              first,
              owner
                  .observe(Optional.of(new Observation(0, false, false)), true, at(seconds, cause))
                  .event()
                  .orElseThrow());
        var maximum =
            new ObservationContext(
                CauseClearance.CONFIRMED,
                Instant.MAX,
                Duration.ofSeconds(Long.MAX_VALUE, 999_999_999));
        assertSame(
            first,
            owner
                .observe(Optional.of(new Observation(0, false, false)), true, maximum)
                .event()
                .orElseThrow());
        assertSame(first, owner.snapshot().orElseThrow());
        assertEquals(critical ? Severity.CRITICAL : Severity.WARNING, first.severity());
        assertEquals(BigInteger.ONE, first.count());
        assertEquals(OBSERVED_AT, first.firstSeen());
        assertEquals(OBSERVED_AT, first.lastSeen());
        assertTrue(first.isOpen());
      }
    }
  }

  @Test
  void dlqMon004UnknownGapAndEscalationPreserveExactHistoricalEvents() {
    var owner = owner();
    var first = sample(owner, 1, false, false, 0).event().orElseThrow();
    assertSame(
        first,
        owner
            .observe(Optional.empty(), true, at(1, CauseClearance.CONFIRMED))
            .event()
            .orElseThrow());
    assertSame(
        first,
        owner
            .observe(
                Optional.of(new Observation(0, false, false)),
                false,
                at(2, CauseClearance.CONFIRMED))
            .event()
            .orElseThrow());
    var critical = sample(owner, 1, false, true, 3).event().orElseThrow();
    assertEquals(Severity.CRITICAL, critical.severity());
    assertEquals(BigInteger.TWO, critical.count());
    assertEquals(OBSERVED_AT, critical.firstSeen());
    assertEquals(OBSERVED_AT.plusSeconds(3), critical.lastSeen());
    assertSame(critical, sample(owner, 0, false, false, 603).event().orElseThrow());
    assertEquals(Severity.WARNING, first.severity());
    assertEquals(BigInteger.ONE, first.count());
  }

  @Test
  void dlqMon005NullNegativeIncoherentAndReversedInputsCannotMutateEvent() {
    assertThrows(NullPointerException.class, () -> new DlqHealthMonitor(null));
    var owner = owner();
    var first = sample(owner, 1, false, false, 5).event().orElseThrow();
    assertThrows(
        NullPointerException.class,
        () -> owner.observe(null, true, at(6, CauseClearance.CONFIRMED)));
    assertThrows(NullPointerException.class, () -> owner.observe(Optional.empty(), true, null));
    for (long count : new long[] {-1, Long.MIN_VALUE})
      assertThrows(IllegalArgumentException.class, () -> sample(owner, count, false, false, 6));
    assertThrows(IllegalArgumentException.class, () -> sample(owner, 0, true, false, 6));
    assertThrows(IllegalArgumentException.class, () -> sample(owner, 0, false, true, 6));
    assertThrows(IllegalArgumentException.class, () -> sample(owner, 0, true, true, 6));
    assertThrows(IllegalArgumentException.class, () -> sample(owner, 0, false, false, 4));
    assertSame(first, owner.snapshot().orElseThrow());
    assertSame(first, sample(owner, 0, false, false, 6).event().orElseThrow());
  }

  @Test
  void dlqMon006ConcurrentSameOwnerAndSeparateOwnerKeepExactCounts() throws Exception {
    var owner = owner();
    var other = new DlqHealthMonitor(Service.API);
    var otherEvent = sample(other, 1, false, false, 0).event().orElseThrow();
    var tasks = new ArrayList<Callable<Boolean>>();
    for (int i = 0; i < 64; i++) {
      boolean pending = i % 2 == 0;
      tasks.add(() -> sample(owner, 1, false, pending, 0).event().orElseThrow().isOpen());
    }
    try (var pool = Executors.newFixedThreadPool(8)) {
      for (var result : pool.invokeAll(tasks)) assertTrue(result.get());
    }
    var last = owner.snapshot().orElseThrow();
    assertEquals(Severity.CRITICAL, last.severity());
    assertEquals(BigInteger.valueOf(64), last.count());
    assertEquals(Service.BROKER, last.service());
    assertEquals(OBSERVED_AT, last.firstSeen());
    assertEquals(OBSERVED_AT, last.lastSeen());
    assertSame(otherEvent, other.snapshot().orElseThrow());
    assertEquals(Service.API, otherEvent.service());
    assertEquals(BigInteger.ONE, otherEvent.count());
    assertEquals(Severity.WARNING, otherEvent.severity());
  }

  @Test
  void dlqMon007ObservationGeneratedContractsUseIndependentLongAndBooleanOracles() {
    var actual = new Observation(1, false, true);
    Object self = actual;
    Object absent = null;
    Object other = "observation";
    assertTrue(actual.equals(self));
    assertEquals(new Observation(1, false, true), actual);
    assertFalse(actual.equals(absent));
    assertFalse(actual.equals(other));
    assertFalse(actual.equals(new Observation(2, false, true)));
    assertFalse(actual.equals(new Observation(1, true, true)));
    assertFalse(actual.equals(new Observation(1, false, false)));
    assertFalse(actual.equals(new Observation(1L << 32, false, true)));
    assertEquals(1, actual.messages());
    assertFalse(actual.increasing());
    assertTrue(actual.uninvestigated());
    assertTrue(new Observation(1, true, false).increasing());
    assertFalse(new Observation(1, true, false).uninvestigated());
    assertEquals(Long.MAX_VALUE, new Observation(Long.MAX_VALUE, false, false).messages());
    assertEquals(40539, actual.hashCode());
    assertEquals(40539, new Observation(1L << 32, false, true).hashCode());
    assertEquals(
        "Observation[messages=1, increasing=false, uninvestigated=true]", actual.toString());
  }

  @Test
  void dlqMon008EvaluationGeneratedContractsUseIndependentBooleanAndIdentityOracles() {
    var actual = new Evaluation(true, Optional.empty());
    Object self = actual;
    Object absent = null;
    Object other = "evaluation";
    assertTrue(actual.equals(self));
    assertEquals(new Evaluation(true, Optional.empty()), actual);
    assertFalse(actual.equals(absent));
    assertFalse(actual.equals(other));
    assertFalse(actual.equals(new Evaluation(false, Optional.empty())));
    assertFalse(new Evaluation(false, Optional.empty()).observationPresent());
    var event = sample(owner(), 1, false, false, 0).event().orElseThrow();
    assertFalse(actual.equals(new Evaluation(true, Optional.of(event))));
    assertTrue(actual.observationPresent());
    assertEquals(Optional.empty(), actual.event());
    assertEquals(38161, actual.hashCode());
    assertEquals(38347, new Evaluation(false, Optional.empty()).hashCode());
    assertEquals("Evaluation[observationPresent=true, event=Optional.empty]", actual.toString());
    var populated = new Evaluation(true, Optional.of(event));
    assertSame(event, populated.event().orElseThrow());
    assertEquals(new Evaluation(true, Optional.of(event)), populated);
    assertEquals(38161 + System.identityHashCode(event), populated.hashCode());
    assertEquals(
        "Evaluation[observationPresent=true, event=Optional[dev.codex.schubert.nk.batch.monitoring.AlertLifecycle$Event@"
            + Integer.toHexString(System.identityHashCode(event))
            + "]]",
        populated.toString());
    assertThrows(NullPointerException.class, () -> new Evaluation(false, null));
  }
}
