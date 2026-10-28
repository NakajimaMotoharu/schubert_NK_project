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
import dev.codex.schubert.nk.batch.monitoring.RestartHealthMonitor.Evaluation;
import java.math.BigInteger;
import java.time.Duration;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Optional;
import java.util.OptionalLong;
import java.util.concurrent.Callable;
import java.util.concurrent.Executors;
import org.junit.jupiter.api.Test;

/**
 * RESTARTMON001..008/1685 independent count/flag/time fixtures; no systemd/control/history read.
 */
class RestartHealthMonitorTest {
  private static final Instant OBSERVED_AT = Instant.parse("2026-10-24T00:00:00Z");

  private static ObservationContext at(long seconds, CauseClearance cause) {
    return new ObservationContext(
        cause, OBSERVED_AT.plusSeconds(seconds), Duration.ofSeconds(seconds));
  }

  private static RestartHealthMonitor owner() {
    return new RestartHealthMonitor(Service.WEB);
  }

  private static Evaluation sample(
      RestartHealthMonitor owner, long count, boolean limited, long seconds) {
    return owner.observe(
        OptionalLong.of(count), Optional.of(limited), true, at(seconds, CauseClearance.CONFIRMED));
  }

  @Test
  void restartMon001KnownNormalUnknownAndPartialFlagsRemainDistinct() {
    var owner = owner();
    assertTrue(owner.snapshot().isEmpty());
    var normal = sample(owner, 0, false, 0);
    assertTrue(normal.restartCountPresent());
    assertTrue(normal.rateLimitPresent());
    assertTrue(normal.event().isEmpty());
    var unknown =
        owner.observe(
            OptionalLong.empty(), Optional.empty(), true, at(1, CauseClearance.CONFIRMED));
    assertFalse(unknown.restartCountPresent());
    assertFalse(unknown.rateLimitPresent());
    assertTrue(unknown.event().isEmpty());
    var onlyCount =
        owner.observe(OptionalLong.of(0), Optional.empty(), true, at(2, CauseClearance.CONFIRMED));
    assertTrue(onlyCount.restartCountPresent());
    assertFalse(onlyCount.rateLimitPresent());
    assertTrue(onlyCount.event().isEmpty());
    var onlyFlag =
        owner.observe(
            OptionalLong.empty(), Optional.of(false), true, at(3, CauseClearance.CONFIRMED));
    assertFalse(onlyFlag.restartCountPresent());
    assertTrue(onlyFlag.rateLimitPresent());
    assertTrue(onlyFlag.event().isEmpty());
  }

  @Test
  void restartMon002CountAndRateLimitUseIndependentFixedGoldenMatrix() {
    long[] counts = {0, 1, 4, 5, Long.MAX_VALUE};
    Severity[] noLimit = {
      Severity.NORMAL, Severity.WARNING, Severity.WARNING, Severity.CRITICAL, Severity.CRITICAL
    };
    for (int i = 0; i < counts.length; i++) {
      for (boolean limited : new boolean[] {false, true}) {
        var result = sample(owner(), counts[i], limited, 0);
        Severity expected = limited ? Severity.CRITICAL : noLimit[i];
        if (expected == Severity.NORMAL) assertTrue(result.event().isEmpty());
        else {
          var event = result.event().orElseThrow();
          assertEquals(expected, event.severity());
          assertEquals(Condition.RESTART, event.condition());
          assertEquals(Service.WEB, event.service());
          assertEquals(BigInteger.ONE, event.count());
          assertEquals(OBSERVED_AT, event.firstSeen());
          assertEquals(OBSERVED_AT, event.lastSeen());
          assertTrue(event.isOpen());
        }
      }
      var countOnly =
          owner()
              .observe(
                  OptionalLong.of(counts[i]),
                  Optional.empty(),
                  true,
                  at(0, CauseClearance.CONFIRMED));
      assertTrue(countOnly.restartCountPresent());
      assertFalse(countOnly.rateLimitPresent());
      if (noLimit[i] == Severity.NORMAL) assertTrue(countOnly.event().isEmpty());
      else assertEquals(noLimit[i], countOnly.event().orElseThrow().severity());
    }
    var flagOnly =
        owner()
            .observe(
                OptionalLong.empty(), Optional.of(true), true, at(0, CauseClearance.CONFIRMED));
    assertFalse(flagOnly.restartCountPresent());
    assertTrue(flagOnly.rateLimitPresent());
    assertEquals(Severity.CRITICAL, flagOnly.event().orElseThrow().severity());
  }

