package dev.codex.schubert.nk.api.monitoring;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.api.monitoring.DbQueryDurationMetricRecorder.Outcome;
import dev.codex.schubert.nk.api.monitoring.DbQueryDurationMetricRecorder.Query;
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
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.concurrent.Callable;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.stream.Collectors;
import org.junit.jupiter.api.Test;

/** DBTIME001..008/1712; own clock/SDK and scalar durations only, never SQL or actual clocks. */
class DbQueryDurationMetricRecorderTest {
  private static final int FAILURE_FACTORY_CALL = 2;
  private static final String DB_DURATION_NAME = "nk_db_query_duration_seconds";
  private static final String QUERY_LABEL = "query_id";
  private static final String OUTCOME_LABEL = "outcome";
  private static final String DEBUG_MODE = "DEBUG";
  private static final String ASYNC_COUNT_QUERY = "ASYNC_JOB_STATE_COUNTS";
  private static final String OUTBOX_COUNT_QUERY = "OUTBOX_STATUS_COUNTS_OLDEST";
  private static final String SUCCESS_OUTCOME = "SUCCESS";
  private static final String FAILURE_OUTCOME = "FAILURE";
  private static final List<Query> QUERIES =
      List.of(Query.ASYNC_JOB_STATE_COUNTS, Query.OUTBOX_STATUS_COUNTS_OLDEST);
  private static final List<Outcome> OUTCOMES = List.of(Outcome.SUCCESS, Outcome.FAILURE);

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
      if (registrations.incrementAndGet() == FAILURE_FACTORY_CALL) fail(factoryFailure);
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

  private static DistributionSummary summary(Registry registry, String query, String outcome) {
    return registry
        .get(DB_DURATION_NAME)
        .tags(QUERY_LABEL, query, OUTCOME_LABEL, outcome)
        .summary();
  }

  private static void shape(Registry registry) {
    shape(
        registry,
        Set.of(
            "ASYNC_JOB_STATE_COUNTS/SUCCESS",
            "ASYNC_JOB_STATE_COUNTS/FAILURE",
            "OUTBOX_STATUS_COUNTS_OLDEST/SUCCESS",
            "OUTBOX_STATUS_COUNTS_OLDEST/FAILURE"));
  }

  private static void shape(Registry registry, Set<String> pairs) {
    // SDK-generated gauges are checked separately, never silently filtered out of the denominator.
    assertEquals(pairs.size() * 6, registry.getMeters().size());
    var actual = new java.util.HashSet<String>();
    var auxiliary = new java.util.HashSet<String>();
    for (var meter : registry.getMeters()) {
      var id = meter.getId();
      var pair = id.getTag(QUERY_LABEL) + "/" + id.getTag(OUTCOME_LABEL);
      assertTrue(pairs.contains(pair));
      if (id.getName().equals(DB_DURATION_NAME)) {
        assertEquals(Meter.Type.DISTRIBUTION_SUMMARY, id.getType());
        assertEquals("seconds", id.getBaseUnit());
        assertEquals(
            Set.of(QUERY_LABEL, OUTCOME_LABEL),
            id.getTags().stream().map(t -> t.getKey()).collect(Collectors.toSet()));
        assertTrue(actual.add(pair));
      } else {
        assertEquals(Meter.Type.GAUGE, id.getType());
        assertEquals("nk_db_query_duration_seconds.histogram", id.getName());
        String label = "le";
        assertEquals(
            Set.of(QUERY_LABEL, OUTCOME_LABEL, label),
            id.getTags().stream().map(t -> t.getKey()).collect(Collectors.toSet()));
        assertTrue(auxiliary.add(pair + "/" + label + "/" + id.getTag(label)));
      }
    }
    assertEquals(pairs, actual);
    var expectedAuxiliary = new java.util.HashSet<String>();
    for (String pair : pairs) {
      for (String boundary : List.of("0.001", "0.01", "0.1", "1", "1.5"))
        expectedAuxiliary.add(pair + "/le/" + boundary);
    }
    assertEquals(expectedAuxiliary, auxiliary);
  }

  @Test
  void dbTime001ExactlyFourFixedSeriesRequestHistogramSecondsAndFiveObservationBuckets() {
    try (var registry = new Registry()) {
      var recorder = new DbQueryDurationMetricRecorder(registry, DEBUG_MODE);
      assertTrue(recorder.detailedMetricsRequested());
      shape(registry);
      assertEquals(4, registry.registrations.get());
      assertEquals(4, registry.configurations.size());
      for (var config : registry.configurations) {
        assertEquals(Boolean.TRUE, config.isPercentileHistogram());
        assertTrue(config.isPublishingHistogram());
        assertArrayEquals(new double[0], config.getPercentiles());
        assertArrayEquals(
            new double[] {.001, .01, .1, 1., 1.5}, config.getServiceLevelObjectiveBoundaries());
      }
      for (String query : List.of(ASYNC_COUNT_QUERY, OUTBOX_COUNT_QUERY))
        for (String outcome : List.of(SUCCESS_OUTCOME, FAILURE_OUTCOME)) {
          var value = summary(registry, query, outcome);
          assertEquals(0, value.count());
          assertEquals(0, value.totalAmount());
        }
      assertEquals(0, registry.records.get());
      assertEquals(0, registry.closes.get());
    }
  }

