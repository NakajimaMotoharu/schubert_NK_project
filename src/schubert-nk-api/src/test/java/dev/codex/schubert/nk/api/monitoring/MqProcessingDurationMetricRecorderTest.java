package dev.codex.schubert.nk.api.monitoring;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.api.monitoring.MqProcessingDurationMetricRecorder.Outcome;
import dev.codex.schubert.nk.protocol.layout.LayoutId;
import dev.codex.schubert.nk.protocol.layout.UnsupportedLayoutException;
import io.micrometer.core.instrument.Clock;
import io.micrometer.core.instrument.Counter;
import io.micrometer.core.instrument.DistributionSummary;
import io.micrometer.core.instrument.Meter;
import io.micrometer.core.instrument.distribution.DistributionStatisticConfig;
import io.micrometer.core.instrument.distribution.HistogramSnapshot;
import io.micrometer.core.instrument.simple.SimpleConfig;
import io.micrometer.core.instrument.simple.SimpleMeterRegistry;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Optional;
import java.util.Set;
import java.util.concurrent.Callable;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.stream.Collectors;
import org.junit.jupiter.api.Test;

/** MQTIME001..008/1716; independent SS323 literal rows, own SDK only, never JMS/clock authority. */
class MqProcessingDurationMetricRecorderTest {
  // Independent SS323 oracle inherited from existing hand-written test vectors, not Production.
  private static final List<String> LAYOUTS =
      List.of(
          "LGNREQ01",
          "LGNRSP01",
          "LOGREQ01",
          "LOGRSP01",
          "GAMREQ01",
          "GAMRSP01",
          "SPKREQ01",
          "SPKRSP01",
          "SRCREQ01",
          "SRCRSP01",
          "RTEREQ01",
          "RTERSP01",
          "SCFREQ01",
          "SCFRSP01",
          "SCNREQ01",
          "SCNRSP01",
          "AUDREQ01",
          "AUDRSP01",
          "ANMREQ01",
          "ANMRSP01",
          "ANLREQ01",
          "ANLRSP01",
          "VIDREQ01",
          "VIDRSP01",
          "MCTREQ01",
          "MCTRSP01",
          "MCSREQ01",
          "MCSRSP01",
          "MTRREQ01",
          "MTRRSP01",
          "MEDREQ01",
          "MEDRSP01",
          "LGSREQ01",
          "LGSRSP01",
          "USRREQ01",
          "USRRSP01",
          "UCRREQ01",
          "UCRRSP01",
          "UDTREQ01",
          "UDTRSP01",
          "USTREQ01",
          "USTRSP01",
          "URLREQ01",
          "URLRSP01",
          "UPWREQ01",
          "UPWRSP01",
          "ULKREQ01",
          "ULKRSP01",
          "QSBREQ01",
          "QSBRSP01",
          "NTSREQ01",
          "NTSRSP01",
          "NTDREQ01",
          "NTDRSP01",
          "NTCREQ01",
          "NTCRSP01",
          "QSSREQ01",
          "QSSRSP01",
          "QSDREQ01",
          "QSDRSP01",
          "QDLREQ01",
          "QDLRSP01",
          "QWKREQ01",
          "WLGEVT01");

  private static final class Registry extends SimpleMeterRegistry
      implements AutoCloseable, ExactDurationSupport {
    final AtomicInteger registrations = new AtomicInteger();
    final AtomicInteger records = new AtomicInteger();
    final AtomicInteger closes = new AtomicInteger();
    final List<DistributionStatisticConfig> configurations = new ArrayList<>();
    Optional<Throwable> factoryFailure = Optional.empty();
    Optional<Throwable> recordFailure = Optional.empty();
    boolean failAfter;

    Registry() {
      super(
          SimpleConfig.DEFAULT,
          new Clock() {
            @Override
            public long wallTime() {
              return 1000;
            }

            @Override
            public long monotonicTime() {
              return 1000000;
            }
          });
    }

    @Override
    protected DistributionSummary newDistributionSummary(
        Meter.Id id, DistributionStatisticConfig config, double scale) {
      if (registrations.incrementAndGet() == 2) fail(factoryFailure);
      configurations.add(config);
      var delegate = ExactDurationMeterRegistry.exactDurationSummary(this, id, config, scale);
      return new DistributionSummary() {
        @Override
        public Meter.Id getId() {
          return delegate.getId();
        }

        @Override
        public long count() {
          return delegate.count();
        }

        @Override
        public double totalAmount() {
          return delegate.totalAmount();
        }

        @Override
        public double max() {
          return delegate.max();
        }

        @Override
        public HistogramSnapshot takeSnapshot() {
          return delegate.takeSnapshot();
        }

        @Override
        public void record(double amount) {
          records.incrementAndGet();
          if (!failAfter) fail(recordFailure);
          delegate.record(amount);
          if (failAfter) fail(recordFailure);
        }
      };
    }

    @Override
    public void close() {
      closes.incrementAndGet();
      super.close();
    }
  }

