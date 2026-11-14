package dev.codex.schubert.nk.migration;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.lang.reflect.Proxy;
import java.sql.Connection;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import org.jspecify.annotations.Nullable;
import org.junit.jupiter.api.Test;

/** PT-MIG-STAGE001..018; independent literal SQL and memory-only JDBC call/ownership fixtures. */
final class ScenarioStagingTablesTest {
  private static final String ORACLE_FILES =
      "CREATE TEMP TABLE nk_mig_script_files ON COMMIT DROP AS SELECT id, game_id, display_order, "
          + "storage_relative_path, display_path, file_name, section_code, chapter_title, sha256, "
          + "byte_size, created_at FROM schubert.script_files WITH NO DATA";
  private static final String ORACLE_ENTRIES =
      "CREATE TEMP TABLE nk_mig_script_entries ON COMMIT DROP AS SELECT id, game_id,"
          + " script_file_id, display_order, entry_index, line_number, entry_type, speaker_id,"
          + " speaker_label, body, raw_block, created_at FROM schubert.script_entries WITH NO DATA";
  private static final String DIAGNOSTIC = "migration staging preparation is invalid";
  private static final String SYNTHETIC_FAILURE = "synthetic";
  private static final int TASKS = 64;
  private static final int WORKERS = 8;
  private static final int WAIT_SECONDS = 5;
  private static final int TERMINATION_SECONDS = 10;

  @Test
  void literalTwoQueriesAreOrderedAndCopyNoGeneratedColumnOrRows() throws Exception {
    var fixture = new Fixture();
    new ScenarioStagingTables().prepare(fixture.connection());
    assertEquals(List.of(ORACLE_FILES, ORACLE_ENTRIES), fixture.sql);
    assertEquals(List.of("auto", "create", "timeout:30", "sql", "sql", "close"), fixture.calls);
  }

  @Test
  void statementIsClosedExactlyOnceAndConnectionRemainsBorrowed() throws Exception {
    var fixture = new Fixture();
    new ScenarioStagingTables().prepare(fixture.connection());
    assertEquals(1, fixture.closeCalls);
    assertEquals(1, fixture.createCalls);
    assertEquals(2, fixture.sql.size());
  }

  @Test
  void nullConnectionFailsWithFixedInputDiagnostic() {
    assertEquals(
        "migration staging input is invalid",
        assertThrows(
                IllegalArgumentException.class, () -> new ScenarioStagingTables().prepare(null))
            .getMessage());
  }

  @Test
  void autoCommitCannotDropTheTablesBeforeCopy() {
    var fixture = new Fixture();
    fixture.autoCommit = true;
    assertEquals(DIAGNOSTIC, failure(fixture).getMessage());
    assertEquals(List.of("auto"), fixture.calls);
    assertEquals(0, fixture.createCalls);
  }

  @Test
  void originalAutoCommitFailureHasNoCreatedStatement() {
    var fixture = new Fixture();
    var expected = new SQLException(SYNTHETIC_FAILURE);
    fixture.autoFailure = expected;
    assertSame(expected, failure(fixture));
    assertEquals(0, fixture.closeCalls);
  }

  @Test
  void originalCreationFailureIsNotAStatementToClose() {
    var fixture = new Fixture();
    var expected = new SQLException(SYNTHETIC_FAILURE);
    fixture.createFailure = expected;
    assertSame(expected, failure(fixture));
    assertEquals(0, fixture.closeCalls);
  }

  @Test
  void nullVendorStatementIsAnExplicitFailure() {
    var fixture = new Fixture();
    fixture.nullStatement = true;
    assertEquals(DIAGNOSTIC, failure(fixture).getMessage());
    assertEquals(0, fixture.closeCalls);
    assertTrue(fixture.sql.isEmpty());
  }

  @Test
  void timeoutFailureStillClosesWithoutAnyDdl() {
    var fixture = new Fixture();
    var expected = new SQLException(SYNTHETIC_FAILURE);
    fixture.timeoutFailure = expected;
    assertSame(expected, failure(fixture));
    assertEquals(1, fixture.closeCalls);
    assertTrue(fixture.sql.isEmpty());
  }

