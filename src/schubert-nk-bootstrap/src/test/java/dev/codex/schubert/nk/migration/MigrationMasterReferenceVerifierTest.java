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
import java.util.Arrays;
import java.util.List;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import org.jspecify.annotations.Nullable;
import org.junit.jupiter.api.Test;

/**
 * PT-MIG-REF001..021; independent DDL relationships, SQL literals and exact resource
 * postconditions.
 */
final class MigrationMasterReferenceVerifierTest {
  private static final String SHA =
      "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad";
  private static final String STAMP = "2026-01-02T03:04:05Z";
  private static final String ONE = "1";
  private static final String THREE = "3";
  private static final String SOURCE_VIDEO = "current/a.mp4";
  private static final String TARGET_VIDEO = "video/a.mp4";
  private static final String VIDEO = "VIDEO";
  private static final String SPEAKER_ID = "42";
  private static final String DIAGNOSTIC = "migration master reference verification is invalid";
  private static final String CALL_AUTO = "auto";
  private static final String CALL_CREATE = "create";
  private static final String CALL_TIMEOUT = "timeout";
  private static final String CALL_QUERY = "query";
  private static final String CALL_NEXT1 = "next1";
  private static final String CALL_GET_LONG = "getLong";
  private static final String CALL_WAS_NULL = "wasNull";
  private static final String CALL_NEXT2 = "next2";
  private static final String CALL_RESULT_CLOSE = "resultClose";
  private static final String CALL_OUTER_CLOSE = "outerClose";
  private static final int COUNT_QUERIES = 6;
  private static final int QUERIES = 28;
  private static final int WORKERS = 8;
  private static final int TASKS = 64;
  private static final int WAIT_SECONDS = 5;
  private static final int TERMINATION_SECONDS = 10;
  private static final List<String> QUERY_SQL =
      List.of(
          "SELECT count(*) FROM schubert.speakers",
          "SELECT count(*) FROM schubert.script_files",
          "SELECT count(*) FROM schubert.script_entries",
          "SELECT count(*) FROM schubert.audio_files",
          "SELECT count(*) FROM schubert.media_assets",
          "SELECT count(*) FROM schubert.entry_audio_links",
          "SELECT count(*) FROM schubert.script_files c LEFT JOIN schubert.games p ON p.id=c.game_id WHERE p.id IS NULL",
          "SELECT count(*) FROM schubert.speakers c LEFT JOIN schubert.games p ON p.id=c.game_id WHERE p.id IS NULL",
          "SELECT count(*) FROM schubert.script_entries c LEFT JOIN schubert.games p ON p.id=c.game_id WHERE p.id IS NULL",
          "SELECT count(*) FROM schubert.audio_files c LEFT JOIN schubert.games p ON p.id=c.game_id WHERE p.id IS NULL",
          "SELECT count(*) FROM schubert.script_entries c LEFT JOIN schubert.script_files p ON p.id=c.script_file_id AND p.game_id=c.game_id WHERE p.id IS NULL",
          "SELECT count(*) FROM schubert.script_entries c LEFT JOIN schubert.speakers p ON p.id=c.speaker_id AND p.game_id=c.game_id WHERE c.speaker_id IS NOT NULL AND p.id IS NULL",
          "SELECT count(*) FROM schubert.entry_audio_links c LEFT JOIN schubert.script_entries p ON p.id=c.entry_id AND p.game_id=c.game_id WHERE p.id IS NULL",
          "SELECT count(*) FROM schubert.entry_audio_links c LEFT JOIN schubert.audio_files p ON p.id=c.audio_file_id AND p.game_id=c.game_id WHERE p.id IS NULL",
          "SELECT count(*) FROM schubert.media_assets c LEFT JOIN schubert.media_assets p ON p.logical_id=c.parent_logical_id WHERE c.parent_logical_id IS NOT NULL AND p.logical_id IS NULL",
          "SELECT count(*) FROM (SELECT entry_id,link_type FROM schubert.entry_audio_links GROUP BY entry_id,link_type HAVING count(*)>999 OR min(display_order)<1 OR max(display_order)>999 OR count(DISTINCT display_order)<>count(*)) violations",
          "SELECT count(*) FROM schubert.speakers WHERE ((id BETWEEN 1 AND 999999999999) AND (octet_length(name) BETWEEN 1 AND 128) AND (octet_length(normalized_name) BETWEEN 1 AND 128)) IS FALSE",
          "SELECT count(*) FROM schubert.script_files WHERE ((byte_size BETWEEN 0 AND 999999999999) AND (\n        chapter_title IS NULL OR octet_length(chapter_title) <= 256) AND (display_order BETWEEN 1 AND 999999999999) AND (octet_length(display_path) BETWEEN 1 AND 512) AND (octet_length(file_name) BETWEEN 1 AND 256) AND (id BETWEEN 1 AND 999999999999) AND (sha256 ~ '^[0-9a-f]{64}$') AND (octet_length(storage_relative_path) BETWEEN 1 AND 512) AND (\n        storage_relative_path !~ '(^/|\\\\|(^|/)\\.\\.?(/|$)|//)')) IS FALSE",
          "SELECT count(*) FROM schubert.script_entries WHERE ((octet_length(body) BETWEEN 1 AND 4096) AND (display_order BETWEEN 1 AND 999999999999) AND (entry_index >= 0) AND (entry_type IN ('dialogue', 'narration')) AND (id BETWEEN 1 AND 999999999999) AND (line_number IS NULL OR line_number >= 1) AND (\n        (entry_type = 'dialogue' AND speaker_id IS NOT NULL)\n        OR (entry_type = 'narration' AND speaker_id IS NULL)) AND (\n        speaker_label IS NULL OR octet_length(speaker_label) <= 128)) IS FALSE",
          "SELECT count(*) FROM schubert.audio_files WHERE ((octet_length(audio_role) BETWEEN 1 AND 8) AND (octet_length(basename) BETWEEN 1 AND 255) AND (byte_size BETWEEN 1 AND 999999999999) AND (octet_length(display_path) BETWEEN 1 AND 512) AND (duration_ms IS NULL OR duration_ms BETWEEN 0 AND 999999999999) AND (octet_length(file_name) BETWEEN 1 AND 256) AND (id BETWEEN 1 AND 999999999999) AND (sha256 ~ '^[0-9a-f]{64}$') AND (octet_length(storage_relative_path) BETWEEN 1 AND 512) AND (\n        storage_relative_path !~ '(^/|\\\\|(^|/)\\.\\.?(/|$)|//)')) IS FALSE",
          "SELECT count(*) FROM schubert.media_assets WHERE ((byte_size BETWEEN 1 AND 999999999999) AND (octet_length(category) BETWEEN 1 AND 64) AND (display_order BETWEEN 1 AND 9999) AND (octet_length(display_path) BETWEEN 1 AND 512) AND (octet_length(file_name) BETWEEN 1 AND 256) AND (id BETWEEN 1 AND 999999999999) AND (octet_length(logical_id) BETWEEN 1 AND 64) AND (media_type IN ('VIDEO', 'MUSIC')) AND (\n        mime_type IN ('video/mp4', 'audio/mp4', 'audio/mpeg', 'audio/ogg', 'audio/wav', 'audio/flac')) AND ((\n        (media_type = 'VIDEO' AND pair_key IS NULL AND pair_role IS NULL)\n        OR (media_type = 'MUSIC' AND (\n            (pair_role IN ('M', 'I') AND octet_length(pair_key) BETWEEN 1 AND 256)\n            OR (pair_role = 'N' AND pair_key IS NULL)))\n    ) IS TRUE) AND (section IS NULL OR octet_length(section) <= 128) AND (sha256 ~ '^[0-9a-f]{64}$') AND (octet_length(storage_relative_path) BETWEEN 1 AND 512) AND (\n        storage_relative_path !~ '(^/|\\\\|(^|/)\\.\\.?(/|$)|//)') AND (octet_length(title) BETWEEN 1 AND 256)) IS FALSE",
          "SELECT count(*) FROM schubert.entry_audio_links WHERE ((display_order BETWEEN 1 AND 999) AND (link_type IN ('voice', 'se', 'bgm', 'other'))) IS FALSE",
          "SELECT count(*) FROM (SELECT 1 FROM schubert.speakers GROUP BY id HAVING count(*)>1 OR (id IS NULL) UNION ALL SELECT 1 FROM schubert.speakers WHERE game_id IS NOT NULL AND normalized_name IS NOT NULL GROUP BY game_id,normalized_name HAVING count(*)>1 UNION ALL SELECT 1 FROM schubert.speakers WHERE id IS NOT NULL AND game_id IS NOT NULL GROUP BY id,game_id HAVING count(*)>1) violations",
          "SELECT count(*) FROM (SELECT 1 FROM schubert.script_files GROUP BY id HAVING count(*)>1 OR (id IS NULL) UNION ALL SELECT 1 FROM schubert.script_files WHERE game_id IS NOT NULL AND display_order IS NOT NULL GROUP BY game_id,display_order HAVING count(*)>1 UNION ALL SELECT 1 FROM schubert.script_files WHERE game_id IS NOT NULL AND storage_relative_path IS NOT NULL GROUP BY game_id,storage_relative_path HAVING count(*)>1 UNION ALL SELECT 1 FROM schubert.script_files WHERE id IS NOT NULL AND game_id IS NOT NULL GROUP BY id,game_id HAVING count(*)>1) violations",
          "SELECT count(*) FROM (SELECT 1 FROM schubert.script_entries GROUP BY id HAVING count(*)>1 OR (id IS NULL) UNION ALL SELECT 1 FROM schubert.script_entries WHERE display_order IS NOT NULL GROUP BY display_order HAVING count(*)>1 UNION ALL SELECT 1 FROM schubert.script_entries WHERE script_file_id IS NOT NULL AND entry_index IS NOT NULL GROUP BY script_file_id,entry_index HAVING count(*)>1 UNION ALL SELECT 1 FROM schubert.script_entries WHERE id IS NOT NULL AND game_id IS NOT NULL GROUP BY id,game_id HAVING count(*)>1) violations",
          "SELECT count(*) FROM (SELECT 1 FROM schubert.audio_files GROUP BY id HAVING count(*)>1 OR (id IS NULL) UNION ALL SELECT 1 FROM schubert.audio_files WHERE game_id IS NOT NULL AND storage_relative_path IS NOT NULL GROUP BY game_id,storage_relative_path HAVING count(*)>1 UNION ALL SELECT 1 FROM schubert.audio_files WHERE id IS NOT NULL AND game_id IS NOT NULL GROUP BY id,game_id HAVING count(*)>1) violations",
          "SELECT count(*) FROM (SELECT 1 FROM schubert.media_assets GROUP BY id HAVING count(*)>1 OR (id IS NULL) UNION ALL SELECT 1 FROM schubert.media_assets WHERE logical_id IS NOT NULL GROUP BY logical_id HAVING count(*)>1 UNION ALL SELECT 1 FROM schubert.media_assets WHERE media_type IS NOT NULL AND storage_relative_path IS NOT NULL GROUP BY media_type,storage_relative_path HAVING count(*)>1) violations",
          "SELECT count(*) FROM (SELECT 1 FROM schubert.entry_audio_links GROUP BY entry_id,audio_file_id,link_type HAVING count(*)>1 OR (entry_id IS NULL OR audio_file_id IS NULL OR link_type IS NULL) UNION ALL SELECT 1 FROM schubert.entry_audio_links WHERE entry_id IS NOT NULL AND link_type IS NOT NULL AND display_order IS NOT NULL GROUP BY entry_id,link_type,display_order HAVING count(*)>1) violations");

