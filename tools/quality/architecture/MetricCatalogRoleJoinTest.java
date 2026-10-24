package dev.codex.schubert.nk.quality;

import static org.junit.jupiter.api.Assertions.*;

import dev.codex.schubert.nk.api.monitoring.ApiMetricCatalog;
import dev.codex.schubert.nk.batch.monitoring.BatchMetricLabelPolicy;
import dev.codex.schubert.nk.batch.monitoring.MetricContract;
import dev.codex.schubert.nk.web.monitoring.WebMetricCatalog;
import io.micrometer.core.instrument.Meter;
import io.micrometer.core.instrument.Tags;
import java.util.HashMap;
import java.util.Map;
import java.util.Set;
import org.junit.jupiter.api.Test;

/** METRICJOIN001..006/1783: independent literal SS351 schema, no production-generated expected. */
class MetricCatalogRoleJoinTest {
  private record Shape(String kind, Set<String> keys) {}

  private static Shape shape(String kind, String... keys) {
    return new Shape(kind, Set.of(keys));
  }

  private static final Map<String, Shape> SS =
      Map.ofEntries(
          Map.entry(
              "nk_http_requests_total",
              shape("counter", "service", "route", "method", "status_class")),
          Map.entry("nk_http_request_duration_seconds", shape("histogram", "service", "route")),
          Map.entry(
              "nk_mq_messages_total",
              shape("counter", "direction", "address", "layout", "outcome")),
          Map.entry(
              "nk_mq_processing_duration_seconds", shape("histogram", "flow", "layout", "outcome")),
          Map.entry("nk_mq_queue_messages", shape("gauge", "queue")),
          Map.entry("nk_mq_queue_bytes", shape("gauge", "queue")),
          Map.entry("nk_mq_address_memory_bytes", shape("gauge", "address")),
          Map.entry("nk_mq_address_paged_bytes", shape("gauge", "address")),
          Map.entry("nk_mq_paging_active", shape("gauge", "address")),
          Map.entry("nk_mq_page_files", shape("gauge", "address")),
          Map.entry("nk_mq_redeliveries_total", shape("counter", "queue", "delivery_count")),
          Map.entry("nk_outbox_rows", shape("gauge", "store", "status")),
          Map.entry("nk_outbox_oldest_seconds", shape("gauge", "store", "status")),
          Map.entry("nk_inbox_replays_total", shape("counter", "layout", "result")),
          Map.entry("nk_operation_token_mismatch_total", shape("counter", "operation")),
          Map.entry("nk_async_jobs", shape("gauge", "state")),
          Map.entry("nk_db_pool_connections", shape("gauge", "service", "state")),
          Map.entry("nk_db_query_duration_seconds", shape("histogram", "query_id", "outcome")),
          Map.entry("nk_file_transfer_files", shape("gauge", "suffix")),
          Map.entry("nk_file_transfer_bytes", shape("gauge", "suffix")),
          Map.entry("nk_media_streams", shape("gauge", "media_type")),
          Map.entry("nk_media_bytes_total", shape("counter", "media_type", "mode", "status")),
          Map.entry("nk_integrity_failures_total", shape("counter", "area", "step")),
          Map.entry("nk_batch_runs_total", shape("counter", "step", "status")),
          Map.entry("nk_batch_last_success_timestamp_seconds", shape("gauge", "step")),
          Map.entry("nk_process_restarts_total", shape("counter", "service", "reason")));
  private static final Set<String> API =
      Set.of(
          "nk_mq_messages_total",
          "nk_mq_processing_duration_seconds",
          "nk_mq_queue_messages",
          "nk_mq_queue_bytes",
          "nk_mq_address_memory_bytes",
          "nk_mq_address_paged_bytes",
          "nk_mq_paging_active",
          "nk_mq_page_files",
          "nk_mq_redeliveries_total",
          "nk_outbox_rows",
          "nk_outbox_oldest_seconds",
          "nk_inbox_replays_total",
          "nk_operation_token_mismatch_total",
          "nk_async_jobs",
          "nk_db_pool_connections",
          "nk_db_query_duration_seconds");
  private static final Set<String> WEB =
      Set.of(
          "nk_http_requests_total",
          "nk_http_request_duration_seconds",
          "nk_outbox_rows",
          "nk_outbox_oldest_seconds",
          "nk_db_pool_connections",
          "nk_media_streams",
          "nk_media_bytes_total");
  private static final Set<String> BATCH =
      Set.of(
          "nk_file_transfer_files",
          "nk_file_transfer_bytes",
          "nk_integrity_failures_total",
          "nk_batch_runs_total",
          "nk_batch_last_success_timestamp_seconds",
          "nk_process_restarts_total");

