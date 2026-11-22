package dev.codex.schubert.nk.migration;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.lang.reflect.Proxy;
import java.security.NoSuchAlgorithmException;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.SQLWarning;
import java.sql.Statement;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;
import org.jspecify.annotations.Nullable;
import org.junit.jupiter.api.Test;

/** PT-MIG-FINAL001..030; memory-only JDBC faults and independent V002/PG18 expectations. */
final class MigrationMasterFinalizerTest {
  private static final String FLUSH_SQL =
      "SET CONSTRAINTS schubert.ck_entry_audio_links_entry_type_limit IMMEDIATE";
  private static final String CALL_CONSTRAINT = "constraint";
  private static final String CALL_CONSTRAINT_WARNINGS = "constraintWarnings";
  private static final String CALL_AUTO = "auto";
  private static final String CALL_CREATE = "create";
  private static final String CALL_QUERY = "query";
  private static final String CALL_PREPARE = "prepare";
  private static final String CALL_OUTER_TIMEOUT = "outerTimeout";
  private static final String CALL_PREPARED_TIMEOUT = "preparedTimeout";
  private static final String CALL_SET_LONG = "setLong";
  private static final String CALL_SET_BOOLEAN = "setBoolean";
  private static final String CALL_PREPARED_QUERY = "preparedQuery";
  private static final String CALL_NEXT1 = "next1";
  private static final String CALL_GET_LONG = "getLong";
  private static final String CALL_WAS_NULL = "wasNull";
  private static final String CALL_NEXT2 = "next2";
  private static final String CALL_RESULT_CLOSE = "resultClose";
  private static final String CALL_PREPARED_CLOSE = "preparedClose";
  private static final String CALL_OUTER_CLOSE = "outerClose";
  private static final String CALL_ANALYZE = "analyze";
  private static final String CALL_WARNINGS = "warnings";

  private static final String SHA =
      "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad";
  private static final String STAMP = "2026-01-02T03:04:05Z";
  private static final String ONE = "1";
  private static final String THREE = "3";
  private static final String SOURCE_VIDEO = "current/a.mp4";
  private static final String TARGET_VIDEO = "video/a.mp4";
  private static final String VIDEO = "VIDEO";
  private static final String SPEAKER_ID = "42";
  private static final String DIAGNOSTIC = "migration master finalization is invalid";
  private static final int IDENTITIES = 5;
  private static final int TABLES = 6;
  private static final int WORKERS = 8;
  private static final int TASKS = 64;
  private static final int WAIT_SECONDS = 5;
  private static final int TERMINATION_SECONDS = 10;
  private static final List<String> MAX_SQL =
      List.of(
          "SELECT COALESCE(MAX(id),0) FROM schubert.speakers",
          "SELECT COALESCE(MAX(id),0) FROM schubert.script_files",
          "SELECT COALESCE(MAX(id),0) FROM schubert.script_entries",
          "SELECT COALESCE(MAX(id),0) FROM schubert.audio_files",
          "SELECT COALESCE(MAX(id),0) FROM schubert.media_assets");
  private static final List<String> SET_SQL =
      List.of(
          "SELECT pg_catalog.setval(pg_catalog.pg_get_serial_sequence('schubert.speakers', 'id'), ?, ?)",
          "SELECT pg_catalog.setval(pg_catalog.pg_get_serial_sequence('schubert.script_files', 'id'), ?, ?)",
          "SELECT pg_catalog.setval(pg_catalog.pg_get_serial_sequence('schubert.script_entries', 'id'), ?, ?)",
          "SELECT pg_catalog.setval(pg_catalog.pg_get_serial_sequence('schubert.audio_files', 'id'), ?, ?)",
          "SELECT pg_catalog.setval(pg_catalog.pg_get_serial_sequence('schubert.media_assets', 'id'), ?, ?)");
  private static final List<String> ANALYZE_SQL =
      List.of(
          "ANALYZE schubert.speakers",
          "ANALYZE schubert.script_files",
          "ANALYZE schubert.script_entries",
          "ANALYZE schubert.audio_files",
          "ANALYZE schubert.media_assets",
          "ANALYZE schubert.entry_audio_links");

