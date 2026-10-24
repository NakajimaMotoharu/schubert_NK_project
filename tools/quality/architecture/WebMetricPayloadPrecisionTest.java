package dev.codex.schubert.nk.web.monitoring;

import static org.junit.jupiter.api.Assertions.*;

import io.micrometer.core.instrument.MockClock;
import io.micrometer.core.instrument.binder.jvm.JvmGcMetrics;
import java.lang.ref.Reference;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.regex.Pattern;
import org.junit.jupiter.api.Test;

/** WEBPIPE001..002/1802: exact HTTP timer + SDK + ready/custom payload, no HTTP operation. */
class WebMetricPayloadPrecisionTest {
  private static final String READY = "# TYPE schubert_nk_web_ready gauge\nschubert_nk_web_ready ";
  private static final String D = "nk_http_request_duration_seconds";
  private static final String C = "nk_http_requests_total";

  private static final class Bundle implements AutoCloseable {
    final OverflowSafeHttpMeterRegistry source = new OverflowSafeHttpMeterRegistry(new MockClock());
    final List<JvmGcMetrics> gcs = new ArrayList<>();

    void supplied(boolean standardFirst, long ns) {
      if (standardFirst) new WebStandardMetrics().bind(source, "DEBUG", gcs::add);
      new HttpMetricRecorder(source, "DEBUG").record("/login", "GET", 200, ns);
      if (!standardFirst) new WebStandardMetrics().bind(source, "DEBUG", gcs::add);
    }

    String text(boolean ready, AtomicInteger calls) {
      try {
        return new WebCustomMetricPayload()
            .render(
                ready,
                "DEBUG",
                () -> {
                  calls.incrementAndGet();
                  return source;
                });
      } finally {
        Reference.reachabilityFence(this);
      }
    }

    public void close() {
      try {
        gcs.forEach(JvmGcMetrics::close);
      } finally {
        source.close();
      }
    }
  }

  private static Map<String, String> labels(String row) {
    String raw = row.substring(row.indexOf('{') + 1, row.lastIndexOf('}'));
    var result = new HashMap<String, String>();
    var matcher = Pattern.compile("([a-z_]+)=\"([^\"]*)\"").matcher(raw);
    while (matcher.find()) assertNull(result.put(matcher.group(1), matcher.group(2)));
    return result;
  }

  private static double sample(String text, String name, Map<String, String> expectedLabels) {
    var rows =
        text.lines()
            .filter(row -> row.startsWith(name + "{"))
            .filter(row -> labels(row).equals(expectedLabels))
            .toList();
    assertEquals(1, rows.size(), name + expectedLabels);
    String row = rows.getFirst();
    return Double.parseDouble(row.substring(row.lastIndexOf(' ') + 1));
  }

  private static void namespace(String text, Set<String> allowed) {
    for (String row : text.lines().filter(row -> !row.startsWith("#") && !row.isBlank()).toList())
      assertTrue(allowed.contains(row.split("[{ ]", 2)[0]), row);
  }

  private static void verify(String text, boolean ready, boolean tiny) {
    assertTrue(text.startsWith(READY + (ready ? "1\n" : "0\n")));
    assertEquals(
        Set.of(
            "# TYPE schubert_nk_web_ready gauge",
            "# TYPE " + C + " counter",
            "# TYPE " + D + " histogram"),
        text.lines()
            .filter(line -> line.startsWith("# TYPE "))
            .collect(java.util.stream.Collectors.toSet()));
    namespace(text, Set.of("schubert_nk_web_ready", C, D + "_bucket", D + "_count", D + "_sum"));
    var tags = Map.of("service", "WEB", "route", "/login");
    assertEquals(1, sample(text, D + "_count", tags));
    assertEquals(tiny ? 1e-9 : 1.5, sample(text, D + "_sum", tags));
    var bounds = List.of("0.05", "0.1", "0.25", "0.5", "1.0", "1.5", "2.0", "2.5", "5.0", "+Inf");
    int[] expected =
        tiny ? new int[] {1, 1, 1, 1, 1, 1, 1, 1, 1, 1} : new int[] {0, 0, 0, 0, 0, 1, 1, 1, 1, 1};
    for (int i = 0; i < bounds.size(); i++) {
      var bucket = new HashMap<>(tags);
      bucket.put("le", bounds.get(i));
      assertEquals(expected[i], sample(text, D + "_bucket", bucket));
    }
    assertEquals(
        1,
        sample(
            text,
            C,
            Map.of("service", "WEB", "route", "/login", "method", "GET", "status_class", "2xx")));
    assertEquals(
        0,
        sample(
            text,
            C,
            Map.of("service", "WEB", "route", "/login", "method", "GET", "status_class", "4xx")));
  }

  @Test
  void webpipe001StandardFirstKeepsOneNanosecondHttpTimer() {
    try (var bundle = new Bundle()) {
      bundle.supplied(true, 1);
      var calls = new AtomicInteger();
      verify(bundle.text(true, calls), true, true);
      assertEquals(1, calls.get());
      assertEquals(1, bundle.gcs.size());
      assertFalse(bundle.source.isClosed());
    }
  }

  @Test
  void webpipe002DurationFirstKeepsInclusiveBoundaryAndDownReady() {
    try (var bundle = new Bundle()) {
      bundle.supplied(false, 1_500_000_000L);
      assertEquals(
          READY + "0\n",
          new WebCustomMetricPayload()
              .render(
                  false,
                  "STANDARD",
                  () -> {
                    throw new AssertionError("not read");
                  }));
      var calls = new AtomicInteger();
      verify(bundle.text(false, calls), false, false);
      assertEquals(1, calls.get());
      assertEquals(1, bundle.gcs.size());
      assertFalse(bundle.source.isClosed());
    }
  }
}
