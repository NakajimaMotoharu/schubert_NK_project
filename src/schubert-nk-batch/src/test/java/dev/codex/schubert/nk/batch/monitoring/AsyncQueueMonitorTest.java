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
import dev.codex.schubert.nk.batch.monitoring.AsyncQueueMonitor.Evaluation;
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
 * ASYNCQUEUE001..008/1674: supplied scalar/elapsed fixtures only, no sampling/control operations.
 */
class AsyncQueueMonitorTest {
  private static final Instant AT = Instant.parse("2026-10-23T00:00:00Z");

  private static ObservationContext at(long seconds, CauseClearance cause) {
    return new ObservationContext(cause, AT.plusSeconds(seconds), Duration.ofSeconds(seconds));
  }

  private static Evaluation sample(
      AsyncQueueMonitor monitor, long queued, long capacity, long seconds) {
    return monitor.observe(
        OptionalLong.of(queued),
        OptionalLong.of(capacity),
        true,
        at(seconds, CauseClearance.CONFIRMED));
  }

  @Test
  void asyncQueue001KnownNormalAndMissingRemainDifferentWithoutInventedEvents() {
    var monitor = new AsyncQueueMonitor();
    assertTrue(monitor.snapshot().isEmpty());
    var normal = sample(monitor, 4999, 100000, 0);
    assertTrue(normal.queuedPresent());
    assertTrue(normal.capacityPresent());
    assertTrue(normal.event().isEmpty());
    var missing =
        monitor.observe(
            OptionalLong.empty(), OptionalLong.empty(), true, at(1, CauseClearance.CONFIRMED));
    assertFalse(missing.queuedPresent());
    assertFalse(missing.capacityPresent());
    assertTrue(missing.event().isEmpty());
    var onlyCount =
        monitor.observe(
            OptionalLong.of(0), OptionalLong.empty(), true, at(2, CauseClearance.CONFIRMED));
    assertTrue(onlyCount.queuedPresent());
    assertFalse(onlyCount.capacityPresent());
    assertTrue(onlyCount.event().isEmpty());
    var onlyAge =
        monitor.observe(
            OptionalLong.empty(), OptionalLong.of(100000), true, at(3, CauseClearance.CONFIRMED));
    assertFalse(onlyAge.queuedPresent());
    assertTrue(onlyAge.capacityPresent());
    assertTrue(onlyAge.event().isEmpty());
  }

  @Test
  void asyncQueue002ExactAbsoluteAndRatioBoundariesUseIndependentGoldenValues() {
    long[][] vectors = {
      {0, 1},
      {69, 100},
      {70, 100},
      {89, 100},
      {90, 100},
      {699, 1000},
      {700, 1000},
      {899, 1000},
      {900, 1000},
      {7, 10},
      {9, 10},
      {1, 1},
      {4999, 100000},
      {5000, 100000},
      {8999, 100000},
      {9000, 100000},
      {5000, Long.MAX_VALUE},
      {9000, Long.MAX_VALUE},
      {Long.MAX_VALUE, Long.MAX_VALUE}
    };
    Severity[] expected = {
      Severity.NORMAL,
      Severity.NORMAL,
      Severity.WARNING,
      Severity.WARNING,
      Severity.CRITICAL,
      Severity.NORMAL,
      Severity.WARNING,
      Severity.WARNING,
      Severity.CRITICAL,
      Severity.WARNING,
      Severity.CRITICAL,
      Severity.CRITICAL,
      Severity.NORMAL,
      Severity.WARNING,
      Severity.WARNING,
      Severity.CRITICAL,
      Severity.WARNING,
      Severity.CRITICAL,
      Severity.CRITICAL
    };
    for (int i = 0; i < vectors.length; i++) {
      var monitor = new AsyncQueueMonitor();
      var result = sample(monitor, vectors[i][0], vectors[i][1], 0);
      assertTrue(result.queuedPresent());
      assertTrue(result.capacityPresent());
      if (expected[i] == Severity.NORMAL) assertTrue(result.event().isEmpty());
      else {
        var event = result.event().orElseThrow();
        assertEquals(expected[i], event.severity());
        assertEquals(Condition.ASYNC_QUEUE, event.condition());
        assertEquals(Service.API, event.service());
        assertEquals(BigInteger.ONE, event.count());
        assertEquals(AT, event.firstSeen());
        assertEquals(AT, event.lastSeen());
        assertTrue(event.isOpen());
      }
    }
    long[] counts = {4999, 5000, 9000, Long.MAX_VALUE};
    Severity[] partial = {Severity.NORMAL, Severity.WARNING, Severity.CRITICAL, Severity.CRITICAL};
    for (int i = 0; i < counts.length; i++) {
      var result =
          new AsyncQueueMonitor()
              .observe(
                  OptionalLong.of(counts[i]),
                  OptionalLong.empty(),
                  true,
                  at(0, CauseClearance.CONFIRMED));
      assertTrue(result.queuedPresent());
      assertFalse(result.capacityPresent());
      if (partial[i] == Severity.NORMAL) assertTrue(result.event().isEmpty());
      else assertEquals(partial[i], result.event().orElseThrow().severity());
    }
    for (long capacity : new long[] {1, 100, Long.MAX_VALUE}) {
      var result =
          new AsyncQueueMonitor()
              .observe(
                  OptionalLong.empty(),
                  OptionalLong.of(capacity),
                  true,
                  at(0, CauseClearance.CONFIRMED));
      assertFalse(result.queuedPresent());
      assertTrue(result.capacityPresent());
      assertTrue(result.event().isEmpty());
    }
  }

