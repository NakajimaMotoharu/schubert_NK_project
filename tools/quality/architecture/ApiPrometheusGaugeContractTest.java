package dev.codex.schubert.nk.api.monitoring;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.api.monitoring.PrometheusGaugeTextFixture.Key;
import java.time.Duration;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Test;

/** APIPROM001..008/1745. Fixed supplied values, no SQL, scheduler, real pool or control. */
class ApiPrometheusGaugeContractTest {
  private static final Map<String, String> TYPES =
      Map.of(
          "nk_outbox_rows",
          "gauge",
          "nk_outbox_oldest_seconds",
          "gauge",
          "nk_async_jobs",
          "gauge",
          "nk_db_pool_connections",
          "gauge");

  private static final class Bundle implements AutoCloseable {
    final PrometheusGaugeTextFixture registry = new PrometheusGaugeTextFixture();
    final OutboxRowsMetricRecorder rows;
    final OutboxAgeMetricRecorder age;
    final AsyncJobMetricRecorder jobs;
    final DbPoolMetricRecorder pool;
    final boolean debug;

    Bundle(String mode) {
      debug = mode.equals("DEBUG");
      rows = new OutboxRowsMetricRecorder(registry, mode);
      age = new OutboxAgeMetricRecorder(registry, mode);
      jobs = new AsyncJobMetricRecorder(registry, mode);
      pool = new DbPoolMetricRecorder(registry, mode);
    }

    Map<Key, Double> text() {
      var actual = registry.text(List.of(rows, age, jobs, pool), debug ? TYPES : Map.of());
      if (debug) assertEquals(keys(), actual.keySet());
      else assertTrue(actual.isEmpty());
      return actual;
    }

    @Override
    public void close() {
      registry.close();
    }
  }

  private static java.util.Set<Key> keys() {
    var keys = new HashSet<Key>();
    for (String status : List.of("PENDING", "SENT", "ERROR")) {
      keys.add(new Key("nk_outbox_rows", Map.of("store", "API", "status", status)));
      keys.add(new Key("nk_outbox_oldest_seconds", Map.of("store", "API", "status", status)));
    }
    for (String state : List.of("RECEIVED", "PROCESSING", "COMPLETED", "ERROR", "CANCELLED"))
      keys.add(new Key("nk_async_jobs", Map.of("state", state)));
    for (String state : List.of("active", "idle", "pending", "max"))
      keys.add(new Key("nk_db_pool_connections", Map.of("service", "API", "state", state)));
    return java.util.Set.copyOf(keys);
  }

  private static double value(Map<Key, Double> actual, String name, Map<String, String> labels) {
    var result = actual.get(new Key(name, labels));
    assertNotNull(result);
    return result;
  }

  private static void statuses(Map<Key, Double> actual, String name, double p, double s, double e) {
    assertEquals(p, value(actual, name, Map.of("store", "API", "status", "PENDING")));
    assertEquals(s, value(actual, name, Map.of("store", "API", "status", "SENT")));
    assertEquals(e, value(actual, name, Map.of("store", "API", "status", "ERROR")));
  }

  private static AsyncJobMetricRecorder.Snapshot jobs() {
    return new AsyncJobMetricRecorder.Snapshot(
        Map.of(
            AsyncJobMetricRecorder.State.RECEIVED,
            11L,
            AsyncJobMetricRecorder.State.PROCESSING,
            23L,
            AsyncJobMetricRecorder.State.COMPLETED,
            37L,
            AsyncJobMetricRecorder.State.ERROR,
            41L,
            AsyncJobMetricRecorder.State.CANCELLED,
            53L));
  }

  private static void supply(Bundle b) {
    b.rows.record(new OutboxRowsMetricRecorder.Counts(3, 5, 2));
    b.age.record(
        new OutboxAgeMetricRecorder.Ages(
            Duration.ofSeconds(7), Duration.ofMillis(3500), Duration.ofNanos(1)));
    b.jobs.record(jobs());
    b.pool.record(new DbPoolMetricRecorder.Counts(3, 5, 2, 8));
  }

  @Test
  void apiprom001AllFifteenActualSamplesStartUnknownAndFixed() {
    try (var b = new Bundle("DEBUG")) {
      var actual = b.text();
      assertEquals(15, actual.size());
      assertTrue(actual.values().stream().allMatch(v -> Double.isNaN(v)));
      assertEquals(0, b.registry.closes.get());
    }
  }

  @Test
  void apiprom002RowsHaveLiteralApiStoreCountsAndNoOtherFamilyChanges() {
    try (var b = new Bundle("DEBUG")) {
      var old = new OutboxRowsMetricRecorder.Counts(3, 5, 2);
      b.rows.record(old);
      var actual = b.text();
      statuses(actual, "nk_outbox_rows", 3, 5, 2);
      statuses(actual, "nk_outbox_oldest_seconds", Double.NaN, Double.NaN, Double.NaN);
      assertEquals(3, old.pending());
      assertEquals(5, old.sent());
      assertEquals(2, old.error());
    }
  }

