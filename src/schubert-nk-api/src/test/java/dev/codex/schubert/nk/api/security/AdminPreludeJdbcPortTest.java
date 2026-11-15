package dev.codex.schubert.nk.api.security;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.api.domain.Role;
import dev.codex.schubert.nk.api.security.AdminCommandAuthenticator.Mutation;
import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.header.ResultCode;
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
import java.util.OptionalLong;
import java.util.UUID;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import org.jspecify.annotations.Nullable;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Timeout;

/** PT-AUT-PRE001..008; SS314 9.2/SS332 12. Own interface callbacks, no database/lock. */
@Timeout(value = 30, threadMode = Timeout.ThreadMode.SEPARATE_THREAD)
final class AdminPreludeJdbcPortTest {
  private static final Instant NOW = Instant.parse("2026-11-06T00:00:00Z");
  private static final AuthenticationContext INPUT = AuthenticationContext.of("a".repeat(64));
  private static final String HASH =
      "ffe054fe7ae0cb6dc65c3af9b61d5209f439851db43d0ba5997337df154668eb";
  private static final long MAX_ID = 999_999_999_999L;
  private static final String OWNER_SQL =
      "select user_id from schubert.auth_sessions where context_hash=?";
  private static final String LOCKED_OWNER_SQL = OWNER_SQL + " for update";
  private static final String ADVISORY_SQL = "select pg_advisory_xact_lock(71419601)";
  private static final String USERS_SQL =
      """
      select id from schubert.app_users
       where id=? or id=? or (? and role='ADMIN' and status='ACTIVE')
       order by id for update
      """;
  private static final String AUTH_USER_SQL =
      "select u.id from schubert.app_users u join schubert.auth_sessions s on s.user_id=u.id where"
          + " s.context_hash=? for update of u";
  private static final String AUTH_SESSION_SQL =
      "select s.id,s.user_id,u.username,u.role,u.status,s.revoked,s.expires_at from"
          + " schubert.auth_sessions s join schubert.app_users u on u.id=s.user_id where"
          + " s.context_hash=? for update of s";
  private static final String TOUCH_SQL =
      "update schubert.auth_sessions set"
          + " last_accessed_at=greatest(last_accessed_at,?),expires_at=greatest(expires_at,cast(?"
          + " as timestamptz)+interval '8 hours') where id=? and not revoked";
  private static final String CANDIDATE = "candidate";
  private static final String LOCKED = "locked";
  private static final String USERS = "users";
  private static final String ADVISORY = "advisory";
  private static final String AUTH_USER = "auth-user";
  private static final String AUTH_SESSION = "auth-session";
  private static final String TOUCH = "touch";
  private static final String PUBLIC_MARKER = "ordinary-prelude-fixture-marker";
  private static final String INFRA = "authentication storage is unavailable";
  private static final String ADMIN = "ADMIN";
  private static final String USER = "USER";

  private static <T> T proxy(Class<T> type, InvocationHandler handler) {
    return type.cast(Proxy.newProxyInstance(type.getClassLoader(), new Class<?>[] {type}, handler));
  }

  private static final class Fixture {
    long candidate = 7;
    long actor = 7;
    List<Long> candidateRows = List.of(7L);
    List<Long> lockedRows = List.of(7L);
    List<Long> userRows = List.of(3L, 7L, 20L);
    int advisoryRows = 1;
    boolean candidateNull;
    boolean autoCommit;
    boolean readOnly;
    boolean authenticated = true;
    String role = ADMIN;
    String faultAt = "";
    String nullStatementAt = "";
    String nullRowAt = "";
    @Nullable RuntimeException runtimeFailure;
    final List<String> order = new ArrayList<>();
    final Map<String, Map<Integer, Object>> bindings = new HashMap<>();
    final List<String> acquired = new ArrayList<>();
    final List<String> closed = new ArrayList<>();
    final List<String> badCloses = new ArrayList<>();
    int forbiddenOwnerCalls;

    void fault(String at) throws SQLException {
      if (faultAt.equals(at)) {
        if (runtimeFailure != null) throw runtimeFailure;
        throw new SQLException(PUBLIC_MARKER, "08006");
      }
    }

