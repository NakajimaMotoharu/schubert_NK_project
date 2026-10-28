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
import dev.codex.schubert.nk.batch.monitoring.BackupHealthMonitor.Completion;
import dev.codex.schubert.nk.batch.monitoring.BackupHealthMonitor.Evaluation;
import java.math.BigInteger;
import java.time.Duration;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Optional;
import java.util.OptionalLong;
import java.util.concurrent.Callable;
import java.util.concurrent.Executors;
import org.junit.jupiter.api.Test;

/** BACKUPMON001..008/1683 independent fixed health/time fixtures, no actual Backup/DB/Root. */
class BackupHealthMonitorTest {
  private static final Instant OBSERVED_AT = Instant.parse("2026-10-24T00:00:00Z");

  private static ObservationContext at(long seconds, CauseClearance cause) {
    return new ObservationContext(
        cause, OBSERVED_AT.plusSeconds(seconds), Duration.ofSeconds(seconds));
  }

  private static Evaluation sample(
      BackupHealthMonitor owner, boolean scheduled, boolean success, long failures, long seconds) {
    return owner.observe(
        Optional.of(new Completion(scheduled, success)),
        OptionalLong.of(failures),
        true,
        at(seconds, CauseClearance.CONFIRMED));
  }

  @Test
  void backupMon001KnownNormalMissingAndPartialStayDistinctWithoutInventedEvents() {
    var owner = new BackupHealthMonitor();
    assertTrue(owner.snapshot().isEmpty());
    var normal = sample(owner, false, false, 0, 0);
    assertTrue(normal.completionPresent());
    assertTrue(normal.failureCountPresent());
    assertTrue(normal.event().isEmpty());
    var missing =
        owner.observe(
            Optional.empty(), OptionalLong.empty(), true, at(1, CauseClearance.CONFIRMED));
    assertFalse(missing.completionPresent());
    assertFalse(missing.failureCountPresent());
    assertTrue(missing.event().isEmpty());
    var onlyCompletion =
        owner.observe(
            Optional.of(new Completion(false, true)),
            OptionalLong.empty(),
            true,
            at(2, CauseClearance.CONFIRMED));
    assertTrue(onlyCompletion.completionPresent());
    assertFalse(onlyCompletion.failureCountPresent());
    assertTrue(onlyCompletion.event().isEmpty());
    var onlyCount =
        owner.observe(Optional.empty(), OptionalLong.of(1), true, at(3, CauseClearance.CONFIRMED));
    assertFalse(onlyCount.completionPresent());
    assertTrue(onlyCount.failureCountPresent());
    assertTrue(onlyCount.event().isEmpty());
  }

  @Test
  void backupMon002FixedSeverityAndPartialAbnormalEvidenceAreIndependent() {
    for (boolean scheduled : new boolean[] {false, true}) {
      for (boolean success : new boolean[] {false, true}) {
        for (long failures : new long[] {0, 1, 2, Long.MAX_VALUE}) {
          Severity expected =
              failures >= 2
                  ? Severity.CRITICAL
                  : scheduled && !success ? Severity.WARNING : Severity.NORMAL;
          var result = sample(new BackupHealthMonitor(), scheduled, success, failures, 0);
          if (expected == Severity.NORMAL) assertTrue(result.event().isEmpty());
          else {
            var event = result.event().orElseThrow();
            assertEquals(expected, event.severity());
            assertEquals(Condition.BACKUP, event.condition());
            assertEquals(Service.BATCH, event.service());
            assertEquals(BigInteger.ONE, event.count());
            assertEquals(OBSERVED_AT, event.firstSeen());
            assertEquals(OBSERVED_AT, event.lastSeen());
            assertTrue(event.isOpen());
          }
        }
      }
    }
    var statusOnly =
        new BackupHealthMonitor()
            .observe(
                Optional.of(new Completion(true, false)),
                OptionalLong.empty(),
                true,
                at(0, CauseClearance.CONFIRMED));
    assertTrue(statusOnly.completionPresent());
    assertFalse(statusOnly.failureCountPresent());
    assertEquals(Severity.WARNING, statusOnly.event().orElseThrow().severity());
    var countOnly =
        new BackupHealthMonitor()
            .observe(Optional.empty(), OptionalLong.of(2), true, at(0, CauseClearance.CONFIRMED));
    assertFalse(countOnly.completionPresent());
    assertTrue(countOnly.failureCountPresent());
    assertEquals(Severity.CRITICAL, countOnly.event().orElseThrow().severity());
  }

