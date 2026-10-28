package dev.codex.schubert.nk.api.monitoring;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTimeoutPreemptively;
import static org.junit.jupiter.api.Assertions.assertTrue;

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
  private static final String FIXTURE_READ_ONLY_A9812E1E = "read-only";
  private static final String FIXTURE_ISOLATION_AB1E8569 = "isolation";
  private static final String FIXTURE_BEGIN_FB45FB7B = "begin";
  private static final String FIXTURE_QUERY_4C4F28A0 = "query";
  private static final String FIXTURE_ROLLBACK_3770B198 = "rollback";
  private static final String FIXTURE_CLOSE_97959247 = "close";
  private static final String FIXTURE_OPEN_35FF74AE = "open";
  private static final String FIXTURE_TIME_C894B672 = "time";
  private static final String FIXTURE_DIAGNOSTIC_19A7ACC1 = "diagnostic";
  private static final String FIXTURE_FIXTURE_B086DE7B = "fixture";

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
                    calls.add(FIXTURE_READ_ONLY_A9812E1E);
                    assertEquals(true, args[0]);
                    fault(FIXTURE_READ_ONLY_A9812E1E);
                    readOnly = true;
                    return null;
                  case "setTransactionIsolation":
                    calls.add(FIXTURE_ISOLATION_AB1E8569);
                    assertEquals(Connection.TRANSACTION_READ_COMMITTED, args[0]);
                    fault(FIXTURE_ISOLATION_AB1E8569);
                    isolation = Connection.TRANSACTION_READ_COMMITTED;
                    return null;
                  case "setAutoCommit":
                    calls.add(FIXTURE_BEGIN_FB45FB7B);
                    assertEquals(false, args[0]);
                    fault(FIXTURE_BEGIN_FB45FB7B);
                    autoCommit = false;
                    return null;
                  case "isReadOnly":
                    calls.add("read-only?");
                    return readOnly;
                  case "getTransactionIsolation":
                    calls.add("isolation?");
                    return isolation;
                  case "prepareStatement":
                    calls.add(FIXTURE_QUERY_4C4F28A0);
                    fault(FIXTURE_QUERY_4C4F28A0);
                    return query.connection().prepareStatement((String) args[0]);
                  case FIXTURE_ROLLBACK_3770B198:
                    calls.add(FIXTURE_ROLLBACK_3770B198);
                    fault(FIXTURE_ROLLBACK_3770B198);
                    return null;
                  case FIXTURE_CLOSE_97959247:
                    calls.add(FIXTURE_CLOSE_97959247);
                    fault(FIXTURE_CLOSE_97959247);
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
                calls.add(FIXTURE_OPEN_35FF74AE);
                fault(FIXTURE_OPEN_35FF74AE);
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
          calls.add(FIXTURE_TIME_C894B672);
          unchecked(FIXTURE_TIME_C894B672);
          return nullTime ? null : Instant.EPOCH;
        }
      };
    }

    void unconfirmed(Throwable failure) {
      calls.add("unknown");
      unknown.add(failure);
      unchecked(FIXTURE_DIAGNOSTIC_19A7ACC1);
    }

    ApiReadOnlyObservationAttempt attempt() {
      return attempt(this::unconfirmed);
    }

    ApiReadOnlyObservationAttempt attempt(Consumer<Throwable> diagnostic) {
      return new ApiReadOnlyObservationAttempt(
          pool(), clock(), new OutboxObservationRepository(), diagnostic);
    }

    void cleanup(int rollbacks, int closes) {
      assertEquals(rollbacks, calls.stream().filter(FIXTURE_ROLLBACK_3770B198::equals).count());
      assertEquals(closes, calls.stream().filter(FIXTURE_CLOSE_97959247::equals).count());
      assertEquals(1, calls.stream().filter(FIXTURE_OPEN_35FF74AE::equals).count());
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
    assertEquals(point.equals(FIXTURE_CLOSE_97959247), value.hasUnconfirmedResource());
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
            FIXTURE_OPEN_35FF74AE,
            "auto?",
            FIXTURE_READ_ONLY_A9812E1E,
            FIXTURE_ISOLATION_AB1E8569,
            FIXTURE_BEGIN_FB45FB7B,
            FIXTURE_TIME_C894B672,
            "auto?",
            "read-only?",
            "isolation?",
            FIXTURE_QUERY_4C4F28A0,
            FIXTURE_ROLLBACK_3770B198,
            FIXTURE_CLOSE_97959247),
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
    assertEquals(List.of(FIXTURE_OPEN_35FF74AE), f.calls);
    assertThrows(IllegalStateException.class, value::read);
    f.cleanup(0, 0);
  }

  @Test
  void roAttempt007() {
    failure(FIXTURE_OPEN_35FF74AE, new SQLException(FIXTURE_FIXTURE_B086DE7B), 0, 0);
  }

  @Test
  void roAttempt008() {
    failure(FIXTURE_OPEN_35FF74AE, new IllegalStateException(FIXTURE_FIXTURE_B086DE7B), 0, 0);
  }

  @Test
  void roAttempt009() {
    failure(FIXTURE_OPEN_35FF74AE, new AssertionError(FIXTURE_FIXTURE_B086DE7B), 0, 0);
  }

  @Test
  void roAttempt010() {
    var f = rows();
    f.autoCommit = false;
    assertThrows(SQLException.class, f.attempt()::read);
    assertEquals(List.of(FIXTURE_OPEN_35FF74AE, "auto?", FIXTURE_CLOSE_97959247), f.calls);
    f.cleanup(0, 1);
  }

  @Test
  void roAttempt011() {
    failure("auto-check-1", new SQLException(FIXTURE_FIXTURE_B086DE7B), 0, 1);
  }

  @Test
  void roAttempt012() {
    failure(FIXTURE_READ_ONLY_A9812E1E, new SQLException(FIXTURE_FIXTURE_B086DE7B), 0, 1);
  }

  @Test
  void roAttempt013() {
    failure(FIXTURE_ISOLATION_AB1E8569, new IllegalStateException(FIXTURE_FIXTURE_B086DE7B), 0, 1);
  }

  @Test
  void roAttempt014() {
    failure(FIXTURE_BEGIN_FB45FB7B, new SQLException("ambiguous begin"), 1, 1);
  }

  @Test
  void roAttempt015() {
    failure(FIXTURE_TIME_C894B672, new IllegalStateException(FIXTURE_FIXTURE_B086DE7B), 1, 1);
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
    failure(FIXTURE_QUERY_4C4F28A0, new SQLException(FIXTURE_FIXTURE_B086DE7B), 1, 1);
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
    failure(FIXTURE_ROLLBACK_3770B198, new SQLException(FIXTURE_FIXTURE_B086DE7B), 1, 1);
  }

  @Test
  void roAttempt021() {
    failure(FIXTURE_ROLLBACK_3770B198, new AssertionError(FIXTURE_FIXTURE_B086DE7B), 1, 1);
  }

  @Test
  void roAttempt022() {
    var f = rows();
    var close = new SQLException(FIXTURE_CLOSE_97959247);
    f.faults.put(FIXTURE_CLOSE_97959247, close);
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
    failure(FIXTURE_CLOSE_97959247, new IllegalStateException(FIXTURE_FIXTURE_B086DE7B), 1, 1);
  }

  @Test
  void roAttempt024() {
    failure(FIXTURE_CLOSE_97959247, new AssertionError(FIXTURE_FIXTURE_B086DE7B), 1, 1);
  }

  @Test
  void roAttempt025() {
    var f = rows();
    var primary = new SQLException("read");
    var rollback = new SQLException(FIXTURE_ROLLBACK_3770B198);
    var close = new SQLException(FIXTURE_CLOSE_97959247);
    f.faults.put(FIXTURE_QUERY_4C4F28A0, primary);
    f.faults.put(FIXTURE_ROLLBACK_3770B198, rollback);
    f.faults.put(FIXTURE_CLOSE_97959247, close);
    assertSame(primary, assertThrows(SQLException.class, f.attempt()::read));
    assertArrayEquals(new Throwable[] {rollback, close}, primary.getSuppressed());
    assertEquals(List.of(close), f.unknown);
    f.cleanup(1, 1);
  }

  @Test
  void roAttempt026() {
    var f = rows();
    var primary = new SQLException("read");
    var fatal = new AssertionError(FIXTURE_ROLLBACK_3770B198);
    f.faults.put(FIXTURE_QUERY_4C4F28A0, primary);
    f.faults.put(FIXTURE_ROLLBACK_3770B198, fatal);
    f.faults.put(FIXTURE_CLOSE_97959247, new SQLException(FIXTURE_CLOSE_97959247));
    assertSame(fatal, assertThrows(AssertionError.class, f.attempt()::read));
    f.cleanup(1, 1);
    assertEquals(1, f.unknown.size());
  }

  @Test
  void roAttempt027() {
    var f = rows();
    var close = new SQLException(FIXTURE_CLOSE_97959247);
    var diagnostic = new IllegalStateException(FIXTURE_DIAGNOSTIC_19A7ACC1);
    f.faults.put(FIXTURE_CLOSE_97959247, close);
    f.faults.put(FIXTURE_DIAGNOSTIC_19A7ACC1, diagnostic);
    assertSame(close, assertThrows(SQLException.class, f.attempt()::read));
    assertArrayEquals(new Throwable[] {diagnostic}, close.getSuppressed());
    f.cleanup(1, 1);
  }

  @Test
  void roAttempt028() {
    var f = rows();
    var fatal = new AssertionError(FIXTURE_DIAGNOSTIC_19A7ACC1);
    f.faults.put(FIXTURE_CLOSE_97959247, new SQLException(FIXTURE_CLOSE_97959247));
    f.faults.put(FIXTURE_DIAGNOSTIC_19A7ACC1, fatal);
    assertSame(fatal, assertThrows(AssertionError.class, f.attempt()::read));
    f.cleanup(1, 1);
  }

  @Test
  void roAttempt029() {
    var f = rows();
    var same = new SQLException("same");
    f.faults.put(FIXTURE_QUERY_4C4F28A0, same);
    f.faults.put(FIXTURE_ROLLBACK_3770B198, same);
    f.faults.put(FIXTURE_CLOSE_97959247, same);
    assertSame(same, assertThrows(SQLException.class, f.attempt()::read));
    assertEquals(0, same.getSuppressed().length);
    f.cleanup(1, 1);
  }

  private static final class SuppressionDisabled extends RuntimeException {
    private static final long serialVersionUID = 1L;

    private SuppressionDisabled() {
      super(FIXTURE_FIXTURE_B086DE7B, null, false, false);
    }
  }

  @Test
  void roAttempt030() {
    var f = rows();
    var fatal = new AssertionError(FIXTURE_CLOSE_97959247);
    f.faults.put(FIXTURE_QUERY_4C4F28A0, new SuppressionDisabled());
    f.faults.put(FIXTURE_CLOSE_97959247, fatal);
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
    f.faults.put(FIXTURE_QUERY_4C4F28A0, primary);
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
