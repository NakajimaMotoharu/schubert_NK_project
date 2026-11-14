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
import java.sql.Timestamp;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.stream.IntStream;
import org.jspecify.annotations.Nullable;
import org.junit.jupiter.api.Test;

/**
 * PT-MIG-TARGET001..024; independent 68 SQL/44 scalar plus six typed result vectors, memory-only
 * borrowed JDBC.
 */
final class MigrationMasterTargetPublisherTest {
  private static final String TRUE_TEXT = "true";
  private static final String FILE_ID_TEXT = "700";
  private static final String FILE_NAME_TEXT = "file.txt";
  private static final String ENTRY_ID_TEXT = "900";
  private static final String AUDIO_ID_TEXT = "500";
  private static final String VOICE_TEXT = "voice";
  private static final String CLOSE_METHOD = "close";
  private static final String SHA =
      "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad";
  private static final String STAMP = "2026-01-02T03:04:05Z";
  private static final String ONE = "1";
  private static final String THREE = "3";
  private static final String SOURCE_VIDEO = "current/a.mp4";
  private static final String TARGET_VIDEO = "video/a.mp4";
  private static final String VIDEO = "VIDEO";
  private static final String SPEAKER_ID = "42";
  private static final int PREPARE_END = 6;
  private static final int TRANSFER_END = 30;
  private static final int REFERENCE_END = 46;
  private static final int CONTENT_END = 52;
  private static final int CONTENT_TABLES = 6;
  private static final int CONTENT_COLUMNS = 65;
  private static final int RESULTS = 50;
  private static final int CLOSES = 14;
  private static final int CONTENT_CLOSE = 7;
  private static final String GET_LONG = "getLong";
  private static final String GET_INT = "getInt";
  private static final String GET_BOOLEAN = "getBoolean";
  private static final String GET_TIMESTAMP = "getTimestamp";
  private static final String GET_STRING = "getString";
  private static final int SETVAL_FIRST = 57;
  private static final int ANALYZE_FIRST = 62;
  private static final int SQL_COUNT = 68;
  private static final int SCALARS = 44;
  private static final int TRANSFER_SCALARS = 18;
  private static final int ORPHAN_FIRST = 24;
  private static final int REFERENCE_SCALARS_END = 34;
  private static final int SETVAL_SCALAR_FIRST = 39;
  private static final int PREPARED_FIRST_CLOSE = 8;
  private static final int OUTER_FINAL_CLOSE = 13;
  private static final int WORKERS = 8;
  private static final int TASKS = 64;
  private static final int WAIT_SECONDS = 5;
  private static final int TERMINATION_SECONDS = 10;
  private static final List<Integer> OWNER_START = List.of(0, 1, 3, 6, 10, 18, 30, 46, 52);
  private static final List<Integer> CLOSE_SQL_PREFIX =
      List.of(1, 3, 6, 10, 18, 30, 46, 52, 58, 59, 60, 61, 62, 68);
  private static final List<Integer> CLOSE_RESULTS =
      List.of(0, 0, 0, 3, 9, 18, 34, 40, 46, 47, 48, 49, 50, 50);
  private static final List<String> CONTENT_SQL =
      List.of(
          "SELECT id,game_id,name,normalized_name,is_protagonist,notes,created_at FROM schubert.speakers ORDER BY id",
          "SELECT id,game_id,display_order,storage_relative_path,display_path,file_name,section_code,chapter_title,sha256,byte_size,created_at FROM schubert.script_files ORDER BY id",
          "SELECT id,game_id,script_file_id,display_order,entry_index,line_number,entry_type,speaker_id,speaker_label,body,raw_block,created_at FROM schubert.script_entries ORDER BY id",
          "SELECT id,game_id,storage_relative_path,display_path,file_name,basename,audio_role,container,duration_ms,byte_size,sha256,created_at FROM schubert.audio_files ORDER BY id",
          "SELECT id,logical_id,media_type,title,category,section,storage_relative_path,display_path,file_name,byte_size,sha256,mime_type,parent_logical_id,pair_key,pair_role,display_order,created_at FROM schubert.media_assets ORDER BY id",
          "SELECT entry_id,audio_file_id,game_id,link_type,display_order,created_at FROM schubert.entry_audio_links ORDER BY entry_id,audio_file_id,link_type COLLATE \"C\"");
  private static final List<String> CONTENT_TYPES =
      List.of(
          "LISSBST", "LILSSSSSSLT", "LILLIISLSSST", "LISSSSSSLLST", "LSSSSSSSSLSSSSSIT", "LLISIT");
  private static final List<String> SQL =
      List.of(
          "CREATE TEMP TABLE nk_mig_speakers ON COMMIT DROP AS SELECT id, game_id, name, normalized_name, is_protagonist, notes, created_at FROM schubert.speakers WITH NO DATA",
          "CREATE TEMP TABLE nk_mig_script_files ON COMMIT DROP AS SELECT id, game_id, display_order, storage_relative_path, display_path, file_name, section_code, chapter_title, sha256, byte_size, created_at FROM schubert.script_files WITH NO DATA",
          "CREATE TEMP TABLE nk_mig_script_entries ON COMMIT DROP AS SELECT id, game_id, script_file_id, display_order, entry_index, line_number, entry_type, speaker_id, speaker_label, body, raw_block, created_at FROM schubert.script_entries WITH NO DATA",
          "CREATE TEMP TABLE nk_mig_audio_files ON COMMIT DROP AS SELECT id, game_id, storage_relative_path, display_path, file_name, basename, audio_role, container, duration_ms, byte_size, sha256, created_at FROM schubert.audio_files WITH NO DATA",
          "CREATE TEMP TABLE nk_mig_media_assets ON COMMIT DROP AS SELECT id, logical_id, media_type, title, category, section, storage_relative_path, display_path, file_name, byte_size, sha256, mime_type, parent_logical_id, pair_key, pair_role, display_order, created_at FROM schubert.media_assets WITH NO DATA",
          "CREATE TEMP TABLE nk_mig_entry_audio_links ON COMMIT DROP AS SELECT entry_id, audio_file_id, game_id, link_type, display_order, created_at FROM schubert.entry_audio_links WITH NO DATA",
          "SELECT count(*) FROM schubert.speakers",
          "SELECT count(*) FROM pg_temp.nk_mig_speakers",
          "INSERT INTO schubert.speakers (id, game_id, name, normalized_name, is_protagonist, notes, created_at) SELECT id, game_id, name, normalized_name, is_protagonist, notes, created_at FROM pg_temp.nk_mig_speakers ORDER BY id",
          "SELECT count(*) FROM schubert.speakers",
          "SELECT count(*) FROM schubert.script_files",
          "SELECT count(*) FROM schubert.script_entries",
          "SELECT count(*) FROM pg_temp.nk_mig_script_files",
          "SELECT count(*) FROM pg_temp.nk_mig_script_entries",
          "INSERT INTO schubert.script_files (id, game_id, display_order, storage_relative_path, display_path, file_name, section_code, chapter_title, sha256, byte_size, created_at) SELECT id, game_id, display_order, storage_relative_path, display_path, file_name, section_code, chapter_title, sha256, byte_size, created_at FROM pg_temp.nk_mig_script_files ORDER BY game_id, display_order",
          "INSERT INTO schubert.script_entries (id, game_id, script_file_id, display_order, entry_index, line_number, entry_type, speaker_id, speaker_label, body, raw_block, created_at) SELECT id, game_id, script_file_id, display_order, entry_index, line_number, entry_type, speaker_id, speaker_label, body, raw_block, created_at FROM pg_temp.nk_mig_script_entries ORDER BY display_order",
          "SELECT count(*) FROM schubert.script_files",
          "SELECT count(*) FROM schubert.script_entries",
          "SELECT count(*) FROM schubert.audio_files",
          "SELECT count(*) FROM schubert.media_assets",
          "SELECT count(*) FROM schubert.entry_audio_links",
          "SELECT count(*) FROM pg_temp.nk_mig_audio_files",
          "SELECT count(*) FROM pg_temp.nk_mig_media_assets",
          "SELECT count(*) FROM pg_temp.nk_mig_entry_audio_links",
          "INSERT INTO schubert.audio_files (id, game_id, storage_relative_path, display_path, file_name, basename, audio_role, container, duration_ms, byte_size, sha256, created_at) SELECT id, game_id, storage_relative_path, display_path, file_name, basename, audio_role, container, duration_ms, byte_size, sha256, created_at FROM pg_temp.nk_mig_audio_files ORDER BY id",
          "INSERT INTO schubert.media_assets (id, logical_id, media_type, title, category, section, storage_relative_path, display_path, file_name, byte_size, sha256, mime_type, parent_logical_id, pair_key, pair_role, display_order, created_at) SELECT id, logical_id, media_type, title, category, section, storage_relative_path, display_path, file_name, byte_size, sha256, mime_type, parent_logical_id, pair_key, pair_role, display_order, created_at FROM pg_temp.nk_mig_media_assets ORDER BY id",
          "INSERT INTO schubert.entry_audio_links (entry_id, audio_file_id, game_id, link_type, display_order, created_at) SELECT entry_id, audio_file_id, game_id, link_type, display_order, created_at FROM pg_temp.nk_mig_entry_audio_links ORDER BY entry_id, link_type, display_order, audio_file_id",
          "SELECT count(*) FROM schubert.audio_files",
          "SELECT count(*) FROM schubert.media_assets",
          "SELECT count(*) FROM schubert.entry_audio_links",
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
          "SELECT id,game_id,name,normalized_name,is_protagonist,notes,created_at FROM schubert.speakers ORDER BY id",
          "SELECT id,game_id,display_order,storage_relative_path,display_path,file_name,section_code,chapter_title,sha256,byte_size,created_at FROM schubert.script_files ORDER BY id",
          "SELECT id,game_id,script_file_id,display_order,entry_index,line_number,entry_type,speaker_id,speaker_label,body,raw_block,created_at FROM schubert.script_entries ORDER BY id",
          "SELECT id,game_id,storage_relative_path,display_path,file_name,basename,audio_role,container,duration_ms,byte_size,sha256,created_at FROM schubert.audio_files ORDER BY id",
          "SELECT id,logical_id,media_type,title,category,section,storage_relative_path,display_path,file_name,byte_size,sha256,mime_type,parent_logical_id,pair_key,pair_role,display_order,created_at FROM schubert.media_assets ORDER BY id",
          "SELECT entry_id,audio_file_id,game_id,link_type,display_order,created_at FROM schubert.entry_audio_links ORDER BY entry_id,audio_file_id,link_type COLLATE \"C\"",
          "SELECT COALESCE(MAX(id),0) FROM schubert.speakers",
          "SELECT COALESCE(MAX(id),0) FROM schubert.script_files",
          "SELECT COALESCE(MAX(id),0) FROM schubert.script_entries",
          "SELECT COALESCE(MAX(id),0) FROM schubert.audio_files",
          "SELECT COALESCE(MAX(id),0) FROM schubert.media_assets",
          "SELECT pg_catalog.setval(pg_catalog.pg_get_serial_sequence('schubert.speakers', 'id'), ?, ?)",
          "SELECT pg_catalog.setval(pg_catalog.pg_get_serial_sequence('schubert.script_files', 'id'), ?, ?)",
          "SELECT pg_catalog.setval(pg_catalog.pg_get_serial_sequence('schubert.script_entries', 'id'), ?, ?)",
          "SELECT pg_catalog.setval(pg_catalog.pg_get_serial_sequence('schubert.audio_files', 'id'), ?, ?)",
          "SELECT pg_catalog.setval(pg_catalog.pg_get_serial_sequence('schubert.media_assets', 'id'), ?, ?)",
          "ANALYZE schubert.speakers",
          "ANALYZE schubert.script_files",
          "ANALYZE schubert.script_entries",
          "ANALYZE schubert.audio_files",
          "ANALYZE schubert.media_assets",
          "ANALYZE schubert.entry_audio_links");
  private static final long[] NORMAL_SCALARS = {
    0L, 1L, 1L, 0L, 0L, 1L, 1L, 1L, 1L, 0L, 0L, 0L, 1L, 1L, 1L, 1L, 1L, 1L, 1L, 1L, 1L, 1L, 1L, 1L,
    0L, 0L, 0L, 0L, 0L, 0L, 0L, 0L, 0L, 0L, 42L, 700L, 900L, 500L, 600L, 42L, 700L, 900L, 500L, 600L
  };

