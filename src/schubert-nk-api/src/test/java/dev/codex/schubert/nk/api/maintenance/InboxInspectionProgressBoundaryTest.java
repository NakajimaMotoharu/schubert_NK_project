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
import java.sql.PreparedStatement;
import java.sql.SQLException;
import java.time.Instant;
import java.util.Arrays;
import java.util.HexFormat;
import java.util.List;
import java.util.UUID;
import org.flywaydb.core.Flyway;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** PT-DB-INBOX-073..080; SS331 3.8/341 7.3; PG-D-127. SQL capability, not AES proof. */
final class InboxInspectionProgressBoundaryTest {
  private static final String FIXTURE_VALUE_E91D96ED = "','";
  private static final String FIXTURE_SELECT_COUNT_FROM_BDA3EEC8 = "select count(*) from ";
  private static final String FIXTURE_SELECT_COUNT_FROM_SCHUBERT_REQUEST_INBOX_E4FAEDDB =
      "select count(*) from schubert.request_inbox";
  private static final String FIXTURE_55000_F2ADCE46 = "55000";
  private static final String FIXTURE_DELETED_1693CDB2 = "DELETED";
  private static final String FIXTURE_END_5AB955DF = "END";
  private static final String FIXTURE_PROTECTED_9E1A622F = "PROTECTED";
  private static final String FIXTURE_22023_CDCA15BB = "22023";
  private static final String FIXTURE_55P03_0FE714C6 = "55P03";
  @TempDir static Path root;
  private static ApiLogDatabaseFixture db;
  private static String url;
  private static byte[] digest;
  private static final UUID RUN = new UUID(0, 61);
  private static final UUID ONE = new UUID(0, 1);
  private static final UUID TWO = new UUID(0, 2);
  private static final Instant CUTOFF = Instant.parse("2026-09-17T00:00:00Z");
  private static final String TABLE = "schubert.inbox_inspection_progress";
  private static final String OPEN = "schubert.maintenance_open_inbox_inspection";
  private static final String RECORD = "schubert.maintenance_record_inbox_inspection";
  private static final String PURGE = "schubert.maintenance_cleanup_inbox_progress";
  private static final List<String> VERSIONS = MigrationInventory.VERSIONS;

  @BeforeAll
  static void start() throws Exception {
    db = new ApiLogDatabaseFixture(root);
    try (var c = db.api()) {
      url = c.getMetaData().getURL();
    }
    digest = MessageDigest.getInstance("SHA-256").digest(new byte[30]);
  }

  @AfterAll
  static void stop() throws Exception {
    if (db != null) db.stop();
  }

  @BeforeEach
  void reset() throws SQLException {
    for (String table : List.of(TABLE, "schubert.request_inbox", "schubert.batch_runs"))
      sql("delete from " + table);
    sql(
        "insert into"
            + " schubert.app_users(id,username,username_key,password_hash,role,status,password_changed_at,created_at,updated_at)"
            + " values(7,'Learner','learner','synthetic-unused','USER','ACTIVE','2026-09-01','2026-09-01','2026-09-01')"
            + " on conflict(id) do nothing");
    backup("BACKUP_DB");
    backup("BACKUP_CONFIG");
  }

  @Test
  void newAndResumedRunKeepOneCutoff() throws Exception {
    try (var c = inspector()) {
      assertEquals(new Progress(null, 0, 0, 0, false), open(c, RUN, CUTOFF.toString()));
      c.commit();
      assertEquals(new Progress(null, 0, 0, 0, false), open(c, RUN, CUTOFF.toString()));
      rejects(c, FIXTURE_55000_F2ADCE46, () -> open(c, RUN, CUTOFF.plusSeconds(1).toString()));
      assertEquals(
          new Progress(ONE, 1, 1, 0, false),
          record(c, null, 0L, ONE, FIXTURE_DELETED_1693CDB2, xact(c)));
      c.commit();
    }
    try (var c = inspector()) {
      assertEquals(new Progress(ONE, 1, 1, 0, false), open(c, RUN, CUTOFF.toString()));
      assertEquals(
          new Progress(ONE, 1, 1, 0, true),
          record(c, ONE, 1L, null, FIXTURE_END_5AB955DF, xact(c)));
      c.commit();
      assertEquals(new Progress(ONE, 1, 1, 0, true), open(c, RUN, CUTOFF.toString()));
      rejects(
          c, FIXTURE_55000_F2ADCE46, () -> record(c, ONE, 1L, null, FIXTURE_END_5AB955DF, xact(c)));
      c.commit();
    }
    assertEquals("1", scalar(FIXTURE_SELECT_COUNT_FROM_BDA3EEC8 + TABLE));
    sql("delete from " + TABLE);
    try (var c = inspector()) {
      open(c, RUN, CUTOFF.toString());
      assertEquals(
          new Progress(null, 0, 0, 0, true),
          record(c, null, 0L, null, FIXTURE_END_5AB955DF, xact(c)));
      c.commit();
    }
  }

