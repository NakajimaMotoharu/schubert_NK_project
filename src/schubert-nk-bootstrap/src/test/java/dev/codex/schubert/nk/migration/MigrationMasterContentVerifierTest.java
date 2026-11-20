package dev.codex.schubert.nk.migration;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.lang.reflect.Proxy;
import java.security.NoSuchAlgorithmException;
import java.sql.Connection;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.time.Instant;
import java.time.OffsetDateTime;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import org.jspecify.annotations.Nullable;
import org.junit.jupiter.api.Test;

/** PT-MIG-CONTENT001..029; independent V002 SQL, literal values and JDBC resource-event model. */
final class MigrationMasterContentVerifierTest {
  private static final String SPEAKER_B = "200";
  private static final String VOICE_ROLE = "voice";
  private static final int TABLES = 7;
  private static final int SEARCH_CHECK = 6;
  private static final int COPY_COLUMNS = 65;
  private static final int WORKERS = 8;
  private static final int TASKS = 64;
  private static final int WAIT_SECONDS = 5;
  private static final int TERMINATION_SECONDS = 10;
  private static final String TIME = "2026-01-02T03:04:05Z";
  private static final String SHA = "0".repeat(64);
  private static final String INPUT_DIAGNOSTIC = "migration master content input is invalid";
  private static final String DIAGNOSTIC = "migration master content verification is invalid";
  private static final String GET_LONG = "getLong";
  private static final String GET_INT = "getInt";
  private static final String GET_BOOLEAN = "getBoolean";
  private static final String GET_OFFSET_DATE_TIME = "getObject";
  private static final String GET_STRING = "getString";
  private static final String CALL_AUTO = "auto";
  private static final String CALL_CREATE = "create";
  private static final String CALL_TIMEOUT = "timeout";
  private static final String CALL_FETCH = "fetch";
  private static final String CALL_STATEMENT_CLOSE = "statement.close";
  private static final String SUFFIX_QUERY = ":query";
  private static final String SUFFIX_NEXT = ":next";
  private static final String SUFFIX_NULL = ":wasNull";
  private static final String SUFFIX_CLOSE = ":close";
  private static final String ENTRY_A = "900";
  private static final String ENTRY_B = "901";
  private static final String AUDIO_A = "500";
  private static final String AUDIO_B = "501";
  private static final String SOURCE_VIDEO_A = "source/a.mp4";
  private static final String SOURCE_VIDEO_B = "source/b.mp4";
  private static final String TARGET_VIDEO_A = "video/a.mp4";
  private static final String TARGET_VIDEO_B = "video/b.mp4";
  private static final List<String> SQL =
      List.of(
          "SELECT id,game_id,name,normalized_name,is_protagonist,notes,created_at FROM schubert.speakers ORDER BY id",
          "SELECT id,game_id,display_order,storage_relative_path,display_path,file_name,section_code,chapter_title,sha256,byte_size,created_at FROM schubert.script_files ORDER BY id",
          "SELECT id,game_id,script_file_id,display_order,entry_index,line_number,entry_type,speaker_id,speaker_label,body,raw_block,created_at FROM schubert.script_entries ORDER BY id",
          "SELECT id,game_id,storage_relative_path,display_path,file_name,basename,audio_role,container,duration_ms,byte_size,sha256,created_at FROM schubert.audio_files ORDER BY id",
          "SELECT id,logical_id,media_type,title,category,section,storage_relative_path,display_path,file_name,byte_size,sha256,mime_type,parent_logical_id,pair_key,pair_role,display_order,created_at FROM schubert.media_assets ORDER BY id",
          "SELECT entry_id,audio_file_id,game_id,link_type,display_order,created_at FROM schubert.entry_audio_links ORDER BY entry_id,audio_file_id,link_type COLLATE \"C\"",
          "SELECT count(*) FROM schubert.script_entries WHERE body_search IS DISTINCT FROM pg_catalog.lower(body)");
  // Independent V002 getter contract, never obtained from the Production descriptor.
  private static final List<String> TYPES =
      List.of(
          "LISSBST",
          "LILSSSSSSLT",
          "LILLIISLSSST",
          "LISSSSSSLLST",
          "LSSSSSSSSLSSSSSIT",
          "LLISIT",
          "L");

