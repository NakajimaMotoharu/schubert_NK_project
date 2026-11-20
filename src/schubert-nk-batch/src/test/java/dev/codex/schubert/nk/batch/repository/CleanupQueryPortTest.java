package dev.codex.schubert.nk.batch.repository;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.lang.reflect.Proxy;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.time.Instant;
import java.time.ZoneOffset;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.function.Executable;

/** CLNQUERY001..010: hand-written SQL and JDBC rows, no actual DB/DELETE or owner. */
final class CleanupQueryPortTest {
  private static final String TEXT_COMPLETE = "complete";
  private static final String TEXT_DELETED_COUNT = "deleted_count";
  private static final String TEXT_REASON_CODE = "reason_code";
  private static final String TEXT_SKIPPED_COUNT = "skipped_count";
  private static final String TEXT_STATEMENTCLOSE = "statementClose";
  private static final String TEXT_TARGET_COUNT = "target_count";
  private static final Instant CUTOFF = Instant.parse("2026-11-05T00:00:00.123456Z");
  private static final BatchRun RUN = new BatchRun(new UUID(0, 1), CUTOFF);
  private static final String FIXED = "batch repository operation failed";
  private static final Map<CleanupKind, String> SUFFIXES =
      Map.of(
          CleanupKind.NOTIFICATIONS,
          "notifications",
          CleanupKind.QUESTIONS,
          "questions",
          CleanupKind.SESSIONS,
          "sessions",
          CleanupKind.OUTBOX,
          "message_stores",
          CleanupKind.LOGS,
          "logs",
          CleanupKind.WEB_RECEIPTS,
          "web_receipt_references",
          CleanupKind.BATCH_RUNS,
          "batch_runs",
          CleanupKind.INBOX_PROGRESS,
          "inbox_progress",
          CleanupKind.LOG_PROGRESS,
          "log_progress");
  private static final String PROGRESS_SQL =
      "select target_count,deleted_count,skipped_count,complete from"
          + " schubert.maintenance_read_log_cleanup_progress(?,?)";

  @Test
  void allNineFixedQueriesBindOnlyLiteralUuidUtcCutoffAndIntegerLimit() {
    for (CleanupKind kind : SUFFIXES.keySet()) {
      Fixture fixture = new Fixture(false);
      fixture.kind = kind;
      var actual = (CleanupChunk) fixture.call();
      assertEquals(
          "select target_count,deleted_count,skipped_count,reason_code from"
              + " schubert.maintenance_cleanup_"
              + SUFFIXES.get(kind)
              + "(?,?,?)",
          fixture.sql);
      assertEquals(
          Map.of(
              1,
              new UUID(0, 1),
              2,
              Instant.parse("2026-11-05T00:00:00.123456Z").atOffset(ZoneOffset.UTC),
              3,
              1000),
          fixture.bindings);
      assertEquals(new CleanupCounts(3, 2, 1), actual.counts());
      assertEquals(CleanupReason.OK, actual.reason());
      fixture.assertClosed();
    }
  }

  @Test
  void okMayRetainProtectedRowsWhileBusyAndBackupGateReturnOnlyTrueZeroObservations() {
    for (String reason : List.of("OK", "LOCK_BUSY", "BACKUP_GATE")) {
      Fixture fixture = new Fixture(false);
      var input = literal();
      input.put(TEXT_REASON_CODE, reason);
      if (!reason.equals("OK"))
        for (String column : List.of(TEXT_TARGET_COUNT, TEXT_DELETED_COUNT, TEXT_SKIPPED_COUNT))
          input.put(column, 0L);
      fixture.results = List.of(input);
      var actual = (CleanupChunk) fixture.call();
      assertEquals(reason, actual.reason().name());
      assertEquals(reason.equals("OK") ? 3 : 0, actual.counts().target());
      fixture.assertClosed();
    }
  }

  @Test
  void progressKeepsActualThreeCountsAndBothCompleteValuesWithTheOriginalRun() {
    for (boolean complete : List.of(false, true)) {
      Fixture fixture = new Fixture(true);
      fixture.results = List.of(changed(TEXT_COMPLETE, complete));
      var actual = (LogCleanupProgress) fixture.call();
      assertSame(RUN, actual.run());
      assertEquals(new CleanupCounts(3, 2, 1), actual.counts());
      assertEquals(complete, actual.complete());
      assertEquals(PROGRESS_SQL, fixture.sql);
      assertEquals(Map.of(1, new UUID(0, 1), 2, CUTOFF.atOffset(ZoneOffset.UTC)), fixture.bindings);
      fixture.assertClosed();
    }
  }

