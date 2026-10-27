package dev.codex.schubert.nk.api.monitoring;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import io.micrometer.core.instrument.Meter;
import io.micrometer.core.instrument.Tag;
import io.micrometer.core.instrument.Tags;
import io.prometheus.metrics.model.snapshots.Labels;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Test;

/** APICAT001..014/1773: expected domains are SS literals and an independent route fixture. */
class ApiMetricCatalogTest {
  private static final String WEB_LOG_ADDRESS = "nk.web.log";
  private static final String SERVICE_LABEL = "service";
  private static final String API_SERVICE_VALUE = "API";
  private static final String STATE_LABEL = "state";
  private static final String ACTIVE_POOL_STATE = "active";
  private static final String LAYOUT_LABEL = "layout";
  private static final String QUEUE_LABEL = "queue";
  private static final String ADDRESS_LABEL = "address";
  private static final String OUTCOME_LABEL = "outcome";
  private static final String SUCCESS_OUTCOME = "SUCCESS";
  private static final String POOL = "nk_db_pool_connections";
  private static final String ROWS = "nk_outbox_rows";
  private static final String AGE = "nk_outbox_oldest_seconds";
  private static final String INBOX = "nk_inbox_replays_total";
  private static final String OP = "nk_operation_token_mismatch_total";
  private static final String RED = "nk_mq_redeliveries_total";
  private static final String MQ = "nk_mq_messages_total";
  private static final String DB = "nk_db_query_duration_seconds";
  private static final String MQD = "nk_mq_processing_duration_seconds";
  private static final List<String> LAYOUTS =
      List.of(
          "LGNREQ01",
          "LGNRSP01",
          "LOGREQ01",
          "LOGRSP01",
          "GAMREQ01",
          "GAMRSP01",
          "SPKREQ01",
          "SPKRSP01",
          "SRCREQ01",
          "SRCRSP01",
          "RTEREQ01",
          "RTERSP01",
          "SCFREQ01",
          "SCFRSP01",
          "SCNREQ01",
          "SCNRSP01",
          "AUDREQ01",
          "AUDRSP01",
          "ANMREQ01",
          "ANMRSP01",
          "ANLREQ01",
          "ANLRSP01",
          "VIDREQ01",
          "VIDRSP01",
          "MCTREQ01",
          "MCTRSP01",
          "MCSREQ01",
          "MCSRSP01",
          "MTRREQ01",
          "MTRRSP01",
          "MEDREQ01",
          "MEDRSP01",
          "LGSREQ01",
          "LGSRSP01",
          "USRREQ01",
          "USRRSP01",
          "UCRREQ01",
          "UCRRSP01",
          "UDTREQ01",
          "UDTRSP01",
          "USTREQ01",
          "USTRSP01",
          "URLREQ01",
          "URLRSP01",
          "UPWREQ01",
          "UPWRSP01",
          "ULKREQ01",
          "ULKRSP01",
          "QSBREQ01",
          "QSBRSP01",
          "NTSREQ01",
          "NTSRSP01",
          "NTDREQ01",
          "NTDRSP01",
          "NTCREQ01",
          "NTCRSP01",
          "QSSREQ01",
          "QSSRSP01",
          "QSDREQ01",
          "QSDRSP01",
          "QDLREQ01",
          "QDLRSP01",
          "QWKREQ01",
          "WLGEVT01");
  private static final List<String> ADDRESSES =
      List.of(
          "nk.sync.request",
          "nk.sync.reply.web",
          "nk.async.work",
          WEB_LOG_ADDRESS,
          "nk.dead.letter",
          "nk.expiry");
  private static final Map<String, Map<String, String>> FIXED =
      Map.ofEntries(
          Map.entry(POOL, Map.of(SERVICE_LABEL, API_SERVICE_VALUE, STATE_LABEL, ACTIVE_POOL_STATE)),
          Map.entry(ROWS, Map.of("store", API_SERVICE_VALUE, "status", "PENDING")),
          Map.entry(AGE, Map.of("store", API_SERVICE_VALUE, "status", "PENDING")),
          Map.entry("nk_async_jobs", Map.of(STATE_LABEL, "RECEIVED")),
          Map.entry(INBOX, Map.of(LAYOUT_LABEL, "LGNREQ01", "result", "0000")),
          Map.entry(OP, Map.of("operation", "UCRREQ01")),
          Map.entry(RED, Map.of(QUEUE_LABEL, "nk.web.log.q", "delivery_count", "2")),
          Map.entry(
              MQ,
              Map.of(
                  "direction",
                  "SEND",
                  ADDRESS_LABEL,
                  WEB_LOG_ADDRESS,
                  LAYOUT_LABEL,
                  "WLGEVT01",
                  OUTCOME_LABEL,
                  SUCCESS_OUTCOME)),
          Map.entry(
              DB, Map.of("query_id", "ASYNC_JOB_STATE_COUNTS", OUTCOME_LABEL, SUCCESS_OUTCOME)),
          Map.entry(
              MQD,
              Map.of("flow", "INTERNAL", LAYOUT_LABEL, "WLGEVT01", OUTCOME_LABEL, SUCCESS_OUTCOME)),
          Map.entry("nk_mq_queue_messages", Map.of(QUEUE_LABEL, "nk.web.log.q")),
          Map.entry("nk_mq_queue_bytes", Map.of(QUEUE_LABEL, "nk.web.log.q")),
          Map.entry("nk_mq_address_memory_bytes", Map.of(ADDRESS_LABEL, WEB_LOG_ADDRESS)),
          Map.entry("nk_mq_address_paged_bytes", Map.of(ADDRESS_LABEL, WEB_LOG_ADDRESS)),
          Map.entry("nk_mq_paging_active", Map.of(ADDRESS_LABEL, WEB_LOG_ADDRESS)),
          Map.entry("nk_mq_page_files", Map.of(ADDRESS_LABEL, WEB_LOG_ADDRESS)));

