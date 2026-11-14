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

/** PT-MIG-CONSTRAINT001..022; independent V002 constraint matrix and JDBC resource-event oracle. */
final class MigrationMasterConstraintVerifierTest {
  private static final int TABLES = 6;
  private static final int COLUMNS = 75;
  private static final int FIELDS = 7;
  private static final int WORKERS = 8;
  private static final int TASKS = 64;
  private static final int WAIT_SECONDS = 5;
  private static final int TERMINATION_SECONDS = 10;
  private static final String DIAGNOSTIC = "migration constraint structure is invalid";
  private static final String GET_INT = "getInt";
  private static final String GET_BOOLEAN = "getBoolean";
  private static final String GET_STRING = "getString";
  private static final String AUTO = "auto";
  private static final String CREATE = "create";
  private static final String TIMEOUT = "timeout";
  private static final String FETCH = "fetch";
  private static final String STATEMENT_CLOSE = "statement.close";
  private static final String QUERY = ":query";
  private static final String NEXT = ":next";
  private static final String WAS_NULL = ":wasNull";
  private static final String CLOSE = ":close";
  private static final List<String> SQL =
      List.of(
          "SELECT (row_number() OVER (ORDER BY k.conname COLLATE \"C\"))::integer,k.conname,k.contype::text,pg_catalog.array_to_string(k.conkey,','),(k.convalidated AND k.conenforced AND NOT k.condeferrable AND NOT k.condeferred AND k.conislocal AND k.coninhcount=0 AND k.conparentid=0 AND k.contypid=0 AND NOT k.conperiod),CASE WHEN k.contype='f' THEN rn.nspname||'.'||rc.relname||'('||pg_catalog.array_to_string(k.confkey,',')||')' ELSE '-' END,CASE WHEN k.contype='f' THEN k.confupdtype::text||'/'||k.confdeltype::text||'/'||k.confmatchtype::text ELSE '-' END FROM pg_catalog.pg_constraint k JOIN pg_catalog.pg_class c ON c.oid=k.conrelid JOIN pg_catalog.pg_namespace n ON n.oid=c.relnamespace LEFT JOIN pg_catalog.pg_class rc ON rc.oid=k.confrelid LEFT JOIN pg_catalog.pg_namespace rn ON rn.oid=rc.relnamespace WHERE n.nspname='schubert' AND k.connamespace=n.oid AND c.relname='speakers' AND c.relkind='r' AND c.relpersistence='p' AND k.contype<>'n' ORDER BY k.conname COLLATE \"C\"",
          "SELECT (row_number() OVER (ORDER BY k.conname COLLATE \"C\"))::integer,k.conname,k.contype::text,pg_catalog.array_to_string(k.conkey,','),(k.convalidated AND k.conenforced AND NOT k.condeferrable AND NOT k.condeferred AND k.conislocal AND k.coninhcount=0 AND k.conparentid=0 AND k.contypid=0 AND NOT k.conperiod),CASE WHEN k.contype='f' THEN rn.nspname||'.'||rc.relname||'('||pg_catalog.array_to_string(k.confkey,',')||')' ELSE '-' END,CASE WHEN k.contype='f' THEN k.confupdtype::text||'/'||k.confdeltype::text||'/'||k.confmatchtype::text ELSE '-' END FROM pg_catalog.pg_constraint k JOIN pg_catalog.pg_class c ON c.oid=k.conrelid JOIN pg_catalog.pg_namespace n ON n.oid=c.relnamespace LEFT JOIN pg_catalog.pg_class rc ON rc.oid=k.confrelid LEFT JOIN pg_catalog.pg_namespace rn ON rn.oid=rc.relnamespace WHERE n.nspname='schubert' AND k.connamespace=n.oid AND c.relname='script_files' AND c.relkind='r' AND c.relpersistence='p' AND k.contype<>'n' ORDER BY k.conname COLLATE \"C\"",
          "SELECT (row_number() OVER (ORDER BY k.conname COLLATE \"C\"))::integer,k.conname,k.contype::text,pg_catalog.array_to_string(k.conkey,','),(k.convalidated AND k.conenforced AND NOT k.condeferrable AND NOT k.condeferred AND k.conislocal AND k.coninhcount=0 AND k.conparentid=0 AND k.contypid=0 AND NOT k.conperiod),CASE WHEN k.contype='f' THEN rn.nspname||'.'||rc.relname||'('||pg_catalog.array_to_string(k.confkey,',')||')' ELSE '-' END,CASE WHEN k.contype='f' THEN k.confupdtype::text||'/'||k.confdeltype::text||'/'||k.confmatchtype::text ELSE '-' END FROM pg_catalog.pg_constraint k JOIN pg_catalog.pg_class c ON c.oid=k.conrelid JOIN pg_catalog.pg_namespace n ON n.oid=c.relnamespace LEFT JOIN pg_catalog.pg_class rc ON rc.oid=k.confrelid LEFT JOIN pg_catalog.pg_namespace rn ON rn.oid=rc.relnamespace WHERE n.nspname='schubert' AND k.connamespace=n.oid AND c.relname='script_entries' AND c.relkind='r' AND c.relpersistence='p' AND k.contype<>'n' ORDER BY k.conname COLLATE \"C\"",
          "SELECT (row_number() OVER (ORDER BY k.conname COLLATE \"C\"))::integer,k.conname,k.contype::text,pg_catalog.array_to_string(k.conkey,','),(k.convalidated AND k.conenforced AND NOT k.condeferrable AND NOT k.condeferred AND k.conislocal AND k.coninhcount=0 AND k.conparentid=0 AND k.contypid=0 AND NOT k.conperiod),CASE WHEN k.contype='f' THEN rn.nspname||'.'||rc.relname||'('||pg_catalog.array_to_string(k.confkey,',')||')' ELSE '-' END,CASE WHEN k.contype='f' THEN k.confupdtype::text||'/'||k.confdeltype::text||'/'||k.confmatchtype::text ELSE '-' END FROM pg_catalog.pg_constraint k JOIN pg_catalog.pg_class c ON c.oid=k.conrelid JOIN pg_catalog.pg_namespace n ON n.oid=c.relnamespace LEFT JOIN pg_catalog.pg_class rc ON rc.oid=k.confrelid LEFT JOIN pg_catalog.pg_namespace rn ON rn.oid=rc.relnamespace WHERE n.nspname='schubert' AND k.connamespace=n.oid AND c.relname='audio_files' AND c.relkind='r' AND c.relpersistence='p' AND k.contype<>'n' ORDER BY k.conname COLLATE \"C\"",
          "SELECT (row_number() OVER (ORDER BY k.conname COLLATE \"C\"))::integer,k.conname,k.contype::text,pg_catalog.array_to_string(k.conkey,','),(k.convalidated AND k.conenforced AND NOT k.condeferrable AND NOT k.condeferred AND k.conislocal AND k.coninhcount=0 AND k.conparentid=0 AND k.contypid=0 AND NOT k.conperiod),CASE WHEN k.contype='f' THEN rn.nspname||'.'||rc.relname||'('||pg_catalog.array_to_string(k.confkey,',')||')' ELSE '-' END,CASE WHEN k.contype='f' THEN k.confupdtype::text||'/'||k.confdeltype::text||'/'||k.confmatchtype::text ELSE '-' END FROM pg_catalog.pg_constraint k JOIN pg_catalog.pg_class c ON c.oid=k.conrelid JOIN pg_catalog.pg_namespace n ON n.oid=c.relnamespace LEFT JOIN pg_catalog.pg_class rc ON rc.oid=k.confrelid LEFT JOIN pg_catalog.pg_namespace rn ON rn.oid=rc.relnamespace WHERE n.nspname='schubert' AND k.connamespace=n.oid AND c.relname='media_assets' AND c.relkind='r' AND c.relpersistence='p' AND k.contype<>'n' ORDER BY k.conname COLLATE \"C\"",
          "SELECT (row_number() OVER (ORDER BY k.conname COLLATE \"C\"))::integer,k.conname,k.contype::text,pg_catalog.array_to_string(k.conkey,','),(k.convalidated AND k.conenforced AND NOT k.condeferrable AND NOT k.condeferred AND k.conislocal AND k.coninhcount=0 AND k.conparentid=0 AND k.contypid=0 AND NOT k.conperiod),CASE WHEN k.contype='f' THEN rn.nspname||'.'||rc.relname||'('||pg_catalog.array_to_string(k.confkey,',')||')' ELSE '-' END,CASE WHEN k.contype='f' THEN k.confupdtype::text||'/'||k.confdeltype::text||'/'||k.confmatchtype::text ELSE '-' END FROM pg_catalog.pg_constraint k JOIN pg_catalog.pg_class c ON c.oid=k.conrelid JOIN pg_catalog.pg_namespace n ON n.oid=c.relnamespace LEFT JOIN pg_catalog.pg_class rc ON rc.oid=k.confrelid LEFT JOIN pg_catalog.pg_namespace rn ON rn.oid=rc.relnamespace WHERE n.nspname='schubert' AND k.connamespace=n.oid AND c.relname='entry_audio_links' AND c.relkind='r' AND c.relpersistence='p' AND k.contype<>'n' ORDER BY k.conname COLLATE \"C\"");
  private static final List<List<String>> DATA =
      List.of(
          List.of(
              "1\tck_speakers_id_n12\tc\t1\ttrue\t-\t-",
              "2\tck_speakers_name_bytes\tc\t3\ttrue\t-\t-",
              "3\tck_speakers_normalized_name_bytes\tc\t4\ttrue\t-\t-",
              "4\tfk_speakers_games_game_id\tf\t2\ttrue\tschubert.games(1)\ta/r/s",
              "5\tpk_speakers\tp\t1\ttrue\t-\t-",
              "6\tuq_speakers_game_normalized_name\tu\t2,4\ttrue\t-\t-",
              "7\tuq_speakers_id_game\tu\t1,2\ttrue\t-\t-"),
          List.of(
              "1\tck_script_files_byte_size\tc\t10\ttrue\t-\t-",
              "2\tck_script_files_chapter_title_bytes\tc\t8\ttrue\t-\t-",
              "3\tck_script_files_display_order_n12\tc\t3\ttrue\t-\t-",
              "4\tck_script_files_display_path_bytes\tc\t5\ttrue\t-\t-",
              "5\tck_script_files_file_name_bytes\tc\t6\ttrue\t-\t-",
              "6\tck_script_files_id_n12\tc\t1\ttrue\t-\t-",
              "7\tck_script_files_sha256\tc\t9\ttrue\t-\t-",
              "8\tck_script_files_storage_path_bytes\tc\t4\ttrue\t-\t-",
              "9\tck_script_files_storage_path_safe\tc\t4\ttrue\t-\t-",
              "10\tfk_script_files_games_game_id\tf\t2\ttrue\tschubert.games(1)\ta/r/s",
              "11\tpk_script_files\tp\t1\ttrue\t-\t-",
              "12\tuq_script_files_game_display_order\tu\t2,3\ttrue\t-\t-",
              "13\tuq_script_files_game_storage_path\tu\t2,4\ttrue\t-\t-",
              "14\tuq_script_files_id_game\tu\t1,2\ttrue\t-\t-"),
          List.of(
              "1\tck_script_entries_body_bytes\tc\t10\ttrue\t-\t-",
              "2\tck_script_entries_display_order_n12\tc\t4\ttrue\t-\t-",
              "3\tck_script_entries_entry_index\tc\t5\ttrue\t-\t-",
              "4\tck_script_entries_entry_type\tc\t7\ttrue\t-\t-",
              "5\tck_script_entries_id_n12\tc\t1\ttrue\t-\t-",
              "6\tck_script_entries_line_number\tc\t6\ttrue\t-\t-",
              "7\tck_script_entries_speaker_by_type\tc\t7,8\ttrue\t-\t-",
              "8\tck_script_entries_speaker_label_bytes\tc\t9\ttrue\t-\t-",
              "9\tfk_script_entries_games_game_id\tf\t2\ttrue\tschubert.games(1)\ta/r/s",
              "10\tfk_script_entries_script_files_file_game\tf\t3,2\ttrue\tschubert.script_files(1,2)\ta/c/s",
              "11\tfk_script_entries_speakers_speaker_game\tf\t8,2\ttrue\tschubert.speakers(1,2)\ta/r/s",
              "12\tpk_script_entries\tp\t1\ttrue\t-\t-",
              "13\tuq_script_entries_display_order\tu\t4\ttrue\t-\t-",
              "14\tuq_script_entries_file_entry_index\tu\t3,5\ttrue\t-\t-",
              "15\tuq_script_entries_id_game\tu\t1,2\ttrue\t-\t-"),
          List.of(
              "1\tck_audio_files_audio_role_bytes\tc\t7\ttrue\t-\t-",
              "2\tck_audio_files_basename_bytes\tc\t6\ttrue\t-\t-",
              "3\tck_audio_files_byte_size\tc\t10\ttrue\t-\t-",
              "4\tck_audio_files_display_path_bytes\tc\t4\ttrue\t-\t-",
              "5\tck_audio_files_duration_ms\tc\t9\ttrue\t-\t-",
              "6\tck_audio_files_file_name_bytes\tc\t5\ttrue\t-\t-",
              "7\tck_audio_files_id_n12\tc\t1\ttrue\t-\t-",
              "8\tck_audio_files_sha256\tc\t11\ttrue\t-\t-",
              "9\tck_audio_files_storage_path_bytes\tc\t3\ttrue\t-\t-",
              "10\tck_audio_files_storage_path_safe\tc\t3\ttrue\t-\t-",
              "11\tfk_audio_files_games_game_id\tf\t2\ttrue\tschubert.games(1)\ta/r/s",
              "12\tpk_audio_files\tp\t1\ttrue\t-\t-",
              "13\tuq_audio_files_game_storage_path\tu\t2,3\ttrue\t-\t-",
              "14\tuq_audio_files_id_game\tu\t1,2\ttrue\t-\t-"),
          List.of(
              "1\tck_media_assets_byte_size\tc\t10\ttrue\t-\t-",
              "2\tck_media_assets_category_bytes\tc\t5\ttrue\t-\t-",
              "3\tck_media_assets_display_order\tc\t16\ttrue\t-\t-",
              "4\tck_media_assets_display_path_bytes\tc\t8\ttrue\t-\t-",
              "5\tck_media_assets_file_name_bytes\tc\t9\ttrue\t-\t-",
              "6\tck_media_assets_id_n12\tc\t1\ttrue\t-\t-",
              "7\tck_media_assets_logical_id_bytes\tc\t2\ttrue\t-\t-",
              "8\tck_media_assets_media_type\tc\t3\ttrue\t-\t-",
              "9\tck_media_assets_mime_type\tc\t12\ttrue\t-\t-",
              "10\tck_media_assets_pair\tc\t3,14,15\ttrue\t-\t-",
              "11\tck_media_assets_section_bytes\tc\t6\ttrue\t-\t-",
              "12\tck_media_assets_sha256\tc\t11\ttrue\t-\t-",
              "13\tck_media_assets_storage_path_bytes\tc\t7\ttrue\t-\t-",
              "14\tck_media_assets_storage_path_safe\tc\t7\ttrue\t-\t-",
              "15\tck_media_assets_title_bytes\tc\t4\ttrue\t-\t-",
              "16\tfk_media_assets_media_assets_parent_logical_id\tf\t13\ttrue\tschubert.media_assets(2)\ta/r/s",
              "17\tpk_media_assets\tp\t1\ttrue\t-\t-",
              "18\tuq_media_assets_logical_id\tu\t2\ttrue\t-\t-",
              "19\tuq_media_assets_type_storage_path\tu\t3,7\ttrue\t-\t-"),
          List.of(
              "1\tck_entry_audio_links_display_order\tc\t5\ttrue\t-\t-",
              "2\tck_entry_audio_links_link_type\tc\t4\ttrue\t-\t-",
              "3\tfk_entry_audio_links_audio_files_audio_game\tf\t2,3\ttrue\tschubert.audio_files(1,2)\ta/r/s",
              "4\tfk_entry_audio_links_script_entries_entry_game\tf\t1,3\ttrue\tschubert.script_entries(1,2)\ta/c/s",
              "5\tpk_entry_audio_links\tp\t1,2,4\ttrue\t-\t-",
              "6\tuq_entry_audio_links_entry_type_order\tu\t1,4,5\ttrue\t-\t-"));