    void close(String at) throws SQLException {
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
              case "isReadOnly" -> readOnly;
              case "prepareStatement" -> statement((String) a[0]);
              case "commit", "rollback", "close", "setAutoCommit", "setReadOnly" -> {
                forbiddenOwnerCalls++;
                throw new AssertionError("borrowed transaction changed");
              }
              default -> throw new AssertionError("unregistered connection method " + m.getName());
            };
          });
    }

    @Nullable PreparedStatement statement(String sql) throws SQLException {
      String name =
          switch (sql) {
            case OWNER_SQL -> CANDIDATE;
            case LOCKED_OWNER_SQL -> LOCKED;
            case USERS_SQL -> USERS;
            case ADVISORY_SQL -> ADVISORY;
            case AUTH_USER_SQL -> AUTH_USER;
            case AUTH_SESSION_SQL -> AUTH_SESSION;
            case TOUCH_SQL -> TOUCH;
            default -> throw new AssertionError("SQL outside independently fixed prelude");
          };
      order.add(name);
      fault(name + ".prepare");
      if (name.equals(nullStatementAt)) return null;
      acquired.add(name + ".statement");
      Map<Integer, Object> bound = new HashMap<>();
      bindings.put(name, bound);
      return proxy(
          PreparedStatement.class,
          (p, m, a) -> {
            fault(name + "." + m.getName());
            return switch (m.getName()) {
              case "setString", "setLong", "setBoolean", "setObject" -> {
                bound.put((Integer) a[0], a[1]);
                yield null;
              }
              case "executeQuery" -> row(name);
              case "executeUpdate" -> 1;
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
      List<Long> ids =
          switch (name) {
            case CANDIDATE -> candidateRows;
            case LOCKED -> lockedRows;
            case USERS -> userRows;
            default -> List.of(candidate);
          };
      int count =
          name.equals(ADVISORY)
              ? advisoryRows
              : name.equals(AUTH_USER) && !authenticated ? 0 : ids.size();
      int[] index = {-1};
      return proxy(
          ResultSet.class,
          (p, m, a) -> {
            fault(name + "." + m.getName());
            return switch (m.getName()) {
              case "next" -> {
                index[0]++;
                yield index[0] < count;
              }
              case "getLong" -> ids.get(index[0]);
              case "wasNull" -> name.equals(CANDIDATE) && candidateNull;
              case "getString" ->
                  switch ((String) a[0]) {
                    case "status" -> "ACTIVE";
                    case "username" -> "fixture-admin";
                    case "role" -> role;
                    default -> throw new AssertionError("unregistered text column");
                  };
              case "getObject" ->
                  switch ((String) a[0]) {
                    case "revoked" -> false;
                    case "expires_at" -> NOW.plusSeconds(28_800).atOffset(ZoneOffset.UTC);
                    case "id" -> UUID.fromString("00000000-0000-4000-8000-000000000007");
                    case "user_id" -> actor;
                    default -> throw new AssertionError("unregistered typed column");
                  };
              case "close" -> {
                close(name + ".row");
                yield null;
              }
              default -> throw new AssertionError("unregistered row method " + m.getName());
            };
          });
    }

    void ownerUnchanged() {
      assertEquals(0, forbiddenOwnerCalls);
      assertEquals(acquired.size(), closed.size());
      for (String item : acquired) assertEquals(1, closed.stream().filter(item::equals).count());
    }
  }

  private static AdminCommandAuthenticator authenticator() {
    try {
      return new AdminCommandAuthenticator(new ContextHash());
    } catch (java.security.NoSuchAlgorithmException unavailable) {
      throw new AssertionError("fixed JDK SHA-256 unavailable", unavailable);
    }
  }

  private static AuthenticatedActor identity(Fixture f, Mutation mutation, OptionalLong target) {
    return authenticator().verifyIdentity(f.connection(), INPUT, mutation, target, NOW);
  }

  private static void infrastructure(Fixture f, Mutation mutation, OptionalLong target) {
    var failure =
        assertThrows(
            AuthenticationInfrastructureException.class, () -> identity(f, mutation, target));
    assertEquals(INFRA, failure.getMessage());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
    f.ownerUnchanged();
  }

  @Test
  void allMutationsUseIndependentOrderedPreludeAndUtcBindings() {
    for (Mutation mutation : Mutation.values()) {
      Fixture f = new Fixture();
      boolean reducing = mutation == Mutation.DISABLE || mutation == Mutation.DEMOTE;
      OptionalLong target =
          mutation == Mutation.CREATE ? OptionalLong.empty() : OptionalLong.of(20);
      AuthenticatedActor result = identity(f, mutation, target);
      assertEquals(new AuthenticatedActor(7, "fixture-admin", Role.ADMIN), result);
      List<String> order = new ArrayList<>();
      order.add(CANDIDATE);
      if (reducing) order.add(ADVISORY);
      order.addAll(List.of(USERS, LOCKED, AUTH_USER, AUTH_SESSION, TOUCH));
      assertEquals(order, f.order);
      assertEquals(Map.of(1, HASH), f.bindings.get(CANDIDATE));
      assertEquals(Map.of(1, HASH), f.bindings.get(LOCKED));
      assertEquals(Map.of(1, 7L, 2, target.orElse(7L), 3, reducing), f.bindings.get(USERS));
      assertEquals(NOW.atOffset(ZoneOffset.UTC), f.bindings.get(TOUCH).get(1));
      f.ownerUnchanged();
    }
    for (long target : new long[] {1, MAX_ID}) {
      Fixture f = new Fixture();
      identity(f, Mutation.UNLOCK, OptionalLong.of(target));
      assertEquals(target, f.bindings.get(USERS).get(2));
      f.ownerUnchanged();
    }
  }

  @Test
  void targetPresenceN12AndNullContractsFailBeforeAnySql() {
    assertThrows(NullPointerException.class, () -> new AdminCommandAuthenticator(null));
    Fixture f = new Fixture();
    var auth = authenticator();
    Connection c = f.connection();
    OptionalLong target = OptionalLong.of(20);
    assertThrows(
        NullPointerException.class,
        () -> auth.verifyIdentity(null, INPUT, Mutation.UNLOCK, target, NOW));
    assertThrows(
        NullPointerException.class,
        () -> auth.verifyIdentity(c, null, Mutation.UNLOCK, target, NOW));
    assertThrows(
        NullPointerException.class, () -> auth.verifyIdentity(c, INPUT, null, target, NOW));
    assertThrows(
        NullPointerException.class,
        () -> auth.verifyIdentity(c, INPUT, Mutation.UNLOCK, null, NOW));
    assertThrows(
        NullPointerException.class,
        () -> auth.verifyIdentity(c, INPUT, Mutation.UNLOCK, target, null));
    assertThrows(IllegalArgumentException.class, () -> identity(f, Mutation.CREATE, target));
    assertThrows(
        IllegalArgumentException.class, () -> identity(f, Mutation.UNLOCK, OptionalLong.empty()));
    for (long invalid : new long[] {-1, 0, MAX_ID + 1})
      assertThrows(
          IllegalArgumentException.class,
          () -> identity(f, Mutation.UNLOCK, OptionalLong.of(invalid)));
    assertTrue(f.order.isEmpty());
    f.ownerUnchanged();
    for (boolean[] mode : new boolean[][] {{true, false}, {true, true}, {false, true}}) {
      Fixture bad = new Fixture();
      bad.autoCommit = mode[0];
      bad.readOnly = mode[1];
      infrastructure(bad, Mutation.CREATE, OptionalLong.empty());
      assertTrue(bad.order.isEmpty());
    }
  }

  @Test
  void candidateLookupIsBoundedSingleRowAndNeverAnAuthorityGrant() {
    Fixture absent = new Fixture();
    absent.candidateRows = List.of();
    assertThrows(
        AuthenticationContextException.class,
        () -> identity(absent, Mutation.CREATE, OptionalLong.empty()));
    absent.ownerUnchanged();
    for (List<Long> rows :
        List.of(List.of(0L), List.of(-1L), List.of(MAX_ID + 1), List.of(7L, 8L))) {
      Fixture f = new Fixture();
      f.candidateRows = rows;
      infrastructure(f, Mutation.CREATE, OptionalLong.empty());
      assertEquals(List.of(CANDIDATE), f.order);
    }
    Fixture nul = new Fixture();
    nul.candidateNull = true;
    infrastructure(nul, Mutation.CREATE, OptionalLong.empty());
    for (long edge : new long[] {1, MAX_ID}) {
      Fixture f = new Fixture();
      f.candidate = edge;
      f.actor = edge;
      f.candidateRows = List.of(edge);
      f.lockedRows = List.of(edge);
      f.userRows = List.of(edge);
      assertEquals(edge, identity(f, Mutation.CREATE, OptionalLong.empty()).userId());
      f.ownerUnchanged();
    }
  }

  @Test
  void reducingAdvisoryAndSortedUserRowsRequireExactCardinality() {
    for (int count : new int[] {0, 2}) {
      Fixture f = new Fixture();
      f.advisoryRows = count;
      infrastructure(f, Mutation.DISABLE, OptionalLong.of(20));
      assertEquals(List.of(CANDIDATE, ADVISORY), f.order);
    }
    for (List<Long> rows :
        List.of(
            List.<Long>of(), List.of(3L, 4L), List.of(7L, 7L), List.of(20L, 7L), List.of(0L, 7L))) {
      Fixture f = new Fixture();
      f.userRows = rows;
      infrastructure(f, Mutation.DEMOTE, OptionalLong.of(20));
      assertFalse(f.order.contains(LOCKED));
    }
    Fixture only = new Fixture();
    only.userRows = List.of(7L);
    assertEquals(7, identity(only, Mutation.ENABLE, OptionalLong.of(20)).userId());
    assertFalse(only.order.contains(ADVISORY));
    only.ownerUnchanged();
  }

  @Test
  void lockedOwnerAndFreshVerifiedActorMustMatchTheCandidate() {
    Fixture changed = new Fixture();
    changed.lockedRows = List.of(8L);
    assertThrows(
        AuthenticationContextException.class,
        () -> identity(changed, Mutation.UNLOCK, OptionalLong.of(20)));
    assertFalse(changed.order.contains(AUTH_USER));
    changed.ownerUnchanged();
    Fixture disappeared = new Fixture();
    disappeared.lockedRows = List.of();
    assertThrows(
        AuthenticationContextException.class,
        () -> identity(disappeared, Mutation.UNLOCK, OptionalLong.of(20)));
    disappeared.ownerUnchanged();
    Fixture drift = new Fixture();
    drift.actor = 8;
    infrastructure(drift, Mutation.UNLOCK, OptionalLong.of(20));
    Fixture denied = new Fixture();
    denied.authenticated = false;
    assertThrows(
        AuthenticationContextException.class,
        () -> identity(denied, Mutation.UNLOCK, OptionalLong.of(20)));
    assertFalse(denied.order.contains(TOUCH));
    denied.ownerUnchanged();
  }

  @Test
  void verifyRequiresFreshAdminButIdentityAloneCannotGrantIt() {
    Fixture current = new Fixture();
    assertEquals(
        Role.ADMIN,
        authenticator()
            .verify(current.connection(), INPUT, Mutation.CREATE, OptionalLong.empty(), NOW)
            .role());
    current.ownerUnchanged();
    Fixture user = new Fixture();
    user.role = USER;
    assertEquals(Role.USER, identity(user, Mutation.CREATE, OptionalLong.empty()).role());
    user.ownerUnchanged();
    Fixture denied = new Fixture();
    denied.role = USER;
    var result =
        assertThrows(
            AuthorizationException.class,
            () ->
                authenticator()
                    .verify(
                        denied.connection(), INPUT, Mutation.CREATE, OptionalLong.empty(), NOW));
    assertEquals(ResultCode.FORBIDDEN, result.resultCode());
    denied.ownerUnchanged();
  }

  @Test
  void ordinaryJdbcAndCloseFailuresPreserveBorrowedOwnershipAndRedaction() {
    for (String label :
        List.of(CANDIDATE, ADVISORY, USERS, LOCKED, AUTH_USER, AUTH_SESSION, TOUCH)) {
      for (String method :
          List.of("prepare", label.equals(TOUCH) ? "executeUpdate" : "executeQuery")) {
        Fixture f = new Fixture();
        f.faultAt = label + "." + method;
        infrastructure(f, Mutation.DISABLE, OptionalLong.of(20));
      }
      for (String resource :
          label.equals(TOUCH) ? List.of("statement") : List.of("row", "statement")) {
        Fixture f = new Fixture();
        f.badCloses.add(label + "." + resource);
        infrastructure(f, Mutation.DISABLE, OptionalLong.of(20));
      }
    }
    for (RuntimeException classified :
        List.of(
            new IllegalArgumentException(PUBLIC_MARKER),
            new java.time.DateTimeException(PUBLIC_MARKER))) {
      Fixture f = new Fixture();
      f.runtimeFailure = classified;
      f.faultAt = USERS + ".executeQuery";
      infrastructure(f, Mutation.ENABLE, OptionalLong.of(20));
    }
    Fixture suppressed = new Fixture();
    suppressed.candidateRows = List.of();
    suppressed.badCloses.add(CANDIDATE + ".row");
    infrastructure(suppressed, Mutation.CREATE, OptionalLong.empty());
    Fixture unknown = new Fixture();
    unknown.runtimeFailure = new IllegalStateException(PUBLIC_MARKER);
    unknown.faultAt = USERS + ".executeQuery";
    assertSame(
        unknown.runtimeFailure,
        assertThrows(
            IllegalStateException.class,
            () -> identity(unknown, Mutation.ENABLE, OptionalLong.of(20))));
    unknown.ownerUnchanged();
  }

  @Test
  void parallelFreshPreludeRowsDoNotShareActorsOrResourceOwnership() throws Exception {
    var pool = Executors.newFixedThreadPool(2);
    try {
      List<Future<Long>> futures = new ArrayList<>();
      for (long id = 1; id <= 32; id++) {
        long expected = id;
        futures.add(
            pool.submit(
                () -> {
                  Fixture f = new Fixture();
                  f.candidate = expected;
                  f.actor = expected;
                  f.candidateRows = List.of(expected);
                  f.lockedRows = List.of(expected);
                  f.userRows = List.of(expected);
                  long actual = identity(f, Mutation.CREATE, OptionalLong.empty()).userId();
                  assertEquals(expected, actual);
                  f.ownerUnchanged();
                  return actual;
                }));
      }
      for (int index = 0; index < futures.size(); index++)
        assertEquals(index + 1L, futures.get(index).get(5, TimeUnit.SECONDS));
    } finally {
      pool.shutdownNow();
      assertTrue(pool.awaitTermination(10, TimeUnit.SECONDS));
    }
  }

  @Test
  void resource001AllPreludeAndAuthenticationStatementsFailClosedOnNull() {
    for (String label :
        List.of(CANDIDATE, ADVISORY, USERS, LOCKED, AUTH_USER, AUTH_SESSION, TOUCH)) {
      Fixture f = new Fixture();
      f.nullStatementAt = label;
      infrastructure(f, Mutation.DISABLE, OptionalLong.of(20));
      assertEquals(label, f.order.getLast());
    }
  }

  @Test
  void resource002AllPreludeAndAuthenticationNullRowsCloseTheirOwnedStatements() {
    for (String label : List.of(CANDIDATE, ADVISORY, USERS, LOCKED, AUTH_USER, AUTH_SESSION)) {
      Fixture f = new Fixture();
      f.nullRowAt = label;
      infrastructure(f, Mutation.DISABLE, OptionalLong.of(20));
      assertEquals(label, f.order.getLast());
    }
  }

  @Test
  void mutation001ClosedVocabularyLookupDefensiveValuesAndMembershipReduction() {
    assertEquals(
        List.of("CREATE", "ENABLE", "DISABLE", "PROMOTE", "DEMOTE", "RESET_PASSWORD", "UNLOCK"),
        java.util.Arrays.stream(Mutation.values()).map(Enum::name).toList());
    assertSame(Mutation.CREATE, Mutation.valueOf("CREATE"));
    assertSame(Mutation.ENABLE, Mutation.valueOf("ENABLE"));
    assertSame(Mutation.DISABLE, Mutation.valueOf("DISABLE"));
    assertSame(Mutation.PROMOTE, Mutation.valueOf("PROMOTE"));
    assertSame(Mutation.DEMOTE, Mutation.valueOf("DEMOTE"));
    assertSame(Mutation.RESET_PASSWORD, Mutation.valueOf("RESET_PASSWORD"));
    assertSame(Mutation.UNLOCK, Mutation.valueOf("UNLOCK"));
    var exposed = Mutation.values();
    exposed[0] = Mutation.UNLOCK;
    assertSame(Mutation.CREATE, Mutation.values()[0]);
    for (Mutation mutation : Mutation.values())
      assertEquals(
          List.of(Mutation.DISABLE, Mutation.DEMOTE).contains(mutation),
          mutation.reducesMembership());
    for (String unknown : List.of("UNKNOWN", "", "create", " CREATE "))
      assertThrows(IllegalArgumentException.class, () -> Mutation.valueOf(unknown));
    assertThrows(NullPointerException.class, () -> Mutation.valueOf(null));
  }
}
