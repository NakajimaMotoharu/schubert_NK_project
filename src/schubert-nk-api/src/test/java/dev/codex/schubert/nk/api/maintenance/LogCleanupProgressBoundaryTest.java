package dev.codex.schubert.nk.api.maintenance;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.api.database.MigrationInventory;
import dev.codex.schubert.nk.api.logging.ApiLogDatabaseFixture;
import java.nio.file.Files;
import java.nio.file.Path;
import java.security.MessageDigest;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.HexFormat;
import java.util.List;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.Callable;
import java.util.concurrent.Executors;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** PT-DB-INBOX-153..160; BUG-104/SSC-051/PG-D-136; independent SQL/retention/lock oracles. */
final class LogCleanupProgressBoundaryTest {
  private static final String FIXTURE_2025_08_01_590D2F8C = "'2025-08-01'";
  private static final String FIXTURE_0_0_0_FALSE_DBD9596F = "0|0|0|false";
  private static final String FIXTURE_1_1_0_OK_A3F53FDF = "1|1|0|OK";
  private static final String FIXTURE_0_0_0_OK_B39BA730 = "0|0|0|OK";
  private static final String FIXTURE_0_0_0_LOCK_BUSY_61A41CE3 = "0|0|0|LOCK_BUSY";
  private static final String FIXTURE_SELECT_COUNT_FROM_BDA3EEC8 = "select count(*) from ";
  private static final String FIXTURE_LOGS_A0526482 = "logs";
  private static final String FIXTURE_LOG_PROGRESS_05F336FC = "log_progress";
  private static final String FIXTURE_NULL_F072CBEC = "null";
  private static final String FIXTURE_INSERT_INTO_11535B2F = "insert into ";
  private static final String FIXTURE_42501_719DF123 = "42501";
  @TempDir static Path root;
  private static ApiLogDatabaseFixture db;
  private static String url;
  private static final String RUN = new UUID(0, 94).toString();
  private static final String START = "'2026-09-17 00:00:00+00'::timestamptz";
  private static final String TABLE = "schubert.log_cleanup_progress";
  private static final List<String> CLEANUPS =
      List.of(
          "notifications",
          "questions",
          "sessions",
          "message_stores",
          FIXTURE_LOGS_A0526482,
          "batch_runs",
          "inbox_progress",
          FIXTURE_LOG_PROGRESS_05F336FC);

  @BeforeAll
  static void start() throws Exception {
    db = new ApiLogDatabaseFixture(root);
    try (var c = db.api()) {
      url = c.getMetaData().getURL();
    }
  }

  @AfterAll
  static void stop() throws Exception {
    if (db != null) db.stop();
  }

  @BeforeEach
  void reset() throws Exception {
    try (var c = db.admin()) {
      sql(c, "delete from " + TABLE);
      sql(c, "delete from schubert.app_logs");
      sql(c, "delete from schubert.batch_runs");
      for (String step : List.of("BACKUP_DB", "BACKUP_CONFIG"))
        sql(
            c,
            "insert into"
                + " schubert.batch_runs(run_id,business_date,step,attempt,started_at,ended_at,status)"
                + " values('"
                + RUN
                + "','2026-09-17','"
                + step
                + "',1,'2026-09-17','2026-09-17','SUCCESS')");
    }
  }

  @Test
  void heldPrefixCannotStarveLaterLogs() throws Exception {
    seedPrefix();
    try (var c = db.admin()) {
      c.setAutoCommit(false);
      var save = c.setSavepoint();
      sql(
          c,
          Files.readString(migrations().resolve("V013__cleanup_backup_and_retention_guards.sql")));
      assertEquals("2|0|2|OK", call(c, FIXTURE_LOGS_A0526482, 2));
      assertEquals("2|0|2|OK", call(c, FIXTURE_LOGS_A0526482, 2));
      assertEquals("1,2,3", ids(c));
      c.rollback(save);
      c.rollback();
    }
    try (var c = batch()) {
      assertEquals(FIXTURE_0_0_0_FALSE_DBD9596F, read(c));
      assertEquals("2|0|2|OK", call(c, FIXTURE_LOGS_A0526482, 2));
      assertEquals("2|0|2|false", read(c));
      assertEquals(FIXTURE_1_1_0_OK_A3F53FDF, call(c, FIXTURE_LOGS_A0526482, 2));
      assertEquals(FIXTURE_0_0_0_OK_B39BA730, call(c, FIXTURE_LOGS_A0526482, 2));
      assertEquals("3|1|2|true", read(c));
      assertEquals(FIXTURE_0_0_0_OK_B39BA730, call(c, FIXTURE_LOGS_A0526482, 2));
    }
    try (var c = db.admin()) {
      assertEquals("1,2", ids(c));
    }
  }

