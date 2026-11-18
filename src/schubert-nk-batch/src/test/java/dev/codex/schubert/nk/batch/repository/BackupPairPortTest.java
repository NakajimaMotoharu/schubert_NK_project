package dev.codex.schubert.nk.batch.repository;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.batch.backup.BackupFileDigest;
import dev.codex.schubert.nk.batch.backup.BackupManifest;
import dev.codex.schubert.nk.batch.backup.BackupVersions;
import java.lang.reflect.Proxy;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.time.Instant;
import java.time.LocalDate;
import java.time.ZoneOffset;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.function.Executable;

/** PT-BKPPORT001..010: synthetic claims and borrowed JDBC only, never actual Backup authority. */
final class BackupPairPortTest {
  private static final String LITERAL_ENDED_AT = "ended_at";
  private static final String LITERAL_RUN_ID = "run_id";
  private static final String LITERAL_BUSINESS_DATE = "business_date";
  private static final String LITERAL_STEP = "step";
  private static final String LITERAL_ATTEMPT = "attempt";
  private static final String LITERAL_STARTED_AT = "started_at";
  private static final String LITERAL_STATUS = "status";
  private static final String LITERAL_TARGET_COUNT = "target_count";
  private static final String LITERAL_SUCCESS_COUNT = "success_count";
  private static final String LITERAL_FAILURE_COUNT = "failure_count";
  private static final String LITERAL_BYTE_COUNT = "byte_count";
  private static final String LITERAL_ERROR_CODE = "error_code";
  private static final String LITERAL_UNTRUSTED = "UNTRUSTED";
  private static final String LITERAL_ERROR_SUMMARY = "error_summary";
  private static final String LITERAL_STATEMENTCLOSE = "statementClose";
  private static final String LITERAL_FIXTURE = "fixture";
  private static final String PAIR_SQL =
      "select id,run_id,business_date,step,attempt,started_at,ended_at,status,"
          + "target_count,success_count,failure_count,byte_count,error_code,error_summary"
          + " from schubert.batch_runs where id in (?,?) order by id for update";
  private static final String REFERENCES =
      "select has_batch_history,has_inbox_progress,has_log_progress,identity_consistent"
          + " from schubert.maintenance_read_run_references(?,?)";
  private static final String UPDATE =
      "update schubert.batch_runs set ended_at=?,status=?,target_count=?,success_count=?,"
          + "failure_count=?,byte_count=?,error_code=?,error_summary=? where "
          + "id=? and run_id=? and business_date=? and step=? and attempt=? and started_at=?"
          + " and status='RUNNING' and ended_at is null";
  private static final Instant BASE = Instant.parse("2026-11-05T00:00:00Z");
  private static final Instant END = BASE.plusSeconds(5);
  private static final BatchRun RUN = new BatchRun(new UUID(0, 1), BASE);
  private static final String DIAGNOSTIC = "batch repository operation failed";

  @Test
  void runningAndSuccessReadExactPairSqlBindingsAndCloseBeforeReturning() {
    for (boolean success : List.of(false, true)) {
      Fixture fixture = new Fixture();
      fixture.observations = List.of(pair(success));
      var actual = new BackupStepRepository(fixture.connection()).inspect(manifest(), END);
      assertEquals(success ? Optional.of(END) : Optional.empty(), actual);
      assertEquals(List.of(REFERENCES, PAIR_SQL, REFERENCES), fixture.sql);
      assertEquals(Map.of(1, 7L, 2, 8L), fixture.pairBindings.getFirst());
      assertEquals(2, fixture.referenceCalls);
      fixture.assertClosed();
    }
  }

