package dev.codex.schubert.nk.api.monitoring;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.api.monitoring.DbPoolMetricObservationTest.Fixture;
import io.micrometer.core.instrument.simple.SimpleMeterRegistry;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.Callable;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Test;

/**
 * POOLCONN001..008: owned fake interface/SDK connection, no actual Hikari/DB/management activity.
 */
class DbPoolMetricCollectorTest {
  private static final String ACTIVE_STATE_LABEL = "active";
  private static final String DEBUG_MONITORING_MODE = "DEBUG";

  private static final class Registry extends SimpleMeterRegistry implements AutoCloseable {
    @Override
    public void close() {
      super.close();
    }
  }

  private static DbPoolMetricCollector collector(Registry registry, String mode) {
    return new DbPoolMetricCollector(new DbPoolMetricObservation(), registry, mode);
  }

  private static void unknown(Registry registry, DbPoolMetricCollector collector) {
    assertTrue(collector.snapshot().isEmpty());
    assertEquals(4, registry.getMeters().size());
    for (String state : List.of(ACTIVE_STATE_LABEL, "idle", "pending", "max"))
      assertTrue(
          Double.isNaN(
              registry
                  .get("nk_db_pool_connections")
                  .tags("service", "API", "state", state)
                  .gauge()
                  .value()));
  }

  @Test
  void poolConn001DebugPublishesCompleteBorrowedGetterValues() {
    try (var registry = new Registry()) {
      var collector = collector(registry, DEBUG_MONITORING_MODE);
      unknown(registry, collector);
      var f = new Fixture();
      var actual = collector.collect(f.pool(), f.config()).orElseThrow();
      f.complete();
      assertSame(actual, collector.snapshot().orElseThrow());
      DbPoolMetricObservationTest.values(actual, 3, 5, 2, 8);
      assertEquals(
          3,
          registry
              .get("nk_db_pool_connections")
              .tags("service", "API", "state", ACTIVE_STATE_LABEL)
              .gauge()
              .value());
      assertEquals(4, registry.getMeters().size());
    }
  }

  @Test
  void poolConn002InvalidObservationClearsOldValuesAndTrueZeroRecovers() {
    try (var registry = new Registry()) {
      var collector = collector(registry, DEBUG_MONITORING_MODE);
      var f = new Fixture();
      var original = collector.collect(f.pool(), f.config()).orElseThrow();
      var invalid = new Fixture();
      invalid.maximum = 0;
      assertTrue(collector.collect(invalid.pool(), invalid.config()).isEmpty());
      invalid.complete();
      unknown(registry, collector);
      var zero = new Fixture();
      zero.active = 0;
      zero.idle = 0;
      zero.pending = 0;
      DbPoolMetricObservationTest.values(
          collector.collect(zero.pool(), zero.config()).orElseThrow(), 0, 0, 0, 8);
      assertEquals(
          0,
          registry
              .get("nk_db_pool_connections")
              .tags("service", "API", "state", ACTIVE_STATE_LABEL)
              .gauge()
              .value());
      assertEquals(3, original.active());
    }
  }

  private static final class UnformattableFailure extends IllegalStateException {
    private static final long serialVersionUID = 1L;

    @Override
    public String getMessage() {
      throw new AssertionError("no failure text access");
    }

    @Override
    public String toString() {
      throw new AssertionError("no failure formatting");
    }
  }

  @Test
  void poolConn003AllGetterFailuresBecomeUnknownAndKeepIdentityWithoutGraphWalk() {
    for (String point : List.of(ACTIVE_STATE_LABEL, "idle", "pending", "max")) {
      var cycle = new IllegalStateException("owned cycle first");
      var peer = new IllegalStateException("owned cycle peer");
      cycle.initCause(peer);
      peer.initCause(cycle);
      for (var failure :
          List.<Throwable>of(
              cycle, new UnformattableFailure(), new AssertionError("owned provider fixture"))) {
        try (var registry = new Registry()) {
          var collector = collector(registry, DEBUG_MONITORING_MODE);
          var success = new Fixture();
          collector.collect(success.pool(), success.config());
          var f = new Fixture();
          f.faults.put(point, failure);
          assertSame(
              failure,
              assertThrows(failure.getClass(), () -> collector.collect(f.pool(), f.config())));
          unknown(registry, collector);
          assertEquals(1, f.calls.stream().filter(point::equals).count());
          var next = new Fixture();
          assertEquals(3, collector.collect(next.pool(), next.config()).orElseThrow().active());
        }
      }
    }
  }