  @Test
  void content001SixFixedQueriesAndEveryPayloadColumnMatch() throws Exception {
    var f = new Fixture();
    verify(f, declared(TIME, null));
    assertEquals(SQL, f.sql);
    assertEquals(List.of(30), f.timeouts);
    assertEquals(List.of(1000), f.fetchSizes);
    assertEquals(List.of(1, TABLES), List.of(f.statementCloses, f.resultCloses));
    assertEquals(
        COPY_COLUMNS, TYPES.subList(0, SEARCH_CHECK).stream().mapToInt(String::length).sum());
    assertEquals(expectedCalls(literals(TIME, null)), f.calls);
  }

  @Test
  void content002EmptyAllTablesStillChecksEveryTerminalRow() throws Exception {
    var f = new Fixture(emptyTables());
    verify(f, emptyMaster());
    assertEquals(SQL, f.sql);
    assertEquals(expectedCalls(emptyTables()), f.calls);
    assertEquals(TABLES, f.resultCloses);
  }

  @Test
  void content003BothNullBoundariesHaveNoIo() throws Exception {
    var verifier = new MigrationMasterContentVerifier();
    var master = declared(TIME, null);
    var f = new Fixture();
    for (boolean both : List.of(true, false)) {
      assertEquals(
          INPUT_DIAGNOSTIC,
          assertThrows(
                  IllegalArgumentException.class, () -> verifier.verify(null, both ? null : master))
              .getMessage());
    }
    assertEquals(
        INPUT_DIAGNOSTIC,
        assertThrows(IllegalArgumentException.class, () -> verifier.verify(f.connection(), null))
            .getMessage());
    assertTrue(f.calls.isEmpty());
  }

  @Test
  void content004AutoCommitIsRejectedWithoutStatementAcquisition() throws Exception {
    var f = new Fixture();
    f.auto = true;
    reject(f, declared(TIME, null));
    assertEquals(List.of(CALL_AUTO), f.calls);
  }

  @Test
  void content005NullStatementNeverCreatesOwnership() throws Exception {
    var f = new Fixture();
    f.nullStatement = true;
    reject(f, declared(TIME, null));
    assertEquals(List.of(CALL_AUTO, CALL_CREATE), f.calls);
    assertEquals(0, f.statementCloses);
  }

  @Test
  void content006NullResultAtEachTableClosesOnlyPriorResults() throws Exception {
    for (int slot = 0; slot < TABLES; slot++) {
      var f = new Fixture();
      f.nullResultSlot = slot;
      reject(f, declared(TIME, null));
      assertEquals(slot, f.resultCloses);
      assertEquals(1, f.statementCloses);
      assertEquals(SQL.subList(0, slot + 1), f.sql);
    }
  }

  @Test
  void content007AcquisitionTimeoutAndFetchFailuresPreserveOriginal() throws Exception {
    for (int index = 0; index < 4; index++) faultAt(index);
  }

  @Test
  void content008MissingRowAtEveryTableRejectsWithNoLaterQuery() throws Exception {
    for (int slot = 0; slot < TABLES; slot++) {
      var f = new Fixture();
      f.rows.get(slot).removeLast();
      reject(f, declared(TIME, null));
      assertEquals(SQL.subList(0, slot + 1), f.sql);
      assertEquals(slot + 1, f.resultCloses);
      assertEquals(1, f.statementCloses);
    }
  }

  @Test
  void content009ExtraRowsIncludingEmptyExpectationAreNeverRead() throws Exception {
    for (boolean empty : List.of(false, true)) {
      for (int slot = 0; slot < TABLES; slot++) {
        var data = empty ? emptyTables() : literals(TIME, null);
        var f = new Fixture(data);
        f.rows.get(slot).add(new ArrayList<>(literals(TIME, null).get(slot).getFirst()));
        reject(f, empty ? emptyMaster() : declared(TIME, null));
        int expectedReads = data.get(slot).size() * TYPES.get(slot).length();
        assertEquals(
            expectedReads,
            f.calls.stream().filter(c -> c.startsWith(slotKey(f.failedTable()) + ":get")).count());
        assertEquals(slot + 1, f.resultCloses);
        assertEquals(1, f.statementCloses);
      }
    }
  }

  @Test
  void content010AllSixtyFiveColumnPositionsDetectIndividualValueChanges() throws Exception {
    var source = literals(TIME, null);
    for (int slot = 0; slot < TABLES; slot++) {
      for (int column = 0; column < TYPES.get(slot).length(); column++) {
        var f = new Fixture(source);
        String old = f.rows.get(slot).getFirst().get(column);
        f.rows.get(slot).getFirst().set(column, changed(old, TYPES.get(slot).charAt(column)));
        reject(f, declared(TIME, null));
        assertEquals(SQL.subList(0, slot + 1), f.sql);
        assertEquals(slot + 1, f.resultCloses);
      }
    }
  }

