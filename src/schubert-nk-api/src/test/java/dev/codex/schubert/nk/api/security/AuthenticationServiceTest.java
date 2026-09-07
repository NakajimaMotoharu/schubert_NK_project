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
import java.nio.file.Path;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.SQLException;
import java.time.Instant;
import java.util.ArrayList;
import java.util.HexFormat;
import java.util.List;
import java.util.UUID;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.function.BiPredicate;
import javax.crypto.SecretKeyFactory;
import javax.crypto.spec.PBEKeySpec;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** PT-AUT-004-01..06: production PBKDF2/JDBC/session/audit, independent hash and SQL oracle. */
final class AuthenticationServiceTest {
  @TempDir static Path root;
  private static ApiLogDatabaseFixture database;
  private static AuthContextCodec codec;
  private static AuthSessionService sessions;
  private static ContextHash hashes;
  private static InetAddress client;
  private static String fixtureHash;
  private static final Instant NOW = Instant.parse("2026-09-08T00:00:00Z");
  private final LoginAttemptRepository attempts = new LoginAttemptRepository();
  private final PasswordHasher hasher = new PasswordHasher();
  private final LoginAuditWriter audit = new LoginAuditWriter();

  @BeforeAll
  static void start() throws Exception {
    database = new ApiLogDatabaseFixture(root);
    codec = new AuthContextCodec("v1", new byte[32], null, null);
    hashes = new ContextHash();
    sessions = new AuthSessionService(hashes, codec);
    client = InetAddress.ofLiteral("127.0.0.1");
    // Synthetic fixture: independent JCA, not PasswordHasher.encode, never an actual credential.
    byte[] salt = new byte[16];
    java.util.Arrays.fill(salt, (byte) 17);
    var spec = new PBEKeySpec("synthetic-password".toCharArray(), salt, 310000, 256);
    try {
      fixtureHash =
          "{pbkdf2-v1}"
              + HexFormat.of().formatHex(salt)
              + HexFormat.of()
                  .formatHex(
                      SecretKeyFactory.getInstance("PBKDF2WithHmacSHA256")
                          .generateSecret(spec)
                          .getEncoded());
    } finally {
      spec.clearPassword();
    }
  }

  @AfterAll
  static void stop() throws Exception {
    codec.close();
    database.stop();
  }

  @BeforeEach
  void seed() throws SQLException {
    execute("delete from schubert.app_logs");
    execute("delete from schubert.auth_sessions");
    execute("delete from schubert.login_ip_attempts");
    execute("delete from schubert.app_users");
    try (Connection connection = database.api();
        var statement =
            connection.prepareStatement(
                "insert into"
                    + " schubert.app_users(id,username,username_key,password_hash,role,status,password_changed_at,created_at,updated_at)"
                    + " values(7,'Login-User','login-user',?,'USER','ACTIVE','2026-09-08','2026-09-08','2026-09-08')")) {
      statement.setString(1, fixtureHash);
      statement.executeUpdate();
    }
  }