  private static final class Unformattable extends IllegalStateException {
    private static final long serialVersionUID = 1L;

    @Override
    public String getMessage() {
      throw new AssertionError("provider message forbidden");
    }

    @Override
    public String toString() {
      throw new AssertionError("provider formatting forbidden");
    }
  }

  private static void fail(Optional<Throwable> failure) {
    if (failure.isPresent()) {
      var problem = failure.orElseThrow();
      if (problem instanceof Error error) throw error;
      throw (RuntimeException) problem;
    }
  }

  private static String flow(String layout) {
    return switch (layout) {
      case "QSBREQ01", "QSBRSP01" -> "ASYNC_ACCEPTANCE";
      case "QWKREQ01", "WLGEVT01" -> "INTERNAL";
      default -> "SYNCHRONOUS";
    };
  }

  private static DistributionSummary summary(Registry registry, String layout, String outcome) {
    return registry
        .get("nk_mq_processing_duration_seconds")
        .tags("flow", flow(layout), "layout", layout, "outcome", outcome)
        .summary();
  }

  private static void shape(Registry registry, Set<String> expectedPairs) {
    assertEquals(expectedPairs.size() * 6, registry.getMeters().size());
    var primary = new java.util.HashSet<String>();
    var auxiliary = new java.util.HashSet<String>();
    for (var meter : registry.getMeters()) {
      var id = meter.getId();
      String layout = id.getTag("layout");
      String outcome = id.getTag("outcome");
      String pair = layout + "/" + outcome;
      assertTrue(expectedPairs.contains(pair));
      assertEquals(flow(layout), id.getTag("flow"));
      if (id.getName().equals("nk_mq_processing_duration_seconds")) {
        assertEquals(Meter.Type.DISTRIBUTION_SUMMARY, id.getType());
        assertEquals("seconds", id.getBaseUnit());
        assertEquals(
            Set.of("flow", "layout", "outcome"),
            id.getTags().stream().map(t -> t.getKey()).collect(Collectors.toSet()));
        assertTrue(primary.add(pair));
      } else {
        assertEquals(Meter.Type.GAUGE, id.getType());
        String kind = "le";
        assertEquals("nk_mq_processing_duration_seconds.histogram", id.getName());
        assertEquals(
            Set.of("flow", "layout", "outcome", kind),
            id.getTags().stream().map(t -> t.getKey()).collect(Collectors.toSet()));
        assertTrue(auxiliary.add(pair + "/" + kind + "/" + id.getTag(kind)));
      }
    }
    assertEquals(expectedPairs, primary);
    var expected = new java.util.HashSet<String>();
    for (String pair : expectedPairs) {
      for (String bound : List.of("0.001", "0.01", "0.1", "1", "1.5"))
        expected.add(pair + "/le/" + bound);
    }
    assertEquals(expected, auxiliary);
  }

  @Test
  void mqTime001AllSixtyFourLiteralLayoutsBindApprovedFlowAndOnlyTwoPrimaryOutcomes() {
    try (var registry = new Registry()) {
      var pairs = new java.util.HashSet<String>();
      for (String layout : LAYOUTS) {
        var recorder =
            new MqProcessingDurationMetricRecorder(registry, "DEBUG", new LayoutId(layout));
        assertTrue(recorder.detailedMetricsRequested());
        for (String outcome : List.of("SUCCESS", "FAILURE")) {
          pairs.add(layout + "/" + outcome);
          assertEquals(0, summary(registry, layout, outcome).count());
          assertEquals(0, summary(registry, layout, outcome).totalAmount());
        }
      }
      assertEquals(64, LAYOUTS.size());
      assertEquals(128, pairs.size());
      shape(registry, pairs);
      assertEquals(128, registry.registrations.get());
      assertEquals(0, registry.records.get());
      for (var config : registry.configurations) {
        assertTrue(config.isPercentileHistogram());
        assertArrayEquals(new double[0], config.getPercentiles());
        assertArrayEquals(
            new double[] {.001, .01, .1, 1., 1.5}, config.getServiceLevelObjectiveBoundaries());
      }
    }
  }

