package dev.codex.schubert.nk.api.maintenance;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.api.idempotency.InboxCompletionState;
import dev.codex.schubert.nk.api.idempotency.InboxResultReference;
import dev.codex.schubert.nk.api.idempotency.ResponseSnapshotIdentity;
import dev.codex.schubert.nk.api.logging.ApiLogDatabaseFixture;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.security.SecureRandom;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashSet;
import java.util.HexFormat;
import java.util.List;
import java.util.Properties;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.Callable;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.function.Executable;
import org.junit.jupiter.api.io.TempDir;

/** PT-DB-INBOX-202..208: real isolated PG SCRAM plus public JDBC fault/ownership probes. */
final class InspectorDatabaseConnectionsTest {
  @TempDir static Path root;
  private static ApiLogDatabaseFixture db;
  private static String url;
  private static byte[] password;
  private static final String ROLE = "schubert_inbox_inspector";

  @BeforeAll
  static void start() throws Exception {
    db = new ApiLogDatabaseFixture(root);
    byte[] random = new byte[32];
    new SecureRandom().nextBytes(random);
    password = HexFormat.of().formatHex(random).getBytes(StandardCharsets.US_ASCII);
    Arrays.fill(random, (byte) 0);
    try (var c = db.admin();
        var s = c.createStatement()) {
      url = c.getMetaData().getURL();
      s.execute("set password_encryption='scram-sha-256'");
      // Test-only generated lowercase hex, never a deployed password or arbitrary SQL text.
      s.execute(
          "alter role schubert_inbox_inspector password '"
              + new String(password, StandardCharsets.US_ASCII)
              + "'");
      Files.writeString(
          root.resolve("data/pg_hba.conf"),
          "host all schubert_inbox_inspector 127.0.0.1/32 scram-sha-256\n"
              + "host all all 127.0.0.1/32 trust\nlocal all all trust\n",
          StandardCharsets.US_ASCII);
      try (var r = s.executeQuery("select pg_reload_conf()")) {
        assertTrue(r.next());
        assertTrue(r.getBoolean(1));
      }
    }
    // Observe rejection, not a sleep-based assumption that postmaster has processed SIGHUP.
    boolean authenticated = false;
    long deadline = System.nanoTime() + TimeUnit.SECONDS.toNanos(5);
    while (System.nanoTime() < deadline) {
      try (var early = DriverManager.getConnection(url, ROLE, "nonempty-public-invalid-canary")) {
        assertFalse(early.isClosed());
      } catch (SQLException rejected) {
        assertEquals("28P01", rejected.getSQLState());
        authenticated = true;
        break;
      }
    }
    assertTrue(authenticated, "isolated SCRAM rule must be active before any PT");
  }

  @AfterAll
  static void stop() throws Exception {
    try {
      if (db != null) db.stop();
    } finally {
      if (password != null) Arrays.fill(password, (byte) 0);
    }
  }

  private static InspectorDbCredential material() {
    return InspectorDbCredential.consume(password.clone());
  }

  private static Connection actual() throws SQLException {
    return DriverManager.getConnection(url, ROLE, new String(password, StandardCharsets.US_ASCII));
  }

  @Test
  void fixedConnectionProperties() throws Exception {
    var observed = new ArrayList<Properties>();
    try (var m = material();
        var provider =
            new InspectorDatabaseConnections(
                url,
                m,
                (target, p) -> {
                  assertEquals(url, target);
                  assertEquals(
                      Set.of("user", "password", "connectTimeout", "ApplicationName"),
                      p.stringPropertyNames());
                  assertEquals(ROLE, p.getProperty("user"));
                  assertEquals("3", p.getProperty("connectTimeout"));
                  assertEquals("schubert-nk-inbox-inspector", p.getProperty("ApplicationName"));
                  assertArrayEquals(
                      password, p.getProperty("password").getBytes(StandardCharsets.US_ASCII));
                  observed.add(p);
                  return DriverManager.getConnection(target, p);
                })) {
      char[] unrelated = m.copyPassword();
      Arrays.fill(unrelated, 'Z');
      try (var c = provider.open()) {
        assertFalse(c.isClosed());
        assertTrue(c.getAutoCommit());
      }
      assertEquals("InspectorDatabaseConnections[REDACTED]", provider.toString());
    }
    assertEquals(1, observed.size());
    assertTrue(observed.getFirst().isEmpty());
    try (var m = material();
        var provider =
            new InspectorDatabaseConnections(
                url,
                m,
                (target, p) -> {
                  observed.add(p);
                  throw new SQLException("private-marker");
                })) {
      failure(provider::open);
      assertTrue(observed.getLast().isEmpty());
    }
  }

