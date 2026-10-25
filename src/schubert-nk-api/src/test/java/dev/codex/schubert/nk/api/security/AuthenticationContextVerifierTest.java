package dev.codex.schubert.nk.api.security;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.api.domain.Role;
import dev.codex.schubert.nk.api.logging.ApiLogDatabaseFixture;
import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.lang.reflect.Proxy;
import java.nio.file.Path;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/**
 * PT-AUT-007: real PostgreSQL/production DDL, literal SQL postconditions and JDBC-boundary faults.
 */
final class AuthenticationContextVerifierTest {
  @TempDir static Path root;
  private static ApiLogDatabaseFixture database;
  private static AuthenticationContextVerifier verifier;
  private static final AuthenticationContext RAW = AuthenticationContext.of("a".repeat(64));
  private static final Instant NOW = Instant.parse("2026-09-07T01:00:00Z");

  @BeforeAll
  static void start() throws Exception {
    database = new ApiLogDatabaseFixture(root);
    verifier = new AuthenticationContextVerifier(new ContextHash());
  }

  @AfterAll
  static void stop() throws Exception {
    if (database != null) database.stop();
  }

  @BeforeEach
  void seed() throws SQLException {
    // Synthetic storage-only ciphertext/hash: this is lookup PT, not encryption validity evidence.
    execute("delete from schubert.auth_sessions");
    execute("delete from schubert.app_users");
    execute(
        "insert into"
            + " schubert.app_users(id,username,username_key,password_hash,role,status,password_changed_at,created_at,updated_at)"
            + " values(7,'verifier-user','verifier-user','unusable-fixture-hash','USER','ACTIVE','2026-09-07','2026-09-07','2026-09-07')");
    execute(
        "insert into"
            + " schubert.auth_sessions(id,user_id,context_hash,context_ciphertext,key_version,issued_at,last_accessed_at,expires_at,client_address,created_message_id)"
            + " values('a1000000-0000-0000-0000-000000000001',7,'ffe054fe7ae0cb6dc65c3af9b61d5209f439851db43d0ba5997337df154668eb',"
            + "decode(repeat('00',29),'hex'),'fixture','2026-09-07T00:00:00Z','2026-09-07T00:00:00Z','2026-09-07T08:00:00Z','127.0.0.1','a2000000-0000-0000-0000-000000000001')");
  }

  @Test
  void currentDatabaseActorAndIdleUpdateUseCallerTransactionWithoutShortening() throws Exception {
    try (Connection connection = database.transaction()) {
      AuthenticatedActor actor = verifier.verify(connection, RAW, NOW);
      assertEquals(new AuthenticatedActor(7, "verifier-user", Role.USER), actor);
      assertTimes("2026-09-07T00:00:00Z", "2026-09-07T08:00:00Z");
      assertFalse(connection.isClosed());
      assertFalse(connection.getAutoCommit());
      connection.rollback();
      assertTimes("2026-09-07T00:00:00Z", "2026-09-07T08:00:00Z");
      verifier.verify(connection, RAW, NOW);
      connection.commit();
    }
    assertTimes("2026-09-07T01:00:00Z", "2026-09-07T09:00:00Z");
    execute("update schubert.app_users set role='ADMIN',username='changed-user' where id=7");
    try (Connection connection = database.transaction()) {
      assertEquals(
          new AuthenticatedActor(7, "changed-user", Role.ADMIN),
          verifier.verify(connection, RAW, NOW.plusSeconds(3600)));
      connection.commit();
      verifier.verify(connection, RAW, NOW);
      connection.commit();
    }
    assertTimes("2026-09-07T02:00:00Z", "2026-09-07T10:00:00Z");
    // No absolute lifetime: frequent access can continue past the issue date.
    try (Connection connection = database.transaction()) {
      for (int hour = 3; hour <= 30; hour++) {
        verifier.verify(
            connection, RAW, Instant.parse("2026-09-07T00:00:00Z").plusSeconds(hour * 3600L));
        connection.commit();
      }
    }
    assertTimes("2026-09-08T06:00:00Z", "2026-09-08T14:00:00Z");
  }