  @Test
  void cursorOrderCutoffAndReplay() throws Exception {
    try (var c = db.admin()) {
      log(c, 2, "'2026-06-18'", "'2026-06-19 00:00:00.000001+00'");
      log(c, 1, "'2026-06-18'", "'2026-06-19 00:00:00+00'");
      log(c, 3, "'2026-06-18 23:59:59.999999+00'", FIXTURE_NULL_F072CBEC);
      log(c, 4, "'2026-06-19 00:00:00+00'", FIXTURE_NULL_F072CBEC);
      log(c, 5, "'2026-06-19 00:00:00.000001+00'", FIXTURE_NULL_F072CBEC);
    }
    try (var c = batch();
        var admin = db.admin()) {
      assertEquals(FIXTURE_1_1_0_OK_A3F53FDF, call(c, FIXTURE_LOGS_A0526482, 1));
      assertEquals("1", cursor(admin));
      assertEquals("1|0|1|OK", call(c, FIXTURE_LOGS_A0526482, 1));
      assertEquals("2", cursor(admin));
      assertEquals(FIXTURE_1_1_0_OK_A3F53FDF, call(c, FIXTURE_LOGS_A0526482, 10000));
      assertEquals(FIXTURE_0_0_0_OK_B39BA730, call(c, FIXTURE_LOGS_A0526482, 10000));
      assertEquals("3|2|1|true", read(c));
      assertEquals("2,4,5", ids(admin));
      // New old log after END must wait for a new maintenance run, not rewind this one.
      log(admin, 6, "'2026-06-01'", FIXTURE_NULL_F072CBEC);
      assertEquals(FIXTURE_0_0_0_OK_B39BA730, call(c, FIXTURE_LOGS_A0526482, 1));
      assertEquals("2,4,5,6", ids(admin));
      String next = new UUID(0, 95).toString();
      sql(admin, "update schubert.batch_runs set run_id='" + next + "'");
      assertEquals(
          "2|1|1|OK",
          scalar(c, projection(FIXTURE_LOGS_A0526482) + "('" + next + "'," + START + ",10000)"));
      assertEquals("2,4,5", ids(admin));
    }
  }

  @Test
  void deletionAndProgressAreAtomic() throws Exception {
    seedPrefix();
    try (var c = batch();
        var admin = db.admin()) {
      c.setAutoCommit(false);
      assertEquals("3|1|2|OK", call(c, FIXTURE_LOGS_A0526482, 3));
      assertEquals("3|1|2|false", read(c));
      assertEquals("1,2,3", ids(admin));
      c.rollback();
      assertEquals(FIXTURE_0_0_0_FALSE_DBD9596F, read(c));
      assertEquals("1,2,3", ids(admin));
      var save = c.setSavepoint();
      assertEquals("3|1|2|OK", call(c, FIXTURE_LOGS_A0526482, 3));
      c.rollback(save);
      assertEquals(FIXTURE_0_0_0_FALSE_DBD9596F, read(c));
      assertEquals("3|1|2|OK", call(c, FIXTURE_LOGS_A0526482, 3));
      c.commit();
      try (var resumed = batch()) {
        assertEquals("3|1|2|false", read(resumed));
        assertEquals(FIXTURE_0_0_0_OK_B39BA730, call(resumed, FIXTURE_LOGS_A0526482, 1));
        assertEquals("3|1|2|true", read(resumed));
      }
    }
    reset();
    try (var c = db.admin()) {
      log(c, 1, "'2026-06-02'", FIXTURE_NULL_F072CBEC);
      sql(
          c,
          FIXTURE_INSERT_INTO_11535B2F
              + TABLE
              + "(run_id,cutoff,after_logged_at,after_id,target_count,deleted_count,skipped_count)"
              + " values('"
              + RUN
              + "',"
              + START
              + ",'2026-06-01',1,9223372036854775807,9223372036854775807,0)");
    }
    try (var c = batch()) {
      assertEquals(
          "22003",
          assertThrows(SQLException.class, () -> call(c, FIXTURE_LOGS_A0526482, 1)).getSQLState());
    }
    try (var c = db.admin()) {
      assertEquals("1", ids(c));
      assertEquals("9223372036854775807", scalar(c, "select target_count from " + TABLE));
    }
  }

