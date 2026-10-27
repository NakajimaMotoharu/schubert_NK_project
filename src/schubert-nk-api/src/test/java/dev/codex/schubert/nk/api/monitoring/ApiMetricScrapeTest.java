package dev.codex.schubert.nk.api.monitoring;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.protocol.header.ResultCode;
import dev.codex.schubert.nk.protocol.layout.LayoutId;
import dev.codex.schubert.nk.protocol.transport.BrokerTopology;
import io.micrometer.core.instrument.Meter;
import io.micrometer.core.instrument.MockClock;
import io.micrometer.core.instrument.Tag;
import io.micrometer.core.instrument.Tags;
import io.micrometer.core.instrument.distribution.CountAtBucket;
import io.micrometer.core.instrument.distribution.HistogramSnapshot;
import io.micrometer.core.instrument.distribution.ValueAtPercentile;
import io.micrometer.core.instrument.noop.NoopCounter;
import io.micrometer.core.instrument.noop.NoopDistributionSummary;
import io.micrometer.core.instrument.noop.NoopGauge;
import io.micrometer.core.instrument.simple.SimpleConfig;
import io.micrometer.core.instrument.simple.SimpleMeterRegistry;
import java.lang.ref.Reference;
import java.time.Duration;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicReference;
import org.junit.jupiter.api.Test;

/** APIPOL001..014/1773: literal domains and values, pure host memory, no business/IO authority. */
class ApiMetricScrapeTest {
  private static final int COUNTER_PROVIDER_KIND = 1;
  private static final String DEBUG_MODE = "DEBUG";
  private static final String LOGIN_LAYOUT = "LGNREQ01";
  private static final String TYPE_LINE_PREFIX = "# TYPE ";
  private static final String SERVICE_LABEL = "service";
  private static final String API_SERVICE = "API";
  private static final String STATE_LABEL = "state";
  private static final String ACTIVE_POOL_STATE = "active";
  private static final String LAYOUT_LABEL = "layout";
  private static final String RESULT_LABEL = "result";
  private static final String SUCCESS_RESULT = "0000";
  private static final String QUERY_ID_LABEL = "query_id";
  private static final String OUTCOME_LABEL = "outcome";
  private static final String SUCCESS_OUTCOME = "SUCCESS";
  private static final String STANDARD_MODE = "STANDARD";
  private static final String POOL = "nk_db_pool_connections";
  private static final String INBOX = "nk_inbox_replays_total";
  private static final String DB = "nk_db_query_duration_seconds";
  private static final String MQD = "nk_mq_processing_duration_seconds";
  private final ApiMetricScrape policy = new ApiMetricScrape();

  private static class Registry extends SimpleMeterRegistry implements AutoCloseable {
    final List<Meter> supplied;
    final AtomicInteger reads = new AtomicInteger();

    Registry(Meter... meters) {
      super(SimpleConfig.DEFAULT, new MockClock());
      supplied = List.of(meters);
    }

    public List<Meter> getMeters() {
      reads.incrementAndGet();
      return supplied;
    }

    public boolean isClosed() {
      reads.incrementAndGet();
      return super.isClosed();
    }
  }

  private static final class Compatible extends Registry implements ExactDurationSupport {
    Compatible(Meter... meters) {
      super(meters);
    }
  }

  private static final class Bundle implements AutoCloseable {
    final ExactDurationMeterRegistry registry =
        new ExactDurationMeterRegistry(SimpleConfig.DEFAULT, new MockClock());
    final OutboxRowsMetricRecorder rows = new OutboxRowsMetricRecorder(registry, DEBUG_MODE);
    final OutboxAgeMetricRecorder age = new OutboxAgeMetricRecorder(registry, DEBUG_MODE);
    final AsyncJobMetricRecorder jobs = new AsyncJobMetricRecorder(registry, DEBUG_MODE);
    final DbPoolMetricRecorder pool = new DbPoolMetricRecorder(registry, DEBUG_MODE);
    final MqPressureMetricRecorder pressure = new MqPressureMetricRecorder(registry, DEBUG_MODE);
    final InboxReplayMetricRecorder inbox = new InboxReplayMetricRecorder(registry, DEBUG_MODE);
    final OperationMismatchMetricRecorder operation =
        new OperationMismatchMetricRecorder(registry, DEBUG_MODE);
    final MqRedeliveryMetricRecorder redelivery =
        new MqRedeliveryMetricRecorder(registry, DEBUG_MODE);
    final MqMessageMetricRecorder messages =
        new MqMessageMetricRecorder(
            registry, DEBUG_MODE, new LayoutId("WLGEVT01"), BrokerTopology.WEB_LOG);
    final DbQueryDurationMetricRecorder db =
        new DbQueryDurationMetricRecorder(registry, DEBUG_MODE);
    final MqProcessingDurationMetricRecorder mq =
        new MqProcessingDurationMetricRecorder(registry, DEBUG_MODE, new LayoutId(LOGIN_LAYOUT));