  @Test
  void outcomesAdvanceOnlyMatchingState() throws Exception {
    UUID high = UUID.fromString("80000000-0000-0000-0000-000000000000");
    inbox(ONE);
    inbox(high);
    try (var c = inspector()) {
      open(c, RUN, CUTOFF.toString());
      rejects(
          c,
          FIXTURE_55000_F2ADCE46,
          () -> record(c, null, 0L, null, FIXTURE_END_5AB955DF, xact(c)));
      rejects(
          c,
          FIXTURE_55000_F2ADCE46,
          () -> record(c, null, 0L, ONE, FIXTURE_DELETED_1693CDB2, xact(c)));
      rejects(
          c,
          FIXTURE_55000_F2ADCE46,
          () -> record(c, null, 0L, TWO, FIXTURE_PROTECTED_9E1A622F, xact(c)));
      sql(
          "update schubert.request_inbox set expires_at='"
              + CUTOFF
              + "' where message_id='"
              + ONE
              + "'");
      rejects(
          c,
          FIXTURE_55000_F2ADCE46,
          () -> record(c, null, 0L, ONE, FIXTURE_PROTECTED_9E1A622F, xact(c)));
      sql(
          "update schubert.request_inbox set"
              + " processing_state='PROCESSING',result_ref_type=null,response_layout_id=null,response_version=null,response_body_encrypted=null,response_key_version=null,completed_at=null"
              + " where message_id='"
              + ONE
              + "'");
      rejects(
          c,
          FIXTURE_55000_F2ADCE46,
          () -> record(c, null, 0L, ONE, FIXTURE_PROTECTED_9E1A622F, xact(c)));
      sql("delete from schubert.request_inbox where message_id='" + ONE + "'");
      inbox(ONE);
      assertEquals(
          new Progress(ONE, 1, 0, 1, false),
          record(c, null, 0L, ONE, FIXTURE_PROTECTED_9E1A622F, xact(c)));
      rejects(
          c,
          FIXTURE_55000_F2ADCE46,
          () -> record(c, null, 0L, high, FIXTURE_PROTECTED_9E1A622F, xact(c)));
      rejects(
          c,
          FIXTURE_55000_F2ADCE46,
          () -> record(c, ONE, 0L, high, FIXTURE_PROTECTED_9E1A622F, xact(c)));
      rejects(
          c,
          FIXTURE_55000_F2ADCE46,
          () -> record(c, TWO, 1L, high, FIXTURE_PROTECTED_9E1A622F, xact(c)));
      rejects(
          c,
          FIXTURE_55000_F2ADCE46,
          () -> record(c, ONE, 1L, ONE, FIXTURE_PROTECTED_9E1A622F, xact(c)));
      rejects(
          c,
          FIXTURE_55000_F2ADCE46,
          () -> record(c, ONE, 1L, new UUID(0, 0), FIXTURE_DELETED_1693CDB2, xact(c)));
      // PostgreSQL UUID byte order advances here even though Java UUID.compareTo is signed.
      assertTrue(high.compareTo(ONE) < 0);
      assertEquals(
          new Progress(high, 2, 0, 2, false),
          record(c, ONE, 1L, high, FIXTURE_PROTECTED_9E1A622F, xact(c)));
      assertEquals(
          new Progress(high, 2, 0, 2, true),
          record(c, high, 2L, null, FIXTURE_END_5AB955DF, xact(c)));
      c.commit();
    }
    assertEquals("2", scalar(FIXTURE_SELECT_COUNT_FROM_SCHUBERT_REQUEST_INBOX_E4FAEDDB));
  }

