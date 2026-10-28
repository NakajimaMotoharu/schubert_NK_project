package dev.codex.schubert.nk.api.security;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.api.domain.Role;
import dev.codex.schubert.nk.api.logging.ApiLogDatabaseFixture;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.lang.reflect.Proxy;
import java.net.InetAddress;
import java.nio.file.Path;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** PT-AUT-003-D01..06. Production DDL/limited role; literal SQL postconditions are the oracle. */
final class LoginAttemptRepositoryTest {
  private static final String FIXTURE_SELECT_COUNT_FROM_SCHUBERT_LOGIN_IP_ATTE_4B6009EB =
      "select count(*) from schubert.login_ip_attempts";
  private static final String FIXTURE_SELECT_FAILED_COUNT_FROM_SCHUBERT_APP_US_FF15412D =
      "select failed_count from schubert.app_users where id=7";
  private static final String FIXTURE_LOGIN_USER_D270AFC0 = "login-user";
  private static final String FIXTURE_127_0_0_1_88270499 = "127.0.0.1";
  private static final String FIXTURE_LOCKED_UNTIL_C81A370E = "locked_until";
  private static final String FIXTURE_2026_09_08T00_15_00Z_5E8331B7 = "2026-09-08T00:15:00Z";
  private static final String FIXTURE_LOGIN_IP_ATTEMPTS_0BA2E9DA = "login_ip_attempts";
  private static final String FIXTURE_TRUE_18D10C7D = "true";
  private static final String FIXTURE_CLOSE_97959247 = "close";
  private static final String FIXTURE_SYNTHETIC_SENSITIVE_CLOSE_16A2CAC4 =
      "synthetic-sensitive-close";
  @TempDir static Path root;
  private static ApiLogDatabaseFixture database;
  private static InetAddress client;
  private static final Instant NOW = Instant.parse("2026-09-08T00:00:00Z");
  private final LoginAttemptRepository repository = new LoginAttemptRepository();

  @BeforeAll
  static void start() throws Exception {
    database = new ApiLogDatabaseFixture(root);
    client = InetAddress.getByAddress(new byte[] {127, 0, 0, 1});
  }

  @AfterAll
  static void stop() throws Exception {
    if (database != null) database.stop();
  }

  @BeforeEach
  void seed() throws SQLException {
    execute("delete from schubert.login_ip_attempts");
    execute("delete from schubert.app_users");
    execute(
        "insert into"
            + " schubert.app_users(id,username,username_key,password_hash,role,status,password_changed_at,created_at,updated_at)"
            + " values"
            + "(7,'Login-User','login-user','unusable-fixture-hash','USER','ACTIVE','2026-09-08','2026-09-08','2026-09-08'),"
            + "(8,'Other-User','other-user','unusable-fixture-hash','ADMIN','DISABLED','2026-09-08','2026-09-08','2026-09-08')");
  }

  @Test
  void knownAndUnknownUsersLockUserBeforeIpAndPersistAcrossConnections() throws Exception {
    var sql = new ArrayList<String>();
    try (Connection connection = database.transaction()) {
      var locked =
          repository.lockForAttempt(
              intercept(connection, "observe", sql), FIXTURE_LOGIN_USER_D270AFC0, client, NOW);
      var account = locked.account().orElseThrow();
      assertEquals(new AuthenticatedActor(7, "Login-User", Role.USER), account.identity());
      assertTrue(account.active());
      assertEquals("unusable-fixture-hash", account.passwordHash());
      assertEquals(0, account.attempts().failedCount());
      assertEquals(0, locked.ip().failedCount());
      assertEquals(Optional.of(NOW), locked.ip().windowStartedAt());
      assertEquals(FIXTURE_127_0_0_1_88270499, locked.clientAddress());
      assertEquals("LoginAccount[REDACTED]", account.toString());
      assertEquals("LockedLoginAttempt[REDACTED]", locked.toString());
      repository.recordFailure(connection, locked, NOW);
      connection.commit();
    }
    assertEquals(3, sql.size());
    assertTrue(sql.get(0).contains("from schubert.app_users"));
    assertTrue(sql.get(0).endsWith("for update"));
    assertTrue(sql.get(1).startsWith("insert into schubert.login_ip_attempts"));
    assertTrue(sql.get(2).endsWith("for update"));
    try (Connection connection = database.transaction()) {
      var restarted =
          new LoginAttemptRepository()
              .lockForAttempt(connection, FIXTURE_LOGIN_USER_D270AFC0, client, NOW.plusSeconds(1));
      assertEquals(1, restarted.account().orElseThrow().attempts().failedCount());
      assertEquals(
          Optional.of(NOW), restarted.account().orElseThrow().attempts().windowStartedAt());
      assertEquals(1, restarted.ip().failedCount());
      assertEquals(Optional.of(NOW), restarted.ip().windowStartedAt());
      connection.rollback();
      var other = repository.lockForAttempt(connection, "other-user", client, NOW);
      assertFalse(other.account().orElseThrow().active());
      assertEquals(Role.ADMIN, other.account().orElseThrow().identity().role());
      connection.rollback();
      var unknown =
          repository.lockForAttempt(connection, "unknown", InetAddress.ofLiteral("::1"), NOW);
      assertTrue(unknown.account().isEmpty());
      repository.recordFailure(connection, unknown, NOW);
      connection.commit();
    }
    assertEquals(
        1,
        scalar("select failed_count from schubert.login_ip_attempts where client_address='::1'"));
    assertEquals(2, scalar(FIXTURE_SELECT_COUNT_FROM_SCHUBERT_LOGIN_IP_ATTE_4B6009EB));
  }

