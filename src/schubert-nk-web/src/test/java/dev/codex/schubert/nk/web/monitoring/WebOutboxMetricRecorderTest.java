package dev.codex.schubert.nk.web.monitoring;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.web.monitoring.WebOutboxMetricRecorder.Observation;
import dev.codex.schubert.nk.web.monitoring.WebOutboxMetricRecorder.Status;
import io.micrometer.core.instrument.Counter;
import io.micrometer.core.instrument.Gauge;
import io.micrometer.core.instrument.Meter;
import io.micrometer.core.instrument.simple.SimpleMeterRegistry;
import java.time.Duration;
import java.util.ArrayList;
import java.util.IdentityHashMap;
import java.util.List;
import java.util.Optional;
import java.util.Set;
import java.util.concurrent.Callable;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.function.ToDoubleFunction;
import java.util.stream.Collectors;
import org.junit.jupiter.api.Test;

/** WEBOBXMET001..008/1721, fixed literals and owned SDK only, never real DB/query/clock. */
class WebOutboxMetricRecorderTest {
  static final class Registry extends SimpleMeterRegistry implements AutoCloseable {
    final AtomicInteger factories = new AtomicInteger();
    final AtomicInteger closes = new AtomicInteger();
    Optional<Throwable> failure = Optional.empty();

