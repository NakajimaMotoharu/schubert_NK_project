package dev.codex.schubert.nk.api.monitoring;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.api.monitoring.MqMessageMetricRecorder.Stage;
import dev.codex.schubert.nk.protocol.layout.LayoutId;
import dev.codex.schubert.nk.protocol.layout.UnsupportedLayoutException;
import dev.codex.schubert.nk.protocol.transport.BrokerTopology;
import io.micrometer.core.instrument.Counter;
import io.micrometer.core.instrument.Gauge;
import io.micrometer.core.instrument.Meter;
import io.micrometer.core.instrument.simple.SimpleMeterRegistry;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Optional;
import java.util.Set;
import java.util.concurrent.Callable;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.stream.Collectors;
import org.junit.jupiter.api.Test;

/** MQEVENT001..008/1718; literal SS321/323 catalog and owned SDK, never JMS operations. */
class MqMessageMetricRecorderTest {
  private static final int FAILURE_FACTORY_CALL = 2;
  private static final String LOGIN_REQUEST_LAYOUT = "LGNREQ01";
  private static final String QUESTION_WORK_LAYOUT = "QWKREQ01";
  private static final String SYNC_REQUEST_ADDRESS = "nk.sync.request";
  private static final String SEND_DIRECTION = "SEND";
  private static final String RECEIVE_DIRECTION = "RECEIVE";
  private static final String SUCCESS_OUTCOME = "SUCCESS";
  private static final String MQ_EVENT_NAME = "nk_mq_messages_total";
  private static final String DIRECTION_LABEL = "direction";
  private static final String ADDRESS_LABEL = "address";
  private static final String LAYOUT_LABEL = "layout";
  private static final String OUTCOME_LABEL = "outcome";
  private static final String DEBUG_MODE = "DEBUG";
  private static final List<String> LAYOUTS =
      List.of(
          LOGIN_REQUEST_LAYOUT,
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
          QUESTION_WORK_LAYOUT,
          "WLGEVT01");
  private static final List<String> ADDRESSES =
      List.of(
          SYNC_REQUEST_ADDRESS,
          "nk.sync.reply.web",
          "nk.async.work",
          "nk.web.log",
          "nk.dead.letter",
          "nk.expiry");
  private static final List<Stage> STAGES =
      List.of(
          Stage.SEND_SUCCESS,
          Stage.SEND_FAILURE,
          Stage.RECEIVE_SUCCESS,
          Stage.RECEIVE_FAILURE,
          Stage.ACK,
          Stage.RETRY,
          Stage.DLQ);
  private static final List<String> DIRECTIONS =
      List.of(
          SEND_DIRECTION,
          SEND_DIRECTION,
          RECEIVE_DIRECTION,
          RECEIVE_DIRECTION,
          RECEIVE_DIRECTION,
          RECEIVE_DIRECTION,
          SEND_DIRECTION);
  private static final List<String> OUTCOMES =
      List.of(SUCCESS_OUTCOME, "FAILURE", SUCCESS_OUTCOME, "FAILURE", "ACK", "RETRY", "DLQ");

  private static final class Registry extends SimpleMeterRegistry implements AutoCloseable {
    final AtomicInteger factories = new AtomicInteger();
    final AtomicInteger increments = new AtomicInteger();
    final AtomicInteger closes = new AtomicInteger();
    Optional<Throwable> factoryFailure = Optional.empty();
    Optional<Throwable> incrementFailure = Optional.empty();
    boolean after;

    @Override
    protected Counter newCounter(Meter.Id id) {
      if (factories.incrementAndGet() == FAILURE_FACTORY_CALL) fail(factoryFailure);
      var delegate = super.newCounter(id);
      return new Counter() {
        public Meter.Id getId() {
          return delegate.getId();
        }

        public double count() {
          return delegate.count();
        }

        public void increment(double amount) {
          increments.incrementAndGet();
          if (!after) fail(incrementFailure);
          delegate.increment(amount);
          if (after) fail(incrementFailure);
        }
      };
    }

    @Override
    public void close() {
      closes.incrementAndGet();
      super.close();
    }
  }

  private static final class Unformattable extends IllegalStateException {
    private static final long serialVersionUID = 1L;

    @Override
    public String getMessage() {
      throw new AssertionError("provider text forbidden");
    }

    @Override
    public String toString() {
      throw new AssertionError("provider formatting forbidden");
    }
  }

  private static void fail(Optional<Throwable> failure) {
    if (failure.isPresent()) {
      var problem = failure.orElseThrow();
      if (problem instanceof Error fatal) throw fatal;
      throw (RuntimeException) problem;
    }
  }