  @Test
  void poolConn004StandardNeverCallsEvenFailingGettersOrRetainsDetails() {
    try (var registry = new Registry()) {
      var collector = collector(registry, "STANDARD");
      var f = new Fixture();
      f.faults.put(ACTIVE_STATE_LABEL, new AssertionError("no standard getter"));
      assertTrue(collector.collect(f.pool(), f.config()).isEmpty());
      assertTrue(f.calls.isEmpty());
      assertTrue(collector.snapshot().isEmpty());
      assertEquals(0, registry.getMeters().size());
      assertThrows(NullPointerException.class, () -> collector.collect(null, f.config()));
      assertThrows(NullPointerException.class, () -> collector.collect(f.pool(), null));
      assertTrue(f.calls.isEmpty());
    }
  }

  @Test
  void poolConn005InvalidBoundariesCannotMutateOrEraseExistingSnapshot() {
    try (var registry = new Registry()) {
      assertThrows(
          NullPointerException.class,
          () -> new DbPoolMetricCollector(null, registry, DEBUG_MONITORING_MODE));
      assertThrows(
          NullPointerException.class,
          () ->
              new DbPoolMetricCollector(
                  new DbPoolMetricObservation(), null, DEBUG_MONITORING_MODE));
      assertThrows(NullPointerException.class, () -> collector(registry, null));
      assertThrows(IllegalArgumentException.class, () -> collector(registry, "unknown-mode"));
      assertEquals(0, registry.getMeters().size());
      var collector = collector(registry, DEBUG_MONITORING_MODE);
      var f = new Fixture();
      var actual = collector.collect(f.pool(), f.config()).orElseThrow();
      assertThrows(NullPointerException.class, () -> collector.collect(null, f.config()));
      assertThrows(NullPointerException.class, () -> collector.collect(f.pool(), null));
      assertSame(actual, collector.snapshot().orElseThrow());
    }
  }

  @Test
  void poolConn006OneOwnerSerializesGettersThroughPublication() throws Exception {
    try (var registry = new Registry();
        var executor = Executors.newFixedThreadPool(2)) {
      var collector = collector(registry, DEBUG_MONITORING_MODE);
      var first = new Fixture();
      first.active = 1;
      var second = new Fixture();
      second.active = 2;
      var entered = new CountDownLatch(1);
      var release = new CountDownLatch(1);
      var calledSecond = new CountDownLatch(1);
      var enteredSecond = new CountDownLatch(1);
      first.beforeActive =
          () -> {
            entered.countDown();
            assertTrue(release.await(5, TimeUnit.SECONDS));
          };
      second.beforeActive = enteredSecond::countDown;
      var one = executor.submit(() -> collector.collect(first.pool(), first.config()));
      try {
        assertTrue(entered.await(5, TimeUnit.SECONDS));
        var two =
            executor.submit(
                () -> {
                  calledSecond.countDown();
                  return collector.collect(second.pool(), second.config());
                });
        assertTrue(calledSecond.await(5, TimeUnit.SECONDS));
        assertFalse(enteredSecond.await(100, TimeUnit.MILLISECONDS));
        assertTrue(collector.snapshot().isEmpty());
        release.countDown();
        assertEquals(1, one.get(5, TimeUnit.SECONDS).orElseThrow().active());
        assertEquals(2, two.get(5, TimeUnit.SECONDS).orElseThrow().active());
        assertEquals(2, collector.snapshot().orElseThrow().active());
        first.complete();
        second.complete();
      } finally {
        release.countDown();
      }
    }
  }

  @Test
  void poolConn007ParallelFakeSourcesHaveCompleteIndependentReturnedCounts() throws Exception {
    try (var registry = new Registry();
        var executor = Executors.newFixedThreadPool(8)) {
      var collector = collector(registry, DEBUG_MONITORING_MODE);
      var tasks = new ArrayList<Callable<Long>>();
      for (int i = 0; i < 64; i++) {
        int active = i;
        tasks.add(
            () -> {
              var f = new Fixture();
              f.active = active;
              var actual = collector.collect(f.pool(), f.config()).orElseThrow();
              DbPoolMetricObservationTest.values(actual, active, 5, 2, 8);
              f.complete();
              return actual.active();
            });
      }
      var actual = executor.invokeAll(tasks);
      for (int i = 0; i < actual.size(); i++) assertEquals((long) i, actual.get(i).get());
      assertEquals(4, registry.getMeters().size());
    }
  }

  @Test
  void poolConn008SeparateOwnersAndRepeatedCollectionCannotGrowSeriesOrControlPool() {
    try (var one = new Registry();
        var two = new Registry()) {
      var first = collector(one, DEBUG_MONITORING_MODE);
      var second = collector(two, DEBUG_MONITORING_MODE);
      var other = new Fixture();
      other.active = 111;
      second.collect(other.pool(), other.config());
      other.complete();
      for (int i = 0; i < 100; i++) {
        var f = new Fixture();
        f.active = i;
        first.collect(f.pool(), f.config());
        f.complete();
      }
      assertEquals(99, first.snapshot().orElseThrow().active());
      assertEquals(111, second.snapshot().orElseThrow().active());
      assertEquals(4, one.getMeters().size());
      assertEquals(4, two.getMeters().size());
    }
  }
}