  @Test
  void backupMon003PartialOrMissingCannotBridgeWarningRecovery() {
    var owner = new BackupHealthMonitor();
    var first = sample(owner, true, false, 0, 0).event().orElseThrow();
    sample(owner, true, true, 0, 1);
    var missing =
        owner.observe(
            Optional.empty(), OptionalLong.empty(), true, at(180, CauseClearance.CONFIRMED));
    assertSame(first, missing.event().orElseThrow());
    var statusOnly =
        owner.observe(
            Optional.of(new Completion(true, true)),
            OptionalLong.empty(),
            true,
            at(181, CauseClearance.CONFIRMED));
    assertSame(first, statusOnly.event().orElseThrow());
    var countOnly =
        owner.observe(
            Optional.empty(), OptionalLong.of(0), true, at(182, CauseClearance.CONFIRMED));
    assertSame(first, countOnly.event().orElseThrow());
    sample(owner, true, true, 0, 200);
    assertTrue(sample(owner, true, true, 0, 499).event().orElseThrow().isOpen());
    var closed = sample(owner, true, true, 0, 500).event().orElseThrow();
    assertFalse(closed.isOpen());
    assertEquals(BigInteger.ONE, closed.count());
    assertEquals(OBSERVED_AT, closed.firstSeen());
    assertEquals(OBSERVED_AT, closed.lastSeen());
    assertTrue(owner.snapshot().isEmpty());
    assertTrue(first.isOpen());
  }

  @Test
  void backupMon004CriticalNeedsTenMinutesAndConfirmedCauseDespiteLowerWarning() {
    var owner = new BackupHealthMonitor();
    var first = sample(owner, false, false, 2, 0).event().orElseThrow();
    var lower = sample(owner, true, false, 0, 1).event().orElseThrow();
    assertEquals(Severity.CRITICAL, lower.severity());
    assertEquals(BigInteger.TWO, lower.count());
    assertEquals(BigInteger.ONE, first.count());
    sample(owner, true, true, 0, 2);
    var unconfirmed =
        owner.observe(
            Optional.of(new Completion(true, true)),
            OptionalLong.of(0),
            true,
            at(602, CauseClearance.UNCONFIRMED));
    assertTrue(unconfirmed.event().orElseThrow().isOpen());
    var closed = sample(owner, true, true, 0, 603).event().orElseThrow();
    assertFalse(closed.isOpen());
    assertEquals(BigInteger.TWO, closed.count());
    assertEquals(Severity.CRITICAL, closed.severity());
    assertEquals(OBSERVED_AT, closed.firstSeen());
    assertEquals(OBSERVED_AT.plusSeconds(1), closed.lastSeen());
    assertTrue(owner.snapshot().isEmpty());
  }

  @Test
  void backupMon005GapInvalidAndNullObservationsCannotFakeRecovery() {
    var owner = new BackupHealthMonitor();
    var first = sample(owner, true, false, 0, 0).event().orElseThrow();
    sample(owner, true, true, 0, 1);
    assertThrows(
        NullPointerException.class,
        () -> owner.observe(null, OptionalLong.empty(), true, at(2, CauseClearance.CONFIRMED)));
    assertThrows(
        NullPointerException.class,
        () -> owner.observe(Optional.empty(), null, true, at(2, CauseClearance.CONFIRMED)));
    assertThrows(
        NullPointerException.class,
        () -> owner.observe(Optional.empty(), OptionalLong.empty(), true, null));
    for (long invalid : new long[] {-1, Long.MIN_VALUE})
      assertThrows(IllegalArgumentException.class, () -> sample(owner, true, true, invalid, 2));
    assertThrows(IllegalArgumentException.class, () -> sample(owner, true, true, 0, 0));
    assertSame(first, owner.snapshot().orElseThrow());
    owner.observe(
        Optional.of(new Completion(true, true)),
        OptionalLong.of(0),
        false,
        at(300, CauseClearance.CONFIRMED));
    assertTrue(sample(owner, true, true, 0, 599).event().orElseThrow().isOpen());
    assertFalse(sample(owner, true, true, 0, 600).event().orElseThrow().isOpen());
    assertTrue(owner.snapshot().isEmpty());
  }

