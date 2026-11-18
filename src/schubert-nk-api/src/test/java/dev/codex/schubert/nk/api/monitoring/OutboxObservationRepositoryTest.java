package dev.codex.schubert.nk.api.monitoring;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.api.monitoring.OutboxAgeMetricRecorder.Ages;
import dev.codex.schubert.nk.api.monitoring.OutboxRowsMetricRecorder.Counts;
import dev.codex.schubert.nk.api.monitoring.OutboxRowsMetricRecorder.Status;
import dev.codex.schubert.nk.api.monitoring.persistence.OutboxObservationRepository;
import dev.codex.schubert.nk.api.monitoring.persistence.OutboxObservationRepository.Snapshot;
import java.lang.reflect.Proxy;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.time.Duration;
import java.time.Instant;
import java.time.OffsetDateTime;
import java.time.ZoneOffset;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.concurrent.Callable;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Test;

/** OUTBOXDB001..010/1664: own JDBC doubles only, not actual DB/driver/source admission. */
class OutboxObservationRepositoryTest {
  private static final int READ_ONLY_TRANSACTION_VARIANT = 1;
  private static final int ISOLATION_TRANSACTION_VARIANT = 2;
  private static final String FIXTURE_ERROR_F717E7D8 = "ERROR";
  private static final String FIXTURE_PENDING_B11DB31F = "PENDING";
  private static final String FIXTURE_OWNED_FIXTURE_FAILURE_CCD2F9F2 = "owned fixture failure";
  private static final String COUNT_READ_POINT = "count";
  private static final String ROWS_CLOSE_POINT = "RSclose";
  private static final String STATEMENT_CLOSE_POINT = "PSclose";
  private static final Instant AS_OF = Instant.EPOCH;
  private static final String SQL =
      "SELECT status, COUNT(*) AS row_count, MIN(created_at) AS oldest_created_at"
          + " FROM schubert.mq_outbox GROUP BY status";