  @Test
  void thresholdsWindowsLocksAndSuccessHaveLiteralSqlPostconditions() throws Exception {
    for (int i = 1; i <= 10; i++) {
      fail(FIXTURE_LOGIN_USER_D270AFC0, NOW);
      assertEquals(
          Math.min(5, i), scalar(FIXTURE_SELECT_FAILED_COUNT_FROM_SCHUBERT_APP_US_FF15412D));
      assertEquals(i, scalar("select failed_count from schubert.login_ip_attempts"));
    }
    assertTimestamp(
        "app_users", FIXTURE_LOCKED_UNTIL_C81A370E, "id=7", FIXTURE_2026_09_08T00_15_00Z_5E8331B7);
    assertTimestamp(
        FIXTURE_LOGIN_IP_ATTEMPTS_0BA2E9DA,
        FIXTURE_LOCKED_UNTIL_C81A370E,
        FIXTURE_TRUE_18D10C7D,
        FIXTURE_2026_09_08T00_15_00Z_5E8331B7);
    fail(FIXTURE_LOGIN_USER_D270AFC0, NOW.plusSeconds(30));
    assertTimestamp(
        "app_users", FIXTURE_LOCKED_UNTIL_C81A370E, "id=7", FIXTURE_2026_09_08T00_15_00Z_5E8331B7);
    assertTimestamp(
        FIXTURE_LOGIN_IP_ATTEMPTS_0BA2E9DA,
        FIXTURE_LOCKED_UNTIL_C81A370E,
        FIXTURE_TRUE_18D10C7D,
        FIXTURE_2026_09_08T00_15_00Z_5E8331B7);
    try (Connection connection = database.transaction()) {
      var locked =
          repository.lockForAttempt(
              connection, FIXTURE_LOGIN_USER_D270AFC0, client, NOW.plusSeconds(901));
      repository.recordSuccess(connection, locked, NOW.plusSeconds(901));
      connection.commit();
    }
    assertEquals(
        1,
        scalar(
            "select count(*) from schubert.app_users where id=7 and failed_count=0 and"
                + " failure_window_started_at is null and locked_until is null"));
    assertEquals(
        1,
        scalar(
            "select count(*) from schubert.login_ip_attempts where failed_count=0 and locked_until"
                + " is null"));
    assertTimestamp("app_users", "last_login_at", "id=7", "2026-09-08T00:15:01Z");
    assertTimestamp(
        FIXTURE_LOGIN_IP_ATTEMPTS_0BA2E9DA,
        "window_started_at",
        FIXTURE_TRUE_18D10C7D,
        "2026-09-08T00:15:01Z");
    assertTimestamp(
        FIXTURE_LOGIN_IP_ATTEMPTS_0BA2E9DA,
        "updated_at",
        FIXTURE_TRUE_18D10C7D,
        "2026-09-08T00:15:01Z");
    for (long offset : new long[] {899_999_999_000L, 900_000_000_000L, 900_000_001_000L}) {
      seed();
      fail(FIXTURE_LOGIN_USER_D270AFC0, NOW);
      fail(FIXTURE_LOGIN_USER_D270AFC0, NOW.plusNanos(offset));
      int expected = offset <= 900_000_000_000L ? 2 : 1; // Current endpoint, SSC-009/BUG-021.
      assertEquals(expected, scalar(FIXTURE_SELECT_FAILED_COUNT_FROM_SCHUBERT_APP_US_FF15412D));
      assertEquals(expected, scalar("select failed_count from schubert.login_ip_attempts"));
      assertEquals(
          1,
          scalar("select count(*) from schubert.app_users where id=7 and last_login_at is null"));
    }
  }

