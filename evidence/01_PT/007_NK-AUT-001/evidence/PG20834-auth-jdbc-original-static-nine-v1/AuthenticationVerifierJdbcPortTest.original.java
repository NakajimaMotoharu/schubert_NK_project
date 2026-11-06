package dev.codex.schubert.nk.api.security;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.api.domain.Role;
import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import java.lang.reflect.InvocationHandler;
import java.lang.reflect.Proxy;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.time.Instant;
import java.time.ZoneOffset;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Test;

/** PT-AUT-JDBC001..006; UI226/SS312314332. New interface fixture, never a DB connection. */
final class AuthenticationVerifierJdbcPortTest {
  private static final Instant NOW = Instant.parse("2026-11-06T00:00:00Z");
  // Public SHA-256 vector: 64 ASCII 'a', independently verified with Python hashlib.
  private static final AuthenticationContext INPUT = AuthenticationContext.of("a".repeat(64));
  private static final String HASH =
      "ffe054fe7ae0cb6dc65c3af9b61d5209f439851db43d0ba5997337df154668eb";
  private static final UUID STORED_ID = UUID.fromString("00000000-0000-4000-8000-000000000007");
  private static final String USER_LOCK =
      "select u.id from schubert.app_users u join schubert.auth_sessions s on s.user_id=u.id"
          + " where s.context_hash=? for update of u";
  private static final String READ =
      "select s.id,s.user_id,u.username,u.role,u.status,s.revoked,s.expires_at"
          + " from schubert.auth_sessions s join schubert.app_users u on u.id=s.user_id"
          + " where s.context_hash=?";
  private static final String SESSION_LOCK = READ + " for update of s";
  private static final String TOUCH =
      "update schubert.auth_sessions set last_accessed_at=greatest(last_accessed_at,?),"
          + "expires_at=greatest(expires_at,cast(? as timestamptz)+interval '8 hours')"
          + " where id=? and not revoked";
  private static final String INFRA_MESSAGE = "authentication storage is unavailable";
  private static final String CONTEXT_MESSAGE = "authentication context is not valid";
  private static final String PUBLIC_MARKER = "ordinary-jdbc-fixture-marker";

  private static <T> T proxy(Class<T> type, InvocationHandler handler) {
    return type.cast(Proxy.newProxyInstance(type.getClassLoader(), new Class<?>[] {type}, handler));
  }

  private static final class Fixture {
    final Map<String, Object> fields = new HashMap<>();
    final List<String> sql = new ArrayList<>();
    final List<Map<Integer, Object>> bindings = new ArrayList<>();
    final List<String> closes = new ArrayList<>();
    final List<String> closeFailures = new ArrayList<>();
    boolean autoCommit;
    boolean readOnly;
    boolean userExists = true;
    boolean sessionExists = true;
    int affected = 1;
    int forbiddenOwnerCalls;
    String failMethod = "";
    RuntimeException runtimeFailure;

    Fixture() {
      fields.put("id", STORED_ID);
      fields.put("user_id", 7L);
      fields.put("username", "fixture-reader");
      fields.put("role", "USER");
      fields.put("status", "ACTIVE");
      fields.put("revoked", false);
      fields.put("expires_at", NOW.plusSeconds(28_800).atOffset(ZoneOffset.UTC));
    }

    void fault(String method) throws SQLException {
      if (method.equals(failMethod)) {
        if (runtimeFailure != null) throw runtimeFailure;
        throw new SQLException(PUBLIC_MARKER, "08006");
      }
    }

    Connection connection() {
      return proxy(
          Connection.class,
          (p, m, args) -> {
            fault(m.getName());
            return switch (m.getName()) {
              case "getAutoCommit" -> autoCommit;
              case "isReadOnly" -> readOnly;
              case "prepareStatement" -> statement((String) args[0]);
              case "commit", "rollback", "close", "setAutoCommit", "setReadOnly" -> {
                forbiddenOwnerCalls++;
                throw new AssertionError("borrowed connection ownership changed");
              }
              case "toString" -> "OwnedMemoryJdbcConnection";
              default -> throw new AssertionError("unregistered Connection method " + m.getName());
            };
          });
    }

    PreparedStatement statement(String actual) {
      assertTrue(List.of(USER_LOCK, SESSION_LOCK, READ, TOUCH).contains(actual));
      sql.add(actual);
      var bound = new HashMap<Integer, Object>();
      bindings.add(bound);
      String name = actual.equals(USER_LOCK) ? "user" : actual.equals(TOUCH) ? "touch" : "session";
      return proxy(
          PreparedStatement.class,
          (p, m, args) -> {
            fault(m.getName());
            return switch (m.getName()) {
              case "setString", "setObject" -> {
                bound.put((Integer) args[0], args[1]);
                yield null;
              }
              case "executeQuery" -> row(name);
              case "executeUpdate" -> affected;
              case "close" -> {
                close(name + ".statement");
                yield null;
              }
              default -> throw new AssertionError("unregistered statement method " + m.getName());
            };
          });
    }