  @Test
  void content011SqlNullIsComparedWithoutInventingZeroFalseOrEmpty() throws Exception {
    var source = literals(TIME, null);
    for (int slot = 0; slot < TABLES; slot++) {
      for (int column = 0; column < TYPES.get(slot).length(); column++) {
        var f = new Fixture(source);
        if (f.rows.get(slot).getFirst().get(column) == null) {
          verify(f, declared(TIME, null));
        } else {
          f.rows.get(slot).getFirst().set(column, null);
          reject(f, declared(TIME, null));
        }
      }
    }
  }

  @Test
  void content012TypedGettersAndImmediateWasNullMatchIndependentEventSequence() throws Exception {
    var f = new Fixture();
    verify(f, declared(TIME, null));
    var expected = expectedCalls(literals(TIME, null));
    assertEquals(expected, f.calls);
    assertEquals(143, f.calls.stream().filter(x -> x.contains(":get")).count());
  }

  @Test
  void content013NullEmptyLiteralBackslashNAndUtf8NotesStayDistinct() throws Exception {
    for (String notes : Arrays.asList(null, "", "\\N", "\t\n日本語\\")) {
      var f = new Fixture(literals(TIME, notes));
      verify(f, declared(TIME, notes));
      f = new Fixture(literals(TIME, notes));
      f.rows.getFirst().getFirst().set(5, notes == null ? "" : null);
      reject(f, declared(TIME, notes));
    }
  }

  @Test
  void content014DeclaredCurrentOrderIsNotReplacedByTargetPkOrder() throws Exception {
    var expected = declared(TIME, null);
    verify(new Fixture(), expected);
    assertEquals(SPEAKER_B, expected.speakers().rows().getFirst().fields().getFirst());
    assertEquals("701", expected.content().scenario().files().rows().getFirst().getFirst());
    assertEquals(
        ENTRY_B, expected.content().scenario().entries().rows().getFirst().fields().getFirst());
    assertEquals(AUDIO_B, expected.content().audio().audioRows().getFirst().fields().getFirst());
  }

  @Test
  void content015LinksSortByBothNumericIdsThenFixedAsciiType() throws Exception {
    var f = new Fixture();
    verify(f, declared(TIME, null));
    assertEquals(
        List.of("other", VOICE_ROLE, "bgm", "se"),
        f.rows.get(5).stream().map(row -> row.get(3)).toList());
    var swapped = new Fixture();
    java.util.Collections.swap(swapped.rows.get(5), 0, 1);
    reject(swapped, declared(TIME, null));
    assertEquals(SEARCH_CHECK, swapped.resultCloses);
  }

  @Test
  void content016TargetN12AndTimestampMicrosecondYearExtremes() throws Exception {
    for (String stamp : List.of("0001-01-01T00:00:00Z", "9999-12-31T23:59:59.999999Z")) {
      var data = emptyTables();
      data.getFirst().add(row("999999999999", "1", "Alice", "alice", "false", null, stamp));
      var f = new Fixture(data);
      var expected =
          new MigrationMasterCopyDataset(
              new SpeakerCopyBatch(List.of(new SpeakerCopyRow(data.getFirst().getFirst()))),
              emptyContent());
      verify(f, expected);
      assertEquals(1, f.calls.stream().filter(c -> c.equals("q0:getLong:1")).count());
    }
  }

  @Test
  void content017TypedTimestamptzUsesInstantAndCanonicalUtc() throws Exception {
    var f = new Fixture();
    f.rows.getFirst().getFirst().set(6, "2026-01-02T12:04:05+09:00");
    verify(f, declared(TIME, null));
    var precision = new Fixture();
    precision.rows.getFirst().getFirst().set(6, "2026-01-02T03:04:05.000001Z");
    reject(precision, declared(TIME, null));
  }

  @Test
  void content018EachQueryFailsWithoutAcquiringItsResult() throws Exception {
    var calls = expectedCalls(literals(TIME, null));
    for (int index = 0; index < calls.size(); index++)
      if (calls.get(index).endsWith(SUFFIX_QUERY)) faultAt(index);
  }

  @Test
  void content019EveryGetterWasNullAndNextOccurrenceKeepsResourcePostconditions() throws Exception {
    var calls = expectedCalls(literals(TIME, null));
    for (int index = 0; index < calls.size(); index++) {
      String call = calls.get(index);
      if (call.contains(":get") || call.endsWith(SUFFIX_NULL) || call.endsWith(SUFFIX_NEXT))
        faultAt(index);
    }
  }

