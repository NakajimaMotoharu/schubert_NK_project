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
import java.sql.Types;
import java.util.ArrayList;
import java.util.HexFormat;
import java.util.List;
import java.util.Map;
import org.flywaydb.core.Flyway;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** NK-DAT-001/OPS009/DAT009/UI251/SS331 3.14/332/341; SSC057/PG164; DB259..266. */
final class StepCleanupBoundaryTest {
  private static final String FIXTURE_1_1_0_1_1_FALSE_OK_AC350453 = "1|1|0|1|1|false|OK";
  private static final String FIXTURE_SELECT_COUNT_FROM_SCHUBERT_NOTIFICATIONS_425F2647 =
      "select count(*) from schubert.notifications";
  private static final String FIXTURE_0_0_0_NULL_NULL_FALSE_LOCK_BUSY_1CBCA5E1 =
      "0|0|0|NULL|NULL|false|LOCK_BUSY";
  private static final String FIXTURE_ID_1_6CF3798F = "id=1";
  private static final String FIXTURE_0_0_0_0_0_TRUE_OK_70CA2E0C = "0|0|0|0|0|true|OK";
  private static final String FIXTURE_NOTIFICATIONS_CEF4B870 = "NOTIFICATIONS";
  private static final String FIXTURE_QUESTIONS_220AA8AB = "QUESTIONS";
  private static final String FIXTURE_SESSIONS_1BB11AB1 = "SESSIONS";
  private static final String FIXTURE_OUTBOX_4A998DF8 = "OUTBOX";
  private static final String FIXTURE_BATCH_RUNS_FB17B0EE = "BATCH_RUNS";
  private static final String FIXTURE_INBOX_PROGRESS_6FF00799 = "INBOX_PROGRESS";
  private static final String FIXTURE_LOG_PROGRESS_8EFCB691 = "LOG_PROGRESS";
  private static final String FIXTURE_SCHUBERT_NOTIFICATIONS_4B64D746 = "schubert.notifications";
  private static final String FIXTURE_55000_F2ADCE46 = "55000";
  private static final String FIXTURE_TRUE_18D10C7D = "true";
  private static final String FIXTURE_DELETE_FROM_AF6A49CB = "delete from ";
  private static final String FIXTURE_2026_09_11T15_00_00Z_564E8A05 = "2026-09-11T15:00:00Z";
  private static final String FIXTURE_2025_08_08T15_00_00Z_45BD5D0B = "2025-08-08T15:00:00Z";
  @TempDir static Path root;
  static ApiLogDatabaseFixture db;
  static String url;
  static final String RUN = "12345678-9abc-def0-8123-456789abcdef";
  static final String CUT = "2026-09-12T15:00:00Z";
  static final String START = "2026-09-13T02:00:00Z";
  static final String FN = "schubert.maintenance_execute_cleanup_step";
  static final String SIG = FN + "(uuid,timestamptz,bigint,integer,timestamptz,text,integer)";
  static final List<String> KINDS =
      List.of(
          FIXTURE_NOTIFICATIONS_CEF4B870,
          FIXTURE_QUESTIONS_220AA8AB,
          FIXTURE_SESSIONS_1BB11AB1,
          FIXTURE_OUTBOX_4A998DF8,
          FIXTURE_BATCH_RUNS_FB17B0EE,
          FIXTURE_INBOX_PROGRESS_6FF00799,
          FIXTURE_LOG_PROGRESS_8EFCB691);
  static final List<String> TABLES =
      List.of(
          FIXTURE_SCHUBERT_NOTIFICATIONS_4B64D746,
          "schubert.questions",
          "schubert.auth_sessions",
          "schubert.login_ip_attempts",
          "schubert_web_session.web_http_sessions",
          "schubert.mq_outbox",
          "schubert_web_session.web_log_outbox",
          "schubert.batch_runs",
          "schubert.inbox_inspection_progress",
          "schubert.log_cleanup_progress");

  @BeforeAll
  static void start() throws Exception {
    db = new ApiLogDatabaseFixture(root);
    try (var c = db.admin()) {
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
      fixture(c);
    }
  }

  @Test
  void sevenKindAtomicCounts() throws Exception {
    StringBuilder trace = new StringBuilder();
    try (var c = locked();
        var admin = db.admin()) {
      int[] targets = {1, 1, 3, 2, 1, 1, 1};
      int[] totals = {1, 1, 3, 2, 1, 2, 3};
      for (int i = 0; i < KINDS.size(); i++) {
        String kind = KINDS.get(i);
        String expected =
            targets[i] + "|" + targets[i] + "|0|" + totals[i] + "|" + totals[i] + "|false|OK";
        String actual = call(c, kind, 1000);
        assertEquals(expected, actual, kind);
        trace.append(kind).append('=').append(actual).append('\n');
        assertEquals(
            "0|0|0|" + totals[i] + "|" + totals[i] + "|true|OK", call(c, kind, 1000), kind);
        assertEquals(
            totals[i] + "|" + totals[i] + "|RUNNING|true|0|0",
            scalar(
                admin,
                "select target_count||'|'||success_count||'|'||status||'|'||(ended_at is null)||'|'||failure_count||'|'||byte_count from schubert.batch_runs where id="
                    + id(kind)));
      }
      assertEquals("1", scalar(admin, "select count(*) from schubert.questions"));
      assertEquals("1", scalar(admin, "select count(*) from schubert.async_jobs"));
      fixture(admin);
      assertEquals(FIXTURE_1_1_0_1_1_FALSE_OK_AC350453, call(c, FIXTURE_SESSIONS_1BB11AB1, 1));
      assertEquals("2|2|0|3|3|false|OK", call(c, FIXTURE_SESSIONS_1BB11AB1, 1000));
      assertEquals("0|0|0|3|3|true|OK", call(c, FIXTURE_SESSIONS_1BB11AB1, 1000));
    }
    Path out = Path.of("target/atomic-cleanup-traces");
    Files.createDirectories(out);
    Files.writeString(out.resolve("PT-DB-INBOX-259-seven-kinds.txt"), trace);
  }