    @Override
    protected <T> Gauge newGauge(Meter.Id id, T object, ToDoubleFunction<T> value) {
      if (factories.incrementAndGet() == 2 && failure.isPresent()) {
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

  static final class Unformattable extends IllegalStateException {
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

  static double gauge(Registry registry, String name, String status) {
    return registry.get(name).tags("store", "WEB", "status", status).gauge().value();
  }

  static void unknown(Registry registry) {
    for (String name : List.of("nk_outbox_rows", "nk_outbox_oldest_seconds"))
      for (String status : List.of("PENDING", "SENT", "ERROR"))
        assertTrue(Double.isNaN(gauge(registry, name, status)));
  }

  static void values(
      Registry registry,
      long pending,
      long sent,
      long error,
      double pendingAge,
      double sentAge,
      double errorAge) {
    assertEquals((double) pending, gauge(registry, "nk_outbox_rows", "PENDING"));
    assertEquals((double) sent, gauge(registry, "nk_outbox_rows", "SENT"));
    assertEquals((double) error, gauge(registry, "nk_outbox_rows", "ERROR"));
    assertEquals(pendingAge, gauge(registry, "nk_outbox_oldest_seconds", "PENDING"));
    assertEquals(sentAge, gauge(registry, "nk_outbox_oldest_seconds", "SENT"));
    assertEquals(errorAge, gauge(registry, "nk_outbox_oldest_seconds", "ERROR"));
  }

  @Test
  void webObxMet001OnlySixFixedWebStoreGaugesDistinguishUnknownAndCompleteKnownValues() {
    try (var registry = new Registry()) {
      var metrics = new WebOutboxMetricRecorder(registry, "DEBUG");
      assertTrue(metrics.detailedMetricsRequested());
      assertTrue(metrics.snapshot().isEmpty());
      unknown(registry);
      assertEquals(6, registry.getMeters().size());
      var actual = new java.util.HashSet<String>();
      for (var meter : registry.getMeters()) {
        var id = meter.getId();
        assertEquals(Meter.Type.GAUGE, id.getType());
        assertEquals(
            Set.of("store", "status"),
            id.getTags().stream().map(t -> t.getKey()).collect(Collectors.toSet()));
        assertEquals("WEB", id.getTag("store"));
        assertTrue(actual.add(id.getName() + "/" + id.getTag("status")));
      }
      assertEquals(
          Set.of(
              "nk_outbox_rows/PENDING",
              "nk_outbox_rows/SENT",
              "nk_outbox_rows/ERROR",
              "nk_outbox_oldest_seconds/PENDING",
              "nk_outbox_oldest_seconds/SENT",
              "nk_outbox_oldest_seconds/ERROR"),
          actual);
      var supplied =
          new Observation(2, 0, 1, Duration.ofMillis(5250), Duration.ZERO, Duration.ofMillis(500));
      metrics.record(supplied);
      assertSame(supplied, metrics.snapshot().orElseThrow());
      values(registry, 2, 0, 1, 5.25, 0, .5);
      assertEquals(0, registry.closes.get());
    }
  }

  @Test
  void webObxMet002EveryCountAgeAndNullInvariantAndMaximumConversionHaveIndependentBoundaries() {
    for (int field = 0; field < 3; field++) {
      for (long negative : List.of(-1L, Long.MIN_VALUE)) {
        long[] counts = {1, 1, 1};
        counts[field] = negative;
        assertThrows(
            IllegalArgumentException.class,
            () ->
                new Observation(
                    counts[0], counts[1], counts[2], Duration.ZERO, Duration.ZERO, Duration.ZERO));
      }
      Duration[] absent = {Duration.ZERO, Duration.ZERO, Duration.ZERO};
      absent[field] = null;
      assertThrows(
          NullPointerException.class,
          () -> new Observation(1, 1, 1, absent[0], absent[1], absent[2]));
      Duration[] negative = {Duration.ZERO, Duration.ZERO, Duration.ZERO};
      negative[field] = Duration.ofNanos(-1);
      assertThrows(
          IllegalArgumentException.class,
          () -> new Observation(1, 1, 1, negative[0], negative[1], negative[2]));
      Duration[] invalid = {Duration.ZERO, Duration.ZERO, Duration.ZERO};
      invalid[field] = Duration.ofNanos(1);
      assertThrows(
          IllegalArgumentException.class,
          () -> new Observation(0, 0, 0, invalid[0], invalid[1], invalid[2]));
    }
    var zero = new Observation(0, 0, 0, Duration.ZERO, Duration.ZERO, Duration.ZERO);
    var now = new Observation(1, 1, 1, Duration.ZERO, Duration.ZERO, Duration.ZERO);
    var maximum = Duration.ofSeconds(Long.MAX_VALUE, 999999999);
    var max =
        new Observation(Long.MAX_VALUE, Long.MAX_VALUE, Long.MAX_VALUE, maximum, maximum, maximum);
    for (var status : List.of(Status.PENDING, Status.SENT, Status.ERROR)) {
      assertEquals(0, zero.count(status));
      assertEquals(Duration.ZERO, zero.age(status));
      assertEquals(1, now.count(status));
      assertEquals(0, now.ageSeconds(status));
      assertEquals(Long.MAX_VALUE, max.count(status));
      assertEquals(maximum, max.age(status));
      assertEquals(9.223372036854776E18, max.ageSeconds(status));
      assertTrue(Double.isFinite(max.ageSeconds(status)));
    }
    try (var registry = new Registry()) {
      var metrics = new WebOutboxMetricRecorder(registry, "DEBUG");
      metrics.record(max);
      assertEquals(9.223372036854776E18, gauge(registry, "nk_outbox_rows", "PENDING"));
      assertEquals(9.223372036854776E18, gauge(registry, "nk_outbox_oldest_seconds", "ERROR"));
    }
  }

  @Test
  void webObxMet003ThreeTypedStatusesAndGeneratedFactoriesRejectUnknownAndDoNotAliasArrays() {
    assertArrayEquals(new Status[] {Status.PENDING, Status.SENT, Status.ERROR}, Status.values());
    assertEquals(Status.PENDING, Status.parse("PENDING"));
    assertEquals(Status.SENT, Status.parse("SENT"));
    assertEquals(Status.ERROR, Status.parse("ERROR"));
    assertEquals(Status.PENDING, Status.valueOf("PENDING"));
    assertEquals(Status.SENT, Status.valueOf("SENT"));
    assertEquals(Status.ERROR, Status.valueOf("ERROR"));
    var values = Status.values();
    values[0] = Status.ERROR;
    assertEquals(Status.PENDING, Status.values()[0]);
    assertThrows(NullPointerException.class, () -> Status.parse(null));
    assertThrows(NullPointerException.class, () -> Status.valueOf(null));
    for (String value : List.of("", "pending", "UNKNOWN"))
      assertThrows(IllegalArgumentException.class, () -> Status.parse(value));
    assertThrows(IllegalArgumentException.class, () -> Status.valueOf("UNKNOWN"));
  }

  @Test
  void webObxMet004MissingNullAndStandardKeepContractsAndNeverTurnUnknownIntoZero() {
    var sample =
        new Observation(
            3, 5, 7, Duration.ofSeconds(2), Duration.ofSeconds(4), Duration.ofSeconds(6));
    assertThrows(NullPointerException.class, () -> sample.count(null));
    assertThrows(NullPointerException.class, () -> sample.age(null));
    assertThrows(NullPointerException.class, () -> sample.ageSeconds(null));
    try (var registry = new Registry()) {
      var metrics = new WebOutboxMetricRecorder(registry, "DEBUG");
      metrics.record(sample);
      assertThrows(NullPointerException.class, () -> metrics.record(null));
      assertSame(sample, metrics.snapshot().orElseThrow());
      values(registry, 3, 5, 7, 2, 4, 6);
      metrics.missing();
      assertTrue(metrics.snapshot().isEmpty());
      unknown(registry);
      metrics.record(new Observation(0, 0, 0, Duration.ZERO, Duration.ZERO, Duration.ZERO));
      values(registry, 0, 0, 0, 0, 0, 0);
    }
    try (var registry = new Registry()) {
      assertThrows(NullPointerException.class, () -> new WebOutboxMetricRecorder(null, "DEBUG"));
      assertThrows(NullPointerException.class, () -> new WebOutboxMetricRecorder(registry, null));
      for (String mode : List.of("", "debug", "unknown"))
        assertEquals(
            "CONFIG_INVALID",
            assertThrows(
                    IllegalArgumentException.class,
                    () -> new WebOutboxMetricRecorder(registry, mode))
                .getMessage());
      var metrics = new WebOutboxMetricRecorder(registry, "STANDARD");
      assertFalse(metrics.detailedMetricsRequested());
      metrics.record(sample);
      assertTrue(metrics.snapshot().isEmpty());
      metrics.missing();
      assertThrows(NullPointerException.class, () -> metrics.record(null));
      assertEquals(0, registry.factories.get());
      assertEquals(0, registry.getMeters().size());
    }
  }

  @Test
  void webObxMet005SecondGaugeFactoryFailureRetainsPrefixIdentityAndBorrowedRegistry() {
    for (var failure : List.<Throwable>of(new Unformattable(), new AssertionError("owned gauge"))) {
      var registry = new Registry();
      registry.failure = Optional.of(failure);
      try {
        assertSame(
            failure,
            assertThrows(failure.getClass(), () -> new WebOutboxMetricRecorder(registry, "DEBUG")));
        assertEquals(2, registry.factories.get());
        assertEquals(1, registry.getMeters().size());
        assertTrue(Double.isNaN(gauge(registry, "nk_outbox_rows", "PENDING")));
        assertEquals(0, registry.closes.get());
      } finally {
        registry.close();
      }
      assertEquals(1, registry.closes.get());
    }
  }

  @Test
  void webObxMet006NineRecordContractsUseSixIndependentValuesFixedHashAndLiteralString() {
    var a =
        new Observation(
            3, 5, 7, Duration.ofSeconds(2), Duration.ofSeconds(4), Duration.ofSeconds(6));
    assertEquals(3, a.pending());
    assertEquals(5, a.sent());
    assertEquals(7, a.error());
    assertEquals(Duration.ofSeconds(2), a.pendingAge());
    assertEquals(Duration.ofSeconds(4), a.sentAge());
    assertEquals(Duration.ofSeconds(6), a.errorAge());
    assertTrue(a.equals(a));
    assertTrue(
        a.equals(
            new Observation(
                3, 5, 7, Duration.ofSeconds(2), Duration.ofSeconds(4), Duration.ofSeconds(6))));
    assertFalse(a.equals(null));
    assertFalse(a.equals("not observation"));
    for (var different :
        List.of(
            new Observation(
                4, 5, 7, Duration.ofSeconds(2), Duration.ofSeconds(4), Duration.ofSeconds(6)),
            new Observation(
                3, 6, 7, Duration.ofSeconds(2), Duration.ofSeconds(4), Duration.ofSeconds(6)),
            new Observation(
                3, 5, 8, Duration.ofSeconds(2), Duration.ofSeconds(4), Duration.ofSeconds(6)),
            new Observation(
                3, 5, 7, Duration.ofSeconds(3), Duration.ofSeconds(4), Duration.ofSeconds(6)),
            new Observation(
                3, 5, 7, Duration.ofSeconds(2), Duration.ofSeconds(5), Duration.ofSeconds(6)),
            new Observation(
                3, 5, 7, Duration.ofSeconds(2), Duration.ofSeconds(4), Duration.ofSeconds(7))))
      assertFalse(a.equals(different));
    // Independent JDK record polynomial: 3*31^5+5*31^4+7*31^3+2*31^2+4*31+6.
    assertEquals(90715647, a.hashCode());
    assertEquals(
        "Observation[pending=3, sent=5, error=7, pendingAge=PT2S, sentAge=PT4S, errorAge=PT6S]",
        a.toString());
  }

  @Test
  void webObxMet007ConcurrentPublicationKeepsWholeFixtureIdentityAndIndependentGaugeVector()
      throws Exception {
    try (var registry = new Registry();
        var other = new Registry();
        var pool = Executors.newFixedThreadPool(8)) {
      var metrics = new WebOutboxMetricRecorder(registry, "DEBUG");
      var oracle = new IdentityHashMap<Observation, long[]>();
      var tasks = new ArrayList<Callable<Void>>();
      for (int i = 1; i <= 64; i++) {
        long p = i;
        long s = i + 1L;
        long e = i + 2L;
        var sample =
            new Observation(
                p, s, e, Duration.ofSeconds(p), Duration.ofSeconds(s), Duration.ofSeconds(e));
        oracle.put(sample, new long[] {p, s, e});
        tasks.add(
            () -> {
              metrics.record(sample);
              return null;
            });
      }
      for (var f : pool.invokeAll(tasks, 5, TimeUnit.SECONDS)) f.get(5, TimeUnit.SECONDS);
      var selected = metrics.snapshot().orElseThrow();
      assertTrue(oracle.containsKey(selected));
      var expected = oracle.get(selected);
      values(
          registry, expected[0], expected[1], expected[2], expected[0], expected[1], expected[2]);
      var independent = new WebOutboxMetricRecorder(other, "DEBUG");
      assertTrue(independent.snapshot().isEmpty());
      unknown(other);
      independent.record(
          new Observation(7, 0, 0, Duration.ofSeconds(3), Duration.ZERO, Duration.ZERO));
      values(other, 7, 0, 0, 3, 0, 0);
      assertSame(selected, metrics.snapshot().orElseThrow());
      values(
          registry, expected[0], expected[1], expected[2], expected[0], expected[1], expected[2]);
    }
  }

  @Test
  void webObxMet008ForeignCounterCannotBeReplacedByGaugeOrClosed() {
    try (var registry = new Registry()) {
      var foreign =
          Counter.builder("nk_outbox_rows")
              .tags("store", "WEB", "status", "PENDING")
              .register(registry);
      foreign.increment(7);
      assertThrows(
          IllegalArgumentException.class, () -> new WebOutboxMetricRecorder(registry, "DEBUG"));
      assertSame(
          foreign,
          registry.get("nk_outbox_rows").tags("store", "WEB", "status", "PENDING").counter());
      assertEquals(7, foreign.count());
      assertEquals(0, registry.closes.get());
    }
  }
}