  private static Counter counter(Registry registry, String layout, String address, int stage) {
    return registry
        .get(MQ_EVENT_NAME)
        .tags(
            DIRECTION_LABEL,
            DIRECTIONS.get(stage),
            ADDRESS_LABEL,
            address,
            LAYOUT_LABEL,
            layout,
            OUTCOME_LABEL,
            OUTCOMES.get(stage))
        .counter();
  }

  @Test
  void mqEvent001EveryLiteralLayoutAddressAndSevenStageTupleHasOnlyApprovedLabels() {
    try (var registry = new Registry()) {
      var expected = new java.util.HashSet<String>();
      for (String layout : LAYOUTS)
        for (String address : ADDRESSES) {
          var recorder =
              new MqMessageMetricRecorder(
                  registry,
                  DEBUG_MODE,
                  new LayoutId(layout),
                  BrokerTopology.requireAddress(address));
          assertTrue(recorder.detailedMetricsRequested());
          for (int i = 0; i < 7; i++) {
            expected.add(layout + "/" + address + "/" + DIRECTIONS.get(i) + "/" + OUTCOMES.get(i));
            assertEquals(0, counter(registry, layout, address, i).count());
          }
        }
      assertEquals(2688, expected.size());
      assertEquals(2688, registry.getMeters().size());
      var actual = new java.util.HashSet<String>();
      for (var meter : registry.getMeters()) {
        var id = meter.getId();
        assertEquals(MQ_EVENT_NAME, id.getName());
        assertEquals(Meter.Type.COUNTER, id.getType());
        assertNull(id.getBaseUnit(), "fixed SS351 counter name must not gain a unit suffix");
        assertEquals(
            Set.of(DIRECTION_LABEL, ADDRESS_LABEL, LAYOUT_LABEL, OUTCOME_LABEL),
            id.getTags().stream().map(t -> t.getKey()).collect(Collectors.toSet()));
        assertTrue(
            actual.add(
                id.getTag(LAYOUT_LABEL)
                    + "/"
                    + id.getTag(ADDRESS_LABEL)
                    + "/"
                    + id.getTag(DIRECTION_LABEL)
                    + "/"
                    + id.getTag(OUTCOME_LABEL)));
      }
      assertEquals(expected, actual);
      assertEquals(2688, registry.factories.get());
      assertEquals(0, registry.increments.get());
      assertEquals(0, registry.closes.get());
    }
  }

  @Test
  void mqEvent002EachSuppliedStageIncrementsOnceAndOtherOwnersStayUnchanged() {
    try (var registry = new Registry()) {
      var active =
          new MqMessageMetricRecorder(
              registry,
              DEBUG_MODE,
              new LayoutId(LOGIN_REQUEST_LAYOUT),
              BrokerTopology.SYNC_REQUEST);
      new MqMessageMetricRecorder(
          registry, DEBUG_MODE, new LayoutId("LOGREQ01"), BrokerTopology.SYNC_REQUEST);
      new MqMessageMetricRecorder(
          registry, DEBUG_MODE, new LayoutId(LOGIN_REQUEST_LAYOUT), BrokerTopology.DEAD_LETTER);
      for (var stage : STAGES) active.record(stage);
      for (int i = 0; i < 3; i++) active.record(Stage.SEND_FAILURE);
      for (int i = 0; i < 7; i++) {
        assertEquals(
            i == 1 ? 4 : 1,
            counter(registry, LOGIN_REQUEST_LAYOUT, SYNC_REQUEST_ADDRESS, i).count());
        assertEquals(0, counter(registry, "LOGREQ01", SYNC_REQUEST_ADDRESS, i).count());
        assertEquals(0, counter(registry, LOGIN_REQUEST_LAYOUT, "nk.dead.letter", i).count());
      }
      assertEquals(10, registry.increments.get());
      assertEquals(0, registry.closes.get());
    }
  }

  @Test
  void mqEvent003SevenTypedStageMappingsAndGeneratedFactoriesRejectUnknownOrNull() {
    assertArrayEquals(
        new Stage[] {
          Stage.SEND_SUCCESS,
          Stage.SEND_FAILURE,
          Stage.RECEIVE_SUCCESS,
          Stage.RECEIVE_FAILURE,
          Stage.ACK,
          Stage.RETRY,
          Stage.DLQ
        },
        Stage.values());
    for (int i = 0; i < 7; i++) {
      var stage = STAGES.get(i);
      assertEquals(DIRECTIONS.get(i), stage.direction());
      assertEquals(OUTCOMES.get(i), stage.outcome());
      assertEquals(
          stage,
          Stage.parse(
              List.of(
                      "SEND_SUCCESS",
                      "SEND_FAILURE",
                      "RECEIVE_SUCCESS",
                      "RECEIVE_FAILURE",
                      "ACK",
                      "RETRY",
                      "DLQ")
                  .get(i)));
      assertEquals(
          stage,
          Stage.valueOf(
              List.of(
                      "SEND_SUCCESS",
                      "SEND_FAILURE",
                      "RECEIVE_SUCCESS",
                      "RECEIVE_FAILURE",
                      "ACK",
                      "RETRY",
                      "DLQ")
                  .get(i)));
    }
    var altered = Stage.values();
    altered[0] = Stage.DLQ;
    assertEquals(Stage.SEND_SUCCESS, Stage.values()[0]);
    assertThrows(NullPointerException.class, () -> Stage.parse(null));
    assertThrows(NullPointerException.class, () -> Stage.valueOf(null));
    for (String value : List.of("", "ack", "unknown", SEND_DIRECTION))
      assertThrows(IllegalArgumentException.class, () -> Stage.parse(value));
    assertThrows(IllegalArgumentException.class, () -> Stage.valueOf("unknown"));
  }

