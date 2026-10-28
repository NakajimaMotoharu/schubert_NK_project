package dev.codex.schubert.nk.web.monitoring;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.web.monitoring.WebOutboxMetricRecorder.Status;
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

/** WEBOBXDB001..010/1721: own JDBC doubles only, not actual DB/driver/source admission. */
class WebOutboxObservationRepositoryTest {
  private static final String FIXTURE_PREPARE_1F4EE68F = "prepare";
  private static final String FIXTURE_TIMEOUT_492BD020 = "timeout";
  private static final String FIXTURE_EXECUTE_7FB37A54 = "execute";
  private static final String FIXTURE_NEXT_CA1733B5 = "next";
  private static final String FIXTURE_STATUS_CFC31BCC = "status";
  private static final String FIXTURE_COUNT_CC3EC73C = "count";
  private static final String FIXTURE_WASNULL_89F0F5E0 = "wasNull";
  private static final String FIXTURE_ERROR_F717E7D8 = "ERROR";
  private static final String FIXTURE_PENDING_B11DB31F = "PENDING";
  private static final String FIXTURE_SENT_6C701E27 = "SENT";
  static final Instant AS_OF = Instant.EPOCH;
  private static final String SQL =
      "SELECT status, COUNT(*) AS row_count, MIN(created_at) AS oldest_created_at"
          + " FROM schubert_web_session.web_log_outbox GROUP BY status";

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
                    fault(FIXTURE_PREPARE_1F4EE68F);
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
                    fault(FIXTURE_TIMEOUT_492BD020);
                    return null;
                  case "executeQuery":
                    executed++;
                    fault(FIXTURE_EXECUTE_7FB37A54);
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
                  case FIXTURE_NEXT_CA1733B5:
                    fault(FIXTURE_NEXT_CA1733B5);
                    return ++cursor < rows.size();
                  case "getString":
                    assertEquals(FIXTURE_STATUS_CFC31BCC, arguments[0]);
                    fault(FIXTURE_STATUS_CFC31BCC);
                    return rows.get(cursor).status().orElse(null);
                  case "getLong":
                    assertEquals("row_count", arguments[0]);
                    fault(FIXTURE_COUNT_CC3EC73C);
                    return rows.get(cursor).count();
                  case "getObject":
                    assertEquals("oldest_created_at", arguments[0]);
                    assertEquals(OffsetDateTime.class, arguments[1]);
                    fault("oldest");
                    return rows.get(cursor).oldest().orElse(null);
                  case FIXTURE_WASNULL_89F0F5E0:
                    fault(FIXTURE_WASNULL_89F0F5E0);
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
  void webObxDb001ShuffledRowsHaveLiteralCountsAndAgesOnlyAfterReverseResourceClose()
      throws SQLException {
    var f =
        new Fixture(
            Row.row(FIXTURE_ERROR_F717E7D8, 7, 11),
            Row.row(FIXTURE_PENDING_B11DB31F, 3, 2),
            Row.row(FIXTURE_SENT_6C701E27, 5, 4));
    var value = new WebOutboxObservationRepository().read(f.connection(), AS_OF);
    assertEquals(3, value.pending());
    assertEquals(5, value.sent());
    assertEquals(7, value.error());
    assertEquals(Duration.ofSeconds(2), value.pendingAge());
    assertEquals(Duration.ofSeconds(4), value.sentAge());
    assertEquals(Duration.ofSeconds(11), value.errorAge());
    f.complete();
  }

  @Test
  void webObxDb002EmptyAndAbsentStatusBecomeKnownZeroOnlyAfterCompleteSuccessfulQuery()
      throws SQLException {
    var empty = new Fixture();
    var a = new WebOutboxObservationRepository().read(empty.connection(), AS_OF);
    for (var status : List.of(Status.PENDING, Status.SENT, Status.ERROR)) {
      assertEquals(0, a.count(status));
      assertEquals(Duration.ZERO, a.age(status));
    }
    empty.complete();
    var sparse = new Fixture(Row.row(FIXTURE_PENDING_B11DB31F, Long.MAX_VALUE, 0));
    var b = new WebOutboxObservationRepository().read(sparse.connection(), AS_OF);
    assertEquals(Long.MAX_VALUE, b.pending());
    assertEquals(0, b.sent());
    assertEquals(0, b.error());
    for (var status : List.of(Status.PENDING, Status.SENT, Status.ERROR))
      assertEquals(Duration.ZERO, b.age(status));
    sparse.complete();
  }

