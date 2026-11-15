package dev.codex.schubert.nk.api.security;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNotSame;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import dev.codex.schubert.nk.api.domain.Role;
import dev.codex.schubert.nk.protocol.header.ResultCode;
import java.lang.reflect.Proxy;
import java.net.InetAddress;
import java.security.SecureRandom;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.time.Instant;
import java.time.ZoneOffset;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.function.BiPredicate;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Timeout;

/**
 * NK-AUT-001; AUT001..004/MON004; UI226/234; SS314/332/351; PT-AUT-MEMPORT001..016. Existing
 * checker/JDBC ports, own in-memory rows and unissued synthetic crypto only. No original DB
 * fixture/helper, socket, driver, server, actual login/session or key file.
 */
@Timeout(value = 30, threadMode = Timeout.ThreadMode.SEPARATE_THREAD)
final class AuthenticationServiceMemoryPortTest {
  private static final String DISABLED_STATUS = "DISABLED";
  private static final String ACTIVE_STATUS = "ACTIVE";
  private static final String FAILED_COUNT_COLUMN = "failed_count";

  private static final Instant NOW = Instant.parse("2026-09-08T00:00:00.123456789Z");
  private static final Instant AT = Instant.parse("2026-09-08T00:00:00.123456Z");
  private static final Instant EXPIRES = Instant.parse("2026-09-08T08:00:00.123456Z");
  private static final UUID MESSAGE = new UUID(0, 11);
  private static final UUID CORRELATION = new UUID(0, 12);
  private static final InetAddress CLIENT = InetAddress.ofLiteral("192.0.2.10");
  private static final String DISPLAY = "ÅLICE";
  private static final String KEY = "ålice";
  private static final String STORED_HASH = "{pbkdf2-v1}" + "1".repeat(96);
  private static final String DUMMY_HASH = "{pbkdf2-v1}" + "0".repeat(96);
  private static final String STORAGE_ERROR = "authentication storage is unavailable";
  private static final String DENIED = "DENIED";
  private static final String REASON_KEY = "reason";
  private static final String RESULT_CODE_KEY = "resultCode";
  private static final String SYNTHETIC_FAULT = "own synthetic provider detail";

  @Test
  void memory001ConstructorsRejectMissingDependenciesAndDefaultCheckerIsConstructionOnly()
      throws Exception {
    try (Fixture f = new Fixture()) {
      PasswordHasher defaultChecker = new PasswordHasher();
      AuthenticationService defaultService =
          new AuthenticationService(f.attempts, defaultChecker, f.sessions, f.audit);
      assertThrows(
          NullPointerException.class,
          () -> new AuthenticationService(f.attempts, (PasswordHasher) null, f.sessions, f.audit));
      assertThrows(
          NullPointerException.class,
          () -> new AuthenticationService(null, f.checker(), f.sessions, f.audit));
      assertThrows(
          NullPointerException.class,
          () ->
              new AuthenticationService(
                  f.attempts, (BiPredicate<char[], String>) null, f.sessions, f.audit));
      assertThrows(
          NullPointerException.class,
          () -> new AuthenticationService(f.attempts, f.checker(), null, f.audit));
      assertThrows(
          NullPointerException.class,
          () -> new AuthenticationService(f.attempts, f.checker(), f.sessions, null));
      assertTrue(f.statements.isEmpty());
      f.userFailures = 5;
      f.userLock = Optional.of(AT.plusSeconds(30));
      assertEquals(ResultCode.LOCKED, f.call(defaultService).resultCode());
      assertEquals(0, f.count(Stage.SESSION_INSERT));
      assertEquals(0, f.checked.get());
      f.verifyReleasedAndConsumed();
    }
  }

  @Test
  void memory002UserSuccessPreservesNormalizedDisplayAndBorrowedTransaction() throws Exception {
    try (Fixture f = new Fixture()) {
      f.userFailures = 3;
      f.ipFailures = 2;
      LoginResult.Success result = assertInstanceOf(LoginResult.Success.class, f.call());
      assertEquals(7, result.actor().userId());
      assertEquals("Ålice", result.actor().username());
      assertEquals(Role.USER, result.actor().role());
      assertEquals(ResultCode.SUCCESS, result.resultCode());
      assertEquals(0, result.retryAfterSeconds());
      assertEquals(AT, result.issued().issuedAt());
      assertEquals(EXPIRES, result.issued().expiresAt());
      assertEquals(KEY, f.param(Stage.USER, 1));
      assertEquals(0, f.param(Stage.UPDATE_USER, 1));
      assertNull(f.param(Stage.UPDATE_USER, 2));
      assertNull(f.param(Stage.UPDATE_USER, 3));
      assertEquals(true, f.param(Stage.UPDATE_USER, 4));
      assertEquals(0, f.param(Stage.UPDATE_IP, 1));
      assertEquals(AT.atOffset(ZoneOffset.UTC), f.param(Stage.UPDATE_IP, 2));
      assertEquals(List.of(Stage.USER, Stage.CREATE_IP, Stage.IP), f.stages().subList(0, 3));
      assertEquals(1, f.count(Stage.SESSION_INSERT));
      assertEquals(1, f.checked.get());
      assertEquals(STORED_HASH, f.observedStoredHash);
      f.verifyAudit("0000", "SUCCEEDED", "LOGIN_SUCCEEDED", "SUCCESS", 0, true);
      f.verifyReleasedAndConsumed();
    }
  }

