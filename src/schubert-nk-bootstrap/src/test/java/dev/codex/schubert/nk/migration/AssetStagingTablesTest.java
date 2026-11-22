package dev.codex.schubert.nk.migration;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.lang.reflect.InvocationHandler;
import java.lang.reflect.Proxy;
import java.sql.Connection;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;
import org.jspecify.annotations.Nullable;
import org.junit.jupiter.api.Test;

/** PT-MIG-ASSETSTAGE001..030; literal V002 SQL and owned-memory-only JDBC proxies. */
final class AssetStagingTablesTest {
  private static final String ORACLE_LITERAL_001 = "ddl";
  private static final String ORACLE_LITERAL_002 = "script_files";
  private static final String ORACLE_LITERAL_003 = "script_entries";
  private static final String AUDIO_COLUMNS =
      "id, game_id, storage_relative_path, display_path, file_name, basename, audio_role, container, duration_ms, byte_size, sha256, created_at";
  private static final String MEDIA_COLUMNS =
      "id, logical_id, media_type, title, category, section, storage_relative_path, display_path, file_name, byte_size, sha256, mime_type, parent_logical_id, pair_key, pair_role, display_order, created_at";
  private static final String LINK_COLUMNS =
      "entry_id, audio_file_id, game_id, link_type, display_order, created_at";
  private static final String AUDIO_TABLE = "audio_files";
  private static final String MEDIA_TABLE = "media_assets";
  private static final String LINK_TABLE = "entry_audio_links";
  private static final String INPUT_DIAGNOSTIC = "migration asset staging input is invalid";
  private static final String DIAGNOSTIC = "migration asset staging preparation is invalid";
  private static final String PRIMARY_MESSAGE = "synthetic primary";
  private static final String CLEANUP_MESSAGE = "synthetic cleanup";
  private static final String CALL_AUTO = "auto";
  private static final String CALL_CLOSE = "close";
  private static final String CALL_CREATE = "create";
  private static final String CALL_TIMEOUT = "timeout:30";
  private static final int SCALAR_QUERIES = 9;
  private static final int BEFORE_INSERT_QUERIES = 6;
  private static final int TABLE_COUNT = 3;
  private static final int SECOND_POSITION = 2;
  private static final int FIRST_POSITION = 1;
  private static final int WORKERS = 8;
  private static final int TASKS = 64;
  private static final int WAIT_SECONDS = 5;
  private static final int TERMINATION_SECONDS = 10;
  private static final List<String> PREPARE_SQL =
      List.of(
          "CREATE TEMP TABLE nk_mig_audio_files ON COMMIT DROP AS SELECT "
              + AUDIO_COLUMNS
              + " FROM schubert.audio_files WITH NO DATA",
          "CREATE TEMP TABLE nk_mig_media_assets ON COMMIT DROP AS SELECT "
              + MEDIA_COLUMNS
              + " FROM schubert.media_assets WITH NO DATA",
          "CREATE TEMP TABLE nk_mig_entry_audio_links ON COMMIT DROP AS SELECT "
              + LINK_COLUMNS
              + " FROM schubert.entry_audio_links WITH NO DATA");
  private static final List<String> INSERT_SQL =
      List.of(
          "INSERT INTO schubert.audio_files ("
              + AUDIO_COLUMNS
              + ") SELECT "
              + AUDIO_COLUMNS
              + " FROM pg_temp.nk_mig_audio_files ORDER BY id",
          "INSERT INTO schubert.media_assets ("
              + MEDIA_COLUMNS
              + ") SELECT "
              + MEDIA_COLUMNS
              + " FROM pg_temp.nk_mig_media_assets ORDER BY id",
          "INSERT INTO schubert.entry_audio_links ("
              + LINK_COLUMNS
              + ") SELECT "
              + LINK_COLUMNS
              + " FROM pg_temp.nk_mig_entry_audio_links ORDER BY entry_id, link_type, display_order, audio_file_id");
  private static final List<String> TARGET_COUNTS =
      List.of(
          "SELECT count(*) FROM schubert.audio_files",
          "SELECT count(*) FROM schubert.media_assets",
          "SELECT count(*) FROM schubert.entry_audio_links");
  private static final List<String> STAGE_COUNTS =
      List.of(
          "SELECT count(*) FROM pg_temp.nk_mig_audio_files",
          "SELECT count(*) FROM pg_temp.nk_mig_media_assets",
          "SELECT count(*) FROM pg_temp.nk_mig_entry_audio_links");

