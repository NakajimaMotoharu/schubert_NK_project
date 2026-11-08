package dev.codex.schubert.nk.batch.monitoring;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.batch.monitoring.TransferMetricRecorder.Counts;
import dev.codex.schubert.nk.batch.monitoring.TransferMetricRecorder.Suffix;
import dev.codex.schubert.nk.batch.monitoring.TransferMetricRecorder.Usage;
import io.micrometer.core.instrument.Gauge;
import io.micrometer.core.instrument.Meter;
import io.micrometer.core.instrument.MockClock;
import io.micrometer.core.instrument.simple.SimpleConfig;
import io.micrometer.core.instrument.simple.SimpleMeterRegistry;
import java.util.Arrays;
import java.util.List;
import java.util.Optional;
import java.util.Set;
import java.util.concurrent.Callable;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.function.ToDoubleFunction;
import java.util.stream.Collectors;
import org.junit.jupiter.api.Test;

/** Literal counts and actual owned SDK, no real transfer-file/directory/provider access. */
class TransferMetricRecorderTest {
  private static final String PART_SUFFIX_LABEL = ".part";
  private static final String READY_SUFFIX_LABEL = ".ready";
  private static final String DEBUG_MONITORING_MODE = "DEBUG";
  private static final String FILES = "nk_file_transfer_files";
  private static final String BYTES = "nk_file_transfer_bytes";

  private static final class OwnedRegistry extends SimpleMeterRegistry implements AutoCloseable {
    final AtomicInteger closes = new AtomicInteger();
    final AtomicInteger registrations = new AtomicInteger();
    Optional<Throwable> failure = Optional.empty();

    OwnedRegistry() {
      super(SimpleConfig.DEFAULT, new MockClock());
    }

    @Override
    protected <T> Gauge newGauge(Meter.Id id, T object, ToDoubleFunction<T> value) {
      if (registrations.incrementAndGet() == 2 && failure.isPresent()) {
        Throwable problem = failure.orElseThrow();
        if (problem instanceof Error fatal) throw fatal;
        throw (RuntimeException) problem;
      }
      return super.newGauge(id, object, value);
    }

    @Override
    public void close() {
      closes.incrementAndGet();
      super.close();
    }
  }

  private static Usage usage(long partFiles, long partBytes, long readyFiles, long readyBytes) {
    return new Usage(new Counts(partFiles, partBytes), new Counts(readyFiles, readyBytes));
  }

  private static double value(OwnedRegistry registry, String name, String suffix) {
    return registry.get(name).tag("suffix", suffix).gauge().value();
  }

  private static void shape(OwnedRegistry registry) {
    assertEquals(4, registry.getMeters().size());
    for (var meter : registry.getMeters()) {
      var id = meter.getId();
      assertEquals(Meter.Type.GAUGE, id.getType());
      assertTrue(Set.of(FILES, BYTES).contains(id.getName()));
      assertEquals(
          Set.of("suffix"), id.getTags().stream().map(t -> t.getKey()).collect(Collectors.toSet()));
      assertTrue(Set.of(PART_SUFFIX_LABEL, READY_SUFFIX_LABEL).contains(id.getTag("suffix")));
    }
  }

  @Test
  void transferMet001ActualDebugHasFourClosedUnknownGaugesAndBorrowedRegistry() {
    try (var registry = new OwnedRegistry()) {
      var recorder = new TransferMetricRecorder(registry, DEBUG_MONITORING_MODE);
      assertTrue(recorder.detailedMetricsRequested());
      assertTrue(recorder.snapshot().isEmpty());
      assertEquals(
          Set.of(PART_SUFFIX_LABEL, READY_SUFFIX_LABEL),
          Arrays.stream(Suffix.values()).map(Suffix::label).collect(Collectors.toSet()));
      shape(registry);
      for (String name : List.of(FILES, BYTES))
        for (String suffix : List.of(PART_SUFFIX_LABEL, READY_SUFFIX_LABEL))
          assertTrue(Double.isNaN(value(registry, name, suffix)));
      assertEquals(4, registry.registrations.get());
      assertEquals(0, registry.closes.get());
      assertFalse(registry.isClosed());
    }
  }