  @Test
  void final001ExactPreflightBoundSetvalAnalyzeOrderAndOwnership()
      throws SQLException, NoSuchAlgorithmException {
    var f = new Fixture();
    finish(f, normal());
    var expected = new ArrayList<String>();
    expected.add(FLUSH_SQL);
    expected.addAll(MAX_SQL);
    expected.addAll(SET_SQL);
    expected.addAll(ANALYZE_SQL);
    assertEquals(expected, f.sql);
    assertEquals(List.of(42L, 700L, 900L, 500L, 600L), f.boundLong);
    assertEquals(List.of(true, true, true, true, true), f.boundBoolean);
    assertEquals(List.of(30, 30, 30, 30, 30, 30), f.timeouts);
    assertEquals(10, f.resultCloses);
    assertEquals(5, f.preparedCloses);
    assertEquals(1, f.outerCloses);
    assertEquals(7, f.warningReads);
  }

  @Test
  void final002EmptyUsesOneFalseWithoutConsumingNextval() throws SQLException {
    var f = new Fixture();
    f.expected = new long[IDENTITIES];
    finish(f, new MigrationMasterCopyDataset(new SpeakerCopyBatch(List.of()), emptyContent()));
    assertEquals(List.of(1L, 1L, 1L, 1L, 1L), f.boundLong);
    assertEquals(List.of(false, false, false, false, false), f.boundBoolean);
    assertEquals(17, f.sql.size());
  }

  @Test
  void final003NullArgumentsBeforeConnectionCalls() throws NoSuchAlgorithmException {
    var declared = normal();
    var f = new Fixture();
    var conn = f.connection();
    String expected = "migration master finalization input is invalid";
    assertEquals(
        expected,
        assertThrows(
                IllegalArgumentException.class,
                () -> new MigrationMasterFinalizer().finish(null, declared))
            .getMessage());
    assertEquals(
        expected,
        assertThrows(
                IllegalArgumentException.class,
                () -> new MigrationMasterFinalizer().finish(conn, null))
            .getMessage());
    assertEquals(
        expected,
        assertThrows(
                IllegalArgumentException.class,
                () -> new MigrationMasterFinalizer().finish(null, null))
            .getMessage());
    assertEquals(0, f.autoReads);
    assertTrue(f.sql.isEmpty());
  }

  @Test
  void final004AutoCommitFailsBeforeStatementCreation() {
    var f = new Fixture();
    f.autoCommit = true;
    assertEquals(
        DIAGNOSTIC, assertThrows(SQLException.class, () -> finish(f, normal())).getMessage());
    assertEquals(0, f.creates);
    assertTrue(f.sql.isEmpty());
  }

  @Test
  void final005AutoCreateOriginalFailuresAndNullVendor() throws NoSuchAlgorithmException {
    failuresAt(CALL_AUTO, 0, 1);
    failuresAt(CALL_CREATE, 0, 1);
    var f = new Fixture();
    f.nullOuter = true;
    assertThrows(SQLException.class, () -> finish(f, normal()));
    assertEquals(0, f.outerCloses);
  }

  @Test
  void final006OuterTimeoutPreservesFailureAndCloses() throws NoSuchAlgorithmException {
    failuresAt(CALL_OUTER_TIMEOUT, 0, 1);
  }

  @Test
  void final007EveryPreflightResultShapeIsStrict() {
    shapes(0, IDENTITIES);
  }

  @Test
  void final008EveryPreflightQueryFailureIsOriginal() throws NoSuchAlgorithmException {
    failuresAt(CALL_QUERY, 0, IDENTITIES);
  }

  @Test
  void final009EveryReadPhaseOriginalFailure() throws NoSuchAlgorithmException {
    for (var phase : List.of(CALL_NEXT1, CALL_GET_LONG, CALL_WAS_NULL, CALL_NEXT2))
      failuresAt(phase, 0, IDENTITIES);
  }

  @Test
  void final010PreflightResultCloseIsNotSuccess() throws NoSuchAlgorithmException {
    failuresAt(CALL_RESULT_CLOSE, 0, IDENTITIES);
  }

