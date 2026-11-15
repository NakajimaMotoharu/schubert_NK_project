package dev.codex.schubert.nk.api.security;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.api.domain.Role;
import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.header.ResultCode;
import java.lang.reflect.InvocationHandler;
import java.lang.reflect.Proxy;
import java.net.InetAddress;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Types;
import java.time.Clock;
import java.time.Instant;
import java.time.ZoneId;
import java.time.ZoneOffset;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import org.jspecify.annotations.Nullable;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Timeout;

/** PT-AUT-REV001..008; SS3146.3/332/35212. Own JDBC/Clock, not a Logout/ADMIN request. */
@Timeout(value = 30, threadMode = Timeout.ThreadMode.SEPARATE_THREAD)
final class SessionRevocationJdbcPortTest {
  private static final Instant NOW = Instant.parse("2026-11-06T00:00:00.123456789Z");
  private static final Instant AT = Instant.parse("2026-11-06T00:00:00.123456Z");
  private static final Instant OLD = Instant.parse("2026-11-05T23:00:00Z");
  private static final AuthenticationContext INPUT = AuthenticationContext.of("a".repeat(64));
  private static final String HASH =
      "ffe054fe7ae0cb6dc65c3af9b61d5209f439851db43d0ba5997337df154668eb";
  private static final UUID SESSION = UUID.fromString("00000000-0000-4000-8000-000000000007");
  private static final UUID MESSAGE = new UUID(0, 10);
  private static final UUID CORRELATION = new UUID(0, 11);
  private static final AuthenticatedActor ADMIN =
      new AuthenticatedActor(9, "fixture-admin", Role.ADMIN);
  private static final String U = "user";
  private static final String S = "session";
  private static final String T = "target";
  private static final String A = "all";
  private static final String X = "update";
  private static final String L = "audit";
  private static final String COL_REVOKED = "revoked";
  private static final String COL_EXPIRES = "expires_at";
  private static final String COL_STATUS = "status";
  private static final String ACTION_LOGOUT = "LOGOUT";
  private static final String SQL_NULL = "SQL_NULL_VARCHAR";
  private static final String INFRA_MESSAGE = "authentication storage is unavailable";
  private static final String PUBLIC_MARKER = "ordinary-revocation-fixture-marker";
  private static final String USER_SQL =
      "select u.id from schubert.app_users u join schubert.auth_sessions s on s.user_id=u.id where"
          + " s.context_hash=? for update of u";
  private static final String SESSION_SQL =
      "select s.id,s.user_id,s.revoked,s.revoked_at,s.expires_at,u.status from"
          + " schubert.auth_sessions s join schubert.app_users u on u.id=s.user_id where"
          + " s.context_hash=? for update of s";
  private static final String TARGET_SQL =
      "select id from schubert.app_users where id=? for update";
  private static final String ALL_SQL =
      "select id from schubert.auth_sessions where user_id=? and not revoked order by id for"
          + " update";
  private static final String UPDATE_SQL =
      "update schubert.auth_sessions set revoked=true,revoked_at=?,revoke_reason=? where id=? and"
          + " not revoked";
  private static final String AUDIT_SQL =
      "insert into schubert.app_logs"
          + " (logged_at,service,category,level,action,message,message_id,correlation_id,actor_user_id,remote_address,details)"
          + " values(?,'API','SECURITY','INFO','SESSION_REVOKED','SESSION_REVOKED',?,?,?,cast(? as"
          + " inet),cast(? as jsonb))";

  private static <R> R proxy(Class<R> type, InvocationHandler handler) {
    return type.cast(Proxy.newProxyInstance(type.getClassLoader(), new Class<?>[] {type}, handler));
  }

