package dev.codex.schubert.nk.batch.monitoring;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.batch.monitoring.BatchMetricContract.Status;
import dev.codex.schubert.nk.batch.monitoring.BatchMetricContract.Step;
import io.micrometer.core.instrument.Counter;
import io.micrometer.core.instrument.Meter;
import io.micrometer.core.instrument.MockClock;
import io.micrometer.core.instrument.simple.SimpleConfig;
import io.micrometer.core.instrument.simple.SimpleMeterRegistry;
import java.time.Instant;
import java.util.List;
import java.util.Optional;
import java.util.Set;
import java.util.concurrent.Callable;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.stream.Collectors;
import org.junit.jupiter.api.Test;

/** Actual pinned SDK with owned registry, never business Batch, Root, DB or external exporter. */
class BatchMetricRecorderTest {
  private static final String STEP_LABEL = "step";
  private static final String DEBUG_MODE = "DEBUG";
  private static final String SUCCESS_STATUS = "SUCCESS";
  private static final String BACKUP_DB_STEP = "BACKUP_DB";
  private static final String RUNS_METRIC_NAME = "nk_batch_runs_total";
  private static final String LAST_METRIC_NAME = "nk_batch_last_success_timestamp_seconds";
  private static final Instant TEN = Instant.parse("1970-01-01T00:00:10.250000Z");

  private static final class UnformattableFailure extends IllegalStateException {
    private static final long serialVersionUID = 1L;

    @Override
    public String getMessage() {
      throw new AssertionError("no failure text");
    }

    @Override
    public String toString() {
      throw new AssertionError("no failure formatting");
    }
  }

  private static final class OwnedRegistry extends SimpleMeterRegistry implements AutoCloseable {
    final AtomicInteger closes = new AtomicInteger();
    final AtomicInteger attempts = new AtomicInteger();
    Optional<Throwable> failure = Optional.empty();
    boolean failRegistration;

    OwnedRegistry() {
      super(SimpleConfig.DEFAULT, new MockClock());
    }

    private void inject() {
      attempts.incrementAndGet();
      Throwable value = failure.orElseThrow();
      if (value instanceof Error fatal) throw fatal;
      throw (RuntimeException) value;
    }

    @Override
    protected Counter newCounter(Meter.Id id) {
      if (failRegistration && failure.isPresent()) inject();
      Counter delegate = super.newCounter(id);
      return new Counter() {
        @Override
        public void increment(double amount) {
          if (failure.isPresent()) inject();
          delegate.increment(amount);
        }

        @Override
        public double count() {
          return delegate.count();
        }

        @Override
        public Meter.Id getId() {
          return delegate.getId();
        }
      };
    }

    @Override
    public void close() {
      closes.incrementAndGet();
      super.close();
    }
  }

  private static double runs(OwnedRegistry registry, String step, String status) {
    return registry
        .get(RUNS_METRIC_NAME)
        .tags(STEP_LABEL, step, "status", status)
        .counter()
        .count();
  }

  private static double last(OwnedRegistry registry, String step) {
    return registry.get(LAST_METRIC_NAME).tag(STEP_LABEL, step).gauge().value();
  }

  private static void shape(OwnedRegistry registry) {
    assertEquals(50, registry.getMeters().size());
    assertEquals(
        40,
        registry.getMeters().stream()
            .filter(m -> m.getId().getType() == Meter.Type.COUNTER)
            .count());
    assertEquals(
        10,
        registry.getMeters().stream().filter(m -> m.getId().getType() == Meter.Type.GAUGE).count());
    for (var meter : registry.getMeters()) {
      var id = meter.getId();
      assertTrue(Set.of(RUNS_METRIC_NAME, LAST_METRIC_NAME).contains(id.getName()));
      assertEquals(
          id.getName().equals(RUNS_METRIC_NAME) ? Set.of(STEP_LABEL, "status") : Set.of(STEP_LABEL),
          id.getTags().stream().map(t -> t.getKey()).collect(Collectors.toSet()));
      assertTrue(Set.of(BatchMetricContractTest.STEPS).contains(id.getTag(STEP_LABEL)));
      if (id.getName().equals(RUNS_METRIC_NAME))
        assertTrue(Set.of(BatchMetricContractTest.STATUSES).contains(id.getTag("status")));
    }
  }