  @Test
  void firstDdlFailureDoesNotAttemptSecondOrRepair() {
    var fixture = new Fixture();
    var expected = new SQLException("synthetic relation exists");
    fixture.sqlFailure = expected;
    fixture.failAt = 1;
    assertSame(expected, failure(fixture));
    assertEquals(List.of(ORACLE_FILES), fixture.sql);
    assertEquals(1, fixture.closeCalls);
  }

  @Test
  void secondDdlFailureClosesAndNeverRollsBackTheBorrowedConnection() {
    var fixture = new Fixture();
    var expected = new SQLException(SYNTHETIC_FAILURE);
    fixture.sqlFailure = expected;
    fixture.failAt = 2;
    assertSame(expected, failure(fixture));
    assertEquals(List.of(ORACLE_FILES, ORACLE_ENTRIES), fixture.sql);
    assertEquals(1, fixture.closeCalls);
  }

  @Test
  void firstUnexpectedUpdateCountsStopBeforeSecondDdl() {
    for (int value : List.of(-1, 1)) {
      var fixture = new Fixture();
      fixture.firstCount = value;
      assertEquals(DIAGNOSTIC, failure(fixture).getMessage());
      assertEquals(List.of(ORACLE_FILES), fixture.sql);
      assertEquals(1, fixture.closeCalls);
    }
  }

  @Test
  void secondUnexpectedUpdateCountsNeverSucceed() {
    for (int value : List.of(-1, 1)) {
      var fixture = new Fixture();
      fixture.secondCount = value;
      assertEquals(DIAGNOSTIC, failure(fixture).getMessage());
      assertEquals(List.of(ORACLE_FILES, ORACLE_ENTRIES), fixture.sql);
      assertEquals(1, fixture.closeCalls);
    }
  }

  @Test
  void closeFailureAfterBothQueriesIsNotSuccess() {
    var fixture = new Fixture();
    var expected = new SQLException("synthetic close");
    fixture.closeFailure = expected;
    assertSame(expected, failure(fixture));
    assertEquals(2, fixture.sql.size());
    assertEquals(1, fixture.closeCalls);
  }

  @Test
  void primarySqlAndCloseFailureRetainJavaSuppressionOrder() {
    var fixture = new Fixture();
    var primary = new SQLException("synthetic primary");
    var cleanup = new SQLException("synthetic cleanup");
    fixture.sqlFailure = primary;
    fixture.failAt = 1;
    fixture.closeFailure = cleanup;
    assertSame(primary, failure(fixture));
    assertEquals(1, primary.getSuppressed().length);
    assertSame(cleanup, primary.getSuppressed()[0]);
    assertEquals(1, fixture.closeCalls);
  }

  @Test
  void runtimeAndErrorFailuresRemainFailuresWithStatementClosed() {
    for (Throwable expected :
        List.of(
            new IllegalStateException(SYNTHETIC_FAILURE), new AssertionError(SYNTHETIC_FAILURE))) {
      var fixture = new Fixture();
      fixture.sqlFailure = expected;
      fixture.failAt = 1;
      assertSame(
          expected,
          assertThrows(
              expected.getClass(),
              () -> new ScenarioStagingTables().prepare(fixture.connection())));
      assertEquals(1, fixture.closeCalls);
      assertEquals(List.of(ORACLE_FILES), fixture.sql);
    }
  }

  @Test
  void repeatedCallsCreateFreshStatementsWithoutRetainingAConnection() throws Exception {
    var fixture = new Fixture();
    var staging = new ScenarioStagingTables();
    var connection = fixture.connection();
    staging.prepare(connection);
    staging.prepare(connection);
    assertEquals(2, fixture.createCalls);
    assertEquals(2, fixture.closeCalls);
    assertEquals(List.of(ORACLE_FILES, ORACLE_ENTRIES, ORACLE_FILES, ORACLE_ENTRIES), fixture.sql);
  }

