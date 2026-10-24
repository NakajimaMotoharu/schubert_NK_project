package dev.codex.schubert.nk.web.monitoring;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.bootstrap.monitoring.PrometheusSummaryExporter;
import io.micrometer.core.instrument.MockClock;
import java.time.Duration;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Test;

/**
 * HTTPEXP001..006/1757: real supplied metric recorders, no HTTP request/Root/service or clock OS.
 */
class WebTimerExporterContractTest {
  private static final String NAME = "nk_http_request_duration_seconds";
  private static final Map<String, Set<String>> SPACE = Map.of(NAME, Set.of("service", "route"));
  private static final String[] BOUNDS = {
    "0.05", "0.1", "0.25", "0.5", "1.0", "1.5", "2.0", "2.5", "5.0", "+Inf"
  };
  private final PrometheusSummaryExporter exporter = new PrometheusSummaryExporter();

  private static double sample(String text, String suffix, String route, String bound) {
    var rows =
        text.lines()
            .filter(line -> line.startsWith(NAME + suffix + "{"))
            .filter(
                line ->
                    line.contains("route=\"" + route + "\"") && line.contains("service=\"WEB\""))
            .filter(line -> bound.isEmpty() || line.contains("le=\"" + bound + "\""))
            .toList();
    assertEquals(1, rows.size());
    String line = rows.getFirst();
    return Double.parseDouble(line.substring(line.lastIndexOf(' ') + 1));
  }

  @Test
  void httpexp001AllApprovedTimersAndNoInternalOrCounterFamilies() {
    try (var source = new OverflowSafeHttpMeterRegistry(new MockClock())) {
      new HttpMetricRecorder(source, "DEBUG");
      String result = exporter.scrapeTimers(source, SPACE);
      assertEquals(1, result.lines().filter(line -> line.startsWith("# TYPE")).count());
      assertEquals(420, result.lines().filter(line -> !line.startsWith("#")).count());
      assertEquals(35, result.lines().filter(line -> line.startsWith(NAME + "_count{")).count());
      assertTrue(result.contains("# TYPE " + NAME + " histogram\n"));
      assertFalse(result.contains("nk_http_requests_total"));
      assertFalse(result.contains(".histogram"));
      for (String bound : BOUNDS) assertEquals(0, sample(result, "_bucket", "/login", bound));
      assertEquals(0, sample(result, "_count", "/login", ""));
      assertEquals(0, sample(result, "_sum", "/login", ""));
      assertFalse(source.isClosed());
    }
  }

  @Test
  void httpexp002NanosecondAndEveryIndependentWireBoundary() {
    try (var source = new OverflowSafeHttpMeterRegistry(new MockClock())) {
      var recorder = new HttpMetricRecorder(source, "DEBUG");
      recorder.record("/login", "GET", 200, 1);
      String one = exporter.scrapeTimers(source, SPACE);
      assertEquals(.000000001, sample(one, "_sum", "/login", ""));
      for (String bound : BOUNDS) assertEquals(1, sample(one, "_bucket", "/login", bound));
    }
    try (var source = new OverflowSafeHttpMeterRegistry(new MockClock())) {
      var recorder = new HttpMetricRecorder(source, "DEBUG");
      for (long bound :
          new long[] {
            50_000_000,
            100_000_000,
            250_000_000,
            500_000_000,
            1_000_000_000,
            1_500_000_000,
            2_000_000_000,
            2_500_000_000L,
            5_000_000_000L
          })
        for (long value : new long[] {bound - 1, bound, bound + 1})
          recorder.record("/login", "GET", 200, value);
      String result = exporter.scrapeTimers(source, SPACE);
      long[] expected = {2, 5, 8, 11, 14, 17, 20, 23, 26, 27};
      for (int index = 0; index < BOUNDS.length; index++)
        assertEquals(expected[index], sample(result, "_bucket", "/login", BOUNDS[index]));
      assertEquals(27, sample(result, "_count", "/login", ""));
      assertEquals(38.7, sample(result, "_sum", "/login", ""), 1e-13);
    }
  }

  @Test
  void httpexp003TwoMaximumNanosecondsNeverWrapSum() {
    try (var source = new OverflowSafeHttpMeterRegistry(new MockClock())) {
      var recorder = new HttpMetricRecorder(source, "DEBUG");
      recorder.record("/login", "GET", 200, Long.MAX_VALUE);
      recorder.record("/login", "GET", 200, Long.MAX_VALUE);
      String result = exporter.scrapeTimers(source, SPACE);
      assertEquals(1.8446744073709553E10, sample(result, "_sum", "/login", ""));
      assertEquals(2, sample(result, "_count", "/login", ""));
      assertEquals(2, sample(result, "_bucket", "/login", "+Inf"));
      assertEquals(0, sample(result, "_bucket", "/login", "5.0"));
    }
  }

  @Test
  void httpexp004ClockWindowExpiryDoesNotEraseExportedLifetimeBuckets() {
    var clock = new MockClock();
    try (var source = new OverflowSafeHttpMeterRegistry(clock)) {
      var recorder = new HttpMetricRecorder(source, "DEBUG");
      recorder.record("/login", "GET", 200, 50_000_000);
      clock.add(Duration.ofDays(1));
      String result = exporter.scrapeTimers(source, SPACE);
      assertEquals(1, sample(result, "_count", "/login", ""));
      assertEquals(.05, sample(result, "_sum", "/login", ""));
      for (String bound : BOUNDS) assertEquals(1, sample(result, "_bucket", "/login", bound));
    }
  }

  @Test
  void httpexp005StandardAndOtherOwnerNeverReceiveFiniteWorkerEvents() throws Exception {
    try (var standard = new OverflowSafeHttpMeterRegistry(new MockClock());
        var source = new OverflowSafeHttpMeterRegistry(new MockClock());
        var workers = Executors.newFixedThreadPool(4)) {
      new HttpMetricRecorder(standard, "STANDARD");
      var recorder = new HttpMetricRecorder(source, "DEBUG");
      var jobs = new java.util.ArrayList<Future<?>>();
      for (int index = 0; index < 64; index++)
        jobs.add(workers.submit(() -> recorder.record("/login", "GET", 200, 1)));
      for (var job : jobs) job.get(10, TimeUnit.SECONDS);
      String result = exporter.scrapeTimers(source, SPACE);
      assertEquals(64, sample(result, "_count", "/login", ""));
      assertEquals(.000000064, sample(result, "_sum", "/login", ""));
      for (String bound : BOUNDS) assertEquals(64, sample(result, "_bucket", "/login", bound));
      assertEquals("", exporter.scrapeTimers(standard, SPACE));
      assertFalse(source.isClosed());
      assertFalse(standard.isClosed());
    }
  }

  @Test
  void httpexp006UnknownInputUsesClosedCatalogNotRawRouteOrMethod() {
    try (var source = new OverflowSafeHttpMeterRegistry(new MockClock())) {
      var recorder = new HttpMetricRecorder(source, "DEBUG");
      recorder.record("/not-approved-123", "UNAPPROVED", 503, 1);
      String result = exporter.scrapeTimers(source, SPACE);
      assertEquals(1, sample(result, "_count", "/**", ""));
      assertEquals(1, sample(result, "_bucket", "/**", "0.05"));
      assertFalse(result.contains("/not-approved-123"));
      assertFalse(result.contains("UNAPPROVED"));
      assertEquals(35, result.lines().filter(line -> line.startsWith(NAME + "_count{")).count());
    }
  }
}
