package dev.codex.schubert.nk.batch.monitoring;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.CauseClearance;
import java.time.Duration;
import java.time.Instant;
import java.util.HashSet;
import java.util.List;
import java.util.Optional;
import java.util.concurrent.Callable;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicLong;
import java.util.function.BiFunction;
import org.junit.jupiter.api.Test;

/** Independent action/count/epoch contracts; callback result does not generate its own expected. */
class MonitoringPollerTest {
  private static final Instant BASE_INSTANT = Instant.parse("2026-10-23T00:00:00Z");

  private static ObservationContext at(long seconds) {
    return new ObservationContext(
        CauseClearance.UNCONFIRMED, BASE_INSTANT, Duration.ofSeconds(seconds));
  }

  private static void fail(Throwable failure) {
    if (failure instanceof Error fatal) throw fatal;
    throw (RuntimeException) failure;
  }

  @Test
  void poll001NormalFlagsContextAndResultHaveNoRetries() {
    var poll = new MonitoringPoller<Integer>();
    var calls = new AtomicInteger();
    var context = at(0);
    assertEquals(
        17,
        poll.observe(
            true,
            context,
            (consecutive, observed) -> {
              assertTrue(consecutive);
              assertSame(context, observed);
              calls.incrementAndGet();
              return 17;
            }));
    assertEquals(
        23,
        poll.observe(
            false,
            at(1),
            (consecutive, observed) -> {
              assertFalse(consecutive);
              assertEquals(Duration.ofSeconds(1), observed.elapsed());
              calls.incrementAndGet();
              return 23;
            }));
    assertEquals(2, calls.get());
  }

  @Test
  void poll002EveryUncheckedFailureRemainsIdenticalAndCutsNextContinuity() {
    for (Throwable failure :
        List.of(new IllegalStateException(), new NullPointerException(), new AssertionError())) {
      var poll = new MonitoringPoller<Integer>();
      var calls = new AtomicInteger();
      poll.observe(true, at(0), (continuous, context) -> 1);
      assertSame(
          failure,
          assertThrows(
              failure.getClass(),
              () ->
                  poll.observe(
                      true,
                      at(10),
                      (continuous, context) -> {
                        calls.incrementAndGet();
                        fail(failure);
                        return 0;
                      })));
      assertEquals(1, calls.get());
      assertEquals(
          7,
          poll.observe(
              true,
              at(5),
              (continuous, context) -> {
                assertFalse(continuous);
                return 7;
              }));
    }
  }

  @Test
  void poll003BackwardsContextIsRejectedBeforeActionAndDoesNotInventGap() {
    var poll = new MonitoringPoller<Integer>();
    var calls = new AtomicInteger();
    BiFunction<Boolean, ObservationContext, Integer> action =
        (continuous, context) -> {
          assertTrue(continuous);
          return calls.incrementAndGet();
        };
    assertEquals(1, poll.observe(true, at(5), action));
    assertThrows(IllegalArgumentException.class, () -> poll.observe(true, at(4), action));
    assertEquals(1, calls.get());
    assertEquals(2, poll.observe(true, at(6), action));
    assertEquals(3, poll.observe(true, at(6), action));
  }

  @Test
  void poll004ClockFailureHasNoActionAndCrossApiGapIsConsumed() {
    for (Throwable failure : List.of(new IllegalStateException(), new AssertionError())) {
      var wall = new MonitoringObservationClockTest.FixtureClock();
      var ticks = new AtomicLong();
      var clock = new MonitoringObservationClock(wall, ticks::get);
      var poll = new MonitoringPoller<Integer>();
      var calls = new AtomicInteger();
      wall.failure = Optional.of(failure);
      assertSame(
          failure,
          assertThrows(
              failure.getClass(),
              () ->
                  poll.observeNow(
                      true,
                      CauseClearance.CONFIRMED,
                      clock,
                      (continuous, context) -> calls.incrementAndGet())));
      assertEquals(0, calls.get());
      wall.failure = Optional.empty();
      poll.observe(
          true,
          at(0),
          (continuous, context) -> {
            assertFalse(continuous);
            return 1;
          });
      ticks.set(1_000_000_000);
      poll.observeNow(
          true,
          CauseClearance.CONFIRMED,
          clock,
          (continuous, context) -> {
            assertTrue(continuous);
            assertEquals(Duration.ofSeconds(1), context.elapsed());
            return 2;
          });
    }
  }

