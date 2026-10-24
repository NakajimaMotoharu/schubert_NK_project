package dev.codex.schubert.nk.api.monitoring;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.api.monitoring.PrometheusGaugeTextFixture.Key;
import dev.codex.schubert.nk.protocol.header.ResultCode;
import dev.codex.schubert.nk.protocol.layout.LayoutId;
import dev.codex.schubert.nk.protocol.transport.BrokerTopology;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Test;

/** APICNT001..008/1747: only supplied events, never actual replay, operation or delivery. */
class ApiPrometheusCounterContractTest {
  private static final String INBOX = "nk_inbox_replays_total";
  private static final String OP = "nk_operation_token_mismatch_total";
  private static final String REDEL = "nk_mq_redeliveries_total";
  private static final String MQ = "nk_mq_messages_total";
  private static final Map<String, String> TYPES =
      Map.of(INBOX, "counter", OP, "counter", REDEL, "counter", MQ, "counter");
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
  private static final List<String> RESULTS =
      List.of(
          "0000", "0100", "0101", "0102", "0103", "0104", "0105", "0106", "0107", "0200", "9000",
          "9001");
  private static final List<String> OPS =
      List.of(
          "UCRREQ01",
          "USTREQ01",
          "URLREQ01",
          "UPWREQ01",
          "ULKREQ01",
          "QSBREQ01",
          "NTCREQ01",
          "QDLREQ01");
  private static final List<String> ADDRESSES =
      List.of(
          "nk.sync.request",
          "nk.sync.reply.web",
          "nk.async.work",
          "nk.web.log",
          "nk.dead.letter",
          "nk.expiry");
  private static final List<String> STAGES =
      List.of(
          "SEND_SUCCESS",
          "SEND_FAILURE",
          "RECEIVE_SUCCESS",
          "RECEIVE_FAILURE",
          "ACK",
          "RETRY",
          "DLQ");
  private static final List<String> DIRECTIONS =
      List.of("SEND", "SEND", "RECEIVE", "RECEIVE", "RECEIVE", "RECEIVE", "SEND");
  private static final List<String> OUTCOMES =
      List.of("SUCCESS", "FAILURE", "SUCCESS", "FAILURE", "ACK", "RETRY", "DLQ");

  private static final class Bundle implements AutoCloseable {
    final PrometheusGaugeTextFixture registry = new PrometheusGaugeTextFixture();
    final InboxReplayMetricRecorder inbox;
    final OperationMismatchMetricRecorder operation;
    final MqRedeliveryMetricRecorder redelivery;
    final MqMessageMetricRecorder message;
    final boolean debug;

    Bundle(String mode) {
      debug = mode.equals("DEBUG");
      inbox = new InboxReplayMetricRecorder(registry, mode);
      operation = new OperationMismatchMetricRecorder(registry, mode);
      redelivery = new MqRedeliveryMetricRecorder(registry, mode);
      message =
          new MqMessageMetricRecorder(
              registry, mode, new LayoutId("WLGEVT01"), BrokerTopology.WEB_LOG);
    }

    Map<Key, Double> text() {
      var actual =
          registry.text(List.of(inbox, operation, redelivery, message), debug ? TYPES : Map.of());
      if (debug) assertEquals(keys(), actual.keySet());
      else assertTrue(actual.isEmpty());
      return actual;
    }

    @Override
    public void close() {
      registry.close();
    }
  }

  private static Key mqKey(int index) {
    return new Key(
        MQ,
        Map.of(
            "direction",
            DIRECTIONS.get(index),
            "address",
            "nk.web.log",
            "layout",
            "WLGEVT01",
            "outcome",
            OUTCOMES.get(index)));
  }