  @Test
  void locksNeverSkipUnseenRows() throws Exception {
    seedPrefix();
    try (var owner = db.admin();
        var c = batch()) {
      owner.setAutoCommit(false);
      sql(c, "set statement_timeout='2s'");
      sql(owner, "select id from schubert.app_logs where id=1 for update");
      assertEquals(FIXTURE_0_0_0_LOCK_BUSY_61A41CE3, call(c, FIXTURE_LOGS_A0526482, 2));
      assertEquals("0", scalar(owner, FIXTURE_SELECT_COUNT_FROM_BDA3EEC8 + TABLE));
      owner.rollback();
      assertEquals("1|0|1|OK", call(c, FIXTURE_LOGS_A0526482, 1));
      sql(owner, "select id from schubert.app_logs where id=2 for update");
      assertEquals(FIXTURE_0_0_0_LOCK_BUSY_61A41CE3, call(c, FIXTURE_LOGS_A0526482, 2));
      assertEquals("1", cursor(owner));
      owner.rollback();
      sql(owner, "select run_id from " + TABLE + " for update");
      assertEquals(FIXTURE_0_0_0_LOCK_BUSY_61A41CE3, call(c, FIXTURE_LOGS_A0526482, 2));
      assertEquals("55P03", assertThrows(SQLException.class, () -> read(c)).getSQLState());
      owner.rollback();
    }
    try (var pool = Executors.newFixedThreadPool(8)) {
      var jobs = new ArrayList<Callable<String>>();
      for (int i = 0; i < 100; i++)
        jobs.add(
            () -> {
              try (var c = batch()) {
                return call(c, FIXTURE_LOGS_A0526482, 1);
              }
            });
      long counted = 0;
      for (var result : pool.invokeAll(jobs)) {
        String value = result.get();
        assertTrue(
            Set.of(
                    "1|0|1|OK",
                    FIXTURE_1_1_0_OK_A3F53FDF,
                    FIXTURE_0_0_0_OK_B39BA730,
                    FIXTURE_0_0_0_LOCK_BUSY_61A41CE3)
                .contains(value));
        counted += Long.parseLong(value.split("\\|")[0]);
      }
      try (var c = batch()) {
        for (int i = 0; i < 3; i++)
          counted += Long.parseLong(call(c, FIXTURE_LOGS_A0526482, 1).split("\\|")[0]);
        assertEquals(2, counted);
        assertEquals("3|1|2|true", read(c));
      }
    }
  }

