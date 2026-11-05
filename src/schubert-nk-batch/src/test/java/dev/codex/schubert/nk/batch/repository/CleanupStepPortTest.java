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
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.function.Executable;

/** CLNPORT001..009: V020 projection and borrowed JDBC, never an actual DELETE or owner. */
final class CleanupStepPortTest {
  private static final String TEXT_FOREIGN_KEY_CONFLICT = "FOREIGN_KEY_CONFLICT";
  private static final String TEXT_COMPLETE = "complete";
  private static final String TEXT_DELETED_COUNT = "deleted_count";
  private static final String TEXT_REASON_CODE = "reason_code";
  private static final String TEXT_SKIPPED_COUNT = "skipped_count";
  private static final String TEXT_STATEMENTCLOSE = "statementClose";
  private static final String TEXT_STEP_SUCCESS_COUNT = "step_success_count";
  private static final String TEXT_STEP_TARGET_COUNT = "step_target_count";
  private static final String TEXT_TARGET_COUNT = "target_count";
  private static final String CLEANUP_SQL =
      "select"
          + " target_count,deleted_count,skipped_count,step_target_count,step_success_count,complete,reason_code"
          + " from schubert.maintenance_execute_cleanup_step(?,?,?,?,?,?,?)";
  private static final String REFERENCES_SQL =
      "select has_batch_history,has_inbox_progress,has_log_progress,identity_consistent"
          + " from schubert.maintenance_read_run_references(?,?)";
  private static final Instant BASE = Instant.parse("2026-11-05T00:00:00Z");
  private static final BatchRun RUN = new BatchRun(new UUID(0, 1), BASE);
  private static final String FIXED = "batch repository operation failed";
  private static final Map<CleanupKind, BatchStep> MAPPINGS =
      Map.of(
          CleanupKind.NOTIFICATIONS, BatchStep.CLEAN_NOTIFICATION,
          CleanupKind.QUESTIONS, BatchStep.CLEAN_QUESTION,
          CleanupKind.SESSIONS, BatchStep.CLEAN_SESSION,
          CleanupKind.OUTBOX, BatchStep.CLEAN_INBOX_OUTBOX,
          CleanupKind.WEB_RECEIPTS, BatchStep.CLEAN_BATCH_RUN,
          CleanupKind.BATCH_RUNS, BatchStep.CLEAN_BATCH_RUN,
          CleanupKind.INBOX_PROGRESS, BatchStep.CLEAN_BATCH_RUN,
          CleanupKind.LOG_PROGRESS, BatchStep.CLEAN_BATCH_RUN);

  @Test
  void literalSevenColumnSqlAndTypedBindingsKeepAllEightApprovedMappingsBorrowed() {
    for (var entry : MAPPINGS.entrySet()) {
      Fixture fixture = new Fixture();
      var handle = handle(entry.getValue(), false);
      var actual = fixture.repository().execute(handle, entry.getKey(), 1000);
      assertSame(handle, actual.attempt());
      assertSame(entry.getKey(), actual.kind());
      assertEquals(new CleanupCounts(1, 1, 0), actual.counts());
      assertEquals(Optional.of(new CleanupCounts(3, 3, 0)), actual.stepCounts());
      assertFalse(actual.complete());
      assertEquals(CleanupStepChunk.Reason.OK, actual.reason());
      assertEquals(List.of(REFERENCES_SQL, CLEANUP_SQL, REFERENCES_SQL), fixture.sql);
      assertEquals(
          Map.of(
              1,
              new UUID(0, 1),
              2,
              BASE.atOffset(ZoneOffset.UTC),
              3,
              7L,
              4,
              1,
              5,
              BASE.plusSeconds(1).atOffset(ZoneOffset.UTC),
              6,
              entry.getKey().name(),
              7,
              1000),
          fixture.cleanupBindings);
      fixture.assertClosed();
    }
  }