  @Test
  void eachRequiredColumnInvalidCountAndUnknownOrContradictoryReasonIsRejectedIndependently() {
    for (boolean progress : List.of(false, true)) {
      for (String column : List.of(TEXT_TARGET_COUNT, TEXT_DELETED_COUNT, TEXT_SKIPPED_COUNT)) {
        reject(progress, changed(column, null));
        reject(progress, changed(column, -1L));
      }
      reject(progress, changed(TEXT_DELETED_COUNT, 4L));
      reject(progress, changed(TEXT_SKIPPED_COUNT, 0L));
      reject(progress, changed(progress ? TEXT_COMPLETE : TEXT_REASON_CODE, null));
    }
    reject(false, changed(TEXT_REASON_CODE, "UNKNOWN"));
    reject(false, changed(TEXT_REASON_CODE, "LOCK_BUSY"));
    reject(false, changed(TEXT_REASON_CODE, "BACKUP_GATE"));
  }

  @Test
  void eachKindLimitOneAndMaximumAreAcceptedButZeroAndMaximumPlusOneAcquireNothing() {
    for (CleanupKind kind : SUFFIXES.keySet()) {
      int maximum = kind == CleanupKind.LOGS ? 10000 : 1000;
      for (int boundary : new int[] {1, maximum}) {
        Fixture fixture = new Fixture(false);
        fixture.kind = kind;
        fixture.limit = boundary;
        var input = literal();
        input.put(TEXT_TARGET_COUNT, (long) boundary);
        input.put(TEXT_DELETED_COUNT, (long) boundary);
        input.put(TEXT_SKIPPED_COUNT, 0L);
        fixture.results = List.of(input);
        assertEquals(boundary, ((CleanupChunk) fixture.call()).counts().target());
        fixture.assertClosed();
      }
      for (int invalid : new int[] {Integer.MIN_VALUE, 0, maximum + 1, Integer.MAX_VALUE}) {
        Fixture fixture = new Fixture(false);
        fixture.kind = kind;
        fixture.limit = invalid;
        assertThrows(IllegalArgumentException.class, fixture::call);
        assertTrue(fixture.visited.isEmpty());
      }
    }
    Fixture exceeded = new Fixture(false);
    exceeded.limit = 2;
    catalog(exceeded::call);
    exceeded.assertClosed();
  }

  @Test
  void publicNullsMissingDuplicateRowsAndIllegalNullJdbcResultsNeverBecomeNormalValues() {
    assertThrows(NullPointerException.class, () -> new CleanupRepository(null));
    Fixture fixture = new Fixture(false);
    var repository = new CleanupRepository(fixture.connection());
    assertThrows(
        NullPointerException.class, () -> repository.execute(null, CleanupKind.SESSIONS, 1));
    assertThrows(NullPointerException.class, () -> repository.execute(RUN, null, 1));
    assertThrows(NullPointerException.class, () -> repository.readLogProgress(null));
    assertTrue(fixture.visited.isEmpty());
    for (boolean progress : List.of(false, true)) {
      for (int count : new int[] {0, 2}) {
        Fixture missing = new Fixture(progress);
        missing.results = count == 0 ? List.of() : List.of(literal(), literal());
        catalog(missing::call);
        missing.assertClosed();
      }
      for (String missing : List.of("statement", "row")) {
        Fixture invalid = new Fixture(progress);
        invalid.missing = missing;
        assertThrows(NullPointerException.class, invalid::call);
        invalid.assertClosed();
      }
      Fixture auto = new Fixture(progress);
      auto.autoCommit = true;
      catalog(auto::call);
      assertEquals(List.of("auto"), auto.visited);
      auto.assertClosed();
    }
  }

  @Test
  void bothEntryProviderFaultMatricesVerifyActualPointReachAndOriginalUnknownIdentity() {
    for (boolean progress : List.of(false, true)) {
      var points =
          new ArrayList<>(
              List.of(
                  "auto",
                  "prepare",
                  "bind1",
                  "bind2",
                  "query",
                  "next1",
                  "next2",
                  TEXT_TARGET_COUNT,
                  TEXT_DELETED_COUNT,
                  TEXT_SKIPPED_COUNT,
                  progress ? TEXT_COMPLETE : TEXT_REASON_CODE,
                  "rowClose",
                  TEXT_STATEMENTCLOSE));
      if (!progress) points.add("bind3");
      for (String point : points)
        for (int type = 0; type < 3; type++) {
          Fixture fixture = new Fixture(progress);
          Throwable failure = failure(type);
          fixture.faults.put(point, failure);
          if (failure instanceof SQLException) catalog(fixture::call);
          else assertSame(failure, assertThrows(failure.getClass(), fixture::call, point));
          assertTrue(fixture.visited.contains(point), "planned fault point reached");
          fixture.assertClosed();
        }
    }
  }

