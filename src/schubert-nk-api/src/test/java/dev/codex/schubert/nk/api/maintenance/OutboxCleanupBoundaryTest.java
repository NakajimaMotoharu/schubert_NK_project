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
import java.time.Instant;
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

/** PT-DB-INBOX-065..072; SS331 3.7/332 11.4; BUG-014/YKT-012; SQL postconditions. */
final class OutboxCleanupBoundaryTest {
  @TempDir static Path root;
  private static ApiLogDatabaseFixture db;
  private static String url;
  private static final UUID RUN = new UUID(0, 52);
  private static final Instant CUTOFF = Instant.parse("2026-09-17T00:00:00Z");
  private static final String FUNCTION = "schubert.maintenance_cleanup_message_stores";
  private static final String SIGNATURE = FUNCTION + "(uuid,timestamptz,integer)";
  private static final List<String> TABLES =
      List.of("schubert.mq_outbox", "schubert_web_session.web_log_outbox");

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
  void reset() throws SQLException {
    for (String table :
        List.of("schubert.request_inbox", TABLES.get(0), TABLES.get(1), "schubert.batch_runs"))
      sql("delete from " + table);
    backup("BACKUP_DB");
    backup("BACKUP_CONFIG");
    sql(
        "insert into schubert.app_users(id,username,username_key,password_hash,role,status,password_changed_at,created_at,updated_at) values(7,'Learner','learner','synthetic-unused','USER','ACTIVE','2026-09-01','2026-09-01','2026-09-01') on conflict(id) do nothing");
  }

  @Test
  void inboxRowsAreNeverTouched() throws Exception {
    var routes =
        List.of(
            "LGN", "LOG", "GAM", "SPK", "RTE", "SCF", "SRC", "SCN", "AUD", "ANM", "ANL", "VID",
            "MCT", "MCS", "MTR", "MED", "USR", "UDT", "LGS", "UCR", "UST", "URL", "UPW", "ULK",
            "QSB", "NTS", "NTD", "NTC", "QSS", "QSD", "QDL", "ZZZ");
    int id = 1;
    for (String route : routes)
      for (String state : List.of("PROCESSING", "COMPLETED", "ERROR")) inbox(id++, route, state);
    for (String type : List.of("AUTH_SESSION", "USER", "QUESTION", "JOB", "SCENARIO_FILE")) {
      sql(
          "update schubert.request_inbox set result_ref_type='"
              + type
              + "',result_ref_id="
              + (type.equals("AUTH_SESSION") ? "null" : "7")
              + ",result_ref_uuid="
              + (type.equals("AUTH_SESSION") ? "'00000000-0000-0000-0000-000000000123'" : "null")
              + " where message_id='00000000-0000-0000-0000-0000000000"
              + String.format("%02x", id - 2)
              + "'");
      id -= 3;
    }
    String before =
        scalar(
            "select md5(string_agg(row_to_json(i)::text,',' order by message_id)) from schubert.request_inbox i");
    assertEquals("96", scalar("select count(*) from schubert.request_inbox"));
    outbox(false, 1, "SENT", CUTOFF.minusSeconds(604801), null);
    outbox(true, 1, "SENT", CUTOFF.minusSeconds(604801), null);
    try (var c = batch()) {
      assertEquals("2|2|0|OK", cleanup(c, RUN, CUTOFF.toString(), 1000));
      assertEquals("0|0|0|OK", cleanup(c, RUN, CUTOFF.toString(), 1000));
    }
    assertEquals(
        before,
        scalar(
            "select md5(string_agg(row_to_json(i)::text,',' order by message_id)) from schubert.request_inbox i"));
    assertEquals("96", scalar("select count(*) from schubert.request_inbox"));
    assertEquals("0", rows());
  }

