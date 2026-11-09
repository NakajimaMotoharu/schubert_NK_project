package dev.codex.schubert.nk.web.monitoring;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import io.micrometer.core.instrument.Gauge;
import io.micrometer.core.instrument.Meter;
import io.micrometer.core.instrument.MeterRegistry;
import io.micrometer.core.instrument.MockClock;
import io.micrometer.core.instrument.Statistic;
import io.micrometer.core.instrument.Timer;
import io.micrometer.core.instrument.distribution.DistributionStatisticConfig;
import io.micrometer.core.instrument.distribution.pause.PauseDetector;
import io.micrometer.core.instrument.simple.SimpleConfig;
import io.micrometer.core.instrument.simple.SimpleMeterRegistry;
import java.time.Duration;
import java.util.ArrayList;
import java.util.EnumMap;
import java.util.List;
import java.util.concurrent.Callable;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.function.Supplier;
import java.util.function.ToDoubleFunction;
import org.jspecify.annotations.Nullable;
import org.junit.jupiter.api.Test;

/** HTTPDUR001..012/1725/BUG1681; literal expectations, owned SDK/MockClock/threads only. */
class OverflowSafeHttpMeterRegistryTest {
  private static final String NAME = "nk_http_request_duration_seconds";

  private static Timer timer(MeterRegistry registry) {
    return Timer.builder(NAME)
        .publishPercentiles()
        .serviceLevelObjectives(
            Duration.ofMillis(50),
            Duration.ofMillis(100),
            Duration.ofMillis(250),
            Duration.ofMillis(500),
            Duration.ofSeconds(1),
            Duration.ofMillis(1500),
            Duration.ofSeconds(2),
            Duration.ofMillis(2500),
            Duration.ofSeconds(5))
        .distributionStatisticExpiry(Duration.ofSeconds(1))
        .distributionStatisticBufferLength(2)
        .register(registry);
  }

  private static void cdf(Timer timer, double... expected) {
    var counts = timer.takeSnapshot().histogramCounts();
    double[] bounds = {
      50000000,
      100000000,
      250000000,
      500000000,
      1000000000,
      1500000000,
      2000000000,
      2500000000L,
      5000000000L
    };
    assertEquals(9, counts.length);
    for (int i = 0; i < 9; i++) {
      assertEquals(bounds[i], counts[i].bucket());
      assertEquals(expected[i], counts[i].count());
    }
  }

  @Test
  void httpDur001EveryBoundaryBelowEqualAboveUsesLiteralIntegerNanoseconds() {
    try (var registry = new OverflowSafeHttpMeterRegistry(new MockClock())) {
      var timer = timer(registry);
      for (long value :
          new long[] {
            49999999,
            50000000,
            50000001,
            99999999,
            100000000,
            100000001,
            249999999,
            250000000,
            250000001,
            499999999,
            500000000,
            500000001,
            999999999,
            1000000000,
            1000000001,
            1499999999,
            1500000000,
            1500000001,
            1999999999,
            2000000000,
            2000000001,
            2499999999L,
            2500000000L,
            2500000001L,
            4999999999L,
            5000000000L,
            5000000001L
          }) timer.record(value, TimeUnit.NANOSECONDS);
      assertEquals(27, timer.count());
      assertEquals(38.7, timer.totalTime(TimeUnit.SECONDS), 1e-13);
      assertEquals(5.000000001, timer.max(TimeUnit.SECONDS));
      cdf(timer, 2, 5, 8, 11, 14, 17, 20, 23, 26);
      assertEquals(10, registry.getMeters().size());
      assertSame(timer, registry.get(NAME).timer());
      assertEquals(TimeUnit.SECONDS, timer.baseTimeUnit());
    }
  }

  @Test
  void httpDur002AllSevenTimeUnitsHaveIndependentLiteralTotals() {
    try (var registry = new OverflowSafeHttpMeterRegistry(new MockClock())) {
      var timer = timer(registry);
      for (var unit :
          List.of(
              TimeUnit.NANOSECONDS,
              TimeUnit.MICROSECONDS,
              TimeUnit.MILLISECONDS,
              TimeUnit.SECONDS,
              TimeUnit.MINUTES,
              TimeUnit.HOURS,
              TimeUnit.DAYS)) timer.record(1, unit);
      assertEquals(7, timer.count());
      assertEquals(90061001001001.0, timer.totalTime(TimeUnit.NANOSECONDS));
      assertEquals(90061001001.001, timer.totalTime(TimeUnit.MICROSECONDS));
      assertEquals(90061001.001001, timer.totalTime(TimeUnit.MILLISECONDS));
      assertEquals(90061.001001001, timer.totalTime(TimeUnit.SECONDS));
      assertEquals(86400, timer.max(TimeUnit.SECONDS));
    }
  }

