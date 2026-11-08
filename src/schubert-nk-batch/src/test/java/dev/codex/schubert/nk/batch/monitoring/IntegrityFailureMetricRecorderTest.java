package dev.codex.schubert.nk.batch.monitoring;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.batch.monitoring.IntegrityFailureMetricRecorder.Area;
import dev.codex.schubert.nk.batch.repository.BatchStep;
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

/** INTEGRITYMET001..008/1708; owned SDK only, no actual integrity probe/repair/retirement. */
class IntegrityFailureMetricRecorderTest {
  private static final int FAILURE_FACTORY_CALL = 2;
  private static final String BACKUP_DB_STEP_NAME = "BACKUP_DB";
  private static final String INTEGRITY_COUNTER_NAME = "nk_integrity_failures_total";
  private static final String AREA_LABEL = "area";
  private static final String STEP_LABEL = "step";
  private static final String HASH_AREA_NAME = "HASH";
  private static final String PATH_AREA_NAME = "PATH";
  private static final String CONFIG_AREA_NAME = "CONFIG";
  private static final String DEBUG_MODE = "DEBUG";
  private static final List<Area> AREAS = List.of(Area.HASH, Area.PATH, Area.CONFIG);
  private static final List<String> STEPS =
      List.of(
          BACKUP_DB_STEP_NAME,
          "BACKUP_CONFIG",
          "CLEAN_NOTIFICATION",
          "CLEAN_QUESTION",
          "CLEAN_SESSION",
          "CLEAN_INBOX_OUTBOX",
          "CLEAN_LOG",
          "CLEAN_BATCH_RUN",
          "CLEAN_TRANSFER",
          "CLEAN_EXPIRY");

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

  private static double count(Registry registry, String area, String step) {
    return registry
        .get(INTEGRITY_COUNTER_NAME)
        .tags(AREA_LABEL, area, STEP_LABEL, step)
        .counter()
        .count();
  }

  private static void shape(Registry registry) {
    assertEquals(30, registry.getMeters().size());
    var actual = new java.util.HashSet<String>();
    for (var meter : registry.getMeters()) {
      var id = meter.getId();
      assertEquals(INTEGRITY_COUNTER_NAME, id.getName());
      assertEquals(Meter.Type.COUNTER, id.getType());
      assertEquals(
          Set.of(AREA_LABEL, STEP_LABEL),
          id.getTags().stream().map(t -> t.getKey()).collect(Collectors.toSet()));
      actual.add(id.getTag(AREA_LABEL) + "/" + id.getTag(STEP_LABEL));
    }
    var expected = new java.util.HashSet<String>();
    for (String area : List.of(HASH_AREA_NAME, PATH_AREA_NAME, CONFIG_AREA_NAME))
      for (String step : STEPS) expected.add(area + "/" + step);
    assertEquals(expected, actual);
  }

  @Test
  void integrityMetric001ThirtyCanonicalBatchSeriesStartAtZero() {
    BatchStep[] expectedSteps = {
      BatchStep.BACKUP_DB,
      BatchStep.BACKUP_CONFIG,
      BatchStep.CLEAN_NOTIFICATION,
      BatchStep.CLEAN_QUESTION,
      BatchStep.CLEAN_SESSION,
      BatchStep.CLEAN_INBOX_OUTBOX,
      BatchStep.CLEAN_LOG,
      BatchStep.CLEAN_BATCH_RUN,
      BatchStep.CLEAN_TRANSFER,
      BatchStep.CLEAN_EXPIRY
    };
    assertArrayEquals(expectedSteps, BatchStep.values());
    var returned = BatchStep.values();
    returned[0] = BatchStep.CLEAN_EXPIRY;
    assertArrayEquals(expectedSteps, BatchStep.values());
    for (int index = 0; index < expectedSteps.length; index++) {
      assertSame(expectedSteps[index], BatchStep.valueOf(STEPS.get(index)));
      assertEquals(index < 2, expectedSteps[index].backup());
    }
    assertThrows(IllegalArgumentException.class, () -> BatchStep.valueOf("unknown-step"));
    assertThrows(NullPointerException.class, () -> BatchStep.valueOf(null));
    try (var registry = new Registry()) {
      var recorder = new IntegrityFailureMetricRecorder(registry, DEBUG_MODE);
      assertTrue(recorder.detailedMetricsRequested());
      shape(registry);
      for (String area : List.of(HASH_AREA_NAME, PATH_AREA_NAME, CONFIG_AREA_NAME))
        for (String step : STEPS) assertEquals(0, count(registry, area, step));
      assertEquals(30, registry.registrations.get());
      assertEquals(0, registry.increments.get());
      assertEquals(0, registry.closes.get());
    }
  }

