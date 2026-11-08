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
import dev.codex.schubert.nk.batch.monitoring.TransferMetricRecorder.Counts;
import dev.codex.schubert.nk.batch.monitoring.TransferMetricRecorder.Usage;
import io.micrometer.core.instrument.Gauge;
import io.micrometer.core.instrument.Meter;
import io.micrometer.core.instrument.MockClock;
import io.micrometer.core.instrument.simple.SimpleConfig;
import io.micrometer.core.instrument.simple.SimpleMeterRegistry;
import java.math.BigInteger;
import java.time.Duration;
import java.time.Instant;
import java.util.List;
import java.util.Optional;
import java.util.concurrent.Callable;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.function.ToDoubleFunction;
import org.junit.jupiter.api.Test;

/** Literal transfer thresholds/recovery clock and real owned SDK, no collection or control. */
class TransferHealthMonitorTest {
  private static final Instant OBSERVED_AT = Instant.parse("2026-10-23T00:00:00Z");
  private static final String DEBUG_MODE_FIXTURE = "DEBUG";

  private static final class Registry extends SimpleMeterRegistry implements AutoCloseable {
    final AtomicInteger calls = new AtomicInteger();
    final AtomicInteger closes = new AtomicInteger();
    Optional<Throwable> failure = Optional.empty();

    Registry() {
      super(SimpleConfig.DEFAULT, new MockClock());
    }

    @Override
    protected <T> Gauge newGauge(Meter.Id id, T object, ToDoubleFunction<T> value) {
      calls.incrementAndGet();
      if (failure.isPresent()) {
        Throwable problem = failure.orElseThrow();
        if (problem instanceof Error fatal) throw fatal;
        throw (RuntimeException) problem;
      }
      return super.newGauge(id, object, value);
    }

    @Override
    public void close() {
      closes.incrementAndGet();
      super.close();
    }
  }

  private static ObservationContext at(long seconds, CauseClearance cause) {
    return new ObservationContext(
        cause, OBSERVED_AT.plusSeconds(seconds), Duration.ofSeconds(seconds));
  }

  private static Usage usage(long files, long bytes) {
    return new Usage(new Counts(files, bytes), new Counts(0, 0));
  }

  private static TransferHealthMonitor.Evaluation sample(
      TransferHealthMonitor monitor, long files, long bytes, long seconds) {
    return monitor.observe(
        Optional.of(usage(files, bytes)), true, at(seconds, CauseClearance.CONFIRMED));
  }

  @Test
  void transferConn001DebugUsesExactCountsMetricsAndSameImmutableInput() {
    try (var registry = new Registry()) {
      var monitor = new TransferHealthMonitor(registry, DEBUG_MODE_FIXTURE, Service.WEB);
      assertTrue(monitor.snapshot().isEmpty());
      assertTrue(monitor.observedUsage().isEmpty());
      assertTrue(monitor.detailedMetricsRequested());
      var input = new Usage(new Counts(2, 1024), new Counts(3, 2048));
      var result = monitor.observe(Optional.of(input), true, at(0, CauseClearance.CONFIRMED));
      assertTrue(result.suppliedValuePresent());
      assertTrue(result.event().isEmpty());
      assertSame(input, monitor.observedUsage().orElseThrow());
      assertEquals(
          2.0, registry.get("nk_file_transfer_files").tag("suffix", ".part").gauge().value());
      assertEquals(
          2048.0, registry.get("nk_file_transfer_bytes").tag("suffix", ".ready").gauge().value());
      assertEquals(4, registry.getMeters().size());
      assertEquals(0, registry.closes.get());
      assertFalse(registry.isClosed());
    }
  }

  @Test
  void transferConn002WarningBytesAndFilesHaveIndependentExactBoundaries() {
    try (var byteRegistry = new Registry();
        var countRegistry = new Registry()) {
      var bytes = new TransferHealthMonitor(byteRegistry, DEBUG_MODE_FIXTURE, Service.WEB);
      var counts = new TransferHealthMonitor(countRegistry, DEBUG_MODE_FIXTURE, Service.API);
      assertTrue(sample(bytes, 0, 3_499_999_999L, 0).event().isEmpty());
      var byteEvent = sample(bytes, 0, 3_500_000_000L, 1).event().orElseThrow();
      assertEquals(Severity.WARNING, byteEvent.severity());
      assertEquals(Condition.TRANSFER, byteEvent.condition());
      assertEquals(OBSERVED_AT.plusSeconds(1), byteEvent.firstSeen());
      assertEquals(Service.WEB, byteEvent.service());
      assertTrue(sample(counts, 4999, 0, 0).event().isEmpty());
      var countEvent = sample(counts, 5000, 0, 1).event().orElseThrow();
      assertEquals(Severity.WARNING, countEvent.severity());
      assertEquals(Service.API, countEvent.service());
      assertEquals(BigInteger.ONE, countEvent.count());
      var combinedCount =
          counts.observe(
              Optional.of(new Usage(new Counts(2500, 0), new Counts(2500, 0))),
              true,
              at(2, CauseClearance.CONFIRMED));
      assertEquals(BigInteger.TWO, combinedCount.event().orElseThrow().count());
      assertEquals(Severity.WARNING, combinedCount.event().orElseThrow().severity());
      var combinedBytes =
          bytes.observe(
              Optional.of(new Usage(new Counts(0, 1_750_000_000L), new Counts(0, 1_750_000_000L))),
              true,
              at(2, CauseClearance.CONFIRMED));
      assertEquals(BigInteger.TWO, combinedBytes.event().orElseThrow().count());
      assertEquals(Severity.WARNING, combinedBytes.event().orElseThrow().severity());
    }
  }