  @Test
  void mqTime002FractionalSecondsCdfAndTwoMaximumSamplesUseIndependentFixedVectors() {
    try (var registry = new Registry()) {
      var recorder =
          new MqProcessingDurationMetricRecorder(registry, "DEBUG", new LayoutId("LGNREQ01"));
      for (var outcome : List.of(Outcome.SUCCESS, Outcome.FAILURE)) {
        for (long ns : List.of(0L, 1L, 500000000L, 1500000000L)) recorder.record(outcome, ns);
        var v = summary(registry, "LGNREQ01", outcome.name());
        assertEquals(4, v.count());
        assertEquals(2.000000001, v.totalAmount(), 1e-15);
        assertEquals(1.5, v.max());
        var counts = new HashMap<Double, Double>();
        for (var b : v.takeSnapshot().histogramCounts()) counts.put(b.bucket(), b.count());
        assertEquals(2., counts.get(.001).doubleValue());
        assertEquals(2., counts.get(.01).doubleValue());
        assertEquals(2., counts.get(.1).doubleValue());
        assertEquals(3., counts.get(1.).doubleValue());
        assertEquals(4., counts.get(1.5).doubleValue());
      }
    }
    try (var registry = new Registry()) {
      var recorder =
          new MqProcessingDurationMetricRecorder(registry, "DEBUG", new LayoutId("WLGEVT01"));
      recorder.record(Outcome.SUCCESS, Long.MAX_VALUE);
      recorder.record(Outcome.SUCCESS, Long.MAX_VALUE);
      var value = summary(registry, "WLGEVT01", "SUCCESS");
      assertEquals(2, value.count());
      assertEquals(1.8446744073709553E10, value.totalAmount());
      assertEquals(9.223372036854776E9, value.max());
      assertTrue(Double.isFinite(value.totalAmount()));
      assertEquals(0, summary(registry, "WLGEVT01", "FAILURE").count());
    }
  }

  @Test
  void mqTime003ClosedOutcomeFactoriesAndUnknownLayoutCannotRegisterArbitraryNamespace() {
    assertEquals(Outcome.SUCCESS, Outcome.parse("SUCCESS"));
    assertEquals(Outcome.FAILURE, Outcome.parse("FAILURE"));
    assertThrows(NullPointerException.class, () -> Outcome.parse(null));
    for (String bad : List.of("", "success", "unknown"))
      assertThrows(IllegalArgumentException.class, () -> Outcome.parse(bad));
    assertArrayEquals(new Outcome[] {Outcome.SUCCESS, Outcome.FAILURE}, Outcome.values());
    var values = Outcome.values();
    values[0] = Outcome.FAILURE;
    assertArrayEquals(new Outcome[] {Outcome.SUCCESS, Outcome.FAILURE}, Outcome.values());
    assertEquals(Outcome.SUCCESS, Outcome.valueOf("SUCCESS"));
    assertEquals(Outcome.FAILURE, Outcome.valueOf("FAILURE"));
    assertThrows(NullPointerException.class, () -> Outcome.valueOf(null));
    assertThrows(IllegalArgumentException.class, () -> Outcome.valueOf("UNKNOWN"));
    try (var registry = new Registry()) {
      for (String mode : List.of("DEBUG", "STANDARD")) {
        assertThrows(
            NullPointerException.class,
            () -> new MqProcessingDurationMetricRecorder(registry, mode, null));
        assertThrows(
            UnsupportedLayoutException.class,
            () -> new MqProcessingDurationMetricRecorder(registry, mode, new LayoutId("UNKNOWN1")));
      }
      assertEquals(0, registry.registrations.get());
      assertEquals(0, registry.getMeters().size());
    }
  }