  @Test
  void prepareMatchesAllThreeIndependentColumnListsAndExactSql() throws SQLException {
    var f = new Fixture();
    new AssetStagingTables().prepare(f.connection());
    assertEquals(PREPARE_SQL, f.sql);
    assertEquals(12, AUDIO_COLUMNS.split(", ").length);
    assertEquals(17, MEDIA_COLUMNS.split(", ").length);
    assertEquals(6, LINK_COLUMNS.split(", ").length);
    assertTrue(AUDIO_COLUMNS.contains("sha256"));
    assertTrue(MEDIA_COLUMNS.contains("sha256"));
  }

  @Test
  void prepareClosesOnlyItsStatementAndBindsOneTimeout() throws SQLException {
    var f = new Fixture();
    new AssetStagingTables().prepare(f.connection());
    assertEquals(
        List.of(
            CALL_AUTO,
            CALL_CREATE,
            CALL_TIMEOUT,
            ORACLE_LITERAL_001,
            ORACLE_LITERAL_001,
            ORACLE_LITERAL_001,
            CALL_CLOSE),
        f.calls);
    assertEquals(1, f.created);
    assertEquals(1, f.statementsClosed);
    assertEquals(0, f.resultsClosed);
  }

  @Test
  void prepareNullConnectionHasFixedInputDiagnostic() {
    assertEquals(
        INPUT_DIAGNOSTIC,
        assertThrows(IllegalArgumentException.class, () -> new AssetStagingTables().prepare(null))
            .getMessage());
  }

  @Test
  void prepareAutoCommitCannotPublishOrDropStagingEarly() {
    var f = new Fixture();
    f.autoCommit = true;
    assertEquals(DIAGNOSTIC, prepareFailure(f).getMessage());
    assertEquals(List.of(CALL_AUTO), f.calls);
    assertEquals(0, f.created);
  }

  @Test
  void prepareAcquisitionExceptionsKeepIdentityWithoutOwnedStatement() {
    for (int point : List.of(0, 1)) {
      var f = new Fixture();
      if (point == 0) f.autoFailure = f.original;
      else f.createFailure = f.original;
      assertSame(f.original, prepareFailure(f));
      assertEquals(0, f.statementsClosed);
    }
  }

  @Test
  void prepareNullVendorStatementIsAnExplicitSqlFailure() {
    var f = new Fixture();
    f.nullStatement = true;
    assertEquals(DIAGNOSTIC, prepareFailure(f).getMessage());
    assertEquals(0, f.statementsClosed);
    assertTrue(f.sql.isEmpty());
  }

  @Test
  void prepareTimeoutFailureStillClosesBeforeAnyDdl() {
    var f = new Fixture();
    f.timeoutFailure = f.original;
    assertSame(f.original, prepareFailure(f));
    assertEquals(1, f.statementsClosed);
    assertTrue(f.sql.isEmpty());
  }

  @Test
  void eachDdlOriginalFailureStopsTheRemainingPrefix() {
    for (int at = 0; at < TABLE_COUNT; at++) {
      var f = new Fixture();
      f.ddlFailureAt = at;
      assertSame(f.original, prepareFailure(f));
      assertEquals(at + 1, f.sql.size());
      assertEquals(1, f.statementsClosed);
    }
  }

  @Test
  void eachDdlMustReturnExactlyZero() {
    for (int at = 0; at < TABLE_COUNT; at++)
      for (int count : List.of(-1, 1)) {
        var f = new Fixture();
        f.ddlNonzeroAt = at;
        f.ddlReturn = count;
        assertEquals(DIAGNOSTIC, prepareFailure(f).getMessage());
        assertEquals(at + 1, f.sql.size());
        assertEquals(1, f.statementsClosed);
      }
  }

  @Test
  void prepareCloseOnlyFailureCannotBeSuccessful() {
    var f = new Fixture();
    f.statementCloseFailure = f.cleanup;
    assertSame(f.cleanup, prepareFailure(f));
    assertEquals(PREPARE_SQL, f.sql);
  }

