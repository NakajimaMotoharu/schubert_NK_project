package dev.codex.schubert.nk.batch.repository;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
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
import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.function.Executable;

/** INSPPORT001..008: inspection data only, never actual child/owner/OS/DB verification. */
final class InspectionSummaryPortTest {
  private static final String TEXT_AUTO = "auto";
  private static final String TEXT_COMPLETE = "complete";
  private static final String TEXT_DELETED_COUNT = "deleted_count";
  private static final String TEXT_INSPECTED_COUNT = "inspected_count";
  private static final String TEXT_ISOLATION = "isolation";
  private static final String TEXT_PROTECTED_COUNT = "protected_count";
  private static final String TEXT_READONLY = "readonly";
  private static final String TEXT_ROWCLOSE = "rowClose";
  private static final String TEXT_STATEMENTCLOSE = "statementClose";
  private static final String SQL =
      "select inspected_count,deleted_count,protected_count,complete"
          + " from schubert.maintenance_read_inbox_summary(?,?)";
  private static final BatchRun RUN =
      new BatchRun(new UUID(0, 1), Instant.parse("2026-11-05T00:00:00.123456Z"));
  private static final String FIXED = "batch repository operation failed";

  @Test
  void literalSqlTimeoutAndUuidUtcBindingsReturnAllFourColumnsWithoutOwnershipMutation() {
    Fixture fixture = new Fixture();
    var actual = fixture.read().orElseThrow();
    assertSame(RUN, actual.run());
    assertEquals(new CleanupCounts(3, 2, 1), actual.counts());
    assertFalse(actual.complete());
    assertEquals(SQL, fixture.sql);
    assertEquals(5, fixture.timeout);
    assertEquals(
        Map.of(
            1,
            new UUID(0, 1),
            2,
            Instant.parse("2026-11-05T00:00:00.123456Z").atOffset(ZoneOffset.UTC)),
        fixture.bindings);
    assertEquals(
        List.of(
            TEXT_AUTO,
            TEXT_READONLY,
            TEXT_ISOLATION,
            "prepare",
            "timeout",
            "bind1",
            "bind2",
            "query",
            "next1",
            TEXT_INSPECTED_COUNT,
            TEXT_DELETED_COUNT,
            TEXT_PROTECTED_COUNT,
            TEXT_COMPLETE,
            "next2",
            TEXT_ROWCLOSE,
            TEXT_STATEMENTCLOSE),
        fixture.visited);
    fixture.assertClosed();
  }

  @Test
  void trueAbsenceIsDifferentFromZeroKnownCountsAndBothCompleteValuesArePreserved() {
    Fixture absent = new Fixture();
    absent.results = List.of();
    assertEquals(Optional.empty(), absent.read());
    absent.assertClosed();
    for (boolean complete : List.of(false, true)) {
      Fixture fixture = new Fixture();
      var row = literal();
      row.put(TEXT_INSPECTED_COUNT, 0L);
      row.put(TEXT_DELETED_COUNT, 0L);
      row.put(TEXT_PROTECTED_COUNT, 0L);
      row.put(TEXT_COMPLETE, complete);
      fixture.results = List.of(row);
      var actual = fixture.read().orElseThrow();
      assertEquals(new CleanupCounts(0, 0, 0), actual.counts());
      assertEquals(complete, actual.complete());
      fixture.assertClosed();
    }
    Fixture max = new Fixture();
    var row = literal();
    row.put(TEXT_INSPECTED_COUNT, Long.MAX_VALUE);
    row.put(TEXT_DELETED_COUNT, Long.MAX_VALUE - 1);
    row.put(TEXT_PROTECTED_COUNT, 1L);
    max.results = List.of(row);
    assertEquals(
        new CleanupCounts(Long.MAX_VALUE, Long.MAX_VALUE - 1, 1),
        max.read().orElseThrow().counts());
    max.assertClosed();
  }

