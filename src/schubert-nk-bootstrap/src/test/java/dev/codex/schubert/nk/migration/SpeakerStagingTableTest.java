package dev.codex.schubert.nk.migration;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
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

/** PT-MIG-SPEAKERSTAGE001..024; independent V002 SQL and memory-only JDBC fault matrix. */
final class SpeakerStagingTableTest {
  private static final int ACQUISITION_STEP = 1;
  private static final String SPEAKER_COLUMNS =
      "id, game_id, name, normalized_name, is_protagonist, notes, created_at";
  private static final String FILE_COLUMNS =
      "id, game_id, display_order, storage_relative_path, display_path, file_name, section_code, chapter_title, sha256, byte_size, created_at";
  private static final String ENTRY_COLUMNS =
      "id, game_id, script_file_id, display_order, entry_index, line_number, entry_type, speaker_id, speaker_label, body, raw_block, created_at";
  private static final String AUDIO_COLUMNS =
      "id, game_id, storage_relative_path, display_path, file_name, basename, audio_role, container, duration_ms, byte_size, sha256, created_at";
  private static final String MEDIA_COLUMNS =
      "id, logical_id, media_type, title, category, section, storage_relative_path, display_path, file_name, byte_size, sha256, mime_type, parent_logical_id, pair_key, pair_role, display_order, created_at";
  private static final String LINK_COLUMNS =
      "entry_id, audio_file_id, game_id, link_type, display_order, created_at";
  private static final String PREPARE_SQL =
      "CREATE TEMP TABLE nk_mig_speakers ON COMMIT DROP AS SELECT "
          + SPEAKER_COLUMNS
          + " FROM schubert.speakers WITH NO DATA";
  private static final String TARGET_COUNT = "SELECT count(*) FROM schubert.speakers";
  private static final String STAGED_COUNT = "SELECT count(*) FROM pg_temp.nk_mig_speakers";
  private static final String INSERT_SQL =
      "INSERT INTO schubert.speakers ("
          + SPEAKER_COLUMNS
          + ") SELECT "
          + SPEAKER_COLUMNS
          + " FROM pg_temp.nk_mig_speakers ORDER BY id";
  private static final String DIAGNOSTIC = "migration speaker staging preparation is invalid";
  private static final String INPUT_DIAGNOSTIC = "migration speaker staging input is invalid";
  private static final String PRIMARY_MESSAGE = "synthetic primary";
  private static final String CLEANUP_MESSAGE = "synthetic cleanup";
  private static final String CALL_AUTO = "getAutoCommit";
  private static final String CALL_CREATE = "createStatement";
  private static final String CALL_CLOSE = "close";
  private static final String CREATE_PREFIX = "CREATE TEMP TABLE";
  private static final int SCALAR_QUERIES = 3;
  private static final int SQL_OPERATIONS = 4;
  private static final int DEFAULT_COUNT = 2;
  private static final int WORKERS = 8;
  private static final int TASKS = 64;
  private static final int WAIT_SECONDS = 5;
  private static final int TERMINATION_SECONDS = 10;
  private static final int FULL_SQL_OPERATIONS = 30;
  private static final int FULL_STATEMENTS = 6;
  private static final int FULL_RESULTS = 18;

  @Test
  void speakerStage001ExactSevenColumnDdlAndBorrowedConnection() throws Exception {
    var f = new Fixture();
    new SpeakerStagingTable().prepare(f.connection());
    assertEquals(List.of(PREPARE_SQL), f.sql);
    assertEquals(List.of(30), f.timeouts);
    assertEquals(1, f.statementCreates);
    assertEquals(1, f.statementCloses);
    assertEquals(0, f.resultCloses);
  }

  @Test
  void speakerStage002NullConnectionHasSafeInputDiagnostic() {
    var failure =
        assertThrows(IllegalArgumentException.class, () -> new SpeakerStagingTable().prepare(null));
    assertEquals(INPUT_DIAGNOSTIC, failure.getMessage());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
  }

  @Test
  void speakerStage003AutoCommitCannotDropStagingPrematurely() {
    var f = new Fixture();
    f.autoCommit = true;
    assertEquals(
        DIAGNOSTIC,
        assertThrows(SQLException.class, () -> new SpeakerStagingTable().prepare(f.connection()))
            .getMessage());
    assertEquals(0, f.statementCreates);
    assertTrue(f.sql.isEmpty());
  }