  private static void add(
      Map<String, Shape> actual, String kind, Map<String, Set<String>> supplied) {
    supplied.forEach(
        (name, keys) -> {
          var next = new Shape(kind, Set.copyOf(keys));
          var old = actual.putIfAbsent(name, next);
          if (old != null) assertEquals(old, next, "same named cross-role metric must keep schema");
        });
  }

  private static Map<String, Shape> api() {
    var catalog = new ApiMetricCatalog();
    var actual = new HashMap<String, Shape>();
    add(actual, "counter", catalog.counters());
    add(actual, "gauge", catalog.gauges());
    add(actual, "histogram", catalog.summaries());
    return Map.copyOf(actual);
  }

  private static Map<String, Shape> web() {
    var catalog = new WebMetricCatalog();
    var actual = new HashMap<String, Shape>();
    add(actual, "counter", catalog.counters());
    add(actual, "gauge", catalog.gauges());
    add(actual, "histogram", catalog.timers());
    return Map.copyOf(actual);
  }

  private static Map<String, Shape> batch() {
    var catalog = new BatchMetricLabelPolicy();
    var actual = new HashMap<String, Shape>();
    add(actual, "counter", catalog.names(MetricContract.Kind.COUNTER));
    add(actual, "gauge", catalog.names(MetricContract.Kind.GAUGE));
    add(actual, "histogram", catalog.names(MetricContract.Kind.HISTOGRAM));
    return Map.copyOf(actual);
  }

  private static Map<String, Shape> expected(Set<String> names) {
    var result = new HashMap<String, Shape>();
    for (String name : names) {
      assertTrue(SS.containsKey(name));
      result.put(name, SS.get(name));
    }
    return Map.copyOf(result);
  }

  @Test
  void metricjoin001All26AndExactlyThreeSharedGaugeNames() {
    var actual = new HashMap<String, Shape>();
    var frequencies = new HashMap<String, Integer>();
    int rows = 0;
    for (var role : java.util.List.of(api(), web(), batch())) {
      rows += role.size();
      role.forEach(
          (name, shape) -> {
            var old = actual.putIfAbsent(name, shape);
            if (old != null) assertEquals(old, shape);
            frequencies.merge(name, 1, Integer::sum);
          });
    }
    assertEquals(26, SS.size());
    assertEquals(SS, actual);
    assertEquals(29, rows);
    var shared = new HashMap<String, Integer>();
    frequencies.forEach(
        (name, count) -> {
          if (count > 1) shared.put(name, count);
        });
    assertEquals(
        Map.of("nk_outbox_rows", 2, "nk_outbox_oldest_seconds", 2, "nk_db_pool_connections", 2),
        shared);
  }

  @Test
  void metricjoin002ApiProjectionIsExactSixteen() {
    assertEquals(16, API.size());
    assertEquals(expected(API), api());
  }

  @Test
  void metricjoin003WebProjectionIsExactSeven() {
    assertEquals(7, WEB.size());
    assertEquals(expected(WEB), web());
  }

  @Test
  void metricjoin004BatchProjectionIsExactSix() {
    assertEquals(6, BATCH.size());
    assertEquals(expected(BATCH), batch());
  }

  @Test
  void metricjoin005SharedNamesDoNotWeakenRoleValues() {
    var api = new ApiMetricCatalog();
    var web = new WebMetricCatalog();
    for (String name :
        Set.of("nk_outbox_rows", "nk_outbox_oldest_seconds", "nk_db_pool_connections")) {
      boolean pool = name.equals("nk_db_pool_connections");
      String key = pool ? "service" : "store",
          other = pool ? "state" : "status",
          value = pool ? "active" : "PENDING";
      var apiId = new Meter.Id(name, Tags.of(key, "API", other, value), "", "", Meter.Type.GAUGE);
      var webId = new Meter.Id(name, Tags.of(key, "WEB", other, value), "", "", Meter.Type.GAUGE);
      assertEquals("API", api.labels(apiId).get(key));
      assertEquals(value, api.labels(apiId).get(other));
      assertEquals("WEB", web.labels(webId).get(key));
      assertEquals(value, web.labels(webId).get(other));
      assertThrows(IllegalArgumentException.class, () -> api.labels(webId));
      assertThrows(IllegalArgumentException.class, () -> web.labels(apiId));
    }
  }

  @Test
  void metricjoin006GlobalMetadataAlsoMatchesIndependentSsLiteral() {
    var actual = new HashMap<String, Shape>();
    for (var contract : MetricContract.values()) {
      String kind =
          switch (contract.type()) {
            case COUNTER -> "counter";
            case GAUGE -> "gauge";
            case HISTOGRAM -> "histogram";
          };
      assertNull(actual.put(contract.externalName(), new Shape(kind, contract.labelNames())));
    }
    assertEquals(SS, actual);
  }
}