  @Test
  void constraint001SixQueriesSeventyFiveConstraintsAndExactResources() throws Exception {
    var f = new Fixture();
    verify(f);
    assertEquals(SQL, f.sql);
    assertEquals(List.of(7, 14, 15, 14, 19, 6), f.rows.stream().map(List::size).toList());
    assertEquals(COLUMNS, f.rows.stream().mapToInt(List::size).sum());
    assertEquals(COLUMNS * FIELDS, f.calls.stream().filter(c -> c.contains(":get")).count());
    assertEquals(List.of(30), f.timeouts);
    assertEquals(List.of(1000), f.fetchSizes);
    assertEquals(List.of(TABLES, 1), List.of(f.resultCloses, f.statementCloses));
    assertEquals(expectedCalls(), f.calls);
  }

  @Test
  void constraint002NullConnectionFailsBeforeIo() {
    var failure =
        assertThrows(
            IllegalArgumentException.class,
            () -> new MigrationMasterConstraintVerifier().verify(null));
    assertEquals("migration constraint input is invalid", failure.getMessage());
    assertNull(failure.getCause());
  }

  @Test
  void constraint003AutoCommitIsNotChangedOrUsed() {
    var f = new Fixture();
    f.auto = true;
    reject(f);
    assertEquals(List.of(AUTO), f.calls);
  }

