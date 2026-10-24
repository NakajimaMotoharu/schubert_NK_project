package dev.codex.schubert.nk.web.monitoring;

import static org.junit.jupiter.api.Assertions.*;

import io.micrometer.core.instrument.MockClock;
import java.time.Duration;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Test;

/** HTTPCOUNT001..006/1759: actual ordinary in-memory Web producer, literal independent samples. */
class WebCounterExporterContractTest {
  private static final String NAME = "nk_http_requests_total";
  private static final Map<String, Set<String>> SPACE =
      Map.of(NAME, Set.of("service", "route", "method", "status_class"));
  private final WebCounterMetricExporter exporter = new WebCounterMetricExporter();

  private static double sample(String text, String route, String method, String status) {
    var rows =
        text.lines()
            .filter(line -> line.startsWith(NAME + "{"))
            .filter(
                line ->
                    line.contains("route=\"" + route + "\"")
                        && line.contains("method=\"" + method + "\"")
                        && line.contains("status_class=\"" + status + "\"")
                        && line.contains("service=\"WEB\""))
            .toList();
    assertEquals(1, rows.size());
    String line = rows.getFirst();
    return Double.parseDouble(line.substring(line.lastIndexOf(' ') + 1));
  }

  @Test
  void httpcount001ApprovedFiniteCatalogHas1750ZeroSeries() {
    try (var source = new OverflowSafeHttpMeterRegistry(new MockClock())) {
      new HttpMetricRecorder(source, "DEBUG");
      String result = exporter.scrapeCounters(source, SPACE);
      assertEquals(1, result.lines().filter(line -> line.startsWith("# TYPE")).count());
      assertEquals(1750, result.lines().filter(line -> !line.startsWith("#")).count());
      assertTrue(result.contains("# TYPE " + NAME + " counter\n"));
      assertFalse(result.contains("_total_total"));
      assertFalse(result.contains("_duration"));
      assertFalse(result.contains(".histogram"));
      assertFalse(result.contains("_created"));
      assertEquals(0, sample(result, "/login", "GET", "2xx"));
      assertEquals(
          0,
          result
              .lines()
              .filter(line -> !line.startsWith("#"))
              .mapToDouble(line -> Double.parseDouble(line.substring(line.lastIndexOf(' ') + 1)))
              .sum());
      assertFalse(source.isClosed());
    }
  }

  @Test
  void httpcount002IndependentRouteMethodStatusCounts() {
    try (var source = new OverflowSafeHttpMeterRegistry(new MockClock())) {
      var recorder = new HttpMetricRecorder(source, "DEBUG");
      recorder.record("/login", "GET", 200, 1);
      recorder.record("/login", "GET", 200, 1);
      recorder.record("/login", "POST", 404, 1);
      recorder.record("/login", "GET", 503, 1);
      String result = exporter.scrapeCounters(source, SPACE);
      assertEquals(2, sample(result, "/login", "GET", "2xx"));
      assertEquals(1, sample(result, "/login", "POST", "4xx"));
      assertEquals(1, sample(result, "/login", "GET", "5xx"));
      assertEquals(0, sample(result, "/login", "POST", "2xx"));
    }
  }

  @Test
  void httpcount003UnknownValuesStayInClosedCatalog() {
    try (var source = new OverflowSafeHttpMeterRegistry(new MockClock())) {
      new HttpMetricRecorder(source, "DEBUG").record("/not-approved-123", "UNAPPROVED", 503, 1);
      String result = exporter.scrapeCounters(source, SPACE);
      assertEquals(1, sample(result, "/**", "OTHER", "5xx"));
      assertFalse(result.contains("/not-approved-123"));
      assertFalse(result.contains("UNAPPROVED"));
    }
  }

  @Test
  void httpcount004TimeWindowCannotEraseCounter() {
    var clock = new MockClock();
    try (var source = new OverflowSafeHttpMeterRegistry(clock)) {
      new HttpMetricRecorder(source, "DEBUG").record("/login", "GET", 200, 1);
      clock.add(Duration.ofDays(1));
      assertEquals(1, sample(exporter.scrapeCounters(source, SPACE), "/login", "GET", "2xx"));
    }
  }

  @Test
  void httpcount005FiniteWorkersAndIndependentOwner() throws Exception {
    try (var source = new OverflowSafeHttpMeterRegistry(new MockClock());
        var other = new OverflowSafeHttpMeterRegistry(new MockClock());
        var standard = new OverflowSafeHttpMeterRegistry(new MockClock());
        var workers = Executors.newFixedThreadPool(4)) {
      var recorder = new HttpMetricRecorder(source, "DEBUG");
      new HttpMetricRecorder(other, "DEBUG");
      new HttpMetricRecorder(standard, "STANDARD");
      var jobs = new java.util.ArrayList<Future<?>>();
      for (int index = 0; index < 64; index++)
        jobs.add(workers.submit(() -> recorder.record("/login", "GET", 200, 1)));
      for (var job : jobs) job.get(10, TimeUnit.SECONDS);
      assertEquals(64, sample(exporter.scrapeCounters(source, SPACE), "/login", "GET", "2xx"));
      assertEquals(0, sample(exporter.scrapeCounters(other, SPACE), "/login", "GET", "2xx"));
      assertEquals("", exporter.scrapeCounters(standard, SPACE));
      assertFalse(source.isClosed());
      assertFalse(other.isClosed());
      assertFalse(standard.isClosed());
    }
  }

  @Test
  void httpcount006EveryIndependentMethodAndStatus() {
    String[] methods = {
      "GET", "HEAD", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "TRACE", "CONNECT", "OTHER"
    };
    String[] statuses = {"1xx", "2xx", "3xx", "4xx", "5xx"};
    try (var source = new OverflowSafeHttpMeterRegistry(new MockClock())) {
      var recorder = new HttpMetricRecorder(source, "DEBUG");
      for (String method : methods)
        for (int status : new int[] {100, 200, 300, 400, 500})
          recorder.record("/login", method, status, 1);
      String result = exporter.scrapeCounters(source, SPACE);
      for (String method : methods)
        for (String status : statuses) assertEquals(1, sample(result, "/login", method, status));
      assertEquals(0, sample(result, "/**", "OTHER", "5xx"));
      assertEquals(
          50,
          result
              .lines()
              .filter(line -> !line.startsWith("#"))
              .mapToDouble(line -> Double.parseDouble(line.substring(line.lastIndexOf(' ') + 1)))
              .sum());
    }
  }
}