  @Test
  void final011ReadPrimaryKeepsResultAndOuterSuppressedOrder() {
    for (Throwable primary : failures()) {
      var f = new Fixture();
      f.failCall = CALL_GET_LONG;
      f.failSlot = 0;
      f.failure = primary;
      var inner = new SQLException("synthetic result close");
      var outer = new IllegalStateException("synthetic outer close");
      f.extraResult = inner;
      f.extraOuter = outer;
      f.faultQuery = 0;
      assertSame(primary, assertThrows(primary.getClass(), () -> finish(f, normal())));
      assertEquals(List.of(inner, outer), List.of(primary.getSuppressed()));
      assertEquals(1, f.resultCloses);
      assertEquals(1, f.outerCloses);
      assertEquals(0, f.prepares);
    }
    var self = new Fixture();
    self.failCall = CALL_GET_LONG;
    self.failSlot = 0;
    self.extraResult = self.failure;
    self.faultQuery = 0;
    assertSame(self.failure, assertThrows(SQLException.class, () -> finish(self, normal())));
    assertEquals(0, self.failure.getSuppressed().length);
    assertEquals(1, self.resultCloses);
    assertEquals(1, self.outerCloses);
  }

  @Test
  void final012LastMaxMismatchCannotIssueSequenceOrAnalyze() {
    var f = new Fixture();
    f.faultQuery = IDENTITIES - 1;
    f.shape = Shape.WRONG;
    assertThrows(SQLException.class, () -> finish(f, normal()));
    assertEquals(FLUSH_SQL, f.sql.get(0));
    assertEquals(MAX_SQL, f.sql.subList(1, f.sql.size()));
    assertEquals(0, f.prepares);
    assertEquals(0, f.analyzes);
  }

  @Test
  void final013EachPrepareNullOrOriginalFailureStopsFollowingCalls()
      throws NoSuchAlgorithmException {
    failuresAt(CALL_PREPARE, 0, IDENTITIES);
    for (int slot = 0; slot < IDENTITIES; slot++) {
      var f = new Fixture();
      f.nullPrepared = slot;
      assertThrows(SQLException.class, () -> finish(f, normal()));
      assertEquals(slot, f.preparedCloses);
      assertEquals(1, f.outerCloses);
      assertEquals(0, f.analyzes);
    }
  }

  @Test
  void final014EachLongBindingFailure() throws NoSuchAlgorithmException {
    failuresAt(CALL_SET_LONG, 0, IDENTITIES);
  }

  @Test
  void final015EachBooleanBindingFailure() throws NoSuchAlgorithmException {
    failuresAt(CALL_SET_BOOLEAN, 0, IDENTITIES);
  }

  @Test
  void final016EachPreparedTimeoutFailure() throws NoSuchAlgorithmException {
    failuresAt(CALL_PREPARED_TIMEOUT, 0, IDENTITIES);
  }

  @Test
  void final017EverySetvalResultShapeIsStrict() {
    shapes(IDENTITIES, IDENTITIES);
  }

  @Test
  void final018EveryPreparedQueryFailure() throws NoSuchAlgorithmException {
    failuresAt(CALL_PREPARED_QUERY, 0, IDENTITIES);
  }

  @Test
  void final019EveryPreparedResultReadPhaseFailure() throws NoSuchAlgorithmException {
    for (var phase : List.of(CALL_NEXT1, CALL_GET_LONG, CALL_WAS_NULL, CALL_NEXT2))
      failuresAt(phase, IDENTITIES, IDENTITIES);
  }

  @Test
  void final020EveryPreparedResultCloseFailure() throws NoSuchAlgorithmException {
    failuresAt(CALL_RESULT_CLOSE, IDENTITIES, IDENTITIES);
  }

  @Test
  void final021PreparedResultPrimaryKeepsAllThreeCloseFailuresInOrder() {
    for (Throwable primary : failures()) {
      var f = new Fixture();
      f.failCall = CALL_GET_LONG;
      f.failSlot = IDENTITIES;
      f.failure = primary;
      f.faultQuery = IDENTITIES;
      var result = new SQLException("synthetic result close");
      var prepared = new IllegalArgumentException("synthetic prepared close");
      var outer = new AssertionError("synthetic outer close");
      f.extraResult = result;
      f.extraPrepared = prepared;
      f.extraOuter = outer;
      assertSame(primary, assertThrows(primary.getClass(), () -> finish(f, normal())));
      assertEquals(List.of(result, prepared, outer), List.of(primary.getSuppressed()));
      assertEquals(6, f.resultCloses);
      assertEquals(1, f.preparedCloses);
      assertEquals(1, f.outerCloses);
      assertEquals(0, f.analyzes);
    }
  }