  @Test
  void content020EachResultCloseFailureIsNotSuccess() throws Exception {
    for (int slot = 0; slot < TABLES; slot++) {
      for (Throwable failure : failures()) {
        var f = new Fixture();
        f.resultFailureSlot = slot;
        f.resultFailure = failure;
        assertFailure(f, failure, List.of());
        assertEquals(slot + 1, f.resultCloses);
        assertEquals(1, f.statementCloses);
      }
    }
  }

  @Test
  void content021StatementCloseFailureIsNotSuccess() throws Exception {
    for (Throwable failure : failures()) {
      var f = new Fixture();
      f.statementFailure = failure;
      assertFailure(f, failure, List.of());
      assertEquals(TABLES, f.resultCloses);
      assertEquals(1, f.statementCloses);
    }
  }

  @Test
  void content022AllThreeFaultKindsPreserveInnerThenOuterSuppressedOrder() throws Exception {
    var calls = expectedCalls(literals(TIME, null));
    for (int slot = 0; slot < TABLES; slot++) {
      for (int p = 0; p < 3; p++) {
        for (int rc = 0; rc < 3; rc++) {
          for (int sc = 0; sc < 3; sc++) {
            Throwable primary = failures().get(p);
            Throwable result = failures().get(rc);
            Throwable statement = failures().get(sc);
            var f = new Fixture();
            f.failAt = calls.indexOf(slotKey(slot) + ":getLong:1");
            f.failure = primary;
            f.resultFailureSlot = slot;
            f.resultFailure = result;
            f.statementFailure = statement;
            assertFailure(f, primary, List.of(result, statement));
            assertEquals(slot + 1, f.resultCloses);
            assertEquals(1, f.statementCloses);
          }
        }
      }
    }
  }

  @Test
  void content023SamePrimaryNeverCreatesSelfSuppressionIncludingCloseOrigin() throws Exception {
    var calls = expectedCalls(literals(TIME, null));
    for (int slot : List.of(0, 5, SEARCH_CHECK)) {
      for (boolean closeOrigin : List.of(true, false)) {
        for (Throwable primary : failures()) {
          var f = new Fixture();
          if (!closeOrigin) f.failAt = calls.indexOf(slotKey(slot) + ":getLong:1");
          f.failure = primary;
          f.resultFailureSlot = slot;
          f.resultFailure = primary;
          f.statementFailure = primary;
          assertFailure(f, primary, List.of());
          assertEquals(slot + 1, f.resultCloses);
          assertEquals(1, f.statementCloses);
        }
      }
    }
  }

  @Test
  void content024EqualValuedDistinctCleanupIsKeptTwice() throws Exception {
    var primary = new EqualFailure();
    var cleanup = new EqualFailure();
    assertTrue(primary.equals(cleanup));
    var f = new Fixture();
    f.failAt = expectedCalls(literals(TIME, null)).indexOf("q0:getLong:1");
    f.failure = primary;
    f.resultFailureSlot = 0;
    f.resultFailure = cleanup;
    f.statementFailure = cleanup;
    assertFailure(f, primary, List.of(cleanup, cleanup));
  }

  @Test
  void content025BorrowedConnectionHasOnlyAutoReadAndStatementAcquisition() throws Exception {
    var f = new Fixture();
    verify(f, declared(TIME, null));
    assertEquals(List.of(CALL_AUTO, CALL_CREATE), f.connectionCalls);
    assertEquals(1, f.statementCloses);
    assertEquals(TABLES, f.resultCloses);
  }

  @Test
  void content026FixedRedactionAndFreshSuccessAfterRejection() throws Exception {
    var verifier = new MigrationMasterContentVerifier();
    var bad = new Fixture();
    bad.nullStatement = true;
    var expected = declared(TIME, null);
    Throwable failure =
        assertThrows(SQLException.class, () -> verifier.verify(bad.connection(), expected));
    assertEquals(DIAGNOSTIC, failure.getMessage());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
    var good = new Fixture();
    verifier.verify(good.connection(), expected);
    assertEquals(SQL, good.sql);
    assertEquals("MigrationMasterContentVerifier[REDACTED]", verifier.toString());
  }

