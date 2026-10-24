package dev.codex.schubert.nk.api.monitoring;

import static org.junit.jupiter.api.Assertions.*;

import dev.codex.schubert.nk.api.monitoring.OutboxObservationRepositoryTest.Row;
import dev.codex.schubert.nk.api.monitoring.persistence.OutboxObservationRepository;
import java.lang.reflect.Proxy;
import java.sql.Connection;
import java.sql.SQLException;
import java.time.Clock;
import java.time.Duration;
import java.time.Instant;
import java.time.ZoneId;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.function.Consumer;
import javax.sql.DataSource;
import org.junit.jupiter.api.Test;

/** 1858/ROATTEMPT001..032: own typed proxies/clock/finite diagnostic, no actual JDBC/network. */
final class ApiReadOnlyObservationAttemptTest {
  static final class Fixture {
    final OutboxObservationRepositoryTest.Fixture query;
    final List<String> calls = new ArrayList<>();
    final Map<String, Throwable> faults = new HashMap<>();
    final List<Throwable> unknown = new ArrayList<>();
    boolean autoCommit = true;
    boolean readOnly;
    boolean nullConnection;
    boolean nullTime;
    int isolation = Connection.TRANSACTION_READ_UNCOMMITTED;
    int autoChecks;

    Fixture(Row... rows) {
      query = new OutboxObservationRepositoryTest.Fixture(rows);
    }

    void fault(String point) throws Throwable {
      var value = faults.get(point);
      if (value != null) throw value;
    }

    void unchecked(String point) {
      var value = faults.get(point);
      if (value instanceof RuntimeException runtime) throw runtime;
      if (value instanceof Error fatal) throw fatal;
      assertNull(value, "checked fault is not valid for clock/diagnostic port");
    }

    Connection connection() {
      return Connection.class.cast(
          Proxy.newProxyInstance(
              Connection.class.getClassLoader(),
              new Class<?>[] {Connection.class},
              (proxy, method, args) -> {
                switch (method.getName()) {
                  case "getAutoCommit":
                    calls.add("auto?");
                    fault("auto-check-" + ++autoChecks);
                    return autoCommit;
                  case "setReadOnly":
                    calls.add("read-only");
                    assertEquals(true, args[0]);
                    fault("read-only");
                    readOnly = true;
                    return null;
                  case "setTransactionIsolation":
                    calls.add("isolation");
                    assertEquals(Connection.TRANSACTION_READ_COMMITTED, args[0]);
                    fault("isolation");
                    isolation = Connection.TRANSACTION_READ_COMMITTED;
                    return null;
                  case "setAutoCommit":
                    calls.add("begin");
                    assertEquals(false, args[0]);
                    fault("begin");
                    autoCommit = false;
                    return null;
                  case "isReadOnly":
                    calls.add("read-only?");
                    return readOnly;
                  case "getTransactionIsolation":
                    calls.add("isolation?");
                    return isolation;
                  case "prepareStatement":
                    calls.add("query");
                    fault("query");
                    return query.connection().prepareStatement((String) args[0]);
                  case "rollback":
                    calls.add("rollback");
                    fault("rollback");
                    return null;
                  case "close":
                    calls.add("close");
                    fault("close");
                    return null;
                  default:
                    throw new AssertionError("unapproved observation connection operation");
                }
              }));
    }

    DataSource pool() {
      return DataSource.class.cast(
          Proxy.newProxyInstance(
              DataSource.class.getClassLoader(),
              new Class<?>[] {DataSource.class},
              (proxy, method, args) -> {
                assertEquals(
                    "getConnection", method.getName(), "pool controls must not be touched");
                assertTrue(args == null || args.length == 0);
                calls.add("open");
                fault("open");
                return nullConnection ? null : connection();
              }));
    }

    Clock clock() {
      return new Clock() {
        @Override
        public ZoneId getZone() {
          throw new AssertionError("instant only");
        }

        @Override
        public Clock withZone(ZoneId zone) {
          throw new AssertionError("instant only");
        }

        @Override
        public Instant instant() {
          calls.add("time");
          unchecked("time");
          return nullTime ? null : Instant.EPOCH;
        }
      };
    }