  @Test
  void handleArgumentsAndIdentity() throws Exception {
    try (var c = locked();
        var admin = db.admin()) {
      List<String> valid =
          new ArrayList<>(
              List.of(
                  "'" + RUN + "'",
                  "'" + CUT + "'",
                  "90010",
                  "1",
                  "'" + START + "'",
                  "'NOTIFICATIONS'",
                  "1"));
      for (int i = 0; i < 7; i++) {
        var args = new ArrayList<>(valid);
        args.set(i, "null");
        state(c, args, "22023");
      }
      Map<Integer, List<String>> bad =
          Map.of(
              1,
              List.of("'infinity'", "'-infinity'", "'0001-01-01 BC'"),
              2,
              List.of("0", "1000000000000", "-9223372036854775808", "9223372036854775807"),
              3,
              List.of("0", "100", "-2147483648", "2147483647"),
              4,
              List.of(
                  "'infinity'",
                  "'-infinity'",
                  "'10000-01-01T00:00:00Z'",
                  "'2026-09-12T14:59:59.999999Z'"),
              5,
              List.of("'LOGS'", "'UNKNOWN'", "'notifications'", "''"),
              6,
              List.of("0", "1001", "-2147483648", "2147483647"));
      for (var e : bad.entrySet())
        for (String value : e.getValue()) {
          var args = new ArrayList<>(valid);
          args.set(e.getKey(), value);
          state(c, args, "22023");
        }
      for (String time :
          List.of("0001-01-01T00:00:00Z", "1582-10-10T00:00:00Z", "9999-12-31T23:59:59.999999Z")) {
        var args = new ArrayList<>(valid);
        args.set(1, "'" + time + "'");
        args.set(4, "'" + time + "'");
        assertEquals("0|0|0|NULL|NULL|false|BACKUP_GATE", observation(c, String.join(",", args)));
      }
      for (String assignment :
          List.of(
              "run_id='00000000-0000-0000-0000-000000000009'",
              "business_date='2026-09-14'",
              "step='CLEAN_TRANSFER'",
              "attempt=2",
              "started_at='2026-09-13T02:00:00.000001Z'",
              "status='SUCCESS'",
              "ended_at='2026-09-13T02:00:01Z'",
              "target_count=1",
              "success_count=1",
              "failure_count=1",
              "byte_count=1")) {
        fixture(admin);
        sql(admin, "update schubert.batch_runs set " + assignment + " where id=90010");
        assertEquals(
            FIXTURE_55000_F2ADCE46,
            assertThrows(SQLException.class, () -> call(c, FIXTURE_NOTIFICATIONS_CEF4B870, 1))
                .getSQLState(),
            assignment);
        assertEquals("1", scalar(admin, FIXTURE_SELECT_COUNT_FROM_SCHUBERT_NOTIFICATIONS_425F2647));
      }
      fixture(admin);
      sql(admin, "delete from schubert.batch_runs where id=90010");
      assertEquals(
          FIXTURE_55000_F2ADCE46,
          assertThrows(SQLException.class, () -> call(c, FIXTURE_NOTIFICATIONS_CEF4B870, 1))
              .getSQLState());
      fixture(admin);
      sql(
          admin,
          "insert into schubert.inbox_inspection_progress(run_id,cutoff) values('"
              + RUN
              + "','2026-09-12T15:00:01Z')");
      assertEquals(
          FIXTURE_55000_F2ADCE46,
          assertThrows(SQLException.class, () -> call(c, FIXTURE_NOTIFICATIONS_CEF4B870, 1))
              .getSQLState());
    }
  }