  @Test
  void speakerStage004AcquisitionFailuresHaveNoOwnedResource() {
    for (boolean duringAuto : List.of(true, false)) {
      for (Throwable expected : failures()) {
        var f = new Fixture();
        if (duringAuto) f.autoFailure = expected;
        else f.createFailure = expected;
        assertSame(
            expected,
            assertThrows(
                expected.getClass(), () -> new SpeakerStagingTable().prepare(f.connection())));
        assertEquals(0, f.statementCloses);
        assertTrue(f.sql.isEmpty());
      }
    }
  }

  @Test
  void speakerStage005NullVendorStatementCreatesNoOwnership() {
    var f = new Fixture();
    f.nullStatement = true;
    assertEquals(
        DIAGNOSTIC,
        assertThrows(SQLException.class, () -> new SpeakerStagingTable().prepare(f.connection()))
            .getMessage());
    assertEquals(0, f.statementCloses);
    assertTrue(f.sql.isEmpty());
  }

  @Test
  void speakerStage006TimeoutFailureStillClosesOneStatement() {
    for (Throwable expected : failures()) {
      var f = new Fixture();
      f.timeoutFailure = expected;
      assertSame(
          expected,
          assertThrows(
              expected.getClass(), () -> new SpeakerStagingTable().prepare(f.connection())));
      assertEquals(1, f.statementCloses);
      assertTrue(f.sql.isEmpty());
    }
  }

  @Test
  void speakerStage007DdlFailureNeverRetriesOrRepairs() {
    var f = new Fixture();
    f.ddlFailure = f.primary;
    assertSame(
        f.primary,
        assertThrows(SQLException.class, () -> new SpeakerStagingTable().prepare(f.connection())));
    assertEquals(List.of(PREPARE_SQL), f.sql);
    assertEquals(1, f.statementCloses);
  }

  @Test
  void speakerStage008DdlMustReturnExactlyZero() {
    for (int result : List.of(-1, 1, Integer.MAX_VALUE)) {
      var f = new Fixture();
      f.ddlCount = result;
      assertEquals(
          DIAGNOSTIC,
          assertThrows(SQLException.class, () -> new SpeakerStagingTable().prepare(f.connection()))
              .getMessage());
      assertEquals(1, f.sql.size());
      assertEquals(1, f.statementCloses);
    }
  }

  @Test
  void speakerStage009CloseOnlyFailuresCannotBecomeSuccess() {
    for (Throwable expected : failures()) {
      var f = new Fixture();
      f.statementCloseFailure = expected;
      assertSame(
          expected,
          assertThrows(
              expected.getClass(), () -> new SpeakerStagingTable().prepare(f.connection())));
      assertEquals(1, f.statementCloses);
      assertEquals(List.of(PREPARE_SQL), f.sql);
    }
  }

  @Test
  void speakerStage010PrimaryAndCleanupTypesKeepJavaSuppression() {
    for (int primaryKind : List.of(0, 1, 2)) {
      for (Throwable cleanup : failures()) {
        Throwable primary = failures().get(primaryKind);
        var f = new Fixture();
        f.ddlFailure = primary;
        f.statementCloseFailure = cleanup;
        assertSame(
            primary,
            assertThrows(
                primary.getClass(), () -> new SpeakerStagingTable().prepare(f.connection())));
        assertEquals(1, primary.getSuppressed().length);
        assertSame(cleanup, primary.getSuppressed()[0]);
        assertEquals(1, f.statementCloses);
      }
    }
    var same = new Fixture();
    same.ddlFailure = same.primary;
    same.statementCloseFailure = same.primary;
    var rejected =
        assertThrows(
            IllegalArgumentException.class,
            () -> new SpeakerStagingTable().prepare(same.connection()));
    assertSame(same.primary, rejected.getCause());
    assertEquals(0, same.primary.getSuppressed().length);
    assertEquals(1, same.statementCloses);
  }

  @Test
  void speakerStage011UncheckedBodyFailuresStillClose() {
    for (Throwable expected :
        List.of(new IllegalStateException(PRIMARY_MESSAGE), new AssertionError(PRIMARY_MESSAGE))) {
      var f = new Fixture();
      f.ddlFailure = expected;
      assertSame(
          expected,
          assertThrows(
              expected.getClass(), () -> new SpeakerStagingTable().prepare(f.connection())));
      assertEquals(1, f.statementCloses);
    }
  }