  private static final class Fixture {
    final AuthSessionRevocationService service =
        new AuthSessionRevocationService(new ContextHash());
    final Map<String, @Nullable Object> fields = new HashMap<>();
    final List<String> order = new ArrayList<>();
    final List<String> events = new ArrayList<>();
    final List<String> acquired = new ArrayList<>();
    final List<String> closed = new ArrayList<>();
    final List<String> badCloses = new ArrayList<>();
    final List<String> getters = new ArrayList<>();
    final List<Map<Integer, Object>> bindings = new ArrayList<>();
    List<@Nullable UUID> ids = List.of(SESSION);
    boolean userPresent = true;
    boolean sessionPresent = true;
    boolean targetPresent = true;
    boolean autoCommit;
    int updated = 1;
    int audited = 1;
    int ownerChanges;
    int clockCalls;
    String failAt = "";
    String nullStatementAt = "";
    String nullRowAt = "";
    @Nullable RuntimeException runtimeFailure;
    Instant observed = NOW;

    Fixture() throws Exception {
      fields.put("id", SESSION);
      fields.put("user_id", 7L);
      fields.put(COL_REVOKED, false);
      fields.put("revoked_at", OLD.atOffset(ZoneOffset.UTC));
      fields.put(COL_EXPIRES, AT.plusSeconds(3600).atOffset(ZoneOffset.UTC));
      fields.put(COL_STATUS, "ACTIVE");
    }

    void fault(String at) throws SQLException {
      if (at.equals(failAt)) {
        if (runtimeFailure != null) throw runtimeFailure;
        throw new SQLException(PUBLIC_MARKER, "08006");
      }
    }

    void finish(String at) throws SQLException {
      closed.add(at);
      if (badCloses.contains(at)) throw new SQLException(PUBLIC_MARKER, "08006");
    }

    Connection connection() {
      return proxy(
          Connection.class,
          (p, m, a) -> {
            fault(m.getName());
            return switch (m.getName()) {
              case "getAutoCommit" -> autoCommit;
              case "prepareStatement" -> statement((String) a[0]);
              case "commit", "rollback", "close", "setAutoCommit", "setReadOnly" -> {
                ownerChanges++;
                throw new AssertionError("borrowed transaction changed");
              }
              default -> throw new AssertionError("unregistered connection method " + m.getName());
            };
          });
    }

    @Nullable PreparedStatement statement(String sql) throws SQLException {
      String label =
          switch (sql) {
            case USER_SQL -> U;
            case SESSION_SQL -> S;
            case TARGET_SQL -> T;
            case ALL_SQL -> A;
            case UPDATE_SQL -> X;
            case AUDIT_SQL -> L;
            default -> throw new AssertionError("SQL outside independent revocation contract");
          };
      order.add(label);
      fault(label + ".prepare");
      if (label.equals(nullStatementAt)) return null;
      String name = label + "-" + order.size();
      acquired.add(name + ".statement");
      Map<Integer, Object> bound = new HashMap<>();
      bindings.add(bound);
      return proxy(
          PreparedStatement.class,
          (p, m, a) -> {
            fault(label + "." + m.getName());
            return switch (m.getName()) {
              case "setString", "setLong", "setObject" -> {
                bound.put((Integer) a[0], a[1]);
                yield null;
              }
              case "setNull" -> {
                assertEquals(Types.VARCHAR, a[1]);
                bound.put((Integer) a[0], SQL_NULL);
                yield null;
              }
              case "executeQuery" -> row(label, name);
              case "executeUpdate" -> label.equals(X) ? updated : audited;
              case "close" -> {
                finish(name + ".statement");
                yield null;
              }
              default -> throw new AssertionError("unregistered statement method " + m.getName());
            };
          });
    }

    @Nullable ResultSet row(String label, String name) {
      if (label.equals(nullRowAt)) return null;
      acquired.add(name + ".row");
      int[] cursor = {-1};
      int count =
          label.equals(A)
              ? ids.size()
              : label.equals(U)
                  ? (userPresent ? 1 : 0)
                  : label.equals(S) ? (sessionPresent ? 1 : 0) : (targetPresent ? 1 : 0);
      return proxy(
          ResultSet.class,
          (p, m, a) -> {
            fault(label + "." + m.getName());
            events.add(label + "." + m.getName());
            return switch (m.getName()) {
              case "next" -> {
                cursor[0]++;
                yield cursor[0] < count;
              }
              case "getObject" -> {
                getters.add((String) a[0]);
                yield label.equals(A) ? ids.get(cursor[0]) : fields.get((String) a[0]);
              }
              case "getString" -> {
                getters.add((String) a[0]);
                yield fields.get((String) a[0]);
              }
              case "close" -> {
                finish(name + ".row");
                yield null;
              }
              default -> throw new AssertionError("unregistered row method " + m.getName());
            };
          });
    }

