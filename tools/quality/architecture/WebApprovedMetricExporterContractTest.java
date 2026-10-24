package dev.codex.schubert.nk.web.monitoring;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.protocol.file.MediaType;
import io.micrometer.core.instrument.Meter;
import io.micrometer.core.instrument.MockClock;
import io.micrometer.core.instrument.Tag;
import io.micrometer.core.instrument.Tags;
import io.micrometer.core.instrument.distribution.CountAtBucket;
import io.micrometer.core.instrument.distribution.HistogramSnapshot;
import io.micrometer.core.instrument.distribution.ValueAtPercentile;
import io.micrometer.core.instrument.noop.NoopCounter;
import io.micrometer.core.instrument.noop.NoopGauge;
import io.micrometer.core.instrument.noop.NoopTimer;
import io.micrometer.core.instrument.simple.SimpleConfig;
import io.micrometer.core.instrument.simple.SimpleMeterRegistry;
import java.lang.ref.Reference;
import java.time.Duration;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.Test;

/** APPROVED001..012/1767: direct copied Labels at each model, no preflight/reread shortcut. */
class WebApprovedMetricExporterContractTest {
  private static final String HTTP = "nk_http_requests_total";
  private static final String TIMER = "nk_http_request_duration_seconds";
  private static final String POOL = "nk_db_pool_connections";
  private static final String ROWS = "nk_outbox_rows";
  private static final String AGE = "nk_outbox_oldest_seconds";
  private static final String STREAMS = "nk_media_streams";
  private static final String BYTES = "nk_media_bytes_total";
  private static final Map<String, Map<String, String>> FIXED =
      Map.of(
          HTTP, Map.of("service", "WEB", "route", "/login", "method", "GET", "status_class", "2xx"),
          TIMER, Map.of("service", "WEB", "route", "/login"),
          POOL, Map.of("service", "WEB", "state", "active"),
          ROWS, Map.of("store", "WEB", "status", "PENDING"),
          AGE, Map.of("store", "WEB", "status", "PENDING"),
          STREAMS, Map.of("media_type", "AUDIO"),
          BYTES, Map.of("media_type", "AUDIO", "mode", "INLINE", "status", "200"));
  private final WebGaugeMetricExporter gauge = new WebGaugeMetricExporter();
  private final WebCounterMetricExporter counter = new WebCounterMetricExporter();
  private final WebDurationMetricExporter timer = new WebDurationMetricExporter();

  private static final class Registry extends SimpleMeterRegistry implements AutoCloseable {
    final List<Meter> meters;

    Registry(Meter... meters) {
      super(SimpleConfig.DEFAULT, new MockClock());
      this.meters = List.of(meters);
    }

    public List<Meter> getMeters() {
      return meters;
    }
  }

  private static final class MutableTag implements Tag {
    final String key;
    String value;

    MutableTag(String key, String value) {
      this.key = key;
      this.value = value;
    }

    public String getKey() {
      return key;
    }

    public String getValue() {
      return value;
    }

    public int compareTo(Tag other) {
      return key.compareTo(other.getKey());
    }
  }

  private static Meter.Id identity(String name, List<Tag> tags) {
    return new Meter.Id(name, Tags.empty(), "", "", Meter.Type.GAUGE) {
      public List<Tag> getTags() {
        return tags;
      }
    };
  }

  private static Meter.Id identity(String name, Map<String, String> tags) {
    return identity(
        name, tags.entrySet().stream().map(e -> Tag.of(e.getKey(), e.getValue())).toList());
  }

  private static HistogramSnapshot snapshot() {
    return new HistogramSnapshot(
        1,
        1,
        0,
        new ValueAtPercentile[0],
        new CountAtBucket[] {new CountAtBucket(1_000_000_000.0, 1)},
        null);
  }

  private static final class Bundle implements AutoCloseable {
    final OverflowSafeHttpMeterRegistry registry =
        new OverflowSafeHttpMeterRegistry(new MockClock());
    final WebDbPoolMetricRecorder pool = new WebDbPoolMetricRecorder(registry, "DEBUG");
    final WebOutboxMetricRecorder outbox = new WebOutboxMetricRecorder(registry, "DEBUG");
    final MediaStreamsMetricRecorder streams = new MediaStreamsMetricRecorder(registry, "DEBUG");
    final HttpMetricRecorder http = new HttpMetricRecorder(registry, "DEBUG");
    final MediaBytesMetricRecorder bytes = new MediaBytesMetricRecorder(registry, "DEBUG");

