package dev.codex.schubert.nk.api.security;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.api.domain.Role;
import java.lang.reflect.Proxy;
import java.net.InetAddress;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Types;
import java.time.Instant;
import java.time.OffsetDateTime;
import java.time.ZoneOffset;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.function.Executable;

/** PT-AUT-ATTEMPTPORT001..010. Pure borrowed JDBC interfaces, no DB/authentication/credential. */
final class LoginAttemptPortTest {
  private static final String USER_SQL =
      "select"
          + " id,username,role,status,password_hash,failed_count,failure_window_started_at,locked_until"
          + " from schubert.app_users where username_key=? for update";
  private static final String CREATE_SQL =
      "insert into schubert.login_ip_attempts"
          + " (client_address,failed_count,window_started_at,updated_at) values(cast(? as"
          + " inet),0,?,?) on conflict(client_address) do nothing";
  private static final String IP_SQL =
      "select failed_count,window_started_at,locked_until from schubert.login_ip_attempts"
          + " where client_address=cast(? as inet) for update";
  private static final String UPDATE_USER_SQL =
      "update schubert.app_users set failed_count=?,failure_window_started_at=?,locked_until=?,"
          + "last_login_at=case when ? then ? else last_login_at end where id=?";
  private static final String UPDATE_IP_SQL =
      "update schubert.login_ip_attempts set"
          + " failed_count=?,window_started_at=?,locked_until=?,updated_at=? where"
          + " client_address=cast(? as inet)";
  private static final String COLUMN_USERNAME = "username";
  private static final String POINT_USER_BIND = "0:bind";
  private static final String NAME = "attempt-user";
  private static final String IP = "127.0.0.1";
  private static final String NON_CREDENTIAL = "NOT_A_CREDENTIAL_OR_DIGEST";
  private static final String FAILED_COUNT = "failed_count";
  private static final String LOCKED_UNTIL = "locked_until";
  private static final String USER_WINDOW = "failure_window_started_at";
  private static final String IP_WINDOW = "window_started_at";
  private static final String ROLE = "role";
  private static final String STATUS = "status";
  private static final String PREPARE = "prepare";
  private static final String QUERY = "query";
  private static final String BIND = "bind";
  private static final String NEXT = "next";
  private static final String ROW_CLOSE = "rowClose";
  private static final String CLOSE = "close";
  private static final String UPDATE = "update";
  private static final String NULL_TIME = "NULL_TIMESTAMP_WITH_TIMEZONE";
  private static final Instant NOW = Instant.parse("2026-11-05T01:02:03.123456Z");
  private static final OffsetDateTime UTC = NOW.atOffset(ZoneOffset.UTC);

  @Test
  void lockOrderAndLiteralSqlBindingsMatchUserThenCreateThenIp() throws Exception {
    Fixture fixture = new Fixture();
    LockedLoginAttempt actual = lock(fixture, NAME, NOW);
    assertEquals(List.of(USER_SQL, CREATE_SQL, IP_SQL), fixture.sqls());
    assertEquals(Map.of(1, NAME), fixture.statements.get(0).bindings);
    assertEquals(Map.of(1, IP, 2, UTC, 3, UTC), fixture.statements.get(1).bindings);
    assertEquals(Map.of(1, IP), fixture.statements.get(2).bindings);
    assertTrue(fixture.events.indexOf("0:" + CLOSE) < fixture.events.indexOf("1:" + PREPARE));
    assertTrue(fixture.events.indexOf("1:" + CLOSE) < fixture.events.indexOf("2:" + PREPARE));
    assertEquals(IP, actual.clientAddress());
    var account = actual.account().orElseThrow();
    assertEquals(7, account.identity().userId());
    assertEquals(NAME, account.identity().username());
    assertEquals(Role.USER, account.identity().role());
    assertTrue(account.active());
    assertTrue(account.passwordHash().equals(NON_CREDENTIAL));
    assertEquals(0, account.attempts().failedCount());
    assertEquals(Optional.empty(), account.attempts().windowStartedAt());
    assertEquals(Optional.empty(), account.attempts().lockedUntil());
    assertEquals(Optional.of(NOW), actual.ip().windowStartedAt());
    fixture.assertClosed(3, 2);
    Fixture absent = new Fixture();
    absent.userPresent = false;
    absent.createCount = 0;
    assertTrue(lock(absent, NAME, NOW).account().isEmpty());
    absent.assertClosed(3, 2);
  }