  @Test
  void constraint004NullVendorStatementHasNoOwnedHandle() {
    var f = new Fixture();
    f.nullStatement = true;
    reject(f);
    assertEquals(List.of(AUTO, CREATE), f.calls);
    assertEquals(0, f.statementCloses);
  }

  @Test
  void constraint005EachNullResultClosesOnlyPreviousResults() {
    for (int table = 0; table < TABLES; table++) {
      var f = new Fixture();
      f.nullResult = table;
      reject(f);
      assertEquals(table, f.resultCloses);
      assertEquals(1, f.statementCloses);
      assertEquals(SQL.subList(0, table + 1), f.sql);
    }
  }

  @Test
  void constraint006AnyMissingDeclaredConstraintIsRejected() {
    for (int table = 0; table < TABLES; table++) {
      for (int column = 0; column < DATA.get(table).size(); column++) {
        var f = new Fixture();
        f.rows.get(table).remove(column);
        reject(f);
        assertEquals(SQL.subList(0, table + 1), f.sql);
        assertEquals(table + 1, f.resultCloses);
      }
    }
  }

  @Test
  void constraint007ExtraMetadataRowsAreNotReadAsAnotherConstraint() {
    for (int table = 0; table < TABLES; table++) {
      var f = new Fixture();
      f.rows.get(table).add(new ArrayList<>(f.rows.get(table).getFirst()));
      reject(f);
      assertEquals(
          DATA.get(table).size(),
          f.calls.stream().filter(c -> c.equals(key(f.lastQuery()) + ":getInt:1")).count());
      assertEquals(table + 1, f.resultCloses);
    }
  }

