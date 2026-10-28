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
import dev.codex.schubert.nk.batch.monitoring.WebLogBacklogMonitor.Evaluation;
import java.math.BigInteger;
import java.time.Duration;
import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.OptionalLong;
import java.util.concurrent.Callable;
import java.util.concurrent.Executors;
import org.junit.jupiter.api.Test;

/** WEBLOG001..008/1672: supplied scalar/elapsed fixtures only, no sampling/control operations. */
class WebLogBacklogMonitorTest {
  private static final Instant OBSERVED_AT = Instant.parse("2026-10-23T00:00:00Z");

  private static ObservationContext at(long seconds, CauseClearance cause) {
    return new ObservationContext(
        cause, OBSERVED_AT.plusSeconds(seconds), Duration.ofSeconds(seconds));
  }

  private static Evaluation sample(
      WebLogBacklogMonitor monitor, long queued, Duration oldest, long seconds) {
    return monitor.observe(
        OptionalLong.of(queued), Optional.of(oldest), true, at(seconds, CauseClearance.CONFIRMED));
  }

  @Test
  void webLog001KnownNormalAndMissingRemainDifferentWithoutInventedEvents() {
    var monitor = new WebLogBacklogMonitor();
    assertTrue(monitor.snapshot().isEmpty());
    var normal = sample(monitor, 4999, Duration.ofSeconds(299, 999999999), 0);
    assertTrue(normal.queuedPresent());
    assertTrue(normal.oldestPresent());
    assertTrue(normal.event().isEmpty());
    var missing =
        monitor.observe(
            OptionalLong.empty(), Optional.empty(), true, at(1, CauseClearance.CONFIRMED));
    assertFalse(missing.queuedPresent());
    assertFalse(missing.oldestPresent());
    assertTrue(missing.event().isEmpty());
    var onlyCount =
        monitor.observe(
            OptionalLong.of(0), Optional.empty(), true, at(2, CauseClearance.CONFIRMED));
    assertTrue(onlyCount.queuedPresent());
    assertFalse(onlyCount.oldestPresent());
    assertTrue(onlyCount.event().isEmpty());
    var onlyAge =
        monitor.observe(
            OptionalLong.empty(),
            Optional.of(Duration.ZERO),
            true,
            at(3, CauseClearance.CONFIRMED));
    assertFalse(onlyAge.queuedPresent());
    assertTrue(onlyAge.oldestPresent());
    assertTrue(onlyAge.event().isEmpty());
  }

  @Test
  void webLog002ExactCountAndAgeBoundariesRaiseWithEitherKnownAbnormalInput() {
    long[] counts = {4999, 5000, 8999, 9000, Long.MAX_VALUE};
    Severity[] countLevels = {
      Severity.NORMAL, Severity.WARNING, Severity.WARNING, Severity.CRITICAL, Severity.CRITICAL
    };
    for (int i = 0; i < counts.length; i++) {
      for (boolean ageKnown : List.of(false, true)) {
        var monitor = new WebLogBacklogMonitor();
        var result =
            monitor.observe(
                OptionalLong.of(counts[i]),
                ageKnown ? Optional.of(Duration.ZERO) : Optional.empty(),
                true,
                at(0, CauseClearance.CONFIRMED));
        assertTrue(result.queuedPresent());
        assertEquals(ageKnown, result.oldestPresent());
        if (countLevels[i] == Severity.NORMAL) assertTrue(result.event().isEmpty());
        else {
          var event = result.event().orElseThrow();
          assertEquals(countLevels[i], event.severity());
          assertEquals(Condition.WEB_LOG, event.condition());
          assertEquals(Service.WEB, event.service());
          assertEquals(BigInteger.ONE, event.count());
          assertEquals(OBSERVED_AT, event.firstSeen());
          assertEquals(OBSERVED_AT, event.lastSeen());
          assertTrue(event.isOpen());
        }
      }
    }
    Duration[] ages = {
      Duration.ofSeconds(299, 999999999),
      Duration.ofMinutes(5),
      Duration.ofSeconds(1799, 999999999),
      Duration.ofMinutes(30),
      Duration.ofSeconds(Long.MAX_VALUE, 999999999)
    };
    Severity[] ageLevels = {
      Severity.NORMAL, Severity.WARNING, Severity.WARNING, Severity.CRITICAL, Severity.CRITICAL
    };
    for (int i = 0; i < ages.length; i++) {
      for (boolean countKnown : List.of(false, true)) {
        var monitor = new WebLogBacklogMonitor();
        var result =
            monitor.observe(
                countKnown ? OptionalLong.of(0) : OptionalLong.empty(),
                Optional.of(ages[i]),
                true,
                at(0, CauseClearance.CONFIRMED));
        assertEquals(countKnown, result.queuedPresent());
        assertTrue(result.oldestPresent());
        if (ageLevels[i] == Severity.NORMAL) assertTrue(result.event().isEmpty());
        else assertEquals(ageLevels[i], result.event().orElseThrow().severity());
      }
    }
  }