  @Test
  void transferConn003CriticalPromotesSameEventAndRemainsStickyAtWarningValues() {
    try (var byteRegistry = new Registry();
        var countRegistry = new Registry()) {
      var bytes = new TransferHealthMonitor(byteRegistry, DEBUG_MODE_FIXTURE, Service.BATCH);
      var counts = new TransferHealthMonitor(countRegistry, DEBUG_MODE_FIXTURE, Service.WEB);
      var warning = sample(bytes, 0, 4_499_999_999L, 0).event().orElseThrow();
      assertEquals(Severity.WARNING, warning.severity());
      var critical = sample(bytes, 0, 4_500_000_000L, 1).event().orElseThrow();
      assertEquals(Severity.CRITICAL, critical.severity());
      assertEquals(warning.firstSeen(), critical.firstSeen());
      assertEquals(BigInteger.TWO, critical.count());
      assertEquals(BigInteger.ONE, warning.count());
      assertEquals(
          Severity.CRITICAL, sample(bytes, 0, 3_500_000_000L, 2).event().orElseThrow().severity());
      assertEquals(Severity.WARNING, sample(counts, 8999, 0, 0).event().orElseThrow().severity());
      assertEquals(Severity.CRITICAL, sample(counts, 9000, 0, 1).event().orElseThrow().severity());
      var combinedCount =
          counts.observe(
              Optional.of(new Usage(new Counts(4500, 0), new Counts(4500, 0))),
              true,
              at(2, CauseClearance.CONFIRMED));
      assertEquals(BigInteger.valueOf(3), combinedCount.event().orElseThrow().count());
      assertEquals(Severity.CRITICAL, combinedCount.event().orElseThrow().severity());
      var combinedBytes =
          bytes.observe(
              Optional.of(new Usage(new Counts(0, 2_250_000_000L), new Counts(0, 2_250_000_000L))),
              true,
              at(3, CauseClearance.CONFIRMED));
      assertEquals(BigInteger.valueOf(4), combinedBytes.event().orElseThrow().count());
      assertEquals(Severity.CRITICAL, combinedBytes.event().orElseThrow().severity());
    }
  }

  @Test
  void transferConn004UnknownClearsGaugesWithoutNormalizingOrClosingEvent() {
    try (var registry = new Registry()) {
      var monitor = new TransferHealthMonitor(registry, DEBUG_MODE_FIXTURE, Service.BATCH);
      var initial = monitor.observe(Optional.empty(), true, at(0, CauseClearance.CONFIRMED));
      assertFalse(initial.suppliedValuePresent());
      assertTrue(initial.event().isEmpty());
      var critical = sample(monitor, 9000, 0, 1).event().orElseThrow();
      sample(monitor, 0, 0, 2);
      var missing = monitor.observe(Optional.empty(), true, at(602, CauseClearance.CONFIRMED));
      assertFalse(missing.suppliedValuePresent());
      assertTrue(missing.event().orElseThrow().isOpen());
      assertEquals(critical.count(), missing.event().orElseThrow().count());
      assertTrue(monitor.observedUsage().isEmpty());
      assertEquals(
          missing.event(),
          monitor.observe(Optional.empty(), false, at(602, CauseClearance.CONFIRMED)).event());
      for (var meter : registry.getMeters()) assertTrue(Double.isNaN(((Gauge) meter).value()));
      assertTrue(sample(monitor, 0, 0, 603).event().orElseThrow().isOpen());
      assertTrue(sample(monitor, 0, 0, 1202).event().orElseThrow().isOpen());
      assertFalse(sample(monitor, 0, 0, 1203).event().orElseThrow().isOpen());
    }
  }

  @Test
  void transferConn005ExplicitGapRestartsCriticalRecoveryWithoutIncrement() {
    try (var registry = new Registry()) {
      var monitor = new TransferHealthMonitor(registry, DEBUG_MODE_FIXTURE, Service.API);
      var critical = sample(monitor, 9000, 0, 0).event().orElseThrow();
      sample(monitor, 0, 0, 1);
      var gap = monitor.observe(Optional.of(usage(0, 0)), false, at(601, CauseClearance.CONFIRMED));
      assertTrue(gap.event().orElseThrow().isOpen());
      assertEquals(critical.count(), gap.event().orElseThrow().count());
      assertTrue(sample(monitor, 0, 0, 1200).event().orElseThrow().isOpen());
      assertFalse(sample(monitor, 0, 0, 1201).event().orElseThrow().isOpen());
      assertTrue(monitor.snapshot().isEmpty());
    }
  }