  @Test
  void memory003AdminIdentityComesFromTheOwnedRow() throws Exception {
    try (Fixture f = new Fixture()) {
      f.role = "ADMIN";
      LoginResult.Success result = assertInstanceOf(LoginResult.Success.class, f.call());
      assertEquals(Role.ADMIN, result.actor().role());
      assertEquals(7, result.issued().identity().userId());
      f.verifyAudit("0000", "SUCCEEDED", "LOGIN_SUCCEEDED", "SUCCESS", 0, true);
      f.verifyReleasedAndConsumed();
    }
  }

  @Test
  void memory004AbsentAndDisabledAccountsUseDummyWorkAndOneCommonFailure() throws Exception {
    for (boolean absent : new boolean[] {true, false}) {
      for (boolean predicateAnswer : new boolean[] {true, false}) {
        try (Fixture f = new Fixture()) {
          f.absent = absent;
          f.status = DISABLED_STATUS;
          f.matches = predicateAnswer;
          LoginResult.Failure result = assertInstanceOf(LoginResult.Failure.class, f.call());
          assertEquals(ResultCode.AUTHENTICATION_FAILED, result.resultCode());
          assertEquals(0, result.retryAfterSeconds());
          assertEquals(DUMMY_HASH, f.observedStoredHash);
          assertEquals(1, f.checked.get());
          assertEquals(0, f.count(Stage.SESSION_INSERT));
          assertEquals(absent ? 0 : 1, f.count(Stage.UPDATE_USER));
          f.verifyAudit(
              "0101", absent ? "NO_ACCOUNT" : DISABLED_STATUS, "LOGIN_FAILED", DENIED, 0, false);
          f.verifyReleasedAndConsumed();
        }
      }
    }
  }

  @Test
  void memory005WrongActivePasswordUpdatesBothCountersWithoutIssuance() throws Exception {
    try (Fixture f = new Fixture()) {
      f.matches = false;
      f.userFailures = 2;
      f.ipFailures = 3;
      assertEquals(ResultCode.AUTHENTICATION_FAILED, f.call().resultCode());
      assertEquals(3, f.param(Stage.UPDATE_USER, 1));
      assertEquals(4, f.param(Stage.UPDATE_IP, 1));
      assertEquals(false, f.param(Stage.UPDATE_USER, 4));
      assertEquals(STORED_HASH, f.observedStoredHash);
      assertEquals(0, f.count(Stage.SESSION_INSERT));
      f.verifyAudit("0101", "PASSWORD_MISMATCH", "LOGIN_FAILED", DENIED, 0, false);
      f.verifyReleasedAndConsumed();
    }
  }

  @Test
  void memory006UserFiveAndIpTenLockOnThisAttempt() throws Exception {
    for (int[] counts : List.of(new int[] {4, 0}, new int[] {0, 9}, new int[] {4, 9})) {
      try (Fixture f = new Fixture()) {
        f.matches = false;
        f.userFailures = counts[0];
        f.ipFailures = counts[1];
        LoginResult result = f.call();
        assertEquals(ResultCode.LOCKED, result.resultCode());
        assertEquals(900, result.retryAfterSeconds());
        assertEquals(counts[0] + 1, f.param(Stage.UPDATE_USER, 1));
        assertEquals(counts[1] + 1, f.param(Stage.UPDATE_IP, 1));
        f.verifyAudit("0106", "PASSWORD_MISMATCH", "LOGIN_LOCKED", DENIED, 900, false);
        f.verifyReleasedAndConsumed();
      }
    }
  }

  @Test
  void memory007ExistingLocksUseMaximumWithoutCheckerOrMutation() throws Exception {
    for (boolean absent : new boolean[] {false, true}) {
      try (Fixture f = new Fixture()) {
        f.absent = absent;
        f.userFailures = 5;
        f.userLock = Optional.of(AT.plusSeconds(120));
        f.ipFailures = 10;
        f.ipLock = Optional.of(AT.plusSeconds(240));
        LoginResult result = f.call();
        assertEquals(ResultCode.LOCKED, result.resultCode());
        assertEquals(240, result.retryAfterSeconds());
        assertEquals(0, f.checked.get());
        assertEquals(0, f.count(Stage.UPDATE_USER));
        assertEquals(0, f.count(Stage.UPDATE_IP));
        assertEquals(0, f.count(Stage.SESSION_INSERT));
        f.verifyAudit("0106", "PREEXISTING_LOCK", "LOGIN_LOCKED", DENIED, 240, false);
        f.verifyReleasedAndConsumed();
      }
    }
  }

  @Test
  void memory008FractionalRetryCeilsAndCapsAtNineHundred() throws Exception {
    for (long[] vector :
        List.of(
            new long[] {1_000, 1},
            new long[] {1_000_001_000L, 2},
            new long[] {899_999_999_000L, 900},
            new long[] {900_000_001_000L, 900})) {
      try (Fixture f = new Fixture()) {
        f.userFailures = 5;
        f.userLock = Optional.of(AT.plusNanos(vector[0]));
        LoginResult result = f.call();
        assertEquals(ResultCode.LOCKED, result.resultCode());
        assertEquals(vector[1], result.retryAfterSeconds());
        assertEquals(0, f.checked.get());
        f.verifyReleasedAndConsumed();
      }
    }
  }