  @Test
  void deletionAndCheckpointCommitTogether() throws Exception {
    inbox(ONE);
    try (var c = inspector()) {
      open(c, RUN, CUTOFF.toString());
      c.commit();
      open(c, RUN, CUTOFF.toString());
      delete(c, ONE);
      assertEquals(
          new Progress(ONE, 1, 1, 0, false),
          record(c, null, 0L, ONE, FIXTURE_DELETED_1693CDB2, xact(c)));
      assertEquals("1", scalar(FIXTURE_SELECT_COUNT_FROM_SCHUBERT_REQUEST_INBOX_E4FAEDDB));
      c.rollback();
      assertEquals(new Progress(null, 0, 0, 0, false), open(c, RUN, CUTOFF.toString()));
      delete(c, ONE);
      record(c, null, 0L, ONE, FIXTURE_DELETED_1693CDB2, xact(c));
      c.commit();
    }
    assertEquals("0", scalar(FIXTURE_SELECT_COUNT_FROM_SCHUBERT_REQUEST_INBOX_E4FAEDDB));
    try (var c = inspector()) {
      assertEquals(new Progress(ONE, 1, 1, 0, false), open(c, RUN, CUTOFF.toString()));
      rejects(
          c,
          FIXTURE_55000_F2ADCE46,
          () -> record(c, null, 0L, ONE, FIXTURE_DELETED_1693CDB2, xact(c)));
      record(c, ONE, 1L, null, FIXTURE_END_5AB955DF, xact(c));
      c.commit();
    }
    assertEquals(
        "1|1|0",
        scalar("select inspected_count||'|'||deleted_count||'|'||protected_count from " + TABLE));
  }

  @Test
  void invalidInputsAndConstraintsReject() throws Exception {
    try (var c = inspector()) {
      for (String cutoff : Arrays.asList(null, "infinity", "-infinity"))
        rejects(c, FIXTURE_22023_CDCA15BB, () -> open(c, RUN, cutoff));
      rejects(c, FIXTURE_22023_CDCA15BB, () -> open(c, null, CUTOFF.toString()));
      rejects(
          c,
          FIXTURE_55000_F2ADCE46,
          () -> record(c, null, 0L, ONE, FIXTURE_DELETED_1693CDB2, xact(c))); // no progress yet
      open(c, RUN, CUTOFF.toString());
      for (String cutoff : Arrays.asList(null, "infinity", "-infinity"))
        rejects(
            c,
            FIXTURE_22023_CDCA15BB,
            () -> recordAt(c, RUN, cutoff, null, 0L, ONE, FIXTURE_DELETED_1693CDB2, xact(c)));
      rejects(
          c,
          FIXTURE_22023_CDCA15BB,
          () ->
              recordAt(
                  c, null, CUTOFF.toString(), null, 0L, ONE, FIXTURE_DELETED_1693CDB2, xact(c)));
      rejects(
          c,
          FIXTURE_55000_F2ADCE46,
          () ->
              recordAt(
                  c,
                  RUN,
                  CUTOFF.plusSeconds(1).toString(),
                  null,
                  0L,
                  ONE,
                  FIXTURE_DELETED_1693CDB2,
                  xact(c)));
      rejects(
          c,
          FIXTURE_55000_F2ADCE46,
          () ->
              recordAt(
                  c,
                  new UUID(0, 62),
                  CUTOFF.toString(),
                  null,
                  0L,
                  ONE,
                  FIXTURE_DELETED_1693CDB2,
                  xact(c)));
      for (String outcome : Arrays.asList(null, "", "SUCCESS", "deleted"))
        rejects(c, FIXTURE_22023_CDCA15BB, () -> record(c, null, 0L, ONE, outcome, xact(c)));
      for (String tx : Arrays.asList(null, "", "-1", "abc", "0".repeat(21)))
        rejects(
            c,
            FIXTURE_22023_CDCA15BB,
            () -> record(c, null, 0L, ONE, FIXTURE_DELETED_1693CDB2, tx));
      rejects(
          c, FIXTURE_55000_F2ADCE46, () -> record(c, null, 0L, ONE, FIXTURE_DELETED_1693CDB2, "0"));
      rejects(
          c,
          FIXTURE_22023_CDCA15BB,
          () -> record(c, null, null, ONE, FIXTURE_DELETED_1693CDB2, xact(c)));
      rejects(
          c,
          FIXTURE_22023_CDCA15BB,
          () -> record(c, null, -1L, ONE, FIXTURE_DELETED_1693CDB2, xact(c)));
      rejects(
          c,
          FIXTURE_22023_CDCA15BB,
          () -> record(c, null, 0L, null, FIXTURE_DELETED_1693CDB2, xact(c)));
      rejects(
          c, FIXTURE_22023_CDCA15BB, () -> record(c, null, 0L, ONE, FIXTURE_END_5AB955DF, xact(c)));
      c.commit();
    }
    try (var c = db.admin()) {
      c.setAutoCommit(false);
      for (String mutation :
          List.of(
              "cutoff='infinity'",
              "cutoff='-infinity'",
              "inspected_count=-1",
              "deleted_count=-1",
              "protected_count=-1",
              "deleted_count=1",
              "protected_count=1",
              "after_message_id='" + ONE + "'",
              "inspected_count=1,deleted_count=1",
              "completed_at='infinity'",
              "completed_at='-infinity'")) {
        rejects(c, "23514", () -> execute(c, "update " + TABLE + " set " + mutation));
      }
      rejects(c, "23502", () -> execute(c, "update " + TABLE + " set cutoff=null"));
      c.rollback();
    }
    sql(
        "update "
            + TABLE
            + " set inspected_count=9223372036854775807,deleted_count=9223372036854775807,after_message_id='"
            + ONE
            + "'");
    inbox(TWO);
    try (var c = inspector()) {
      open(c, RUN, CUTOFF.toString());
      delete(c, TWO);
      assertEquals(
          "22003",
          assertThrows(
                  SQLException.class,
                  () -> record(c, ONE, Long.MAX_VALUE, TWO, FIXTURE_DELETED_1693CDB2, xact(c)))
              .getSQLState());
      c.rollback();
    }
    assertEquals("1", scalar(FIXTURE_SELECT_COUNT_FROM_SCHUBERT_REQUEST_INBOX_E4FAEDDB));
    assertEquals("9223372036854775807", scalar("select inspected_count from " + TABLE));
  }