  @Test
  void urlAndNullContracts() throws Exception {
    try (var m = material()) {
      assertThrows(NullPointerException.class, () -> new InspectorDatabaseConnections(null, m));
      assertThrows(NullPointerException.class, () -> new InspectorDatabaseConnections(url, null));
      assertThrows(
          NullPointerException.class, () -> new InspectorDatabaseConnections(url, m, null));
      for (String bad :
          List.of(
              "",
              "jdbc:postgresql:postgres",
              "jdbc:postgresql://localhost:5432/postgres",
              "jdbc:postgresql://127.0.0.1:0/postgres",
              "jdbc:postgresql://127.0.0.1:65536/postgres",
              "jdbc:postgresql://127.0.0.1:05432/postgres",
              "jdbc:postgresql://127.0.0.1:5432/Postgres",
              "jdbc:postgresql://127.0.0.1:5432/",
              url + "?user=pgpt_admin",
              url + "#fragment",
              "jdbc:postgresql://name@127.0.0.1:5432/postgres",
              "jdbc:postgresql://127.0.0.1:5432/a-b",
              "jdbc:postgresql://127.0.0.1:5432/" + "a".repeat(64))) {
        var called = new AtomicInteger();
        var error =
            assertThrows(
                IllegalArgumentException.class,
                () ->
                    new InspectorDatabaseConnections(
                        bad,
                        m,
                        (u, p) -> {
                          called.incrementAndGet();
                          return actual();
                        }));
        assertEquals(0, called.get());
        assertNull(error.getCause());
      }
      for (String valid :
          List.of(
              "jdbc:postgresql://127.0.0.1:1/a",
              "jdbc:postgresql://127.0.0.1:65535/_" + "a".repeat(62)))
        try (var ignored = new InspectorDatabaseConnections(valid, m)) {
          assertEquals("InspectorDatabaseConnections[REDACTED]", ignored.toString());
        }
    }
    var closed = material();
    try {
      closed.close();
      assertThrows(
          IllegalStateException.class, () -> new InspectorDatabaseConnections(url, closed));
    } finally {
      closed.close();
    }
  }

  @Test
  void connectionAdmission() throws Exception {
    try (var m = material()) {
      try (var provider = new InspectorDatabaseConnections(url, m, (u, p) -> null)) {
        failure(provider::open);
      }
      for (String mode : List.of("transaction", "readonly", "app", "admin")) {
        var returned = new ArrayList<Connection>();
        try (var provider =
            new InspectorDatabaseConnections(
                url,
                m,
                (u, p) -> {
                  Connection c =
                      mode.equals("app") ? db.api() : mode.equals("admin") ? db.admin() : actual();
                  returned.add(c);
                  if (mode.equals("transaction")) c.setAutoCommit(false);
                  if (mode.equals("readonly")) c.setReadOnly(true);
                  return c;
                })) {
          failure(provider::open);
          assertTrue(returned.getFirst().isClosed());
        }
      }
      for (String column : List.of("effective_role", "login_role", "database_name", "recovery")) {
        for (Object wrong :
            Arrays.asList(null, column.equals("recovery") ? Boolean.TRUE : "wrong")) {
          var p = new MaintenanceJdbcProbe();
          p.selectedSql = "current_user";
          p.columns.put(column, wrong);
          try (var provider =
              new InspectorDatabaseConnections(url, m, (u, props) -> p.wrap(actual()))) {
            failure(provider::open);
            assertEquals(1, p.closes);
          }
        }
      }
      for (boolean empty : List.of(true, false)) {
        var p = new MaintenanceJdbcProbe();
        p.selectedSql = "current_user";
        p.empty = empty;
        p.duplicate = !empty;
        try (var provider =
            new InspectorDatabaseConnections(url, m, (u, props) -> p.wrap(actual()))) {
          failure(provider::open);
          assertEquals(1, p.closes);
        }
      }
    }
  }