  @Test
  void unknownRevokedExpiredAndDisabledAllDenyWithoutTouch() throws Exception {
    for (String scenario : List.of("unknown", "revoked", "equalExpiry", "pastExpiry", "disabled")) {
      seed();
      switch (scenario) {
        case "revoked" ->
            execute(
                "update schubert.auth_sessions set"
                    + " revoked=true,revoked_at='2026-09-07T00:30:00Z',revoke_reason='LOGOUT'");
        case "equalExpiry" ->
            execute("update schubert.auth_sessions set expires_at='2026-09-07T01:00:00Z'");
        case "pastExpiry" ->
            execute("update schubert.auth_sessions set expires_at='2026-09-07T00:59:59.999999Z'");
        case "disabled" -> execute("update schubert.app_users set status='DISABLED'");
        default -> {}
      }
      try (Connection connection = database.transaction()) {
        AuthenticationContext raw =
            scenario.equals("unknown") ? AuthenticationContext.of("b".repeat(64)) : RAW;
        AuthenticationContextException error =
            assertThrows(
                AuthenticationContextException.class, () -> verifier.verify(connection, raw, NOW));
        assertEquals("authentication context is not valid", error.getMessage());
        assertNull(error.getCause());
        assertEquals(0, error.getSuppressed().length);
        connection.rollback();
      }
      try (Connection connection = database.api();
          var statement = connection.createStatement();
          var row = statement.executeQuery("select last_accessed_at from schubert.auth_sessions")) {
        assertTrue(row.next());
        assertEquals(
            Instant.parse("2026-09-07T00:00:00Z"),
            row.getObject(1, java.time.OffsetDateTime.class).toInstant());
      }
    }
  }

  @Test
  void concurrentVerificationsSerializeUserThenSessionAndRemainUsable() throws Exception {
    // 100 submitted calls, 16 concurrent JDBC transactions: stay below the isolated PG connection
    // cap.
    try (var executor = Executors.newFixedThreadPool(16)) {
      var results = new ArrayList<Future<AuthenticatedActor>>();
      for (int i = 0; i < 100; i++) {
        results.add(
            executor.submit(
                () -> {
                  try (Connection connection = database.transaction()) {
                    var actor = verifier.verify(connection, RAW, NOW);
                    connection.commit();
                    return actor;
                  }
                }));
      }
      for (var result : results) assertEquals(7, result.get().userId());
    }
    assertTimes("2026-09-07T01:00:00Z", "2026-09-07T09:00:00Z");
    List<String> sql = new ArrayList<>();
    try (Connection connection = database.transaction()) {
      verifier.verify(intercept(connection, "observe", sql), RAW, NOW);
      connection.rollback();
    }
    assertEquals(3, sql.size());
    assertTrue(sql.get(0).endsWith("for update of u"));
    assertTrue(sql.get(1).endsWith("for update of s"));
    assertTrue(sql.get(2).startsWith("update schubert.auth_sessions"));
  }

  @Test
  void sqlNullAndUnknownRoleNeverBecomeAValidActor() throws Exception {
    for (String column :
        List.of("revoked", "expires_at", "status", "id", "user_id", "username", "role")) {
      try (Connection connection = database.transaction()) {
        assertInfrastructure(
            () ->
                verifier.verify(
                    intercept(connection, "null:" + column, new ArrayList<>()), RAW, NOW));
        connection.rollback();
      }
    }
    try (Connection connection = database.transaction()) {
      assertInfrastructure(
          () -> verifier.verify(intercept(connection, "unknownRole", new ArrayList<>()), RAW, NOW));
      connection.rollback();
      assertThrows(
          AuthenticationContextException.class,
          () ->
              verifier.verify(
                  intercept(connection, "missingSession", new ArrayList<>()), RAW, NOW));
      connection.rollback();
    }
  }