  @Test
  void speakerStage012TransferUsesFourExactSqlStepsAndCounts() throws Exception {
    var f = new Fixture();
    transfer(f);
    assertEquals(List.of(TARGET_COUNT, STAGED_COUNT, INSERT_SQL, TARGET_COUNT), f.sql);
    assertEquals(List.of(30), f.timeouts);
    assertEquals(SCALAR_QUERIES, f.resultCloses);
    assertEquals(1, f.statementCloses);
    assertEquals(1, f.largeUpdates);
  }

  @Test
  void speakerStage013EmptyAndLongMaximumCountsAreNotTruncated() throws Exception {
    for (long count : List.of(0L, Long.MAX_VALUE)) {
      var f = new Fixture();
      f.expected = count;
      f.inserted = count;
      f.answers = List.of(0L, count, count);
      transfer(f);
      assertEquals(SQL_OPERATIONS, f.sql.size());
      assertEquals(1, f.largeUpdates);
      assertEquals(SCALAR_QUERIES, f.resultCloses);
    }
  }

  @Test
  void speakerStage014BadTransferArgumentsFailBeforeConnectionUse() {
    assertEquals(
        INPUT_DIAGNOSTIC,
        assertThrows(
                IllegalArgumentException.class, () -> new SpeakerStagingTable().transfer(null, 1))
            .getMessage());
    var f = new Fixture();
    assertEquals(
        INPUT_DIAGNOSTIC,
        assertThrows(
                IllegalArgumentException.class,
                () -> new SpeakerStagingTable().transfer(f.connection(), -1))
            .getMessage());
    assertEquals(0, f.autoCalls);
    assertEquals(0, f.statementCreates);
  }

  @Test
  void speakerStage015TransferAutoCommitNullAndAcquisitionTimeoutFailures() {
    var auto = new Fixture();
    auto.autoCommit = true;
    assertEquals(DIAGNOSTIC, transferFailure(auto).getMessage());
    var missing = new Fixture();
    missing.nullStatement = true;
    assertEquals(DIAGNOSTIC, transferFailure(missing).getMessage());
    for (int step : List.of(0, 1, 2)) {
      for (Throwable expected : failures()) {
        var f = new Fixture();
        if (step == 0) f.autoFailure = expected;
        else if (step == ACQUISITION_STEP) f.createFailure = expected;
        else f.timeoutFailure = expected;
        assertSame(expected, assertThrows(expected.getClass(), () -> transfer(f)));
        assertTrue(f.sql.isEmpty());
        assertEquals(step == DEFAULT_COUNT ? 1 : 0, f.statementCloses);
      }
    }
  }

  @Test
  void speakerStage016EveryScalarRejectsNullMissingWrongAndExtra() {
    for (Fault fault :
        List.of(Fault.NULL_RESULT, Fault.MISSING, Fault.SQL_NULL, Fault.WRONG, Fault.EXTRA)) {
      for (int at = 0; at < SCALAR_QUERIES; at++) {
        var f = new Fixture();
        f.fault = fault;
        f.badQuery = at;
        assertEquals(DIAGNOSTIC, transferFailure(f).getMessage());
        assertEquals(at + (fault == Fault.NULL_RESULT ? 0 : 1), f.resultCloses);
        assertEquals(1, f.statementCloses);
      }
    }
  }

  @Test
  void speakerStage017EveryScalarOperationKeepsOriginalThrowable() {
    for (Fault fault :
        List.of(Fault.QUERY, Fault.READ, Fault.WAS_NULL, Fault.NEXT_FIRST, Fault.NEXT_SECOND)) {
      for (int at = 0; at < SCALAR_QUERIES; at++) {
        for (Throwable expected : failures()) {
          var f = new Fixture();
          f.fault = fault;
          f.badQuery = at;
          f.phaseFailure = expected;
          assertSame(expected, assertThrows(expected.getClass(), () -> transfer(f)));
          assertEquals(at + (fault == Fault.QUERY ? 0 : 1), f.resultCloses);
          assertEquals(1, f.statementCloses);
        }
      }
    }
  }