  @Test
  void memory009ExpiryEqualityPermitsCheckWhileWindowEqualityStillAccumulates() throws Exception {
    for (boolean matches : new boolean[] {true, false}) {
      try (Fixture f = new Fixture()) {
        f.matches = matches;
        f.userFailures = 5;
        f.userWindow = AT.minusSeconds(900);
        f.userLock = Optional.of(AT);
        LoginResult result = f.call();
        assertEquals(matches ? ResultCode.SUCCESS : ResultCode.LOCKED, result.resultCode());
        assertEquals(matches ? 0 : 900, result.retryAfterSeconds());
        assertEquals(1, f.checked.get());
        f.verifyReleasedAndConsumed();
      }
    }
    try (Fixture f = new Fixture()) {
      f.matches = false;
      f.userFailures = 5;
      f.userWindow = AT.minusSeconds(900).minusNanos(1_000);
      f.userLock = Optional.of(AT.minusNanos(1_000));
      assertEquals(ResultCode.AUTHENTICATION_FAILED, f.call().resultCode());
      assertEquals(1, f.param(Stage.UPDATE_USER, 1));
      assertNull(f.param(Stage.UPDATE_USER, 3));
      f.verifyReleasedAndConsumed();
    }
  }

  @Test
  void memory010NullAndInvalidInputsNeverSkipPasswordConsumption() throws Exception {
    for (int missing = 0; missing < 6; missing++) {
      try (Fixture f = new Fixture()) {
        int slot = missing;
        AuthenticationService service = f.service();
        assertThrows(
            NullPointerException.class,
            () ->
                service.authenticate(
                    slot == 0 ? null : f.connection,
                    slot == 1 ? null : " ÅLICE ",
                    f.password,
                    slot == 2 ? null : CLIENT,
                    slot == 3 ? null : MESSAGE,
                    slot == 4 ? null : CORRELATION,
                    slot == 5 ? null : NOW));
        assertTrue(f.statements.isEmpty());
        f.verifyReleasedAndConsumed();
      }
    }
    for (String bad : List.of("", " ", "x".repeat(65), "bad\nname")) {
      try (Fixture f = new Fixture()) {
        expectStorageFailure(
            () ->
                f.service()
                    .authenticate(
                        f.connection, bad, f.password, CLIENT, MESSAGE, CORRELATION, NOW));
        assertTrue(f.statements.isEmpty());
        f.verifyReleasedAndConsumed();
      }
    }
    try (Fixture f = new Fixture()) {
      assertThrows(
          NullPointerException.class,
          () ->
              f.service()
                  .authenticate(f.connection, "Alice", null, CLIENT, MESSAGE, CORRELATION, NOW));
      assertTrue(f.statements.isEmpty());
    }
  }

  @Test
  void memory011CheckerFailuresMapOnlyDeclaredCatalogAndPreserveDirectFatalIdentity()
      throws Exception {
    for (RuntimeException failure :
        List.of(
            new IllegalArgumentException(SYNTHETIC_FAULT),
            new IllegalStateException(SYNTHETIC_FAULT),
            new AuthContextCryptoException(AuthContextCryptoException.Reason.CRYPTO_UNAVAILABLE))) {
      try (Fixture f = new Fixture()) {
        f.checkerFault = Optional.of(failure);
        expectStorageFailure(f::call);
        assertEquals(0, f.count(Stage.UPDATE_USER));
        assertEquals(0, f.count(Stage.LOGIN_AUDIT));
        f.verifyReleasedAndConsumed();
      }
    }
    for (Throwable failure :
        List.of(
            new UnsupportedOperationException(SYNTHETIC_FAULT),
            new AssertionError(SYNTHETIC_FAULT))) {
      try (Fixture f = new Fixture()) {
        f.checkerFault = Optional.of(failure);
        assertSame(failure, assertThrows(failure.getClass(), f::call));
        f.verifyReleasedAndConsumed();
      }
    }
  }

  @Test
  void memory012JdbcReadUpdateAndResourceFaultsFailClosedWithoutOwningTheConnection()
      throws Exception {
    for (Stage stage :
        List.of(
            Stage.USER,
            Stage.CREATE_IP,
            Stage.IP,
            Stage.UPDATE_USER,
            Stage.UPDATE_IP,
            Stage.SESSION_INSERT)) {
      for (Site site : List.of(Site.PREPARE, Site.EXECUTE, Site.CLOSE_STATEMENT)) {
        try (Fixture f = new Fixture()) {
          f.fault = Optional.of(new Fault(stage, site, new SQLException(SYNTHETIC_FAULT, "ZZ901")));
          expectStorageFailure(f::call);
          assertEquals(0, f.count(Stage.LOGIN_AUDIT));
          f.verifyReleasedAndConsumed();
        }
      }
    }
    for (Site site : List.of(Site.NEXT, Site.CLOSE_RESULT)) {
      try (Fixture f = new Fixture()) {
        f.fault = Optional.of(new Fault(Stage.USER, site, new SQLException(SYNTHETIC_FAULT)));
        expectStorageFailure(f::call);
        f.verifyReleasedAndConsumed();
      }
    }
    for (String column :
        List.of("role", "status", "id", "username", "password_hash", FAILED_COUNT_COLUMN)) {
      try (Fixture f = new Fixture()) {
        f.nullUserColumn = Optional.of(column);
        expectStorageFailure(f::call);
        f.verifyReleasedAndConsumed();
      }
    }
    for (boolean badRole : new boolean[] {true, false}) {
      try (Fixture f = new Fixture()) {
        f.role = badRole ? "UNKNOWN" : "USER";
        f.status = badRole ? ACTIVE_STATUS : "UNKNOWN";
        expectStorageFailure(f::call);
        f.verifyReleasedAndConsumed();
      }
    }
  }