  @Test
  void batchRec001ActualDebugRegistryHasFortyCountersAndTenUnknownSuccessGauges() {
    try (var registry = new OwnedRegistry()) {
      var recorder = new BatchMetricRecorder(registry, DEBUG_MODE);
      assertTrue(recorder.detailedMetricsRequested());
      shape(registry);
      for (String step : BatchMetricContractTest.STEPS) {
        assertTrue(Double.isNaN(last(registry, step)));
        for (String status : BatchMetricContractTest.STATUSES)
          assertEquals(0.0, runs(registry, step, status));
      }
      assertEquals(0, registry.closes.get());
      assertFalse(registry.isClosed());
    }
  }

  @Test
  void batchRec002WholeIndependentMatrixCountsOnceAndOnlySuccessUpdatesTime() {
    try (var registry = new OwnedRegistry()) {
      var recorder = new BatchMetricRecorder(registry, DEBUG_MODE);
      var contract = new BatchMetricContract();
      for (String step : BatchMetricContractTest.STEPS) {
        for (String status : BatchMetricContractTest.STATUSES)
          recorder.record(
              contract.step(step),
              contract.status(status),
              status.equals(SUCCESS_STATUS) ? TEN : Instant.ofEpochSecond(20));
        assertEquals(10.25, last(registry, step), 0.0);
        for (String status : BatchMetricContractTest.STATUSES)
          assertEquals(1.0, runs(registry, step, status));
      }
      shape(registry);
    }
  }

  @Test
  void batchRec003LastSuccessIsMaximumNotLastCallAndNonSuccessCannotReplaceIt() {
    try (var registry = new OwnedRegistry()) {
      var recorder = new BatchMetricRecorder(registry, DEBUG_MODE);
      recorder.record(Step.BACKUP_DB, Status.FAILED, Instant.ofEpochSecond(99));
      assertTrue(Double.isNaN(last(registry, BACKUP_DB_STEP)));
      recorder.record(Step.BACKUP_DB, Status.SUCCESS, TEN);
      recorder.record(Step.BACKUP_DB, Status.SUCCESS, Instant.ofEpochSecond(11, 500_000_000));
      recorder.record(Step.BACKUP_DB, Status.SUCCESS, TEN);
      recorder.record(Step.BACKUP_DB, Status.SUCCESS, Instant.ofEpochSecond(11, 500_000_000));
      recorder.record(Step.BACKUP_DB, Status.WARNING, Instant.ofEpochSecond(100));
      recorder.record(Step.BACKUP_DB, Status.SKIPPED, Instant.ofEpochSecond(101));
      assertEquals(11.5, last(registry, BACKUP_DB_STEP), 0.0);
      assertEquals(4.0, runs(registry, BACKUP_DB_STEP, SUCCESS_STATUS));
      assertEquals(1.0, runs(registry, BACKUP_DB_STEP, "FAILED"));
    }
  }

  @Test
  void batchRec004StandardHasNoCustomSeriesButStillValidatesInputs() {
    try (var registry = new OwnedRegistry()) {
      var recorder = new BatchMetricRecorder(registry, "STANDARD");
      assertFalse(recorder.detailedMetricsRequested());
      for (var step : Step.values())
        for (var status : Status.values()) recorder.record(step, status, TEN);
      assertTrue(registry.getMeters().isEmpty());
      assertThrows(NullPointerException.class, () -> recorder.record(null, Status.SUCCESS, TEN));
      assertThrows(NullPointerException.class, () -> recorder.record(Step.BACKUP_DB, null, TEN));
      assertThrows(
          NullPointerException.class, () -> recorder.record(Step.BACKUP_DB, Status.SUCCESS, null));
      assertThrows(
          IllegalArgumentException.class,
          () -> recorder.record(Step.BACKUP_DB, Status.SUCCESS, Instant.MAX));
      assertTrue(registry.getMeters().isEmpty());
    }
  }

  @Test
  void batchRec005NullUtcRangeAndMicrosecondPrecisionRejectBeforeSideEffects() {
    assertThrows(NullPointerException.class, () -> new BatchMetricRecorder(null, "STANDARD"));
    try (var registry = new OwnedRegistry()) {
      assertThrows(NullPointerException.class, () -> new BatchMetricRecorder(registry, null));
      assertThrows(
          IllegalArgumentException.class, () -> new BatchMetricRecorder(registry, "debug"));
      assertTrue(registry.getMeters().isEmpty());
      var recorder = new BatchMetricRecorder(registry, DEBUG_MODE);
      for (Instant invalid :
          List.of(
              Instant.parse("0000-12-31T23:59:59Z"),
              Instant.parse("+10000-01-01T00:00:00Z"),
              Instant.parse("1970-01-01T00:00:00.000000001Z")))
        assertThrows(
            IllegalArgumentException.class,
            () -> recorder.record(Step.BACKUP_DB, Status.SUCCESS, invalid));
      assertEquals(0.0, runs(registry, BACKUP_DB_STEP, SUCCESS_STATUS));
      assertTrue(Double.isNaN(last(registry, BACKUP_DB_STEP)));
      recorder.record(Step.BACKUP_DB, Status.SUCCESS, Instant.parse("0001-01-01T00:00:00Z"));
      assertEquals(-62_135_596_800.0, last(registry, BACKUP_DB_STEP), 0.0);
      recorder.record(Step.BACKUP_DB, Status.SUCCESS, Instant.parse("9999-12-31T23:59:59.999999Z"));
      assertEquals(253_402_300_800.0, last(registry, BACKUP_DB_STEP), 0.0);
      assertEquals(2.0, runs(registry, BACKUP_DB_STEP, SUCCESS_STATUS));
    }
  }