  @Test
  void completeWritesIndependentFourteenBindingsAndReplayRetainsOriginalTimeWithoutUpdate() {
    Fixture fixture = new Fixture();
    fixture.observations = List.of(pair(false), pair(true));
    assertEquals(END, new BackupStepRepository(fixture.connection()).complete(manifest(), END));
    assertEquals(2, fixture.updates.size());
    for (int index = 0; index < 2; index++) {
      var expected = new HashMap<Integer, Object>();
      expected.put(1, END.atOffset(ZoneOffset.UTC));
      expected.put(2, "SUCCESS");
      expected.put(3, index == 0 ? 1L : 2L);
      expected.put(4, index == 0 ? 1L : 2L);
      expected.put(5, 0L);
      expected.put(6, index == 0 ? 3L : 12L);
      expected.put(7, null);
      expected.put(8, null);
      expected.put(9, index == 0 ? 7L : 8L);
      expected.put(10, new UUID(0, 1));
      expected.put(11, LocalDate.of(2026, 11, 5));
      expected.put(12, index == 0 ? "BACKUP_DB" : "BACKUP_CONFIG");
      expected.put(13, 1);
      expected.put(14, BASE.plusSeconds(index + 1).atOffset(ZoneOffset.UTC));
      assertEquals(expected, fixture.updates.get(index));
    }
    fixture.assertClosed();
    Fixture replay = new Fixture();
    replay.observations = List.of(pair(true));
    assertEquals(
        END,
        new BackupStepRepository(replay.connection()).complete(manifest(), END.plusSeconds(9)));
    assertTrue(replay.updates.isEmpty());
    replay.assertClosed();
  }

  @Test
  void missingDuplicateExtraUnknownAndMixedPairsNeverBecomeComplete() {
    var running = pair(false);
    for (var invalid :
        List.of(
            List.<Map<String, Object>>of(),
            List.of(running.getFirst()),
            List.of(running.getFirst(), running.getFirst()),
            List.of(running.getFirst(), running.get(1), running.getFirst()),
            List.of(row(false, true), changed(row(false, false), "id", 9L)),
            List.of(row(false, true), row(true, false)))) {
      Fixture fixture = new Fixture();
      fixture.observations = List.of(invalid);
      catalog(() -> new BackupStepRepository(fixture.connection()).inspect(manifest(), END));
      fixture.assertClosed();
    }
    Fixture disagreement = new Fixture();
    disagreement.observations =
        List.of(
            List.of(
                row(true, true),
                changed(
                    row(true, false),
                    LITERAL_ENDED_AT,
                    END.minusNanos(1000).atOffset(ZoneOffset.UTC))));
    catalog(() -> new BackupStepRepository(disagreement.connection()).inspect(manifest(), END));
    disagreement.assertClosed();
  }

  @Test
  void everyRequiredColumnAndRunningCounterOrIdentityDifferenceRejectsIndependently() {
    var invalid = new ArrayList<Map<String, Object>>();
    for (String column :
        List.of(
            "id",
            LITERAL_RUN_ID,
            LITERAL_BUSINESS_DATE,
            LITERAL_STEP,
            LITERAL_ATTEMPT,
            LITERAL_STARTED_AT,
            LITERAL_STATUS,
            LITERAL_TARGET_COUNT,
            LITERAL_SUCCESS_COUNT,
            LITERAL_FAILURE_COUNT,
            LITERAL_BYTE_COUNT)) invalid.add(changed(row(false, true), column, null));
    var replacements = new HashMap<String, Object>();
    replacements.put(LITERAL_RUN_ID, new UUID(0, 2));
    replacements.put(LITERAL_BUSINESS_DATE, LocalDate.of(2026, 11, 6));
    replacements.put(LITERAL_STEP, "BACKUP_CONFIG");
    replacements.put(LITERAL_ATTEMPT, 2);
    replacements.put(LITERAL_STARTED_AT, BASE.atOffset(ZoneOffset.UTC));
    replacements.put(LITERAL_ENDED_AT, END.atOffset(ZoneOffset.UTC));
    replacements.put(LITERAL_STATUS, "UNKNOWN");
    replacements.put(LITERAL_TARGET_COUNT, 1L);
    replacements.put(LITERAL_SUCCESS_COUNT, 1L);
    replacements.put(LITERAL_FAILURE_COUNT, 1L);
    replacements.put(LITERAL_BYTE_COUNT, 1L);
    replacements.put(LITERAL_ERROR_CODE, LITERAL_UNTRUSTED);
    replacements.put(LITERAL_ERROR_SUMMARY, LITERAL_UNTRUSTED);
    replacements.forEach((key, value) -> invalid.add(changed(row(false, true), key, value)));
    for (var input : invalid) rejectRow(input, false);
  }