  @Test
  void mqEvent004NullUnknownLayoutAndModeNeverFallBackAndStandardStoresNoEvents() {
    try (var registry = new Registry()) {
      assertThrows(
          NullPointerException.class,
          () ->
              new MqMessageMetricRecorder(
                  null,
                  DEBUG_MODE,
                  new LayoutId(LOGIN_REQUEST_LAYOUT),
                  BrokerTopology.SYNC_REQUEST));
      assertThrows(
          NullPointerException.class,
          () ->
              new MqMessageMetricRecorder(
                  registry, null, new LayoutId(LOGIN_REQUEST_LAYOUT), BrokerTopology.SYNC_REQUEST));
      for (String mode : List.of(DEBUG_MODE, "STANDARD")) {
        assertThrows(
            NullPointerException.class,
            () -> new MqMessageMetricRecorder(registry, mode, null, BrokerTopology.SYNC_REQUEST));
        assertThrows(
            NullPointerException.class,
            () ->
                new MqMessageMetricRecorder(
                    registry, mode, new LayoutId(LOGIN_REQUEST_LAYOUT), null));
        assertThrows(
            UnsupportedLayoutException.class,
            () ->
                new MqMessageMetricRecorder(
                    registry, mode, new LayoutId("UNKNOWN1"), BrokerTopology.SYNC_REQUEST));
      }
      for (String mode : List.of("", "debug", "unknown"))
        assertEquals(
            "CONFIG_INVALID",
            assertThrows(
                    IllegalArgumentException.class,
                    () ->
                        new MqMessageMetricRecorder(
                            registry,
                            mode,
                            new LayoutId(LOGIN_REQUEST_LAYOUT),
                            BrokerTopology.SYNC_REQUEST))
                .getMessage());
      var standard =
          new MqMessageMetricRecorder(
              registry,
              "STANDARD",
              new LayoutId(LOGIN_REQUEST_LAYOUT),
              BrokerTopology.SYNC_REQUEST);
      assertFalse(standard.detailedMetricsRequested());
      for (var stage : STAGES) standard.record(stage);
      assertThrows(NullPointerException.class, () -> standard.record(null));
      assertEquals(0, registry.factories.get());
      assertEquals(0, registry.increments.get());
      assertEquals(0, registry.getMeters().size());
    }
    try (var registry = new Registry()) {
      var active =
          new MqMessageMetricRecorder(
              registry,
              DEBUG_MODE,
              new LayoutId(LOGIN_REQUEST_LAYOUT),
              BrokerTopology.SYNC_REQUEST);
      active.record(Stage.ACK);
      assertThrows(NullPointerException.class, () -> active.record(null));
      assertEquals(1, counter(registry, LOGIN_REQUEST_LAYOUT, SYNC_REQUEST_ADDRESS, 4).count());
      assertEquals(1, registry.increments.get());
    }
  }

  @Test
  void mqEvent005PartialFactoryFailureKeepsOriginalIdentityAndCallerRegistryOwnership() {
    for (var problem :
        List.<Throwable>of(new Unformattable(), new AssertionError("owned factory"))) {
      var registry = new Registry();
      registry.factoryFailure = Optional.of(problem);
      try {
        assertSame(
            problem,
            assertThrows(
                problem.getClass(),
                () ->
                    new MqMessageMetricRecorder(
                        registry,
                        DEBUG_MODE,
                        new LayoutId(LOGIN_REQUEST_LAYOUT),
                        BrokerTopology.SYNC_REQUEST)));
        assertEquals(2, registry.factories.get());
        assertEquals(1, registry.getMeters().size());
        assertEquals(0, counter(registry, LOGIN_REQUEST_LAYOUT, SYNC_REQUEST_ADDRESS, 0).count());
        assertEquals(0, registry.increments.get());
        assertEquals(0, registry.closes.get());
      } finally {
        registry.close();
      }
      assertEquals(1, registry.closes.get());
    }
  }