  @Test
  void requiredNullCountBalanceAndDuplicateRowsCannotFabricateAValidSummary() {
    for (String column :
        List.of(TEXT_INSPECTED_COUNT, TEXT_DELETED_COUNT, TEXT_PROTECTED_COUNT, TEXT_COMPLETE))
      reject(changed(column, null));
    for (String column : List.of(TEXT_INSPECTED_COUNT, TEXT_DELETED_COUNT, TEXT_PROTECTED_COUNT))
      reject(changed(column, -1L));
    reject(changed(TEXT_DELETED_COUNT, 4L));
    reject(changed(TEXT_PROTECTED_COUNT, 0L));
    Fixture duplicate = new Fixture();
    duplicate.results = List.of(literal(), literal());
    catalog(duplicate::read);
    duplicate.assertClosed();
  }

  @Test
  void nullAndExplicitAutocommitWritableReadCommittedPrerequisitesRejectBeforeOwnedSql() {
    assertThrows(NullPointerException.class, () -> new InspectionSummaryRepository(null));
    Fixture fixture = new Fixture();
    assertThrows(
        NullPointerException.class,
        () -> new InspectionSummaryRepository(fixture.connection()).read(null));
    assertTrue(fixture.visited.isEmpty());
    for (String bad : List.of(TEXT_AUTO, TEXT_READONLY, TEXT_ISOLATION)) {
      Fixture invalid = new Fixture();
      invalid.badTransaction = bad;
      catalog(invalid::read);
      assertEquals(null, invalid.sql);
      invalid.assertClosed();
    }
  }

  @Test
  void nullStatementOrResultSetIsCataloguedAndEveryAcquiredResourceStillCloses() {
    for (String missing : List.of("statement", "row")) {
      Fixture fixture = new Fixture();
      fixture.missing = missing;
      catalog(fixture::read);
      fixture.assertClosed();
      assertEquals(missing.equals("statement") ? 0 : 1, fixture.closedStatements);
      assertEquals(0, fixture.closedRows);
    }
  }

  @Test
  void everyProviderFaultPointIsReachedAndOnlySqlLosesPrivateDiagnostics() {
    for (String point :
        List.of(
            TEXT_AUTO,
            TEXT_READONLY,
            TEXT_ISOLATION,
            "prepare",
            "timeout",
            "bind1",
            "bind2",
            "query",
            "next1",
            TEXT_INSPECTED_COUNT,
            TEXT_DELETED_COUNT,
            TEXT_PROTECTED_COUNT,
            TEXT_COMPLETE,
            "next2",
            TEXT_ROWCLOSE,
            TEXT_STATEMENTCLOSE))
      for (int type = 0; type < 3; type++) {
        Fixture fixture = new Fixture();
        Throwable failure = failure(type);
        fixture.faults.put(point, failure);
        if (failure instanceof SQLException) catalog(fixture::read);
        else assertSame(failure, assertThrows(failure.getClass(), fixture::read, point));
        assertTrue(fixture.visited.contains(point), "planned provider fault point reached");
        fixture.assertClosed();
      }
  }

  @Test
  void primaryAndBothCloseScopesHaveIndependentPriorityAndExactSafeSecondaryCounts() {
    for (boolean rowClosing : List.of(false, true))
      for (int bodyType = 0; bodyType < 3; bodyType++)
        for (int closeType = 0; closeType < 3; closeType++) {
          Fixture fixture = new Fixture();
          Throwable body = failure(bodyType);
          Throwable closing = failure(closeType);
          fixture.faults.put(TEXT_COMPLETE, body);
          fixture.faults.put(rowClosing ? TEXT_ROWCLOSE : TEXT_STATEMENTCLOSE, closing);
          if (rowClosing)
            fixture.faults.put(TEXT_STATEMENTCLOSE, new SQLException("private final close"));
          Throwable expected = bodyType == 0 ? closing : body;
          if (expected instanceof SQLException) catalog(fixture::read);
          else {
            var actual = assertThrows(expected.getClass(), fixture::read);
            assertSame(expected, actual);
            assertEquals(
                rowClosing ? (bodyType == 0 ? 1 : 2) : (bodyType == 0 ? 0 : 1),
                actual.getSuppressed().length);
            for (Throwable secondary : actual.getSuppressed()) {
              assertEquals(BatchRepositoryException.class, secondary.getClass());
              assertEquals(FIXED, secondary.getMessage());
            }
          }
          fixture.assertClosed();
        }
  }