  @Test
  void poll005NullBoundariesDoNotCallOrChangeContinuity() {
    var poll = new MonitoringPoller<Integer>();
    var calls = new AtomicInteger();
    var clock =
        new MonitoringObservationClock(new MonitoringObservationClockTest.FixtureClock(), () -> 0);
    BiFunction<Boolean, ObservationContext, Integer> action =
        (continuous, context) -> {
          assertTrue(continuous);
          return calls.incrementAndGet();
        };
    assertThrows(NullPointerException.class, () -> poll.observe(true, null, action));
    assertThrows(NullPointerException.class, () -> poll.observe(true, at(0), null));
    assertThrows(NullPointerException.class, () -> poll.observeNow(true, null, clock, action));
    assertThrows(
        NullPointerException.class,
        () -> poll.observeNow(true, CauseClearance.CONFIRMED, null, action));
    assertThrows(
        NullPointerException.class,
        () -> poll.observeNow(true, CauseClearance.CONFIRMED, clock, null));
    assertEquals(0, calls.get());
    assertEquals(1, poll.observe(true, at(0), action));
  }

  @Test
  void poll006NullResultIsFailureAndDoesNotCommitLaterEpoch() {
    var poll = new MonitoringPoller<Integer>();
    assertEquals(1, poll.observe(true, at(0), (continuous, context) -> 1));
    assertThrows(
        NullPointerException.class,
        () -> poll.observe(true, at(10), (continuous, context) -> null));
    assertEquals(
        2,
        poll.observe(
            true,
            at(5),
            (continuous, context) -> {
              assertFalse(continuous);
              return 2;
            }));
  }

  @Test
  void poll007ParallelNonAtomicActionsAreSerializedIntoOneToSixtyFour() throws Exception {
    var poll = new MonitoringPoller<Integer>();
    int[] count = {0};
    var actual = new HashSet<Integer>();
    var pool = Executors.newFixedThreadPool(8);
    try {
      var jobs =
          java.util.stream.IntStream.range(0, 64)
              .<Callable<Integer>>mapToObj(
                  i -> () -> poll.observe(true, at(1), (continuous, context) -> ++count[0]))
              .toList();
      for (var result : pool.invokeAll(jobs, 10, TimeUnit.SECONDS))
        assertTrue(actual.add(result.get()));
    } finally {
      pool.shutdownNow();
      assertTrue(pool.awaitTermination(10, TimeUnit.SECONDS));
    }
    var expected = new HashSet<Integer>();
    for (int i = 1; i <= 64; i++) expected.add(i);
    assertEquals(expected, actual);
    assertEquals(64, count[0]);
  }

  @Test
  void poll008ActionFailureThenClockPathRecoversAfterOneGapOnly() {
    var wall = new MonitoringObservationClockTest.FixtureClock();
    var ticks = new AtomicLong();
    var clock = new MonitoringObservationClock(wall, ticks::get);
    var poll = new MonitoringPoller<Integer>();
    var failure = new IllegalArgumentException();
    assertSame(
        failure,
        assertThrows(
            IllegalArgumentException.class,
            () ->
                poll.observe(
                    false,
                    at(0),
                    (continuous, context) -> {
                      throw failure;
                    })));
    poll.observeNow(
        true,
        CauseClearance.CONFIRMED,
        clock,
        (continuous, context) -> {
          assertFalse(continuous);
          return 1;
        });
    ticks.set(1);
    poll.observeNow(
        true,
        CauseClearance.CONFIRMED,
        clock,
        (continuous, context) -> {
          assertTrue(continuous);
          return 2;
        });
    assertThrows(
        IllegalArgumentException.class,
        () ->
            poll.observeNow(
                true,
                CauseClearance.CONFIRMED,
                clock,
                (continuous, context) -> {
                  throw failure;
                }));
    poll.observeNow(
        false,
        CauseClearance.CONFIRMED,
        clock,
        (continuous, context) -> {
          assertFalse(continuous);
          return 3;
        });
  }
}