  @Test
  void restartMon003MissingOrPartialNormalCannotBridgeFiveMinuteRecovery() {
    var owner = owner();
    var first = sample(owner, 1, false, 0).event().orElseThrow();
    sample(owner, 0, false, 1);
    assertSame(
        first,
        owner
            .observe(
                OptionalLong.empty(), Optional.empty(), true, at(180, CauseClearance.CONFIRMED))
            .event()
            .orElseThrow());
    assertSame(
        first,
        owner
            .observe(OptionalLong.of(0), Optional.empty(), true, at(181, CauseClearance.CONFIRMED))
            .event()
            .orElseThrow());
    assertSame(
        first,
        owner
            .observe(
                OptionalLong.empty(), Optional.of(false), true, at(182, CauseClearance.CONFIRMED))
            .event()
            .orElseThrow());
    sample(owner, 0, false, 200);
    assertTrue(sample(owner, 0, false, 499).event().orElseThrow().isOpen());
    var closed = sample(owner, 0, false, 500).event().orElseThrow();
    assertFalse(closed.isOpen());
    assertEquals(BigInteger.ONE, closed.count());
    assertEquals(OBSERVED_AT, closed.firstSeen());
    assertEquals(OBSERVED_AT, closed.lastSeen());
    assertTrue(owner.snapshot().isEmpty());
    assertTrue(first.isOpen());
  }

  @Test
  void restartMon004RateLimitCriticalNeedsTenMinutesAndCauseConfirmation() {
    var owner = owner();
    var first = sample(owner, 0, true, 0).event().orElseThrow();
    var lower = sample(owner, 1, false, 1).event().orElseThrow();
    assertEquals(Severity.CRITICAL, lower.severity());
    assertEquals(BigInteger.TWO, lower.count());
    assertEquals(BigInteger.ONE, first.count());
    sample(owner, 0, false, 2);
    assertTrue(
        owner
            .observe(
                OptionalLong.of(0), Optional.of(false), true, at(602, CauseClearance.UNCONFIRMED))
            .event()
            .orElseThrow()
            .isOpen());
    var closed = sample(owner, 0, false, 603).event().orElseThrow();
    assertFalse(closed.isOpen());
    assertEquals(Severity.CRITICAL, closed.severity());
    assertEquals(BigInteger.TWO, closed.count());
    assertEquals(OBSERVED_AT, closed.firstSeen());
    assertEquals(OBSERVED_AT.plusSeconds(1), closed.lastSeen());
    assertTrue(owner.snapshot().isEmpty());
  }

  @Test
  void restartMon005GapNullNegativeAndReversedTimeCannotFakeRecovery() {
    assertThrows(NullPointerException.class, () -> new RestartHealthMonitor(null));
    var owner = owner();
    var first = sample(owner, 1, false, 0).event().orElseThrow();
    sample(owner, 0, false, 1);
    assertThrows(
        NullPointerException.class,
        () -> owner.observe(null, Optional.empty(), true, at(2, CauseClearance.CONFIRMED)));
    assertThrows(
        NullPointerException.class,
        () -> owner.observe(OptionalLong.empty(), null, true, at(2, CauseClearance.CONFIRMED)));
    assertThrows(
        NullPointerException.class,
        () -> owner.observe(OptionalLong.empty(), Optional.empty(), true, null));
    for (long invalid : new long[] {-1, Long.MIN_VALUE})
      assertThrows(IllegalArgumentException.class, () -> sample(owner, invalid, true, 2));
    assertThrows(IllegalArgumentException.class, () -> sample(owner, 0, false, 0));
    assertSame(first, owner.snapshot().orElseThrow());
    owner.observe(OptionalLong.of(0), Optional.of(false), false, at(300, CauseClearance.CONFIRMED));
    assertTrue(sample(owner, 0, false, 599).event().orElseThrow().isOpen());
    assertFalse(sample(owner, 0, false, 600).event().orElseThrow().isOpen());
    assertTrue(owner.snapshot().isEmpty());
  }