  @Test
  void persistedClosedRoleStatusAndNullableTimesHaveExactProjection() throws Exception {
    for (String role : List.of("USER", "ADMIN")) {
      for (String status : List.of("ACTIVE", "DISABLED")) {
        Fixture fixture = new Fixture();
        fixture.user.put(ROLE, role);
        fixture.user.put(STATUS, status);
        fixture.user.put(FAILED_COUNT, 5);
        fixture.user.put(USER_WINDOW, UTC);
        fixture.user.put(LOCKED_UNTIL, NOW.plusSeconds(900).atOffset(ZoneOffset.UTC));
        fixture.ip.put(FAILED_COUNT, 10);
        fixture.ip.put(LOCKED_UNTIL, NOW.plusSeconds(900).atOffset(ZoneOffset.UTC));
        var actual = lock(fixture, NAME, NOW);
        var account = actual.account().orElseThrow();
        assertEquals(role.equals("USER") ? Role.USER : Role.ADMIN, account.identity().role());
        assertEquals(status.equals("ACTIVE"), account.active());
        assertEquals(Optional.of(NOW), account.attempts().windowStartedAt());
        assertEquals(Optional.of(NOW.plusSeconds(900)), account.attempts().lockedUntil());
        assertEquals(Optional.of(NOW.plusSeconds(900)), actual.ip().lockedUntil());
        fixture.assertClosed(3, 2);
      }
    }
  }

  @Test
  void usernameByteAndNullContractsRejectBeforeBorrowedTransactionMutation() throws Exception {
    for (String name : List.of("a", "a".repeat(96), "é".repeat(48))) {
      Fixture fixture = new Fixture();
      lock(fixture, name, NOW);
      assertEquals(name, fixture.statements.getFirst().bindings.get(1));
    }
    for (String name : List.of("", "a".repeat(97), "é".repeat(49))) {
      Fixture fixture = new Fixture();
      assertThrows(IllegalArgumentException.class, () -> lock(fixture, name, NOW));
      assertTrue(fixture.statements.isEmpty());
    }
    Fixture fixture = new Fixture();
    var repository = new LoginAttemptRepository();
    assertThrows(
        NullPointerException.class, () -> repository.lockForAttempt(null, NAME, client(), NOW));
    assertThrows(
        NullPointerException.class,
        () -> repository.lockForAttempt(fixture.connection(), null, client(), NOW));
    assertThrows(
        NullPointerException.class,
        () -> repository.lockForAttempt(fixture.connection(), NAME, null, NOW));
    assertThrows(
        NullPointerException.class,
        () -> repository.lockForAttempt(fixture.connection(), NAME, client(), null));
    var locked = snapshot(true, 0, 0, Optional.empty(), Optional.empty());
    assertThrows(NullPointerException.class, () -> repository.recordSuccess(null, locked, NOW));
    assertThrows(
        NullPointerException.class,
        () -> repository.recordFailure(fixture.connection(), null, NOW));
    assertThrows(
        NullPointerException.class,
        () -> repository.recordSuccess(fixture.connection(), locked, null));
    assertTrue(fixture.statements.isEmpty());
    for (boolean reading : new boolean[] {false, true}) {
      Fixture automatic = new Fixture();
      automatic.autoCommit = true;
      catalog(
          () -> {
            if (reading) lock(automatic, NAME, NOW);
            else repository.recordFailure(automatic.connection(), locked, NOW);
          });
      assertTrue(automatic.statements.isEmpty());
    }
  }