    void unconfirmed(Throwable failure) {
      calls.add("unknown");
      unknown.add(failure);
      unchecked("diagnostic");
    }

    ApiReadOnlyObservationAttempt attempt() {
      return attempt(this::unconfirmed);
    }

    ApiReadOnlyObservationAttempt attempt(Consumer<Throwable> diagnostic) {
      return new ApiReadOnlyObservationAttempt(
          pool(), clock(), new OutboxObservationRepository(), diagnostic);
    }

    void cleanup(int rollbacks, int closes) {
      assertEquals(rollbacks, calls.stream().filter("rollback"::equals).count());
      assertEquals(closes, calls.stream().filter("close"::equals).count());
      assertEquals(1, calls.stream().filter("open"::equals).count());
    }
  }

  private static Fixture rows() {
    return new Fixture(Row.row("ERROR", 7, 6), Row.row("PENDING", 3, 2), Row.row("SENT", 5, 4));
  }

  private static void await(CountDownLatch value) {
    try {
      assertTrue(value.await(10, TimeUnit.SECONDS));
    } catch (InterruptedException interrupted) {
      Thread.currentThread().interrupt();
      throw new AssertionError(interrupted);
    }
  }

  private static void failure(String point, Throwable failure, int rollbacks, int closes) {
    var f = rows();
    f.faults.put(point, failure);
    var value = f.attempt();
    assertSame(failure, assertThrows(failure.getClass(), value::read));
    f.cleanup(rollbacks, closes);
    assertEquals(point.equals("close"), value.hasUnconfirmedResource());
    assertThrows(IllegalStateException.class, value::read);
    f.cleanup(rollbacks, closes);
  }

  @Test
  void roAttempt001() {
    var f = rows();
    var repository = new OutboxObservationRepository();
    assertThrows(
        NullPointerException.class,
        () -> new ApiReadOnlyObservationAttempt(null, f.clock(), repository, f::unconfirmed));
    assertThrows(
        NullPointerException.class,
        () -> new ApiReadOnlyObservationAttempt(f.pool(), null, repository, f::unconfirmed));
    assertThrows(
        NullPointerException.class,
        () -> new ApiReadOnlyObservationAttempt(f.pool(), f.clock(), null, f::unconfirmed));
    assertThrows(
        NullPointerException.class,
        () -> new ApiReadOnlyObservationAttempt(f.pool(), f.clock(), repository, null));
    assertTrue(f.calls.isEmpty());
  }

  @Test
  void roAttempt002() {
    var f = rows();
    var value = f.attempt();
    assertFalse(value.hasUnconfirmedResource());
    assertTrue(f.calls.isEmpty());
  }

  @Test
  void roAttempt003() throws SQLException {
    var f = rows();
    var value = f.attempt();
    var actual = value.read();
    assertEquals(3, actual.counts().pending());
    assertEquals(5, actual.counts().sent());
    assertEquals(7, actual.counts().error());
    assertEquals(Duration.ofSeconds(2), actual.ages().pending());
    assertEquals(Duration.ofSeconds(4), actual.ages().sent());
    assertEquals(Duration.ofSeconds(6), actual.ages().error());
    assertEquals(
        List.of(
            "open",
            "auto?",
            "read-only",
            "isolation",
            "begin",
            "time",
            "auto?",
            "read-only?",
            "isolation?",
            "query",
            "rollback",
            "close"),
        f.calls);
    assertFalse(value.hasUnconfirmedResource());
    f.query.complete();
  }

  @Test
  void roAttempt004() throws SQLException {
    var f = new Fixture();
    var actual = f.attempt().read();
    assertEquals(0, actual.counts().pending());
    assertEquals(0, actual.counts().sent());
    assertEquals(0, actual.counts().error());
    assertEquals(Duration.ZERO, actual.ages().pending());
    assertEquals(Duration.ZERO, actual.ages().sent());
    assertEquals(Duration.ZERO, actual.ages().error());
    f.cleanup(1, 1);
    f.query.complete();
  }