  @Test
  void backupLockAndRoleBoundary() throws Exception {
    try (var c = locked();
        var admin = db.admin()) {
      for (String step : List.of("BACKUP_DB", "BACKUP_CONFIG")) {
        sql(admin, "update schubert.batch_runs set status='FAILED' where step='" + step + "'");
        assertEquals(
            "0|0|0|NULL|NULL|false|BACKUP_GATE", call(c, FIXTURE_NOTIFICATIONS_CEF4B870, 1));
        fixture(admin);
      }
      admin.setAutoCommit(false);
      scalar(admin, "select id from schubert.batch_runs where id=90010 for update");
      assertEquals(
          FIXTURE_0_0_0_NULL_NULL_FALSE_LOCK_BUSY_1CBCA5E1,
          call(c, FIXTURE_NOTIFICATIONS_CEF4B870, 1));
      assertEquals("1", scalar(admin, FIXTURE_SELECT_COUNT_FROM_SCHUBERT_NOTIFICATIONS_425F2647));
      admin.rollback();
      assertEquals(
          "nk_owner|true|search_path=pg_catalog, schubert, schubert_web_session|TimeZone=UTC",
          scalar(
              admin,
              "select pg_get_userbyid(proowner)||'|'||prosecdef||'|'||array_to_string(proconfig,'|') from pg_proc where oid='"
                  + SIG
                  + "'::regprocedure"));
      assertEquals(
          "false",
          scalar(admin, "select has_function_privilege('public','" + SIG + "','EXECUTE')::text"));
      assertEquals(
          FIXTURE_TRUE_18D10C7D,
          scalar(
              admin,
              "select has_function_privilege('schubert_batch','" + SIG + "','EXECUTE')::text"));
      for (String role :
          List.of(
              "schubert_app",
              "schubert_web_session",
              "schubert_backup",
              "schubert_ops_ro",
              "schubert_inbox_inspector"))
        try (var denied = DriverManager.getConnection(url, role, "")) {
          assertEquals(
              "42501",
              assertThrows(
                      SQLException.class, () -> call(denied, FIXTURE_NOTIFICATIONS_CEF4B870, 1))
                  .getSQLState());
        }
      try (var other = DriverManager.getConnection(url, "schubert_batch", "")) {
        assertEquals(
            FIXTURE_0_0_0_NULL_NULL_FALSE_LOCK_BUSY_1CBCA5E1,
            call(other, FIXTURE_NOTIFICATIONS_CEF4B870, 1));
      }
      admin.rollback();
    }
  }

  @Test
  void zeroChunkLockedRemainder() throws Exception {
    String[] kinds = {
      FIXTURE_NOTIFICATIONS_CEF4B870,
      FIXTURE_QUESTIONS_220AA8AB,
      FIXTURE_SESSIONS_1BB11AB1,
      FIXTURE_SESSIONS_1BB11AB1,
      FIXTURE_SESSIONS_1BB11AB1,
      FIXTURE_OUTBOX_4A998DF8,
      FIXTURE_OUTBOX_4A998DF8,
      FIXTURE_BATCH_RUNS_FB17B0EE,
      FIXTURE_INBOX_PROGRESS_6FF00799,
      FIXTURE_LOG_PROGRESS_8EFCB691
    };
    String[] where = {
      FIXTURE_ID_1_6CF3798F,
      "id=2",
      FIXTURE_TRUE_18D10C7D,
      FIXTURE_TRUE_18D10C7D,
      FIXTURE_TRUE_18D10C7D,
      FIXTURE_ID_1_6CF3798F,
      FIXTURE_ID_1_6CF3798F,
      FIXTURE_ID_1_6CF3798F,
      FIXTURE_TRUE_18D10C7D,
      FIXTURE_TRUE_18D10C7D
    };
    for (int i = 0; i < TABLES.size(); i++) {
      String table = TABLES.get(i);
      String kind = kinds[i];
      try (var c = locked();
          var writer = db.admin();
          var admin = db.admin()) {
        fixture(admin);
        // All other session/outbox components absent, so only the held row is eligible.
        if (kind.equals(FIXTURE_SESSIONS_1BB11AB1))
          for (String t : TABLES.subList(2, 5))
            if (!t.equals(table)) sql(admin, FIXTURE_DELETE_FROM_AF6A49CB + t);
        if (kind.equals(FIXTURE_OUTBOX_4A998DF8))
          for (String t : TABLES.subList(5, 7))
            if (!t.equals(table)) sql(admin, FIXTURE_DELETE_FROM_AF6A49CB + t);
        writer.setAutoCommit(false);
        scalar(
            writer,
            "select count(*) from (select 1 from "
                + table
                + " where "
                + where[i]
                + " for update) held");
        assertEquals(FIXTURE_0_0_0_NULL_NULL_FALSE_LOCK_BUSY_1CBCA5E1, call(c, kind, 1000), table);
        assertEquals(
            "0",
            scalar(admin, "select target_count from schubert.batch_runs where id=" + id(kind)));
        writer.rollback();
        assertEquals(FIXTURE_1_1_0_1_1_FALSE_OK_AC350453, call(c, kind, 1000), table);
        assertEquals("0|0|0|1|1|true|OK", call(c, kind, 1000), table);
      }
    }
  }