  @Test
  void realPasswordSuccessClearsCountersIssuesContextAndAuditsAtomically() throws Exception {
    var service = realService();
    execute(
        "update schubert.app_users set"
            + " role='ADMIN',failed_count=2,failure_window_started_at='2026-09-07T23:59:00Z' where"
            + " id=7");
    execute(
        "insert into"
            + " schubert.login_ip_attempts(client_address,failed_count,window_started_at,updated_at)"
            + " values('127.0.0.1',2,'2026-09-07T23:59:00Z','2026-09-07T23:59:00Z')");
    UUID message = UUID.randomUUID(), correlation = UUID.randomUUID();
    try (Connection connection = database.transaction()) {
      char[] password = password();
      var accepted =
          assertInstanceOf(
              LoginResult.Success.class,
              service.authenticate(
                  connection, "login-user", password, client, message, correlation, NOW));
      assertArrayEquals(new char[password.length], password);
      assertEquals(ResultCode.SUCCESS, accepted.resultCode());
      assertEquals(0, accepted.retryAfterSeconds());
      assertEquals(new AuthenticatedActor(7, "Login-User", Role.ADMIN), accepted.actor());
      assertEquals(7, accepted.issued().identity().userId());
      assertEquals(NOW, accepted.issued().issuedAt());
      assertEquals(Instant.parse("2026-09-08T08:00:00Z"), accepted.issued().expiresAt());
      assertEquals("LoginSuccess[REDACTED]", accepted.toString());
      assertEquals(0, scalar("select count(*) from schubert.auth_sessions"));
      assertEquals(0, scalar("select count(*) from schubert.app_logs"));
      assertEquals(2, scalar("select failed_count from schubert.app_users"));
      connection.rollback();
      service.authenticate(connection, "login-user", password(), client, message, correlation, NOW);
      connection.commit();
      assertFalse(connection.isClosed());
    }
    assertEquals(1, scalar("select count(*) from schubert.auth_sessions where not revoked"));
    assertEquals(
        1,
        scalar(
            "select count(*) from schubert.app_users where failed_count=0 and"
                + " failure_window_started_at is null and locked_until is null and"
                + " last_login_at='2026-09-08T00:00:00Z'"));
    assertEquals(
        1,
        scalar(
            "select count(*) from schubert.login_ip_attempts where failed_count=0 and locked_until"
                + " is null and window_started_at='2026-09-08T00:00:00Z'"));
    assertEquals(
        1,
        scalar(
            "select count(*) from schubert.app_logs where service='API' and category='SECURITY' and"
                + " level='INFO' and action='LOGIN_SUCCEEDED' and message='LOGIN_SUCCEEDED' and"
                + " actor_user_id=7 and actor_username='login-user' and remote_address='127.0.0.1'"
                + " and request_id is null and source_message_id is null and details='{"
                + "\"resultCode\":\"0000\",\"reason\":\"SUCCEEDED\",\"retryAfterSeconds\":0,\"outcome\":\"SUCCESS\"}'::jsonb"));
    try (Connection connection = database.api();
        var statement = connection.createStatement();
        var row =
            statement.executeQuery("select message_id,correlation_id from schubert.app_logs")) {
      assertTrue(row.next());
      assertEquals(message, row.getObject(1, UUID.class));
      assertEquals(correlation, row.getObject(2, UUID.class));
    }
  }

  @Test
  void absentDisabledAndWrongPasswordHaveSameFailureShapeAndDummyWork() throws Exception {
    var seenHashes = new ArrayList<String>();
    var service =
        checked(
            (raw, stored) -> {
              seenHashes.add(stored);
              return hasher.matches(raw, stored);
            });
    for (String condition : List.of("absent", "disabled", "wrong")) {
      seed();
      seenHashes.clear();
      if (condition.equals("disabled")) execute("update schubert.app_users set status='DISABLED'");
      char[] raw = condition.equals("wrong") ? "synthetic-wrong".toCharArray() : password();
      var failure =
          assertInstanceOf(
              LoginResult.Failure.class,
              call(service, condition.equals("absent") ? "unknown" : "login-user", raw, NOW));
      assertEquals(new LoginResult.Failure(ResultCode.AUTHENTICATION_FAILED, 0), failure);
      assertEquals("LoginFailure[code=0101, retryAfterSeconds=0]", failure.toString());
      assertArrayEquals(new char[raw.length], raw);
      assertEquals(1, seenHashes.size());
      if (condition.equals("wrong")) assertEquals(fixtureHash, seenHashes.getFirst());
      else assertEquals("{pbkdf2-v1}" + "0".repeat(96), seenHashes.getFirst());
      assertEquals(0, scalar("select count(*) from schubert.auth_sessions"));
      assertEquals(1, scalar("select failed_count from schubert.login_ip_attempts"));
      assertEquals(
          condition.equals("absent") ? 0 : 1,
          scalar("select failed_count from schubert.app_users"));
      assertEquals(
          1,
          scalar(
              "select count(*) from schubert.app_logs where action='LOGIN_FAILED' and level='WARN'"
                  + " and actor_user_id is null and details->>'resultCode'='0101' and"
                  + " details->>'outcome'='DENIED'"));
    }
    seed();
    var alwaysTrue = checked((raw, stored) -> true);
    assertEquals(
        ResultCode.AUTHENTICATION_FAILED,
        call(alwaysTrue, "unknown", password(), NOW).resultCode());
    execute("update schubert.app_users set status='DISABLED'");
    assertEquals(
        ResultCode.AUTHENTICATION_FAILED,
        call(alwaysTrue, "login-user", password(), NOW).resultCode());
    assertEquals(0, scalar("select count(*) from schubert.auth_sessions"));
  }

