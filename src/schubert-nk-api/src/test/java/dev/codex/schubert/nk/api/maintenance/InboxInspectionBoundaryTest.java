package dev.codex.schubert.nk.api.maintenance;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assertions.fail;

import dev.codex.schubert.nk.api.database.MigrationInventory;
import dev.codex.schubert.nk.api.idempotency.InboxResultReference;
import dev.codex.schubert.nk.api.idempotency.ResponseSnapshotIdentity;
import dev.codex.schubert.nk.api.logging.ApiLogDatabaseFixture;
import java.nio.file.Path;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;
import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import org.flywaydb.core.Flyway;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** PT-DB-INBOX-017..024; independent SQLSTATE/catalog/row and lock postconditions for V008. */
final class InboxInspectionBoundaryTest {
  private static final String FIXTURE_SELECT_COUNT_FROM_SCHUBERT_REQUEST_INBOX_E4FAEDDB =
      "select count(*) from schubert.request_inbox";
  private static final String FIXTURE_PGPT_ADMIN_F5D1227C = "pgpt_admin";
  private static final String FIXTURE_SCHUBERT_APP_5AB151CF = "schubert_app";
  private static final String FIXTURE_LGNREQ01_217C66A4 = "LGNREQ01";
  private static final String FIXTURE_ERROR_F717E7D8 = "ERROR";
  private static final String FIXTURE_COMPLETED_BA0AE16A = "COMPLETED";
  private static final String FIXTURE_55P03_0FE714C6 = "55P03";
  @TempDir static Path root;
  private static ApiLogDatabaseFixture db;
  private static String url;
  private static final String ROLE = "schubert_inbox_inspector";
  private static final UUID RUN = new UUID(0, 42);
  private static final UUID SESSION = new UUID(0, 104);
  private static final Instant CUTOFF = Instant.parse("2026-09-09T00:00:00.123Z");
  private static final String CALL =
      "select message_id from schubert.maintenance_next_auth_inbox('"
          + RUN
          + "','2026-09-09T00:00:00.123Z',null)";

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
  void seed() throws Exception {
    try (var c = db.api();
        var s = c.createStatement()) {
      for (String table :
          List.of("request_inbox", "auth_sessions", "app_logs", "batch_runs", "app_users"))
        s.execute("delete from schubert." + table);
      s.execute(
          "insert into schubert.app_users(id,username,username_key,password_hash,role,status,password_changed_at,created_at,updated_at) values(7,'Learner','learner','synthetic-unused','USER','ACTIVE','2026-09-09','2026-09-09','2026-09-09')");
    }
  }

  @Test
  void roleAndFunctionCatalogAreClosed() throws Exception {
    try (var c = db.admin();
        var s = c.createStatement();
        var r =
            s.executeQuery(
                "select rolcanlogin,rolsuper,rolcreatedb,rolcreaterole,rolreplication,rolbypassrls from pg_roles where rolname='schubert_inbox_inspector'")) {
      assertTrue(r.next());
      assertTrue(r.getBoolean(1));
      for (int i = 2; i <= 6; i++) assertFalse(r.getBoolean(i));
      assertFalse(r.next());
    }
    assertEquals(
        "0",
        scalar(
            FIXTURE_PGPT_ADMIN_F5D1227C,
            "select count(*) from pg_auth_members where member=(select oid from pg_roles where rolname='schubert_inbox_inspector')"));
    assertEquals(
        "nk_owner|true|search_path=pg_catalog, schubert,TimeZone=UTC",
        scalar(
            FIXTURE_PGPT_ADMIN_F5D1227C,
            "select pg_get_userbyid(proowner)||'|'||prosecdef::text||'|'||array_to_string(proconfig,',') from pg_proc where oid='schubert.maintenance_next_auth_inbox(uuid,timestamptz,uuid)'::regprocedure"));
    assertEquals(
        "false",
        scalar(
            FIXTURE_PGPT_ADMIN_F5D1227C,
            "select has_function_privilege('public','schubert.maintenance_next_auth_inbox(uuid,timestamptz,uuid)','execute')::text"));
    assertEquals(
        "true",
        scalar(
            ROLE,
            "select has_function_privilege(current_user,'schubert.maintenance_next_auth_inbox(uuid,timestamptz,uuid)','execute')::text"));
  }

