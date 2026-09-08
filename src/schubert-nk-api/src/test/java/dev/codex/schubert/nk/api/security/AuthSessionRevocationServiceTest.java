package dev.codex.schubert.nk.api.security;

import static org.junit.jupiter.api.Assertions.*;

import dev.codex.schubert.nk.api.domain.Role;
import dev.codex.schubert.nk.api.logging.ApiLogDatabaseFixture;
import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.header.ResultCode;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.lang.reflect.Proxy;
import java.net.InetAddress;
import java.nio.charset.StandardCharsets;
import java.nio.file.Path;
import java.security.MessageDigest;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.time.Instant;
import java.util.ArrayList;
import java.util.HexFormat;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/**
 * PT-AUT-008-R01..04: independent SQL postconditions; storage-only synthetic ciphertext, not AES
 * PT.
 */
final class AuthSessionRevocationServiceTest {
  @TempDir static Path root;
  private static ApiLogDatabaseFixture database;
  private static AuthSessionRevocationService service;
  private static Optional<InetAddress> client;
  private static final AuthenticationContext RAW = AuthenticationContext.of("a".repeat(64));
  private static final Instant NOW = Instant.parse("2026-09-08T01:00:00Z");
  private static final UUID MESSAGE = UUID.fromString("c1000000-0000-0000-0000-000000000001");
  private static final UUID CORRELATION = UUID.fromString("c2000000-0000-0000-0000-000000000001");
  private static final UUID SESSION = new UUID(0, 1);
  private static final AuthenticatedActor ADMIN =
      new AuthenticatedActor(8, "admin-user", Role.ADMIN);

  @BeforeAll
  static void start() throws Exception {
    database = new ApiLogDatabaseFixture(root);
    service = new AuthSessionRevocationService(new ContextHash());
    client = Optional.of(InetAddress.getByAddress(new byte[] {127, 0, 0, 1}));
  }

  @AfterAll
  static void stop() throws Exception {
    database.stop();
  }

  @BeforeEach
  void seed() throws Exception {
    execute("delete from schubert.app_logs");
    execute("delete from schubert.auth_sessions");
    execute("delete from schubert.app_users");
    execute(
        "insert into schubert.app_users(id,username,username_key,password_hash,role,status,password_changed_at,created_at,updated_at) "
            + "values(7,'logout-user','logout-user','unusable-fixture-hash','USER','ACTIVE','2026-09-08','2026-09-08','2026-09-08'),"
            + "(8,'admin-user','admin-user','unusable-fixture-hash','ADMIN','ACTIVE','2026-09-08','2026-09-08','2026-09-08'),"
            + "(9,'other-user','other-user','unusable-fixture-hash','USER','ACTIVE','2026-09-08','2026-09-08','2026-09-08')");
    session(1, 7, "a");
    session(2, 9, "b");
  }

