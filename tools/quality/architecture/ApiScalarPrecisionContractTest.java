package dev.codex.schubert.nk.api.monitoring;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.protocol.header.ResultCode;
import dev.codex.schubert.nk.protocol.layout.LayoutId;
import dev.codex.schubert.nk.protocol.transport.BrokerTopology;
import io.micrometer.core.instrument.Gauge;
import io.micrometer.core.instrument.MockClock;
import io.micrometer.core.instrument.simple.SimpleConfig;
import java.lang.ref.Reference;
import java.time.Duration;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.Test;

/** APISCALAR001..008/1771: actual supplied precision API registry, no SQL/JMS/control. */
class ApiScalarPrecisionContractTest {
  private static final String INBOX = "nk_inbox_replays_total";
  private static final String OP = "nk_operation_token_mismatch_total";
  private static final String RED = "nk_mq_redeliveries_total";
  private static final String MQ = "nk_mq_messages_total";
  private static final String ROWS = "nk_outbox_rows";
  private static final String AGE = "nk_outbox_oldest_seconds";
  private static final String POOL = "nk_db_pool_connections";
  private static final Map<String, Set<String>> COUNTERS =
      Map.of(
          INBOX,
          Set.of("layout", "result"),
          OP,
          Set.of("operation"),
          RED,
          Set.of("queue", "delivery_count"),
          MQ,
          Set.of("direction", "address", "layout", "outcome"));
  private static final Map<String, Set<String>> GAUGES =
      Map.of(
          ROWS,
          Set.of("store", "status"),
          AGE,
          Set.of("store", "status"),
          "nk_async_jobs",
          Set.of("state"),
          POOL,
          Set.of("service", "state"),
          "nk_mq_queue_messages",
          Set.of("queue"),
          "nk_mq_queue_bytes",
          Set.of("queue"),
          "nk_mq_address_memory_bytes",
          Set.of("address"),
          "nk_mq_address_paged_bytes",
          Set.of("address"),
          "nk_mq_paging_active",
          Set.of("address"),
          "nk_mq_page_files",
          Set.of("address"));
  private final ApiScalarMetricExporter exporter = new ApiScalarMetricExporter();

  private static final class Bundle implements AutoCloseable {
    final ExactDurationMeterRegistry registry =
        new ExactDurationMeterRegistry(SimpleConfig.DEFAULT, new MockClock());
    final OutboxRowsMetricRecorder rows;
    final OutboxAgeMetricRecorder age;
    final AsyncJobMetricRecorder jobs;
    final DbPoolMetricRecorder pool;
    final MqPressureMetricRecorder pressure;
    final InboxReplayMetricRecorder inbox;
    final OperationMismatchMetricRecorder operation;
    final MqRedeliveryMetricRecorder redelivery;
    final MqMessageMetricRecorder messages;
    final DbQueryDurationMetricRecorder unselectedDuration;

    Bundle(String mode) {
      rows = new OutboxRowsMetricRecorder(registry, mode);
      age = new OutboxAgeMetricRecorder(registry, mode);
      jobs = new AsyncJobMetricRecorder(registry, mode);
      pool = new DbPoolMetricRecorder(registry, mode);
      pressure = new MqPressureMetricRecorder(registry, mode);
      inbox = new InboxReplayMetricRecorder(registry, mode);
      operation = new OperationMismatchMetricRecorder(registry, mode);
      redelivery = new MqRedeliveryMetricRecorder(registry, mode);
      messages =
          new MqMessageMetricRecorder(
              registry, mode, new LayoutId("WLGEVT01"), BrokerTopology.WEB_LOG);
      unselectedDuration = new DbQueryDurationMetricRecorder(registry, mode);
    }

    String text(ApiScalarMetricExporter target) {
      try {
        return target.scrapeGauges(registry, GAUGES) + target.scrapeCounters(registry, COUNTERS);
      } finally {
        Reference.reachabilityFence(this);
      }
    }