  @Test
  void backupAndConcurrentRunsStayLocked() throws Exception {
    for (String mutation :
        List.of(
            "status='RUNNING'",
            "status='WARNING'",
            "status='FAILED'",
            "status='SKIPPED'",
            "business_date='2026-09-16'",
            "ended_at=null")) {
      sql("update schubert.batch_runs set " + mutation + " where step='BACKUP_CONFIG'");
      try (var c = inspector()) {
        rejects(c, FIXTURE_55000_F2ADCE46, () -> open(c, RUN, CUTOFF.toString()));
      }
      sql("delete from schubert.batch_runs where step='BACKUP_CONFIG'");
      backup("BACKUP_CONFIG");
    }
    try (var a = inspector();
        var b = inspector();
        var writer = db.admin()) {
      assertEquals(new Progress(null, 0, 0, 0, false), open(a, RUN, CUTOFF.toString()));
      rejects(b, FIXTURE_55P03_0FE714C6, () -> open(b, RUN, CUTOFF.toString()));
      rejects(b, FIXTURE_55P03_0FE714C6, () -> open(b, new UUID(0, 62), CUTOFF.toString()));
      for (String step : List.of("BACKUP_DB", "BACKUP_CONFIG"))
        assertEquals(
            FIXTURE_55P03_0FE714C6,
            assertThrows(
                    SQLException.class,
                    () ->
                        scalar(
                            writer,
                            "select id from schubert.batch_runs where step='"
                                + step
                                + "' for update nowait"))
                .getSQLState());
      a.commit();
      open(a, RUN, CUTOFF.toString());
      assertEquals(
          FIXTURE_55P03_0FE714C6,
          assertThrows(
                  SQLException.class,
                  () -> scalar(writer, "select run_id from " + TABLE + " for update nowait"))
              .getSQLState());
      a.rollback();
      assertEquals(new Progress(null, 0, 0, 0, false), open(b, RUN, CUTOFF.toString()));
      b.commit();
    }
    assertEquals("1", scalar(FIXTURE_SELECT_COUNT_FROM_BDA3EEC8 + TABLE));
  }

