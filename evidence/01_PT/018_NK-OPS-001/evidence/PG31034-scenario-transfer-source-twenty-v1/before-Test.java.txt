package dev.codex.schubert.nk.migration;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.lang.reflect.Proxy;
import java.sql.Connection;
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