  @Test
  void backupAndNullArgumentsFailClosed() throws Exception {
    for (String args :
        List.of(
            "null,'2026-09-09',null",
            "'" + RUN + "',null,null",
            "'" + RUN + "','infinity',null",
            "'" + RUN + "','-infinity',null"))
      denied(
          ROLE,
          "22023",
          "select message_id from schubert.maintenance_next_auth_inbox(" + args + ")");
    denied(ROLE, "55000", CALL);
    backups();
    for (String mutation :
        List.of(
            "delete from schubert.batch_runs where step='BACKUP_DB'",
            "delete from schubert.batch_runs where step='BACKUP_CONFIG'",
            "update schubert.batch_runs set status='FAILED'",
            "update schubert.batch_runs set ended_at=null",
            "update schubert.batch_runs set business_date='2026-09-08'",
            "update schubert.batch_runs set run_id='00000000-0000-0000-0000-000000000099'")) {
      try (var c = db.api();
          var s = c.createStatement()) {
        s.execute(mutation);
      }
      denied(ROLE, "55000", CALL);
      try (var c = db.api();
          var s = c.createStatement()) {
        s.execute("delete from schubert.batch_runs");
      }
      backups();
    }
    try (var c = inspection()) {
      assertEquals(List.of(), read(c, null));
      c.rollback();
    }
    assertEquals(
        "0",
        scalar(
            FIXTURE_SCHUBERT_APP_5AB151CF,
            FIXTURE_SELECT_COUNT_FROM_SCHUBERT_REQUEST_INBOX_E4FAEDDB));
  }

  @Test
  void expiryStateLayoutAndCursorAreExact() throws Exception {
    backups();
    try (var c = db.api()) {
      inbox(
          c, 5, FIXTURE_LGNREQ01_217C66A4, FIXTURE_ERROR_F717E7D8, CUTOFF.minusNanos(1000), false);
      inbox(c, 4, "LOGREQ01", FIXTURE_COMPLETED_BA0AE16A, CUTOFF.minusSeconds(1), false);
      inbox(c, 1, FIXTURE_LGNREQ01_217C66A4, "PROCESSING", CUTOFF.minusSeconds(1), false);
      inbox(c, 2, "GAMREQ01", FIXTURE_COMPLETED_BA0AE16A, CUTOFF.minusSeconds(1), false);
      inbox(c, 3, FIXTURE_LGNREQ01_217C66A4, FIXTURE_COMPLETED_BA0AE16A, CUTOFF, false);
      inbox(c, 6, "LOGREQ01", FIXTURE_ERROR_F717E7D8, CUTOFF.plusNanos(1000), false);
    }
    try (var c = inspection()) {
      assertEquals(List.of(new UUID(0, 4)), read(c, null));
      assertEquals(List.of(new UUID(0, 5)), read(c, new UUID(0, 4)));
      assertEquals(List.of(), read(c, new UUID(0, 5)));
      assertEquals(List.of(), read(c, new UUID(0, 999)));
      c.rollback();
    }
    assertEquals(
        "6",
        scalar(
            FIXTURE_SCHUBERT_APP_5AB151CF,
            FIXTURE_SELECT_COUNT_FROM_SCHUBERT_REQUEST_INBOX_E4FAEDDB));
  }

  @Test
  void candidateLocksLiveUntilCallerEndsTransaction() throws Exception {
    backups();
    try (var c = db.api()) {
      inbox(c, 1, FIXTURE_LGNREQ01_217C66A4, FIXTURE_ERROR_F717E7D8, CUTOFF.minusSeconds(1), false);
    }
    try (var held = inspection()) {
      assertEquals(List.of(new UUID(0, 1)), read(held, null));
      denied(
          FIXTURE_SCHUBERT_APP_5AB151CF,
          FIXTURE_55P03_0FE714C6,
          "select message_id from schubert.request_inbox for update nowait");
      try (var concurrent = db.api();
          var s = concurrent.createStatement()) {
        s.execute("set lock_timeout='50ms'");
        for (String change :
            List.of(
                "update schubert.request_inbox set fingerprint_key_version='v2'",
                "delete from schubert.request_inbox"))
          assertEquals(
              FIXTURE_55P03_0FE714C6,
              assertThrows(SQLException.class, () -> s.execute(change)).getSQLState());
      }
      held.rollback();
      assertEquals(
          "00000000-0000-0000-0000-000000000001",
          scalar(
              FIXTURE_SCHUBERT_APP_5AB151CF,
              "select message_id::text from schubert.request_inbox for update nowait"));
    }
  }

