package dev.codex.schubert.nk.api.monitoring;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.api.monitoring.AsyncJobCountRepositoryTest.Fixture;
import dev.codex.schubert.nk.api.monitoring.AsyncJobCountRepositoryTest.Row;
import dev.codex.schubert.nk.api.monitoring.AsyncJobMetricRecorder.State;
import dev.codex.schubert.nk.api.monitoring.persistence.AsyncJobCountRepository;
import io.micrometer.core.instrument.simple.SimpleMeterRegistry;
import java.lang.reflect.Proxy;
import java.sql.Connection;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.Callable;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Test;

/** ASYNCCONN001..008: owned JDBC doubles and SDK, not actual DB/runtime collection. */
class AsyncJobMetricCollectorTest {
  private static final String RECEIVED_STATE = "RECEIVED";
  private static final String PROCESSING_STATE = "PROCESSING";
  private static final String COMPLETED_STATE = "COMPLETED";
  private static final String ERROR_VALUE = "ERROR";
  private static final String CANCELLED_STATE = "CANCELLED";
  private static final String STATE_LABEL = "state";
  private static final String DEBUG_MODE = "DEBUG";

  private static final class Registry extends SimpleMeterRegistry implements AutoCloseable {
    @Override
    public void close() {
      super.close();
    }
  }

  private static AsyncJobMetricCollector collector(SimpleMeterRegistry registry, String mode) {
    return new AsyncJobMetricCollector(new AsyncJobCountRepository(), registry, mode);
  }

  private static void missing(SimpleMeterRegistry registry, AsyncJobMetricCollector collector) {
    assertTrue(collector.snapshot().isEmpty());
    assertEquals(5, registry.getMeters().size());
    for (String state :
        List.of(RECEIVED_STATE, PROCESSING_STATE, COMPLETED_STATE, ERROR_VALUE, CANCELLED_STATE))
      assertTrue(
          Double.isNaN(registry.get("nk_async_jobs").tag(STATE_LABEL, state).gauge().value()));
  }

  @Test
  void asyncConn001DebugCollectPublishesOnlyAfterSuccessfulClose() throws SQLException {
    try (var registry = new Registry()) {
      var collector = collector(registry, DEBUG_MODE);
      missing(registry, collector);
      var f =
          new Fixture(
              Row.row(RECEIVED_STATE, 1),
              Row.row(PROCESSING_STATE, 2),
              Row.row(COMPLETED_STATE, 3),
              Row.row(ERROR_VALUE, 4),
              Row.row(CANCELLED_STATE, 5));
      f.beforeStatementClose = () -> missing(registry, collector);
      var result = collector.collect(f.connection()).orElseThrow();
      f.complete();
      assertSame(result, collector.snapshot().orElseThrow());
      assertEquals(15, result.totalJobs());
      assertEquals(5, registry.getMeters().size());
      int count = 0;
      for (String state :
          List.of(
              RECEIVED_STATE, PROCESSING_STATE, COMPLETED_STATE, ERROR_VALUE, CANCELLED_STATE)) {
        ++count;
        assertEquals(count, registry.get("nk_async_jobs").tag(STATE_LABEL, state).gauge().value());
      }
    }
  }

  @Test
  void asyncConn002FailureClearsStaleSuccessAndTrueEmptyCanRecover() throws SQLException {
    try (var registry = new Registry()) {
      var collector = collector(registry, DEBUG_MODE);
      var old = collector.collect(new Fixture(Row.row(ERROR_VALUE, 4)).connection()).orElseThrow();
      var f = new Fixture();
      var failure = new SQLException("owned query failure");
      f.faults.put("execute", failure);
      assertSame(
          failure, assertThrows(SQLException.class, () -> collector.collect(f.connection())));
      missing(registry, collector);
      assertEquals(4, old.totalJobs());
      assertEquals(1, f.executed);
      assertEquals(List.of("PS"), f.closes);
      var empty = new Fixture();
      assertEquals(0, collector.collect(empty.connection()).orElseThrow().totalJobs());
      empty.complete();
      for (String state :
          List.of(RECEIVED_STATE, PROCESSING_STATE, COMPLETED_STATE, ERROR_VALUE, CANCELLED_STATE))
        assertEquals(0, registry.get("nk_async_jobs").tag(STATE_LABEL, state).gauge().value());
    }
  }