  @Test
  void reference001ExactSixCountsNineForeignKeysAndOrderQuery() throws Exception {
    var f = new Fixture();
    verify(f, normal());
    assertEquals(QUERY_SQL, f.sql);
    assertEquals(List.of(30), f.timeouts);
    assertEquals(QUERIES, f.resultCloses);
    assertEquals(1, f.outerCloses);
    assertEquals(1, f.creates);
  }

  @Test
  void reference002EmptyStillChecksAllSixTablesAndAllReferences() throws Exception {
    var f = new Fixture();
    f.expected = new long[QUERIES];
    verify(f, new MigrationMasterCopyDataset(new SpeakerCopyBatch(List.of()), emptyContent()));
    assertEquals(QUERY_SQL, f.sql);
    assertEquals(QUERIES, f.resultCloses);
  }

  @Test
  void reference003BothNullArgumentsFailBeforeConnectionCalls() throws Exception {
    var f = new Fixture();
    var conn = f.connection();
    var declared = normal();
    String expected = "migration master reference input is invalid";
    assertEquals(
        expected,
        assertThrows(
                IllegalArgumentException.class,
                () -> new MigrationMasterReferenceVerifier().verify(null, declared))
            .getMessage());
    assertEquals(
        expected,
        assertThrows(
                IllegalArgumentException.class,
                () -> new MigrationMasterReferenceVerifier().verify(conn, null))
            .getMessage());
    assertEquals(
        expected,
        assertThrows(
                IllegalArgumentException.class,
                () -> new MigrationMasterReferenceVerifier().verify(null, null))
            .getMessage());
    assertEquals(0, f.autoReads);
    assertTrue(f.sql.isEmpty());
  }

