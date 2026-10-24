package dev.codex.schubert.nk.api.monitoring;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.protocol.layout.LayoutId;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Test;

/** APISUM001..006/1753: supplied nanoseconds and literal SS351 buckets, no DB/JMS. */
class ApiSummaryExporterContractTest {
  private static final String DB = "nk_db_query_duration_seconds";
  private static final String MQ = "nk_mq_processing_duration_seconds";
  private static final Map<String, Set<String>> SPACE =
      Map.of(DB, Set.of("query_id", "outcome"), MQ, Set.of("flow", "layout", "outcome"));
  private static final String[] BOUNDS = {"0.001", "0.01", "0.1", "1.0", "1.5", "+Inf"};
  private final ApiDurationMetricExporter exporter = new ApiDurationMetricExporter();

  private static double sample(String text, String name, Map<String, String> labels) {
    var matches =
        text.lines()
            .filter(line -> line.startsWith(name + "{"))
            .filter(
                line ->
                    labels.entrySet().stream()
                        .allMatch(
                            entry ->
                                line.contains(entry.getKey() + "=\"" + entry.getValue() + "\"")))
            .toList();
    assertEquals(1, matches.size(), name + labels);
    String line = matches.getFirst();
    return Double.parseDouble(line.substring(line.lastIndexOf(' ') + 1));
  }

  private static Map<String, String> db() {
    return Map.of("query_id", "ASYNC_JOB_STATE_COUNTS", "outcome", "SUCCESS");
  }

  private static Map<String, String> bucket(Map<String, String> labels, String bound) {
    var copy = new java.util.HashMap<>(labels);
    copy.put("le", bound);
    return Map.copyOf(copy);
  }

  private static DbQueryDurationMetricRecorder dbRecorder(ExactDurationMeterRegistry registry) {
    return new DbQueryDurationMetricRecorder(registry, "DEBUG");
  }

  private static void record(DbQueryDurationMetricRecorder recorder, long ns) {
    recorder.record(
        DbQueryDurationMetricRecorder.Query.ASYNC_JOB_STATE_COUNTS,
        DbQueryDurationMetricRecorder.Outcome.SUCCESS,
        ns);
  }

  @Test
  void apisum001BothApprovedFamiliesHaveAllInitialSeriesAndBuckets() {
    try (var registry = new ExactDurationMeterRegistry()) {
      dbRecorder(registry);
      new MqProcessingDurationMetricRecorder(registry, "DEBUG", new LayoutId("LGNREQ01"));
      String result = exporter.scrape(registry, SPACE);
      assertEquals(2, result.lines().filter(line -> line.startsWith("# TYPE")).count());
      assertEquals(48, result.lines().filter(line -> !line.startsWith("#")).count());
      assertTrue(result.contains("# TYPE " + DB + " histogram\n"));
      assertTrue(result.contains("# TYPE " + MQ + " histogram\n"));
      for (String bound : BOUNDS)
        assertEquals(0, sample(result, DB + "_bucket", bucket(db(), bound)));
      assertEquals(0, sample(result, DB + "_count", db()));
      assertEquals(0, sample(result, DB + "_sum", db()));
      assertFalse(registry.isClosed());
    }
  }

  @Test
  void apisum002NanosecondAndFiveExactFiniteBoundaries() {
    try (var registry = new ExactDurationMeterRegistry()) {
      var recorder = dbRecorder(registry);
      record(recorder, 1);
      String one = exporter.scrape(registry, SPACE);
      assertEquals(.000000001, sample(one, DB + "_sum", db()));
      for (String bound : BOUNDS) assertEquals(1, sample(one, DB + "_bucket", bucket(db(), bound)));
    }
    try (var registry = new ExactDurationMeterRegistry()) {
      var recorder = dbRecorder(registry);
      for (long bound :
          new long[] {1_000_000, 10_000_000, 100_000_000, 1_000_000_000, 1_500_000_000})
        for (long value : new long[] {bound - 1, bound, bound + 1}) record(recorder, value);
      String result = exporter.scrape(registry, SPACE);
      long[] expected = {2, 5, 8, 11, 14, 15};
      for (int index = 0; index < BOUNDS.length; index++)
        assertEquals(expected[index], sample(result, DB + "_bucket", bucket(db(), BOUNDS[index])));
      assertEquals(15, sample(result, DB + "_count", db()));
      assertEquals(7.833, sample(result, DB + "_sum", db()), 1e-14);
    }
  }