  @Test
  void asyncConn003EveryObservationFailureIsUnknownAndPropagatedOnce() throws SQLException {
    for (var point :
        List.of(
            "autoCommit",
            "readOnly",
            "isolation",
            "prepare",
            "timeout",
            "execute",
            "next",
            STATE_LABEL,
            "count",
            "wasNull",
            "RSclose",
            "PSclose")) {
      for (var failure :
          List.<Throwable>of(
              new SQLException("owned fixture failure"),
              new IllegalStateException("owned fixture failure"),
              new AssertionError("owned fixture failure"))) {
        try (var registry = new Registry()) {
          var collector = collector(registry, DEBUG_MODE);
          collector.collect(new Fixture(Row.row(RECEIVED_STATE, 9)).connection());
          var f = new Fixture(Row.row(COMPLETED_STATE, 1));
          f.faults.put(point, failure);
          assertSame(
              failure, assertThrows(failure.getClass(), () -> collector.collect(f.connection())));
          missing(registry, collector);
          assertTrue(f.prepared <= 1);
          assertTrue(f.executed <= 1);
        }
      }
    }
  }

  @Test
  void asyncConn004StandardNeverReadsOrRegistersButRejectsNull() throws SQLException {
    try (var registry = new Registry()) {
      var collector = collector(registry, "STANDARD");
      var f = new Fixture(Row.row(ERROR_VALUE, 3));
      f.faults.put("autoCommit", new AssertionError("no standard detailed read"));
      assertTrue(collector.collect(f.connection()).isEmpty());
      assertTrue(collector.snapshot().isEmpty());
      assertEquals(0, registry.getMeters().size());
      assertEquals(0, f.prepared);
      assertEquals(0, f.executed);
      assertTrue(f.closes.isEmpty());
      assertThrows(NullPointerException.class, () -> collector.collect(null));
    }
  }

  @Test
  void asyncConn005ConstructorInvariantsAndInvalidNullCannotErasePriorSuccess()
      throws SQLException {
    try (var registry = new Registry()) {
      assertThrows(
          NullPointerException.class,
          () -> new AsyncJobMetricCollector(null, registry, DEBUG_MODE));
      assertThrows(
          NullPointerException.class,
          () -> new AsyncJobMetricCollector(new AsyncJobCountRepository(), null, DEBUG_MODE));
      assertThrows(
          NullPointerException.class,
          () -> new AsyncJobMetricCollector(new AsyncJobCountRepository(), registry, null));
      assertThrows(IllegalArgumentException.class, () -> collector(registry, "unknown-canary"));
      assertEquals(0, registry.getMeters().size());
      var collector = collector(registry, DEBUG_MODE);
      var actual =
          collector.collect(new Fixture(Row.row(ERROR_VALUE, 3)).connection()).orElseThrow();
      assertThrows(NullPointerException.class, () -> collector.collect(null));
      assertSame(actual, collector.snapshot().orElseThrow());
      assertEquals(3, actual.value(State.ERROR));
    }
  }

  private static Connection gate(
      Connection delegate, CountDownLatch entered, CountDownLatch release) {
    return Connection.class.cast(
        Proxy.newProxyInstance(
            Connection.class.getClassLoader(),
            new Class<?>[] {Connection.class},
            (object, method, arguments) -> {
              switch (method.getName()) {
                case "getAutoCommit":
                  return delegate.getAutoCommit();
                case "isReadOnly":
                  return delegate.isReadOnly();
                case "getTransactionIsolation":
                  return delegate.getTransactionIsolation();
                case "prepareStatement":
                  entered.countDown();
                  if (!release.await(5, TimeUnit.SECONDS))
                    throw new AssertionError("owned fixture gate deadline");
                  return delegate.prepareStatement((String) arguments[0]);
                default:
                  throw new AssertionError("no connection ownership transfer");
              }
            }));
  }

