package dev.codex.schubert.nk.api.application.admin;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.api.logging.ApiLogDatabaseFixture;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Proxy;
import java.nio.file.Path;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HexFormat;
import java.util.List;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.Callable;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import javax.crypto.SecretKeyFactory;
import javax.crypto.spec.PBEKeySpec;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** Real PG18 grants/DDL; independent SQL/JCA/parallel writers. SSC188, PT-ADM-BOOT001..006. */
class BootstrapAdminServiceTest {
  @TempDir static Path root;
  static ApiLogDatabaseFixture db;
  static final Instant NOW = Instant.parse("2026-10-05T00:00:00Z");
  static final UserCommandMetadata META =
      new UserCommandMetadata(new UUID(9, 1), new UUID(9, 2), NOW);
  final BootstrapAdminService service = new BootstrapAdminService();

  @BeforeAll
  static void start() throws Exception {
    db = new ApiLogDatabaseFixture(root);
  }

  @AfterAll
  static void stop() throws Exception {
    if (db != null) db.stop();
  }

  @BeforeEach
  void reset() throws Exception {
    try (var c = db.admin();
        var s = c.createStatement()) {
      s.execute("truncate schubert.app_users,schubert.app_logs restart identity cascade");
    }
  }

  @Test
  void boot001CreateAndAuditWithIndependentPbkdf2AndSql() throws Exception {
    for (String password : List.of("p".repeat(12), "é".repeat(128), "e\u0301".repeat(12))) {
      reset();
      char[] input = password.toCharArray();
      try (var c = db.transaction()) {
        assertEquals(
            BootstrapAdminService.Outcome.CREATED,
            service.create(c, " Initial.Admin ", input, META));
        assertArrayEquals(new char[input.length], input);
        assertFalse(c.getAutoCommit());
        assertFalse(c.isClosed());
        c.commit();
      }
      try (var c = db.api();
          var s = c.createStatement();
          var r = s.executeQuery("select * from schubert.app_users")) {
        assertTrue(r.next());
        assertEquals(1, r.getLong("id"));
        assertEquals("Initial.Admin", r.getString("username"));
        assertEquals("initial.admin", r.getString("username_key"));
        assertEquals("ADMIN", r.getString("role"));
        assertEquals("ACTIVE", r.getString("status"));
        assertEquals(0, r.getInt("failed_count"));
        assertEquals(0, r.getLong("version"));
        assertNull(r.getObject("created_by"));
        assertNull(r.getObject("updated_by"));
        for (String column : List.of("created_at", "updated_at", "password_changed_at"))
          assertEquals(NOW, r.getObject(column, java.time.OffsetDateTime.class).toInstant());
        independentHash(
            r.getString("password_hash"),
            java.text.Normalizer.normalize(password, java.text.Normalizer.Form.NFC));
        assertFalse(r.next());
      }
      try (var c = db.api();
          var s = c.createStatement();
          var r =
              s.executeQuery(
                  "select category,level,action,message,actor_user_id,actor_username,details,logged_at,message_id,correlation_id from schubert.app_logs order by category")) {
        for (String category : List.of("ACTION", "SECURITY")) {
          assertTrue(r.next());
          assertEquals(category, r.getString(1));
          assertEquals("INFO", r.getString(2));
          assertEquals("USER_CREATED", r.getString(3));
          assertEquals("USER_CREATED", r.getString(4));
          assertNull(r.getObject(5));
          assertNull(r.getObject(6));
          var details = com.google.gson.JsonParser.parseString(r.getString(7)).getAsJsonObject();
          assertEquals(Set.of("outcome", "source", "targetUserId"), details.keySet());
          assertEquals("SUCCESS", details.get("outcome").getAsString());
          assertEquals("BOOTSTRAP", details.get("source").getAsString());
          assertEquals(1, details.get("targetUserId").getAsLong());
          assertEquals(NOW, r.getObject(8, java.time.OffsetDateTime.class).toInstant());
          assertEquals(META.messageId(), r.getObject(9));
          assertEquals(META.correlationId(), r.getObject(10));
        }
        assertFalse(r.next());
      }
    }
  }

  @Test
  void boot002ExistingAnyUserAndRepeatAreUnchangedEvenInvalidCreationPassword() throws Exception {
    for (String role : List.of("USER", "ADMIN"))
      for (String status : List.of("ACTIVE", "DISABLED")) {
        reset();
        seed(role, status);
        String before = snapshot();
        for (String password : List.of("x", "valid-but-not-used")) {
          char[] input = password.toCharArray();
          try (var c = db.transaction()) {
            assertEquals(
                BootstrapAdminService.Outcome.ALREADY_EXISTS,
                service.create(c, "ignored", input, META));
            c.commit();
          }
          assertArrayEquals(new char[input.length], input);
          assertEquals(before, snapshot());
          assertEquals(0, count("app_logs"));
        }
      }
  }

