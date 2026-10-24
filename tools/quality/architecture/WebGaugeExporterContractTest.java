package dev.codex.schubert.nk.web.monitoring;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.protocol.file.MediaType;
import io.micrometer.core.instrument.MockClock;
import java.lang.ref.Reference;
import java.time.Duration;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Test;

/** WEBGAUGE001..006/1761: actual supplied Web precision registry, no pool/DB/HTTP/service. */
class WebGaugeExporterContractTest {
  private static final String POOL = "nk_db_pool_connections";
  private static final String ROWS = "nk_outbox_rows";
  private static final String AGE = "nk_outbox_oldest_seconds";
  private static final String STREAMS = "nk_media_streams";
  private static final Map<String, Set<String>> SPACE =
      Map.of(
          POOL,
          Set.of("service", "state"),
          ROWS,
          Set.of("store", "status"),
          AGE,
          Set.of("store", "status"),
          STREAMS,
          Set.of("media_type"));

  private static final class Bundle implements AutoCloseable {
    final OverflowSafeHttpMeterRegistry registry =
        new OverflowSafeHttpMeterRegistry(new MockClock());
    final WebDbPoolMetricRecorder pool;
    final WebOutboxMetricRecorder outbox;
    final MediaStreamsMetricRecorder streams;
    final WebGaugeMetricExporter exporter = new WebGaugeMetricExporter();

    Bundle(String mode) {
      pool = new WebDbPoolMetricRecorder(registry, mode);
      outbox = new WebOutboxMetricRecorder(registry, mode);
      streams = new MediaStreamsMetricRecorder(registry, mode);
      new HttpMetricRecorder(registry, mode);
      new MediaBytesMetricRecorder(registry, mode);
    }

    String text() {
      try {
        return exporter.scrapeGauges(registry, SPACE);
      } finally {
        Reference.reachabilityFence(this);
      }
    }

    public void close() {
      registry.close();
    }
  }

  private static double value(String text, String name, String key, String label) {
    var rows =
        text.lines()
            .filter(line -> line.startsWith(name + "{"))
            .filter(line -> line.contains(key + "=\"" + label + "\""))
            .toList();
    assertEquals(1, rows.size());
    String line = rows.getFirst();
    return Double.parseDouble(line.substring(line.lastIndexOf(' ') + 1));
  }

  private static void catalog(String text) {
    var types = text.lines().filter(line -> line.startsWith("# TYPE ")).toList();
    assertEquals(4, types.size());
    for (String name : List.of(POOL, ROWS, AGE, STREAMS))
      assertTrue(types.contains("# TYPE " + name + " gauge"));
    assertEquals(13, text.lines().filter(line -> !line.startsWith("#")).count());
    assertFalse(text.contains("nk_http_"));
    assertFalse(text.contains("nk_media_bytes"));
    assertFalse(text.contains(".histogram"));
    assertFalse(text.contains("_created"));
  }

  @Test
  void webgauge001ActualWebRegistryAllUnknownAndNoOtherFamilies() {
    try (var b = new Bundle("DEBUG")) {
      String result = b.text();
      catalog(result);
      assertEquals(13, result.lines().filter(line -> line.endsWith("} NaN")).count());
      assertFalse(b.registry.isClosed());
    }
  }

  @Test
  void webgauge002PoolTupleMissingAndKnownZero() {
    try (var b = new Bundle("DEBUG")) {
      var original = new WebDbPoolMetricRecorder.Counts(3, 5, 2, 8);
      b.pool.record(original);
      String result = b.text();
      assertEquals(3, value(result, POOL, "state", "active"));
      assertEquals(5, value(result, POOL, "state", "idle"));
      assertEquals(2, value(result, POOL, "state", "pending"));
      assertEquals(8, value(result, POOL, "state", "max"));
      b.pool.missing();
      String missing = b.text();
      for (String state : List.of("active", "idle", "pending", "max"))
        assertTrue(Double.isNaN(value(missing, POOL, "state", state)));
      b.pool.record(new WebDbPoolMetricRecorder.Counts(0, 0, 0, 1));
      String zero = b.text();
      for (String state : List.of("active", "idle", "pending"))
        assertEquals(0, value(zero, POOL, "state", state));
      assertEquals(1, value(zero, POOL, "state", "max"));
      assertEquals(3, original.active());
      assertEquals(8, original.maximum());
    }
  }