  @Test
  void sqlFaultsAndSuppressedCloseErrorsAreBoundedAndDoNotCommit() throws Exception {
    for (String point :
        List.of(
            "getAutoCommit",
            "prepareStatement",
            "setString",
            "executeQuery",
            "getObject",
            "executeUpdate",
            "rowClose",
            "statementClose",
            "zeroUpdate")) {
      try (Connection connection = database.transaction()) {
        assertInfrastructure(
            () -> verifier.verify(intercept(connection, point, new ArrayList<>()), RAW, NOW));
        assertFalse(connection.isClosed());
        connection.rollback();
      }
      assertTimes("2026-09-07T00:00:00Z", "2026-09-07T08:00:00Z");
    }
    try (Connection connection = database.transaction()) {
      assertInfrastructure(
          () ->
              verifier.verify(
                  intercept(connection, "rowClose", new ArrayList<>()),
                  AuthenticationContext.of("b".repeat(64)),
                  NOW));
      connection.rollback();
    }
  }

  @Test
  void nullAndAutocommitBoundariesRejectBeforeModifyingState() throws Exception {
    assertThrows(NullPointerException.class, () -> new AuthenticationContextVerifier(null));
    assertThrows(NullPointerException.class, () -> verifier.verify(null, RAW, NOW));
    try (Connection connection = database.api()) {
      assertThrows(NullPointerException.class, () -> verifier.verify(connection, null, NOW));
      assertThrows(NullPointerException.class, () -> verifier.verify(connection, RAW, null));
      assertInfrastructure(() -> verifier.verify(connection, RAW, NOW));
      assertFalse(connection.isClosed());
    }
    assertTimes("2026-09-07T00:00:00Z", "2026-09-07T08:00:00Z");
  }

  @Test
  void readOnlyPreflightReturnsCurrentActorWithoutTouchOrTransactionOwnership() throws Exception {
    for (Role role : List.of(Role.USER, Role.ADMIN)) {
      execute("update schubert.app_users set role='" + role.name() + "'");
      List<String> sql = new ArrayList<>();
      try (Connection connection = database.transaction()) {
        connection.setReadOnly(true);
        assertEquals(
            new AuthenticatedActor(7, "verifier-user", role),
            verifier.inspectReadOnly(intercept(connection, "observe", sql), RAW, NOW));
        assertFalse(connection.isClosed());
        assertFalse(connection.getAutoCommit());
        try (var statement = connection.createStatement();
            var row = statement.executeQuery("show transaction_read_only")) {
          assertTrue(row.next());
          assertEquals("on", row.getString(1));
        }
        assertEquals(1, sql.size());
        assertEquals(
            "select s.id,s.user_id,u.username,u.role,u.status,s.revoked,s.expires_at from"
                + " schubert.auth_sessions s join schubert.app_users u on u.id=s.user_id where"
                + " s.context_hash=?",
            sql.getFirst());
        connection.commit();
      }
      assertTimes("2026-09-07T00:00:00Z", "2026-09-07T08:00:00Z");
    }
  }

  @Test
  void readOnlyPreflightRejectsUnknownRevokedExpiredAndDisabled() throws Exception {
    for (String scenario : List.of("unknown", "revoked", "equalExpiry", "pastExpiry", "disabled")) {
      seed();
      switch (scenario) {
        case "revoked" ->
            execute(
                "update schubert.auth_sessions set"
                    + " revoked=true,revoked_at='2026-09-07T00:30:00Z',revoke_reason='LOGOUT'");
        case "equalExpiry" ->
            execute("update schubert.auth_sessions set expires_at='2026-09-07T01:00:00Z'");
        case "pastExpiry" ->
            execute("update schubert.auth_sessions set expires_at='2026-09-07T00:59:59.999999Z'");
        case "disabled" -> execute("update schubert.app_users set status='DISABLED'");
        default -> {}
      }
      try (Connection connection = database.transaction()) {
        connection.setReadOnly(true);
        AuthenticationContext raw =
            scenario.equals("unknown") ? AuthenticationContext.of("b".repeat(64)) : RAW;
        AuthenticationContextException error =
            assertThrows(
                AuthenticationContextException.class,
                () -> verifier.inspectReadOnly(connection, raw, NOW));
        assertEquals("authentication context is not valid", error.getMessage());
        assertNull(error.getCause());
        assertEquals(0, error.getSuppressed().length);
        connection.commit();
      }
      try (Connection connection = database.api();
          var statement = connection.createStatement();
          var row = statement.executeQuery("select last_accessed_at from schubert.auth_sessions")) {
        assertTrue(row.next());
        assertEquals(
            Instant.parse("2026-09-07T00:00:00Z"),
            row.getObject(1, java.time.OffsetDateTime.class).toInstant());
      }
    }
  }