  @Test
  void final022EachPreparedCloseFailureIsPropagated() throws NoSuchAlgorithmException {
    failuresAt(CALL_PREPARED_CLOSE, 0, IDENTITIES);
  }

  @Test
  void final023OuterCloseFailureCannotBeSuccess() throws NoSuchAlgorithmException {
    failuresAt(CALL_OUTER_CLOSE, 0, 1);
  }

  @Test
  void final024EachAnalyzeWrongCountWarningAndOriginalFailures() throws NoSuchAlgorithmException {
    failuresAt(CALL_ANALYZE, 0, TABLES);
    failuresAt(CALL_WARNINGS, 0, TABLES);
    for (int slot = 0; slot < TABLES; slot++) {
      var wrong = new Fixture();
      wrong.badAnalyze = slot;
      assertThrows(SQLException.class, () -> finish(wrong, normal()));
      assertEquals(slot + 1, wrong.analyzes);
      assertEquals(slot + 1, wrong.warningReads);
      var warning = new Fixture();
      warning.badWarning = slot;
      assertEquals(
          DIAGNOSTIC,
          assertThrows(SQLException.class, () -> finish(warning, normal())).getMessage());
      assertEquals(slot + 1, warning.analyzes);
      assertEquals(1, warning.outerCloses);
    }
  }

  @Test
  void final025FreshSuccessAfterRejectedFixtureDoesNotReuseOwner()
      throws SQLException, NoSuchAlgorithmException {
    var rejected = new Fixture();
    rejected.faultQuery = 0;
    rejected.shape = Shape.WRONG;
    assertThrows(SQLException.class, () -> finish(rejected, normal()));
    var next = new Fixture();
    finish(next, normal());
    assertEquals(17, next.sql.size());
    assertEquals(0, rejected.prepares);
  }

  @Test
  void final026MaximumN12IsRetainedWithoutAddingOneOrReorderingRows()
      throws SQLException, NoSuchAlgorithmException {
    var source = normal();
    var input = new ArrayList<SpeakerCopyRow>();
    input.add(
        new SpeakerCopyRow(
            Arrays.<@Nullable String>asList(
                "999999999999", ONE, "Last", "last", "false", null, STAMP)));
    input.addAll(source.speakers().rows());
    var declared = new MigrationMasterCopyDataset(new SpeakerCopyBatch(input), source.content());
    var f = new Fixture();
    f.expected[0] = 999999999999L;
    finish(f, declared);
    assertEquals(List.of(999999999999L, 700L, 900L, 500L, 600L), f.boundLong);
    assertEquals(List.of(true, true, true, true, true), f.boundBoolean);
  }

  @Test
  void final027DiagnosticsFixedAndNoFailureNormalized() {
    assertEquals("MigrationMasterFinalizer[REDACTED]", new MigrationMasterFinalizer().toString());
    var f = new Fixture();
    f.faultQuery = 0;
    f.shape = Shape.SQL_NULL;
    assertEquals(
        DIAGNOSTIC, assertThrows(SQLException.class, () -> finish(f, normal())).getMessage());
  }

  @Test
  void final028FiniteReadersOwnIndependentProxiesAndTerminate()
      throws InterruptedException, ExecutionException, TimeoutException, NoSuchAlgorithmException {
    var declared = normal();
    var executor = Executors.newFixedThreadPool(WORKERS);
    try {
      var futures = new ArrayList<Future<List<Long>>>();
      for (int index = 0; index < TASKS; index++)
        futures.add(
            executor.submit(
                () -> {
                  var f = new Fixture();
                  finish(f, declared);
                  assertEquals(1, f.outerCloses);
                  return f.boundLong;
                }));
      for (var future : futures)
        assertEquals(
            List.of(42L, 700L, 900L, 500L, 600L), future.get(WAIT_SECONDS, TimeUnit.SECONDS));
    } finally {
      executor.shutdownNow();
      assertTrue(executor.awaitTermination(TERMINATION_SECONDS, TimeUnit.SECONDS));
    }
  }