  @Test
  void backupMon006ConcurrentSameOwnerKeepsExactCountAndOtherOwnerIndependent() throws Exception {
    var owner = new BackupHealthMonitor();
    var other = new BackupHealthMonitor();
    var otherEvent = sample(other, true, false, 0, 0).event().orElseThrow();
    var tasks = new ArrayList<Callable<Boolean>>();
    for (int i = 0; i < 64; i++) {
      long failures = i % 2 == 0 ? 0 : 2;
      tasks.add(() -> sample(owner, true, false, failures, 0).event().orElseThrow().isOpen());
    }
    try (var pool = Executors.newFixedThreadPool(8)) {
      for (var result : pool.invokeAll(tasks)) assertTrue(result.get());
    }
    var last = owner.snapshot().orElseThrow();
    assertEquals(BigInteger.valueOf(64), last.count());
    assertEquals(Severity.CRITICAL, last.severity());
    assertEquals(OBSERVED_AT, last.firstSeen());
    assertEquals(OBSERVED_AT, last.lastSeen());
    assertSame(otherEvent, other.snapshot().orElseThrow());
    assertEquals(BigInteger.ONE, otherEvent.count());
    assertEquals(Severity.WARNING, otherEvent.severity());
  }

  @Test
  void backupMon007CompletionGeneratedContractUsesIndependentBooleanHashAndText() {
    var actual = new Completion(true, false);
    Object self = actual;
    Object absent = null;
    Object other = "completion";
    assertTrue(actual.equals(self));
    assertEquals(new Completion(true, false), actual);
    assertFalse(actual.equals(absent));
    assertFalse(actual.equals(other));
    assertFalse(actual.equals(new Completion(false, false)));
    assertFalse(actual.equals(new Completion(true, true)));
    assertTrue(actual.scheduledRunPassed());
    assertFalse(actual.todaySuccess());
    assertFalse(new Completion(false, true).scheduledRunPassed());
    assertTrue(new Completion(false, true).todaySuccess());
    assertEquals(39398, actual.hashCode());
    assertEquals(39584, new Completion(false, false).hashCode());
    assertEquals("Completion[scheduledRunPassed=true, todaySuccess=false]", actual.toString());
  }

  @Test
  void backupMon008EvaluationGeneratedContractUsesIndependentIdentityAndBooleanOracles() {
    var actual = new Evaluation(true, true, Optional.empty());
    Object self = actual;
    Object absent = null;
    Object other = "evaluation";
    assertTrue(actual.equals(self));
    assertEquals(new Evaluation(true, true, Optional.empty()), actual);
    assertFalse(actual.equals(absent));
    assertFalse(actual.equals(other));
    assertFalse(actual.equals(new Evaluation(false, true, Optional.empty())));
    assertFalse(actual.equals(new Evaluation(true, false, Optional.empty())));
    assertFalse(new Evaluation(false, true, Optional.empty()).completionPresent());
    assertFalse(new Evaluation(true, false, Optional.empty()).failureCountPresent());
    var event = sample(new BackupHealthMonitor(), true, false, 0, 0).event().orElseThrow();
    assertFalse(actual.equals(new Evaluation(true, true, Optional.of(event))));
    assertTrue(actual.completionPresent());
    assertTrue(actual.failureCountPresent());
    assertEquals(Optional.empty(), actual.event());
    assertEquals(1221152, actual.hashCode());
    assertEquals(
        "Evaluation[completionPresent=true, failureCountPresent=true, event=Optional.empty]",
        actual.toString());
    var populated = new Evaluation(true, true, Optional.of(event));
    assertSame(event, populated.event().orElseThrow());
    assertEquals(new Evaluation(true, true, Optional.of(event)), populated);
    assertEquals(1221152 + System.identityHashCode(event), populated.hashCode());
    assertEquals(
        "Evaluation[completionPresent=true, failureCountPresent=true, event=Optional[dev.codex.schubert.nk.batch.monitoring.AlertLifecycle$Event@"
            + Integer.toHexString(System.identityHashCode(event))
            + "]]",
        populated.toString());
    assertThrows(NullPointerException.class, () -> new Evaluation(false, false, null));
  }
}