  @Test
  void target001OneConnectionFixedSixtyEightSqlAndExactResources() throws Exception {
    var f = new Fixture();
    workflow(new MigrationMasterTargetPublisher(), f, normal());
    assertEquals(SQL, f.sql);
    assertEquals(RESULTS, f.resultCloses);
    assertEquals(CLOSES, f.closeAttempts);
    assertEquals(9, f.autoReads);
    assertEquals(9, f.statementCreates);
    assertEquals(5, f.preparedCreates);
    assertEquals(5, f.preparedExecutions);
    assertEquals(6, f.analyzes);
    assertEquals(java.util.Collections.nCopies(CLOSES, 30), f.timeouts);
    assertEquals(List.of(42L, 700L, 900L, 500L, 600L), f.boundLong);
    assertEquals(java.util.Collections.nCopies(5, true), f.boundBoolean);
  }

  @Test
  void target002EmptyHasNoInventedRowsAndOneFalseSetval() throws Exception {
    var f = new Fixture();
    f.empty = true;
    f.scalars = new long[SCALARS];
    Arrays.fill(f.scalars, SETVAL_SCALAR_FIRST, SCALARS, 1L);
    workflow(
        new MigrationMasterTargetPublisher(),
        f,
        new MigrationMasterCopyDataset(new SpeakerCopyBatch(List.of()), emptyContent()));
    assertEquals(SQL, f.sql);
    assertEquals(List.of(1L, 1L, 1L, 1L, 1L), f.boundLong);
    assertEquals(java.util.Collections.nCopies(5, false), f.boundBoolean);
    assertEquals(RESULTS, f.resultCloses);
    assertEquals(CLOSES, f.closeAttempts);
  }

