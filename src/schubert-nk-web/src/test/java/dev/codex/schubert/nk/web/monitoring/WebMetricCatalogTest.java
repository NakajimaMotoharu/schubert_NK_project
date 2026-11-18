package dev.codex.schubert.nk.web.monitoring;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import io.micrometer.core.instrument.Meter;
import io.micrometer.core.instrument.Tag;
import io.micrometer.core.instrument.Tags;
import io.prometheus.metrics.model.snapshots.Labels;
import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Test;

/** WEBCAT001..015/1763: expected domains are SS literals and an independent route fixture. */
class WebMetricCatalogTest {
  private static final String SERVICE_LABEL = "service";
  private static final String WEB_SERVICE_VALUE = "WEB";
  private static final String ROUTE_LABEL = "route";
  private static final String STATE_LABEL = "state";
  private static final String ACTIVE_POOL_STATE = "active";
  private static final String STORE_LABEL = "store";
  private static final String STATUS_LABEL = "status";
  private static final String MEDIA_TYPE_LABEL = "media_type";
  private static final String AUDIO_TYPE_NAME = "AUDIO";
  private static final String HTTP = "nk_http_requests_total";
  private static final String TIMER = "nk_http_request_duration_seconds";
  private static final String POOL = "nk_db_pool_connections";
  private static final String ROWS = "nk_outbox_rows";
  private static final String AGE = "nk_outbox_oldest_seconds";
  private static final String STREAMS = "nk_media_streams";
  private static final String BYTES = "nk_media_bytes_total";
  private static final Map<String, Map<String, String>> FIXED =
      Map.of(
          HTTP,
              Map.of(
                  SERVICE_LABEL,
                  WEB_SERVICE_VALUE,
                  ROUTE_LABEL,
                  "/login",
                  "method",
                  "GET",
                  "status_class",
                  "2xx"),
          TIMER, Map.of(SERVICE_LABEL, WEB_SERVICE_VALUE, ROUTE_LABEL, "/login"),
          POOL, Map.of(SERVICE_LABEL, WEB_SERVICE_VALUE, STATE_LABEL, ACTIVE_POOL_STATE),
          ROWS, Map.of(STORE_LABEL, WEB_SERVICE_VALUE, STATUS_LABEL, "PENDING"),
          AGE, Map.of(STORE_LABEL, WEB_SERVICE_VALUE, STATUS_LABEL, "PENDING"),
          STREAMS, Map.of(MEDIA_TYPE_LABEL, AUDIO_TYPE_NAME),
          BYTES, Map.of(MEDIA_TYPE_LABEL, AUDIO_TYPE_NAME, "mode", "INLINE", STATUS_LABEL, "200"));
  private final WebMetricCatalog catalog = new WebMetricCatalog();

  private static Meter.Id raw(String name, List<Tag> tags) {
    return new Meter.Id("safe_fixture", Tags.empty(), "", "", Meter.Type.GAUGE) {
      public String getName() {
        return name;
      }

      public List<Tag> getTags() {
        return tags;
      }
    };
  }

  private static Meter.Id identity(String name, Map<String, String> values) {
    return raw(
        name, values.entrySet().stream().map(e -> Tag.of(e.getKey(), e.getValue())).toList());
  }

  private static void labels(Map<String, String> expected, Labels actual) {
    assertEquals(expected.size(), actual.size());
    expected.forEach((key, value) -> assertEquals(value, actual.get(key)));
  }

  private static List<String> routes() throws Exception {
    try (var stream =
        WebMetricCatalogTest.class.getResourceAsStream("/monitoring/http-route-labels.txt")) {
      assertNotNull(stream);
      try (var reader = new BufferedReader(new InputStreamReader(stream, StandardCharsets.UTF_8))) {
        var result = reader.lines().toList();
        assertEquals(35, result.size());
        assertEquals(35, Set.copyOf(result).size());
        return result;
      }
    }
  }

  private static final class MutableTag implements Tag {
    String key;
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

  @Test
  void webcat001ExactSevenNamesTypesAndKeys() {
    assertEquals(
        Map.of(
            POOL,
            Set.of(SERVICE_LABEL, STATE_LABEL),
            ROWS,
            Set.of(STORE_LABEL, STATUS_LABEL),
            AGE,
            Set.of(STORE_LABEL, STATUS_LABEL),
            STREAMS,
            Set.of(MEDIA_TYPE_LABEL)),
        catalog.gauges());
    assertEquals(
        Map.of(
            HTTP,
            Set.of(SERVICE_LABEL, ROUTE_LABEL, "method", "status_class"),
            BYTES,
            Set.of(MEDIA_TYPE_LABEL, "mode", STATUS_LABEL)),
        catalog.counters());
    assertEquals(Map.of(TIMER, Set.of(SERVICE_LABEL, ROUTE_LABEL)), catalog.timers());
  }