  @Test
  void logoutAndRepeatedLogoutKeepOriginalTimeWithoutExtendingIdle() throws Exception {
    try (Connection connection = database.transaction()) {
      var first =
          service.logout(connection, RAW, client, MESSAGE, CORRELATION, NOW.plusNanos(123456789));
      assertEquals(new AuthContextIdentity(SESSION, 7), first.identity());
      assertEquals(NOW.plusNanos(123456000), first.revokedAt());
      assertEquals(ResultCode.SUCCESS, first.resultCode());
      assertEquals("RevokedContext[REDACTED]", first.toString());
      assertEquals(0, count("select count(*) from schubert.auth_sessions where revoked"));
      assertEquals(0, count("select count(*) from schubert.app_logs"));
      connection.rollback();
      service.logout(connection, RAW, client, MESSAGE, CORRELATION, NOW);
      connection.commit();
      assertFalse(connection.isClosed());
      assertFalse(connection.getAutoCommit());
      execute("update schubert.app_users set status='DISABLED' where id=7");
      var repeat =
          service.logout(
              connection, RAW, client, UUID.randomUUID(), CORRELATION, NOW.plusSeconds(86400));
      assertEquals(ResultCode.IDEMPOTENT_SUCCESS, repeat.resultCode());
      assertEquals(NOW, repeat.revokedAt());
      connection.commit();
    }
    assertEquals(
        1,
        count(
            "select count(*) from schubert.auth_sessions where user_id=7 and revoked_at='2026-09-08T01:00:00Z' and revoke_reason='LOGOUT' and last_accessed_at='2026-09-08T00:00:00Z' and expires_at='2026-09-08T08:00:00Z'"));
    assertEquals(
        1,
        count(
            "select count(*) from schubert.app_logs where details='{\"targetUserId\":7,\"reason\":\"LOGOUT\",\"resultCode\":\"0000\"}'::jsonb and message_id='"
                + MESSAGE
                + "' and correlation_id='"
                + CORRELATION
                + "' and actor_user_id=7"));
    assertEquals(
        1,
        count(
            "select count(*) from schubert.app_logs where details='{\"targetUserId\":7,\"reason\":\"LOGOUT\",\"resultCode\":\"0200\"}'::jsonb"));
    for (String condition :
        List.of(
            "expires_at='2026-09-08T01:00:00Z'",
            "expires_at='2026-09-08T00:59:59.999999Z'",
            "expires_at='2026-09-08T08:00:00Z'")) {
      seed();
      execute("update schubert.auth_sessions set " + condition + " where user_id=7");
      if (condition.contains("08:00:00"))
        execute("update schubert.app_users set status='DISABLED' where id=7");
      try (Connection connection = database.transaction()) {
        assertDenied(() -> service.logout(connection, RAW, client, MESSAGE, CORRELATION, NOW));
        assertDenied(
            () ->
                service.logout(
                    connection,
                    AuthenticationContext.of("f".repeat(64)),
                    client,
                    MESSAGE,
                    CORRELATION,
                    NOW));
        connection.rollback();
      }
      assertEquals(0, count("select count(*) from schubert.auth_sessions where revoked"));
      assertEquals(0, count("select count(*) from schubert.app_logs"));
    }
    seed();
    execute(
        "update schubert.auth_sessions set expires_at='2026-09-08T01:00:00.000001Z' where user_id=7");
    assertEquals(ResultCode.SUCCESS, logout(NOW).resultCode());
  }

  @Test
  void absentRequestIpIsNotReplacedByLoginAddress() throws Exception {
    try (Connection connection = database.transaction()) {
      service.logout(connection, RAW, Optional.empty(), MESSAGE, CORRELATION, NOW);
      connection.commit();
      assertEquals(1, count("select count(*) from schubert.app_logs where remote_address is null"));
      service.logout(connection, RAW, client, UUID.randomUUID(), CORRELATION, NOW.plusSeconds(1));
      connection.commit();
      assertEquals(
          1,
          count("select count(*) from schubert.app_logs where remote_address='127.0.0.1'::inet"));
      assertEquals(1, count("select count(*) from schubert.app_logs where remote_address is null"));
    }
    for (var reason :
        List.of(
            SessionRevocationReason.ADMIN,
            SessionRevocationReason.DISABLED,
            SessionRevocationReason.PASSWORD_RESET)) {
      seed();
      try (Connection connection = database.transaction()) {
        assertEquals(
            1,
            service.revokeAll(
                connection, ADMIN, 7, reason, Optional.empty(), MESSAGE, CORRELATION, NOW));
        connection.commit();
      }
      assertEquals(1, count("select count(*) from schubert.app_logs where remote_address is null"));
      assertEquals(
          1, count("select count(*) from schubert.auth_sessions where user_id=7 and revoked"));
      assertEquals(
          0, count("select count(*) from schubert.app_logs where remote_address is not null"));
    }
  }

  @Test
  void adminReasonsRevokeOnlyTargetAndPreserveExistingRevocations() throws Exception {
    for (var reason :
        List.of(
            SessionRevocationReason.DISABLED,
            SessionRevocationReason.PASSWORD_RESET,
            SessionRevocationReason.ADMIN)) {
      seed();
      session(3, 7, "c");
      session(4, 7, "d");
      execute(
          "update schubert.auth_sessions set expires_at='2026-09-08T00:59:00Z' where id='"
              + new UUID(0, 3)
              + "'");
      execute(
          "update schubert.auth_sessions set revoked=true,revoked_at='2026-09-08T00:30:00Z',revoke_reason='LOGOUT' where id='"
              + new UUID(0, 4)
              + "'");
      execute("update schubert.app_users set status='DISABLED' where id=7");
      try (Connection connection = database.transaction()) {
        assertEquals(2, revokeAll(connection, 7, reason));
        assertEquals(1, count("select count(*) from schubert.auth_sessions where revoked"));
        connection.rollback();
        assertEquals(2, revokeAll(connection, 7, reason));
        connection.commit();
        assertEquals(0, revokeAll(connection, 7, reason));
        connection.commit();
        assertEquals(0, revokeAll(connection, 8, reason));
        connection.rollback();
      }
      assertEquals(
          2,
          count(
              "select count(*) from schubert.auth_sessions where user_id=7 and revoke_reason='"
                  + reason
                  + "' and revoked_at='2026-09-08T01:00:00Z'"));
      assertEquals(
          1,
          count(
              "select count(*) from schubert.auth_sessions where user_id=7 and revoke_reason='LOGOUT' and revoked_at='2026-09-08T00:30:00Z'"));
      assertEquals(
          1, count("select count(*) from schubert.auth_sessions where user_id=9 and not revoked"));
      assertEquals(
          2,
          count(
              "select count(*) from schubert.app_logs where actor_user_id=8 and details='{\"targetUserId\":7,\"reason\":\""
                  + reason
                  + "\",\"resultCode\":\"0000\"}'::jsonb"));
    }
  }

