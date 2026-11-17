package dev.codex.schubert.nk.web.monitoring;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotSame;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.web.monitoring.HttpMetricContract.Labels;
import dev.codex.schubert.nk.web.monitoring.HttpMetricContract.Method;
import dev.codex.schubert.nk.web.monitoring.HttpMetricContract.Metric;
import dev.codex.schubert.nk.web.monitoring.HttpMetricContract.Route;
import dev.codex.schubert.nk.web.monitoring.HttpMetricContract.Status;
import io.micrometer.core.instrument.simple.SimpleMeterRegistry;
import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.time.Duration;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import java.util.function.Function;
import java.util.function.Supplier;
import org.junit.jupiter.api.Test;

/** RD171 MON005..013/UI252/SS313/351: fixed values, no exporter or real DB observation. */
class WebMonitoringValueContractTest {
  private static final String SERVICE_LABEL = "service";
  private static final String ROUTE_LABEL = "route";
  private static final String INDEX_VALUE = "fixed";

  @Test
  void metricsExposeOnlyTheTwoApprovedNamesTypesAndLabelSets() {
    dictionary(new String[] {"REQUESTS", "DURATION"}, Metric::values, Metric::valueOf);
    assertEquals("nk_http_requests_total", Metric.REQUESTS.externalName());
    assertEquals("counter", Metric.REQUESTS.type());
    assertEquals(
        Set.of(SERVICE_LABEL, ROUTE_LABEL, "method", "status_class"), Metric.REQUESTS.labelNames());
    assertEquals("nk_http_request_duration_seconds", Metric.DURATION.externalName());
    assertEquals("histogram", Metric.DURATION.type());
    assertEquals(Set.of(SERVICE_LABEL, ROUTE_LABEL), Metric.DURATION.labelNames());
    assertSame(Metric.REQUESTS, Metric.parse("nk_http_requests_total"));
    assertSame(Metric.DURATION, Metric.parse("nk_http_request_duration_seconds"));
    assertThrows(IllegalArgumentException.class, () -> Metric.parse(""));
    assertThrows(IllegalArgumentException.class, () -> Metric.parse("unknown"));
    assertThrows(NullPointerException.class, () -> Metric.parse(null));
    assertThrows(
        UnsupportedOperationException.class, () -> Metric.REQUESTS.labelNames().add("other"));
  }

  @Test
  void routesRetainTheIndependentSs313OrderAndNeverRetainRawPaths() throws Exception {
    dictionary(
        new String[] {
          "ROOT",
          "LOGIN",
          "LOGOUT",
          "SEARCH",
          "LOGS",
          "ERROR",
          "SCENARIOS",
          "SCENARIO_ID",
          "SCENARIO_GAME",
          "SCENARIO_PREFIX",
          "ANIMATION",
          "ANIMATION_MAIN",
          "ANIMATION_OVA",
          "ANIMATION_OPENING",
          "ANIMATION_VIDEO",
          "ANIMATION_MEDIA",
          "MUSIC",
          "MUSIC_CATEGORY",
          "MUSIC_SECTION",
          "MUSIC_MEDIA",
          "MUSIC_DOWNLOAD",
          "AUDIO",
          "AUDIO_DOWNLOAD",
          "ADMIN_USERS",
          "ADMIN_USER_NEW",
          "ADMIN_USER_ID",
          "QUESTIONS",
          "QUESTION_NEW",
          "QUESTION_ACCEPTED",
          "QUESTION_ID",
          "NOTIFICATIONS",
          "NOTIFICATION_ID",
          "STYLES",
          "SCRIPTS",
          "UNKNOWN"
        },
        Route::values,
        Route::valueOf);
    List<String> templates;
    try (var reader =
        new BufferedReader(
            new InputStreamReader(
                Objects.requireNonNull(
                    getClass().getResourceAsStream("/monitoring/http-route-labels.txt")),
                StandardCharsets.UTF_8))) {
      templates = reader.lines().toList();
    }
    assertEquals(35, templates.size());
    Route[] routes = Route.values();
    for (int i = 0; i < 35; i++) {
      assertEquals(templates.get(i), routes[i].template());
      assertSame(routes[i], Route.parse(templates.get(i)));
    }
    for (String raw : List.of("", "/scenarios/42", "/scenarios/42?q=public", "unknown"))
      assertSame(Route.UNKNOWN, Route.parse(raw));
    assertThrows(NullPointerException.class, () -> Route.parse(null));
  }

