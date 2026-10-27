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
import io.micrometer.core.instrument.noop.NoopCounter;
import io.micrometer.core.instrument.noop.NoopGauge;
import io.micrometer.core.instrument.simple.SimpleConfig;
import io.micrometer.core.instrument.simple.SimpleMeterRegistry;
import java.lang.ref.Reference;
import java.time.Duration;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicReference;
import org.junit.jupiter.api.Test;

/** SCRAPE001..014/1769: literal SS catalog, pure mode control and borrowed owner invariants. */
class WebMetricScrapeTest {
  private static final String SERVICE_LABEL = "service";
  private static final String WEB_SERVICE = "WEB";
  private static final String DEBUG_MODE = "DEBUG";
  private static final String GAUGE_TYPE = "gauge";
  private static final String STATE_LABEL = "state";
  private static final String ACTIVE_POOL_STATE = "active";
  private static final String STANDARD_MODE = "STANDARD";
  private static final String HTTP = "nk_http_requests_total";
  private static final String TIMER = "nk_http_request_duration_seconds";
  private static final String POOL = "nk_db_pool_connections";
  private static final String BYTES = "nk_media_bytes_total";
  private static final Map<String, String> HTTP_LABELS =
      Map.of(SERVICE_LABEL, WEB_SERVICE, "route", "/login", "method", "GET", "status_class", "2xx");
  private final WebMetricScrape policy = new WebMetricScrape();

  private static class Registry extends SimpleMeterRegistry implements AutoCloseable {
    final List<Meter> supplied;
    final AtomicInteger reads = new AtomicInteger();

    Registry(Meter... meters) {
      super(SimpleConfig.DEFAULT, new MockClock());
      supplied = List.of(meters);
    }

    public List<Meter> getMeters() {
      reads.incrementAndGet();
      return supplied;
    }

    public boolean isClosed() {
      reads.incrementAndGet();
      return super.isClosed();
    }
  }

  private static final class Compatible extends Registry implements OverflowSafeDurationSupport {
    Compatible(Meter... meters) {
      super(meters);
    }
  }

  private static final class Bundle implements AutoCloseable {
    final OverflowSafeHttpMeterRegistry registry =
        new OverflowSafeHttpMeterRegistry(new MockClock());
    final WebDbPoolMetricRecorder pool = new WebDbPoolMetricRecorder(registry, DEBUG_MODE);
    final WebOutboxMetricRecorder outbox = new WebOutboxMetricRecorder(registry, DEBUG_MODE);
    final MediaStreamsMetricRecorder streams = new MediaStreamsMetricRecorder(registry, DEBUG_MODE);
    final HttpMetricRecorder http = new HttpMetricRecorder(registry, DEBUG_MODE);
    final MediaBytesMetricRecorder bytes = new MediaBytesMetricRecorder(registry, DEBUG_MODE);

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

    String text(WebMetricScrape target, String mode) {
      try {
        return target.scrape(registry, mode);
      } finally {
        Reference.reachabilityFence(this);
      }
    }

    public void close() {
      registry.close();
    }
  }

  private static Meter.Id identity(String name, Tags tags, Meter.Type type) {
    return new Meter.Id(name, tags, "", "", type);
  }