  @Test
  void webgauge003OutboxIndependentCountsAndFractionalSeconds() {
    try (var b = new Bundle("DEBUG")) {
      b.outbox.record(
          new WebOutboxMetricRecorder.Observation(
              2, 3, 0, Duration.ofMillis(1500), Duration.ofSeconds(2), Duration.ZERO));
      String result = b.text();
      assertEquals(2, value(result, ROWS, "status", "PENDING"));
      assertEquals(3, value(result, ROWS, "status", "SENT"));
      assertEquals(0, value(result, ROWS, "status", "ERROR"));
      assertEquals(1.5, value(result, AGE, "status", "PENDING"));
      assertEquals(2, value(result, AGE, "status", "SENT"));
      assertEquals(0, value(result, AGE, "status", "ERROR"));
      assertEquals(
          6,
          result
              .lines()
              .filter(line -> line.startsWith(ROWS + "{") || line.startsWith(AGE + "{"))
              .filter(line -> line.contains("store=\"WEB\""))
              .count());
      b.outbox.missing();
      String missing = b.text();
      for (String name : List.of(ROWS, AGE))
        for (String status : List.of("PENDING", "SENT", "ERROR"))
          assertTrue(Double.isNaN(value(missing, name, "status", status)));
      b.outbox.record(
          new WebOutboxMetricRecorder.Observation(
              0, 0, 0, Duration.ZERO, Duration.ZERO, Duration.ZERO));
      String zero = b.text();
      for (String name : List.of(ROWS, AGE))
        for (String status : List.of("PENDING", "SENT", "ERROR"))
          assertEquals(0, value(zero, name, "status", status));
    }
  }

  @Test
  void webgauge004EachMediaTypeHasIndependentKnownness() {
    try (var b = new Bundle("DEBUG")) {
      b.streams.record(MediaType.AUDIO, 2);
      b.streams.record(MediaType.VIDEO, 0);
      String result = b.text();
      assertEquals(2, value(result, STREAMS, "media_type", "AUDIO"));
      assertEquals(0, value(result, STREAMS, "media_type", "VIDEO"));
      assertTrue(Double.isNaN(value(result, STREAMS, "media_type", "MUSIC")));
      b.streams.missing(MediaType.AUDIO);
      String missing = b.text();
      assertTrue(Double.isNaN(value(missing, STREAMS, "media_type", "AUDIO")));
      assertEquals(0, value(missing, STREAMS, "media_type", "VIDEO"));
    }
  }

  @Test
  void webgauge005OtherOwnerAndStandardRemainIndependent() {
    try (var b = new Bundle("DEBUG");
        var other = new Bundle("DEBUG");
        var standard = new Bundle("STANDARD")) {
      b.pool.record(new WebDbPoolMetricRecorder.Counts(3, 5, 2, 8));
      assertEquals(3, value(b.text(), POOL, "state", "active"));
      assertEquals(13, other.text().lines().filter(line -> line.endsWith("} NaN")).count());
      assertEquals("", standard.text());
      assertFalse(b.registry.isClosed());
      assertFalse(other.registry.isClosed());
      assertFalse(standard.registry.isClosed());
    }
  }

  @Test
  void webgauge006FiniteConcurrentScrapesKeepLiteralValues() throws Exception {
    try (var b = new Bundle("DEBUG");
        var workers = Executors.newFixedThreadPool(4)) {
      b.pool.record(new WebDbPoolMetricRecorder.Counts(3, 5, 2, 8));
      b.outbox.record(
          new WebOutboxMetricRecorder.Observation(
              2, 3, 0, Duration.ofMillis(1500), Duration.ofSeconds(2), Duration.ZERO));
      b.streams.record(MediaType.AUDIO, 2);
      b.streams.record(MediaType.VIDEO, 0);
      b.streams.record(MediaType.MUSIC, 7);
      var jobs = new java.util.ArrayList<Future<?>>();
      for (int index = 0; index < 64; index++)
        jobs.add(
            workers.submit(
                () -> {
                  String result = b.text();
                  catalog(result);
                  assertEquals(3, value(result, POOL, "state", "active"));
                  assertEquals(5, value(result, POOL, "state", "idle"));
                  assertEquals(2, value(result, POOL, "state", "pending"));
                  assertEquals(8, value(result, POOL, "state", "max"));
                  assertEquals(2, value(result, ROWS, "status", "PENDING"));
                  assertEquals(3, value(result, ROWS, "status", "SENT"));
                  assertEquals(0, value(result, ROWS, "status", "ERROR"));
                  assertEquals(1.5, value(result, AGE, "status", "PENDING"));
                  assertEquals(2, value(result, AGE, "status", "SENT"));
                  assertEquals(0, value(result, AGE, "status", "ERROR"));
                  assertEquals(2, value(result, STREAMS, "media_type", "AUDIO"));
                  assertEquals(0, value(result, STREAMS, "media_type", "VIDEO"));
                  assertEquals(7, value(result, STREAMS, "media_type", "MUSIC"));
                  assertEquals(0, result.lines().filter(line -> line.endsWith("} NaN")).count());
                }));
      for (var job : jobs) job.get(10, TimeUnit.SECONDS);
      assertFalse(b.registry.isClosed());
    }
  }
}