  @Test
  void gatesRolesAndClosedReadProjection() throws Exception {
    try (var admin = db.admin();
        var c = batch()) {
      assertEquals(FIXTURE_0_0_0_FALSE_DBD9596F, read(c));
      for (String name : CLEANUPS) {
        int limit = name.equals(FIXTURE_LOGS_A0526482) ? 10000 : 1000;
        for (String bad :
            List.of(
                "null," + START + ",1",
                "'" + RUN + "',null,1",
                "'" + RUN + "','infinity',1",
                "'" + RUN + "','-infinity',1",
                "'" + RUN + "'," + START + ",null",
                "'" + RUN + "'," + START + ",0",
                "'" + RUN + "'," + START + "," + (limit + 1))) {
          assertEquals(
              "22023",
              assertThrows(SQLException.class, () -> scalar(c, projection(name) + "(" + bad + ")"))
                  .getSQLState());
        }
      }
      for (String step : List.of("BACKUP_DB", "BACKUP_CONFIG")) {
        sql(admin, "update schubert.batch_runs set status='FAILED' where step='" + step + "'");
        for (String name : CLEANUPS) assertEquals("0|0|0|BACKUP_GATE", call(c, name, 1));
        assertEquals("55000", assertThrows(SQLException.class, () -> read(c)).getSQLState());
        sql(admin, "update schubert.batch_runs set status='SUCCESS' where step='" + step + "'");
      }
      assertEquals(FIXTURE_0_0_0_OK_B39BA730, call(c, FIXTURE_LOGS_A0526482, 1));
      assertEquals(
          "55000",
          assertThrows(
                  SQLException.class,
                  () ->
                      scalar(
                          c,
                          "select complete from schubert.maintenance_read_log_cleanup_progress('"
                              + RUN
                              + "',"
                              + START
                              + "+interval '1 microsecond')"))
              .getSQLState());
      assertEquals(
          "55000",
          assertThrows(
                  SQLException.class,
                  () ->
                      scalar(
                          c,
                          projection(FIXTURE_LOGS_A0526482)
                              + "('"
                              + RUN
                              + "',"
                              + START
                              + "+interval '1 microsecond',1)"))
              .getSQLState());
      for (String args : List.of("null," + START, "'" + RUN + "',null", "'" + RUN + "','infinity'"))
        assertEquals(
            "22023",
            assertThrows(
                    SQLException.class,
                    () ->
                        scalar(
                            c,
                            "select complete from schubert.maintenance_read_log_cleanup_progress("
                                + args
                                + ")"))
                .getSQLState());
      try (var s = c.createStatement();
          var r =
              s.executeQuery(
                  "select target_count,deleted_count,skipped_count,complete from"
                      + " schubert.maintenance_read_log_cleanup_progress('"
                      + RUN
                      + "',"
                      + START
                      + ")")) {
        assertEquals(4, r.getMetaData().getColumnCount());
        for (int i = 1; i <= 4; i++)
          assertEquals(
              List.of("target_count", "deleted_count", "skipped_count", "complete").get(i - 1),
              r.getMetaData().getColumnName(i));
        assertTrue(r.next());
        assertTrue(r.getBoolean(4));
        assertFalse(r.next());
      }
      for (String role :
          List.of(
              "schubert_app",
              "schubert_batch",
              "schubert_inbox_inspector",
              "schubert_web_session",
              "schubert_ops_ro")) {
        try (var other = DriverManager.getConnection(url, role, "")) {
          assertEquals(
              FIXTURE_42501_719DF123,
              assertThrows(
                      SQLException.class,
                      () -> scalar(other, FIXTURE_SELECT_COUNT_FROM_BDA3EEC8 + TABLE))
                  .getSQLState());
        }
      }
      for (String role :
          List.of(
              "schubert_app",
              "schubert_inbox_inspector",
              "schubert_web_session",
              "schubert_ops_ro",
              "schubert_backup")) {
        try (var other = DriverManager.getConnection(url, role, "")) {
          assertEquals(
              FIXTURE_42501_719DF123,
              assertThrows(SQLException.class, () -> read(other)).getSQLState());
          assertEquals(
              FIXTURE_42501_719DF123,
              assertThrows(SQLException.class, () -> call(other, FIXTURE_LOG_PROGRESS_05F336FC, 1))
                  .getSQLState());
        }
      }
      try (var backup = DriverManager.getConnection(url, "schubert_backup", "")) {
        assertEquals("1", scalar(backup, FIXTURE_SELECT_COUNT_FROM_BDA3EEC8 + TABLE));
        assertEquals(
            FIXTURE_42501_719DF123,
            assertThrows(SQLException.class, () -> sql(backup, "delete from " + TABLE))
                .getSQLState());
      }
    }
  }

  @Test
  void progressConstraintsAndFailures() throws Exception {
    try (var c = db.admin()) {
      c.setAutoCommit(false);
      for (String zone : List.of("UTC", "Asia/Tokyo", "America/New_York")) {
        sql(c, "set timezone='" + zone + "'");
        String insert =
            FIXTURE_INSERT_INTO_11535B2F
                + TABLE
                + "(run_id,cutoff) values('"
                + RUN
                + "',"
                + START
                + ")";
        sql(c, insert);
        var save = c.setSavepoint();
        for (String change :
            List.of(
                "run_id=null",
                "cutoff=null",
                "target_count=null",
                "deleted_count=null",
                "skipped_count=null",
                "cutoff='infinity'",
                "cutoff='-infinity'",
                "target_count=-1",
                "deleted_count=-1",
                "skipped_count=-1",
                "deleted_count=1",
                "skipped_count=1",
                "after_id=1",
                "after_logged_at='2026-06-01'",
                "target_count=1,skipped_count=1",
                "target_count=1,skipped_count=1,after_id=0,after_logged_at='2026-06-01'",
                "target_count=1,skipped_count=1,after_id=1000000000000,after_logged_at='2026-06-01'",
                "target_count=1,skipped_count=1,after_id=1,after_logged_at='-infinity'",
                "target_count=1,skipped_count=1,after_id=1,after_logged_at='2026-06-19 00:00:00+00'",
                "completed_at='infinity'",
                "completed_at='-infinity'")) {
          String state =
              assertThrows(
                      SQLException.class,
                      () -> sql(c, "update " + TABLE + " set " + change),
                      change)
                  .getSQLState();
          assertTrue(Set.of("23502", "23514").contains(state));
          c.rollback(save);
        }
        assertEquals("23505", assertThrows(SQLException.class, () -> sql(c, insert)).getSQLState());
        c.rollback(save);
        sql(
            c,
            "update "
                + TABLE
                + " set after_logged_at='2026-06-18"
                + " 23:59:59.999999+00',after_id=999999999999,target_count=1,deleted_count=1,completed_at='2026-09-17'");
        assertEquals("1|1|0|true", read(c));
        c.rollback();
      }
    }
  }

