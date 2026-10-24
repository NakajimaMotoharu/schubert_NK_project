package dev.codex.schubert.nk.api.monitoring;

import static org.junit.jupiter.api.Assertions.*;

import dev.codex.schubert.nk.protocol.layout.LayoutId;
import io.micrometer.core.instrument.MockClock;
import io.micrometer.core.instrument.binder.jvm.JvmGcMetrics;
import io.micrometer.core.instrument.simple.SimpleConfig;
import java.lang.ref.Reference;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.regex.Pattern;
import org.junit.jupiter.api.Test;

/** APIPIPE001..002/1802: exact duration + SDK + ready/custom payload, no query/JMS/network. */
class ApiMetricPayloadPrecisionTest {
  private static final String READY = "# TYPE schubert_nk_api_ready gauge\nschubert_nk_api_ready ";
  private static final String DB = "nk_db_query_duration_seconds";
  private static final String MQ = "nk_mq_processing_duration_seconds";

  private static final class Bundle implements AutoCloseable {
    final ExactDurationMeterRegistry source =
        new ExactDurationMeterRegistry(SimpleConfig.DEFAULT, new MockClock());
    final List<JvmGcMetrics> gcs = new ArrayList<>();

    void supplied(boolean standardFirst, long db, long mq) {
      if (standardFirst) new ApiStandardMetrics().bind(source, "DEBUG", gcs::add);
      new DbQueryDurationMetricRecorder(source, "DEBUG")
          .record(
              DbQueryDurationMetricRecorder.Query.ASYNC_JOB_STATE_COUNTS,
              DbQueryDurationMetricRecorder.Outcome.SUCCESS,
              db);
      new MqProcessingDurationMetricRecorder(source, "DEBUG", new LayoutId("LGNREQ01"))
          .record(MqProcessingDurationMetricRecorder.Outcome.SUCCESS, mq);
      if (!standardFirst) new ApiStandardMetrics().bind(source, "DEBUG", gcs::add);
    }

    String text(boolean ready, AtomicInteger calls) {
      try {
        return new ApiCustomMetricPayload()
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

  private static void duration(String text, String name, Map<String, String> base, boolean tiny) {
    assertEquals(1, sample(text, name + "_count", base));
    assertEquals(tiny ? 1e-9 : 1.5, sample(text, name + "_sum", base));
    var bounds = List.of("0.001", "0.01", "0.1", "1.0", "1.5", "+Inf");
    int[] expected = tiny ? new int[] {1, 1, 1, 1, 1, 1} : new int[] {0, 0, 0, 0, 1, 1};
    for (int i = 0; i < bounds.size(); i++) {
      var tags = new HashMap<>(base);
      tags.put("le", bounds.get(i));
      assertEquals(expected[i], sample(text, name + "_bucket", tags));
    }
  }

  private static void verify(String text, boolean ready, boolean dbTiny) {
    assertTrue(text.startsWith(READY + (ready ? "1\n" : "0\n")));
    assertEquals(
        Set.of(
            "# TYPE schubert_nk_api_ready gauge",
            "# TYPE " + DB + " histogram",
            "# TYPE " + MQ + " histogram"),
        text.lines()
            .filter(line -> line.startsWith("# TYPE "))
            .collect(java.util.stream.Collectors.toSet()));
    assertEquals(49, text.lines().filter(line -> !line.startsWith("#") && !line.isBlank()).count());
    namespace(
        text,
        Set.of(
            "schubert_nk_api_ready",
            DB + "_bucket",
            DB + "_count",
            DB + "_sum",
            MQ + "_bucket",
            MQ + "_count",
            MQ + "_sum"));
    duration(text, DB, Map.of("query_id", "ASYNC_JOB_STATE_COUNTS", "outcome", "SUCCESS"), dbTiny);
    duration(
        text,
        MQ,
        Map.of("flow", "SYNCHRONOUS", "layout", "LGNREQ01", "outcome", "SUCCESS"),
        !dbTiny);
    assertEquals(
        0,
        sample(
            text,
            DB + "_count",
            Map.of("query_id", "OUTBOX_STATUS_COUNTS_OLDEST", "outcome", "SUCCESS")));
    assertEquals(
        0,
        sample(
            text,
            MQ + "_count",
            Map.of("flow", "SYNCHRONOUS", "layout", "LGNREQ01", "outcome", "FAILURE")));
  }

  @Test
  void apipipe001StandardFirstKeepsNanosecondDbAndBoundaryMq() {
    try (var bundle = new Bundle()) {
      bundle.supplied(true, 1, 1_500_000_000L);
      var calls = new AtomicInteger();
      verify(bundle.text(true, calls), true, true);
      assertEquals(1, calls.get());
      assertEquals(1, bundle.gcs.size());
      assertFalse(bundle.source.isClosed());
    }
  }

  @Test
  void apipipe002DurationFirstKeepsBoundaryDbAndNanosecondMqWithDownReady() {
    try (var bundle = new Bundle()) {
      bundle.supplied(false, 1_500_000_000L, 1);
      assertEquals(
          READY + "0\n",
          new ApiCustomMetricPayload()
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