  @Test
  void requiredAndMalformedUserColumnsBecomeFixedCatalogAfterClosingOwnedResources() {
    for (String column :
        List.of(ROLE, STATUS, "id", COLUMN_USERNAME, "password_hash", FAILED_COUNT)) {
      Fixture fixture = new Fixture();
      fixture.user.put(column, null);
      catalog(() -> lock(fixture, NAME, NOW));
      fixture.assertClosed(1, 1);
    }
    for (Map.Entry<String, Object> invalid :
        Map.<String, Object>of(
                ROLE,
                "UNKNOWN",
                STATUS,
                "UNKNOWN",
                "id",
                0L,
                COLUMN_USERNAME,
                "",
                "password_hash",
                "x".repeat(256),
                FAILED_COUNT,
                -1)
            .entrySet()) {
      Fixture fixture = new Fixture();
      fixture.user.put(invalid.getKey(), invalid.getValue());
      catalog(() -> lock(fixture, NAME, NOW));
      fixture.assertClosed(1, 1);
    }
  }

  @Test
  void missingIpAndInvalidRequiredIpStateNeverEscapeAsDefaultOrSuccessfulSnapshot() {
    Fixture missing = new Fixture();
    missing.ipPresent = false;
    catalog(() -> lock(missing, NAME, NOW));
    missing.assertClosed(3, 2);
    for (String column : List.of(FAILED_COUNT, IP_WINDOW)) {
      Fixture fixture = new Fixture();
      fixture.ip.put(column, null);
      catalog(() -> lock(fixture, NAME, NOW));
      fixture.assertClosed(3, 2);
    }
    Fixture malformed = new Fixture();
    malformed.ip.put(FAILED_COUNT, 11);
    catalog(() -> lock(malformed, NAME, NOW));
    malformed.assertClosed(3, 2);
    Fixture time = new Fixture();
    catalog(() -> lock(time, NAME, Instant.MAX));
    time.assertClosed(2, 1);
  }

  @Test
  void failureWritesIndependentFirstAndThresholdWindowGoldenBindings() {
    var repository = new LoginAttemptRepository();
    Fixture first = new Fixture();
    repository.recordFailure(
        first.connection(), snapshot(true, 0, 0, Optional.empty(), Optional.empty()), NOW);
    assertEquals(List.of(UPDATE_USER_SQL, UPDATE_IP_SQL), first.sqls());
    assertEquals(
        Map.of(1, 1, 2, UTC, 3, NULL_TIME, 4, false, 5, UTC, 6, 7L),
        first.statements.getFirst().bindings);
    assertEquals(
        Map.of(1, 1, 2, UTC, 3, NULL_TIME, 4, UTC, 5, IP), first.statements.getLast().bindings);
    first.assertClosed(2, 0);
    Fixture threshold = new Fixture();
    repository.recordFailure(
        threshold.connection(),
        snapshot(true, 4, 9, Optional.of(NOW.minusSeconds(900)), Optional.empty()),
        NOW);
    assertEquals(5, threshold.statements.getFirst().bindings.get(1));
    assertEquals(10, threshold.statements.getLast().bindings.get(1));
    assertEquals(
        NOW.minusSeconds(900).atOffset(ZoneOffset.UTC),
        threshold.statements.getFirst().bindings.get(2));
    assertEquals(
        NOW.plusSeconds(900).atOffset(ZoneOffset.UTC),
        threshold.statements.getFirst().bindings.get(3));
    assertEquals(
        NOW.plusSeconds(900).atOffset(ZoneOffset.UTC),
        threshold.statements.getLast().bindings.get(3));
    Fixture expired = new Fixture();
    repository.recordFailure(
        expired.connection(),
        snapshot(false, 0, 10, Optional.of(NOW.minusSeconds(901)), Optional.of(NOW)),
        NOW);
    assertEquals(List.of(UPDATE_IP_SQL), expired.sqls());
    assertEquals(1, expired.statements.getFirst().bindings.get(1));
    assertEquals(UTC, expired.statements.getFirst().bindings.get(2));
    Fixture backwards = new Fixture();
    catalog(
        () ->
            repository.recordFailure(
                backwards.connection(),
                snapshot(true, 1, 1, Optional.of(NOW.plusSeconds(1)), Optional.empty()),
                NOW));
    assertTrue(backwards.statements.isEmpty());
    Fixture date = new Fixture();
    catalog(
        () ->
            repository.recordFailure(
                date.connection(),
                snapshot(true, 0, 0, Optional.empty(), Optional.empty()),
                Instant.MAX));
    date.assertClosed(1, 0);
    assertFalse(date.events.contains("0:" + UPDATE));
  }