  @Test
  void finiteParallelIndependentBorrowedTransactionsDoNotShareState() throws Exception {
    var staging = new ScenarioStagingTables();
    var executor = Executors.newFixedThreadPool(WORKERS);
    try {
      var results = new ArrayList<Future<List<String>>>();
      for (int index = 0; index < TASKS; index++) {
        results.add(
            executor.submit(
                () -> {
                  var fixture = new Fixture();
                  staging.prepare(fixture.connection());
                  assertEquals(1, fixture.closeCalls);
                  return List.copyOf(fixture.sql);
                }));
      }
      for (var result : results)
        assertEquals(
            List.of(ORACLE_FILES, ORACLE_ENTRIES), result.get(WAIT_SECONDS, TimeUnit.SECONDS));
    } finally {
      executor.shutdownNow();
      assertTrue(executor.awaitTermination(TERMINATION_SECONDS, TimeUnit.SECONDS));
    }
  }

  @Test
  void fixedRedactionAndIndependentSuccessAfterFailure() throws Exception {
    var staging = new ScenarioStagingTables();
    var broken = new Fixture();
    broken.autoCommit = true;
    assertEquals(DIAGNOSTIC, failure(broken).getMessage());
    var normal = new Fixture();
    staging.prepare(normal.connection());
    assertEquals(List.of(ORACLE_FILES, ORACLE_ENTRIES), normal.sql);
    assertEquals("ScenarioStagingTables[REDACTED]", staging.toString());
  }

  private static final String ORACLE_TARGET_FILES = "SELECT count(*) FROM schubert.script_files";
  private static final String ORACLE_TARGET_ENTRIES =
      "SELECT count(*) FROM schubert.script_entries";
  private static final String ORACLE_STAGED_FILES =
      "SELECT count(*) FROM pg_temp.nk_mig_script_files";
  private static final String ORACLE_STAGED_ENTRIES =
      "SELECT count(*) FROM pg_temp.nk_mig_script_entries";
  private static final String ORACLE_INSERT_FILES =
      "INSERT INTO schubert.script_files (id, game_id, display_order, storage_relative_path,"
          + " display_path, file_name, section_code, chapter_title, sha256, byte_size, created_at)"
          + " SELECT id, game_id, display_order, storage_relative_path, display_path, file_name,"
          + " section_code, chapter_title, sha256, byte_size, created_at FROM"
          + " pg_temp.nk_mig_script_files ORDER BY game_id, display_order";
  private static final String ORACLE_INSERT_ENTRIES =
      "INSERT INTO schubert.script_entries (id, game_id, script_file_id, display_order,"
          + " entry_index, line_number, entry_type, speaker_id, speaker_label, body, raw_block,"
          + " created_at) SELECT id, game_id, script_file_id, display_order, entry_index,"
          + " line_number, entry_type, speaker_id, speaker_label, body, raw_block, created_at FROM"
          + " pg_temp.nk_mig_script_entries ORDER BY display_order";
  private static final int SCALAR_QUERIES = 6;

  @Test
  void transferChecksEveryCountAndUsesOnlyTheIndependentEightSqlLiterals() throws Exception {
    var fixture = new TransferFixture();
    new ScenarioStagingTables().transfer(fixture.connection(), 1, 1);
    assertEquals(
        List.of(
            ORACLE_TARGET_FILES,
            ORACLE_TARGET_ENTRIES,
            ORACLE_STAGED_FILES,
            ORACLE_STAGED_ENTRIES,
            ORACLE_INSERT_FILES,
            ORACLE_INSERT_ENTRIES,
            ORACLE_TARGET_FILES,
            ORACLE_TARGET_ENTRIES),
        fixture.operations);
    assertEquals(SCALAR_QUERIES, fixture.resultsClosed);
    assertEquals(1, fixture.statementsClosed);
    assertEquals(30, fixture.timeoutSeconds);
  }