  @Test
  void successRequiresExactFilesBytesErrorsAndMicrosecondContentObservationWindow() {
    var replacements = new HashMap<String, Object>();
    replacements.put(LITERAL_TARGET_COUNT, 2L);
    replacements.put(LITERAL_SUCCESS_COUNT, 0L);
    replacements.put(LITERAL_FAILURE_COUNT, 1L);
    replacements.put(LITERAL_BYTE_COUNT, 4L);
    replacements.put(LITERAL_STATUS, "FAILED");
    replacements.put(LITERAL_ENDED_AT, null);
    replacements.put(LITERAL_ERROR_CODE, LITERAL_UNTRUSTED);
    replacements.put(LITERAL_ERROR_SUMMARY, LITERAL_UNTRUSTED);
    replacements.forEach((key, value) -> rejectRow(changed(row(true, true), key, value), true));
    for (Instant invalid : List.of(BASE.plusSeconds(3), END.plusSeconds(1), END.minusNanos(1)))
      rejectRow(changed(row(true, true), LITERAL_ENDED_AT, invalid.atOffset(ZoneOffset.UTC)), true);
    Fixture edge = new Fixture();
    var atContentFinish = BASE.plusSeconds(4).atOffset(ZoneOffset.UTC);
    edge.observations =
        List.of(
            List.of(
                changed(row(true, true), LITERAL_ENDED_AT, atContentFinish),
                changed(row(true, false), LITERAL_ENDED_AT, atContentFinish)));
    assertEquals(
        Optional.of(BASE.plusSeconds(4)),
        new BackupStepRepository(edge.connection()).inspect(manifest(), END));
    edge.assertClosed();
    Fixture configBytes = new Fixture();
    configBytes.observations =
        List.of(List.of(row(true, true), changed(row(true, false), LITERAL_BYTE_COUNT, 11L)));
    catalog(() -> new BackupStepRepository(configBytes.connection()).inspect(manifest(), END));
    configBytes.assertClosed();
  }

  @Test
  void eachJdbcFailurePreservesUnknownIdentityCatalogsSqlAndClosesOwnedScopes() {
    for (String point :
        List.of(
            "prepare",
            "timeout",
            "bind1",
            "bind2",
            "query",
            "next",
            "id",
            LITERAL_RUN_ID,
            LITERAL_BUSINESS_DATE,
            LITERAL_STEP,
            LITERAL_ATTEMPT,
            LITERAL_STARTED_AT,
            LITERAL_STATUS,
            LITERAL_ENDED_AT,
            LITERAL_TARGET_COUNT,
            LITERAL_SUCCESS_COUNT,
            LITERAL_FAILURE_COUNT,
            LITERAL_BYTE_COUNT,
            LITERAL_ERROR_CODE,
            LITERAL_ERROR_SUMMARY,
            "rowClose",
            LITERAL_STATEMENTCLOSE)) {
      for (Throwable failure : failures()) {
        Fixture fixture = new Fixture();
        fixture.faults.put(point, failure);
        Executable action =
            () -> new BackupStepRepository(fixture.connection()).inspect(manifest(), END);
        if (failure instanceof SQLException) catalog(action);
        else assertSame(failure, assertThrows(failure.getClass(), action));
        fixture.assertClosed();
      }
    }
    for (String missing : List.of("statement", "row")) {
      Fixture fixture = new Fixture();
      fixture.missing = missing;
      catalog(() -> new BackupStepRepository(fixture.connection()).inspect(manifest(), END));
      fixture.assertClosed();
    }
  }