  @Test
  void outboxBoundariesAndSharedLimit() throws Exception {
    Instant boundary = CUTOFF.minusSeconds(604800);
    for (boolean web : List.of(false, true)) {
      outbox(web, 1, "SENT", boundary.minusNanos(1000), null);
      outbox(web, 2, "SENT", boundary, null);
      outbox(web, 3, "SENT", boundary.plusNanos(1000), null);
      outbox(web, 4, "SENT", boundary.minusNanos(1000), CUTOFF.minusNanos(1000));
      outbox(web, 5, "SENT", boundary.minusNanos(1000), CUTOFF);
      outbox(web, 6, "SENT", boundary.minusNanos(1000), CUTOFF.plusNanos(1000));
      outbox(web, 7, "PENDING", null, null);
      outbox(web, 8, "ERROR", null, CUTOFF.minusSeconds(1));
    }
    try (var c = batch()) {
      c.setAutoCommit(false);
      assertEquals("1|1|0|OK", cleanup(c, RUN, CUTOFF.toString(), 1));
      assertEquals("16", rows());
      c.rollback();
      assertEquals("16", rows());
      assertEquals("1|1|0|OK", cleanup(c, RUN, CUTOFF.toString(), 1));
      c.commit();
      assertEquals("2,3,4,5,6,7,8", ids(TABLES.get(0)));
      assertEquals("1,2,3,4,5,6,7,8", ids(TABLES.get(1)));
      assertEquals("3|3|0|OK", cleanup(c, RUN, CUTOFF.toString(), 1000));
      c.commit();
      for (String table : TABLES) assertEquals("2,3,5,6,7,8", ids(table));
      assertEquals("0|0|0|OK", cleanup(c, RUN, CUTOFF.toString(), 1000));
      c.commit();
    }
  }

  @Test
  void invalidArgumentsAndFixedReasons() throws Exception {
    outbox(false, 1, "SENT", CUTOFF.minusSeconds(604801), null);
    try (var c = batch()) {
      Object[][] invalid = {
        {null, CUTOFF.toString(), 1},
        {RUN, null, 1},
        {RUN, CUTOFF.toString(), null},
        {RUN, "infinity", 1},
        {RUN, "-infinity", 1},
        {RUN, CUTOFF.toString(), 0},
        {RUN, CUTOFF.toString(), 1001}
      };
      for (Object[] args : invalid) {
        SQLException ex =
            assertThrows(
                SQLException.class,
                () -> cleanup(c, (UUID) args[0], (String) args[1], (Integer) args[2]));
        assertEquals("22023", ex.getSQLState());
        assertFalse(ex.getMessage().contains(RUN.toString()));
      }
      assertEquals("0|0|0|BACKUP_GATE", cleanup(c, new UUID(0, 53), CUTOFF.toString(), 1));
    }
    sql("delete from schubert.batch_runs");
    try (var c = batch()) {
      assertEquals("0|0|0|BACKUP_GATE", cleanup(c, RUN, CUTOFF.toString(), 1));
    }
    assertEquals("1", rows());
    backup("BACKUP_DB");
    backup("BACKUP_CONFIG");
    outbox(true, 1, "SENT", CUTOFF.minusSeconds(604801), null);
    sql(
        "create function schubert.pt_cleanup_failure() returns trigger language plpgsql as $f$ begin raise exception using errcode='P0001',message='synthetic cleanup failure'; end $f$");
    sql(
        "create trigger pt_cleanup_failure before delete on schubert_web_session.web_log_outbox for each row execute function schubert.pt_cleanup_failure()");
    try (var c = batch()) {
      assertEquals(
          "P0001",
          assertThrows(SQLException.class, () -> cleanup(c, RUN, CUTOFF.toString(), 1000))
              .getSQLState());
      assertEquals("2", rows()); // API deletion preceding Web trigger failure must roll back too.
    } finally {
      sql("drop trigger pt_cleanup_failure on schubert_web_session.web_log_outbox");
      sql("drop function schubert.pt_cleanup_failure()");
    }
    try (var c = batch()) {
      assertEquals("2|2|0|OK", cleanup(c, RUN, CUTOFF.toString(), 1000));
    }
    assertEquals("0", rows());
  }

