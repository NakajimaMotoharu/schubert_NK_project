package dev.codex.schubert.nk.api.monitoring;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.api.monitoring.OutboxObservationRepositoryTest.Fixture;
import dev.codex.schubert.nk.api.monitoring.OutboxObservationRepositoryTest.Row;
import dev.codex.schubert.nk.api.monitoring.persistence.OutboxObservationRepository;
import io.micrometer.core.instrument.Gauge;
import io.micrometer.core.instrument.Meter;
import io.micrometer.core.instrument.simple.SimpleMeterRegistry;
import java.lang.reflect.Proxy;
import java.sql.Connection;
import java.sql.SQLException;
import java.time.Duration;
import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.concurrent.Callable;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.function.ToDoubleFunction;
import org.junit.jupiter.api.Test;

/** OUTBOXCONN001..008/1668: own JDBC/registry fixtures, not actual DB/runtime operations. */
class OutboxMetricCollectorTest {
  private static final String OUTBOX_ROWS_METRIC = "nk_outbox_rows";
  private static final String OUTBOX_AGES_METRIC = "nk_outbox_oldest_seconds";
  private static final String PENDING_STATUS = "PENDING";
  private static final String SENT_STATUS = "SENT";
  private static final String ERROR_VALUE = "ERROR";
  private static final String DEBUG_MODE = "DEBUG";
  private static final Instant AS_OF = Instant.EPOCH;

  private static final class Registry extends SimpleMeterRegistry implements AutoCloseable {
    final AtomicInteger registrations = new AtomicInteger();
    final AtomicInteger closes = new AtomicInteger();
    Optional<Throwable> failure = Optional.empty();