  @Test
  void speakerStage018EveryResultCloseFailureRemainsFailure() {
    for (int at = 0; at < SCALAR_QUERIES; at++) {
      for (Throwable expected : failures()) {
        var f = new Fixture();
        f.fault = Fault.RESULT_CLOSE;
        f.badQuery = at;
        f.resultCloseFailure = expected;
        assertSame(expected, assertThrows(expected.getClass(), () -> transfer(f)));
        assertEquals(at + 1, f.resultCloses);
        assertEquals(1, f.statementCloses);
      }
    }
  }

  @Test
  void speakerStage019ReadAndBothCloseFailuresPreserveOrderedSuppressed() {
    for (int at = 0; at < SCALAR_QUERIES; at++) {
      var f = new Fixture();
      f.fault = Fault.COMBINED;
      f.badQuery = at;
      var outer = new SQLException("synthetic outer cleanup");
      f.statementCloseFailure = outer;
      assertSame(f.primary, transferFailure(f));
      assertEquals(2, f.primary.getSuppressed().length);
      assertSame(f.cleanup, f.primary.getSuppressed()[0]);
      assertSame(outer, f.primary.getSuppressed()[1]);
      assertEquals(at + 1, f.resultCloses);
      assertEquals(1, f.statementCloses);
    }
  }

  @Test
  void speakerStage020InsertMustReturnExactNonnegativeLongCount() {
    for (long result : List.of(-2L, -1L, 0L, 1L, 3L, Long.MAX_VALUE)) {
      var f = new Fixture();
      f.inserted = result;
      assertEquals(DIAGNOSTIC, transferFailure(f).getMessage());
      assertEquals(3, f.sql.size());
      assertEquals(DEFAULT_COUNT, f.resultCloses);
      assertEquals(1, f.largeUpdates);
    }
  }

  @Test
  void speakerStage021InsertFailureHasNoPostCountOrRetry() {
    for (Throwable expected : failures()) {
      var f = new Fixture();
      f.insertFailure = expected;
      assertSame(expected, assertThrows(expected.getClass(), () -> transfer(f)));
      assertEquals(List.of(TARGET_COUNT, STAGED_COUNT, INSERT_SQL), f.sql);
      assertEquals(1, f.statementCloses);
      assertEquals(DEFAULT_COUNT, f.resultCloses);
    }
  }

  @Test
  void speakerStage022SixTablesShareBorrowedConnectionAndParentOrder() throws Exception {
    var f = new Fixture();
    f.fullFlow = true;
    f.answers = List.of(0L, 2L, 2L, 0L, 0L, 1L, 1L, 1L, 1L, 0L, 0L, 0L, 1L, 1L, 1L, 1L, 1L, 1L);
    var connection = f.connection();
    var speaker = new SpeakerStagingTable();
    var scenario = new ScenarioStagingTables();
    var asset = new AssetStagingTables();
    speaker.prepare(connection);
    scenario.prepare(connection);
    asset.prepare(connection);
    speaker.transfer(connection, DEFAULT_COUNT);
    scenario.transfer(connection, 1, 1);
    asset.transfer(connection, 1, 1, 1);
    assertEquals(fullSqlOracle(), f.sql);
    assertEquals(FULL_SQL_OPERATIONS, f.sql.size());
    assertEquals(FULL_STATEMENTS, f.statementCreates);
    assertEquals(FULL_STATEMENTS, f.statementCloses);
    assertEquals(FULL_RESULTS, f.resultCloses);
    assertEquals(List.of(30, 30, 30, 30, 30, 30), f.timeouts);
  }

  @Test
  void speakerStage023CloseFailureAndRejectedInputDoNotPoisonFreshBorrowing() throws Exception {
    var broken = new Fixture();
    broken.fault = Fault.QUERY;
    broken.statementCloseFailure = broken.cleanup;
    assertSame(broken.primary, transferFailure(broken));
    assertSame(broken.cleanup, broken.primary.getSuppressed()[0]);
    var closeOnly = new Fixture();
    closeOnly.statementCloseFailure = closeOnly.cleanup;
    assertSame(closeOnly.cleanup, transferFailure(closeOnly));
    var fresh = new Fixture();
    transfer(fresh);
    assertEquals(SCALAR_QUERIES, fresh.resultCloses);
    assertEquals("SpeakerStagingTable[REDACTED]", new SpeakerStagingTable().toString());
  }

