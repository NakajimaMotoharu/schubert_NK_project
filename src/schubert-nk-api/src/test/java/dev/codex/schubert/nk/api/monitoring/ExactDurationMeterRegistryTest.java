package dev.codex.schubert.nk.api.monitoring;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotSame;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.protocol.layout.LayoutId;
import io.micrometer.core.instrument.Clock;
import io.micrometer.core.instrument.DistributionSummary;
import io.micrometer.core.instrument.Gauge;
import io.micrometer.core.instrument.Meter;
import io.micrometer.core.instrument.MeterRegistry;
import io.micrometer.core.instrument.Tags;
import io.micrometer.core.instrument.distribution.CountAtBucket;
import io.micrometer.core.instrument.distribution.DistributionStatisticConfig;
import io.micrometer.core.instrument.simple.SimpleConfig;
import io.micrometer.core.instrument.simple.SimpleMeterRegistry;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.Callable;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.function.ToDoubleFunction;
import org.junit.jupiter.api.Test;

/** EXDUR001..010/1723/BUG1678; literal CDF vectors, owned SDK and threads only. */
class ExactDurationMeterRegistryTest {
  private static final String SECONDS_UNIT = "seconds";
  private static final String NAME = "nk_db_query_duration_seconds";
  private static final Clock FIXED =
      new Clock() {
        public long wallTime() {
          return 1000;
        }

        public long monotonicTime() {
          return 1000000;
        }
      };

  private static ExactDurationMeterRegistry registry() {
    return new ExactDurationMeterRegistry(SimpleConfig.DEFAULT, FIXED);
  }

  private static DistributionSummary summary(MeterRegistry registry) {
    return DistributionSummary.builder(NAME)
        .baseUnit(SECONDS_UNIT)
        .publishPercentileHistogram()
        .publishPercentiles()
        .serviceLevelObjectives(.001, .01, .1, 1., 1.5)
        .register(registry);
  }

  private static void cdf(DistributionSummary summary, double... expected) {
    var snapshot = summary.takeSnapshot();
    assertEquals(0, snapshot.percentileValues().length);
    assertEquals(5, snapshot.histogramCounts().length);
    double[] boundaries = {.001, .01, .1, 1., 1.5};
    for (int i = 0; i < 5; i++) {
      assertEquals(boundaries[i], snapshot.histogramCounts()[i].bucket());
      assertEquals(expected[i], snapshot.histogramCounts()[i].count());
    }
  }

  @Test
  void exDur001IndependentBelowEqualAboveEveryFiniteBoundary() {
    try (var registry = registry()) {
      var summary = summary(registry);
      for (double value :
          new double[] {
            .000999999,
            .001,
            .001000001,
            .009999999,
            .01,
            .010000001,
            .099999999,
            .1,
            .100000001,
            .999999999,
            1.,
            1.000000001,
            1.499999999,
            1.5,
            1.500000001
          }) summary.record(value);
      assertEquals(15, summary.count());
      assertEquals(7.833, summary.totalAmount(), 1e-14);
      assertEquals(1.500000001, summary.max());
      cdf(summary, 2, 5, 8, 11, 14);
      assertEquals(6, registry.getMeters().size());
      assertSame(summary, registry.get(NAME).summary());
      assertEquals(NAME, summary.getId().getName());
      assertEquals(SECONDS_UNIT, summary.getId().getBaseUnit());
    }
  }

  @Test
  void exDur002BothMixedExtremeOrdersKeepSmallSamplesAndFiniteSum() {
    for (double[] values :
        List.of(
            new double[] {0, .000000001, 9.223372036854776E9, 9.223372036854776E9, .000000001},
            new double[] {9.223372036854776E9, 9.223372036854776E9, .000000001, 0, .000000001})) {
      try (var registry = registry()) {
        var summary = summary(registry);
        for (double value : values) summary.record(value);
        assertEquals(5, summary.count());
        assertEquals(1.8446744073709553E10, summary.totalAmount());
        assertEquals(9.223372036854776E9, summary.max());
        cdf(summary, 3, 3, 3, 3, 3);
      }
    }
  }

