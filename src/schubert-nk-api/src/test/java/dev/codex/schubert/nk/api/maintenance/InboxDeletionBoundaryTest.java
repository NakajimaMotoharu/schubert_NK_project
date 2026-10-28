package dev.codex.schubert.nk.api.maintenance;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assertions.fail;

import dev.codex.schubert.nk.api.database.MigrationInventory;
import dev.codex.schubert.nk.api.logging.ApiLogDatabaseFixture;
import java.nio.file.Path;
import java.security.MessageDigest;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;
import java.time.Instant;
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

/** PT-DB-INBOX-025..032; SS331 3.5; SQL capability is NOT an AES/reference validation oracle. */
final class InboxDeletionBoundaryTest {
  private static final String FIXTURE_42501_719DF123 = "42501";
  @TempDir static Path root;
  private static ApiLogDatabaseFixture db;
  private static String url;
  private static final UUID RUN = new UUID(0, 42);
  private static final UUID MESSAGE = new UUID(0, 101);
  private static final String ROLE = "schubert_inbox_inspector";
  private static final String SIGNATURE =
      "schubert.maintenance_delete_auth_inbox(uuid,timestamptz,uuid,text,bytea)";
  private static final Instant CUTOFF = Instant.parse("2026-09-17T00:00:00.123Z");
  // Public synthetic non-secret bytes: not valid encrypted response. SQL must not claim otherwise.
  private static final byte[] BODY = new byte[30];
  private static byte[] digest;

  @BeforeAll
  static void start() throws Exception {
    db = new ApiLogDatabaseFixture(root);
    try (var c = db.api()) {
      url = c.getMetaData().getURL();
    }
    digest = MessageDigest.getInstance("SHA-256").digest(BODY);
  }

  @AfterAll
  static void stop() throws Exception {
    if (db != null) db.stop();
  }

  @BeforeEach
  void seed() throws SQLException {
    sql("delete from schubert.request_inbox");
    sql("delete from schubert.auth_sessions");
    sql("delete from schubert.batch_runs");
    sql("delete from schubert.app_users");
    sql(
        "insert into schubert.app_users(id,username,username_key,password_hash,role,status,password_changed_at,created_at,updated_at) values(7,'Learner','learner','synthetic-unused','USER','ACTIVE','2026-09-09','2026-09-09','2026-09-09')");
    backup("BACKUP_DB");
    backup("BACKUP_CONFIG");
    sql(
        "insert into schubert.request_inbox(message_id,correlation_id,request_layout_id,request_version,request_fingerprint_hmac,fingerprint_key_version,processing_state,result_ref_type,response_layout_id,response_version,response_body_encrypted,response_key_version,created_at,completed_at,expires_at) values('"
            + MESSAGE
            + "','"
            + MESSAGE
            + "','LGNREQ01','001',repeat('a',64),'v1','ERROR','NONE','LGNRSP01','001',decode(repeat('00',30),'hex'),'v1','2026-09-09T00:00:00Z','2026-09-09T00:00:00.123Z','2026-09-16T00:00:00.123Z')");
  }

  @Test
  void exactDeleteRollbackAndReplay() throws Exception {
    for (String layout : List.of("LGN", "LOG")) {
      for (String state : List.of("COMPLETED", "ERROR")) {
        sql(
            "update schubert.request_inbox set request_layout_id='"
                + layout
                + "REQ01',response_layout_id='"
                + layout
                + "RSP01',owner_user_id="
                + (layout.equals("LGN") ? "null" : "7")
                + ",processing_state='"
                + state
                + "'");
        try (var c = connection()) {
          String xact = capture(c);
          assertTrue(remove(c, RUN, CUTOFF, MESSAGE, xact, digest));
          assertFalse(remove(c, RUN, CUTOFF, MESSAGE, xact, digest));
          assertEquals(
              "0",
              value(
                  c,
                  "select count(*) from schubert.maintenance_next_auth_inbox('"
                      + RUN
                      + "','2026-09-17T00:00:00.123Z',null)"));
          c.rollback();
        }
        assertEquals("1", count());
      }
    }
    try (var c = connection()) {
      assertTrue(remove(c, RUN, CUTOFF, MESSAGE, capture(c), digest));
      c.commit();
      assertFalse(remove(c, RUN, CUTOFF, MESSAGE, xact(c), digest));
      c.commit();
    }
    assertEquals("0", count());
    try (var c = db.api()) {
      assertEquals("1", value(c, "select count(*) from schubert.app_users"));
      assertEquals("2", value(c, "select count(*) from schubert.batch_runs"));
    }
  }

