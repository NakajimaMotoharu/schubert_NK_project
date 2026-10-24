package dev.codex.schubert.nk.web.monitoring;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.protocol.file.MediaType;
import io.micrometer.core.instrument.Counter;
import io.micrometer.core.instrument.Meter;
import io.micrometer.core.instrument.MockClock;
import io.micrometer.prometheusmetrics.PrometheusConfig;
import io.micrometer.prometheusmetrics.PrometheusMeterRegistry;
import io.prometheus.metrics.model.registry.PrometheusRegistry;
import java.lang.ref.Reference;
import java.time.Duration;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Properties;
import java.util.Set;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.regex.Pattern;
import org.jspecify.annotations.Nullable;
import org.junit.jupiter.api.Test;

/**
 * Test-only in-memory actual SDK. PGPROM001..008/1741; no server, DB, raw data or live collector.
 */
class WebPrometheusGaugeContractTest {
  private static final List<MediaType> TYPES =
      List.of(MediaType.AUDIO, MediaType.VIDEO, MediaType.MUSIC);
  private static final List<MediaBytesMetricRecorder.Mode> MODES =
      List.of(
          MediaBytesMetricRecorder.Mode.INLINE,
          MediaBytesMetricRecorder.Mode.DOWNLOAD,
          MediaBytesMetricRecorder.Mode.RANGE);
  private static final List<Integer> STATUSES = List.of(200, 206, 416, 503);
  private static final String POOL = "nk_db_pool_connections";
  private static final String ROWS = "nk_outbox_rows";
  private static final String AGE = "nk_outbox_oldest_seconds";
  private static final String STREAMS = "nk_media_streams";
  private static final String BYTES = "nk_media_bytes_total";
  private static final Set<String> NAMES = Set.of(POOL, ROWS, AGE, STREAMS, BYTES);
  private static final Pattern LINE =
      Pattern.compile("([a-z_]+)(?:\\{([^{}]*)\\})? (NaN|[-+0-9.eE]+)");
  private static final Pattern LABEL = Pattern.compile("([a-z_]+)=\"([^\"\\\\]*)\"");

  private static final PrometheusConfig CONFIG =
      new PrometheusConfig() {
        @Override
        public @Nullable String get(String key) {
          return null;
        }

        @Override
        public Properties prometheusProperties() {
          var p = new Properties();
          p.setProperty("io.prometheus.exporter.include_created_timestamps", "false");
          p.setProperty("io.prometheus.exporter.exemplars_on_all_metric_types", "false");
          return p;
        }
      };

  private static class Registry extends PrometheusMeterRegistry implements AutoCloseable {
    final AtomicInteger closes = new AtomicInteger();

    Registry() {
      super(CONFIG, new PrometheusRegistry(), new MockClock());
    }

    @Override
    public void close() {
      closes.incrementAndGet();
      super.close();
    }
  }

  private static final class Bundle implements AutoCloseable {
    final Registry registry = new Registry();
    final WebDbPoolMetricRecorder pool;
    final WebOutboxMetricRecorder outbox;
    final MediaStreamsMetricRecorder streams;
    final MediaBytesMetricRecorder bytes;

    Bundle(String mode) {
      pool = new WebDbPoolMetricRecorder(registry, mode);
      outbox = new WebOutboxMetricRecorder(registry, mode);
      streams = new MediaStreamsMetricRecorder(registry, mode);
      bytes = new MediaBytesMetricRecorder(registry, mode);
    }

    Map<Key, Double> text() {
      try {
        return parse(registry.scrape());
      } finally {
        Reference.reachabilityFence(this);
      }
    }

    @Override
    public void close() {
      registry.close();
    }
  }

  private record Key(String name, Map<String, String> labels) {
    Key {
      name = Objects.requireNonNull(name);
      labels = Map.copyOf(labels);
    }
  }

  private static Key key(String name, String... values) {
    var labels = new HashMap<String, String>();
    for (int i = 0; i < values.length; i += 2) {
      assertNull(labels.put(values[i], values[i + 1]), "unique fixed expected label");
    }
    return new Key(name, Map.copyOf(labels));
  }

