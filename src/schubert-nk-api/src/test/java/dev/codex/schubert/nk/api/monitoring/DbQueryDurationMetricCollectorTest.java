package dev.codex.schubert.nk.api.monitoring;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.api.monitoring.DbQueryDurationMetricCollector.Observation;
import dev.codex.schubert.nk.api.monitoring.DbQueryDurationMetricRecorder.Outcome;
import dev.codex.schubert.nk.api.monitoring.DbQueryDurationMetricRecorder.Query;
import io.micrometer.core.instrument.Clock;
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
import java.util.concurrent.Callable;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicReference;
import java.util.function.Function;
import org.junit.jupiter.api.Test;

/**
 * DBCONN001..008/1714. Independent integer vectors and own providers/threads, no DB or real clock.
 */
class DbQueryDurationMetricCollectorTest {
  private static final String FIXTURE_DEBUG_B6DFBABB = "DEBUG";
  private static final List<Query> QUERIES =
      List.of(Query.ASYNC_JOB_STATE_COUNTS, Query.OUTBOX_STATUS_COUNTS_OLDEST);
  private static final List<Outcome> OUTCOMES = List.of(Outcome.SUCCESS, Outcome.FAILURE);

  private static final class Registry extends SimpleMeterRegistry
      implements AutoCloseable, ExactDurationSupport {
    final AtomicInteger closes = new AtomicInteger();
    final AtomicInteger factories = new AtomicInteger();
    final AtomicInteger records = new AtomicInteger();
    Optional<Throwable> factoryFailure = Optional.empty();
    Optional<Throwable> recordFailure = Optional.empty();

    Registry() {
      super(
          SimpleConfig.DEFAULT,
          new Clock() {
            public long wallTime() {
              return 1000;
            }

            public long monotonicTime() {
              return 1000000;
            }
          });
    }

    @Override
    protected DistributionSummary newDistributionSummary(
        Meter.Id id, DistributionStatisticConfig config, double scale) {
      if (factories.incrementAndGet() == 2) fail(factoryFailure);
      var delegate = ExactDurationMeterRegistry.exactDurationSummary(this, id, config, scale);
      return new DistributionSummary() {
        public Meter.Id getId() {
          return delegate.getId();
        }

        public long count() {
          return delegate.count();
        }

        public double totalAmount() {
          return delegate.totalAmount();
        }

        public double max() {
          return delegate.max();
        }

        public HistogramSnapshot takeSnapshot() {
          return delegate.takeSnapshot();
        }

        public void record(double value) {
          records.incrementAndGet();
          delegate.record(value);
          fail(recordFailure);
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
      throw new AssertionError("provider text forbidden");
    }

    @Override
    public String toString() {
      throw new AssertionError("provider format forbidden");
    }
  }

  private static void fail(Optional<Throwable> failure) {
    if (failure.isPresent()) {
      var problem = failure.orElseThrow();
      if (problem instanceof Error fatal) throw fatal;
      throw (RuntimeException) problem;
    }
  }

  private static DistributionSummary summary(Registry registry, Query query, Outcome outcome) {
    return registry
        .get("nk_db_query_duration_seconds")
        .tags("query_id", query.name(), "outcome", outcome.name())
        .summary();
  }

  private static void await(CountDownLatch latch) {
    try {
      assertTrue(latch.await(5, TimeUnit.SECONDS));
    } catch (InterruptedException interrupted) {
      Thread.currentThread().interrupt();
      throw new AssertionError("owned fixture interrupted", interrupted);
    }
  }

  @Test
  void dbConn001CompleteProviderResultIsPublishedOnlyAfterAcquisitionAndSameObjectReturned() {
    try (var registry = new Registry()) {
      var calls = new AtomicInteger();
      var supplied = new AtomicReference<Observation>();
      var collector =
          new DbQueryDurationMetricCollector(
              query -> {
                calls.incrementAndGet();
                var value = supplied.get();
                assertEquals(0, summary(registry, query, value.outcome()).count());
                return Optional.of(value);
              },
              registry,
              FIXTURE_DEBUG_B6DFBABB);
      assertEquals(0, calls.get());
      for (var query : QUERIES)
        for (var outcome : OUTCOMES) {
          var value = new Observation(outcome, 500000000);
          supplied.set(value);
          assertSame(value, collector.collect(query).orElseThrow());
          assertEquals(1, summary(registry, query, outcome).count());
          assertEquals(.5, summary(registry, query, outcome).totalAmount());
        }
      assertEquals(4, calls.get());
      assertEquals(4, registry.records.get());
      assertEquals(0, registry.closes.get());
    }
  }

  @Test
  void dbConn002MissingObservationNeverInventsZeroOrOutcomeAndTrueZeroIsOneSuppliedEvent() {
    try (var registry = new Registry()) {
      var supplied = new AtomicReference<Optional<Observation>>(Optional.empty());
      var calls = new AtomicInteger();
      var collector =
          new DbQueryDurationMetricCollector(
              query -> {
                calls.incrementAndGet();
                return supplied.get();
              },
              registry,
              FIXTURE_DEBUG_B6DFBABB);
      for (var query : QUERIES) {
        assertTrue(collector.collect(query).isEmpty());
        for (var outcome : OUTCOMES) assertEquals(0, summary(registry, query, outcome).count());
        var value = new Observation(Outcome.FAILURE, 1);
        supplied.set(Optional.of(value));
        assertSame(value, collector.collect(query).orElseThrow());
        supplied.set(Optional.empty());
        assertTrue(collector.collect(query).isEmpty());
        assertEquals(1, summary(registry, query, Outcome.FAILURE).count());
        assertEquals(1e-9, summary(registry, query, Outcome.FAILURE).totalAmount());
        supplied.set(Optional.of(new Observation(Outcome.SUCCESS, 0)));
        collector.collect(query);
        assertEquals(1, summary(registry, query, Outcome.SUCCESS).count());
        assertEquals(0, summary(registry, query, Outcome.SUCCESS).totalAmount());
        supplied.set(Optional.empty());
      }
      assertEquals(8, calls.get());
      assertEquals(4, registry.records.get());
    }
  }

  @Test
  void dbConn003RuntimeErrorAndNullProviderResultPropagateWithoutInventedFailureSample() {
    for (var problem :
        List.<Throwable>of(new Unformattable(), new AssertionError("owned provider"))) {
      try (var registry = new Registry()) {
        var broken = new AtomicReference<>(false);
        var calls = new AtomicInteger();
        var collector =
            new DbQueryDurationMetricCollector(
                query -> {
                  calls.incrementAndGet();
                  if (broken.get()) {
                    fail(Optional.of(problem));
                  }
                  return Optional.of(new Observation(Outcome.SUCCESS, 250000000));
                },
                registry,
                FIXTURE_DEBUG_B6DFBABB);
        collector.collect(Query.ASYNC_JOB_STATE_COUNTS);
        broken.set(true);
        assertSame(
            problem,
            assertThrows(
                problem.getClass(), () -> collector.collect(Query.ASYNC_JOB_STATE_COUNTS)));
        assertEquals(2, calls.get());
        assertEquals(1, registry.records.get());
        assertEquals(1, summary(registry, Query.ASYNC_JOB_STATE_COUNTS, Outcome.SUCCESS).count());
        assertEquals(
            .25, summary(registry, Query.ASYNC_JOB_STATE_COUNTS, Outcome.SUCCESS).totalAmount());
        assertEquals(0, summary(registry, Query.ASYNC_JOB_STATE_COUNTS, Outcome.FAILURE).count());
        assertEquals(0, registry.closes.get());
      }
    }
    try (var registry = new Registry()) {
      var calls = new AtomicInteger();
      var collector =
          new DbQueryDurationMetricCollector(
              query -> {
                calls.incrementAndGet();
                return null;
              },
              registry,
              FIXTURE_DEBUG_B6DFBABB);
      assertEquals(
          "DB duration observation",
          assertThrows(
                  NullPointerException.class,
                  () -> collector.collect(Query.OUTBOX_STATUS_COUNTS_OLDEST))
              .getMessage());
      assertEquals(1, calls.get());
      assertEquals(0, registry.records.get());
      assertThrows(NullPointerException.class, () -> collector.collect(null));
      assertEquals(1, calls.get());
    }
  }

  @Test
  void dbConn004StandardDoesNotReadProviderAndConstructorBoundaryNeverSubstitutesDefaults() {
    try (var registry = new Registry()) {
      var calls = new AtomicInteger();
      Function<Query, Optional<Observation>> source =
          query -> {
            calls.incrementAndGet();
            throw new AssertionError("STANDARD provider forbidden");
          };
      assertThrows(
          NullPointerException.class,
          () -> new DbQueryDurationMetricCollector(null, registry, FIXTURE_DEBUG_B6DFBABB));
      assertThrows(
          NullPointerException.class,
          () -> new DbQueryDurationMetricCollector(source, null, FIXTURE_DEBUG_B6DFBABB));
      assertThrows(
          NullPointerException.class,
          () -> new DbQueryDurationMetricCollector(source, registry, null));
      for (String mode : List.of("", "debug", "unknown"))
        assertEquals(
            "CONFIG_INVALID",
            assertThrows(
                    IllegalArgumentException.class,
                    () -> new DbQueryDurationMetricCollector(source, registry, mode))
                .getMessage());
      var collector = new DbQueryDurationMetricCollector(source, registry, "STANDARD");
      for (var query : QUERIES) assertTrue(collector.collect(query).isEmpty());
      assertThrows(NullPointerException.class, () -> collector.collect(null));
      assertEquals(0, calls.get());
      assertEquals(0, registry.factories.get());
      assertEquals(0, registry.records.get());
      assertEquals(0, registry.getMeters().size());
      assertEquals(0, registry.closes.get());
    }
  }

  @Test
  void
      dbConn005ImmutableObservationNullNegativeBoundaryAndFiveGeneratedContractsHaveIndependentOracle() {
    assertThrows(NullPointerException.class, () -> new Observation(null, 0));
    for (long value : List.of(-1L, Long.MIN_VALUE))
      assertEquals(
          "invalid DB duration observation",
          assertThrows(
                  IllegalArgumentException.class, () -> new Observation(Outcome.SUCCESS, value))
              .getMessage());
    var first = new Observation(Outcome.SUCCESS, 1);
    var equal = new Observation(Outcome.SUCCESS, 1);
    assertEquals(Outcome.SUCCESS, first.outcome());
    assertEquals(1, first.elapsedNanoseconds());
    assertEquals(first, first);
    assertEquals(first, equal);
    assertEquals(first.hashCode(), equal.hashCode());
    assertFalse(first.equals(null));
    assertFalse(first.equals("unknown"));
    assertNotEquals(first, new Observation(Outcome.FAILURE, 1));
    assertNotEquals(first, new Observation(Outcome.SUCCESS, 0));
    assertEquals("Observation[outcome=SUCCESS, elapsedNanoseconds=1]", first.toString());
    assertEquals(
        Long.MAX_VALUE, new Observation(Outcome.FAILURE, Long.MAX_VALUE).elapsedNanoseconds());
  }

  @Test
  void dbConn006OwnedContenderBlocksUntilFirstObservationIsPublished() throws Exception {
    try (var registry = new Registry();
        var executor = Executors.newFixedThreadPool(2)) {
      var entered = new CountDownLatch(1);
      var release = new CountDownLatch(1);
      var attempted = new CountDownLatch(1);
      var contender = new AtomicReference<Thread>();
      var calls = new AtomicInteger();
      var first = new Observation(Outcome.SUCCESS, 250000000);
      var second = new Observation(Outcome.FAILURE, 500000000);
      var collector =
          new DbQueryDurationMetricCollector(
              query -> {
                if (calls.incrementAndGet() == 1) {
                  entered.countDown();
                  await(release);
                  return Optional.of(first);
                }
                assertEquals(1, summary(registry, query, Outcome.SUCCESS).count());
                assertEquals(.25, summary(registry, query, Outcome.SUCCESS).totalAmount());
                return Optional.of(second);
              },
              registry,
              FIXTURE_DEBUG_B6DFBABB);
      var a = executor.submit(() -> collector.collect(Query.ASYNC_JOB_STATE_COUNTS));
      try {
        await(entered);
        var b =
            executor.submit(
                () -> {
                  contender.set(Thread.currentThread());
                  attempted.countDown();
                  return collector.collect(Query.ASYNC_JOB_STATE_COUNTS);
                });
        await(attempted);
        long deadline = System.nanoTime() + TimeUnit.SECONDS.toNanos(5);
        while (contender.get().getState() != Thread.State.BLOCKED && System.nanoTime() < deadline)
          Thread.onSpinWait();
        assertEquals(Thread.State.BLOCKED, contender.get().getState());
        assertEquals(1, calls.get());
        assertEquals(0, registry.records.get());
        release.countDown();
        assertSame(first, a.get(5, TimeUnit.SECONDS).orElseThrow());
        assertSame(second, b.get(5, TimeUnit.SECONDS).orElseThrow());
      } finally {
        release.countDown();
      }
      assertEquals(2, calls.get());
      assertEquals(2, registry.records.get());
      assertEquals(1, summary(registry, Query.ASYNC_JOB_STATE_COUNTS, Outcome.FAILURE).count());
      assertEquals(
          .5, summary(registry, Query.ASYNC_JOB_STATE_COUNTS, Outcome.FAILURE).totalAmount());
    }
  }

  @Test
  void dbConn007ConcurrentSamplesUsePrecomputedIdentityInputsAndSeparateOwners() throws Exception {
    try (var registry = new Registry();
        var other = new Registry();
        var executor = Executors.newFixedThreadPool(8)) {
      var inputs = new ArrayList<Observation>();
      var sums = new HashMap<String, Long>();
      var counts = new HashMap<String, Long>();
      var requested = new ThreadLocal<Observation>();
      var calls = new AtomicInteger();
      var collector =
          new DbQueryDurationMetricCollector(
              query -> {
                calls.incrementAndGet();
                return Optional.of(requested.get());
              },
              registry,
              FIXTURE_DEBUG_B6DFBABB);
      var jobs = new ArrayList<Callable<Optional<Observation>>>();
      for (int i = 0; i < 64; i++) {
        var query = QUERIES.get(i % 2);
        var outcome = OUTCOMES.get((i / 2) % 2);
        var value = new Observation(outcome, i * 1000000L);
        inputs.add(value);
        String key = query.name() + "/" + outcome.name();
        sums.merge(key, i * 1000000L, Long::sum);
        counts.merge(key, 1L, Long::sum);
        jobs.add(
            () -> {
              requested.set(value);
              try {
                return collector.collect(query);
              } finally {
                requested.remove();
              }
            });
      }
      var futures = executor.invokeAll(jobs, 5, TimeUnit.SECONDS);
      for (int i = 0; i < 64; i++)
        assertSame(inputs.get(i), futures.get(i).get(5, TimeUnit.SECONDS).orElseThrow());
      for (var query : QUERIES)
        for (var outcome : OUTCOMES) {
          String key = query.name() + "/" + outcome.name();
          assertEquals(counts.get(key).longValue(), summary(registry, query, outcome).count());
          assertEquals(sums.get(key) / 1e9, summary(registry, query, outcome).totalAmount(), 1e-12);
        }
      var independent =
          new DbQueryDurationMetricCollector(
              query -> Optional.of(new Observation(Outcome.SUCCESS, 1000000000)),
              other,
              FIXTURE_DEBUG_B6DFBABB);
      independent.collect(Query.ASYNC_JOB_STATE_COUNTS);
      assertEquals(1, summary(other, Query.ASYNC_JOB_STATE_COUNTS, Outcome.SUCCESS).count());
      assertEquals(1, summary(other, Query.ASYNC_JOB_STATE_COUNTS, Outcome.SUCCESS).totalAmount());
      assertEquals(64, calls.get());
      assertEquals(64, registry.records.get());
    }
  }

  @Test
  void dbConn008RegistryFailureKeepsPartialEffectsOriginalProblemAndBorrowedOwnership() {
    for (var problem : List.<Throwable>of(new Unformattable(), new AssertionError("owned SDK"))) {
      var registry = new Registry();
      var calls = new AtomicInteger();
      registry.factoryFailure = Optional.of(problem);
      try {
        assertSame(
            problem,
            assertThrows(
                problem.getClass(),
                () ->
                    new DbQueryDurationMetricCollector(
                        query -> {
                          calls.incrementAndGet();
                          return Optional.empty();
                        },
                        registry,
                        FIXTURE_DEBUG_B6DFBABB)));
        assertEquals(0, calls.get());
        assertEquals(2, registry.factories.get());
        assertEquals(6, registry.getMeters().size());
        assertEquals(0, registry.closes.get());
      } finally {
        registry.close();
      }
      assertEquals(1, registry.closes.get());
      try (var recording = new Registry()) {
        var sample = new Observation(Outcome.FAILURE, 500000000);
        var read = new AtomicInteger();
        var collector =
            new DbQueryDurationMetricCollector(
                query -> {
                  read.incrementAndGet();
                  return Optional.of(sample);
                },
                recording,
                FIXTURE_DEBUG_B6DFBABB);
        recording.recordFailure = Optional.of(problem);
        assertSame(
            problem,
            assertThrows(
                problem.getClass(), () -> collector.collect(Query.OUTBOX_STATUS_COUNTS_OLDEST)));
        assertEquals(1, read.get());
        assertEquals(1, recording.records.get());
        assertEquals(
            1, summary(recording, Query.OUTBOX_STATUS_COUNTS_OLDEST, Outcome.FAILURE).count());
        assertEquals(
            .5,
            summary(recording, Query.OUTBOX_STATUS_COUNTS_OLDEST, Outcome.FAILURE).totalAmount());
        assertEquals(0, recording.closes.get());
      }
    }
  }
}