  @Test
  void target003NullPrepareIsRejectedBeforeDelegation() {
    assertEquals(
        "migration master target input is invalid",
        assertThrows(
                IllegalArgumentException.class,
                () -> new MigrationMasterTargetPublisher().prepare(null))
            .getMessage());
  }

  @Test
  void target004AllNullTransferCombinationsHaveNoConnectionCalls() throws Exception {
    var f = new Fixture();
    var conn = f.connection();
    var declared = normal();
    var publisher = new MigrationMasterTargetPublisher();
    assertThrows(
        IllegalArgumentException.class, () -> publisher.transferAndFinalize(null, declared));
    assertThrows(IllegalArgumentException.class, () -> publisher.transferAndFinalize(conn, null));
    assertEquals(
        "migration master target input is invalid",
        assertThrows(
                IllegalArgumentException.class, () -> publisher.transferAndFinalize(null, null))
            .getMessage());
    assertEquals(0, f.autoReads);
    assertEquals(0, f.statementCreates);
    assertTrue(f.sql.isEmpty());
  }

  @Test
  void target005AutoCommitDelegationNeverMutatesConnection() throws Exception {
    var prepare = new Fixture();
    prepare.autoCommit = true;
    assertThrows(
        SQLException.class,
        () -> new MigrationMasterTargetPublisher().prepare(prepare.connection()));
    assertTrue(prepare.sql.isEmpty());
    assertEquals(0, prepare.closeAttempts);
    var transfer = new Fixture();
    transfer.autoCommit = true;
    assertThrows(
        SQLException.class,
        () ->
            new MigrationMasterTargetPublisher()
                .transferAndFinalize(transfer.connection(), normal()));
    assertTrue(transfer.sql.isEmpty());
    assertEquals(0, transfer.closeAttempts);
  }

