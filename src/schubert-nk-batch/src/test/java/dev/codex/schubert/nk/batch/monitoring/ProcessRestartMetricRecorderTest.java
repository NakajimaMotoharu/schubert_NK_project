package dev.codex.schubert.nk.batch.monitoring;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.Service;
import dev.codex.schubert.nk.batch.monitoring.ProcessRestartMetricRecorder.Reason;
import io.micrometer.core.instrument.Counter;
import io.micrometer.core.instrument.Gauge;
import io.micrometer.core.instrument.Meter;
import io.micrometer.core.instrument.simple.SimpleMeterRegistry;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.concurrent.Callable;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.stream.Collectors;
import org.junit.jupiter.api.Test;

/**
 * RESTARTMET001..008/1710; owned SDK only, no actual process observation/restart or suppression
 * changes.
 */
class ProcessRestartMetricRecorderTest {
  private static final int FAILURE_FACTORY_CALL = 2;
  private static final String WEB_SERVICE_NAME = "WEB";
  private static final String RESTART_COUNTER_NAME = "nk_process_restarts_total";
  private static final String REASON_LABEL = "reason";
  private static final String SERVICE_LABEL = "service";
  private static final String NONZERO_EXIT_REASON = "NONZERO_EXIT";
  private static final String SIGNAL_EXIT_REASON = "SIGNAL_EXIT";
  private static final String OOM_REASON = "OOM";
  private static final String UNKNOWN_REASON = "UNKNOWN";
  private static final String DEBUG_MODE = "DEBUG";
  private static final List<Reason> REASONS =
      List.of(Reason.NONZERO_EXIT, Reason.SIGNAL_EXIT, Reason.OOM, Reason.UNKNOWN);
  private static final List<String> SERVICES =
      List.of(WEB_SERVICE_NAME, "API", "BATCH", "BROKER", "DB", "CADDY");

  private static final class Registry extends SimpleMeterRegistry implements AutoCloseable {
    final AtomicInteger registrations = new AtomicInteger();
    final AtomicInteger increments = new AtomicInteger();
    final AtomicInteger closes = new AtomicInteger();
    Optional<Throwable> registrationFailure = Optional.empty();
    Optional<Throwable> incrementFailure = Optional.empty();
    boolean failAfter;