  @Test
  void memory013CriticalAuditFaultAndNestedFatalNeverReturnSuccess() throws Exception {
    try (Fixture f = new Fixture()) {
      f.fault =
          Optional.of(
              new Fault(Stage.LOGIN_AUDIT, Site.EXECUTE, new SQLException(SYNTHETIC_FAULT)));
      expectStorageFailure(f::call);
      assertEquals(1, f.count(Stage.SESSION_INSERT));
      f.verifyReleasedAndConsumed();
    }
    AssertionError fatal = new AssertionError(SYNTHETIC_FAULT);
    SQLException wrapper = new SQLException(SYNTHETIC_FAULT, fatal);
    try (Fixture f = new Fixture()) {
      f.fault = Optional.of(new Fault(Stage.USER, Site.EXECUTE, wrapper));
      assertSame(fatal, assertThrows(AssertionError.class, f::call));
      f.verifyReleasedAndConsumed();
    }
  }

  @Test
  void memory014ThirdSessionDelegatesOldestRevocationWithSeparateSafeAudit() throws Exception {
    try (Fixture f = new Fixture()) {
      UUID oldest = new UUID(0, 101);
      f.priorActive = List.of(oldest, new UUID(0, 102));
      assertInstanceOf(LoginResult.Success.class, f.call());
      assertEquals(1, f.count(Stage.SESSION_REPLACE));
      assertTrue(oldest.equals(f.param(Stage.SESSION_REPLACE, 2)));
      assertEquals(1, f.count(Stage.SESSION_AUDIT));
      JsonObject audit =
          JsonParser.parseString((String) f.param(Stage.SESSION_AUDIT, 6)).getAsJsonObject();
      assertEquals(Set.of("targetUserId", REASON_KEY, RESULT_CODE_KEY), audit.keySet());
      assertEquals(7, audit.get("targetUserId").getAsLong());
      assertEquals("REPLACED", audit.get(REASON_KEY).getAsString());
      assertEquals("0000", audit.get(RESULT_CODE_KEY).getAsString());
      f.verifyReleasedAndConsumed();
    }
    try (Fixture f = new Fixture()) {
      f.codec.close();
      expectStorageFailure(f::call);
      assertEquals(0, f.count(Stage.SESSION_INSERT));
      assertEquals(0, f.count(Stage.LOGIN_AUDIT));
      f.verifyReleasedAndConsumed();
    }
  }

  @Test
  void memory015RepeatedConsumerCallsKeepCallerRowsAndPasswordsIndependent() throws Exception {
    try (Fixture first = new Fixture();
        Fixture second = new Fixture()) {
      second.useSecondActor();
      AuthenticationService service = first.service();
      assertEquals(ResultCode.SUCCESS, first.call(service).resultCode());
      // A different caller row controls the outcome; the shared consumer retains no prior actor.
      second.status = DISABLED_STATUS;
      assertEquals(ResultCode.AUTHENTICATION_FAILED, second.call(service).resultCode());
      assertEquals(0, second.count(Stage.SESSION_INSERT));
      first.verifyReleasedAndConsumed();
      second.verifyReleasedAndConsumed();
    }
  }

  @Test
  void memory016TwoOwnedFiniteTasksUseSeparateBorrowedConnectionsAndConsumeEachArray()
      throws Exception {
    Fixture first = new Fixture();
    Fixture second = new Fixture();
    var executor = Executors.newFixedThreadPool(2);
    try {
      second.useSecondActor();
      AuthenticationService service = first.service();
      var one =
          executor.submit(
              () -> {
                return first.call(service);
              });
      var two =
          executor.submit(
              () -> {
                return second.call(service);
              });
      LoginResult.Success firstResult =
          assertInstanceOf(LoginResult.Success.class, one.get(5, TimeUnit.SECONDS));
      LoginResult.Success secondResult =
          assertInstanceOf(LoginResult.Success.class, two.get(5, TimeUnit.SECONDS));
      assertEquals(7, firstResult.actor().userId());
      assertEquals(8, secondResult.actor().userId());
      assertEquals("Ålice", firstResult.actor().username());
      assertEquals("Bob", secondResult.actor().username());
      assertNotSame(first.connection, second.connection);
      assertEquals(1, first.count(Stage.LOGIN_AUDIT));
      assertEquals(1, second.count(Stage.LOGIN_AUDIT));
      first.verifyReleasedAndConsumed();
      second.verifyReleasedAndConsumed();
    } finally {
      executor.shutdownNow();
      assertTrue(executor.awaitTermination(10, TimeUnit.SECONDS));
      try {
        first.close();
      } finally {
        second.close();
      }
    }
  }

  private static void expectStorageFailure(org.junit.jupiter.api.function.Executable action) {
    AuthenticationInfrastructureException failure =
        assertThrows(AuthenticationInfrastructureException.class, action);
    assertEquals(STORAGE_ERROR, failure.getMessage());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
  }

  private enum Stage {
    USER,
    CREATE_IP,
    IP,
    UPDATE_USER,
    UPDATE_IP,
    SESSION_USER,
    SESSION_INSERT,
    SESSION_ACTIVE,
    SESSION_REPLACE,
    SESSION_AUDIT,
    LOGIN_AUDIT
  }

