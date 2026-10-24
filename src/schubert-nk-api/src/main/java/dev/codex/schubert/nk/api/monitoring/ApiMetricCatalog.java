package dev.codex.schubert.nk.api.monitoring;

import dev.codex.schubert.nk.protocol.header.ResultCode;
import dev.codex.schubert.nk.protocol.layout.LayoutRegistry;
import dev.codex.schubert.nk.protocol.transport.BrokerTopology;
import io.micrometer.core.instrument.Meter;
import io.micrometer.core.instrument.Tag;
import io.prometheus.metrics.model.snapshots.Labels;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import java.util.TreeMap;
import java.util.stream.Collectors;

/** NK-OPS-001/RD171/UI252/SS351/1773 APICAT: API-only closed sixteen-family label domains. */
public final class ApiMetricCatalog {
  private static final String ROWS = "nk_outbox_rows";
  private static final String AGE = "nk_outbox_oldest_seconds";
  private static final String POOL = "nk_db_pool_connections";
  private static final String JOBS = "nk_async_jobs";
  private static final String INBOX = "nk_inbox_replays_total";
  private static final String OPERATION = "nk_operation_token_mismatch_total";
  private static final String REDELIVERY = "nk_mq_redeliveries_total";
  private static final String MESSAGE = "nk_mq_messages_total";
  private static final String DB_DURATION = "nk_db_query_duration_seconds";
  private static final String MQ_DURATION = "nk_mq_processing_duration_seconds";
  private static final String QUEUE_MESSAGES = "nk_mq_queue_messages";
  private static final String QUEUE_BYTES = "nk_mq_queue_bytes";
  private static final String ADDRESS_MEMORY = "nk_mq_address_memory_bytes";
  private static final String ADDRESS_PAGED = "nk_mq_address_paged_bytes";
  private static final String PAGING = "nk_mq_paging_active";
  private static final String PAGE_FILES = "nk_mq_page_files";
  private static final String QUEUE = "queue";
  private static final String ADDRESS = "address";
  private static final String LAYOUT = "layout";
  private static final String OUTCOME = "outcome";
  private static final String STATE = "state";
  private static final Set<String> GAUGE_NAMES =
      Set.of(
          ROWS,
          AGE,
          POOL,
          JOBS,
          QUEUE_MESSAGES,
          QUEUE_BYTES,
          ADDRESS_MEMORY,
          ADDRESS_PAGED,
          PAGING,
          PAGE_FILES);
  private static final Set<String> COUNTER_NAMES = Set.of(INBOX, OPERATION, REDELIVERY, MESSAGE);
  private static final Set<String> SUMMARY_NAMES = Set.of(DB_DURATION, MQ_DURATION);
  private static final Set<String> LAYOUTS =
      LayoutRegistry.standard().all().stream()
          .map(d -> d.id().value())
          .collect(Collectors.toUnmodifiableSet());
  private static final Set<String> QUEUES =
      Arrays.stream(BrokerTopology.values())
          .map(BrokerTopology::queue)
          .collect(Collectors.toUnmodifiableSet());
  private static final Set<String> ADDRESSES =
      Arrays.stream(BrokerTopology.values())
          .map(BrokerTopology::address)
          .collect(Collectors.toUnmodifiableSet());
  private static final Set<String> SUCCESS_FAILURE = Set.of("SUCCESS", "FAILURE");
  private static final Map<String, Set<String>> OUTBOX =
      Map.of("store", Set.of("API"), "status", Set.of("PENDING", "SENT", "ERROR"));
  private static final Map<String, Map<String, Set<String>>> VALUES =
      Map.ofEntries(
          Map.entry(ROWS, OUTBOX),
          Map.entry(AGE, OUTBOX),
          Map.entry(
              POOL,
              Map.of("service", Set.of("API"), STATE, Set.of("active", "idle", "pending", "max"))),
          Map.entry(
              JOBS,
              Map.of(STATE, Set.of("RECEIVED", "PROCESSING", "COMPLETED", "ERROR", "CANCELLED"))),
          Map.entry(
              INBOX,
              Map.of(
                  LAYOUT,
                  LAYOUTS,
                  "result",
                  Arrays.stream(ResultCode.values())
                      .map(ResultCode::wireValue)
                      .collect(Collectors.toUnmodifiableSet()))),
          Map.entry(
              OPERATION,
              Map.of(
                  "operation",
                  Set.of(
                      "UCRREQ01",
                      "USTREQ01",
                      "URLREQ01",
                      "UPWREQ01",
                      "ULKREQ01",
                      "QSBREQ01",
                      "NTCREQ01",
                      "QDLREQ01"))),
          Map.entry(REDELIVERY, Map.of(QUEUE, QUEUES, "delivery_count", Set.of("2", "3", "4"))),
          Map.entry(
              MESSAGE,
              Map.of(
                  "direction",
                  Set.of("SEND", "RECEIVE"),
                  ADDRESS,
                  ADDRESSES,
                  LAYOUT,
                  LAYOUTS,
                  OUTCOME,
                  Set.of("SUCCESS", "FAILURE", "ACK", "RETRY", "DLQ"))),
          Map.entry(
              DB_DURATION,
              Map.of(
                  "query_id",
                  Set.of("ASYNC_JOB_STATE_COUNTS", "OUTBOX_STATUS_COUNTS_OLDEST"),
                  OUTCOME,
                  SUCCESS_FAILURE)),
          Map.entry(
              MQ_DURATION,
              Map.of(
                  "flow",
                  Set.of("SYNCHRONOUS", "ASYNC_ACCEPTANCE", "INTERNAL"),
                  LAYOUT,
                  LAYOUTS,
                  OUTCOME,
                  SUCCESS_FAILURE)),
          Map.entry(QUEUE_MESSAGES, Map.of(QUEUE, QUEUES)),
          Map.entry(QUEUE_BYTES, Map.of(QUEUE, QUEUES)),
          Map.entry(ADDRESS_MEMORY, Map.of(ADDRESS, ADDRESSES)),
          Map.entry(ADDRESS_PAGED, Map.of(ADDRESS, ADDRESSES)),
          Map.entry(PAGING, Map.of(ADDRESS, ADDRESSES)),
          Map.entry(PAGE_FILES, Map.of(ADDRESS, ADDRESSES)));