  @Test
  void content027CallerLiteralRowsAndDeclaredOrderStayUnchanged() throws Exception {
    var inputs = literals(TIME, null);
    var f = new Fixture(inputs);
    var expected = declared(TIME, null);
    verify(f, expected);
    assertEquals(inputs, f.rows);
    assertEquals(literals(TIME, null), inputs);
    assertEquals(SPEAKER_B, expected.speakers().rows().getFirst().fields().getFirst());
  }

  @Test
  void content028FiniteWorkersKeepIndependentBorrowedResources() throws Exception {
    var verifier = new MigrationMasterContentVerifier();
    var expected = declared(TIME, null);
    var executor = Executors.newFixedThreadPool(WORKERS);
    try {
      var futures = new ArrayList<Future<Integer>>();
      for (int index = 0; index < TASKS; index++) {
        futures.add(
            executor.submit(
                () -> {
                  var f = new Fixture();
                  verifier.verify(f.connection(), expected);
                  assertEquals(SQL, f.sql);
                  assertEquals(1, f.statementCloses);
                  return f.resultCloses;
                }));
      }
      for (var future : futures) assertEquals(TABLES, future.get(WAIT_SECONDS, TimeUnit.SECONDS));
    } finally {
      executor.shutdownNow();
      assertTrue(executor.awaitTermination(TERMINATION_SECONDS, TimeUnit.SECONDS));
    }
  }

  @Test
  void content029EmptyDeclaredRowsCannotHideGeneratedSearchMismatchCount() throws Exception {
    for (String count : Arrays.asList("1", "-1", "9223372036854775807", null)) {
      var f = new Fixture(emptyTables());
      f.rows.get(SEARCH_CHECK).getFirst().set(0, count);
      reject(f, emptyMaster());
      assertEquals(SQL, f.sql);
      assertEquals(TABLES, f.resultCloses);
      assertEquals(1, f.statementCloses);
      assertEquals(1, f.calls.stream().filter(call -> call.equals("q6:getLong:1")).count());
    }
    var zero = new Fixture(emptyTables());
    verify(zero, emptyMaster());
    assertEquals(SQL, zero.sql);
    assertEquals(TABLES, zero.resultCloses);
    assertEquals(List.of(CALL_AUTO, CALL_CREATE), zero.connectionCalls);
  }

  private static void verify(Fixture f, MigrationMasterCopyDataset expected) throws SQLException {
    new MigrationMasterContentVerifier().verify(f.connection(), expected);
  }

  private static void reject(Fixture f, MigrationMasterCopyDataset expected) {
    assertEquals(
        DIAGNOSTIC, assertThrows(SQLException.class, () -> verify(f, expected)).getMessage());
  }

  private static void assertFailure(Fixture f, Throwable primary, List<Throwable> suppressed)
      throws Exception {
    var expected = declared(TIME, null);
    assertSame(primary, assertThrows(primary.getClass(), () -> verify(f, expected)));
    assertEquals(suppressed.size(), primary.getSuppressed().length);
    for (int index = 0; index < suppressed.size(); index++)
      assertSame(suppressed.get(index), primary.getSuppressed()[index]);
  }

  private static void faultAt(int index) throws Exception {
    var calls = expectedCalls(literals(TIME, null));
    for (Throwable failure : failures()) {
      var f = new Fixture();
      f.failAt = index;
      f.failure = failure;
      assertFailure(f, failure, List.of());
      var expected = new ArrayList<>(calls.subList(0, index + 1));
      int activeResult = -1;
      for (int pos = 0; pos <= index; pos++) {
        String call = calls.get(pos);
        if (call.endsWith(SUFFIX_QUERY) && pos != index)
          activeResult = Integer.parseInt(call.substring(1, 2));
        if (call.endsWith(SUFFIX_CLOSE)) activeResult = -1;
      }
      if (activeResult >= 0) expected.add(slotKey(activeResult) + SUFFIX_CLOSE);
      if (index > 1 && !calls.get(index).equals(CALL_STATEMENT_CLOSE))
        expected.add(CALL_STATEMENT_CLOSE);
      assertEquals(expected, f.calls);
      assertEquals(index > 1 ? 1 : 0, f.statementCloses);
      assertEquals(expected.stream().filter(c -> c.endsWith(SUFFIX_CLOSE)).count(), f.resultCloses);
    }
  }

  private static List<Throwable> failures() {
    return List.of(
        new SQLException("synthetic sql"),
        new IllegalStateException("synthetic runtime"),
        new AssertionError("synthetic error"));
  }

  private static String slotKey(int slot) {
    return "q" + slot;
  }