  @Test
  void asyncQueue003UnknownAndPartialLowEvidenceBreakNormalRecoveryWithoutClosing() {
    var monitor = new AsyncQueueMonitor();
    var first = sample(monitor, 5000, 100000, 0).event().orElseThrow();
    sample(monitor, 0, 100000, 1);
    var absent =
        monitor.observe(
            OptionalLong.empty(), OptionalLong.empty(), true, at(180, CauseClearance.CONFIRMED));
    assertSame(first, absent.event().orElseThrow());
    var countOnly =
        monitor.observe(
            OptionalLong.of(0), OptionalLong.empty(), true, at(181, CauseClearance.CONFIRMED));
    assertSame(first, countOnly.event().orElseThrow());
    var ageOnly =
        monitor.observe(
            OptionalLong.empty(), OptionalLong.of(100000), true, at(182, CauseClearance.CONFIRMED));
    assertSame(first, ageOnly.event().orElseThrow());
    sample(monitor, 0, 100000, 200);
    assertTrue(sample(monitor, 0, 100000, 499).event().orElseThrow().isOpen());
    var closed = sample(monitor, 0, 100000, 500).event().orElseThrow();
    assertFalse(closed.isOpen());
    assertEquals(BigInteger.ONE, closed.count());
    assertEquals(AT, closed.firstSeen());
    assertEquals(AT, closed.lastSeen());
    assertTrue(monitor.snapshot().isEmpty());
    assertTrue(first.isOpen());
  }

  @Test
  void asyncQueue004CriticalStaysStickyUntilTenNormalMinutesAndConfirmedCause() {
    var monitor = new AsyncQueueMonitor();
    var first = sample(monitor, 9000, 100000, 0).event().orElseThrow();
    var lower = sample(monitor, 5000, 100000, 1).event().orElseThrow();
    assertEquals(Severity.CRITICAL, lower.severity());
    assertEquals(BigInteger.TWO, lower.count());
    assertEquals(BigInteger.ONE, first.count());
    sample(monitor, 0, 100000, 2);
    var unconfirmed =
        monitor.observe(
            OptionalLong.of(0), OptionalLong.of(100000), true, at(602, CauseClearance.UNCONFIRMED));
    assertTrue(unconfirmed.event().orElseThrow().isOpen());
    var closed = sample(monitor, 0, 100000, 603).event().orElseThrow();
    assertFalse(closed.isOpen());
    assertEquals(Severity.CRITICAL, closed.severity());
    assertEquals(BigInteger.TWO, closed.count());
    assertEquals(AT, closed.firstSeen());
    assertEquals(AT.plusSeconds(1), closed.lastSeen());
    assertTrue(monitor.snapshot().isEmpty());
  }

  @Test
  void asyncQueue005ExplicitGapCannotBridgeTheFiveMinuteNormalWindow() {
    var monitor = new AsyncQueueMonitor();
    sample(monitor, 5000, 100000, 0);
    sample(monitor, 0, 100000, 1);
    monitor.observe(
        OptionalLong.of(0), OptionalLong.of(100000), false, at(300, CauseClearance.CONFIRMED));
    assertTrue(sample(monitor, 0, 100000, 599).event().orElseThrow().isOpen());
    assertFalse(sample(monitor, 0, 100000, 600).event().orElseThrow().isOpen());
    assertTrue(monitor.snapshot().isEmpty());
  }