  @Test
  void concurrentLogoutAndIssuanceSerializeWithoutLostRevocation() throws Exception {
    try (var executor = Executors.newFixedThreadPool(16)) {
      var results = new ArrayList<Future<RevokedContext>>();
      for (int i = 0; i < 100; i++) results.add(executor.submit(() -> logout(NOW)));
      int first = 0;
      for (var result : results) {
        var value = result.get();
        assertEquals(NOW, value.revokedAt());
        if (value.resultCode() == ResultCode.SUCCESS) first++;
        else assertEquals(ResultCode.IDEMPOTENT_SUCCESS, value.resultCode());
      }
      assertEquals(1, first);
      assertEquals(100, count("select count(*) from schubert.app_logs"));
      assertEquals(
          99, count("select count(*) from schubert.app_logs where details->>'resultCode'='0200'"));
      seed();
      try (var codec = new AuthContextCodec("v1", new byte[32], null, null)) {
        var issuer = new AuthSessionService(new ContextHash(), codec);
        var tasks = new ArrayList<Future<?>>();
        for (int i = 0; i < 20; i++) {
          tasks.add(executor.submit(() -> logout(NOW)));
          tasks.add(
              executor.submit(
                  () -> {
                    try (Connection connection = database.transaction()) {
                      issuer.issue(
                          connection, 7, client.orElseThrow(), UUID.randomUUID(), CORRELATION, NOW);
                      connection.commit();
                      return true;
                    }
                  }));
        }
        for (var task : tasks) assertNotNull(task.get());
      }
    }
    assertEquals(
        2, count("select count(*) from schubert.auth_sessions where user_id=7 and not revoked"));
    assertEquals(
        1,
        count(
            "select count(*) from schubert.auth_sessions where id='" + SESSION + "' and revoked"));
    assertEquals(
        1, count("select count(*) from schubert.auth_sessions where user_id=9 and not revoked"));
  }