  @Test
  void methodsRetainTheirClosedDictionaryAndStrictUnknownFallback() {
    dictionary(
        new String[] {
          "GET", "HEAD", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "TRACE", "CONNECT", "OTHER"
        },
        Method::values,
        Method::valueOf);
    for (String method :
        List.of(
            "GET", "HEAD", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "TRACE", "CONNECT",
            "OTHER")) assertEquals(method, Method.parse(method).name());
    assertSame(Method.OTHER, Method.parse(""));
    assertSame(Method.OTHER, Method.parse("get"));
    assertSame(Method.OTHER, Method.parse("UNKNOWN"));
    assertThrows(NullPointerException.class, () -> Method.parse(null));
  }

  @Test
  void statusesCoverTheFiveClassesAndBothIntegerBoundaries() {
    dictionary(
        new String[] {"INFORMATIONAL", "SUCCESS", "REDIRECTION", "CLIENT_ERROR", "SERVER_ERROR"},
        Status::values,
        Status::valueOf);
    String[] labels = {"1xx", "2xx", "3xx", "4xx", "5xx"};
    for (int i = 0; i < 5; i++) {
      assertEquals(labels[i], Status.values()[i].label());
      assertSame(Status.values()[i], Status.from(100 + i * 100));
      assertSame(Status.values()[i], Status.from(199 + i * 100));
    }
    for (int value : new int[] {Integer.MIN_VALUE, 0, 99, 600, Integer.MAX_VALUE})
      assertThrows(IllegalArgumentException.class, () -> Status.from(value));
  }

  @Test
  void outboxStatusesRetainExactPersistedNamesOnly() {
    dictionary(
        new String[] {"PENDING", "SENT", "ERROR"},
        WebOutboxMetricRecorder.Status::values,
        WebOutboxMetricRecorder.Status::valueOf);
    for (String name : List.of("PENDING", "SENT", "ERROR"))
      assertEquals(name, WebOutboxMetricRecorder.Status.parse(name).name());
    assertThrows(IllegalArgumentException.class, () -> WebOutboxMetricRecorder.Status.parse(""));
    assertThrows(
        IllegalArgumentException.class, () -> WebOutboxMetricRecorder.Status.parse("pending"));
    assertThrows(NullPointerException.class, () -> WebOutboxMetricRecorder.Status.parse(null));
  }

  @Test
  void poolStatesRetainLowercaseLabelsAndCaseSensitiveParsing() {
    dictionary(
        new String[] {"ACTIVE", "IDLE", "PENDING", "MAX"},
        WebDbPoolMetricRecorder.State::values,
        WebDbPoolMetricRecorder.State::valueOf);
    String[] labels = {"active", "idle", "pending", "max"};
    for (int i = 0; i < 4; i++) {
      assertEquals(labels[i], WebDbPoolMetricRecorder.State.values()[i].label());
      assertSame(
          WebDbPoolMetricRecorder.State.values()[i], WebDbPoolMetricRecorder.state(labels[i]));
    }
    assertThrows(IllegalArgumentException.class, () -> WebDbPoolMetricRecorder.state(""));
    assertThrows(IllegalArgumentException.class, () -> WebDbPoolMetricRecorder.state("ACTIVE"));
    assertThrows(NullPointerException.class, () -> WebDbPoolMetricRecorder.state(null));
  }