  @Test
  void concurrentAttemptsHaveNoLostUpdatesAndRollbackRestoresAllRows() throws Exception {
    try (var executor = Executors.newFixedThreadPool(16)) {
      var results = new ArrayList<Future<?>>();
      for (int i = 0; i < 100; i++) {
        String name = List.of(FIXTURE_LOGIN_USER_D270AFC0, "other-user", "unknown").get(i % 3);
        results.add(
            executor.submit(
                () -> {
                  fail(name, NOW);
                  return null;
                }));
      }
      for (var result : results) result.get();
    }
    assertEquals(
        2,
        scalar(
            "select count(*) from schubert.app_users where failed_count=5 and"
                + " locked_until='2026-09-08T00:15:00Z'"));
    assertEquals(
        1,
        scalar(
            "select count(*) from schubert.login_ip_attempts where failed_count=10 and"
                + " locked_until='2026-09-08T00:15:00Z'"));
    try (Connection connection = database.transaction()) {
      var locked =
          repository.lockForAttempt(
              connection, FIXTURE_LOGIN_USER_D270AFC0, client, NOW.plusSeconds(901));
      repository.recordSuccess(connection, locked, NOW.plusSeconds(901));
      connection.rollback();
      assertFalse(connection.isClosed());
    }
    assertEquals(5, scalar(FIXTURE_SELECT_FAILED_COUNT_FROM_SCHUBERT_APP_US_FF15412D));
    assertEquals(10, scalar("select failed_count from schubert.login_ip_attempts"));
    seed();
    try (Connection connection = database.transaction()) {
      repository.recordFailure(
          connection,
          repository.lockForAttempt(connection, FIXTURE_LOGIN_USER_D270AFC0, client, NOW),
          NOW);
      connection.rollback();
    }
    assertEquals(0, scalar(FIXTURE_SELECT_FAILED_COUNT_FROM_SCHUBERT_APP_US_FF15412D));
    assertEquals(0, scalar(FIXTURE_SELECT_COUNT_FROM_SCHUBERT_LOGIN_IP_ATTE_4B6009EB));
  }