  @Test
  void constraint008NullZeroNegativeDuplicateAndWrongOrdinalsFail() {
    for (int table = 0; table < TABLES; table++) {
      for (String value : java.util.Arrays.asList(null, "0", "-1", "2147483647", "2")) {
        var f = new Fixture();
        f.rows.get(table).getFirst().set(0, value);
        reject(f);
        assertEquals(table + 1, f.resultCloses);
      }
      var duplicate = new Fixture();
      duplicate.rows.get(table).get(1).set(0, "1");
      reject(duplicate);
    }
  }

  @Test
  void constraint009EveryConstraintAttributeMismatchIsDetected() {
    for (int table = 0; table < TABLES; table++) {
      for (int row = 0; row < DATA.get(table).size(); row++) {
        for (int field = 1; field < FIELDS; field++) {
          var f = new Fixture();
          String old = f.rows.get(table).get(row).get(field);
          f.rows
              .get(table)
              .get(row)
              .set(field, field == 4 ? Boolean.toString(!Boolean.parseBoolean(old)) : old + "X");
          reject(f);
          assertEquals(table + 1, f.resultCloses);
          assertEquals(1, f.statementCloses);
        }
      }
    }
  }

  @Test
  void constraint010AllStringMetadataSqlNullsDifferFromEmptyFlags() {
    for (int table = 0; table < TABLES; table++) {
      for (int row = 0; row < DATA.get(table).size(); row++) {
        for (int field : List.of(1, 2, 3, 5, 6)) {
          var f = new Fixture();
          f.rows.get(table).get(row).set(field, null);
          reject(f);
          assertEquals(table + 1, f.resultCloses);
        }
      }
    }
  }