  @Test
  void retentionAndProtectedRows() throws Exception {
    try (var c = locked();
        var admin = db.admin()) {
      for (String[] pair :
          List.of(
              new String[] {
                FIXTURE_NOTIFICATIONS_CEF4B870,
                "update schubert.notifications set state_changed_at='2026-09-11T15:00:00.000001Z'"
              },
              new String[] {
                FIXTURE_QUESTIONS_220AA8AB,
                "update schubert.questions set deleted_at='2026-09-12T15:00:00Z' where id=2"
              },
              new String[] {
                FIXTURE_SESSIONS_1BB11AB1,
                "update schubert.auth_sessions set expires_at='2026-09-11T15:00:00.000001Z';update schubert.login_ip_attempts set window_started_at='2026-09-11T14:45:00.000001Z';update schubert_web_session.web_http_sessions set expires_at='2026-09-12T15:00:00.000001Z'"
              },
              new String[] {
                FIXTURE_OUTBOX_4A998DF8,
                "update schubert.mq_outbox set sent_at='2026-09-05T15:00:00Z';update schubert_web_session.web_log_outbox set sent_at='2026-09-05T15:00:00Z'"
              },
              new String[] {
                FIXTURE_BATCH_RUNS_FB17B0EE,
                "update schubert.batch_runs set ended_at=timestamptz '2026-09-12T15:00:00Z'-interval '9600 hours' where id=1"
              },
              new String[] {
                FIXTURE_INBOX_PROGRESS_6FF00799,
                "update schubert.inbox_inspection_progress set completed_at=timestamptz '2026-09-12T15:00:00Z'-interval '9600 hours'"
              },
              new String[] {
                FIXTURE_LOG_PROGRESS_8EFCB691,
                "update schubert.log_cleanup_progress set completed_at=timestamptz '2026-09-12T15:00:00Z'-interval '9600 hours'"
              })) {
        fixture(admin);
        sql(admin, pair[1]);
        assertEquals(FIXTURE_0_0_0_0_0_TRUE_OK_70CA2E0C, call(c, pair[0], 1000), pair[0]);
      }
      for (String status : List.of("RUNNING", "FAILED")) {
        fixture(admin);
        sql(admin, "update schubert.batch_runs set status='" + status + "' where id=1");
        sql(
            admin,
            "update schubert.inbox_inspection_progress set run_id='00000000-0000-0000-0000-000000000001'");
        sql(
            admin,
            "update schubert.log_cleanup_progress set run_id='00000000-0000-0000-0000-000000000001'");
        for (String kind :
            List.of(
                FIXTURE_BATCH_RUNS_FB17B0EE,
                FIXTURE_INBOX_PROGRESS_6FF00799,
                FIXTURE_LOG_PROGRESS_8EFCB691))
          assertEquals(FIXTURE_0_0_0_0_0_TRUE_OK_70CA2E0C, call(c, kind, 1000));
      }
      fixture(admin);
      sql(
          admin,
          "update schubert.mq_outbox set lease_owner='public-owner',lease_until='"
              + CUT
              + "';update schubert_web_session.web_log_outbox set lease_owner='public-owner',lease_until='"
              + CUT
              + "'");
      assertEquals(FIXTURE_0_0_0_0_0_TRUE_OK_70CA2E0C, call(c, FIXTURE_OUTBOX_4A998DF8, 1000));
      fixture(admin);
      sql(
          admin,
          "update schubert.notifications set state='PROCESSING',notification_type='ACCEPTED'");
      assertEquals(
          FIXTURE_0_0_0_0_0_TRUE_OK_70CA2E0C, call(c, FIXTURE_NOTIFICATIONS_CEF4B870, 1000));
      sql(
          admin,
          "update schubert.questions set is_deleted=true,deleted_at='2026-09-01T00:00:00Z',deleted_by=7 where id=1;delete from schubert.questions where id=2");
      assertEquals(FIXTURE_0_0_0_0_0_TRUE_OK_70CA2E0C, call(c, FIXTURE_QUESTIONS_220AA8AB, 1000));
    }
    predicateMatrix();
  }

