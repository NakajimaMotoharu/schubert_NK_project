package dev.codex.schubert.nk.batch.monitoring;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.CauseClearance;
import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.Service;
import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.Severity;
import java.time.Clock;
import java.time.Duration;
import java.time.Instant;
import java.time.ZoneId;
import java.util.HashSet;
import java.util.List;
import java.util.Optional;
import java.util.concurrent.Callable;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicLong;
import java.util.function.LongSupplier;
import org.junit.jupiter.api.Test;

/** Independent UTC/ns vectors, no system clock mutation or live source. Spec1586. */
class MonitoringObservationClockTest {
  private static final Instant AT = Instant.parse("2026-10-23T00:00:00Z");

  static final class FixtureClock extends Clock {
    Optional<Instant> at = Optional.of(AT);
    Optional<Throwable> failure = Optional.empty();
    final AtomicInteger reads = new AtomicInteger();

    @Override
    public Instant instant() {
      reads.incrementAndGet();
      if (failure.isPresent()) {
        Throwable value = failure.orElseThrow();
        if (value instanceof Error fatal) throw fatal;
        throw assertInstanceOf(RuntimeException.class, value);
      }
      return at.orElse(null);
    }

    @Override
    public ZoneId getZone() {
      throw new AssertionError("no zone conversion");
    }

    @Override
    public Clock withZone(ZoneId zone) {
      throw new AssertionError("no zone conversion");
    }

    @Override
    public String toString() {
      throw new AssertionError("no source formatting");
    }
  }

  private static final class UnformattableFailure extends IllegalStateException {
    private static final long serialVersionUID = 1L;

    @Override
    public String getMessage() {
      throw new AssertionError("no failure text");
    }

    @Override
    public String toString() {
      throw new AssertionError("no failure formatting");
    }
  }

  @Test
  void obsClock001IndependentNanosAndActualUtcAreNotRebasedOrClamped() {
    var wall = new FixtureClock();
    var ticks = new AtomicLong(100);
    var clock = new MonitoringObservationClock(wall, ticks::get);
    var initial = clock.context(CauseClearance.UNCONFIRMED);
    assertEquals(Duration.ZERO, initial.elapsed());
    assertEquals(AT, initial.at());
    assertEquals(CauseClearance.UNCONFIRMED, initial.clearance());
    ticks.set(102);
    assertEquals(Duration.ofNanos(2), clock.context(CauseClearance.CONFIRMED).elapsed());
    ticks.set(2100);
    wall.at = Optional.of(AT.minusSeconds(3600));
    var backwardUtc = clock.context(CauseClearance.CONFIRMED);
    assertEquals(Duration.ofNanos(2000), backwardUtc.elapsed());
    assertEquals(AT.minusSeconds(3600), backwardUtc.at());
    assertEquals(CauseClearance.CONFIRMED, backwardUtc.clearance());
    assertEquals(Duration.ZERO, initial.elapsed());
    assertEquals(AT, initial.at());
  }

  @Test
  void obsClock002SignedOriginAndRegularLongWrapHaveFiveNanos() {
    for (long[] values :
        List.of(new long[] {-10, -5}, new long[] {Long.MAX_VALUE - 3, Long.MIN_VALUE + 1})) {
      var ticks = new AtomicLong(values[0]);
      var clock = new MonitoringObservationClock(new FixtureClock(), ticks::get);
      ticks.set(values[1]);
      assertEquals(Duration.ofNanos(5), clock.context(CauseClearance.UNCONFIRMED).elapsed());
    }
  }

  @Test
  void obsClock003EpochMaximumAndOverflowHaveExplicitDifferentOutcomes() {
    var wall = new FixtureClock();
    var ticks = new AtomicLong();
    var clock = new MonitoringObservationClock(wall, ticks::get);
    ticks.set(Long.MAX_VALUE);
    var maximum = clock.context(CauseClearance.UNCONFIRMED);
    assertEquals(Duration.ofSeconds(9_223_372_036L, 854_775_807), maximum.elapsed());
    ticks.set(Long.MIN_VALUE);
    var denied =
        assertThrows(IllegalArgumentException.class, () -> clock.context(CauseClearance.CONFIRMED));
    assertEquals("invalid monitoring clock sequence", denied.getMessage());
    assertEquals(1, wall.reads.get());
    ticks.set(Long.MAX_VALUE);
    assertEquals(maximum.elapsed(), clock.context(CauseClearance.UNCONFIRMED).elapsed());
  }