  private final ApiMetricCatalog catalog = new ApiMetricCatalog();

  private static Meter.Id raw(String name, List<Tag> tags) {
    return new Meter.Id("safe_fixture", Tags.empty(), "", "", Meter.Type.GAUGE) {
      public String getName() {
        return name;
      }

      public List<Tag> getTags() {
        return tags;
      }
    };
  }

  private static Meter.Id identity(String name, Map<String, String> values) {
    return raw(
        name, values.entrySet().stream().map(e -> Tag.of(e.getKey(), e.getValue())).toList());
  }

  private static void labels(Map<String, String> expected, Labels actual) {
    assertEquals(expected.size(), actual.size());
    expected.forEach((key, value) -> assertEquals(value, actual.get(key)));
  }

  private static final class MutableTag implements Tag {
    String key;
    String value;

    MutableTag(String key, String value) {
      this.key = key;
      this.value = value;
    }

    public String getKey() {
      return key;
    }

    public String getValue() {
      return value;
    }

    public int compareTo(Tag other) {
      return key.compareTo(other.getKey());
    }
  }

  @Test
  void apicat001ExactSixteenNamesTypesAndKeys() {
    var expectedGauges = new HashMap<String, Set<String>>();
    FIXED.forEach(
        (name, labels) -> {
          if (!Set.of(INBOX, OP, RED, MQ, DB, MQD).contains(name))
            expectedGauges.put(name, labels.keySet());
        });
    assertEquals(expectedGauges, catalog.gauges());
    assertEquals(
        Map.of(
            INBOX,
            Set.of(LAYOUT_LABEL, "result"),
            OP,
            Set.of("operation"),
            RED,
            Set.of(QUEUE_LABEL, "delivery_count"),
            MQ,
            Set.of("direction", ADDRESS_LABEL, LAYOUT_LABEL, OUTCOME_LABEL)),
        catalog.counters());
    assertEquals(
        Map.of(
            DB,
            Set.of("query_id", OUTCOME_LABEL),
            MQD,
            Set.of("flow", LAYOUT_LABEL, OUTCOME_LABEL)),
        catalog.summaries());
  }

  @Test
  void apicat002AllIndependent64LayoutsBy12Results() {
    assertEquals(64, LAYOUTS.size());
    assertEquals(64, Set.copyOf(LAYOUTS).size());
    int count = 0;
    for (String layout : LAYOUTS)
      for (String result :
          List.of(
              "0000", "0100", "0101", "0102", "0103", "0104", "0105", "0106", "0107", "0200",
              "9000", "9001")) {
        var expected = Map.of(LAYOUT_LABEL, layout, "result", result);
        labels(expected, catalog.labels(identity(INBOX, expected)));
        count++;
      }
    assertEquals(768, count);
  }