  private void predicateMatrix() throws Exception {
    // All alternatives in the copied read-only remainder predicate, with independently chosen
    // minus/equal/plus microsecond thresholds. A held eligible row must never report END.
    record Boundary(
        String kind,
        String table,
        String where,
        String update,
        String instant,
        boolean inclusive) {}
    var cases =
        List.of(
            new Boundary(
                FIXTURE_NOTIFICATIONS_CEF4B870,
                FIXTURE_SCHUBERT_NOTIFICATIONS_4B64D746,
                FIXTURE_ID_1_6CF3798F,
                "state='CANCELLED',state_changed_at=",
                CUT,
                false),
            new Boundary(
                FIXTURE_NOTIFICATIONS_CEF4B870,
                FIXTURE_SCHUBERT_NOTIFICATIONS_4B64D746,
                FIXTURE_ID_1_6CF3798F,
                "state='COMPLETED',state_changed_at=",
                FIXTURE_2026_09_11T15_00_00Z_564E8A05,
                true),
            new Boundary(
                FIXTURE_NOTIFICATIONS_CEF4B870,
                FIXTURE_SCHUBERT_NOTIFICATIONS_4B64D746,
                FIXTURE_ID_1_6CF3798F,
                "state='ERROR',notification_type='ERROR',error_code='PROCESS_FAILED',error_message='public fixture',state_changed_at=",
                FIXTURE_2026_09_11T15_00_00Z_564E8A05,
                true),
            new Boundary(
                FIXTURE_QUESTIONS_220AA8AB,
                "schubert.questions",
                "id=2",
                "deleted_at=",
                CUT,
                false),
            new Boundary(
                FIXTURE_SESSIONS_1BB11AB1,
                "schubert.auth_sessions",
                FIXTURE_TRUE_18D10C7D,
                "expires_at=",
                FIXTURE_2026_09_11T15_00_00Z_564E8A05,
                true),
            new Boundary(
                FIXTURE_SESSIONS_1BB11AB1,
                "schubert.auth_sessions",
                FIXTURE_TRUE_18D10C7D,
                "expires_at='2026-09-14T00:00:00Z',revoked=true,revoked_at=",
                FIXTURE_2026_09_11T15_00_00Z_564E8A05,
                true),
            new Boundary(
                FIXTURE_SESSIONS_1BB11AB1,
                "schubert.login_ip_attempts",
                FIXTURE_TRUE_18D10C7D,
                "locked_until=null,window_started_at=",
                "2026-09-11T14:45:00Z",
                true),
            new Boundary(
                FIXTURE_SESSIONS_1BB11AB1,
                "schubert.login_ip_attempts",
                FIXTURE_TRUE_18D10C7D,
                "window_started_at='2026-09-01T00:00:00Z',locked_until=",
                FIXTURE_2026_09_11T15_00_00Z_564E8A05,
                true),
            new Boundary(
                FIXTURE_SESSIONS_1BB11AB1,
                "schubert_web_session.web_http_sessions",
                FIXTURE_TRUE_18D10C7D,
                "expires_at=",
                CUT,
                true),
            new Boundary(
                FIXTURE_OUTBOX_4A998DF8,
                "schubert.mq_outbox",
                FIXTURE_ID_1_6CF3798F,
                "sent_at=",
                "2026-09-05T15:00:00Z",
                false),
            new Boundary(
                FIXTURE_OUTBOX_4A998DF8,
                "schubert_web_session.web_log_outbox",
                FIXTURE_ID_1_6CF3798F,
                "sent_at=",
                "2026-09-05T15:00:00Z",
                false),
            new Boundary(
                FIXTURE_OUTBOX_4A998DF8,
                "schubert.mq_outbox",
                FIXTURE_ID_1_6CF3798F,
                "lease_owner='public-owner',lease_until=",
                CUT,
                false),
            new Boundary(
                FIXTURE_OUTBOX_4A998DF8,
                "schubert_web_session.web_log_outbox",
                FIXTURE_ID_1_6CF3798F,
                "lease_owner='public-owner',lease_until=",
                CUT,
                false),
            new Boundary(
                FIXTURE_BATCH_RUNS_FB17B0EE,
                "schubert.batch_runs",
                FIXTURE_ID_1_6CF3798F,
                "status='WARNING',ended_at=",
                FIXTURE_2025_08_08T15_00_00Z_45BD5D0B,
                false),
            new Boundary(
                FIXTURE_BATCH_RUNS_FB17B0EE,
                "schubert.batch_runs",
                FIXTURE_ID_1_6CF3798F,
                "status='SKIPPED',ended_at=",
                FIXTURE_2025_08_08T15_00_00Z_45BD5D0B,
                false),
            new Boundary(
                FIXTURE_INBOX_PROGRESS_6FF00799,
                "schubert.inbox_inspection_progress",
                FIXTURE_TRUE_18D10C7D,
                "completed_at=",
                FIXTURE_2025_08_08T15_00_00Z_45BD5D0B,
                false),
            new Boundary(
                FIXTURE_LOG_PROGRESS_8EFCB691,
                "schubert.log_cleanup_progress",
                FIXTURE_TRUE_18D10C7D,
                "completed_at=",
                FIXTURE_2025_08_08T15_00_00Z_45BD5D0B,
                false));
    for (var b : cases)
      for (int micro : new int[] {-1, 0, 1}) {
        try (var c = locked();
            var admin = db.admin();
            var holder = db.admin()) {
          fixture(admin);
          if (b.kind().equals(FIXTURE_SESSIONS_1BB11AB1))
            for (String t : TABLES.subList(2, 5))
              if (!t.equals(b.table())) sql(admin, FIXTURE_DELETE_FROM_AF6A49CB + t);
          if (b.kind().equals(FIXTURE_OUTBOX_4A998DF8))
            for (String t : TABLES.subList(5, 7))
              if (!t.equals(b.table())) sql(admin, FIXTURE_DELETE_FROM_AF6A49CB + t);
          sql(
              admin,
              "update "
                  + b.table()
                  + " set "
                  + b.update()
                  + "timestamptz '"
                  + b.instant()
                  + "'+interval '"
                  + micro
                  + " microseconds' where "
                  + b.where());
          holder.setAutoCommit(false);
          sql(holder, "select 1 from " + b.table() + " where " + b.where() + " for update");
          boolean eligible = micro < 0 || (micro == 0 && b.inclusive());
          assertEquals(
              eligible
                  ? FIXTURE_0_0_0_NULL_NULL_FALSE_LOCK_BUSY_1CBCA5E1
                  : FIXTURE_0_0_0_0_0_TRUE_OK_70CA2E0C,
              call(c, b.kind(), 1000),
              b.toString() + micro);
          holder.rollback();
          assertEquals(
              eligible ? FIXTURE_1_1_0_1_1_FALSE_OK_AC350453 : FIXTURE_0_0_0_0_0_TRUE_OK_70CA2E0C,
              call(c, b.kind(), 1000),
              b.toString() + micro);
        }
      }
  }