  @Test
  void reference004AutoCommitHasNoStatementOrQuery() throws Exception {
    var f = new Fixture();
    f.autoCommit = true;
    assertEquals(
        DIAGNOSTIC, assertThrows(SQLException.class, () -> verify(f, normal())).getMessage());
    assertEquals(0, f.creates);
    assertEquals(0, f.outerCloses);
    assertTrue(f.sql.isEmpty());
  }

  @Test
  void reference005AutoAndCreateFailuresPreserveEveryOriginalType() throws Exception {
    failuresAt(CALL_AUTO, 0, 1);
    failuresAt(CALL_CREATE, 0, 1);
  }

  @Test
  void reference006NullVendorStatementCannotBecomeNpe() throws Exception {
    var f = new Fixture();
    f.nullOuter = true;
    assertEquals(
        DIAGNOSTIC, assertThrows(SQLException.class, () -> verify(f, normal())).getMessage());
    assertEquals(0, f.outerCloses);
    assertTrue(f.sql.isEmpty());
  }

  @Test
  void reference007TimeoutFailureClosesOwnedStatement() throws Exception {
    failuresAt(CALL_TIMEOUT, 0, 1);
  }

  @Test
  void reference008EveryScalarRejectsNullMissingSqlNullWrongAndExtra() throws Exception {
    for (int slot = 0; slot < QUERIES; slot++)
      for (var shape :
          List.of(Shape.NULL_RESULT, Shape.MISSING, Shape.SQL_NULL, Shape.WRONG, Shape.EXTRA)) {
        var f = new Fixture();
        f.faultQuery = slot;
        f.shape = shape;
        assertEquals(
            DIAGNOSTIC, assertThrows(SQLException.class, () -> verify(f, normal())).getMessage());
        assertEquals(QUERY_SQL.subList(0, slot + 1), f.sql);
        assertEquals(slot + (shape == Shape.NULL_RESULT ? 0 : 1), f.resultCloses);
        assertEquals(1, f.outerCloses);
      }
  }