  @Test
  void literalOkEmptyBusyBackupGateAndQuestionConflictKeepKnownTotalsDistinctFromUnknown() {
    for (String reason : List.of("OK", "LOCK_BUSY", "BACKUP_GATE", TEXT_FOREIGN_KEY_CONFLICT)) {
      Fixture fixture = new Fixture();
      var row = literal();
      row.put(TEXT_TARGET_COUNT, 0L);
      row.put(TEXT_DELETED_COUNT, 0L);
      row.put(TEXT_REASON_CODE, reason);
      row.put(TEXT_COMPLETE, reason.equals("OK"));
      boolean known = reason.equals("OK") || reason.equals(TEXT_FOREIGN_KEY_CONFLICT);
      row.put(TEXT_STEP_TARGET_COUNT, known ? 3L : null);
      row.put(TEXT_STEP_SUCCESS_COUNT, known ? 3L : null);
      fixture.results = List.of(row);
      var actual =
          fixture
              .repository()
              .execute(handle(BatchStep.CLEAN_QUESTION, false), CleanupKind.QUESTIONS, 1);
      assertEquals(0, actual.counts().target());
      assertEquals(reason.equals("OK"), actual.complete());
      assertEquals(
          known ? Optional.of(new CleanupCounts(3, 3, 0)) : Optional.empty(), actual.stepCounts());
      assertEquals(reason, actual.reason().name());
      fixture.assertClosed();
    }
  }

  @Test
  void eachRequiredNullAndCounterOrPairedTotalViolationRejectsTheProjection() {
    for (String column :
        List.of(
            TEXT_TARGET_COUNT,
            TEXT_DELETED_COUNT,
            TEXT_SKIPPED_COUNT,
            TEXT_COMPLETE,
            TEXT_REASON_CODE)) reject(changed(column, null));
    for (String column :
        List.of(
            TEXT_TARGET_COUNT,
            TEXT_DELETED_COUNT,
            TEXT_SKIPPED_COUNT,
            TEXT_STEP_TARGET_COUNT,
            TEXT_STEP_SUCCESS_COUNT)) reject(changed(column, -1L));
    reject(changed(TEXT_DELETED_COUNT, 2L));
    reject(changed(TEXT_DELETED_COUNT, 0L));
    reject(changed(TEXT_SKIPPED_COUNT, 1L));
    reject(changed(TEXT_STEP_SUCCESS_COUNT, 2L));
    reject(changed(TEXT_STEP_TARGET_COUNT, null));
    reject(changed(TEXT_STEP_SUCCESS_COUNT, null));
    var bothMissing = changed(TEXT_STEP_TARGET_COUNT, null);
    bothMissing.put(TEXT_STEP_SUCCESS_COUNT, null);
    reject(bothMissing);
  }

  @Test
  void unknownReasonsWrongCompletionAndIncompatibleKindCannotBecomeSuccessfulCounts() {
    reject(changed(TEXT_REASON_CODE, "UNKNOWN"));
    reject(changed(TEXT_COMPLETE, true));
    var emptyNotComplete = changed(TEXT_TARGET_COUNT, 0L);
    emptyNotComplete.put(TEXT_DELETED_COUNT, 0L);
    reject(emptyNotComplete);
    var retained = changed(TEXT_DELETED_COUNT, 0L);
    retained.put(TEXT_SKIPPED_COUNT, 1L);
    reject(retained);
    var totalsTooSmall = changed(TEXT_STEP_TARGET_COUNT, 0L);
    totalsTooSmall.put(TEXT_STEP_SUCCESS_COUNT, 0L);
    reject(totalsTooSmall);
    for (String reason : List.of("LOCK_BUSY", "BACKUP_GATE", TEXT_FOREIGN_KEY_CONFLICT)) {
      reject(changed(TEXT_REASON_CODE, reason));
      var known = changed(TEXT_TARGET_COUNT, 0L);
      known.put(TEXT_DELETED_COUNT, 0L);
      known.put(TEXT_REASON_CODE, reason);
      if (reason.equals(TEXT_FOREIGN_KEY_CONFLICT)) {
        Fixture fixture = new Fixture();
        fixture.results = List.of(known);
        catalog(
            () ->
                fixture
                    .repository()
                    .execute(handle(BatchStep.CLEAN_SESSION, false), CleanupKind.SESSIONS, 10));
        fixture.assertClosed();
        known.put(TEXT_STEP_TARGET_COUNT, null);
        known.put(TEXT_STEP_SUCCESS_COUNT, null);
      }
      reject(known);
    }
  }