  @Test
  void backupStatesAndDatesAreLocked() throws Exception {
    outbox(false, 1, "SENT", CUTOFF.minusSeconds(604801), null);
    for (String mutation :
        List.of(
            "status='RUNNING'",
            "status='WARNING'",
            "status='FAILED'",
            "status='SKIPPED'",
            "business_date='2026-09-16'",
            "ended_at=null",
            "run_id='00000000-0000-0000-0000-000000000099'")) {
      sql("update schubert.batch_runs set " + mutation + " where step='BACKUP_CONFIG'");
      try (var c = batch()) {
        assertEquals("0|0|0|BACKUP_GATE", cleanup(c, RUN, CUTOFF.toString(), 1));
      }
      assertEquals("1", rows());
      sql("delete from schubert.batch_runs where step='BACKUP_CONFIG'");
      backup("BACKUP_CONFIG");
    }
    try (var c = batch();
        var writer = db.admin()) {
      c.setAutoCommit(false);
      assertEquals("1|1|0|OK", cleanup(c, RUN, CUTOFF.toString(), 1));
      for (String step : List.of("BACKUP_DB", "BACKUP_CONFIG")) {
        assertEquals(
            "55P03",
            assertThrows(
                    SQLException.class,
                    () ->
                        scalar(
                            writer,
                            "select id from schubert.batch_runs where step='"
                                + step
                                + "' for update nowait"))
                .getSQLState());
      }
      c.rollback();
      assertEquals("1", rows());
      assertFalse(
          scalar(
                  writer,
                  "select id from schubert.batch_runs where step='BACKUP_CONFIG' for update nowait")
              .isEmpty());
    }
  }

  @Test
  void competingMaintenanceNeverDeletes() throws Exception {
    for (long id : List.of(1L, 2L)) outbox(false, id, "SENT", CUTOFF.minusSeconds(604801), null);
    try (var c = batch();
        var locked = db.admin()) {
      locked.setAutoCommit(false);
      assertEquals("true", scalar(locked, "select pg_try_advisory_xact_lock(71419602)::text"));
      assertEquals("0|0|0|LOCK_BUSY", cleanup(c, RUN, CUTOFF.toString(), 1000));
      assertEquals("2", rows());
      locked.rollback();
      assertEquals("1", scalar(locked, "select id from schubert.mq_outbox where id=1 for update"));
      assertEquals("1|1|0|OK", cleanup(c, RUN, CUTOFF.toString(), 1000));
      assertEquals("1", ids(TABLES.get(0)));
      assertEquals("0|0|0|OK", cleanup(c, RUN, CUTOFF.toString(), 1000));
      locked.rollback();
      assertEquals("1|1|0|OK", cleanup(c, RUN, CUTOFF.toString(), 1000));
      assertEquals("0", rows());
    }
  }

  @Test
  void backupSnapshotCannotBeReplaced() throws Exception {
    sql("delete from schubert.batch_runs where step='BACKUP_CONFIG'");
    outbox(false, 1, "SENT", CUTOFF.minusSeconds(604801), null);
    try (var c = batch();
        var writer = db.admin();
        var pool = Executors.newSingleThreadExecutor()) {
      writer.setAutoCommit(false);
      scalar(writer, "select id from schubert.batch_runs where step='BACKUP_DB' for update");
      int pid = Integer.parseInt(scalar(c, "select pg_backend_pid()"));
      var result = pool.submit(() -> cleanup(c, RUN, CUTOFF.toString(), 1000));
      try {
        awaitBlocked(pid);
        backup("BACKUP_CONFIG");
      } finally {
        writer.commit();
      }
      assertEquals("0|0|0|BACKUP_GATE", result.get(5, TimeUnit.SECONDS));
      assertEquals("1", rows());
      assertEquals("1|1|0|OK", cleanup(c, RUN, CUTOFF.toString(), 1000));
      assertEquals("0", rows());
    }
  }