  @Test
  void transferEmptyAndMaximumIntManifestCountsAreExact() throws Exception {
    for (int count : List.of(0, Integer.MAX_VALUE)) {
      var fixture = new TransferFixture();
      fixture.counts = List.of(0L, 0L, (long) count, (long) count, (long) count, (long) count);
      fixture.filesInserted = count;
      fixture.entriesInserted = count;
      new ScenarioStagingTables().transfer(fixture.connection(), count, count);
      assertEquals(SCALAR_QUERIES, fixture.resultsClosed);
      assertEquals(2, fixture.updateCalls);
      assertEquals(1, fixture.statementsClosed);
    }
    var fileOnly = new TransferFixture();
    fileOnly.counts = List.of(0L, 0L, 1L, 0L, 1L, 0L);
    fileOnly.entriesInserted = 0;
    new ScenarioStagingTables().transfer(fileOnly.connection(), 1, 0);
    assertEquals(SCALAR_QUERIES, fileOnly.resultsClosed);
    assertEquals(2, fileOnly.updateCalls);
  }

  @Test
  void transferNullNegativeAndEntryOnlyManifestCountsAreRejectedBeforeUse() {
    var staging = new ScenarioStagingTables();
    assertThrows(IllegalArgumentException.class, () -> staging.transfer(null, 1, 1));
    for (var pair : List.of(List.of(-1, 0), List.of(1, -1), List.of(0, -1), List.of(0, 1))) {
      var fixture = new Fixture();
      assertEquals(
          "migration staging input is invalid",
          assertThrows(
                  IllegalArgumentException.class,
                  () -> staging.transfer(fixture.connection(), pair.get(0), pair.get(1)))
              .getMessage());
      assertTrue(fixture.calls.isEmpty());
    }
  }

  @Test
  void transferAutoCommitAndNullStatementNeverReachAnyQuery() {
    var fixture = new Fixture();
    fixture.autoCommit = true;
    assertEquals(
        DIAGNOSTIC,
        assertThrows(
                SQLException.class,
                () -> new ScenarioStagingTables().transfer(fixture.connection(), 1, 1))
            .getMessage());
    assertEquals(List.of("auto"), fixture.calls);
    var other = new Fixture();
    other.nullStatement = true;
    assertEquals(
        DIAGNOSTIC,
        assertThrows(
                SQLException.class,
                () -> new ScenarioStagingTables().transfer(other.connection(), 1, 1))
            .getMessage());
    assertEquals(0, other.closeCalls);
  }

  @Test
  void transferMissingRowAtEveryScalarPositionCannotSucceed() {
    rejectEachScalar(Fault.MISSING, true);
  }

  @Test
  void transferSqlNullAtEveryScalarPositionCannotSucceed() {
    rejectEachScalar(Fault.NULL_VALUE, true);
  }

  @Test
  void transferEveryCountMismatchIncludesNegativeDatabaseResults() {
    rejectEachScalar(Fault.WRONG_COUNT, true);
    var fixture = new TransferFixture();
    fixture.counts = List.of(-1L, 0L, 1L, 1L, 1L, 1L);
    assertEquals(DIAGNOSTIC, transferFailure(fixture).getMessage());
    assertEquals(0, fixture.updateCalls);
    assertEquals(1, fixture.resultsClosed);
  }

  @Test
  void transferExtraRowAtEveryScalarPositionCannotSucceed() {
    rejectEachScalar(Fault.EXTRA, true);
  }

  @Test
  void transferNullResultAtEveryScalarPositionIsAnExplicitFailure() {
    rejectEachScalar(Fault.NULL_RESULT, false);
  }

  @Test
  void transferOriginalQuerySqlFailureAtEveryPositionIsRetained() {
    rejectEachScalar(Fault.QUERY_FAILURE, false);
  }

  @Test
  void transferOriginalGetLongFailureAtEveryPositionStillClosesResult() {
    rejectEachScalar(Fault.READ_FAILURE, true);
  }

  @Test
  void transferOriginalNextFailureAtEveryPositionStillClosesResult() {
    rejectEachScalar(Fault.NEXT_FAILURE, true);
  }

  @Test
  void transferResultCloseFailureAtEveryPositionCannotSucceed() {
    rejectEachScalar(Fault.RESULT_CLOSE_FAILURE, true);
  }