  @Test
  void
      everyNullMappingAndLimitViolationRejectsBeforeAcquisitionAndRowsCannotBeMissingOrDuplicate() {
    assertThrows(NullPointerException.class, () -> new CleanupStepRepository(null));
    Fixture fixture = new Fixture();
    var repository = fixture.repository();
    assertThrows(
        NullPointerException.class, () -> repository.execute(null, CleanupKind.SESSIONS, 1));
    assertThrows(
        NullPointerException.class,
        () -> repository.execute(handle(BatchStep.CLEAN_SESSION, false), null, 1));
    for (int invalid : new int[] {Integer.MIN_VALUE, 0, 1001, Integer.MAX_VALUE})
      assertThrows(
          IllegalArgumentException.class,
          () ->
              repository.execute(
                  handle(BatchStep.CLEAN_SESSION, false), CleanupKind.SESSIONS, invalid));
    for (BatchStepAttempt wrong :
        List.of(handle(BatchStep.CLEAN_SESSION, true), handle(BatchStep.CLEAN_QUESTION, false)))
      assertThrows(
          IllegalArgumentException.class, () -> repository.execute(wrong, CleanupKind.SESSIONS, 1));
    assertThrows(
        IllegalArgumentException.class,
        () -> repository.execute(handle(BatchStep.CLEAN_LOG, false), CleanupKind.LOGS, 1));
    assertTrue(fixture.sql.isEmpty());
    for (int count : new int[] {0, 2}) {
      Fixture rows = new Fixture();
      rows.results = count == 0 ? List.of() : List.of(literal(), literal());
      catalog(() -> rows.execute());
      rows.assertClosed();
    }
    for (String missing : List.of("statement", "row")) {
      Fixture rows = new Fixture();
      rows.missing = missing;
      catalog(() -> rows.execute());
      rows.assertClosed();
    }
  }

  @Test
  void allProviderPointsReallyReachedKeepUnknownIdentityAndCatalogOnlySql() {
    var points =
        new ArrayList<>(
            List.of(
                "prepare",
                "timeout",
                "query",
                "next1",
                "next2",
                "rowClose",
                TEXT_STATEMENTCLOSE,
                TEXT_TARGET_COUNT,
                TEXT_DELETED_COUNT,
                TEXT_SKIPPED_COUNT,
                TEXT_STEP_TARGET_COUNT,
                TEXT_STEP_SUCCESS_COUNT,
                TEXT_COMPLETE,
                TEXT_REASON_CODE));
    for (int index = 1; index <= 7; index++) points.add("bind" + index);
    for (String point : points)
      for (Throwable failure : failures()) {
        Fixture fixture = new Fixture();
        fixture.faults.put(point, failure);
        if (failure instanceof SQLException) catalog(fixture::execute);
        else assertSame(failure, assertThrows(failure.getClass(), fixture::execute, point));
        assertTrue(fixture.visited.contains(point), "planned fault point reached");
        fixture.assertClosed();
      }
  }

  @Test
  void bodyAndEachClosingFailureUseIndependentPriorityAndSafeSecondaryWithoutSkippingClose() {
    for (boolean rowClosing : List.of(false, true))
      for (Throwable body : failures())
        for (Throwable closing : failures()) {
          Fixture fixture = new Fixture();
          fixture.faults.put(TEXT_REASON_CODE, body);
          fixture.faults.put(rowClosing ? "rowClose" : TEXT_STATEMENTCLOSE, closing);
          if (rowClosing)
            fixture.faults.put(TEXT_STATEMENTCLOSE, new SQLException("private remaining close"));
          Throwable expected = body instanceof SQLException ? closing : body;
          if (expected instanceof SQLException) catalog(fixture::execute);
          else {
            var actual = assertThrows(expected.getClass(), fixture::execute);
            assertSame(expected, actual);
            for (Throwable secondary : actual.getSuppressed()) {
              assertEquals(BatchRepositoryException.class, secondary.getClass());
              assertEquals(FIXED, secondary.getMessage());
            }
          }
          fixture.assertClosed();
        }
  }