  @Test
  void dbTime002IndependentSecondsHistogramCdfAndTwoMaximumSamplesNeverLongWrap() {
    try (var registry = new Registry()) {
      var recorder = new DbQueryDurationMetricRecorder(registry, DEBUG_MODE);
      for (var query : QUERIES)
        for (var outcome : OUTCOMES) {
          for (long ns : List.of(0L, 1L, 500000000L, 1500000000L))
            recorder.record(query, outcome, ns);
          var value = summary(registry, query.name(), outcome.name());
          assertEquals(4, value.count());
          assertEquals(2.000000001, value.totalAmount(), 1e-15);
          assertEquals(1.5, value.max());
          Map<Double, Double> counts = new HashMap<>();
          for (var bucket : value.takeSnapshot().histogramCounts())
            counts.put(bucket.bucket(), bucket.count());
          assertEquals(2.0, counts.get(.001).doubleValue());
          assertEquals(2.0, counts.get(.01).doubleValue());
          assertEquals(2.0, counts.get(.1).doubleValue());
          assertEquals(3.0, counts.get(1.0).doubleValue());
          assertEquals(4.0, counts.get(1.5).doubleValue());
        }
      shape(registry);
    }
    try (var registry = new Registry()) {
      var recorder = new DbQueryDurationMetricRecorder(registry, DEBUG_MODE);
      recorder.record(Query.ASYNC_JOB_STATE_COUNTS, Outcome.SUCCESS, Long.MAX_VALUE);
      var value = summary(registry, ASYNC_COUNT_QUERY, SUCCESS_OUTCOME);
      assertEquals(1, value.count());
      assertEquals(9.223372036854776E9, value.totalAmount());
      recorder.record(Query.ASYNC_JOB_STATE_COUNTS, Outcome.SUCCESS, Long.MAX_VALUE);
      assertEquals(2, value.count());
      assertEquals(1.8446744073709553E10, value.totalAmount());
      assertTrue(Double.isFinite(value.totalAmount()));
      assertEquals(9.223372036854776E9, value.max());
      assertEquals(0, summary(registry, ASYNC_COUNT_QUERY, FAILURE_OUTCOME).count());
    }
  }

  @Test
  void dbTime003QueryAndOutcomeClosedParsersAndGeneratedFactoriesUseIndependentTypedConstants() {
    assertSame(Query.ASYNC_JOB_STATE_COUNTS, Query.parse(ASYNC_COUNT_QUERY));
    assertSame(Query.OUTBOX_STATUS_COUNTS_OLDEST, Query.parse(OUTBOX_COUNT_QUERY));
    assertSame(Outcome.SUCCESS, Outcome.parse(SUCCESS_OUTCOME));
    assertSame(Outcome.FAILURE, Outcome.parse(FAILURE_OUTCOME));
    for (String invalid : List.of("", "async_job_state_counts", "SELECT state FROM untrusted"))
      assertEquals(
          "invalid DB metric query",
          assertThrows(IllegalArgumentException.class, () -> Query.parse(invalid)).getMessage());
    for (String invalid : List.of("", "success", "unknown-outcome"))
      assertEquals(
          "invalid DB metric outcome",
          assertThrows(IllegalArgumentException.class, () -> Outcome.parse(invalid)).getMessage());
    assertThrows(NullPointerException.class, () -> Query.parse(null));
    assertThrows(NullPointerException.class, () -> Outcome.parse(null));
    Query[] queries = {Query.ASYNC_JOB_STATE_COUNTS, Query.OUTBOX_STATUS_COUNTS_OLDEST};
    Outcome[] outcomes = {Outcome.SUCCESS, Outcome.FAILURE};
    assertArrayEquals(queries, Query.values());
    assertArrayEquals(outcomes, Outcome.values());
    var mutableQueries = Query.values();
    mutableQueries[0] = Query.OUTBOX_STATUS_COUNTS_OLDEST;
    var mutableOutcomes = Outcome.values();
    mutableOutcomes[0] = Outcome.FAILURE;
    assertArrayEquals(queries, Query.values());
    assertArrayEquals(outcomes, Outcome.values());
    assertSame(Query.ASYNC_JOB_STATE_COUNTS, Query.valueOf(ASYNC_COUNT_QUERY));
    assertSame(Query.OUTBOX_STATUS_COUNTS_OLDEST, Query.valueOf(OUTBOX_COUNT_QUERY));
    assertSame(Outcome.SUCCESS, Outcome.valueOf(SUCCESS_OUTCOME));
    assertSame(Outcome.FAILURE, Outcome.valueOf(FAILURE_OUTCOME));
    assertThrows(IllegalArgumentException.class, () -> Query.valueOf("unknown-query"));
    assertThrows(IllegalArgumentException.class, () -> Outcome.valueOf("unknown-outcome"));
    assertThrows(NullPointerException.class, () -> Query.valueOf(null));
    assertThrows(NullPointerException.class, () -> Outcome.valueOf(null));
  }

