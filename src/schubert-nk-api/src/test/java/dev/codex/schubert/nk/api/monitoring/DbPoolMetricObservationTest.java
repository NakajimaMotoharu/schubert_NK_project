package dev.codex.schubert.nk.api.monitoring;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.zaxxer.hikari.HikariConfigMXBean;
import com.zaxxer.hikari.HikariPoolMXBean;
import dev.codex.schubert.nk.api.monitoring.DbPoolMetricRecorder.Counts;
import java.lang.reflect.Proxy;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.Callable;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.function.Executable;

/** POOLREAD001..008: fake typed interfaces only, never a Hikari pool/config/JMX connection. */
class DbPoolMetricObservationTest {
  private static final int FAULT_IDLE_INDEX = 1;
  private static final int FAULT_PENDING_INDEX = 2;
  private static final int FAULT_NEGATIVE_MAXIMUM_INDEX = 3;
  private static final int FAULT_ZERO_MAXIMUM_INDEX = 4;
  private static final String ACTIVE_GETTER_POINT = "active";

  static final class Fixture {
    int active = 3;
    int idle = 5;
    int pending = 2;
    int maximum = 8;
    final List<String> calls = new ArrayList<>();
    final Map<String, Throwable> faults = new HashMap<>();
    Executable beforeActive = () -> {};

    private int getter(String point, int value) throws Throwable {
      calls.add(point);
      if (point.equals(ACTIVE_GETTER_POINT)) beforeActive.execute();
      var failure = faults.get(point);
      if (failure != null) throw failure;
      return value;
    }

    HikariPoolMXBean pool() {
      return HikariPoolMXBean.class.cast(
          Proxy.newProxyInstance(
              HikariPoolMXBean.class.getClassLoader(),
              new Class<?>[] {HikariPoolMXBean.class},
              (object, method, args) ->
                  switch (method.getName()) {
                    case "getActiveConnections" -> getter(ACTIVE_GETTER_POINT, active);
                    case "getIdleConnections" -> getter("idle", idle);
                    case "getThreadsAwaitingConnection" -> getter("pending", pending);
                    default -> throw new AssertionError("no total/control/management operations");
                  }));
    }

    HikariConfigMXBean config() {
      return HikariConfigMXBean.class.cast(
          Proxy.newProxyInstance(
              HikariConfigMXBean.class.getClassLoader(),
              new Class<?>[] {HikariConfigMXBean.class},
              (object, method, args) -> {
                if (method.getName().equals("getMaximumPoolSize")) return getter("max", maximum);
                throw new AssertionError("no config/credential getter or mutation");
              }));
    }

    void complete() {
      assertEquals(List.of(ACTIVE_GETTER_POINT, "idle", "pending", "max"), calls);
    }
  }

  static void values(Counts actual, long active, long idle, long pending, long maximum) {
    assertEquals(active, actual.active());
    assertEquals(idle, actual.idle());
    assertEquals(pending, actual.pending());
    assertEquals(maximum, actual.maximum());
  }

  @Test
  void poolRead001FourBorrowedGettersHaveIndependentValuesAndExactCalls() {
    var f = new Fixture();
    values(new DbPoolMetricObservation().observe(f.pool(), f.config()).orElseThrow(), 3, 5, 2, 8);
    f.complete();
  }

  @Test
  void poolRead002TrueZeroWithPositiveMaximumIsKnownNotMissing() {
    var f = new Fixture();
    f.active = 0;
    f.idle = 0;
    f.pending = 0;
    f.maximum = 1;
    values(new DbPoolMetricObservation().observe(f.pool(), f.config()).orElseThrow(), 0, 0, 0, 1);
    f.complete();
  }

  @Test
  void poolRead003InvalidStatisticsRemainUnknownNotZero() {
    for (int point = 0; point < 5; point++) {
      var f = new Fixture();
      if (point == 0) f.active = -1;
      if (point == FAULT_IDLE_INDEX) f.idle = -1;
      if (point == FAULT_PENDING_INDEX) f.pending = -1;
      if (point == FAULT_NEGATIVE_MAXIMUM_INDEX) f.maximum = -1;
      if (point == FAULT_ZERO_MAXIMUM_INDEX) f.maximum = 0;
      assertTrue(new DbPoolMetricObservation().observe(f.pool(), f.config()).isEmpty());
      f.complete();
    }
  }

  @Test
  void poolRead004NullOwnersAreRejectedBeforeAnyGetter() {
    var f = new Fixture();
    var observation = new DbPoolMetricObservation();
    assertThrows(NullPointerException.class, () -> observation.observe(null, f.config()));
    assertThrows(NullPointerException.class, () -> observation.observe(f.pool(), null));
    assertThrows(NullPointerException.class, () -> observation.observe(null, null));
    assertTrue(f.calls.isEmpty());
  }

  @Test
  void poolRead005ProviderFailuresPreserveIdentityWithoutRetryOrLaterGetters() {
    var order = List.of(ACTIVE_GETTER_POINT, "idle", "pending", "max");
    for (int i = 0; i < order.size(); i++) {
      for (var failure :
          List.<Throwable>of(
              new IllegalStateException("owned provider fixture"),
              new AssertionError("owned provider fixture"))) {
        var f = new Fixture();
        f.faults.put(order.get(i), failure);
        assertSame(
            failure,
            assertThrows(
                failure.getClass(),
                () -> new DbPoolMetricObservation().observe(f.pool(), f.config())));
        assertEquals(order.subList(0, i + 1), f.calls);
      }
    }
  }

  @Test
  void poolRead006MaximumIntegersBecomeExactLongsWithoutSumOrWrap() {
    var f = new Fixture();
    f.active = Integer.MAX_VALUE;
    f.idle = Integer.MAX_VALUE;
    f.pending = Integer.MAX_VALUE;
    f.maximum = Integer.MAX_VALUE;
    values(
        new DbPoolMetricObservation().observe(f.pool(), f.config()).orElseThrow(),
        2147483647L,
        2147483647L,
        2147483647L,
        2147483647L);
    f.complete();
  }

  @Test
  void poolRead007ParallelOwnedInterfacesCannotShareMutableObservationState() throws Exception {
    var observation = new DbPoolMetricObservation();
    var tasks = new ArrayList<Callable<Long>>();
    for (int i = 0; i < 64; i++) {
      int active = i;
      tasks.add(
          () -> {
            var f = new Fixture();
            f.active = active;
            var actual = observation.observe(f.pool(), f.config()).orElseThrow();
            values(actual, active, 5, 2, 8);
            f.complete();
            return actual.active();
          });
    }
    var pool = Executors.newFixedThreadPool(8);
    try {
      var actual = pool.invokeAll(tasks, 10, TimeUnit.SECONDS);
      for (int i = 0; i < actual.size(); i++) assertEquals((long) i, actual.get(i).get());
    } finally {
      pool.shutdownNow();
      assertTrue(pool.awaitTermination(10, TimeUnit.SECONDS));
    }
  }

  @Test
  void poolRead008LaterGetterValuesAndSeparateOwnersCannotMutateSnapshots() {
    var f = new Fixture();
    var observation = new DbPoolMetricObservation();
    var original = observation.observe(f.pool(), f.config()).orElseThrow();
    f.active = 7;
    f.maximum = 9;
    f.calls.clear();
    values(observation.observe(f.pool(), f.config()).orElseThrow(), 7, 5, 2, 9);
    f.complete();
    values(original, 3, 5, 2, 8);
    var other = new Fixture();
    other.active = 111;
    values(observation.observe(other.pool(), other.config()).orElseThrow(), 111, 5, 2, 8);
    other.complete();
  }
}