    String text() {
      try {
        return new WebGaugeMetricExporter().scrapeApprovedGauges(registry)
            + new WebCounterMetricExporter().scrapeApprovedCounters(registry)
            + new WebDurationMetricExporter().scrapeApprovedTimers(registry);
      } finally {
        Reference.reachabilityFence(this);
      }
    }

    void supplied() {
      pool.record(new WebDbPoolMetricRecorder.Counts(3, 5, 2, 8));
      outbox.record(
          new WebOutboxMetricRecorder.Observation(
              2, 3, 0, Duration.ofMillis(1500), Duration.ofSeconds(2), Duration.ZERO));
      streams.record(MediaType.AUDIO, 2);
      streams.record(MediaType.VIDEO, 0);
      streams.record(MediaType.MUSIC, 7);
      http.record("/login", "GET", 200, 1);
      bytes.record(MediaType.AUDIO, MediaBytesMetricRecorder.Mode.INLINE, 200, 7);
    }

    public void close() {
      registry.close();
    }
  }

  private static void catalog(String text) {
    var expected =
        Map.of(
            HTTP,
            "counter",
            TIMER,
            "histogram",
            POOL,
            "gauge",
            ROWS,
            "gauge",
            AGE,
            "gauge",
            STREAMS,
            "gauge",
            BYTES,
            "counter");
    var types = text.lines().filter(line -> line.startsWith("# TYPE ")).toList();
    assertEquals(7, types.size());
    expected.forEach((name, type) -> assertTrue(types.contains("# TYPE " + name + " " + type)));
    assertEquals(2219, text.lines().filter(line -> !line.startsWith("#")).count());
    assertFalse(text.contains("_total_total"));
    assertFalse(text.contains(".histogram"));
  }

  private static double value(String text, String name, Map<String, String> labels) {
    var rows =
        text.lines()
            .filter(line -> line.startsWith(name + "{"))
            .filter(
                line ->
                    labels.entrySet().stream()
                        .allMatch(e -> line.contains(e.getKey() + "=\"" + e.getValue() + "\"")))
            .toList();
    assertEquals(1, rows.size());
    String line = rows.getFirst();
    return Double.parseDouble(line.substring(line.lastIndexOf(' ') + 1));
  }

  @Test
  void approved001RealSevenFamilyRegistryAndIndependentWireCounts() {
    try (var b = new Bundle()) {
      String initial = b.text();
      catalog(initial);
      assertEquals(13, initial.lines().filter(line -> line.endsWith("} NaN")).count());
      assertEquals(0, value(initial, HTTP, FIXED.get(HTTP)));
      b.supplied();
      String result = b.text();
      catalog(result);
      assertEquals(1, value(result, HTTP, FIXED.get(HTTP)));
      assertEquals(7, value(result, BYTES, FIXED.get(BYTES)));
      assertEquals(1.0E-9, value(result, TIMER + "_sum", FIXED.get(TIMER)));
      assertEquals(3, value(result, POOL, FIXED.get(POOL)));
      assertEquals(0, result.lines().filter(line -> line.endsWith("} NaN")).count());
    }
  }

  @Test
  void approved002EveryGaugeFieldRejectsUnknownWhileGenericApiIsPreserved() {
    for (String name : List.of(POOL, ROWS, AGE, STREAMS))
      for (String key : FIXED.get(name).keySet()) {
        var invalid = new HashMap<>(FIXED.get(name));
        invalid.put(key, "UNAPPROVED_FIXTURE");
        try (var source = new Registry(new NoopGauge(identity(name, invalid)))) {
          assertThrows(IllegalArgumentException.class, () -> gauge.scrapeApprovedGauges(source));
          assertTrue(
              gauge
                  .scrapeGauges(source, Map.of(name, FIXED.get(name).keySet()))
                  .contains("UNAPPROVED_FIXTURE"));
        }
      }
  }