  @Test
  void completedProgressRetention() throws Exception {
    try (var admin = db.admin();
        var c = batch()) {
      String[] ends = {
        "'2025-08-12 23:59:59.999999+00'",
        "'2025-08-13 00:00:00+00'",
        "'2025-08-13 00:00:00.000001+00'",
        FIXTURE_NULL_F072CBEC,
        FIXTURE_2025_08_01_590D2F8C,
        FIXTURE_2025_08_01_590D2F8C,
        FIXTURE_2025_08_01_590D2F8C,
        FIXTURE_2025_08_01_590D2F8C
      };
      for (int i = 0; i < ends.length; i++)
        sql(
            admin,
            FIXTURE_INSERT_INTO_11535B2F
                + TABLE
                + "(run_id,cutoff,completed_at) values('"
                + new UUID(0, 100 + i)
                + "',"
                + START
                + ","
                + ends[i]
                + ")");
      sql(
          admin,
          FIXTURE_INSERT_INTO_11535B2F
              + TABLE
              + "(run_id,cutoff,completed_at) values('"
              + RUN
              + "',"
              + START
              + ",'2025-08-01')");
      for (int i = 0; i < 2; i++)
        sql(
            admin,
            "insert into schubert.batch_runs(run_id,business_date,step,attempt,started_at,status)"
                + " values('"
                + new UUID(0, 104 + i)
                + "','2026-09-17','INVESTIGATE_"
                + i
                + "',1,'2026-09-17','"
                + (i == 0 ? "RUNNING" : "FAILED")
                + "')");
      admin.setAutoCommit(false);
      sql(
          admin,
          "select run_id from " + TABLE + " where run_id='" + new UUID(0, 106) + "' for update");
      c.setAutoCommit(false);
      assertEquals(FIXTURE_1_1_0_OK_A3F53FDF, call(c, FIXTURE_LOG_PROGRESS_05F336FC, 1));
      c.rollback();
      assertEquals("2|2|0|OK", call(c, FIXTURE_LOG_PROGRESS_05F336FC, 1000));
      c.commit();
      assertEquals("7", scalar(admin, FIXTURE_SELECT_COUNT_FROM_BDA3EEC8 + TABLE));
      admin.rollback();
      assertEquals(FIXTURE_1_1_0_OK_A3F53FDF, call(c, FIXTURE_LOG_PROGRESS_05F336FC, 1000));
      c.commit();
      assertEquals("6", scalar(admin, FIXTURE_SELECT_COUNT_FROM_BDA3EEC8 + TABLE));
      assertEquals(FIXTURE_0_0_0_OK_B39BA730, call(c, FIXTURE_LOG_PROGRESS_05F336FC, 1000));
      c.rollback();
    }
  }