  @Test
  void target006EveryPrepareSqlOriginalFailureStopsThePath() throws Exception {
    sqlFailures(0, PREPARE_END);
  }

  @Test
  void target007EveryTransferSqlOriginalFailureStopsThePath() throws Exception {
    sqlFailures(PREPARE_END, TRANSFER_END);
  }

  @Test
  void target008EveryReferenceSqlFailurePreventsSetvalAndAnalyze() throws Exception {
    sqlFailures(TRANSFER_END, REFERENCE_END);
  }

  @Test
  void target009EveryFinalizationSqlAndPreparedExecuteOriginalFailure() throws Exception {
    sqlFailures(CONTENT_END, SQL_COUNT);
    for (int slot = 0; slot < 5; slot++)
      for (Throwable failure : failures()) {
        var f = new Fixture();
        f.badPreparedExecute = slot;
        f.failure = failure;
        assertSame(
            failure,
            assertThrows(
                failure.getClass(),
                () -> workflow(new MigrationMasterTargetPublisher(), f, normal())));
        assertEquals(SQL.subList(0, SETVAL_FIRST + slot + 1), f.sql);
        assertEquals(SETVAL_SCALAR_FIRST + CONTENT_TABLES + slot, f.resultCloses);
        assertEquals(10 + slot, f.closeAttempts);
        assertEquals(slot + 1, f.preparedExecutions);
        assertEquals(0, f.analyzes);
      }
  }

  @Test
  void target010EveryTransferScalarMismatchCannotReachLaterStage() throws Exception {
    for (int query = 0; query < TRANSFER_SCALARS; query++) {
      var f = new Fixture();
      f.badScalar = query;
      assertThrows(
          SQLException.class, () -> workflow(new MigrationMasterTargetPublisher(), f, normal()));
      int sqlIndex = scalarSqlIndex(query);
      assertEquals(SQL.subList(0, sqlIndex + 1), f.sql);
      assertEquals(query + 1, f.resultCloses);
      assertEquals(ordinaryOwnersThrough(sqlIndex), f.closeAttempts);
      assertEquals(0, f.preparedExecutions);
    }
  }

  @Test
  void target011EveryReferenceOrphanAndOrderViolationPreventsSequenceMutation() throws Exception {
    for (int query = ORPHAN_FIRST; query < REFERENCE_SCALARS_END; query++) {
      var f = new Fixture();
      f.badScalar = query;
      assertThrows(
          SQLException.class, () -> workflow(new MigrationMasterTargetPublisher(), f, normal()));
      assertEquals(SQL.subList(0, scalarSqlIndex(query) + 1), f.sql);
      assertEquals(query + 1, f.resultCloses);
      assertEquals(7, f.closeAttempts);
      assertEquals(0, f.preparedExecutions);
      assertEquals(0, f.analyzes);
    }
  }

  @Test
  void target012PartialSetvalAndAnalyzeWarningAreNotRetriedOrSuccess() throws Exception {
    for (int slot = 0; slot < 5; slot++) {
      var f = new Fixture();
      f.badScalar = SETVAL_SCALAR_FIRST + slot;
      assertThrows(
          SQLException.class, () -> workflow(new MigrationMasterTargetPublisher(), f, normal()));
      assertEquals(SQL.subList(0, SETVAL_FIRST + slot + 1), f.sql);
      assertEquals(slot + 1, f.preparedExecutions);
      assertEquals(10 + slot, f.closeAttempts);
      assertEquals(0, f.analyzes);
    }
    for (int slot = 0; slot < 6; slot++) {
      var f = new Fixture();
      f.badWarning = slot;
      assertThrows(
          SQLException.class, () -> workflow(new MigrationMasterTargetPublisher(), f, normal()));
      assertEquals(SQL.subList(0, ANALYZE_FIRST + slot + 1), f.sql);
      assertEquals(5, f.preparedExecutions);
      assertEquals(slot + 1, f.analyzes);
      assertEquals(CLOSES, f.closeAttempts);
      assertEquals(RESULTS, f.resultCloses);
    }
  }