  @Test
  void bodyAndBothCloseFailuresFollowIndependentDeclaredPrecedenceAndRedactSecondary() {
    for (Throwable body : failures()) {
      for (Throwable closing : failures()) {
        Fixture fixture = new Fixture();
        fixture.faults.put(LITERAL_STATUS, body);
        fixture.faults.put("rowClose", closing);
        fixture.faults.put(LITERAL_STATEMENTCLOSE, new SQLException("private second close"));
        Executable action =
            () -> new BackupStepRepository(fixture.connection()).inspect(manifest(), END);
        Throwable expected = body instanceof SQLException ? closing : body;
        if (expected instanceof SQLException) catalog(action);
        else {
          var actual = assertThrows(expected.getClass(), action);
          assertSame(expected, actual);
          for (var secondary : actual.getSuppressed()) {
            assertEquals(BatchRepositoryException.class, secondary.getClass());
            assertEquals(DIAGNOSTIC, secondary.getMessage());
          }
        }
        fixture.assertClosed();
      }
    }
    for (Throwable body : failures()) {
      for (Throwable closing : failures()) {
        Fixture fixture = new Fixture();
        fixture.faults.put(LITERAL_STATUS, body);
        fixture.faults.put(LITERAL_STATEMENTCLOSE, closing);
        Executable action =
            () -> new BackupStepRepository(fixture.connection()).inspect(manifest(), END);
        Throwable expected = body instanceof SQLException ? closing : body;
        if (expected instanceof SQLException) catalog(action);
        else assertSame(expected, assertThrows(expected.getClass(), action));
        fixture.assertClosed();
      }
    }
  }

  @Test
  void parentIdentityMustSurviveBeforeAfterAndCompletionReadbackCannotBeManufactured() {
    for (int failedRead : new int[] {1, 2}) {
      Fixture fixture = new Fixture();
      fixture.badReference = failedRead;
      catalog(() -> new BackupStepRepository(fixture.connection()).inspect(manifest(), END));
      assertEquals(failedRead == 1 ? 0 : 1, fixture.pairBindings.size());
      fixture.assertClosed();
    }
    Fixture unchanged = new Fixture();
    catalog(() -> new BackupStepRepository(unchanged.connection()).complete(manifest(), END));
    assertEquals(2, unchanged.updates.size());
    unchanged.assertClosed();
    Fixture wrongTime = new Fixture();
    wrongTime.observations =
        List.of(
            pair(false),
            List.of(
                changed(
                    row(true, true),
                    LITERAL_ENDED_AT,
                    END.minusNanos(1000).atOffset(ZoneOffset.UTC)),
                changed(
                    row(true, false),
                    LITERAL_ENDED_AT,
                    END.minusNanos(1000).atOffset(ZoneOffset.UTC))));
    catalog(() -> new BackupStepRepository(wrongTime.connection()).complete(manifest(), END));
    wrongTime.assertClosed();
  }

  @Test
  void nullAndObservationBoundsRejectBeforeBorrowingResourcesIncludingMaximumAcceptedTime() {
    assertThrows(NullPointerException.class, () -> new BackupStepRepository(null));
    Fixture fixture = new Fixture();
    var repository = new BackupStepRepository(fixture.connection());
    assertThrows(NullPointerException.class, () -> repository.inspect(null, END));
    assertThrows(NullPointerException.class, () -> repository.inspect(manifest(), null));
    for (Instant invalid :
        List.of(BASE.plusSeconds(3), Instant.parse("+10000-01-01T00:00:00Z"), END.plusNanos(1)))
      assertThrows(IllegalArgumentException.class, () -> repository.inspect(manifest(), invalid));
    assertTrue(fixture.sql.isEmpty());
    assertEquals(
        Optional.empty(),
        repository.inspect(manifest(), Instant.parse("9999-12-31T23:59:59.999999Z")));
    fixture.assertClosed();
  }

  @Test
  void terminalFalseSkipBranchAndTypedColumnFailuresDoNotCreateCapabilities() throws Exception {
    var input = BackupTerminalRows.literal();
    input.put(LITERAL_STATUS, "SKIPPED");
    input.put(LITERAL_ENDED_AT, BackupTerminalRows.START.atOffset(ZoneOffset.UTC));
    input.put(LITERAL_ERROR_CODE, "ALREADY_SUCCESSFUL");
    input.put(LITERAL_ERROR_SUMMARY, "step already successful for business date");
    for (String key :
        List.of(
            LITERAL_TARGET_COUNT, LITERAL_SUCCESS_COUNT, LITERAL_FAILURE_COUNT, LITERAL_BYTE_COUNT))
      input.put(key, 0L);
    assertThrows(
        SQLException.class,
        () ->
            BackupStepRepository.readTerminal(
                BackupTerminalRows.row(input), BackupTerminalRows.DB, END));
    for (Throwable expected : failures()) {
      ResultSet driver =
          (ResultSet)
              Proxy.newProxyInstance(
                  BackupPairPortTest.class.getClassLoader(),
                  new Class<?>[] {ResultSet.class},
                  (proxy, method, args) -> {
                    throw expected;
                  });
      assertSame(
          expected,
          assertThrows(
              expected.getClass(),
              () -> BackupStepRepository.readTerminal(driver, BackupTerminalRows.DB, END)));
    }
  }