  @Test
  void prepareOriginalFailureRetainsSuppressedCleanup() {
    var f = new Fixture();
    f.ddlFailureAt = 1;
    f.statementCloseFailure = f.cleanup;
    assertSame(f.original, prepareFailure(f));
    assertEquals(1, f.original.getSuppressed().length);
    assertSame(f.cleanup, f.original.getSuppressed()[0]);
  }

  @Test
  void prepareRuntimeAndErrorStillCloseTheStatement() {
    for (Throwable error :
        List.of(new IllegalStateException(PRIMARY_MESSAGE), new AssertionError(PRIMARY_MESSAGE))) {
      var f = new Fixture();
      f.ddlFailureAt = 0;
      f.operationFailure = error;
      assertSame(
          error,
          assertThrows(error.getClass(), () -> new AssetStagingTables().prepare(f.connection())));
      assertEquals(1, f.statementsClosed);
    }
  }

  @Test
  void transferMatchesAllTwelveIndependentSqlOperationsAndCounts() throws SQLException {
    var f = new Fixture();
    transfer(f);
    var expected = new ArrayList<>(TARGET_COUNTS);
    expected.addAll(STAGE_COUNTS);
    expected.addAll(INSERT_SQL);
    expected.addAll(TARGET_COUNTS);
    assertEquals(expected, f.sql);
    assertEquals(3, f.largeUpdates);
    assertEquals(9, f.resultsClosed);
    assertEquals(1, f.statementsClosed);
    assertEquals(
        Map.of(
            AUDIO_TABLE,
            2L,
            MEDIA_TABLE,
            149L,
            LINK_TABLE,
            3L,
            ORACLE_LITERAL_002,
            0L,
            ORACLE_LITERAL_003,
            0L),
        f.targets);
  }

  @Test
  void emptyCountsAndAudioZeroWithNoLinksRemainValid() throws SQLException {
    for (long media : List.of(0L, 149L)) {
      var f = new Fixture();
      f.staged.put(AUDIO_TABLE, 0L);
      f.staged.put(MEDIA_TABLE, media);
      f.staged.put(LINK_TABLE, 0L);
      new AssetStagingTables().transfer(f.connection(), 0, media, 0);
      assertEquals(9, f.resultsClosed);
      assertEquals(3, f.largeUpdates);
    }
  }

  @Test
  void largeUpdateAndCountUseLongWithoutIntegerTruncation() throws SQLException {
    var f = new Fixture();
    for (var table : List.of(AUDIO_TABLE, MEDIA_TABLE, LINK_TABLE))
      f.staged.put(table, Long.MAX_VALUE);
    new AssetStagingTables()
        .transfer(f.connection(), Long.MAX_VALUE, Long.MAX_VALUE, Long.MAX_VALUE);
    assertEquals(Long.MAX_VALUE, f.targets.get(MEDIA_TABLE));
    assertEquals(3, f.largeUpdates);
  }

  @Test
  void transferNullNegativeAndImpossibleAudioLinkInputsFailBeforeJdbc() {
    assertEquals(
        INPUT_DIAGNOSTIC,
        assertThrows(
                IllegalArgumentException.class,
                () -> new AssetStagingTables().transfer(null, 2, 149, 3))
            .getMessage());
    for (long[] counts :
        List.of(
            new long[] {-1, 149, 3},
            new long[] {2, -1, 3},
            new long[] {2, 149, -1},
            new long[] {0, 149, 3})) {
      var f = new Fixture();
      assertEquals(
          INPUT_DIAGNOSTIC,
          assertThrows(
                  IllegalArgumentException.class,
                  () ->
                      new AssetStagingTables()
                          .transfer(f.connection(), counts[0], counts[1], counts[2]))
              .getMessage());
      assertTrue(f.calls.isEmpty());
    }
  }

  @Test
  void transferAutoCommitAndNullVendorStatementAreRejected() {
    var f = new Fixture();
    f.autoCommit = true;
    assertEquals(DIAGNOSTIC, transferFailure(f).getMessage());
    assertEquals(0, f.created);
    f = new Fixture();
    f.nullStatement = true;
    assertEquals(DIAGNOSTIC, transferFailure(f).getMessage());
    assertEquals(0, f.statementsClosed);
  }

