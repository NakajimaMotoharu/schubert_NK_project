package dev.codex.schubert.nk.api.monitoring;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.api.monitoring.AsyncJobMetricRecorder.Snapshot;
import dev.codex.schubert.nk.api.monitoring.AsyncJobMetricRecorder.State;
import io.micrometer.core.instrument.Gauge;
import io.micrometer.core.instrument.Meter;
import io.micrometer.core.instrument.MockClock;
import io.micrometer.core.instrument.simple.SimpleConfig;
import io.micrometer.core.instrument.simple.SimpleMeterRegistry;
import java.util.Arrays;
import java.util.EnumMap;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.concurrent.Callable;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.function.ToDoubleFunction;
import java.util.stream.Collectors;
import org.junit.jupiter.api.Test;

/** Independent five-state vectors, actual owned SDK and no business database or worker. */
class AsyncJobMetricRecorderTest {
  private static final int FAILURE_REGISTRATION_ORDINAL = 2;
  private static final String DEBUG_MODE = "DEBUG";
  private static final String NAME = "nk_async_jobs";
  private static final String[] STATES = {
    "RECEIVED", "PROCESSING", "COMPLETED", "ERROR", "CANCELLED"
  };

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

  private static final class Registry extends SimpleMeterRegistry implements AutoCloseable {
    final AtomicInteger calls = new AtomicInteger();
    final AtomicInteger closes = new AtomicInteger();
    Optional<Throwable> failure = Optional.empty();

    Registry() {
      super(SimpleConfig.DEFAULT, new MockClock());
    }