  private static BackupManifest manifest() {
    var db = new BatchStepAttempt(7, RUN, BatchStep.BACKUP_DB, 1, BASE.plusSeconds(1), false);
    var config =
        new BatchStepAttempt(8, RUN, BatchStep.BACKUP_CONFIG, 1, BASE.plusSeconds(2), false);
    String synthetic = "0".repeat(64);
    return new BackupManifest(
        db,
        config,
        BASE.plusSeconds(3),
        BASE.plusSeconds(4),
        new BackupVersions(
            LITERAL_FIXTURE,
            LITERAL_FIXTURE,
            "001",
            LITERAL_FIXTURE,
            LITERAL_FIXTURE,
            LITERAL_FIXTURE,
            LITERAL_FIXTURE,
            LITERAL_FIXTURE),
        synthetic,
        new BackupFileDigest(3, synthetic),
        new BackupFileDigest(5, synthetic),
        new BackupFileDigest(7, synthetic));
  }

  private static List<Map<String, Object>> pair(boolean success) {
    return List.of(row(success, true), row(success, false));
  }

  private static Map<String, Object> row(boolean success, boolean database) {
    var result = new HashMap<String, Object>();
    result.put("id", database ? 7L : 8L);
    result.put(LITERAL_RUN_ID, new UUID(0, 1));
    result.put(LITERAL_BUSINESS_DATE, LocalDate.of(2026, 11, 5));
    result.put(LITERAL_STEP, database ? "BACKUP_DB" : "BACKUP_CONFIG");
    result.put(LITERAL_ATTEMPT, 1);
    result.put(LITERAL_STARTED_AT, BASE.plusSeconds(database ? 1 : 2).atOffset(ZoneOffset.UTC));
    result.put(LITERAL_ENDED_AT, success ? END.atOffset(ZoneOffset.UTC) : null);
    result.put(LITERAL_STATUS, success ? "SUCCESS" : "RUNNING");
    result.put(LITERAL_TARGET_COUNT, success ? (database ? 1L : 2L) : 0L);
    result.put(LITERAL_SUCCESS_COUNT, success ? (database ? 1L : 2L) : 0L);
    result.put(LITERAL_FAILURE_COUNT, 0L);
    result.put(LITERAL_BYTE_COUNT, success ? (database ? 3L : 12L) : 0L);
    result.put(LITERAL_ERROR_CODE, null);
    result.put(LITERAL_ERROR_SUMMARY, null);
    return result;
  }

  private static Map<String, Object> changed(Map<String, Object> row, String key, Object value) {
    var result = new HashMap<>(row);
    result.put(key, value);
    return result;
  }

