package dev.codex.schubert.nk.api.bootstrap;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicLong;
import org.junit.jupiter.api.Test;

/** 1870/APISTOP001..020: literal arithmetic and own finite clock ports, no runtime hooks/TERM. */
final class ApiStopBudgetTest {
  private static final String FIXTURE_CLOCK_49F3C56E = "clock";

  private static final class Fixture {
    final AtomicLong now = new AtomicLong();
    final AtomicInteger reads = new AtomicInteger();
    volatile Throwable failure;
    volatile Runnable beforeTime = () -> {};
    final ApiStopBudget budget =
        new ApiStopBudget(
            () -> {
              reads.incrementAndGet();
              beforeTime.run();
              if (failure instanceof RuntimeException runtime) throw runtime;
              if (failure instanceof Error fatal) throw fatal;
              assertNull(failure);
              return now.get();
            });
  }

  private static void await(CountDownLatch latch) {
    try {
      assertTrue(latch.await(10, TimeUnit.SECONDS));
    } catch (InterruptedException interrupted) {
      Thread.currentThread().interrupt();
      throw new AssertionError(interrupted);
    }
  }

  @Test
  void apiStop019AtomicClaimPublishesStopAndWaitsForTheFirstClock() throws Exception {
    var f = new Fixture();
    f.now.set(37);
    var entered = new CountDownLatch(1);
    var release = new CountDownLatch(1);
    f.beforeTime =
        () -> {
          if (f.reads.get() == 1) {
            entered.countDown();
            await(release);
          }
        };
    assertFalse(f.budget.stopping());
    try (var executor = Executors.newFixedThreadPool(2)) {
      var first = executor.submit(f.budget::begin);
      Future<Long> remaining;
      try {
        await(entered);
        assertTrue(f.budget.stopping());
        remaining = executor.submit(f.budget::remainingNanos);
        assertThrows(TimeoutException.class, () -> remaining.get(50, TimeUnit.MILLISECONDS));
        assertEquals(1, f.reads.get());
      } finally {
        release.countDown();
      }
      first.get(10, TimeUnit.SECONDS);
      assertEquals(60_000_000_000L, remaining.get(10, TimeUnit.SECONDS));
      assertEquals(2, f.reads.get());
      assertTrue(f.budget.stopping());
    }
  }

  @Test
  void apiStop020FailedFirstClockKeepsThePublishedStopAndExhaustedBudget() {
    var f = new Fixture();
    var failure = new IllegalStateException(FIXTURE_CLOCK_49F3C56E);
    f.failure = failure;
    assertFalse(f.budget.stopping());
    assertSame(failure, assertThrows(IllegalStateException.class, f.budget::begin));
    assertTrue(f.budget.stopping());
    f.failure = null;
    f.budget.begin();
    assertEquals(0, f.budget.remainingNanos());
    assertEquals(1, f.reads.get());
  }

  @Test
  void apiStop001() {
    assertThrows(NullPointerException.class, () -> new ApiStopBudget(null));
  }

  @Test
  void apiStop002() {
    var f = new Fixture();
    assertEquals(0, f.reads.get());
  }

  @Test
  void apiStop003() {
    var f = new Fixture();
    assertEquals(
        "API stop budget not begun",
        assertThrows(IllegalStateException.class, f.budget::remainingNanos).getMessage());
    assertEquals(0, f.reads.get());
  }

  @Test
  void apiStop004() {
    var f = new Fixture();
    f.now.set(7);
    f.budget.begin();
    assertEquals(60_000_000_000L, f.budget.remainingNanos());
    assertEquals(2, f.reads.get());
  }

  @Test
  void apiStop005() {
    var f = new Fixture();
    f.budget.begin();
    f.now.set(9);
    f.budget.begin();
    assertEquals(1, f.reads.get());
    assertEquals(59_999_999_991L, f.budget.remainingNanos());
    assertEquals(2, f.reads.get());
  }

  @Test
  void apiStop006() {
    var f = new Fixture();
    f.budget.begin();
    long[][] vectors = {
      {0, 60_000_000_000L},
      {1, 59_999_999_999L},
      {1_000_000_000L, 59_000_000_000L},
      {59_999_999_999L, 1}
    };
    for (long[] vector : vectors) {
      f.now.set(vector[0]);
      assertEquals(vector[1], f.budget.remainingNanos());
    }
  }

  @Test
  void apiStop007() {
    var f = new Fixture();
    f.budget.begin();
    f.now.set(60_000_000_000L);
    assertEquals(0, f.budget.remainingNanos());
    f.now.set(0);
    assertEquals(0, f.budget.remainingNanos());
    assertEquals(2, f.reads.get());
  }

