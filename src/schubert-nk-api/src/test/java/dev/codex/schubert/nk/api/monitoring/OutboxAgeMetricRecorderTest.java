package dev.codex.schubert.nk.api.monitoring;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.api.monitoring.OutboxAgeMetricRecorder.Ages;
import dev.codex.schubert.nk.api.monitoring.OutboxRowsMetricRecorder.Status;
import io.micrometer.core.instrument.Gauge;
import io.micrometer.core.instrument.Meter;
import io.micrometer.core.instrument.simple.SimpleMeterRegistry;
import java.time.Duration;
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

/** OUTBOXAGE001..008/1660: supplied immutable durations and owned SDK only. */
class OutboxAgeMetricRecorderTest {
  private static final int FAILURE_REGISTRATION_ORDINAL = 2;
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
      assertEquals("nk_outbox_oldest_seconds", id.getName());
      assertEquals(Meter.Type.GAUGE, id.getType());
      assertEquals(
          Set.of("store", "status"),
          id.getTags().stream().map(t -> t.getKey()).collect(Collectors.toSet()));
      assertEquals("API", id.getTag("store"));
      statuses.add(id.getTag("status"));
    }
    assertEquals(Set.of(PENDING_STATUS, SENT_STATUS, ERROR_STATUS), statuses);
  }

  private static double gauge(Registry registry, String status) {
    return registry
        .get("nk_outbox_oldest_seconds")
        .tags("store", "API", "status", status)
        .gauge()
        .value();
  }

  private static Ages ages(long pending, long sent, long error) {
    return new Ages(
        Duration.ofSeconds(pending), Duration.ofSeconds(sent), Duration.ofSeconds(error));
  }

  @Test
  void outboxAge001CanonicalUnknownSeriesDoNotClaimObservedZero() {
    try (var registry = new Registry()) {
      var recorder = new OutboxAgeMetricRecorder(registry, DEBUG_MODE);
      assertTrue(recorder.detailedMetricsRequested());
      assertTrue(recorder.snapshot().isEmpty());
      for (String status : List.of(PENDING_STATUS, SENT_STATUS, ERROR_STATUS))
        assertTrue(Double.isNaN(gauge(registry, status)));
      shape(registry);
      assertEquals(0, registry.closes.get());
    }
  }

  @Test
  void outboxAge002ExactFractionalSecondsAndSuppliedSnapshotAreIndependent() {
    try (var registry = new Registry()) {
      var recorder = new OutboxAgeMetricRecorder(registry, DEBUG_MODE);
      var supplied =
          new Ages(Duration.ofMillis(1500), Duration.ofNanos(1), Duration.ofSeconds(300));
      recorder.record(supplied);
      assertSame(supplied, recorder.snapshot().orElseThrow());
      assertEquals(1.5, gauge(registry, PENDING_STATUS));
      assertEquals(0.000000001, gauge(registry, SENT_STATUS));
      assertEquals(300, gauge(registry, ERROR_STATUS));
      assertEquals(Duration.ofMillis(1500), supplied.value(Status.PENDING));
      assertEquals(Duration.ofNanos(1), supplied.value(Status.SENT));
      assertEquals(Duration.ofSeconds(300), supplied.value(Status.ERROR));
      shape(registry);
    }
  }

  @Test
  void outboxAge003ZeroMissingRecoveryAndMaximumDurationNeverOverflow() {
    try (var registry = new Registry()) {
      var recorder = new OutboxAgeMetricRecorder(registry, DEBUG_MODE);
      var zero = ages(0, 0, 0);
      recorder.record(zero);
      for (String status : List.of(PENDING_STATUS, SENT_STATUS, ERROR_STATUS))
        assertEquals(0, gauge(registry, status));
      recorder.missing();
      assertTrue(recorder.snapshot().isEmpty());
      for (String status : List.of(PENDING_STATUS, SENT_STATUS, ERROR_STATUS))
        assertTrue(Double.isNaN(gauge(registry, status)));
      Duration maximum = Duration.ofSeconds(Long.MAX_VALUE, 999_999_999);
      var supplied = new Ages(maximum, maximum, maximum);
      recorder.record(supplied);
      for (String status : List.of(PENDING_STATUS, SENT_STATUS, ERROR_STATUS))
        assertEquals(0x1.0p63, gauge(registry, status));
      assertSame(maximum, supplied.pending());
      assertSame(maximum, supplied.sent());
      assertSame(maximum, supplied.error());
      assertEquals(Duration.ZERO, zero.pending());
    }
  }

  @Test
  void outboxAge004StandardRegistersAndRetainsNothingButChecksNull() {
    try (var registry = new Registry()) {
      var recorder = new OutboxAgeMetricRecorder(registry, "STANDARD");
      assertFalse(recorder.detailedMetricsRequested());
      recorder.record(ages(1, 2, 3));
      recorder.missing();
      assertTrue(recorder.snapshot().isEmpty());
      assertEquals(0, registry.registrations.get());
      assertEquals(0, registry.getMeters().size());
      assertThrows(NullPointerException.class, () -> recorder.record(null));
    }
  }

  @Test
  void outboxAge005NullNegativeAndUnknownModesCannotChangeExistingObservation() {
    Duration zero = Duration.ZERO;
    assertThrows(NullPointerException.class, () -> new Ages(null, zero, zero));
    assertThrows(NullPointerException.class, () -> new Ages(zero, null, zero));
    assertThrows(NullPointerException.class, () -> new Ages(zero, zero, null));
    assertThrows(IllegalArgumentException.class, () -> new Ages(Duration.ofNanos(-1), zero, zero));
    assertThrows(
        IllegalArgumentException.class, () -> new Ages(zero, Duration.ofSeconds(-1), zero));
    assertThrows(
        IllegalArgumentException.class,
        () -> new Ages(zero, zero, Duration.ofSeconds(Long.MIN_VALUE)));
    assertThrows(NullPointerException.class, () -> ages(0, 0, 0).value(null));
    try (var registry = new Registry()) {
      assertThrows(NullPointerException.class, () -> new OutboxAgeMetricRecorder(null, DEBUG_MODE));
      assertThrows(NullPointerException.class, () -> new OutboxAgeMetricRecorder(registry, null));
      for (String mode : List.of("debug", "", "unknown-mode"))
        assertEquals(
            "CONFIG_INVALID",
            assertThrows(
                    IllegalArgumentException.class,
                    () -> new OutboxAgeMetricRecorder(registry, mode))
                .getMessage());
      assertEquals(0, registry.registrations.get());
      var recorder = new OutboxAgeMetricRecorder(registry, DEBUG_MODE);
      var saved = ages(1, 2, 3);
      recorder.record(saved);
      assertThrows(NullPointerException.class, () -> recorder.record(null));
      assertSame(saved, recorder.snapshot().orElseThrow());
    }
  }

  @Test
  void outboxAge006OneOwnerPublishesWholeImmutableSnapshotsConcurrently() throws Exception {
    try (var registry = new Registry();
        var executor = Executors.newFixedThreadPool(8)) {
      var recorder = new OutboxAgeMetricRecorder(registry, DEBUG_MODE);
      var one = ages(1, 2, 3);
      var two = ages(4, 5, 6);
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
      assertEquals(Duration.ofSeconds(1), one.pending());
      assertEquals(Duration.ofSeconds(3), one.error());
      shape(registry);
    }
  }

  @Test
  void outboxAge007PartialProviderFailureKeepsCallerResourcesAndFailureIdentity() {
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
                failure.getClass(), () -> new OutboxAgeMetricRecorder(registry, DEBUG_MODE)));
        assertEquals(2, registry.registrations.get());
        assertEquals(1, registry.getMeters().size());
        assertEquals(0, registry.closes.get());
      } finally {
        registry.close();
      }
      assertEquals(1, registry.closes.get());
    }
  }

  @Test
  void outboxAge008SeparateOwnersAndGeneratedValueContractsAreExact() {
    var actual = ages(3, 5, 7);
    Object sameInstance = actual;
    Object absent = null;
    Object otherType = "not ages";
    assertTrue(actual.equals(sameInstance));
    assertTrue(actual.equals(ages(3, 5, 7)));
    assertFalse(actual.equals(absent));
    assertFalse(actual.equals(otherType));
    for (var changed : List.of(ages(4, 5, 7), ages(3, 6, 7), ages(3, 5, 8)))
      assertFalse(actual.equals(changed));
    assertEquals(3045, actual.hashCode());
    assertEquals("Ages[pending=PT3S, sent=PT5S, error=PT7S]", actual.toString());
    assertEquals(Duration.ofSeconds(3), actual.pending());
    assertEquals(Duration.ofSeconds(5), actual.sent());
    assertEquals(Duration.ofSeconds(7), actual.error());
    try (var one = new Registry();
        var two = new Registry()) {
      var first = new OutboxAgeMetricRecorder(one, DEBUG_MODE);
      var second = new OutboxAgeMetricRecorder(two, DEBUG_MODE);
      second.record(ages(7, 0, 0));
      for (int i = 0; i < 1000; i++) {
        first.record(ages(i, 0, 0));
        if (i % 2 == 0) first.missing();
      }
      assertEquals(999, gauge(one, PENDING_STATUS));
      assertEquals(7, gauge(two, PENDING_STATUS));
      shape(one);
      shape(two);
      assertEquals(0, one.closes.get());
      assertEquals(0, two.closes.get());
    }
  }
}
