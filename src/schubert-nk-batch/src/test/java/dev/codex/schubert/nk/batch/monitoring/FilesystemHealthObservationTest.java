package dev.codex.schubert.nk.batch.monitoring;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.CauseClearance;
import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.Service;
import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.Severity;
import java.io.IOException;
import java.math.BigInteger;
import java.nio.file.FileStore;
import java.nio.file.attribute.FileAttributeView;
import java.nio.file.attribute.FileStoreAttributeView;
import java.time.Duration;
import java.time.Instant;
import java.util.List;
import java.util.Optional;
import java.util.concurrent.Callable;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.Test;

/** Fixed independent byte/IEEE vectors and caller-owned store, not a production filesystem. */
class FilesystemHealthObservationTest {
  private static final Instant AT = Instant.parse("2026-10-23T00:00:00Z");

  static final class FixtureStore extends FileStore {
    long total = 1000;
    long usable = 200;
    boolean failTotal;
    Optional<Throwable> fault = Optional.empty();
    final AtomicInteger totalReads = new AtomicInteger();
    final AtomicInteger usableReads = new AtomicInteger();

    private void inject() throws IOException {
      if (fault.isEmpty()) return;
      Throwable failure = fault.orElseThrow();
      if (failure instanceof IOException checked) throw checked;
      if (failure instanceof Error fatal) throw fatal;
      throw (RuntimeException) failure;
    }

    @Override
    public long getTotalSpace() throws IOException {
      totalReads.incrementAndGet();
      if (failTotal) inject();
      return total;
    }

    @Override
    public long getUsableSpace() throws IOException {
      usableReads.incrementAndGet();
      if (!failTotal) inject();
      return usable;
    }

    @Override
    public String name() {
      throw new AssertionError("no filesystem identity read");
    }

    @Override
    public String type() {
      throw new AssertionError("no filesystem type read");
    }

    @Override
    public boolean isReadOnly() {
      throw new AssertionError("no filesystem authority read");
    }

    @Override
    public long getUnallocatedSpace() {
      throw new AssertionError("must use caller-usable bytes");
    }

    @Override
    public boolean supportsFileAttributeView(Class<? extends FileAttributeView> type) {
      throw new AssertionError("no attribute read");
    }

    @Override
    public boolean supportsFileAttributeView(String type) {
      throw new AssertionError("no attribute read");
    }

    @Override
    public <V extends FileStoreAttributeView> V getFileStoreAttributeView(Class<V> type) {
      throw new AssertionError("no attribute view");
    }

    @Override
    public Object getAttribute(String name) {
      throw new AssertionError("no attribute read");
    }

    @Override
    public String toString() {
      throw new AssertionError("no path/identity formatting");
    }
  }

  private static final class UnformattableIOException extends IOException {
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

  private static ObservationContext context(long seconds, CauseClearance clearance) {
    return new ObservationContext(clearance, AT.plusSeconds(seconds), Duration.ofSeconds(seconds));
  }

  @Test
  void fsInput001FixedIndependentByteTableReadsExactlyTwoValues() {
    var store = new FixtureStore();
    var source = new FilesystemHealthObservation(store);
    long[] free = {1000, 200, 100, 0};
    double[] expected = {0, 80, 90, 100};
    for (int i = 0; i < free.length; i++) {
      store.usable = free[i];
      assertEquals(expected[i], source.read().orElseThrow());
    }
    assertEquals(4, store.totalReads.get());
    assertEquals(4, store.usableReads.get());
  }

  @Test
  void fsInput002InvalidValuesAreUnknownWithoutClampingOrStickyFailure() {
    var store = new FixtureStore();
    var source = new FilesystemHealthObservation(store);
    for (long[] row :
        List.of(
            new long[] {0, 0},
            new long[] {-1, 0},
            new long[] {1000, -1},
            new long[] {1000, 1001})) {
      store.total = row[0];
      store.usable = row[1];
      assertTrue(source.read().isEmpty());
    }
    store.total = 1000;
    store.usable = 200;
    assertEquals(80, source.read().orElseThrow());
  }