  @Test
  void final029DeferredConstraintMustSucceedBeforeAnyMaxOrSequence() {
    for (boolean warning : List.of(false, true)) {
      var f = new Fixture();
      f.badConstraintUpdate = !warning;
      f.badConstraintWarning = warning;
      assertEquals(
          DIAGNOSTIC, assertThrows(SQLException.class, () -> finish(f, normal())).getMessage());
      assertEquals(List.of(FLUSH_SQL), f.sql);
      assertEquals(0, f.reads);
      assertEquals(0, f.prepares);
      assertEquals(0, f.analyzes);
      assertEquals(0, f.resultCloses);
      assertEquals(0, f.preparedCloses);
      assertEquals(1, f.outerCloses);
      assertEquals(warning ? 1 : 0, f.warningReads);
    }
  }

  @Test
  void final030BothDeferredPhasesPreservePrimaryAndOuterCleanupIdentity()
      throws NoSuchAlgorithmException {
    failuresAt(CALL_CONSTRAINT, 0, 1);
    failuresAt(CALL_CONSTRAINT_WARNINGS, 0, 1);
    var declared = normal();
    for (String phase : List.of(CALL_CONSTRAINT, CALL_CONSTRAINT_WARNINGS)) {
      for (int kind = 0; kind < failures().size(); kind++) {
        for (int cleanup = 0; cleanup <= failures().size(); cleanup++) {
          Throwable primary = failures().get(kind);
          Throwable secondary = cleanup == failures().size() ? primary : failures().get(cleanup);
          var f = new Fixture();
          f.failCall = phase;
          f.failSlot = 0;
          f.failure = primary;
          f.extraOuter = secondary;
          assertSame(primary, assertThrows(primary.getClass(), () -> finish(f, declared)));
          assertEquals(secondary == primary ? 0 : 1, primary.getSuppressed().length);
          if (secondary != primary) assertSame(secondary, primary.getSuppressed()[0]);
          assertEquals(List.of(FLUSH_SQL), f.sql);
          assertEquals(0, f.reads);
          assertEquals(0, f.prepares);
          assertEquals(0, f.analyzes);
          assertEquals(1, f.outerCloses);
          assertEquals(0, f.resultCloses);
          assertEquals(0, f.preparedCloses);
        }
      }
    }
  }

  private static void finish(Fixture f, MigrationMasterCopyDataset declared) throws SQLException {
    new MigrationMasterFinalizer().finish(f.connection(), declared);
  }

  private static List<Throwable> failures() {
    return List.of(
        new SQLException("synthetic sql"),
        new IllegalStateException("synthetic runtime"),
        new AssertionError("synthetic error"));
  }

  private static void failuresAt(String call, int first, int count)
      throws NoSuchAlgorithmException {
    var declared = normal();
    for (int slot = first; slot < first + count; slot++)
      for (Throwable failure : failures()) {
        var f = new Fixture();
        f.failCall = call;
        f.failSlot = slot;
        f.failure = failure;
        assertSame(failure, assertThrows(failure.getClass(), () -> finish(f, declared)));
        assertEquals(1, f.failureHits);
        List<Integer> expectedClose =
            switch (call) {
              case CALL_AUTO, CALL_CREATE -> List.of(0, 0, 0);
              case CALL_OUTER_TIMEOUT, CALL_CONSTRAINT, CALL_CONSTRAINT_WARNINGS ->
                  List.of(0, 0, 1);
              case CALL_QUERY -> List.of(slot, 0, 1);
              case CALL_NEXT1, CALL_GET_LONG, CALL_WAS_NULL, CALL_NEXT2, CALL_RESULT_CLOSE ->
                  List.of(slot + 1, Math.max(0, slot - IDENTITIES + 1), 1);
              case CALL_PREPARE -> List.of(IDENTITIES + slot, slot, 1);
              case CALL_PREPARED_TIMEOUT, CALL_SET_LONG, CALL_SET_BOOLEAN, CALL_PREPARED_QUERY ->
                  List.of(IDENTITIES + slot, slot + 1, 1);
              case CALL_PREPARED_CLOSE -> List.of(IDENTITIES + slot + 1, slot + 1, 1);
              case CALL_ANALYZE, CALL_WARNINGS, CALL_OUTER_CLOSE ->
                  List.of(IDENTITIES * 2, IDENTITIES, 1);
              default -> throw new AssertionError("Unspecified independent phase: " + call);
            };
        assertEquals(expectedClose, List.of(f.resultCloses, f.preparedCloses, f.outerCloses));
      }
  }

