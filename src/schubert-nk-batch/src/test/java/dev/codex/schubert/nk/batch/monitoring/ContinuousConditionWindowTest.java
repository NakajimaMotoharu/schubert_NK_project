package dev.codex.schubert.nk.batch.monitoring;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.Severity;
import dev.codex.schubert.nk.batch.monitoring.ContinuousConditionWindow.State;
import java.time.Duration;
import java.util.ArrayList;
import java.util.concurrent.Callable;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Test;

/** Fixed independent elapsed differences/severity, no real clock or target. Spec1561. */
class ContinuousConditionWindowTest {
  private final ContinuousConditionWindow window = new ContinuousConditionWindow();

  @Test
  void monWindow001FirstContinuousAndSameTimestampBoundaries() {
    assertEquals(
        Duration.ZERO, window.observe(State.VIOLATING, Duration.ofSeconds(10), true).orElseThrow());
    assertEquals(
        Duration.ofSeconds(299, 999_999_999),
        window.observe(State.VIOLATING, Duration.ofSeconds(309, 999_999_999), true).orElseThrow());
    assertEquals(
        Duration.ofMinutes(5),
        window.observe(State.VIOLATING, Duration.ofSeconds(310), true).orElseThrow());
    assertEquals(
        Duration.ofMinutes(5),
        window.observe(State.VIOLATING, Duration.ofSeconds(310), true).orElseThrow());
  }

  @Test
  void monWindow002NormalBreaksViolationHistory() {
    assertEquals(Duration.ZERO, window.observe(State.NORMAL, Duration.ZERO, true).orElseThrow());
    assertEquals(
        Duration.ZERO, window.observe(State.VIOLATING, Duration.ofSeconds(1), false).orElseThrow());
    assertEquals(
        Duration.ofSeconds(4),
        window.observe(State.VIOLATING, Duration.ofSeconds(5), true).orElseThrow());
    assertEquals(
        Duration.ZERO, window.observe(State.NORMAL, Duration.ofSeconds(6), true).orElseThrow());
    assertEquals(
        Duration.ZERO, window.observe(State.VIOLATING, Duration.ofSeconds(7), true).orElseThrow());
  }

  @Test
  void monWindow003UnknownIsAbsentAndBreaksHistory() {
    assertTrue(window.observe(State.UNKNOWN, Duration.ZERO, true).isEmpty());
    assertEquals(
        Duration.ZERO, window.observe(State.VIOLATING, Duration.ofSeconds(1), true).orElseThrow());
    assertEquals(
        Duration.ofSeconds(4),
        window.observe(State.VIOLATING, Duration.ofSeconds(5), true).orElseThrow());
    assertTrue(window.observe(State.UNKNOWN, Duration.ofSeconds(6), true).isEmpty());
    assertEquals(
        Duration.ZERO,
        window.observe(State.VIOLATING, Duration.ofSeconds(100), true).orElseThrow());
    assertEquals(
        Duration.ZERO, window.observe(State.NORMAL, Duration.ofSeconds(101), true).orElseThrow());
  }

  @Test
  void monWindow004ExplicitGapNeverBridgesOldPeriod() {
    assertEquals(
        Duration.ZERO, window.observe(State.VIOLATING, Duration.ZERO, false).orElseThrow());
    assertEquals(
        Duration.ofSeconds(5),
        window.observe(State.VIOLATING, Duration.ofSeconds(5), true).orElseThrow());
    assertEquals(
        Duration.ZERO,
        window.observe(State.VIOLATING, Duration.ofSeconds(100), false).orElseThrow());
    assertEquals(
        Duration.ofSeconds(1),
        window.observe(State.VIOLATING, Duration.ofSeconds(101), true).orElseThrow());
    assertEquals(
        Duration.ZERO, window.observe(State.NORMAL, Duration.ofSeconds(102), false).orElseThrow());
    assertTrue(window.observe(State.UNKNOWN, Duration.ofSeconds(103), false).isEmpty());
  }