    Clock clock() {
      return new Clock() {
        public ZoneId getZone() {
          return ZoneOffset.UTC;
        }

        public Clock withZone(ZoneId zone) {
          assertEquals(ZoneOffset.UTC, zone);
          return this;
        }

        public Instant instant() {
          assertEquals(List.of(U, S), order);
          assertTrue(events.contains(S + ".next"));
          assertFalse(closed.contains("session-2.row"));
          clockCalls++;
          return observed;
        }
      };
    }

    RevokedContext logout() {
      return service.logoutCurrent(
          connection(), INPUT, Optional.empty(), MESSAGE, CORRELATION, clock());
    }

    int revoke() {
      return service.revokeAll(
          connection(),
          ADMIN,
          7,
          SessionRevocationReason.ADMIN,
          Optional.empty(),
          MESSAGE,
          CORRELATION,
          NOW);
    }

    void owned() {
      assertEquals(0, ownerChanges);
      assertEquals(acquired.size(), closed.size());
      for (String n : acquired) assertEquals(1, closed.stream().filter(n::equals).count());
    }

    void audit(
        int index,
        long actor,
        long target,
        String reason,
        String result,
        UUID message,
        UUID correlation) {
      assertEquals(
          Map.of(
              1,
              AT.atOffset(ZoneOffset.UTC),
              2,
              message,
              3,
              correlation,
              4,
              actor,
              5,
              SQL_NULL,
              6,
              "{\"targetUserId\":"
                  + target
                  + ",\"reason\":\""
                  + reason
                  + "\",\"resultCode\":\""
                  + result
                  + "\"}"),
          bindings.get(index));
    }
  }

  private static void infra(Fixture f, boolean admin) {
    var e =
        assertThrows(
            AuthenticationInfrastructureException.class,
            () -> {
              if (admin) f.revoke();
              else f.logout();
            });
    assertEquals(INFRA_MESSAGE, e.getMessage());
    assertNull(e.getCause());
    assertEquals(0, e.getSuppressed().length);
    f.owned();
  }

  @Test
  void logoutSamplesCurrentClockAfterBothLocksAndStagesExactUtcAudit() throws Exception {
    Fixture f = new Fixture();
    var out = f.logout();
    assertEquals(new AuthContextIdentity(SESSION, 7), out.identity());
    assertEquals(AT, out.revokedAt());
    assertEquals(ResultCode.SUCCESS, out.resultCode());
    assertEquals("RevokedContext[REDACTED]", out.toString());
    assertEquals(1, f.clockCalls);
    assertEquals(List.of(U, S, X, L), f.order);
    assertEquals(Map.of(1, HASH), f.bindings.get(0));
    assertEquals(Map.of(1, HASH), f.bindings.get(1));
    assertEquals(
        Map.of(1, AT.atOffset(ZoneOffset.UTC), 2, ACTION_LOGOUT, 3, SESSION), f.bindings.get(2));
    f.audit(3, 7, 7, ACTION_LOGOUT, "0000", MESSAGE, CORRELATION);
    f.owned();
    Fixture wrapper = new Fixture();
    var legacy =
        wrapper.service.logout(
            wrapper.connection(),
            INPUT,
            Optional.of(InetAddress.getByAddress(new byte[] {127, 0, 0, 1})),
            MESSAGE,
            CORRELATION,
            NOW);
    assertEquals(AT, legacy.revokedAt());
    assertEquals("127.0.0.1", wrapper.bindings.get(3).get(5));
    assertEquals(0, wrapper.clockCalls);
    wrapper.owned();
  }

