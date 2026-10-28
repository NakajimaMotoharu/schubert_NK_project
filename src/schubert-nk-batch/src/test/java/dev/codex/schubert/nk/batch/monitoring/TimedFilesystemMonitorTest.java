package dev.codex.schubert.nk.batch.monitoring;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.CauseClearance;
import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.Service;
import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.Severity;
import java.math.BigInteger;
import java.time.Duration;
import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.OptionalDouble;
import java.util.concurrent.Callable;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Test;

/** One finite pure sample-to-local-status path, independent literals. Spec1563/TIMEDFS001..006. */
class TimedFilesystemMonitorTest {
  private final TimedFilesystemMonitor monitor = new TimedFilesystemMonitor(Service.WEB);
  private static final Instant AT = Instant.parse("2026-10-23T00:00:00Z");

  private static ObservationContext context(Duration elapsed, CauseClearance cause) {
    return new ObservationContext(cause, AT.plusSeconds(elapsed.getSeconds()), elapsed);
  }

  private TimedFilesystemMonitor.Evaluation sample(
      double value, long seconds, boolean consecutive) {
    return monitor.observe(
        OptionalDouble.of(value),
        consecutive,
        context(Duration.ofSeconds(seconds), CauseClearance.UNCONFIRMED));
  }

  @Test
  void timedFs001WarningBoundaryAndFiveMinuteRecovery() {
    assertTrue(monitor.snapshot().isEmpty());
    assertTrue(sample(80, 0, false).event().isEmpty());
    assertTrue(
        monitor
            .observe(
                OptionalDouble.of(80),
                true,
                context(Duration.ofSeconds(299, 999_999_999), CauseClearance.UNCONFIRMED))
            .event()
            .isEmpty());
    var warning = sample(80, 300, true);
    assertTrue(warning.suppliedValuePresent());
    assertEquals(Severity.WARNING, warning.event().orElseThrow().severity());
    assertEquals(Service.WEB, warning.event().orElseThrow().service());
    assertEquals(BigInteger.ONE, warning.event().orElseThrow().count());
    assertEquals(AT.plusSeconds(300), warning.event().orElseThrow().firstSeen());
    assertTrue(sample(0, 301, true).event().orElseThrow().isOpen());
    assertTrue(sample(0, 600, true).event().orElseThrow().isOpen());
    assertFalse(sample(0, 601, true).event().orElseThrow().isOpen());
    assertTrue(monitor.snapshot().isEmpty());
  }

  @Test
  void timedFs002CriticalBoundaryAndExplicitCause() {
    assertTrue(sample(90, 0, true).event().isEmpty());
    assertTrue(
        monitor
            .observe(
                OptionalDouble.of(90),
                true,
                context(Duration.ofSeconds(59, 999_999_999), CauseClearance.UNCONFIRMED))
            .event()
            .isEmpty());
    assertEquals(Severity.CRITICAL, sample(90, 60, true).event().orElseThrow().severity());
    assertTrue(sample(0, 61, true).event().orElseThrow().isOpen());
    assertTrue(sample(0, 661, true).event().orElseThrow().isOpen());
    var closed =
        monitor.observe(
            OptionalDouble.of(0), true, context(Duration.ofSeconds(661), CauseClearance.CONFIRMED));
    assertFalse(closed.event().orElseThrow().isOpen());
    assertTrue(monitor.snapshot().isEmpty());
  }

  @Test
  void timedFs003MissingBreaksViolationWithoutClearingOpenEvent() {
    var missing =
        monitor.observe(
            OptionalDouble.empty(), true, context(Duration.ZERO, CauseClearance.CONFIRMED));
    assertFalse(missing.suppliedValuePresent());
    assertTrue(missing.event().isEmpty());
    assertTrue(sample(80, 1, true).event().isEmpty());
    assertFalse(
        monitor
            .observe(
                OptionalDouble.empty(),
                true,
                context(Duration.ofSeconds(299), CauseClearance.CONFIRMED))
            .suppliedValuePresent());
    assertTrue(sample(80, 300, true).event().isEmpty());
    assertTrue(sample(80, 599, true).event().isEmpty());
    var open = sample(80, 600, true).event();
    var held =
        monitor.observe(
            OptionalDouble.empty(),
            false,
            context(Duration.ofSeconds(601), CauseClearance.CONFIRMED));
    assertFalse(held.suppliedValuePresent());
    assertEquals(open, held.event());
    assertEquals(open, monitor.snapshot());
    assertEquals(Severity.WARNING, sample(90, 602, true).event().orElseThrow().severity());
    assertEquals(Severity.CRITICAL, sample(90, 662, true).event().orElseThrow().severity());
    assertEquals(BigInteger.TWO, monitor.snapshot().orElseThrow().count());
  }