  private static String getter(char type) {
    return switch (type) {
      case 'L' -> GET_LONG;
      case 'I' -> GET_INT;
      case 'B' -> GET_BOOLEAN;
      case 'T' -> GET_OFFSET_DATE_TIME;
      default -> GET_STRING;
    };
  }

  private static List<String> expectedCalls(List<List<List<@Nullable String>>> rows) {
    var result = new ArrayList<>(List.of(CALL_AUTO, CALL_CREATE, CALL_TIMEOUT, CALL_FETCH));
    for (int slot = 0; slot < TABLES; slot++) {
      String key = slotKey(slot);
      result.add(key + SUFFIX_QUERY);
      for (var ignored : rows.get(slot)) {
        result.add(key + SUFFIX_NEXT);
        for (int column = 0; column < TYPES.get(slot).length(); column++) {
          char type = TYPES.get(slot).charAt(column);
          result.add(key + ":" + getter(type) + ":" + (column + 1));
          if (type == 'L' || type == 'I' || type == 'B') result.add(key + SUFFIX_NULL);
        }
      }
      result.add(key + SUFFIX_NEXT);
      result.add(key + SUFFIX_CLOSE);
    }
    result.add(CALL_STATEMENT_CLOSE);
    return result;
  }

  private static String changed(@Nullable String value, char type) {
    if (value == null) return type == 'L' || type == 'I' ? "1" : type == 'T' ? TIME : "changed";
    return switch (type) {
      case 'L', 'I' -> Long.toString(Long.parseLong(value) + 1);
      case 'B' -> value.equals("true") ? "false" : "true";
      case 'T' -> Instant.parse(value).plusNanos(1000).toString();
      default -> value + "X";
    };
  }

  private static List<@Nullable String> row(@Nullable String... fields) {
    return new ArrayList<>(Arrays.asList(fields));
  }

  private static List<List<List<@Nullable String>>> emptyTables() {
    var result = new ArrayList<List<List<@Nullable String>>>();
    for (int slot = 0; slot < TABLES; slot++) result.add(new ArrayList<>());
    result.get(SEARCH_CHECK).add(row("0"));
    return result;
  }

  private static List<List<List<@Nullable String>>> literals(String stamp, @Nullable String notes) {
    var tables = emptyTables();
    tables.get(0).add(row("100", "1", "Alice", "alice", "true", notes, stamp));
    tables.get(0).add(row(SPEAKER_B, "1", "Bob", "bob", "false", "", stamp));
    tables
        .get(1)
        .add(row("700", "1", "2", "scenario/a.txt", "表示A", "a.txt", "01", "章A", SHA, "3", stamp));
    tables
        .get(1)
        .add(row("701", "1", "1", "scenario/b.txt", "表示B", "b.txt", "02", "章B", SHA, "3", stamp));
    tables
        .get(2)
        .add(
            row(
                ENTRY_A,
                "1",
                "700",
                "2",
                "0",
                "20",
                "dialogue",
                "100",
                "Alice",
                "Body A",
                "Raw A",
                stamp));
    tables
        .get(2)
        .add(
            row(
                ENTRY_B,
                "1",
                "701",
                "1",
                "0",
                null,
                "dialogue",
                SPEAKER_B,
                null,
                "Body B",
                "Raw B",
                stamp));
    tables
        .get(3)
        .add(
            row(
                AUDIO_A,
                "1",
                "voice/a.ogg",
                "音声A",
                "a.ogg",
                "a",
                VOICE_ROLE,
                "ogg",
                "0",
                "3",
                SHA,
                stamp));
    tables
        .get(3)
        .add(
            row(
                AUDIO_B,
                "1",
                "voice/b.ogg",
                "音声B",
                "b.ogg",
                "b",
                VOICE_ROLE,
                null,
                null,
                "3",
                SHA,
                stamp));
    tables
        .get(4)
        .add(
            row(
                "600",
                "video-a",
                "VIDEO",
                "Video A",
                "MAIN",
                null,
                TARGET_VIDEO_A,
                SOURCE_VIDEO_A,
                "a.mp4",
                "3",
                SHA,
                "video/mp4",
                null,
                null,
                null,
                "1",
                stamp));
    tables
        .get(4)
        .add(
            row(
                "601",
                "video-b",
                "VIDEO",
                "Video B",
                "MAIN",
                null,
                TARGET_VIDEO_B,
                SOURCE_VIDEO_B,
                "b.mp4",
                "3",
                SHA,
                "video/mp4",
                null,
                null,
                null,
                "2",
                stamp));
    tables.get(5).add(row(ENTRY_A, AUDIO_A, "1", "other", "1", stamp));
    tables.get(5).add(row(ENTRY_A, AUDIO_A, "1", VOICE_ROLE, "1", stamp));
    tables.get(5).add(row(ENTRY_A, AUDIO_B, "1", "bgm", "1", stamp));
    tables.get(5).add(row(ENTRY_B, AUDIO_B, "1", "se", "1", stamp));
    return tables;
  }

