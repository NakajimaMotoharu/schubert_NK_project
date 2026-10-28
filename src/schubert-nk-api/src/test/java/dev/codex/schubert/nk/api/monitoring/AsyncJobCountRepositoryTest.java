package dev.codex.schubert.nk.api.monitoring;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.api.monitoring.AsyncJobMetricRecorder.State;
import dev.codex.schubert.nk.api.monitoring.persistence.AsyncJobCountRepository;
import java.lang.reflect.Proxy;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.concurrent.Callable;
import java.util.concurrent.Executors;
import org.junit.jupiter.api.Test;

/**
 * ASYNCDB001..008: owned JDBC doubles only; SQL/count/ownership oracles independent of production.
 */
class AsyncJobCountRepositoryTest {
  private static final String FIXTURE_ERROR_F717E7D8 = "ERROR";
  private static final String FIXTURE_RECEIVED_35302D54 = "RECEIVED";
  private static final String SQL =
      "SELECT state, COUNT(*) AS job_count FROM schubert.async_jobs GROUP BY state";

  record Row(Optional<String> state, long count, boolean sqlNull) {
    static Row row(String state, long count) {
      return new Row(Optional.of(state), count, false);
    }
  }

  static final class Fixture {
    final List<Row> rows;
    final List<String> closes = new ArrayList<>();
    final Map<String, Throwable> faults = new HashMap<>();
    boolean autoCommit;
    boolean readOnly = true;
    int isolation = Connection.TRANSACTION_READ_COMMITTED;
    boolean nullStatement;
    boolean nullRows;
    int prepared;
    int executed;
    int timeout;
    int cursor = -1;
    Runnable beforeStatementClose = () -> {};

    Fixture(Row... rows) {
      this.rows = List.of(rows);
    }

    private void fault(String point) throws Throwable {
      var failure = faults.get(point);
      if (failure != null) throw failure;
    }

    Connection connection() {
      return Connection.class.cast(
          Proxy.newProxyInstance(
              Connection.class.getClassLoader(),
              new Class<?>[] {Connection.class},
              (object, method, arguments) -> {
                switch (method.getName()) {
                  case "getAutoCommit":
                    fault("autoCommit");
                    return autoCommit;
                  case "isReadOnly":
                    fault("readOnly");
                    return readOnly;
                  case "getTransactionIsolation":
                    fault("isolation");
                    return isolation;
                  case "prepareStatement":
                    prepared++;
                    assertEquals(SQL, arguments[0]);
                    fault("prepare");
                    return nullStatement ? null : statement();
                  default:
                    throw new AssertionError("borrowed connection must not be mutated or closed");
                }
              }));
    }

    private PreparedStatement statement() {
      return PreparedStatement.class.cast(
          Proxy.newProxyInstance(
              PreparedStatement.class.getClassLoader(),
              new Class<?>[] {PreparedStatement.class},
              (object, method, arguments) -> {
                switch (method.getName()) {
                  case "setQueryTimeout":
                    timeout = (Integer) arguments[0];
                    assertEquals(1, timeout);
                    fault("timeout");
                    return null;
                  case "executeQuery":
                    executed++;
                    fault("execute");
                    return nullRows ? null : result();
                  case "close":
                    beforeStatementClose.run();
                    closes.add("PS");
                    fault("PSclose");
                    return null;
                  default:
                    throw new AssertionError("unexpected prepared-statement operation");
                }
              }));
    }

    private ResultSet result() {
      return ResultSet.class.cast(
          Proxy.newProxyInstance(
              ResultSet.class.getClassLoader(),
              new Class<?>[] {ResultSet.class},
              (object, method, arguments) -> {
                switch (method.getName()) {
                  case "next":
                    fault("next");
                    return ++cursor < rows.size();
                  case "getString":
                    assertEquals("state", arguments[0]);
                    fault("state");
                    return rows.get(cursor).state().orElse(null);
                  case "getLong":
                    assertEquals("job_count", arguments[0]);
                    fault("count");
                    return rows.get(cursor).count();
                  case "wasNull":
                    fault("wasNull");
                    return rows.get(cursor).sqlNull();
                  case "close":
                    closes.add("RS");
                    fault("RSclose");
                    return null;
                  default:
                    throw new AssertionError("unexpected result-set operation");
                }
              }));
    }