  @Test
  void transferAcquisitionAndTimeoutFailuresKeepOriginalIdentity() {
    for (int point : List.of(0, 1, 2)) {
      var f = new Fixture();
      if (point == 0) f.autoFailure = f.original;
      else if (point == FIRST_POSITION) f.createFailure = f.original;
      else f.timeoutFailure = f.original;
      assertSame(f.original, transferFailure(f));
      assertEquals(point == SECOND_POSITION ? 1 : 0, f.statementsClosed);
      assertTrue(f.sql.isEmpty());
    }
  }

  @Test
  void allNineNullResultsAreRejectedWithoutInventedOwnership() {
    eachScalar(Fault.NULL_RESULT, false);
  }

  @Test
  void allNineMissingScalarRowsAreRejected() {
    eachScalar(Fault.MISSING, true);
  }

  @Test
  void allNineSqlNullCountsAreRejected() {
    eachScalar(Fault.NULL_VALUE, true);
  }

  @Test
  void allNineWrongCountsAreRejected() {
    eachScalar(Fault.WRONG_COUNT, true);
  }

  @Test
  void allNineExtraScalarRowsAreRejected() {
    eachScalar(Fault.EXTRA, true);
  }

  @Test
  void everyScalarQueryReadWasNullAndNextFailureKeepsTheOriginal() {
    for (var fault :
        List.of(
            Fault.QUERY_FAILURE,
            Fault.READ_FAILURE,
            Fault.WAS_NULL_FAILURE,
            Fault.NEXT_FIRST_FAILURE,
            Fault.NEXT_SECOND_FAILURE)) eachScalar(fault, fault != Fault.QUERY_FAILURE);
  }

  @Test
  void everyResultCloseAndCombinedFailureRetainsTwrSuppression() {
    eachScalar(Fault.RESULT_CLOSE_FAILURE, true);
    for (int at = 0; at < SCALAR_QUERIES; at++) {
      var f = new Fixture();
      f.badQuery = at;
      f.fault = Fault.COMBINED;
      assertSame(f.original, transferFailure(f));
      assertEquals(1, f.original.getSuppressed().length);
      assertSame(f.cleanup, f.original.getSuppressed()[0]);
      assertEquals(at + 1, f.resultsClosed);
      assertEquals(1, f.statementsClosed);
    }
  }

  @Test
  void eachLargeInsertRequiresTheExactNonnegativeLongCount() {
    for (int at = 0; at < TABLE_COUNT; at++)
      for (long count : List.of(-1L, 0L, 999L)) {
        var f = new Fixture();
        f.badInsertCount = at;
        f.insertReturn = count;
        assertEquals(DIAGNOSTIC, transferFailure(f).getMessage());
        assertEquals(at + 1, f.largeUpdates);
        assertEquals(6, f.resultsClosed);
        assertEquals(1, f.statementsClosed);
      }
  }

  @Test
  void insertAndRuntimeFailuresCannotRetryOrCommitThePartialPrefix() {
    for (int at = 0; at < TABLE_COUNT; at++) {
      var f = new Fixture();
      f.insertFailureAt = at;
      assertSame(f.original, transferFailure(f));
      assertEquals(at + 1, f.largeUpdates);
      assertEquals(6, f.resultsClosed);
    }
    for (Throwable error :
        List.of(new IllegalStateException(PRIMARY_MESSAGE), new AssertionError(PRIMARY_MESSAGE))) {
      var f = new Fixture();
      f.fault = Fault.QUERY_FAILURE;
      f.badQuery = 0;
      f.operationFailure = error;
      assertSame(error, assertThrows(error.getClass(), () -> transfer(f)));
      assertEquals(1, f.statementsClosed);
      assertEquals(0, f.largeUpdates);
    }
  }