  @Test
  void dbTime004NullNegativeAndUnknownModeNeverRecordAndStandardStoresNoDetailedSamples() {
    for (String mode : List.of(DEBUG_MODE, "STANDARD"))
      try (var registry = new Registry()) {
        var recorder = new DbQueryDurationMetricRecorder(registry, mode);
        recorder.record(Query.ASYNC_JOB_STATE_COUNTS, Outcome.SUCCESS, 250000000);
        int before = registry.records.get();
        assertThrows(NullPointerException.class, () -> recorder.record(null, Outcome.SUCCESS, 1));
        assertThrows(
            NullPointerException.class,
            () -> recorder.record(Query.ASYNC_JOB_STATE_COUNTS, null, 1));
        for (long invalid : List.of(-1L, Long.MIN_VALUE))
          assertThrows(
              IllegalArgumentException.class,
              () -> recorder.record(Query.ASYNC_JOB_STATE_COUNTS, Outcome.SUCCESS, invalid));
        assertEquals(before, registry.records.get());
        assertEquals(0, registry.closes.get());
        if (mode.equals(DEBUG_MODE)) {
          assertTrue(recorder.detailedMetricsRequested());
          assertEquals(.25, summary(registry, ASYNC_COUNT_QUERY, SUCCESS_OUTCOME).totalAmount());
          shape(registry);
        } else {
          assertFalse(recorder.detailedMetricsRequested());
          for (var query : QUERIES)
            for (var outcome : OUTCOMES) recorder.record(query, outcome, Long.MAX_VALUE);
          assertEquals(0, registry.records.get());
          assertEquals(0, registry.getMeters().size());
        }
      }
    try (var registry = new Registry()) {
      assertThrows(
          NullPointerException.class, () -> new DbQueryDurationMetricRecorder(null, DEBUG_MODE));
      assertThrows(
          NullPointerException.class, () -> new DbQueryDurationMetricRecorder(registry, null));
      for (String mode : List.of("", "debug", "unknown-mode"))
        assertEquals(
            "CONFIG_INVALID",
            assertThrows(
                    IllegalArgumentException.class,
                    () -> new DbQueryDurationMetricRecorder(registry, mode))
                .getMessage());
      assertEquals(0, registry.registrations.get());
    }
  }

  @Test
  void dbTime005PartialFactoryFailurePreservesOriginalProblemAndCallerRegistryOwnership() {
    for (var problem :
        List.<Throwable>of(new Unformattable(), new AssertionError("owned summary factory"))) {
      var registry = new Registry();
      registry.factoryFailure = Optional.of(problem);
      try {
        assertSame(
            problem,
            assertThrows(
                problem.getClass(), () -> new DbQueryDurationMetricRecorder(registry, DEBUG_MODE)));
        assertEquals(2, registry.registrations.get());
        shape(registry, Set.of("ASYNC_JOB_STATE_COUNTS/SUCCESS"));
        assertEquals(0, summary(registry, ASYNC_COUNT_QUERY, SUCCESS_OUTCOME).count());
        assertEquals(0, registry.records.get());
        assertEquals(0, registry.closes.get());
      } finally {
        registry.close();
      }
      assertEquals(1, registry.closes.get());
    }
  }

  @Test
  void dbTime006FailureBeforeOrAfterSampleNeverRetriesCompensatesOrNormalizesSuccess() {
    for (var problem : List.<Throwable>of(new Unformattable(), new AssertionError("owned record")))
      for (boolean after : List.of(false, true)) {
        var registry = new Registry();
        try {
          var recorder = new DbQueryDurationMetricRecorder(registry, DEBUG_MODE);
          registry.recordFailure = Optional.of(problem);
          registry.failAfter = after;
          assertSame(
              problem,
              assertThrows(
                  problem.getClass(),
                  () ->
                      recorder.record(Query.ASYNC_JOB_STATE_COUNTS, Outcome.SUCCESS, 1500000000)));
          assertEquals(1, registry.records.get());
          var value = summary(registry, ASYNC_COUNT_QUERY, SUCCESS_OUTCOME);
          assertEquals(after ? 1 : 0, value.count());
          assertEquals(after ? 1.5 : 0, value.totalAmount());
          assertEquals(0, summary(registry, ASYNC_COUNT_QUERY, FAILURE_OUTCOME).count());
          assertEquals(0, registry.closes.get());
          shape(registry);
        } finally {
          registry.close();
        }
        assertEquals(1, registry.closes.get());
      }
  }