  @Test
  void roAttempt005() throws SQLException {
    var f = rows();
    var value = f.attempt();
    value.read();
    assertThrows(IllegalStateException.class, value::read);
    f.cleanup(1, 1);
  }

  @Test
  void roAttempt006() {
    var f = rows();
    f.nullConnection = true;
    var value = f.attempt();
    assertThrows(SQLException.class, value::read);
    assertFalse(value.hasUnconfirmedResource());
    assertEquals(List.of("open"), f.calls);
    assertThrows(IllegalStateException.class, value::read);
    f.cleanup(0, 0);
  }

  @Test
  void roAttempt007() {
    failure("open", new SQLException("fixture"), 0, 0);
  }

  @Test
  void roAttempt008() {
    failure("open", new IllegalStateException("fixture"), 0, 0);
  }

  @Test
  void roAttempt009() {
    failure("open", new AssertionError("fixture"), 0, 0);
  }

  @Test
  void roAttempt010() {
    var f = rows();
    f.autoCommit = false;
    assertThrows(SQLException.class, f.attempt()::read);
    assertEquals(List.of("open", "auto?", "close"), f.calls);
    f.cleanup(0, 1);
  }

  @Test
  void roAttempt011() {
    failure("auto-check-1", new SQLException("fixture"), 0, 1);
  }

  @Test
  void roAttempt012() {
    failure("read-only", new SQLException("fixture"), 0, 1);
  }

  @Test
  void roAttempt013() {
    failure("isolation", new IllegalStateException("fixture"), 0, 1);
  }

  @Test
  void roAttempt014() {
    failure("begin", new SQLException("ambiguous begin"), 1, 1);
  }

  @Test
  void roAttempt015() {
    failure("time", new IllegalStateException("fixture"), 1, 1);
  }

  @Test
  void roAttempt016() {
    var f = rows();
    f.nullTime = true;
    assertThrows(NullPointerException.class, f.attempt()::read);
    f.cleanup(1, 1);
  }

  @Test
  void roAttempt017() {
    failure("query", new SQLException("fixture"), 1, 1);
  }

  @Test
  void roAttempt018() {
    var f = rows();
    var primary = new IllegalStateException("result");
    f.query.faults.put("next", primary);
    assertSame(primary, assertThrows(IllegalStateException.class, f.attempt()::read));
    f.query.complete();
    f.cleanup(1, 1);
  }

  @Test
  void roAttempt019() {
    var f = rows();
    var primary = new AssertionError("result");
    f.query.faults.put("next", primary);
    assertSame(primary, assertThrows(AssertionError.class, f.attempt()::read));
    f.query.complete();
    f.cleanup(1, 1);
  }

  @Test
  void roAttempt020() {
    failure("rollback", new SQLException("fixture"), 1, 1);
  }

  @Test
  void roAttempt021() {
    failure("rollback", new AssertionError("fixture"), 1, 1);
  }

  @Test
  void roAttempt022() {
    var f = rows();
    var close = new SQLException("close");
    f.faults.put("close", close);
    var owner = new java.util.concurrent.atomic.AtomicReference<ApiReadOnlyObservationAttempt>();
    var value =
        f.attempt(
            failure -> {
              assertTrue(owner.get().hasUnconfirmedResource());
              assertThrows(IllegalStateException.class, owner.get()::read);
              f.unconfirmed(failure);
            });
    owner.set(value);
    assertSame(close, assertThrows(SQLException.class, value::read));
    assertEquals(List.of(close), f.unknown);
    assertTrue(value.hasUnconfirmedResource());
    assertThrows(IllegalStateException.class, value::read);
    f.cleanup(1, 1);
  }

  @Test
  void roAttempt023() {
    failure("close", new IllegalStateException("fixture"), 1, 1);
  }

  @Test
  void roAttempt024() {
    failure("close", new AssertionError("fixture"), 1, 1);
  }