  record Row(
      Optional<String> status, long count, boolean sqlNull, Optional<OffsetDateTime> oldest) {
    static Row row(String status, long count, long ageSeconds) {
      return new Row(
          Optional.of(status),
          count,
          false,
          Optional.of(AS_OF.minusSeconds(ageSeconds).atOffset(ZoneOffset.UTC)));
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
                    fault(STATEMENT_CLOSE_POINT);
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
                    cursor++;
                    return cursor < rows.size();
                  case "getString":
                    assertEquals("status", arguments[0]);
                    fault("status");
                    return rows.get(cursor).status().orElse(null);
                  case "getLong":
                    assertEquals("row_count", arguments[0]);
                    fault(COUNT_READ_POINT);
                    return rows.get(cursor).count();
                  case "getObject":
                    assertEquals("oldest_created_at", arguments[0]);
                    assertEquals(OffsetDateTime.class, arguments[1]);
                    fault("oldest");
                    return rows.get(cursor).oldest().orElse(null);
                  case "wasNull":
                    fault("wasNull");
                    return rows.get(cursor).sqlNull();
                  case "close":
                    closes.add("RS");
                    fault(ROWS_CLOSE_POINT);
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
  void outboxDb001ShuffledRowsHaveLiteralCountsAndAgesAfterReverseClose() throws SQLException {
    var f =
        new Fixture(
            Row.row(FIXTURE_ERROR_F717E7D8, 7, 11),
            Row.row(FIXTURE_PENDING_B11DB31F, 3, 2),
            Row.row("SENT", 5, 4));
    var actual = new OutboxObservationRepository().read(f.connection(), AS_OF);
    assertEquals(3, actual.counts().pending());
    assertEquals(5, actual.counts().sent());
    assertEquals(7, actual.counts().error());
    assertEquals(Duration.ofSeconds(2), actual.ages().pending());
    assertEquals(Duration.ofSeconds(4), actual.ages().sent());
    assertEquals(Duration.ofSeconds(11), actual.ages().error());
    f.complete();
  }

  @Test
  void outboxDb002EmptyAndSparseGroupsAreZeroOnlyAfterQueryCompletes() throws SQLException {
    var empty = new Fixture();
    var actual = new OutboxObservationRepository().read(empty.connection(), AS_OF);
    for (var status : Status.values()) {
      assertEquals(0, actual.counts().value(status));
      assertEquals(Duration.ZERO, actual.ages().value(status));
    }
    empty.complete();
    var sparse = new Fixture(Row.row(FIXTURE_PENDING_B11DB31F, Long.MAX_VALUE, 0));
    var value = new OutboxObservationRepository().read(sparse.connection(), AS_OF);
    assertEquals(Long.MAX_VALUE, value.counts().pending());
    assertEquals(0, value.counts().sent());
    assertEquals(0, value.counts().error());
    for (var status : Status.values()) assertEquals(Duration.ZERO, value.ages().value(status));
    sparse.complete();
  }

  @Test
  void outboxDb003NullAndWrongTransactionNeverPrepareOrMutateBorrowedConnection() {
    var repository = new OutboxObservationRepository();
    assertThrows(NullPointerException.class, () -> repository.read(null, AS_OF));
    var absentTime = new Fixture();
    assertThrows(NullPointerException.class, () -> repository.read(absentTime.connection(), null));
    assertEquals(0, absentTime.prepared);
    for (int variant = 0; variant < 3; variant++) {
      var f = new Fixture();
      if (variant == 0) f.autoCommit = true;
      if (variant == READ_ONLY_TRANSACTION_VARIANT) f.readOnly = false;
      if (variant == ISOLATION_TRANSACTION_VARIANT)
        f.isolation = Connection.TRANSACTION_SERIALIZABLE;
      assertEquals(
          "outbox metric source rejected",
          assertThrows(SQLException.class, () -> repository.read(f.connection(), AS_OF))
              .getMessage());
      assertEquals(0, f.prepared);
      assertTrue(f.closes.isEmpty());
    }
    for (var point : List.of("autoCommit", "readOnly", "isolation")) {
      var f = new Fixture();
      var fault = new SQLException("owned fixture transaction failure");
      f.faults.put(point, fault);
      assertSame(
          fault, assertThrows(SQLException.class, () -> repository.read(f.connection(), AS_OF)));
      assertEquals(0, f.prepared);
      assertTrue(f.closes.isEmpty());
    }
  }

  @Test
  void outboxDb004NullUnknownAndDuplicateStatusCannotReturnPartialValues() {
    var cases =
        List.of(
            new Fixture(
                new Row(
                    Optional.empty(),
                    1,
                    false,
                    Optional.of(OffsetDateTime.ofInstant(AS_OF, ZoneOffset.UTC)))),
            new Fixture(Row.row("pending-canary", 1, 0)),
            new Fixture(
                Row.row(FIXTURE_PENDING_B11DB31F, 1, 0), Row.row(FIXTURE_PENDING_B11DB31F, 2, 1)));
    for (var f : cases) {
      assertEquals(
          "outbox metric source rejected",
          assertThrows(
                  SQLException.class,
                  () -> new OutboxObservationRepository().read(f.connection(), AS_OF))
              .getMessage());
      f.complete();
    }
  }

  @Test
  void outboxDb005NullNonpositiveCountAndNullOrFutureTimeAreNotKnownZero() {
    var present = Optional.of(OffsetDateTime.ofInstant(AS_OF, ZoneOffset.UTC));
    var cases =
        List.of(
            new Fixture(new Row(Optional.of(FIXTURE_ERROR_F717E7D8), 1, true, present)),
            new Fixture(Row.row(FIXTURE_ERROR_F717E7D8, -1, 0)),
            new Fixture(Row.row(FIXTURE_ERROR_F717E7D8, 0, 0)),
            new Fixture(new Row(Optional.of("SENT"), 2, false, Optional.empty())),
            new Fixture(Row.row(FIXTURE_PENDING_B11DB31F, 3, -1)));
    for (var f : cases) {
      assertEquals(
          "outbox metric source rejected",
          assertThrows(
                  SQLException.class,
                  () -> new OutboxObservationRepository().read(f.connection(), AS_OF))
              .getMessage());
      f.complete();
    }
  }

  @Test
  void outboxDb006TypedOffsetTimeHasExactUtcAndCalendarBoundaryOracles() throws SQLException {
    var jst =
        new Fixture(
            new Row(
                Optional.of(FIXTURE_PENDING_B11DB31F),
                1,
                false,
                Optional.of(OffsetDateTime.parse("1970-01-01T08:59:58.500000+09:00"))));
    assertEquals(
        Duration.ofMillis(1500),
        new OutboxObservationRepository().read(jst.connection(), AS_OF).ages().pending());
    jst.complete();
    var earliest =
        new Fixture(
            new Row(
                Optional.of(FIXTURE_ERROR_F717E7D8),
                1,
                false,
                Optional.of(OffsetDateTime.parse("0001-01-01T00:00:00Z"))));
    var distant =
        new OutboxObservationRepository()
            .read(earliest.connection(), Instant.parse("9999-12-31T23:59:59.999999Z"));
    assertEquals(Duration.ofSeconds(315537897599L, 999999000), distant.ages().error());
    earliest.complete();
    var same = new Fixture(Row.row("SENT", 1, 0));
    assertEquals(
        Duration.ZERO,
        new OutboxObservationRepository().read(same.connection(), AS_OF).ages().sent());
    same.complete();
  }

  @Test
  void outboxDb007NullResourcesAndAcquisitionFailuresNeverRetryOrCloseConnection() {
    var none = new Fixture();
    none.nullStatement = true;
    assertThrows(
        SQLException.class, () -> new OutboxObservationRepository().read(none.connection(), AS_OF));
    assertEquals(1, none.prepared);
    assertEquals(0, none.executed);
    assertTrue(none.closes.isEmpty());
    var noRows = new Fixture();
    noRows.nullRows = true;
    assertThrows(
        SQLException.class,
        () -> new OutboxObservationRepository().read(noRows.connection(), AS_OF));
    assertEquals(List.of("PS"), noRows.closes);
    for (var point : List.of("prepare", "timeout", "execute")) {
      for (var fault :
          List.<Throwable>of(
              new SQLException(FIXTURE_OWNED_FIXTURE_FAILURE_CCD2F9F2),
              new IllegalStateException(FIXTURE_OWNED_FIXTURE_FAILURE_CCD2F9F2),
              new AssertionError(FIXTURE_OWNED_FIXTURE_FAILURE_CCD2F9F2))) {
        var f = new Fixture();
        f.faults.put(point, fault);
        assertSame(
            fault,
            assertThrows(
                fault.getClass(),
                () -> new OutboxObservationRepository().read(f.connection(), AS_OF)));
        assertEquals(1, f.prepared);
        assertEquals(point.equals("execute") ? 1 : 0, f.executed);
        assertEquals(point.equals("prepare") ? List.of() : List.of("PS"), f.closes);
      }
    }
  }

  @Test
  void outboxDb008ReadAndCloseFailuresPreserveOriginalIdentityAndSuppressedOrder() {
    for (var point :
        List.of(
            "next",
            "status",
            COUNT_READ_POINT,
            "wasNull",
            "oldest",
            ROWS_CLOSE_POINT,
            STATEMENT_CLOSE_POINT)) {
      for (var fault :
          List.<Throwable>of(
              new SQLException(FIXTURE_OWNED_FIXTURE_FAILURE_CCD2F9F2),
              new IllegalStateException(FIXTURE_OWNED_FIXTURE_FAILURE_CCD2F9F2),
              new AssertionError(FIXTURE_OWNED_FIXTURE_FAILURE_CCD2F9F2))) {
        var f = new Fixture(Row.row(FIXTURE_PENDING_B11DB31F, 3, 5));
        f.faults.put(point, fault);
        assertSame(
            fault,
            assertThrows(
                fault.getClass(),
                () -> new OutboxObservationRepository().read(f.connection(), AS_OF)));
        f.complete();
      }
    }
    var f = new Fixture(Row.row(FIXTURE_PENDING_B11DB31F, 3, 5));
    var primary = new SQLException("owned query failure");
    var rs = new SQLException("owned rows close failure");
    var ps = new SQLException("owned statement close failure");
    f.faults.put(COUNT_READ_POINT, primary);
    f.faults.put(ROWS_CLOSE_POINT, rs);
    f.faults.put(STATEMENT_CLOSE_POINT, ps);
    assertSame(
        primary,
        assertThrows(
            SQLException.class,
            () -> new OutboxObservationRepository().read(f.connection(), AS_OF)));
    assertEquals(List.of(rs, ps), List.of(primary.getSuppressed()));
    f.complete();
  }

  @Test
  void outboxDb009ParallelBorrowedConnectionsHaveNoCrossOwnerState() throws Exception {
    var repository = new OutboxObservationRepository();
    var tasks = new ArrayList<Callable<Long>>();
    for (int owner = 1; owner <= 64; owner++) {
      long count = owner;
      tasks.add(
          () -> {
            var f =
                new Fixture(
                    Row.row(FIXTURE_PENDING_B11DB31F, count, count),
                    Row.row(FIXTURE_ERROR_F717E7D8, 2, 4));
            var actual = repository.read(f.connection(), AS_OF);
            assertEquals(count, actual.counts().pending());
            assertEquals(2, actual.counts().error());
            assertEquals(0, actual.counts().sent());
            assertEquals(Duration.ofSeconds(count), actual.ages().pending());
            f.complete();
            return actual.counts().pending();
          });
    }
    var pool = Executors.newFixedThreadPool(8);
    try {
      var results = pool.invokeAll(tasks, 10, TimeUnit.SECONDS);
      for (int index = 0; index < results.size(); index++)
        assertEquals(index + 1L, results.get(index).get());
    } finally {
      pool.shutdownNow();
      assertTrue(pool.awaitTermination(10, TimeUnit.SECONDS));
    }
  }

  @Test
  void outboxDb010SnapshotInvariantsAndGeneratedContractsUseIndependentFixedValues() {
    var counts = new Counts(3, 5, 7);
    var ages = new Ages(Duration.ofSeconds(2), Duration.ofSeconds(4), Duration.ofSeconds(6));
    var actual = new Snapshot(counts, ages);
    Object sameInstance = actual;
    Object absent = null;
    Object otherType = "not snapshot";
    assertTrue(actual.equals(sameInstance));
    assertTrue(
        actual.equals(
            new Snapshot(
                new Counts(3, 5, 7),
                new Ages(Duration.ofSeconds(2), Duration.ofSeconds(4), Duration.ofSeconds(6)))));
    assertFalse(actual.equals(absent));
    assertFalse(actual.equals(otherType));
    assertFalse(actual.equals(new Snapshot(new Counts(4, 5, 7), ages)));
    assertFalse(
        actual.equals(
            new Snapshot(
                counts,
                new Ages(Duration.ofSeconds(3), Duration.ofSeconds(4), Duration.ofSeconds(6)))));
    assertSame(counts, actual.counts());
    assertSame(ages, actual.ages());
    assertEquals(96447, actual.hashCode());
    assertEquals(
        "Snapshot[counts=Counts[pending=3, sent=5, error=7], ages=Ages[pending=PT2S, sent=PT4S, error=PT6S]]",
        actual.toString());
    assertThrows(NullPointerException.class, () -> new Snapshot(null, ages));
    assertThrows(NullPointerException.class, () -> new Snapshot(counts, null));
  }

  @Test
  void outboxDb011SameReadAndCloseThrowablePreservesJdkSelfSuppressionAndReverseClose() {
    var repository = new OutboxObservationRepository();
    var rowFailure = new SQLException(FIXTURE_OWNED_FIXTURE_FAILURE_CCD2F9F2);
    var statementSecondary = new SQLException("owned fixture statement secondary");
    var rows = new Fixture(Row.row(FIXTURE_PENDING_B11DB31F, 3, 5));
    rows.faults.put(COUNT_READ_POINT, rowFailure);
    rows.faults.put(ROWS_CLOSE_POINT, rowFailure);
    rows.faults.put(STATEMENT_CLOSE_POINT, statementSecondary);
    var failedRows =
        assertThrows(
            IllegalArgumentException.class, () -> repository.read(rows.connection(), AS_OF));
    assertSame(rowFailure, failedRows.getCause());
    assertEquals(List.of(statementSecondary), List.of(failedRows.getSuppressed()));
    assertEquals(List.of(), List.of(rowFailure.getSuppressed()));
    rows.complete();

    var statementFailure = new SQLException(FIXTURE_OWNED_FIXTURE_FAILURE_CCD2F9F2);
    var statement = new Fixture();
    statement.faults.put("timeout", statementFailure);
    statement.faults.put(STATEMENT_CLOSE_POINT, statementFailure);
    var failedStatement =
        assertThrows(
            IllegalArgumentException.class, () -> repository.read(statement.connection(), AS_OF));
    assertSame(statementFailure, failedStatement.getCause());
    assertEquals(List.of(), List.of(failedStatement.getSuppressed()));
    assertEquals(List.of(), List.of(statementFailure.getSuppressed()));
    assertEquals(1, statement.prepared);
    assertEquals(0, statement.executed);
    assertEquals(1, statement.timeout);
    assertEquals(List.of("PS"), statement.closes);
  }
}