  @Test
  void httpDur003BothExtremeOrdersKeepFiniteTotalsAndEverySmallBucket() {
    for (long[] values :
        List.of(
            new long[] {0, 1, Long.MAX_VALUE, Long.MAX_VALUE, 1},
            new long[] {Long.MAX_VALUE, Long.MAX_VALUE, 1, 0, 1})) {
      try (var registry = new OverflowSafeHttpMeterRegistry(new MockClock())) {
        var timer = timer(registry);
        for (long value : values) timer.record(value, TimeUnit.NANOSECONDS);
        assertEquals(5, timer.count());
        assertEquals(1.8446744073709553E10, timer.totalTime(TimeUnit.SECONDS));
        assertEquals(1.8446744073709553E10, timer.takeSnapshot().total(TimeUnit.SECONDS));
        assertEquals(3.6893488147419105E9, timer.mean(TimeUnit.SECONDS));
        var measured = new EnumMap<Statistic, Double>(Statistic.class);
        timer.measure().forEach(m -> measured.put(m.getStatistic(), m.getValue()));
        assertEquals(1.8446744073709553E10, measured.get(Statistic.TOTAL_TIME).doubleValue());
        assertEquals(3, registry.get(NAME + ".histogram").tag("le", "0.05").gauge().value());
        assertEquals(9.223372036854776E9, timer.max(TimeUnit.SECONDS));
        cdf(timer, 3, 3, 3, 3, 3, 3, 3, 3, 3);
      }
    }
  }

  @Test
  void httpDur004SnapshotMeanAndMeasurementsReadSafeTotalInCorrectUnits() {
    try (var registry = new OverflowSafeHttpMeterRegistry(new MockClock())) {
      var timer = timer(registry);
      timer.record(1, TimeUnit.SECONDS);
      timer.record(1500, TimeUnit.MILLISECONDS);
      var snapshot = timer.takeSnapshot();
      assertEquals(2, snapshot.count());
      assertEquals(2.5, snapshot.total(TimeUnit.SECONDS));
      assertEquals(1.5, snapshot.max(TimeUnit.SECONDS));
      assertEquals(1.25, timer.mean(TimeUnit.SECONDS));
      var values = new EnumMap<Statistic, Double>(Statistic.class);
      timer.measure().forEach(m -> values.put(m.getStatistic(), m.getValue()));
      assertEquals(3, values.size());
      assertEquals(2.0, values.get(Statistic.COUNT).doubleValue());
      assertEquals(2.5, values.get(Statistic.TOTAL_TIME).doubleValue());
      assertEquals(1.5, values.get(Statistic.MAX).doubleValue());
    }
  }

  @Test
  void httpDur005SdkTimeWindowMaximumExpiresButCumulativeTotalDoesNot() {
    var clock = new MockClock();
    try (var registry = new OverflowSafeHttpMeterRegistry(clock)) {
      var timer = timer(registry);
      timer.record(1, TimeUnit.SECONDS);
      timer.record(1500, TimeUnit.MILLISECONDS);
      assertEquals(1.5, timer.max(TimeUnit.SECONDS));
      clock.add(Duration.ofSeconds(3));
      assertEquals(0, timer.max(TimeUnit.SECONDS));
      assertEquals(2, timer.count());
      assertEquals(2.5, timer.totalTime(TimeUnit.SECONDS));
    }
  }

  private static class GenericRegistry extends SimpleMeterRegistry implements AutoCloseable {
    GenericRegistry() {
      super(SimpleConfig.DEFAULT, new MockClock());
    }
  }

  @Test
  void httpDur006UnknownRegistryIsNotDetailedCapabilityAndNullNeverNormalizes() {
    try (var registry = new GenericRegistry()) {
      assertFalse(new HttpMetricRecorder(registry, "STANDARD").detailedMetricsRequested());
      assertThrows(IllegalArgumentException.class, () -> new HttpMetricRecorder(registry, "DEBUG"));
      assertThrows(
          IllegalArgumentException.class,
          () -> OverflowSafeHttpMeterRegistry.requireCompatible(null));
      assertEquals(0, registry.getMeters().size());
    }
    assertThrows(NullPointerException.class, () -> new OverflowSafeHttpMeterRegistry(null));
    try (var registry = new OverflowSafeHttpMeterRegistry()) {
      assertDoesNotThrow(() -> OverflowSafeHttpMeterRegistry.requireCompatible(registry));
      assertTrue(registry.getMeters().isEmpty());
    }
  }

