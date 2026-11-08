package dev.codex.schubert.nk.batch.monitoring;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.CauseClearance;
import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.Condition;
import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.Event;
import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.Service;
import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.Severity;
import java.math.BigInteger;
import java.time.Duration;
import java.time.Instant;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.concurrent.Callable;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Test;

/** Independent time/state vectors, PT-OPS-ALERT-001..010/spec1545. */
class AlertLifecycleTest {
  private static final Instant TIME = Instant.parse("2026-10-23T00:00:00Z");

  private static AlertLifecycle lifecycle() {
    return new AlertLifecycle(Condition.FILESYSTEM, Service.WEB);
  }

  private static Event signal(AlertLifecycle owner, Severity severity, Duration elapsed) {
    return owner.observe(severity, CauseClearance.UNCONFIRMED, TIME, elapsed).orElseThrow();
  }

  private static Event normal(AlertLifecycle owner, Duration elapsed, CauseClearance cause) {
    return owner.observe(Severity.NORMAL, cause, TIME.plusSeconds(100), elapsed).orElseThrow();
  }

  @Test
  void alert001InitialNormalAndFirstWarningIdentity() {
    var owner = lifecycle();
    assertTrue(owner.snapshot().isEmpty());
    assertTrue(
        owner.observe(Severity.NORMAL, CauseClearance.UNCONFIRMED, TIME, Duration.ZERO).isEmpty());
    Event event = signal(owner, Severity.WARNING, Duration.ZERO);
    assertEquals(Condition.FILESYSTEM, event.condition());
    assertEquals(Service.WEB, event.service());
    assertEquals(Severity.WARNING, event.severity());
    assertEquals(TIME, event.firstSeen());
    assertEquals(TIME, event.lastSeen());
    assertEquals(BigInteger.ONE, event.count());
    assertTrue(event.isOpen());
    assertEquals(event, owner.snapshot().orElseThrow());
  }

  @Test
  void alert002DedupEscalationAndNoAutomaticDowngrade() {
    var owner = lifecycle();
    var first = signal(owner, Severity.WARNING, Duration.ZERO);
    var second =
        owner
            .observe(
                Severity.WARNING,
                CauseClearance.UNCONFIRMED,
                TIME.plusSeconds(1),
                Duration.ofSeconds(1))
            .orElseThrow();
    assertEquals(BigInteger.TWO, second.count());
    assertEquals(TIME, second.firstSeen());
    assertEquals(TIME.plusSeconds(1), second.lastSeen());
    assertEquals(Severity.WARNING, second.severity());
    var third = signal(owner, Severity.CRITICAL, Duration.ofSeconds(2));
    assertEquals(BigInteger.valueOf(3), third.count());
    assertEquals(Severity.CRITICAL, third.severity());
    var fourth = signal(owner, Severity.WARNING, Duration.ofSeconds(3));
    assertEquals(BigInteger.valueOf(4), fourth.count());
    assertEquals(Severity.CRITICAL, fourth.severity());
    assertEquals(BigInteger.ONE, first.count());
    assertEquals(Severity.WARNING, first.severity());
  }

  @Test
  void alert003WarningFiveMinuteExactBoundary() {
    var owner = lifecycle();
    signal(owner, Severity.WARNING, Duration.ZERO);
    assertTrue(normal(owner, Duration.ZERO, CauseClearance.UNCONFIRMED).isOpen());
    assertTrue(
        normal(owner, Duration.ofSeconds(300).minusNanos(1), CauseClearance.UNCONFIRMED).isOpen());
    var closed = normal(owner, Duration.ofSeconds(300), CauseClearance.UNCONFIRMED);
    assertFalse(closed.isOpen());
    assertEquals(TIME, closed.firstSeen());
    assertEquals(TIME, closed.lastSeen());
    assertEquals(BigInteger.ONE, closed.count());
    assertTrue(owner.snapshot().isEmpty());
  }

  @Test
  void alert004CriticalNeedsTenMinutesAndCauseConfirmation() {
    var owner = lifecycle();
    signal(owner, Severity.CRITICAL, Duration.ZERO);
    assertTrue(normal(owner, Duration.ZERO, CauseClearance.CONFIRMED).isOpen());
    assertTrue(
        normal(owner, Duration.ofSeconds(600).minusNanos(1), CauseClearance.CONFIRMED).isOpen());
    assertTrue(normal(owner, Duration.ofSeconds(600), CauseClearance.UNCONFIRMED).isOpen());
    assertTrue(normal(owner, Duration.ofDays(1), CauseClearance.UNCONFIRMED).isOpen());
    assertFalse(normal(owner, Duration.ofDays(1), CauseClearance.CONFIRMED).isOpen());
  }