  @Test
  void currentFunctionsAndRolesCloseBypasses() throws Exception {
    try (var c = db.admin()) {
      assertEquals(
          "true|nk_owner",
          scalar(
              c,
              "select prosecdef::text||'|'||pg_get_userbyid(proowner) from pg_proc where oid='"
                  + SIGNATURE
                  + "'::regprocedure"));
      assertEquals(
          "{\"search_path=pg_catalog, schubert, schubert_web_session\",TimeZone=UTC}",
          scalar(
              c,
              "select proconfig::text from pg_proc where oid='" + SIGNATURE + "'::regprocedure"));
      for (String role :
          List.of(
              "schubert_batch",
              "schubert_app",
              "schubert_inbox_inspector",
              "schubert_web_session",
              "schubert_backup",
              "schubert_ops_ro")) {
        assertEquals(
            Boolean.toString(role.equals("schubert_batch")),
            scalar(
                c,
                "select has_function_privilege('"
                    + role
                    + "','"
                    + SIGNATURE
                    + "','EXECUTE')::text"));
        if (!role.equals("schubert_batch"))
          try (var denied = DriverManager.getConnection(url, role, "")) {
            assertEquals(
                "42501",
                assertThrows(SQLException.class, () -> cleanup(denied, RUN, CUTOFF.toString(), 1))
                    .getSQLState());
          }
      }
      assertEquals(
          "0",
          scalar(
              c,
              "select count(*) from pg_proc p join pg_namespace n on n.oid=p.pronamespace where n.nspname='schubert' and p.proname like 'maintenance_cleanup_%' and lower(pg_get_functiondef(p.oid)) like '%request_inbox%'"));
      assertEquals(
          "0",
          scalar(
              c,
              "select count(*) from pg_proc p, lateral aclexplode(coalesce(p.proacl,acldefault('f',p.proowner))) a where p.oid='"
                  + SIGNATURE
                  + "'::regprocedure and a.grantee=0 and a.privilege_type='EXECUTE'"));
      var deletes = new ArrayList<String>();
      try (var s = c.createStatement();
          var row =
              s.executeQuery(
                  "select p.proname from pg_proc p join pg_namespace n on n.oid=p.pronamespace where n.nspname='schubert' and p.prokind='f' and lower(pg_get_functiondef(p.oid)) like '%delete from schubert.request_inbox%' order by p.proname")) {
        while (row.next()) deletes.add(row.getString(1));
      }
      assertEquals(List.of("maintenance_delete_auth_inbox", "maintenance_delete_inbox"), deletes);
      for (String name : deletes) {
        String signature = "schubert." + name + "(uuid,timestamptz,uuid,text,bytea)";
        assertEquals(
            "false",
            scalar(
                c,
                "select has_function_privilege('schubert_batch','"
                    + signature
                    + "','EXECUTE')::text"));
        assertEquals(
            "true",
            scalar(
                c,
                "select has_function_privilege('schubert_inbox_inspector','"
                    + signature
                    + "','EXECUTE')::text"));
      }
      // BUG-091/YKT-082: reject both wrong UTC and unapproved extra settings, not only bad paths.
      c.setAutoCommit(false);
      for (String setting : List.of("timezone='Asia/Tokyo'", "statement_timeout='1s'")) {
        try (var s = c.createStatement()) {
          s.execute("alter function " + SIGNATURE + " set " + setting);
        }
        assertEquals(
            // SSC175 adds one fixed function; one deliberately altered function is excluded.
            "8",
            scalar(
                c,
                "select count(*) from pg_proc p join pg_namespace n on n.oid=p.pronamespace "
                    + "where n.nspname='schubert' and p.proname like 'maintenance_cleanup_%' "
                    + "and p.prosecdef and p.proconfig="
                    + "array['search_path=pg_catalog, schubert, schubert_web_session','TimeZone=UTC'] "
                    + ""));
        c.rollback();
      }
    }
    try (var c = batch()) {
      for (String query :
          List.of(
              "select message_id from schubert.request_inbox",
              "delete from schubert.request_inbox",
              "select schubert.maintenance_delete_inbox(null,null,null,null,null)",
              "select schubert.maintenance_delete_auth_inbox(null,null,null,null,null)",
              "select schubert.maintenance_lock_inbox_backup(null,null)",
              "set role nk_owner",
              "set role schubert_inbox_inspector"))
        assertEquals(
            "42501", assertThrows(SQLException.class, () -> scalar(c, query)).getSQLState());
    }
  }