  @Test
  void scenarioTwoThenAssetThreeShareTheSameBorrowedTransactionInRequiredOrder()
      throws SQLException {
    var f = new Fixture();
    var connection = f.connection();
    var scenario = new ScenarioStagingTables();
    var assets = new AssetStagingTables();
    scenario.prepare(connection);
    assets.prepare(connection);
    scenario.transfer(connection, 1, 1);
    assets.transfer(connection, 2, 149, 3);
    assertEquals(25, f.sql.size());
    assertEquals(4, f.created);
    assertEquals(4, f.statementsClosed);
    assertEquals(15, f.resultsClosed);
    assertEquals(3, f.largeUpdates);
    assertEquals(
        Map.of(
            ORACLE_LITERAL_002,
            1L,
            ORACLE_LITERAL_003,
            1L,
            AUDIO_TABLE,
            2L,
            MEDIA_TABLE,
            149L,
            LINK_TABLE,
            3L),
        f.targets);
    assertEquals(
        "CREATE TEMP TABLE nk_mig_script_files ON COMMIT DROP AS SELECT "
            + "id, game_id, display_order, storage_relative_path, display_path, file_name, section_code, chapter_title, sha256, byte_size, created_at FROM schubert.script_files WITH NO DATA",
        f.sql.get(0));
    assertEquals(PREPARE_SQL, f.sql.subList(2, 5));
    assertTrue(f.sql.get(9).startsWith("INSERT INTO schubert.script_files"));
    assertEquals(TARGET_COUNTS, f.sql.subList(13, 16));
  }

  @Test
  void closeFailuresAndRejectedCallsDoNotPoisonAnIndependentTransaction() throws SQLException {
    var broken = new Fixture();
    broken.fault = Fault.QUERY_FAILURE;
    broken.badQuery = 0;
    broken.statementCloseFailure = broken.cleanup;
    assertSame(broken.original, transferFailure(broken));
    assertSame(broken.cleanup, broken.original.getSuppressed()[0]);
    var closed = new Fixture();
    closed.statementCloseFailure = closed.cleanup;
    assertSame(closed.cleanup, transferFailure(closed));
    assertEquals(9, closed.resultsClosed);
    var normal = new Fixture();
    transfer(normal);
    assertEquals(9, normal.resultsClosed);
    assertEquals("AssetStagingTables[REDACTED]", new AssetStagingTables().toString());
  }

  @Test
  void finiteWorkersOwnIndependentStatementsAndAllResultsTerminate()
      throws InterruptedException, ExecutionException, TimeoutException {
    var tables = new AssetStagingTables();
    var executor = Executors.newFixedThreadPool(WORKERS);
    try {
      var results = new ArrayList<Future<Integer>>();
      for (int i = 0; i < TASKS; i++)
        results.add(
            executor.submit(
                () -> {
                  var f = new Fixture();
                  tables.prepare(f.connection());
                  tables.transfer(f.connection(), 2, 149, 3);
                  assertEquals(2, f.statementsClosed);
                  return f.resultsClosed;
                }));
      for (var result : results) assertEquals(9, result.get(WAIT_SECONDS, TimeUnit.SECONDS));
    } finally {
      executor.shutdownNow();
      assertTrue(executor.awaitTermination(TERMINATION_SECONDS, TimeUnit.SECONDS));
    }
  }

  private static void transfer(Fixture f) throws SQLException {
    new AssetStagingTables().transfer(f.connection(), 2, 149, 3);
  }

  private static SQLException transferFailure(Fixture f) {
    return assertThrows(SQLException.class, () -> transfer(f));
  }

  private static SQLException prepareFailure(Fixture f) {
    return assertThrows(SQLException.class, () -> new AssetStagingTables().prepare(f.connection()));
  }

  private static void eachScalar(Fault fault, boolean ownsResult) {
    for (int at = 0; at < SCALAR_QUERIES; at++) {
      var f = new Fixture();
      f.fault = fault;
      f.badQuery = at;
      var failure = transferFailure(f);
      if (List.of(
              Fault.QUERY_FAILURE,
              Fault.READ_FAILURE,
              Fault.WAS_NULL_FAILURE,
              Fault.NEXT_FIRST_FAILURE,
              Fault.NEXT_SECOND_FAILURE)
          .contains(fault)) assertSame(f.original, failure);
      else if (fault == Fault.RESULT_CLOSE_FAILURE) assertSame(f.cleanup, failure);
      else assertEquals(DIAGNOSTIC, failure.getMessage());
      assertEquals(at + (ownsResult ? 1 : 0), f.resultsClosed);
      assertEquals(1, f.statementsClosed);
      assertEquals(at < BEFORE_INSERT_QUERIES ? 0 : TABLE_COUNT, f.largeUpdates);
    }
  }