  @Test
  void argumentsAndTransactionIdentity() throws Exception {
    Object[][] invalid = {
      {null, CUTOFF, MESSAGE, "1", digest},
      {RUN, null, MESSAGE, "1", digest},
      {RUN, CUTOFF, null, "1", digest},
      {RUN, CUTOFF, MESSAGE, null, digest},
      {RUN, CUTOFF, MESSAGE, "", digest},
      {RUN, CUTOFF, MESSAGE, "-1", digest},
      {RUN, CUTOFF, MESSAGE, "1x", digest},
      {RUN, CUTOFF, MESSAGE, "1".repeat(21), digest},
      {RUN, CUTOFF, MESSAGE, "1", null},
      {RUN, CUTOFF, MESSAGE, "1", new byte[0]},
      {RUN, CUTOFF, MESSAGE, "1", new byte[31]},
      {RUN, CUTOFF, MESSAGE, "1", new byte[33]}
    };
    for (Object[] args : invalid) {
      try (var c = connection()) {
        assertEquals(
            "22023",
            assertThrows(
                    SQLException.class,
                    () ->
                        remove(
                            c,
                            (UUID) args[0],
                            (Instant) args[1],
                            (UUID) args[2],
                            (String) args[3],
                            (byte[]) args[4]))
                .getSQLState());
        c.rollback();
      }
    }
    for (String infinity : List.of("infinity", "-infinity")) {
      denied(
          ROLE,
          "22023",
          "select schubert.maintenance_delete_auth_inbox('"
              + RUN
              + "','"
              + infinity
              + "','"
              + MESSAGE
              + "','1',decode(repeat('00',32),'hex'))");
    }
    try (var c = connection();
        var other = connection()) {
      String old = capture(c);
      assertFalse(remove(other, RUN, CUTOFF, MESSAGE, old, digest));
      other.rollback();
      c.commit();
      assertFalse(remove(c, RUN, CUTOFF, MESSAGE, old, digest));
      assertFalse(remove(c, RUN, CUTOFF, MESSAGE, "0", digest));
      assertFalse(remove(c, RUN, CUTOFF, MESSAGE, "9".repeat(20), digest));
      c.rollback();
    }
    assertEquals("1", count());
  }