  @Test
  void mqTime004NullNegativeAndStandardNeverRecordOrChooseDefaultMode() {
    try (var registry = new Registry()) {
      assertThrows(
          NullPointerException.class,
          () -> new MqProcessingDurationMetricRecorder(null, "DEBUG", new LayoutId("LGNREQ01")));
      assertThrows(
          NullPointerException.class,
          () -> new MqProcessingDurationMetricRecorder(registry, null, new LayoutId("LGNREQ01")));
      for (String mode : List.of("", "debug", "unknown"))
        assertEquals(
            "CONFIG_INVALID",
            assertThrows(
                    IllegalArgumentException.class,
                    () ->
                        new MqProcessingDurationMetricRecorder(
                            registry, mode, new LayoutId("LGNREQ01")))
                .getMessage());
      assertEquals(0, registry.registrations.get());
    }
    for (String mode : List.of("DEBUG", "STANDARD"))
      try (var registry = new Registry()) {
        var recorder =
            new MqProcessingDurationMetricRecorder(registry, mode, new LayoutId("LGNREQ01"));
        assertEquals(mode.equals("DEBUG"), recorder.detailedMetricsRequested());
        assertThrows(NullPointerException.class, () -> recorder.record(null, 0));
        for (var outcome : List.of(Outcome.SUCCESS, Outcome.FAILURE)) {
          for (long invalid : List.of(-1L, Long.MIN_VALUE))
            assertThrows(IllegalArgumentException.class, () -> recorder.record(outcome, invalid));
          recorder.record(outcome, Long.MAX_VALUE);
        }
        if (mode.equals("STANDARD")) {
          assertEquals(0, registry.getMeters().size());
          assertEquals(0, registry.records.get());
        } else {
          assertEquals(2, registry.records.get());
          shape(registry, Set.of("LGNREQ01/SUCCESS", "LGNREQ01/FAILURE"));
        }
      }
  }

  @Test
  void mqTime005PartialFactoryFailurePreservesIdentityPrefixAndCallerOwnership() {
    for (var problem :
        List.<Throwable>of(new Unformattable(), new AssertionError("owned factory"))) {
      var registry = new Registry();
      registry.factoryFailure = Optional.of(problem);
      try {
        assertSame(
            problem,
            assertThrows(
                problem.getClass(),
                () ->
                    new MqProcessingDurationMetricRecorder(
                        registry, "DEBUG", new LayoutId("LGNREQ01"))));
        assertEquals(2, registry.registrations.get());
        shape(registry, Set.of("LGNREQ01/SUCCESS"));
        assertEquals(0, registry.records.get());
        assertEquals(0, registry.closes.get());
      } finally {
        registry.close();
      }
      assertEquals(1, registry.closes.get());
    }
  }

  @Test
  void mqTime006RecordFailureBeforeOrAfterIncrementNeverRetriesOrCompensates() {
    for (var problem : List.<Throwable>of(new Unformattable(), new AssertionError("owned record")))
      for (boolean after : List.of(false, true))
        try (var registry = new Registry()) {
          var recorder =
              new MqProcessingDurationMetricRecorder(registry, "DEBUG", new LayoutId("LGNREQ01"));
          registry.recordFailure = Optional.of(problem);
          registry.failAfter = after;
          assertSame(
              problem,
              assertThrows(problem.getClass(), () -> recorder.record(Outcome.FAILURE, 500000000)));
          assertEquals(1, registry.records.get());
          assertEquals(after ? 1 : 0, summary(registry, "LGNREQ01", "FAILURE").count());
          assertEquals(after ? .5 : 0, summary(registry, "LGNREQ01", "FAILURE").totalAmount());
          assertEquals(0, summary(registry, "LGNREQ01", "SUCCESS").count());
          assertEquals(0, registry.closes.get());
        }
  }