  private static void shapes(int first, int count) {
    for (int slot = first; slot < first + count; slot++)
      for (var shape :
          List.of(Shape.NULL_RESULT, Shape.MISSING, Shape.SQL_NULL, Shape.WRONG, Shape.EXTRA)) {
        var f = new Fixture();
        f.faultQuery = slot;
        f.shape = shape;
        assertEquals(
            DIAGNOSTIC, assertThrows(SQLException.class, () -> finish(f, normal())).getMessage());
        assertEquals(0, f.analyzes);
        assertEquals(
            List.of(
                slot + (shape == Shape.NULL_RESULT ? 0 : 1), Math.max(0, slot - IDENTITIES + 1), 1),
            List.of(f.resultCloses, f.preparedCloses, f.outerCloses));
      }
  }

  private enum Shape {
    NONE,
    NULL_RESULT,
    MISSING,
    SQL_NULL,
    WRONG,
    EXTRA
  }

  private static final class Fixture {
    private long[] expected = {42, 700, 900, 500, 600};
    private final List<String> sql = new ArrayList<>();
    private final List<Long> boundLong = new ArrayList<>();
    private final List<Boolean> boundBoolean = new ArrayList<>();
    private final List<Integer> timeouts = new ArrayList<>();
    private boolean autoCommit;
    private boolean nullOuter;
    private int nullPrepared = -1;
    private int faultQuery = -1;
    private Shape shape = Shape.NONE;
    private String failCall = "";
    private int failSlot = -1;
    private Throwable failure = new SQLException("synthetic failure");
    private @Nullable Throwable extraResult;
    private @Nullable Throwable extraPrepared;
    private @Nullable Throwable extraOuter;
    private boolean badConstraintUpdate;
    private boolean badConstraintWarning;
    private boolean constraintWarningPending;
    private int badAnalyze = -1;
    private int badWarning = -1;
    private int autoReads;
    private int creates;
    private int reads;
    private int prepares;
    private int analyzes;
    private int warningReads;
    private int resultCloses;
    private int preparedCloses;
    private int outerCloses;
    private int failureHits;

    private void hit(String call, int slot) throws Throwable {
      if (failCall.equals(call) && failSlot == slot) {
        failureHits++;
        throw failure;
      }
    }

    private Connection connection() {
      return (Connection)
          Proxy.newProxyInstance(
              Connection.class.getClassLoader(),
              new Class<?>[] {Connection.class},
              (proxy, method, args) -> {
                switch (method.getName()) {
                  case "getAutoCommit":
                    autoReads++;
                    hit(CALL_AUTO, 0);
                    return autoCommit;
                  case "createStatement":
                    creates++;
                    hit(CALL_CREATE, 0);
                    return nullOuter ? null : statement();
                  case "prepareStatement":
                    int slot = prepares;
                    prepares++;
                    sql.add((String) args[0]);
                    assertEquals(SET_SQL.get(slot), args[0]);
                    hit(CALL_PREPARE, slot);
                    return nullPrepared == slot ? null : prepared(slot);
                  default:
                    throw new AssertionError(
                        "Unexpected borrowed Connection operation: " + method.getName());
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
                    assertEquals(30, args[0]);
                    timeouts.add((Integer) args[0]);
                    hit(CALL_OUTER_TIMEOUT, 0);
                    return null;
                  case "executeQuery":
                    int query = reads;
                    reads++;
                    sql.add((String) args[0]);
                    assertEquals(MAX_SQL.get(query), args[0]);
                    hit(CALL_QUERY, query);
                    return result(query);
                  case "executeUpdate":
                    if (FLUSH_SQL.equals(args[0])) {
                      sql.add(FLUSH_SQL);
                      constraintWarningPending = true;
                      hit(CALL_CONSTRAINT, 0);
                      return badConstraintUpdate ? 1 : 0;
                    }
                    int position = analyzes;
                    analyzes++;
                    sql.add((String) args[0]);
                    assertEquals(ANALYZE_SQL.get(position), args[0]);
                    hit(CALL_ANALYZE, position);
                    return badAnalyze == position ? 1 : 0;
                  case "getWarnings":
                    warningReads++;
                    if (constraintWarningPending) {
                      constraintWarningPending = false;
                      hit(CALL_CONSTRAINT_WARNINGS, 0);
                      return badConstraintWarning
                          ? new SQLWarning("synthetic deferred constraint")
                          : null;
                    }
                    int warning = analyzes - 1;
                    hit(CALL_WARNINGS, warning);
                    return badWarning == warning ? new SQLWarning("synthetic skipped table") : null;
                  case "close":
                    outerCloses++;
                    hit(CALL_OUTER_CLOSE, 0);
                    if (extraOuter != null) throw extraOuter;
                    return null;
                  default:
                    throw new AssertionError("Unexpected Statement operation: " + method.getName());
                }
              });
    }

