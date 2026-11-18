package dev.codex.schubert.nk.api.monitoring;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.api.monitoring.OperationMismatchMetricRecorder.Operation;
import io.micrometer.core.instrument.Counter;
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

/** OPMIS001..008: enum-only supplied observations and owned SDK, no real tokens/keys/HMAC/auth. */
class OperationMismatchMetricRecorderTest {
  private static final int FAILED_REGISTRATION_ORDINAL = 2;
  private static final String DELETE_QUESTION_OPERATION = "QDLREQ01";
  private static final String DEBUG_MONITORING_MODE = "DEBUG";
  private static final Set<String> OPERATIONS =
      Set.of(
          "UCRREQ01",
          "USTREQ01",
          "URLREQ01",
          "UPWREQ01",
          "ULKREQ01",
          "QSBREQ01",
          "NTCREQ01",
          DELETE_QUESTION_OPERATION);

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
      if (registrations.incrementAndGet() == FAILED_REGISTRATION_ORDINAL) fail(registrationFailure);
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

  private static double count(Registry registry, String operation) {
    return registry
        .get("nk_operation_token_mismatch_total")
        .tag("operation", operation)
        .counter()
        .count();
  }

  private static void shape(Registry registry) {
    assertEquals(8, registry.getMeters().size());
    var actual = new java.util.HashSet<String>();
    for (var meter : registry.getMeters()) {
      assertEquals("nk_operation_token_mismatch_total", meter.getId().getName());
      assertEquals(Meter.Type.COUNTER, meter.getId().getType());
      assertEquals(
          Set.of("operation"),
          meter.getId().getTags().stream().map(t -> t.getKey()).collect(Collectors.toSet()));
      actual.add(meter.getId().getTag("operation"));
    }
    assertEquals(OPERATIONS, actual);
  }

  @Test
  void opMis001DebugHasExactlyEightCanonicalZeroCounters() {
    try (var registry = new Registry()) {
      var recorder = new OperationMismatchMetricRecorder(registry, DEBUG_MONITORING_MODE);
      assertTrue(recorder.detailedMetricsRequested());
      assertEquals(
          OPERATIONS,
          java.util.Arrays.stream(Operation.values()).map(Enum::name).collect(Collectors.toSet()));
      for (String operation : OPERATIONS) {
        assertEquals(operation, OperationMismatchMetricRecorder.operation(operation).name());
        assertEquals(0, count(registry, operation));
      }
      shape(registry);
      assertEquals(8, registry.registrations.get());
      assertEquals(0, registry.increments.get());
      assertEquals(0, registry.closes.get());
    }
  }

  @Test
  void opMis002EachObservationIncrementsOnlyItsCanonicalCounterOnce() {
    try (var registry = new Registry()) {
      var recorder = new OperationMismatchMetricRecorder(registry, DEBUG_MONITORING_MODE);
      for (var operation : Operation.values()) recorder.record(operation);
      recorder.record(Operation.UCRREQ01);
      assertEquals(2, count(registry, "UCRREQ01"));
      for (String operation :
          Set.of(
              "USTREQ01",
              "URLREQ01",
              "UPWREQ01",
              "ULKREQ01",
              "QSBREQ01",
              "NTCREQ01",
              DELETE_QUESTION_OPERATION)) assertEquals(1, count(registry, operation));
      assertEquals(9, registry.increments.get());
      assertThrows(NullPointerException.class, () -> recorder.record(null));
      assertEquals(9, registry.increments.get());
      shape(registry);
    }
  }

  @Test
  void opMis003StandardHasNoDetailedRegistrationOrIncrement() {
    try (var registry = new Registry()) {
      var recorder = new OperationMismatchMetricRecorder(registry, "STANDARD");
      assertFalse(recorder.detailedMetricsRequested());
      for (var operation : Operation.values()) recorder.record(operation);
      assertEquals(0, registry.registrations.get());
      assertEquals(0, registry.increments.get());
      assertEquals(0, registry.getMeters().size());
      assertThrows(NullPointerException.class, () -> recorder.record(null));
    }
  }

