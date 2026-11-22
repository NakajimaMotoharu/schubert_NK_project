package dev.codex.schubert.nk.web.monitoring;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.web.monitoring.HttpMetricContract.Labels;
import dev.codex.schubert.nk.web.monitoring.HttpMetricContract.Method;
import dev.codex.schubert.nk.web.monitoring.HttpMetricContract.Metric;
import dev.codex.schubert.nk.web.monitoring.HttpMetricContract.Route;
import dev.codex.schubert.nk.web.monitoring.HttpMetricContract.Status;
import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.time.Duration;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import java.util.concurrent.Callable;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Test;

/** SS351 literal metadata and independent35 route fixture, not a real provider. Spec1570. */
class HttpMetricContractTest {
  private static final String SERVICE_LABEL = "service";
  private static final String WEB_SERVICE_VALUE = "WEB";
  private static final String ROUTE_LABEL = "route";
  private static final String METHOD_LABEL = "method";
  private static final String STATUS_CLASS_LABEL = "status_class";
  private static final String HTTP_GET_VALUE = "GET";
  private final HttpMetricContract contract = new HttpMetricContract();
  private static final Map<String, String> UNKNOWN =
      Map.of(
          SERVICE_LABEL,
          WEB_SERVICE_VALUE,
          ROUTE_LABEL,
          "/**",
          METHOD_LABEL,
          "OTHER",
          STATUS_CLASS_LABEL,
          "2xx");

  private static List<String> routes() throws IOException {
    try (var reader =
        new BufferedReader(
            new InputStreamReader(
                Objects.requireNonNull(
                    HttpMetricContractTest.class.getResourceAsStream(
                        "/monitoring/http-route-labels.txt")),
                StandardCharsets.UTF_8))) {
      return reader.lines().toList();
    }
  }

  @Test
  void httpMetric001ApprovedCatalogModesAndBuckets() {
    assertEquals("nk_http_requests_total", Metric.REQUESTS.externalName());
    assertEquals("counter", Metric.REQUESTS.type());
    assertEquals(
        Set.of(SERVICE_LABEL, ROUTE_LABEL, METHOD_LABEL, STATUS_CLASS_LABEL),
        Metric.REQUESTS.labelNames());
    assertEquals("nk_http_request_duration_seconds", Metric.DURATION.externalName());
    assertEquals("histogram", Metric.DURATION.type());
    assertEquals(Set.of(SERVICE_LABEL, ROUTE_LABEL), Metric.DURATION.labelNames());
    assertEquals(Metric.REQUESTS, Metric.parse("nk_http_requests_total"));
    assertEquals(Metric.DURATION, Metric.parse("nk_http_request_duration_seconds"));
    assertFalse(contract.detailedMetricsEnabled("STANDARD"));
    assertTrue(contract.detailedMetricsEnabled("DEBUG"));
    assertEquals(
        List.of(
            Duration.ofMillis(50),
            Duration.ofMillis(100),
            Duration.ofMillis(250),
            Duration.ofMillis(500),
            Duration.ofMillis(1000),
            Duration.ofMillis(1500),
            Duration.ofMillis(2000),
            Duration.ofMillis(2500),
            Duration.ofMillis(5000)),
        contract.durationBuckets());
    assertEquals(1750, contract.requestCardinalityBound());
    assertEquals(35, contract.durationCardinalityBound());
  }

  @Test
  void httpMetric002IndependentWholeFiniteLabelMatrix() throws IOException {
    var routes = routes();
    assertEquals(35, routes.size());
    assertEquals(routes, contract.routeTemplates());
    String[] methods = {
      HTTP_GET_VALUE,
      "HEAD",
      "POST",
      "PUT",
      "PATCH",
      "DELETE",
      "OPTIONS",
      "TRACE",
      "CONNECT",
      "OTHER"
    };
    int[] statuses = {101, 201, 301, 401, 501};
    String[] classes = {"1xx", "2xx", "3xx", "4xx", "5xx"};
    var requestKeys = new HashSet<Map<String, String>>();
    var durationKeys = new HashSet<Map<String, String>>();
    for (String route : routes)
      for (String method : methods)
        for (int index = 0; index < 5; index++) {
          var labels = contract.labels(route, method, statuses[index]);
          assertEquals(route, labels.route().template());
          assertEquals(method, labels.method().name());
          assertEquals(classes[index], labels.status().label());
          assertEquals(
              Map.of(
                  SERVICE_LABEL,
                  WEB_SERVICE_VALUE,
                  ROUTE_LABEL,
                  route,
                  METHOD_LABEL,
                  method,
                  STATUS_CLASS_LABEL,
                  classes[index]),
              labels.requestLabels());
          assertEquals(
              Map.of(SERVICE_LABEL, WEB_SERVICE_VALUE, ROUTE_LABEL, route),
              labels.durationLabels());
          requestKeys.add(labels.requestLabels());
          durationKeys.add(labels.durationLabels());
        }
    assertEquals(1750, requestKeys.size());
    assertEquals(35, durationKeys.size());
  }

