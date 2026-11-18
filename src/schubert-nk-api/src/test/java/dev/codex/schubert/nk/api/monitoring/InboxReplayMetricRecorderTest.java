package dev.codex.schubert.nk.api.monitoring;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.protocol.header.ResultCode;
import dev.codex.schubert.nk.protocol.layout.LayoutId;
import dev.codex.schubert.nk.protocol.layout.UnsupportedLayoutException;
import io.micrometer.core.instrument.Counter;
import io.micrometer.core.instrument.Gauge;
import io.micrometer.core.instrument.Meter;
import io.micrometer.core.instrument.simple.SimpleMeterRegistry;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.Set;
import java.util.concurrent.Callable;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.stream.Collectors;
import org.junit.jupiter.api.Test;

/**
 * INBOXMET001..008/1691, independent SS323 rows/SS351 codes, own SDK only, no replay/DB/JMS/Root.
 */
class InboxReplayMetricRecorderTest {
  private static final int FAILURE_FACTORY_CALL = 2;
  private static final String LOGIN_REQUEST_LAYOUT = "LGNREQ01";
  private static final String SUBMIT_REQUEST_LAYOUT = "QSBREQ01";
  private static final String SUCCESS_CODE = "0000";
  private static final String IDEMPOTENT_CODE = "0200";
  private static final String INBOX_REPLAY_NAME = "nk_inbox_replays_total";
  private static final String LAYOUT_LABEL = "layout";
  private static final String RESULT_LABEL = "result";
  private static final String DEBUG_MODE = "DEBUG";
  // Independent oracle copied from SS323 table rows, not LayoutRegistry/Production method output.
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
          SUBMIT_REQUEST_LAYOUT,
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
          SUCCESS_CODE,
          "0100",
          "0101",
          "0102",
          "0103",
          "0104",
          "0105",
          "0106",
          "0107",
          IDEMPOTENT_CODE,
          "9000",
          "9001");

  private static final class Registry extends SimpleMeterRegistry implements AutoCloseable {
    final AtomicInteger registrations = new AtomicInteger();
    final AtomicInteger increments = new AtomicInteger();
    final AtomicInteger closes = new AtomicInteger();
    Optional<Throwable> registrationFailure = Optional.empty();
    Optional<Throwable> beforeIncrement = Optional.empty();
    Optional<Throwable> afterIncrement = Optional.empty();

    private static void fail(Optional<Throwable> supplied) {
      if (supplied.isPresent()) {
        var failure = supplied.orElseThrow();
        if (failure instanceof Error fatal) throw fatal;
        throw (RuntimeException) failure;
      }
    }

    @Override
    protected Counter newCounter(Meter.Id id) {
      if (registrations.incrementAndGet() == FAILURE_FACTORY_CALL) fail(registrationFailure);
      var actual = super.newCounter(id);
      return new Counter() {
        @Override
        public Meter.Id getId() {
          return actual.getId();
        }

        @Override
        public double count() {
          return actual.count();
        }

        @Override
        public void increment(double amount) {
          increments.incrementAndGet();
          fail(beforeIncrement);
          actual.increment(amount);
          fail(afterIncrement);
        }
      };
    }

    @Override
    public void close() {
      closes.incrementAndGet();
      super.close();
    }
  }

  private static double count(Registry registry, String layout, String result) {
    return registry
        .get(INBOX_REPLAY_NAME)
        .tag(LAYOUT_LABEL, layout)
        .tag(RESULT_LABEL, result)
        .counter()
        .count();
  }

  private static void shape(Registry registry) {
    assertEquals(64, LAYOUTS.size());
    assertEquals(12, RESULTS.size());
    assertEquals(768, registry.getMeters().size());
    var pairs = new java.util.HashSet<String>();
    for (var meter : registry.getMeters()) {
      assertEquals(INBOX_REPLAY_NAME, meter.getId().getName());
      assertEquals(Meter.Type.COUNTER, meter.getId().getType());
      assertEquals(
          Set.of(LAYOUT_LABEL, RESULT_LABEL),
          meter.getId().getTags().stream().map(t -> t.getKey()).collect(Collectors.toSet()));
      pairs.add(meter.getId().getTag(LAYOUT_LABEL) + ":" + meter.getId().getTag(RESULT_LABEL));
    }
    var expected = new java.util.HashSet<String>();
    for (String layout : LAYOUTS) for (String result : RESULTS) expected.add(layout + ":" + result);
    assertEquals(expected, pairs);
  }

  @Test
  void inboxMet001DebugRegistersOnlyAllApprovedLayoutResultPairsAtZero() {
    try (var registry = new Registry()) {
      var recorder = new InboxReplayMetricRecorder(registry, DEBUG_MODE);
      assertTrue(recorder.detailedMetricsRequested());
      shape(registry);
      for (String layout : LAYOUTS)
        for (String result : RESULTS) assertEquals(0, count(registry, layout, result));
      assertEquals(768, registry.registrations.get());
      assertEquals(0, registry.increments.get());
      assertEquals(0, registry.closes.get());
    }
  }

  @Test
  void inboxMet002EachSuppliedReplayIncrementsExactlyOnePairOnce() {
    try (var registry = new Registry()) {
      var recorder = new InboxReplayMetricRecorder(registry, DEBUG_MODE);
      for (String layout : LAYOUTS)
        for (String result : RESULTS)
          recorder.record(new LayoutId(layout), ResultCode.fromWire(result));
      for (String layout : LAYOUTS)
        for (String result : RESULTS) assertEquals(1, count(registry, layout, result));
      recorder.record(new LayoutId(SUBMIT_REQUEST_LAYOUT), ResultCode.IDEMPOTENT_SUCCESS);
      assertEquals(2, count(registry, SUBMIT_REQUEST_LAYOUT, IDEMPOTENT_CODE));
      assertEquals(769, registry.increments.get());
      shape(registry);
    }
  }

  @Test
  void inboxMet003StandardRegistersAndRecordsNoDetailedCounters() {
    try (var registry = new Registry()) {
      var recorder = new InboxReplayMetricRecorder(registry, "STANDARD");
      assertFalse(recorder.detailedMetricsRequested());
      for (String layout : LAYOUTS)
        for (String result : RESULTS)
          recorder.record(new LayoutId(layout), ResultCode.fromWire(result));
      assertEquals(0, registry.getMeters().size());
      assertEquals(0, registry.registrations.get());
      assertEquals(0, registry.increments.get());
      assertEquals(0, registry.closes.get());
    }
  }

  @Test
  void inboxMet004NullUnknownAndInvalidModeCannotCreateLabelsOrChangeCounters() {
    try (var registry = new Registry()) {
      assertThrows(
          NullPointerException.class, () -> new InboxReplayMetricRecorder(null, DEBUG_MODE));
      assertThrows(NullPointerException.class, () -> new InboxReplayMetricRecorder(registry, null));
      for (String mode : List.of("", "debug", "unknown-mode", "DEBTf", "STANDAQc"))
        assertEquals(
            "CONFIG_INVALID",
            assertThrows(
                    IllegalArgumentException.class,
                    () -> new InboxReplayMetricRecorder(registry, mode))
                .getMessage());
      assertEquals(0, registry.registrations.get());
    }
    for (String mode : List.of(DEBUG_MODE, "STANDARD")) {
      try (var registry = new Registry()) {
        var recorder = new InboxReplayMetricRecorder(registry, mode);
        assertThrows(NullPointerException.class, () -> recorder.record(null, ResultCode.SUCCESS));
        assertThrows(
            NullPointerException.class,
            () -> recorder.record(new LayoutId(LOGIN_REQUEST_LAYOUT), null));
        assertThrows(
            UnsupportedLayoutException.class,
            () -> recorder.record(new LayoutId("UNKNOWN1"), ResultCode.SUCCESS));
        assertEquals(0, registry.increments.get());
        if (mode.equals(DEBUG_MODE)) {
          shape(registry);
          assertEquals(0, count(registry, LOGIN_REQUEST_LAYOUT, SUCCESS_CODE));
        } else assertEquals(0, registry.getMeters().size());
      }
    }
  }

  private static final class UnformattableFailure extends IllegalStateException {
    private static final long serialVersionUID = 1L;

    @Override
    public String getMessage() {
      throw new AssertionError("no provider failure text access");
    }

    @Override
    public String toString() {
      throw new AssertionError("no provider failure formatting");
    }
  }

  @Test
  void inboxMet005PartialFactoryFailurePreservesExactProblemAndCallerRegistry() {
    for (var failure :
        List.<Throwable>of(
            new UnformattableFailure(), new AssertionError("owned provider fixture"))) {
      var registry = new Registry();
      try {
        registry.registrationFailure = Optional.of(failure);
        assertSame(
            failure,
            assertThrows(
                failure.getClass(), () -> new InboxReplayMetricRecorder(registry, DEBUG_MODE)));
        assertEquals(2, registry.registrations.get());
        assertEquals(1, registry.getMeters().size());
        assertEquals(0, registry.closes.get());
        assertEquals(0, registry.increments.get());
        assertEquals(0, count(registry, LOGIN_REQUEST_LAYOUT, SUCCESS_CODE));
      } finally {
        registry.close();
      }
      assertEquals(1, registry.closes.get());
    }
  }

  @Test
  void inboxMet006IncrementFailuresAreNotRetriedCompensatedOrFormatted() {
    for (boolean after : List.of(false, true)) {
      for (var failure :
          List.<Throwable>of(
              new UnformattableFailure(), new AssertionError("owned increment fixture"))) {
        try (var registry = new Registry()) {
          var recorder = new InboxReplayMetricRecorder(registry, DEBUG_MODE);
          if (after) registry.afterIncrement = Optional.of(failure);
          else registry.beforeIncrement = Optional.of(failure);
          assertSame(
              failure,
              assertThrows(
                  failure.getClass(),
                  () -> recorder.record(new LayoutId(LOGIN_REQUEST_LAYOUT), ResultCode.SUCCESS)));
          assertEquals(1, registry.increments.get());
          assertEquals(after ? 1 : 0, count(registry, LOGIN_REQUEST_LAYOUT, SUCCESS_CODE));
          assertEquals(768, registry.getMeters().size());
          assertEquals(0, registry.closes.get());
        }
      }
    }
  }

  @Test
  void inboxMet007ConcurrentSuppliedEventsKeepExactCountsAndSeparateOwners() throws Exception {
    try (var registry = new Registry();
        var other = new Registry()) {
      var recorder = new InboxReplayMetricRecorder(registry, DEBUG_MODE);
      var second = new InboxReplayMetricRecorder(other, DEBUG_MODE);
      second.record(new LayoutId(LOGIN_REQUEST_LAYOUT), ResultCode.SUCCESS);
      var tasks = new ArrayList<Callable<String>>();
      for (int i = 0; i < 64; i++)
        tasks.add(
            () -> {
              recorder.record(new LayoutId(SUBMIT_REQUEST_LAYOUT), ResultCode.IDEMPOTENT_SUCCESS);
              return "recorded";
            });
      var pool = Executors.newFixedThreadPool(8);
      try {
        for (var result : pool.invokeAll(tasks, 10, TimeUnit.SECONDS))
          assertEquals("recorded", result.get());
      } finally {
        pool.shutdownNow();
        assertTrue(pool.awaitTermination(10, TimeUnit.SECONDS));
      }
      assertEquals(64, count(registry, SUBMIT_REQUEST_LAYOUT, IDEMPOTENT_CODE));
      assertEquals(0, count(registry, LOGIN_REQUEST_LAYOUT, SUCCESS_CODE));
      assertEquals(1, count(other, LOGIN_REQUEST_LAYOUT, SUCCESS_CODE));
      assertEquals(0, count(other, SUBMIT_REQUEST_LAYOUT, IDEMPOTENT_CODE));
      assertEquals(64, registry.increments.get());
      assertEquals(1, other.increments.get());
      shape(registry);
      shape(other);
    }
  }

  @Test
  void inboxMet008ForeignNamespaceTypeCollisionCannotReplaceOrCloseCallerMeter() {
    try (var registry = new Registry()) {
      var foreign =
          Gauge.builder(INBOX_REPLAY_NAME, () -> 7d)
              .tag(LAYOUT_LABEL, LOGIN_REQUEST_LAYOUT)
              .tag(RESULT_LABEL, SUCCESS_CODE)
              .register(registry);
      assertThrows(
          IllegalArgumentException.class,
          () -> new InboxReplayMetricRecorder(registry, DEBUG_MODE));
      assertEquals(1, registry.getMeters().size());
      assertSame(
          foreign,
          registry
              .get(INBOX_REPLAY_NAME)
              .tag(LAYOUT_LABEL, LOGIN_REQUEST_LAYOUT)
              .tag(RESULT_LABEL, SUCCESS_CODE)
              .gauge());
      assertEquals(7, foreign.value());
      assertEquals(0, registry.increments.get());
      assertEquals(0, registry.closes.get());
      Gauge.builder("owned_fixture", () -> 1d).register(registry);
      assertEquals(2, registry.getMeters().size());
    }
  }
}