  @Test
  void obsClock004BackwardsTickDoesNotReadUtcCommitOrResetTheEpoch() {
    var wall = new FixtureClock();
    var ticks = new AtomicLong();
    var clock = new MonitoringObservationClock(wall, ticks::get);
    ticks.set(5);
    var first = clock.context(CauseClearance.UNCONFIRMED);
    ticks.set(4);
    assertThrows(IllegalArgumentException.class, () -> clock.context(CauseClearance.CONFIRMED));
    assertEquals(1, wall.reads.get());
    ticks.set(6);
    assertEquals(Duration.ofNanos(6), clock.context(CauseClearance.CONFIRMED).elapsed());
    assertEquals(Duration.ofNanos(5), first.elapsed());
  }

  @Test
  void obsClock005SourceFailuresRemainUnformattedAndDoNotCommitFailedContexts() {
    var wall = new FixtureClock();
    var ticks = new AtomicLong();
    var clock = new MonitoringObservationClock(wall, ticks::get);
    ticks.set(10);
    wall.at = Optional.empty();
    assertThrows(NullPointerException.class, () -> clock.context(CauseClearance.UNCONFIRMED));
    ticks.set(5);
    wall.at = Optional.of(AT);
    assertEquals(Duration.ofNanos(5), clock.context(CauseClearance.UNCONFIRMED).elapsed());
    for (Throwable failure : List.of(new UnformattableFailure(), new AssertionError())) {
      ticks.set(20);
      wall.failure = Optional.of(failure);
      assertSame(
          failure, assertThrows(failure.getClass(), () -> clock.context(CauseClearance.CONFIRMED)));
      ticks.set(6);
      wall.failure = Optional.empty();
      assertEquals(Duration.ofNanos(6), clock.context(CauseClearance.CONFIRMED).elapsed());
      LongSupplier broken =
          () -> {
            if (failure instanceof Error fatal) throw fatal;
            throw assertInstanceOf(RuntimeException.class, failure);
          };
      assertSame(
          failure,
          assertThrows(failure.getClass(), () -> new MonitoringObservationClock(wall, broken)));
      var armed = new AtomicInteger();
      var source =
          new MonitoringObservationClock(
              wall,
              () -> {
                if (armed.getAndIncrement() == 0) return 0;
                if (failure instanceof Error fatal) throw fatal;
                throw assertInstanceOf(RuntimeException.class, failure);
              });
      int readBefore = wall.reads.get();
      assertSame(
          failure,
          assertThrows(failure.getClass(), () -> source.context(CauseClearance.UNCONFIRMED)));
      assertEquals(readBefore, wall.reads.get());
    }
  }

  @Test
  void obsClock006NullContractsDoNotTouchProvidersAndSnapshotsStayImmutable() {
    var calls = new AtomicInteger();
    var wall = new FixtureClock();
    LongSupplier ticks = () -> calls.getAndIncrement();
    assertThrows(NullPointerException.class, () -> new MonitoringObservationClock(null, ticks));
    assertThrows(NullPointerException.class, () -> new MonitoringObservationClock(wall, null));
    assertEquals(0, calls.get());
    var clock = new MonitoringObservationClock(wall, ticks);
    assertEquals(1, calls.get());
    assertThrows(NullPointerException.class, () -> clock.context(null));
    assertEquals(1, calls.get());
    assertEquals(0, wall.reads.get());
    var snapshot = clock.context(CauseClearance.UNCONFIRMED);
    wall.at = Optional.of(AT.plusSeconds(500));
    var next = clock.context(CauseClearance.CONFIRMED);
    assertEquals(Duration.ofNanos(1), snapshot.elapsed());
    assertEquals(AT, snapshot.at());
    assertEquals(Duration.ofNanos(2), next.elapsed());
    assertEquals(AT.plusSeconds(500), next.at());
  }