  @Test
  void httpMetric003UnknownUserValuesCannotGrowLabelSpace() {
    var keys = new HashSet<Map<String, String>>();
    var durations = new HashSet<Map<String, String>>();
    for (int index = 0; index < 10_000; index++) {
      var labels =
          contract.labels(
              "/questions/accepted/PT_FIXTURE_ONLY_" + index + "?actor=fixture",
              "X-FIXTURE-" + index,
              200);
      assertEquals(UNKNOWN, labels.requestLabels());
      keys.add(labels.requestLabels());
      durations.add(labels.durationLabels());
    }
    assertEquals(1, keys.size());
    assertEquals(1, durations.size());
    for (String raw :
        List.of(
            "/search?context=fixture",
            "/home/fixture/file",
            "\r\n\tfixture",
            "fixture-user",
            "/notifications/12345")) {
      assertEquals(UNKNOWN, contract.labels(raw, raw, 200).requestLabels());
      assertFalse(contract.labels(raw, raw, 200).requestLabels().containsValue(raw));
    }
    assertEquals(Method.OTHER, Method.parse("get"));
  }

  @Test
  void httpMetric004NullUnknownAndStatusBoundariesAreExplicit() {
    assertThrows(NullPointerException.class, () -> Metric.parse(null));
    assertEquals(
        "unknown HTTP metric",
        assertThrows(IllegalArgumentException.class, () -> Metric.parse("opaque\r\nfixture"))
            .getMessage());
    assertThrows(NullPointerException.class, () -> contract.detailedMetricsEnabled(null));
    for (String mode : List.of("debug", "STANDARD ", "", "opaque\r\nfixture"))
      assertEquals(
          "invalid monitoring mode",
          assertThrows(IllegalArgumentException.class, () -> contract.detailedMetricsEnabled(mode))
              .getMessage());
    assertThrows(NullPointerException.class, () -> Route.parse(null));
    assertThrows(NullPointerException.class, () -> Method.parse(null));
    assertThrows(NullPointerException.class, () -> contract.labels(null, HTTP_GET_VALUE, 200));
    assertThrows(NullPointerException.class, () -> contract.labels("/", null, 200));
    assertThrows(NullPointerException.class, () -> new Labels(null, Method.GET, Status.SUCCESS));
    assertThrows(NullPointerException.class, () -> new Labels(Route.ROOT, null, Status.SUCCESS));
    assertThrows(NullPointerException.class, () -> new Labels(Route.ROOT, Method.GET, null));
    for (int status : new int[] {-1, 99, 600, Integer.MAX_VALUE})
      assertEquals(
          "invalid HTTP status",
          assertThrows(
                  IllegalArgumentException.class,
                  () -> contract.labels("/", HTTP_GET_VALUE, status))
              .getMessage());
    assertEquals(Status.INFORMATIONAL, contract.labels("/", HTTP_GET_VALUE, 100).status());
    assertEquals(Status.SERVER_ERROR, contract.labels("/", HTTP_GET_VALUE, 599).status());
  }

  @Test
  void httpMetric005AllReturnedCollectionsAreImmutable() {
    var labels = contract.labels("/login", "POST", 302);
    assertThrows(UnsupportedOperationException.class, () -> labels.requestLabels().clear());
    assertThrows(UnsupportedOperationException.class, () -> labels.durationLabels().clear());
    for (var metric : Metric.values())
      assertThrows(UnsupportedOperationException.class, () -> metric.labelNames().clear());
    assertThrows(
        UnsupportedOperationException.class, () -> contract.durationBuckets().add(Duration.ZERO));
    assertThrows(
        UnsupportedOperationException.class, () -> contract.routeTemplates().set(0, "opaque"));
    assertEquals(
        Map.of(
            SERVICE_LABEL,
            WEB_SERVICE_VALUE,
            ROUTE_LABEL,
            "/login",
            METHOD_LABEL,
            "POST",
            STATUS_CLASS_LABEL,
            "3xx"),
        labels.requestLabels());
    assertEquals(35, contract.routeTemplates().size());
  }

  @Test
  void httpMetric006ConcurrentClassifiersAreStateless()
      throws InterruptedException, ExecutionException {
    var executor = Executors.newFixedThreadPool(4);
    try {
      var tasks = new ArrayList<Callable<Map<String, String>>>();
      for (int index = 0; index < 64; index++) {
        String raw = "/fixture/" + index;
        tasks.add(() -> contract.labels(raw, raw, 204).requestLabels());
      }
      for (var future : executor.invokeAll(tasks, 10, TimeUnit.SECONDS))
        assertEquals(UNKNOWN, future.get());
    } finally {
      executor.shutdownNow();
      assertTrue(executor.awaitTermination(10, TimeUnit.SECONDS));
    }
  }
}