  @Test
  void parentIdentityBeforeAndAfterAndInvalidBorrowedTransactionNeverReturnAResult() {
    for (int bad : new int[] {1, 2}) {
      Fixture fixture = new Fixture();
      fixture.badReference = bad;
      catalog(fixture::execute);
      assertEquals(bad, fixture.referenceCalls);
      assertEquals(bad == 1 ? 0 : 7, fixture.cleanupBindings.size());
      fixture.assertClosed();
    }
    for (String bad : List.of("auto", "readonly", "isolation")) {
      Fixture fixture = new Fixture();
      fixture.badTransaction = bad;
      catalog(fixture::execute);
      assertTrue(fixture.sql.isEmpty());
      fixture.assertClosed();
    }
  }

  @Test
  void exactLimitsOneAndThousandAcceptOnlyTheirBoundedCountsAndNeverCommitTheBorrowedConnection() {
    for (int limit : new int[] {1, 1000}) {
      Fixture fixture = new Fixture();
      var input = literal();
      for (String column :
          List.of(
              TEXT_TARGET_COUNT,
              TEXT_DELETED_COUNT,
              TEXT_STEP_TARGET_COUNT,
              TEXT_STEP_SUCCESS_COUNT)) input.put(column, (long) limit);
      fixture.results = List.of(input);
      var actual =
          fixture
              .repository()
              .execute(handle(BatchStep.CLEAN_QUESTION, false), CleanupKind.QUESTIONS, limit);
      assertEquals(limit, actual.counts().target());
      assertEquals(limit, actual.counts().deleted());
      assertFalse(actual.complete());
      fixture.assertClosed();
      Fixture tooLarge = new Fixture();
      var overflow = literal();
      overflow.put(TEXT_TARGET_COUNT, limit + 1L);
      overflow.put(TEXT_DELETED_COUNT, limit + 1L);
      tooLarge.results = List.of(overflow);
      catalog(
          () ->
              tooLarge
                  .repository()
                  .execute(handle(BatchStep.CLEAN_QUESTION, false), CleanupKind.QUESTIONS, limit));
      tooLarge.assertClosed();
    }
  }

  private static BatchStepAttempt handle(BatchStep step, boolean skipped) {
    return new BatchStepAttempt(7, RUN, step, 1, BASE.plusSeconds(1), skipped);
  }

  private static Map<String, Object> literal() {
    var row = new HashMap<String, Object>();
    row.put(TEXT_TARGET_COUNT, 1L);
    row.put(TEXT_DELETED_COUNT, 1L);
    row.put(TEXT_SKIPPED_COUNT, 0L);
    row.put(TEXT_STEP_TARGET_COUNT, 3L);
    row.put(TEXT_STEP_SUCCESS_COUNT, 3L);
    row.put(TEXT_COMPLETE, false);
    row.put(TEXT_REASON_CODE, "OK");
    return row;
  }

  private static Map<String, Object> changed(String column, Object value) {
    var row = literal();
    row.put(column, value);
    return row;
  }

  private static void reject(Map<String, Object> input) {
    Fixture fixture = new Fixture();
    fixture.results = List.of(input);
    catalog(fixture::execute);
    fixture.assertClosed();
  }

  private static List<Throwable> failures() {
    return List.of(
        new SQLException("private JDBC"),
        new IllegalStateException("private provider"),
        new AssertionError("private fatal"));
  }