    @Override
    protected <T> Gauge newGauge(Meter.Id id, T object, ToDoubleFunction<T> value) {
      if (calls.incrementAndGet() == FAILURE_REGISTRATION_ORDINAL && failure.isPresent()) {
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

  private static Map<State, Long> values(
      long received, long processing, long completed, long error, long cancelled) {
    return Map.of(
        State.RECEIVED,
        received,
        State.PROCESSING,
        processing,
        State.COMPLETED,
        completed,
        State.ERROR,
        error,
        State.CANCELLED,
        cancelled);
  }

  private static double gauge(Registry registry, String state) {
    return registry.get(NAME).tag("state", state).gauge().value();
  }

  private static void shape(Registry registry) {
    assertEquals(5, registry.getMeters().size());
    for (var meter : registry.getMeters()) {
      var id = meter.getId();
      assertEquals(NAME, id.getName());
      assertEquals(Meter.Type.GAUGE, id.getType());
      assertEquals(
          Set.of("state"), id.getTags().stream().map(t -> t.getKey()).collect(Collectors.toSet()));
      assertTrue(Set.of(STATES).contains(id.getTag("state")));
    }
  }

  @Test
  void asyncGauge001ActualDebugHasFiveCanonicalUnknownGaugesAndBorrowedOwner() {
    try (var registry = new Registry()) {
      var recorder = new AsyncJobMetricRecorder(registry, DEBUG_MODE);
      assertTrue(recorder.detailedMetricsRequested());
      assertTrue(recorder.snapshot().isEmpty());
      shape(registry);
      assertEquals(
          Set.of(STATES),
          Arrays.stream(State.values()).map(Enum::name).collect(Collectors.toSet()));
      for (String state : STATES) {
        assertEquals(state, AsyncJobMetricRecorder.state(state).name());
        assertTrue(Double.isNaN(gauge(registry, state)));
      }
      assertEquals(5, registry.calls.get());
      assertEquals(0, registry.closes.get());
      assertFalse(registry.isClosed());
    }
  }

  @Test
  void asyncGauge002LiteralCountsRemainImmutableAndUnknownNamesCannotBecomeLabels() {
    try (var registry = new Registry()) {
      var recorder = new AsyncJobMetricRecorder(registry, DEBUG_MODE);
      var input = new EnumMap<>(values(1, 2, 3, 4, 5));
      var snapshot = new Snapshot(input);
      recorder.record(snapshot);
      input.put(State.RECEIVED, 999L);
      assertEquals(15, snapshot.totalJobs());
      assertEquals(1, snapshot.value(State.RECEIVED));
      double[] expected = {1, 2, 3, 4, 5};
      for (int i = 0; i < STATES.length; i++)
        assertEquals(expected[i], gauge(registry, STATES[i]), 0.0);
      for (String invalid :
          List.of("", "received", "RECEIVED ", "ACCEPTED", "PT_SECRET_CANARY_ONLY"))
        assertEquals(
            "CONFIG_INVALID",
            assertThrows(
                    IllegalArgumentException.class, () -> AsyncJobMetricRecorder.state(invalid))
                .getMessage());
      for (int i = 0; i < 1000; i++) {
        String invalid = "PT_CANARY_ONLY_" + i;
        assertEquals(
            "CONFIG_INVALID",
            assertThrows(
                    IllegalArgumentException.class, () -> AsyncJobMetricRecorder.state(invalid))
                .getMessage());
      }
      shape(registry);
      assertSame(snapshot, recorder.snapshot().orElseThrow());
    }
  }

  @Test
  void asyncGauge003TrueZeroAndMissingAreDistinctAndKnownValuesRecover() {
    try (var registry = new Registry()) {
      var recorder = new AsyncJobMetricRecorder(registry, DEBUG_MODE);
      recorder.record(new Snapshot(values(0, 0, 0, 0, 0)));
      for (String state : STATES) assertEquals(0.0, gauge(registry, state));
      assertEquals(0, recorder.snapshot().orElseThrow().totalJobs());
      recorder.missing();
      assertTrue(recorder.snapshot().isEmpty());
      for (String state : STATES) assertTrue(Double.isNaN(gauge(registry, state)));
      recorder.record(new Snapshot(values(5, 4, 3, 2, 1)));
      double[] expected = {5, 4, 3, 2, 1};
      for (int i = 0; i < STATES.length; i++)
        assertEquals(expected[i], gauge(registry, STATES[i]), 0.0);
    }
  }

  @Test
  void asyncGauge004StandardDoesNotRegisterOrRetainAndStillRejectsInvalidBoundaries() {
    assertThrows(NullPointerException.class, () -> new AsyncJobMetricRecorder(null, "STANDARD"));
    try (var registry = new Registry()) {
      assertThrows(NullPointerException.class, () -> new AsyncJobMetricRecorder(registry, null));
      for (String invalid : List.of("", "debug", " DEBUG", "PT_CANARY_ONLY"))
        assertThrows(
            IllegalArgumentException.class, () -> new AsyncJobMetricRecorder(registry, invalid));
      assertEquals(0, registry.calls.get());
      var recorder = new AsyncJobMetricRecorder(registry, "STANDARD");
      assertFalse(recorder.detailedMetricsRequested());
      recorder.record(new Snapshot(values(1, 2, 3, 4, 5)));
      assertTrue(recorder.snapshot().isEmpty());
      recorder.missing();
      assertTrue(recorder.snapshot().isEmpty());
      assertThrows(NullPointerException.class, () -> recorder.record(null));
      assertEquals(0, registry.calls.get());
      assertTrue(registry.getMeters().isEmpty());
    }
  }

  @Test
  void asyncGauge005NullMissingAndNegativeCountsCannotChangeExistingSnapshot() {
    assertThrows(NullPointerException.class, () -> new Snapshot(null));
    assertThrows(NullPointerException.class, () -> AsyncJobMetricRecorder.state(null));
    var valid = values(1, 2, 3, 4, 5);
    var nullKey = new HashMap<>(valid);
    nullKey.put(null, 1L);
    assertThrows(NullPointerException.class, () -> new Snapshot(nullKey));
    var nullValue = new EnumMap<>(valid);
    nullValue.put(State.ERROR, null);
    assertThrows(NullPointerException.class, () -> new Snapshot(nullValue));
    for (State missing : State.values()) {
      var incomplete = new EnumMap<>(valid);
      incomplete.remove(missing);
      assertThrows(IllegalArgumentException.class, () -> new Snapshot(incomplete));
    }
    assertThrows(IllegalArgumentException.class, () -> new Snapshot(Map.of()));
    assertThrows(IllegalArgumentException.class, () -> new Snapshot(values(1, 2, 3, -1, 5)));
    var before = new Snapshot(valid);
    assertThrows(NullPointerException.class, () -> before.value(null));
    try (var registry = new Registry()) {
      var recorder = new AsyncJobMetricRecorder(registry, DEBUG_MODE);
      recorder.record(before);
      assertThrows(NullPointerException.class, () -> recorder.record(null));
      assertSame(before, recorder.snapshot().orElseThrow());
      assertEquals(15, before.totalJobs());
      assertEquals(4.0, gauge(registry, "ERROR"));
    }
  }

  @Test
  void asyncGauge006MaximumLongIsExactInSnapshotAndOverflowCannotWrap() {
    var maximum = new Snapshot(values(0, 0, 0, 0, Long.MAX_VALUE));
    assertEquals(Long.MAX_VALUE, maximum.totalJobs());
    assertEquals(Long.MAX_VALUE, maximum.value(State.CANCELLED));
    assertThrows(ArithmeticException.class, () -> new Snapshot(values(1, 0, 0, 0, Long.MAX_VALUE)));
    try (var registry = new Registry()) {
      var recorder = new AsyncJobMetricRecorder(registry, DEBUG_MODE);
      recorder.record(maximum);
      assertEquals(9_223_372_036_854_776_000.0, gauge(registry, "CANCELLED"), 0.0);
      for (String state : List.of("RECEIVED", "PROCESSING", "COMPLETED", "ERROR"))
        assertEquals(0.0, gauge(registry, state));
    }
  }

  @Test
  void asyncGauge007ParallelSnapshotsRemainCompleteWithoutCrossOwnerOrSeriesGrowth()
      throws Exception {
    try (var registry = new Registry()) {
      var pool = Executors.newFixedThreadPool(8);
      try {
        var recorder = new AsyncJobMetricRecorder(registry, DEBUG_MODE);
        var first = new Snapshot(values(1, 2, 3, 4, 5));
        var second = new Snapshot(values(10, 20, 30, 40, 50));
        recorder.record(first);
        var jobs =
            java.util.stream.IntStream.range(0, 64)
                .<Callable<Boolean>>mapToObj(
                    i ->
                        () -> {
                          recorder.record(i % 2 == 0 ? first : second);
                          var read = recorder.snapshot().orElseThrow();
                          return read == first || read == second;
                        })
                .toList();
        for (var result : pool.invokeAll(jobs, 10, TimeUnit.SECONDS)) assertTrue(result.get());
        assertEquals(15, first.totalJobs());
        recorder.record(second);
        assertSame(second, recorder.snapshot().orElseThrow());
        double[] expected = {10, 20, 30, 40, 50};
        for (int i = 0; i < STATES.length; i++)
          assertEquals(expected[i], gauge(registry, STATES[i]), 0.0);
        shape(registry);
      } finally {
        pool.shutdownNow();
        assertTrue(pool.awaitTermination(10, TimeUnit.SECONDS));
      }
    }
  }

  @Test
  void asyncGauge008PartialProviderFailureKeepsIdentityAndCallerOwnedRegistry() {
    for (Throwable failure :
        List.of(
            new UnformattableFailure(),
            new NullPointerException(),
            new AssertionError(),
            new OutOfMemoryError("synthetic-test-only-no-allocation"))) {
      try (var registry = new Registry()) {
        registry.failure = Optional.of(failure);
        assertSame(
            failure,
            assertThrows(
                failure.getClass(), () -> new AsyncJobMetricRecorder(registry, DEBUG_MODE)));
        assertEquals(2, registry.calls.get());
        assertEquals(1, registry.getMeters().size());
        assertEquals(0, registry.closes.get());
        assertFalse(registry.isClosed());
      }
    }
    try (var first = new Registry();
        var second = new Registry()) {
      var one = new AsyncJobMetricRecorder(first, DEBUG_MODE);
      var two = new AsyncJobMetricRecorder(second, DEBUG_MODE);
      one.record(new Snapshot(values(1, 2, 3, 4, 5)));
      assertTrue(two.snapshot().isEmpty());
      for (String state : STATES) assertTrue(Double.isNaN(gauge(second, state)));
      shape(first);
      shape(second);
    }
  }
}