  @Test
  void webObxDb003TypedOffsetTimeFractionAndCalendarBoundaryHaveIndependentUtcOracles()
      throws SQLException {
    var jst =
        new Fixture(
            new Row(
                Optional.of(FIXTURE_PENDING_B11DB31F),
                1,
                false,
                Optional.of(OffsetDateTime.parse("1970-01-01T08:59:58.500000+09:00"))));
    assertEquals(
        Duration.ofMillis(1500),
        new WebOutboxObservationRepository().read(jst.connection(), AS_OF).pendingAge());
    jst.complete();
    var earliest =
        new Fixture(
            new Row(
                Optional.of(FIXTURE_ERROR_F717E7D8),
                Long.MAX_VALUE,
                false,
                Optional.of(OffsetDateTime.parse("0001-01-01T00:00:00Z"))));
    var distant =
        new WebOutboxObservationRepository()
            .read(earliest.connection(), Instant.parse("9999-12-31T23:59:59.999999Z"));
    assertEquals(Long.MAX_VALUE, distant.error());
    assertEquals(Duration.ofSeconds(315537897599L, 999999000), distant.errorAge());
    assertEquals(315537897600.0, distant.ageSeconds(Status.ERROR));
    earliest.complete();
    var same = new Fixture(Row.row(FIXTURE_SENT_6C701E27, 1, 0));
    assertEquals(
        Duration.ZERO,
        new WebOutboxObservationRepository().read(same.connection(), AS_OF).sentAge());
    same.complete();
  }

  @Test
  void webObxDb004NullOrWrongTransactionRejectsBeforeQueryAndNeverMutatesBorrowedConnection() {
    var repo = new WebOutboxObservationRepository();
    assertThrows(NullPointerException.class, () -> repo.read(null, AS_OF));
    var absent = new Fixture();
    assertThrows(NullPointerException.class, () -> repo.read(absent.connection(), null));
    assertEquals(0, absent.prepared);
    for (int variant = 0; variant < 3; variant++) {
      var f = new Fixture();
      if (variant == 0) f.autoCommit = true;
      if (variant == 1) f.readOnly = false;
      if (variant == 2) f.isolation = Connection.TRANSACTION_SERIALIZABLE;
      assertEquals(
          "Web outbox metric source rejected",
          assertThrows(SQLException.class, () -> repo.read(f.connection(), AS_OF)).getMessage());
      assertEquals(0, f.prepared);
      assertTrue(f.closes.isEmpty());
    }
  }

  @Test
  void
      webObxDb005UnknownDuplicateNullOrNonpositiveCountAndInvalidTimestampNeverReturnPartialSuccess() {
    var now = Optional.of(AS_OF.atOffset(ZoneOffset.UTC));
    var cases = new ArrayList<Fixture>();
    cases.add(new Fixture(new Row(Optional.empty(), 1, false, now)));
    for (String bad : List.of("", "pending", "UNKNOWN", "PENDING canary"))
      cases.add(new Fixture(Row.row(bad, 1, 0)));
    cases.add(
        new Fixture(
            Row.row(FIXTURE_PENDING_B11DB31F, 1, 0), Row.row(FIXTURE_PENDING_B11DB31F, 2, 1)));
    cases.add(new Fixture(new Row(Optional.of(FIXTURE_ERROR_F717E7D8), 1, true, now)));
    for (long invalid : List.of(0L, -1L, Long.MIN_VALUE))
      cases.add(new Fixture(Row.row(FIXTURE_ERROR_F717E7D8, invalid, 0)));
    cases.add(new Fixture(new Row(Optional.of(FIXTURE_SENT_6C701E27), 2, false, Optional.empty())));
    cases.add(
        new Fixture(
            new Row(
                Optional.of(FIXTURE_PENDING_B11DB31F),
                3,
                false,
                Optional.of(AS_OF.plusNanos(1).atOffset(ZoneOffset.UTC)))));
    for (var f : cases) {
      assertEquals(
          "Web outbox metric source rejected",
          assertThrows(
                  SQLException.class,
                  () -> new WebOutboxObservationRepository().read(f.connection(), AS_OF))
              .getMessage());
      f.complete();
    }
  }