  private enum Site {
    PREPARE,
    EXECUTE,
    NEXT,
    CLOSE_RESULT,
    CLOSE_STATEMENT
  }

  private record Fault(Stage stage, Site site, Throwable failure) {}

  private static final class CountingRandom extends SecureRandom {
    private static final long serialVersionUID = 1L;
    private final AtomicInteger sequence = new AtomicInteger(16);

    @Override
    public void nextBytes(byte[] bytes) {
      Arrays.fill(bytes, (byte) sequence.incrementAndGet());
    }
  }

  private static final class Fixture implements AutoCloseable {
    final LoginAttemptRepository attempts = new LoginAttemptRepository();
    final LoginAuditWriter audit = new LoginAuditWriter();
    final AuthContextCodec codec =
        new AuthContextCodec("v1", new byte[32], null, null, new CountingRandom());
    final AtomicInteger ids = new AtomicInteger(1000);
    final AuthSessionService sessions;
    final Connection connection;
    final List<Statement> statements = new ArrayList<>();
    final AtomicInteger checked = new AtomicInteger();
    final char[] password = new char[16];
    boolean absent;
    boolean autoCommit;
    boolean ipAbsent;
    boolean userWindowAbsent;
    Optional<String> nullIpColumn = Optional.empty();
    final Map<Stage, Integer> updateCounts = new HashMap<>();
    String role = "USER";
    String status = ACTIVE_STATUS;
    boolean matches = true;
    int userFailures;
    int ipFailures;
    Instant userWindow = AT.minusSeconds(30);
    Instant ipWindow = AT.minusSeconds(20);
    Optional<Instant> userLock = Optional.empty();
    Optional<Instant> ipLock = Optional.empty();
    Optional<Throwable> checkerFault = Optional.empty();
    Optional<Fault> fault = Optional.empty();
    Optional<Stage> nullStatementAt = Optional.empty();
    Optional<Stage> nullRowsAt = Optional.empty();
    final List<Stage> prepareAttempts = new ArrayList<>();
    Optional<String> nullUserColumn = Optional.empty();
    List<UUID> priorActive = List.of();
    volatile String observedStoredHash = "";
    UUID insertedId;
    long userId = 7;
    String rowUsername = "Ålice";
    String inputName = " ÅLICE ";
    String expectedKey = KEY;
    String expectedDisplay = DISPLAY;
    InetAddress client = CLIENT;
    String expectedClient = "192.0.2.10";
    UUID messageId = MESSAGE;
    UUID correlationId = CORRELATION;

    Fixture() throws Exception {
      Arrays.fill(password, 'x');
      sessions =
          new AuthSessionService(
              new ContextHash(),
              codec,
              new CountingRandom(),
              () -> new UUID(0, ids.getAndIncrement()));
      connection =
          proxy(
              Connection.class,
              (method, args) ->
                  switch (method) {
                    case "getAutoCommit" -> autoCommit;
                    case "prepareStatement" -> prepare((String) args[0]);
                    case "toString" -> "OwnMemoryJdbc";
                    default ->
                        throw new AssertionError(
                            "borrowed connection operation is forbidden: " + method);
                  });
    }

    BiPredicate<char[], String> checker() {
      return (supplied, stored) -> {
        assertEquals(16, supplied.length);
        for (char value : supplied) assertEquals('x', value);
        checked.incrementAndGet();
        observedStoredHash = stored;
        if (checkerFault.isPresent()) {
          Throwable failure = checkerFault.orElseThrow();
          if (failure instanceof RuntimeException runtime) throw runtime;
          if (failure instanceof Error error) throw error;
          throw new AssertionError("unexpected checker fixture failure type");
        }
        return matches;
      };
    }

    AuthenticationService service() {
      return new AuthenticationService(attempts, checker(), sessions, audit);
    }

    LoginResult call() {
      return call(service());
    }

    LoginResult call(AuthenticationService service) {
      return service.authenticate(
          connection, inputName, password, client, messageId, correlationId, NOW);
    }

    @org.jspecify.annotations.Nullable
    PreparedStatement prepare(String sql) throws SQLException {
      Stage stage = classify(sql);
      inject(stage, Site.PREPARE);
      prepareAttempts.add(stage);
      if (nullStatementAt.filter(value -> value == stage).isPresent()) return null;
      Statement statement = new Statement(stage);
      statements.add(statement);
      return statement.proxy;
    }