  @Test
  void integrityMetric002EachSuppliedFailureIncrementsOnlyItsPairOnce() {
    try (var registry = new Registry()) {
      var recorder = new IntegrityFailureMetricRecorder(registry, DEBUG_MODE);
      for (var area : AREAS)
        for (String name : STEPS) {
          var step = BatchStep.valueOf(name);
          for (int i = 0; i < 4; i++) recorder.record(area, step);
          assertEquals(4, count(registry, area.name(), name));
        }
      recorder.record(Area.HASH, BatchStep.BACKUP_DB);
      assertEquals(5, count(registry, HASH_AREA_NAME, BACKUP_DB_STEP_NAME));
      assertEquals(4, count(registry, PATH_AREA_NAME, BACKUP_DB_STEP_NAME));
      assertEquals(4, count(registry, CONFIG_AREA_NAME, "CLEAN_EXPIRY"));
      assertEquals(121, registry.increments.get());
      assertEquals(30, registry.registrations.get());
      shape(registry);
    }
  }

  @Test
  void integrityMetric003ClosedAreaParserAndGeneratedFactoriesUseTypedLiteralOracles() {
    assertEquals(Area.HASH, Area.parse(HASH_AREA_NAME));
    assertEquals(Area.PATH, Area.parse(PATH_AREA_NAME));
    assertEquals(Area.CONFIG, Area.parse(CONFIG_AREA_NAME));
    for (String input : List.of("", "hash", "unknown-area"))
      assertEquals(
          "invalid integrity metric area",
          assertThrows(IllegalArgumentException.class, () -> Area.parse(input)).getMessage());
    assertThrows(NullPointerException.class, () -> Area.parse(null));
    assertArrayEquals(new Area[] {Area.HASH, Area.PATH, Area.CONFIG}, Area.values());
    var mutable = Area.values();
    mutable[0] = Area.CONFIG;
    assertArrayEquals(new Area[] {Area.HASH, Area.PATH, Area.CONFIG}, Area.values());
    assertSame(Area.HASH, Area.valueOf(HASH_AREA_NAME));
    assertSame(Area.PATH, Area.valueOf(PATH_AREA_NAME));
    assertSame(Area.CONFIG, Area.valueOf(CONFIG_AREA_NAME));
    assertThrows(IllegalArgumentException.class, () -> Area.valueOf("hash"));
    assertThrows(NullPointerException.class, () -> Area.valueOf(null));
  }

  @Test
  void integrityMetric004BothModesRejectNullAndStandardKeepsNoDetailedState() {
    for (String mode : List.of(DEBUG_MODE, "STANDARD"))
      try (var registry = new Registry()) {
        var recorder = new IntegrityFailureMetricRecorder(registry, mode);
        recorder.record(Area.HASH, BatchStep.BACKUP_DB);
        int before = registry.increments.get();
        assertThrows(NullPointerException.class, () -> recorder.record(null, BatchStep.BACKUP_DB));
        assertThrows(NullPointerException.class, () -> recorder.record(Area.HASH, null));
        assertEquals(before, registry.increments.get());
        assertEquals(0, registry.closes.get());
        if (mode.equals(DEBUG_MODE)) {
          assertTrue(recorder.detailedMetricsRequested());
          assertEquals(1, count(registry, HASH_AREA_NAME, BACKUP_DB_STEP_NAME));
          shape(registry);
        } else {
          assertFalse(recorder.detailedMetricsRequested());
          for (var area : AREAS)
            for (String name : STEPS) recorder.record(area, BatchStep.valueOf(name));
          assertEquals(0, registry.increments.get());
          assertEquals(0, registry.getMeters().size());
        }
      }
    try (var registry = new Registry()) {
      assertThrows(
          NullPointerException.class, () -> new IntegrityFailureMetricRecorder(null, DEBUG_MODE));
      assertThrows(
          NullPointerException.class, () -> new IntegrityFailureMetricRecorder(registry, null));
      for (String mode : List.of("", "debug", "unknown-mode"))
        assertEquals(
            "CONFIG_INVALID",
            assertThrows(
                    IllegalArgumentException.class,
                    () -> new IntegrityFailureMetricRecorder(registry, mode))
                .getMessage());
      assertEquals(0, registry.registrations.get());
    }
  }