  @Test
  void webcat002All1750IndependentHttpCounterTuples() throws Exception {
    int count = 0;
    for (String route : routes())
      for (String method :
          List.of(
              "GET", "HEAD", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "TRACE", "CONNECT",
              "OTHER"))
        for (String status : List.of("1xx", "2xx", "3xx", "4xx", "5xx")) {
          var expected =
              Map.of(
                  SERVICE_LABEL,
                  WEB_SERVICE_VALUE,
                  ROUTE_LABEL,
                  route,
                  "method",
                  method,
                  "status_class",
                  status);
          labels(expected, catalog.labels(identity(HTTP, expected)));
          count++;
        }
    assertEquals(1750, count);
  }

  @Test
  void webcat003All35IndependentTimerRoutes() throws Exception {
    for (String route : routes()) {
      var expected = Map.of(SERVICE_LABEL, WEB_SERVICE_VALUE, ROUTE_LABEL, route);
      labels(expected, catalog.labels(identity(TIMER, expected)));
    }
  }

  @Test
  void webcat004AllThirteenGaugeLabelTuples() {
    int count = 0;
    for (String state : List.of(ACTIVE_POOL_STATE, "idle", "pending", "max")) {
      var expected = Map.of(SERVICE_LABEL, WEB_SERVICE_VALUE, STATE_LABEL, state);
      labels(expected, catalog.labels(identity(POOL, expected)));
      count++;
    }
    for (String name : List.of(ROWS, AGE))
      for (String status : List.of("PENDING", "SENT", "ERROR")) {
        var expected = Map.of(STORE_LABEL, WEB_SERVICE_VALUE, STATUS_LABEL, status);
        labels(expected, catalog.labels(identity(name, expected)));
        count++;
      }
    for (String type : List.of(AUDIO_TYPE_NAME, "VIDEO", "MUSIC")) {
      var expected = Map.of(MEDIA_TYPE_LABEL, type);
      labels(expected, catalog.labels(identity(STREAMS, expected)));
      count++;
    }
    assertEquals(13, count);
  }

  @Test
  void webcat005All36MediaByteTuples() {
    int count = 0;
    for (String type : List.of(AUDIO_TYPE_NAME, "VIDEO", "MUSIC"))
      for (String mode : List.of("INLINE", "DOWNLOAD", "RANGE"))
        for (String status : List.of("200", "206", "416", "503")) {
          var expected = Map.of(MEDIA_TYPE_LABEL, type, "mode", mode, STATUS_LABEL, status);
          labels(expected, catalog.labels(identity(BYTES, expected)));
          count++;
        }
    assertEquals(36, count);
  }

  @Test
  void webcat006UnknownNamesUseOnlyFixedDiagnostic() {
    for (String name :
        List.of(
            "nk_unknown_fixture_id", "nk_mq_messages_total", "", "nk_db_pool_connections_extra")) {
      var failure =
          assertThrows(
              IllegalArgumentException.class, () -> catalog.labels(identity(name, Map.of())));
      assertEquals("unknown Web metric", failure.getMessage());
    }
  }

  @Test
  void webcat007EveryFieldRejectsUnknownValueAndRawRoute() {
    FIXED.forEach(
        (name, values) ->
            values.forEach(
                (key, unused) -> {
                  var invalid = new HashMap<>(values);
                  invalid.put(key, "INVALID_FIXTURE_VALUE");
                  var failure =
                      assertThrows(
                          IllegalArgumentException.class,
                          () -> catalog.labels(identity(name, invalid)));
                  assertEquals("invalid Web metric label", failure.getMessage());
                }));
    var invalid = new HashMap<>(FIXED.get(HTTP));
    invalid.put(ROUTE_LABEL, "/scenarios/123");
    assertThrows(IllegalArgumentException.class, () -> catalog.labels(identity(HTTP, invalid)));
  }

  @Test
  void webcat008EveryFamilyRejectsMissingAndExtraKeys() {
    FIXED.forEach(
        (name, values) -> {
          values.forEach(
              (key, unused) -> {
                var missing = new HashMap<>(values);
                missing.remove(key);
                assertThrows(
                    IllegalArgumentException.class, () -> catalog.labels(identity(name, missing)));
              });
          var extra = new HashMap<>(values);
          extra.put("actor", "UNAPPROVED_FIXTURE");
          assertThrows(IllegalArgumentException.class, () -> catalog.labels(identity(name, extra)));
        });
  }

  @Test
  void webcat009ActualDuplicateIdentityIsRejected() {
    var duplicateTags =
        List.of(
            Tag.of(SERVICE_LABEL, WEB_SERVICE_VALUE),
            Tag.of(SERVICE_LABEL, WEB_SERVICE_VALUE),
            Tag.of(STATE_LABEL, ACTIVE_POOL_STATE));
    var duplicateIdentity = raw(POOL, duplicateTags);
    assertSame(duplicateTags, duplicateIdentity.getTags());
    assertEquals(
        List.of(SERVICE_LABEL, SERVICE_LABEL, STATE_LABEL),
        duplicateIdentity.getTags().stream().map(Tag::getKey).toList());
    assertThrows(IllegalArgumentException.class, () -> catalog.labels(duplicateIdentity));
  }