  private static void catalog(String text) {
    var expected =
        Map.of(
            HTTP,
            "counter",
            TIMER,
            "histogram",
            POOL,
            GAUGE_TYPE,
            "nk_outbox_rows",
            GAUGE_TYPE,
            "nk_outbox_oldest_seconds",
            GAUGE_TYPE,
            "nk_media_streams",
            GAUGE_TYPE,
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
    String row = rows.getFirst();
    return Double.parseDouble(row.substring(row.lastIndexOf(' ') + 1));
  }

  private static void supplied(String text) {
    catalog(text);
    assertEquals(1, value(text, HTTP, HTTP_LABELS));
    assertEquals(
        3, value(text, POOL, Map.of(SERVICE_LABEL, WEB_SERVICE, STATE_LABEL, ACTIVE_POOL_STATE)));
    assertEquals(
        1.0E-9, value(text, TIMER + "_sum", Map.of(SERVICE_LABEL, WEB_SERVICE, "route", "/login")));
    assertEquals(
        7, value(text, BYTES, Map.of("media_type", "AUDIO", "mode", "INLINE", "status", "200")));
  }

  @Test
  void scrape001StandardNeverReadsDetailedSourceOrProvider() {
    var values = new AtomicInteger();
    var meter =
        new NoopGauge(
            identity(
                POOL,
                Tags.of(SERVICE_LABEL, "UNAPPROVED", STATE_LABEL, ACTIVE_POOL_STATE),
                Meter.Type.GAUGE)) {
          public double value() {
            values.incrementAndGet();
            throw new AssertionError("no detailed provider");
          }
        };
    try (var source = new Registry(meter)) {
      source.reads.set(0);
      assertEquals("", policy.scrape(source, STANDARD_MODE));
      assertEquals(0, source.reads.get());
      assertEquals(0, values.get());
      assertFalse(source.isClosed());
    }
  }

  @Test
  void scrape002DebugRealInitialRegistryHasOnlySevenFamilies() {
    try (var b = new Bundle()) {
      String result = b.text(policy, DEBUG_MODE);
      catalog(result);
      assertEquals(13, result.lines().filter(line -> line.endsWith("} NaN")).count());
      assertEquals(0, value(result, HTTP, HTTP_LABELS));
      assertEquals(
          0,
          value(result, BYTES, Map.of("media_type", "AUDIO", "mode", "INLINE", "status", "200")));
    }
  }

  @Test
  void scrape003SuppliedRealRegistryUsesIndependentLiteralValues() {
    try (var b = new Bundle()) {
      b.supplied();
      supplied(b.text(policy, DEBUG_MODE));
      assertFalse(b.registry.isClosed());
    }
  }

  @Test
  void scrape004PureModeCallsDoNotResetOrCloseSource() {
    try (var b = new Bundle()) {
      b.supplied();
      supplied(b.text(policy, DEBUG_MODE));
      assertEquals("", b.text(policy, STANDARD_MODE));
      assertFalse(b.registry.isClosed());
      supplied(b.text(policy, DEBUG_MODE));
    }
  }

  @Test
  void scrape005EmptyCompatibleRegistryIsEmptyNotAnUnknownObservation() {
    try (var source = new OverflowSafeHttpMeterRegistry(new MockClock())) {
      assertEquals("", policy.scrape(source, DEBUG_MODE));
      assertFalse(source.isClosed());
    }
  }

  @Test
  void scrape006DebugRejectsUnsupportedSourceBeforeAnyRead() {
    try (var source = new Registry()) {
      source.reads.set(0);
      var failure =
          assertThrows(IllegalArgumentException.class, () -> policy.scrape(source, DEBUG_MODE));
      assertEquals("CONFIG_INVALID", failure.getMessage());
      assertEquals(0, source.reads.get());
    }
  }

  @Test
  void scrape007NullAndInvalidModesFailWithoutProviderReads() {
    assertThrows(NullPointerException.class, () -> policy.scrape(null, STANDARD_MODE));
    try (var source = new Registry()) {
      source.reads.set(0);
      assertThrows(NullPointerException.class, () -> policy.scrape(source, null));
      for (String mode : List.of("", "debug", "DEBUG ", "UNKNOWN"))
        assertThrows(IllegalArgumentException.class, () -> policy.scrape(source, mode));
      assertEquals(0, source.reads.get());
    }
  }

  @Test
  void scrape008ClosedSourceIsNotReopenedOrReadInStandard() {
    var source = new Compatible();
    try {
      source.close();
      source.reads.set(0);
      assertEquals("", policy.scrape(source, STANDARD_MODE));
      assertEquals(0, source.reads.get());
      assertThrows(IllegalStateException.class, () -> policy.scrape(source, DEBUG_MODE));
    } finally {
      source.close();
    }
  }

  @Test
  void scrape009ProviderRuntimeAndErrorIdentityAreRetained() {
    var failure = new IllegalStateException("fixture");
    var bad =
        new Meter.Id(POOL, Tags.empty(), "", "", Meter.Type.GAUGE) {
          public List<Tag> getTags() {
            throw failure;
          }
        };
    try (var source = new Compatible(new NoopGauge(bad))) {
      assertSame(
          failure,
          assertThrows(IllegalStateException.class, () -> policy.scrape(source, DEBUG_MODE)));
      assertFalse(source.isClosed());
    }
    var fatal = new AssertionError("fixture");
    var broken =
        new Meter.Id(POOL, Tags.empty(), "", "", Meter.Type.GAUGE) {
          public List<Tag> getTags() {
            throw fatal;
          }
        };
    try (var source = new Compatible(new NoopGauge(broken))) {
      assertSame(
          fatal, assertThrows(AssertionError.class, () -> policy.scrape(source, DEBUG_MODE)));
      assertFalse(source.isClosed());
    }
  }

  @Test
  void scrape010LaterFailureDoesNotReturnEarlierFormattedText() {
    var firstReads = new AtomicInteger();
    var first =
        new NoopGauge(
            identity(
                POOL,
                Tags.of(SERVICE_LABEL, WEB_SERVICE, STATE_LABEL, ACTIVE_POOL_STATE),
                Meter.Type.GAUGE)) {
          public double value() {
            firstReads.incrementAndGet();
            return 3;
          }
        };
    var later =
        new NoopCounter(
            identity(
                HTTP,
                Tags.of(
                    SERVICE_LABEL,
                    WEB_SERVICE,
                    "route",
                    "/unapproved/123",
                    "method",
                    "GET",
                    "status_class",
                    "2xx"),
                Meter.Type.COUNTER));
    var returned = new AtomicReference<Optional<String>>(Optional.empty());
    try (var source = new Compatible(first, later)) {
      assertThrows(
          IllegalArgumentException.class,
          () -> returned.set(Optional.of(policy.scrape(source, DEBUG_MODE))));
      assertEquals(1, firstReads.get());
      assertTrue(returned.get().isEmpty());
      assertFalse(source.isClosed());
    }
  }

  @Test
  void scrape011UnknownMetricsNeverReadValues() {
    var values = new AtomicInteger();
    var unknown =
        new NoopGauge(
            identity("nk_unapproved_fixture", Tags.of("actor", "UNAPPROVED"), Meter.Type.GAUGE)) {
          public double value() {
            values.incrementAndGet();
            throw new AssertionError("unselected provider");
          }
        };
    try (var source = new Compatible(unknown)) {
      assertEquals("", policy.scrape(source, DEBUG_MODE));
      assertEquals(0, values.get());
    }
  }

  @Test
  void scrape012FiniteConcurrentScrapesRemainIndependent() throws Exception {
    try (var b = new Bundle();
        var workers = Executors.newFixedThreadPool(4)) {
      b.supplied();
      var jobs = new ArrayList<Future<?>>();
      for (int index = 0; index < 64; index++)
        jobs.add(workers.submit(() -> supplied(b.text(policy, DEBUG_MODE))));
      for (var job : jobs) job.get(10, TimeUnit.SECONDS);
      assertFalse(b.registry.isClosed());
    }
  }

  @Test
  void scrape013PoisonedApprovedLabelNeverFallsBackToGenericApi() {
    var bad =
        new NoopGauge(
            identity(
                POOL,
                Tags.of(SERVICE_LABEL, "API", STATE_LABEL, ACTIVE_POOL_STATE),
                Meter.Type.GAUGE));
    try (var source = new Compatible(bad)) {
      var failure =
          assertThrows(IllegalArgumentException.class, () -> policy.scrape(source, DEBUG_MODE));
      assertEquals("invalid Web metric label", failure.getMessage());
    }
  }

  @Test
  void scrape014SamePolicyDoesNotRetainPriorSourceOrPartialFailure() {
    var bad =
        new NoopGauge(
            identity(
                POOL,
                Tags.of(SERVICE_LABEL, "API", STATE_LABEL, ACTIVE_POOL_STATE),
                Meter.Type.GAUGE));
    try (var broken = new Compatible(bad);
        var valid = new Bundle()) {
      assertThrows(IllegalArgumentException.class, () -> policy.scrape(broken, DEBUG_MODE));
      valid.supplied();
      supplied(valid.text(policy, DEBUG_MODE));
      assertFalse(valid.registry.isClosed());
    }
  }
}