  @Test
  void readOnlyPreflightBoundsNullContractsAndJdbcFailures() throws Exception {
    assertThrows(NullPointerException.class, () -> verifier.inspectReadOnly(null, RAW, NOW));
    try (Connection connection = database.api()) {
      assertThrows(
          NullPointerException.class, () -> verifier.inspectReadOnly(connection, null, NOW));
      assertThrows(
          NullPointerException.class, () -> verifier.inspectReadOnly(connection, RAW, null));
      assertInfrastructure(() -> verifier.inspectReadOnly(connection, RAW, NOW));
      connection.setAutoCommit(false);
      assertInfrastructure(() -> verifier.inspectReadOnly(connection, RAW, NOW));
    }
    for (String point :
        List.of(
            "getAutoCommit",
            "isReadOnly",
            "prepareStatement",
            "setString",
            "executeQuery",
            "getObject",
            "rowClose",
            "statementClose",
            "null:revoked",
            "null:expires_at",
            "null:status",
            "null:id",
            "null:user_id",
            "null:username",
            "null:role",
            "unknownRole")) {
      try (Connection connection = database.transaction()) {
        connection.setReadOnly(true);
        assertInfrastructure(
            () ->
                verifier.inspectReadOnly(
                    intercept(connection, point, new ArrayList<>()), RAW, NOW));
        assertFalse(connection.isClosed());
        assertFalse(connection.getAutoCommit());
        connection.rollback();
      }
    }
    for (String point : List.of("rowClose", "statementClose")) {
      try (Connection connection = database.transaction()) {
        connection.setReadOnly(true);
        assertInfrastructure(
            () ->
                verifier.inspectReadOnly(
                    intercept(connection, point, new ArrayList<>()),
                    AuthenticationContext.of("b".repeat(64)),
                    NOW));
        connection.rollback();
      }
    }
    try (Connection connection = database.transaction()) {
      connection.setReadOnly(true);
      assertThrows(
          AuthenticationContextException.class,
          () ->
              verifier.inspectReadOnly(
                  intercept(connection, "missingSession", new ArrayList<>()), RAW, NOW));
      connection.rollback();
    }
    assertTimes("2026-09-07T00:00:00Z", "2026-09-07T08:00:00Z");
  }

  @Test
  void readOnlyPreflightDoesNotWaitForRowLocksAndCannotAuthorizeAfterRevocation() throws Exception {
    try (Connection locked = database.transaction();
        var statement = locked.createStatement()) {
      try (var row = statement.executeQuery("select id from schubert.app_users for update")) {
        assertTrue(row.next());
      }
      try (var row = statement.executeQuery("select id from schubert.auth_sessions for update")) {
        assertTrue(row.next());
      }
      try (var executor = Executors.newFixedThreadPool(16)) {
        var results = new ArrayList<Future<AuthenticatedActor>>();
        for (int i = 0; i < 100; i++) {
          results.add(
              executor.submit(
                  () -> {
                    try (Connection connection = database.transaction()) {
                      connection.setReadOnly(true);
                      try (var timeout = connection.createStatement()) {
                        timeout.execute("set local statement_timeout='500ms'");
                      }
                      AuthenticatedActor actor = verifier.inspectReadOnly(connection, RAW, NOW);
                      connection.commit();
                      return actor;
                    }
                  }));
        }
        for (var result : results) {
          assertEquals(new AuthenticatedActor(7, "verifier-user", Role.USER), result.get());
        }
      }
      assertTimes("2026-09-07T00:00:00Z", "2026-09-07T08:00:00Z");
      assertEquals(
          1,
          statement.executeUpdate(
              "update schubert.auth_sessions set revoked=true,"
                  + "revoked_at='2026-09-07T01:00:01Z',revoke_reason='LOGOUT'"));
      locked.commit();
    }
    try (Connection connection = database.transaction()) {
      assertThrows(
          AuthenticationContextException.class,
          () -> verifier.verify(connection, RAW, NOW.plusSeconds(2)));
      connection.rollback();
    }
    assertTimes("2026-09-07T00:00:00Z", "2026-09-07T08:00:00Z");
  }