  @Test
  void dbTime007ConcurrentSampleCountSumAndMaximumUsePrecomputedIntegerInputs() throws Exception {
    try (var registry = new Registry();
        var otherRegistry = new Registry()) {
      var executor = Executors.newFixedThreadPool(8);
      try {
        var recorder = new DbQueryDurationMetricRecorder(registry, DEBUG_MODE);
        Map<String, Long> counts = new HashMap<>();
        Map<String, Long> sums = new HashMap<>();
        Map<String, Long> maxima = new HashMap<>();
        var tasks = new ArrayList<Callable<Void>>();
        for (int index = 0; index < 64; index++) {
          var query = QUERIES.get(index % 2);
          var outcome = OUTCOMES.get((index / 2) % 2);
          long ns = (index + 1L) * 1000000;
          String key = query.name() + "/" + outcome.name();
          counts.merge(key, 1L, Long::sum);
          sums.merge(key, ns, Long::sum);
          maxima.merge(key, ns, Long::max);
          tasks.add(
              () -> {
                recorder.record(query, outcome, ns);
                return null;
              });
        }
        for (var result : executor.invokeAll(tasks, 10, TimeUnit.SECONDS))
          result.get(5, TimeUnit.SECONDS);
        for (String query : List.of(ASYNC_COUNT_QUERY, OUTBOX_COUNT_QUERY))
          for (String outcome : List.of(SUCCESS_OUTCOME, FAILURE_OUTCOME)) {
            String key = query + "/" + outcome;
            var value = summary(registry, query, outcome);
            assertEquals(counts.get(key).longValue(), value.count());
            assertEquals(sums.get(key) / 1000000000.0, value.totalAmount(), 1e-12);
            assertEquals(maxima.get(key) / 1000000000.0, value.max());
          }
        assertEquals(64, registry.records.get());
        var other = new DbQueryDurationMetricRecorder(otherRegistry, DEBUG_MODE);
        other.record(Query.ASYNC_JOB_STATE_COUNTS, Outcome.SUCCESS, 250000000);
        assertEquals(.25, summary(otherRegistry, ASYNC_COUNT_QUERY, SUCCESS_OUTCOME).totalAmount());
        assertEquals(
            sums.get("ASYNC_JOB_STATE_COUNTS/SUCCESS") / 1000000000.0,
            summary(registry, ASYNC_COUNT_QUERY, SUCCESS_OUTCOME).totalAmount(),
            1e-12);
        shape(registry);
        shape(otherRegistry);
      } finally {
        executor.shutdownNow();
        assertTrue(executor.awaitTermination(10, TimeUnit.SECONDS));
      }
    }
  }

  @Test
  void dbTime008ForeignCounterCannotBeReplacedBySummaryOrClosed() {
    try (var registry = new Registry()) {
      var foreign =
          Counter.builder(DB_DURATION_NAME)
              .tags(QUERY_LABEL, ASYNC_COUNT_QUERY, OUTCOME_LABEL, SUCCESS_OUTCOME)
              .register(registry);
      foreign.increment(7);
      assertThrows(
          IllegalArgumentException.class,
          () -> new DbQueryDurationMetricRecorder(registry, DEBUG_MODE));
      assertSame(
          foreign,
          registry
              .get(DB_DURATION_NAME)
              .tags(QUERY_LABEL, ASYNC_COUNT_QUERY, OUTCOME_LABEL, SUCCESS_OUTCOME)
              .counter());
      assertEquals(7, foreign.count());
      assertEquals(0, registry.closes.get());
    }
  }

  @Test
  void dbTime009ExtremeRangeOrdersKeepIndependentSmallBucketCountsAndFiniteTotals() {
    for (var vector :
        List.of(
            List.of(0L, 1L, Long.MAX_VALUE, Long.MAX_VALUE, 1L),
            List.of(Long.MAX_VALUE, Long.MAX_VALUE, 1L, 0L, 1L)))
      for (var query : QUERIES)
        for (var outcome : OUTCOMES)
          try (var registry = new Registry()) {
            var recorder = new DbQueryDurationMetricRecorder(registry, DEBUG_MODE);
            for (long ns : vector) recorder.record(query, outcome, ns);
            var value = summary(registry, query.name(), outcome.name());
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