  @Test
  void completedProgressRetentionIsBounded() throws Exception {
    Instant edge = CUTOFF.minusSeconds(400L * 86400);
    for (int id = 100; id <= 107; id++)
      progress(
          new UUID(0, id),
          id == 103 ? null : edge.plusNanos(id == 101 ? 0 : id == 102 ? 1000 : -1000));
    progress(RUN, edge.minusNanos(1000));
    sql(
        "insert into schubert.batch_runs(run_id,business_date,step,attempt,started_at,status)"
            + " values('"
            + new UUID(0, 104)
            + "','2025-01-01','INSPECT',1,'2025-01-01','RUNNING'),('"
            + new UUID(0, 105)
            + "','2025-01-01','INSPECT',2,'2025-01-01','FAILED')");
    try (var c = connection("schubert_batch");
        var lock = db.admin()) {
      lock.setAutoCommit(false);
      scalar(
          lock,
          "select run_id from " + TABLE + " where run_id='" + new UUID(0, 106) + "' for update");
      c.setAutoCommit(false);
      assertEquals("1|1|0|OK", purge(c, RUN, CUTOFF.toString(), 1));
      c.rollback();
      assertEquals("9", scalar(FIXTURE_SELECT_COUNT_FROM_BDA3EEC8 + TABLE));
      assertEquals("2|2|0|OK", purge(c, RUN, CUTOFF.toString(), 1000));
      c.commit();
      assertEquals("7", scalar(FIXTURE_SELECT_COUNT_FROM_BDA3EEC8 + TABLE));
      lock.rollback();
      assertEquals("1|1|0|OK", purge(c, RUN, CUTOFF.toString(), 1000));
      c.commit();
      assertEquals("6", scalar(FIXTURE_SELECT_COUNT_FROM_BDA3EEC8 + TABLE));
      assertEquals("0|0|0|OK", purge(c, RUN, CUTOFF.toString(), 1000));
      c.commit();
      for (Integer limit : Arrays.asList(null, 0, 1001))
        rejects(c, FIXTURE_22023_CDCA15BB, () -> purge(c, RUN, CUTOFF.toString(), limit));
      for (String cutoff : Arrays.asList(null, "infinity", "-infinity"))
        rejects(c, FIXTURE_22023_CDCA15BB, () -> purge(c, RUN, cutoff, 1));
      rejects(c, FIXTURE_22023_CDCA15BB, () -> purge(c, null, CUTOFF.toString(), 1));
      c.rollback();
      assertEquals("true", scalar(lock, "select pg_try_advisory_xact_lock(71419602)::text"));
      assertEquals("0|0|0|LOCK_BUSY", purge(c, RUN, CUTOFF.toString(), 1));
      c.commit();
      lock.rollback();
      assertEquals("0|0|0|BACKUP_GATE", purge(c, new UUID(0, 63), CUTOFF.toString(), 1));
      c.commit();
    }
    assertEquals("4", scalar("select count(*) from schubert.batch_runs"));
  }

  @Test
  void rolesAndFixedFunctionsCannotEscalate() throws Exception {
    var signatures =
        List.of(
            OPEN + "(uuid,timestamptz)",
            RECORD + "(uuid,timestamptz,uuid,bigint,uuid,text,text)",
            PURGE + "(uuid,timestamptz,integer)");
    try (var admin = db.admin()) {
      for (String role :
          List.of(
              "schubert_app",
              "schubert_web_session",
              "schubert_batch",
              "schubert_inbox_inspector",
              "schubert_backup",
              "schubert_ops_ro")) {
        assertEquals(
            Boolean.toString(role.equals("schubert_backup")),
            scalar(
                admin,
                "select has_table_privilege('"
                    + role
                    + FIXTURE_VALUE_E91D96ED
                    + TABLE
                    + "','SELECT')::text"));
        for (String permission : List.of("INSERT", "UPDATE", "DELETE", "TRUNCATE"))
          assertEquals(
              "false",
              scalar(
                  admin,
                  "select has_table_privilege('"
                      + role
                      + FIXTURE_VALUE_E91D96ED
                      + TABLE
                      + FIXTURE_VALUE_E91D96ED
                      + permission
                      + "')::text"));
        for (int i = 0; i < signatures.size(); i++) {
          assertEquals(
              Boolean.toString(
                  i == 2 ? role.equals("schubert_batch") : role.equals("schubert_inbox_inspector")),
              scalar(
                  admin,
                  "select has_function_privilege('"
                      + role
                      + FIXTURE_VALUE_E91D96ED
                      + signatures.get(i)
                      + "','EXECUTE')::text"));
        }
        try (var c = connection(role)) {
          if (!role.equals("schubert_backup"))
            assertEquals(
                "42501",
                assertThrows(SQLException.class, () -> scalar(c, "select run_id from " + TABLE))
                    .getSQLState());
          else assertEquals("0", scalar(c, FIXTURE_SELECT_COUNT_FROM_BDA3EEC8 + TABLE));
          for (String statement : List.of("delete from " + TABLE, "set role nk_owner"))
            assertEquals(
                "42501",
                assertThrows(SQLException.class, () -> execute(c, statement)).getSQLState());
        }
      }
      for (int i = 0; i < signatures.size(); i++) {
        String signature = signatures.get(i);
        assertEquals(
            "true|nk_owner",
            scalar(
                admin,
                "select prosecdef::text||'|'||pg_get_userbyid(proowner) from pg_proc where oid='"
                    + signature
                    + "'::regprocedure"));
        assertEquals(
            i == 2
                ? "search_path=pg_catalog, schubert, schubert_web_session|TimeZone=UTC"
                : "search_path=pg_catalog, schubert|TimeZone=UTC",
            scalar(
                admin,
                "select array_to_string(proconfig,'|') from pg_proc where oid='"
                    + signature
                    + "'::regprocedure"));
        assertEquals(
            "false",
            scalar(
                admin,
                "select has_function_privilege('public','" + signature + "','EXECUTE')::text"));
      }
    }
  }