  private static void assertInfrastructure(org.junit.jupiter.api.function.Executable operation) {
    AuthenticationInfrastructureException error =
        assertThrows(AuthenticationInfrastructureException.class, operation);
    assertEquals("authentication storage is unavailable", error.getMessage());
    assertNull(error.getCause());
    assertEquals(0, error.getSuppressed().length);
  }

  private static void execute(String sql) throws SQLException {
    try (Connection connection = database.api();
        var statement = connection.createStatement()) {
      statement.executeUpdate(sql);
    }
  }

  private static void assertTimes(String accessed, String expires) throws SQLException {
    try (Connection connection = database.api();
        var statement = connection.createStatement();
        var row =
            statement.executeQuery(
                "select last_accessed_at,expires_at from schubert.auth_sessions")) {
      assertTrue(row.next());
      assertEquals(
          Instant.parse(accessed), row.getObject(1, java.time.OffsetDateTime.class).toInstant());
      assertEquals(
          Instant.parse(expires), row.getObject(2, java.time.OffsetDateTime.class).toInstant());
      assertFalse(row.next());
    }
  }

  private static Connection intercept(Connection real, String point, List<String> sql) {
    return (Connection)
        Proxy.newProxyInstance(
            Connection.class.getClassLoader(),
            new Class<?>[] {Connection.class},
            (proxy, method, arguments) -> {
              if (method.getName().equals(point))
                throw new SQLException("synthetic-sensitive-provider-text");
              Object result = invoke(real, method, arguments);
              if (method.getName().equals("prepareStatement")) {
                sql.add((String) arguments[0]);
                int stage = sql.size();
                return Proxy.newProxyInstance(
                    PreparedStatement.class.getClassLoader(),
                    new Class<?>[] {PreparedStatement.class},
                    (sp, sm, sa) -> {
                      if (sm.getName().equals(point))
                        throw new SQLException("synthetic-sensitive-provider-text");
                      if (point.equals("zeroUpdate") && sm.getName().equals("executeUpdate"))
                        return 0;
                      Object sr = invoke(result, sm, sa);
                      if (sm.getName().equals("close") && point.equals("statementClose"))
                        throw new SQLException("synthetic-sensitive-close");
                      if (sm.getName().equals("executeQuery")) {
                        return Proxy.newProxyInstance(
                            ResultSet.class.getClassLoader(),
                            new Class<?>[] {ResultSet.class},
                            (rp, rm, ra) -> {
                              if (rm.getName().equals(point))
                                throw new SQLException("synthetic-sensitive-provider-text");
                              if (sql.get(stage - 1).startsWith("select s.id,")) {
                                if (point.equals("missingSession") && rm.getName().equals("next"))
                                  return false;
                                if (point.startsWith("null:")
                                    && ra != null
                                    && point.substring(5).equals(ra[0])) return null;
                                if (point.equals("unknownRole")
                                    && rm.getName().equals("getString")
                                    && ra[0].equals("role")) return "UNKNOWN";
                              }
                              Object rr = invoke(sr, rm, ra);
                              if (point.equals("rowClose") && rm.getName().equals("close"))
                                throw new SQLException("synthetic-sensitive-close");
                              return rr;
                            });
                      }
                      return sr;
                    });
              }
              return result;
            });
  }

  private static Object invoke(Object target, Method method, Object[] arguments) throws Throwable {
    try {
      return method.invoke(target, arguments);
    } catch (InvocationTargetException failure) {
      throw failure.getCause();
    }
  }
}