    void supplied() {
      rows.record(new OutboxRowsMetricRecorder.Counts(3, 5, 2));
      age.record(
          new OutboxAgeMetricRecorder.Ages(Duration.ofMillis(3500), Duration.ZERO, Duration.ZERO));
      pool.record(new DbPoolMetricRecorder.Counts(3, 5, 2, 8));
      inbox.record(new LayoutId(LOGIN_LAYOUT), ResultCode.SUCCESS);
      db.record(
          DbQueryDurationMetricRecorder.Query.ASYNC_JOB_STATE_COUNTS,
          DbQueryDurationMetricRecorder.Outcome.SUCCESS,
          1);
      mq.record(MqProcessingDurationMetricRecorder.Outcome.SUCCESS, 1_500_000_000);
    }

    String text(ApiMetricScrape formatter, String mode) {
      try {
        return formatter.scrape(registry, mode);
      } finally {
        Reference.reachabilityFence(this);
      }
    }

    public void close() {
      registry.close();
    }
  }

  private static Meter.Id id(String name, Tags tags, Meter.Type type) {
    return new Meter.Id(name, tags, "", "", type);
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

  private static void catalog(String text) {
    assertEquals(16, text.lines().filter(line -> line.startsWith(TYPE_LINE_PREFIX)).count());
    assertEquals(
        10,
        text.lines()
            .filter(line -> line.startsWith(TYPE_LINE_PREFIX) && line.endsWith(" gauge"))
            .count());
    assertEquals(
        4,
        text.lines()
            .filter(line -> line.startsWith(TYPE_LINE_PREFIX) && line.endsWith(" counter"))
            .count());
    assertEquals(
        2,
        text.lines()
            .filter(line -> line.startsWith(TYPE_LINE_PREFIX) && line.endsWith(" histogram"))
            .count());
    assertEquals(900, text.lines().filter(line -> !line.startsWith("#")).count());
    assertFalse(text.contains("_total_total"));
    assertFalse(text.contains(".histogram"));
  }

  private static void supplied(String text) {
    catalog(text);
    assertEquals(
        3, value(text, POOL, Map.of(SERVICE_LABEL, API_SERVICE, STATE_LABEL, ACTIVE_POOL_STATE)));
    assertEquals(
        1, value(text, INBOX, Map.of(LAYOUT_LABEL, LOGIN_LAYOUT, RESULT_LABEL, SUCCESS_RESULT)));
    assertEquals(
        3.5,
        value(text, "nk_outbox_oldest_seconds", Map.of("store", API_SERVICE, "status", "PENDING")));
    var db = Map.of(QUERY_ID_LABEL, "ASYNC_JOB_STATE_COUNTS", OUTCOME_LABEL, SUCCESS_OUTCOME);
    assertEquals(1e-9, value(text, DB + "_sum", db));
    var mq =
        Map.of("flow", "SYNCHRONOUS", LAYOUT_LABEL, LOGIN_LAYOUT, OUTCOME_LABEL, SUCCESS_OUTCOME);
    assertEquals(1.5, value(text, MQD + "_sum", mq));
    for (String boundary : List.of("0.001", "0.01", "0.1", "1.0")) {
      assertEquals(
          0,
          value(
              text,
              MQD + "_bucket",
              Map.of(
                  "flow",
                  "SYNCHRONOUS",
                  LAYOUT_LABEL,
                  LOGIN_LAYOUT,
                  OUTCOME_LABEL,
                  SUCCESS_OUTCOME,
                  "le",
                  boundary)));
    }
    for (String boundary : List.of("1.5", "+Inf")) {
      assertEquals(
          1,
          value(
              text,
              MQD + "_bucket",
              Map.of(
                  "flow",
                  "SYNCHRONOUS",
                  LAYOUT_LABEL,
                  LOGIN_LAYOUT,
                  OUTCOME_LABEL,
                  SUCCESS_OUTCOME,
                  "le",
                  boundary)));
    }
  }

  @Test
  void apipol001StandardReadsNoDetailedSourceOrValues() {
    var values = new AtomicInteger();
    var meter =
        new NoopGauge(
            id(
                POOL,
                Tags.of(SERVICE_LABEL, "INVALID", STATE_LABEL, ACTIVE_POOL_STATE),
                Meter.Type.GAUGE)) {
          public double value() {
            values.incrementAndGet();
            throw new AssertionError("not read");
          }
        };
    try (var source = new Registry(meter)) {
      source.reads.set(0);
      assertEquals("", policy.scrape(source, STANDARD_MODE));
      assertEquals(0, source.reads.get());
      assertEquals(0, values.get());
      assertFalse(source.isClosed());
    }
  }

  @Test
  void apipol002RealInitialSixteenFamiliesAndNineHundredSamples() {
    try (var b = new Bundle()) {
      String result = b.text(policy, DEBUG_MODE);
      catalog(result);
      assertEquals(51, result.lines().filter(line -> line.endsWith("} NaN")).count());
      assertEquals(
          0,
          value(result, INBOX, Map.of(LAYOUT_LABEL, LOGIN_LAYOUT, RESULT_LABEL, SUCCESS_RESULT)));
      assertFalse(b.registry.isClosed());
    }
  }

  @Test
  void apipol003IndependentSuppliedValuesAndCumulativeBoundary() {
    try (var b = new Bundle()) {
      b.supplied();
      supplied(b.text(policy, DEBUG_MODE));
      assertFalse(b.registry.isClosed());
    }
  }

  @Test
  void apipol004PureModeSwitchDoesNotResetOrClose() {
    try (var b = new Bundle()) {
      b.supplied();
      supplied(b.text(policy, DEBUG_MODE));
      assertEquals("", b.text(policy, STANDARD_MODE));
      supplied(b.text(policy, DEBUG_MODE));
    }
  }

  @Test
  void apipol005EmptyCompatibleRegistryDoesNotFabricateUnknown() {
    try (var source = new ExactDurationMeterRegistry(SimpleConfig.DEFAULT, new MockClock())) {
      assertEquals("", policy.scrape(source, DEBUG_MODE));
      assertFalse(source.isClosed());
    }
  }

  @Test
  void apipol006UnsupportedSourceRejectedBeforeRead() {
    try (var source = new Registry()) {
      source.reads.set(0);
      assertEquals(
          "CONFIG_INVALID",
          assertThrows(IllegalArgumentException.class, () -> policy.scrape(source, DEBUG_MODE))
              .getMessage());
      assertEquals(0, source.reads.get());
    }
  }

  @Test
  void apipol007NullAndUnknownModesNeverReadSource() {
    assertThrows(NullPointerException.class, () -> policy.scrape(null, STANDARD_MODE));
    try (var source = new Registry()) {
      source.reads.set(0);
      assertThrows(NullPointerException.class, () -> policy.scrape(source, null));
      for (String mode : List.of("", "debug", "DEBUG ", "UNKNOWN"))
        assertEquals(
            "CONFIG_INVALID",
            assertThrows(IllegalArgumentException.class, () -> policy.scrape(source, mode))
                .getMessage());
      assertEquals(0, source.reads.get());
    }
  }

  @Test
  void apipol008ClosedSourceNotReopenedOrReadByStandard() {
    var source = new Compatible();
    source.close();
    source.reads.set(0);
    assertEquals("", policy.scrape(source, STANDARD_MODE));
    assertEquals(0, source.reads.get());
    assertThrows(IllegalStateException.class, () -> policy.scrape(source, DEBUG_MODE));
    assertTrue(source.isClosed());
  }

  @Test
  void apipol009ProviderRuntimeAndErrorKeepIdentity() {
    var failure = new IllegalStateException("fixture");
    var broken =
        new Meter.Id(POOL, Tags.empty(), "", "", Meter.Type.GAUGE) {
          public List<Tag> getTags() {
            throw failure;
          }
        };
    try (var source = new Compatible(new NoopGauge(broken))) {
      assertSame(
          failure,
          assertThrows(IllegalStateException.class, () -> policy.scrape(source, DEBUG_MODE)));
      assertFalse(source.isClosed());
    }
    var fatal = new AssertionError("fixture");
    var bad =
        new Meter.Id(POOL, Tags.empty(), "", "", Meter.Type.GAUGE) {
          public List<Tag> getTags() {
            throw fatal;
          }
        };
    try (var source = new Compatible(new NoopGauge(bad))) {
      assertSame(
          fatal, assertThrows(AssertionError.class, () -> policy.scrape(source, DEBUG_MODE)));
      assertFalse(source.isClosed());
    }
  }

  @Test
  void apipol010LaterFailureNeverReturnsPartialText() {
    var reads = new AtomicInteger();
    var first =
        new NoopGauge(
            id(
                POOL,
                Tags.of(SERVICE_LABEL, API_SERVICE, STATE_LABEL, ACTIVE_POOL_STATE),
                Meter.Type.GAUGE)) {
          public double value() {
            reads.incrementAndGet();
            return 3;
          }
        };
    var later =
        new NoopCounter(
            id(
                INBOX,
                Tags.of(LAYOUT_LABEL, "UNAPPROVED", RESULT_LABEL, SUCCESS_RESULT),
                Meter.Type.COUNTER));
    var returned = new AtomicReference<Optional<String>>(Optional.empty());
    try (var source = new Compatible(first, later)) {
      assertThrows(
          IllegalArgumentException.class,
          () -> returned.set(Optional.of(policy.scrape(source, DEBUG_MODE))));
      assertEquals(1, reads.get());
      assertTrue(returned.get().isEmpty());
      assertFalse(source.isClosed());
    }
  }

  @Test
  void apipol011UnknownProvidersIgnored() {
    var reads = new AtomicInteger();
    var unknown =
        new NoopGauge(id("nk_unknown_fixture", Tags.of("actor", "INVALID"), Meter.Type.GAUGE)) {
          public double value() {
            reads.incrementAndGet();
            throw new AssertionError("not read");
          }
        };
    try (var source = new Compatible(unknown)) {
      assertEquals("", policy.scrape(source, DEBUG_MODE));
      assertEquals(0, reads.get());
    }
  }

  @Test
  void apipol012FiniteConcurrentCallsKeepSource() {
    try (var b = new Bundle();
        var workers = Executors.newFixedThreadPool(4)) {
      b.supplied();
      var jobs = new ArrayList<Future<?>>();
      for (int i = 0; i < 64; i++)
        jobs.add(workers.submit(() -> supplied(b.text(policy, DEBUG_MODE))));
      for (var job : jobs) assertDoesNotThrow(() -> job.get(10, TimeUnit.SECONDS));
      assertFalse(b.registry.isClosed());
    }
  }

  @Test
  void apipol013AllThreeCodecsRejectPoisonedLabelsAndPolicyRecovers() {
    var gauge =
        new NoopGauge(
            id(
                POOL,
                Tags.of(SERVICE_LABEL, "WEB", STATE_LABEL, ACTIVE_POOL_STATE),
                Meter.Type.GAUGE));
    var counter =
        new NoopCounter(
            id(
                INBOX,
                Tags.of(LAYOUT_LABEL, LOGIN_LAYOUT, RESULT_LABEL, "9999"),
                Meter.Type.COUNTER));
    var summary =
        new NoopDistributionSummary(
            id(
                DB,
                Tags.of(QUERY_ID_LABEL, "RAW SQL", OUTCOME_LABEL, SUCCESS_OUTCOME),
                Meter.Type.DISTRIBUTION_SUMMARY));
    for (Meter bad : List.of(gauge, counter, summary)) {
      try (var source = new Compatible(bad)) {
        assertEquals(
            "invalid API metric label",
            assertThrows(IllegalArgumentException.class, () -> policy.scrape(source, DEBUG_MODE))
                .getMessage());
      }
    }
    try (var first = new Bundle();
        var other = new Bundle()) {
      first.supplied();
      supplied(first.text(policy, DEBUG_MODE));
      assertEquals(
          0,
          value(
              other.text(policy, DEBUG_MODE),
              INBOX,
              Map.of(LAYOUT_LABEL, LOGIN_LAYOUT, RESULT_LABEL, SUCCESS_RESULT)));
      assertEquals(
          51,
          other.text(policy, DEBUG_MODE).lines().filter(line -> line.endsWith("} NaN")).count());
      assertFalse(first.registry.isClosed());
      assertFalse(other.registry.isClosed());
    }
  }

  @Test
  void apipol014NameLabelsAndValueCapturedOnceInSameApprovedModel() {
    for (int kind = 0; kind < 3; kind++) {
      final int selected = kind;
      String name = kind == 0 ? POOL : kind == 1 ? INBOX : DB;
      var tags =
          new ArrayList<Tag>(
              kind == 0
                  ? List.of(
                      Tag.of(SERVICE_LABEL, API_SERVICE), Tag.of(STATE_LABEL, ACTIVE_POOL_STATE))
                  : kind == 1
                      ? List.of(
                          Tag.of(LAYOUT_LABEL, LOGIN_LAYOUT), Tag.of(RESULT_LABEL, SUCCESS_RESULT))
                      : List.of(
                          Tag.of(QUERY_ID_LABEL, "ASYNC_JOB_STATE_COUNTS"),
                          Tag.of(OUTCOME_LABEL, SUCCESS_OUTCOME)));
      var nameReads = new AtomicInteger();
      var tagReads = new AtomicInteger();
      var valueReads = new AtomicInteger();
      var identity =
          new Meter.Id(
              "safe_fixture",
              Tags.empty(),
              "",
              "",
              kind == 0
                  ? Meter.Type.GAUGE
                  : kind == 1 ? Meter.Type.COUNTER : Meter.Type.DISTRIBUTION_SUMMARY) {
            public String getName() {
              return nameReads.incrementAndGet() == 1 ? name : "nk_unknown_after_capture";
            }

            public List<Tag> getTags() {
              tagReads.incrementAndGet();
              return tags;
            }
          };
      Runnable mutate =
          () -> {
            valueReads.incrementAndGet();
            tags.clear();
            tags.add(Tag.of("actor", "UNAPPROVED"));
          };
      Meter meter;
      if (kind == 0)
        meter =
            new NoopGauge(identity) {
              public double value() {
                mutate.run();
                return 3;
              }
            };
      else if (kind == COUNTER_PROVIDER_KIND)
        meter =
            new NoopCounter(identity) {
              public double count() {
                mutate.run();
                return 2;
              }
            };
      else
        meter =
            new NoopDistributionSummary(identity) {
              public HistogramSnapshot takeSnapshot() {
                mutate.run();
                return new HistogramSnapshot(
                    1,
                    .1,
                    .1,
                    new ValueAtPercentile[0],
                    new CountAtBucket[] {new CountAtBucket(.1, 1)},
                    null);
              }
            };
      try (var source = new Compatible(meter)) {
        String result =
            selected == 0
                ? new ApiScalarMetricExporter().scrapeApprovedGauges(source)
                : selected == 1
                    ? new ApiScalarMetricExporter().scrapeApprovedCounters(source)
                    : new ApiDurationMetricExporter().scrapeApproved(source);
        assertTrue(result.contains(TYPE_LINE_PREFIX + name + " "));
        assertFalse(result.contains("UNAPPROVED"));
        assertFalse(result.contains("nk_unknown_after_capture"));
        assertEquals(1, nameReads.get());
        assertEquals(1, tagReads.get());
        assertEquals(1, valueReads.get());
        if (kind == 0)
          assertEquals(
              3,
              value(
                  result,
                  POOL,
                  Map.of(SERVICE_LABEL, API_SERVICE, STATE_LABEL, ACTIVE_POOL_STATE)));
        else if (kind == COUNTER_PROVIDER_KIND)
          assertEquals(
              2,
              value(
                  result, INBOX, Map.of(LAYOUT_LABEL, LOGIN_LAYOUT, RESULT_LABEL, SUCCESS_RESULT)));
        else
          assertEquals(
              .1,
              value(
                  result,
                  DB + "_sum",
                  Map.of(
                      QUERY_ID_LABEL, "ASYNC_JOB_STATE_COUNTS", OUTCOME_LABEL, SUCCESS_OUTCOME)));
        assertFalse(source.isClosed());
      }
    }
  }
}