  @Test
  void speakerStage024FiniteWorkersHaveIndependentBorrowedResources() throws Exception {
    var table = new SpeakerStagingTable();
    var executor = Executors.newFixedThreadPool(WORKERS);
    try {
      var futures = new ArrayList<Future<List<Integer>>>();
      for (int index = 0; index < TASKS; index++)
        futures.add(
            executor.submit(
                () -> {
                  var f = new Fixture();
                  var connection = f.connection();
                  table.prepare(connection);
                  table.transfer(connection, DEFAULT_COUNT);
                  return List.of(
                      f.sql.size(), f.statementCreates, f.statementCloses, f.resultCloses);
                }));
      for (var future : futures)
        assertEquals(List.of(5, 2, 2, 3), future.get(WAIT_SECONDS, TimeUnit.SECONDS));
    } finally {
      executor.shutdownNow();
      assertTrue(executor.awaitTermination(TERMINATION_SECONDS, TimeUnit.SECONDS));
    }
  }

  private static List<Throwable> failures() {
    return List.of(
        new SQLException(PRIMARY_MESSAGE),
        new IllegalStateException(PRIMARY_MESSAGE),
        new AssertionError(PRIMARY_MESSAGE));
  }

  private static void transfer(Fixture f) throws SQLException {
    new SpeakerStagingTable().transfer(f.connection(), f.expected);
  }

  private static SQLException transferFailure(Fixture f) {
    return assertThrows(SQLException.class, () -> transfer(f));
  }

  private static List<String> fullSqlOracle() {
    var result = new ArrayList<String>();
    var tables =
        List.of(
            "speakers",
            "script_files",
            "script_entries",
            "audio_files",
            "media_assets",
            "entry_audio_links");
    var columns =
        List.of(
            SPEAKER_COLUMNS,
            FILE_COLUMNS,
            ENTRY_COLUMNS,
            AUDIO_COLUMNS,
            MEDIA_COLUMNS,
            LINK_COLUMNS);
    var orders =
        List.of(
            "id",
            "game_id, display_order",
            "display_order",
            "id",
            "id",
            "entry_id, link_type, display_order, audio_file_id");
    for (int index = 0; index < tables.size(); index++)
      result.add(
          "CREATE TEMP TABLE nk_mig_"
              + tables.get(index)
              + " ON COMMIT DROP AS SELECT "
              + columns.get(index)
              + " FROM schubert."
              + tables.get(index)
              + " WITH NO DATA");
    result.add(TARGET_COUNT);
    result.add(STAGED_COUNT);
    result.add(INSERT_SQL);
    result.add(TARGET_COUNT);
    addTransfer(result, tables.subList(1, 3), columns.subList(1, 3), orders.subList(1, 3));
    addTransfer(result, tables.subList(3, 6), columns.subList(3, 6), orders.subList(3, 6));
    return result;
  }

  private static void addTransfer(
      List<String> result, List<String> tables, List<String> columns, List<String> orders) {
    for (String table : tables) result.add("SELECT count(*) FROM schubert." + table);
    for (String table : tables) result.add("SELECT count(*) FROM pg_temp.nk_mig_" + table);
    for (int index = 0; index < tables.size(); index++)
      result.add(
          "INSERT INTO schubert."
              + tables.get(index)
              + " ("
              + columns.get(index)
              + ") SELECT "
              + columns.get(index)
              + " FROM pg_temp.nk_mig_"
              + tables.get(index)
              + " ORDER BY "
              + orders.get(index));
    for (String table : tables) result.add("SELECT count(*) FROM schubert." + table);
  }

  private enum Fault {
    NONE,
    QUERY,
    READ,
    WAS_NULL,
    NEXT_FIRST,
    NEXT_SECOND,
    NULL_RESULT,
    MISSING,
    SQL_NULL,
    WRONG,
    EXTRA,
    RESULT_CLOSE,
    COMBINED
  }

