package dev.codex.schubert.nk.batch.monitoring;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Locale;
import java.util.Set;
import java.util.concurrent.Callable;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Test;

/** SS351 independently transcribed TSV and literals; PT-OPS-METRIC-001..006/spec1543. */
class MetricContractTest {
  private static final String INVALID_CONFIGURATION_CODE = "CONFIG_INVALID";

  private static List<List<String>> fixture() throws IOException {
    try (var stream =
        MetricContractTest.class.getResourceAsStream("/monitoring/metric-catalog.tsv")) {
      assertNotNull(stream, "independent approved metric fixture");
      return new String(stream.readAllBytes(), StandardCharsets.UTF_8)
          .lines()
          .map(line -> List.of(line.split("\t", -1)))
          .toList();
    }
  }

  @Test
  void metric001CompleteIndependentCatalog() throws IOException {
    var fixture = fixture();
    assertEquals(26, fixture.size());
    assertEquals(26, MetricContract.values().length);
    var seen = new HashSet<String>();
    for (var row : fixture) {
      assertEquals(3, row.size());
      assertTrue(seen.add(row.get(0)));
      var actual = MetricContract.parse(row.get(0));
      assertEquals(row.get(0), actual.externalName());
      assertEquals(row.get(1), actual.type().name().toLowerCase(Locale.ROOT));
      assertEquals(Set.of(row.get(2).split(",")), actual.labelNames());
    }
  }

  @Test
  void metric002UnknownMissingAndAliasedNamesRejected() {
    assertThrows(NullPointerException.class, () -> MetricContract.parse(null));
    for (String value :
        List.of(
            "",
            "unknown",
            "NK_HTTP_REQUESTS_TOTAL",
            "nk_http_requests_total ",
            " nk_http_requests_total",
            "nk_http_requests_total\n",
            "synthetic-private-canary")) {
      assertEquals(
          INVALID_CONFIGURATION_CODE,
          assertThrows(IllegalArgumentException.class, () -> MetricContract.parse(value))
              .getMessage());
    }
  }

  @Test
  void metric003ExactLabelNamesNoImplicitOrSensitiveKeys() throws IOException {
    for (var row : fixture()) {
      var metric = MetricContract.parse(row.get(0));
      var expected = Set.of(row.get(2).split(","));
      assertDoesNotThrow(() -> metric.verifyLabelNames(expected));
      assertEquals(
          INVALID_CONFIGURATION_CODE,
          assertThrows(IllegalArgumentException.class, () -> metric.verifyLabelNames(Set.of()))
              .getMessage());
      for (String key : expected) {
        var missing = new HashSet<>(expected);
        missing.remove(key);
        assertEquals(
            INVALID_CONFIGURATION_CODE,
            assertThrows(IllegalArgumentException.class, () -> metric.verifyLabelNames(missing))
                .getMessage());
      }
      for (String extra :
          List.of(
              "username",
              "ip",
              "request_id",
              "message_id",
              "correlation_id",
              "token",
              "receipt_id",
              "media_id",
              "path",
              "exception",
              "SERVICE")) {
        var invalid = new HashSet<>(expected);
        invalid.add(extra);
        assertEquals(
            INVALID_CONFIGURATION_CODE,
            assertThrows(IllegalArgumentException.class, () -> metric.verifyLabelNames(invalid))
                .getMessage());
      }
      assertThrows(NullPointerException.class, () -> metric.verifyLabelNames(null));
      var nullElement = new HashSet<>(expected);
      nullElement.add(null);
      assertThrows(NullPointerException.class, () -> metric.verifyLabelNames(nullElement));
    }
  }

  @Test
  void metric004NoMutableStateExposureOrRetention() {
    var metric = MetricContract.HTTP_REQUESTS;
    assertThrows(UnsupportedOperationException.class, () -> metric.labelNames().add("username"));
    var input = new HashSet<>(Set.of("service", "route", "method", "status_class"));
    metric.verifyLabelNames(input);
    input.add("username");
    assertEquals(Set.of("service", "route", "method", "status_class"), metric.labelNames());
    assertDoesNotThrow(
        () -> metric.verifyLabelNames(Set.of("service", "route", "method", "status_class")));
  }

  @Test
  void metric005IndependentHttpBucketsAndImmutableResult() {
    var actual = MetricContract.httpDurationBucketsSeconds();
    assertEquals(List.of(0.05, 0.1, 0.25, 0.5, 1.0, 1.5, 2.0, 2.5, 5.0), actual);
    assertThrows(UnsupportedOperationException.class, () -> actual.add(10.0));
  }

  @Test
  void metric006ConcurrentCallersObserveOnlyOriginalCatalog() throws Exception {
    var expected = fixture();
    var executor = Executors.newFixedThreadPool(4);
    try {
      var tasks = new ArrayList<Callable<String>>();
      for (int index = 0; index < 64; index++) {
        tasks.add(
            () -> {
              for (var row : expected) {
                var metric = MetricContract.parse(row.get(0));
                assertEquals(row.get(0), metric.externalName());
                assertEquals(Set.of(row.get(2).split(",")), metric.labelNames());
                metric.verifyLabelNames(Set.of(row.get(2).split(",")));
              }
              return "verified";
            });
      }
      for (var future : executor.invokeAll(tasks)) assertEquals("verified", future.get());
    } finally {
      executor.shutdownNow();
      assertTrue(executor.awaitTermination(10, TimeUnit.SECONDS));
    }
  }
}
