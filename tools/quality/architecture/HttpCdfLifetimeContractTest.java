package dev.codex.schubert.nk.web.monitoring;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;

import io.micrometer.core.instrument.MockClock;
import io.micrometer.core.instrument.Timer;
import java.math.BigDecimal;
import java.time.Duration;
import java.util.ArrayList;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Test;

/** HTTPCDF001..003/1755: provider-only fixture, never an actual HTTP request or clock authority. */
class HttpCdfLifetimeContractTest {
  private static Timer timer(OverflowSafeHttpMeterRegistry registry) {
    return Timer.builder("nk_http_request_duration_seconds")
        .publishPercentiles()
        .serviceLevelObjectives(
            Duration.ofMillis(50),
            Duration.ofMillis(100),
            Duration.ofMillis(250),
            Duration.ofMillis(500),
            Duration.ofSeconds(1),
            Duration.ofMillis(1500),
            Duration.ofSeconds(2),
            Duration.ofMillis(2500),
            Duration.ofSeconds(5))
        .distributionStatisticExpiry(Duration.ofSeconds(1))
        .distributionStatisticBufferLength(2)
        .register(registry);
  }

  private static void cdf(
      Timer timer, long count, double total, double tolerance, long... expected) {
    var snapshot = timer.takeSnapshot();
    assertEquals(count, snapshot.count());
    assertEquals(total, snapshot.total(TimeUnit.SECONDS), tolerance);
    var counts = snapshot.histogramCounts();
    long[] bounds = {
      50_000_000,
      100_000_000,
      250_000_000,
      500_000_000,
      1_000_000_000,
      1_500_000_000,
      2_000_000_000,
      2_500_000_000L,
      5_000_000_000L
    };
    assertEquals(9, counts.length);
    assertEquals(9, expected.length);
    for (int index = 0; index < 9; index++) {
      assertEquals((double) bounds[index], counts[index].bucket());
      assertEquals((double) expected[index], counts[index].count());
    }
  }

  @Test
  void httpcdf001LifetimeCdfSurvivesCompleteWindowExpiryAndTwoMaximumSamples() {
    var clock = new MockClock();
    try (var registry = new OverflowSafeHttpMeterRegistry(clock)) {
      var timer = timer(registry);
      for (long ns :
          new long[] {0, 1, 50_000_000, 50_000_001, 5_000_000_000L, Long.MAX_VALUE, Long.MAX_VALUE})
        timer.record(ns, TimeUnit.NANOSECONDS);
      double expected = new BigDecimal("18446744078809551616").movePointLeft(9).doubleValue();
      cdf(timer, 7, expected, .000008, 3, 4, 4, 4, 4, 4, 4, 4, 5);
      clock.add(Duration.ofSeconds(3));
      assertEquals(0, timer.max(TimeUnit.NANOSECONDS));
      cdf(timer, 7, expected, .000008, 3, 4, 4, 4, 4, 4, 4, 4, 5);
      timer.record(1, TimeUnit.NANOSECONDS);
      clock.add(Duration.ofDays(100));
      double next = new BigDecimal("18446744078809551617").movePointLeft(9).doubleValue();
      cdf(timer, 8, next, .000008, 4, 5, 5, 5, 5, 5, 5, 5, 6);
      assertEquals(0, timer.max(TimeUnit.NANOSECONDS));
      assertFalse(registry.isClosed());
    }
  }

  @Test
  void httpcdf002TwoOwnersKeepSeparateCumulativeBucketsAfterSameClockRotations() {
    var clock = new MockClock();
    try (var a = new OverflowSafeHttpMeterRegistry(clock);
        var b = new OverflowSafeHttpMeterRegistry(clock)) {
      var first = timer(a);
      var second = timer(b);
      first.record(50_000_000, TimeUnit.NANOSECONDS);
      second.record(5_000_000_000L, TimeUnit.NANOSECONDS);
      clock.add(Duration.ofSeconds(3));
      cdf(first, 1, .05, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1);
      cdf(second, 1, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1);
      assertEquals(0, first.max(TimeUnit.NANOSECONDS));
      assertEquals(0, second.max(TimeUnit.NANOSECONDS));
      first.record(50_000_001, TimeUnit.NANOSECONDS);
      clock.add(Duration.ofSeconds(3));
      cdf(first, 2, .100000001, 1e-16, 1, 2, 2, 2, 2, 2, 2, 2, 2);
      cdf(second, 1, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1);
    }
  }

  @Test
  void httpcdf003FiniteWorkerObservationsNeverExpireOutOfHistogram() throws Exception {
    var clock = new MockClock();
    try (var registry = new OverflowSafeHttpMeterRegistry(clock);
        var workers = Executors.newFixedThreadPool(4)) {
      var timer = timer(registry);
      var jobs = new ArrayList<Future<?>>();
      for (int index = 0; index < 64; index++)
        jobs.add(workers.submit(() -> timer.record(1, TimeUnit.NANOSECONDS)));
      for (var job : jobs) job.get(10, TimeUnit.SECONDS);
      for (int index = 0; index < 2; index++) {
        clock.add(Duration.ofSeconds(3));
        cdf(timer, 64, .000000064, 0, 64, 64, 64, 64, 64, 64, 64, 64, 64);
        assertEquals(0, timer.max(TimeUnit.NANOSECONDS));
      }
      assertFalse(registry.isClosed());
    }
  }
}
