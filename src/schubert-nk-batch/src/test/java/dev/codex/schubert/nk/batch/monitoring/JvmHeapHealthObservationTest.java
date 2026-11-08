package dev.codex.schubert.nk.batch.monitoring;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.lang.management.MemoryMXBean;
import java.lang.management.MemoryUsage;
import java.lang.reflect.Proxy;
import java.util.List;
import java.util.Optional;
import java.util.concurrent.Callable;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.Test;

/** Heap getter-only capability with owned fixed values, no actual JVM/GC/management connection. */
class JvmHeapHealthObservationTest {
  static final class Fixture {
    Optional<MemoryUsage> usage = Optional.of(new MemoryUsage(-1, 750, 1000, 1000));
    Optional<Throwable> failure = Optional.empty();
    final AtomicInteger reads = new AtomicInteger();
    final MemoryMXBean bean =
        (MemoryMXBean)
            Proxy.newProxyInstance(
                MemoryMXBean.class.getClassLoader(),
                new Class<?>[] {MemoryMXBean.class},
                (instance, method, args) -> {
                  if (!method.getName().equals("getHeapMemoryUsage"))
                    throw new AssertionError("no identity/nonheap/GC/control/format operation");
                  reads.incrementAndGet();
                  if (failure.isPresent()) {
                    Throwable value = failure.orElseThrow();
                    if (value instanceof Error fatal) throw fatal;
                    throw (RuntimeException) value;
                  }
                  return usage.orElse(null);
                });
  }

  private static final class UnformattableFailure extends IllegalStateException {
    private static final long serialVersionUID = 1L;

    @Override
    public String getMessage() {
      throw new AssertionError("no provider text");
    }

    @Override
    public String toString() {
      throw new AssertionError("no provider formatting");
    }
  }

  @Test
  void heapInput001FixedHeapTableAndBindingPerformOnlyOneReadPerSample() {
    var fixture = new Fixture();
    var source = JvmHeapHealthObservation.from(fixture.bean);
    assertEquals(0, fixture.reads.get());
    long[] used = {0, 750, 900, 1000};
    double[] expected = {0, 75, 90, 100};
    for (int i = 0; i < used.length; i++) {
      fixture.usage = Optional.of(new MemoryUsage(-1, used[i], 1000, 1000));
      assertEquals(expected[i], source.read().orElseThrow());
    }
    assertEquals(4, fixture.reads.get());
  }

  @Test
  void heapInput002UnknownMaximumNeverFallsBackToCommittedOrInventsZero() {
    var fixture = new Fixture();
    var source = JvmHeapHealthObservation.from(fixture.bean);
    fixture.usage = Optional.of(new MemoryUsage(-1, 100, 100, -1));
    assertTrue(source.read().isEmpty());
    fixture.usage = Optional.of(new MemoryUsage(-1, 0, 0, 0));
    assertTrue(source.read().isEmpty());
    fixture.usage = Optional.of(new MemoryUsage(-1, 750, 800, 1000));
    assertEquals(75, source.read().orElseThrow());
    assertEquals(3, fixture.reads.get());
  }

  @Test
  void heapInput003RatioBoundaryRejectsInvalidCountsRatherThanClamping() {
    var ratio = new HealthUsageRatio();
    for (long[] row :
        List.of(
            new long[] {0, 0}, new long[] {0, -1}, new long[] {-1, 1000}, new long[] {1001, 1000}))
      assertTrue(ratio.fromUsed(row[0], row[1]).isEmpty());
    assertEquals(25, ratio.fromUsed(250, 1000).orElseThrow());
  }

  @Test
  void heapInput004OneByteBoundaryHasIndependentIeeeExpectedValues() {
    var fixture = new Fixture();
    var source = JvmHeapHealthObservation.from(fixture.bean);
    long maximum = 1_000_000_000_000_000_000L;
    long[] exact = {750_000_000_000_000_000L, 900_000_000_000_000_000L};
    long[] belowBits = {0x4052bfffffffffffL, 0x40567fffffffffffL};
    double[] threshold = {75, 90};
    for (int i = 0; i < exact.length; i++) {
      fixture.usage = Optional.of(new MemoryUsage(-1, exact[i] - 1, maximum, maximum));
      double below = source.read().orElseThrow();
      assertEquals(Double.longBitsToDouble(belowBits[i]), below);
      assertTrue(below < threshold[i]);
      fixture.usage = Optional.of(new MemoryUsage(-1, exact[i], maximum, maximum));
      assertEquals(threshold[i], source.read().orElseThrow());
      fixture.usage = Optional.of(new MemoryUsage(-1, exact[i] + 1, maximum, maximum));
      assertTrue(source.read().orElseThrow() >= threshold[i]);
    }
  }