  @Test
  void migrationAndLegacyOraclesRemainExplicit() throws Exception {
    assertEquals(
        MigrationInventory.COUNT_TEXT,
        scalar(
            "select count(*) from schubert_meta.flyway_schema_history where success and version is not null"));
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
    // V001..009 hashes are independently fixed in InboxMaintenanceBoundaryTest; V010 was frozen
    // before V011.
    assertEquals(
        "c27a17adba2367ded5dcefe1532f5b42e7e4e35259f32388fe2667049e8644b0",
        HexFormat.of()
            .formatHex(
                MessageDigest.getInstance("SHA-256")
                    .digest(
                        Files.readAllBytes(
                            migrations.resolve(
                                "V010__full_inbox_scan_and_restricted_deletion.sql")))));
    inbox(1, "LGN", "COMPLETED");
    inbox(2, "LGN", "PROCESSING");
    try (var c = batch()) {
      assertEquals("0|0|0|OK", cleanup(c, RUN, CUTOFF.toString(), 10));
    }
    assertEquals("2", scalar("select count(*) from schubert.request_inbox"));
  }

  private static Connection batch() throws SQLException {
    return DriverManager.getConnection(url, "schubert_batch", "");
  }

  private static String cleanup(Connection c, UUID run, String cutoff, Integer limit)
      throws SQLException {
    try (var s =
        c.prepareStatement(
            "select target_count,deleted_count,skipped_count,reason_code from "
                + FUNCTION
                + "(?,?::timestamptz,?)")) {
      s.setObject(1, run);
      s.setString(2, cutoff);
      s.setObject(3, limit);
      try (var row = s.executeQuery()) {
        assertTrue(row.next());
        String result =
            row.getLong(1) + "|" + row.getLong(2) + "|" + row.getLong(3) + "|" + row.getString(4);
        assertFalse(row.next());
        return result;
      }
    }
  }

  private static String scalar(String query) throws SQLException {
    try (var c = db.admin()) {
      return scalar(c, query);
    }
  }

  private static String scalar(Connection c, String query) throws SQLException {
    try (var s = c.createStatement();
        var row = s.executeQuery(query)) {
      assertTrue(row.next());
      String value = row.getString(1);
      assertNotNull(value);
      assertFalse(row.next());
      return value;
    }
  }

  private static void sql(String query) throws SQLException {
    try (var c = db.admin();
        var s = c.createStatement()) {
      s.execute(query);
    }
  }

  private static String rows() throws SQLException {
    return scalar(
        "select (select count(*) from schubert.mq_outbox)+(select count(*) from schubert_web_session.web_log_outbox)");
  }

  private static String ids(String table) throws SQLException {
    return scalar("select coalesce(string_agg(id::text,',' order by id),'') from " + table);
  }

  private static void backup(String step) throws SQLException {
    try (var c = db.admin();
        var s =
            c.prepareStatement(
                "insert into schubert.batch_runs(run_id,business_date,step,attempt,started_at,ended_at,status) values(?,'2026-09-17',?,1,?,?,'SUCCESS')")) {
      s.setObject(1, RUN);
      s.setString(2, step);
      s.setObject(3, CUTOFF.atOffset(java.time.ZoneOffset.UTC));
      s.setObject(4, CUTOFF.atOffset(java.time.ZoneOffset.UTC));
      assertEquals(1, s.executeUpdate());
    }
  }