  @Test
  void sessionAndBackupLocksProtectReadOnlyValidation() throws Exception {
    backups();
    var id = ResponseSnapshotIdentity.anonymous(new UUID(0, 101), "LGNRSP01", "001");
    try (var f = new AuthenticationInboxInspectorTest.Fixture()) {
      var saved = f.saved(id, "0000", InboxResultReference.authSession(SESSION));
      try (var c = db.api()) {
        f.seed(c, true);
        inbox(
            c,
            101,
            FIXTURE_LGNREQ01_217C66A4,
            FIXTURE_COMPLETED_BA0AE16A,
            CUTOFF.minusSeconds(1),
            true);
        try (var s =
            c.prepareStatement(
                "update schubert.request_inbox set response_body_encrypted=?,response_key_version='s1',completed_at=?")) {
          s.setBytes(1, saved.responseSnapshot().orElseThrow().ciphertext());
          s.setObject(2, saved.completedAt().atOffset(java.time.ZoneOffset.UTC));
          assertEquals(1, s.executeUpdate());
        }
      }
      try (var held = inspection()) {
        assertEquals(List.of(new UUID(0, 101)), read(held, null));
        assertTrue(f.inspector.isConsistent(held, id, saved));
        denied(
            FIXTURE_SCHUBERT_APP_5AB151CF,
            FIXTURE_55P03_0FE714C6,
            "select id from schubert.auth_sessions for update nowait");
        denied(
            "schubert_batch",
            FIXTURE_55P03_0FE714C6,
            "select id from schubert.batch_runs for update nowait");
        held.rollback();
      }
      try (var c = db.api();
          var s = c.createStatement()) {
        s.execute("delete from schubert.auth_sessions");
      }
      try (var held = inspection()) {
        assertEquals(List.of(new UUID(0, 101)), read(held, null));
        assertFalse(f.inspector.isConsistent(held, id, saved));
        held.rollback();
      }
      assertEquals(
          "1",
          scalar(
              FIXTURE_SCHUBERT_APP_5AB151CF,
              FIXTURE_SELECT_COUNT_FROM_SCHUBERT_REQUEST_INBOX_E4FAEDDB));
    }
    // BUG-080: lock wait pins the first query snapshot before CONFIG is committed.
    try (var setup = db.api();
        var statement = setup.createStatement()) {
      statement.execute("delete from schubert.batch_runs where step='BACKUP_CONFIG'");
    }
    try (var writer = db.api();
        var inspected = inspection();
        var pool = Executors.newSingleThreadExecutor()) {
      writer.setAutoCommit(false);
      try (var statement = writer.createStatement()) {
        statement.execute("select id from schubert.batch_runs where step='BACKUP_DB' for update");
      }
      int pid;
      try (var statement = inspected.createStatement();
          var row = statement.executeQuery("select pg_backend_pid()")) {
        assertTrue(row.next());
        pid = row.getInt(1);
      }
      var outcome =
          pool.submit(
              () -> {
                try {
                  read(inspected, null);
                  inspected.rollback();
                  return "ACCEPTED";
                } catch (SQLException failure) {
                  inspected.rollback();
                  return failure.getSQLState();
                }
              });
      awaitBlocked(pid);
      backup("BACKUP_CONFIG");
      writer.commit();
      assertEquals("55000", outcome.get(5, TimeUnit.SECONDS));
    }
    try (var retry = inspection()) {
      assertEquals(List.of(new UUID(0, 101)), read(retry, null));
      denied(
          "schubert_batch",
          FIXTURE_55P03_0FE714C6,
          "select id from schubert.batch_runs for update nowait");
      retry.rollback();
    }
  }