    void gauges() {
      rows.record(new OutboxRowsMetricRecorder.Counts(3, 5, 2));
      age.record(
          new OutboxAgeMetricRecorder.Ages(
              Duration.ofSeconds(7), Duration.ofMillis(3500), Duration.ofNanos(1)));
      pool.record(new DbPoolMetricRecorder.Counts(3, 5, 2, 8));
      jobs.record(
          new AsyncJobMetricRecorder.Snapshot(
              Map.of(
                  AsyncJobMetricRecorder.State.RECEIVED,
                  11L,
                  AsyncJobMetricRecorder.State.PROCESSING,
                  23L,
                  AsyncJobMetricRecorder.State.COMPLETED,
                  37L,
                  AsyncJobMetricRecorder.State.ERROR,
                  41L,
                  AsyncJobMetricRecorder.State.CANCELLED,
                  53L)));
      pressure.record(
          BrokerTopology.WEB_LOG, new MqPressureMetricRecorder.Snapshot(3, 30, 10, 20, true, 2));
    }

    void counters() {
      inbox.record(new LayoutId("LGNREQ01"), ResultCode.SUCCESS);
      operation.record(OperationMismatchMetricRecorder.Operation.UCRREQ01);
      redelivery.recordDelivery(BrokerTopology.WEB_LOG, 2);
      messages.record(MqMessageMetricRecorder.Stage.SEND_SUCCESS);
      messages.record(MqMessageMetricRecorder.Stage.SEND_SUCCESS);
    }

    public void close() {
      registry.close();
    }
  }