  @Test
  void appendOnlyInventoryAndCrossCleanup() throws Exception {
    assertEquals(
        "d56446bcfb7b3fa74ad0939baa3e2c0d263dd8a975cb7e3a9ce06bac2be85a74",
        HexFormat.of()
            .formatHex(
                MessageDigest.getInstance("SHA-256")
                    .digest(
                        Files.readAllBytes(
                            migrations()
                                .resolve("V013__cleanup_backup_and_retention_guards.sql")))));
    try (var c = db.admin()) {
      assertEquals(
          MigrationInventory.CSV,
          scalar(
              c,
              "select string_agg(version,',' order by installed_rank) from"
                  + " schubert_meta.flyway_schema_history where success and version is not null"));
      assertEquals(
          "159|23|30|24|1",
          scalar(
              c,
              "select count(*) filter(where contype='c')||'|'||count(*) filter(where"
                  + " contype='f')||'|'||count(*) filter(where contype='u')||'|'||count(*)"
                  + " filter(where contype='p')||'|'||count(*) filter(where contype='t') from"
                  + " pg_constraint c join pg_namespace n on n.oid=c.connamespace where n.nspname"
                  + " in ('schubert','schubert_web_session')"));
      assertEquals(
          "run_id,cutoff,after_logged_at,after_id,target_count,deleted_count,skipped_count,completed_at",
          scalar(
              c,
              "select string_agg(column_name,',' order by ordinal_position) from"
                  + " information_schema.columns where table_schema='schubert' and"
                  + " table_name='log_cleanup_progress'"));
      for (String signature :
          List.of(
              "maintenance_cleanup_logs(uuid,timestamptz,integer)",
              "maintenance_read_log_cleanup_progress(uuid,timestamptz)",
              "maintenance_cleanup_log_progress(uuid,timestamptz,integer)")) {
        assertEquals(
            "nk_owner|true|search_path=pg_catalog, schubert, schubert_web_session|TimeZone=UTC",
            scalar(
                c,
                "select"
                    + " pg_get_userbyid(proowner)||'|'||prosecdef||'|'||array_to_string(proconfig,'|')"
                    + " from pg_proc where oid='schubert."
                    + signature
                    + "'::regprocedure"));
        assertEquals(
            "false|true",
            scalar(
                c,
                "select has_function_privilege('public','schubert."
                    + signature
                    + "','EXECUTE')||'|'||has_function_privilege('schubert_batch','schubert."
                    + signature
                    + "','EXECUTE')"));
      }
      // Other cleanup predicates/hold regimes are independently covered by PT089..096 and073..080.
      // This test additionally proves this table grants neither a log projection nor a generic
      // delete.
      assertEquals(
          "0",
          scalar(
              c,
              "select count(*) from information_schema.role_table_grants where"
                  + " table_schema='schubert' and table_name='log_cleanup_progress' and grantee in"
                  + " ('schubert_app','schubert_batch','schubert_inbox_inspector','PUBLIC')"));
    }
  }

  private static void seedPrefix() throws SQLException {
    try (var c = db.admin()) {
      log(c, 1, "'2026-06-01'", "'2026-10-01'");
      log(c, 2, "'2026-06-02'", "'2026-10-01'");
      log(c, 3, "'2026-06-03'", FIXTURE_NULL_F072CBEC);
    }
  }

  private static void log(Connection c, int id, String at, String hold) throws SQLException {
    sql(
        c,
        "insert into"
            + " schubert.app_logs(id,logged_at,service,category,level,action,message,security_hold_until)"
            + " values("
            + id
            + ","
            + at
            + ",'API','SECURITY','INFO','PUBLIC_TEST','public fixture',"
            + hold
            + ")");
  }

  private static Connection batch() throws SQLException {
    return DriverManager.getConnection(url, "schubert_batch", "");
  }

  private static void sql(Connection c, String query) throws SQLException {
    try (var s = c.createStatement()) {
      s.execute(query);
    }
  }

  private static String scalar(Connection c, String query) throws SQLException {
    try (var s = c.createStatement();
        var r = s.executeQuery(query)) {
      assertTrue(r.next());
      String value = r.getString(1);
      assertNotNull(value);
      assertFalse(r.next());
      return value;
    }
  }

  private static String projection(String suffix) {
    return "select target_count||'|'||deleted_count||'|'||skipped_count||'|'||reason_code from"
        + " schubert.maintenance_cleanup_"
        + suffix;
  }

  private static String call(Connection c, String suffix, int limit) throws SQLException {
    return scalar(c, projection(suffix) + "('" + RUN + "'," + START + "," + limit + ")");
  }

  private static String read(Connection c) throws SQLException {
    return scalar(
        c,
        "select target_count||'|'||deleted_count||'|'||skipped_count||'|'||complete from"
            + " schubert.maintenance_read_log_cleanup_progress('"
            + RUN
            + "',"
            + START
            + ")");
  }

  private static String ids(Connection c) throws SQLException {
    return scalar(
        c, "select coalesce(string_agg(id::text,',' order by id),'empty') from schubert.app_logs");
  }

  private static String cursor(Connection c) throws SQLException {
    return scalar(c, "select after_id from " + TABLE + " where run_id='" + RUN + "'");
  }

  private static Path migrations() {
    return Path.of(System.getProperty("nk.pt.repository"))
        .resolve("src/schubert-nk-api/src/main/resources/db/migration");
  }
}