  @Test
  void transferPrimaryAndResultCloseFailureKeepJavaSuppression() {
    var fixture = new TransferFixture();
    fixture.fault = Fault.COMBINED_FAILURE;
    fixture.badAt = 2;
    assertSame(fixture.original, transferFailure(fixture));
    assertEquals(1, fixture.original.getSuppressed().length);
    assertSame(fixture.cleanup, fixture.original.getSuppressed()[0]);
    assertEquals(3, fixture.resultsClosed);
    assertEquals(1, fixture.statementsClosed);
    assertEquals(0, fixture.updateCalls);
  }

  @Test
  void transferBothInsertCountsMustMatchTheIndependentManifest() {
    for (int at : List.of(1, 2)) {
      for (int count : List.of(-1, 0, 2)) {
        var fixture = new TransferFixture();
        if (at == 1) fixture.filesInserted = count;
        else fixture.entriesInserted = count;
        assertEquals(DIAGNOSTIC, transferFailure(fixture).getMessage());
        assertEquals(at, fixture.updateCalls);
        assertEquals(4, fixture.resultsClosed);
        assertEquals(1, fixture.statementsClosed);
      }
    }
  }

  @Test
  void transferBothOriginalInsertFailuresStopWithoutPostOrRetries() {
    for (int at : List.of(1, 2)) {
      var fixture = new TransferFixture();
      fixture.insertFailureAt = at;
      assertSame(fixture.original, transferFailure(fixture));
      assertEquals(at, fixture.updateCalls);
      assertEquals(4, fixture.resultsClosed);
      assertEquals(1, fixture.statementsClosed);
    }
  }

  @Test
  void transferAcquisitionTimeoutAndStatementCloseFailuresRemainFailures() {
    for (int at : List.of(0, 1, 2)) {
      var fixture = new Fixture();
      var expected = new SQLException(SYNTHETIC_FAILURE);
      if (at == 0) fixture.autoFailure = expected;
      else if (at == 1) fixture.createFailure = expected;
      else fixture.timeoutFailure = expected;
      assertSame(
          expected,
          assertThrows(
              SQLException.class,
              () -> new ScenarioStagingTables().transfer(fixture.connection(), 1, 1)));
      assertEquals(at == 2 ? 1 : 0, fixture.closeCalls);
    }
    var completed = new TransferFixture();
    completed.statementCloseFailure = completed.cleanup;
    assertSame(completed.cleanup, transferFailure(completed));
    assertEquals(SCALAR_QUERIES, completed.resultsClosed);
    assertEquals(1, completed.statementsClosed);
  }

  @Test
  void transferRuntimeAndErrorStillCloseTheOwnedStatement() {
    for (Throwable expected :
        List.of(
            new IllegalStateException(SYNTHETIC_FAILURE), new AssertionError(SYNTHETIC_FAILURE))) {
      var fixture = new TransferFixture();
      fixture.fault = Fault.QUERY_FAILURE;
      fixture.badAt = 0;
      fixture.queryFailure = expected;
      assertSame(
          expected,
          assertThrows(
              expected.getClass(),
              () -> new ScenarioStagingTables().transfer(fixture.connection(), 1, 1)));
      assertEquals(1, fixture.statementsClosed);
      assertEquals(0, fixture.resultsClosed);
    }
  }

  @Test
  void transferFiniteWorkersHaveIndependentSqlCountsAndTermination() throws Exception {
    var staging = new ScenarioStagingTables();
    var executor = Executors.newFixedThreadPool(WORKERS);
    try {
      var results = new ArrayList<Future<Integer>>();
      for (int index = 0; index < TASKS; index++) {
        results.add(
            executor.submit(
                () -> {
                  var fixture = new TransferFixture();
                  staging.transfer(fixture.connection(), 1, 1);
                  assertEquals(1, fixture.statementsClosed);
                  return fixture.resultsClosed;
                }));
      }
      for (var result : results)
        assertEquals(SCALAR_QUERIES, result.get(WAIT_SECONDS, TimeUnit.SECONDS));
    } finally {
      executor.shutdownNow();
      assertTrue(executor.awaitTermination(TERMINATION_SECONDS, TimeUnit.SECONDS));
    }
  }