  @Test
  void mqEvent006IncrementFailureBeforeOrAfterEffectNeverRetriesCompensatesOrCloses() {
    for (var problem :
        List.<Throwable>of(new Unformattable(), new AssertionError("owned increment")))
      for (boolean after : List.of(false, true))
        try (var registry = new Registry()) {
          var active =
              new MqMessageMetricRecorder(
                  registry,
                  DEBUG_MODE,
                  new LayoutId(LOGIN_REQUEST_LAYOUT),
                  BrokerTopology.SYNC_REQUEST);
          registry.incrementFailure = Optional.of(problem);
          registry.after = after;
          assertSame(problem, assertThrows(problem.getClass(), () -> active.record(Stage.RETRY)));
          assertEquals(1, registry.increments.get());
          assertEquals(
              after ? 1 : 0,
              counter(registry, LOGIN_REQUEST_LAYOUT, SYNC_REQUEST_ADDRESS, 5).count());
          for (int i : List.of(0, 1, 2, 3, 4, 6))
            assertEquals(
                0, counter(registry, LOGIN_REQUEST_LAYOUT, SYNC_REQUEST_ADDRESS, i).count());
          assertEquals(0, registry.closes.get());
        }
  }

  @Test
  void mqEvent007ConcurrentCountsUsePrecomputedStageOwnerVectorsAndSeparateRegistry()
      throws Exception {
    try (var registry = new Registry();
        var other = new Registry();
        var executor = Executors.newFixedThreadPool(8)) {
      var a =
          new MqMessageMetricRecorder(
              registry, DEBUG_MODE, new LayoutId("QSBREQ01"), BrokerTopology.SYNC_REQUEST);
      var b =
          new MqMessageMetricRecorder(
              registry, DEBUG_MODE, new LayoutId(QUESTION_WORK_LAYOUT), BrokerTopology.ASYNC_WORK);
      var jobs = new ArrayList<Callable<Void>>();
      var expected = new HashMap<String, Long>();
      for (int i = 0; i < 64; i++) {
        boolean first = i % 2 == 0;
        var owner = first ? a : b;
        int index = i % 7;
        var stage = STAGES.get(index);
        String key = (first ? "A" : "B") + "/" + index;
        expected.merge(key, 1L, Long::sum);
        jobs.add(
            () -> {
              owner.record(stage);
              return null;
            });
      }
      for (var f : executor.invokeAll(jobs, 5, TimeUnit.SECONDS)) f.get(5, TimeUnit.SECONDS);
      for (int i = 0; i < 7; i++) {
        assertEquals(
            expected.get("A/" + i).longValue(),
            counter(registry, "QSBREQ01", SYNC_REQUEST_ADDRESS, i).count());
        assertEquals(
            expected.get("B/" + i).longValue(),
            counter(registry, QUESTION_WORK_LAYOUT, "nk.async.work", i).count());
      }
      var independent =
          new MqMessageMetricRecorder(
              other, DEBUG_MODE, new LayoutId(QUESTION_WORK_LAYOUT), BrokerTopology.ASYNC_WORK);
      independent.record(Stage.DLQ);
      assertEquals(1, counter(other, QUESTION_WORK_LAYOUT, "nk.async.work", 6).count());
      assertEquals(64, registry.increments.get());
    }
  }

  @Test
  void mqEvent008ForeignGaugeCannotBecomeCounterAndKeepsIdentityValueAndOwnership() {
    try (var registry = new Registry()) {
      var foreign =
          Gauge.builder(MQ_EVENT_NAME, () -> 7)
              .tags(
                  DIRECTION_LABEL,
                  SEND_DIRECTION,
                  ADDRESS_LABEL,
                  SYNC_REQUEST_ADDRESS,
                  LAYOUT_LABEL,
                  LOGIN_REQUEST_LAYOUT,
                  OUTCOME_LABEL,
                  SUCCESS_OUTCOME)
              .register(registry);
      assertThrows(
          IllegalArgumentException.class,
          () ->
              new MqMessageMetricRecorder(
                  registry,
                  DEBUG_MODE,
                  new LayoutId(LOGIN_REQUEST_LAYOUT),
                  BrokerTopology.SYNC_REQUEST));
      assertSame(
          foreign,
          registry
              .get(MQ_EVENT_NAME)
              .tags(
                  DIRECTION_LABEL,
                  SEND_DIRECTION,
                  ADDRESS_LABEL,
                  SYNC_REQUEST_ADDRESS,
                  LAYOUT_LABEL,
                  LOGIN_REQUEST_LAYOUT,
                  OUTCOME_LABEL,
                  SUCCESS_OUTCOME)
              .gauge());
      assertEquals(7, foreign.value());
      assertEquals(0, registry.closes.get());
    }
  }
}