    void complete() {
      assertEquals(1, prepared);
      assertEquals(1, executed);
      assertEquals(1, timeout);
      assertEquals(List.of("RS", "PS"), closes);
    }
  }

  @Test
  void asyncDb001ShuffledFiveRowsHaveIndependentCountsAndBorrowedOwnership() throws SQLException {
    var f =
        new Fixture(
            Row.row("CANCELLED", 5),
            Row.row(FIXTURE_ERROR_F717E7D8, 4),
            Row.row(FIXTURE_RECEIVED_35302D54, 1),
            Row.row("COMPLETED", 3),
            Row.row("PROCESSING", 2));
    var actual = new AsyncJobCountRepository().read(f.connection());
    assertEquals(15, actual.totalJobs());
    assertEquals(1, actual.value(State.RECEIVED));
    assertEquals(2, actual.value(State.PROCESSING));
    assertEquals(3, actual.value(State.COMPLETED));
    assertEquals(4, actual.value(State.ERROR));
    assertEquals(5, actual.value(State.CANCELLED));
    f.complete();
  }

  @Test
  void asyncDb002EmptyAndSparseGroupsAreKnownZeroOnlyAfterSuccessfulQuery() throws SQLException {
    var empty = new Fixture();
    var zero = new AsyncJobCountRepository().read(empty.connection());
    assertEquals(0, zero.totalJobs());
    for (var state : State.values()) assertEquals(0, zero.value(state));
    empty.complete();
    var sparse =
        new Fixture(Row.row(FIXTURE_RECEIVED_35302D54, 7), Row.row(FIXTURE_ERROR_F717E7D8, 3));
    var actual = new AsyncJobCountRepository().read(sparse.connection());
    assertEquals(10, actual.totalJobs());
    assertEquals(7, actual.value(State.RECEIVED));
    assertEquals(3, actual.value(State.ERROR));
    assertEquals(0, actual.value(State.PROCESSING));
    assertEquals(0, actual.value(State.COMPLETED));
    assertEquals(0, actual.value(State.CANCELLED));
    sparse.complete();
  }

  @Test
  void asyncDb003NullOrWrongTransactionCannotPrepareOrMutateConnection() {
    var repository = new AsyncJobCountRepository();
    assertThrows(NullPointerException.class, () -> repository.read(null));
    for (int variant = 0; variant < 3; variant++) {
      var f = new Fixture();
      if (variant == 0) f.autoCommit = true;
      if (variant == 1) f.readOnly = false;
      if (variant == 2) f.isolation = Connection.TRANSACTION_SERIALIZABLE;
      assertEquals(
          "async metric source rejected",
          assertThrows(SQLException.class, () -> repository.read(f.connection())).getMessage());
      assertEquals(0, f.prepared);
      assertEquals(0, f.executed);
      assertTrue(f.closes.isEmpty());
    }
    for (var point : List.of("autoCommit", "readOnly", "isolation")) {
      var f = new Fixture();
      var fault = new SQLException("owned fixture contract failure");
      f.faults.put(point, fault);
      assertSame(fault, assertThrows(SQLException.class, () -> repository.read(f.connection())));
      assertEquals(0, f.prepared);
      assertTrue(f.closes.isEmpty());
    }
  }

  @Test
  void asyncDb004NullUnknownNegativeAndDuplicateRowsCannotPublishPartialCounts() {
    var cases =
        List.of(
            new Fixture(new Row(Optional.empty(), 1, false)),
            new Fixture(new Row(Optional.of(FIXTURE_RECEIVED_35302D54), 0, true)),
            new Fixture(Row.row("received-canary", 1)),
            new Fixture(Row.row(FIXTURE_ERROR_F717E7D8, -1)),
            new Fixture(
                Row.row(FIXTURE_RECEIVED_35302D54, 1), Row.row(FIXTURE_RECEIVED_35302D54, 2)));
    for (var f : cases) {
      var failure =
          assertThrows(
              SQLException.class, () -> new AsyncJobCountRepository().read(f.connection()));
      assertEquals("async metric source rejected", failure.getMessage());
      f.complete();
    }
  }