  private static Set<Key> keys() {
    var result = new HashSet<Key>();
    for (String layout : LAYOUTS)
      for (String code : RESULTS)
        result.add(new Key(INBOX, Map.of("layout", layout, "result", code)));
    for (String operation : OPS) result.add(new Key(OP, Map.of("operation", operation)));
    for (String address : ADDRESSES)
      for (String delivery : List.of("2", "3", "4"))
        result.add(new Key(REDEL, Map.of("queue", address + ".q", "delivery_count", delivery)));
    for (int n = 0; n < 7; n++) result.add(mqKey(n));
    return Set.copyOf(result);
  }

  private static double value(Map<Key, Double> actual, Key key) {
    var result = actual.get(key);
    assertNotNull(result);
    return result;
  }

  private static double sum(Map<Key, Double> actual, String name) {
    return actual.entrySet().stream()
        .filter(e -> e.getKey().name().equals(name))
        .mapToDouble(Map.Entry::getValue)
        .sum();
  }

  @Test
  void apicnt001AllFourCounterTypesAndEightHundredOneClosedSamplesStartZero() {
    try (var b = new Bundle("DEBUG")) {
      var actual = b.text();
      assertEquals(801, actual.size());
      assertTrue(actual.values().stream().allMatch(v -> v == 0));
      assertEquals(0, b.registry.closes.get());
    }
  }

  @Test
  void apicnt002EveryApprovedLayoutResultPairIncrementsOnlyItself() {
    try (var b = new Bundle("DEBUG")) {
      for (String layout : LAYOUTS)
        for (String result : RESULTS)
          b.inbox.record(new LayoutId(layout), ResultCode.fromWire(result));
      var actual = b.text();
      for (String layout : LAYOUTS)
        for (String result : RESULTS)
          assertEquals(
              1, value(actual, new Key(INBOX, Map.of("layout", layout, "result", result))));
      assertEquals(768, sum(actual, INBOX));
      assertEquals(0, sum(actual, OP));
      assertEquals(0, sum(actual, REDEL));
      assertEquals(0, sum(actual, MQ));
    }
  }

  @Test
  void apicnt003EightOperationsUseLiteralOneToEightVector() {
    try (var b = new Bundle("DEBUG")) {
      for (int n = 0; n < 8; n++)
        for (int k = 0; k <= n; k++)
          b.operation.record(OperationMismatchMetricRecorder.Operation.valueOf(OPS.get(n)));
      var actual = b.text();
      for (int n = 0; n < 8; n++)
        assertEquals(n + 1, value(actual, new Key(OP, Map.of("operation", OPS.get(n)))));
      assertEquals(36, sum(actual, OP));
      assertEquals(0, sum(actual, INBOX));
    }
  }

  @Test
  void apicnt004InitialDeliveryDoesNotCountAndAllEighteenRedeliveriesCountOnce() {
    try (var b = new Bundle("DEBUG")) {
      for (String address : ADDRESSES)
        b.redelivery.recordDelivery(BrokerTopology.requireAddress(address), 1);
      assertEquals(0, sum(b.text(), REDEL));
      for (String address : ADDRESSES)
        for (int delivery : List.of(2, 3, 4))
          b.redelivery.recordDelivery(BrokerTopology.requireAddress(address), delivery);
      var actual = b.text();
      for (String address : ADDRESSES)
        for (String delivery : List.of("2", "3", "4"))
          assertEquals(
              1,
              value(
                  actual,
                  new Key(REDEL, Map.of("queue", address + ".q", "delivery_count", delivery))));
      assertEquals(18, sum(actual, REDEL));
    }
  }

  @Test
  void apicnt005SevenStageTypesHaveExactCounterSuffixDirectionAndOutcome() {
    try (var b = new Bundle("DEBUG")) {
      for (int n = 0; n < 7; n++)
        for (int k = 0; k <= n; k++)
          b.message.record(MqMessageMetricRecorder.Stage.valueOf(STAGES.get(n)));
      var actual = b.text();
      for (int n = 0; n < 7; n++) assertEquals(n + 1, value(actual, mqKey(n)));
      assertEquals(28, sum(actual, MQ));
      assertEquals(0, sum(actual, OP));
    }
  }