  @Test
  void faultsNullRowsAndAuditFailuresRollbackWithoutLeakingData() throws Exception {
    for (String fault :
        List.of(
            "getAutoCommit",
            "prepareStatement",
            "setString",
            "executeQuery",
            "rowClose",
            "statementClose",
            "zeroUpdate",
            "updateAfter",
            "auditPrepare",
            "zeroAudit",
            "auditAfter",
            "auditClose",
            "null:id",
            "null:user_id",
            "null:revoked",
            "null:expires_at",
            "null:status",
            "badOwner")) {
      try (Connection connection = database.transaction()) {
        assertInfrastructure(
            () ->
                service.logout(
                    intercept(connection, fault), RAW, client, MESSAGE, CORRELATION, NOW));
        assertFalse(connection.isClosed());
        connection.rollback();
      }
      assertEquals(0, count("select count(*) from schubert.auth_sessions where revoked"));
      assertEquals(0, count("select count(*) from schubert.app_logs"));
    }
    execute(
        "update schubert.auth_sessions set revoked=true,revoked_at='2026-09-08T00:30:00Z',revoke_reason='ADMIN' where user_id=7");
    try (Connection connection = database.transaction()) {
      assertInfrastructure(
          () ->
              service.logout(
                  intercept(connection, "null:revoked_at"),
                  RAW,
                  client,
                  MESSAGE,
                  CORRELATION,
                  NOW));
      connection.rollback();
      for (String fault : List.of("auditPrepare", "zeroAudit", "auditAfter", "auditClose")) {
        assertInfrastructure(
            () ->
                service.logout(
                    intercept(connection, fault), RAW, client, MESSAGE, CORRELATION, NOW));
        connection.rollback();
      }
    }
    seed();
    for (String fault :
        List.of(
            "getAutoCommit",
            "prepareStatement",
            "setLong",
            "executeQuery",
            "rowClose",
            "statementClose",
            "zeroUpdate",
            "updateAfter",
            "auditPrepare",
            "zeroAudit",
            "auditAfter",
            "auditClose",
            "null:id")) {
      try (Connection connection = database.transaction()) {
        assertInfrastructure(
            () -> revokeAll(intercept(connection, fault), 7, SessionRevocationReason.ADMIN));
        connection.rollback();
      }
      assertEquals(0, count("select count(*) from schubert.auth_sessions where revoked"));
      assertEquals(0, count("select count(*) from schubert.app_logs"));
    }
    try (Connection connection = database.transaction()) {
      assertDenied(
          () ->
              service.logout(
                  intercept(connection, "missingSession"), RAW, client, MESSAGE, CORRELATION, NOW));
      assertInfrastructure(
          () ->
              service.logout(
                  intercept(connection, "rowClose"),
                  AuthenticationContext.of("f".repeat(64)),
                  client,
                  MESSAGE,
                  CORRELATION,
                  NOW));
      var absent =
          assertThrows(
              AuthorizationException.class,
              () -> revokeAll(connection, 99, SessionRevocationReason.ADMIN));
      assertEquals(ResultCode.NOT_FOUND, absent.resultCode());
      assertNull(absent.getCause());
      assertEquals(0, absent.getSuppressed().length);
      assertInfrastructure(
          () -> revokeAll(intercept(connection, "rowClose"), 99, SessionRevocationReason.ADMIN));
      assertThrows(NullPointerException.class, () -> new AuthSessionRevocationService(null));
      for (var operation :
          List.<org.junit.jupiter.api.function.Executable>of(
              () -> service.logout(null, RAW, client, MESSAGE, CORRELATION, NOW),
              () -> service.logout(connection, null, client, MESSAGE, CORRELATION, NOW),
              () -> service.logout(connection, RAW, null, MESSAGE, CORRELATION, NOW),
              () -> service.logout(connection, RAW, client, null, CORRELATION, NOW),
              () -> service.logout(connection, RAW, client, MESSAGE, null, NOW),
              () -> service.logout(connection, RAW, client, MESSAGE, CORRELATION, null),
              () ->
                  service.revokeAll(
                      connection,
                      null,
                      7,
                      SessionRevocationReason.ADMIN,
                      client,
                      MESSAGE,
                      CORRELATION,
                      NOW),
              () -> revokeAll(connection, 7, null)))
        assertThrows(NullPointerException.class, operation);
      for (long id : new long[] {0, -1, 1_000_000_000_000L})
        assertThrows(
            IllegalArgumentException.class,
            () -> revokeAll(connection, id, SessionRevocationReason.ADMIN));
      for (long id : new long[] {1, 999_999_999_999L})
        assertThrows(
            AuthorizationException.class,
            () -> revokeAll(connection, id, SessionRevocationReason.ADMIN));
      for (var reason :
          List.of(
              SessionRevocationReason.LOGOUT,
              SessionRevocationReason.REPLACED,
              SessionRevocationReason.EXPIRED))
        assertThrows(IllegalArgumentException.class, () -> revokeAll(connection, 7, reason));
      var denied =
          assertThrows(
              AuthorizationException.class,
              () ->
                  service.revokeAll(
                      connection,
                      new AuthenticatedActor(7, "logout-user", Role.USER),
                      9,
                      SessionRevocationReason.ADMIN,
                      client,
                      MESSAGE,
                      CORRELATION,
                      NOW));
      assertEquals(ResultCode.FORBIDDEN, denied.resultCode());
      connection.rollback();
    }
    try (Connection connection = database.api()) {
      assertInfrastructure(
          () -> service.logout(connection, RAW, client, MESSAGE, CORRELATION, NOW));
      assertInfrastructure(() -> revokeAll(connection, 7, SessionRevocationReason.ADMIN));
    }
    var identity = new AuthContextIdentity(SESSION, 7);
    assertThrows(
        NullPointerException.class, () -> new RevokedContext(null, NOW, ResultCode.SUCCESS));
    assertThrows(
        NullPointerException.class, () -> new RevokedContext(identity, null, ResultCode.SUCCESS));
    assertThrows(NullPointerException.class, () -> new RevokedContext(identity, NOW, null));
    assertThrows(
        IllegalArgumentException.class,
        () -> new RevokedContext(identity, NOW, ResultCode.AUTHENTICATION_FAILED));
  }