  @Test
  void constraint011SqlNullBooleanCannotMasqueradeAsFalse() throws Exception {
    for (int table = 0; table < TABLES; table++) {
      for (int row = 0; row < DATA.get(table).size(); row++) {
        var f = new Fixture();
        f.rows.get(table).get(row).set(4, null);
        reject(f);
      }
    }
    var normal = new Fixture();
    verify(normal);
    assertTrue(
        normal.rows.stream().flatMap(List::stream).allMatch(row -> "true".equals(row.get(4))));
  }

  @Test
  void constraint012EveryConstraintValidatedEnforcedLocalStatusIsRequired() {
    for (int table = 0; table < TABLES; table++) {
      for (int row = 0; row < DATA.get(table).size(); row++) {
        var f = new Fixture();
        var value = f.rows.get(table).get(row);
        value.set(4, Boolean.toString(!Boolean.parseBoolean(value.get(4))));
        reject(f);
      }
    }
  }

  @Test
  void constraint013ReferencedSchemaTableKeysAndNonForeignMarkerAreDistinct() {
    flagAlternatives(
        5,
        List.of(
            "",
            "-",
            "schubert.games(1)",
            "schubert.script_files(2,1)",
            "public.games(1)",
            "unknown"));
  }

  @Test
  void constraint014UpdateDeleteMatchActionsNeverCoerceOrDefault() {
    flagAlternatives(6, List.of("", "-", "a/r/s", "a/c/s", "r/r/s", "a/a/s", "a/r/f", "unknown"));
  }

