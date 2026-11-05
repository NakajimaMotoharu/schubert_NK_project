package dev.codex.schubert.nk.api.security;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.google.gson.JsonParser;
import dev.codex.schubert.nk.api.domain.Role;
import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.header.ResultCode;
import java.lang.reflect.Proxy;
import java.net.InetAddress;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.SQLException;
import java.sql.Types;
import java.time.Instant;
import java.time.ZoneOffset;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Test;

/** PT-AUT-AUDITPORT001..007. Pure caller-owned JDBC ports; no provider or issued credentials. */
final class LoginAuditPortTest {
  private static final String SQL =
      "insert into schubert.app_logs"
          + " (logged_at,service,category,level,action,message,message_id,correlation_id,actor_user_id,actor_username,remote_address,details)"
          + " values(?,'API','SECURITY',?,?,?,?,?,?,?,cast(? as inet),cast(? as jsonb))";
  private static final String PREPARE = "prepare";
  private static final String CLOSE = "close";
  private static final String EXECUTE = "execute";
  private static final String BIND = "bind";
  private static final String USER = "audit-user";
  private static final Instant NOW = Instant.parse("2026-11-05T01:02:03.123456Z");
  private static final UUID MESSAGE = new UUID(0, 1);
  private static final UUID CORRELATION = new UUID(0, 2);
  private static final LoginResult DENIED =
      new LoginResult.Failure(ResultCode.AUTHENTICATION_FAILED, 0);

  @Test
  void successLiteralSqlAndTenBindingsExcludeSessionOrCredentialData() throws Exception {
    Fixture fixture = new Fixture();
    write(fixture, accepted(), LoginAuditReason.SUCCEEDED, USER);
    assertEquals(SQL, fixture.sql);
    assertEquals(
        Map.of(
            1,
            NOW.atOffset(ZoneOffset.UTC),
            2,
            "INFO",
            3,
            "LOGIN_SUCCEEDED",
            4,
            "LOGIN_SUCCEEDED",
            5,
            MESSAGE,
            6,
            CORRELATION,
            7,
            7L,
            8,
            USER,
            9,
            "127.0.0.1"),
        withoutDetails(fixture));
    assertEquals(
        "{\"resultCode\":\"0000\",\"reason\":\"SUCCEEDED\",\"retryAfterSeconds\":0,\"outcome\":\"SUCCESS\"}",
        fixture.bindings.get(10));
    detailsOnly(fixture);
    assertEquals(1, fixture.closeAttempts);
    assertEquals(1, fixture.updates);
    assertEquals(
        List.of(
            PREPARE, BIND, BIND, BIND, BIND, BIND, BIND, BIND, BIND, BIND, BIND, EXECUTE, CLOSE),
        fixture.events);
  }

  @Test
  void deniedAndLockedReasonsKeepExactClosedJsonAndNullActor() throws Exception {
    for (LoginAuditReason reason :
        List.of(
            LoginAuditReason.NO_ACCOUNT,
            LoginAuditReason.DISABLED,
            LoginAuditReason.PASSWORD_MISMATCH,
            LoginAuditReason.PREEXISTING_LOCK)) {
      for (int retry : new int[] {0, 1, 900}) {
        Fixture fixture = new Fixture();
        LoginResult result =
            retry == 0 ? DENIED : new LoginResult.Failure(ResultCode.LOCKED, retry);
        write(fixture, result, reason, USER);
        String action = retry == 0 ? "LOGIN_FAILED" : "LOGIN_LOCKED";
        assertEquals("WARN", fixture.bindings.get(2));
        assertEquals(action, fixture.bindings.get(3));
        assertEquals(action, fixture.bindings.get(4));
        assertEquals("NULL_BIGINT", fixture.bindings.get(7));
        var details = JsonParser.parseString((String) fixture.bindings.get(10)).getAsJsonObject();
        assertEquals(retry == 0 ? "0101" : "0106", details.get("resultCode").getAsString());
        assertEquals(reason.name(), details.get("reason").getAsString());
        assertEquals(retry, details.get("retryAfterSeconds").getAsInt());
        assertEquals("DENIED", details.get("outcome").getAsString());
        detailsOnly(fixture);
        assertEquals(1, fixture.closeAttempts);
      }
    }
  }