  private static void event(Bundle b) {
    b.inbox.record(new LayoutId("WLGEVT01"), ResultCode.SUCCESS);
    b.operation.record(OperationMismatchMetricRecorder.Operation.QSBREQ01);
    b.redelivery.recordDelivery(BrokerTopology.WEB_LOG, 2);
    b.message.record(MqMessageMetricRecorder.Stage.ACK);
  }

  @Test
  void apicnt006StandardDoesNotRetainEmitOrCloseBorrowedRegistry() {
    try (var b = new Bundle("STANDARD")) {
      event(b);
      assertTrue(b.text().isEmpty());
      assertTrue(b.registry.getMeters().isEmpty());
      assertEquals(0, b.registry.closes.get());
    }
  }

  @Test
  void apicnt007FiniteOwnedWorkersKeepExactCountsAndSeparateOwners() throws Exception {
    try (var b = new Bundle("DEBUG");
        var other = new Bundle("DEBUG")) {
      var pool = Executors.newFixedThreadPool(4);
      try {
        var futures = new ArrayList<java.util.concurrent.Future<?>>();
        for (int n = 0; n < 64; n++) futures.add(pool.submit(() -> event(b)));
        for (var f : futures) f.get(5, TimeUnit.SECONDS);
        var actual = b.text();
        assertEquals(
            64, value(actual, new Key(INBOX, Map.of("layout", "WLGEVT01", "result", "0000"))));
        assertEquals(64, value(actual, new Key(OP, Map.of("operation", "QSBREQ01"))));
        assertEquals(
            64,
            value(actual, new Key(REDEL, Map.of("queue", "nk.web.log.q", "delivery_count", "2"))));
        assertEquals(64, value(actual, mqKey(4)));
        assertEquals(801, b.registry.getMeters().size());
        assertTrue(other.text().values().stream().allMatch(v -> v == 0));
      } finally {
        pool.shutdownNow();
        assertTrue(pool.awaitTermination(5, TimeUnit.SECONDS));
      }
    }
  }

  @Test
  void apicnt008OperationFactoriesStayClosedAndCallerOwnsLifetime() {
    var expected =
        List.of(
            OperationMismatchMetricRecorder.Operation.UCRREQ01,
            OperationMismatchMetricRecorder.Operation.USTREQ01,
            OperationMismatchMetricRecorder.Operation.URLREQ01,
            OperationMismatchMetricRecorder.Operation.UPWREQ01,
            OperationMismatchMetricRecorder.Operation.ULKREQ01,
            OperationMismatchMetricRecorder.Operation.QSBREQ01,
            OperationMismatchMetricRecorder.Operation.NTCREQ01,
            OperationMismatchMetricRecorder.Operation.QDLREQ01);
    for (int n = 0; n < 8; n++)
      assertEquals(expected.get(n), OperationMismatchMetricRecorder.Operation.valueOf(OPS.get(n)));
    assertThrows(
        NullPointerException.class, () -> OperationMismatchMetricRecorder.Operation.valueOf(null));
    assertThrows(
        IllegalArgumentException.class,
        () -> OperationMismatchMetricRecorder.Operation.valueOf("unknown"));
    var copy = OperationMismatchMetricRecorder.Operation.values();
    copy[0] = OperationMismatchMetricRecorder.Operation.QDLREQ01;
    assertEquals(
        OperationMismatchMetricRecorder.Operation.UCRREQ01,
        OperationMismatchMetricRecorder.Operation.values()[0]);
    try (var b = new Bundle("DEBUG")) {
      for (int n = 0; n < 1000; n++) event(b);
      assertEquals(1000, value(b.text(), mqKey(4)));
      assertEquals(801, b.text().size());
      assertEquals(0, b.registry.closes.get());
    }
  }
}
