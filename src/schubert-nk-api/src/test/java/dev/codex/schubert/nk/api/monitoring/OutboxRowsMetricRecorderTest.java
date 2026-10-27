package dev.codex.schubert.nk.api.monitoring;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.api.monitoring.OutboxRowsMetricRecorder.Counts;
import dev.codex.schubert.nk.api.monitoring.OutboxRowsMetricRecorder.Status;
import io.micrometer.core.instrument.Gauge;
import io.micrometer.core.instrument.Meter;
import io.micrometer.core.instrument.simple.SimpleMeterRegistry;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.Set;
import java.util.concurrent.Callable;
import java.util.concurrent.Executors;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.function.ToDoubleFunction;
import java.util.stream.Collectors;
import org.junit.jupiter.api.Test;

/** OUTBOXMET001..008: supplied counts and owned SDK only, no rows/DB/dispatcher/Root operations. */
class OutboxRowsMetricRecorderTest {
  private static final int FAILURE_REGISTRATION_ORDINAL = 2;
  private static final String STORE_LABEL = "store";
  private static final String PENDING_STATUS = "PENDING";
  private static final String SENT_STATUS = "SENT";
  private static final String ERROR_STATUS = "ERROR";
  private static final String DEBUG_MODE = "DEBUG";

  private static final class Registry extends SimpleMeterRegistry implements AutoCloseable {
    final AtomicInteger registrations = new AtomicInteger();
    final AtomicInteger closes = new AtomicInteger();
    Optional<Throwable> failure = Optional.empty();