  @Test
  void boot003CreationValidationAndNullBoundariesConsumePassword() throws Exception {
    for (String name : List.of("", "a".repeat(65), "admin!", "日本", "a\n")) {
      // trim removes a trailing LF by the same approved username contract; use interior control.
      if (name.equals("a\n")) name = "a\nb";
      char[] input = "valid-password".toCharArray();
      try (var c = db.transaction()) {
        String invalid = name;
        assertThrows(IllegalArgumentException.class, () -> service.create(c, invalid, input, META));
        c.rollback();
      }
      assertArrayEquals(new char[input.length], input);
    }
    for (String invalid :
        List.of(
            "x".repeat(11),
            "x".repeat(129),
            "é".repeat(129),
            "abcdefghijkl",
            "a".repeat(12) + " ",
            "a".repeat(12) + "\n")) {
      char[] input = invalid.toCharArray();
      try (var c = db.transaction()) {
        assertThrows(
            IllegalArgumentException.class, () -> service.create(c, "abcdefghijkl", input, META));
        c.rollback();
      }
      assertArrayEquals(new char[input.length], input);
    }
    for (int i = 0; i < 3; i++) {
      char[] input = "valid-password".toCharArray();
      try (var c = db.transaction()) {
        int index = i;
        assertThrows(
            NullPointerException.class,
            () ->
                service.create(
                    index == 0 ? null : c,
                    index == 1 ? null : "admin",
                    input,
                    index == 2 ? null : META));
      }
      assertArrayEquals(new char[input.length], input);
    }
    try (var c = db.transaction()) {
      assertThrows(NullPointerException.class, () -> service.create(c, "admin", null, META));
    }
    assertEquals(0, count("app_users"));
    assertEquals(0, count("app_logs"));
  }

  @Test
  void boot004OneWinnerAmong100ConcurrentBootstrapTransactions() throws Exception {
    try (var executor = Executors.newFixedThreadPool(12)) {
      var tasks = new ArrayList<Callable<BootstrapAdminService.Outcome>>();
      for (int i = 0; i < 100; i++) {
        int index = i;
        tasks.add(
            () -> {
              char[] input = "synthetic-credential".toCharArray();
              try (var c = db.transaction()) {
                var outcome = service.create(c, "owner" + index, input, META);
                c.commit();
                assertArrayEquals(new char[input.length], input);
                return outcome;
              }
            });
      }
      int winners = 0;
      for (var result : executor.invokeAll(tasks))
        if (result.get(30, TimeUnit.SECONDS) == BootstrapAdminService.Outcome.CREATED) winners++;
      assertEquals(1, winners);
    }
    assertEquals(1, count("app_users"));
    assertEquals(2, count("app_logs"));
  }

  @Test
  void boot004NonCooperatingInsertIsSeenAfterTableLockWait() throws Exception {
    try (var c = db.admin();
        var executor = Executors.newSingleThreadExecutor()) {
      c.setAutoCommit(false);
      try (var s = c.createStatement()) {
        s.execute("lock table schubert.app_users in row exclusive mode");
      }
      CountDownLatch issued = new CountDownLatch(1);
      var future =
          executor.submit(
              () -> {
                try (var app = db.transaction()) {
                  issued.countDown();
                  var result =
                      service.create(app, "second", "synthetic-credential".toCharArray(), META);
                  app.commit();
                  return result;
                }
              });
      assertTrue(issued.await(10, TimeUnit.SECONDS));
      try (var s = c.createStatement()) {
        s.executeUpdate(seedSql("USER", "DISABLED"));
      }
      c.commit();
      assertEquals(BootstrapAdminService.Outcome.ALREADY_EXISTS, future.get(15, TimeUnit.SECONDS));
    }
    assertEquals(1, count("app_users"));
    assertEquals(0, count("app_logs"));
  }

  @Test
  void boot005TransactionContractAndRollbackAreNotNormalCompletion() throws Exception {
    for (int mode = 0; mode < 3; mode++) {
      char[] input = "synthetic-credential".toCharArray();
      try (var c = db.api()) {
        if (mode != 0) c.setAutoCommit(false);
        if (mode == 1) c.setReadOnly(true);
        if (mode == 2) c.setTransactionIsolation(Connection.TRANSACTION_SERIALIZABLE);
        assertThrows(SQLException.class, () -> service.create(c, "admin", input, META));
      }
      assertArrayEquals(new char[input.length], input);
    }
    try (var c = db.transaction()) {
      assertEquals(
          BootstrapAdminService.Outcome.CREATED,
          service.create(c, "admin", "synthetic-credential".toCharArray(), META));
      c.rollback();
    }
    assertEquals(0, count("app_users"));
    assertEquals(0, count("app_logs"));
  }

