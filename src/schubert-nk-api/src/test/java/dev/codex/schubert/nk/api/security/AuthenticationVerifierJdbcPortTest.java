package dev.codex.schubert.nk.api.security;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
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
import org.jspecify.annotations.Nullable;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Timeout;

/** PT-AUT-JDBC001..006; UI226/SS312314332. New interface fixture, never a DB connection. */
@Timeout(value = 30, threadMode = Timeout.ThreadMode.SEPARATE_THREAD)
final class AuthenticationVerifierJdbcPortTest {
  private static final String JDBC_GET_AUTO_COMMIT = "getAutoCommit";
  private static final String JDBC_PREPARE_STATEMENT = "prepareStatement";
  private static final String JDBC_SET_STRING = "setString";
  private static final String JDBC_EXECUTE_QUERY = "executeQuery";
  private static final String JDBC_GET_OBJECT = "getObject";
  private static final String JDBC_GET_STRING = "getString";
  private static final String PUBLIC_SQL_STATE = "08006";
  private static final String CLOSE_SUFFIX = ".close";

  private static final String USER_LABEL = "user";
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
  private static final String COL_ROLE = "role";
  private static final String COL_REVOKED = "revoked";
  private static final String COL_EXPIRES = "expires_at";
  private static final String USER_ROW = "user.row";
  private static final String USER_STATEMENT = "user.statement";
  private static final String SESSION_ROW = "session.row";
  private static final String SESSION_STATEMENT = "session.statement";
  private static final String TOUCH_STATEMENT = "touch.statement";

  private static <T> T proxy(Class<T> type, InvocationHandler handler) {
    return type.cast(Proxy.newProxyInstance(type.getClassLoader(), new Class<?>[] {type}, handler));
  }

  private static final class Fixture {
    final Map<String, @Nullable Object> fields = new HashMap<>();
    final List<String> sql = new ArrayList<>();
    final List<Map<Integer, Object>> bindings = new ArrayList<>();
    final List<String> closes = new ArrayList<>();
    final List<String> acquired = new ArrayList<>();
    final List<String> closeFailures = new ArrayList<>();
    boolean autoCommit;
    boolean readOnly;
    boolean userExists = true;
    boolean sessionExists = true;
    int affected = 1;
    int forbiddenOwnerCalls;
    final Map<String, Throwable> injectedFailures = new HashMap<>();
    String failMethod = "";
    String nullStatementAt = "";
    String nullRowAt = "";
    @Nullable RuntimeException runtimeFailure;

    Fixture() {
      fields.put("id", STORED_ID);
      fields.put("user_id", 7L);
      fields.put("username", "fixture-reader");
      fields.put(COL_ROLE, "USER");
      fields.put("status", "ACTIVE");
      fields.put(COL_REVOKED, false);
      fields.put(COL_EXPIRES, NOW.plusSeconds(28_800).atOffset(ZoneOffset.UTC));
    }