  @Test
  void asyncQueue006InvalidInputsAndReversedElapsedCannotMutatePriorEvent() {
    var monitor = new AsyncQueueMonitor();
    var first = sample(monitor, 5000, 100000, 5).event().orElseThrow();
    assertThrows(
        NullPointerException.class,
        () -> monitor.observe(null, OptionalLong.empty(), true, at(6, CauseClearance.CONFIRMED)));
    assertThrows(
        NullPointerException.class,
        () -> monitor.observe(OptionalLong.empty(), null, true, at(6, CauseClearance.CONFIRMED)));
    assertThrows(
        NullPointerException.class,
        () -> monitor.observe(OptionalLong.empty(), OptionalLong.empty(), true, null));
    assertThrows(IllegalArgumentException.class, () -> sample(monitor, -1, 100000, 6));
    assertThrows(IllegalArgumentException.class, () -> sample(monitor, 0, -1, 6));
    assertThrows(IllegalArgumentException.class, () -> sample(monitor, 0, 100000, 4));
    assertThrows(IllegalArgumentException.class, () -> sample(monitor, 0, 0, 6));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            monitor.observe(
                OptionalLong.empty(), OptionalLong.of(0), true, at(6, CauseClearance.CONFIRMED)));
    assertSame(first, monitor.snapshot().orElseThrow());
    sample(monitor, 0, 100000, 6);
    assertFalse(sample(monitor, 0, 100000, 306).event().orElseThrow().isOpen());
    assertTrue(monitor.snapshot().isEmpty());
  }

  @Test
  void asyncQueue007ConcurrentSameOwnerAndIndependentOwnerHaveExactCounts() throws Exception {
    var monitor = new AsyncQueueMonitor();
    var other = new AsyncQueueMonitor();
    var otherEvent = sample(other, 5000, 100000, 0).event().orElseThrow();
    var tasks = new ArrayList<Callable<Boolean>>();
    for (int i = 0; i < 64; i++) {
      long count = i % 2 == 0 ? 5000 : 9000;
      tasks.add(
          () -> {
            var result = sample(monitor, count, 100000, 0);
            return result.queuedPresent()
                && result.capacityPresent()
                && result.event().orElseThrow().isOpen();
          });
    }
    try (var pool = Executors.newFixedThreadPool(8)) {
      for (var result : pool.invokeAll(tasks)) assertTrue(result.get());
    }
    var finalEvent = monitor.snapshot().orElseThrow();
    assertEquals(BigInteger.valueOf(64), finalEvent.count());
    assertEquals(Severity.CRITICAL, finalEvent.severity());
    assertEquals(AT, finalEvent.firstSeen());
    assertEquals(AT, finalEvent.lastSeen());
    assertSame(otherEvent, other.snapshot().orElseThrow());
    assertEquals(BigInteger.ONE, otherEvent.count());
    assertEquals(Severity.WARNING, otherEvent.severity());
  }

  @Test
  void asyncQueue008GeneratedEvaluationContractsHaveIndependentFieldAndPlatformOracles() {
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
    assertFalse(new Evaluation(true, false, Optional.empty()).capacityPresent());
    var event = sample(new AsyncQueueMonitor(), 5000, 100000, 0).event().orElseThrow();
    assertFalse(actual.equals(new Evaluation(true, true, Optional.of(event))));
    assertTrue(actual.queuedPresent());
    assertTrue(actual.capacityPresent());
    assertEquals(Optional.empty(), actual.event());
    assertEquals(1221152, actual.hashCode());
    assertEquals(
        "Evaluation[queuedPresent=true, capacityPresent=true, event=Optional.empty]",
        actual.toString());
    var populated = new Evaluation(true, true, Optional.of(event));
    assertSame(event, populated.event().orElseThrow());
    assertTrue(populated.equals(new Evaluation(true, true, Optional.of(event))));
    assertEquals(1221152 + System.identityHashCode(event), populated.hashCode());
    assertEquals(
        "Evaluation[queuedPresent=true, capacityPresent=true, event=Optional[dev.codex.schubert.nk.batch.monitoring.AlertLifecycle$Event@"
            + Integer.toHexString(System.identityHashCode(event))
            + "]]",
        populated.toString());
    assertThrows(NullPointerException.class, () -> new Evaluation(false, false, null));
  }
}