  @Test
  void transferFailureDoesNotAuthorizeCommitOrPoisonIndependentInput() throws Exception {
    var broken = new TransferFixture();
    broken.fault = Fault.WRONG_COUNT;
    broken.badAt = 0;
    assertEquals(DIAGNOSTIC, transferFailure(broken).getMessage());
    assertEquals(0, broken.updateCalls);
    var staging = new ScenarioStagingTables();
    var normal = new TransferFixture();
    staging.transfer(normal.connection(), 1, 1);
    assertEquals(SCALAR_QUERIES, normal.resultsClosed);
    assertEquals("ScenarioStagingTables[REDACTED]", staging.toString());
  }

  private static SQLException transferFailure(TransferFixture fixture) {
    return assertThrows(
        SQLException.class, () -> new ScenarioStagingTables().transfer(fixture.connection(), 1, 1));
  }

  private static void rejectEachScalar(Fault fault, boolean hasResult) {
    for (int index = 0; index < SCALAR_QUERIES; index++) {
      var fixture = new TransferFixture();
      fixture.fault = fault;
      fixture.badAt = index;
      var actual = transferFailure(fixture);
      if (fault == Fault.QUERY_FAILURE
          || fault == Fault.READ_FAILURE
          || fault == Fault.NEXT_FAILURE) assertSame(fixture.original, actual);
      else if (fault == Fault.RESULT_CLOSE_FAILURE) assertSame(fixture.cleanup, actual);
      else assertEquals(DIAGNOSTIC, actual.getMessage());
      assertEquals(index + (hasResult ? 1 : 0), fixture.resultsClosed);
      assertEquals(1, fixture.statementsClosed);
      assertEquals(index < 4 ? 0 : 2, fixture.updateCalls);
    }
  }

  private enum Fault {
    NORMAL,
    MISSING,
    NULL_VALUE,
    WRONG_COUNT,
    EXTRA,
    NULL_RESULT,
    QUERY_FAILURE,
    READ_FAILURE,
    NEXT_FAILURE,
    RESULT_CLOSE_FAILURE,
    COMBINED_FAILURE
  }

  /** All returned JDBC objects are memory-only proxies; unexpected ownership operations fail. */
  private static final class TransferFixture {
    private final List<String> operations = new ArrayList<>();
    private final SQLException original = new SQLException(SYNTHETIC_FAILURE);
    private final SQLException cleanup = new SQLException("synthetic cleanup");
    private List<Long> counts = List.of(0L, 0L, 1L, 1L, 1L, 1L);
    private Fault fault = Fault.NORMAL;
    private int badAt = -1;
    private int queryIndex;
    private int updateCalls;
    private int resultsClosed;
    private int statementsClosed;
    private int timeoutSeconds;
    private int filesInserted = 1;
    private int entriesInserted = 1;
    private int insertFailureAt = -1;
    private @Nullable Throwable queryFailure;
    private @Nullable SQLException statementCloseFailure;

    private Connection connection() {
      return (Connection)
          Proxy.newProxyInstance(
              Connection.class.getClassLoader(),
              new Class<?>[] {Connection.class},
              (proxy, method, args) ->
                  switch (method.getName()) {
                    case "getAutoCommit" -> false;
                    case "createStatement" -> statement();
                    default ->
                        throw new AssertionError(
                            "Unexpected transfer connection call: " + method.getName());
                  });
    }

    private Statement statement() {
      return (Statement)
          Proxy.newProxyInstance(
              Statement.class.getClassLoader(),
              new Class<?>[] {Statement.class},
              (proxy, method, args) -> {
                switch (method.getName()) {
                  case "setQueryTimeout":
                    timeoutSeconds = (Integer) args[0];
                    return null;
                  case "executeQuery":
                    operations.add((String) args[0]);
                    int position = queryIndex++;
                    if (position == badAt && fault == Fault.QUERY_FAILURE) {
                      if (queryFailure != null) throw queryFailure;
                      throw original;
                    }
                    if (position == badAt && fault == Fault.NULL_RESULT) return null;
                    return result(position);
                  case "executeUpdate":
                    operations.add((String) args[0]);
                    updateCalls++;
                    if (updateCalls == insertFailureAt) throw original;
                    return updateCalls == 1 ? filesInserted : entriesInserted;
                  case "close":
                    statementsClosed++;
                    if (statementCloseFailure != null) throw statementCloseFailure;
                    return null;
                  default:
                    throw new AssertionError(
                        "Unexpected transfer statement call: " + method.getName());
                }
              });
    }