  @Test
  void asyncConn006OwnerSerializesReadCloseAndPublication() throws Exception {
    try (var registry = new Registry();
        var pool = Executors.newFixedThreadPool(2)) {
      var collector = collector(registry, DEBUG_MODE);
      var first = new Fixture(Row.row(RECEIVED_STATE, 1));
      var second = new Fixture(Row.row(RECEIVED_STATE, 2));
      var entered = new CountDownLatch(1);
      var release = new CountDownLatch(1);
      var secondCalled = new CountDownLatch(1);
      var secondEntered = new CountDownLatch(1);
      var secondRelease = new CountDownLatch(0);
      var one = pool.submit(() -> collector.collect(gate(first.connection(), entered, release)));
      try {
        assertTrue(entered.await(5, TimeUnit.SECONDS));
        var two =
            pool.submit(
                () -> {
                  secondCalled.countDown();
                  return collector.collect(gate(second.connection(), secondEntered, secondRelease));
                });
        assertTrue(secondCalled.await(5, TimeUnit.SECONDS));
        assertFalse(secondEntered.await(100, TimeUnit.MILLISECONDS));
        assertTrue(collector.snapshot().isEmpty());
        release.countDown();
        assertEquals(1, one.get(5, TimeUnit.SECONDS).orElseThrow().totalJobs());
        assertEquals(2, two.get(5, TimeUnit.SECONDS).orElseThrow().totalJobs());
        assertEquals(2, collector.snapshot().orElseThrow().value(State.RECEIVED));
        first.complete();
        second.complete();
      } finally {
        release.countDown();
      }
    }
  }

  @Test
  void asyncConn007ParallelCallersAndIndependentOwnersHaveNoCrossState() throws Exception {
    try (var registry = new Registry();
        var otherRegistry = new Registry();
        var pool = Executors.newFixedThreadPool(8)) {
      var collector = collector(registry, DEBUG_MODE);
      var other = collector(otherRegistry, DEBUG_MODE);
      other.collect(new Fixture(Row.row(CANCELLED_STATE, 222)).connection());
      var tasks = new ArrayList<Callable<Long>>();
      for (int owner = 0; owner < 64; owner++) {
        long count = owner;
        tasks.add(
            () -> {
              var f = new Fixture(Row.row(RECEIVED_STATE, count), Row.row(ERROR_VALUE, 2));
              var result = collector.collect(f.connection()).orElseThrow();
              assertEquals(count, result.value(State.RECEIVED));
              assertEquals(2, result.value(State.ERROR));
              assertEquals(0, result.value(State.CANCELLED));
              f.complete();
              return result.totalJobs();
            });
      }
      var actual = pool.invokeAll(tasks);
      for (int i = 0; i < actual.size(); i++) assertEquals(i + 2L, actual.get(i).get());
      assertEquals(222, other.snapshot().orElseThrow().totalJobs());
      assertEquals(5, registry.getMeters().size());
      assertEquals(5, otherRegistry.getMeters().size());
    }
  }

  private static final class UnformattableFailure extends IllegalStateException {
    private static final long serialVersionUID = 1L;

    @Override
    public String getMessage() {
      throw new AssertionError("no failure message inspection");
    }

    @Override
    public String toString() {
      throw new AssertionError("no failure formatting");
    }
  }

  @Test
  void asyncConn008FailureGraphsAreNotWalkedAndNextSuccessRecovers() throws SQLException {
    var cycle = new SQLException("owned cycle first");
    var peer = new SQLException("owned cycle peer");
    cycle.initCause(peer);
    peer.initCause(cycle);
    for (var failure :
        List.<Throwable>of(
            cycle, new UnformattableFailure(), new AssertionError("owned fatal fixture"))) {
      try (var registry = new Registry()) {
        var collector = collector(registry, DEBUG_MODE);
        var f = new Fixture(Row.row(ERROR_VALUE, 1));
        f.faults.put("count", failure);
        var close = new SQLException("owned close fixture");
        f.faults.put("PSclose", close);
        assertSame(
            failure, assertThrows(failure.getClass(), () -> collector.collect(f.connection())));
        assertEquals(List.of(close), List.of(failure.getSuppressed()));
        missing(registry, collector);
        f.complete();
        assertEquals(
            4,
            collector
                .collect(new Fixture(Row.row(COMPLETED_STATE, 4)).connection())
                .orElseThrow()
                .totalJobs());
      }
    }
  }
}
