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
import java.util.concurrent.atomic.AtomicInteger;
import java.util.stream.Collectors;
import org.junit.jupiter.api.Test;

/**
 * INBOXMET001..008/1691, independent SS323 rows/SS351 codes, own SDK only, no replay/DB/JMS/Root.
 */
class InboxReplayMetricRecorderTest {
  // Independent oracle copied from SS323 table rows, not LayoutRegistry/Production method output.
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
      if (registrations.incrementAndGet() == 2) fail(registrationFailure);
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
        .get("nk_inbox_replays_total")
        .tag("layout", layout)
        .tag("result", result)
        .counter()
        .count();
  }

  private static void shape(Registry registry) {
    assertEquals(64, LAYOUTS.size());
    assertEquals(12, RESULTS.size());
    assertEquals(768, registry.getMeters().size());
    var pairs = new java.util.HashSet<String>();
    for (var meter : registry.getMeters()) {
      assertEquals("nk_inbox_replays_total", meter.getId().getName());
      assertEquals(Meter.Type.COUNTER, meter.getId().getType());
      assertEquals(
          Set.of("layout", "result"),
          meter.getId().getTags().stream().map(t -> t.getKey()).collect(Collectors.toSet()));
      pairs.add(meter.getId().getTag("layout") + ":" + meter.getId().getTag("result"));
    }
    var expected = new java.util.HashSet<String>();
    for (String layout : LAYOUTS) for (String result : RESULTS) expected.add(layout + ":" + result);
    assertEquals(expected, pairs);
  }

  @Test
  void inboxMet001DebugRegistersOnlyAllApprovedLayoutResultPairsAtZero() {
    try (var registry = new Registry()) {
      var recorder = new InboxReplayMetricRecorder(registry, "DEBUG");
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
      var recorder = new InboxReplayMetricRecorder(registry, "DEBUG");
      for (String layout : LAYOUTS)
        for (String result : RESULTS)
          recorder.record(new LayoutId(layout), ResultCode.fromWire(result));
      for (String layout : LAYOUTS)
        for (String result : RESULTS) assertEquals(1, count(registry, layout, result));
      recorder.record(new LayoutId("QSBREQ01"), ResultCode.IDEMPOTENT_SUCCESS);
      assertEquals(2, count(registry, "QSBREQ01", "0200"));
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
      assertThrows(NullPointerException.class, () -> new InboxReplayMetricRecorder(null, "DEBUG"));
      assertThrows(NullPointerException.class, () -> new InboxReplayMetricRecorder(registry, null));
      for (String mode : List.of("", "debug", "unknown-mode"))
        assertEquals(
            "CONFIG_INVALID",
            assertThrows(
                    IllegalArgumentException.class,
                    () -> new InboxReplayMetricRecorder(registry, mode))
                .getMessage());
      assertEquals(0, registry.registrations.get());
    }
    for (String mode : List.of("DEBUG", "STANDARD")) {
      try (var registry = new Registry()) {
        var recorder = new InboxReplayMetricRecorder(registry, mode);
        assertThrows(NullPointerException.class, () -> recorder.record(null, ResultCode.SUCCESS));
        assertThrows(
            NullPointerException.class, () -> recorder.record(new LayoutId("LGNREQ01"), null));
        assertThrows(
            UnsupportedLayoutException.class,
            () -> recorder.record(new LayoutId("UNKNOWN1"), ResultCode.SUCCESS));
        assertEquals(0, registry.increments.get());
        if (mode.equals("DEBUG")) {
          shape(registry);
          assertEquals(0, count(registry, "LGNREQ01", "0000"));
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
                failure.getClass(), () -> new InboxReplayMetricRecorder(registry, "DEBUG")));
        assertEquals(2, registry.registrations.get());
        assertEquals(1, registry.getMeters().size());
        assertEquals(0, registry.closes.get());
        assertEquals(0, registry.increments.get());
        assertEquals(0, count(registry, "LGNREQ01", "0000"));
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
          var recorder = new InboxReplayMetricRecorder(registry, "DEBUG");
          if (after) registry.afterIncrement = Optional.of(failure);
          else registry.beforeIncrement = Optional.of(failure);
          assertSame(
              failure,
              assertThrows(
                  failure.getClass(),
                  () -> recorder.record(new LayoutId("LGNREQ01"), ResultCode.SUCCESS)));
          assertEquals(1, registry.increments.get());
          assertEquals(after ? 1 : 0, count(registry, "LGNREQ01", "0000"));
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
      var recorder = new InboxReplayMetricRecorder(registry, "DEBUG");
      var second = new InboxReplayMetricRecorder(other, "DEBUG");
      second.record(new LayoutId("LGNREQ01"), ResultCode.SUCCESS);
      var tasks = new ArrayList<Callable<String>>();
      for (int i = 0; i < 64; i++)
        tasks.add(
            () -> {
              recorder.record(new LayoutId("QSBREQ01"), ResultCode.IDEMPOTENT_SUCCESS);
              return "recorded";
            });
      try (var pool = Executors.newFixedThreadPool(8)) {
        for (var result : pool.invokeAll(tasks)) assertEquals("recorded", result.get());
      }
      assertEquals(64, count(registry, "QSBREQ01", "0200"));
      assertEquals(0, count(registry, "LGNREQ01", "0000"));
      assertEquals(1, count(other, "LGNREQ01", "0000"));
      assertEquals(0, count(other, "QSBREQ01", "0200"));
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
          Gauge.builder("nk_inbox_replays_total", () -> 7d)
              .tag("layout", "LGNREQ01")
              .tag("result", "0000")
              .register(registry);
      assertThrows(
          IllegalArgumentException.class, () -> new InboxReplayMetricRecorder(registry, "DEBUG"));
      assertEquals(1, registry.getMeters().size());
      assertSame(
          foreign,
          registry
              .get("nk_inbox_replays_total")
              .tag("layout", "LGNREQ01")
              .tag("result", "0000")
              .gauge());
      assertEquals(7, foreign.value());
      assertEquals(0, registry.increments.get());
      assertEquals(0, registry.closes.get());
      Gauge.builder("owned_fixture", () -> 1d).register(registry);
      assertEquals(2, registry.getMeters().size());
    }
  }
}