  @Test
  void fsInput003CheckedIoFailureIsUnknownAndNeverFormattedOrRetried() {
    for (boolean first : List.of(false, true)) {
      var store = new FixtureStore();
      store.failTotal = first;
      store.fault = Optional.of(new UnformattableIOException());
      assertTrue(new FilesystemHealthObservation(store).read().isEmpty());
      assertEquals(1, store.totalReads.get());
      assertEquals(first ? 0 : 1, store.usableReads.get());
    }
  }

  @Test
  void fsInput004UncheckedAndFatalRemainTheSameFailureNotNormalData() {
    for (boolean first : List.of(false, true))
      for (Throwable failure :
          List.of(new IllegalStateException(), new NullPointerException(), new AssertionError())) {
        var store = new FixtureStore();
        store.failTotal = first;
        store.fault = Optional.of(failure);
        var source = new FilesystemHealthObservation(store);
        assertSame(failure, assertThrows(failure.getClass(), source::read));
        assertEquals(1, store.totalReads.get());
        assertEquals(first ? 0 : 1, store.usableReads.get());
      }
  }

  @Test
  void fsInput005MaximumAndSingleByteTotalsDoNotOverflow() {
    var store = new FixtureStore();
    var source = new FilesystemHealthObservation(store);
    for (long total : new long[] {1, Long.MAX_VALUE}) {
      store.total = total;
      store.usable = total;
      assertEquals(0, source.read().orElseThrow());
      store.usable = 0;
      assertEquals(100, source.read().orElseThrow());
    }
  }

  @Test
  void fsInput006OneByteBeforeIntegerThresholdNeverRoundsUpAcrossIt() {
    var store = new FixtureStore();
    store.total = 1_000_000_000_000_000_000L;
    var source = new FilesystemHealthObservation(store);
    long[] exactUsable = {
      200_000_000_000_000_000L, 100_000_000_000_000_000L, 50_000_000_000_000_000L
    };
    long[] beforeBits = {0x4053ffffffffffffL, 0x40567fffffffffffL, 0x4057bfffffffffffL};
    double[] threshold = {80, 90, 95};
    for (int i = 0; i < threshold.length; i++) {
      store.usable = exactUsable[i] + 1;
      double below = source.read().orElseThrow();
      assertEquals(Double.longBitsToDouble(beforeBits[i]), below);
      assertTrue(below < threshold[i]);
      store.usable = exactUsable[i];
      assertEquals(threshold[i], source.read().orElseThrow());
      store.usable = exactUsable[i] - 1;
      assertTrue(source.read().orElseThrow() >= threshold[i]);
    }
  }

  @Test
  void fsInput007NullAndConcurrentIndependentReadsDoNotAcquireOwnership()
      throws InterruptedException, ExecutionException {
    assertThrows(NullPointerException.class, () -> new FilesystemHealthObservation(null));
    var store = new FixtureStore();
    var source = new FilesystemHealthObservation(store);
    var pool = Executors.newFixedThreadPool(8);
    try {
      var jobs =
          java.util.stream.IntStream.range(0, 64)
              .<Callable<Double>>mapToObj(i -> () -> source.read().orElseThrow())
              .toList();
      for (var result : pool.invokeAll(jobs, 10, TimeUnit.SECONDS)) assertEquals(80, result.get());
    } finally {
      pool.shutdownNow();
      assertTrue(pool.awaitTermination(10, TimeUnit.SECONDS));
    }
    assertEquals(64, store.totalReads.get());
    assertEquals(64, store.usableReads.get());
    assertEquals(1000, store.total);
    assertEquals(200, store.usable);
  }

  @Test
  void fsInput008ActualObservationPortDrivesWarningAndCriticalBoundaries() {
    for (long free : new long[] {200, 100}) {
      var store = new FixtureStore();
      store.usable = free;
      var monitor = new FilesystemHealthMonitor(store, Service.BATCH);
      assertTrue(monitor.snapshot().isEmpty());
      assertTrue(monitor.observe(false, context(0, CauseClearance.UNCONFIRMED)).event().isEmpty());
      long boundary = free == 200 ? 300 : 60;
      assertTrue(
          monitor
              .observe(true, context(boundary - 1, CauseClearance.UNCONFIRMED))
              .event()
              .isEmpty());
      var observed = monitor.observe(true, context(boundary, CauseClearance.UNCONFIRMED));
      assertTrue(observed.suppliedValuePresent());
      var event = observed.event().orElseThrow();
      assertEquals(free == 200 ? Severity.WARNING : Severity.CRITICAL, event.severity());
      assertEquals(BigInteger.ONE, event.count());
      assertEquals(Service.BATCH, event.service());
      assertEquals(AT.plusSeconds(boundary), event.firstSeen());
      assertEquals(event, monitor.snapshot().orElseThrow());
    }
  }

