package dev.codex.schubert.nk.api.monitoring;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.api.monitoring.DbPoolMetricRecorder.Counts;
import dev.codex.schubert.nk.api.monitoring.DbPoolMetricRecorder.State;
import io.micrometer.core.instrument.Gauge;
import io.micrometer.core.instrument.Meter;
import io.micrometer.core.instrument.simple.SimpleMeterRegistry;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.Set;
import java.util.concurrent.Callable;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.function.ToDoubleFunction;
import java.util.stream.Collectors;
import org.junit.jupiter.api.Test;

/** POOLMET001..008: supplied vectors and owned SDK only, no Hikari/DB/management activity. */
class DbPoolMetricRecorderTest {
  private static final String SERVICE_LABEL = "service";
  private static final String ACTIVE_POOL_STATE = "active";
  private static final String IDLE_POOL_STATE = "idle";
  private static final String PENDING_POOL_STATE = "pending";
  private static final String MAXIMUM_POOL_STATE = "max";
  private static final String DEBUG_MODE = "DEBUG";

  private static final class Registry extends SimpleMeterRegistry implements AutoCloseable {
    private static final int FAILURE_REGISTRATION_NUMBER = 2;

    final AtomicInteger registrations = new AtomicInteger();
    final AtomicInteger closes = new AtomicInteger();
    Optional<Runnable> secondRegistrationFailure = Optional.empty();

    @Override
    protected <T> Gauge newGauge(Meter.Id id, T object, ToDoubleFunction<T> value) {
      if (registrations.incrementAndGet() == FAILURE_REGISTRATION_NUMBER) {
        secondRegistrationFailure.ifPresent(Runnable::run);
      }
      return super.newGauge(id, object, value);
    }

    @Override
    public void close() {
      closes.incrementAndGet();
      super.close();
    }
  }

  private static void shape(Registry registry) {
    assertEquals(4, registry.getMeters().size());
    var labels = new java.util.HashSet<String>();
    for (var meter : registry.getMeters()) {
      var id = meter.getId();
      assertEquals("nk_db_pool_connections", id.getName());
      assertEquals(Meter.Type.GAUGE, id.getType());
      assertEquals(
          Set.of(SERVICE_LABEL, "state"),
          id.getTags().stream().map(t -> t.getKey()).collect(Collectors.toSet()));
      assertEquals("API", id.getTag(SERVICE_LABEL));
      labels.add(id.getTag("state"));
    }
    assertEquals(
        Set.of(ACTIVE_POOL_STATE, IDLE_POOL_STATE, PENDING_POOL_STATE, MAXIMUM_POOL_STATE), labels);
  }

  private static double gauge(Registry registry, String state) {
    return registry
        .get("nk_db_pool_connections")
        .tags(SERVICE_LABEL, "API", "state", state)
        .gauge()
        .value();
  }

  @Test
  void poolMetric001DebugHasExactlyFourCanonicalUnknownSeries() {
    try (var registry = new Registry()) {
      var recorder = new DbPoolMetricRecorder(registry, DEBUG_MODE);
      assertTrue(recorder.detailedMetricsRequested());
      assertTrue(recorder.snapshot().isEmpty());
      shape(registry);
      assertEquals(4, State.values().length);
      for (String state :
          List.of(ACTIVE_POOL_STATE, IDLE_POOL_STATE, PENDING_POOL_STATE, MAXIMUM_POOL_STATE)) {
        assertEquals(state, DbPoolMetricRecorder.state(state).label());
        assertTrue(Double.isNaN(gauge(registry, state)));
      }
      assertEquals(0, registry.closes.get());
    }
  }