  @Test
  void nestedSqlNextErrorPreservesIdentityAtBothResourceBoundaries() {
    for (boolean progress : List.of(false, true)) {
      var beforeAcquisition = new Fixture(progress);
      var afterAcquisition = new Fixture(progress);
      var before = new LinkageError("public acquisition fixture");
      var after = new LinkageError("public row fixture");
      beforeAcquisition.faults.put("prepare", withNextError(before));
      afterAcquisition.faults.put(TEXT_TARGET_COUNT, withNextError(after));

      assertSame(before, assertThrows(LinkageError.class, beforeAcquisition::call));
      assertEquals(0, before.getSuppressed().length);
      assertEquals(List.of("auto", "prepare"), beforeAcquisition.visited);
      assertEquals(0, beforeAcquisition.openedStatements);
      assertEquals(0, beforeAcquisition.openedRows);
      beforeAcquisition.assertClosed();

      assertSame(after, assertThrows(LinkageError.class, afterAcquisition::call));
      assertEquals(0, after.getSuppressed().length);
      assertEquals(
          List.of(TEXT_TARGET_COUNT, "rowClose", TEXT_STATEMENTCLOSE),
          afterAcquisition.visited.subList(
              afterAcquisition.visited.size() - 3, afterAcquisition.visited.size()));
      assertEquals(1, afterAcquisition.openedStatements);
      assertEquals(1, afterAcquisition.openedRows);
      afterAcquisition.assertClosed();
    }
  }

  private static SQLException withNextError(LinkageError fatal) {
    var sql = new SQLException("public JDBC failure fixture");
    sql.setNextException(new SQLException("public next fixture", fatal));
    return sql;
  }

  @Test
  void independentPrimaryClosePrecedenceAndExactSafeSuppressedCountsHoldForBothEntries() {
    for (boolean progress : List.of(false, true))
      for (boolean rowClosing : List.of(false, true))
        for (int bodyType = 0; bodyType < 3; bodyType++)
          for (int closeType = 0; closeType < 3; closeType++) {
            Fixture fixture = new Fixture(progress);
            Throwable body = failure(bodyType);
            Throwable closing = failure(closeType);
            fixture.faults.put(progress ? TEXT_COMPLETE : TEXT_REASON_CODE, body);
            fixture.faults.put(rowClosing ? "rowClose" : TEXT_STATEMENTCLOSE, closing);
            if (rowClosing)
              fixture.faults.put(TEXT_STATEMENTCLOSE, new SQLException("private final close"));
            Throwable expected = bodyType == 0 ? closing : body;
            if (expected instanceof SQLException) catalog(fixture::call);
            else {
              var actual = assertThrows(expected.getClass(), fixture::call);
              assertSame(expected, actual);
              int expectedSecondary =
                  rowClosing ? (bodyType == 0 ? 1 : 2) : (bodyType == 0 ? 0 : 1);
              assertEquals(expectedSecondary, actual.getSuppressed().length);
              for (Throwable secondary : actual.getSuppressed()) {
                assertEquals(BatchRepositoryException.class, secondary.getClass());
                assertEquals(FIXED, secondary.getMessage());
              }
            }
            fixture.assertClosed();
          }
  }

  @Test
  void zeroCountsAndMaximumLongCountsRemainDataAndCallerTransactionIsNeverCommitted() {
    for (boolean progress : List.of(false, true)) {
      Fixture zero = new Fixture(progress);
      var empty = literal();
      for (String column : List.of(TEXT_TARGET_COUNT, TEXT_DELETED_COUNT, TEXT_SKIPPED_COUNT))
        empty.put(column, 0L);
      zero.results = List.of(empty);
      Object observed = zero.call();
      CleanupCounts counts =
          progress ? ((LogCleanupProgress) observed).counts() : ((CleanupChunk) observed).counts();
      assertEquals(new CleanupCounts(0, 0, 0), counts);
      zero.assertClosed();
    }
    Fixture large = new Fixture(true);
    var input = literal();
    input.put(TEXT_TARGET_COUNT, Long.MAX_VALUE);
    input.put(TEXT_DELETED_COUNT, Long.MAX_VALUE - 1);
    input.put(TEXT_SKIPPED_COUNT, 1L);
    large.results = List.of(input);
    assertEquals(
        new CleanupCounts(Long.MAX_VALUE, Long.MAX_VALUE - 1, 1),
        ((LogCleanupProgress) large.call()).counts());
    large.assertClosed();
  }