  @Test
  void approved003EveryCounterFieldUsesClosedValues() {
    for (String name : List.of(HTTP, BYTES))
      for (String key : FIXED.get(name).keySet()) {
        var invalid = new HashMap<>(FIXED.get(name));
        invalid.put(key, "UNAPPROVED_FIXTURE");
        try (var source = new Registry(new NoopCounter(identity(name, invalid)))) {
          assertThrows(
              IllegalArgumentException.class, () -> counter.scrapeApprovedCounters(source));
        }
      }
  }

  @Test
  void approved004RawTimerRouteAndOtherServiceAreRejected() {
    for (String key : List.of("route", "service")) {
      var invalid = new HashMap<>(FIXED.get(TIMER));
      invalid.put(key, "UNAPPROVED_FIXTURE");
      try (var source = new Registry(new NoopTimer(identity(TIMER, invalid)))) {
        assertThrows(IllegalArgumentException.class, () -> timer.scrapeApprovedTimers(source));
      }
    }
  }

  @Test
  void approved005GaugeValueMutationCannotChangeCopiedLabels() {
    var state = new MutableTag("state", "active");
    var meter =
        new NoopGauge(identity(POOL, List.of(Tag.of("service", "WEB"), state))) {
          public double value() {
            state.value = "UNAPPROVED_FIXTURE";
            return 3;
          }
        };
    try (var source = new Registry(meter)) {
      String result = gauge.scrapeApprovedGauges(source);
      assertEquals(3, value(result, POOL, FIXED.get(POOL)));
      assertEquals("UNAPPROVED_FIXTURE", state.value);
      assertFalse(result.contains(state.value));
    }
  }

  @Test
  void approved006CounterNameAndTagAreCopiedBeforeValueRead() {
    var route = new MutableTag("route", "/login");
    var names = new AtomicInteger();
    var meterIdentity =
        new Meter.Id(HTTP, Tags.empty(), "", "", Meter.Type.COUNTER) {
          public String getName() {
            return names.incrementAndGet() == 1 ? HTTP : "nk_unapproved_fixture_total";
          }

          public List<Tag> getTags() {
            return List.of(
                Tag.of("service", "WEB"),
                route,
                Tag.of("method", "GET"),
                Tag.of("status_class", "2xx"));
          }
        };
    var meter =
        new NoopCounter(meterIdentity) {
          public double count() {
            route.value = "/unapproved-fixture/123";
            return 1;
          }
        };
    names.set(0);
    try (var source = new Registry(meter)) {
      String result = counter.scrapeApprovedCounters(source);
      assertEquals(1, value(result, HTTP, FIXED.get(HTTP)));
      assertEquals(1, names.get());
      assertEquals("/unapproved-fixture/123", route.value);
      assertFalse(result.contains("unapproved"));
    }
  }

  @Test
  void approved007TimerSnapshotMutationCannotChangeCopiedLabels() {
    var route = new MutableTag("route", "/login");
    var meter =
        new NoopTimer(identity(TIMER, List.of(Tag.of("service", "WEB"), route))) {
          public HistogramSnapshot takeSnapshot() {
            route.value = "/unapproved-fixture/123";
            return snapshot();
          }
        };
    try (var source = new Registry(meter)) {
      String result = timer.scrapeApprovedTimers(source);
      assertEquals(1.0E-9, value(result, TIMER + "_sum", FIXED.get(TIMER)));
      assertEquals("/unapproved-fixture/123", route.value);
      assertFalse(result.contains("unapproved"));
    }
  }

  @Test
  void approved008UnknownMetersNeverInvokeValueProvider() {
    var reads = new AtomicInteger();
    var meter =
        new NoopGauge(identity("nk_unknown_fixture", Map.of("actor", "UNAPPROVED"))) {
          public double value() {
            reads.incrementAndGet();
            throw new AssertionError("unselected provider");
          }
        };
    try (var source = new Registry(meter)) {
      assertEquals("", gauge.scrapeApprovedGauges(source));
      assertEquals("", counter.scrapeApprovedCounters(source));
      assertEquals("", timer.scrapeApprovedTimers(source));
      assertEquals(0, reads.get());
    }
  }