  public ApiMetricCatalog() {}

  public Map<String, Set<String>> gauges() {
    return namespace(GAUGE_NAMES);
  }

  public Map<String, Set<String>> counters() {
    return namespace(COUNTER_NAMES);
  }

  public Map<String, Set<String>> summaries() {
    return namespace(SUMMARY_NAMES);
  }

  private static Map<String, Set<String>> namespace(Set<String> names) {
    var result = new HashMap<String, Set<String>>();
    for (String name : names)
      result.put(
          name, Set.copyOf(Objects.requireNonNull(VALUES.get(name), "metric domain").keySet()));
    return Map.copyOf(result);
  }

  /** Return one detached immutable copy; the codec uses these exact Labels in the model. */
  public Labels labels(Meter.Id id) {
    Objects.requireNonNull(id, "metric identity");
    var allowed = domain(id.getName());
    return copy(allowed, id.getTags());
  }

  // APIAPPROVED: the caller captured the name once before namespace selection.
  Labels labels(String name, List<Tag> tags) {
    return copy(domain(name), tags);
  }

  private static Map<String, Set<String>> domain(String name) {
    var allowed = VALUES.get(Objects.requireNonNull(name, "metric name"));
    if (allowed == null) throw new IllegalArgumentException("unknown API metric");
    return allowed;
  }

  private static Labels copy(Map<String, Set<String>> allowed, List<Tag> tags) {
    var result = new TreeMap<String, String>();
    for (var tag : Objects.requireNonNull(tags, "metric tags")) {
      Objects.requireNonNull(tag, "metric tag");
      String key = Objects.requireNonNull(tag.getKey(), "metric label key");
      String value = Objects.requireNonNull(tag.getValue(), "metric label value");
      var choices = allowed.get(key);
      if (choices == null || !choices.contains(value))
        throw new IllegalArgumentException("invalid API metric label");
      if (result.put(key, value) != null)
        throw new IllegalArgumentException("duplicate API metric label");
    }
    if (!result.keySet().equals(allowed.keySet()))
      throw new IllegalArgumentException("missing API metric label");
    return Labels.of(new ArrayList<>(result.keySet()), new ArrayList<>(result.values()));
  }
}