  @Test
  void monWindow005RejectedSequenceLeavesStateUnchanged() {
    assertThrows(NullPointerException.class, () -> window.observe(null, Duration.ZERO, true));
    assertThrows(NullPointerException.class, () -> window.observe(State.NORMAL, null, true));
    assertEquals(
        "invalid observation sequence",
        assertThrows(
                IllegalArgumentException.class,
                () -> window.observe(State.NORMAL, Duration.ofNanos(-1), true))
            .getMessage());
    assertEquals(
        Duration.ZERO, window.observe(State.VIOLATING, Duration.ofSeconds(2), true).orElseThrow());
    assertThrows(
        IllegalArgumentException.class,
        () -> window.observe(State.UNKNOWN, Duration.ofSeconds(1), true));
    assertThrows(
        NullPointerException.class, () -> window.observe(null, Duration.ofSeconds(99), false));
    assertEquals(
        Duration.ofSeconds(1),
        window.observe(State.VIOLATING, Duration.ofSeconds(3), true).orElseThrow());
    assertThrows(
        IllegalArgumentException.class,
        () -> window.observe(State.VIOLATING, Duration.ofSeconds(-1), false));
    assertEquals(
        Duration.ofSeconds(2),
        window.observe(State.VIOLATING, Duration.ofSeconds(4), true).orElseThrow());
  }

  @Test
  void monWindow006WholeNonnegativeDurationDomain() {
    Duration maximum = Duration.ofSeconds(Long.MAX_VALUE, 999_999_999);
    var atMaximum = new ContinuousConditionWindow();
    assertEquals(Duration.ZERO, atMaximum.observe(State.VIOLATING, maximum, true).orElseThrow());
    assertEquals(Duration.ZERO, atMaximum.observe(State.VIOLATING, maximum, true).orElseThrow());
    assertEquals(Duration.ZERO, window.observe(State.VIOLATING, Duration.ZERO, true).orElseThrow());
    assertEquals(
        Duration.ofNanos(1),
        window.observe(State.VIOLATING, Duration.ofNanos(1), true).orElseThrow());
    assertEquals(
        Duration.ofSeconds(59, 999_999_999),
        window.observe(State.VIOLATING, Duration.ofSeconds(59, 999_999_999), true).orElseThrow());
    assertEquals(
        Duration.ofMinutes(1),
        window.observe(State.VIOLATING, Duration.ofMinutes(1), true).orElseThrow());
    assertEquals(maximum, window.observe(State.VIOLATING, maximum, true).orElseThrow());
  }

  @Test
  void monWindow007ConcurrentSamePointHasOneOrigin() throws Exception {
    var executor = Executors.newFixedThreadPool(4);
    try {
      var tasks = new ArrayList<Callable<Duration>>();
      for (int index = 0; index < 64; index++)
        tasks.add(
            () -> window.observe(State.VIOLATING, Duration.ofSeconds(100), true).orElseThrow());
      for (var future : executor.invokeAll(tasks, 10, TimeUnit.SECONDS))
        assertEquals(Duration.ZERO, future.get());
      assertEquals(
          Duration.ofSeconds(1),
          window.observe(State.VIOLATING, Duration.ofSeconds(101), true).orElseThrow());
    } finally {
      executor.shutdownNow();
      assertTrue(executor.awaitTermination(10, TimeUnit.SECONDS));
    }
  }

  @Test
  void monWindow008SeparateThresholdPeriodsConnectWithoutActualObservations() {
    var warning = new ContinuousConditionWindow();
    var critical = new ContinuousConditionWindow();
    var threshold = new AlertThresholds();
    assertEquals(
        Severity.NORMAL,
        threshold.filesystem(
            90,
            warning.observe(State.VIOLATING, Duration.ZERO, false).orElseThrow(),
            critical.observe(State.VIOLATING, Duration.ZERO, false).orElseThrow()));
    assertEquals(
        Severity.NORMAL,
        threshold.filesystem(
            90,
            warning
                .observe(State.VIOLATING, Duration.ofSeconds(59, 999_999_999), true)
                .orElseThrow(),
            critical
                .observe(State.VIOLATING, Duration.ofSeconds(59, 999_999_999), true)
                .orElseThrow()));
    assertEquals(
        Severity.CRITICAL,
        threshold.filesystem(
            90,
            warning.observe(State.VIOLATING, Duration.ofSeconds(60), true).orElseThrow(),
            critical.observe(State.VIOLATING, Duration.ofSeconds(60), true).orElseThrow()));
    assertEquals(
        Severity.WARNING,
        threshold.filesystem(
            80,
            warning.observe(State.VIOLATING, Duration.ofSeconds(300), true).orElseThrow(),
            critical.observe(State.NORMAL, Duration.ofSeconds(300), true).orElseThrow()));
    assertTrue(warning.observe(State.UNKNOWN, Duration.ofSeconds(301), true).isEmpty());
    assertEquals(
        Severity.NORMAL,
        threshold.filesystem(
            80,
            warning.observe(State.VIOLATING, Duration.ofSeconds(600), true).orElseThrow(),
            Duration.ZERO));
  }
}