  @Test
  void approved009EmptyAndClosedBorrowedRegistriesRemainDistinct() {
    var source = new Registry();
    try {
      assertEquals("", gauge.scrapeApprovedGauges(source));
      assertEquals("", counter.scrapeApprovedCounters(source));
      assertEquals("", timer.scrapeApprovedTimers(source));
      assertFalse(source.isClosed());
      source.close();
      assertThrows(IllegalStateException.class, () -> gauge.scrapeApprovedGauges(source));
      assertThrows(IllegalStateException.class, () -> counter.scrapeApprovedCounters(source));
      assertThrows(IllegalStateException.class, () -> timer.scrapeApprovedTimers(source));
    } finally {
      source.close();
    }
  }

  @Test
  void approved010TagProviderRuntimeAndErrorKeepIdentity() {
    var failure = new IllegalStateException("fixture");
    var meterIdentity =
        new Meter.Id(POOL, Tags.empty(), "", "", Meter.Type.GAUGE) {
          public List<Tag> getTags() {
            throw failure;
          }
        };
    try (var source = new Registry(new NoopGauge(meterIdentity))) {
      assertSame(
          failure,
          assertThrows(IllegalStateException.class, () -> gauge.scrapeApprovedGauges(source)));
    }
    var fatal = new AssertionError("fixture");
    var fatalIdentity =
        new Meter.Id(TIMER, Tags.empty(), "", "", Meter.Type.TIMER) {
          public List<Tag> getTags() {
            throw fatal;
          }
        };
    try (var source = new Registry(new NoopTimer(fatalIdentity))) {
      assertSame(
          fatal, assertThrows(AssertionError.class, () -> timer.scrapeApprovedTimers(source)));
    }
  }

  @Test
  void approved011ConcurrentRealScrapesUseOnlyLiteralCatalog() throws Exception {
    try (var b = new Bundle();
        var workers = Executors.newFixedThreadPool(4)) {
      b.supplied();
      var jobs = new ArrayList<Future<?>>();
      for (int index = 0; index < 64; index++)
        jobs.add(
            workers.submit(
                () -> {
                  String result = b.text();
                  catalog(result);
                  assertEquals(1, value(result, HTTP, FIXED.get(HTTP)));
                  assertEquals(3, value(result, POOL, FIXED.get(POOL)));
                  assertEquals(1.0E-9, value(result, TIMER + "_sum", FIXED.get(TIMER)));
                }));
      for (var job : jobs) job.get(10, TimeUnit.SECONDS);
      assertFalse(b.registry.isClosed());
    }
  }

  @Test
  void approved012NullMissingExtraDuplicateContractsNeverBypassCatalog() {
    assertThrows(NullPointerException.class, () -> gauge.scrapeApprovedGauges(null));
    assertThrows(NullPointerException.class, () -> counter.scrapeApprovedCounters(null));
    assertThrows(NullPointerException.class, () -> timer.scrapeApprovedTimers(null));
    FIXED.forEach(
        (name, values) -> {
          var missing = new HashMap<>(values);
          missing.remove(values.keySet().iterator().next());
          var extra = new HashMap<>(values);
          extra.put("actor", "UNAPPROVED_FIXTURE");
          for (var invalid : List.of(missing, extra))
            reject(name, identity(name, invalid), IllegalArgumentException.class);
          var tags = new ArrayList<Tag>();
          values.forEach((key, value) -> tags.add(Tag.of(key, value)));
          tags.add(tags.getFirst());
          reject(name, identity(name, tags), IllegalArgumentException.class);
          var nullTags = new ArrayList<Tag>();
          nullTags.add(null);
          reject(name, identity(name, nullTags), NullPointerException.class);
          var nullValue = new MutableTag(values.keySet().iterator().next(), null);
          reject(name, identity(name, List.of(nullValue)), NullPointerException.class);
        });
  }

  private void reject(String name, Meter.Id meterIdentity, Class<? extends Throwable> expected) {
    if (name.equals(HTTP) || name.equals(BYTES)) {
      try (var source = new Registry(new NoopCounter(meterIdentity))) {
        assertThrows(expected, () -> counter.scrapeApprovedCounters(source));
      }
    } else if (name.equals(TIMER)) {
      try (var source = new Registry(new NoopTimer(meterIdentity))) {
        assertThrows(expected, () -> timer.scrapeApprovedTimers(source));
      }
    } else {
      try (var source = new Registry(new NoopGauge(meterIdentity))) {
        assertThrows(expected, () -> gauge.scrapeApprovedGauges(source));
      }
    }
  }
}
