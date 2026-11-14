package dev.codex.schubert.nk.migration;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.lang.reflect.Proxy;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.SQLWarning;
import java.sql.Statement;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import org.jspecify.annotations.Nullable;
import org.junit.jupiter.api.Test;

/** PT-MIG-FINAL001..028; memory-only JDBC faults and independent V002/PG18 expectations. */
final class MigrationMasterFinalizerTest {
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
  void final001ExactPreflightBoundSetvalAnalyzeOrderAndOwnership() throws Exception {
    var f = new Fixture();
    finish(f, normal());
    var expected = new ArrayList<String>();
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
    assertEquals(6, f.warningReads);
  }

  @Test
  void final002EmptyUsesOneFalseWithoutConsumingNextval() throws Exception {
    var f = new Fixture();
    f.expected = new long[IDENTITIES];
    finish(f, new MigrationMasterCopyDataset(new SpeakerCopyBatch(List.of()), emptyContent()));
    assertEquals(List.of(1L, 1L, 1L, 1L, 1L), f.boundLong);
    assertEquals(List.of(false, false, false, false, false), f.boundBoolean);
    assertEquals(16, f.sql.size());
  }

  @Test
  void final003NullArgumentsBeforeConnectionCalls() throws Exception {
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
  void final004AutoCommitFailsBeforeStatementCreation() throws Exception {
    var f = new Fixture();
    f.autoCommit = true;
    assertEquals(
        DIAGNOSTIC, assertThrows(SQLException.class, () -> finish(f, normal())).getMessage());
    assertEquals(0, f.creates);
    assertTrue(f.sql.isEmpty());
  }

  @Test
  void final005AutoCreateOriginalFailuresAndNullVendor() throws Exception {
    failuresAt("auto", 0, 1);
    failuresAt("create", 0, 1);
    var f = new Fixture();
    f.nullOuter = true;
    assertThrows(SQLException.class, () -> finish(f, normal()));
    assertEquals(0, f.outerCloses);
  }

  @Test
  void final006OuterTimeoutPreservesFailureAndCloses() throws Exception {
    failuresAt("outerTimeout", 0, 1);
  }

  @Test
  void final007EveryPreflightResultShapeIsStrict() throws Exception {
    shapes(0, IDENTITIES);
  }

  @Test
  void final008EveryPreflightQueryFailureIsOriginal() throws Exception {
    failuresAt("query", 0, IDENTITIES);
  }

  @Test
  void final009EveryReadPhaseOriginalFailure() throws Exception {
    for (var phase : List.of("next1", "getLong", "wasNull", "next2"))
      failuresAt(phase, 0, IDENTITIES);
  }

  @Test
  void final010PreflightResultCloseIsNotSuccess() throws Exception {
    failuresAt("resultClose", 0, IDENTITIES);
  }

  @Test
  void final011ReadPrimaryKeepsResultAndOuterSuppressedOrder() throws Exception {
    for (Throwable primary : failures()) {
      var f = new Fixture();
      f.failCall = "getLong";
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
    self.failCall = "getLong";
    self.failSlot = 0;
    self.extraResult = self.failure;
    self.faultQuery = 0;
    assertThrows(IllegalArgumentException.class, () -> finish(self, normal()));
    assertEquals(1, self.resultCloses);
    assertEquals(1, self.outerCloses);
  }

  @Test
  void final012LastMaxMismatchCannotIssueAnyMutation() throws Exception {
    var f = new Fixture();
    f.faultQuery = IDENTITIES - 1;
    f.shape = Shape.WRONG;
    assertThrows(SQLException.class, () -> finish(f, normal()));
    assertEquals(MAX_SQL, f.sql);
    assertEquals(0, f.prepares);
    assertEquals(0, f.analyzes);
  }

  @Test
  void final013EachPrepareNullOrOriginalFailureStopsFollowingCalls() throws Exception {
    failuresAt("prepare", 0, IDENTITIES);
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
  void final014EachLongBindingFailure() throws Exception {
    failuresAt("setLong", 0, IDENTITIES);
  }

  @Test
  void final015EachBooleanBindingFailure() throws Exception {
    failuresAt("setBoolean", 0, IDENTITIES);
  }

  @Test
  void final016EachPreparedTimeoutFailure() throws Exception {
    failuresAt("preparedTimeout", 0, IDENTITIES);
  }

  @Test
  void final017EverySetvalResultShapeIsStrict() throws Exception {
    shapes(IDENTITIES, IDENTITIES);
  }

  @Test
  void final018EveryPreparedQueryFailure() throws Exception {
    failuresAt("preparedQuery", 0, IDENTITIES);
  }

  @Test
  void final019EveryPreparedResultReadPhaseFailure() throws Exception {
    for (var phase : List.of("next1", "getLong", "wasNull", "next2"))
      failuresAt(phase, IDENTITIES, IDENTITIES);
  }

  @Test
  void final020EveryPreparedResultCloseFailure() throws Exception {
    failuresAt("resultClose", IDENTITIES, IDENTITIES);
  }

  @Test
  void final021PreparedResultPrimaryKeepsAllThreeCloseFailuresInOrder() throws Exception {
    for (Throwable primary : failures()) {
      var f = new Fixture();
      f.failCall = "getLong";
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
  void final022EachPreparedCloseFailureIsPropagated() throws Exception {
    failuresAt("preparedClose", 0, IDENTITIES);
  }

  @Test
  void final023OuterCloseFailureCannotBeSuccess() throws Exception {
    failuresAt("outerClose", 0, 1);
  }

  @Test
  void final024EachAnalyzeWrongCountWarningAndOriginalFailures() throws Exception {
    failuresAt("analyze", 0, TABLES);
    failuresAt("warnings", 0, TABLES);
    for (int slot = 0; slot < TABLES; slot++) {
      var wrong = new Fixture();
      wrong.badAnalyze = slot;
      assertThrows(SQLException.class, () -> finish(wrong, normal()));
      assertEquals(slot + 1, wrong.analyzes);
      assertEquals(slot, wrong.warningReads);
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
  void final025FreshSuccessAfterRejectedFixtureDoesNotReuseOwner() throws Exception {
    var rejected = new Fixture();
    rejected.faultQuery = 0;
    rejected.shape = Shape.WRONG;
    assertThrows(SQLException.class, () -> finish(rejected, normal()));
    var next = new Fixture();
    finish(next, normal());
    assertEquals(16, next.sql.size());
    assertEquals(0, rejected.prepares);
  }

  @Test
  void final026MaximumN12IsRetainedWithoutAddingOneOrReorderingRows() throws Exception {
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
  void final027DiagnosticsFixedAndNoFailureNormalized() throws Exception {
    assertEquals("MigrationMasterFinalizer[REDACTED]", new MigrationMasterFinalizer().toString());
    var f = new Fixture();
    f.faultQuery = 0;
    f.shape = Shape.SQL_NULL;
    assertEquals(
        DIAGNOSTIC, assertThrows(SQLException.class, () -> finish(f, normal())).getMessage());
  }

  @Test
  void final028FiniteReadersOwnIndependentProxiesAndTerminate() throws Exception {
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

  private static void finish(Fixture f, MigrationMasterCopyDataset declared) throws SQLException {
    new MigrationMasterFinalizer().finish(f.connection(), declared);
  }

  private static List<Throwable> failures() {
    return List.of(
        new SQLException("synthetic sql"),
        new IllegalStateException("synthetic runtime"),
        new AssertionError("synthetic error"));
  }

  private static void failuresAt(String call, int first, int count) throws Exception {
    var declared = normal();
    for (int slot = first; slot < first + count; slot++)
      for (Throwable failure : failures()) {
        var f = new Fixture();
        f.failCall = call;
        f.failSlot = slot;
        f.failure = failure;
        assertSame(failure, assertThrows(failure.getClass(), () -> finish(f, declared)));
        assertEquals(1, f.failureHits);
        assertTrue(f.outerCloses <= 1);
        assertTrue(f.preparedCloses <= IDENTITIES);
        assertTrue(f.resultCloses <= IDENTITIES * 2);
      }
  }

  private static void shapes(int first, int count) throws Exception {
    for (int slot = first; slot < first + count; slot++)
      for (var shape :
          List.of(Shape.NULL_RESULT, Shape.MISSING, Shape.SQL_NULL, Shape.WRONG, Shape.EXTRA)) {
        var f = new Fixture();
        f.faultQuery = slot;
        f.shape = shape;
        assertEquals(
            DIAGNOSTIC, assertThrows(SQLException.class, () -> finish(f, normal())).getMessage());
        assertEquals(0, f.analyzes);
        assertEquals(1, f.outerCloses);
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
                    hit("auto", 0);
                    return autoCommit;
                  case "createStatement":
                    creates++;
                    hit("create", 0);
                    return nullOuter ? null : statement();
                  case "prepareStatement":
                    int slot = prepares;
                    prepares++;
                    sql.add((String) args[0]);
                    assertEquals(SET_SQL.get(slot), args[0]);
                    hit("prepare", slot);
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
                    hit("outerTimeout", 0);
                    return null;
                  case "executeQuery":
                    int query = reads;
                    reads++;
                    sql.add((String) args[0]);
                    assertEquals(MAX_SQL.get(query), args[0]);
                    hit("query", query);
                    return result(query);
                  case "executeUpdate":
                    int position = analyzes;
                    analyzes++;
                    sql.add((String) args[0]);
                    assertEquals(ANALYZE_SQL.get(position), args[0]);
                    hit("analyze", position);
                    return badAnalyze == position ? 1 : 0;
                  case "getWarnings":
                    warningReads++;
                    int warning = analyzes - 1;
                    hit("warnings", warning);
                    return badWarning == warning ? new SQLWarning("synthetic skipped table") : null;
                  case "close":
                    outerCloses++;
                    hit("outerClose", 0);
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
                    hit("preparedTimeout", slot);
                    return null;
                  case "setLong":
                    assertEquals(1, args[0]);
                    hit("setLong", slot);
                    boundLong.add((Long) args[1]);
                    return null;
                  case "setBoolean":
                    assertEquals(2, args[0]);
                    hit("setBoolean", slot);
                    boundBoolean.add((Boolean) args[1]);
                    return null;
                  case "executeQuery":
                    hit("preparedQuery", slot);
                    return result(IDENTITIES + slot);
                  case "close":
                    preparedCloses++;
                    hit("preparedClose", slot);
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
                    hit(call == 0 ? "next1" : "next2", query);
                    return call == 0
                        ? !(selected && shape == Shape.MISSING)
                        : selected && shape == Shape.EXTRA;
                  case "getLong":
                    assertEquals(1, args[0]);
                    hit("getLong", query);
                    long value =
                        query < IDENTITIES
                            ? expected[query]
                            : Math.max(1, expected[query - IDENTITIES]);
                    return selected && shape == Shape.WRONG ? value + 1 : value;
                  case "wasNull":
                    hit("wasNull", query);
                    return selected && shape == Shape.SQL_NULL;
                  case "close":
                    resultCloses++;
                    hit("resultClose", query);
                    if (selected && extraResult != null) throw extraResult;
                    return null;
                  default:
                    throw new AssertionError("Unexpected ResultSet operation: " + method.getName());
                }
              });
    }
  }

  private static MigrationMasterCopyDataset normal() throws Exception {
    return new MigrationMasterCopyDataset(speakers(STAMP), content(STAMP));
  }

  private static MigrationCopyDataset content(String stamp) throws Exception {
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

  private static MediaAssetCopyBatch media(String stamp) throws Exception {
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