  @Test
  void thresholdRequestLocksImmediatelyAndLockedRequestsDoNotHashOrExtend() throws Exception {
    var calls = new AtomicInteger();
    var service =
        checked(
            (raw, stored) -> {
              calls.incrementAndGet();
              return false;
            });
    for (int i = 1; i <= 5; i++) {
      var result = call(service, "login-user", password(), NOW);
      assertEquals(
          i == 5 ? ResultCode.LOCKED : ResultCode.AUTHENTICATION_FAILED, result.resultCode());
      assertEquals(i == 5 ? 900 : 0, result.retryAfterSeconds());
    }
    assertEquals(5, calls.get());
    assertEquals(1, scalar("select count(*) from schubert.app_logs where action='LOGIN_LOCKED'"));
    execute("update schubert.app_users set password_hash='unsupported-fixture-hash'");
    char[] lockedPassword = password();
    assertEquals(
        new LoginResult.Failure(ResultCode.LOCKED, 870),
        call(service, "login-user", lockedPassword, NOW.plusSeconds(30)));
    assertArrayEquals(new char[lockedPassword.length], lockedPassword);
    assertEquals(5, calls.get());
    assertEquals(5, scalar("select failed_count from schubert.app_users"));
    assertEquals(5, scalar("select failed_count from schubert.login_ip_attempts"));
    assertEquals(
        1,
        scalar(
            "select count(*) from schubert.app_users where locked_until='2026-09-08T00:15:00Z'"));
    seed();
    calls.set(0);
    for (int i = 1; i <= 10; i++)
      assertEquals(
          i == 10 ? ResultCode.LOCKED : ResultCode.AUTHENTICATION_FAILED,
          call(service, "unknown", password(), NOW).resultCode());
    assertEquals(10, calls.get());
    assertEquals(
        new LoginResult.Failure(ResultCode.LOCKED, 900), call(service, "unknown", password(), NOW));
    assertEquals(10, calls.get());
    assertEquals(0, scalar("select failed_count from schubert.app_users"));
    // Two locks: select the later deadline, then ceil fractional microsecond and cap at 900.
    execute(
        "update schubert.app_users set"
            + " failed_count=5,failure_window_started_at='2026-09-08T00:00:00Z',locked_until='2026-09-08T00:20:00Z'");
    assertEquals(900, call(service, "login-user", password(), NOW).retryAfterSeconds());
    execute("update schubert.app_users set locked_until='2026-09-08T00:00:01.000001Z'");
    execute("update schubert.login_ip_attempts set locked_until='2026-09-08T00:00:01Z'");
    assertEquals(2, call(service, "login-user", password(), NOW).retryAfterSeconds());
    // At strict lock expiry, hashing resumes. At the inclusive failure-window endpoint it relocks.
    assertEquals(
        ResultCode.LOCKED,
        call(service, "login-user", password(), NOW.plusSeconds(900)).resultCode());
    assertEquals(11, calls.get());
  }