  @Test
  void opMis004NullUnknownAndAliasedBoundariesCannotBecomeSeriesOrDiagnosticValues() {
    try (var registry = new Registry()) {
      assertThrows(
          NullPointerException.class,
          () -> new OperationMismatchMetricRecorder(null, DEBUG_MONITORING_MODE));
      assertThrows(
          NullPointerException.class, () -> new OperationMismatchMetricRecorder(registry, null));
      assertThrows(
          NullPointerException.class, () -> OperationMismatchMetricRecorder.operation(null));
      for (String value : List.of("", "qsbreq01", "LGNREQ01", "unknown-secret-canary"))
        assertEquals(
            "CONFIG_INVALID",
            assertThrows(
                    IllegalArgumentException.class,
                    () -> OperationMismatchMetricRecorder.operation(value))
                .getMessage());
      for (String mode : List.of("debug", "", "unknown-mode", "DEBTf", "STANDAQc"))
        assertEquals(
            "CONFIG_INVALID",
            assertThrows(
                    IllegalArgumentException.class,
                    () -> new OperationMismatchMetricRecorder(registry, mode))
                .getMessage());
      assertEquals(0, registry.registrations.get());
      assertEquals(0, registry.getMeters().size());
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
  void opMis005PartialRegistrationFailureKeepsIdentityAndRegistryOwnership() {
    for (var failure :
        List.<Throwable>of(
            new UnformattableFailure(), new AssertionError("owned provider fixture"))) {
      var registry = new Registry();
      try {
        registry.registrationFailure = Optional.of(failure);
        assertSame(
            failure,
            assertThrows(
                failure.getClass(),
                () -> new OperationMismatchMetricRecorder(registry, DEBUG_MONITORING_MODE)));
        assertEquals(2, registry.registrations.get());
        assertEquals(1, registry.getMeters().size());
        assertEquals(0, registry.closes.get());
      } finally {
        registry.close();
      }
      assertEquals(1, registry.closes.get());
    }
  }

  @Test
  void opMis006IncrementFailuresAreNeverRetriedOrCompensated() {
    for (boolean after : List.of(false, true)) {
      for (var failure :
          List.<Throwable>of(
              new UnformattableFailure(), new AssertionError("owned increment fixture"))) {
        try (var registry = new Registry()) {
          var recorder = new OperationMismatchMetricRecorder(registry, DEBUG_MONITORING_MODE);
          if (after) registry.afterIncrement = Optional.of(failure);
          else registry.beforeIncrement = Optional.of(failure);
          assertSame(
              failure, assertThrows(failure.getClass(), () -> recorder.record(Operation.QSBREQ01)));
          assertEquals(1, registry.increments.get());
          assertEquals(after ? 1 : 0, count(registry, "QSBREQ01"));
          shape(registry);
        }
      }
    }
  }

  @Test
  void opMis007ParallelObservationsHaveExactCountsWithoutCardinalityGrowth() throws Exception {
    try (var registry = new Registry()) {
      var executor = Executors.newFixedThreadPool(8);
      try {
        var recorder = new OperationMismatchMetricRecorder(registry, DEBUG_MONITORING_MODE);
        var tasks = new ArrayList<Callable<Boolean>>();
        for (int i = 0; i < 64; i++) {
          var operation = Operation.values()[i % 8];
          tasks.add(
              () -> {
                recorder.record(operation);
                return true;
              });
        }
        for (var result : executor.invokeAll(tasks, 10, TimeUnit.SECONDS)) assertTrue(result.get());
        for (String operation : OPERATIONS) assertEquals(8, count(registry, operation));
        assertEquals(64, registry.increments.get());
        shape(registry);
      } finally {
        executor.shutdownNow();
        assertTrue(executor.awaitTermination(10, TimeUnit.SECONDS));
      }
    }
  }

  @Test
  void opMis008IndependentOwnersAndRepeatedObservationsDoNotShareCounts() {
    try (var one = new Registry();
        var two = new Registry()) {
      var first = new OperationMismatchMetricRecorder(one, DEBUG_MONITORING_MODE);
      var second = new OperationMismatchMetricRecorder(two, DEBUG_MONITORING_MODE);
      second.record(Operation.QDLREQ01);
      for (int i = 0; i < 1000; i++) first.record(Operation.QDLREQ01);
      assertEquals(1000, count(one, DELETE_QUESTION_OPERATION));
      assertEquals(1, count(two, DELETE_QUESTION_OPERATION));
      assertEquals(0, count(one, "NTCREQ01"));
      shape(one);
      shape(two);
      assertEquals(0, one.closes.get());
      assertEquals(0, two.closes.get());
    }
  }
}