  private enum Fault {
    NORMAL,
    NULL_RESULT,
    MISSING,
    NULL_VALUE,
    WRONG_COUNT,
    EXTRA,
    QUERY_FAILURE,
    READ_FAILURE,
    WAS_NULL_FAILURE,
    NEXT_FIRST_FAILURE,
    NEXT_SECOND_FAILURE,
    RESULT_CLOSE_FAILURE,
    COMBINED
  }

  private static final class Fixture {
    private final SQLException original = new SQLException(PRIMARY_MESSAGE);
    private final SQLException cleanup = new SQLException(CLEANUP_MESSAGE);
    private final List<String> sql = new ArrayList<>();
    private final List<String> calls = new ArrayList<>();
    private final Map<String, Long> staged =
        new HashMap<>(
            Map.of(
                AUDIO_TABLE,
                2L,
                MEDIA_TABLE,
                149L,
                LINK_TABLE,
                3L,
                ORACLE_LITERAL_002,
                1L,
                ORACLE_LITERAL_003,
                1L));
    private final Map<String, Long> targets =
        new HashMap<>(
            Map.of(
                AUDIO_TABLE,
                0L,
                MEDIA_TABLE,
                0L,
                LINK_TABLE,
                0L,
                ORACLE_LITERAL_002,
                0L,
                ORACLE_LITERAL_003,
                0L));
    private boolean autoCommit;
    private boolean nullStatement;
    private @Nullable SQLException autoFailure;
    private @Nullable SQLException createFailure;
    private @Nullable SQLException timeoutFailure;
    private @Nullable SQLException statementCloseFailure;
    private Throwable operationFailure = original;
    private int ddlFailureAt = -1;
    private int ddlNonzeroAt = -1;
    private int ddlReturn;
    private int insertFailureAt = -1;
    private int badInsertCount = -1;
    private long insertReturn;
    private Fault fault = Fault.NORMAL;
    private int badQuery = -1;
    private int created;
    private int statementsClosed;
    private int resultsClosed;
    private int ddlCalls;
    private int queryCalls;
    private int largeUpdates;

    private Connection connection() {
      return proxy(
          Connection.class,
          (object, method, args) -> {
            switch (method.getName()) {
              case "getAutoCommit":
                calls.add(CALL_AUTO);
                if (autoFailure != null) throw autoFailure;
                return autoCommit;
              case "createStatement":
                calls.add(CALL_CREATE);
                created++;
                if (createFailure != null) throw createFailure;
                return nullStatement ? null : statement();
              default:
                throw new AssertionError(
                    "unexpected borrowed connection operation: " + method.getName());
            }
          });
    }

    private Statement statement() {
      return proxy(
          Statement.class,
          (object, method, args) -> {
            switch (method.getName()) {
              case "setQueryTimeout":
                calls.add("timeout:" + args[0]);
                assertEquals(30, args[0]);
                if (timeoutFailure != null) throw timeoutFailure;
                return null;
              case "close":
                calls.add(CALL_CLOSE);
                statementsClosed++;
                if (statementCloseFailure != null) throw statementCloseFailure;
                return null;
              case "executeUpdate":
                {
                  String text = (String) args[0];
                  sql.add(text);
                  if (text.startsWith("CREATE TEMP TABLE")) {
                    calls.add(ORACLE_LITERAL_001);
                    int at = ddlCalls;
                    ddlCalls++;
                    if (at == ddlFailureAt) throw operationFailure;
                    return at == ddlNonzeroAt ? ddlReturn : 0;
                  }
                  assertTrue(text.startsWith("INSERT INTO schubert.script_"));
                  String table = text.split(" ")[2].substring("schubert.".length());
                  long count = staged.get(table);
                  targets.put(table, count);
                  return Math.toIntExact(count);
                }
              case "executeLargeUpdate":
                {
                  String text = (String) args[0];
                  sql.add(text);
                  int at = largeUpdates;
                  largeUpdates++;
                  if (at == insertFailureAt) throw original;
                  String table = text.split(" ")[2].substring("schubert.".length());
                  long count = at == badInsertCount ? insertReturn : staged.get(table);
                  targets.put(table, count);
                  return count;
                }
              case "executeQuery":
                {
                  String text = (String) args[0];
                  sql.add(text);
                  int at = queryCalls;
                  queryCalls++;
                  Fault selected = at == badQuery ? fault : Fault.NORMAL;
                  if (selected == Fault.QUERY_FAILURE) throw operationFailure;
                  if (selected == Fault.NULL_RESULT) return null;
                  String qualified = text.substring(text.indexOf(" FROM ") + 6);
                  String table =
                      qualified
                          .substring(qualified.lastIndexOf('.') + 1)
                          .replaceFirst("^nk_mig_", "");
                  long value = (qualified.startsWith("pg_temp.") ? staged : targets).get(table);
                  return result(value, selected);
                }
              default:
                throw new AssertionError("unexpected statement operation: " + method.getName());
            }
          });
    }