  @Test
  void retainedAndMalformedMetadata() throws Exception {
    List<String> rejected =
        List.of(
            "expires_at='2026-09-17T00:00:00.123Z'",
            "expires_at='2026-09-17T00:00:00.123001Z'",
            "expires_at='2026-09-16T00:00:00.122999Z'",
            "request_version='002'",
            "response_version='002'",
            "response_layout_id='LOGRSP01'",
            "request_layout_id='GAMREQ01',owner_user_id=7,response_layout_id='GAMRSP01'",
            "result_ref_type='USER',result_ref_id=7",
            "response_body_encrypted=null,response_key_version=null",
            "created_at='-infinity'",
            "expires_at='infinity'",
            "completed_at='infinity'",
            "processing_state='PROCESSING',completed_at=null,result_ref_type=null,response_layout_id=null,response_version=null,response_body_encrypted=null,response_key_version=null");
    for (String change : rejected) {
      seed();
      sql("update schubert.request_inbox set " + change);
      try (var c = connection()) {
        assertFalse(remove(c, RUN, CUTOFF, MESSAGE, xact(c), digest), change);
        c.commit();
      }
      assertEquals("1", count(), change);
    }
    for (String change :
        List.of(
            "owner_user_id=7",
            "operation_token='00000000-0000-0000-0000-000000000001'",
            "result_ref_type='AUTH_SESSION',result_ref_id=7,result_ref_uuid='00000000-0000-0000-0000-000000000104'",
            "completed_at='2026-09-08'")) {
      seed();
      try (var c = db.api();
          var s = c.createStatement()) {
        assertEquals(
            "23514",
            assertThrows(
                    SQLException.class,
                    () -> s.execute("update schubert.request_inbox set " + change))
                .getSQLState());
      }
      assertEquals("1", count());
    }
    for (String expiry :
        List.of(
            "2026-09-16T00:00:00.123Z",
            "2026-09-16T00:00:00.123001Z",
            "2026-09-17T00:00:00.122999Z")) {
      seed();
      sql("update schubert.request_inbox set expires_at='" + expiry + "'");
      try (var c = connection()) {
        assertTrue(remove(c, RUN, CUTOFF, MESSAGE, capture(c), digest));
        c.commit();
      }
      assertEquals("0", count());
    }
  }

  @Test
  void ciphertextAndMessageBinding() throws Exception {
    try (var c = connection()) {
      String tx = capture(c);
      assertFalse(remove(c, RUN, CUTOFF, new UUID(0, 999), tx, digest));
      assertFalse(remove(c, RUN, CUTOFF, MESSAGE, tx, new byte[32]));
      c.rollback();
    }
    try (var c = db.admin();
        var s = c.createStatement()) {
      c.setAutoCommit(false);
      String tx = capture(c);
      s.execute(
          "update schubert.request_inbox set response_body_encrypted=decode(repeat('01',30),'hex')");
      assertFalse(remove(c, RUN, CUTOFF, MESSAGE, tx, digest));
      c.rollback();
    }
    sql("update schubert.request_inbox set response_body_encrypted=decode(repeat('01',30),'hex')");
    try (var c = connection()) {
      assertFalse(remove(c, RUN, CUTOFF, MESSAGE, xact(c), digest));
      c.rollback();
    }
    assertEquals("1", count());
  }

  @Test
  void backupAndLockGate() throws Exception {
    for (String mutation :
        List.of(
            "delete from schubert.batch_runs",
            "delete from schubert.batch_runs where step='BACKUP_CONFIG'",
            "delete from schubert.batch_runs where step='BACKUP_DB'",
            "update schubert.batch_runs set status='FAILED'",
            "update schubert.batch_runs set ended_at=null",
            "update schubert.batch_runs set business_date='2026-09-16'",
            "update schubert.batch_runs set run_id='00000000-0000-0000-0000-000000000099'")) {
      seed();
      sql(mutation);
      try (var c = connection()) {
        String tx = xact(c);
        assertEquals(
            "55000",
            assertThrows(SQLException.class, () -> remove(c, RUN, CUTOFF, MESSAGE, tx, digest))
                .getSQLState());
        c.rollback();
      }
      assertEquals("1", count());
    }
    seed();
    try (var lock = db.api();
        var s = lock.createStatement();
        var c = connection()) {
      s.execute("select pg_advisory_lock(71419602)");
      String tx = xact(c);
      assertEquals(
          "55P03",
          assertThrows(SQLException.class, () -> remove(c, RUN, CUTOFF, MESSAGE, tx, digest))
              .getSQLState());
      c.rollback();
      s.execute("select pg_advisory_unlock(71419602)");
      assertTrue(remove(c, RUN, CUTOFF, MESSAGE, capture(c), digest));
      c.rollback();
    }
    assertEquals("1", count());
    // YKT-071: reject a success inserted after the locked backup query snapshot.
    sql("delete from schubert.batch_runs where step='BACKUP_CONFIG'");
    try (var writer = db.transaction();
        var inspected = connection();
        var pool = Executors.newSingleThreadExecutor()) {
      try (var statement = writer.createStatement()) {
        statement.execute("select id from schubert.batch_runs where step='BACKUP_DB' for update");
      }
      int pid = Integer.parseInt(value(inspected, "select pg_backend_pid()"));
      String tx = xact(inspected);
      var outcome =
          pool.submit(
              () -> {
                try {
                  remove(inspected, RUN, CUTOFF, MESSAGE, tx, digest);
                  return "ACCEPTED";
                } catch (SQLException failure) {
                  return failure.getSQLState();
                } finally {
                  inspected.rollback();
                }
              });
      awaitBlocked(pid);
      backup("BACKUP_CONFIG");
      writer.commit();
      assertEquals("55000", outcome.get(5, TimeUnit.SECONDS));
      assertTrue(remove(inspected, RUN, CUTOFF, MESSAGE, capture(inspected), digest));
      inspected.rollback();
    }
    assertEquals("1", count());
  }