  @Test
  void asyncDb005MaximumLongIsExactAndTotalOverflowCannotWrap() throws SQLException {
    var maximum = new Fixture(Row.row("COMPLETED", Long.MAX_VALUE));
    var actual = new AsyncJobCountRepository().read(maximum.connection());
    assertEquals(Long.MAX_VALUE, actual.totalJobs());
    assertEquals(Long.MAX_VALUE, actual.value(State.COMPLETED));
    maximum.complete();
    var overflow =
        new Fixture(
            Row.row(FIXTURE_RECEIVED_35302D54, Long.MAX_VALUE), Row.row(FIXTURE_ERROR_F717E7D8, 1));
    var failure =
        assertThrows(
            SQLException.class, () -> new AsyncJobCountRepository().read(overflow.connection()));
    assertEquals("async metric source rejected", failure.getMessage());
    assertTrue(failure.getCause() instanceof ArithmeticException);
    overflow.complete();
  }

  @Test
  void asyncDb006NullResourcesAndPreparationFaultsPreserveOriginalFailureWithoutRetry() {
    var noStatement = new Fixture();
    noStatement.nullStatement = true;
    assertThrows(
        SQLException.class, () -> new AsyncJobCountRepository().read(noStatement.connection()));
    assertEquals(1, noStatement.prepared);
    assertEquals(0, noStatement.executed);
    assertTrue(noStatement.closes.isEmpty());
    var noRows = new Fixture();
    noRows.nullRows = true;
    assertThrows(SQLException.class, () -> new AsyncJobCountRepository().read(noRows.connection()));
    assertEquals(List.of("PS"), noRows.closes);
    for (var point : List.of("prepare", "timeout", "execute")) {
      for (var fault :
          List.<Throwable>of(
              new SQLException("owned fixture failure"),
              new IllegalStateException("owned fixture failure"),
              new AssertionError("owned fixture failure"))) {
        var f = new Fixture();
        f.faults.put(point, fault);
        assertSame(
            fault,
            assertThrows(
                fault.getClass(), () -> new AsyncJobCountRepository().read(f.connection())));
        assertEquals(1, f.prepared);
        assertEquals(point.equals("execute") ? 1 : 0, f.executed);
        assertEquals(point.equals("prepare") ? List.of() : List.of("PS"), f.closes);
      }
    }
  }

  @Test
  void asyncDb007ReadAndCloseFaultsKeepIdentityAndSuppressionWithoutCauseTraversal() {
    for (var point : List.of("next", "state", "count", "wasNull", "RSclose", "PSclose")) {
      var f = new Fixture(Row.row(FIXTURE_RECEIVED_35302D54, 3));
      var primary = new SQLException("owned cyclic fixture failure");
      var cause = new SQLException("owned cycle peer");
      primary.initCause(cause);
      cause.initCause(primary);
      f.faults.put(point, primary);
      assertSame(
          primary,
          assertThrows(
              SQLException.class, () -> new AsyncJobCountRepository().read(f.connection())));
      f.complete();
    }
    var f = new Fixture(Row.row(FIXTURE_RECEIVED_35302D54, 3));
    var primary = new SQLException("owned query failure");
    var rs = new SQLException("owned rows-close failure");
    var ps = new SQLException("owned statement-close failure");
    f.faults.put("count", primary);
    f.faults.put("RSclose", rs);
    f.faults.put("PSclose", ps);
    assertSame(
        primary,
        assertThrows(SQLException.class, () -> new AsyncJobCountRepository().read(f.connection())));
    assertEquals(List.of(rs, ps), List.of(primary.getSuppressed()));
    f.complete();
  }

  @Test
  void asyncDb008ParallelBorrowedConnectionsHaveNoCrossOwnerState() throws Exception {
    var repository = new AsyncJobCountRepository();
    var tasks = new ArrayList<Callable<Long>>();
    for (int owner = 0; owner < 64; owner++) {
      long count = owner;
      tasks.add(
          () -> {
            var f = new Fixture(Row.row("PROCESSING", count), Row.row(FIXTURE_ERROR_F717E7D8, 2));
            var actual = repository.read(f.connection());
            assertEquals(count, actual.value(State.PROCESSING));
            assertEquals(2, actual.value(State.ERROR));
            assertEquals(0, actual.value(State.RECEIVED));
            f.complete();
            return actual.totalJobs();
          });
    }
    try (var pool = Executors.newFixedThreadPool(8)) {
      var results = pool.invokeAll(tasks);
      for (int owner = 0; owner < results.size(); owner++)
        assertEquals(owner + 2L, results.get(owner).get());
    }
  }
}