  @Test
  void beforeAndAfterInterruptRejectOnAnOwnedWorkerAndNeverChangeTheParentFlag() throws Exception {
    boolean parentFlag = Thread.currentThread().isInterrupted();
    try (var worker = Executors.newSingleThreadExecutor()) {
      for (boolean before : List.of(false, true)) {
        worker
            .submit(
                () -> {
                  Fixture fixture = new Fixture();
                  fixture.interruptOnRowClose = !before;
                  try {
                    if (before) Thread.currentThread().interrupt();
                    catalog(fixture::read);
                    assertTrue(Thread.currentThread().isInterrupted());
                    if (before) assertTrue(fixture.visited.isEmpty());
                    else assertTrue(fixture.visited.contains(TEXT_STATEMENTCLOSE));
                    fixture.assertClosed();
                  } finally {
                    Thread.interrupted();
                  }
                  assertFalse(Thread.currentThread().isInterrupted());
                })
            .get(5, TimeUnit.SECONDS);
      }
    }
    assertEquals(parentFlag, Thread.currentThread().isInterrupted());
  }

  private static Map<String, Object> literal() {
    var row = new HashMap<String, Object>();
    row.put(TEXT_INSPECTED_COUNT, 3L);
    row.put(TEXT_DELETED_COUNT, 2L);
    row.put(TEXT_PROTECTED_COUNT, 1L);
    row.put(TEXT_COMPLETE, false);
    return row;
  }

  private static Map<String, Object> changed(String column, Object value) {
    var row = literal();
    row.put(column, value);
    return row;
  }

  private static void reject(Map<String, Object> row) {
    Fixture fixture = new Fixture();
    fixture.results = List.of(row);
    catalog(fixture::read);
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
    private List<Map<String, Object>> results = List.of(literal());
    private final Map<String, Throwable> faults = new HashMap<>();
    private final List<String> visited = new ArrayList<>();
    private final Map<Integer, Object> bindings = new HashMap<>();
    private String sql;
    private int timeout;
    private String missing = "";
    private String badTransaction = "";
    private boolean interruptOnRowClose;
    private int openedStatements;
    private int closedStatements;
    private int openedRows;
    private int closedRows;

    private Optional<InspectionSummary> read() {
      return new InspectionSummaryRepository(connection()).read(RUN);
    }

    private Connection connection() {
      return (Connection)
          Proxy.newProxyInstance(
              Fixture.class.getClassLoader(),
              new Class<?>[] {Connection.class},
              (proxy, method, args) ->
                  switch (method.getName()) {
                    case "getAutoCommit" -> {
                      hit(TEXT_AUTO);
                      yield !badTransaction.equals(TEXT_AUTO);
                    }
                    case "isReadOnly" -> {
                      hit(TEXT_READONLY);
                      yield badTransaction.equals(TEXT_READONLY);
                    }
                    case "getTransactionIsolation" -> {
                      hit(TEXT_ISOLATION);
                      yield badTransaction.equals(TEXT_ISOLATION)
                          ? Connection.TRANSACTION_SERIALIZABLE
                          : Connection.TRANSACTION_READ_COMMITTED;
                    }
                    case "prepareStatement" -> {
                      sql = (String) args[0];
                      hit("prepare");
                      yield missing.equals("statement") ? null : statement();
                    }
                    default ->
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
                if (name.equals("setQueryTimeout")) {
                  hit("timeout");
                  timeout = (Integer) args[0];
                  return null;
                }
                if (name.equals("setObject")) {
                  hit("bind" + args[0]);
                  bindings.put((Integer) args[0], args[1]);
                  return null;
                }
                if (name.equals("executeQuery")) {
                  hit("query");
                  return missing.equals("row") ? null : resultSet();
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
                if (name.equals("getObject")) {
                  String column = (String) args[0];
                  hit(column);
                  assertTrue(results.get(index[0]).containsKey(column));
                  return results.get(index[0]).get(column);
                }
                if (name.equals("close")) {
                  closedRows++;
                  hit(TEXT_ROWCLOSE);
                  if (interruptOnRowClose) Thread.currentThread().interrupt();
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