  /** Actual parser only; expected names/labels/values are independent literals below. */
  private static Map<Key, Double> parse(String text) {
    var result = new HashMap<Key, Double>();
    var types = new HashMap<String, String>();
    for (String line : text.split("\n")) {
      if (line.isEmpty() || line.startsWith("# HELP ")) continue;
      if (line.startsWith("# TYPE ")) {
        String[] parts = line.split(" ");
        assertEquals(4, parts.length);
        assertNull(types.put(parts[2], parts[3]), "unique native family type");
        continue;
      }
      var match = LINE.matcher(line);
      assertTrue(match.matches(), "fixed-label native text only, no arbitrary timestamp");
      var labels = new HashMap<String, String>();
      if (match.group(2) != null && !match.group(2).isEmpty()) {
        for (String part : match.group(2).split(",")) {
          var label = LABEL.matcher(part);
          assertTrue(label.matches(), "fixed labels need no value escaping");
          assertNull(labels.put(label.group(1), label.group(2)), "no duplicate actual label");
        }
      }
      var k = new Key(match.group(1), Map.copyOf(labels));
      assertNull(result.put(k, Double.valueOf(match.group(3))), "no duplicate actual series");
    }
    if (!result.isEmpty()) {
      assertEquals(
          Map.of(POOL, "gauge", ROWS, "gauge", AGE, "gauge", STREAMS, "gauge", BYTES, "counter"),
          types);
      assertEquals(
          NAMES,
          result.keySet().stream().map(Key::name).collect(java.util.stream.Collectors.toSet()));
    } else assertTrue(types.isEmpty(), "STANDARD emits no family");
    return Map.copyOf(result);
  }

  private static Set<Key> expectedKeys() {
    var result = new HashSet<Key>();
    for (String state : List.of("active", "idle", "pending", "max"))
      result.add(key(POOL, "service", "WEB", "state", state));
    for (String status : List.of("PENDING", "SENT", "ERROR")) {
      result.add(key(ROWS, "store", "WEB", "status", status));
      result.add(key(AGE, "store", "WEB", "status", status));
    }
    for (String type : List.of("AUDIO", "VIDEO", "MUSIC")) {
      result.add(key(STREAMS, "media_type", type));
      for (String mode : List.of("INLINE", "DOWNLOAD", "RANGE"))
        for (String status : List.of("200", "206", "416", "503"))
          result.add(key(BYTES, "media_type", type, "mode", mode, "status", status));
    }
    return Set.copyOf(result);
  }

  private static double value(Map<Key, Double> actual, String name, String... labels) {
    Double result = actual.get(key(name, labels));
    assertNotNull(result, "declared literal sample must exist");
    return result;
  }

  private static WebOutboxMetricRecorder.Observation outbox(
      long pending, long sent, long error, Duration a, Duration b, Duration c) {
    return new WebOutboxMetricRecorder.Observation(pending, sent, error, a, b, c);
  }

  @Test
  void pgprom001InitialActualNativeTextUsesAllFortyNineClosedSeries() {
    try (var b = new Bundle("DEBUG")) {
      var actual = b.text();
      assertEquals(49, actual.size());
      assertEquals(expectedKeys(), actual.keySet());
      assertEquals(13, actual.values().stream().filter(v -> Double.isNaN(v)).count());
      assertEquals(36, actual.values().stream().filter(v -> v == 0.0).count());
      assertEquals(0, b.registry.closes.get());
    }
  }

  @Test
  void pgprom002PoolUnknownZeroAndSuppliedTupleAreNotConflated() {
    try (var b = new Bundle("DEBUG")) {
      var original = new WebDbPoolMetricRecorder.Counts(3, 5, 2, 8);
      b.pool.record(original);
      var actual = b.text();
      assertEquals(3.0, value(actual, POOL, "service", "WEB", "state", "active"));
      assertEquals(5.0, value(actual, POOL, "service", "WEB", "state", "idle"));
      assertEquals(2.0, value(actual, POOL, "service", "WEB", "state", "pending"));
      assertEquals(8.0, value(actual, POOL, "service", "WEB", "state", "max"));
      b.pool.missing();
      for (String state : List.of("active", "idle", "pending", "max"))
        assertTrue(Double.isNaN(value(b.text(), POOL, "service", "WEB", "state", state)));
      b.pool.record(new WebDbPoolMetricRecorder.Counts(0, 0, 0, 1));
      assertEquals(0.0, value(b.text(), POOL, "service", "WEB", "state", "active"));
      assertEquals(1.0, value(b.text(), POOL, "service", "WEB", "state", "max"));
      b.pool.record(
          new WebDbPoolMetricRecorder.Counts(
              Long.MAX_VALUE, Long.MAX_VALUE, Long.MAX_VALUE, Long.MAX_VALUE));
      assertEquals(9.223372036854776E18, value(b.text(), POOL, "service", "WEB", "state", "max"));
      assertEquals(3, original.active());
      assertEquals(8, original.maximum());
    }
  }