  @Test
  void reference009EveryQueryFailureStopsAtTheOriginalFailure() throws Exception {
    failuresAt(CALL_QUERY, 0, QUERIES);
  }

  @Test
  void reference010EveryScalarReadPhasePreservesOriginalFailure() throws Exception {
    for (var call : List.of(CALL_NEXT1, CALL_GET_LONG, CALL_WAS_NULL, CALL_NEXT2))
      failuresAt(call, 0, QUERIES);
  }

  @Test
  void reference011EveryResultCloseFailureCannotBeSuccess() throws Exception {
    failuresAt(CALL_RESULT_CLOSE, 0, QUERIES);
  }

  @Test
  void reference012OriginalPrimaryKeepsInnerOuterCloseOrderAndSelfSuppression() throws Exception {
    for (Throwable primary : failures()) {
      var f = new Fixture();
      f.failCall = CALL_GET_LONG;
      f.failSlot = 0;
      f.failure = primary;
      f.faultQuery = 0;
      var inner = new SQLException("synthetic inner close");
      var outer = new AssertionError("synthetic outer close");
      f.extraResult = inner;
      f.extraOuter = outer;
      assertSame(primary, assertThrows(primary.getClass(), () -> verify(f, normal())));
      assertEquals(List.of(inner, outer), List.of(primary.getSuppressed()));
      assertEquals(1, f.resultCloses);
      assertEquals(1, f.outerCloses);
    }
    var self = new Fixture();
    self.failCall = CALL_GET_LONG;
    self.failSlot = 0;
    self.faultQuery = 0;
    self.extraResult = self.failure;
    assertSame(self.failure, assertThrows(SQLException.class, () -> verify(self, normal())));
    assertEquals(0, self.failure.getSuppressed().length);
    assertEquals(1, self.resultCloses);
    assertEquals(1, self.outerCloses);
  }