  @Test
  void sessionOrAuditFaultRollsBackSuccessAndFailureWithoutLeakingInput() throws Exception {
    var service = realService();
    for (String fault : List.of("auditPrepare", "auditZero", "auditAfter", "auditClose")) {
      for (boolean accepted : new boolean[] {true, false}) {
        seed();
        try (Connection connection = database.transaction()) {
          char[] raw = accepted ? password() : "synthetic-wrong".toCharArray();
          assertInfrastructure(
              () ->
                  service.authenticate(
                      intercept(connection, fault),
                      "login-user",
                      raw,
                      client,
                      UUID.randomUUID(),
                      UUID.randomUUID(),
                      NOW));
          assertArrayEquals(new char[raw.length], raw);
          assertFalse(connection.isClosed());
          connection.rollback();
        }
        assertEmptyTransactionEffects();
      }
    }
    for (String fault : List.of("sessionInsert", "sessionAfter", "getAutoCommit")) {
      seed();
      try (Connection connection = database.transaction()) {
        char[] raw = password();
        assertInfrastructure(
            () ->
                service.authenticate(
                    intercept(connection, fault),
                    "login-user",
                    raw,
                    client,
                    UUID.randomUUID(),
                    UUID.randomUUID(),
                    NOW));
        assertArrayEquals(new char[raw.length], raw);
        connection.rollback();
      }
      assertEmptyTransactionEffects();
    }
    var closed = new AuthContextCodec("v1", new byte[32], null, null);
    closed.close();
    var unavailable =
        new AuthenticationService(attempts, hasher, new AuthSessionService(hashes, closed), audit);
    try (Connection connection = database.transaction()) {
      char[] raw = password();
      assertInfrastructure(
          () ->
              unavailable.authenticate(
                  connection,
                  "login-user",
                  raw,
                  client,
                  UUID.randomUUID(),
                  UUID.randomUUID(),
                  NOW));
      assertArrayEquals(new char[raw.length], raw);
      connection.rollback();
    }
    assertEmptyTransactionEffects();
    // Error type is bounded even when a dependency carries synthetic sensitive diagnostics.
    for (RuntimeException error :
        List.of(
            new IllegalArgumentException("synthetic-sensitive"),
            new AuthContextCryptoException(AuthContextCryptoException.Reason.CRYPTO_UNAVAILABLE))) {
      try (Connection connection = database.transaction()) {
        char[] raw = password();
        assertInfrastructure(
            () ->
                checked(
                        (p, h) -> {
                          throw error;
                        })
                    .authenticate(
                        connection,
                        "login-user",
                        raw,
                        client,
                        UUID.randomUUID(),
                        UUID.randomUUID(),
                        NOW));
        assertArrayEquals(new char[raw.length], raw);
        connection.rollback();
      }
      assertEmptyTransactionEffects();
    }
  }

  @Test
  void threeSuccessfulLoginsAndConcurrentAttemptsKeepDatabaseInvariants() throws Exception {
    var service = realService();
    var first =
        assertInstanceOf(LoginResult.Success.class, call(service, "login-user", password(), NOW));
    call(service, "login-user", password(), NOW.plusSeconds(1));
    call(service, "login-user", password(), NOW.plusSeconds(2));
    assertEquals(2, scalar("select count(*) from schubert.auth_sessions where not revoked"));
    assertEquals(
        1,
        scalar(
            "select count(*) from schubert.auth_sessions where id='"
                + first.issued().identity().sessionId()
                + "' and revoked and revoke_reason='REPLACED'"));
    assertEquals(
        3, scalar("select count(*) from schubert.app_logs where action='LOGIN_SUCCEEDED'"));
    seed();
    try (var executor = Executors.newFixedThreadPool(8)) {
      var successes = new ArrayList<Future<LoginResult>>();
      for (int i = 0; i < 12; i++)
        successes.add(executor.submit(() -> call(service, "login-user", password(), NOW)));
      for (var result : successes) assertEquals(ResultCode.SUCCESS, result.get().resultCode());
      assertEquals(12, scalar("select count(*) from schubert.auth_sessions"));
      assertEquals(2, scalar("select count(*) from schubert.auth_sessions where not revoked"));
      assertEquals(
          12, scalar("select count(*) from schubert.app_logs where action='LOGIN_SUCCEEDED'"));
      var failures = new ArrayList<Future<LoginResult>>();
      for (int i = 0; i < 20; i++)
        failures.add(
            executor.submit(
                () -> call(service, "login-user", "synthetic-wrong".toCharArray(), NOW)));
      int invalid = 0, locked = 0;
      for (var result : failures) {
        if (result.get().resultCode() == ResultCode.AUTHENTICATION_FAILED) invalid++;
        else if (result.get().resultCode() == ResultCode.LOCKED) locked++;
        else fail("unexpected Login outcome");
      }
      assertEquals(4, invalid);
      assertEquals(16, locked);
    }
    assertEquals(5, scalar("select failed_count from schubert.app_users"));
    assertEquals(5, scalar("select failed_count from schubert.login_ip_attempts"));
    assertEquals(32, scalar("select count(*) from schubert.app_logs where action like 'LOGIN_%'"));
    assertEquals(
        10, scalar("select count(*) from schubert.app_logs where action='SESSION_REVOKED'"));
    assertEquals(12, scalar("select count(*) from schubert.auth_sessions"));
  }