  private static int revokeAll(Connection connection, long target, SessionRevocationReason reason) {
    return service.revokeAll(connection, ADMIN, target, reason, client, MESSAGE, CORRELATION, NOW);
  }

  private static RevokedContext logout(Instant now) throws Exception {
    try (Connection connection = database.transaction()) {
      var result = service.logout(connection, RAW, client, UUID.randomUUID(), CORRELATION, now);
      connection.commit();
      return result;
    }
  }

  private static void session(long id, long user, String character) throws Exception {
    String hash =
        HexFormat.of()
            .formatHex(
                MessageDigest.getInstance("SHA-256")
                    .digest(character.repeat(64).getBytes(StandardCharsets.US_ASCII)));
    execute(
        "insert into schubert.auth_sessions(id,user_id,context_hash,context_ciphertext,key_version,issued_at,last_accessed_at,expires_at,client_address,created_message_id) values('"
            + new UUID(0, id)
            + "',"
            + user
            + ",'"
            + hash
            + "',decode(repeat('00',29),'hex'),'fixture','2026-09-08T00:00:00Z','2026-09-08T00:00:00Z','2026-09-08T08:00:00Z','127.0.0.1','"
            + new UUID(1, id)
            + "')");
  }

  private static void execute(String sql) throws SQLException {
    try (Connection connection = database.api();
        var statement = connection.createStatement()) {
      statement.executeUpdate(sql);
    }
  }

  private static int count(String sql) throws SQLException {
    try (Connection connection = database.api();
        var statement = connection.createStatement();
        var row = statement.executeQuery(sql)) {
      assertTrue(row.next());
      return row.getInt(1);
    }
  }

  private static void assertDenied(org.junit.jupiter.api.function.Executable operation) {
    var failure = assertThrows(AuthenticationContextException.class, operation);
    assertEquals("authentication context is not valid", failure.getMessage());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
  }

  private static void assertInfrastructure(org.junit.jupiter.api.function.Executable operation) {
    var failure = assertThrows(AuthenticationInfrastructureException.class, operation);
    assertEquals("authentication storage is unavailable", failure.getMessage());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
  }

  private static Connection intercept(Connection real, String fault) {
    int[] stage = {0};
    return (Connection)
        Proxy.newProxyInstance(
            Connection.class.getClassLoader(),
            new Class<?>[] {Connection.class},
            (proxy, method, args) -> {
              if (method.getName().equals(fault))
                throw new SQLException("synthetic-sensitive-provider-text");
              boolean prepare = method.getName().equals("prepareStatement");
              boolean audit =
                  prepare && ((String) args[0]).startsWith("insert into schubert.app_logs");
              if (audit && fault.equals("auditPrepare"))
                throw new SQLException("synthetic-sensitive-audit");
              Object result = invoke(real, method, args);
              if (!prepare) return result;
              int step = ++stage[0];
              return Proxy.newProxyInstance(
                  PreparedStatement.class.getClassLoader(),
                  new Class<?>[] {PreparedStatement.class},
                  (sp, sm, sa) -> {
                    if (sm.getName().equals(fault))
                      throw new SQLException("synthetic-sensitive-statement");
                    if (sm.getName().equals("executeUpdate")
                        && ((!audit && fault.equals("zeroUpdate"))
                            || (audit && fault.equals("zeroAudit")))) return 0;
                    Object sr = invoke(result, sm, sa);
                    if (sm.getName().equals("executeUpdate")
                        && ((!audit && fault.equals("updateAfter"))
                            || (audit && fault.equals("auditAfter"))))
                      throw new SQLException("synthetic-sensitive-after");
                    if (sm.getName().equals("close")
                        && (fault.equals("statementClose")
                            || (audit && fault.equals("auditClose"))))
                      throw new SQLException("synthetic-sensitive-close");
                    if (!sm.getName().equals("executeQuery")) return sr;
                    return Proxy.newProxyInstance(
                        ResultSet.class.getClassLoader(),
                        new Class<?>[] {ResultSet.class},
                        (rp, rm, ra) -> {
                          if (step == 2
                              && rm.getName().equals("next")
                              && fault.equals("missingSession")) return false;
                          if (step == 2
                              && rm.getName().startsWith("get")
                              && ra != null
                              && ra[0] instanceof String field) {
                            if (fault.equals("null:" + field)) return null;
                            if (fault.equals("badOwner") && field.equals("user_id")) return 0L;
                          }
                          Object rr = invoke(sr, rm, ra);
                          if (rm.getName().equals("close") && fault.equals("rowClose"))
                            throw new SQLException("synthetic-sensitive-row-close");
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