  private static void rejectRow(Map<String, Object> input, boolean success) {
    Fixture fixture = new Fixture();
    fixture.observations = List.of(List.of(input, row(success, false)));
    catalog(() -> new BackupStepRepository(fixture.connection()).inspect(manifest(), END));
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
    assertEquals(DIAGNOSTIC, failure.getMessage());
    assertEquals(null, failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
  }

  private static final class Fixture {
    private List<List<Map<String, Object>>> observations = List.of(pair(false));
    private final Map<String, Throwable> faults = new HashMap<>();
    private final List<String> sql = new ArrayList<>();
    private final List<Map<Integer, Object>> pairBindings = new ArrayList<>();
    private final List<Map<Integer, Object>> updates = new ArrayList<>();
    private String missing = "";
    private int pairCalls;
    private int referenceCalls;
    private int badReference;
    private int openedStatements;
    private int closedStatements;
    private int openedRows;
    private int closedRows;

    private Connection connection() {
      return (Connection)
          Proxy.newProxyInstance(
              Fixture.class.getClassLoader(),
              new Class<?>[] {Connection.class},
              (proxy, method, args) ->
                  switch (method.getName()) {
                    case "getAutoCommit", "isReadOnly" -> false;
                    case "getTransactionIsolation" -> Connection.TRANSACTION_READ_COMMITTED;
                    case "prepareStatement" -> statement((String) args[0]);
                    default ->
                        throw new AssertionError(
                            "borrowed connection operation forbidden: " + method.getName());
                  });
    }

    private PreparedStatement statement(String text) throws Throwable {
      assertTrue(List.of(REFERENCES, PAIR_SQL, UPDATE).contains(text), text);
      sql.add(text);
      boolean pair = text.equals(PAIR_SQL);
      boolean update = text.equals(UPDATE);
      if (pair) hit("prepare");
      if (pair && missing.equals("statement")) return null;
      openedStatements++;
      var bindings = new HashMap<Integer, Object>();
      if (pair) pairBindings.add(bindings);
      return (PreparedStatement)
          Proxy.newProxyInstance(
              Fixture.class.getClassLoader(),
              new Class<?>[] {PreparedStatement.class},
              (proxy, method, args) -> {
                String name = method.getName();
                if (name.equals("setQueryTimeout")) {
                  if (pair) hit("timeout");
                  assertEquals(5, args[0]);
                  return null;
                }
                if (List.of("setObject", "setString", "setLong", "setInt").contains(name)) {
                  if (pair) hit("bind" + args[0]);
                  int position = (Integer) args[0];
                  String expectedSetter = "setObject";
                  if (pair) expectedSetter = "setLong";
                  else if (update) {
                    expectedSetter =
                        switch (position) {
                          case 1, 10, 11, 14 -> "setObject";
                          case 2, 7, 8, 12 -> "setString";
                          case 3, 4, 5, 6, 9 -> "setLong";
                          case 13 -> "setInt";
                          default -> throw new AssertionError("unknown update parameter position");
                        };
                  }
                  assertEquals(expectedSetter, name);
                  bindings.put(position, args[1]);
                  return null;
                }
                if (name.equals("executeUpdate")) {
                  assertTrue(update);
                  updates.add(new HashMap<>(bindings));
                  return 1;
                }
                if (name.equals("executeQuery")) {
                  assertTrue(!update);
                  if (pair) {
                    hit("query");
                    if (missing.equals("row")) return null;
                    var selected = observations.get(Math.min(pairCalls, observations.size() - 1));
                    pairCalls++;
                    return result(selected, true);
                  }
                  referenceCalls++;
                  return result(
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
                  if (pair) hit(LITERAL_STATEMENTCLOSE);
                  return null;
                }
                throw new AssertionError("unexpected statement operation: " + name);
              });
    }

    private ResultSet result(List<Map<String, Object>> values, boolean pair) {
      openedRows++;
      int[] index = {-1};
      return (ResultSet)
          Proxy.newProxyInstance(
              Fixture.class.getClassLoader(),
              new Class<?>[] {ResultSet.class},
              (proxy, method, args) -> {
                String name = method.getName();
                if (name.equals("next")) {
                  if (pair) hit("next");
                  index[0]++;
                  return index[0] < values.size();
                }
                if (name.equals("getObject") || name.equals("getString")) {
                  if (pair) hit((String) args[0]);
                  assertTrue(values.get(index[0]).containsKey(args[0]));
                  return values.get(index[0]).get(args[0]);
                }
                if (name.equals("close")) {
                  closedRows++;
                  if (pair) hit("rowClose");
                  return null;
                }
                throw new AssertionError("unexpected row operation: " + name);
              });
    }

    private void hit(String point) throws Throwable {
      if (faults.containsKey(point)) throw faults.get(point);
    }

    private void assertClosed() {
      assertEquals(openedRows, closedRows, "all owned rows closed exactly once");
      assertEquals(openedStatements, closedStatements, "all owned statements closed exactly once");
    }
  }
}