    @Override
    protected <T> Gauge newGauge(Meter.Id id, T object, ToDoubleFunction<T> value) {
      if (registrations.incrementAndGet() == 4 && failure.isPresent()) {
        var problem = failure.orElseThrow();
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

  private static OutboxMetricCollector collector(Registry registry, String mode) {
    return new OutboxMetricCollector(new OutboxObservationRepository(), registry, mode);
  }

  private static double gauge(Registry registry, String metric, String status) {
    return registry.get(metric).tags("store", "API", "status", status).gauge().value();
  }

  private static void missing(Registry registry, OutboxMetricCollector collector) {
    assertTrue(collector.snapshot().isEmpty());
    assertEquals(6, registry.getMeters().size());
    for (String metric : List.of(OUTBOX_ROWS_METRIC, OUTBOX_AGES_METRIC))
      for (String status : List.of(PENDING_STATUS, SENT_STATUS, ERROR_VALUE))
        assertTrue(Double.isNaN(gauge(registry, metric, status)));
  }

  @Test
  void outboxConn001BothFamiliesPublishOnlyAfterAllSuccessfulClose() throws SQLException {
    try (var registry = new Registry()) {
      var collector = collector(registry, DEBUG_MODE);
      missing(registry, collector);
      var f =
          new Fixture(
              Row.row(PENDING_STATUS, 3, 2),
              Row.row(SENT_STATUS, 5, 4),
              Row.row(ERROR_VALUE, 7, 6));
      f.beforeStatementClose = () -> missing(registry, collector);
      var actual = collector.collect(f.connection(), AS_OF).orElseThrow();
      f.complete();
      assertSame(actual, collector.snapshot().orElseThrow());
      assertEquals(3, actual.counts().pending());
      assertEquals(5, actual.counts().sent());
      assertEquals(7, actual.counts().error());
      assertEquals(Duration.ofSeconds(2), actual.ages().pending());
      assertEquals(3, gauge(registry, OUTBOX_ROWS_METRIC, PENDING_STATUS));
      assertEquals(5, gauge(registry, OUTBOX_ROWS_METRIC, SENT_STATUS));
      assertEquals(7, gauge(registry, OUTBOX_ROWS_METRIC, ERROR_VALUE));
      assertEquals(2, gauge(registry, OUTBOX_AGES_METRIC, PENDING_STATUS));
      assertEquals(4, gauge(registry, OUTBOX_AGES_METRIC, SENT_STATUS));
      assertEquals(6, gauge(registry, OUTBOX_AGES_METRIC, ERROR_VALUE));
      assertEquals(0, registry.closes.get());
    }
  }

  @Test
  void outboxConn002FailureClearsBothFamiliesAndTrueEmptyQueryRecovers() throws SQLException {
    try (var registry = new Registry()) {
      var collector = collector(registry, DEBUG_MODE);
      var old =
          collector
              .collect(new Fixture(Row.row(PENDING_STATUS, 9, 8)).connection(), AS_OF)
              .orElseThrow();
      var f = new Fixture();
      var failure = new SQLException("owned observation failure");
      f.faults.put("execute", failure);
      assertSame(
          failure,
          assertThrows(SQLException.class, () -> collector.collect(f.connection(), AS_OF)));
      missing(registry, collector);
      assertEquals(9, old.counts().pending());
      assertEquals(Duration.ofSeconds(8), old.ages().pending());
      assertEquals(1, f.executed);
      assertEquals(List.of("PS"), f.closes);
      var empty = new Fixture();
      assertEquals(
          0, collector.collect(empty.connection(), AS_OF).orElseThrow().counts().pending());
      empty.complete();
      for (String metric : List.of(OUTBOX_ROWS_METRIC, OUTBOX_AGES_METRIC))
        for (String status : List.of(PENDING_STATUS, SENT_STATUS, ERROR_VALUE))
          assertEquals(0, gauge(registry, metric, status));
    }
  }

  @Test
  void outboxConn003EveryObservationFailureIsUnknownAndPropagatesUnchangedOnce()
      throws SQLException {
    for (var point :
        List.of(
            "autoCommit",
            "readOnly",
            "isolation",
            "prepare",
            "timeout",
            "execute",
            "next",
            "status",
            "count",
            "wasNull",
            "oldest",
            "RSclose",
            "PSclose")) {
      for (var failure :
          List.<Throwable>of(
              new SQLException("owned fixture failure"),
              new IllegalStateException("owned fixture failure"),
              new AssertionError("owned fixture failure"))) {
        try (var registry = new Registry()) {
          var collector = collector(registry, DEBUG_MODE);
          collector.collect(new Fixture(Row.row(PENDING_STATUS, 9, 3)).connection(), AS_OF);
          var f = new Fixture(Row.row(ERROR_VALUE, 1, 2));
          f.faults.put(point, failure);
          assertSame(
              failure,
              assertThrows(failure.getClass(), () -> collector.collect(f.connection(), AS_OF)));
          missing(registry, collector);
          assertTrue(f.prepared <= 1);
          assertTrue(f.executed <= 1);
        }
      }
    }
  }

  @Test
  void outboxConn004StandardDoesNotReadRegisterOrRetainButChecksBoundaryNull() throws SQLException {
    try (var registry = new Registry()) {
      var collector = collector(registry, "STANDARD");
      var f = new Fixture(Row.row(ERROR_VALUE, 3, 4));
      f.faults.put("autoCommit", new AssertionError("no detailed standard read"));
      assertTrue(collector.collect(f.connection(), AS_OF).isEmpty());
      assertTrue(collector.snapshot().isEmpty());
      assertEquals(0, registry.getMeters().size());
      assertEquals(0, f.prepared);
      assertEquals(0, f.executed);
      assertTrue(f.closes.isEmpty());
      assertThrows(NullPointerException.class, () -> collector.collect(null, AS_OF));
      assertThrows(NullPointerException.class, () -> collector.collect(f.connection(), null));
    }
  }

  @Test
  void outboxConn005ConstructorAndBoundaryNullCannotErasePreviouslyAcceptedObservation()
      throws SQLException {
    try (var registry = new Registry()) {
      assertThrows(
          NullPointerException.class, () -> new OutboxMetricCollector(null, registry, DEBUG_MODE));
      assertThrows(
          NullPointerException.class,
          () -> new OutboxMetricCollector(new OutboxObservationRepository(), null, DEBUG_MODE));
      assertThrows(
          NullPointerException.class,
          () -> new OutboxMetricCollector(new OutboxObservationRepository(), registry, null));
      assertThrows(IllegalArgumentException.class, () -> collector(registry, "unknown-canary"));
      assertEquals(0, registry.getMeters().size());
      var collector = collector(registry, DEBUG_MODE);
      var actual =
          collector
              .collect(new Fixture(Row.row(PENDING_STATUS, 3, 4)).connection(), AS_OF)
              .orElseThrow();
      assertThrows(NullPointerException.class, () -> collector.collect(null, AS_OF));
      assertThrows(
          NullPointerException.class, () -> collector.collect(new Fixture().connection(), null));
      assertSame(actual, collector.snapshot().orElseThrow());
      assertEquals(3, gauge(registry, OUTBOX_ROWS_METRIC, PENDING_STATUS));
      assertEquals(4, gauge(registry, OUTBOX_AGES_METRIC, PENDING_STATUS));
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
                    throw new AssertionError("owned gate deadline");
                  return delegate.prepareStatement((String) arguments[0]);
                default:
                  throw new AssertionError("no borrowed ownership transfer");
              }
            }));
  }