  private static void catalog(Executable action) {
    var failure = assertThrows(BatchRepositoryException.class, action);
    assertEquals(FIXED, failure.getMessage());
    assertEquals(null, failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
  }

  private static final class Fixture {
    private List<Map<String, Object>> results = List.of(literal());
    private final List<String> sql = new ArrayList<>();
    private final Map<Integer, Object> cleanupBindings = new HashMap<>();
    private final Map<String, Throwable> faults = new HashMap<>();
    private final List<String> visited = new ArrayList<>();
    private String missing = "";
    private String badTransaction = "";
    private int badReference;
    private int referenceCalls;
    private int openedStatements;
    private int closedStatements;
    private int openedRows;
    private int closedRows;

    private CleanupStepRepository repository() {
      return new CleanupStepRepository(connection());
    }

    private CleanupStepChunk execute() {
      return repository()
          .execute(handle(BatchStep.CLEAN_QUESTION, false), CleanupKind.QUESTIONS, 10);
    }

    private Connection connection() {
      return (Connection)
          Proxy.newProxyInstance(
              Fixture.class.getClassLoader(),
              new Class<?>[] {Connection.class},
              (proxy, method, args) ->
                  switch (method.getName()) {
                    case "getAutoCommit" -> badTransaction.equals("auto");
                    case "isReadOnly" -> badTransaction.equals("readonly");
                    case "getTransactionIsolation" ->
                        badTransaction.equals("isolation")
                            ? Connection.TRANSACTION_SERIALIZABLE
                            : Connection.TRANSACTION_READ_COMMITTED;
                    case "prepareStatement" -> statement((String) args[0]);
                    default ->
                        throw new AssertionError(
                            "borrowed connection operation forbidden: " + method.getName());
                  });
    }

    private PreparedStatement statement(String text) throws Throwable {
      assertTrue(List.of(REFERENCES_SQL, CLEANUP_SQL).contains(text), text);
      sql.add(text);
      boolean cleanup = text.equals(CLEANUP_SQL);
      if (cleanup) hit("prepare");
      if (cleanup && missing.equals("statement")) return null;
      openedStatements++;
      return (PreparedStatement)
          Proxy.newProxyInstance(
              Fixture.class.getClassLoader(),
              new Class<?>[] {PreparedStatement.class},
              (proxy, method, args) -> {
                String name = method.getName();
                if (name.equals("setQueryTimeout")) {
                  if (cleanup) hit("timeout");
                  assertEquals(5, args[0]);
                  return null;
                }
                if (List.of("setObject", "setLong", "setInt", "setString").contains(name)) {
                  int position = (Integer) args[0];
                  if (cleanup) {
                    hit("bind" + position);
                    assertEquals(
                        switch (position) {
                          case 1, 2, 5 -> "setObject";
                          case 3 -> "setLong";
                          case 4, 7 -> "setInt";
                          case 6 -> "setString";
                          default -> throw new AssertionError("unknown cleanup parameter");
                        },
                        name);
                    cleanupBindings.put(position, args[1]);
                  } else assertEquals("setObject", name);
                  return null;
                }
                if (name.equals("executeQuery")) {
                  if (cleanup) {
                    hit("query");
                    if (missing.equals("row")) return null;
                    return resultSet(results, true);
                  }
                  referenceCalls++;
                  return resultSet(
                      List.of(
                          Map.of(
                              "has_batch_history",
                              true,
                              "has_inbox_progress",
                              false,
                              "has_log_progress",
                              false,
                              "identity_consistent",
                              referenceCalls != badReference)),
                      false);
                }
                if (name.equals("close")) {
                  closedStatements++;
                  if (cleanup) hit(TEXT_STATEMENTCLOSE);
                  return null;
                }
                throw new AssertionError("unexpected statement operation: " + name);
              });
    }

    private ResultSet resultSet(List<Map<String, Object>> values, boolean cleanup) {
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
                  if (cleanup) hit("next" + (index[0] + 1));
                  return index[0] < values.size();
                }
                if (name.equals("getObject") || name.equals("getString")) {
                  String column = (String) args[0];
                  if (cleanup) hit(column);
                  assertTrue(values.get(index[0]).containsKey(column));
                  return values.get(index[0]).get(column);
                }
                if (name.equals("close")) {
                  closedRows++;
                  if (cleanup) hit("rowClose");
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