  @Test
  void transferMet002LiteralCountsAndExactTotalsPreservePreviousSnapshot() {
    try (var registry = new OwnedRegistry()) {
      var recorder = new TransferMetricRecorder(registry, DEBUG_MONITORING_MODE);
      var first = usage(2, 1024, 3, 2048);
      recorder.record(first);
      assertSame(first, recorder.snapshot().orElseThrow());
      assertEquals(5, first.totalFiles());
      assertEquals(3072, first.totalBytes());
      assertEquals(2.0, value(registry, FILES, PART_SUFFIX_LABEL));
      assertEquals(1024.0, value(registry, BYTES, PART_SUFFIX_LABEL));
      assertEquals(3.0, value(registry, FILES, READY_SUFFIX_LABEL));
      assertEquals(2048.0, value(registry, BYTES, READY_SUFFIX_LABEL));
      recorder.record(usage(8, 9, 10, 11));
      assertEquals(2, first.part().files());
      assertEquals(2048, first.ready().bytes());
      assertEquals(18, recorder.snapshot().orElseThrow().totalFiles());
      shape(registry);
    }
  }

  @Test
  void transferMet003RealZeroAndMissingAreDifferentAndRecoveryUsesNewValues() {
    try (var registry = new OwnedRegistry()) {
      var recorder = new TransferMetricRecorder(registry, DEBUG_MONITORING_MODE);
      recorder.record(usage(0, 0, 0, 0));
      for (String name : List.of(FILES, BYTES))
        for (String suffix : List.of(PART_SUFFIX_LABEL, READY_SUFFIX_LABEL))
          assertEquals(0.0, value(registry, name, suffix));
      recorder.missing();
      assertTrue(recorder.snapshot().isEmpty());
      for (String name : List.of(FILES, BYTES))
        for (String suffix : List.of(PART_SUFFIX_LABEL, READY_SUFFIX_LABEL))
          assertTrue(Double.isNaN(value(registry, name, suffix)));
      recorder.record(usage(1, 2, 3, 4));
      assertEquals(1.0, value(registry, FILES, PART_SUFFIX_LABEL));
      assertEquals(2.0, value(registry, BYTES, PART_SUFFIX_LABEL));
      assertEquals(3.0, value(registry, FILES, READY_SUFFIX_LABEL));
      assertEquals(4.0, value(registry, BYTES, READY_SUFFIX_LABEL));
    }
  }

  @Test
  void transferMet004StandardDoesNotRegisterOrRetainDetailedValues() {
    try (var registry = new OwnedRegistry()) {
      var recorder = new TransferMetricRecorder(registry, "STANDARD");
      assertFalse(recorder.detailedMetricsRequested());
      recorder.record(usage(1, 2, 3, 4));
      assertTrue(recorder.snapshot().isEmpty());
      recorder.missing();
      assertTrue(recorder.snapshot().isEmpty());
      assertThrows(NullPointerException.class, () -> recorder.record(null));
      assertEquals(0, registry.registrations.get());
      assertTrue(registry.getMeters().isEmpty());
    }
  }

  @Test
  void transferMet005NullNegativeAndOverflowInputsCannotMutateExistingSnapshot() {
    assertThrows(NullPointerException.class, () -> new TransferMetricRecorder(null, "STANDARD"));
    try (var registry = new OwnedRegistry()) {
      assertThrows(NullPointerException.class, () -> new TransferMetricRecorder(registry, null));
      assertThrows(
          IllegalArgumentException.class, () -> new TransferMetricRecorder(registry, "debug"));
      assertTrue(registry.getMeters().isEmpty());
      var recorder = new TransferMetricRecorder(registry, DEBUG_MONITORING_MODE);
      var before = usage(1, 2, 3, 4);
      recorder.record(before);
      assertThrows(NullPointerException.class, () -> recorder.record(null));
      assertThrows(NullPointerException.class, () -> new Usage(null, new Counts(0, 0)));
      assertThrows(NullPointerException.class, () -> new Usage(new Counts(0, 0), null));
      assertThrows(IllegalArgumentException.class, () -> new Counts(-1, 0));
      assertThrows(IllegalArgumentException.class, () -> new Counts(0, -1));
      assertThrows(ArithmeticException.class, () -> usage(Long.MAX_VALUE, 0, 1, 0));
      assertThrows(ArithmeticException.class, () -> usage(0, Long.MAX_VALUE, 0, 1));
      assertSame(before, recorder.snapshot().orElseThrow());
      assertEquals(2.0, value(registry, BYTES, PART_SUFFIX_LABEL));
    }
  }