  @Test
  void apicat003IndependentOperationAndMqDomains() {
    for (String operation :
        List.of(
            "UCRREQ01",
            "USTREQ01",
            "URLREQ01",
            "UPWREQ01",
            "ULKREQ01",
            "QSBREQ01",
            "NTCREQ01",
            "QDLREQ01")) {
      var expected = Map.of("operation", operation);
      labels(expected, catalog.labels(identity(OP, expected)));
    }
    int count = 0;
    for (String address : ADDRESSES) {
      for (String delivery : List.of("2", "3", "4")) {
        var expected = Map.of(QUEUE_LABEL, address + ".q", "delivery_count", delivery);
        labels(expected, catalog.labels(identity(RED, expected)));
        count++;
      }
      for (String layout : LAYOUTS)
        for (String direction : List.of("SEND", "RECEIVE"))
          for (String outcome : List.of(SUCCESS_OUTCOME, "FAILURE", "ACK", "RETRY", "DLQ")) {
            var expected =
                Map.of(
                    ADDRESS_LABEL,
                    address,
                    LAYOUT_LABEL,
                    layout,
                    "direction",
                    direction,
                    OUTCOME_LABEL,
                    outcome);
            labels(expected, catalog.labels(identity(MQ, expected)));
          }
    }
    assertEquals(18, count);
  }

  @Test
  void apicat004AllFiftyOneGaugeTuples() {
    int count = 0;
    for (String state : List.of(ACTIVE_POOL_STATE, "idle", "pending", "max")) {
      var expected = Map.of(SERVICE_LABEL, API_SERVICE_VALUE, STATE_LABEL, state);
      labels(expected, catalog.labels(identity(POOL, expected)));
      count++;
    }
    for (String name : List.of(ROWS, AGE))
      for (String status : List.of("PENDING", "SENT", "ERROR")) {
        var expected = Map.of("store", API_SERVICE_VALUE, "status", status);
        labels(expected, catalog.labels(identity(name, expected)));
        count++;
      }
    for (String state : List.of("RECEIVED", "PROCESSING", "COMPLETED", "ERROR", "CANCELLED")) {
      var expected = Map.of(STATE_LABEL, state);
      labels(expected, catalog.labels(identity("nk_async_jobs", expected)));
      count++;
    }
    for (String address : ADDRESSES) {
      for (String name : List.of("nk_mq_queue_messages", "nk_mq_queue_bytes")) {
        var expected = Map.of(QUEUE_LABEL, address + ".q");
        labels(expected, catalog.labels(identity(name, expected)));
        count++;
      }
      for (String name :
          List.of(
              "nk_mq_address_memory_bytes",
              "nk_mq_address_paged_bytes",
              "nk_mq_paging_active",
              "nk_mq_page_files")) {
        var expected = Map.of(ADDRESS_LABEL, address);
        labels(expected, catalog.labels(identity(name, expected)));
        count++;
      }
    }
    assertEquals(51, count);
  }

  @Test
  void apicat005AllDurationLabelDomains() {
    for (String query : List.of("ASYNC_JOB_STATE_COUNTS", "OUTBOX_STATUS_COUNTS_OLDEST"))
      for (String outcome : List.of(SUCCESS_OUTCOME, "FAILURE")) {
        var expected = Map.of("query_id", query, OUTCOME_LABEL, outcome);
        labels(expected, catalog.labels(identity(DB, expected)));
      }
    for (String layout : LAYOUTS)
      for (String flow : List.of("SYNCHRONOUS", "ASYNC_ACCEPTANCE", "INTERNAL"))
        for (String outcome : List.of(SUCCESS_OUTCOME, "FAILURE")) {
          var expected = Map.of(LAYOUT_LABEL, layout, "flow", flow, OUTCOME_LABEL, outcome);
          labels(expected, catalog.labels(identity(MQD, expected)));
        }
  }

  @Test
  void apicat006UnknownNamesUseOnlyFixedDiagnostic() {
    for (String name :
        List.of(
            "nk_unknown_fixture_id",
            "nk_http_requests_total",
            "",
            "nk_db_pool_connections_extra")) {
      var failure =
          assertThrows(
              IllegalArgumentException.class, () -> catalog.labels(identity(name, Map.of())));
      assertEquals("unknown API metric", failure.getMessage());
    }
  }

  @Test
  void apicat007EveryFieldRejectsUnknownValueAndRawRoute() {
    FIXED.forEach(
        (name, values) ->
            values.forEach(
                (key, unused) -> {
                  var invalid = new HashMap<>(values);
                  invalid.put(key, "INVALID_FIXTURE_VALUE");
                  var failure =
                      assertThrows(
                          IllegalArgumentException.class,
                          () -> catalog.labels(identity(name, invalid)));
                  assertEquals("invalid API metric label", failure.getMessage());
                }));
  }

  @Test
  void apicat008EveryFamilyRejectsMissingAndExtraKeys() {
    FIXED.forEach(
        (name, values) -> {
          values.forEach(
              (key, unused) -> {
                var missing = new HashMap<>(values);
                missing.remove(key);
                assertThrows(
                    IllegalArgumentException.class, () -> catalog.labels(identity(name, missing)));
              });
          var extra = new HashMap<>(values);
          extra.put("actor", "UNAPPROVED_FIXTURE");
          assertThrows(IllegalArgumentException.class, () -> catalog.labels(identity(name, extra)));
        });
  }