  @Test
  void apiprom003FractionalTinyZeroAndMaximumAgeNeverUseLongNanos() {
    try (var b = new Bundle("DEBUG")) {
      supply(b);
      statuses(b.text(), "nk_outbox_oldest_seconds", 7, 3.5, 0.000000001);
      b.age.record(new OutboxAgeMetricRecorder.Ages(Duration.ZERO, Duration.ZERO, Duration.ZERO));
      statuses(b.text(), "nk_outbox_oldest_seconds", 0, 0, 0);
      b.age.record(
          new OutboxAgeMetricRecorder.Ages(
              Duration.ofSeconds(Long.MAX_VALUE, 999999999), Duration.ZERO, Duration.ZERO));
      statuses(b.text(), "nk_outbox_oldest_seconds", 9.223372036854776E18, 0, 0);
    }
  }

  @Test
  void apiprom004EveryClosedJobStateUsesItsIndependentSuppliedCount() {
    try (var b = new Bundle("DEBUG")) {
      b.jobs.record(jobs());
      var actual = b.text();
      assertEquals(11, value(actual, "nk_async_jobs", Map.of("state", "RECEIVED")));
      assertEquals(23, value(actual, "nk_async_jobs", Map.of("state", "PROCESSING")));
      assertEquals(37, value(actual, "nk_async_jobs", Map.of("state", "COMPLETED")));
      assertEquals(41, value(actual, "nk_async_jobs", Map.of("state", "ERROR")));
      assertEquals(53, value(actual, "nk_async_jobs", Map.of("state", "CANCELLED")));
    }
  }

  @Test
  void apiprom005PoolShowsApiServiceAndRealZeroVersusMaximum() {
    try (var b = new Bundle("DEBUG")) {
      supply(b);
      var actual = b.text();
      assertEquals(
          3, value(actual, "nk_db_pool_connections", Map.of("service", "API", "state", "active")));
      assertEquals(
          5, value(actual, "nk_db_pool_connections", Map.of("service", "API", "state", "idle")));
      assertEquals(
          2, value(actual, "nk_db_pool_connections", Map.of("service", "API", "state", "pending")));
      assertEquals(
          8, value(actual, "nk_db_pool_connections", Map.of("service", "API", "state", "max")));
      b.pool.record(new DbPoolMetricRecorder.Counts(0, 0, 0, 1));
      assertEquals(
          0,
          value(b.text(), "nk_db_pool_connections", Map.of("service", "API", "state", "active")));
      assertEquals(
          1, value(b.text(), "nk_db_pool_connections", Map.of("service", "API", "state", "max")));
      b.pool.record(
          new DbPoolMetricRecorder.Counts(
              Long.MAX_VALUE, Long.MAX_VALUE, Long.MAX_VALUE, Long.MAX_VALUE));
      assertEquals(
          9.223372036854776E18,
          value(b.text(), "nk_db_pool_connections", Map.of("service", "API", "state", "active")));
    }
  }

  @Test
  void apiprom006MissingNeverChangesOtherOwnerOrPreviouslyReturnedText() {
    try (var a = new Bundle("DEBUG");
        var b = new Bundle("DEBUG")) {
      supply(a);
      supply(b);
      var original = a.text();
      a.rows.missing();
      a.age.missing();
      a.jobs.missing();
      a.pool.missing();
      assertTrue(a.text().values().stream().allMatch(v -> Double.isNaN(v)));
      statuses(original, "nk_outbox_rows", 3, 5, 2);
      statuses(b.text(), "nk_outbox_rows", 3, 5, 2);
      assertEquals(15, b.registry.getMeters().size());
    }
  }

  @Test
  void apiprom007StandardRetainsAndPublishesNothingAndCallerOwnsRegistry() {
    try (var b = new Bundle("STANDARD")) {
      supply(b);
      b.rows.missing();
      b.age.missing();
      b.jobs.missing();
      b.pool.missing();
      assertTrue(b.text().isEmpty());
      assertTrue(b.registry.getMeters().isEmpty());
      assertTrue(b.rows.snapshot().isEmpty());
      assertTrue(b.age.snapshot().isEmpty());
      assertTrue(b.jobs.snapshot().isEmpty());
      assertTrue(b.pool.snapshot().isEmpty());
      assertEquals(0, b.registry.closes.get());
    }
  }

  @Test
  void apiprom008FinitePublicationAndRepeatedSuppliesKeepFifteenSeries() throws Exception {
    try (var b = new Bundle("DEBUG");
        var other = new Bundle("DEBUG")) {
      var executor = Executors.newFixedThreadPool(4);
      try {
        var futures = new ArrayList<java.util.concurrent.Future<?>>();
        for (int n = 0; n < 64; n++) futures.add(executor.submit(() -> supply(b)));
        for (var f : futures) f.get(5, TimeUnit.SECONDS);
        for (int n = 0; n < 1000; n++) supply(b);
        statuses(b.text(), "nk_outbox_rows", 3, 5, 2);
        statuses(b.text(), "nk_outbox_oldest_seconds", 7, 3.5, 0.000000001);
        assertEquals(15, b.registry.getMeters().size());
        assertTrue(other.text().values().stream().allMatch(v -> Double.isNaN(v)));
      } finally {
        executor.shutdownNow();
        assertTrue(executor.awaitTermination(5, TimeUnit.SECONDS));
      }
    }
  }
}