  @Test
  void rollbackOverflowAndForeignKey() throws Exception {
    try (var c = db.admin()) {
      sql(c, "select pg_advisory_lock(71419602)");
      c.setAutoCommit(false);
      var save = c.setSavepoint();
      assertEquals(FIXTURE_1_1_0_1_1_FALSE_OK_AC350453, call(c, FIXTURE_NOTIFICATIONS_CEF4B870, 1));
      c.rollback(save);
      assertEquals("1", scalar(c, FIXTURE_SELECT_COUNT_FROM_SCHUBERT_NOTIFICATIONS_425F2647));
      assertEquals("0", scalar(c, "select target_count from schubert.batch_runs where id=90010"));
      sql(
          c,
          "update schubert.batch_runs set target_count=9223372036854775807,success_count=9223372036854775807 where id=90010");
      save = c.setSavepoint();
      assertEquals(
          "22003",
          assertThrows(SQLException.class, () -> call(c, FIXTURE_NOTIFICATIONS_CEF4B870, 1))
              .getSQLState());
      c.rollback(save);
      assertEquals("1", scalar(c, FIXTURE_SELECT_COUNT_FROM_SCHUBERT_NOTIFICATIONS_425F2647));
      c.rollback();
      sql(
          c,
          "create table schubert.pt_question_reference(question_id bigint references schubert.questions(id));insert into schubert.pt_question_reference values(2)");
      assertEquals("0|0|0|0|0|false|FOREIGN_KEY_CONFLICT", call(c, FIXTURE_QUESTIONS_220AA8AB, 1));
      assertEquals("1", scalar(c, "select count(*) from schubert.questions where id=2"));
      assertEquals("0", scalar(c, "select target_count from schubert.batch_runs where id=90011"));
      c.rollback();
      sql(
          c,
          "create table schubert.pt_notification_reference(notification_id bigint references schubert.notifications(id));insert into schubert.pt_notification_reference values(1)");
      save = c.setSavepoint();
      assertEquals(
          "23503",
          assertThrows(SQLException.class, () -> call(c, FIXTURE_NOTIFICATIONS_CEF4B870, 1))
              .getSQLState());
      c.rollback(save);
      assertEquals("1", scalar(c, FIXTURE_SELECT_COUNT_FROM_SCHUBERT_NOTIFICATIONS_425F2647));
      c.rollback();
      sql(
          c,
          "create function schubert.pt_skip_count_update() returns trigger language plpgsql as $$begin return null;end$$");
      sql(
          c,
          "create trigger pt_skip_count_update before update on schubert.batch_runs for each row execute function schubert.pt_skip_count_update()");
      save = c.setSavepoint();
      assertEquals(
          FIXTURE_55000_F2ADCE46,
          assertThrows(SQLException.class, () -> call(c, FIXTURE_NOTIFICATIONS_CEF4B870, 1))
              .getSQLState());
      c.rollback(save);
      assertEquals("1", scalar(c, FIXTURE_SELECT_COUNT_FROM_SCHUBERT_NOTIFICATIONS_425F2647));
      c.rollback();
    }
  }