  @Test
  void successClearsUserWindowsAndMapsNonNullIpWindowToNow() {
    var repository = new LoginAttemptRepository();
    Fixture fixture = new Fixture();
    repository.recordSuccess(
        fixture.connection(),
        snapshot(true, 5, 10, Optional.of(NOW.minusSeconds(2)), Optional.of(NOW.plusSeconds(898))),
        NOW);
    assertEquals(
        Map.of(1, 0, 2, NULL_TIME, 3, NULL_TIME, 4, true, 5, UTC, 6, 7L),
        fixture.statements.getFirst().bindings);
    assertEquals(
        Map.of(1, 0, 2, UTC, 3, NULL_TIME, 4, UTC, 5, IP), fixture.statements.getLast().bindings);
    fixture.assertClosed(2, 0);
    Fixture noAccount = new Fixture();
    repository.recordSuccess(
        noAccount.connection(), snapshot(false, 0, 0, Optional.of(NOW), Optional.empty()), NOW);
    assertEquals(List.of(UPDATE_IP_SQL), noAccount.sqls());
    assertEquals(0, noAccount.statements.getFirst().bindings.get(1));
    assertEquals(UTC, noAccount.statements.getFirst().bindings.get(2));
  }

  @Test
  void unexpectedUserOrIpUpdateCountsRejectAndNeverTouchCallerLifetime() {
    for (int count : new int[] {Integer.MIN_VALUE, -1, 0, 2, Integer.MAX_VALUE}) {
      for (int failed : new int[] {0, 1}) {
        Fixture fixture = new Fixture();
        fixture.changed.put(failed, count);
        catalog(
            () ->
                new LoginAttemptRepository()
                    .recordSuccess(
                        fixture.connection(),
                        snapshot(true, 0, 0, Optional.empty(), Optional.empty()),
                        NOW));
        fixture.assertClosed(failed + 1, 0);
      }
    }
  }

  @Test
  void scriptedProviderFailuresCleanupAndHiddenFatalSelectionFollowBorrowedOwnership() {
    for (String point :
        List.of(
            "auto",
            "0:prepare",
            POINT_USER_BIND,
            "0:query",
            "0:next",
            "0:role",
            "0:status",
            "0:id",
            "0:username",
            "0:password_hash",
            "0:failed_count",
            "0:failure_window_started_at",
            "0:locked_until",
            "0:rowClose",
            "0:close",
            "1:prepare",
            "1:bind",
            "1:update",
            "1:close",
            "2:prepare",
            "2:query",
            "2:next",
            "2:failed_count",
            "2:window_started_at",
            "2:locked_until",
            "2:rowClose",
            "2:close")) {
      for (Throwable original : providerFailures()) {
        Fixture fixture = new Fixture();
        fixture.faults = Map.of(point, original);
        providerExpected(original, () -> lock(fixture, NAME, NOW));
        fixture.assertAllCreatedClosed();
      }
    }
    for (String point :
        List.of(
            "0:prepare",
            POINT_USER_BIND,
            "0:update",
            "0:close",
            "1:prepare",
            "1:bind",
            "1:update",
            "1:close")) {
      for (Throwable original : providerFailures()) {
        Fixture fixture = new Fixture();
        fixture.faults = Map.of(point, original);
        providerExpected(
            original,
            () ->
                new LoginAttemptRepository()
                    .recordFailure(
                        fixture.connection(),
                        snapshot(true, 0, 0, Optional.empty(), Optional.empty()),
                        NOW));
        fixture.assertAllCreatedClosed();
      }
    }
    for (boolean reading : new boolean[] {false, true}) {
      Fixture fixture = new Fixture();
      AssertionError fatal = new AssertionError("own fatal fixture");
      fixture.faults = Map.of(POINT_USER_BIND, new SQLException("own primary SQL", fatal));
      assertSame(
          fatal,
          assertThrows(
              AssertionError.class,
              () -> {
                if (reading) lock(fixture, NAME, NOW);
                else
                  new LoginAttemptRepository()
                      .recordSuccess(
                          fixture.connection(),
                          snapshot(true, 0, 0, Optional.empty(), Optional.empty()),
                          NOW);
              }));
      fixture.assertAllCreatedClosed();
    }
    Fixture unknown = new Fixture();
    IllegalStateException primary = new IllegalStateException("own unknown fixture");
    unknown.faults = Map.of(POINT_USER_BIND, primary);
    assertSame(primary, assertThrows(IllegalStateException.class, () -> lock(unknown, NAME, NOW)));
    unknown.assertAllCreatedClosed();
  }