  @Test
  void mediaModesRetainOnlyTheThreeDeliveryLabels() {
    dictionary(
        new String[] {"INLINE", "DOWNLOAD", "RANGE"},
        MediaBytesMetricRecorder.Mode::values,
        MediaBytesMetricRecorder.Mode::valueOf);
    for (String mode : List.of("INLINE", "DOWNLOAD", "RANGE"))
      assertEquals(mode, MediaBytesMetricRecorder.Mode.parse(mode).name());
    assertThrows(IllegalArgumentException.class, () -> MediaBytesMetricRecorder.Mode.parse(""));
    assertThrows(
        IllegalArgumentException.class, () -> MediaBytesMetricRecorder.Mode.parse("inline"));
    assertThrows(NullPointerException.class, () -> MediaBytesMetricRecorder.Mode.parse(null));
  }

  @Test
  void labelsHaveIndependentValueHashDisplayAndImmutableMapContracts() {
    Labels value = new Labels(Route.ROOT, Method.GET, Status.SUCCESS);
    Labels same = new Labels(Route.ROOT, Method.GET, Status.SUCCESS);
    assertEquals(Route.ROOT, value.route());
    assertEquals(Method.GET, value.method());
    assertEquals(Status.SUCCESS, value.status());
    assertEquals(value, value);
    assertEquals(value, same);
    assertFalse(value.equals(null));
    assertFalse(value.equals("not-labels"));
    for (Labels different :
        List.of(
            new Labels(Route.LOGIN, Method.GET, Status.SUCCESS),
            new Labels(Route.ROOT, Method.POST, Status.SUCCESS),
            new Labels(Route.ROOT, Method.GET, Status.CLIENT_ERROR)))
      assertFalse(value.equals(different));
    int expected =
        31 * (31 * System.identityHashCode(Route.ROOT) + System.identityHashCode(Method.GET))
            + System.identityHashCode(Status.SUCCESS);
    assertEquals(expected, value.hashCode());
    assertEquals("Labels[route=ROOT, method=GET, status=SUCCESS]", value.toString());
    assertEquals(
        Map.of(SERVICE_LABEL, "WEB", ROUTE_LABEL, "/", "method", "GET", "status_class", "2xx"),
        value.requestLabels());
    assertEquals(Map.of(SERVICE_LABEL, "WEB", ROUTE_LABEL, "/"), value.durationLabels());
    var index = new HashMap<Labels, String>();
    index.put(value, INDEX_VALUE);
    assertEquals(INDEX_VALUE, index.get(same));
  }

  @Test
  void outboxObservationRetainsAllSixValueComponentsAndTheFixedZeroAgeHash() {
    var value =
        new WebOutboxMetricRecorder.Observation(
            1, 2, 3, Duration.ZERO, Duration.ZERO, Duration.ZERO);
    var same =
        new WebOutboxMetricRecorder.Observation(
            1, 2, 3, Duration.ZERO, Duration.ZERO, Duration.ZERO);
    assertEquals(1, value.pending());
    assertEquals(2, value.sent());
    assertEquals(3, value.error());
    assertEquals(Duration.ZERO, value.pendingAge());
    assertEquals(Duration.ZERO, value.sentAge());
    assertEquals(Duration.ZERO, value.errorAge());
    assertEquals(value, value);
    assertEquals(value, same);
    assertFalse(value.equals(null));
    assertFalse(value.equals("not-observation"));
    for (var different :
        List.of(
            new WebOutboxMetricRecorder.Observation(
                2, 2, 3, Duration.ZERO, Duration.ZERO, Duration.ZERO),
            new WebOutboxMetricRecorder.Observation(
                1, 3, 3, Duration.ZERO, Duration.ZERO, Duration.ZERO),
            new WebOutboxMetricRecorder.Observation(
                1, 2, 4, Duration.ZERO, Duration.ZERO, Duration.ZERO),
            new WebOutboxMetricRecorder.Observation(
                1, 2, 3, Duration.ofSeconds(1), Duration.ZERO, Duration.ZERO),
            new WebOutboxMetricRecorder.Observation(
                1, 2, 3, Duration.ZERO, Duration.ofSeconds(1), Duration.ZERO),
            new WebOutboxMetricRecorder.Observation(
                1, 2, 3, Duration.ZERO, Duration.ZERO, Duration.ofSeconds(1))))
      assertFalse(value.equals(different));
    assertEquals(30_565_566, value.hashCode()); // independent polynomial, components 1,2,3,0,0,0
    assertEquals(
        "Observation[pending=1, sent=2, error=3, pendingAge=PT0S, sentAge=PT0S, errorAge=PT0S]",
        value.toString());
    var index = new HashMap<WebOutboxMetricRecorder.Observation, String>();
    index.put(value, INDEX_VALUE);
    assertEquals(INDEX_VALUE, index.get(same));
  }