    private PreparedStatement prepared(int slot) {
      return (PreparedStatement)
          Proxy.newProxyInstance(
              PreparedStatement.class.getClassLoader(),
              new Class<?>[] {PreparedStatement.class},
              (proxy, method, args) -> {
                switch (method.getName()) {
                  case "setQueryTimeout":
                    assertEquals(30, args[0]);
                    timeouts.add((Integer) args[0]);
                    hit(CALL_PREPARED_TIMEOUT, slot);
                    return null;
                  case CALL_SET_LONG:
                    assertEquals(1, args[0]);
                    hit(CALL_SET_LONG, slot);
                    boundLong.add((Long) args[1]);
                    return null;
                  case CALL_SET_BOOLEAN:
                    assertEquals(2, args[0]);
                    hit(CALL_SET_BOOLEAN, slot);
                    boundBoolean.add((Boolean) args[1]);
                    return null;
                  case "executeQuery":
                    hit(CALL_PREPARED_QUERY, slot);
                    return result(IDENTITIES + slot);
                  case "close":
                    preparedCloses++;
                    hit(CALL_PREPARED_CLOSE, slot);
                    if (extraPrepared != null) throw extraPrepared;
                    return null;
                  default:
                    throw new AssertionError(
                        "Unexpected PreparedStatement operation: " + method.getName());
                }
              });
    }

    private @Nullable ResultSet result(int query) {
      if (faultQuery == query && shape == Shape.NULL_RESULT) return null;
      int[] nextCalls = {0};
      return (ResultSet)
          Proxy.newProxyInstance(
              ResultSet.class.getClassLoader(),
              new Class<?>[] {ResultSet.class},
              (proxy, method, args) -> {
                boolean selected = faultQuery == query;
                switch (method.getName()) {
                  case "next":
                    int call = nextCalls[0];
                    nextCalls[0]++;
                    hit(call == 0 ? CALL_NEXT1 : CALL_NEXT2, query);
                    return call == 0
                        ? !(selected && shape == Shape.MISSING)
                        : selected && shape == Shape.EXTRA;
                  case CALL_GET_LONG:
                    assertEquals(1, args[0]);
                    hit(CALL_GET_LONG, query);
                    long value =
                        query < IDENTITIES
                            ? expected[query]
                            : Math.max(1, expected[query - IDENTITIES]);
                    return selected && shape == Shape.WRONG ? value + 1 : value;
                  case CALL_WAS_NULL:
                    hit(CALL_WAS_NULL, query);
                    return selected && shape == Shape.SQL_NULL;
                  case "close":
                    resultCloses++;
                    hit(CALL_RESULT_CLOSE, query);
                    if (selected && extraResult != null) throw extraResult;
                    return null;
                  default:
                    throw new AssertionError("Unexpected ResultSet operation: " + method.getName());
                }
              });
    }
  }

  private static MigrationMasterCopyDataset normal() throws NoSuchAlgorithmException {
    return new MigrationMasterCopyDataset(speakers(STAMP), content(STAMP));
  }