    void fault(String method) throws SQLException {
      Throwable injected = injectedFailures.get(method);
      if (injected instanceof SQLException sqlFailure) throw sqlFailure;
      if (injected instanceof RuntimeException runtime) throw runtime;
      if (injected instanceof Error fatal) throw fatal;
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
              case JDBC_GET_AUTO_COMMIT -> autoCommit;
              case "isReadOnly" -> readOnly;
              case JDBC_PREPARE_STATEMENT -> statement((String) args[0]);
              case "commit", "rollback", "close", "setAutoCommit", "setReadOnly" -> {
                forbiddenOwnerCalls++;
                throw new AssertionError("borrowed connection ownership changed");
              }
              case "toString" -> "OwnedMemoryJdbcConnection";
              default -> throw new AssertionError("unregistered Connection method " + m.getName());
            };
          });
    }

    @Nullable PreparedStatement statement(String actual) {
      assertTrue(List.of(USER_LOCK, SESSION_LOCK, READ, TOUCH).contains(actual));
      sql.add(actual);
      var bound = new HashMap<Integer, Object>();
      bindings.add(bound);
      String name = actual.equals(USER_LOCK) ? "user" : actual.equals(TOUCH) ? "touch" : "session";
      if (actual.equals(nullStatementAt)) return null;
      acquired.add(name + ".statement");
      return proxy(
          PreparedStatement.class,
          (p, m, args) -> {
            fault(m.getName());
            return switch (m.getName()) {
              case JDBC_SET_STRING, "setObject" -> {
                bound.put((Integer) args[0], args[1]);
                yield null;
              }
              case JDBC_EXECUTE_QUERY -> row(name);
              case "executeUpdate" -> affected;
              case "close" -> {
                close(name + ".statement");
                yield null;
              }
              default -> throw new AssertionError("unregistered statement method " + m.getName());
            };
          });
    }

    @Nullable ResultSet row(String name) {
      if (name.equals(nullRowAt)) return null;
      acquired.add(name + ".row");
      return proxy(
          ResultSet.class,
          (p, m, args) -> {
            fault(m.getName());
            return switch (m.getName()) {
              case "next" -> name.equals("user") ? userExists : sessionExists;
              case JDBC_GET_STRING -> fields.get((String) args[0]);
              case JDBC_GET_OBJECT -> {
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
      fault(name + CLOSE_SUFFIX);
      if (closeFailures.contains(name)) throw new SQLException(PUBLIC_MARKER, "08006");
    }

    void owned() {
      assertEquals(0, forbiddenOwnerCalls);
      assertEquals(acquired.size(), closes.size());
      for (String name : acquired) assertEquals(1, closes.stream().filter(name::equals).count());
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
      f.fields.put(COL_ROLE, role.name());
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
          List.of(USER_ROW, USER_STATEMENT, SESSION_ROW, SESSION_STATEMENT, TOUCH_STATEMENT),
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
    assertEquals(List.of(SESSION_ROW, SESSION_STATEMENT), f.closes);
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
      for (String condition : List.of("missing", COL_REVOKED, "equal", "past", "disabled")) {
        var f = new Fixture();
        f.readOnly = inspect;
        switch (condition) {
          case "missing" -> f.sessionExists = false;
          case COL_REVOKED -> f.fields.put(COL_REVOKED, true);
          case "equal" -> f.fields.put(COL_EXPIRES, NOW.atOffset(ZoneOffset.UTC));
          case "past" -> f.fields.put(COL_EXPIRES, NOW.minusNanos(1).atOffset(ZoneOffset.UTC));
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
          List.of(COL_REVOKED, COL_EXPIRES, "status", "id", "user_id", "username", COL_ROLE)) {
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
      role.fields.put(COL_ROLE, "UNKNOWN");
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
      assertEquals(TOUCH_STATEMENT, f.closes.getLast());
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
            JDBC_GET_AUTO_COMMIT,
            JDBC_PREPARE_STATEMENT,
            JDBC_SET_STRING,
            JDBC_EXECUTE_QUERY,
            JDBC_GET_OBJECT,
            JDBC_GET_STRING,
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
        f.fields.put(COL_REVOKED, primaryDenied);
        f.closeFailures.add(SESSION_ROW);
        f.closeFailures.add(SESSION_STATEMENT);
        fixedInfrastructure(
            () -> {
              if (inspect) verifier.inspectReadOnly(f.connection(), INPUT, NOW);
              else verifier.verify(f.connection(), INPUT, NOW);
            });
        assertEquals(
            List.of(SESSION_ROW, SESSION_STATEMENT),
            f.closes.subList(f.closes.size() - 2, f.closes.size()));
        assertFalse(f.sql.contains(TOUCH));
      }
    }
    for (String position :
        List.of(USER_ROW, USER_STATEMENT, SESSION_ROW, SESSION_STATEMENT, TOUCH_STATEMENT)) {
      var f = new Fixture();
      f.closeFailures.add(position);
      fixedInfrastructure(() -> verifier.verify(f.connection(), INPUT, NOW));
      List<String> expected =
          position.startsWith("user.")
              ? List.of(USER_ROW, USER_STATEMENT)
              : position.equals(TOUCH_STATEMENT)
                  ? List.of(
                      USER_ROW, USER_STATEMENT, SESSION_ROW, SESSION_STATEMENT, TOUCH_STATEMENT)
                  : List.of(USER_ROW, USER_STATEMENT, SESSION_ROW, SESSION_STATEMENT);
      assertEquals(expected, f.closes);
      assertEquals(0, f.forbiddenOwnerCalls);
    }
    var unknown = new Fixture();
    unknown.failMethod = JDBC_GET_OBJECT;
    var marker = new IllegalStateException(PUBLIC_MARKER);
    unknown.runtimeFailure = marker;
    assertSame(
        marker,
        assertThrows(
            IllegalStateException.class, () -> verifier.verify(unknown.connection(), INPUT, NOW)));
    assertEquals(List.of(USER_ROW, USER_STATEMENT, SESSION_ROW, SESSION_STATEMENT), unknown.closes);
  }

  @Test
  void parallelFreshRowsDoNotShareActorOrTransactionState() throws Exception {
    var verifier = new AuthenticationContextVerifier(new ContextHash());
    var results = new ArrayList<Future<Long>>();
    var executor = Executors.newFixedThreadPool(2);
    try {
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
    } finally {
      executor.shutdownNow();
      assertTrue(executor.awaitTermination(10, TimeUnit.SECONDS));
    }
  }

  @Test
  void resource001NullStatementsFailClosedBeforeAnyLaterStatement() throws Exception {
    var verifier = new AuthenticationContextVerifier(new ContextHash());
    for (boolean inspect : List.of(false, true)) {
      for (String sql : inspect ? List.of(READ) : List.of(USER_LOCK, SESSION_LOCK, TOUCH)) {
        var f = new Fixture();
        f.readOnly = inspect;
        f.nullStatementAt = sql;
        fixedInfrastructure(
            () -> {
              if (inspect) verifier.inspectReadOnly(f.connection(), INPUT, NOW);
              else verifier.verify(f.connection(), INPUT, NOW);
            });
        assertEquals(sql, f.sql.getLast());
        f.owned();
      }
    }
  }

  @Test
  void resource002NullRowsCloseOnlyThePreviouslyAcquiredResourcesExactlyOnce() throws Exception {
    var verifier = new AuthenticationContextVerifier(new ContextHash());
    for (boolean inspect : List.of(false, true)) {
      for (String label : inspect ? List.of("session") : List.of(USER_LABEL, "session")) {
        var f = new Fixture();
        f.readOnly = inspect;
        f.nullRowAt = label;
        fixedInfrastructure(
            () -> {
              if (inspect) verifier.inspectReadOnly(f.connection(), INPUT, NOW);
              else verifier.verify(f.connection(), INPUT, NOW);
            });
        assertEquals(
            inspect ? READ : label.equals(USER_LABEL) ? USER_LOCK : SESSION_LOCK, f.sql.getLast());
        f.owned();
      }
    }
  }

  @Test
  void roleCollision001WrongRoleStringsWithEqualHashesStillFailClosedInBothModes()
      throws Exception {
    // Independent ASCII 31-polynomial golden values; these are fixture preconditions only.
    assertEquals(2_614_219, "USER".hashCode());
    assertEquals(2_614_219, "V4ER".hashCode());
    assertEquals(62_130_991, "ADMIN".hashCode());
    assertEquals(62_130_991, "B%MIN".hashCode());
    var verifier = new AuthenticationContextVerifier(new ContextHash());
    for (boolean inspect : List.of(false, true)) {
      for (String rejected : List.of("V4ER", "B%MIN", "", "admin", " USER ")) {
        var f = new Fixture();
        f.readOnly = inspect;
        f.fields.put(COL_ROLE, rejected);
        fixedInfrastructure(
            () -> {
              if (inspect) verifier.inspectReadOnly(f.connection(), INPUT, NOW);
              else verifier.verify(f.connection(), INPUT, NOW);
            });
        assertFalse(f.sql.contains(TOUCH));
        assertEquals(inspect ? List.of(READ) : List.of(USER_LOCK, SESSION_LOCK), f.sql);
        assertEquals(
            inspect
                ? List.of(SESSION_ROW, SESSION_STATEMENT)
                : List.of(USER_ROW, USER_STATEMENT, SESSION_ROW, SESSION_STATEMENT),
            f.closes);
        f.owned();
      }
    }
  }

  @Test
  void fatal001DirectBodyAndOwnedCloseErrorsKeepIdentityInBothVerificationModes() throws Exception {
    var verifier = new AuthenticationContextVerifier(new ContextHash());
    for (boolean inspect : List.of(false, true)) {
      List<String> body =
          inspect
              ? List.of(
                  JDBC_GET_AUTO_COMMIT,
                  "isReadOnly",
                  JDBC_PREPARE_STATEMENT,
                  JDBC_SET_STRING,
                  JDBC_EXECUTE_QUERY,
                  "next",
                  JDBC_GET_OBJECT,
                  JDBC_GET_STRING)
              : List.of(
                  JDBC_GET_AUTO_COMMIT,
                  JDBC_PREPARE_STATEMENT,
                  JDBC_SET_STRING,
                  JDBC_EXECUTE_QUERY,
                  "next",
                  JDBC_GET_OBJECT,
                  JDBC_GET_STRING,
                  "setObject",
                  "executeUpdate");
      List<String> closes =
          inspect
              ? List.of(SESSION_ROW, SESSION_STATEMENT)
              : List.of(USER_ROW, USER_STATEMENT, SESSION_ROW, SESSION_STATEMENT, TOUCH_STATEMENT);
      var positions = new ArrayList<>(body);
      for (String name : closes) positions.add(name + CLOSE_SUFFIX);
      for (String position : positions) {
        var f = new Fixture();
        f.readOnly = inspect;
        var fatal = new AssertionError("PUBLIC direct error");
        f.injectedFailures.put(position, fatal);
        assertSame(
            fatal,
            assertThrows(
                AssertionError.class,
                () -> {
                  if (inspect) verifier.inspectReadOnly(f.connection(), INPUT, NOW);
                  else verifier.verify(f.connection(), INPUT, NOW);
                }));
        assertNull(fatal.getCause());
        assertEquals(0, fatal.getSuppressed().length);
        f.owned();
      }
    }
  }

  @Test
  void fatal002SqlAndDomainFailureSuppressedFatalUsesTheOriginalErrorInstance() throws Exception {
    var verifier = new AuthenticationContextVerifier(new ContextHash());
    for (boolean inspect : List.of(false, true)) {
      var f = new Fixture();
      f.readOnly = inspect;
      var fatal = new AssertionError("PUBLIC wrapped error");
      var sql = new SQLException("PUBLIC wrapper", PUBLIC_SQL_STATE);
      sql.addSuppressed(fatal);
      f.injectedFailures.put(JDBC_GET_OBJECT, sql);
      assertSame(
          fatal,
          assertThrows(
              AssertionError.class,
              () -> {
                if (inspect) verifier.inspectReadOnly(f.connection(), INPUT, NOW);
                else verifier.verify(f.connection(), INPUT, NOW);
              }));
      assertArrayEquals(new Throwable[] {fatal}, sql.getSuppressed());
      f.owned();
      var denied = new Fixture();
      denied.readOnly = inspect;
      denied.fields.put(COL_REVOKED, true);
      var cleanupError = new AssertionError("PUBLIC domain cleanup error");
      denied.injectedFailures.put(SESSION_ROW + CLOSE_SUFFIX, cleanupError);
      assertSame(
          cleanupError,
          assertThrows(
              AssertionError.class,
              () -> {
                if (inspect) verifier.inspectReadOnly(denied.connection(), INPUT, NOW);
                else verifier.verify(denied.connection(), INPUT, NOW);
              }));
      assertFalse(denied.sql.contains(TOUCH));
      denied.owned();
    }
  }

  @Test
  void fatal003PrimarySecondaryAndSelfAliasPreserveOriginalFailureGraphInBothModes()
      throws Exception {
    var verifier = new AuthenticationContextVerifier(new ContextHash());
    for (boolean inspect : List.of(false, true)) {
      for (int primaryKind = 0; primaryKind < 3; primaryKind++) {
        for (boolean fatalClose : List.of(false, true)) {
          var f = new Fixture();
          f.readOnly = inspect;
          Throwable primary =
              primaryKind == 0
                  ? new SQLException("PUBLIC body", PUBLIC_SQL_STATE)
                  : primaryKind == 1
                      ? new IllegalStateException("PUBLIC body")
                      : new AssertionError("PUBLIC body");
          Throwable secondary =
              fatalClose
                  ? new AssertionError("PUBLIC close")
                  : new SQLException("PUBLIC close", PUBLIC_SQL_STATE);
          f.injectedFailures.put(JDBC_GET_OBJECT, primary);
          f.injectedFailures.put(SESSION_ROW + CLOSE_SUFFIX, secondary);
          if (primaryKind == 0 && !fatalClose) {
            fixedInfrastructure(
                () -> {
                  if (inspect) verifier.inspectReadOnly(f.connection(), INPUT, NOW);
                  else verifier.verify(f.connection(), INPUT, NOW);
                });
          } else {
            Throwable expected = primaryKind == 0 ? secondary : primary;
            assertSame(
                expected,
                assertThrows(
                    expected.getClass(),
                    () -> {
                      if (inspect) verifier.inspectReadOnly(f.connection(), INPUT, NOW);
                      else verifier.verify(f.connection(), INPUT, NOW);
                    }));
          }
          assertArrayEquals(new Throwable[] {secondary}, primary.getSuppressed());
          f.owned();
        }
      }
      var alias = new Fixture();
      alias.readOnly = inspect;
      var same = new SQLException("PUBLIC same alias", PUBLIC_SQL_STATE);
      alias.injectedFailures.put(JDBC_GET_OBJECT, same);
      alias.injectedFailures.put(SESSION_ROW + CLOSE_SUFFIX, same);
      var observed =
          assertThrows(
              IllegalArgumentException.class,
              () -> {
                if (inspect) verifier.inspectReadOnly(alias.connection(), INPUT, NOW);
                else verifier.verify(alias.connection(), INPUT, NOW);
              });
      assertSame(same, observed.getCause());
      assertEquals(0, same.getSuppressed().length);
      alias.owned();
    }
  }
}