  @Test
  void constraint015FixedStatusNamespaceAndColumnOrderPredicatesAreLiteral() {
    for (String query : SQL) {
      for (String predicate :
          List.of(
              "k.convalidated AND k.conenforced",
              "NOT k.condeferrable AND NOT k.condeferred",
              "k.conislocal AND k.coninhcount=0",
              "k.conparentid=0 AND k.contypid=0",
              "NOT k.conperiod",
              "k.connamespace=n.oid",
              "c.relkind='r' AND c.relpersistence='p'",
              "k.contype<>'n'",
              "ORDER BY k.conname COLLATE \"C\"")) assertTrue(query.contains(predicate));
    }
    var reverse = new Fixture();
    int index =
        DATA.get(2).stream()
            .map(row -> row.split("\\t", -1)[1])
            .toList()
            .indexOf("fk_script_entries_script_files_file_game");
    assertTrue(index >= 0);
    reverse.rows.get(2).get(index).set(3, "2,3");
    reject(reverse);
    var type = new Fixture();
    type.rows.getFirst().getFirst().set(2, "x");
    reject(type);
  }

  @Test
  void constraint016EveryJdbcEventSqlRuntimeAndErrorKeepsOwnership() throws Exception {
    var calls = expectedCalls();
    for (int index = 0; index < calls.size(); index++) {
      for (Throwable primary : failures()) {
        var f = new Fixture();
        f.failAt = index;
        f.failure = primary;
        assertFailure(f, primary, List.of());
        var expected = new ArrayList<>(calls.subList(0, index + 1));
        int active = -1;
        for (int event = 0; event <= index; event++) {
          String call = calls.get(event);
          if (call.endsWith(QUERY) && event != index)
            active = Integer.parseInt(call.substring(1, 2));
          if (call.endsWith(CLOSE)) active = -1;
        }
        if (active >= 0) expected.add(key(active) + CLOSE);
        if (index > 1 && !calls.get(index).equals(STATEMENT_CLOSE)) expected.add(STATEMENT_CLOSE);
        assertEquals(expected, f.calls);
        assertEquals(index > 1 ? 1 : 0, f.statementCloses);
        assertEquals(expected.stream().filter(c -> c.endsWith(CLOSE)).count(), f.resultCloses);
      }
    }
  }

  @Test
  void constraint017EveryResultCloseFailureStopsLaterQueries() throws Exception {
    for (int table = 0; table < TABLES; table++) {
      for (Throwable primary : failures()) {
        var f = new Fixture();
        f.resultFailureTable = table;
        f.resultFailure = primary;
        assertFailure(f, primary, List.of());
        assertEquals(SQL.subList(0, table + 1), f.sql);
        assertEquals(table + 1, f.resultCloses);
      }
    }
  }