  @Test
  void sqlFailuresRemainRedacted() throws Exception {
    try (var m = material()) {
      for (String fault :
          List.of(
              "getAutoCommit",
              "isReadOnly",
              "prepareStatement",
              "executeQuery",
              "next",
              "getString",
              "getObject",
              "resultClose",
              "statementClose",
              "close")) {
        var p = new MaintenanceJdbcProbe();
        p.selectedSql = "current_user";
        p.fault = fault;
        if (fault.equals("close")) p.empty = true;
        var props = new ArrayList<Properties>();
        try (var provider =
            new InspectorDatabaseConnections(
                url,
                m,
                (u, value) -> {
                  props.add(value);
                  return p.wrap(actual());
                })) {
          failure(provider::open);
          assertEquals(1, p.closes);
          assertTrue(props.getFirst().isEmpty());
        }
      }
    }
  }

  @Test
  void closeAndConcurrentOpen() throws Exception {
    try (var m = material();
        var pool = Executors.newFixedThreadPool(12)) {
      var p = new InspectorDatabaseConnections(url, m);
      try {
        var calls = new ArrayList<Callable<Integer>>();
        for (int i = 0; i < 100; i++)
          calls.add(
              () -> {
                try (var c = p.open();
                    var s = c.createStatement();
                    var r = s.executeQuery("select pg_backend_pid()")) {
                  assertTrue(r.next());
                  return r.getInt(1);
                }
              });
        var ids = new HashSet<Integer>();
        for (var done : pool.invokeAll(calls)) assertTrue(ids.add(done.get(10, TimeUnit.SECONDS)));
        try (var returned = p.open()) {
          p.close();
          p.close();
          assertFalse(returned.isClosed());
          failure(p::open);
        }
      } finally {
        p.close();
      }
      var entered = new CountDownLatch(1);
      var release = new CountDownLatch(1);
      var closing = new CountDownLatch(1);
      var racing =
          new InspectorDatabaseConnections(
              url,
              m,
              (u, props) -> {
                entered.countDown();
                try {
                  assertTrue(release.await(5, TimeUnit.SECONDS));
                } catch (InterruptedException e) {
                  Thread.currentThread().interrupt();
                  throw new SQLException("interrupted");
                }
                return actual();
              });
      try {
        var open = pool.submit(racing::open);
        assertTrue(entered.await(5, TimeUnit.SECONDS));
        var close =
            pool.submit(
                () -> {
                  closing.countDown();
                  racing.close();
                });
        assertTrue(closing.await(5, TimeUnit.SECONDS));
        assertFalse(close.isDone());
        release.countDown();
        try (var c = open.get(5, TimeUnit.SECONDS)) {
          close.get(5, TimeUnit.SECONDS);
          assertFalse(c.isClosed());
          failure(racing::open);
        }
      } finally {
        release.countDown();
        racing.close();
      }
    }
  }

  @Test
  void realScramRoleAndPassword() throws Exception {
    try (var m = material();
        var provider = new InspectorDatabaseConnections(url, m);
        var c = provider.open();
        var s = c.createStatement()) {
      try (var r =
          s.executeQuery(
              "select current_user,session_user,current_database(),current_setting('statement_timeout'),current_setting('lock_timeout'),current_setting('application_name')")) {
        assertTrue(r.next());
        assertEquals(ROLE, r.getString(1));
        assertEquals(ROLE, r.getString(2));
        assertEquals("postgres", r.getString(3));
        assertEquals("30s", r.getString(4));
        assertEquals("5s", r.getString(5));
        assertEquals("schubert-nk-inbox-inspector", r.getString(6));
        assertFalse(r.next());
      }
      for (String denied :
          List.of(
              "select password_hash from schubert.app_users",
              "delete from schubert.request_inbox",
              "set role nk_owner")) {
        assertEquals(
            "42501", assertThrows(SQLException.class, () -> s.execute(denied)).getSQLState());
      }
    }
    byte[] wrong = password.clone();
    wrong[0] = wrong[0] == '0' ? (byte) '1' : (byte) '0';
    try (var m = InspectorDbCredential.consume(wrong);
        var provider = new InspectorDatabaseConnections(url, m)) {
      failure(provider::open);
    }
    try (var c = db.admin();
        var s = c.createStatement();
        var r =
            s.executeQuery(
                "select auth_method from pg_hba_file_rules where 'schubert_inbox_inspector'=any(user_name)")) {
      assertTrue(r.next());
      assertEquals("scram-sha-256", r.getString(1));
      assertFalse(r.next());
    }
  }