    private ResultSet result(int position) {
      final int[] cursor = {0};
      boolean broken = position == badAt;
      return (ResultSet)
          Proxy.newProxyInstance(
              ResultSet.class.getClassLoader(),
              new Class<?>[] {ResultSet.class},
              (proxy, method, args) -> {
                switch (method.getName()) {
                  case "next":
                    if (broken && fault == Fault.NEXT_FAILURE) throw original;
                    cursor[0]++;
                    if (broken && fault == Fault.MISSING) return false;
                    return cursor[0] == 1 || broken && fault == Fault.EXTRA;
                  case "getLong":
                    assertEquals(1, args[0]);
                    if (broken && (fault == Fault.READ_FAILURE || fault == Fault.COMBINED_FAILURE))
                      throw original;
                    return counts.get(position) + (broken && fault == Fault.WRONG_COUNT ? 1 : 0);
                  case "wasNull":
                    return broken && fault == Fault.NULL_VALUE;
                  case "close":
                    resultsClosed++;
                    if (broken
                        && (fault == Fault.RESULT_CLOSE_FAILURE || fault == Fault.COMBINED_FAILURE))
                      throw cleanup;
                    return null;
                  default:
                    throw new AssertionError("Unexpected scalar result call: " + method.getName());
                }
              });
    }
  }

  private static SQLException failure(Fixture fixture) {
    return assertThrows(
        SQLException.class, () -> new ScenarioStagingTables().prepare(fixture.connection()));
  }

  /** No real JDBC driver, connection, stream, file, socket or database is constructed. */
  private static final class Fixture {
    private final List<String> sql = new ArrayList<>();
    private final List<String> calls = new ArrayList<>();
    private boolean autoCommit;
    private boolean nullStatement;
    private int createCalls;
    private int closeCalls;
    private int firstCount;
    private int secondCount;
    private int failAt;
    private @Nullable SQLException autoFailure;
    private @Nullable SQLException createFailure;
    private @Nullable SQLException timeoutFailure;
    private @Nullable SQLException closeFailure;
    private @Nullable Throwable sqlFailure;

    private Connection connection() {
      return (Connection)
          Proxy.newProxyInstance(
              Connection.class.getClassLoader(),
              new Class<?>[] {Connection.class},
              (proxy, method, args) -> {
                switch (method.getName()) {
                  case "getAutoCommit":
                    calls.add("auto");
                    if (autoFailure != null) throw autoFailure;
                    return autoCommit;
                  case "createStatement":
                    calls.add("create");
                    createCalls++;
                    if (createFailure != null) throw createFailure;
                    return nullStatement ? null : statement();
                  default:
                    throw new AssertionError(
                        "Unexpected borrowed connection call: " + method.getName());
                }
              });
    }

    private Statement statement() {
      return (Statement)
          Proxy.newProxyInstance(
              Statement.class.getClassLoader(),
              new Class<?>[] {Statement.class},
              (proxy, method, args) -> {
                switch (method.getName()) {
                  case "setQueryTimeout":
                    calls.add("timeout:" + args[0]);
                    if (timeoutFailure != null) throw timeoutFailure;
                    return null;
                  case "executeUpdate":
                    calls.add("sql");
                    sql.add((String) args[0]);
                    if (sql.size() == failAt && sqlFailure != null) throw sqlFailure;
                    return sql.size() == 1 ? firstCount : secondCount;
                  case "close":
                    calls.add("close");
                    closeCalls++;
                    if (closeFailure != null) throw closeFailure;
                    return null;
                  default:
                    throw new AssertionError(
                        "Unexpected owned statement call: " + method.getName());
                }
              });
    }
  }
}