  @Test
  void alreadyRevokedReturnsOriginalInstantWithoutTouchOrPrincipal() throws Exception {
    Fixture f = new Fixture();
    f.fields.put(COL_REVOKED, true);
    f.fields.put(COL_EXPIRES, null);
    f.fields.put(COL_STATUS, null);
    var out = f.logout();
    assertEquals(ResultCode.IDEMPOTENT_SUCCESS, out.resultCode());
    assertEquals(OLD, out.revokedAt());
    assertEquals(List.of(U, S, L), f.order);
    assertFalse(f.getters.contains(COL_EXPIRES));
    assertFalse(f.getters.contains(COL_STATUS));
    f.audit(2, 7, 7, ACTION_LOGOUT, "0200", MESSAGE, CORRELATION);
    assertEquals("RevokedContext[REDACTED]", out.toString());
    f.owned();
  }

  @Test
  void expiryDisabledAbsentAndNullRowsFailClosedWithRequiredAuditOnly() throws Exception {
    for (Instant expires : List.of(AT, AT.minusNanos(1000))) {
      Fixture f = new Fixture();
      f.fields.put(COL_EXPIRES, expires.atOffset(ZoneOffset.UTC));
      assertThrows(AuthenticationContextException.class, f::logout);
      assertEquals(List.of(U, S, X, L), f.order);
      assertEquals("EXPIRED", f.bindings.get(2).get(2));
      f.audit(3, 7, 7, "EXPIRED", "0102", MESSAGE, CORRELATION);
      f.owned();
    }
    Fixture after = new Fixture();
    after.fields.put(COL_EXPIRES, AT.plusNanos(1000).atOffset(ZoneOffset.UTC));
    assertEquals(ResultCode.SUCCESS, after.logout().resultCode());
    after.owned();
    Fixture disabled = new Fixture();
    disabled.fields.put(COL_STATUS, "DISABLED");
    assertThrows(AuthenticationContextException.class, disabled::logout);
    assertEquals(List.of(U, S), disabled.order);
    disabled.owned();
    for (boolean missingUser : new boolean[] {true, false}) {
      Fixture f = new Fixture();
      f.userPresent = !missingUser;
      f.sessionPresent = missingUser;
      assertThrows(AuthenticationContextException.class, f::logout);
      assertEquals(0, f.clockCalls);
      f.owned();
    }
    for (String key :
        List.of("id", "user_id", COL_REVOKED, COL_EXPIRES, COL_STATUS, "revoked_at")) {
      Fixture f = new Fixture();
      if (key.equals("revoked_at")) f.fields.put(COL_REVOKED, true);
      f.fields.put(key, null);
      infra(f, false);
    }
  }

  @Test
  void administrativeRevocationStagesEachTargetInFixedOrderForAllowedReasons() throws Exception {
    var reasons =
        Map.of(
            SessionRevocationReason.DISABLED,
            "DISABLED",
            SessionRevocationReason.PASSWORD_RESET,
            "PASSWORD_RESET",
            SessionRevocationReason.ADMIN,
            "ADMIN");
    for (var reason : reasons.entrySet())
      for (int count : new int[] {0, 1, 2}) {
        Fixture f = new Fixture();
        f.ids =
            count == 0
                ? List.of()
                : count == 1 ? List.of(SESSION) : List.of(new UUID(0, 1), SESSION);
        int n =
            f.service.revokeAll(
                f.connection(),
                ADMIN,
                7,
                reason.getKey(),
                Optional.empty(),
                MESSAGE,
                CORRELATION,
                NOW);
        assertEquals(count, n);
        assertEquals(Map.of(1, 7L), f.bindings.get(0));
        assertEquals(Map.of(1, 7L), f.bindings.get(1));
        assertEquals(2 + 2 * count, f.order.size());
        for (int i = 0; i < count; i++) {
          int at = 2 + 2 * i;
          assertEquals(X, f.order.get(at));
          assertEquals(L, f.order.get(at + 1));
          assertEquals(
              Map.of(1, AT.atOffset(ZoneOffset.UTC), 2, reason.getValue(), 3, f.ids.get(i)),
              f.bindings.get(at));
          f.audit(at + 1, 9, 7, reason.getValue(), "0000", MESSAGE, CORRELATION);
        }
        f.owned();
      }
    for (long target : new long[] {1, 999_999_999_999L}) {
      Fixture f = new Fixture();
      f.ids = List.of();
      assertEquals(
          0,
          f.service.revokeAll(
              f.connection(),
              ADMIN,
              target,
              SessionRevocationReason.ADMIN,
              Optional.empty(),
              MESSAGE,
              CORRELATION,
              NOW));
      assertEquals(target, f.bindings.get(0).get(1));
      f.owned();
    }
  }