  @Test
  void integrityMetric005PartialFactoryFailureKeepsPrefixAndOriginalProblem() {
    for (var problem :
        List.<Throwable>of(new Unformattable(), new AssertionError("owned factory"))) {
      var registry = new Registry();
      registry.registrationFailure = Optional.of(problem);
      try {
        assertSame(
            problem,
            assertThrows(
                problem.getClass(),
                () -> new IntegrityFailureMetricRecorder(registry, DEBUG_MODE)));
        assertEquals(2, registry.registrations.get());
        assertEquals(1, registry.getMeters().size());
        assertEquals(0, count(registry, HASH_AREA_NAME, BACKUP_DB_STEP_NAME));
        assertEquals(0, registry.increments.get());
        assertEquals(0, registry.closes.get());
      } finally {
        registry.close();
      }
      assertEquals(1, registry.closes.get());
    }
  }

  @Test
  void integrityMetric006IncrementFailureNeverRetriesCompensatesOrNormalizesSuccess() {
    for (var problem :
        List.<Throwable>of(new Unformattable(), new AssertionError("owned increment")))
      for (boolean after : List.of(false, true)) {
        var registry = new Registry();
        try {
          var recorder = new IntegrityFailureMetricRecorder(registry, DEBUG_MODE);
          registry.incrementFailure = Optional.of(problem);
          registry.failAfter = after;
          assertSame(
              problem,
              assertThrows(
                  problem.getClass(), () -> recorder.record(Area.HASH, BatchStep.BACKUP_DB)));
          assertEquals(1, registry.increments.get());
          assertEquals(after ? 1 : 0, count(registry, HASH_AREA_NAME, BACKUP_DB_STEP_NAME));
          assertEquals(0, count(registry, PATH_AREA_NAME, BACKUP_DB_STEP_NAME));
          assertEquals(0, registry.closes.get());
          shape(registry);
        } finally {
          registry.close();
        }
        assertEquals(1, registry.closes.get());
      }
  }

  @Test
  void integrityMetric007ConcurrentTotalsComeFromPrecomputedInputsAndOwnersStaySeparate()
      throws Exception {
    try (var registry = new Registry();
        var otherRegistry = new Registry()) {
      var executor = Executors.newFixedThreadPool(8);
      try {
        var recorder = new IntegrityFailureMetricRecorder(registry, DEBUG_MODE);
        Map<String, Integer> expected = new HashMap<>();
        var tasks = new ArrayList<Callable<Void>>();
        for (int i = 0; i < 64; i++) {
          var area = AREAS.get(i % 3);
          String name = STEPS.get((i / 3) % 10);
          var step = BatchStep.valueOf(name);
          expected.merge(area.name() + "/" + name, 1, Integer::sum);
          tasks.add(
              () -> {
                recorder.record(area, step);
                return null;
              });
        }
        for (var result : executor.invokeAll(tasks, 10, TimeUnit.SECONDS))
          result.get(5, TimeUnit.SECONDS);
        for (String area : List.of(HASH_AREA_NAME, PATH_AREA_NAME, CONFIG_AREA_NAME))
          for (String step : STEPS)
            assertEquals(
                expected.getOrDefault(area + "/" + step, 0).doubleValue(),
                count(registry, area, step));
        assertEquals(64, registry.increments.get());
        var other = new IntegrityFailureMetricRecorder(otherRegistry, DEBUG_MODE);
        for (int i = 0; i < 7; i++) other.record(Area.HASH, BatchStep.BACKUP_DB);
        assertEquals(7, count(otherRegistry, HASH_AREA_NAME, BACKUP_DB_STEP_NAME));
        assertEquals(
            expected.get("HASH/BACKUP_DB").doubleValue(),
            count(registry, HASH_AREA_NAME, BACKUP_DB_STEP_NAME));
        shape(registry);
        shape(otherRegistry);
      } finally {
        executor.shutdownNow();
        assertTrue(executor.awaitTermination(10, TimeUnit.SECONDS));
      }
    }
  }

  @Test
  void integrityMetric008ForeignGaugeCannotBeReplacedOrClosed() {
    try (var registry = new Registry()) {
      var foreign =
          Gauge.builder(INTEGRITY_COUNTER_NAME, new AtomicInteger(7), AtomicInteger::get)
              .tags(AREA_LABEL, HASH_AREA_NAME, STEP_LABEL, BACKUP_DB_STEP_NAME)
              .register(registry);
      assertThrows(
          IllegalArgumentException.class,
          () -> new IntegrityFailureMetricRecorder(registry, DEBUG_MODE));
      assertSame(
          foreign,
          registry
              .get(INTEGRITY_COUNTER_NAME)
              .tags(AREA_LABEL, HASH_AREA_NAME, STEP_LABEL, BACKUP_DB_STEP_NAME)
              .gauge());
      assertEquals(7, foreign.value());
      assertEquals(0, registry.closes.get());
    }
  }
}