  @Test
  void webLog003UnknownAndPartialLowEvidenceBreakNormalRecoveryWithoutClosing() {
    var monitor = new WebLogBacklogMonitor();
    var first = sample(monitor, 5000, Duration.ZERO, 0).event().orElseThrow();
    sample(monitor, 0, Duration.ZERO, 1);
    var absent =
        monitor.observe(
            OptionalLong.empty(), Optional.empty(), true, at(180, CauseClearance.CONFIRMED));
    assertSame(first, absent.event().orElseThrow());
    var countOnly =
        monitor.observe(
            OptionalLong.of(0), Optional.empty(), true, at(181, CauseClearance.CONFIRMED));
    assertSame(first, countOnly.event().orElseThrow());
    var ageOnly =
        monitor.observe(
            OptionalLong.empty(),
            Optional.of(Duration.ZERO),
            true,
            at(182, CauseClearance.CONFIRMED));
    assertSame(first, ageOnly.event().orElseThrow());
    sample(monitor, 0, Duration.ZERO, 200);
    assertTrue(sample(monitor, 0, Duration.ZERO, 499).event().orElseThrow().isOpen());
    var closed = sample(monitor, 0, Duration.ZERO, 500).event().orElseThrow();
    assertFalse(closed.isOpen());
    assertEquals(BigInteger.ONE, closed.count());
    assertEquals(OBSERVED_AT, closed.firstSeen());
    assertEquals(OBSERVED_AT, closed.lastSeen());
    assertTrue(monitor.snapshot().isEmpty());
    assertTrue(first.isOpen());
  }

  @Test
  void webLog004CriticalStaysStickyUntilTenNormalMinutesAndConfirmedCause() {
    var monitor = new WebLogBacklogMonitor();
    var first = sample(monitor, 9000, Duration.ZERO, 0).event().orElseThrow();
    var lower = sample(monitor, 5000, Duration.ZERO, 1).event().orElseThrow();
    assertEquals(Severity.CRITICAL, lower.severity());
    assertEquals(BigInteger.TWO, lower.count());
    assertEquals(BigInteger.ONE, first.count());
    sample(monitor, 0, Duration.ZERO, 2);
    var unconfirmed =
        monitor.observe(
            OptionalLong.of(0),
            Optional.of(Duration.ZERO),
            true,
            at(602, CauseClearance.UNCONFIRMED));
    assertTrue(unconfirmed.event().orElseThrow().isOpen());
    var closed = sample(monitor, 0, Duration.ZERO, 603).event().orElseThrow();
    assertFalse(closed.isOpen());
    assertEquals(Severity.CRITICAL, closed.severity());
    assertEquals(BigInteger.TWO, closed.count());
    assertEquals(OBSERVED_AT, closed.firstSeen());
    assertEquals(OBSERVED_AT.plusSeconds(1), closed.lastSeen());
    assertTrue(monitor.snapshot().isEmpty());
  }

  @Test
  void webLog005ExplicitGapCannotBridgeTheFiveMinuteNormalWindow() {
    var monitor = new WebLogBacklogMonitor();
    sample(monitor, 5000, Duration.ZERO, 0);
    sample(monitor, 0, Duration.ZERO, 1);
    monitor.observe(
        OptionalLong.of(0), Optional.of(Duration.ZERO), false, at(300, CauseClearance.CONFIRMED));
    assertTrue(sample(monitor, 0, Duration.ZERO, 599).event().orElseThrow().isOpen());
    assertFalse(sample(monitor, 0, Duration.ZERO, 600).event().orElseThrow().isOpen());
    assertTrue(monitor.snapshot().isEmpty());
  }