  @Test
  void obsClock007ConcurrentContextsHaveUniqueMonotonicSnapshots()
      throws InterruptedException, ExecutionException {
    var wall = new FixtureClock();
    var ticks = new AtomicLong();
    var clock = new MonitoringObservationClock(wall, ticks::getAndIncrement);
    var actual = new HashSet<Duration>();
    var pool = Executors.newFixedThreadPool(8);
    try {
      var jobs =
          java.util.stream.IntStream.range(0, 64)
              .<Callable<ObservationContext>>mapToObj(
                  i -> () -> clock.context(CauseClearance.UNCONFIRMED))
              .toList();
      for (var result : pool.invokeAll(jobs, 10, TimeUnit.SECONDS)) {
        var context = result.get();
        assertEquals(AT, context.at());
        assertTrue(actual.add(context.elapsed()));
      }
    } finally {
      pool.shutdownNow();
      assertTrue(pool.awaitTermination(10, TimeUnit.SECONDS));
    }
    var expected = new HashSet<Duration>();
    for (int i = 1; i <= 64; i++) expected.add(Duration.ofNanos(i));
    assertEquals(expected, actual);
    assertEquals(65, ticks.get());
    assertEquals(64, wall.reads.get());
  }

  @Test
  void obsClock008HealthConnectionBreaksClockAndUncheckedInputGapsAcrossBothApis() {
    for (Throwable failure :
        List.of(new UnformattableFailure(), new AssertionError(), new NullPointerException()))
      for (boolean clockFault : List.of(false, true)) {
        var store = new FilesystemHealthObservationTest.FixtureStore();
        store.usable = 100;
        var wall = new FixtureClock();
        var ticks = new AtomicLong();
        var clock = new MonitoringObservationClock(wall, ticks::get);
        var monitor = new FilesystemHealthMonitor(store, Service.WEB);
        assertThrows(NullPointerException.class, () -> monitor.observeNow(true, null, clock));
        assertThrows(
            NullPointerException.class,
            () -> monitor.observeNow(true, CauseClearance.CONFIRMED, null));
        assertEquals(0, store.totalReads.get());
        assertTrue(monitor.observeNow(false, CauseClearance.UNCONFIRMED, clock).event().isEmpty());
        ticks.set(60_000_000_000L);
        wall.at = Optional.of(AT.minusSeconds(3600));
        var event =
            monitor.observeNow(true, CauseClearance.UNCONFIRMED, clock).event().orElseThrow();
        assertEquals(Severity.CRITICAL, event.severity());
        assertEquals(AT.minusSeconds(3600), event.firstSeen());
        store.usable = 1000;
        ticks.set(61_000_000_000L);
        assertTrue(
            monitor
                .observeNow(true, CauseClearance.CONFIRMED, clock)
                .event()
                .orElseThrow()
                .isOpen());
        var before = monitor.snapshot();
        int reads = store.totalReads.get();
        ticks.set(661_000_000_000L);
        if (clockFault) wall.failure = Optional.of(failure);
        else store.fault = Optional.of(failure);
        assertSame(
            failure,
            assertThrows(
                failure.getClass(),
                () -> monitor.observeNow(true, CauseClearance.CONFIRMED, clock)));
        assertEquals(before, monitor.snapshot());
        assertEquals(reads + (clockFault ? 0 : 1), store.totalReads.get());
        wall.failure = Optional.empty();
        store.fault = Optional.empty();
        ticks.set(662_000_000_000L);
        var recovered =
            clockFault
                ? monitor.observeNow(true, CauseClearance.CONFIRMED, clock)
                : monitor.observe(
                    true,
                    new ObservationContext(CauseClearance.CONFIRMED, AT, Duration.ofSeconds(662)));
        assertTrue(recovered.event().orElseThrow().isOpen());
        assertTrue(
            monitor
                .observe(
                    true,
                    new ObservationContext(CauseClearance.CONFIRMED, AT, Duration.ofSeconds(1261)))
                .event()
                .orElseThrow()
                .isOpen());
        assertFalse(
            monitor
                .observe(
                    true,
                    new ObservationContext(CauseClearance.CONFIRMED, AT, Duration.ofSeconds(1262)))
                .event()
                .orElseThrow()
                .isOpen());
        assertTrue(monitor.snapshot().isEmpty());
      }
  }
}