    private static Stage classify(String sql) {
      String q = sql.replaceAll("\\s+", " ").trim();
      if (q.startsWith("select id,username,role,status,password_hash,failed_count,")) {
        assertTrue(q.endsWith("from schubert.app_users where username_key=? for update"));
        return Stage.USER;
      }
      if (q.startsWith("insert into schubert.login_ip_attempts ")) {
        assertTrue(q.endsWith("on conflict(client_address) do nothing"));
        return Stage.CREATE_IP;
      }
      if (q.startsWith(
          "select failed_count,window_started_at,locked_until from schubert.login_ip_attempts ")) {
        assertTrue(q.endsWith("where client_address=cast(? as inet) for update"));
        return Stage.IP;
      }
      if (q.startsWith("update schubert.app_users set failed_count=")) return Stage.UPDATE_USER;
      if (q.startsWith("update schubert.login_ip_attempts set failed_count="))
        return Stage.UPDATE_IP;
      if (q.equals("select status from schubert.app_users where id=? for update"))
        return Stage.SESSION_USER;
      if (q.startsWith("insert into schubert.auth_sessions ")) return Stage.SESSION_INSERT;
      if (q.startsWith("select id from schubert.auth_sessions ")) {
        assertTrue(q.endsWith("order by last_accessed_at,id for update"));
        return Stage.SESSION_ACTIVE;
      }
      if (q.startsWith("update schubert.auth_sessions set revoked=true,revoked_at=?")) {
        assertTrue(q.contains("revoke_reason='REPLACED'"));
        return Stage.SESSION_REPLACE;
      }
      if (q.startsWith("insert into schubert.app_logs ")) {
        return q.contains("'SESSION_REVOKED'") ? Stage.SESSION_AUDIT : Stage.LOGIN_AUDIT;
      }
      throw new AssertionError("unexpected in-memory SQL shape");
    }

    void inject(Stage stage, Site site) throws SQLException {
      if (fault.isPresent()
          && fault.orElseThrow().stage() == stage
          && fault.orElseThrow().site() == site) {
        Throwable failure = fault.orElseThrow().failure();
        if (failure instanceof SQLException sql) throw sql;
        if (failure instanceof RuntimeException runtime) throw runtime;
        if (failure instanceof Error error) throw error;
        throw new AssertionError("unsupported JDBC fixture failure type");
      }
    }

    void useSecondActor() {
      userId = 8;
      rowUsername = "Bob";
      inputName = " Bob ";
      expectedKey = "bob";
      expectedDisplay = "Bob";
      client = InetAddress.ofLiteral("192.0.2.11");
      expectedClient = "192.0.2.11";
      messageId = new UUID(0, 21);
      correlationId = new UUID(0, 22);
    }

    List<Stage> stages() {
      return statements.stream().map(v -> v.stage).toList();
    }

    long count(Stage stage) {
      return statements.stream().filter(v -> v.stage == stage).count();
    }

    Object param(Stage stage, int index) {
      Statement statement =
          statements.stream().filter(v -> v.stage == stage).findFirst().orElseThrow();
      assertTrue(statement.parameters.containsKey(index), "required bound index is missing");
      return statement.parameters.get(index);
    }

    void verifyAudit(
        String code, String reason, String action, String outcome, int retry, boolean success) {
      assertEquals(success ? "INFO" : "WARN", param(Stage.LOGIN_AUDIT, 2));
      assertEquals(action, param(Stage.LOGIN_AUDIT, 3));
      assertEquals(action, param(Stage.LOGIN_AUDIT, 4));
      assertEquals(AT.atOffset(ZoneOffset.UTC), param(Stage.LOGIN_AUDIT, 1));
      assertEquals(messageId, param(Stage.LOGIN_AUDIT, 5));
      assertEquals(correlationId, param(Stage.LOGIN_AUDIT, 6));
      assertEquals(success ? userId : null, param(Stage.LOGIN_AUDIT, 7));
      assertEquals(expectedDisplay, param(Stage.LOGIN_AUDIT, 8));
      assertEquals(expectedClient, param(Stage.LOGIN_AUDIT, 9));
      JsonObject details =
          JsonParser.parseString((String) param(Stage.LOGIN_AUDIT, 10)).getAsJsonObject();
      assertEquals(
          Set.of(RESULT_CODE_KEY, REASON_KEY, "retryAfterSeconds", "outcome"), details.keySet());
      assertEquals(code, details.get(RESULT_CODE_KEY).getAsString());
      assertEquals(reason, details.get(REASON_KEY).getAsString());
      assertEquals(retry, details.get("retryAfterSeconds").getAsInt());
      assertEquals(outcome, details.get("outcome").getAsString());
    }

    void verifyReleasedAndConsumed() {
      assertArrayEquals(new char[16], password);
      for (Statement statement : statements) {
        assertEquals(1, statement.closed);
        for (Cursor cursor : statement.cursors) assertEquals(1, cursor.closed);
      }
    }

    @Override
    public void close() {
      codec.close();
      Arrays.fill(password, '\0');
      for (Statement statement : statements) {
        for (Object value : statement.parameters.values())
          if (value instanceof byte[] bytes) Arrays.fill(bytes, (byte) 0);
      }
    }

    private final class Statement {
      final Stage stage;
      final Map<Integer, Object> parameters = new HashMap<>();
      final List<Cursor> cursors = new ArrayList<>();
      final PreparedStatement proxy;
      int closed;

      Statement(Stage stage) {
        this.stage = stage;
        proxy =
            proxy(
                PreparedStatement.class,
                (method, args) -> {
                  if (method.startsWith("set")) {
                    int key = (Integer) args[0];
                    Object value = method.equals("setNull") ? null : args[1];
                    parameters.put(key, value instanceof byte[] bytes ? bytes.clone() : value);
                    return null;
                  }
                  return switch (method) {
                    case "executeQuery" -> {
                      inject(stage, Site.EXECUTE);
                      if (nullRowsAt.filter(value -> value == stage).isPresent()) yield null;
                      Cursor cursor = new Cursor(stage, rows());
                      cursors.add(cursor);
                      yield cursor.proxy;
                    }
                    case "executeUpdate" -> {
                      inject(stage, Site.EXECUTE);
                      if (stage == Stage.SESSION_INSERT) insertedId = (UUID) parameters.get(1);
                      yield updateCounts.getOrDefault(stage, 1);
                    }
                    case "close" -> {
                      closed++;
                      inject(stage, Site.CLOSE_STATEMENT);
                      yield null;
                    }
                    case "toString" -> "OwnMemoryStatement";
                    default ->
                        throw new AssertionError("unexpected statement operation: " + method);
                  };
                });
      }