  @Test
  void ownedInspectionConnection() throws Exception {
    var run = new InspectionRun(new UUID(0, 42), Instant.parse("2026-09-17T00:00:00.123Z"));
    try (var f = new AuthenticationInboxInspectorTest.Fixture();
        var m = material();
        var provider = new InspectorDatabaseConnections(url, m)) {
      try (var c = db.admin();
          var s = c.createStatement()) {
        s.execute("delete from schubert.inbox_inspection_progress");
        s.execute("delete from schubert.request_inbox");
        s.execute("delete from schubert.batch_runs");
      }
      try (var c = db.admin();
          var s =
              c.prepareStatement(
                  "insert into schubert.batch_runs(run_id,business_date,step,attempt,started_at,ended_at,status) values(?,'2026-09-17',?,1,'2026-09-17T00:00:00Z','2026-09-17T00:00:00.001Z','SUCCESS')")) {
        for (String step : List.of("BACKUP_DB", "BACKUP_CONFIG")) {
          s.setObject(1, run.id());
          s.setString(2, step);
          assertEquals(1, s.executeUpdate());
        }
      }
      try (var c = db.admin();
          var s =
              c.prepareStatement(
                  "insert into schubert.request_inbox(message_id,correlation_id,request_layout_id,request_version,request_fingerprint_hmac,fingerprint_key_version,processing_state,result_ref_type,response_layout_id,response_version,response_body_encrypted,response_key_version,created_at,completed_at,expires_at) values(?,?,'LGNREQ01','001',repeat('a',64),'fp1','ERROR','NONE','LGNRSP01','001',?,'s1','2026-09-09T00:00:00Z','2026-09-09T00:00:00.123Z','2026-09-16T00:00:00.123Z')")) {
        for (int i = 0; i < 2; i++) {
          UUID message = new UUID(0, 100 + i);
          s.setObject(1, message);
          s.setObject(2, message);
          byte[] cipher = new byte[30];
          if (i == 0) {
            var identity = ResponseSnapshotIdentity.anonymous(message, "LGNRSP01", "001");
            byte[] wire = f.wire(identity, "0101");
            // BUG-133/YKT-104: old fixture has a fixed request; this case owns a different one.
            System.arraycopy(
                message.toString().getBytes(StandardCharsets.US_ASCII), 0, wire, 60, 36);
            assertEquals(message.toString(), new String(wire, 60, 36, StandardCharsets.US_ASCII));
            var saved =
                f.savedBytes(
                    identity, wire, InboxCompletionState.ERROR, InboxResultReference.none());
            assertTrue(
                new InboxResponseInspector(f.snapshots).isStructurallyValid(identity, saved));
            cipher = saved.responseSnapshot().orElseThrow().ciphertext();
          }
          try {
            s.setBytes(3, cipher);
            assertEquals(1, s.executeUpdate());
          } finally {
            Arrays.fill(cipher, (byte) 0);
          }
        }
      }
      var bad = new MaintenanceJdbcProbe();
      bad.fault = "commit";
      try (var broken =
          new InspectorDatabaseConnections(url, m, (u, props) -> bad.wrap(actual()))) {
        var service =
            new InboxCleanup(
                broken,
                f.inspector,
                new NonAuthenticationInboxInspector(f.snapshots),
                Set.of("fp1"));
        assertThrows(InboxMaintenanceException.class, () -> service.inspectStoredNext(run));
        assertEquals(1, bad.rollbacks);
      }
      assertEquals("2/0", counts());
      var service =
          new InboxCleanup(
              provider,
              f.inspector,
              new NonAuthenticationInboxInspector(f.snapshots),
              Set.of("fp1"));
      var progress = service.runChunk(run, 3);
      assertTrue(progress.complete());
      assertEquals(2, progress.inspected());
      assertEquals(1, progress.deleted());
      assertEquals(1, progress.protectedRows());
      assertEquals("1/1", counts());
      assertEquals(progress, service.runChunk(run, 3));
    }
  }

  private static String counts() throws SQLException {
    try (var c = db.admin();
        var s = c.createStatement();
        var r =
            s.executeQuery(
                "select (select count(*) from schubert.request_inbox)||'/'||(select count(*) from schubert.inbox_inspection_progress)")) {
      assertTrue(r.next());
      return r.getString(1);
    }
  }

  private static void failure(Executable operation) {
    var error = assertThrows(SQLException.class, operation);
    assertEquals("inspector database connection unavailable", error.getMessage());
    assertEquals("08001", error.getSQLState());
    assertNull(error.getCause());
    assertEquals(0, error.getSuppressed().length);
  }
}