  @Test
  void batchRec006ProviderFailuresHaveExactIdentityNoRetryAndBorrowedRegistry() {
    for (Throwable failure :
        List.of(
            new UnformattableFailure(),
            new NullPointerException(),
            new AssertionError(),
            new OutOfMemoryError("synthetic-test-only-no-allocation"))) {
      try (var registry = new OwnedRegistry()) {
        var recorder = new BatchMetricRecorder(registry, DEBUG_MODE);
        registry.failure = Optional.of(failure);
        assertSame(
            failure,
            assertThrows(
                failure.getClass(), () -> recorder.record(Step.BACKUP_DB, Status.SUCCESS, TEN)));
        assertEquals(1, registry.attempts.get());
        assertEquals(0.0, runs(registry, BACKUP_DB_STEP, SUCCESS_STATUS));
        assertTrue(Double.isNaN(last(registry, BACKUP_DB_STEP)));
        assertEquals(0, registry.closes.get());
        assertFalse(registry.isClosed());
        registry.failure = Optional.empty();
        recorder.record(Step.BACKUP_DB, Status.SUCCESS, TEN);
        assertEquals(1.0, runs(registry, BACKUP_DB_STEP, SUCCESS_STATUS));
        assertEquals(10.25, last(registry, BACKUP_DB_STEP), 0.0);
      }
    }
  }

  @Test
  void batchRec007SixtyFourParallelSuccessesKeepExactCountAndMaximumTime() throws Exception {
    try (var registry = new OwnedRegistry()) {
      var pool = Executors.newFixedThreadPool(8);
      try {
        var recorder = new BatchMetricRecorder(registry, DEBUG_MODE);
        var jobs =
            java.util.stream.IntStream.range(0, 64)
                .<Callable<Boolean>>mapToObj(
                    i ->
                        () -> {
                          recorder.record(
                              Step.CLEAN_LOG, Status.SUCCESS, Instant.ofEpochSecond(64 - i));
                          return true;
                        })
                .toList();
        for (var result : pool.invokeAll(jobs, 10, TimeUnit.SECONDS)) assertTrue(result.get());
        assertEquals(64.0, runs(registry, "CLEAN_LOG", SUCCESS_STATUS));
        assertEquals(64.0, last(registry, "CLEAN_LOG"), 0.0);
        shape(registry);
      } finally {
        pool.shutdownNow();
        assertTrue(pool.awaitTermination(10, TimeUnit.SECONDS));
      }
    }
  }

  @Test
  void batchRec008FailedConstructionAndSeparateOwnersRetainRegistryOwnership() {
    var failure = new UnformattableFailure();
    try (var failed = new OwnedRegistry()) {
      failed.failure = Optional.of(failure);
      failed.failRegistration = true;
      assertSame(
          failure,
          assertThrows(
              UnformattableFailure.class, () -> new BatchMetricRecorder(failed, DEBUG_MODE)));
      assertEquals(1, failed.attempts.get());
      assertEquals(0, failed.closes.get());
      assertFalse(failed.isClosed());
    }
    try (var first = new OwnedRegistry();
        var second = new OwnedRegistry()) {
      var one = new BatchMetricRecorder(first, DEBUG_MODE);
      new BatchMetricRecorder(second, DEBUG_MODE);
      for (int i = 0; i < 1000; i++) one.record(Step.CLEAN_SESSION, Status.SUCCESS, TEN);
      assertEquals(1000.0, runs(first, "CLEAN_SESSION", SUCCESS_STATUS));
      assertEquals(0.0, runs(second, "CLEAN_SESSION", SUCCESS_STATUS));
      assertTrue(Double.isNaN(last(second, "CLEAN_SESSION")));
      shape(first);
      shape(second);
    }
  }
}