  @Test
  void jdbcNullUnknownEnumAndFaultsFailClosedWithoutProviderData() throws Exception {
    // BUG169/YKT130: unknown-user insertion and successful-attempt persistence both bind time.
    for (Instant invalid : List.of(Instant.MIN, Instant.MAX)) {
      try (var c = database.transaction()) {
        assertInfrastructure(() -> repository.lockForAttempt(c, "unknown", client, invalid));
        c.rollback();
      }
      try (var c = database.transaction()) {
        var locked = repository.lockForAttempt(c, FIXTURE_LOGIN_USER_D270AFC0, client, NOW);
        assertInfrastructure(() -> repository.recordSuccess(c, locked, invalid));
        c.rollback();
        assertFalse(c.isClosed());
      }
      assertEquals(0, scalar(FIXTURE_SELECT_COUNT_FROM_SCHUBERT_LOGIN_IP_ATTE_4B6009EB));
    }
    for (String fault :
        List.of(
            "getAutoCommit",
            "prepareStatement",
            "setString",
            "executeQuery",
            "executeUpdate",
            "rowClose",
            "statementClose",
            "user:null:role",
            "user:null:status",
            "user:null:id",
            "user:null:username",
            "user:null:password_hash",
            "user:null:failed_count",
            "ip:null:failed_count",
            "ip:null:window_started_at",
            "unknownRole",
            "unknownStatus",
            "badCount",
            "emptyHash",
            "missingIp")) {
      try (Connection connection = database.transaction()) {
        assertInfrastructure(
            () ->
                repository.lockForAttempt(
                    intercept(connection, fault, new ArrayList<>()),
                    FIXTURE_LOGIN_USER_D270AFC0,
                    client,
                    NOW));
        connection.rollback();
        assertFalse(connection.isClosed());
      }
      assertEquals(0, scalar(FIXTURE_SELECT_COUNT_FROM_SCHUBERT_LOGIN_IP_ATTE_4B6009EB));
    }
    for (String fault :
        List.of(
            "getAutoCommit",
            "prepareStatement",
            "setInt",
            "setNull",
            "setObject",
            "zeroUser",
            "zeroIp",
            "afterIp",
            "statementClose")) {
      try (Connection connection = database.transaction()) {
        var locked =
            repository.lockForAttempt(connection, FIXTURE_LOGIN_USER_D270AFC0, client, NOW);
        assertInfrastructure(
            () ->
                repository.recordFailure(
                    intercept(connection, fault, new ArrayList<>()), locked, NOW));
        connection.rollback();
      }
      assertEquals(0, scalar(FIXTURE_SELECT_FAILED_COUNT_FROM_SCHUBERT_APP_US_FF15412D));
      assertEquals(0, scalar(FIXTURE_SELECT_COUNT_FROM_SCHUBERT_LOGIN_IP_ATTE_4B6009EB));
    }
    fail(FIXTURE_LOGIN_USER_D270AFC0, NOW);
    try (Connection connection = database.transaction()) {
      var locked = repository.lockForAttempt(connection, FIXTURE_LOGIN_USER_D270AFC0, client, NOW);
      assertInfrastructure(() -> repository.recordFailure(connection, locked, NOW.minusSeconds(1)));
      connection.rollback();
    }
    assertEquals(1, scalar(FIXTURE_SELECT_FAILED_COUNT_FROM_SCHUBERT_APP_US_FF15412D));
  }

  @Test
  void providerIllegalArgumentAndCloseSqlRemainRedactedInfrastructure() throws Exception {
    // PT-AUT-003-D06/YKT-162: provider IAE is not a model-validation result. Close failure is
    // secondary; the two production catch sites must keep their fixed Infrastructure contract.
    try (Connection connection = database.transaction()) {
      assertInfrastructure(
          () ->
              repository.lockForAttempt(
                  intercept(connection, "providerIaeReadAndRowClose", new ArrayList<>()),
                  FIXTURE_LOGIN_USER_D270AFC0,
                  client,
                  NOW));
      connection.rollback();
      assertFalse(connection.isClosed());
    }
    assertEquals(0, scalar(FIXTURE_SELECT_COUNT_FROM_SCHUBERT_LOGIN_IP_ATTE_4B6009EB));
    try (Connection connection = database.transaction()) {
      var locked = repository.lockForAttempt(connection, FIXTURE_LOGIN_USER_D270AFC0, client, NOW);
      assertInfrastructure(
          () ->
              repository.recordFailure(
                  intercept(connection, "providerIaeWriteAndStatementClose", new ArrayList<>()),
                  locked,
                  NOW));
      connection.rollback();
      assertFalse(connection.isClosed());
    }
    assertEquals(0, scalar(FIXTURE_SELECT_FAILED_COUNT_FROM_SCHUBERT_APP_US_FF15412D));
    assertEquals(0, scalar(FIXTURE_SELECT_COUNT_FROM_SCHUBERT_LOGIN_IP_ATTE_4B6009EB));
  }

