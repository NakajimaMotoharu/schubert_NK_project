package dev.codex.schubert.nk.api.maintenance;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assertions.fail;

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
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import org.flywaydb.core.Flyway;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** NK-DAT-001; PT-DB-INBOX-089..096; UI251; SS331/332/341; SSC-050; BUG-092/093. */
final class CleanupSafetyBoundaryTest {
  @TempDir static Path root;
  private static ApiLogDatabaseFixture db;
  private static String url;
  private static final String RUN = new UUID(0, 81).toString();
  private static final String START = "'2026-09-17 00:00:00+00'::timestamptz";
  private static final List<String> NAMES =
      List.of(
          "notifications",
          "questions",
          "sessions",
          "logs",
          "batch_runs",
          "message_stores",
          "log_progress",
          "inbox_progress");

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
      for (String table :
          List.of(
              "notifications",
              "questions",
              "auth_sessions",
              "login_ip_attempts",
              "app_logs",
              "request_inbox",
              "mq_outbox",
              "inbox_inspection_progress",
              "log_cleanup_progress",
              "batch_runs")) sql(c, "delete from schubert." + table);
      sql(c, "delete from schubert_web_session.web_http_sessions");
      sql(c, "delete from schubert_web_session.web_log_outbox");
      sql(
          c,
          "insert into"
              + " schubert.app_users(id,username,username_key,password_hash,role,status,password_changed_at,created_at,updated_at)"
              + " values(7,'Learner','learner','synthetic-unused','USER','ACTIVE','2026-09-01','2026-09-01','2026-09-01')"
              + " on conflict(id) do nothing");
      backup(c, "BACKUP_DB");
      backup(c, "BACKUP_CONFIG");
    }
  }

  @Test
  void backupMatrixAndLegacyCounterexample() throws Exception {
    try (var c = db.admin()) {
      c.setAutoCommit(false);
      for (String name : NAMES) {
        assertEquals("0|0|0|OK", call(c, name, START, 1));
        for (String step : List.of("BACKUP_DB", "BACKUP_CONFIG"))
          for (String mutation :
              List.of(
                  "update schubert.batch_runs set status='RUNNING'",
                  "update schubert.batch_runs set status='WARNING'",
                  "update schubert.batch_runs set status='FAILED'",
                  "update schubert.batch_runs set status='SKIPPED'",
                  "update schubert.batch_runs set business_date='2026-09-16'",
                  "update schubert.batch_runs set business_date='2026-09-18'",
                  "update schubert.batch_runs set ended_at=null",
                  "update schubert.batch_runs set run_id='00000000-0000-0000-0000-000000000082'",
                  "delete from schubert.batch_runs")) {
            var save = c.setSavepoint();
            sql(c, mutation + " where step='" + step + "'");
            String before =
                scalar(
                    c,
                    "select md5(string_agg(row_to_json(b)::text,',' order by id)) from"
                        + " schubert.batch_runs b");
            assertEquals(
                "0|0|0|BACKUP_GATE", call(c, name, START, 1), name + ":" + step + ":" + mutation);
            assertEquals(
                before,
                scalar(
                    c,
                    "select md5(string_agg(row_to_json(b)::text,',' order by id)) from"
                        + " schubert.batch_runs b"));
            c.rollback(save);
          }
      }
      // Actual pre-fix V006, in a rollback-only isolated fixture database.
      var save = c.setSavepoint();
      sql(
          c,
          Files.readString(
              migrations().resolve("V006__cleanup_null_bounds_and_outbox_retention.sql")));
      sql(c, "update schubert.batch_runs set business_date='2026-09-16',ended_at=null");
      for (String name : NAMES.subList(0, 5))
        assertEquals("0|0|0|OK", call(c, name, START, 1), "BUG-092 legacy counterexample " + name);
      c.rollback(save);
      sql(c, "update schubert.batch_runs set business_date='2026-09-16',ended_at=null");
      for (String name : NAMES) assertEquals("0|0|0|BACKUP_GATE", call(c, name, START, 1));
      c.rollback();
    }
  }

  @Test
  void backupLocksAndSnapshotRace() throws Exception {
    for (String name : NAMES) {
      try (var owner = db.admin();
          var caller = batch()) {
        owner.setAutoCommit(false);
        caller.setAutoCommit(false);
        scalar(owner, "select pg_try_advisory_xact_lock(71419602)::text");
        assertEquals("0|0|0|LOCK_BUSY", call(caller, name, START, 1));
        owner.rollback();
        caller.rollback();
        assertEquals("0|0|0|OK", call(caller, name, START, 1));
        for (String step : List.of("BACKUP_DB", "BACKUP_CONFIG")) {
          var save = owner.setSavepoint();
          assertEquals(
              "55P03",
              assertThrows(
                      SQLException.class,
                      () ->
                          scalar(
                              owner,
                              "select id from schubert.batch_runs where step='"
                                  + step
                                  + "' for update nowait"))
                  .getSQLState());
          owner.rollback(save);
        }
        caller.rollback();
        assertEquals(
            "2",
            scalar(
                owner,
                "select count(*) from (select id from schubert.batch_runs for update nowait) b"));
        owner.rollback();
      }
      try (var writer = db.admin();
          var caller = batch();
          var pool = Executors.newSingleThreadExecutor()) {
        sql(writer, "delete from schubert.batch_runs where step='BACKUP_CONFIG'");
        writer.setAutoCommit(false);
        scalar(writer, "select id from schubert.batch_runs where step='BACKUP_DB' for update");
        int pid = Integer.parseInt(scalar(caller, "select pg_backend_pid()"));
        var result = pool.submit(() -> call(caller, name, START, 1));
        try {
          awaitBlocked(pid);
          try (var other = db.admin()) {
            backup(other, "BACKUP_CONFIG");
          }
        } finally {
          writer.commit();
        }
        assertEquals("0|0|0|BACKUP_GATE", result.get(5, TimeUnit.SECONDS));
        assertEquals("0|0|0|OK", call(caller, name, START, 1));
      }
    }
  }

  @Test
  void invalidInputsAndTimezone() throws Exception {
    try (var c = batch()) {
      for (String name : NAMES) {
        int max = name.equals("logs") ? 10000 : 1000;
        for (String args :
            List.of(
                "null," + START + ",1",
                "'" + RUN + "',null,1",
                "'" + RUN + "','infinity',1",
                "'" + RUN + "','-infinity',1",
                "'" + RUN + "'," + START + ",null",
                "'" + RUN + "'," + START + ",0",
                "'" + RUN + "'," + START + "," + (max + 1),
                "'" + RUN + "'," + START + ",-2147483648",
                "'" + RUN + "'," + START + ",2147483647"))
          assertEquals(
              "22023",
              assertThrows(
                      SQLException.class,
                      () -> scalar(c, "select count(*) from " + function(name) + "(" + args + ")"))
                  .getSQLState());
        for (String zone : List.of("UTC", "America/Los_Angeles", "Asia/Tokyo")) {
          sql(c, "set timezone='" + zone + "'");
          assertEquals("0|0|0|OK", call(c, name, "'2026-09-16 17:00:00-07'::timestamptz", max));
          assertEquals(
              "0|0|0|BACKUP_GATE",
              call(c, name, "'2026-09-16 14:59:59.999999+00'::timestamptz", 1));
        }
      }
    }
  }

  @Test
  void rolesInventoryAndImmutableHistory() throws Exception {
    try (var c = db.admin()) {
      for (String name : NAMES) {
        String sig = function(name) + "(uuid,timestamptz,integer)";
        assertEquals(
            "nk_owner|true|search_path=pg_catalog, schubert, schubert_web_session|TimeZone=UTC",
            scalar(
                c,
                "select"
                    + " pg_get_userbyid(proowner)||'|'||prosecdef||'|'||array_to_string(proconfig,'|')"
                    + " from pg_proc where oid='"
                    + sig
                    + "'::regprocedure"));
        assertEquals(
            "true",
            scalar(
                c,
                "select has_function_privilege('schubert_batch','" + sig + "','EXECUTE')::text"));
        assertEquals(
            "false",
            scalar(c, "select has_function_privilege('public','" + sig + "','EXECUTE')::text"));
        for (String role :
            List.of(
                "schubert_app",
                "schubert_web_session",
                "schubert_backup",
                "schubert_ops_ro",
                "schubert_inbox_inspector"))
          try (var denied = DriverManager.getConnection(url, role, "")) {
            assertEquals(
                "1", scalar(c, "select count(*) from pg_roles where rolname='" + role + "'"));
            assertEquals(
                "42501",
                assertThrows(SQLException.class, () -> call(denied, name, START, 1)).getSQLState());
          }
        c.setAutoCommit(false);
        for (String setting : List.of("timezone='Asia/Tokyo'", "statement_timeout='1s'")) {
          sql(c, "alter function " + sig + " set " + setting);
          assertEquals(
              "false",
              scalar(
                  c,
                  "select (proconfig=array['search_path=pg_catalog, schubert,"
                      + " schubert_web_session','TimeZone=UTC'])::text from pg_proc where oid='"
                      + sig
                      + "'::regprocedure"));
          c.rollback();
        }
        c.setAutoCommit(true);
      }
      assertEquals(
          MigrationInventory.CSV,
          scalar(
              c,
              "select string_agg(version,',' order by installed_rank) from"
                  + " schubert_meta.flyway_schema_history where success and version is not null"));
    }
    var flyway =
        Flyway.configure()
            .dataSource(url, "schubert_migration", "")
            .defaultSchema("schubert_meta")
            .schemas("schubert_meta")
            .initSql("SET ROLE nk_owner")
            .locations("filesystem:" + migrations())
            .cleanDisabled(true)
            .load();
    assertTrue(flyway.validateWithResult().validationSuccessful);
    assertEquals(0, flyway.migrate().migrationsExecuted);
    // V001..011 hashes are independent fixed vectors in older boundary PT; add V012 here.
    assertEquals(
        "21e4c781a4b4c1a18240d8e47fae5bc2d11593d7b4ad05590ed10a67ebcb9411",
        HexFormat.of()
            .formatHex(
                MessageDigest.getInstance("SHA-256")
                    .digest(
                        Files.readAllBytes(
                            migrations().resolve("V012__durable_inbox_inspection_progress.sql")))));
  }

  @Test
  void rollbackAndRowLocks() throws Exception {
    try (var c = db.admin();
        var caller = batch()) {
      log(c, 1, "'2026-01-01'", "null");
      log(c, 2, "'2026-01-01'", "null");
      c.setAutoCommit(false);
      caller.setAutoCommit(false);
      scalar(c, "select id from schubert.app_logs where id=1 for update");
      assertEquals("0|0|0|LOCK_BUSY", call(caller, "logs", START, 10000));
      assertEquals("0", scalar(c, "select count(*) from schubert.log_cleanup_progress"));
      assertEquals("1,2", ids(c, "app_logs"));
      assertEquals(
          "42501", assertThrows(SQLException.class, () -> ids(caller, "app_logs")).getSQLState());
      caller.rollback();
      c.rollback();
      assertEquals("1,2", ids(c, "app_logs"));
      assertEquals("1|1|0|OK", call(caller, "logs", START, 1));
      caller.rollback();
      sql(
          c,
          "create function schubert.pt_cleanup_failure() returns trigger language plpgsql as $$"
              + " begin raise exception using errcode='P0001',message='public fault'; end $$");
      sql(
          c,
          "create trigger pt_cleanup_failure before delete on schubert.app_logs for each row"
              + " execute function schubert.pt_cleanup_failure()");
      c.commit();
      assertEquals(
          "P0001",
          assertThrows(SQLException.class, () -> call(caller, "logs", START, 10000)).getSQLState());
      caller.rollback();
      assertEquals("1,2", ids(c, "app_logs"));
      sql(c, "drop trigger pt_cleanup_failure on schubert.app_logs");
      sql(c, "drop function schubert.pt_cleanup_failure()");
      c.commit();
      assertEquals("2|2|0|OK", call(caller, "logs", START, 10000));
      caller.commit();
      assertEquals("0|0|0|OK", call(caller, "logs", START, 10000));
      caller.rollback();
    }
  }

  @Test
  void businessAndSessionBoundaries() throws Exception {
    try (var c = db.admin()) {
      c.setAutoCommit(false);
      List<String> states = List.of("RECEIVED", "PROCESSING", "COMPLETED", "ERROR", "CANCELLED");
      int id = 0;
      var expected = new ArrayList<String>();
      for (String state : states)
        for (String changed :
            List.of(
                "'2026-09-15 23:59:59.999999+00'",
                "'2026-09-16 00:00:00+00'",
                "'2026-09-16 00:00:00.000001+00'",
                START,
                "'2026-09-17 00:00:00.000001+00'")) {
          id++;
          question(c, id, true, "'2026-09-01'");
          notification(c, id, state, changed);
          boolean deleted =
              state.equals("CANCELLED")
                  ? id % 5 >= 1 && id % 5 <= 3
                  : (state.equals("COMPLETED") || state.equals("ERROR"))
                      && (id % 5 == 1 || id % 5 == 2);
          if (!deleted) expected.add(Integer.toString(id));
        }
      assertEquals("7|7|0|OK", call(c, "notifications", START, 1000));
      assertEquals(String.join(",", expected), ids(c, "notifications"));
      assertEquals("7|7|0|OK", call(c, "questions", START, 1000));
      assertEquals(String.join(",", expected), ids(c, "questions"));
      assertEquals("18", scalar(c, "select count(*) from schubert.async_jobs"));
      question(c, 30, false, "null");
      question(c, 31, true, START);
      question(c, 32, true, "'2026-09-17 00:00:00.000001+00'");
      assertEquals("0|0|0|OK", call(c, "questions", START, 1000));
      c.rollback();

      for (int i = 1; i <= 3; i++) {
        String expiry =
            List.of(
                    "'2026-09-15 23:59:59.999999+00'",
                    "'2026-09-16 00:00:00+00'",
                    "'2026-09-16 00:00:00.000001+00'")
                .get(i - 1);
        sql(
            c,
            "insert into"
                + " schubert.auth_sessions(id,user_id,context_hash,context_ciphertext,key_version,issued_at,last_accessed_at,expires_at,client_address,created_message_id)"
                + " values('"
                + new UUID(0, i)
                + "',7,lpad('"
                + i
                + "',64,'0'),decode(repeat('00',30),'hex'),'v1','2026-09-01','2026-09-01',"
                + expiry
                + ",'127.0.0.1','"
                + new UUID(1, i)
                + "')");
        String window =
            List.of(
                    "'2026-09-15 23:44:59.999999+00'",
                    "'2026-09-15 23:45:00+00'",
                    "'2026-09-15 23:45:00.000001+00'")
                .get(i - 1);
        sql(
            c,
            "insert into schubert.login_ip_attempts values('127.0.0."
                + i
                + "',1,"
                + window
                + ",null,"
                + window
                + ")");
        String webExpiry =
            List.of("'2026-09-16 23:59:59.999999+00'", START, "'2026-09-17 00:00:00.000001+00'")
                .get(i - 1);
        sql(
            c,
            "insert into schubert_web_session.web_http_sessions values('"
                + new UUID(0, i)
                + "',lpad('"
                + i
                + "',64,'0'),decode(repeat('00',30),'hex'),'v1','2026-09-01','2026-09-01',"
                + webExpiry
                + ",28800,0)");
      }
      assertEquals("2|2|0|OK", call(c, "sessions", START, 2));
      assertEquals(
          "1|3|3",
          scalar(
              c,
              "select (select count(*) from schubert.auth_sessions)||'|'||(select count(*) from"
                  + " schubert.login_ip_attempts)||'|'||(select count(*) from"
                  + " schubert_web_session.web_http_sessions)"));
      assertEquals("3|3|0|OK", call(c, "sessions", START, 3));
      assertEquals(
          "1|1|2",
          scalar(
              c,
              "select (select count(*) from schubert.auth_sessions)||'|'||(select count(*) from"
                  + " schubert.login_ip_attempts)||'|'||(select count(*) from"
                  + " schubert_web_session.web_http_sessions)"));
      assertEquals("1|1|0|OK", call(c, "sessions", START, 1000));
      assertEquals("0|0|0|OK", call(c, "sessions", START, 1000));
      // Independent revocation/lock-window matrix, not just expiry.
      for (String time :
          List.of(
              "'2026-09-15 23:59:59.999999+00'",
              "'2026-09-16 00:00:00+00'",
              "'2026-09-16 00:00:00.000001+00'")) {
        var save = c.setSavepoint();
        sql(
            c,
            "update schubert.auth_sessions set expires_at='2026-10-01',revoked=true,revoked_at="
                + time
                + ",revoke_reason='LOGOUT'");
        sql(
            c,
            "update schubert.login_ip_attempts set window_started_at='2026-09-01',locked_until="
                + time);
        boolean expired = !time.contains(".000001");
        assertEquals(expired ? "2|2|0|OK" : "0|0|0|OK", call(c, "sessions", START, 1000));
        assertEquals(
            expired ? "0|0|1" : "1|1|1",
            scalar(
                c,
                "select (select count(*) from schubert.auth_sessions)||'|'||(select count(*) from"
                    + " schubert.login_ip_attempts)||'|'||(select count(*) from"
                    + " schubert_web_session.web_http_sessions)"));
        c.rollback(save);
      }
      sql(
          c,
          "update schubert.login_ip_attempts set"
              + " window_started_at='2026-09-17',locked_until='2026-09-01'");
      assertEquals(
          "0|0|0|OK",
          call(c, "sessions", START, 1000),
          "active window protects even when old lock expired");
      c.rollback();
    }
  }

  @Test
  void logRetentionAndHold() throws Exception {
    try (var c = db.admin()) {
      c.setAutoCommit(false);
      log(c, 1, "'2026-06-18 23:59:59.999999+00'", "null");
      log(c, 2, "'2026-06-19 00:00:00+00'", "null");
      log(c, 3, "'2026-06-19 00:00:00.000001+00'", "null");
      log(c, 4, "'2026-10-01'", "null");
      log(c, 5, "'2026-06-18'", "'2026-06-18 23:59:59.999999+00'");
      log(c, 6, "'2026-06-18'", "'2026-06-19 00:00:00+00'");
      log(c, 7, "'2026-06-18'", "'2026-06-19 00:00:00.000001+00'");
      var save = c.setSavepoint();
      assertEquals("4|3|1|OK", call(c, "logs", START, 10000));
      assertEquals("2,3,4,7", ids(c, "app_logs"));
      assertEquals("0|0|0|OK", call(c, "logs", START, 10000)); // SSC-051: hold already counted.
      c.rollback(save);
      assertEquals("1,2,3,4,5,6,7", ids(c, "app_logs"));
      assertEquals("2|2|0|OK", call(c, "logs", START, 2));
      assertEquals("1,2,3,4,7", ids(c, "app_logs"));
      c.rollback(save);
      sql(
          c,
          Files.readString(
              migrations().resolve("V006__cleanup_null_bounds_and_outbox_retention.sql")));
      assertEquals(
          "6|6|0|OK",
          call(c, "logs", START, 10000),
          "BUG-093 old run-anchor oracle deletes 90-day rows");
      assertEquals("4", ids(c, "app_logs"));
      c.rollback();
    }
  }

  @Test
  void batchCompletionRetention() throws Exception {
    try (var c = db.admin()) {
      c.setAutoCommit(false);
      history(c, 101, 101, "SUCCESS", "'2025-08-12 23:59:59.999999+00'");
      history(c, 102, 102, "WARNING", "'2025-08-13 00:00:00+00'");
      history(c, 103, 103, "SKIPPED", "'2025-08-13 00:00:00.000001+00'");
      history(c, 104, 104, "SUCCESS", "'2026-09-01'");
      history(c, 105, 105, "RUNNING", "null");
      history(c, 106, 106, "FAILED", "'2025-08-01'");
      history(c, 107, 106, "SUCCESS", "'2025-08-01'");
      history(c, 108, 105, "WARNING", "'2025-08-01'");
      history(c, 109, 109, "SUCCESS", "null");
      history(c, 110, 110, "WARNING", "'2025-08-01'");
      history(c, 111, 111, "SKIPPED", "'2025-08-01'");
      history(c, 112, 81, "SUCCESS", "'2025-08-01'");
      var save = c.setSavepoint();
      assertEquals("2|2|0|OK", call(c, "batch_runs", START, 2));
      assertEquals("101,102,103,104,105,106,107,108,109,112", historyIds(c));
      assertEquals("1|1|0|OK", call(c, "batch_runs", START, 1000));
      assertEquals("102,103,104,105,106,107,108,109,112", historyIds(c));
      assertEquals("0|0|0|OK", call(c, "batch_runs", START, 1000));
      c.rollback(save);
      sql(
          c,
          Files.readString(
              migrations().resolve("V006__cleanup_null_bounds_and_outbox_retention.sql")));
      assertEquals(
          "9|9|0|OK",
          call(c, "batch_runs", "'2025-08-13 00:00:00+00'", 1000),
          "BUG-093 old started_at/caller-cutoff deletes recent completions");
      assertEquals("105,106,112", historyIds(c));
      c.rollback();
    }
  }

  private static Connection batch() throws SQLException {
    return DriverManager.getConnection(url, "schubert_batch", "");
  }

  private static String function(String name) {
    return "schubert.maintenance_cleanup_" + name;
  }

  private static String call(Connection c, String name, String cutoff, int limit)
      throws SQLException {
    return scalar(
        c,
        "select target_count||'|'||deleted_count||'|'||skipped_count||'|'||reason_code from "
            + function(name)
            + "('"
            + RUN
            + "',"
            + cutoff
            + ","
            + limit
            + ")");
  }

  private static void sql(Connection c, String text) throws SQLException {
    try (var s = c.createStatement()) {
      s.execute(text);
    }
  }

  private static String scalar(Connection c, String text) throws SQLException {
    try (var s = c.createStatement();
        var row = s.executeQuery(text)) {
      assertTrue(row.next());
      String value = row.getString(1);
      assertNotNull(value);
      assertFalse(row.next());
      return value;
    }
  }

  private static String ids(Connection c, String table) throws SQLException {
    return scalar(
        c, "select coalesce(string_agg(id::text,',' order by id),'') from schubert." + table);
  }

  private static String historyIds(Connection c) throws SQLException {
    return scalar(
        c,
        "select coalesce(string_agg(id::text,',' order by id),'') from schubert.batch_runs where"
            + " id>=101");
  }

  private static void backup(Connection c, String step) throws SQLException {
    sql(
        c,
        "insert into"
            + " schubert.batch_runs(run_id,business_date,step,attempt,started_at,ended_at,status)"
            + " values('"
            + RUN
            + "','2026-09-17','"
            + step
            + "',1,"
            + START
            + ","
            + START
            + ",'SUCCESS')");
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

  private static void history(Connection c, int id, int run, String status, String end)
      throws SQLException {
    sql(
        c,
        "insert into"
            + " schubert.batch_runs(id,run_id,business_date,step,attempt,started_at,ended_at,status)"
            + " values("
            + id
            + ",'"
            + new UUID(0, run)
            + "','2025-01-01','PUBLIC_TEST_"
            + id
            + "',1,'2025-01-01',"
            + end
            + ",'"
            + status
            + "')");
  }

  private static void question(Connection c, int id, boolean deleted, String at)
      throws SQLException {
    sql(
        c,
        "insert into"
            + " schubert.questions(id,receipt_id,owner_user_id,body,operation_token,submitted_at,is_deleted,deleted_at,deleted_by)"
            + " values("
            + id
            + ",lpad('"
            + id
            + "',26,'0'),7,'public question','"
            + new UUID(0, id)
            + "','2026-09-01',"
            + deleted
            + ","
            + at
            + ","
            + (deleted ? "7" : "null")
            + ")");
  }

  private static void notification(Connection c, int id, String state, String at)
      throws SQLException {
    sql(
        c,
        "insert into"
            + " schubert.async_jobs(id,question_id,owner_user_id,state,message_id,correlation_id,received_at,state_changed_at)"
            + " values("
            + id
            + ","
            + id
            + ",7,'RECEIVED','"
            + new UUID(1, id)
            + "','"
            + new UUID(2, id)
            + "','2026-09-01','2026-09-01')");
    String type = Set.of("ERROR", "COMPLETED").contains(state) ? state : "ACCEPTED";
    String error = state.equals("ERROR") ? "'PROCESS_FAILED','public failure'" : "null,null";
    sql(
        c,
        "insert into"
            + " schubert.notifications(id,job_id,question_id,owner_user_id,notification_type,state,accepted_at,state_changed_at,error_code,error_message,created_at,updated_at)"
            + " values("
            + id
            + ","
            + id
            + ","
            + id
            + ",7,'"
            + type
            + "','"
            + state
            + "','2026-09-01',"
            + at
            + ","
            + error
            + ",'2026-09-01',"
            + at
            + ")");
  }

  private static Path migrations() {
    return Path.of(System.getProperty("nk.pt.repository"))
        .resolve("src/schubert-nk-api/src/main/resources/db/migration");
  }

  private static void awaitBlocked(int pid) throws SQLException {
    long deadline = System.nanoTime() + TimeUnit.SECONDS.toNanos(4);
    try (var c = db.admin()) {
      do {
        if (scalar(c, "select (cardinality(pg_blocking_pids(" + pid + "))>0)::text").equals("true"))
          return;
      } while (System.nanoTime() < deadline);
      fail("backup lock synchronization not reached");
    }
  }
}