  @Test
  void boot005ExclusiveMaintenanceDeniesBeforeAnyAccountMutationAndSharedLockEndsAtCommit()
      throws Exception {
    try (var maintenance = db.admin();
        var s = maintenance.createStatement()) {
      s.execute("select pg_advisory_lock(71419602)");
      char[] input = "synthetic-credential".toCharArray();
      try (var c = db.transaction()) {
        assertThrows(SQLException.class, () -> service.create(c, "admin", input, META));
        c.rollback();
      }
      assertArrayEquals(new char[input.length], input);
      assertEquals(0, count("app_users"));
      assertEquals(0, count("app_logs"));
      s.execute("select pg_advisory_unlock(71419602)");
      try (var c = db.transaction()) {
        assertEquals(
            BootstrapAdminService.Outcome.CREATED,
            service.create(c, "admin", "synthetic-credential".toCharArray(), META));
        try (var r = s.executeQuery("select pg_try_advisory_lock(71419602)")) {
          assertTrue(r.next());
          assertFalse(r.getBoolean(1));
        }
        c.commit();
        try (var r = s.executeQuery("select pg_try_advisory_lock(71419602)")) {
          assertTrue(r.next());
          assertTrue(r.getBoolean(1));
        }
        s.execute("select pg_advisory_unlock(71419602)");
      }
    }
  }

  @Test
  void boot006MalformedRowsAndAuditCountFailClosed() throws Exception {
    for (String sql :
        List.of(
            "select pg_catalog.pg_try_advisory_xact_lock_shared",
            "select pg_advisory",
            "select exists",
            "insert into schubert.app_users",
            "insert into schubert.app_logs")) {
      List<String> modes =
          sql.contains("app_logs")
              ? List.of("count0", "count2")
              : List.of("empty", "duplicate", "null");
      if (sql.contains("app_users"))
        modes = List.of("empty", "duplicate", "null", "zero", "negative", "large");
      if (sql.contains("pg_advisory")) modes = List.of("empty", "duplicate");
      if (sql.contains("pg_try_advisory")) modes = List.of("empty", "duplicate", "null", "false");
      for (String mode : modes) {
        char[] input = "synthetic-credential".toCharArray();
        try (var c = db.transaction()) {
          var wrapped = fault(c, sql, mode);
          assertThrows(
              SQLException.class,
              () -> service.create(wrapped, "admin", input, META),
              sql + "/" + mode);
          c.rollback();
        }
        assertArrayEquals(new char[input.length], input);
        assertEquals(0, count("app_users"));
        assertEquals(0, count("app_logs"));
      }
    }
  }

  @Test
  void boot005SecurityAuditFaultRollsBackWholeCreation() throws Exception {
    try (var c = db.admin();
        var s = c.createStatement()) {
      s.execute(
          "create function schubert.pt_boot_audit_fault() returns trigger language plpgsql as $$ begin if NEW.category='SECURITY' then raise exception 'synthetic audit failure'; end if; return NEW; end $$");
      s.execute(
          "create trigger pt_boot_audit_fault before insert on schubert.app_logs for each row execute function schubert.pt_boot_audit_fault()");
    }
    char[] input = "synthetic-credential".toCharArray();
    try {
      try (var c = db.transaction()) {
        assertThrows(SQLException.class, () -> service.create(c, "admin", input, META));
        c.rollback();
      }
      assertArrayEquals(new char[input.length], input);
      assertEquals(0, count("app_users"));
      assertEquals(0, count("app_logs"));
    } finally {
      try (var c = db.admin();
          var s = c.createStatement()) {
        s.execute("drop trigger pt_boot_audit_fault on schubert.app_logs");
        s.execute("drop function schubert.pt_boot_audit_fault()");
      }
    }
  }

  @Test
  void boot006ExistingResultAndStatementCloseFaultCannotReturnNormalSkip() throws Exception {
    seed("USER", "DISABLED");
    String before = snapshot();
    for (String mode : List.of("resultClose", "statementClose", "doubleClose")) {
      char[] input = "synthetic-credential".toCharArray();
      try (var c = db.transaction()) {
        SQLException failure =
            assertThrows(
                SQLException.class,
                () -> service.create(fault(c, "select exists", mode), "ignored", input, META));
        assertEquals(mode.equals("doubleClose") ? 1 : 0, failure.getSuppressed().length);
        c.rollback();
      }
      assertEquals(before, snapshot());
      assertArrayEquals(new char[input.length], input);
      assertEquals(0, count("app_logs"));
    }
  }