  @Test
  void displayUsernameUsesNfcAndSingleSpaceForEveryForbiddenControl() throws Exception {
    Fixture fixture = new Fixture();
    write(fixture, DENIED, LoginAuditReason.NO_ACCOUNT, "e\u0301\r\n\t\u2028\u2029Z");
    assertEquals("é     Z", fixture.bindings.get(8));
    assertEquals(10, fixture.bindings.size());
    assertEquals(1, fixture.updates);
    assertEquals(1, fixture.closeAttempts);
  }

  @Test
  void allNonOneCountsRejectBeforeCallerCanCommitAndCloseStatement() {
    for (int changed : new int[] {Integer.MIN_VALUE, -1, 0, 2, Integer.MAX_VALUE}) {
      Fixture fixture = new Fixture();
      fixture.changed = changed;
      SQLException failure =
          assertThrows(
              SQLException.class, () -> write(fixture, DENIED, LoginAuditReason.NO_ACCOUNT, USER));
      assertEquals("critical login audit did not create one row", failure.getMessage());
      assertEquals("40001", failure.getSQLState());
      assertEquals(1, fixture.updates);
      assertEquals(1, fixture.closeAttempts);
    }
  }

  @Test
  void providerFailuresPreserveIdentityAndTwrSecondaryWhileBorrowedConnectionIsUntouched() {
    for (String point : List.of(PREPARE, BIND, EXECUTE, CLOSE)) {
      for (Throwable original : failures()) {
        Fixture fixture = new Fixture();
        fixture.faults = Map.of(point, original);
        Throwable actual =
            assertThrows(
                original.getClass(),
                () -> write(fixture, DENIED, LoginAuditReason.NO_ACCOUNT, USER));
        assertSame(original, actual);
        assertEquals(point.equals(PREPARE) ? 0 : 1, fixture.closeAttempts);
      }
    }
    for (int kind = 0; kind < 3; kind++) {
      for (Throwable secondary : failures()) {
        Throwable primary = failures().get(kind);
        Fixture fixture = new Fixture();
        fixture.faults = Map.of(EXECUTE, primary, CLOSE, secondary);
        assertSame(
            primary,
            assertThrows(
                primary.getClass(),
                () -> write(fixture, DENIED, LoginAuditReason.NO_ACCOUNT, USER)));
        assertEquals(1, primary.getSuppressed().length);
        assertSame(secondary, primary.getSuppressed()[0]);
        assertEquals(1, fixture.closeAttempts);
      }
    }
  }

  @Test
  void nullCallerContractIsRejectedAndAnAcquiredStatementStillCloses() throws Exception {
    Fixture result = new Fixture();
    assertThrows(
        NullPointerException.class, () -> write(result, null, LoginAuditReason.NO_ACCOUNT, USER));
    assertNull(result.sql);
    Fixture name = new Fixture();
    assertThrows(
        NullPointerException.class, () -> write(name, DENIED, LoginAuditReason.NO_ACCOUNT, null));
    assertNull(name.sql);
    Fixture clock = new Fixture();
    assertThrows(
        NullPointerException.class,
        () ->
            new LoginAuditWriter()
                .write(
                    clock.connection(),
                    DENIED,
                    LoginAuditReason.NO_ACCOUNT,
                    USER,
                    client(),
                    MESSAGE,
                    CORRELATION,
                    null));
    assertEquals(1, clock.closeAttempts);
    Fixture address = new Fixture();
    assertThrows(
        NullPointerException.class,
        () ->
            new LoginAuditWriter()
                .write(
                    address.connection(),
                    DENIED,
                    LoginAuditReason.NO_ACCOUNT,
                    USER,
                    null,
                    MESSAGE,
                    CORRELATION,
                    NOW));
    assertEquals(1, address.closeAttempts);
    assertEquals(0, address.updates);
    assertThrows(
        NullPointerException.class,
        () ->
            new LoginAuditWriter()
                .write(
                    null,
                    DENIED,
                    LoginAuditReason.NO_ACCOUNT,
                    USER,
                    client(),
                    MESSAGE,
                    CORRELATION,
                    NOW));
  }