  @Test
  void nullInvalidInputsAndOutcomeInvariantsAreRejectedAndConsumed() throws Exception {
    assertThrows(
        NullPointerException.class, () -> new AuthenticationService(null, hasher, sessions, audit));
    assertThrows(
        NullPointerException.class,
        () -> new AuthenticationService(attempts, (PasswordHasher) null, sessions, audit));
    assertThrows(
        NullPointerException.class,
        () ->
            new AuthenticationService(
                attempts, (BiPredicate<char[], String>) null, sessions, audit));
    assertThrows(
        NullPointerException.class, () -> new AuthenticationService(attempts, hasher, null, audit));
    assertThrows(
        NullPointerException.class,
        () -> new AuthenticationService(attempts, hasher, sessions, null));
    var service = realService();
    try (Connection connection = database.transaction()) {
      for (int input = 0; input < 6; input++) {
        int index = input;
        char[] raw = password();
        assertThrows(
            NullPointerException.class,
            () ->
                service.authenticate(
                    index == 0 ? null : connection,
                    index == 1 ? null : "login-user",
                    raw,
                    index == 2 ? null : client,
                    index == 3 ? null : UUID.randomUUID(),
                    index == 4 ? null : UUID.randomUUID(),
                    index == 5 ? null : NOW));
        assertArrayEquals(new char[raw.length], raw);
      }
      assertThrows(
          NullPointerException.class,
          () ->
              service.authenticate(
                  connection,
                  "login-user",
                  null,
                  client,
                  UUID.randomUUID(),
                  UUID.randomUUID(),
                  NOW));
      execute("update schubert.app_users set password_hash='unsupported-fixture-hash'");
      char[] raw = password();
      assertInfrastructure(
          () ->
              service.authenticate(
                  connection,
                  "login-user",
                  raw,
                  client,
                  UUID.randomUUID(),
                  UUID.randomUUID(),
                  NOW));
      assertArrayEquals(new char[raw.length], raw);
      connection.rollback();
    }
    assertEmptyTransactionEffects();
    assertThrows(NullPointerException.class, () -> new LoginResult.Failure(null, 0));
    for (ResultCode code : ResultCode.values()) {
      if (code != ResultCode.AUTHENTICATION_FAILED && code != ResultCode.LOCKED)
        assertThrows(IllegalArgumentException.class, () -> new LoginResult.Failure(code, 0));
    }
    assertThrows(
        IllegalArgumentException.class,
        () -> new LoginResult.Failure(ResultCode.AUTHENTICATION_FAILED, 1));
    for (int retry : new int[] {-1, 0, 901})
      assertThrows(
          IllegalArgumentException.class, () -> new LoginResult.Failure(ResultCode.LOCKED, retry));
    assertEquals(1, new LoginResult.Failure(ResultCode.LOCKED, 1).retryAfterSeconds());
    assertEquals(900, new LoginResult.Failure(ResultCode.LOCKED, 900).retryAfterSeconds());
    var actor = new AuthenticatedActor(7, "user", Role.USER);
    var issued =
        new IssuedContext(
            new AuthContextIdentity(UUID.randomUUID(), 8),
            AuthenticationContext.of("a".repeat(64)),
            NOW,
            NOW.plusSeconds(1));
    assertThrows(NullPointerException.class, () -> new LoginResult.Success(null, issued));
    assertThrows(NullPointerException.class, () -> new LoginResult.Success(actor, null));
    assertThrows(IllegalArgumentException.class, () -> new LoginResult.Success(actor, issued));
  }