    @Override
    protected Counter newCounter(Meter.Id id) {
      if (registrations.incrementAndGet() == FAILURE_FACTORY_CALL) fail(registrationFailure);
      var delegate = super.newCounter(id);
      return new Counter() {
        @Override
        public Meter.Id getId() {
          return delegate.getId();
        }

        @Override
        public double count() {
          return delegate.count();
        }

        @Override
        public void increment(double amount) {
          increments.incrementAndGet();
          if (!failAfter) fail(incrementFailure);
          delegate.increment(amount);
          if (failAfter) fail(incrementFailure);
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
      throw new AssertionError("provider message forbidden");
    }

    @Override
    public String toString() {
      throw new AssertionError("provider formatting forbidden");
    }
  }

  private static void fail(Optional<Throwable> failure) {
    if (failure.isPresent()) {
      var problem = failure.orElseThrow();
      if (problem instanceof Error error) throw error;
      throw (RuntimeException) problem;
    }
  }

  private static double count(Registry registry, String reason, String service) {
    return registry
        .get(RESTART_COUNTER_NAME)
        .tags(REASON_LABEL, reason, SERVICE_LABEL, service)
        .counter()
        .count();
  }

  private static void shape(Registry registry) {
    assertEquals(24, registry.getMeters().size());
    var actual = new java.util.HashSet<String>();
    for (var meter : registry.getMeters()) {
      var id = meter.getId();
      assertEquals(RESTART_COUNTER_NAME, id.getName());
      assertEquals(Meter.Type.COUNTER, id.getType());
      assertEquals(
          Set.of(REASON_LABEL, SERVICE_LABEL),
          id.getTags().stream().map(t -> t.getKey()).collect(Collectors.toSet()));
      actual.add(id.getTag(REASON_LABEL) + "/" + id.getTag(SERVICE_LABEL));
    }
    var expected = new java.util.HashSet<String>();
    for (String reason :
        List.of(NONZERO_EXIT_REASON, SIGNAL_EXIT_REASON, OOM_REASON, UNKNOWN_REASON))
      for (String service : SERVICES) expected.add(reason + "/" + service);
    assertEquals(expected, actual);
  }

  @Test
  void restartMetric001TwentyFourCanonicalServiceSeriesStartAtZero() {
    try (var registry = new Registry()) {
      var recorder = new ProcessRestartMetricRecorder(registry, DEBUG_MODE);
      assertTrue(recorder.detailedMetricsRequested());
      shape(registry);
      for (String reason :
          List.of(NONZERO_EXIT_REASON, SIGNAL_EXIT_REASON, OOM_REASON, UNKNOWN_REASON))
        for (String service : SERVICES) assertEquals(0, count(registry, reason, service));
      assertEquals(24, registry.registrations.get());
      assertEquals(0, registry.increments.get());
      assertEquals(0, registry.closes.get());
    }
  }

  @Test
  void restartMetric002EachSuppliedRestartIncrementsOnlyItsPairOnce() {
    try (var registry = new Registry()) {
      var recorder = new ProcessRestartMetricRecorder(registry, DEBUG_MODE);
      for (var reason : REASONS)
        for (String name : SERVICES) {
          var service = Service.valueOf(name);
          for (int i = 0; i < 4; i++) recorder.record(reason, service);
          assertEquals(4, count(registry, reason.name(), name));
        }
      recorder.record(Reason.NONZERO_EXIT, Service.WEB);
      assertEquals(5, count(registry, NONZERO_EXIT_REASON, WEB_SERVICE_NAME));
      assertEquals(4, count(registry, SIGNAL_EXIT_REASON, WEB_SERVICE_NAME));
      assertEquals(4, count(registry, OOM_REASON, "CADDY"));
      assertEquals(97, registry.increments.get());
      assertEquals(24, registry.registrations.get());
      shape(registry);
    }
  }

  @Test
  void restartMetric003ClosedReasonParserAndGeneratedFactoriesUseTypedLiteralOracles() {
    assertEquals(Reason.NONZERO_EXIT, Reason.parse(NONZERO_EXIT_REASON));
    assertEquals(Reason.SIGNAL_EXIT, Reason.parse(SIGNAL_EXIT_REASON));
    assertEquals(Reason.OOM, Reason.parse(OOM_REASON));
    assertEquals(Reason.UNKNOWN, Reason.parse(UNKNOWN_REASON));
    for (String input : List.of("", "nonzero_exit", "unknown-reason"))
      assertEquals(
          "invalid restart metric reason",
          assertThrows(IllegalArgumentException.class, () -> Reason.parse(input)).getMessage());
    assertThrows(NullPointerException.class, () -> Reason.parse(null));
    assertArrayEquals(
        new Reason[] {Reason.NONZERO_EXIT, Reason.SIGNAL_EXIT, Reason.OOM, Reason.UNKNOWN},
        Reason.values());
    var mutable = Reason.values();
    mutable[0] = Reason.OOM;
    assertArrayEquals(
        new Reason[] {Reason.NONZERO_EXIT, Reason.SIGNAL_EXIT, Reason.OOM, Reason.UNKNOWN},
        Reason.values());
    assertSame(Reason.NONZERO_EXIT, Reason.valueOf(NONZERO_EXIT_REASON));
    assertSame(Reason.SIGNAL_EXIT, Reason.valueOf(SIGNAL_EXIT_REASON));
    assertSame(Reason.OOM, Reason.valueOf(OOM_REASON));
    assertSame(Reason.UNKNOWN, Reason.valueOf(UNKNOWN_REASON));
    assertThrows(IllegalArgumentException.class, () -> Reason.valueOf("nonzero_exit"));
    assertThrows(NullPointerException.class, () -> Reason.valueOf(null));
  }

  @Test
  void restartMetric004BothModesRejectNullAndStandardKeepsNoDetailedState() {
    for (String mode : List.of(DEBUG_MODE, "STANDARD"))
      try (var registry = new Registry()) {
        var recorder = new ProcessRestartMetricRecorder(registry, mode);
        recorder.record(Reason.NONZERO_EXIT, Service.WEB);
        int before = registry.increments.get();
        assertThrows(NullPointerException.class, () -> recorder.record(null, Service.WEB));
        assertThrows(NullPointerException.class, () -> recorder.record(Reason.NONZERO_EXIT, null));
        assertEquals(before, registry.increments.get());
        assertEquals(0, registry.closes.get());
        if (mode.equals(DEBUG_MODE)) {
          assertTrue(recorder.detailedMetricsRequested());
          assertEquals(1, count(registry, NONZERO_EXIT_REASON, WEB_SERVICE_NAME));
          shape(registry);
        } else {
          assertFalse(recorder.detailedMetricsRequested());
          for (var reason : REASONS)
            for (String name : SERVICES) recorder.record(reason, Service.valueOf(name));
          assertEquals(0, registry.increments.get());
          assertEquals(0, registry.getMeters().size());
        }
      }
    try (var registry = new Registry()) {
      assertThrows(
          NullPointerException.class, () -> new ProcessRestartMetricRecorder(null, DEBUG_MODE));
      assertThrows(
          NullPointerException.class, () -> new ProcessRestartMetricRecorder(registry, null));
      for (String mode : List.of("", "debug", "unknown-mode"))
        assertEquals(
            "CONFIG_INVALID",
            assertThrows(
                    IllegalArgumentException.class,
                    () -> new ProcessRestartMetricRecorder(registry, mode))
                .getMessage());
      assertEquals(0, registry.registrations.get());
    }
  }

  @Test
  void restartMetric005PartialFactoryFailureKeepsPrefixAndOriginalProblem() {
    for (var problem :
        List.<Throwable>of(new Unformattable(), new AssertionError("owned factory"))) {
      var registry = new Registry();
      registry.registrationFailure = Optional.of(problem);
      try {
        assertSame(
            problem,
            assertThrows(
                problem.getClass(), () -> new ProcessRestartMetricRecorder(registry, DEBUG_MODE)));
        assertEquals(2, registry.registrations.get());
        assertEquals(1, registry.getMeters().size());
        assertEquals(0, count(registry, NONZERO_EXIT_REASON, WEB_SERVICE_NAME));
        assertEquals(0, registry.increments.get());
        assertEquals(0, registry.closes.get());
      } finally {
        registry.close();
      }
      assertEquals(1, registry.closes.get());
    }
  }

  @Test
  void restartMetric006IncrementFailureNeverRetriesCompensatesOrNormalizesSuccess() {
    for (var problem :
        List.<Throwable>of(new Unformattable(), new AssertionError("owned increment")))
      for (boolean after : List.of(false, true)) {
        var registry = new Registry();
        try {
          var recorder = new ProcessRestartMetricRecorder(registry, DEBUG_MODE);
          registry.incrementFailure = Optional.of(problem);
          registry.failAfter = after;
          assertSame(
              problem,
              assertThrows(
                  problem.getClass(), () -> recorder.record(Reason.NONZERO_EXIT, Service.WEB)));
          assertEquals(1, registry.increments.get());
          assertEquals(after ? 1 : 0, count(registry, NONZERO_EXIT_REASON, WEB_SERVICE_NAME));
          assertEquals(0, count(registry, SIGNAL_EXIT_REASON, WEB_SERVICE_NAME));
          assertEquals(0, registry.closes.get());
          shape(registry);
        } finally {
          registry.close();
        }
        assertEquals(1, registry.closes.get());
      }
  }

  @Test
  void restartMetric007ConcurrentTotalsComeFromPrecomputedInputsAndOwnersStaySeparate()
      throws Exception {
    try (var registry = new Registry();
        var otherRegistry = new Registry()) {
      var executor = Executors.newFixedThreadPool(8);
      try {
        var recorder = new ProcessRestartMetricRecorder(registry, DEBUG_MODE);
        Map<String, Integer> expected = new HashMap<>();
        var tasks = new ArrayList<Callable<Void>>();
        for (int i = 0; i < 64; i++) {
          var reason = REASONS.get(i % 4);
          String name = SERVICES.get((i / 4) % 6);
          var service = Service.valueOf(name);
          expected.merge(reason.name() + "/" + name, 1, Integer::sum);
          tasks.add(
              () -> {
                recorder.record(reason, service);
                return null;
              });
        }
        for (var result : executor.invokeAll(tasks, 10, TimeUnit.SECONDS))
          result.get(5, TimeUnit.SECONDS);
        for (String reason :
            List.of(NONZERO_EXIT_REASON, SIGNAL_EXIT_REASON, OOM_REASON, UNKNOWN_REASON))
          for (String service : SERVICES)
            assertEquals(
                expected.getOrDefault(reason + "/" + service, 0).doubleValue(),
                count(registry, reason, service));
        assertEquals(64, registry.increments.get());
        var other = new ProcessRestartMetricRecorder(otherRegistry, DEBUG_MODE);
        for (int i = 0; i < 7; i++) other.record(Reason.NONZERO_EXIT, Service.WEB);
        assertEquals(7, count(otherRegistry, NONZERO_EXIT_REASON, WEB_SERVICE_NAME));
        assertEquals(
            expected.get("NONZERO_EXIT/WEB").doubleValue(),
            count(registry, NONZERO_EXIT_REASON, WEB_SERVICE_NAME));
        shape(registry);
        shape(otherRegistry);
      } finally {
        executor.shutdownNow();
        assertTrue(executor.awaitTermination(10, TimeUnit.SECONDS));
      }
    }
  }

  @Test
  void restartMetric008ForeignGaugeCannotBeReplacedOrClosed() {
    try (var registry = new Registry()) {
      var foreign =
          Gauge.builder(RESTART_COUNTER_NAME, new AtomicInteger(7), AtomicInteger::get)
              .tags(REASON_LABEL, NONZERO_EXIT_REASON, SERVICE_LABEL, WEB_SERVICE_NAME)
              .register(registry);
      assertThrows(
          IllegalArgumentException.class,
          () -> new ProcessRestartMetricRecorder(registry, DEBUG_MODE));
      assertSame(
          foreign,
          registry
              .get(RESTART_COUNTER_NAME)
              .tags(REASON_LABEL, NONZERO_EXIT_REASON, SERVICE_LABEL, WEB_SERVICE_NAME)
              .gauge());
      assertEquals(7, foreign.value());
      assertEquals(0, registry.closes.get());
    }
  }
}
