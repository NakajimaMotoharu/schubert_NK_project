package dev.codex.schubert.nk.batch.monitoring;

import java.util.List;
import java.util.Objects;
import java.util.Set;

/**
 * Closed metadata only, not a metric recorder/exporter or label-value policy. NK-OPS-001/P018-09;
 * MON005/006/009/013; UI252; SS351 §6/10; PG-D518/PT-OPS-METRIC-001..006.
 */
public enum MetricContract {
  HTTP_REQUESTS(
      "nk_http_requests_total",
      Kind.COUNTER,
      MetricContract.SERVICE_LABEL,
      "route",
      "method",
      "status_class"),
  HTTP_DURATION(
      "nk_http_request_duration_seconds", Kind.HISTOGRAM, MetricContract.SERVICE_LABEL, "route"),
  MQ_MESSAGES(
      "nk_mq_messages_total",
      Kind.COUNTER,
      "direction",
      MetricContract.ADDRESS_LABEL,
      "layout",
      "outcome"),
  MQ_DURATION("nk_mq_processing_duration_seconds", Kind.HISTOGRAM, "flow", "layout", "outcome"),
  MQ_QUEUE_MESSAGES("nk_mq_queue_messages", Kind.GAUGE, "queue"),
  MQ_QUEUE_BYTES("nk_mq_queue_bytes", Kind.GAUGE, "queue"),
  MQ_ADDRESS_MEMORY("nk_mq_address_memory_bytes", Kind.GAUGE, MetricContract.ADDRESS_LABEL),
  MQ_ADDRESS_PAGED("nk_mq_address_paged_bytes", Kind.GAUGE, MetricContract.ADDRESS_LABEL),
  MQ_PAGING_ACTIVE("nk_mq_paging_active", Kind.GAUGE, MetricContract.ADDRESS_LABEL),
  MQ_PAGE_FILES("nk_mq_page_files", Kind.GAUGE, MetricContract.ADDRESS_LABEL),
  MQ_REDELIVERIES("nk_mq_redeliveries_total", Kind.COUNTER, "queue", "delivery_count"),
  OUTBOX_ROWS("nk_outbox_rows", Kind.GAUGE, "store", MetricContract.STATUS_LABEL),
  OUTBOX_OLDEST("nk_outbox_oldest_seconds", Kind.GAUGE, "store", MetricContract.STATUS_LABEL),
  INBOX_REPLAYS("nk_inbox_replays_total", Kind.COUNTER, "layout", "result"),
  OPERATION_TOKEN_MISMATCH("nk_operation_token_mismatch_total", Kind.COUNTER, "operation"),
  ASYNC_JOBS("nk_async_jobs", Kind.GAUGE, "state"),
  DB_POOL_CONNECTIONS("nk_db_pool_connections", Kind.GAUGE, MetricContract.SERVICE_LABEL, "state"),
  DB_QUERY_DURATION("nk_db_query_duration_seconds", Kind.HISTOGRAM, "query_id", "outcome"),
  FILE_TRANSFER_FILES("nk_file_transfer_files", Kind.GAUGE, "suffix"),
  FILE_TRANSFER_BYTES("nk_file_transfer_bytes", Kind.GAUGE, "suffix"),
  MEDIA_STREAMS("nk_media_streams", Kind.GAUGE, "media_type"),
  MEDIA_BYTES(
      "nk_media_bytes_total", Kind.COUNTER, "media_type", "mode", MetricContract.STATUS_LABEL),
  INTEGRITY_FAILURES("nk_integrity_failures_total", Kind.COUNTER, "area", "step"),
  BATCH_RUNS("nk_batch_runs_total", Kind.COUNTER, "step", MetricContract.STATUS_LABEL),
  BATCH_LAST_SUCCESS("nk_batch_last_success_timestamp_seconds", Kind.GAUGE, "step"),
  PROCESS_RESTARTS(
      "nk_process_restarts_total", Kind.COUNTER, MetricContract.SERVICE_LABEL, "reason");

  private static final String SERVICE_LABEL = "service";
  private static final String ADDRESS_LABEL = "address";
  private static final String STATUS_LABEL = "status";

  public enum Kind {
    COUNTER,
    GAUGE,
    HISTOGRAM
  }

  private final String wireName;
  private final Kind kind;
  private final Set<String> labels;

  MetricContract(String wireName, Kind kind, String... labels) {
    this.wireName = wireName;
    this.kind = kind;
    this.labels = Set.copyOf(List.of(labels));
  }

  /** Strict catalogue lookup. Unknown names are not echoed or normalized into known names. */
  public static MetricContract parse(String value) {
    Objects.requireNonNull(value, "metric name");
    for (var contract : values()) {
      if (contract.wireName.equals(value)) return contract;
    }
    throw new IllegalArgumentException("CONFIG_INVALID");
  }

  public String externalName() {
    return wireName;
  }

  public Kind type() {
    return kind;
  }

  public Set<String> labelNames() {
    return labels;
  }

  /** Validate names only. Caller must separately establish closed, nonsecret label values. */
  public void verifyLabelNames(Set<String> observed) {
    var snapshot = Set.copyOf(Objects.requireNonNull(observed, "metric label names"));
    if (!labels.equals(snapshot)) throw new IllegalArgumentException("CONFIG_INVALID");
  }

  /** SS351 HTTP duration buckets only; no implied bucket policy for MQ or DB histograms. */
  public static List<Double> httpDurationBucketsSeconds() {
    return List.of(.05, .1, .25, .5, 1., 1.5, 2., 2.5, 5.);
  }
}