  @Test
  void restartMon006ConcurrentSameOwnerAndDifferentOwnerKeepExactEvents() throws Exception {
    var owner = owner();
    var other = new RestartHealthMonitor(Service.API);
    var otherEvent = sample(other, 1, false, 0).event().orElseThrow();
    var tasks = new ArrayList<Callable<Boolean>>();
    for (int i = 0; i < 64; i++) {
      boolean limited = i % 2 == 0;
      tasks.add(() -> sample(owner, 1, limited, 0).event().orElseThrow().isOpen());
    }
    try (var pool = Executors.newFixedThreadPool(8)) {
      for (var result : pool.invokeAll(tasks)) assertTrue(result.get());
    }
    var last = owner.snapshot().orElseThrow();
    assertEquals(BigInteger.valueOf(64), last.count());
    assertEquals(Severity.CRITICAL, last.severity());
    assertEquals(Service.WEB, last.service());
    assertEquals(OBSERVED_AT, last.firstSeen());
    assertEquals(OBSERVED_AT, last.lastSeen());
    assertSame(otherEvent, other.snapshot().orElseThrow());
    assertEquals(Service.API, otherEvent.service());
    assertEquals(BigInteger.ONE, otherEvent.count());
    assertEquals(Severity.WARNING, otherEvent.severity());
  }

  @Test
  void restartMon007EveryClosedServicePreservesCountAndIndependentFlagIdentity() {
    for (var service : Service.values()) {
      var owner = new RestartHealthMonitor(service);
      assertTrue(sample(owner, 0, false, 0).event().isEmpty());
      var warning = sample(owner, 4, false, 1).event().orElseThrow();
      assertEquals(Severity.WARNING, warning.severity());
      assertEquals(service, warning.service());
      var critical = sample(owner, 0, true, 2).event().orElseThrow();
      assertEquals(Severity.CRITICAL, critical.severity());
      assertEquals(service, critical.service());
      assertEquals(Condition.RESTART, critical.condition());
      assertEquals(BigInteger.TWO, critical.count());
      assertEquals(OBSERVED_AT.plusSeconds(1), critical.firstSeen());
      assertEquals(OBSERVED_AT.plusSeconds(2), critical.lastSeen());
    }
  }

  @Test
  void restartMon008GeneratedEvaluationContractsUseIndependentBooleanAndIdentityOracles() {
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
    assertFalse(new Evaluation(false, true, Optional.empty()).restartCountPresent());
    assertFalse(new Evaluation(true, false, Optional.empty()).rateLimitPresent());
    var event = sample(owner(), 1, false, 0).event().orElseThrow();
    assertFalse(actual.equals(new Evaluation(true, true, Optional.of(event))));
    assertTrue(actual.restartCountPresent());
    assertTrue(actual.rateLimitPresent());
    assertEquals(Optional.empty(), actual.event());
    assertEquals(1221152, actual.hashCode());
    assertEquals(
        "Evaluation[restartCountPresent=true, rateLimitPresent=true, event=Optional.empty]",
        actual.toString());
    var populated = new Evaluation(true, true, Optional.of(event));
    assertSame(event, populated.event().orElseThrow());
    assertEquals(new Evaluation(true, true, Optional.of(event)), populated);
    assertEquals(1221152 + System.identityHashCode(event), populated.hashCode());
    assertEquals(
        "Evaluation[restartCountPresent=true, rateLimitPresent=true, event=Optional[dev.codex.schubert.nk.batch.monitoring.AlertLifecycle$Event@"
            + Integer.toHexString(System.identityHashCode(event))
            + "]]",
        populated.toString());
    assertThrows(NullPointerException.class, () -> new Evaluation(false, false, null));
  }
}