  @Test
  void noRoleCanEscalateInspectionPrivileges() throws Exception {
    for (String role :
        List.of(
            FIXTURE_SCHUBERT_APP_5AB151CF,
            "schubert_batch",
            "schubert_backup",
            "schubert_web_session",
            "schubert_ops_ro")) denied(role, "42501", CALL);
    for (String sql :
        List.of(
            "select response_body_encrypted from schubert.request_inbox",
            "select password_hash from schubert.app_users",
            "select id from schubert_web_session.web_http_sessions",
            "update schubert.auth_sessions set revoked=false",
            "delete from schubert.request_inbox",
            "insert into schubert.batch_runs(run_id) values(null)",
            "create table schubert.forbidden(id int)",
            "set role nk_owner",
            "set role schubert_app",
            "select expires_at from schubert.auth_sessions",
            "select last_accessed_at from schubert.auth_sessions",
            "select client_address from schubert.auth_sessions")) denied(ROLE, "42501", sql);
    try (var c = connection(ROLE);
        var s = c.createStatement();
        var r =
            s.executeQuery(
                "select id,user_id,created_message_id,context_hash,context_ciphertext,key_version,issued_at,revoked,revoked_at from schubert.auth_sessions")) {
      assertFalse(r.next());
    }
  }

  @Test
  void advisoryContentionAndEmptyCandidatesAreExplicit() throws Exception {
    backups();
    try (var lock = db.api();
        var s = lock.createStatement()) {
      s.execute("select pg_advisory_lock(71419602)");
      denied(ROLE, FIXTURE_55P03_0FE714C6, CALL);
      s.execute("select pg_advisory_unlock(71419602)");
      try (var c = inspection()) {
        assertEquals(List.of(), read(c, null));
        c.commit();
      }
    }
    try (var c = db.api()) {
      inbox(c, 1, FIXTURE_LGNREQ01_217C66A4, FIXTURE_ERROR_F717E7D8, CUTOFF.minusSeconds(1), false);
    }
    try (var c = inspection()) {
      assertEquals(List.of(new UUID(0, 1)), read(c, null));
      c.rollback();
    }
    // No deletion command is part of this capability.
    assertEquals(
        "1",
        scalar(
            FIXTURE_SCHUBERT_APP_5AB151CF,
            FIXTURE_SELECT_COUNT_FROM_SCHUBERT_REQUEST_INBOX_E4FAEDDB));
  }

  @Test
  void appendOnlyMigrationAndUnverifiedCiphertextRemainDistinct() throws Exception {
    assertEquals(
        MigrationInventory.COUNT_TEXT,
        scalar(
            FIXTURE_PGPT_ADMIN_F5D1227C,
            "select count(*) from schubert_meta.flyway_schema_history where success and version is not null"));
    var flyway =
        Flyway.configure()
            .dataSource(url, "schubert_migration", "")
            .defaultSchema("schubert_meta")
            .schemas("schubert_meta")
            .initSql("SET ROLE nk_owner")
            .locations(
                "filesystem:"
                    + Path.of(System.getProperty("nk.pt.repository"))
                        .resolve("src/schubert-nk-api/src/main/resources/db/migration"))
            .cleanDisabled(true)
            .load();
    assertTrue(flyway.validateWithResult().validationSuccessful);
    assertEquals(0, flyway.migrate().migrationsExecuted);
    backups();
    try (var c = db.api()) {
      inbox(c, 1, FIXTURE_LGNREQ01_217C66A4, FIXTURE_ERROR_F717E7D8, CUTOFF.minusSeconds(1), false);
    }
    try (var c = inspection();
        var s = c.createStatement();
        var r =
            s.executeQuery(
                "select response_body_encrypted from schubert.maintenance_next_auth_inbox('"
                    + RUN
                    + "','2026-09-09T00:00:00.123Z',null)")) {
      assertTrue(r.next());
      assertArrayEquals(new byte[30], r.getBytes(1));
      assertFalse(r.next());
      // Returning a locked row is not a cryptographic validation result.
      c.rollback();
    }
  }