      List<Map<String, Object>> rows() {
        if (stage == Stage.USER) {
          if (absent) return List.of();
          Map<String, Object> row = new HashMap<>();
          assertEquals(expectedKey, parameters.get(1));
          row.put("id", userId);
          row.put("username", rowUsername);
          row.put("role", role);
          row.put("status", status);
          row.put("password_hash", STORED_HASH);
          row.put(FAILED_COUNT_COLUMN, userFailures);
          row.put(
              "failure_window_started_at",
              userWindowAbsent ? null : userWindow.atOffset(ZoneOffset.UTC));
          row.put("locked_until", userLock.map(v -> v.atOffset(ZoneOffset.UTC)).orElse(null));
          nullUserColumn.ifPresent(v -> row.put(v, null));
          return List.of(row);
        }
        if (stage == Stage.IP) {
          if (ipAbsent) return List.of();
          Map<String, Object> row = new HashMap<>();
          row.put(FAILED_COUNT_COLUMN, ipFailures);
          row.put("window_started_at", ipWindow.atOffset(ZoneOffset.UTC));
          nullIpColumn.ifPresent(value -> row.put(value, null));
          row.put("locked_until", ipLock.map(v -> v.atOffset(ZoneOffset.UTC)).orElse(null));
          return List.of(row);
        }
        if (stage == Stage.SESSION_USER) return List.of(Map.of("status", ACTIVE_STATUS));
        if (stage == Stage.SESSION_ACTIVE) {
          List<Map<String, Object>> rows = new ArrayList<>();
          for (UUID old : priorActive) rows.add(Map.of("id", old));
          assertNotNull(insertedId);
          rows.add(Map.of("id", insertedId));
          return rows;
        }
        throw new AssertionError("unexpected query stage");
      }
    }

    private final class Cursor {
      final Stage stage;
      final List<Map<String, Object>> rows;
      final ResultSet proxy;
      int at = -1;
      int closed;

      Cursor(Stage stage, List<Map<String, Object>> rows) {
        this.stage = stage;
        this.rows = rows;
        proxy =
            proxy(
                ResultSet.class,
                (method, args) ->
                    switch (method) {
                      case "next" -> {
                        inject(stage, Site.NEXT);
                        at++;
                        yield at < rows.size();
                      }
                      case "getString", "getObject" -> {
                        assertTrue(at >= 0 && at < rows.size());
                        assertTrue(
                            rows.get(at).containsKey((String) args[0]), "unknown fixture column");
                        Object value = rows.get(at).get((String) args[0]);
                        if (method.equals("getObject") && value != null)
                          assertTrue(((Class<?>) args[1]).isInstance(value));
                        yield value;
                      }
                      case "close" -> {
                        closed++;
                        inject(stage, Site.CLOSE_RESULT);
                        yield null;
                      }
                      case "toString" -> "OwnMemoryCursor";
                      default -> throw new AssertionError("unexpected cursor operation: " + method);
                    });
      }
    }
  }

  @FunctionalInterface
  private interface Invocation {
    Object invoke(String name, Object[] args) throws Throwable;
  }

  private static <T> T proxy(Class<T> type, Invocation invocation) {
    return type.cast(
        Proxy.newProxyInstance(
            type.getClassLoader(),
            new Class<?>[] {type},
            (ignored, method, args) -> invocation.invoke(method.getName(), args)));
  }

  @Test
  void resource017AllLoginStatementsRejectNullAndConsumePassword() throws Exception {
    List<Stage> route =
        List.of(
            Stage.USER,
            Stage.CREATE_IP,
            Stage.IP,
            Stage.UPDATE_USER,
            Stage.UPDATE_IP,
            Stage.SESSION_USER,
            Stage.SESSION_INSERT,
            Stage.SESSION_ACTIVE,
            Stage.LOGIN_AUDIT);
    for (Stage stage :
        List.of(
            Stage.USER,
            Stage.CREATE_IP,
            Stage.IP,
            Stage.UPDATE_USER,
            Stage.UPDATE_IP,
            Stage.LOGIN_AUDIT)) {
      try (Fixture f = new Fixture()) {
        f.nullStatementAt = Optional.of(stage);
        expectStorageFailure(f::call);
        int stop = route.indexOf(stage);
        assertEquals(route.subList(0, stop + 1), f.prepareAttempts);
        assertEquals(route.subList(0, stop), f.stages());
        f.verifyReleasedAndConsumed();
      }
    }
  }

  @Test
  void resource018BothLoginNullRowsCloseTheirOwnedStatement() throws Exception {
    for (Stage stage : List.of(Stage.USER, Stage.IP)) {
      try (Fixture f = new Fixture()) {
        f.nullRowsAt = Optional.of(stage);
        expectStorageFailure(f::call);
        assertEquals(stage, f.prepareAttempts.getLast());
        assertEquals(
            stage == Stage.USER
                ? List.of(Stage.USER)
                : List.of(Stage.USER, Stage.CREATE_IP, Stage.IP),
            f.stages());
        assertTrue(f.statements.getLast().cursors.isEmpty());
        f.verifyReleasedAndConsumed();
      }
    }
  }