  @Test
  void constraint018StatementCloseFailureCannotBecomeSuccess() throws Exception {
    for (Throwable primary : failures()) {
      var f = new Fixture();
      f.statementFailure = primary;
      assertFailure(f, primary, List.of());
      assertEquals(TABLES, f.resultCloses);
      assertEquals(1, f.statementCloses);
    }
  }

  @Test
  void constraint019AllFaultKindsPreserveResultThenStatementSuppression() throws Exception {
    for (int p = 0; p < 3; p++) {
      for (int rc = 0; rc < 3; rc++) {
        for (int sc = 0; sc < 3; sc++) {
          Throwable primary = failures().get(p);
          Throwable inner = failures().get(rc);
          Throwable outer = failures().get(sc);
          var f = readFailure(primary);
          f.resultFailureTable = 0;
          f.resultFailure = inner;
          f.statementFailure = outer;
          assertFailure(f, primary, List.of(inner, outer));
          assertEquals(List.of(1, 1), List.of(f.resultCloses, f.statementCloses));
        }
      }
    }
  }

  @Test
  void constraint020SamePrimaryAndEqualValuedDistinctCleanupIdentities() throws Exception {
    for (boolean closeOrigin : List.of(true, false)) {
      for (Throwable primary : failures()) {
        var f = closeOrigin ? new Fixture() : readFailure(primary);
        f.resultFailureTable = 0;
        f.resultFailure = primary;
        f.statementFailure = primary;
        assertFailure(f, primary, List.of());
      }
    }
    var primary = new EqualFailure();
    var cleanup = new EqualFailure();
    assertTrue(primary.equals(cleanup));
    var f = readFailure(primary);
    f.resultFailureTable = 0;
    f.resultFailure = cleanup;
    f.statementFailure = cleanup;
    assertFailure(f, primary, List.of(cleanup, cleanup));
  }

  @Test
  void constraint021RedactionFreshSuccessAndBorrowedConnectionContract() throws Exception {
    var verifier = new MigrationMasterConstraintVerifier();
    var bad = new Fixture();
    bad.nullStatement = true;
    var failure = assertThrows(SQLException.class, () -> verifier.verify(bad.connection()));
    assertEquals(DIAGNOSTIC, failure.getMessage());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
    var good = new Fixture();
    verifier.verify(good.connection());
    assertEquals(SQL, good.sql);
    assertEquals(List.of(AUTO, CREATE), good.connectionCalls);
    assertEquals("MigrationMasterConstraintVerifier[REDACTED]", verifier.toString());
  }