  private static void catalog(String text) {
    var types = text.lines().filter(line -> line.startsWith("# TYPE ")).toList();
    assertEquals(14, types.size());
    GAUGES.keySet().forEach(name -> assertTrue(types.contains("# TYPE " + name + " gauge")));
    COUNTERS.keySet().forEach(name -> assertTrue(types.contains("# TYPE " + name + " counter")));
    assertEquals(852, text.lines().filter(line -> !line.startsWith("#")).count());
    assertFalse(text.contains("_total_total"));
    assertFalse(text.contains("_messages_total_messages"));
    assertFalse(text.contains(".histogram"));
    assertFalse(text.contains("_bucket"));
    assertFalse(text.contains("nk_db_query_duration_seconds"));
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

  @Test
  void apiscalar001ActualPrecisionInitialFourteenFamiliesAnd852Samples() {
    try (var b = new Bundle("DEBUG")) {
      String result = b.text(exporter);
      catalog(result);
      assertEquals(51, result.lines().filter(line -> line.endsWith("} NaN")).count());
      assertEquals(801, result.lines().filter(line -> line.endsWith("} 0.0")).count());
      assertFalse(b.registry.isClosed());
    }
  }

  @Test
  void apiscalar002KnownApiGaugesAndOneMqDestinationKeepIndependentUnknowns() {
    try (var b = new Bundle("DEBUG")) {
      b.gauges();
      String result = b.text(exporter);
      catalog(result);
      assertEquals(3, value(result, ROWS, Map.of("store", "API", "status", "PENDING")));
      assertEquals(3.5, value(result, AGE, Map.of("store", "API", "status", "SENT")));
      assertEquals(1.0E-9, value(result, AGE, Map.of("store", "API", "status", "ERROR")));
      assertEquals(37, value(result, "nk_async_jobs", Map.of("state", "COMPLETED")));
      assertEquals(8, value(result, POOL, Map.of("service", "API", "state", "max")));
      assertEquals(3, value(result, "nk_mq_queue_messages", Map.of("queue", "nk.web.log.q")));
      assertEquals(30, value(result, "nk_mq_queue_bytes", Map.of("queue", "nk.web.log.q")));
      assertEquals(
          10, value(result, "nk_mq_address_memory_bytes", Map.of("address", "nk.web.log")));
      assertEquals(20, value(result, "nk_mq_address_paged_bytes", Map.of("address", "nk.web.log")));
      assertEquals(1, value(result, "nk_mq_paging_active", Map.of("address", "nk.web.log")));
      assertEquals(2, value(result, "nk_mq_page_files", Map.of("address", "nk.web.log")));
      assertEquals(30, result.lines().filter(line -> line.endsWith("} NaN")).count());
    }
  }

  @Test
  void apiscalar003EachSuppliedCounterEventHasIndependentLiteralIncrement() {
    try (var b = new Bundle("DEBUG")) {
      b.counters();
      String result = b.text(exporter);
      catalog(result);
      assertEquals(1, value(result, INBOX, Map.of("layout", "LGNREQ01", "result", "0000")));
      assertEquals(1, value(result, OP, Map.of("operation", "UCRREQ01")));
      assertEquals(1, value(result, RED, Map.of("queue", "nk.web.log.q", "delivery_count", "2")));
      assertEquals(
          2,
          value(
              result,
              MQ,
              Map.of(
                  "direction",
                  "SEND",
                  "address",
                  "nk.web.log",
                  "layout",
                  "WLGEVT01",
                  "outcome",
                  "SUCCESS")));
    }
  }

  @Test
  void apiscalar004StandardIsUnregisteredNotFiftyOneUnknownGauges() {
    try (var b = new Bundle("STANDARD")) {
      assertEquals("", b.text(exporter));
      assertFalse(b.registry.isClosed());
    }
  }

  @Test
  void apiscalar005FiniteConcurrentEventsReachSixtyFourAfterJoin() throws Exception {
    try (var b = new Bundle("DEBUG");
        var workers = Executors.newFixedThreadPool(4)) {
      var jobs = new ArrayList<Future<?>>();
      for (int index = 0; index < 64; index++)
        jobs.add(
            workers.submit(() -> b.inbox.record(new LayoutId("LGNREQ01"), ResultCode.SUCCESS)));
      for (var job : jobs) job.get(10, TimeUnit.SECONDS);
      String result = b.text(exporter);
      catalog(result);
      assertEquals(64, value(result, INBOX, Map.of("layout", "LGNREQ01", "result", "0000")));
      assertFalse(b.registry.isClosed());
    }
  }

  @Test
  void apiscalar006MissingKnownZeroAndFractionalSecondsAreDifferent() {
    try (var b = new Bundle("DEBUG")) {
      b.rows.record(new OutboxRowsMetricRecorder.Counts(3, 5, 2));
      b.age.record(
          new OutboxAgeMetricRecorder.Ages(Duration.ofMillis(3500), Duration.ZERO, Duration.ZERO));
      assertEquals(3.5, value(b.text(exporter), AGE, Map.of("store", "API", "status", "PENDING")));
      b.rows.missing();
      b.age.missing();
      String missing = b.text(exporter);
      assertTrue(Double.isNaN(value(missing, ROWS, Map.of("store", "API", "status", "PENDING"))));
      assertTrue(Double.isNaN(value(missing, AGE, Map.of("store", "API", "status", "PENDING"))));
      b.rows.record(new OutboxRowsMetricRecorder.Counts(0, 0, 0));
      b.age.record(new OutboxAgeMetricRecorder.Ages(Duration.ZERO, Duration.ZERO, Duration.ZERO));
      assertEquals(0, value(b.text(exporter), ROWS, Map.of("store", "API", "status", "PENDING")));
      assertEquals(0, value(b.text(exporter), AGE, Map.of("store", "API", "status", "PENDING")));
    }
  }

  @Test
  void apiscalar007SubsetAndUnknownProvidersDoNotChangeCallerNamespace() {
    try (var b = new Bundle("DEBUG")) {
      var unknownReads = new AtomicInteger();
      Gauge.builder(
              "nk_unapproved_fixture",
              unknownReads,
              ref -> {
                ref.incrementAndGet();
                throw new AssertionError("unselected provider");
              })
          .register(b.registry);
      var space = new HashMap<String, Set<String>>();
      space.put(ROWS, Set.of("store", "status"));
      String result = exporter.scrapeGauges(b.registry, space);
      assertEquals(4, result.lines().count());
      assertEquals(3, result.lines().filter(line -> line.endsWith("} NaN")).count());
      assertEquals(Map.of(ROWS, Set.of("store", "status")), space);
      assertFalse(result.contains("nk_unapproved_fixture"));
      assertEquals(0, unknownReads.get());
      String counters =
          exporter.scrapeCounters(b.registry, Map.of(INBOX, Set.of("layout", "result")));
      assertEquals(769, counters.lines().count());
      assertEquals(0, unknownReads.get());
    }
  }

  @Test
  void apiscalar008ExporterDoesNotShareObservationsBetweenSourceOwners() {
    try (var first = new Bundle("DEBUG");
        var other = new Bundle("DEBUG")) {
      first.gauges();
      first.counters();
      String initialOther = other.text(exporter);
      catalog(initialOther);
      assertEquals(51, initialOther.lines().filter(line -> line.endsWith("} NaN")).count());
      assertEquals(0, value(initialOther, INBOX, Map.of("layout", "LGNREQ01", "result", "0000")));
      assertEquals(
          1, value(first.text(exporter), INBOX, Map.of("layout", "LGNREQ01", "result", "0000")));
      assertFalse(first.registry.isClosed());
      assertFalse(other.registry.isClosed());
    }
  }
}