  private static Connection fault(Connection c, String selectedSql, String mode) {
    return (Connection)
        Proxy.newProxyInstance(
            Connection.class.getClassLoader(),
            new Class<?>[] {Connection.class},
            (p, m, a) -> {
              Object value = invoke(c, m, a);
              if (!m.getName().equals("prepareStatement")
                  || !((String) a[0]).startsWith(selectedSql)) return value;
              var s = (PreparedStatement) value;
              return Proxy.newProxyInstance(
                  PreparedStatement.class.getClassLoader(),
                  new Class<?>[] {PreparedStatement.class},
                  (sp, sm, sa) -> {
                    if (sm.getName().equals("executeUpdate") && mode.startsWith("count"))
                      return mode.equals("count0") ? 0 : 2;
                    Object actual = invoke(s, sm, sa);
                    if (sm.getName().equals("close")
                        && (mode.equals("statementClose") || mode.equals("doubleClose")))
                      throw new SQLException("synthetic statement close");
                    if (!sm.getName().equals("executeQuery")) return actual;
                    var r = (ResultSet) actual;
                    int[] n = {0};
                    return Proxy.newProxyInstance(
                        ResultSet.class.getClassLoader(),
                        new Class<?>[] {ResultSet.class},
                        (rp, rm, ra) -> {
                          if (rm.getName().equals("next")) {
                            if (mode.equals("empty")) return false;
                            if (mode.equals("duplicate") && ++n[0] == 2) return true;
                          }
                          if (rm.getName().equals("wasNull") && mode.equals("null")) return true;
                          if (rm.getName().equals("getBoolean") && mode.equals("false"))
                            return false;
                          if (rm.getName().equals("getLong")) {
                            if (mode.equals("zero")) return 0L;
                            if (mode.equals("negative")) return -1L;
                            if (mode.equals("large")) return 1_000_000_000_000L;
                          }
                          Object result = invoke(r, rm, ra);
                          if (rm.getName().equals("close")
                              && (mode.equals("resultClose") || mode.equals("doubleClose")))
                            throw new SQLException("synthetic result close");
                          return result;
                        });
                  });
            });
  }

  private static Object invoke(Object owner, java.lang.reflect.Method method, Object[] args)
      throws Throwable {
    try {
      return method.invoke(owner, args);
    } catch (InvocationTargetException e) {
      throw e.getCause();
    }
  }

  private static void independentHash(String hash, String expected) throws Exception {
    assertTrue(hash.matches("\\{pbkdf2-v1}[0-9a-f]{96}"));
    byte[] decoded = HexFormat.of().parseHex(hash.substring(11));
    var spec = new PBEKeySpec(expected.toCharArray(), Arrays.copyOf(decoded, 16), 310_000, 256);
    try {
      assertArrayEquals(
          Arrays.copyOfRange(decoded, 16, 48),
          SecretKeyFactory.getInstance("PBKDF2WithHmacSHA256").generateSecret(spec).getEncoded());
    } finally {
      spec.clearPassword();
      Arrays.fill(decoded, (byte) 0);
    }
  }

  private static String seedSql(String role, String status) {
    return "insert into schubert.app_users(username,username_key,password_hash,role,status,password_changed_at,created_at,updated_at) values ('seed','seed','{pbkdf2-v1}"
        + "0".repeat(96)
        + "','"
        + role
        + "','"
        + status
        + "',now(),now(),now())";
  }

  private static void seed(String role, String status) throws Exception {
    try (var c = db.api();
        var s = c.createStatement()) {
      assertEquals(1, s.executeUpdate(seedSql(role, status)));
    }
  }

  private static long count(String table) throws Exception {
    assertTrue(Set.of("app_users", "app_logs").contains(table));
    try (var c = db.api();
        var s = c.createStatement();
        var r = s.executeQuery("select count(*) from schubert." + table)) {
      assertTrue(r.next());
      return r.getLong(1);
    }
  }

  private static String snapshot() throws Exception {
    try (var c = db.api();
        var s = c.createStatement();
        var r =
            s.executeQuery("select row_to_json(u)::text from schubert.app_users u order by id")) {
      var rows = new ArrayList<String>();
      while (r.next()) rows.add(r.getString(1));
      return rows.toString();
    }
  }
}