  @Test
  void webLog006InvalidInputsAndReversedElapsedCannotMutatePriorEvent() {
    var monitor = new WebLogBacklogMonitor();
    var first = sample(monitor, 5000, Duration.ZERO, 5).event().orElseThrow();
    assertThrows(
        NullPointerException.class,
        () -> monitor.observe(null, Optional.empty(), true, at(6, CauseClearance.CONFIRMED)));
    assertThrows(
        NullPointerException.class,
        () -> monitor.observe(OptionalLong.empty(), null, true, at(6, CauseClearance.CONFIRMED)));
    assertThrows(
        NullPointerException.class,
        () -> monitor.observe(OptionalLong.empty(), Optional.empty(), true, null));
    assertThrows(IllegalArgumentException.class, () -> sample(monitor, -1, Duration.ZERO, 6));
    assertThrows(IllegalArgumentException.class, () -> sample(monitor, 0, Duration.ofNanos(-1), 6));
    assertThrows(IllegalArgumentException.class, () -> sample(monitor, 0, Duration.ZERO, 4));
    assertSame(first, monitor.snapshot().orElseThrow());
    sample(monitor, 0, Duration.ZERO, 6);
    assertFalse(sample(monitor, 0, Duration.ZERO, 306).event().orElseThrow().isOpen());
    assertTrue(monitor.snapshot().isEmpty());
  }

  @Test
  void webLog007ConcurrentSameOwnerAndIndependentOwnerHaveExactCounts() throws Exception {
    var monitor = new WebLogBacklogMonitor();
    var other = new WebLogBacklogMonitor();
    var otherEvent = sample(other, 5000, Duration.ZERO, 0).event().orElseThrow();
    var tasks = new ArrayList<Callable<Boolean>>();
    for (int i = 0; i < 64; i++) {
      long count = i % 2 == 0 ? 5000 : 9000;
      tasks.add(
          () -> {
            var result = sample(monitor, count, Duration.ZERO, 0);
            return result.queuedPresent()
                && result.oldestPresent()
                && result.event().orElseThrow().isOpen();
          });
    }
    try (var pool = Executors.newFixedThreadPool(8)) {
      for (var result : pool.invokeAll(tasks)) assertTrue(result.get());
    }
    var finalEvent = monitor.snapshot().orElseThrow();
    assertEquals(BigInteger.valueOf(64), finalEvent.count());
    assertEquals(Severity.CRITICAL, finalEvent.severity());
    assertEquals(OBSERVED_AT, finalEvent.firstSeen());
    assertEquals(OBSERVED_AT, finalEvent.lastSeen());
    assertSame(otherEvent, other.snapshot().orElseThrow());
    assertEquals(BigInteger.ONE, otherEvent.count());
    assertEquals(Severity.WARNING, otherEvent.severity());
  }

  @Test
  void webLog008GeneratedEvaluationContractsHaveIndependentFieldAndPlatformOracles() {
    var actual = new Evaluation(true, true, Optional.empty());
    Object sameInstance = actual;
    Object absent = null;
    Object otherType = "not evaluation";
    assertTrue(actual.equals(sameInstance));
    assertTrue(actual.equals(new Evaluation(true, true, Optional.empty())));
    assertFalse(actual.equals(absent));
    assertFalse(actual.equals(otherType));
    assertFalse(actual.equals(new Evaluation(false, true, Optional.empty())));
    assertFalse(actual.equals(new Evaluation(true, false, Optional.empty())));
    assertFalse(new Evaluation(false, true, Optional.empty()).queuedPresent());
    assertFalse(new Evaluation(true, false, Optional.empty()).oldestPresent());
    var event = sample(new WebLogBacklogMonitor(), 5000, Duration.ZERO, 0).event().orElseThrow();
    assertFalse(actual.equals(new Evaluation(true, true, Optional.of(event))));
    assertTrue(actual.queuedPresent());
    assertTrue(actual.oldestPresent());
    assertEquals(Optional.empty(), actual.event());
    assertEquals(1221152, actual.hashCode());
    assertEquals(
        "Evaluation[queuedPresent=true, oldestPresent=true, event=Optional.empty]",
        actual.toString());
    var populated = new Evaluation(true, true, Optional.of(event));
    assertSame(event, populated.event().orElseThrow());
    assertTrue(populated.equals(new Evaluation(true, true, Optional.of(event))));
    assertEquals(1221152 + System.identityHashCode(event), populated.hashCode());
    assertEquals(
        "Evaluation[queuedPresent=true, oldestPresent=true, event=Optional[dev.codex.schubert.nk.batch.monitoring.AlertLifecycle$Event@"
            + Integer.toHexString(System.identityHashCode(event))
            + "]]",
        populated.toString());
    assertThrows(NullPointerException.class, () -> new Evaluation(false, false, null));
  }
}