  @Test
  void concurrentWriterUsesOnlyEachCallersSeparateStatement() throws Exception {
    Fixture first = new Fixture();
    Fixture second = new Fixture();
    try (var workers = Executors.newFixedThreadPool(2)) {
      var one =
          workers.submit(
              () -> {
                write(first, DENIED, LoginAuditReason.NO_ACCOUNT, USER);
                return true;
              });
      var two =
          workers.submit(
              () -> {
                write(second, accepted(), LoginAuditReason.SUCCEEDED, "second");
                return true;
              });
      assertTrue(one.get(5, TimeUnit.SECONDS));
      assertTrue(two.get(5, TimeUnit.SECONDS));
    }
    assertEquals(USER, first.bindings.get(8));
    assertEquals("second", second.bindings.get(8));
    assertEquals("WARN", first.bindings.get(2));
    assertEquals("INFO", second.bindings.get(2));
    assertEquals(1, first.closeAttempts);
    assertEquals(1, second.closeAttempts);
  }

  private static InetAddress client() throws Exception {
    return InetAddress.getByAddress(new byte[] {127, 0, 0, 1});
  }

  private static LoginResult accepted() {
    // Deliberately nonissued pure DTO. No context value or session UUID is projected/logged.
    return new LoginResult.Success(
        new AuthenticatedActor(7, USER, Role.USER),
        new IssuedContext(
            new AuthContextIdentity(new UUID(0, 0), 7),
            AuthenticationContext.of("0".repeat(64)),
            NOW,
            NOW.plusSeconds(1)));
  }

  private static void write(
      Fixture fixture, LoginResult result, LoginAuditReason reason, String username)
      throws Exception {
    new LoginAuditWriter()
        .write(fixture.connection(), result, reason, username, client(), MESSAGE, CORRELATION, NOW);
  }

  private static Map<Integer, Object> withoutDetails(Fixture fixture) {
    Map<Integer, Object> values = new HashMap<>(fixture.bindings);
    values.remove(10);
    return values;
  }

  private static void detailsOnly(Fixture fixture) {
    var details = JsonParser.parseString((String) fixture.bindings.get(10)).getAsJsonObject();
    assertEquals(Set.of("resultCode", "reason", "retryAfterSeconds", "outcome"), details.keySet());
    assertFalse(SQL.contains("password"));
    assertFalse(SQL.contains("session_id"));
    assertFalse(SQL.contains("context"));
  }

  private static List<Throwable> failures() {
    return List.of(
        new SQLException("own SQL fixture", "08006"),
        new IllegalStateException("own runtime fixture"),
        new AssertionError("own error fixture"));
  }

  private static final class Fixture {
    final Map<Integer, Object> bindings = new HashMap<>();
    final List<String> events = new ArrayList<>();
    Map<String, Throwable> faults = Map.of();
    String sql;
    int changed = 1;
    int updates;
    int closeAttempts;

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
                if (!method.getName().equals("prepareStatement"))
                  throw new AssertionError("borrowed connection lifetime mutated");
                sql = (String) args[0];
                event(PREPARE);
                return statement();
              });
    }

    PreparedStatement statement() {
      return (PreparedStatement)
          Proxy.newProxyInstance(
              PreparedStatement.class.getClassLoader(),
              new Class<?>[] {PreparedStatement.class},
              (proxy, method, args) -> {
                switch (method.getName()) {
                  case "setObject", "setString", "setLong" -> {
                    bindings.put((Integer) args[0], args[1]);
                    event(BIND);
                    return null;
                  }
                  case "setNull" -> {
                    assertEquals(Types.BIGINT, args[1]);
                    bindings.put((Integer) args[0], "NULL_BIGINT");
                    event(BIND);
                    return null;
                  }
                  case "executeUpdate" -> {
                    updates++;
                    event(EXECUTE);
                    return changed;
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
  }
}