  @Test
  void exDur003RejectedScalarInputsLeaveCompleteSnapshotUnchanged() {
    try (var registry = registry()) {
      var summary = summary(registry);
      summary.record(.01);
      for (double invalid :
          new double[] {
            -1,
            -.000000001,
            Double.NaN,
            Double.POSITIVE_INFINITY,
            Double.NEGATIVE_INFINITY,
            9.223372036854778E9
          }) {
        assertEquals(
            "invalid duration",
            assertThrows(IllegalArgumentException.class, () -> summary.record(invalid))
                .getMessage());
      }
      assertEquals(1, summary.count());
      assertEquals(.01, summary.totalAmount());
      assertEquals(.01, summary.max());
      cdf(summary, 0, 1, 1, 1, 1);
    }
  }

  @Test
  void exDur004SnapshotIsAtomicDefensiveAndDoesNotAliasMutableBuckets() {
    try (var registry = registry()) {
      var summary = summary(registry);
      var empty = summary.takeSnapshot();
      assertEquals(0, empty.count());
      assertEquals(0, empty.total());
      assertEquals(0, empty.max());
      empty.histogramCounts()[0] = new CountAtBucket(99.0, 99);
      cdf(summary, 0, 0, 0, 0, 0);
      summary.record(1);
      var first = summary.takeSnapshot();
      summary.record(1.5);
      assertNotSame(first.histogramCounts(), summary.takeSnapshot().histogramCounts());
      assertEquals(1, first.count());
      assertEquals(1, first.total());
      assertEquals(1, first.max());
      cdf(summary, 0, 0, 0, 1, 2);
    }
  }

  private static final class Probe extends SimpleMeterRegistry implements AutoCloseable {
    Probe() {
      super(SimpleConfig.DEFAULT, FIXED);
    }

    DistributionSummary create(String unit, DistributionStatisticConfig config, double scale) {
      return ExactDurationMeterRegistry.exactDurationSummary(
          this,
          new Meter.Id(NAME, Tags.empty(), unit, null, Meter.Type.DISTRIBUTION_SUMMARY),
          config,
          scale);
    }
  }

  private static DistributionStatisticConfig.Builder configuration() {
    return DistributionStatisticConfig.builder()
        .percentilesHistogram(true)
        .percentiles()
        .serviceLevelObjectives(.001, .01, .1, 1., 1.5);
  }

  @Test
  void exDur005EveryIncompatibleFactoryConfigurationFailsClosed() {
    try (var registry = new Probe()) {
      assertThrows(
          IllegalArgumentException.class,
          () -> registry.create(SECONDS_UNIT, configuration().build(), 2));
      assertThrows(
          IllegalArgumentException.class,
          () -> registry.create("bytes", configuration().build(), 1));
      assertThrows(
          IllegalArgumentException.class, () -> registry.create(null, configuration().build(), 1));
      assertThrows(
          IllegalArgumentException.class,
          () ->
              registry.create(
                  SECONDS_UNIT, configuration().percentilesHistogram(false).build(), 1));
      assertThrows(
          IllegalArgumentException.class,
          () -> registry.create(SECONDS_UNIT, configuration().percentiles(.95).build(), 1));
      assertThrows(
          IllegalArgumentException.class,
          () ->
              registry.create(
                  SECONDS_UNIT, configuration().serviceLevelObjectives(.01).build(), 1));
      assertEquals(0, registry.getMeters().size());
    }
  }

  @Test
  void exDur006GenericRegistryAcceptedOnlyWhenDetailedObservationDisabled() {
    try (var registry = new GenericRegistry()) {
      assertFalse(
          new DbQueryDurationMetricRecorder(registry, "STANDARD").detailedMetricsRequested());
      assertFalse(
          new MqProcessingDurationMetricRecorder(registry, "STANDARD", new LayoutId("LGNREQ01"))
              .detailedMetricsRequested());
      assertThrows(
          IllegalArgumentException.class,
          () -> new DbQueryDurationMetricRecorder(registry, "DEBUG"));
      assertThrows(
          IllegalArgumentException.class,
          () ->
              new MqProcessingDurationMetricRecorder(registry, "DEBUG", new LayoutId("LGNREQ01")));
      assertThrows(
          IllegalArgumentException.class, () -> ExactDurationMeterRegistry.requireCompatible(null));
      assertEquals(0, registry.getMeters().size());
    }
  }

  private static class GenericRegistry extends SimpleMeterRegistry implements AutoCloseable {
    GenericRegistry() {
      super(SimpleConfig.DEFAULT, FIXED);
    }
  }