  @Test
  void fsInput009MissingIoAndInvalidStatsBreakRecoveryRatherThanClosingAlert() {
    for (boolean invalid : List.of(false, true)) {
      var store = new FixtureStore();
      store.usable = 100;
      var monitor = new FilesystemHealthMonitor(store, Service.WEB);
      monitor.observe(false, context(0, CauseClearance.UNCONFIRMED));
      var open =
          monitor.observe(true, context(60, CauseClearance.UNCONFIRMED)).event().orElseThrow();
      store.usable = 1000;
      assertTrue(
          monitor
              .observe(true, context(61, CauseClearance.CONFIRMED))
              .event()
              .orElseThrow()
              .isOpen());
      if (invalid) store.total = 0;
      else store.fault = Optional.of(new UnformattableIOException());
      var missing = monitor.observe(true, context(661, CauseClearance.CONFIRMED));
      assertFalse(missing.suppliedValuePresent());
      assertEquals(open.count(), missing.event().orElseThrow().count());
      assertTrue(missing.event().orElseThrow().isOpen());
      store.total = 1000;
      store.fault = Optional.empty();
      assertTrue(
          monitor
              .observe(true, context(662, CauseClearance.CONFIRMED))
              .event()
              .orElseThrow()
              .isOpen());
      assertTrue(
          monitor
              .observe(true, context(1261, CauseClearance.CONFIRMED))
              .event()
              .orElseThrow()
              .isOpen());
      assertFalse(
          monitor
              .observe(true, context(1262, CauseClearance.CONFIRMED))
              .event()
              .orElseThrow()
              .isOpen());
      assertTrue(monitor.snapshot().isEmpty());
    }
  }

  @Test
  void fsInput010NullBackwardsGapAndConcurrentPollHaveOneSerializedOwner()
      throws InterruptedException, ExecutionException {
    var store = new FixtureStore();
    store.usable = 100;
    assertThrows(NullPointerException.class, () -> new FilesystemHealthMonitor(null, Service.WEB));
    assertThrows(NullPointerException.class, () -> new FilesystemHealthMonitor(store, null));
    var monitor = new FilesystemHealthMonitor(store, Service.WEB);
    assertThrows(NullPointerException.class, () -> monitor.observe(true, null));
    assertEquals(0, store.totalReads.get());
    monitor.observe(false, context(0, CauseClearance.UNCONFIRMED));
    assertTrue(monitor.observe(false, context(60, CauseClearance.UNCONFIRMED)).event().isEmpty());
    var event =
        monitor.observe(true, context(120, CauseClearance.UNCONFIRMED)).event().orElseThrow();
    assertThrows(
        IllegalArgumentException.class,
        () -> monitor.observe(true, context(119, CauseClearance.CONFIRMED)));
    assertEquals(event, monitor.snapshot().orElseThrow());
    var pool = Executors.newFixedThreadPool(8);
    try {
      var jobs =
          java.util.stream.IntStream.range(0, 64)
              .<Callable<Severity>>mapToObj(
                  i ->
                      () ->
                          monitor
                              .observe(true, context(120, CauseClearance.UNCONFIRMED))
                              .event()
                              .orElseThrow()
                              .severity())
              .toList();
      for (var result : pool.invokeAll(jobs, 10, TimeUnit.SECONDS))
        assertEquals(Severity.CRITICAL, result.get());
    } finally {
      pool.shutdownNow();
      assertTrue(pool.awaitTermination(10, TimeUnit.SECONDS));
    }
    assertEquals(BigInteger.valueOf(65), monitor.snapshot().orElseThrow().count());
  }
}