  private static MigrationCopyDataset content(String stamp) throws NoSuchAlgorithmException {
    return new MigrationCopyDataset(
        scenario(true, SPEAKER_ID, ONE, stamp),
        List.of(audio(stamp)),
        List.of(Arrays.<@Nullable String>asList("900", "500", ONE, "voice", ONE, stamp)),
        media(stamp));
  }

  private static MigrationCopyDataset emptyContent() {
    return new MigrationCopyDataset(emptyScenario(), List.of(), List.of(), emptyMedia());
  }

  private static SpeakerCopyBatch speakers(String stamp) {
    return new SpeakerCopyBatch(
        List.of(
            new SpeakerCopyRow(
                Arrays.<@Nullable String>asList(
                    SPEAKER_ID, ONE, "Alice", "alice", "true", null, stamp))));
  }

  private static ScenarioCopyDataset scenario(
      boolean withEntry, @Nullable String speaker, String game, String stamp) {
    var files =
        new ScenarioFileMigrationMap(
            List.of(new ScenarioFileMigrationMap.FilePair(Integer.parseInt(game), 10, 700)));
    var entries =
        new ScenarioEntryMigrationMap(
            withEntry ? List.of(new ScenarioEntryMigrationMap.IdPair(20, 900)) : List.of());
    var placement =
        new ScenarioEntryPlacementMap(
            files,
            entries,
            withEntry
                ? List.of(
                    new ScenarioEntryPlacementMap.Placement(Integer.parseInt(game), 10, 20, 0))
                : List.of());
    var fileRows =
        new ScenarioFileCopyBatch(
            files,
            List.of(
                Arrays.<@Nullable String>asList(
                    "700",
                    game,
                    ONE,
                    "script/file.txt",
                    "file.txt",
                    "file.txt",
                    null,
                    "chapter",
                    SHA,
                    THREE,
                    stamp)));
    var entryRows =
        withEntry
            ? List.of(
                new ScenarioEntryCopyRow(
                    Arrays.<@Nullable String>asList(
                        "900",
                        game,
                        "700",
                        ONE,
                        "0",
                        null,
                        speaker == null ? "narration" : "dialogue",
                        speaker,
                        null,
                        "hello",
                        "raw",
                        stamp)))
            : List.<ScenarioEntryCopyRow>of();
    return new ScenarioCopyDataset(fileRows, new ScenarioEntryCopyBatch(placement, entryRows));
  }

  private static ScenarioCopyDataset emptyScenario() {
    var files = new ScenarioFileMigrationMap(List.of());
    var entries = new ScenarioEntryMigrationMap(List.of());
    return new ScenarioCopyDataset(
        new ScenarioFileCopyBatch(files, List.of()),
        new ScenarioEntryCopyBatch(
            new ScenarioEntryPlacementMap(files, entries, List.of()), List.of()));
  }

  private static AudioFileCopyRow audio(String stamp) {
    return new AudioFileCopyRow(
        Arrays.<@Nullable String>asList(
            "500",
            ONE,
            "voice/a.ogg",
            "表示",
            "a.ogg",
            "a",
            "voice",
            "ogg",
            "1200",
            THREE,
            SHA,
            stamp));
  }

  private static MediaAssetCopyBatch media(String stamp) throws NoSuchAlgorithmException {
    var manifest =
        new AssetMigrationManifest(
            List.of(
                new AssetMigrationManifest.Entry(
                    AssetMigrationManifest.Kind.VIDEO, SOURCE_VIDEO, TARGET_VIDEO, 3, SHA)));
    var row =
        new MediaAssetCopyRow(
            Arrays.<@Nullable String>asList(
                "600",
                "video-a",
                VIDEO,
                "A",
                "MAIN",
                null,
                TARGET_VIDEO,
                SOURCE_VIDEO,
                "a.mp4",
                THREE,
                SHA,
                "video/mp4",
                null,
                null,
                null,
                ONE,
                stamp));
    return new MediaAssetCopyBatch(manifest, List.of(row));
  }

  private static MediaAssetCopyBatch emptyMedia() {
    return new MediaAssetCopyBatch(new AssetMigrationManifest(List.of()), List.of());
  }
}