  private AuthenticationService realService() {
    return new AuthenticationService(attempts, hasher, sessions, audit);
  }

  private AuthenticationService checked(BiPredicate<char[], String> check) {
    return new AuthenticationService(attempts, check, sessions, audit);
  }

  private static char[] password() {
    return "synthetic-password".toCharArray();
  }

  private static LoginResult call(
      AuthenticationService service, String name, char[] raw, Instant now) throws SQLException {
    try (Connection connection = database.transaction()) {
      var result =
          service.authenticate(
              connection, name, raw, client, UUID.randomUUID(), UUID.randomUUID(), now);
      connection.commit();
      return result;
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

  private static void assertEmptyTransactionEffects() throws SQLException {
    assertEquals(0, scalar("select failed_count from schubert.app_users"));
    assertEquals(0, scalar("select count(*) from schubert.login_ip_attempts"));
    assertEquals(0, scalar("select count(*) from schubert.auth_sessions"));
    assertEquals(0, scalar("select count(*) from schubert.app_logs"));
  }

  private static void assertInfrastructure(org.junit.jupiter.api.function.Executable operation) {
    var error = assertThrows(AuthenticationInfrastructureException.class, operation);
    assertEquals("authentication storage is unavailable", error.getMessage());
    assertNull(error.getCause());
    assertEquals(0, error.getSuppressed().length);
  }

  private static Connection intercept(Connection real, String fault) {
    return (Connection)
        Proxy.newProxyInstance(
            Connection.class.getClassLoader(),
            new Class<?>[] {Connection.class},
            (proxy, method, args) -> {
              if (method.getName().equals(fault))
                throw new SQLException("synthetic-sensitive-provider");
              if (method.getName().equals("prepareStatement")
                  && ((String) args[0]).startsWith("insert into schubert.app_logs")
                  && fault.equals("auditPrepare"))
                throw new SQLException("synthetic-sensitive-audit");
              Object result = invoke(real, method, args);
              if (!method.getName().equals("prepareStatement")) return result;
              boolean audit = ((String) args[0]).startsWith("insert into schubert.app_logs");
              boolean session = ((String) args[0]).startsWith("insert into schubert.auth_sessions");
              return Proxy.newProxyInstance(
                  PreparedStatement.class.getClassLoader(),
                  new Class<?>[] {PreparedStatement.class},
                  (sp, sm, sa) -> {
                    if (sm.getName().equals("executeUpdate")
                        && session
                        && fault.equals("sessionInsert"))
                      throw new SQLException("synthetic-sensitive-session");
                    if (sm.getName().equals("executeUpdate") && audit && fault.equals("auditZero"))
                      return 0;
                    Object sr = invoke(result, sm, sa);
                    if (sm.getName().equals("executeUpdate")
                        && ((audit && fault.equals("auditAfter"))
                            || (session && fault.equals("sessionAfter"))))
                      throw new SQLException("synthetic-sensitive-after-write");
                    if (sm.getName().equals("close") && audit && fault.equals("auditClose"))
                      throw new SQLException("synthetic-sensitive-close");
                    return sr;
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