  @Test
  void leastPrivilegeIsUnchanged() throws Exception {
    try (var c = db.admin()) {
      assertEquals(
          "nk_owner|true|search_path=pg_catalog, schubert,TimeZone=UTC",
          value(
              c,
              "select pg_get_userbyid(proowner)||'|'||prosecdef::text||'|'||array_to_string(proconfig,',') from pg_proc where oid='"
                  + SIGNATURE
                  + "'::regprocedure"));
      for (String role :
          List.of(
              "public",
              "schubert_app",
              "schubert_batch",
              "schubert_web_session",
              "schubert_backup",
              "schubert_ops_ro"))
        assertEquals(
            "false",
            value(
                c,
                "select has_function_privilege('"
                    + role
                    + "','"
                    + SIGNATURE
                    + "','execute')::text"));
      assertEquals(
          "true",
          value(
              c,
              "select has_function_privilege('" + ROLE + "','" + SIGNATURE + "','execute')::text"));
    }
    for (String role :
        List.of(
            "schubert_app",
            "schubert_batch",
            "schubert_web_session",
            "schubert_backup",
            "schubert_ops_ro"))
      denied(
          role,
          FIXTURE_42501_719DF123,
          "select schubert.maintenance_delete_auth_inbox(null,null,null,null,null)");
    denied(ROLE, FIXTURE_42501_719DF123, "delete from schubert.request_inbox");
    denied(ROLE, FIXTURE_42501_719DF123, "update schubert.auth_sessions set revoked=true");
    denied(ROLE, FIXTURE_42501_719DF123, "set role nk_owner");
    assertEquals("1", count());
  }

  @Test
  void concurrentRowsCannotChangeDuringValidation() throws Exception {
    try (var fixture = new AuthenticationInboxInspectorTest.Fixture();
        var api = db.api()) {
      fixture.seed(api, false);
    }
    sql(
        "update schubert.request_inbox set result_ref_type='AUTH_SESSION',result_ref_uuid='"
            + new UUID(0, 104)
            + "'");
    try (var c = db.api()) {
      assertEquals(
          "1",
          value(
              c,
              "select count(*) from schubert.request_inbox i join schubert.auth_sessions s on s.id=i.result_ref_uuid"));
    }
    try (var c = connection()) {
      String tx = capture(c);
      blocked("update schubert.request_inbox set fingerprint_key_version='v2'");
      blocked(
          "update schubert.auth_sessions set revoked=true,revoked_at='2026-09-17',revoke_reason='ADMIN'");
      blocked("update schubert.batch_runs set status='FAILED'");
      assertTrue(remove(c, RUN, CUTOFF, MESSAGE, tx, digest));
      blocked("update schubert.request_inbox set fingerprint_key_version='v2'");
      blocked(
          "update schubert.auth_sessions set revoked=true,revoked_at='2026-09-17',revoke_reason='ADMIN'");
      blocked("update schubert.batch_runs set status='FAILED'");
      c.rollback();
    }
    assertEquals("1", count());
    sql(
        "update schubert.auth_sessions set revoked=true,revoked_at='2026-09-17',revoke_reason='ADMIN'");
    try (var c = db.api()) {
      assertEquals("true", value(c, "select revoked::text from schubert.auth_sessions"));
    }
  }