  @Test
  void reference013StatementCloseFailureIsNotNormalCompletion() throws Exception {
    failuresAt(CALL_OUTER_CLOSE, 0, 1);
  }

  @Test
  void reference014EachOrphanOrOrderNonzeroRejectsWithNoLaterQuery() throws Exception {
    for (int slot = COUNT_QUERIES; slot < QUERIES; slot++)
      for (long delta : List.of(-1L, 1L, Long.MAX_VALUE)) {
        var f = new Fixture();
        f.faultQuery = slot;
        f.shape = Shape.WRONG;
        f.delta = delta;
        assertThrows(SQLException.class, () -> verify(f, normal()));
        assertEquals(slot + 1, f.resultCloses);
        assertEquals(QUERY_SQL.subList(0, slot + 1), f.sql);
        assertEquals(1, f.outerCloses);
      }
  }

  @Test
  void reference015EachDeclaredCountMismatchRejectsBeforeReferenceChecks() throws Exception {
    for (int slot = 0; slot < COUNT_QUERIES; slot++)
      for (long delta : List.of(-2L, 1L, Long.MAX_VALUE)) {
        var f = new Fixture();
        f.faultQuery = slot;
        f.shape = Shape.WRONG;
        f.delta = delta;
        assertThrows(SQLException.class, () -> verify(f, normal()));
        assertEquals(QUERY_SQL.subList(0, slot + 1), f.sql);
        assertEquals(slot + 1, f.resultCloses);
      }
  }

  @Test
  void reference016OnlyReadOnlyBorrowedCallsAndExactResourcesExist() throws Exception {
    var f = new Fixture();
    verify(f, normal());
    assertEquals(1, f.autoReads);
    assertEquals(1, f.creates);
    assertEquals(QUERIES, f.resultCloses);
    assertEquals(1, f.outerCloses);
    assertEquals(QUERY_SQL, f.sql);
    // All unlisted Connection/Statement/ResultSet calls throw; phase matrices assert exact counts.
  }