  @Test
  void transferMet006MaximumLongRemainsExactInSnapshotAndDoubleUsesGoldenRounding() {
    try (var registry = new OwnedRegistry()) {
      var recorder = new TransferMetricRecorder(registry, DEBUG_MONITORING_MODE);
      var maximum = usage(Long.MAX_VALUE - 1, Long.MAX_VALUE - 1, 1, 1);
      recorder.record(maximum);
      assertEquals(Long.MAX_VALUE, maximum.totalFiles());
      assertEquals(Long.MAX_VALUE, maximum.totalBytes());
      assertEquals(Long.MAX_VALUE - 1, maximum.part().files());
      assertEquals(1, maximum.ready().bytes());
      assertEquals(9_223_372_036_854_776_000.0, value(registry, FILES, PART_SUFFIX_LABEL), 0.0);
      assertEquals(9_223_372_036_854_776_000.0, value(registry, BYTES, PART_SUFFIX_LABEL), 0.0);
      assertEquals(1.0, value(registry, FILES, READY_SUFFIX_LABEL));
      assertEquals(1.0, value(registry, BYTES, READY_SUFFIX_LABEL));
    }
  }

  @Test
  void transferMet007ConcurrentAtomicSnapshotNeverMixesCohortsOrChangesOldValues()
      throws Exception {
    try (var registry = new OwnedRegistry()) {
      var pool = Executors.newFixedThreadPool(8);
      try {
        var recorder = new TransferMetricRecorder(registry, DEBUG_MONITORING_MODE);
        var first = usage(1, 10, 2, 20);
        var second = usage(3, 30, 4, 40);
        recorder.record(first);
        var jobs =
            java.util.stream.IntStream.range(0, 64)
                .<Callable<Boolean>>mapToObj(
                    i ->
                        () -> {
                          recorder.record(i % 2 == 0 ? first : second);
                          var snapshot = recorder.snapshot().orElseThrow();
                          return snapshot == first || snapshot == second;
                        })
                .toList();
        for (var result : pool.invokeAll(jobs, 10, TimeUnit.SECONDS)) assertTrue(result.get());
        assertEquals(3, first.totalFiles());
        assertEquals(30, first.totalBytes());
        recorder.record(second);
        assertSame(second, recorder.snapshot().orElseThrow());
        assertEquals(3.0, value(registry, FILES, PART_SUFFIX_LABEL));
        assertEquals(40.0, value(registry, BYTES, READY_SUFFIX_LABEL));
        shape(registry);
      } finally {
        pool.shutdownNow();
        assertTrue(pool.awaitTermination(10, TimeUnit.SECONDS));
      }
    }
  }

  @Test
  void transferMet008PartialRegistrationFailureAndSeparateOwnersKeepCallerOwnership() {
    for (Throwable failure : List.of(new IllegalStateException(), new AssertionError())) {
      try (var registry = new OwnedRegistry()) {
        registry.failure = Optional.of(failure);
        assertSame(
            failure,
            assertThrows(
                failure.getClass(),
                () -> new TransferMetricRecorder(registry, DEBUG_MONITORING_MODE)));
        assertEquals(2, registry.registrations.get());
        assertEquals(1, registry.getMeters().size());
        assertEquals(0, registry.closes.get());
        assertFalse(registry.isClosed());
      }
    }
    try (var first = new OwnedRegistry();
        var second = new OwnedRegistry()) {
      var one = new TransferMetricRecorder(first, DEBUG_MONITORING_MODE);
      var two = new TransferMetricRecorder(second, DEBUG_MONITORING_MODE);
      one.record(usage(1, 2, 3, 4));
      assertTrue(two.snapshot().isEmpty());
      assertTrue(Double.isNaN(value(second, FILES, PART_SUFFIX_LABEL)));
      shape(first);
      shape(second);
    }
  }
}