  @Test
  void timedFs004MissingAndExplicitGapBreakNormalRecovery() {
    for (boolean missing : new boolean[] {false, true}) {
      var owner = new TimedFilesystemMonitor(Service.API);
      owner.observe(
          OptionalDouble.of(80), false, context(Duration.ZERO, CauseClearance.UNCONFIRMED));
      owner.observe(
          OptionalDouble.of(80),
          true,
          context(Duration.ofSeconds(300), CauseClearance.UNCONFIRMED));
      owner.observe(
          OptionalDouble.of(0), true, context(Duration.ofSeconds(301), CauseClearance.UNCONFIRMED));
      var gap =
          owner.observe(
              missing ? OptionalDouble.empty() : OptionalDouble.of(0),
              false,
              context(Duration.ofSeconds(600), CauseClearance.CONFIRMED));
      assertEquals(!missing, gap.suppliedValuePresent());
      assertTrue(gap.event().orElseThrow().isOpen());
      assertTrue(
          owner
              .observe(
                  OptionalDouble.of(0),
                  true,
                  context(Duration.ofSeconds(601), CauseClearance.CONFIRMED))
              .event()
              .orElseThrow()
              .isOpen());
      assertTrue(
          owner
              .observe(
                  OptionalDouble.of(0),
                  true,
                  context(Duration.ofSeconds(899), CauseClearance.CONFIRMED))
              .event()
              .orElseThrow()
              .isOpen());
      assertFalse(
          owner
              .observe(
                  OptionalDouble.of(0),
                  true,
                  context(Duration.ofSeconds(missing ? 901 : 900), CauseClearance.CONFIRMED))
              .event()
              .orElseThrow()
              .isOpen());
    }
  }

  @Test
  void timedFs005InvalidInputsCannotChangeOwnerState() {
    assertThrows(NullPointerException.class, () -> new TimedFilesystemMonitor(null));
    assertThrows(
        NullPointerException.class, () -> new TimedFilesystemMonitor.Evaluation(false, null));
    assertEquals(
        Optional.empty(), new TimedFilesystemMonitor.Evaluation(false, Optional.empty()).event());
    assertThrows(
        NullPointerException.class,
        () -> monitor.observe(null, true, context(Duration.ZERO, CauseClearance.UNCONFIRMED)));
    assertThrows(
        NullPointerException.class, () -> monitor.observe(OptionalDouble.empty(), true, null));
    assertTrue(sample(0, 0, true).event().isEmpty());
    assertTrue(sample(100, 1, true).event().isEmpty());
    for (double value :
        new double[] {
          Double.NaN, Double.POSITIVE_INFINITY, Double.NEGATIVE_INFINITY, -1, 100.000001
        }) assertThrows(IllegalArgumentException.class, () -> sample(value, 1000, false));
    assertEquals(
        "invalid monitoring sequence",
        assertThrows(IllegalArgumentException.class, () -> sample(0, 0, true)).getMessage());
    assertEquals(Severity.CRITICAL, sample(100, 61, true).event().orElseThrow().severity());
    var before = monitor.snapshot();
    assertThrows(IllegalArgumentException.class, () -> sample(101, 62, false));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            monitor.observe(
                OptionalDouble.empty(),
                true,
                context(Duration.ofSeconds(60), CauseClearance.CONFIRMED)));
    assertEquals(before, monitor.snapshot());
  }

  @Test
  void timedFs006ConcurrentOwnerAndLocalStatusLiteral() throws Exception {
    sample(80, 0, false);
    var before = sample(80, 300, true).event().orElseThrow();
    try (var executor = Executors.newFixedThreadPool(4)) {
      try {
        var tasks = new ArrayList<Callable<TimedFilesystemMonitor.Evaluation>>();
        for (int index = 0; index < 64; index++) tasks.add(() -> sample(80, 300, true));
        for (var future : executor.invokeAll(tasks, 10, TimeUnit.SECONDS)) {
          assertTrue(future.get().suppliedValuePresent());
          assertTrue(future.get().event().orElseThrow().isOpen());
        }
      } finally {
        executor.shutdownNow();
        assertTrue(executor.awaitTermination(10, TimeUnit.SECONDS));
      }
    }
    assertEquals(BigInteger.ONE, before.count());
    var current = monitor.snapshot().orElseThrow();
    assertEquals(BigInteger.valueOf(65), current.count());
    String expected =
        "# SUPPLIED_MONITORING_STATE_V1 MODE=STANDARD\n"
            + "condition\tservice\tseverity\tcount\tfirstSeen\tlastSeen\n"
            + "FILESYSTEM\tWEB\tWARNING\t65\t2026-10-23T00:05:00.000Z\t2026-10-23T00:05:00.000Z\n";
    assertEquals(
        expected,
        new MonitoringStatusText().render(MonitoringModePolicy.STANDARD, List.of(current)));
  }
}