  @Test
  void transferConn006StandardStillMaintainsWarningCriticalAndCauseRecovery() {
    try (var registry = new Registry()) {
      var monitor = new TransferHealthMonitor(registry, "STANDARD", Service.WEB);
      assertFalse(monitor.detailedMetricsRequested());
      assertEquals(Severity.WARNING, sample(monitor, 5000, 0, 0).event().orElseThrow().severity());
      sample(monitor, 0, 0, 1);
      assertTrue(sample(monitor, 0, 0, 300).event().orElseThrow().isOpen());
      assertFalse(sample(monitor, 0, 0, 301).event().orElseThrow().isOpen());
      assertEquals(
          Severity.CRITICAL, sample(monitor, 9000, 0, 302).event().orElseThrow().severity());
      sample(monitor, 0, 0, 303);
      assertTrue(
          monitor
              .observe(Optional.of(usage(0, 0)), true, at(903, CauseClearance.UNCONFIRMED))
              .event()
              .orElseThrow()
              .isOpen());
      assertFalse(sample(monitor, 0, 0, 903).event().orElseThrow().isOpen());
      assertTrue(
          monitor
              .observe(Optional.empty(), false, at(904, CauseClearance.CONFIRMED))
              .event()
              .isEmpty());
      assertTrue(monitor.observedUsage().isEmpty());
      assertTrue(registry.getMeters().isEmpty());
      assertEquals(0, registry.calls.get());
    }
  }

  @Test
  void transferConn007InvalidInputsAndProviderFailuresPreserveOwnerAndCurrentValues() {
    assertThrows(
        NullPointerException.class, () -> new TransferHealthMonitor.Evaluation(false, null));
    assertThrows(
        NullPointerException.class, () -> new TransferHealthMonitor(null, "STANDARD", Service.WEB));
    try (var registry = new Registry()) {
      assertThrows(
          NullPointerException.class,
          () -> new TransferHealthMonitor(registry, DEBUG_MODE_FIXTURE, null));
      assertThrows(
          NullPointerException.class, () -> new TransferHealthMonitor(registry, null, Service.WEB));
      assertThrows(
          IllegalArgumentException.class,
          () -> new TransferHealthMonitor(registry, "debug", Service.WEB));
      assertEquals(0, registry.calls.get());
      var monitor = new TransferHealthMonitor(registry, DEBUG_MODE_FIXTURE, Service.WEB);
      var input = usage(9000, 0);
      var before =
          monitor
              .observe(Optional.of(input), true, at(5, CauseClearance.CONFIRMED))
              .event()
              .orElseThrow();
      assertThrows(
          NullPointerException.class,
          () -> monitor.observe(null, true, at(6, CauseClearance.CONFIRMED)));
      assertThrows(
          NullPointerException.class, () -> monitor.observe(Optional.of(input), true, null));
      assertThrows(IllegalArgumentException.class, () -> sample(monitor, 0, 0, 4));
      assertEquals(before, monitor.snapshot().orElseThrow());
      assertSame(input, monitor.observedUsage().orElseThrow());
      assertEquals(
          9000.0, registry.get("nk_file_transfer_files").tag("suffix", ".part").gauge().value());
    }
    for (Throwable failure : List.of(new IllegalStateException(), new AssertionError()))
      try (var registry = new Registry()) {
        registry.failure = Optional.of(failure);
        assertSame(
            failure,
            assertThrows(
                failure.getClass(),
                () -> new TransferHealthMonitor(registry, DEBUG_MODE_FIXTURE, Service.WEB)));
        assertEquals(1, registry.calls.get());
        assertEquals(0, registry.closes.get());
        assertFalse(registry.isClosed());
      }
  }

  @Test
  void transferConn008ConcurrentOneOwnerHasExactCountAndImmutableOldSnapshot() throws Exception {
    try (var registry = new Registry()) {
      var pool = Executors.newFixedThreadPool(8);
      try {
        var monitor = new TransferHealthMonitor(registry, DEBUG_MODE_FIXTURE, Service.BATCH);
        var input = usage(9000, 1024);
        var first =
            monitor
                .observe(Optional.of(input), true, at(0, CauseClearance.CONFIRMED))
                .event()
                .orElseThrow();
        var jobs =
            java.util.stream.IntStream.range(0, 64)
                .<Callable<Severity>>mapToObj(
                    i ->
                        () ->
                            monitor
                                .observe(Optional.of(input), true, at(1, CauseClearance.CONFIRMED))
                                .event()
                                .orElseThrow()
                                .severity())
                .toList();
        for (var result : pool.invokeAll(jobs, 10, TimeUnit.SECONDS))
          assertEquals(Severity.CRITICAL, result.get());
        assertEquals(BigInteger.ONE, first.count());
        assertEquals(OBSERVED_AT, first.lastSeen());
        assertEquals(BigInteger.valueOf(65), monitor.snapshot().orElseThrow().count());
        assertSame(input, monitor.observedUsage().orElseThrow());
        assertEquals(4, registry.getMeters().size());
      } finally {
        pool.shutdownNow();
        assertTrue(pool.awaitTermination(10, TimeUnit.SECONDS));
      }
    }
  }
}