  @Test
  void reference017DiagnosticsAndToStringRemainFixedRedacted() throws Exception {
    assertEquals(
        "MigrationMasterReferenceVerifier[REDACTED]",
        new MigrationMasterReferenceVerifier().toString());
    var f = new Fixture();
    f.shape = Shape.SQL_NULL;
    f.faultQuery = 0;
    assertEquals(
        DIAGNOSTIC, assertThrows(SQLException.class, () -> verify(f, normal())).getMessage());
  }

  @Test
  void reference018IndependentFreshSuccessAfterFailedPriorQuery() throws Exception {
    var failed = new Fixture();
    failed.shape = Shape.EXTRA;
    failed.faultQuery = 0;
    assertThrows(SQLException.class, () -> verify(failed, normal()));
    var next = new Fixture();
    verify(next, normal());
    assertEquals(QUERY_SQL, next.sql);
    assertEquals(1, failed.sql.size());
  }

  @Test
  void reference019EachCountUsesItsOwnDeclaredTableWithoutInventingRows() throws Exception {
    var source = normal();
    var content = source.content();
    var speakerRows = new ArrayList<>(source.speakers().rows());
    speakerRows.add(
        new SpeakerCopyRow(
            Arrays.<@Nullable String>asList("999", ONE, "Other", "other", "false", null, STAMP)));
    counts(
        new MigrationMasterCopyDataset(new SpeakerCopyBatch(speakerRows), content),
        new long[] {2, 1, 1, 1, 1, 1});
    counts(
        new MigrationMasterCopyDataset(
            source.speakers(),
            new MigrationCopyDataset(
                content.scenario(), content.audio().audioRows(), List.of(), content.media())),
        new long[] {1, 1, 1, 1, 1, 0});
    counts(
        new MigrationMasterCopyDataset(
            source.speakers(),
            new MigrationCopyDataset(content.scenario(), List.of(), List.of(), content.media())),
        new long[] {1, 1, 1, 0, 1, 0});
    counts(
        new MigrationMasterCopyDataset(
            source.speakers(),
            new MigrationCopyDataset(
                content.scenario(),
                content.audio().audioRows(),
                content.audio().linkRows(),
                emptyMedia())),
        new long[] {1, 1, 1, 1, 0, 1});
    counts(
        new MigrationMasterCopyDataset(
            source.speakers(),
            new MigrationCopyDataset(
                scenario(false, null, ONE, STAMP),
                content.audio().audioRows(),
                List.of(),
                content.media())),
        new long[] {1, 1, 0, 1, 1, 0});
    counts(
        new MigrationMasterCopyDataset(
            source.speakers(),
            new MigrationCopyDataset(
                emptyScenario(), content.audio().audioRows(), List.of(), content.media())),
        new long[] {1, 0, 0, 1, 1, 0});
  }

  @Test
  void reference020FiniteWorkersHaveIndependentSqlResultsAndTerminate() throws Exception {
    var declared = normal();
    var executor = Executors.newFixedThreadPool(WORKERS);
    try {
      var futures = new ArrayList<Future<Integer>>();
      for (int index = 0; index < TASKS; index++)
        futures.add(
            executor.submit(
                () -> {
                  var f = new Fixture();
                  verify(f, declared);
                  assertEquals(1, f.outerCloses);
                  return f.resultCloses;
                }));
      for (var future : futures) assertEquals(QUERIES, future.get(WAIT_SECONDS, TimeUnit.SECONDS));
    } finally {
      executor.shutdownNow();
      assertTrue(executor.awaitTermination(TERMINATION_SECONDS, TimeUnit.SECONDS));
    }
  }