  @Test
  void outboxConn006OneOwnerSerializesReadCloseAndBothPublications() throws Exception {
    try (var registry = new Registry();
        var pool = Executors.newFixedThreadPool(2)) {
      var collector = collector(registry, DEBUG_MODE);
      var first = new Fixture(Row.row(PENDING_STATUS, 1, 3));
      var second = new Fixture(Row.row(PENDING_STATUS, 2, 4));
      var entered = new CountDownLatch(1);
      var release = new CountDownLatch(1);
      var secondCalled = new CountDownLatch(1);
      var secondEntered = new CountDownLatch(1);
      var secondRelease = new CountDownLatch(0);
      var one =
          pool.submit(() -> collector.collect(gate(first.connection(), entered, release), AS_OF));
      try {
        assertTrue(entered.await(5, TimeUnit.SECONDS));
        var two =
            pool.submit(
                () -> {
                  secondCalled.countDown();
                  return collector.collect(
                      gate(second.connection(), secondEntered, secondRelease), AS_OF);
                });
        assertTrue(secondCalled.await(5, TimeUnit.SECONDS));
        assertFalse(secondEntered.await(100, TimeUnit.MILLISECONDS));
        missing(registry, collector);
        release.countDown();
        assertEquals(1, one.get(5, TimeUnit.SECONDS).orElseThrow().counts().pending());
        assertEquals(2, two.get(5, TimeUnit.SECONDS).orElseThrow().counts().pending());
        assertEquals(2, collector.snapshot().orElseThrow().counts().pending());
        assertEquals(4, gauge(registry, OUTBOX_AGES_METRIC, PENDING_STATUS));
        first.complete();
        second.complete();
      } finally {
        release.countDown();
      }
    }
  }

  @Test
  void outboxConn007ParallelCallersAndSeparateOwnersCannotCrossState() throws Exception {
    try (var registry = new Registry();
        var otherRegistry = new Registry();
        var pool = Executors.newFixedThreadPool(8)) {
      var collector = collector(registry, DEBUG_MODE);
      var other = collector(otherRegistry, DEBUG_MODE);
      other.collect(new Fixture(Row.row(ERROR_VALUE, 222, 333)).connection(), AS_OF);
      var tasks = new ArrayList<Callable<Long>>();
      for (int owner = 1; owner <= 64; owner++) {
        long count = owner;
        tasks.add(
            () -> {
              var f = new Fixture(Row.row(PENDING_STATUS, count, count));
              var actual = collector.collect(f.connection(), AS_OF).orElseThrow();
              assertEquals(count, actual.counts().pending());
              assertEquals(Duration.ofSeconds(count), actual.ages().pending());
              f.complete();
              return actual.counts().pending();
            });
      }
      var results = pool.invokeAll(tasks);
      for (int i = 0; i < results.size(); i++) assertEquals(i + 1L, results.get(i).get());
      assertEquals(222, other.snapshot().orElseThrow().counts().error());
      assertEquals(333, gauge(otherRegistry, OUTBOX_AGES_METRIC, ERROR_VALUE));
      assertEquals(6, registry.getMeters().size());
      assertEquals(6, otherRegistry.getMeters().size());
    }
  }

  @Test
  void outboxConn008PartialConstructionFailureRetainsCallerRegistryAndExactProblem() {
    for (var failure :
        List.<Throwable>of(
            new IllegalStateException("owned provider fixture"),
            new AssertionError("owned provider fixture"))) {
      var registry = new Registry();
      try {
        registry.failure = Optional.of(failure);
        assertSame(
            failure, assertThrows(failure.getClass(), () -> collector(registry, DEBUG_MODE)));
        assertEquals(4, registry.registrations.get());
        assertEquals(3, registry.getMeters().size());
        assertEquals(0, registry.closes.get());
      } finally {
        registry.close();
      }
      assertEquals(1, registry.closes.get());
    }
  }
}