  @Test
  void migrationInventoryAndSqlScope() throws Exception {
    try (var c = db.admin()) {
      assertEquals(
          MigrationInventory.COUNT_TEXT,
          value(
              c,
              "select count(*) from schubert_meta.flyway_schema_history where success and version is not null"));
    }
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
    // SQL is a trusted conditional-delete capability, NOT an independent decryption certificate.
    try (var c = connection()) {
      assertTrue(remove(c, RUN, CUTOFF, MESSAGE, capture(c), digest));
      c.rollback();
    }
    assertEquals("1", count());
  }

  private static Connection connection() throws SQLException {
    var c = DriverManager.getConnection(url, ROLE, "");
    c.setAutoCommit(false);
    return c;
  }

  private static String capture(Connection c) throws SQLException {
    try (var s =
        c.prepareStatement(
            "select pg_current_xact_id()::text,sha256(response_body_encrypted) from schubert.maintenance_next_auth_inbox(?,?,null)")) {
      s.setObject(1, RUN);
      s.setObject(2, CUTOFF.atOffset(java.time.ZoneOffset.UTC));
      try (var r = s.executeQuery()) {
        assertTrue(r.next());
        assertArrayEquals(digest, r.getBytes(2));
        String tx = r.getString(1);
        assertFalse(r.next());
        return tx;
      }
    }
  }

  private static String xact(Connection c) throws SQLException {
    return value(c, "select pg_current_xact_id()::text");
  }

  private static boolean remove(
      Connection c, UUID run, Instant cutoff, UUID message, String tx, byte[] hash)
      throws SQLException {
    try (var s = c.prepareStatement("select schubert.maintenance_delete_auth_inbox(?,?,?,?,?)")) {
      s.setObject(1, run);
      s.setObject(2, cutoff == null ? null : cutoff.atOffset(java.time.ZoneOffset.UTC));
      s.setObject(3, message);
      s.setString(4, tx);
      s.setBytes(5, hash);
      try (var r = s.executeQuery()) {
        assertTrue(r.next());
        boolean result = r.getBoolean(1);
        assertFalse(r.wasNull());
        assertFalse(r.next());
        return result;
      }
    }
  }

  private static void backup(String step) throws SQLException {
    try (var c = db.api();
        var s =
            c.prepareStatement(
                "insert into schubert.batch_runs(run_id,business_date,step,attempt,started_at,ended_at,status) values (?,'2026-09-17',?,1,'2026-09-17T00:00:00Z','2026-09-17T00:00:01Z','SUCCESS')")) {
      s.setObject(1, RUN);
      s.setString(2, step);
      assertEquals(1, s.executeUpdate());
    }
  }

  private static String value(Connection c, String query) throws SQLException {
    try (var s = c.createStatement();
        var r = s.executeQuery(query)) {
      assertTrue(r.next());
      String value = r.getString(1);
      assertFalse(r.next());
      return value;
    }
  }

  private static void sql(String command) throws SQLException {
    try (var c = db.api();
        var s = c.createStatement()) {
      s.execute(command);
    }
  }

  private static String count() throws SQLException {
    try (var c = db.api()) {
      return value(c, "select count(*) from schubert.request_inbox");
    }
  }

  private static void denied(String role, String state, String command) throws SQLException {
    try (var c = DriverManager.getConnection(url, role, "");
        var s = c.createStatement()) {
      assertEquals(state, assertThrows(SQLException.class, () -> s.execute(command)).getSQLState());
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

  private static void blocked(String command) throws SQLException {
    try (var c = db.transaction();
        var s = c.createStatement()) {
      s.execute("set local lock_timeout='50ms'");
      assertEquals(
          "55P03", assertThrows(SQLException.class, () -> s.execute(command)).getSQLState());
      c.rollback();
    }
  }
}