  @Test
  void poolMetric002LiteralCountsAndIndependentGaugeValuesRemainExact() {
    try (var registry = new Registry()) {
      var recorder = new DbPoolMetricRecorder(registry, DEBUG_MODE);
      var counts = new Counts(3, 5, 2, 8);
      recorder.record(counts);
      assertSame(counts, recorder.snapshot().orElseThrow());
      assertEquals(3, counts.active());
      assertEquals(5, counts.idle());
      assertEquals(2, counts.pending());
      assertEquals(8, counts.maximum());
      assertEquals(3, counts.value(State.ACTIVE));
      assertEquals(5, counts.value(State.IDLE));
      assertEquals(2, counts.value(State.PENDING));
      assertEquals(8, counts.value(State.MAX));
      assertEquals(3, gauge(registry, ACTIVE_POOL_STATE));
      assertEquals(5, gauge(registry, IDLE_POOL_STATE));
      assertEquals(2, gauge(registry, PENDING_POOL_STATE));
      assertEquals(8, gauge(registry, MAXIMUM_POOL_STATE));
      shape(registry);
    }
  }

  @Test
  void poolMetric003MissingAndTrueZeroAreDistinctAndRecoverable() {
    try (var registry = new Registry()) {
      var recorder = new DbPoolMetricRecorder(registry, DEBUG_MODE);
      var zero = new Counts(0, 0, 0, 8);
      recorder.record(zero);
      assertEquals(0, gauge(registry, ACTIVE_POOL_STATE));
      assertEquals(0, gauge(registry, IDLE_POOL_STATE));
      assertEquals(0, gauge(registry, PENDING_POOL_STATE));
      assertEquals(8, gauge(registry, MAXIMUM_POOL_STATE));
      recorder.missing();
      assertTrue(recorder.snapshot().isEmpty());
      for (String state :
          List.of(ACTIVE_POOL_STATE, IDLE_POOL_STATE, PENDING_POOL_STATE, MAXIMUM_POOL_STATE))
        assertTrue(Double.isNaN(gauge(registry, state)));
      assertEquals(8, zero.maximum());
      recorder.record(new Counts(1, 0, 0, 1));
      assertEquals(1, gauge(registry, ACTIVE_POOL_STATE));
      assertEquals(1, gauge(registry, MAXIMUM_POOL_STATE));
      shape(registry);
    }
  }

  @Test
  void poolMetric004StandardNeverRegistersOrRetainsAndStillRejectsNull() {
    try (var registry = new Registry()) {
      var recorder = new DbPoolMetricRecorder(registry, "STANDARD");
      assertFalse(recorder.detailedMetricsRequested());
      recorder.record(new Counts(1, 2, 3, 8));
      recorder.missing();
      assertTrue(recorder.snapshot().isEmpty());
      assertEquals(0, registry.registrations.get());
      assertEquals(0, registry.getMeters().size());
      assertThrows(NullPointerException.class, () -> recorder.record(null));
      assertThrows(NullPointerException.class, () -> new DbPoolMetricRecorder(null, DEBUG_MODE));
      assertThrows(NullPointerException.class, () -> new DbPoolMetricRecorder(registry, null));
      for (String mode : List.of("", "debug", "unknown-canary", "DEBTf", "STANDAQc"))
        assertEquals(
            "CONFIG_INVALID",
            assertThrows(
                    IllegalArgumentException.class, () -> new DbPoolMetricRecorder(registry, mode))
                .getMessage());
      assertEquals(0, registry.registrations.get());
    }
  }

  @Test
  void poolMetric005NegativeMissingUnknownAndMaximumBoundariesDoNotWrap() {
    assertThrows(IllegalArgumentException.class, () -> new Counts(-1, 0, 0, 1));
    assertThrows(IllegalArgumentException.class, () -> new Counts(0, -1, 0, 1));
    assertThrows(IllegalArgumentException.class, () -> new Counts(0, 0, -1, 1));
    assertThrows(IllegalArgumentException.class, () -> new Counts(0, 0, 0, 0));
    assertThrows(IllegalArgumentException.class, () -> new Counts(0, 0, 0, -1));
    assertThrows(NullPointerException.class, () -> new Counts(0, 0, 0, 1).value(null));
    assertThrows(NullPointerException.class, () -> DbPoolMetricRecorder.state(null));
    for (String state : List.of("ACTIVE", "", "max-canary"))
      assertEquals(
          "CONFIG_INVALID",
          assertThrows(IllegalArgumentException.class, () -> DbPoolMetricRecorder.state(state))
              .getMessage());
    try (var registry = new Registry()) {
      var recorder = new DbPoolMetricRecorder(registry, DEBUG_MODE);
      var maximum = new Counts(Long.MAX_VALUE, Long.MAX_VALUE, Long.MAX_VALUE, Long.MAX_VALUE);
      recorder.record(maximum);
      for (var state : State.values()) assertEquals(Long.MAX_VALUE, maximum.value(state));
      // IEEE754 rounds Long.MAX_VALUE to exactly 2^63, supplied long snapshot stays exact.
      for (String state :
          List.of(ACTIVE_POOL_STATE, IDLE_POOL_STATE, PENDING_POOL_STATE, MAXIMUM_POOL_STATE))
        assertEquals(0x1.0p63, gauge(registry, state));
      assertThrows(NullPointerException.class, () -> recorder.record(null));
      assertSame(maximum, recorder.snapshot().orElseThrow());
    }
  }