  @Test
  void pgprom003OutboxRowsAgesMissingAndTrueZeroHaveIndependentValues() {
    try (var b = new Bundle("DEBUG")) {
      var original = outbox(2, 1, 0, Duration.ofSeconds(7), Duration.ofMillis(3500), Duration.ZERO);
      b.outbox.record(original);
      var actual = b.text();
      assertEquals(2.0, value(actual, ROWS, "store", "WEB", "status", "PENDING"));
      assertEquals(1.0, value(actual, ROWS, "store", "WEB", "status", "SENT"));
      assertEquals(0.0, value(actual, ROWS, "store", "WEB", "status", "ERROR"));
      assertEquals(7.0, value(actual, AGE, "store", "WEB", "status", "PENDING"));
      assertEquals(3.5, value(actual, AGE, "store", "WEB", "status", "SENT"));
      assertEquals(0.0, value(actual, AGE, "store", "WEB", "status", "ERROR"));
      b.outbox.missing();
      assertTrue(Double.isNaN(value(b.text(), AGE, "store", "WEB", "status", "PENDING")));
      b.outbox.record(outbox(0, 0, 0, Duration.ZERO, Duration.ZERO, Duration.ZERO));
      assertEquals(0.0, value(b.text(), AGE, "store", "WEB", "status", "PENDING"));
      assertEquals(2, original.pending());
    }
  }

  @Test
  void pgprom004MediaNativeCounterSuffixAndLiteralVectorSurviveExtremeDeltas() {
    try (var b = new Bundle("DEBUG")) {
      b.streams.record(MediaType.AUDIO, 0);
      b.streams.record(MediaType.VIDEO, 2);
      b.streams.record(MediaType.MUSIC, 4);
      assertEquals(0.0, value(b.text(), STREAMS, "media_type", "AUDIO"));
      assertEquals(2.0, value(b.text(), STREAMS, "media_type", "VIDEO"));
      assertEquals(4.0, value(b.text(), STREAMS, "media_type", "MUSIC"));
      b.streams.missing(MediaType.VIDEO);
      assertTrue(Double.isNaN(value(b.text(), STREAMS, "media_type", "VIDEO")));
      int index = 0;
      for (var type : TYPES)
        for (var mode : MODES)
          for (int status : STATUSES) b.bytes.record(type, mode, status, ++index);
      var actual = b.text();
      int expected = 0;
      for (String type : List.of("AUDIO", "VIDEO", "MUSIC"))
        for (String mode : List.of("INLINE", "DOWNLOAD", "RANGE"))
          for (String status : List.of("200", "206", "416", "503"))
            assertEquals(
                (double) ++expected,
                value(actual, BYTES, "media_type", type, "mode", mode, "status", status));
      assertEquals(
          666.0,
          actual.entrySet().stream()
              .filter(e -> e.getKey().name().equals(BYTES))
              .mapToDouble(Map.Entry::getValue)
              .sum());
      b.bytes.record(MediaType.AUDIO, MediaBytesMetricRecorder.Mode.INLINE, 200, 0);
      assertEquals(
          1.0, value(b.text(), BYTES, "media_type", "AUDIO", "mode", "INLINE", "status", "200"));
      b.bytes.record(MediaType.AUDIO, MediaBytesMetricRecorder.Mode.INLINE, 200, Long.MAX_VALUE);
      b.bytes.record(MediaType.AUDIO, MediaBytesMetricRecorder.Mode.INLINE, 200, Long.MAX_VALUE);
      assertEquals(
          1.8446744073709552E19,
          value(b.text(), BYTES, "media_type", "AUDIO", "mode", "INLINE", "status", "200"));
    }
  }