  @Test
  void modelAndMethodNullBoundsDoNotInventPersistedState() throws Exception {
    var actor = new AuthenticatedActor(7, "user", Role.USER);
    var user = LoginAttemptState.empty(LoginAttemptKind.USER);
    var ip = LoginAttemptState.empty(LoginAttemptKind.IP);
    assertThrows(NullPointerException.class, () -> new LoginAccount(null, true, "hash", user));
    assertThrows(NullPointerException.class, () -> new LoginAccount(actor, true, null, user));
    assertThrows(NullPointerException.class, () -> new LoginAccount(actor, true, "hash", null));
    for (String hash : List.of("", "a".repeat(256)))
      assertThrows(IllegalArgumentException.class, () -> new LoginAccount(actor, true, hash, user));
    assertEquals(255, new LoginAccount(actor, true, "a".repeat(255), user).passwordHash().length());
    assertThrows(IllegalArgumentException.class, () -> new LoginAccount(actor, true, "hash", ip));
    assertThrows(
        NullPointerException.class, () -> new LockedLoginAttempt(null, Optional.empty(), ip));
    assertThrows(
        NullPointerException.class,
        () -> new LockedLoginAttempt(FIXTURE_127_0_0_1_88270499, null, ip));
    assertThrows(
        NullPointerException.class,
        () -> new LockedLoginAttempt(FIXTURE_127_0_0_1_88270499, Optional.empty(), null));
    assertThrows(
        IllegalArgumentException.class,
        () -> new LockedLoginAttempt(FIXTURE_127_0_0_1_88270499, Optional.empty(), user));
    var locked = new LockedLoginAttempt(FIXTURE_127_0_0_1_88270499, Optional.empty(), ip);
    assertEquals(
        "0:0:0:0:0:0:0:1", new LockedLoginAttempt("::1", Optional.empty(), ip).clientAddress());
    for (String invalid : List.of("", "localhost", "127.0.0.999", "fe80::1%1", "127.0.0.1\n")) {
      var error =
          assertThrows(
              IllegalArgumentException.class,
              () -> new LockedLoginAttempt(invalid, Optional.empty(), ip));
      assertNull(error.getCause());
      assertTrue(
          error.getMessage().equals("login IP literal is invalid")
              || error.getMessage().equals("login IP scope is invalid"));
    }
    try (Connection connection = database.api()) {
      assertInfrastructure(
          () -> repository.lockForAttempt(connection, FIXTURE_LOGIN_USER_D270AFC0, client, NOW));
      assertInfrastructure(() -> repository.recordFailure(connection, locked, NOW));
    }
    try (Connection connection = database.transaction()) {
      assertThrows(
          NullPointerException.class, () -> repository.lockForAttempt(null, "x", client, NOW));
      assertThrows(
          NullPointerException.class,
          () -> repository.lockForAttempt(connection, null, client, NOW));
      assertThrows(
          NullPointerException.class, () -> repository.lockForAttempt(connection, "x", null, NOW));
      assertThrows(
          NullPointerException.class,
          () -> repository.lockForAttempt(connection, "x", client, null));
      for (String key : List.of("", "a".repeat(97)))
        assertThrows(
            IllegalArgumentException.class,
            () -> repository.lockForAttempt(connection, key, client, NOW));
      assertThrows(NullPointerException.class, () -> repository.recordFailure(null, locked, NOW));
      assertThrows(
          NullPointerException.class, () -> repository.recordFailure(connection, null, NOW));
      assertThrows(
          NullPointerException.class, () -> repository.recordSuccess(connection, locked, null));
      assertTrue(
          repository.lockForAttempt(connection, "a".repeat(96), client, NOW).account().isEmpty());
      connection.rollback();
    }
    assertEquals(0, scalar(FIXTURE_SELECT_COUNT_FROM_SCHUBERT_LOGIN_IP_ATTE_4B6009EB));
  }

  private void fail(String name, Instant now) throws SQLException {
    try (Connection connection = database.transaction()) {
      repository.recordFailure(
          connection, repository.lockForAttempt(connection, name, client, now), now);
      connection.commit();
    }
  }

  private static void execute(String sql) throws SQLException {
    try (Connection connection = database.api();
        var statement = connection.createStatement()) {
      statement.executeUpdate(sql);
    }
  }

  private static int scalar(String sql) throws SQLException {
    try (Connection connection = database.api();
        var statement = connection.createStatement();
        var row = statement.executeQuery(sql)) {
      assertTrue(row.next());
      return row.getInt(1);
    }
  }

  private static void assertTimestamp(
      String table, String column, String predicate, String expected) throws SQLException {
    try (Connection connection = database.api();
        var statement = connection.createStatement();
        var row =
            statement.executeQuery(
                "select " + column + " from schubert." + table + " where " + predicate)) {
      assertTrue(row.next());
      assertEquals(
          Instant.parse(expected), row.getObject(1, java.time.OffsetDateTime.class).toInstant());
    }
  }

  private static void assertInfrastructure(org.junit.jupiter.api.function.Executable action) {
    var failure = assertThrows(AuthenticationInfrastructureException.class, action);
    assertEquals("authentication storage is unavailable", failure.getMessage());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
  }