  @Test
  void poolMetric006ParallelUpdatesKeepWholeImmutableSnapshots()
      throws InterruptedException, ExecutionException {
    try (var registry = new Registry()) {
      var pool = Executors.newFixedThreadPool(8);
      try {
        var recorder = new DbPoolMetricRecorder(registry, DEBUG_MODE);
        var first = new Counts(1, 2, 3, 8);
        var second = new Counts(4, 5, 6, 9);
        recorder.record(first);
        var tasks = new ArrayList<Callable<Boolean>>();
        for (int i = 0; i < 64; i++) {
          var supplied = i % 2 == 0 ? first : second;
          tasks.add(
              () -> {
                recorder.record(supplied);
                var actual = recorder.snapshot().orElseThrow();
                return actual == first || actual == second;
              });
        }
        for (var actual : pool.invokeAll(tasks, 10, TimeUnit.SECONDS)) assertTrue(actual.get());
        assertEquals(1, first.active());
        assertEquals(8, first.maximum());
        shape(registry);
      } finally {
        pool.shutdownNow();
        assertTrue(pool.awaitTermination(10, TimeUnit.SECONDS));
      }
    }
  }

  @Test
  void poolMetric007PartialProviderFailurePreservesIdentityAndBorrowedLifetime() {
    var runtime = new IllegalStateException("owned provider fixture");
    var fatal = new AssertionError("owned provider fixture");
    assertPartialProviderFailure(
        runtime,
        () -> {
          throw runtime;
        });
    assertPartialProviderFailure(
        fatal,
        () -> {
          throw fatal;
        });
  }

  private static void assertPartialProviderFailure(Throwable failure, Runnable signal) {
    var registry = new Registry();
    try {
      registry.secondRegistrationFailure = Optional.of(signal);
      assertSame(
          failure,
          assertThrows(failure.getClass(), () -> new DbPoolMetricRecorder(registry, DEBUG_MODE)));
      assertEquals(2, registry.registrations.get());
      assertEquals(1, registry.getMeters().size());
      assertEquals(0, registry.closes.get());
      assertEquals("API", registry.getMeters().getFirst().getId().getTag(SERVICE_LABEL));
    } finally {
      registry.close();
    }
    assertEquals(1, registry.closes.get());
  }

  @Test
  void poolMetric008OwnersAndRepeatedObservationsCannotGrowLabelCardinality() {
    try (var one = new Registry();
        var two = new Registry()) {
      var first = new DbPoolMetricRecorder(one, DEBUG_MODE);
      var second = new DbPoolMetricRecorder(two, DEBUG_MODE);
      second.record(new Counts(7, 0, 0, 8));
      for (int i = 0; i < 1000; i++) {
        first.record(new Counts(i, 0, 0, 8));
        if (i % 2 == 0) first.missing();
      }
      assertEquals(999, first.snapshot().orElseThrow().active());
      assertEquals(7, second.snapshot().orElseThrow().active());
      assertEquals(999, gauge(one, ACTIVE_POOL_STATE));
      assertEquals(7, gauge(two, ACTIVE_POOL_STATE));
      shape(one);
      shape(two);
    }
  }
}