  @Test
  void pgprom005StandardRetainsNothingAndDoesNotCloseBorrowedRegistry() {
    try (var b = new Bundle("STANDARD")) {
      b.pool.record(new WebDbPoolMetricRecorder.Counts(1, 2, 0, 8));
      b.outbox.record(outbox(0, 0, 0, Duration.ZERO, Duration.ZERO, Duration.ZERO));
      b.streams.record(MediaType.AUDIO, 2);
      b.bytes.record(MediaType.AUDIO, MediaBytesMetricRecorder.Mode.INLINE, 200, 3);
      assertTrue(b.text().isEmpty());
      assertEquals(0, b.registry.getMeters().size());
      assertTrue(b.pool.snapshot().isEmpty());
      assertTrue(b.outbox.snapshot().isEmpty());
      assertTrue(b.streams.snapshot(MediaType.AUDIO).isEmpty());
      assertEquals(0, b.registry.closes.get());
    }
  }

  private static final class FailedCounterRegistry extends Registry {
    final AtomicInteger calls = new AtomicInteger();
    final Throwable failure;

    FailedCounterRegistry(Throwable failure) {
      this.failure = failure;
    }

    @Override
    public Counter newCounter(Meter.Id id) {
      if (calls.incrementAndGet() == 2) {
        if (failure instanceof Error error) throw error;
        throw (RuntimeException) failure;
      }
      return super.newCounter(id);
    }
  }

  @Test
  void pgprom006PartialActualSdkRegistrationRetainsCallerLifetimeAndFailureIdentity() {
    for (Throwable failure :
        List.of(new IllegalStateException("owned fixture"), new AssertionError("owned fixture"))) {
      var r = new FailedCounterRegistry(failure);
      try {
        assertSame(
            failure,
            assertThrows(failure.getClass(), () -> new MediaBytesMetricRecorder(r, "DEBUG")));
        assertEquals(2, r.calls.get());
        assertEquals(1, r.getMeters().size());
        assertEquals(0, r.closes.get());
      } finally {
        r.close();
      }
      assertEquals(1, r.closes.get());
    }
  }

  @Test
  void pgprom007FiniteOwnedWorkersDoNotGrowCardinalityOrLoseIncrements() throws Exception {
    try (var b = new Bundle("DEBUG")) {
      var pool = Executors.newFixedThreadPool(4);
      try {
        var futures = new ArrayList<java.util.concurrent.Future<?>>();
        for (int n = 0; n < 64; n++) {
          futures.add(
              pool.submit(
                  () -> {
                    b.bytes.record(MediaType.AUDIO, MediaBytesMetricRecorder.Mode.INLINE, 200, 7);
                    b.pool.record(new WebDbPoolMetricRecorder.Counts(3, 5, 2, 8));
                    b.outbox.record(
                        outbox(
                            2,
                            1,
                            0,
                            Duration.ofSeconds(7),
                            Duration.ofMillis(3500),
                            Duration.ZERO));
                    b.streams.record(MediaType.MUSIC, 4);
                  }));
        }
        for (var future : futures) future.get(5, TimeUnit.SECONDS);
        assertEquals(
            448.0,
            value(b.text(), BYTES, "media_type", "AUDIO", "mode", "INLINE", "status", "200"));
        assertEquals(expectedKeys(), b.text().keySet());
        assertEquals(49, b.registry.getMeters().size());
      } finally {
        pool.shutdownNow();
        assertTrue(pool.awaitTermination(5, TimeUnit.SECONDS), "owned finite worker cleanup");
      }
    }
  }

  @Test
  void pgprom008SeparateOwnersAndRepeatedSuppliesKeepOnlyClosedNativeLabels() {
    try (var first = new Bundle("DEBUG");
        var second = new Bundle("DEBUG")) {
      for (int n = 0; n < 1000; n++) {
        first.pool.record(new WebDbPoolMetricRecorder.Counts(3, 5, 2, 8));
        first.bytes.record(MediaType.MUSIC, MediaBytesMetricRecorder.Mode.RANGE, 206, 1);
      }
      var a = first.text();
      var b = second.text();
      assertEquals(expectedKeys(), a.keySet());
      assertEquals(expectedKeys(), b.keySet());
      assertEquals(
          1000.0, value(a, BYTES, "media_type", "MUSIC", "mode", "RANGE", "status", "206"));
      assertEquals(0.0, value(b, BYTES, "media_type", "MUSIC", "mode", "RANGE", "status", "206"));
      assertTrue(Double.isNaN(value(b, POOL, "service", "WEB", "state", "active")));
      assertEquals(0, first.registry.closes.get());
      assertEquals(0, second.registry.closes.get());
    }
  }
}