  private static Connection connection(String role) throws SQLException {
    return DriverManager.getConnection(url, role, "");
  }

  private static Connection inspection() throws SQLException {
    var c = connection(ROLE);
    c.setAutoCommit(false);
    return c;
  }

  private static String scalar(String role, String sql) throws SQLException {
    try (var c = connection(role);
        var s = c.createStatement();
        var r = s.executeQuery(sql)) {
      assertTrue(r.next());
      var value = r.getString(1);
      assertFalse(r.next());
      return value;
    }
  }

  private static void denied(String role, String state, String sql) throws SQLException {
    try (var c = connection(role);
        var s = c.createStatement()) {
      assertEquals(state, assertThrows(SQLException.class, () -> s.execute(sql)).getSQLState());
    }
  }

  private static List<UUID> read(Connection c, UUID after) throws SQLException {
    try (var s =
        c.prepareStatement("select message_id from schubert.maintenance_next_auth_inbox(?,?,?)")) {
      s.setObject(1, RUN);
      s.setObject(2, CUTOFF.atOffset(java.time.ZoneOffset.UTC));
      s.setObject(3, after);
      try (var r = s.executeQuery()) {
        var ids = new ArrayList<UUID>();
        while (r.next()) ids.add(r.getObject(1, UUID.class));
        return ids;
      }
    }
  }

  private static void backups() throws SQLException {
    for (String step : List.of("BACKUP_DB", "BACKUP_CONFIG")) backup(step);
  }

  private static void backup(String step) throws SQLException {
    try (var c = db.api();
        var s =
            c.prepareStatement(
                "insert into schubert.batch_runs(run_id,business_date,step,attempt,started_at,ended_at,status) values (?,'2026-09-09',?,1,'2026-09-09T00:00:00Z','2026-09-09T00:00:01Z','SUCCESS')")) {
      s.setObject(1, RUN);
      s.setString(2, step);
      assertEquals(1, s.executeUpdate());
    }
  }

  private static void awaitBlocked(int pid) throws SQLException {
    long deadline = System.nanoTime() + TimeUnit.SECONDS.toNanos(4);
    try (var c = db.admin();
        var statement = c.prepareStatement("select cardinality(pg_blocking_pids(?)) > 0")) {
      statement.setInt(1, pid);
      do {
        try (var row = statement.executeQuery()) {
          assertTrue(row.next());
          if (row.getBoolean(1)) return;
        }
      } while (System.nanoTime() < deadline);
      fail("controlled SQL snapshot lock was not reached");
    }
  }

  private static void inbox(
      Connection c, long sequence, String layout, String state, Instant expiry, boolean session)
      throws SQLException {
    boolean processing = state.equals("PROCESSING");
    UUID id = new UUID(0, sequence);
    try (var s =
        c.prepareStatement(
            "insert into schubert.request_inbox(message_id,correlation_id,request_layout_id,request_version,owner_user_id,request_fingerprint_hmac,fingerprint_key_version,processing_state,result_ref_type,result_ref_uuid,response_layout_id,response_version,response_body_encrypted,response_key_version,created_at,completed_at,expires_at) values (?,?,?,'001',?,repeat('a',64),'v1',?,?,?,?,?,?,?,'2026-09-08T00:00:00Z',?,?)")) {
      s.setObject(1, id);
      s.setObject(2, id);
      s.setString(3, layout);
      s.setObject(4, layout.equals(FIXTURE_LGNREQ01_217C66A4) ? null : 7L);
      s.setString(5, state);
      s.setString(6, processing ? null : session ? "AUTH_SESSION" : "NONE");
      s.setObject(7, session ? SESSION : null);
      s.setString(8, processing ? null : layout.replace("REQ", "RSP"));
      s.setString(9, processing ? null : "001");
      s.setBytes(10, processing ? null : new byte[30]);
      s.setString(11, processing ? null : "v1");
      s.setObject(
          12, processing ? null : CUTOFF.minusSeconds(100).atOffset(java.time.ZoneOffset.UTC));
      s.setObject(13, expiry.atOffset(java.time.ZoneOffset.UTC));
      assertEquals(1, s.executeUpdate());
    }
  }
}