  @Test
  void target013EveryOwnedStatementCloseFailureKeepsExactPrefixAndOuterOwnership()
      throws Exception {
    for (int close = 0; close < CLOSES; close++)
      for (Throwable failure : failures()) {
        var f = new Fixture();
        f.badClose = close;
        f.closeFailure = failure;
        assertSame(
            failure,
            assertThrows(
                failure.getClass(),
                () -> workflow(new MigrationMasterTargetPublisher(), f, normal())));
        assertEquals(SQL.subList(0, CLOSE_SQL_PREFIX.get(close)), f.sql);
        assertEquals(CLOSE_RESULTS.get(close), f.resultCloses);
        assertEquals(
            close + 1 + (close >= PREPARED_FIRST_CLOSE && close < OUTER_FINAL_CLOSE ? 1 : 0),
            f.closeAttempts);
      }
  }

  @Test
  void target014OriginalReadFailureKeepsResultThenStatementSuppressedOrder() throws Exception {
    for (Throwable primary : failures()) {
      var f = new Fixture();
      f.badRead = 0;
      f.failure = primary;
      f.extraResultAt = 0;
      var result = new SQLException("synthetic inner close");
      var outer = new IllegalStateException("synthetic statement close");
      f.extraResult = result;
      f.badClose = 3;
      f.closeFailure = outer;
      assertSame(
          primary,
          assertThrows(
              primary.getClass(),
              () -> workflow(new MigrationMasterTargetPublisher(), f, normal())));
      assertEquals(List.of(result, outer), List.of(primary.getSuppressed()));
      assertEquals(SQL.subList(0, 7), f.sql);
      assertEquals(1, f.resultCloses);
      assertEquals(4, f.closeAttempts);
      assertEquals(0, f.preparedExecutions);
    }
  }

  @Test
  void target015FixedRedactionAndSamePublisherFreshConnectionAfterFailure() throws Exception {
    var publisher = new MigrationMasterTargetPublisher();
    assertEquals("MigrationMasterTargetPublisher[REDACTED]", publisher.toString());
    var failed = new Fixture();
    failed.badSql = PREPARE_END;
    assertThrows(SQLException.class, () -> workflow(publisher, failed, normal()));
    var next = new Fixture();
    workflow(publisher, next, normal());
    assertEquals(SQL, next.sql);
    assertEquals(PREPARE_END + 1, failed.sql.size());
    assertEquals(CLOSES, next.closeAttempts);
  }

  @Test
  void target016SharedPublisherFiniteIndependentConnectionsAndTermination() throws Exception {
    var publisher = new MigrationMasterTargetPublisher();
    var declared = normal();
    var executor = Executors.newFixedThreadPool(WORKERS);
    try {
      var futures = new ArrayList<Future<List<String>>>();
      for (int index = 0; index < TASKS; index++)
        futures.add(
            executor.submit(
                () -> {
                  var f = new Fixture();
                  workflow(publisher, f, declared);
                  assertEquals(CLOSES, f.closeAttempts);
                  assertEquals(RESULTS, f.resultCloses);
                  return f.sql;
                }));
      for (var future : futures) assertEquals(SQL, future.get(WAIT_SECONDS, TimeUnit.SECONDS));
    } finally {
      executor.shutdownNow();
      assertTrue(executor.awaitTermination(TERMINATION_SECONDS, TimeUnit.SECONDS));
    }
  }

  @Test
  void target017AllSixContentQueryFaultsStopBeforeFinalization() throws Exception {
    sqlFailures(REFERENCE_END, CONTENT_END);
  }

  @Test
  void target018AllSixtyFiveValueChangesStopBeforeMaxSetvalAnalyze() throws Exception {
    for (int table = 0; table < CONTENT_TABLES; table++) {
      for (int column = 0; column < CONTENT_TYPES.get(table).length(); column++) {
        var f = new Fixture();
        f.badContentTable = table;
        f.badContentColumn = column;
        assertThrows(
            SQLException.class, () -> workflow(new MigrationMasterTargetPublisher(), f, normal()));
        contentFailurePost(f, table, true);
      }
    }
  }

  @Test
  void target019NullContentResultsDoNotCreateResultOwnership() throws Exception {
    for (int table = 0; table < CONTENT_TABLES; table++) {
      var f = new Fixture();
      f.nullContentResult = table;
      assertThrows(
          SQLException.class, () -> workflow(new MigrationMasterTargetPublisher(), f, normal()));
      contentFailurePost(f, table, false);
    }
  }

  @Test
  void target020MissingAndExtraRowsHaveNoExtraColumnReads() throws Exception {
    for (int table = 0; table < CONTENT_TABLES; table++) {
      for (boolean missing : List.of(true, false)) {
        var f = new Fixture();
        if (missing) f.missingContent = table;
        else f.extraContent = table;
        assertThrows(
            SQLException.class, () -> workflow(new MigrationMasterTargetPublisher(), f, normal()));
        int expected = CONTENT_TYPES.subList(0, table).stream().mapToInt(String::length).sum();
        if (!missing) expected += CONTENT_TYPES.get(table).length();
        assertEquals(expected, f.contentFieldReads);
        contentFailurePost(f, table, true);
      }
    }
  }