  @Test
  void concurrentIndependentAttemptsNeverShareBorrowedStatementsOrRowSnapshots() throws Exception {
    Fixture one = new Fixture();
    Fixture two = new Fixture();
    two.user.put("id", 8L);
    two.user.put(COLUMN_USERNAME, "second");
    try (var workers = Executors.newFixedThreadPool(2)) {
      var first = workers.submit(() -> lock(one, NAME, NOW));
      var second = workers.submit(() -> lock(two, "second", NOW));
      assertEquals(7, first.get(5, TimeUnit.SECONDS).account().orElseThrow().identity().userId());
      assertEquals(8, second.get(5, TimeUnit.SECONDS).account().orElseThrow().identity().userId());
    }
    assertEquals(NAME, one.statements.getFirst().bindings.get(1));
    assertEquals("second", two.statements.getFirst().bindings.get(1));
    one.assertClosed(3, 2);
    two.assertClosed(3, 2);
  }

  private static LockedLoginAttempt snapshot(
      boolean account,
      int userCount,
      int ipCount,
      Optional<Instant> window,
      Optional<Instant> locked) {
    return new LockedLoginAttempt(
        IP,
        account
            ? Optional.of(
                new LoginAccount(
                    new AuthenticatedActor(7, NAME, Role.USER),
                    true,
                    NON_CREDENTIAL,
                    new LoginAttemptState(LoginAttemptKind.USER, userCount, window, locked)))
            : Optional.empty(),
        new LoginAttemptState(LoginAttemptKind.IP, ipCount, window, locked));
  }

  private static InetAddress client() throws Exception {
    return InetAddress.getByAddress(new byte[] {127, 0, 0, 1});
  }

  private static LockedLoginAttempt lock(Fixture fixture, String name, Instant now)
      throws Exception {
    return new LoginAttemptRepository().lockForAttempt(fixture.connection(), name, client(), now);
  }

  private static List<Throwable> providerFailures() {
    return List.of(
        new SQLException("own provider SQL"),
        new IllegalStateException("own provider unknown"),
        new AssertionError("own provider Error"));
  }

  private static void providerExpected(Throwable original, Executable work) {
    if (original instanceof SQLException) catalog(work);
    else assertSame(original, assertThrows(original.getClass(), work));
  }

  private static void catalog(Executable work) {
    var failure = assertThrows(AuthenticationInfrastructureException.class, work);
    assertEquals("authentication storage is unavailable", failure.getMessage());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
  }

  private static final class Fixture {
    final Map<String, Object> user = new HashMap<>();
    final Map<String, Object> ip = new HashMap<>();
    final List<Statement> statements = new ArrayList<>();
    final List<String> events = new ArrayList<>();
    final Map<Integer, Integer> changed = new HashMap<>();
    Map<String, Throwable> faults = Map.of();
    boolean autoCommit;
    boolean userPresent = true;
    boolean ipPresent = true;
    int createCount = 1;

    Fixture() {
      user.putAll(
          Map.of(
              "id",
              7L,
              COLUMN_USERNAME,
              NAME,
              ROLE,
              "USER",
              STATUS,
              "ACTIVE",
              "password_hash",
              NON_CREDENTIAL,
              FAILED_COUNT,
              0));
      ip.putAll(Map.of(FAILED_COUNT, 0, IP_WINDOW, UTC));
    }