  @Test
  void negative019DirectRequiredArgumentsKeyBytesAndTransactionBoundary() throws Exception {
    try (Fixture f = new Fixture()) {
      for (int missing = 0; missing < 4; missing++) {
        int slot = missing;
        assertThrows(
            NullPointerException.class,
            () ->
                f.attempts.lockForAttempt(
                    slot == 0 ? null : f.connection, slot == 1 ? null : KEY,
                    slot == 2 ? null : CLIENT, slot == 3 ? null : AT));
      }
      for (String invalid : List.of("", "x".repeat(97), "é".repeat(49)))
        assertThrows(
            IllegalArgumentException.class,
            () -> f.attempts.lockForAttempt(f.connection, invalid, CLIENT, AT));
      assertTrue(f.statements.isEmpty());
    }
    for (String boundary : List.of("a", "x".repeat(96), "é".repeat(48))) {
      try (Fixture f = new Fixture()) {
        f.expectedKey = boundary;
        var result = f.attempts.lockForAttempt(f.connection, boundary, CLIENT, AT);
        assertEquals(7, result.account().orElseThrow().identity().userId());
        assertEquals(List.of(Stage.USER, Stage.CREATE_IP, Stage.IP), f.stages());
        for (var statement : f.statements) {
          assertEquals(1, statement.closed);
          for (var cursor : statement.cursors) assertEquals(1, cursor.closed);
        }
      }
    }
    try (Fixture f = new Fixture()) {
      f.autoCommit = true;
      expectStorageFailure(f::call);
      var locked =
          new LockedLoginAttempt(
              CLIENT.getHostAddress(),
              Optional.empty(),
              new LoginAttemptState(LoginAttemptKind.IP, 0, Optional.of(AT), Optional.empty()));
      expectStorageFailure(() -> f.attempts.recordSuccess(f.connection, locked, AT));
      expectStorageFailure(() -> f.attempts.recordFailure(f.connection, locked, AT));
      assertTrue(f.statements.isEmpty());
      f.verifyReleasedAndConsumed();
    }
  }

  @Test
  void negative020PersistedRoleAndStatusHashCollisionsNeverAcquireAuthority() throws Exception {
    assertEquals(2614219, "USER".hashCode());
    assertEquals(2614219, "V4ER".hashCode());
    assertEquals(62130991, "ADMIN".hashCode());
    assertEquals(62130991, "B%MIN".hashCode());
    assertEquals(ACTIVE_STATUS.hashCode(), "B$TIVE".hashCode());
    assertEquals(DISABLED_STATUS.hashCode(), "E*SABLED".hashCode());
    for (String role : List.of("V4ER", "B%MIN", "", "user", " USER ")) {
      try (Fixture f = new Fixture()) {
        f.role = role;
        expectStorageFailure(f::call);
        assertEquals(List.of(Stage.USER), f.stages());
        assertEquals(0, f.checked.get());
        f.verifyReleasedAndConsumed();
      }
    }
    for (String status : List.of("B$TIVE", "E*SABLED", "", "active", " ACTIVE ")) {
      try (Fixture f = new Fixture()) {
        f.status = status;
        expectStorageFailure(f::call);
        assertEquals(List.of(Stage.USER), f.stages());
        assertEquals(0, f.checked.get());
        f.verifyReleasedAndConsumed();
      }
    }
  }

  @Test
  void negative021MissingIpRequiredColumnsAndOptionalUserWindow() throws Exception {
    for (String missing : List.of("ROW", FAILED_COUNT_COLUMN, "window_started_at")) {
      try (Fixture f = new Fixture()) {
        f.ipAbsent = missing.equals("ROW");
        if (!f.ipAbsent) f.nullIpColumn = Optional.of(missing);
        expectStorageFailure(f::call);
        assertEquals(List.of(Stage.USER, Stage.CREATE_IP, Stage.IP), f.stages());
        assertEquals(0, f.checked.get());
        f.verifyReleasedAndConsumed();
      }
    }
    try (Fixture f = new Fixture()) {
      f.userWindowAbsent = true;
      f.matches = false;
      assertEquals(ResultCode.AUTHENTICATION_FAILED, f.call().resultCode());
      assertEquals(1, f.param(Stage.UPDATE_USER, 1));
      assertEquals(AT.atOffset(ZoneOffset.UTC), f.param(Stage.UPDATE_USER, 2));
      f.verifyAudit("0101", "PASSWORD_MISMATCH", "LOGIN_FAILED", DENIED, 0, false);
      f.verifyReleasedAndConsumed();
    }
  }

  @Test
  void negative022EveryCriticalUpdateRequiresExactlyOneRowInEitherOutcome() throws Exception {
    for (Stage stage : List.of(Stage.UPDATE_USER, Stage.UPDATE_IP, Stage.LOGIN_AUDIT)) {
      for (int count : new int[] {0, 2}) {
        for (boolean matches : new boolean[] {false, true}) {
          try (Fixture f = new Fixture()) {
            f.matches = matches;
            f.updateCounts.put(stage, count);
            expectStorageFailure(f::call);
            assertEquals(stage, f.prepareAttempts.getLast());
            assertEquals(1, f.count(stage));
            f.verifyReleasedAndConsumed();
          }
        }
      }
    }
  }
}