  @Test
  void apiStop008() {
    for (long value : new long[] {60_000_000_001L, Long.MAX_VALUE}) {
      var f = new Fixture();
      f.budget.begin();
      f.now.set(value);
      assertEquals(0, f.budget.remainingNanos());
      assertEquals(2, f.reads.get());
    }
  }

  @Test
  void apiStop009() {
    var f = new Fixture();
    f.now.set(100);
    f.budget.begin();
    f.now.set(99);
    assertEquals(0, f.budget.remainingNanos());
    f.now.set(101);
    assertEquals(0, f.budget.remainingNanos());
    assertEquals(2, f.reads.get());
  }

  @Test
  void apiStop010() {
    var f = new Fixture();
    f.now.set(Long.MAX_VALUE - 10);
    f.budget.begin();
    f.now.set(Long.MIN_VALUE + 9);
    assertEquals(59_999_999_980L, f.budget.remainingNanos());
    assertEquals(2, f.reads.get());
  }

  @Test
  void apiStop011() {
    var f = new Fixture();
    var primary = new IllegalStateException(FIXTURE_CLOCK_49F3C56E);
    f.failure = primary;
    assertSame(primary, assertThrows(IllegalStateException.class, f.budget::begin));
    f.failure = null;
    f.budget.begin();
    assertEquals(0, f.budget.remainingNanos());
    assertEquals(1, f.reads.get());
  }

  @Test
  void apiStop012() {
    var f = new Fixture();
    var fatal = new AssertionError(FIXTURE_CLOCK_49F3C56E);
    f.failure = fatal;
    assertSame(fatal, assertThrows(AssertionError.class, f.budget::begin));
    f.failure = null;
    f.budget.begin();
    assertEquals(0, f.budget.remainingNanos());
    assertEquals(1, f.reads.get());
  }

  @Test
  void apiStop013() {
    var f = new Fixture();
    f.budget.begin();
    var primary = new IllegalStateException(FIXTURE_CLOCK_49F3C56E);
    f.failure = primary;
    assertSame(primary, assertThrows(IllegalStateException.class, f.budget::remainingNanos));
    f.failure = null;
    assertEquals(0, f.budget.remainingNanos());
    assertEquals(2, f.reads.get());
  }

  @Test
  void apiStop014() {
    var f = new Fixture();
    f.budget.begin();
    var fatal = new AssertionError(FIXTURE_CLOCK_49F3C56E);
    f.failure = fatal;
    assertSame(fatal, assertThrows(AssertionError.class, f.budget::remainingNanos));
    f.failure = null;
    assertEquals(0, f.budget.remainingNanos());
    assertEquals(2, f.reads.get());
  }

  @Test
  void apiStop015() throws Exception {
    var f = new Fixture();
    var entered = new CountDownLatch(1);
    var release = new CountDownLatch(1);
    f.beforeTime =
        () -> {
          entered.countDown();
          await(release);
        };
    try (var executor = Executors.newFixedThreadPool(2)) {
      var first = executor.submit(f.budget::begin);
      Future<?> second;
      try {
        await(entered);
        second = executor.submit(f.budget::begin);
        assertEquals(1, f.reads.get());
      } finally {
        release.countDown();
      }
      first.get(10, TimeUnit.SECONDS);
      second.get(10, TimeUnit.SECONDS);
      assertEquals(1, f.reads.get());
      f.beforeTime = () -> {};
      assertEquals(60_000_000_000L, f.budget.remainingNanos());
    }
  }

  @Test
  void apiStop016() throws Exception {
    var f = new Fixture();
    f.budget.begin();
    try (var executor = Executors.newFixedThreadPool(4)) {
      List<Future<Long>> values = new ArrayList<>();
      for (int i = 0; i < 8; i++) values.add(executor.submit(f.budget::remainingNanos));
      for (var value : values) assertEquals(60_000_000_000L, value.get(10, TimeUnit.SECONDS));
    }
    assertEquals(9, f.reads.get());
  }

  @Test
  void apiStop017() {
    var f = new Fixture();
    f.now.set(Long.MIN_VALUE);
    f.budget.begin();
    f.now.set(0);
    assertEquals(0, f.budget.remainingNanos());
    assertEquals(2, f.reads.get());
  }

  @Test
  void apiStop018() {
    var f = new Fixture();
    f.budget.begin();
    f.now.set(60_000_000_001L);
    assertEquals(0, f.budget.remainingNanos());
    f.now.set(0);
    f.failure = new AssertionError("must not read after expiry");
    f.budget.begin();
    assertEquals(0, f.budget.remainingNanos());
    assertEquals(2, f.reads.get());
  }
}