    ResultSet row(String name) {
      return proxy(
          ResultSet.class,
          (p, m, args) -> {
            fault(m.getName());
            return switch (m.getName()) {
              case "next" -> name.equals("user") ? userExists : sessionExists;
              case "getString" -> fields.get((String) args[0]);
              case "getObject" -> {
                var value = fields.get((String) args[0]);
                if (value != null) assertTrue(((Class<?>) args[1]).isInstance(value));
                yield value;
              }
              case "close" -> {
                close(name + ".row");
                yield null;
              }
              default -> throw new AssertionError("unregistered row method " + m.getName());
            };
          });
    }

    void close(String name) throws SQLException {
      closes.add(name);
      if (closeFailures.contains(name)) throw new SQLException(PUBLIC_MARKER, "08006");
    }
  }

  private static void fixedInfrastructure(Runnable call) {
    var failure = assertThrows(AuthenticationInfrastructureException.class, call::run);
    assertEquals(INFRA_MESSAGE, failure.getMessage());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
    assertFalse(failure.getMessage().contains(PUBLIC_MARKER));
  }

  private static void denied(Runnable call) {
    var failure = assertThrows(AuthenticationContextException.class, call::run);
    assertEquals(CONTEXT_MESSAGE, failure.getMessage());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
  }

  @Test
  void writerUsesCurrentActorLockOrderUtcBindingsAndBorrowedTransaction() throws Exception {
    var verifier = new AuthenticationContextVerifier(new ContextHash());
    for (Role role : Role.values()) {
      var f = new Fixture();
      f.fields.put("role", role.name());
      f.fields.put("username", "current-" + role.name());
      var actor = verifier.verify(f.connection(), INPUT, NOW);
      assertEquals(new AuthenticatedActor(7, "current-" + role.name(), role), actor);
      assertEquals(List.of(USER_LOCK, SESSION_LOCK, TOUCH), f.sql);
      assertEquals(Map.of(1, HASH), f.bindings.get(0));
      assertEquals(Map.of(1, HASH), f.bindings.get(1));
      assertEquals(
          Map.of(1, NOW.atOffset(ZoneOffset.UTC), 2, NOW.atOffset(ZoneOffset.UTC), 3, STORED_ID),
          f.bindings.get(2));
      assertEquals(
          List.of(
              "user.row", "user.statement", "session.row", "session.statement", "touch.statement"),
          f.closes);
      assertEquals(0, f.forbiddenOwnerCalls);
    }
  }

  @Test
  void readOnlyPreflightNeverLocksTouchesOrChangesConnectionMode() throws Exception {
    var verifier = new AuthenticationContextVerifier(new ContextHash());
    var f = new Fixture();
    f.readOnly = true;
    assertEquals(
        new AuthenticatedActor(7, "fixture-reader", Role.USER),
        verifier.inspectReadOnly(f.connection(), INPUT, NOW));
    assertEquals(List.of(READ), f.sql);
    assertEquals(Map.of(1, HASH), f.bindings.get(0));
    assertEquals(List.of("session.row", "session.statement"), f.closes);
    assertEquals(0, f.forbiddenOwnerCalls);
    for (boolean auto : List.of(false, true)) {
      for (boolean ro : List.of(false, true)) {
        if (!auto && ro) continue;
        var bad = new Fixture();
        bad.autoCommit = auto;
        bad.readOnly = ro;
        fixedInfrastructure(() -> verifier.inspectReadOnly(bad.connection(), INPUT, NOW));
        assertTrue(bad.sql.isEmpty());
      }
    }
  }

  @Test
  void missingRevokedExpiredAndDisabledRowsNeverReachTouch() throws Exception {
    var verifier = new AuthenticationContextVerifier(new ContextHash());
    for (boolean inspect : List.of(false, true)) {
      for (String condition : List.of("missing", "revoked", "equal", "past", "disabled")) {
        var f = new Fixture();
        f.readOnly = inspect;
        switch (condition) {
          case "missing" -> f.sessionExists = false;
          case "revoked" -> f.fields.put("revoked", true);
          case "equal" -> f.fields.put("expires_at", NOW.atOffset(ZoneOffset.UTC));
          case "past" -> f.fields.put("expires_at", NOW.minusNanos(1).atOffset(ZoneOffset.UTC));
          case "disabled" -> f.fields.put("status", "DISABLED");
          default -> throw new AssertionError(condition);
        }
        denied(
            () -> {
              if (inspect) verifier.inspectReadOnly(f.connection(), INPUT, NOW);
              else verifier.verify(f.connection(), INPUT, NOW);
            });
        assertFalse(f.sql.contains(TOUCH));
        assertEquals(0, f.forbiddenOwnerCalls);
      }
    }
    var absent = new Fixture();
    absent.userExists = false;
    denied(() -> verifier.verify(absent.connection(), INPUT, NOW));
    assertEquals(List.of(USER_LOCK), absent.sql);
  }