  @Test
  void webcat010NullContractsFailWithoutNormalizingUnknown() {
    assertThrows(NullPointerException.class, () -> catalog.labels(null));
    assertThrows(NullPointerException.class, () -> catalog.labels(raw(null, List.of())));
    assertThrows(NullPointerException.class, () -> catalog.labels(raw(POOL, null)));
    var tags = new ArrayList<Tag>();
    tags.add(null);
    assertThrows(NullPointerException.class, () -> catalog.labels(raw(POOL, tags)));
    assertThrows(
        NullPointerException.class,
        () -> catalog.labels(raw(POOL, List.of(new MutableTag(null, WEB_SERVICE_VALUE)))));
    assertThrows(
        NullPointerException.class,
        () -> catalog.labels(raw(POOL, List.of(new MutableTag(SERVICE_LABEL, null)))));
  }

  @Test
  void webcat011CopyDetachedFromMutableProvider() {
    var mutable = new MutableTag(SERVICE_LABEL, WEB_SERVICE_VALUE);
    var tags = new ArrayList<Tag>();
    tags.add(mutable);
    tags.add(Tag.of(STATE_LABEL, ACTIVE_POOL_STATE));
    Labels result = catalog.labels(raw(POOL, tags));
    mutable.key = "actor";
    mutable.value = "INVALID_FIXTURE";
    tags.clear();
    labels(Map.of(SERVICE_LABEL, WEB_SERVICE_VALUE, STATE_LABEL, ACTIVE_POOL_STATE), result);
  }

  @Test
  void webcat012NamespacesAreDeepImmutableAndIndependent() {
    for (var space : List.of(catalog.gauges(), catalog.counters(), catalog.timers())) {
      assertThrows(UnsupportedOperationException.class, () -> space.put("nk_unknown", Set.of()));
      for (var keys : space.values())
        assertThrows(UnsupportedOperationException.class, () -> keys.add("actor"));
    }
    assertEquals(4, catalog.gauges().size());
    assertEquals(2, catalog.counters().size());
    assertEquals(1, catalog.timers().size());
    labels(FIXED.get(POOL), catalog.labels(identity(POOL, FIXED.get(POOL))));
  }

  @Test
  void webcat013ProviderFailuresKeepIdentity() {
    var failure = new IllegalStateException("fixture");
    var provider =
        new Meter.Id(POOL, Tags.empty(), "", "", Meter.Type.GAUGE) {
          public List<Tag> getTags() {
            throw failure;
          }
        };
    assertSame(failure, assertThrows(IllegalStateException.class, () -> catalog.labels(provider)));
    var fatal = new AssertionError("fixture");
    var fatalProvider =
        new Meter.Id(POOL, Tags.empty(), "", "", Meter.Type.GAUGE) {
          public List<Tag> getTags() {
            throw fatal;
          }
        };
    assertSame(fatal, assertThrows(AssertionError.class, () -> catalog.labels(fatalProvider)));
  }

  @Test
  void webcat014FiniteConcurrentCallsHaveNoRetainedMutableState() throws Exception {
    var workers = Executors.newFixedThreadPool(4);
    try {
      var jobs = new ArrayList<Future<?>>();
      for (int index = 0; index < 64; index++)
        jobs.add(
            workers.submit(
                () -> {
                  FIXED.forEach(
                      (name, expected) ->
                          labels(expected, catalog.labels(identity(name, expected))));
                  assertEquals(4, catalog.gauges().size());
                  assertEquals(2, catalog.counters().size());
                  assertEquals(1, catalog.timers().size());
                }));
      for (var job : jobs) job.get(10, TimeUnit.SECONDS);
    } finally {
      workers.shutdownNow();
      assertTrue(workers.awaitTermination(10, TimeUnit.SECONDS));
    }
  }

  @Test
  void webcat015CapturedNameUsesTheSameClosedDetachedLabelContract() {
    FIXED.forEach(
        (name, expected) -> {
          List<Tag> input =
              expected.entrySet().stream().map(e -> Tag.of(e.getKey(), e.getValue())).toList();
          labels(expected, catalog.labels(name, input));
        });

    var mutable = new MutableTag(STATE_LABEL, ACTIVE_POOL_STATE);
    var input = new ArrayList<Tag>();
    input.add(mutable);
    input.add(Tag.of(SERVICE_LABEL, WEB_SERVICE_VALUE));
    Labels checked = catalog.labels(POOL, input);
    mutable.key = "unexpected-captured-label";
    mutable.value = "INVALID_CAPTURED_STATE";
    input.clear();
    labels(Map.of(SERVICE_LABEL, WEB_SERVICE_VALUE, STATE_LABEL, ACTIVE_POOL_STATE), checked);

    var missing =
        assertThrows(
            IllegalArgumentException.class,
            () -> catalog.labels(POOL, List.of(Tag.of(STATE_LABEL, ACTIVE_POOL_STATE))));
    assertEquals("missing Web metric label", missing.getMessage());
    var unknown =
        assertThrows(
            IllegalArgumentException.class,
            () -> catalog.labels("nk_unregistered_fixture_name", List.of()));
    assertEquals("unknown Web metric", unknown.getMessage());
    assertThrows(NullPointerException.class, () -> catalog.labels(POOL, null));
  }
}