  @Test
  void typedProjectionAndNoBypass() throws Exception {
    try (var c = locked();
        var admin = db.admin();
        var s = c.createStatement();
        var rows =
            s.executeQuery(
                "select target_count,deleted_count,skipped_count,step_target_count,step_success_count,complete,reason_code from "
                    + FN
                    + "("
                    + args(FIXTURE_NOTIFICATIONS_CEF4B870, 1)
                    + ")")) {
      var md = rows.getMetaData();
      assertEquals(7, md.getColumnCount());
      for (int i = 1; i <= 5; i++) assertEquals(Types.BIGINT, md.getColumnType(i));
      assertEquals(Types.BIT, md.getColumnType(6));
      assertEquals(Types.VARCHAR, md.getColumnType(7));
      assertTrue(rows.next());
      assertFalse(rows.next());
      assertEquals(
          "false|false",
          scalar(
              admin,
              "select has_table_privilege('schubert_batch','schubert.request_inbox','DELETE')||'|'||has_table_privilege('schubert_batch','schubert.questions','SELECT')"));
      assertEquals("0", scalar(admin, "select count(*) from schubert.request_inbox"));
    }
    try (var c = db.admin()) {
      sql(c, "select pg_advisory_lock(71419602)");
      c.setAutoCommit(false);
      for (String select :
          List.of(
              "select -1::bigint,-1::bigint,0::bigint,'OK'::varchar(32)",
              "select 2::bigint,2::bigint,0::bigint,'OK'::varchar(32)",
              "select 1::bigint,0::bigint,1::bigint,'OK'::varchar(32)",
              "select 0::bigint,0::bigint,0::bigint,'UNKNOWN'::varchar(32)",
              "select null::bigint,0::bigint,0::bigint,'OK'::varchar(32)",
              "select 0::bigint,null::bigint,0::bigint,'OK'::varchar(32)",
              "select 0::bigint,0::bigint,null::bigint,'OK'::varchar(32)",
              "select 0::bigint,0::bigint,0::bigint,null::varchar(32)",
              "select 1::bigint,1::bigint,0::bigint,'LOCK_BUSY'::varchar(32)")) {
        var save = c.setSavepoint();
        replaceNotification(c, select);
        assertEquals(
            FIXTURE_55000_F2ADCE46,
            assertThrows(SQLException.class, () -> call(c, FIXTURE_NOTIFICATIONS_CEF4B870, 1))
                .getSQLState(),
            select);
        c.rollback(save);
      }
      for (String reason : List.of("LOCK_BUSY", "BACKUP_GATE")) {
        var save = c.setSavepoint();
        replaceNotification(
            c, "select 0::bigint,0::bigint,0::bigint,'" + reason + "'::varchar(32)");
        assertEquals("0|0|0|NULL|NULL|false|" + reason, call(c, FIXTURE_NOTIFICATIONS_CEF4B870, 1));
        c.rollback(save);
      }
      for (String[] counter :
          List.of(
              new String[] {
                "select 0::bigint,0::bigint,0::bigint,'OK'::varchar(32) where false", "P0002"
              },
              new String[] {
                "select 0::bigint,0::bigint,0::bigint,'OK'::varchar(32) from generate_series(1,2)",
                "P0003"
              })) {
        var save = c.setSavepoint();
        replaceNotification(c, counter[0]);
        assertEquals(
            counter[1],
            assertThrows(SQLException.class, () -> call(c, FIXTURE_NOTIFICATIONS_CEF4B870, 1))
                .getSQLState());
        c.rollback(save);
      }
      c.rollback();
    }
  }

  @Test
  void appendOnlyMigrationInventory() throws Exception {
    Path migrations = repo().resolve("src/schubert-nk-api/src/main/resources/db/migration");
    List<String> expected =
        List.of(
            "f687a36d1e296d38306997808b0f4440e484e24dd37b3862476fb470e56930da",
            "23f82d08f89bf6abfb75cbf41d126b174fcef5cf77563755fc316b31fb817e8e",
            "85f05cda30be1dd7856fb1eee3b25f42c6513641ab5d30b92410210f5460aa5e",
            "fdf634ace2beef2d57e28ad65c2ed488eab493cb2b0d8b1d421eab8397b8079e",
            "daf64a15c753cea106b593e6da944db08f7b13c94d3f2aa4ec6626fcd8b56ff9",
            "79623b56b8fe9d27af75df6a5db5cf47f4b93fb7b5ae2b9eb4d19ce6d6624052",
            "3b93f98b801c967c78113f3931b89b32aa9dc821d336af6c81076efc26da0401",
            "a90b338170322bd190335d2cfd382bb36b6f8b1243410345ef35b54dda928412",
            "537c7844709ed116f23fa60c64ae378e79eadad79f2e8003bbfd688f42335312",
            "c27a17adba2367ded5dcefe1532f5b42e7e4e35259f32388fe2667049e8644b0",
            "18e92bfc225f39c7a0ecaf9bdbeef329e5a47c0af3283d12f858deb4aec09928",
            "21e4c781a4b4c1a18240d8e47fae5bc2d11593d7b4ad05590ed10a67ebcb9411",
            "d56446bcfb7b3fa74ad0939baa3e2c0d263dd8a975cb7e3a9ce06bac2be85a74",
            "d2ba884de86c59c5815559aaf17a83b7a0546fcc7f9f48649dd744d127270229",
            "1c5544165e1ab8441f6edf3dcc83dbb5ac9e05a6e6bfb9a7086d0d8ea0f6396b",
            "99a9ae01ff3a6833d22d7c514c67c2229eb459e38bbf3e38da17a6b796f38aa8",
            "c412685a319defa1cb4f91846c02d69dbbc18457da5feb9d66266d2aec3446ce",
            "8799bd8dbe60b34e8c7a4e507ad54b2c41979be47973943b5e868d1224f302c9",
            "6b03d147fff575c05ac20d8a706e2fd83b5fc7565c55f4df8511ed0c3f07be5a",
            "e91ef0d596f08e891a025da7e760761b7836f6e298d1c362f9fd02c05ff99983",
            "608d028dcaa17713165090db60d7b3af2da9df7edfd493dc7bef4d9e1aa6435e",
            // Frozen from pre-V023 commit 802e9c26a, not current production expected generation.
            "56968e34731b766afd7b59523c2734be5fe0d063deda77414670729df9b12735",
            // Approved V023 before SSC152/V024; independent sha256sum, old bytes unmodified.
            "f604fcbe406c79ab3271482da1d509e7b64aa32bace21bdd766f4ee8ca986492",
            "d4f2060b208e2bf181aa0bf28eb5b11a04a0e4b3d9bd81ec5cd9ea0435428c9b");
    List<Path> files;
    try (var stream = Files.list(migrations)) {
      files = stream.sorted().toList();
    }
    assertEquals(28, files.size());
    for (int i = 0; i < 24; i++)
      assertEquals(
          expected.get(i),
          HexFormat.of()
              .formatHex(
                  MessageDigest.getInstance("SHA-256").digest(Files.readAllBytes(files.get(i)))));
    assertEquals(
        "V023__startup_schema_history_projection.sql", files.get(22).getFileName().toString());
    assertEquals("V025__question_dlq_outbox_identity.sql", files.get(24).getFileName().toString());
    assertEquals(
        "040ffee84a17abbbbcc7f5817a56ec9332826ea06e57deeffc2eac83bd6b7609",
        HexFormat.of()
            .formatHex(
                MessageDigest.getInstance("SHA-256").digest(Files.readAllBytes(files.get(24)))));
    assertEquals(
        "V027__pending_revocation_unknown_expiry.sql", files.get(26).getFileName().toString());
    assertEquals(
        "V028__retained_success_progress_seals.sql", files.getLast().getFileName().toString());
    assertEquals(
        List.of(
            "001", "002", "003", "004", "005", "006", "007", "008", "009", "010", "011", "012",
            "013", "014", "015", "016", "017", "018", "019", "020", "021", "022", "023", "024",
            "025", "026", "027", "028"),
        MigrationInventory.VERSIONS);
    try (var c = db.admin()) {
      assertEquals(
          "28|1",
          scalar(
              c,
              "select (select count(*) from schubert_meta.flyway_schema_history where success and type='SQL' and version is not null)||'|'||(select count(*) from schubert_meta.flyway_schema_history where success and type='SCHEMA' and version is null)"));
      assertEquals(
          "24",
          scalar(
              c,
              "select count(*) from information_schema.tables where table_schema in ('schubert','schubert_web_session') and table_type='BASE TABLE'"));
    }
    var flyway =
        Flyway.configure()
            .dataSource(url, "schubert_migration", "")
            .defaultSchema("schubert_meta")
            .schemas("schubert_meta")
            .initSql("SET ROLE nk_owner")
            .locations("filesystem:" + migrations)
            .validateOnMigrate(true)
            .cleanDisabled(true)
            .load();
    flyway.validate();
    assertEquals(0, flyway.migrate().migrationsExecuted);
  }