  @Test
  void nullColumnsUnknownRoleAffectedRowsAndApiNullsFailClosed() throws Exception {
    var verifier = new AuthenticationContextVerifier(new ContextHash());
    assertThrows(NullPointerException.class, () -> new AuthenticationContextVerifier(null));
    for (boolean inspect : List.of(false, true)) {
      for (String key :
          List.of("revoked", "expires_at", "status", "id", "user_id", "username", "role")) {
        var f = new Fixture();
        f.readOnly = inspect;
        f.fields.put(key, null);
        fixedInfrastructure(
            () -> {
              if (inspect) verifier.inspectReadOnly(f.connection(), INPUT, NOW);
              else verifier.verify(f.connection(), INPUT, NOW);
            });
        assertFalse(f.sql.contains(TOUCH));
      }
      var role = new Fixture();
      role.readOnly = inspect;
      role.fields.put("role", "UNKNOWN");
      fixedInfrastructure(
          () -> {
            if (inspect) verifier.inspectReadOnly(role.connection(), INPUT, NOW);
            else verifier.verify(role.connection(), INPUT, NOW);
          });
      var f = new Fixture();
      f.readOnly = inspect;
      if (inspect) {
        assertThrows(NullPointerException.class, () -> verifier.inspectReadOnly(null, INPUT, NOW));
        assertThrows(
            NullPointerException.class, () -> verifier.inspectReadOnly(f.connection(), null, NOW));
        assertThrows(
            NullPointerException.class,
            () -> verifier.inspectReadOnly(f.connection(), INPUT, null));
      } else {
        assertThrows(NullPointerException.class, () -> verifier.verify(null, INPUT, NOW));
        assertThrows(NullPointerException.class, () -> verifier.verify(f.connection(), null, NOW));
        assertThrows(
            NullPointerException.class, () -> verifier.verify(f.connection(), INPUT, null));
      }
      assertTrue(f.sql.isEmpty());
    }
    for (int count : new int[] {0, 2}) {
      var f = new Fixture();
      f.affected = count;
      fixedInfrastructure(() -> verifier.verify(f.connection(), INPUT, NOW));
      assertEquals("touch.statement", f.closes.getLast());
    }
    var auto = new Fixture();
    auto.autoCommit = true;
    fixedInfrastructure(() -> verifier.verify(auto.connection(), INPUT, NOW));
    assertTrue(auto.sql.isEmpty());
  }

  @Test
  void ordinaryJdbcCloseFaultsPreserveCleanupAndUnknownIdentity() throws Exception {
    var verifier = new AuthenticationContextVerifier(new ContextHash());
    for (String position :
        List.of(
            "getAutoCommit",
            "prepareStatement",
            "setString",
            "executeQuery",
            "getObject",
            "getString",
            "setObject",
            "executeUpdate")) {
      var f = new Fixture();
      f.failMethod = position;
      fixedInfrastructure(() -> verifier.verify(f.connection(), INPUT, NOW));
      assertEquals(0, f.forbiddenOwnerCalls);
    }
    for (boolean inspect : List.of(false, true)) {
      for (boolean primaryDenied : List.of(false, true)) {
        var f = new Fixture();
        f.readOnly = inspect;
        f.fields.put("revoked", primaryDenied);
        f.closeFailures.add("session.row");
        f.closeFailures.add("session.statement");
        fixedInfrastructure(
            () -> {
              if (inspect) verifier.inspectReadOnly(f.connection(), INPUT, NOW);
              else verifier.verify(f.connection(), INPUT, NOW);
            });
        assertEquals(
            List.of("session.row", "session.statement"),
            f.closes.subList(f.closes.size() - 2, f.closes.size()));
        assertFalse(f.sql.contains(TOUCH));
      }
    }
    var unknown = new Fixture();
    unknown.failMethod = "getObject";
    var marker = new IllegalStateException(PUBLIC_MARKER);
    unknown.runtimeFailure = marker;
    assertSame(
        marker,
        assertThrows(
            IllegalStateException.class, () -> verifier.verify(unknown.connection(), INPUT, NOW)));
    assertEquals(
        List.of("user.row", "user.statement", "session.row", "session.statement"), unknown.closes);
  }

  @Test
  void parallelFreshRowsDoNotShareActorOrTransactionState() throws Exception {
    var verifier = new AuthenticationContextVerifier(new ContextHash());
    var results = new ArrayList<Future<Long>>();
    try (var executor = Executors.newFixedThreadPool(2)) {
      for (long id = 1; id <= 32; id++) {
        long expected = id;
        results.add(
            executor.submit(
                () -> {
                  var f = new Fixture();
                  f.fields.put("user_id", expected);
                  var actor = verifier.verify(f.connection(), INPUT, NOW);
                  assertEquals(Map.of(1, HASH), f.bindings.get(0));
                  assertEquals(0, f.forbiddenOwnerCalls);
                  return actor.userId();
                }));
      }
      for (int index = 0; index < 32; index++)
        assertEquals((long) index + 1, results.get(index).get(10, TimeUnit.SECONDS));
    }
  }
}