  @Test
  void
      webObxDb006SqlFailuresAtEachAcquisitionOrReadPointKeepIdentityAndOnlyAcquiredResourcesClose() {
    for (String point :
        List.of(
            "autoCommit",
            "readOnly",
            "isolation",
            FIXTURE_PREPARE_1F4EE68F,
            FIXTURE_TIMEOUT_492BD020,
            FIXTURE_EXECUTE_7FB37A54,
            FIXTURE_NEXT_CA1733B5,
            FIXTURE_STATUS_CFC31BCC,
            FIXTURE_COUNT_CC3EC73C,
            FIXTURE_WASNULL_89F0F5E0,
            "oldest")) {
      var f = new Fixture(Row.row(FIXTURE_PENDING_B11DB31F, 3, 5));
      var failure = new SQLException("owned JDBC fixture");
      f.faults.put(point, failure);
      assertSame(
          failure,
          assertThrows(
              SQLException.class,
              () -> new WebOutboxObservationRepository().read(f.connection(), AS_OF)));
      if (List.of("autoCommit", "readOnly", "isolation").contains(point)) {
        assertEquals(0, f.prepared);
        assertTrue(f.closes.isEmpty());
      } else if (point.equals(FIXTURE_PREPARE_1F4EE68F)) {
        assertEquals(1, f.prepared);
        assertEquals(0, f.executed);
        assertTrue(f.closes.isEmpty());
      } else if (point.equals(FIXTURE_TIMEOUT_492BD020) || point.equals(FIXTURE_EXECUTE_7FB37A54)) {
        assertEquals(1, f.prepared);
        assertEquals(point.equals(FIXTURE_EXECUTE_7FB37A54) ? 1 : 0, f.executed);
        assertEquals(List.of("PS"), f.closes);
      } else f.complete();
    }
  }

  @Test
  void webObxDb007NullResourcesAndUncheckedFailuresRemainAbnormalAndNeverRetry() {
    var none = new Fixture();
    none.nullStatement = true;
    assertThrows(
        SQLException.class,
        () -> new WebOutboxObservationRepository().read(none.connection(), AS_OF));
    assertEquals(1, none.prepared);
    assertEquals(0, none.executed);
    assertTrue(none.closes.isEmpty());
    var noRows = new Fixture();
    noRows.nullRows = true;
    assertThrows(
        SQLException.class,
        () -> new WebOutboxObservationRepository().read(noRows.connection(), AS_OF));
    assertEquals(List.of("PS"), noRows.closes);
    for (String point :
        List.of(
            FIXTURE_PREPARE_1F4EE68F,
            FIXTURE_TIMEOUT_492BD020,
            FIXTURE_EXECUTE_7FB37A54,
            FIXTURE_NEXT_CA1733B5,
            FIXTURE_STATUS_CFC31BCC,
            FIXTURE_COUNT_CC3EC73C,
            FIXTURE_WASNULL_89F0F5E0,
            "oldest"))
      for (var failure :
          List.<Throwable>of(
              new IllegalStateException("owned JDBC fixture"),
              new AssertionError("owned JDBC fixture"))) {
        var f = new Fixture(Row.row(FIXTURE_PENDING_B11DB31F, 3, 5));
        f.faults.put(point, failure);
        assertSame(
            failure,
            assertThrows(
                failure.getClass(),
                () -> new WebOutboxObservationRepository().read(f.connection(), AS_OF)));
        assertEquals(1, f.prepared);
        if (point.equals(FIXTURE_PREPARE_1F4EE68F)) assertTrue(f.closes.isEmpty());
        else if (point.equals(FIXTURE_TIMEOUT_492BD020) || point.equals(FIXTURE_EXECUTE_7FB37A54))
          assertEquals(List.of("PS"), f.closes);
        else f.complete();
      }
  }