    void event(String point) throws Throwable {
      events.add(point);
      Throwable failure = faults.get(point);
      if (failure != null) throw failure;
    }

    Connection connection() {
      return (Connection)
          Proxy.newProxyInstance(
              Connection.class.getClassLoader(),
              new Class<?>[] {Connection.class},
              (proxy, method, args) -> {
                if (method.getName().equals("getAutoCommit")) {
                  event("auto");
                  return autoCommit;
                }
                if (!method.getName().equals("prepareStatement"))
                  throw new AssertionError("borrowed transaction lifetime mutated");
                int index = statements.size();
                event(index + ":" + PREPARE);
                var statement = new Statement(this, index, (String) args[0]);
                statements.add(statement);
                return statement.proxy();
              });
    }

    List<String> sqls() {
      return statements.stream().map(s -> s.sql).toList();
    }

    void assertAllCreatedClosed() {
      for (Statement statement : statements) {
        assertEquals(1, statement.closeAttempts);
        assertEquals(statement.queried ? 1 : 0, statement.rowCloseAttempts);
      }
    }

    void assertClosed(int statementCount, int rowCount) {
      assertEquals(statementCount, statements.size());
      assertAllCreatedClosed();
      assertEquals(rowCount, statements.stream().mapToInt(s -> s.rowCloseAttempts).sum());
    }
  }

  private static final class Statement {
    final Fixture fixture;
    final int index;
    final String sql;
    final Map<Integer, Object> bindings = new HashMap<>();
    boolean queried;
    int closeAttempts;
    int rowCloseAttempts;
    int nextCalls;

    Statement(Fixture fixture, int index, String sql) {
      this.fixture = fixture;
      this.index = index;
      this.sql = sql;
    }

    void event(String point) throws Throwable {
      fixture.event(index + ":" + point);
    }

    PreparedStatement proxy() {
      return (PreparedStatement)
          Proxy.newProxyInstance(
              PreparedStatement.class.getClassLoader(),
              new Class<?>[] {PreparedStatement.class},
              (proxy, method, args) -> {
                switch (method.getName()) {
                  case "setString", "setObject", "setInt", "setBoolean", "setLong" -> {
                    bindings.put((Integer) args[0], args[1]);
                    event(BIND);
                    return null;
                  }
                  case "setNull" -> {
                    assertEquals(Types.TIMESTAMP_WITH_TIMEZONE, args[1]);
                    bindings.put((Integer) args[0], NULL_TIME);
                    event(BIND);
                    return null;
                  }
                  case "executeUpdate" -> {
                    event(UPDATE);
                    return sql.equals(CREATE_SQL)
                        ? fixture.createCount
                        : fixture.changed.getOrDefault(index, 1);
                  }
                  case "executeQuery" -> {
                    event(QUERY);
                    queried = true;
                    return rows();
                  }
                  case "close" -> {
                    closeAttempts++;
                    event(CLOSE);
                    return null;
                  }
                  default -> throw new AssertionError("unexpected statement method");
                }
              });
    }

    ResultSet rows() {
      return (ResultSet)
          Proxy.newProxyInstance(
              ResultSet.class.getClassLoader(),
              new Class<?>[] {ResultSet.class},
              (proxy, method, args) -> {
                switch (method.getName()) {
                  case "next" -> {
                    event(NEXT);
                    nextCalls++;
                    return nextCalls == 1 && (index == 0 ? fixture.userPresent : fixture.ipPresent);
                  }
                  case "getString", "getObject" -> {
                    String column = (String) args[0];
                    event(column);
                    Object value = (index == 0 ? fixture.user : fixture.ip).get(column);
                    if (args.length == 2 && value != null)
                      assertTrue(((Class<?>) args[1]).isInstance(value));
                    return value;
                  }
                  case "close" -> {
                    rowCloseAttempts++;
                    event(ROW_CLOSE);
                    return null;
                  }
                  default -> throw new AssertionError("unexpected result method");
                }
              });
    }
  }
}