    @Override
    protected <T> Gauge newGauge(Meter.Id id, T object, ToDoubleFunction<T> value) {
      if (registrations.incrementAndGet() == FAILURE_REGISTRATION_ORDINAL && failure.isPresent()) {
        var problem = failure.orElseThrow();
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

  private static void shape(Registry registry) {
    assertEquals(3, registry.getMeters().size());
    var statuses = new java.util.HashSet<String>();
    for (var meter : registry.getMeters()) {
      var id = meter.getId();
      assertEquals("nk_outbox_rows", id.getName());
      assertEquals(Meter.Type.GAUGE, id.getType());
      assertEquals(
          Set.of(STORE_LABEL, "status"),
          id.getTags().stream().map(t -> t.getKey()).collect(Collectors.toSet()));
      assertEquals("API", id.getTag(STORE_LABEL));
      statuses.add(id.getTag("status"));
    }
    assertEquals(Set.of(PENDING_STATUS, SENT_STATUS, ERROR_STATUS), statuses);
  }

  private static double gauge(Registry registry, String status) {
    return registry
        .get("nk_outbox_rows")
        .tags(STORE_LABEL, "API", "status", status)
        .gauge()
        .value();
  }

  @Test
  void outboxMetric001DebugHasThreeCanonicalUnknownSeries() {
    try (var registry = new Registry()) {
      var recorder = new OutboxRowsMetricRecorder(registry, DEBUG_MODE);
      assertTrue(recorder.detailedMetricsRequested());
      assertTrue(recorder.snapshot().isEmpty());
      shape(registry);
      assertEquals(3, Status.values().length);
      for (String status : List.of(PENDING_STATUS, SENT_STATUS, ERROR_STATUS)) {
        assertEquals(status, OutboxRowsMetricRecorder.status(status).name());
        assertTrue(Double.isNaN(gauge(registry, status)));
      }
      assertEquals(0, registry.closes.get());
    }
  }

  @Test
  void outboxMetric002LiteralCountValuesAndImmutableSnapshotMatchSdk() {
    try (var registry = new Registry()) {
      var recorder = new OutboxRowsMetricRecorder(registry, DEBUG_MODE);
      var counts = new Counts(3, 5, 2);
      recorder.record(counts);
      assertSame(counts, recorder.snapshot().orElseThrow());
      assertEquals(3, counts.pending());
      assertEquals(5, counts.sent());
      assertEquals(2, counts.error());
      assertEquals(3, counts.value(Status.PENDING));
      assertEquals(5, counts.value(Status.SENT));
      assertEquals(2, counts.value(Status.ERROR));
      assertEquals(3, gauge(registry, PENDING_STATUS));
      assertEquals(5, gauge(registry, SENT_STATUS));
      assertEquals(2, gauge(registry, ERROR_STATUS));
      shape(registry);
    }
  }

  @Test
  void outboxMetric003TrueZeroAndMissingStayDistinctAndRecover() {
    try (var registry = new Registry()) {
      var recorder = new OutboxRowsMetricRecorder(registry, DEBUG_MODE);
      var zero = new Counts(0, 0, 0);
      recorder.record(zero);
      for (String status : List.of(PENDING_STATUS, SENT_STATUS, ERROR_STATUS))
        assertEquals(0, gauge(registry, status));
      recorder.missing();
      assertTrue(recorder.snapshot().isEmpty());
      for (String status : List.of(PENDING_STATUS, SENT_STATUS, ERROR_STATUS))
        assertTrue(Double.isNaN(gauge(registry, status)));
      assertEquals(0, zero.pending());
      recorder.record(new Counts(1, 0, 0));
      assertEquals(1, gauge(registry, PENDING_STATUS));
      assertEquals(0, gauge(registry, SENT_STATUS));
      shape(registry);
    }
  }

  @Test
  void outboxMetric004StandardDoesNotRegisterOrRetainAndStillRejectsNull() {
    try (var registry = new Registry()) {
      var recorder = new OutboxRowsMetricRecorder(registry, "STANDARD");
      assertFalse(recorder.detailedMetricsRequested());
      recorder.record(new Counts(1, 2, 3));
      recorder.missing();
      assertTrue(recorder.snapshot().isEmpty());
      assertEquals(0, registry.getMeters().size());
      assertEquals(0, registry.registrations.get());
      assertThrows(NullPointerException.class, () -> recorder.record(null));
    }
  }

  @Test
  void outboxMetric005InvalidBoundariesCannotEchoOrWrapMaximumValues() {
    assertThrows(IllegalArgumentException.class, () -> new Counts(-1, 0, 0));
    assertThrows(IllegalArgumentException.class, () -> new Counts(0, -1, 0));
    assertThrows(IllegalArgumentException.class, () -> new Counts(0, 0, -1));
    assertThrows(NullPointerException.class, () -> new Counts(0, 0, 0).value(null));
    assertThrows(NullPointerException.class, () -> OutboxRowsMetricRecorder.status(null));
    for (String status : List.of("pending", "", "unknown-secret-canary"))
      assertEquals(
          "CONFIG_INVALID",
          assertThrows(
                  IllegalArgumentException.class, () -> OutboxRowsMetricRecorder.status(status))
              .getMessage());
    try (var registry = new Registry()) {
      assertThrows(
          NullPointerException.class, () -> new OutboxRowsMetricRecorder(null, DEBUG_MODE));
      assertThrows(NullPointerException.class, () -> new OutboxRowsMetricRecorder(registry, null));
      for (String mode : List.of("debug", "", "unknown-mode"))
        assertEquals(
            "CONFIG_INVALID",
            assertThrows(
                    IllegalArgumentException.class,
                    () -> new OutboxRowsMetricRecorder(registry, mode))
                .getMessage());
      assertEquals(0, registry.registrations.get());
      var recorder = new OutboxRowsMetricRecorder(registry, DEBUG_MODE);
      var maximum = new Counts(Long.MAX_VALUE, Long.MAX_VALUE, Long.MAX_VALUE);
      recorder.record(maximum);
      for (var status : Status.values()) assertEquals(Long.MAX_VALUE, maximum.value(status));
      for (String status : List.of(PENDING_STATUS, SENT_STATUS, ERROR_STATUS))
        assertEquals(0x1.0p63, gauge(registry, status));
      assertThrows(NullPointerException.class, () -> recorder.record(null));
      assertSame(maximum, recorder.snapshot().orElseThrow());
    }
  }

  @Test
  void outboxMetric006ParallelSnapshotsRemainCompleteAndImmutable() throws Exception {
    try (var registry = new Registry();
        var executor = Executors.newFixedThreadPool(8)) {
      var recorder = new OutboxRowsMetricRecorder(registry, DEBUG_MODE);
      var one = new Counts(1, 2, 3);
      var two = new Counts(4, 5, 6);
      recorder.record(one);
      var tasks = new ArrayList<Callable<Boolean>>();
      for (int i = 0; i < 64; i++) {
        var supplied = i % 2 == 0 ? one : two;
        tasks.add(
            () -> {
              recorder.record(supplied);
              var actual = recorder.snapshot().orElseThrow();
              return actual == one || actual == two;
            });
      }
      for (var actual : executor.invokeAll(tasks)) assertTrue(actual.get());
      assertEquals(1, one.pending());
      assertEquals(3, one.error());
      shape(registry);
    }
  }

  @Test
  void outboxMetric007PartialRegistrationFailureKeepsIdentityAndCallerOwnership() {
    for (var failure :
        List.<Throwable>of(
            new IllegalStateException("owned provider fixture"),
            new AssertionError("owned provider fixture"))) {
      var registry = new Registry();
      try {
        registry.failure = Optional.of(failure);
        assertSame(
            failure,
            assertThrows(
                failure.getClass(), () -> new OutboxRowsMetricRecorder(registry, DEBUG_MODE)));
        assertEquals(2, registry.registrations.get());
        assertEquals(1, registry.getMeters().size());
        assertEquals(0, registry.closes.get());
        assertEquals("API", registry.getMeters().getFirst().getId().getTag(STORE_LABEL));
      } finally {
        registry.close();
      }
      assertEquals(1, registry.closes.get());
    }
  }

  @Test
  void outboxMetric008OwnersAndRepeatedValuesCannotShareOrGrowSeries() {
    try (var one = new Registry();
        var two = new Registry()) {
      var first = new OutboxRowsMetricRecorder(one, DEBUG_MODE);
      var second = new OutboxRowsMetricRecorder(two, DEBUG_MODE);
      second.record(new Counts(7, 0, 0));
      for (int i = 0; i < 1000; i++) {
        first.record(new Counts(i, 0, 0));
        if (i % 2 == 0) first.missing();
      }
      assertEquals(999, first.snapshot().orElseThrow().pending());
      assertEquals(7, second.snapshot().orElseThrow().pending());
      assertEquals(999, gauge(one, PENDING_STATUS));
      assertEquals(7, gauge(two, PENDING_STATUS));
      shape(one);
      shape(two);
      assertEquals(0, one.closes.get());
      assertEquals(0, two.closes.get());
    }
  }
}