  private static void outbox(boolean web, long id, String status, Instant sent, Instant lease)
      throws SQLException {
    String table = TABLES.get(web ? 1 : 0);
    String columns = web ? "payload_ciphertext,key_version" : "body,destination";
    String values =
        web ? "decode(repeat('00',30),'hex'),'unused-v1'" : "decode('00','hex'),'nk.async.work'";
    try (var c = db.admin();
        var s =
            c.prepareStatement(
                "insert into "
                    + table
                    + "(id,message_id,correlation_id,layout_id,layout_version,"
                    + columns
                    + ",status,next_attempt_at,created_at,sent_at,lease_owner,lease_until) values(?,?,?,?,'001',"
                    + values
                    + ",?,?,?,?,?,?)")) {
      s.setLong(1, id);
      s.setObject(2, new UUID(0, id));
      s.setObject(3, new UUID(1, id));
      s.setString(4, web ? "WLGEVT01" : "QWKREQ01");
      s.setString(5, status);
      s.setObject(6, CUTOFF.minusSeconds(864000).atOffset(java.time.ZoneOffset.UTC));
      s.setObject(7, CUTOFF.minusSeconds(864000).atOffset(java.time.ZoneOffset.UTC));
      s.setObject(8, sent == null ? null : sent.atOffset(java.time.ZoneOffset.UTC));
      s.setString(9, lease == null ? null : "synthetic-worker");
      s.setObject(10, lease == null ? null : lease.atOffset(java.time.ZoneOffset.UTC));
      assertEquals(1, s.executeUpdate());
    }
  }

  private static void inbox(int id, String route, String state) throws SQLException {
    boolean processing = state.equals("PROCESSING");
    boolean token = Set.of("UCR", "UST", "URL", "UPW", "ULK", "QSB", "NTC", "QDL").contains(route);
    try (var c = db.admin();
        var s =
            c.prepareStatement(
                "insert into schubert.request_inbox(message_id,correlation_id,request_layout_id,request_version,owner_user_id,operation_token,request_fingerprint_hmac,fingerprint_key_version,processing_state,result_ref_type,response_layout_id,response_version,response_body_encrypted,response_key_version,created_at,completed_at,expires_at) values(?,?,?,'001',?,?,repeat('a',64),'v1',?,?,?,?,?,?,'2026-09-01',?,'2026-09-10')")) {
      s.setObject(1, new UUID(0, id));
      s.setObject(2, new UUID(1, id));
      s.setString(3, route + "REQ01");
      s.setObject(4, route.equals("LGN") ? null : 7L);
      s.setObject(5, token ? new UUID(2, id) : null);
      s.setString(6, state);
      s.setString(7, processing ? null : "NONE");
      s.setString(8, processing ? null : route + "RSP01");
      s.setString(9, processing ? null : "001");
      s.setBytes(10, processing || id % 2 == 0 ? null : new byte[30]);
      s.setString(11, processing || id % 2 == 0 ? null : "v1");
      s.setObject(
          12,
          processing
              ? null
              : Instant.parse("2026-09-01T00:00:00Z").atOffset(java.time.ZoneOffset.UTC));
      assertEquals(1, s.executeUpdate());
    }
  }

  private static void awaitBlocked(int pid) throws SQLException {
    long deadline = System.nanoTime() + TimeUnit.SECONDS.toNanos(4);
    try (var c = db.admin();
        var s = c.prepareStatement("select cardinality(pg_blocking_pids(?))>0")) {
      s.setInt(1, pid);
      do {
        try (var row = s.executeQuery()) {
          assertTrue(row.next());
          if (row.getBoolean(1)) return;
        }
      } while (System.nanoTime() < deadline);
      fail("controlled backup lock not reached");
    }
  }
}