  @Test
  void boundaryNullOwnerReasonAndCurrentAdminContractsPrecedeSql() throws Exception {
    Fixture f = new Fixture();
    var c = f.connection();
    var service = f.service;
    assertThrows(NullPointerException.class, () -> new AuthSessionRevocationService(null));
    assertThrows(
        NullPointerException.class,
        () -> service.logout(c, null, Optional.empty(), MESSAGE, CORRELATION, NOW));
    assertThrows(
        NullPointerException.class,
        () -> service.logout(null, INPUT, Optional.empty(), MESSAGE, CORRELATION, NOW));
    assertThrows(
        NullPointerException.class,
        () -> service.logout(c, INPUT, null, MESSAGE, CORRELATION, NOW));
    assertThrows(
        NullPointerException.class,
        () -> service.logout(c, INPUT, Optional.empty(), null, CORRELATION, NOW));
    assertThrows(
        NullPointerException.class,
        () -> service.logout(c, INPUT, Optional.empty(), MESSAGE, null, NOW));
    assertThrows(
        NullPointerException.class,
        () -> service.logout(c, INPUT, Optional.empty(), MESSAGE, CORRELATION, null));
    assertThrows(
        NullPointerException.class,
        () ->
            service.logoutCurrent(
                null, INPUT, Optional.empty(), MESSAGE, CORRELATION, Clock.systemUTC()));
    assertThrows(
        NullPointerException.class,
        () ->
            service.logoutCurrent(
                c, null, Optional.empty(), MESSAGE, CORRELATION, Clock.systemUTC()));
    assertThrows(
        NullPointerException.class,
        () -> service.logoutCurrent(c, INPUT, null, MESSAGE, CORRELATION, Clock.systemUTC()));
    assertThrows(
        NullPointerException.class,
        () ->
            service.logoutCurrent(
                c, INPUT, Optional.empty(), null, CORRELATION, Clock.systemUTC()));
    assertThrows(
        NullPointerException.class,
        () -> service.logoutCurrent(c, INPUT, Optional.empty(), MESSAGE, null, Clock.systemUTC()));
    assertThrows(
        NullPointerException.class,
        () -> service.logoutCurrent(c, INPUT, Optional.empty(), MESSAGE, CORRELATION, null));
    assertThrows(
        NullPointerException.class,
        () ->
            service.revokeAll(
                c,
                null,
                7,
                SessionRevocationReason.ADMIN,
                Optional.empty(),
                MESSAGE,
                CORRELATION,
                NOW));
    assertThrows(
        NullPointerException.class,
        () -> service.revokeAll(c, ADMIN, 7, null, Optional.empty(), MESSAGE, CORRELATION, NOW));
    assertThrows(
        NullPointerException.class,
        () ->
            service.revokeAll(
                null,
                ADMIN,
                7,
                SessionRevocationReason.ADMIN,
                Optional.empty(),
                MESSAGE,
                CORRELATION,
                NOW));
    assertThrows(
        NullPointerException.class,
        () ->
            service.revokeAll(
                c, ADMIN, 7, SessionRevocationReason.ADMIN, null, MESSAGE, CORRELATION, NOW));
    assertThrows(
        NullPointerException.class,
        () ->
            service.revokeAll(
                c,
                ADMIN,
                7,
                SessionRevocationReason.ADMIN,
                Optional.empty(),
                null,
                CORRELATION,
                NOW));
    assertThrows(
        NullPointerException.class,
        () ->
            service.revokeAll(
                c, ADMIN, 7, SessionRevocationReason.ADMIN, Optional.empty(), MESSAGE, null, NOW));
    assertThrows(
        NullPointerException.class,
        () ->
            service.revokeAll(
                c,
                ADMIN,
                7,
                SessionRevocationReason.ADMIN,
                Optional.empty(),
                MESSAGE,
                CORRELATION,
                null));
    for (long id : new long[] {-1, 0, 1_000_000_000_000L})
      assertThrows(
          IllegalArgumentException.class,
          () ->
              service.revokeAll(
                  c,
                  ADMIN,
                  id,
                  SessionRevocationReason.ADMIN,
                  Optional.empty(),
                  MESSAGE,
                  CORRELATION,
                  NOW));
    for (var reason :
        List.of(
            SessionRevocationReason.LOGOUT,
            SessionRevocationReason.EXPIRED,
            SessionRevocationReason.REPLACED))
      assertThrows(
          IllegalArgumentException.class,
          () ->
              service.revokeAll(c, ADMIN, 7, reason, Optional.empty(), MESSAGE, CORRELATION, NOW));
    var forbidden =
        assertThrows(
            AuthorizationException.class,
            () ->
                service.revokeAll(
                    c,
                    new AuthenticatedActor(9, "fixture-user", Role.USER),
                    7,
                    SessionRevocationReason.ADMIN,
                    Optional.empty(),
                    MESSAGE,
                    CORRELATION,
                    NOW));
    assertEquals(ResultCode.FORBIDDEN, forbidden.resultCode());
    assertTrue(f.order.isEmpty());
    f.owned();
    for (boolean admin : new boolean[] {true, false}) {
      Fixture bad = new Fixture();
      bad.autoCommit = true;
      infra(bad, admin);
      assertTrue(bad.order.isEmpty());
    }
  }