  private static MigrationMasterCopyDataset declared(String stamp, @Nullable String notes)
      throws NoSuchAlgorithmException {
    var data = literals(stamp, notes);
    var files =
        new ScenarioFileMigrationMap(
            List.of(
                new ScenarioFileMigrationMap.FilePair(1, 10, 701),
                new ScenarioFileMigrationMap.FilePair(1, 20, 700)));
    var entries =
        new ScenarioEntryMigrationMap(
            List.of(
                new ScenarioEntryMigrationMap.IdPair(30, 901),
                new ScenarioEntryMigrationMap.IdPair(40, 900)));
    var placement =
        new ScenarioEntryPlacementMap(
            files,
            entries,
            List.of(
                new ScenarioEntryPlacementMap.Placement(1, 20, 40, 0),
                new ScenarioEntryPlacementMap.Placement(1, 10, 30, 0)));
    var scenario =
        new ScenarioCopyDataset(
            new ScenarioFileCopyBatch(files, data.get(1)),
            new ScenarioEntryCopyBatch(
                placement,
                List.of(
                    new ScenarioEntryCopyRow(data.get(2).get(0)),
                    new ScenarioEntryCopyRow(data.get(2).get(1)))));
    var assets =
        new AssetMigrationManifest(
            List.of(
                new AssetMigrationManifest.Entry(
                    AssetMigrationManifest.Kind.VIDEO, SOURCE_VIDEO_A, TARGET_VIDEO_A, 3, SHA),
                new AssetMigrationManifest.Entry(
                    AssetMigrationManifest.Kind.VIDEO, SOURCE_VIDEO_B, TARGET_VIDEO_B, 3, SHA)));
    var media =
        new MediaAssetCopyBatch(
            assets,
            List.of(
                new MediaAssetCopyRow(data.get(4).get(1)),
                new MediaAssetCopyRow(data.get(4).get(0))));
    var content =
        new MigrationCopyDataset(
            scenario,
            List.of(
                new AudioFileCopyRow(data.get(3).get(1)), new AudioFileCopyRow(data.get(3).get(0))),
            List.of(data.get(5).get(3), data.get(5).get(2), data.get(5).get(1), data.get(5).get(0)),
            media);
    return new MigrationMasterCopyDataset(
        new SpeakerCopyBatch(
            List.of(
                new SpeakerCopyRow(data.get(0).get(1)), new SpeakerCopyRow(data.get(0).get(0)))),
        content);
  }

  private static MigrationMasterCopyDataset emptyMaster() {
    return new MigrationMasterCopyDataset(new SpeakerCopyBatch(List.of()), emptyContent());
  }

  private static MigrationCopyDataset emptyContent() {
    var files = new ScenarioFileMigrationMap(List.of());
    var entries = new ScenarioEntryMigrationMap(List.of());
    var scenario =
        new ScenarioCopyDataset(
            new ScenarioFileCopyBatch(files, List.of()),
            new ScenarioEntryCopyBatch(
                new ScenarioEntryPlacementMap(files, entries, List.of()), List.of()));
    return new MigrationCopyDataset(
        scenario,
        List.of(),
        List.of(),
        new MediaAssetCopyBatch(new AssetMigrationManifest(List.of()), List.of()));
  }

  private static final class EqualFailure extends SQLException {
    private static final long serialVersionUID = 1L;

    private EqualFailure() {
      super("synthetic equal-valued failure");
    }

    @Override
    public boolean equals(@Nullable Object other) {
      return other instanceof EqualFailure;
    }

    @Override
    public int hashCode() {
      return 1;
    }
  }

  private static final class Fixture {
    final List<List<List<@Nullable String>>> rows;
    final List<String> calls = new ArrayList<>();
    final List<String> sql = new ArrayList<>();
    final List<String> connectionCalls = new ArrayList<>();
    final List<Integer> timeouts = new ArrayList<>();
    final List<Integer> fetchSizes = new ArrayList<>();
    boolean auto;
    boolean nullStatement;
    int nullResultSlot = -1;
    int resultFailureSlot = -1;
    @Nullable Throwable resultFailure;
    @Nullable Throwable statementFailure;
    int failAt = -1;
    Throwable failure = new SQLException("synthetic primary");
    int resultCloses;
    int statementCloses;
    int nextQuery;