  private static DistributionStatisticConfig.Builder configuration() {
    return DistributionStatisticConfig.builder()
        .percentilesHistogram(false)
        .percentiles()
        .serviceLevelObjectives(
            50000000,
            100000000,
            250000000,
            500000000,
            1000000000,
            1500000000,
            2000000000,
            2500000000L,
            5000000000L)
        .expiry(Duration.ofSeconds(1))
        .bufferLength(2);
  }

  @Test
  void httpDur007IncompatibleHistogramPercentilesOrBoundariesFailClosed() {
    try (var registry = new GenericRegistry()) {
      for (var config :
          List.of(
              configuration().percentilesHistogram(true).build(),
              configuration().percentiles(.95).build(),
              configuration().serviceLevelObjectives(1).build())) {
        assertThrows(
            IllegalArgumentException.class,
            () ->
                OverflowSafeHttpMeterRegistry.durationTimer(
                    registry,
                    config,
                    registry.config().pauseDetector(),
                    () -> {
                      throw new AssertionError("invalid config factory forbidden");
                    }));
      }
      var valid = configuration().build().merge(DistributionStatisticConfig.DEFAULT);
      assertThrows(
          IllegalArgumentException.class,
          () ->
              OverflowSafeHttpMeterRegistry.durationTimer(
                  registry,
                  valid,
                  new PauseDetector() {},
                  () -> {
                    throw new AssertionError("unknown pause factory");
                  }));
      assertThrows(
          IllegalArgumentException.class,
          () ->
              OverflowSafeHttpMeterRegistry.durationTimer(
                  registry,
                  valid,
                  null,
                  () -> {
                    throw new AssertionError("null pause factory");
                  }));
      assertThrows(
          NullPointerException.class,
          () ->
              OverflowSafeHttpMeterRegistry.durationTimer(
                  registry, valid, registry.config().pauseDetector(), () -> null));
      assertThrows(
          NullPointerException.class,
          () ->
              OverflowSafeHttpMeterRegistry.durationTimer(
                  registry, valid, registry.config().pauseDetector(), null));
      assertEquals(0, registry.getMeters().size());
    }
  }

  @Test
  void httpDur008ConcurrentWorkersAndIndependentOwnersKeepExactIntegerVector() throws Exception {
    try (var registry = new OverflowSafeHttpMeterRegistry(new MockClock());
        var other = new OverflowSafeHttpMeterRegistry(new MockClock())) {
      var executor = Executors.newFixedThreadPool(4);
      try {
        var timer = timer(registry);
        var unrelated = timer(other);
        List<Callable<Void>> tasks = new ArrayList<>();
        for (int worker = 0; worker < 4; worker++)
          tasks.add(
              () -> {
                for (int i = 0; i < 64; i++) timer.record(1, TimeUnit.SECONDS);
                return null;
              });
        for (var future : executor.invokeAll(tasks, 10, TimeUnit.SECONDS))
          future.get(10, TimeUnit.SECONDS);
        assertEquals(256, timer.count());
        assertEquals(256, timer.totalTime(TimeUnit.SECONDS));
        assertEquals(1, timer.max(TimeUnit.SECONDS));
        cdf(timer, 0, 0, 0, 0, 256, 256, 256, 256, 256);
        assertEquals(0, unrelated.count());
        assertEquals(0, unrelated.totalTime(TimeUnit.SECONDS));
      } finally {
        executor.shutdownNow();
        assertTrue(executor.awaitTermination(10, TimeUnit.SECONDS));
      }
    }
  }