  private static Map<String, Object> literal() {
    var row = new HashMap<String, Object>();
    row.put(TEXT_TARGET_COUNT, 3L);
    row.put(TEXT_DELETED_COUNT, 2L);
    row.put(TEXT_SKIPPED_COUNT, 1L);
    row.put(TEXT_REASON_CODE, "OK");
    row.put(TEXT_COMPLETE, false);
    return row;
  }

  private static Map<String, Object> changed(String column, Object value) {
    var row = literal();
    row.put(column, value);
    return row;
  }

  private static void reject(boolean progress, Map<String, Object> input) {
    Fixture fixture = new Fixture(progress);
    fixture.results = List.of(input);
    catalog(fixture::call);
    fixture.assertClosed();
  }

  private static Throwable failure(int kind) {
    return switch (kind) {
      case 0 -> new SQLException("private JDBC");
      case 1 -> new IllegalStateException("private provider");
      case 2 -> new AssertionError("private fatal");
      default -> throw new AssertionError("unknown fixture kind");
    };
  }

  private static void catalog(Executable action) {
    var failure = assertThrows(BatchRepositoryException.class, action);
    assertEquals(FIXED, failure.getMessage());
    assertEquals(null, failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
  }

  private static final class Fixture {
    private final boolean progress;
    private CleanupKind kind = CleanupKind.SESSIONS;
    private int limit = 1000;
    private List<Map<String, Object>> results = List.of(literal());
    private final Map<String, Throwable> faults = new HashMap<>();
    private final List<String> visited = new ArrayList<>();
    private final Map<Integer, Object> bindings = new HashMap<>();
    private String sql;
    private String missing = "";
    private boolean autoCommit;
    private int openedStatements;
    private int closedStatements;
    private int openedRows;
    private int closedRows;

    private Fixture(boolean progress) {
      this.progress = progress;
    }

    private Object call() {
      var repository = new CleanupRepository(connection());
      return progress ? repository.readLogProgress(RUN) : repository.execute(RUN, kind, limit);
    }

    private Connection connection() {
      return (Connection)
          Proxy.newProxyInstance(
              Fixture.class.getClassLoader(),
              new Class<?>[] {Connection.class},
              (proxy, method, args) -> {
                if (method.getName().equals("getAutoCommit")) {
                  hit("auto");
                  return autoCommit;
                }
                if (method.getName().equals("prepareStatement")) {
                  sql = (String) args[0];
                  hit("prepare");
                  if (missing.equals("statement")) return null;
                  return statement();
                }
                throw new AssertionError(
                    "borrowed connection operation forbidden: " + method.getName());
              });
    }

    private PreparedStatement statement() {
      openedStatements++;
      return (PreparedStatement)
          Proxy.newProxyInstance(
              Fixture.class.getClassLoader(),
              new Class<?>[] {PreparedStatement.class},
              (proxy, method, args) -> {
                String name = method.getName();
                if (name.equals("setObject") || name.equals("setInt")) {
                  int position = (Integer) args[0];
                  hit("bind" + position);
                  assertEquals(position == 3 ? "setInt" : "setObject", name);
                  bindings.put(position, args[1]);
                  return null;
                }
                if (name.equals("executeQuery")) {
                  hit("query");
                  if (missing.equals("row")) return null;
                  return resultSet();
                }
                if (name.equals("close")) {
                  closedStatements++;
                  hit(TEXT_STATEMENTCLOSE);
                  return null;
                }
                throw new AssertionError("unexpected statement operation: " + name);
              });
    }

    private ResultSet resultSet() {
      openedRows++;
      int[] index = {-1};
      return (ResultSet)
          Proxy.newProxyInstance(
              Fixture.class.getClassLoader(),
              new Class<?>[] {ResultSet.class},
              (proxy, method, args) -> {
                String name = method.getName();
                if (name.equals("next")) {
                  index[0]++;
                  hit("next" + (index[0] + 1));
                  return index[0] < results.size();
                }
                if (name.equals("getObject") || name.equals("getString")) {
                  String column = (String) args[0];
                  hit(column);
                  assertTrue(results.get(index[0]).containsKey(column));
                  return results.get(index[0]).get(column);
                }
                if (name.equals("close")) {
                  closedRows++;
                  hit("rowClose");
                  return null;
                }
                throw new AssertionError("unexpected row operation: " + name);
              });
    }

    private void hit(String point) throws Throwable {
      visited.add(point);
      Throwable failure = faults.get(point);
      if (failure != null) throw failure;
    }

    private void assertClosed() {
      assertEquals(openedStatements, closedStatements, "all owned statements closed exactly once");
      assertEquals(openedRows, closedRows, "all owned rows closed exactly once");
    }
  }
}