    Fixture() {
      this(literals(TIME, null));
    }

    Fixture(List<List<List<@Nullable String>>> input) {
      rows = emptyTables();
      rows.get(SEARCH_CHECK).clear();
      for (int slot = 0; slot < TABLES; slot++)
        for (var value : input.get(slot)) rows.get(slot).add(new ArrayList<>(value));
    }

    int failedTable() {
      return nextQuery - 1;
    }

    void hit(String call) throws Throwable {
      int index = calls.size();
      calls.add(call);
      if (index == failAt) throw failure;
    }

    Connection connection() {
      return (Connection)
          Proxy.newProxyInstance(
              Connection.class.getClassLoader(),
              new Class<?>[] {Connection.class},
              (proxy, method, args) -> {
                switch (method.getName()) {
                  case "getAutoCommit" -> {
                    connectionCalls.add(CALL_AUTO);
                    hit(CALL_AUTO);
                    return auto;
                  }
                  case "createStatement" -> {
                    connectionCalls.add(CALL_CREATE);
                    hit(CALL_CREATE);
                    return nullStatement ? null : statement();
                  }
                  default ->
                      throw new AssertionError(
                          "unexpected connection operation " + method.getName());
                }
              });
    }

    Statement statement() {
      return (Statement)
          Proxy.newProxyInstance(
              Statement.class.getClassLoader(),
              new Class<?>[] {Statement.class},
              (proxy, method, args) -> {
                switch (method.getName()) {
                  case "setQueryTimeout" -> {
                    hit(CALL_TIMEOUT);
                    timeouts.add((Integer) args[0]);
                    return null;
                  }
                  case "setFetchSize" -> {
                    hit(CALL_FETCH);
                    fetchSizes.add((Integer) args[0]);
                    return null;
                  }
                  case "executeQuery" -> {
                    int slot = nextQuery;
                    nextQuery++;
                    sql.add((String) args[0]);
                    hit(slotKey(slot) + SUFFIX_QUERY);
                    return slot == nullResultSlot ? null : result(slot);
                  }
                  case "close" -> {
                    statementCloses++;
                    hit(CALL_STATEMENT_CLOSE);
                    if (statementFailure != null) throw statementFailure;
                    return null;
                  }
                  default ->
                      throw new AssertionError(
                          "unexpected statement operation " + method.getName());
                }
              });
    }

    ResultSet result(int slot) {
      int[] position = {-1};
      boolean[] lastNull = {false};
      String key = slotKey(slot);
      return (ResultSet)
          Proxy.newProxyInstance(
              ResultSet.class.getClassLoader(),
              new Class<?>[] {ResultSet.class},
              (proxy, method, args) -> {
                String name = method.getName();
                if (name.equals("next")) {
                  hit(key + SUFFIX_NEXT);
                  position[0]++;
                  return position[0] < rows.get(slot).size();
                }
                if (name.equals("wasNull")) {
                  hit(key + SUFFIX_NULL);
                  return lastNull[0];
                }
                if (name.equals("close")) {
                  resultCloses++;
                  hit(key + SUFFIX_CLOSE);
                  if (slot == resultFailureSlot && resultFailure != null) throw resultFailure;
                  return null;
                }
                if (List.of(GET_LONG, GET_INT, GET_BOOLEAN, GET_OFFSET_DATE_TIME, GET_STRING)
                    .contains(name)) {
                  if (name.equals(GET_OFFSET_DATE_TIME)) {
                    assertEquals(2, args.length);
                    assertSame(OffsetDateTime.class, args[1]);
                  }
                  int column = (Integer) args[0];
                  hit(key + ":" + name + ":" + column);
                  String value = rows.get(slot).get(position[0]).get(column - 1);
                  lastNull[0] = value == null;
                  return switch (name) {
                    case GET_LONG -> value == null ? 0L : Long.parseLong(value);
                    case GET_INT -> value == null ? 0 : Integer.parseInt(value);
                    case GET_BOOLEAN -> value != null && Boolean.parseBoolean(value);
                    case GET_OFFSET_DATE_TIME -> value == null ? null : OffsetDateTime.parse(value);
                    default -> value;
                  };
                }
                throw new AssertionError("unexpected result operation " + name);
              });
    }
  }
}