  @Test
  void heapInput005LargestAndSingleByteMaximaDoNotOverflow() {
    var fixture = new Fixture();
    var source = JvmHeapHealthObservation.from(fixture.bean);
    for (long maximum : new long[] {1, Long.MAX_VALUE}) {
      fixture.usage = Optional.of(new MemoryUsage(-1, 0, maximum, maximum));
      assertEquals(0, source.read().orElseThrow());
      fixture.usage = Optional.of(new MemoryUsage(-1, maximum, maximum, maximum));
      assertEquals(100, source.read().orElseThrow());
    }
  }

  @Test
  void heapInput006NullBoundaryNeverBecomesValidZeroAndBindingIsBorrowed() {
    assertThrows(NullPointerException.class, () -> JvmHeapHealthObservation.from(null));
    var fixture = new Fixture();
    fixture.usage = Optional.empty();
    var source = JvmHeapHealthObservation.from(fixture.bean);
    assertEquals(0, fixture.reads.get());
    var denied = assertThrows(NullPointerException.class, source::read);
    assertEquals("heap usage", denied.getMessage());
    fixture.usage = Optional.of(new MemoryUsage(-1, 750, 1000, 1000));
    assertEquals(75, source.read().orElseThrow());
    assertEquals(2, fixture.reads.get());
  }

  @Test
  void heapInput007AllProviderFailuresKeepIdentityWithoutFormattingOrRetry() {
    for (Throwable failure :
        List.of(
            new UnformattableFailure(),
            new NullPointerException(),
            new AssertionError(),
            new OutOfMemoryError("synthetic-test-only-no-allocation"))) {
      var fixture = new Fixture();
      fixture.failure = Optional.of(failure);
      var source = JvmHeapHealthObservation.from(fixture.bean);
      assertEquals(0, fixture.reads.get());
      assertSame(failure, assertThrows(failure.getClass(), source::read));
      assertEquals(1, fixture.reads.get());
    }
  }

  @Test
  void heapInput008ManyBindingsDoNotReadOrMutateAndConcurrentReadsAreExact() throws Exception {
    var fixture = new Fixture();
    var other = new Fixture();
    other.usage = Optional.of(new MemoryUsage(-1, 500, 1000, 1000));
    var source = JvmHeapHealthObservation.from(fixture.bean);
    var otherSource = JvmHeapHealthObservation.from(other.bean);
    assertEquals(0, fixture.reads.get());
    assertEquals(0, other.reads.get());
    assertEquals(50, otherSource.read().orElseThrow());
    assertEquals(0, fixture.reads.get());
    assertEquals(1, other.reads.get());
    var pool = Executors.newFixedThreadPool(8);
    try {
      var jobs =
          java.util.stream.IntStream.range(0, 64)
              .<Callable<Double>>mapToObj(i -> () -> source.read().orElseThrow())
              .toList();
      for (var result : pool.invokeAll(jobs, 10, TimeUnit.SECONDS))
        assertEquals(75, result.get().doubleValue());
    } finally {
      pool.shutdownNow();
      assertTrue(pool.awaitTermination(10, TimeUnit.SECONDS));
    }
    assertEquals(64, fixture.reads.get());
    assertEquals(1, other.reads.get());
    assertEquals(750, fixture.usage.orElseThrow().getUsed());
  }

  @Test
  void heapInput009HeapSnapshotIsIndependentOfCommittedAndLaterProviderValues() {
    var fixture = new Fixture();
    var original = new MemoryUsage(-1, 750, 800, 1000);
    fixture.usage = Optional.of(original);
    var source = JvmHeapHealthObservation.from(fixture.bean);
    var first = source.read();
    fixture.usage = Optional.of(new MemoryUsage(-1, 125, 500, 1000));
    assertEquals(12.5, source.read().orElseThrow());
    assertEquals(75, first.orElseThrow());
    assertEquals(750, original.getUsed());
    assertEquals(800, original.getCommitted());
    assertEquals(1000, original.getMax());
    assertEquals(2, fixture.reads.get());
  }
}