  @Test
  void httpDur009SdkCallbackWrappersKeepReturnsAndOriginalCheckedFailure() throws Exception {
    var clock = new MockClock();
    try (var registry = new OverflowSafeHttpMeterRegistry(clock)) {
      var timer = timer(registry);
      timer.record((Runnable) () -> clock.add(Duration.ofSeconds(1)));
      assertEquals(
          "callable",
          timer.recordCallable(
              () -> {
                clock.add(Duration.ofSeconds(2));
                return "callable";
              }));
      assertEquals(
          "supplier",
          timer.record(
              (Supplier<String>)
                  () -> {
                    clock.add(Duration.ofSeconds(3));
                    return "supplier";
                  }));
      var failure = new Exception("owned callback fault");
      assertSame(
          failure,
          assertThrows(
              Exception.class,
              () ->
                  timer.recordCallable(
                      () -> {
                        clock.add(Duration.ofSeconds(4));
                        throw failure;
                      })));
      assertEquals(4, timer.count());
      assertEquals(10, timer.totalTime(TimeUnit.SECONDS));
      assertEquals(4, timer.max(TimeUnit.SECONDS));
      var runtime = new IllegalStateException("owned supplier fault");
      assertSame(
          runtime,
          assertThrows(
              IllegalStateException.class,
              () ->
                  timer.record(
                      (Supplier<String>)
                          () -> {
                            clock.add(Duration.ofSeconds(5));
                            throw runtime;
                          })));
      var fatal = new AssertionError("owned runnable fault");
      assertSame(
          fatal,
          assertThrows(
              AssertionError.class,
              () ->
                  timer.record(
                      (Runnable)
                          () -> {
                            clock.add(Duration.ofSeconds(6));
                            throw fatal;
                          })));
      assertEquals(6, timer.count());
      assertEquals(21, timer.totalTime(TimeUnit.SECONDS));
      assertEquals(6, timer.max(TimeUnit.SECONDS));
      Supplier<@Nullable Object> nullSupplier = () -> null;
      Callable<@Nullable Object> nullCallable = () -> null;
      assertNull(timer.record(nullSupplier));
      assertNull(timer.recordCallable(nullCallable));
      assertEquals(8, timer.count());
      assertEquals(21, timer.totalTime(TimeUnit.SECONDS));
      assertEquals(6, timer.max(TimeUnit.SECONDS));
    }
  }

  @Test
  void httpDur010UnrelatedTimerAndCounterKeepStandardSdkBehavior() {
    try (var registry = new OverflowSafeHttpMeterRegistry(new MockClock())) {
      var other = registry.timer("unrelated_timer");
      other.record(3, TimeUnit.SECONDS);
      assertEquals(1, other.count());
      assertEquals(3, other.totalTime(TimeUnit.SECONDS));
      assertEquals(3, other.max(TimeUnit.SECONDS));
      registry.counter("unrelated_counter").increment(7);
      assertEquals(7, registry.get("unrelated_counter").counter().count());
      assertEquals(2, registry.getMeters().size());
    }
  }

  private static final class FaultRegistry extends GenericRegistry
      implements OverflowSafeDurationSupport {
    final IllegalStateException failure = new IllegalStateException("owned factory fault");

    @Override
    protected Timer newTimer(Meter.Id id, DistributionStatisticConfig config, PauseDetector pause) {
      return OverflowSafeHttpMeterRegistry.durationTimer(
          this, config, pause, () -> super.newTimer(id, config, pause));
    }

    @Override
    protected <T> Gauge newGauge(Meter.Id id, T object, ToDoubleFunction<T> function) {
      throw failure;
    }
  }

  @Test
  void httpDur011AuxiliaryFactoryFailurePropagatesIdentityAndPreservesOwner() {
    try (var registry = new FaultRegistry()) {
      assertSame(
          registry.failure, assertThrows(IllegalStateException.class, () -> timer(registry)));
      assertFalse(registry.isClosed());
      assertEquals(0, registry.getMeters().size());
    }
  }

  @Test
  void httpDur012NullUnitAndNegativeSdkRecordNeverProduceNormalObservation() {
    try (var registry = new OverflowSafeHttpMeterRegistry(new MockClock())) {
      var timer = timer(registry);
      assertThrows(NullPointerException.class, () -> timer.record(1, null));
      assertThrows(NullPointerException.class, () -> timer.totalTime(null));
      assertThrows(NullPointerException.class, () -> timer.max(null));
      assertThrows(NullPointerException.class, () -> timer.record((Supplier<Object>) null));
      assertThrows(NullPointerException.class, () -> timer.recordCallable(null));
      assertThrows(NullPointerException.class, () -> timer.record((Runnable) null));
      timer.record(-1, TimeUnit.NANOSECONDS);
      assertEquals(0, timer.count());
      timer.record(0, TimeUnit.NANOSECONDS);
      assertEquals(1, timer.count());
      assertEquals(0, timer.totalTime(TimeUnit.SECONDS));
      cdf(timer, 1, 1, 1, 1, 1, 1, 1, 1, 1);
    }
  }
}