  private static Connection intercept(Connection real, String fault, List<String> sql) {
    return (Connection)
        Proxy.newProxyInstance(
            Connection.class.getClassLoader(),
            new Class<?>[] {Connection.class},
            (proxy, method, args) -> {
              if (method.getName().equals(fault))
                throw new SQLException("synthetic-sensitive-provider-text");
              Object result = invoke(real, method, args);
              if (!method.getName().equals("prepareStatement")) return result;
              String statementSql = (String) args[0];
              sql.add(statementSql);
              boolean userQuery = statementSql.contains("from schubert.app_users");
              boolean ipQuery = statementSql.startsWith("select") && !userQuery;
              boolean userUpdate = statementSql.startsWith("update schubert.app_users");
              boolean ipUpdate = statementSql.startsWith("update schubert.login_ip_attempts");
              return Proxy.newProxyInstance(
                  PreparedStatement.class.getClassLoader(),
                  new Class<?>[] {PreparedStatement.class},
                  (sp, sm, sa) -> {
                    if (fault.equals("providerIaeWriteAndStatementClose")
                        && sm.getName().equals("setInt"))
                      throw new IllegalArgumentException("synthetic-sensitive-provider-identity");
                    if (fault.equals("providerIaeWriteAndStatementClose")
                        && sm.getName().equals(FIXTURE_CLOSE_97959247))
                      throw new SQLException(FIXTURE_SYNTHETIC_SENSITIVE_CLOSE_16A2CAC4);
                    if (sm.getName().equals(fault))
                      throw new SQLException("synthetic-sensitive-provider-text");
                    if (sm.getName().equals("executeUpdate")
                        && ((userUpdate && fault.equals("zeroUser"))
                            || (ipUpdate && fault.equals("zeroIp")))) return 0;
                    Object sr = invoke(result, sm, sa);
                    if (ipUpdate && fault.equals("afterIp") && sm.getName().equals("executeUpdate"))
                      throw new SQLException("synthetic-sensitive-after-write");
                    if (sm.getName().equals(FIXTURE_CLOSE_97959247)
                        && fault.equals("statementClose"))
                      throw new SQLException(FIXTURE_SYNTHETIC_SENSITIVE_CLOSE_16A2CAC4);
                    if (!sm.getName().equals("executeQuery")) return sr;
                    return Proxy.newProxyInstance(
                        ResultSet.class.getClassLoader(),
                        new Class<?>[] {ResultSet.class},
                        (rp, rm, ra) -> {
                          if (fault.equals("providerIaeReadAndRowClose")
                              && rm.getName().equals("getObject"))
                            throw new IllegalArgumentException(
                                "synthetic-sensitive-provider-identity");
                          if (fault.equals("providerIaeReadAndRowClose")
                              && rm.getName().equals(FIXTURE_CLOSE_97959247))
                            throw new SQLException(FIXTURE_SYNTHETIC_SENSITIVE_CLOSE_16A2CAC4);
                          String scope = userQuery ? "user:" : "ip:";
                          if (fault.startsWith(scope + "null:")
                              && ra != null
                              && fault.substring((scope + "null:").length()).equals(ra[0]))
                            return null;
                          if (userQuery && rm.getName().equals("getString")) {
                            if (fault.equals("unknownRole") && ra[0].equals("role"))
                              return "UNKNOWN";
                            if (fault.equals("unknownStatus") && ra[0].equals("status"))
                              return "UNKNOWN";
                            if (fault.equals("emptyHash") && ra[0].equals("password_hash"))
                              return "";
                          }
                          if (userQuery
                              && fault.equals("badCount")
                              && rm.getName().equals("getObject")
                              && ra[0].equals("failed_count")) return -1;
                          if (ipQuery && fault.equals("missingIp") && rm.getName().equals("next"))
                            return false;
                          Object rr = invoke(sr, rm, ra);
                          if (rm.getName().equals(FIXTURE_CLOSE_97959247)
                              && fault.equals("rowClose"))
                            throw new SQLException(FIXTURE_SYNTHETIC_SENSITIVE_CLOSE_16A2CAC4);
                          return rr;
                        });
                  });
            });
  }

  private static Object invoke(Object target, Method method, Object[] args) throws Throwable {
    try {
      return method.invoke(target, args);
    } catch (InvocationTargetException failure) {
      throw failure.getCause();
    }
  }
}