  @Test
  void affectedSqlAndEveryCloseFailureRemainUnsuccessfulAndRedacted() throws Exception {
    for (boolean admin : new boolean[] {false, true}) {
      for (int bad : new int[] {0, 2}) {
        Fixture update = new Fixture();
        update.updated = bad;
        infra(update, admin);
        Fixture audit = new Fixture();
        audit.audited = bad;
        infra(audit, admin);
      }
      for (String label : admin ? List.of(T, A, X, L) : List.of(U, S, X, L))
        for (String method :
            List.of(
                "prepare",
                label.equals(U) || label.equals(S) || label.equals(T) || label.equals(A)
                    ? "executeQuery"
                    : "executeUpdate")) {
          Fixture f = new Fixture();
          f.failAt = label + "." + method;
          infra(f, admin);
        }
      for (String resource :
          admin
              ? List.of(
                  "target-1.row",
                  "target-1.statement",
                  "all-2.row",
                  "all-2.statement",
                  "update-3.statement",
                  "audit-4.statement")
              : List.of(
                  "user-1.row",
                  "user-1.statement",
                  "session-2.row",
                  "session-2.statement",
                  "update-3.statement",
                  "audit-4.statement")) {
        Fixture f = new Fixture();
        f.badCloses.add(resource);
        infra(f, admin);
      }
    }
    Fixture suppressed = new Fixture();
    suppressed.userPresent = false;
    suppressed.badCloses.add("user-1.row");
    infra(suppressed, false);
    Fixture missing = new Fixture();
    missing.targetPresent = false;
    var denial = assertThrows(AuthorizationException.class, missing::revoke);
    assertEquals(ResultCode.NOT_FOUND, denial.resultCode());
    assertNull(denial.getCause());
    assertEquals(0, denial.getSuppressed().length);
    missing.owned();
    Fixture targetCleanup = new Fixture();
    targetCleanup.targetPresent = false;
    targetCleanup.badCloses.add("target-1.row");
    infra(targetCleanup, true);
  }