  @Test
  void webObxDb008CloseFailuresKeepOriginalAndSuppressedOrderWithoutBorrowedConnectionChanges() {
    for (String point : List.of("RSclose", "PSclose"))
      for (var failure :
          List.<Throwable>of(
              new SQLException("owned close"),
              new IllegalStateException("owned close"),
              new AssertionError("owned close"))) {
        var f = new Fixture(Row.row(FIXTURE_PENDING_B11DB31F, 3, 5));
        f.faults.put(point, failure);
        assertSame(
            failure,
            assertThrows(
                failure.getClass(),
                () -> new WebOutboxObservationRepository().read(f.connection(), AS_OF)));
        f.complete();
      }
    var f = new Fixture(Row.row(FIXTURE_PENDING_B11DB31F, 3, 5));
    var primary = new SQLException("owned count");
    var rs = new SQLException("owned rows close");
    var ps = new SQLException("owned statement close");
    f.faults.put(FIXTURE_COUNT_CC3EC73C, primary);
    f.faults.put("RSclose", rs);
    f.faults.put("PSclose", ps);
    assertSame(
        primary,
        assertThrows(
            SQLException.class,
            () -> new WebOutboxObservationRepository().read(f.connection(), AS_OF)));
    assertEquals(List.of(rs, ps), List.of(primary.getSuppressed()));
    f.complete();
  }

  @Test
  void webObxDb009AllSixStatusOrdersUseOnlyLiteralReadonlySqlAndMetadataColumns()
      throws SQLException {
    var p = Row.row(FIXTURE_PENDING_B11DB31F, 3, 2);
    var s = Row.row(FIXTURE_SENT_6C701E27, 5, 4);
    var e = Row.row(FIXTURE_ERROR_F717E7D8, 7, 11);
    for (var order :
        List.of(
            List.of(p, s, e),
            List.of(p, e, s),
            List.of(s, p, e),
            List.of(s, e, p),
            List.of(e, p, s),
            List.of(e, s, p))) {
      var f = new Fixture(order.toArray(Row[]::new));
      var value = new WebOutboxObservationRepository().read(f.connection(), AS_OF);
      assertEquals(3, value.pending());
      assertEquals(5, value.sent());
      assertEquals(7, value.error());
      assertEquals(Duration.ofSeconds(2), value.pendingAge());
      assertEquals(Duration.ofSeconds(4), value.sentAge());
      assertEquals(Duration.ofSeconds(11), value.errorAge());
      f.complete();
    }
  }

  @Test
  void webObxDb010ParallelIndependentConnectionsAndInstantsNeverShareMutableRepositoryState()
      throws Exception {
    var repo = new WebOutboxObservationRepository();
    var tasks = new ArrayList<Callable<Long>>();
    for (int index = 1; index <= 64; index++) {
      long count = index;
      tasks.add(
          () -> {
            var f =
                new Fixture(
                    Row.row(FIXTURE_PENDING_B11DB31F, count, count),
                    Row.row(FIXTURE_ERROR_F717E7D8, 2, 4));
            var actual = repo.read(f.connection(), AS_OF);
            assertEquals(count, actual.pending());
            assertEquals(2, actual.error());
            assertEquals(0, actual.sent());
            assertEquals(Duration.ofSeconds(count), actual.pendingAge());
            f.complete();
            return actual.pending();
          });
    }
    try (var pool = Executors.newFixedThreadPool(8)) {
      var results = pool.invokeAll(tasks, 5, TimeUnit.SECONDS);
      for (int index = 0; index < 64; index++)
        assertEquals(index + 1L, results.get(index).get(5, TimeUnit.SECONDS));
    }
    var later = new Fixture(Row.row(FIXTURE_PENDING_B11DB31F, 1, 3));
    assertEquals(
        Duration.ofSeconds(4), repo.read(later.connection(), AS_OF.plusSeconds(1)).pendingAge());
    later.complete();
  }
}