  @Test
  void migrationAndInventoryAreAppendOnly() throws Exception {
    assertEquals(
        String.join(",", VERSIONS),
        scalar(
            "select string_agg(version,',' order by installed_rank) from"
                + " schubert_meta.flyway_schema_history where success and version is not null"));
    assertEquals(
        "159|23|30|24|1",
        scalar(
            "select count(*) filter(where contype='c')||'|'||count(*) filter(where"
                + " contype='f')||'|'||count(*) filter(where contype='u')||'|'||count(*)"
                + " filter(where contype='p')||'|'||count(*) filter(where contype='t') from"
                + " pg_constraint c join pg_namespace n on n.oid=c.connamespace where n.nspname in"
                + " ('schubert','schubert_web_session')"));
    Path migrations =
        Path.of(System.getProperty("nk.pt.repository"))
            .resolve("src/schubert-nk-api/src/main/resources/db/migration");
    var flyway =
        Flyway.configure()
            .dataSource(url, "schubert_migration", "")
            .defaultSchema("schubert_meta")
            .schemas("schubert_meta")
            .initSql("SET ROLE nk_owner")
            .locations("filesystem:" + migrations)
            .cleanDisabled(true)
            .load();
    assertTrue(flyway.validateWithResult().validationSuccessful);
    assertEquals(0, flyway.migrate().migrationsExecuted);
    // V001..010 independently frozen in the previous two boundary test classes.
    assertEquals(
        "18e92bfc225f39c7a0ecaf9bdbeef329e5a47c0af3283d12f858deb4aec09928",
        HexFormat.of()
            .formatHex(
                MessageDigest.getInstance("SHA-256")
                    .digest(
                        Files.readAllBytes(
                            migrations.resolve("V011__batch_outbox_only_cleanup.sql")))));
  }

  private record Progress(
      UUID after, long inspected, long deleted, long protectedRows, boolean complete) {}

  @FunctionalInterface
  private interface Query {
    Object run() throws SQLException;
  }

  private static void rejects(Connection c, String state, Query action) throws SQLException {
    var save = c.setSavepoint();
    assertEquals(state, assertThrows(SQLException.class, action::run).getSQLState());
    c.rollback(save);
    c.releaseSavepoint(save);
  }

  private static Connection connection(String role) throws SQLException {
    return DriverManager.getConnection(url, role, "");
  }

  private static Connection inspector() throws SQLException {
    var c = connection("schubert_inbox_inspector");
    c.setAutoCommit(false);
    return c;
  }

  private static Progress open(Connection c, UUID run, String cutoff) throws SQLException {
    try (var s =
        c.prepareStatement(
            "select after_message_id,inspected_count,deleted_count,protected_count,completed_at"
                + " from "
                + OPEN
                + "(?,?::timestamptz)")) {
      s.setObject(1, run);
      s.setString(2, cutoff);
      return read(s);
    }
  }

  private static Progress record(
      Connection c, UUID after, Long count, UUID message, String outcome, String tx)
      throws SQLException {
    return recordAt(c, RUN, CUTOFF.toString(), after, count, message, outcome, tx);
  }