  @Test
  void invalidValuesAndUnknownProviderExceptionsKeepTheirDefinedBoundary() throws Exception {
    for (long id : new long[] {0, 1_000_000_000_000L}) {
      Fixture f = new Fixture();
      f.fields.put("user_id", id);
      infra(f, false);
    }
    Fixture time = new Fixture();
    time.observed = Instant.MAX;
    infra(time, false);
    Fixture nullAdminId = new Fixture();
    nullAdminId.ids = new ArrayList<>();
    nullAdminId.ids.add(null);
    infra(nullAdminId, true);
    for (boolean admin : new boolean[] {false, true}) {
      Fixture f = new Fixture();
      f.runtimeFailure = new IllegalStateException(PUBLIC_MARKER);
      f.failAt = (admin ? A : S) + ".executeQuery";
      assertSame(
          f.runtimeFailure,
          assertThrows(
              IllegalStateException.class,
              () -> {
                if (admin) f.revoke();
                else f.logout();
              }));
      f.owned();
    }
    Fixture classified = new Fixture();
    classified.runtimeFailure = new IllegalArgumentException(PUBLIC_MARKER);
    classified.failAt = S + ".getObject";
    infra(classified, false);
    for (String point :
        List.of(
            "getAutoCommit",
            "user.setString",
            "session.getString",
            "session.getObject",
            "session.next",
            "update.setObject",
            "update.setString",
            "audit.setNull",
            "audit.setString")) {
      Fixture f = new Fixture();
      f.failAt = point;
      infra(f, false);
    }
    for (String point :
        List.of(
            "target.setLong",
            "target.next",
            "all.next",
            "all.getObject",
            "all.setLong",
            "audit.setLong")) {
      Fixture f = new Fixture();
      f.failAt = point;
      infra(f, true);
    }
  }

  @Test
  void sharedServiceParallelCallsRetainOwnResultCorrelationAndResourceState() throws Exception {
    var shared = new AuthSessionRevocationService(new ContextHash());
    var workers = Executors.newFixedThreadPool(2);
    try {
      List<Future<Integer>> results = new ArrayList<>();
      for (int i = 0; i < 16; i++) {
        int index = i;
        results.add(
            workers.submit(
                () -> {
                  Fixture f = new Fixture();
                  boolean revoked = index % 2 == 0;
                  f.fields.put(COL_REVOKED, revoked);
                  UUID msg = new UUID(0, 100 + index);
                  UUID corr = new UUID(0, 200 + index);
                  var out =
                      shared.logoutCurrent(
                          f.connection(), INPUT, Optional.empty(), msg, corr, f.clock());
                  assertEquals(revoked ? OLD : AT, out.revokedAt());
                  assertEquals(
                      revoked ? ResultCode.IDEMPOTENT_SUCCESS : ResultCode.SUCCESS,
                      out.resultCode());
                  assertEquals(Map.of(1, HASH), f.bindings.get(0));
                  assertEquals(Map.of(1, HASH), f.bindings.get(1));
                  f.audit(
                      revoked ? 2 : 3, 7, 7, ACTION_LOGOUT, revoked ? "0200" : "0000", msg, corr);
                  f.owned();
                  return f.order.size();
                }));
      }
      for (int i = 0; i < results.size(); i++)
        assertEquals(i % 2 == 0 ? 3 : 4, results.get(i).get(5, TimeUnit.SECONDS));
    } finally {
      workers.shutdownNow();
      assertTrue(workers.awaitTermination(10, TimeUnit.SECONDS));
    }
  }

  @Test
  void resource001NullStatementsFailClosedForLogoutAndAdministrativeRevocation() throws Exception {
    for (boolean admin : new boolean[] {false, true}) {
      for (String label : admin ? List.of(T, A, X, L) : List.of(U, S, X, L)) {
        Fixture f = new Fixture();
        f.nullStatementAt = label;
        infra(f, admin);
        assertEquals(label, f.order.getLast());
      }
    }
  }

  @Test
  void resource002NullRowsStillCloseTheirOwnedStatementExactlyOnce() throws Exception {
    for (boolean admin : new boolean[] {false, true}) {
      for (String label : admin ? List.of(T, A) : List.of(U, S)) {
        Fixture f = new Fixture();
        f.nullRowAt = label;
        infra(f, admin);
        assertEquals(label, f.order.getLast());
      }
    }
  }
}