  @Test
  void exDur007UnrelatedSummaryAndCounterRemainNormalSdkOwnedMeters() {
    try (var registry = registry()) {
      var other = registry.summary("unrelated_summary");
      other.record(2);
      other.record(3);
      assertEquals(2, other.count());
      assertEquals(5, other.totalAmount());
      assertEquals(3, other.max());
      var counter = registry.counter("unrelated_counter");
      counter.increment(7);
      assertEquals(7, counter.count());
      assertEquals(2, registry.getMeters().size());
    }
  }

  @Test
  void exDur008ConstructorsRejectNullAndDurationStateNeverReadsClock() {
    assertThrows(NullPointerException.class, () -> new ExactDurationMeterRegistry(null, FIXED));
    assertThrows(
        NullPointerException.class,
        () -> new ExactDurationMeterRegistry(SimpleConfig.DEFAULT, null));
    var forbidden = new AtomicBoolean();
    Clock clock =
        new Clock() {
          public long wallTime() {
            if (forbidden.get()) throw new AssertionError("clock forbidden");
            return 1000;
          }

          public long monotonicTime() {
            if (forbidden.get()) throw new AssertionError("clock forbidden");
            return 1000000;
          }
        };
    try (var registry = new ExactDurationMeterRegistry(SimpleConfig.DEFAULT, clock)) {
      forbidden.set(true);
      var summary = summary(registry);
      summary.record(.1);
      assertEquals(1, summary.count());
      assertEquals(.1, summary.totalAmount());
      assertEquals(.1, summary.max());
      cdf(summary, 0, 0, 1, 1, 1);
    }
    try (var registry = new ExactDurationMeterRegistry()) {
      assertTrue(registry.getMeters().isEmpty());
    }
  }

  @Test
  void exDur009ConcurrentUpdatesAndSnapshotsHaveConsistentIndependentIdentity() throws Exception {
    try (var registry = registry();
        var executor = Executors.newFixedThreadPool(5)) {
      var summary = summary(registry);
      var start = new CountDownLatch(1);
      List<Callable<Void>> tasks = new ArrayList<>();
      for (int thread = 0; thread < 4; thread++)
        tasks.add(
            () -> {
              assertTrue(start.await(5, TimeUnit.SECONDS));
              for (int i = 0; i < 64; i++) summary.record(1);
              return null;
            });
      tasks.add(
          () -> {
            assertTrue(start.await(5, TimeUnit.SECONDS));
            for (int i = 0; i < 128; i++) {
              var snapshot = summary.takeSnapshot();
              assertEquals(snapshot.count(), snapshot.total());
              assertEquals(0, snapshot.histogramCounts()[2].count());
              assertEquals(snapshot.count(), snapshot.histogramCounts()[3].count());
              assertEquals(snapshot.count(), snapshot.histogramCounts()[4].count());
            }
            return null;
          });
      var futures = tasks.stream().map(executor::submit).toList();
      start.countDown();
      for (var future : futures) future.get(10, TimeUnit.SECONDS);
      assertEquals(256, summary.count());
      assertEquals(256, summary.totalAmount());
      assertEquals(1, summary.max());
      cdf(summary, 0, 0, 0, 256, 256);
    }
  }

  @Test
  void exDur010AuxiliaryGaugeFactoryFailureRetainsCallerOwnershipAndIdentity() {
    var failure = new IllegalStateException("owned factory fault");
    try (var registry = new FaultRegistry(failure)) {
      assertSame(failure, assertThrows(IllegalStateException.class, () -> summary(registry)));
      assertTrue(registry.getMeters().isEmpty());
    }
    try (var registry = registry()) {
      var summary = summary(registry);
      summary.record(.001);
      assertEquals(1, registry.get(NAME + ".histogram").tag("le", "0.001").gauge().value());
      assertEquals(0, summary.takeSnapshot().percentileValues().length);
    }
  }

  private static final class FaultRegistry extends GenericRegistry implements ExactDurationSupport {
    private final IllegalStateException failure;

    FaultRegistry(IllegalStateException failure) {
      this.failure = failure;
    }

    @Override
    protected DistributionSummary newDistributionSummary(
        Meter.Id id, DistributionStatisticConfig config, double scale) {
      return ExactDurationMeterRegistry.exactDurationSummary(this, id, config, scale);
    }

    @Override
    protected <T> Gauge newGauge(Meter.Id id, T object, ToDoubleFunction<T> value) {
      throw failure;
    }
  }
}