  static long id(String k) {
    return switch (k) {
      case FIXTURE_NOTIFICATIONS_CEF4B870 -> 90010;
      case FIXTURE_QUESTIONS_220AA8AB -> 90011;
      case FIXTURE_SESSIONS_1BB11AB1 -> 90012;
      case FIXTURE_OUTBOX_4A998DF8 -> 90013;
      default -> 90014;
    };
  }

  static String args(String kind, int limit) {
    return "'" + RUN + "','" + CUT + "'," + id(kind) + ",1,'" + START + "','" + kind + "'," + limit;
  }

  static String call(Connection c, String kind, int limit) throws SQLException {
    return observation(c, args(kind, limit));
  }

  static String observation(Connection c, String args) throws SQLException {
    return scalar(
        c,
        "select target_count||'|'||deleted_count||'|'||skipped_count||'|'||coalesce(step_target_count::text,'NULL')||'|'||coalesce(step_success_count::text,'NULL')||'|'||complete||'|'||reason_code from "
            + FN
            + "("
            + args
            + ")");
  }

  static void state(Connection c, List<String> args, String expected) {
    assertEquals(
        expected,
        assertThrows(SQLException.class, () -> observation(c, String.join(",", args)))
            .getSQLState());
  }

  static Connection locked() throws SQLException {
    var c = DriverManager.getConnection(url, "schubert_batch", "");
    sql(c, "set timezone='UTC'");
    sql(c, "select pg_advisory_lock(71419602)");
    return c;
  }

  static void fixture(Connection c) throws Exception {
    sql(
        c,
        Files.readString(
            repo()
                .resolve(
                    "src/schubert-nk-api/src/test/resources/maintenance/step-cleanup-fixture.sql")));
  }

  static Path repo() {
    return Path.of(System.getProperty("nk.pt.repository"));
  }

  static void sql(Connection c, String text) throws SQLException {
    try (var s = c.createStatement()) {
      s.execute(text);
    }
  }

  static String scalar(Connection c, String text) throws SQLException {
    try (var s = c.createStatement();
        var row = s.executeQuery(text)) {
      assertTrue(row.next());
      String v = row.getString(1);
      assertNotNull(v);
      assertFalse(row.next());
      return v;
    }
  }

  static void replaceNotification(Connection c, String body) throws SQLException {
    sql(
        c,
        "create or replace function schubert.maintenance_cleanup_notifications(p_run_id uuid,p_cutoff timestamptz,p_limit integer) returns table(target_count bigint,deleted_count bigint,skipped_count bigint,reason_code varchar(32)) language sql security definer set search_path=pg_catalog,schubert,schubert_web_session set timezone='UTC' as $$"
            + body
            + "$$");
  }
}