  @Test
  void alert005AnyViolationRestartsContinuousNormalPeriod() {
    for (var severity : new Severity[] {Severity.WARNING, Severity.CRITICAL}) {
      var owner = lifecycle();
      signal(owner, severity, Duration.ZERO);
      normal(owner, Duration.ZERO, CauseClearance.CONFIRMED);
      signal(owner, severity, Duration.ofSeconds(299));
      normal(owner, Duration.ofSeconds(300), CauseClearance.CONFIRMED);
      long required = severity == Severity.WARNING ? 300 : 600;
      assertTrue(
          normal(owner, Duration.ofSeconds(300 + required).minusNanos(1), CauseClearance.CONFIRMED)
              .isOpen());
      var closed = normal(owner, Duration.ofSeconds(300 + required), CauseClearance.CONFIRMED);
      assertFalse(closed.isOpen());
      assertEquals(BigInteger.TWO, closed.count());
    }
  }

  @Test
  void alert006ClosedEventRetiredAndNewViolationStartsFresh() {
    var owner = lifecycle();
    var historical = signal(owner, Severity.WARNING, Duration.ZERO);
    normal(owner, Duration.ZERO, CauseClearance.UNCONFIRMED);
    assertFalse(normal(owner, Duration.ofMinutes(5), CauseClearance.UNCONFIRMED).isOpen());
    assertTrue(
        owner
            .observe(Severity.NORMAL, CauseClearance.UNCONFIRMED, TIME, Duration.ofMinutes(6))
            .isEmpty());
    var nextTime = TIME.plusSeconds(1000);
    var next =
        owner
            .observe(Severity.WARNING, CauseClearance.UNCONFIRMED, nextTime, Duration.ofMinutes(7))
            .orElseThrow();
    assertEquals(nextTime, next.firstSeen());
    assertEquals(nextTime, next.lastSeen());
    assertEquals(BigInteger.ONE, next.count());
    assertTrue(historical.isOpen());
    assertEquals(TIME, historical.firstSeen());
  }

  @Test
  void alert007NullAndInvalidElapsedLeaveStateUnchanged() {
    assertThrows(NullPointerException.class, () -> new AlertLifecycle(null, Service.WEB));
    assertThrows(NullPointerException.class, () -> new AlertLifecycle(Condition.FILESYSTEM, null));
    var owner = lifecycle();
    assertThrows(
        IllegalArgumentException.class,
        () -> signal(owner, Severity.WARNING, Duration.ofNanos(-1)));
    assertTrue(owner.snapshot().isEmpty());
    var before = signal(owner, Severity.WARNING, Duration.ofSeconds(1));
    assertThrows(
        NullPointerException.class,
        () -> owner.observe(null, CauseClearance.UNCONFIRMED, TIME, Duration.ZERO));
    assertThrows(
        NullPointerException.class,
        () -> owner.observe(Severity.WARNING, null, TIME, Duration.ZERO));
    assertThrows(
        NullPointerException.class,
        () -> owner.observe(Severity.WARNING, CauseClearance.UNCONFIRMED, null, Duration.ZERO));
    assertThrows(
        NullPointerException.class,
        () -> owner.observe(Severity.WARNING, CauseClearance.UNCONFIRMED, TIME, null));
    assertEquals(
        "invalid alert elapsed time",
        assertThrows(
                IllegalArgumentException.class,
                () -> signal(owner, Severity.WARNING, Duration.ZERO))
            .getMessage());
    assertEquals(before, owner.snapshot().orElseThrow());
    assertEquals(BigInteger.TWO, signal(owner, Severity.WARNING, Duration.ofSeconds(1)).count());
  }

  @Test
  void alert008WallClockJumpDoesNotShortenRecoveryOrOverflow() {
    var owner = lifecycle();
    signal(owner, Severity.WARNING, Duration.ZERO);
    assertTrue(
        owner
            .observe(Severity.NORMAL, CauseClearance.UNCONFIRMED, Instant.MAX, Duration.ZERO)
            .orElseThrow()
            .isOpen());
    assertTrue(
        owner
            .observe(Severity.NORMAL, CauseClearance.UNCONFIRMED, Instant.MIN, Duration.ofNanos(1))
            .orElseThrow()
            .isOpen());
    assertFalse(
        owner
            .observe(Severity.NORMAL, CauseClearance.UNCONFIRMED, TIME, Duration.ofSeconds(300))
            .orElseThrow()
            .isOpen());
    var critical = lifecycle();
    signal(critical, Severity.CRITICAL, Duration.ZERO);
    normal(critical, Duration.ZERO, CauseClearance.CONFIRMED);
    assertFalse(
        normal(critical, Duration.ofSeconds(Long.MAX_VALUE, 999_999_999), CauseClearance.CONFIRMED)
            .isOpen());
  }