  @Test
  void mqTime007ConcurrentCountsSumsAndMaxUseIndependentIntegerVectorsAndSeparateLayoutOwners()
      throws Exception {
    try (var registry = new Registry();
        var other = new Registry();
        var executor = Executors.newFixedThreadPool(8)) {
      var a = new MqProcessingDurationMetricRecorder(registry, "DEBUG", new LayoutId("QSBREQ01"));
      var b = new MqProcessingDurationMetricRecorder(registry, "DEBUG", new LayoutId("QWKREQ01"));
      var jobs = new ArrayList<Callable<Void>>();
      var sums = new HashMap<String, Long>();
      var counts = new HashMap<String, Long>();
      var max = new HashMap<String, Long>();
      for (int i = 0; i < 64; i++) {
        String layout = i % 2 == 0 ? "QSBREQ01" : "QWKREQ01";
        var target = i % 2 == 0 ? a : b;
        var outcome = (i / 2) % 2 == 0 ? Outcome.SUCCESS : Outcome.FAILURE;
        long ns = i * 1000000L;
        String key = layout + "/" + outcome.name();
        sums.merge(key, ns, Long::sum);
        counts.merge(key, 1L, Long::sum);
        max.merge(key, ns, Long::max);
        jobs.add(
            () -> {
              target.record(outcome, ns);
              return null;
            });
      }
      for (var f : executor.invokeAll(jobs, 5, TimeUnit.SECONDS)) f.get(5, TimeUnit.SECONDS);
      for (String layout : List.of("QSBREQ01", "QWKREQ01"))
        for (String outcome : List.of("SUCCESS", "FAILURE")) {
          var value = summary(registry, layout, outcome);
          String key = layout + "/" + outcome;
          assertEquals(counts.get(key).longValue(), value.count());
          assertEquals(sums.get(key) / 1e9, value.totalAmount(), 1e-12);
          assertEquals(max.get(key) / 1e9, value.max());
        }
      new MqProcessingDurationMetricRecorder(other, "DEBUG", new LayoutId("QWKREQ01"))
          .record(Outcome.SUCCESS, 250000000);
      assertEquals(1, summary(other, "QWKREQ01", "SUCCESS").count());
      assertEquals(.25, summary(other, "QWKREQ01", "SUCCESS").totalAmount());
      assertEquals(64, registry.records.get());
    }
  }

  @Test
  void mqTime008ForeignCounterCannotBecomeSummaryOrBeClosed() {
    try (var registry = new Registry()) {
      var foreign =
          Counter.builder("nk_mq_processing_duration_seconds")
              .tags("flow", "SYNCHRONOUS", "layout", "LGNREQ01", "outcome", "SUCCESS")
              .register(registry);
      foreign.increment(7);
      assertThrows(
          IllegalArgumentException.class,
          () ->
              new MqProcessingDurationMetricRecorder(registry, "DEBUG", new LayoutId("LGNREQ01")));
      assertSame(
          foreign,
          registry
              .get("nk_mq_processing_duration_seconds")
              .tags("flow", "SYNCHRONOUS", "layout", "LGNREQ01", "outcome", "SUCCESS")
              .counter());
      assertEquals(7, foreign.count());
      assertEquals(0, registry.closes.get());
    }
  }

  @Test
  void mqTime009ExtremeRangeOrdersKeepIndependentSmallBucketCountsAndFiniteTotals() {
    for (var vector :
        List.of(
            List.of(0L, 1L, Long.MAX_VALUE, Long.MAX_VALUE, 1L),
            List.of(Long.MAX_VALUE, Long.MAX_VALUE, 1L, 0L, 1L)))
      for (String layout : List.of("LGNREQ01", "WLGEVT01"))
        for (var outcome : List.of(Outcome.SUCCESS, Outcome.FAILURE))
          try (var registry = new Registry()) {
            var recorder =
                new MqProcessingDurationMetricRecorder(registry, "DEBUG", new LayoutId(layout));
            for (long ns : vector) recorder.record(outcome, ns);
            var value = summary(registry, layout, outcome.name());
            assertEquals(5, value.count());
            assertEquals(1.8446744073709553E10, value.totalAmount());
            assertEquals(9.223372036854776E9, value.max());
            var buckets = new HashMap<Double, Double>();
            for (var item : value.takeSnapshot().histogramCounts())
              buckets.put(item.bucket(), item.count());
            assertEquals(Set.of(.001, .01, .1, 1., 1.5), buckets.keySet());
            for (double boundary : List.of(.001, .01, .1, 1., 1.5))
              assertEquals(3.0, buckets.get(boundary).doubleValue());
            assertEquals(5, registry.records.get());
            assertEquals(0, registry.closes.get());
          }
  }
}