  @Test
  void poolCountsRetainIndependentValuesAndFixedHash() {
    var value = new WebDbPoolMetricRecorder.Counts(1, 2, 3, 4);
    var same = new WebDbPoolMetricRecorder.Counts(1, 2, 3, 4);
    assertEquals(1, value.active());
    assertEquals(2, value.idle());
    assertEquals(3, value.pending());
    assertEquals(4, value.maximum());
    assertEquals(value, value);
    assertEquals(value, same);
    assertFalse(value.equals(null));
    assertFalse(value.equals("not-counts"));
    for (var different :
        List.of(
            new WebDbPoolMetricRecorder.Counts(2, 2, 3, 4),
            new WebDbPoolMetricRecorder.Counts(1, 3, 3, 4),
            new WebDbPoolMetricRecorder.Counts(1, 2, 4, 4),
            new WebDbPoolMetricRecorder.Counts(1, 2, 3, 5))) assertFalse(value.equals(different));
    assertEquals(31_810, value.hashCode());
    assertEquals("Counts[active=1, idle=2, pending=3, maximum=4]", value.toString());
    var index = new HashMap<WebDbPoolMetricRecorder.Counts, String>();
    index.put(value, INDEX_VALUE);
    assertEquals(INDEX_VALUE, index.get(same));
  }

  @Test
  void allThreeModeParsersRejectValidStringsThatCollideWithApprovedModeHashes() {
    assertEquals(2_095_255_229, "STANDARD".hashCode());
    assertEquals(2_095_255_229, "T5ANDARD".hashCode());
    assertEquals(64_921_139, "DEBUG".hashCode());
    assertEquals(64_921_139, "E&BUG".hashCode());
    var registry = new SimpleMeterRegistry();
    try {
      var contract = new HttpMetricContract();
      for (String invalid : List.of("T5ANDARD", "E&BUG")) {
        assertThrows(
            IllegalArgumentException.class, () -> contract.detailedMetricsEnabled(invalid));
        assertThrows(
            IllegalArgumentException.class, () -> new WebOutboxMetricRecorder(registry, invalid));
        assertThrows(
            IllegalArgumentException.class, () -> new WebDbPoolMetricRecorder(registry, invalid));
        assertThrows(
            IllegalArgumentException.class, () -> new MediaBytesMetricRecorder(registry, invalid));
        assertTrue(registry.getMeters().isEmpty(), "invalid config must not register meters");
      }
    } finally {
      registry.close();
    }
  }

  private static <E extends Enum<E>> void dictionary(
      String[] names, Supplier<E[]> values, Function<String, E> parse) {
    E[] first = values.get();
    assertArrayEquals(names, Arrays.stream(first).map(Enum::name).toArray(String[]::new));
    for (int i = 0; i < names.length; i++) {
      assertEquals(i, first[i].ordinal());
      assertSame(first[i], parse.apply(names[i]));
    }
    E[] second = values.get();
    E retained = first[0];
    assertNotSame(first, second);
    first[0] = null; // Caller-owned poison: neither another array nor future lookup may change.
    assertSame(retained, second[0]);
    assertSame(retained, values.get()[0]);
    assertThrows(IllegalArgumentException.class, () -> parse.apply("NOT_AN_APPROVED_VALUE"));
    assertThrows(IllegalArgumentException.class, () -> parse.apply(""));
    assertThrows(NullPointerException.class, () -> parse.apply(null));
  }
}