  @Test
  void target021RequiredSqlNullNeverBecomesZeroFalseOrEmpty() throws Exception {
    for (int table = 0; table < CONTENT_TABLES; table++) {
      for (int column = 0; column < CONTENT_TYPES.get(table).length(); column++) {
        if (contentLiteral(table).get(column) == null) continue;
        var f = new Fixture();
        f.badContentTable = table;
        f.badContentColumn = column;
        f.nullContentValue = true;
        assertThrows(
            SQLException.class, () -> workflow(new MigrationMasterTargetPublisher(), f, normal()));
        contentFailurePost(f, table, true);
      }
    }
  }

  @Test
  void target022EveryContentGetterKeepsPrimaryThenBothCleanupIdentities() throws Exception {
    for (int table = 0; table < CONTENT_TABLES; table++) {
      for (int column = 0; column < CONTENT_TYPES.get(table).length(); column++) {
        for (Throwable primary : failures()) {
          var f = new Fixture();
          f.badContentTable = table;
          f.badContentColumn = column;
          f.failContentRead = true;
          f.failure = primary;
          var inner = new SQLException("synthetic content close");
          var outer = new IllegalStateException("synthetic content statement close");
          f.extraResult = inner;
          f.badClose = CONTENT_CLOSE;
          f.closeFailure = outer;
          assertSame(
              primary,
              assertThrows(
                  primary.getClass(),
                  () -> workflow(new MigrationMasterTargetPublisher(), f, normal())));
          assertEquals(2, primary.getSuppressed().length);
          assertSame(inner, primary.getSuppressed()[0]);
          assertSame(outer, primary.getSuppressed()[1]);
          contentFailurePost(f, table, true);
        }
      }
    }
  }

  @Test
  void target023ScalarAndTypedResultsRemainSeparateOnOneBorrowedConnection() throws Exception {
    var f = new Fixture();
    var declared = normal();
    workflow(new MigrationMasterTargetPublisher(), f, declared);
    assertEquals(CONTENT_COLUMNS, f.contentFieldReads);
    assertEquals(SCALARS, f.scalarReads);
    assertEquals(RESULTS, f.resultCloses);
    assertEquals(CLOSES, f.closeAttempts);
    assertEquals(List.of(1000), f.fetchSizes);
    assertEquals(SQL, f.sql);
    assertEquals(SPEAKER_ID, declared.speakers().rows().getFirst().fields().getFirst());
  }

  @Test
  void target024FiniteFailedContentCallsCannotReachFinalizerOrRetainResources() throws Exception {
    var publisher = new MigrationMasterTargetPublisher();
    var declared = normal();
    var executor = Executors.newFixedThreadPool(WORKERS);
    try {
      var futures = new ArrayList<Future<Integer>>();
      for (int index = 0; index < TASKS; index++) {
        int table = index % CONTENT_TABLES;
        futures.add(
            executor.submit(
                () -> {
                  var f = new Fixture();
                  f.badContentTable = table;
                  f.badContentColumn = 0;
                  assertThrows(SQLException.class, () -> workflow(publisher, f, declared));
                  contentFailurePost(f, table, true);
                  return f.closeAttempts;
                }));
      }
      for (var future : futures) assertEquals(8, future.get(WAIT_SECONDS, TimeUnit.SECONDS));
    } finally {
      executor.shutdownNow();
      assertTrue(executor.awaitTermination(TERMINATION_SECONDS, TimeUnit.SECONDS));
    }
  }

  private static void contentFailurePost(Fixture f, int table, boolean ownedResult) {
    assertEquals(SQL.subList(0, REFERENCE_END + table + 1), f.sql);
    assertEquals(REFERENCE_SCALARS_END + table + (ownedResult ? 1 : 0), f.resultCloses);
    assertEquals(8, f.closeAttempts);
    assertEquals(0, f.preparedCreates);
    assertEquals(0, f.preparedExecutions);
    assertEquals(0, f.analyzes);
  }

  private static String contentGetter(char kind) {
    return switch (kind) {
      case 'L' -> GET_LONG;
      case 'I' -> GET_INT;
      case 'B' -> GET_BOOLEAN;
      case 'T' -> GET_TIMESTAMP;
      default -> GET_STRING;
    };
  }

  private static String changedContent(@Nullable String value, char kind) {
    if (value == null) return kind == 'L' || kind == 'I' ? ONE : "changed";
    return switch (kind) {
      case 'L', 'I' -> Long.toString(Long.parseLong(value) + 1);
      case 'B' -> value.equals(TRUE_TEXT) ? "false" : TRUE_TEXT;
      case 'T' -> Instant.parse(value).plusNanos(1000).toString();
      default -> value + "X";
    };
  }