  @Test
  void alert009ConcurrentSameTickCountsAndPrivateMonitor() throws Exception {
    var owner = lifecycle();
    signal(owner, Severity.WARNING, Duration.ZERO);
    var executor = Executors.newFixedThreadPool(4);
    try {
      var tasks = new ArrayList<Callable<BigInteger>>();
      for (int index = 0; index < 64; index++)
        tasks.add(() -> signal(owner, Severity.WARNING, Duration.ofSeconds(1)).count());
      var counts = new HashSet<BigInteger>();
      synchronized (owner) {
        for (var future : executor.invokeAll(tasks, 10, TimeUnit.SECONDS)) counts.add(future.get());
      }
      var expected = new HashSet<BigInteger>();
      for (int value = 2; value <= 65; value++) expected.add(BigInteger.valueOf(value));
      assertEquals(expected, counts);
      assertEquals(BigInteger.valueOf(65), owner.snapshot().orElseThrow().count());
      assertEquals(TIME, owner.snapshot().orElseThrow().firstSeen());
    } finally {
      executor.shutdownNow();
      assertTrue(executor.awaitTermination(10, TimeUnit.SECONDS));
    }
  }

  @Test
  void alert010AllClosedConditionServiceIdentities() {
    assertEquals(12, Condition.values().length);
    assertEquals(6, Service.values().length);
    for (var condition : Condition.values()) {
      for (var service : Service.values()) {
        var event = signal(new AlertLifecycle(condition, service), Severity.WARNING, Duration.ZERO);
        assertEquals(condition, event.condition());
        assertEquals(service, event.service());
      }
    }
  }

  @Test
  void protectedAlert001AllKeysHonorNoAutomaticCloseDespiteConfirmedCause() {
    for (var condition : Condition.values()) {
      for (var service : Service.values()) {
        for (var level : new Severity[] {Severity.WARNING, Severity.CRITICAL}) {
          for (var clearance : CauseClearance.values()) {
            var owner = new AlertLifecycle(condition, service);
            var first = signal(owner, level, Duration.ZERO);
            normal(owner, Duration.ofSeconds(1), clearance);
            var result = normal(owner, Duration.ofDays(1), clearance);
            boolean protectedKey =
                condition == Condition.DLQ || condition == Condition.INTEGRITY_CONFIG;
            boolean staysOpen =
                protectedKey
                    || (level == Severity.CRITICAL && clearance == CauseClearance.UNCONFIRMED);
            assertEquals(staysOpen, result.isOpen());
            assertEquals(condition, result.condition());
            assertEquals(service, result.service());
            assertEquals(level, result.severity());
            assertEquals(BigInteger.ONE, result.count());
            assertEquals(TIME, result.firstSeen());
            assertEquals(TIME, result.lastSeen());
            if (protectedKey) assertSame(first, owner.snapshot().orElseThrow());
            else assertEquals(staysOpen, owner.snapshot().isPresent());
          }
        }
      }
    }
  }

  @Test
  void protectedAlert002ConcurrentNormalSamplesCannotRetireOrChangeProtectedEvent()
      throws Exception {
    for (var condition : new Condition[] {Condition.DLQ, Condition.INTEGRITY_CONFIG}) {
      var owner = new AlertLifecycle(condition, Service.BROKER);
      var first = signal(owner, Severity.CRITICAL, Duration.ZERO);
      var tasks = new ArrayList<Callable<Event>>();
      for (int i = 0; i < 64; i++) {
        var cause = i % 2 == 0 ? CauseClearance.CONFIRMED : CauseClearance.UNCONFIRMED;
        tasks.add(() -> normal(owner, Duration.ofSeconds(Long.MAX_VALUE, 999_999_999), cause));
      }
      var executor = Executors.newFixedThreadPool(8);
      try {
        for (var result : executor.invokeAll(tasks, 10, TimeUnit.SECONDS))
          assertSame(first, result.get());
      } finally {
        executor.shutdownNow();
        assertTrue(executor.awaitTermination(10, TimeUnit.SECONDS));
      }
      assertSame(first, owner.snapshot().orElseThrow());
      assertTrue(first.isOpen());
      assertEquals(BigInteger.ONE, first.count());
      assertEquals(TIME, first.firstSeen());
      assertEquals(TIME, first.lastSeen());
    }
  }
}