  @Test
  void apisum003TwoLongMaximumNanosecondsRetainPositiveSumAndInfiniteCount() {
    try (var registry = new ExactDurationMeterRegistry()) {
      var recorder = dbRecorder(registry);
      record(recorder, Long.MAX_VALUE);
      record(recorder, Long.MAX_VALUE);
      String result = exporter.scrape(registry, SPACE);
      assertEquals(1.8446744073709553E10, sample(result, DB + "_sum", db()));
      assertEquals(2, sample(result, DB + "_count", db()));
      for (String bound : List.of("0.001", "0.01", "0.1", "1.0", "1.5"))
        assertEquals(0, sample(result, DB + "_bucket", bucket(db(), bound)));
      assertEquals(2, sample(result, DB + "_bucket", bucket(db(), "+Inf")));
    }
  }

  @Test
  void apisum004MqUsesIndependentLayoutFlowAndOutcomeSeries() {
    try (var registry = new ExactDurationMeterRegistry()) {
      var recorder =
          new MqProcessingDurationMetricRecorder(registry, "DEBUG", new LayoutId("LGNREQ01"));
      recorder.record(MqProcessingDurationMetricRecorder.Outcome.SUCCESS, 1);
      recorder.record(MqProcessingDurationMetricRecorder.Outcome.FAILURE, 1_500_000_001L);
      String result = exporter.scrape(registry, SPACE);
      var success = Map.of("flow", "SYNCHRONOUS", "layout", "LGNREQ01", "outcome", "SUCCESS");
      var failure = Map.of("flow", "SYNCHRONOUS", "layout", "LGNREQ01", "outcome", "FAILURE");
      assertEquals(.000000001, sample(result, MQ + "_sum", success));
      assertEquals(1.500000001, sample(result, MQ + "_sum", failure));
      for (String bound : BOUNDS)
        assertEquals(1, sample(result, MQ + "_bucket", bucket(success, bound)));
      assertEquals(0, sample(result, MQ + "_bucket", bucket(failure, "1.5")));
      assertEquals(1, sample(result, MQ + "_bucket", bucket(failure, "+Inf")));
    }
  }

  @Test
  void apisum005StandardAndSeparateRegistryAreNotPopulatedOrClosed() {
    try (var first = new ExactDurationMeterRegistry();
        var second = new ExactDurationMeterRegistry()) {
      new DbQueryDurationMetricRecorder(first, "STANDARD");
      new MqProcessingDurationMetricRecorder(first, "STANDARD", new LayoutId("LGNREQ01"));
      assertEquals("", exporter.scrape(first, SPACE));
      record(dbRecorder(second), 1_000_000);
      assertEquals(1, sample(exporter.scrape(second, SPACE), DB + "_count", db()));
      assertEquals("", exporter.scrape(first, SPACE));
      assertFalse(first.isClosed());
      assertFalse(second.isClosed());
    }
  }

  @Test
  void apisum006FiniteWorkersAndSimultaneousScrapesKeepAtomicBucketCount() throws Exception {
    try (var registry = new ExactDurationMeterRegistry();
        var workers = Executors.newFixedThreadPool(4)) {
      var recorder = dbRecorder(registry);
      var futures = new java.util.ArrayList<java.util.concurrent.Future<?>>();
      for (int index = 0; index < 64; index++)
        futures.add(workers.submit(() -> record(recorder, 1_000_000)));
      String intermediate = exporter.scrape(registry, SPACE);
      assertEquals(
          sample(intermediate, DB + "_count", db()),
          sample(intermediate, DB + "_bucket", bucket(db(), "+Inf")));
      for (var future : futures) future.get(10, TimeUnit.SECONDS);
      String result = exporter.scrape(registry, SPACE);
      assertEquals(64, sample(result, DB + "_count", db()));
      assertEquals(.064, sample(result, DB + "_sum", db()), 1e-15);
      for (String bound : BOUNDS)
        assertEquals(64, sample(result, DB + "_bucket", bucket(db(), bound)));
      assertFalse(registry.isClosed());
    }
  }
}