  /** All JDBC methods are local counters/scalars. Any connection mutation or real access fails. */
  private static final class Fixture {
    private final SQLException primary = new SQLException(PRIMARY_MESSAGE);
    private final SQLException cleanup = new SQLException(CLEANUP_MESSAGE);
    private final List<String> sql = new ArrayList<>();
    private final List<Integer> timeouts = new ArrayList<>();
    private boolean autoCommit;
    private boolean nullStatement;
    private boolean fullFlow;
    private int autoCalls;
    private int statementCreates;
    private int statementCloses;
    private int resultCloses;
    private int largeUpdates;
    private int queryIndex;
    private int badQuery;
    private int ddlCount;
    private long expected = DEFAULT_COUNT;
    private long inserted = DEFAULT_COUNT;
    private List<Long> answers = List.of(0L, 2L, 2L);
    private Fault fault = Fault.NONE;
    private @Nullable Throwable autoFailure;
    private @Nullable Throwable createFailure;
    private @Nullable Throwable timeoutFailure;
    private @Nullable Throwable ddlFailure;
    private @Nullable Throwable insertFailure;
    private @Nullable Throwable statementCloseFailure;
    private @Nullable Throwable resultCloseFailure;
    private @Nullable Throwable phaseFailure;

    private Connection connection() {
      return (Connection)
          Proxy.newProxyInstance(
              Connection.class.getClassLoader(),
              new Class<?>[] {Connection.class},
              (proxy, method, args) -> {
                switch (method.getName()) {
                  case CALL_AUTO:
                    autoCalls++;
                    if (autoFailure != null) throw autoFailure;
                    return autoCommit;
                  case CALL_CREATE:
                    statementCreates++;
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
                    timeouts.add((Integer) args[0]);
                    if (timeoutFailure != null) throw timeoutFailure;
                    return null;
                  case "executeUpdate":
                    String ddl = (String) args[0];
                    sql.add(ddl);
                    if (ddlFailure != null) throw ddlFailure;
                    return ddl.startsWith(CREATE_PREFIX) ? ddlCount : 1;
                  case "executeLargeUpdate":
                    sql.add((String) args[0]);
                    int update = largeUpdates;
                    largeUpdates++;
                    if (insertFailure != null) throw insertFailure;
                    return fullFlow && update > 0 ? 1L : inserted;
                  case "executeQuery":
                    sql.add((String) args[0]);
                    int position = queryIndex;
                    queryIndex++;
                    if (position == badQuery && fault == Fault.QUERY)
                      throw phaseFailure == null ? primary : phaseFailure;
                    if (position == badQuery && fault == Fault.NULL_RESULT) return null;
                    return result(position);
                  case CALL_CLOSE:
                    statementCloses++;
                    if (statementCloseFailure != null) throw statementCloseFailure;
                    return null;
                  default:
                    throw new AssertionError("Unexpected statement call: " + method.getName());
                }
              });
    }

    private ResultSet result(int position) {
      boolean broken = position == badQuery;
      final int[] cursor = {0};
      return (ResultSet)
          Proxy.newProxyInstance(
              ResultSet.class.getClassLoader(),
              new Class<?>[] {ResultSet.class},
              (proxy, method, args) -> {
                switch (method.getName()) {
                  case "next":
                    if (broken
                        && (fault == Fault.NEXT_FIRST && cursor[0] == 0
                            || fault == Fault.NEXT_SECOND && cursor[0] == 1))
                      throw phaseFailure == null ? primary : phaseFailure;
                    cursor[0]++;
                    if (broken && fault == Fault.MISSING) return false;
                    return cursor[0] == 1 || broken && fault == Fault.EXTRA;
                  case "getLong":
                    assertEquals(1, args[0]);
                    if (broken && (fault == Fault.READ || fault == Fault.COMBINED))
                      throw phaseFailure == null ? primary : phaseFailure;
                    return answers.get(position) + (broken && fault == Fault.WRONG ? 1 : 0);
                  case "wasNull":
                    if (broken && fault == Fault.WAS_NULL)
                      throw phaseFailure == null ? primary : phaseFailure;
                    return broken && fault == Fault.SQL_NULL;
                  case CALL_CLOSE:
                    resultCloses++;
                    if (broken && (fault == Fault.RESULT_CLOSE || fault == Fault.COMBINED))
                      throw resultCloseFailure == null ? cleanup : resultCloseFailure;
                    return null;
                  default:
                    throw new AssertionError("Unexpected result call: " + method.getName());
                }
              });
    }
  }
}