    private ResultSet result(long value, Fault selected) {
      int[] nextCalls = {0};
      return proxy(
          ResultSet.class,
          (object, method, args) -> {
            switch (method.getName()) {
              case "next":
                nextCalls[0]++;
                if (selected == Fault.NEXT_FIRST_FAILURE && nextCalls[0] == FIRST_POSITION
                    || selected == Fault.NEXT_SECOND_FAILURE && nextCalls[0] == SECOND_POSITION)
                  throw original;
                if (selected == Fault.MISSING) return false;
                return nextCalls[0] == FIRST_POSITION
                    || selected == Fault.EXTRA && nextCalls[0] == SECOND_POSITION;
              case "getLong":
                assertEquals(1, args[0]);
                if (selected == Fault.READ_FAILURE || selected == Fault.COMBINED) throw original;
                return selected == Fault.WRONG_COUNT ? value + 1 : value;
              case "wasNull":
                if (selected == Fault.WAS_NULL_FAILURE) throw original;
                return selected == Fault.NULL_VALUE;
              case "close":
                resultsClosed++;
                if (selected == Fault.RESULT_CLOSE_FAILURE || selected == Fault.COMBINED)
                  throw cleanup;
                return null;
              default:
                throw new AssertionError("unexpected scalar operation: " + method.getName());
            }
          });
    }

    private static <T> T proxy(Class<T> type, InvocationHandler handler) {
      return type.cast(
          Proxy.newProxyInstance(type.getClassLoader(), new Class<?>[] {type}, handler));
    }
  }

  /** SSC366/PT-MIG-CLEANUP003: query primary and outer cleanup, no following SQL. */
  @Test
  void transferPrimaryAndOuterCleanupHaveOneIndependentSuppressedInstance() {
    var fixture = new Fixture();
    fixture.fault = Fault.QUERY_FAILURE;
    fixture.badQuery = 0;
    fixture.statementCloseFailure = fixture.cleanup;
    assertSame(fixture.original, transferFailure(fixture));
    assertEquals(1, fixture.original.getSuppressed().length);
    assertSame(fixture.cleanup, fixture.original.getSuppressed()[0]);
    assertEquals(List.of(TARGET_COUNTS.getFirst()), fixture.sql);
    assertEquals(0, fixture.resultsClosed);
    assertEquals(1, fixture.statementsClosed);
  }

  /** SSC366/PT-MIG-CLEANUP004: two cleanup failures retain their exact order. */
  @Test
  void transferInnerAndOuterCleanupKeepBothFailuresOnOriginalPrimary() {
    var fixture = new Fixture();
    fixture.fault = Fault.COMBINED;
    fixture.badQuery = 0;
    var outer = new SQLException("synthetic outer close");
    fixture.statementCloseFailure = outer;
    assertSame(fixture.original, transferFailure(fixture));
    assertEquals(2, fixture.original.getSuppressed().length);
    assertSame(fixture.cleanup, fixture.original.getSuppressed()[0]);
    assertSame(outer, fixture.original.getSuppressed()[1]);
    assertEquals(List.of(TARGET_COUNTS.getFirst()), fixture.sql);
    assertEquals(1, fixture.resultsClosed);
    assertEquals(1, fixture.statementsClosed);
  }
}