  @Test
  void apicat009ActualDuplicateIdentityIsRejected() {
    var duplicateTags =
        List.of(
            Tag.of(SERVICE_LABEL, API_SERVICE_VALUE),
            Tag.of(SERVICE_LABEL, API_SERVICE_VALUE),
            Tag.of(STATE_LABEL, ACTIVE_POOL_STATE));
    var duplicateIdentity = raw(POOL, duplicateTags);
    assertSame(duplicateTags, duplicateIdentity.getTags());
    assertEquals(
        List.of(SERVICE_LABEL, SERVICE_LABEL, STATE_LABEL),
        duplicateIdentity.getTags().stream().map(Tag::getKey).toList());
    assertThrows(IllegalArgumentException.class, () -> catalog.labels(duplicateIdentity));
  }

  @Test
  void apicat010NullContractsFailWithoutNormalizingUnknown() {
    assertThrows(NullPointerException.class, () -> catalog.labels(null));
    assertThrows(NullPointerException.class, () -> catalog.labels(raw(null, List.of())));
    assertThrows(NullPointerException.class, () -> catalog.labels(raw(POOL, null)));
    var tags = new ArrayList<Tag>();
    tags.add(null);
    assertThrows(NullPointerException.class, () -> catalog.labels(raw(POOL, tags)));
    assertThrows(
        NullPointerException.class,
        () -> catalog.labels(raw(POOL, List.of(new MutableTag(null, API_SERVICE_VALUE)))));
    assertThrows(
        NullPointerException.class,
        () -> catalog.labels(raw(POOL, List.of(new MutableTag(SERVICE_LABEL, null)))));
  }

  @Test
  void apicat011CopyDetachedFromMutableProvider() {
    var mutable = new MutableTag(SERVICE_LABEL, API_SERVICE_VALUE);
    var tags = new ArrayList<Tag>();
    tags.add(mutable);
    tags.add(Tag.of(STATE_LABEL, ACTIVE_POOL_STATE));
    Labels result = catalog.labels(raw(POOL, tags));
    mutable.key = "actor";
    mutable.value = "INVALID_FIXTURE";
    tags.clear();
    labels(Map.of(SERVICE_LABEL, API_SERVICE_VALUE, STATE_LABEL, ACTIVE_POOL_STATE), result);
  }

  @Test
  void apicat012NamespacesAreDeepImmutableAndIndependent() {
    for (var space : List.of(catalog.gauges(), catalog.counters(), catalog.summaries())) {
      assertThrows(UnsupportedOperationException.class, () -> space.put("nk_unknown", Set.of()));
      for (var keys : space.values())
        assertThrows(UnsupportedOperationException.class, () -> keys.add("actor"));
    }
    assertEquals(10, catalog.gauges().size());
    assertEquals(4, catalog.counters().size());
    assertEquals(2, catalog.summaries().size());
    labels(FIXED.get(POOL), catalog.labels(identity(POOL, FIXED.get(POOL))));
  }

  @Test
  void apicat013ProviderFailuresKeepIdentity() {
    var failure = new IllegalStateException("fixture");
    var provider =
        new Meter.Id(POOL, Tags.empty(), "", "", Meter.Type.GAUGE) {
          public List<Tag> getTags() {
            throw failure;
          }
        };
    assertSame(failure, assertThrows(IllegalStateException.class, () -> catalog.labels(provider)));
    var fatal = new AssertionError("fixture");
    var fatalProvider =
        new Meter.Id(POOL, Tags.empty(), "", "", Meter.Type.GAUGE) {
          public List<Tag> getTags() {
            throw fatal;
          }
        };
    assertSame(fatal, assertThrows(AssertionError.class, () -> catalog.labels(fatalProvider)));
  }

  @Test
  void apicat014FiniteConcurrentCallsHaveNoRetainedMutableState() throws Exception {
    try (var workers = Executors.newFixedThreadPool(4)) {
      var jobs = new ArrayList<Future<?>>();
      for (int index = 0; index < 64; index++)
        jobs.add(
            workers.submit(
                () -> {
                  FIXED.forEach(
                      (name, expected) ->
                          labels(expected, catalog.labels(identity(name, expected))));
                  assertEquals(10, catalog.gauges().size());
                  assertEquals(4, catalog.counters().size());
                  assertEquals(2, catalog.summaries().size());
                }));
      for (var job : jobs) job.get(10, TimeUnit.SECONDS);
    }
  }
}