  @Test
  void constraint022FiniteSharedVerifierHasOnlyPerCallOwnedResources() throws Exception {
    var verifier = new MigrationMasterConstraintVerifier();
    var executor = Executors.newFixedThreadPool(WORKERS);
    try {
      var futures = new ArrayList<Future<Integer>>();
      for (int index = 0; index < TASKS; index++) {
        futures.add(
            executor.submit(
                () -> {
                  var f = new Fixture();
                  verifier.verify(f.connection());
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

  private static void verify(Fixture f) throws SQLException {
    new MigrationMasterConstraintVerifier().verify(f.connection());
  }

  private static void reject(Fixture f) {
    assertEquals(DIAGNOSTIC, assertThrows(SQLException.class, () -> verify(f)).getMessage());
  }

  private static void assertFailure(Fixture f, Throwable primary, List<Throwable> suppressed) {
    assertSame(primary, assertThrows(primary.getClass(), () -> verify(f)));
    assertEquals(suppressed.size(), primary.getSuppressed().length);
    for (int index = 0; index < suppressed.size(); index++)
      assertSame(suppressed.get(index), primary.getSuppressed()[index]);
  }

  private static Fixture readFailure(Throwable primary) {
    var f = new Fixture();
    f.failAt = expectedCalls().indexOf("q0:getInt:1");
    f.failure = primary;
    return f;
  }

  private static void flagAlternatives(int field, List<String> alternatives) {
    for (int table = 0; table < TABLES; table++) {
      for (int row = 0; row < DATA.get(table).size(); row++) {
        for (String flag : alternatives) {
          var f = new Fixture();
          if (flag.equals(f.rows.get(table).get(row).get(field))) continue;
          f.rows.get(table).get(row).set(field, flag);
          reject(f);
        }
      }
    }
  }

  private static List<Throwable> failures() {
    return List.of(
        new SQLException("synthetic sql"),
        new IllegalStateException("synthetic runtime"),
        new AssertionError("synthetic error"));
  }

  private static String key(int table) {
    return "q" + table;
  }

  private static List<String> expectedCalls() {
    var result = new ArrayList<>(List.of(AUTO, CREATE, TIMEOUT, FETCH));
    for (int table = 0; table < TABLES; table++) {
      String key = key(table);
      result.add(key + QUERY);
      for (int row = 0; row < DATA.get(table).size(); row++) {
        result.add(key + NEXT);
        result.add(key + ":getInt:1");
        result.add(key + WAS_NULL);
        result.add(key + ":getString:2");
        result.add(key + ":getString:3");
        result.add(key + ":getString:4");
        result.add(key + ":getBoolean:5");
        result.add(key + WAS_NULL);
        result.add(key + ":getString:6");
        result.add(key + ":getString:7");
      }
      result.add(key + NEXT);
      result.add(key + CLOSE);
    }
    result.add(STATEMENT_CLOSE);
    return result;
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
    final List<List<List<@Nullable String>>> rows = new ArrayList<>();
    final List<String> calls = new ArrayList<>();
    final List<String> sql = new ArrayList<>();
    final List<String> connectionCalls = new ArrayList<>();
    final List<Integer> timeouts = new ArrayList<>();
    final List<Integer> fetchSizes = new ArrayList<>();
    boolean auto;
    boolean nullStatement;
    int nullResult = -1;
    int resultFailureTable = -1;
    @Nullable Throwable resultFailure;
    @Nullable Throwable statementFailure;
    int failAt = -1;
    Throwable failure = new SQLException("synthetic primary");
    int query;
    int resultCloses;
    int statementCloses;

    Fixture() {
      for (var table : DATA) {
        var copied = new ArrayList<List<@Nullable String>>();
        for (String row : table) copied.add(new ArrayList<>(List.of(row.split("\t", -1))));
        rows.add(copied);
      }
    }

    int lastQuery() {
      return query - 1;
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
                    connectionCalls.add(AUTO);
                    hit(AUTO);
                    return auto;
                  }
                  case "createStatement" -> {
                    connectionCalls.add(CREATE);
                    hit(CREATE);
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
                    hit(TIMEOUT);
                    timeouts.add((Integer) args[0]);
                    return null;
                  }
                  case "setFetchSize" -> {
                    hit(FETCH);
                    fetchSizes.add((Integer) args[0]);
                    return null;
                  }
                  case "executeQuery" -> {
                    int table = query;
                    query++;
                    sql.add((String) args[0]);
                    hit(key(table) + QUERY);
                    return table == nullResult ? null : result(table);
                  }
                  case "close" -> {
                    statementCloses++;
                    hit(STATEMENT_CLOSE);
                    if (statementFailure != null) throw statementFailure;
                    return null;
                  }
                  default ->
                      throw new AssertionError(
                          "unexpected statement operation " + method.getName());
                }
              });
    }

    ResultSet result(int table) {
      int[] row = {-1};
      boolean[] wasNull = {false};
      String key = key(table);
      return (ResultSet)
          Proxy.newProxyInstance(
              ResultSet.class.getClassLoader(),
              new Class<?>[] {ResultSet.class},
              (proxy, method, args) -> {
                String name = method.getName();
                if (name.equals("next")) {
                  hit(key + NEXT);
                  row[0]++;
                  return row[0] < rows.get(table).size();
                }
                if (name.equals("wasNull")) {
                  hit(key + WAS_NULL);
                  return wasNull[0];
                }
                if (name.equals("close")) {
                  resultCloses++;
                  hit(key + CLOSE);
                  if (table == resultFailureTable && resultFailure != null) throw resultFailure;
                  return null;
                }
                if (List.of(GET_INT, GET_BOOLEAN, GET_STRING).contains(name)) {
                  int column = (Integer) args[0];
                  hit(key + ":" + name + ":" + column);
                  String value = rows.get(table).get(row[0]).get(column - 1);
                  wasNull[0] = value == null;
                  return switch (name) {
                    case GET_INT -> value == null ? 0 : Integer.parseInt(value);
                    case GET_BOOLEAN -> value != null && Boolean.parseBoolean(value);
                    default -> value;
                  };
                }
                throw new AssertionError("unexpected result operation " + name);
              });
    }
  }
}