  @Test
  void reference021EmptyDeclaredRowsCannotHideAnyCheckViolationOrUnknownCount() throws Exception {
    var declared = new MigrationMasterCopyDataset(new SpeakerCopyBatch(List.of()), emptyContent());
    for (int slot = 16; slot < QUERIES; slot++) {
      for (var shape :
          List.of(Shape.NULL_RESULT, Shape.MISSING, Shape.SQL_NULL, Shape.WRONG, Shape.EXTRA)) {
        var f = new Fixture();
        f.expected = new long[QUERIES];
        f.faultQuery = slot;
        f.shape = shape;
        f.delta = 1;
        assertThrows(SQLException.class, () -> verify(f, declared));
        assertEquals(QUERY_SQL.subList(0, slot + 1), f.sql);
        assertEquals(slot + (shape == Shape.NULL_RESULT ? 0 : 1), f.resultCloses);
        assertEquals(1, f.outerCloses);
      }
      for (long count : List.of(-1L, Long.MAX_VALUE)) {
        var f = new Fixture();
        f.expected = new long[QUERIES];
        f.faultQuery = slot;
        f.shape = Shape.WRONG;
        f.delta = count;
        assertThrows(SQLException.class, () -> verify(f, declared));
        assertEquals(QUERY_SQL.subList(0, slot + 1), f.sql);
        assertEquals(slot + 1, f.resultCloses);
        assertEquals(1, f.outerCloses);
      }
    }
    var zero = new Fixture();
    zero.expected = new long[QUERIES];
    verify(zero, declared);
    assertEquals(QUERY_SQL, zero.sql);
    assertEquals(QUERIES, zero.resultCloses);
    assertEquals(1, zero.outerCloses);
  }

  private static void counts(MigrationMasterCopyDataset declared, long[] six) throws SQLException {
    var f = new Fixture();
    f.expected = Arrays.copyOf(six, QUERIES);
    verify(f, declared);
    assertEquals(QUERY_SQL, f.sql);
    assertEquals(QUERIES, f.resultCloses);
  }

  private static void verify(Fixture f, MigrationMasterCopyDataset declared) throws SQLException {
    new MigrationMasterReferenceVerifier().verify(f.connection(), declared);
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
        assertSame(failure, assertThrows(failure.getClass(), () -> verify(f, declared)));
        assertEquals(1, f.failureHits);
        var expected =
            switch (call) {
              case CALL_AUTO, CALL_CREATE -> List.of(0, 0);
              case CALL_TIMEOUT -> List.of(0, 1);
              case CALL_QUERY -> List.of(slot, 1);
              case CALL_OUTER_CLOSE -> List.of(QUERIES, 1);
              default -> List.of(slot + 1, 1);
            };
        assertEquals(expected, List.of(f.resultCloses, f.outerCloses));
        if (call.equals(CALL_QUERY)
            || List.of(CALL_NEXT1, CALL_GET_LONG, CALL_WAS_NULL, CALL_NEXT2, CALL_RESULT_CLOSE)
                .contains(call)) assertEquals(QUERY_SQL.subList(0, slot + 1), f.sql);
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
    private long[] expected = {
      1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
    };
    private final List<String> sql = new ArrayList<>();
    private final List<Integer> timeouts = new ArrayList<>();
    private boolean autoCommit;
    private boolean nullOuter;
    private int faultQuery = -1;
    private Shape shape = Shape.NONE;
    private long delta = 1;
    private String failCall = "";
    private int failSlot = -1;
    private Throwable failure = new SQLException("synthetic failure");
    private @Nullable Throwable extraResult;
    private @Nullable Throwable extraOuter;
    private int autoReads;
    private int creates;
    private int reads;
    private int resultCloses;
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
                    hit(CALL_TIMEOUT, 0);
                    return null;
                  case "executeQuery":
                    int query = reads;
                    reads++;
                    sql.add((String) args[0]);
                    assertEquals(QUERY_SQL.get(query), args[0]);
                    hit(CALL_QUERY, query);
                    return result(query);
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
                    return selected && shape == Shape.WRONG
                        ? expected[query] + delta
                        : expected[query];
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