  private static List<@Nullable String> contentLiteral(int table) {
    return switch (table) {
      case 0 ->
          Arrays.<@Nullable String>asList(
              SPEAKER_ID, ONE, "Alice", "alice", TRUE_TEXT, null, STAMP);
      case 1 ->
          Arrays.<@Nullable String>asList(
              FILE_ID_TEXT,
              ONE,
              ONE,
              "script/file.txt",
              FILE_NAME_TEXT,
              FILE_NAME_TEXT,
              null,
              "chapter",
              SHA,
              THREE,
              STAMP);
      case 2 ->
          Arrays.<@Nullable String>asList(
              ENTRY_ID_TEXT,
              ONE,
              FILE_ID_TEXT,
              ONE,
              "0",
              null,
              "dialogue",
              SPEAKER_ID,
              null,
              "hello",
              "raw",
              STAMP);
      case 3 ->
          Arrays.<@Nullable String>asList(
              AUDIO_ID_TEXT,
              ONE,
              "voice/a.ogg",
              "表示",
              "a.ogg",
              "a",
              VOICE_TEXT,
              "ogg",
              "1200",
              THREE,
              SHA,
              STAMP);
      case 4 ->
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
              STAMP);
      default ->
          Arrays.<@Nullable String>asList(
              ENTRY_ID_TEXT, AUDIO_ID_TEXT, ONE, VOICE_TEXT, ONE, STAMP);
    };
  }

  private static void workflow(
      MigrationMasterTargetPublisher publisher, Fixture f, MigrationMasterCopyDataset declared)
      throws SQLException {
    var connection = f.connection();
    publisher.prepare(connection);
    publisher.transferAndFinalize(connection, declared);
  }

  private static List<Throwable> failures() {
    return List.of(
        new SQLException("synthetic sql"),
        new IllegalStateException("synthetic runtime"),
        new AssertionError("synthetic error"));
  }

  private static int ordinaryOwnersThrough(int sqlIndex) {
    return (int) OWNER_START.stream().filter(index -> index <= sqlIndex).count();
  }

  private static int scalarSqlIndex(int query) {
    return IntStream.range(0, SQL_COUNT)
        .filter(
            index -> SQL.get(index).startsWith("SELECT ") && !CONTENT_SQL.contains(SQL.get(index)))
        .skip(query)
        .findFirst()
        .orElseThrow();
  }

  private static void sqlFailures(int first, int end) throws Exception {
    var declared = normal();
    for (int index = first; index < end; index++)
      for (Throwable failure : failures()) {
        var f = new Fixture();
        f.badSql = index;
        f.failure = failure;
        assertSame(
            failure,
            assertThrows(
                failure.getClass(),
                () -> workflow(new MigrationMasterTargetPublisher(), f, declared)));
        assertEquals(SQL.subList(0, index + 1), f.sql);
        assertEquals(
            (int)
                SQL.subList(0, index).stream().filter(query -> query.startsWith("SELECT ")).count(),
            f.resultCloses);
        assertEquals(
            ordinaryOwnersThrough(index) + Math.max(0, Math.min(5, index - SETVAL_FIRST)),
            f.closeAttempts);
        assertEquals(0, failure.getSuppressed().length);
        if (index < CONTENT_END) {
          assertEquals(0, f.preparedExecutions);
          assertEquals(0, f.analyzes);
        }
      }
  }

  private static final class Fixture {
    private final List<String> sql = new ArrayList<>();
    private final List<Integer> timeouts = new ArrayList<>();
    private final List<Long> boundLong = new ArrayList<>();
    private final List<Boolean> boundBoolean = new ArrayList<>();
    private long[] scalars = NORMAL_SCALARS.clone();
    private boolean empty;
    private boolean autoCommit;
    private int badContentTable = -1;
    private int badContentColumn = -1;
    private int nullContentResult = -1;
    private int missingContent = -1;
    private int extraContent = -1;
    private boolean nullContentValue;
    private boolean failContentRead;
    private int contentFieldReads;
    private final List<Integer> fetchSizes = new ArrayList<>();
    private int badSql = -1;
    private int badScalar = -1;
    private int badRead = -1;
    private int badPreparedExecute = -1;
    private int badWarning = -1;
    private int badClose = -1;
    private int extraResultAt = -1;
    private Throwable failure = new SQLException("synthetic primary");
    private Throwable closeFailure = new SQLException("synthetic close");
    private @Nullable Throwable extraResult;
    private int autoReads;
    private int statementCreates;
    private int preparedCreates;
    private int preparedExecutions;
    private int analyzes;
    private int scalarReads;
    private int resultCloses;
    private int closeAttempts;

    private void recordSql(String actual) throws Throwable {
      int index = sql.size();
      sql.add(actual);
      assertEquals(SQL.get(index), actual);
      if (index == badSql) throw failure;
    }

    private void closeOwned() throws Throwable {
      int index = closeAttempts;
      closeAttempts++;
      if (index == badClose) throw closeFailure;
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
                    return autoCommit;
                  case "createStatement":
                    statementCreates++;
                    return statement();
                  case "prepareStatement":
                    recordSql((String) args[0]);
                    int slot = preparedCreates;
                    preparedCreates++;
                    return prepared(slot);
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
                    return null;
                  case "executeUpdate":
                    String update = (String) args[0];
                    int operation = sql.size();
                    assertTrue(
                        operation < PREPARE_END
                            || List.of(14, 15).contains(operation)
                            || operation >= ANALYZE_FIRST);
                    recordSql(update);
                    if (update.startsWith("ANALYZE ")) analyzes++;
                    return update.startsWith("INSERT INTO ") ? (empty ? 0 : 1) : 0;
                  case "executeLargeUpdate":
                    assertTrue(List.of(8, 24, 25, 26).contains(sql.size()));
                    recordSql((String) args[0]);
                    return empty ? 0L : 1L;
                  case "setFetchSize":
                    assertEquals(1000, args[0]);
                    fetchSizes.add((Integer) args[0]);
                    return null;
                  case "executeQuery":
                    String query = (String) args[0];
                    recordSql(query);
                    int contentTable = CONTENT_SQL.indexOf(query);
                    if (contentTable >= 0)
                      return contentTable == nullContentResult ? null : contentResult(contentTable);
                    return result();
                  case "getWarnings":
                    return badWarning == analyzes - 1
                        ? new SQLWarning("synthetic skipped analyze")
                        : null;
                  case CLOSE_METHOD:
                    closeOwned();
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
                    return null;
                  case "setLong":
                    assertEquals(1, args[0]);
                    boundLong.add((Long) args[1]);
                    return null;
                  case "setBoolean":
                    assertEquals(2, args[0]);
                    boundBoolean.add((Boolean) args[1]);
                    return null;
                  case "executeQuery":
                    preparedExecutions++;
                    if (slot == badPreparedExecute) throw failure;
                    return result();
                  case CLOSE_METHOD:
                    closeOwned();
                    return null;
                  default:
                    throw new AssertionError(
                        "Unexpected PreparedStatement operation: " + method.getName());
                }
              });
    }

    private ResultSet contentResult(int table) {
      int[] position = {-1};
      boolean[] wasNull = {false};
      return (ResultSet)
          Proxy.newProxyInstance(
              ResultSet.class.getClassLoader(),
              new Class<?>[] {ResultSet.class},
              (proxy, method, args) -> {
                String name = method.getName();
                if (name.equals("next")) {
                  position[0]++;
                  if (empty || table == missingContent) return false;
                  return position[0] == 0 || table == extraContent && position[0] == 1;
                }
                if (name.equals("wasNull")) return wasNull[0];
                if (name.equals(CLOSE_METHOD)) {
                  resultCloses++;
                  if (table == badContentTable && extraResult != null) throw extraResult;
                  return null;
                }
                if (List.of(GET_LONG, GET_INT, GET_BOOLEAN, GET_TIMESTAMP, GET_STRING)
                    .contains(name)) {
                  int column = (Integer) args[0] - 1;
                  assertEquals(contentGetter(CONTENT_TYPES.get(table).charAt(column)), name);
                  contentFieldReads++;
                  boolean bad = table == badContentTable && column == badContentColumn;
                  if (bad && failContentRead) throw failure;
                  String value = contentLiteral(table).get(column);
                  if (bad)
                    value =
                        nullContentValue
                            ? null
                            : changedContent(value, CONTENT_TYPES.get(table).charAt(column));
                  wasNull[0] = value == null;
                  return switch (name) {
                    case GET_LONG -> value == null ? 0L : Long.parseLong(value);
                    case GET_INT -> value == null ? 0 : Integer.parseInt(value);
                    case GET_BOOLEAN -> value != null && Boolean.parseBoolean(value);
                    case GET_TIMESTAMP ->
                        value == null ? null : Timestamp.from(Instant.parse(value));
                    default -> value;
                  };
                }
                throw new AssertionError("Unexpected content ResultSet operation " + name);
              });
    }

    private ResultSet result() {
      int query = scalarReads;
      scalarReads++;
      int[] nextCalls = {0};
      return (ResultSet)
          Proxy.newProxyInstance(
              ResultSet.class.getClassLoader(),
              new Class<?>[] {ResultSet.class},
              (proxy, method, args) -> {
                switch (method.getName()) {
                  case "next":
                    int call = nextCalls[0];
                    nextCalls[0]++;
                    return call == 0;
                  case "getLong":
                    assertEquals(1, args[0]);
                    if (query == badRead) throw failure;
                    return scalars[query] + (query == badScalar ? 1 : 0);
                  case "wasNull":
                    return false;
                  case CLOSE_METHOD:
                    resultCloses++;
                    if (query == extraResultAt && extraResult != null) throw extraResult;
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
        List.of(
            Arrays.<@Nullable String>asList(
                ENTRY_ID_TEXT, AUDIO_ID_TEXT, ONE, VOICE_TEXT, ONE, stamp)),
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
                    SPEAKER_ID, ONE, "Alice", "alice", TRUE_TEXT, null, stamp))));
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
                    FILE_ID_TEXT,
                    game,
                    ONE,
                    "script/file.txt",
                    FILE_NAME_TEXT,
                    FILE_NAME_TEXT,
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
                        ENTRY_ID_TEXT,
                        game,
                        FILE_ID_TEXT,
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
            AUDIO_ID_TEXT,
            ONE,
            "voice/a.ogg",
            "表示",
            "a.ogg",
            "a",
            VOICE_TEXT,
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