  @Test
  void roAttempt025() {
    var f = rows();
    var primary = new SQLException("read");
    var rollback = new SQLException("rollback");
    var close = new SQLException("close");
    f.faults.put("query", primary);
    f.faults.put("rollback", rollback);
    f.faults.put("close", close);
    assertSame(primary, assertThrows(SQLException.class, f.attempt()::read));
    assertArrayEquals(new Throwable[] {rollback, close}, primary.getSuppressed());
    assertEquals(List.of(close), f.unknown);
    f.cleanup(1, 1);
  }

  @Test
  void roAttempt026() {
    var f = rows();
    var primary = new SQLException("read");
    var fatal = new AssertionError("rollback");
    f.faults.put("query", primary);
    f.faults.put("rollback", fatal);
    f.faults.put("close", new SQLException("close"));
    assertSame(fatal, assertThrows(AssertionError.class, f.attempt()::read));
    f.cleanup(1, 1);
    assertEquals(1, f.unknown.size());
  }

  @Test
  void roAttempt027() {
    var f = rows();
    var close = new SQLException("close");
    var diagnostic = new IllegalStateException("diagnostic");
    f.faults.put("close", close);
    f.faults.put("diagnostic", diagnostic);
    assertSame(close, assertThrows(SQLException.class, f.attempt()::read));
    assertArrayEquals(new Throwable[] {diagnostic}, close.getSuppressed());
    f.cleanup(1, 1);
  }

  @Test
  void roAttempt028() {
    var f = rows();
    var fatal = new AssertionError("diagnostic");
    f.faults.put("close", new SQLException("close"));
    f.faults.put("diagnostic", fatal);
    assertSame(fatal, assertThrows(AssertionError.class, f.attempt()::read));
    f.cleanup(1, 1);
  }

  @Test
  void roAttempt029() {
    var f = rows();
    var same = new SQLException("same");
    f.faults.put("query", same);
    f.faults.put("rollback", same);
    f.faults.put("close", same);
    assertSame(same, assertThrows(SQLException.class, f.attempt()::read));
    assertEquals(0, same.getSuppressed().length);
    f.cleanup(1, 1);
  }

  private static final class SuppressionDisabled extends RuntimeException {
    private static final long serialVersionUID = 1L;

    private SuppressionDisabled() {
      super("fixture", null, false, false);
    }
  }

  @Test
  void roAttempt030() {
    var f = rows();
    var fatal = new AssertionError("close");
    f.faults.put("query", new SuppressionDisabled());
    f.faults.put("close", fatal);
    assertSame(fatal, assertThrows(AssertionError.class, f.attempt()::read));
    f.cleanup(1, 1);
    assertEquals(List.of(fatal), f.unknown);
  }

  @Test
  void roAttempt031() {
    var f = rows();
    var primary = new SQLException("first");
    var next = new SQLException("next");
    primary.setNextException(next);
    next.setNextException(primary);
    f.faults.put("query", primary);
    assertTimeoutPreemptively(
        Duration.ofSeconds(5),
        () -> assertSame(primary, assertThrows(SQLException.class, f.attempt()::read)));
    f.cleanup(1, 1);
  }

  @Test
  void roAttempt032() throws Exception {
    var f = rows();
    var closing = new CountDownLatch(1);
    var release = new CountDownLatch(1);
    var started = new CountDownLatch(1);
    f.query.beforeStatementClose =
        () -> {
          closing.countDown();
          await(release);
        };
    var value = f.attempt();
    try (var workers = Executors.newFixedThreadPool(2)) {
      var first = workers.submit(value::read);
      try {
        await(closing);
        var second =
            workers.submit(
                () -> {
                  started.countDown();
                  return value.read();
                });
        await(started);
        assertFalse(value.hasUnconfirmedResource());
        release.countDown();
        assertEquals(3, first.get(10, TimeUnit.SECONDS).counts().pending());
        assertInstanceOf(
            IllegalStateException.class,
            assertThrows(ExecutionException.class, () -> second.get(10, TimeUnit.SECONDS))
                .getCause());
      } finally {
        release.countDown();
      }
    }
    f.query.complete();
    f.cleanup(1, 1);
  }
}