  private static Progress recordAt(
      Connection c,
      UUID run,
      String cutoff,
      UUID after,
      Long count,
      UUID message,
      String outcome,
      String tx)
      throws SQLException {
    try (var s =
        c.prepareStatement(
            "select after_message_id,inspected_count,deleted_count,protected_count,completed_at"
                + " from "
                + RECORD
                + "(?,?::timestamptz,?,?,?,?,?)")) {
      s.setObject(1, run);
      s.setString(2, cutoff);
      s.setObject(3, after);
      s.setObject(4, count);
      s.setObject(5, message);
      s.setString(6, outcome);
      s.setString(7, tx);
      return read(s);
    }
  }

  private static Progress read(PreparedStatement s) throws SQLException {
    try (var r = s.executeQuery()) {
      assertTrue(r.next());
      var p =
          new Progress(
              r.getObject(1, UUID.class),
              r.getLong(2),
              r.getLong(3),
              r.getLong(4),
              r.getObject(5, java.time.OffsetDateTime.class) != null);
      assertFalse(r.next());
      return p;
    }
  }

  private static String purge(Connection c, UUID run, String cutoff, Integer limit)
      throws SQLException {
    try (var s =
        c.prepareStatement(
            "select target_count||'|'||deleted_count||'|'||skipped_count||'|'||reason_code from "
                + PURGE
                + "(?,?::timestamptz,?)")) {
      s.setObject(1, run);
      s.setString(2, cutoff);
      s.setObject(3, limit);
      try (var r = s.executeQuery()) {
        assertTrue(r.next());
        String result = r.getString(1);
        assertFalse(r.next());
        return result;
      }
    }
  }

  private static void delete(Connection c, UUID message) throws SQLException {
    try (var s = c.prepareStatement("select schubert.maintenance_delete_inbox(?,?,?,?,?)")) {
      s.setObject(1, RUN);
      s.setObject(2, CUTOFF.atOffset(java.time.ZoneOffset.UTC));
      s.setObject(3, message);
      s.setString(4, xact(c));
      s.setBytes(5, digest);
      try (var r = s.executeQuery()) {
        assertTrue(r.next());
        assertTrue(r.getBoolean(1));
        assertFalse(r.next());
      }
    }
  }

  private static String xact(Connection c) throws SQLException {
    return scalar(c, "select pg_current_xact_id()::text");
  }

  private static String scalar(String q) throws SQLException {
    try (var c = db.admin()) {
      return scalar(c, q);
    }
  }

  private static String scalar(Connection c, String q) throws SQLException {
    try (var s = c.createStatement();
        var r = s.executeQuery(q)) {
      assertTrue(r.next());
      String result = r.getString(1);
      assertNotNull(result);
      assertFalse(r.next());
      return result;
    }
  }

  private static Boolean execute(Connection c, String q) throws SQLException {
    try (var s = c.createStatement()) {
      return s.execute(q);
    }
  }

  private static void sql(String q) throws SQLException {
    try (var c = db.admin()) {
      execute(c, q);
    }
  }

  private static void backup(String step) throws SQLException {
    sql(
        "insert into"
            + " schubert.batch_runs(run_id,business_date,step,attempt,started_at,ended_at,status)"
            + " values('"
            + RUN
            + "','2026-09-17','"
            + step
            + "',1,'2026-09-17','2026-09-17','SUCCESS')");
  }

  private static void inbox(UUID id) throws SQLException {
    sql(
        "insert into"
            + " schubert.request_inbox(message_id,correlation_id,request_layout_id,request_version,owner_user_id,request_fingerprint_hmac,fingerprint_key_version,processing_state,result_ref_type,response_layout_id,response_version,response_body_encrypted,response_key_version,created_at,completed_at,expires_at)"
            + " values('"
            + id
            + FIXTURE_VALUE_E91D96ED
            + id
            + "','GAMREQ01','001',7,repeat('a',64),'v1','ERROR','NONE','GAMRSP01','001',decode(repeat('00',30),'hex'),'v1','2026-09-01','2026-09-01','2026-09-10')");
  }

  private static void progress(UUID id, Instant completed) throws SQLException {
    try (var c = db.admin();
        var s =
            c.prepareStatement(
                "insert into " + TABLE + "(run_id,cutoff,completed_at) values(?,'2025-01-01',?)")) {
      s.setObject(1, id);
      s.setObject(2, completed == null ? null : completed.atOffset(java.time.ZoneOffset.UTC));
      assertEquals(1, s.executeUpdate());
    }
  }
}
