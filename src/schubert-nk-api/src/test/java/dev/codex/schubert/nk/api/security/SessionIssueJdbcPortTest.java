package dev.codex.schubert.nk.api.security;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import java.lang.reflect.InvocationHandler;
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
import java.util.HexFormat;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import org.jspecify.annotations.Nullable;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Timeout;

/** PT-AUT-ISS001..008; DIF016/UI226/SS314332352. Public vectors, fake JDBC, no live session. */
@Timeout(value = 30, threadMode = Timeout.ThreadMode.SEPARATE_THREAD)
final class SessionIssueJdbcPortTest {
  private static final Instant NOW = Instant.parse("2026-11-06T00:00:00.123456789Z");
  private static final Instant ISSUED = Instant.parse("2026-11-06T00:00:00.123456Z");
  private static final Instant EXPIRES = Instant.parse("2026-11-06T08:00:00.123456Z");
  private static final UUID SESSION = UUID.fromString("00000000-0000-4000-8000-000000000007");
  private static final UUID MESSAGE = new UUID(0, 10);
  private static final UUID CORRELATION = new UUID(0, 11);
  private static final UUID OLDEST = new UUID(0, 1);
  private static final UUID SECOND = new UUID(0, 2);
  private static final String VERSION = "fixture-v1";
  private static final String PUBLIC_HASH =
      "ffe054fe7ae0cb6dc65c3af9b61d5209f439851db43d0ba5997337df154668eb";
  private static final String USER_SQL =
      "select status from schubert.app_users where id=? for update";
  private static final String INSERT_SQL =
      "insert into schubert.auth_sessions"
          + " (id,user_id,context_hash,context_ciphertext,key_version,issued_at,last_accessed_at,expires_at,client_address,created_message_id)"
          + " values(?,?,?,?,?,?,?,?,cast(? as inet),?)";
  private static final String ACTIVE_SQL =
      "select id from schubert.auth_sessions where user_id=? and not revoked and expires_at>? order"
          + " by last_accessed_at,id for update";
  private static final String REPLACE_SQL =
      "update schubert.auth_sessions set revoked=true,revoked_at=?,revoke_reason='REPLACED' where"
          + " id=? and not revoked";
  private static final String AUDIT_SQL =
      "insert into schubert.app_logs"
          + " (logged_at,service,category,level,action,message,message_id,correlation_id,actor_user_id,remote_address,details)"
          + " values(?,'API','SECURITY','INFO','SESSION_REVOKED','SESSION_REVOKED',?,?,?,cast(? as"
          + " inet),cast(? as jsonb))";
  private static final String USER = "user";
  private static final String INSERT = "insert";
  private static final String ACTIVE = "active";
  private static final String REPLACE = "replace";
  private static final String AUDIT = "audit";
  private static final String PUBLIC_MARKER = "ordinary-session-issue-fixture-marker";
  private static final String INFRA_MESSAGE = "authentication storage is unavailable";
  private static final Map<Long, String> GOLDEN =
      Map.of(
          1L,
          "4e4b454e4331010a666978747572652d7631111111111111111111111111c56e5089bcfc5332a6c2a7fcf862083a51fbeb685c84cef344e0441803b144b6df411cb2cd4ed6a8c6801777acbc27429a7262a4e9b82245c203715b87b293aac8ceeffe0cd616b433ff264e4842563f",
          7L,
          "4e4b454e4331010a666978747572652d7631111111111111111111111111c56e5089bcfc5332a6c2a7fcf862083a51fbeb685c84cef344e0441803b144b6df411cb2cd4ed6a8c6801777acbc27429a7262a4e9b82245c203715b87b293aa2079fe26ed5f3d44bc38b22dcac6c805",
          999999999999L,
          "4e4b454e4331010a666978747572652d7631111111111111111111111111c56e5089bcfc5332a6c2a7fcf862083a51fbeb685c84cef344e0441803b144b6df411cb2cd4ed6a8c6801777acbc27429a7262a4e9b82245c203715b87b293aa45dc8be7cf1cb96620086e6482a3270f");

  private static <T> T proxy(Class<T> type, InvocationHandler handler) {
    return type.cast(Proxy.newProxyInstance(type.getClassLoader(), new Class<?>[] {type}, handler));
  }

  private static final class FixedRandom extends SecureRandom {
    private static final long serialVersionUID = 1L;
    final byte value;
    byte @Nullable [] last;
    @Nullable RuntimeException failure;

    FixedRandom(byte value) {
      this.value = value;
    }

    @Override
    public void nextBytes(byte[] bytes) {
      last = bytes;
      Arrays.fill(bytes, value);
      if (failure != null) throw failure;
    }
  }

  private static InetAddress client() throws Exception {
    return InetAddress.getByAddress(new byte[] {127, 0, 0, 1});
  }

  private static final class Fixture implements AutoCloseable {
    final ContextHash hashes = new ContextHash();
    final FixedRandom rawRandom = new FixedRandom((byte) 0xaa);
    final FixedRandom nonceRandom = new FixedRandom((byte) 0x11);
    final AuthContextCodec codec =
        new AuthContextCodec(VERSION, new byte[32], null, null, nonceRandom);
    final AuthSessionService service =
        new AuthSessionService(hashes, codec, rawRandom, () -> SESSION);
    final List<String> sqlOrder = new ArrayList<>();
    final List<Map<Integer, Object>> bindings = new ArrayList<>();
    final List<String> acquired = new ArrayList<>();
    final List<String> closed = new ArrayList<>();
    final List<String> badCloses = new ArrayList<>();
    List<UUID> active = List.of(SESSION);
    boolean userExists = true;
    @Nullable String status = "ACTIVE";
    boolean autoCommit;
    int inserted = 1;
    int replaced = 1;
    int audited = 1;
    int ownerChanges;
    String failAt = "";
    String nullStatementAt = "";
    String nullRowAt = "";
    @Nullable RuntimeException runtimeFailure;
    byte @Nullable [] borrowedCiphertext;
    byte @Nullable [] receivedCiphertext;

    Fixture() throws Exception {}

    void fault(String at) throws SQLException {
      if (at.equals(failAt)) {
        if (runtimeFailure != null) throw runtimeFailure;
        throw new SQLException(PUBLIC_MARKER, "08006");
      }
    }

    void close(String name) throws SQLException {
      closed.add(name);
      if (badCloses.contains(name)) throw new SQLException(PUBLIC_MARKER, "08006");
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
            case USER_SQL -> USER;
            case INSERT_SQL -> INSERT;
            case ACTIVE_SQL -> ACTIVE;
            case REPLACE_SQL -> REPLACE;
            case AUDIT_SQL -> AUDIT;
            default -> throw new AssertionError("SQL outside independently fixed session contract");
          };
      sqlOrder.add(label);
      fault(label + ".prepare");
      if (label.equals(nullStatementAt)) return null;
      String name = label + "-" + sqlOrder.size();
      acquired.add(name + ".statement");
      Map<Integer, Object> bound = new HashMap<>();
      bindings.add(bound);
      return proxy(
          PreparedStatement.class,
          (p, m, a) -> {
            fault(label + "." + m.getName());
            return switch (m.getName()) {
              case "setLong", "setString", "setObject" -> {
                bound.put((Integer) a[0], a[1]);
                yield null;
              }
              case "setBytes" -> {
                borrowedCiphertext = (byte[]) a[1];
                receivedCiphertext = borrowedCiphertext.clone();
                bound.put((Integer) a[0], "PUBLIC_SYNTHETIC_CIPHERTEXT_CHECKED_SEPARATELY");
                yield null;
              }
              case "executeUpdate" ->
                  label.equals(INSERT) ? inserted : label.equals(REPLACE) ? replaced : audited;
              case "executeQuery" -> row(label, name);
              case "close" -> {
                close(name + ".statement");
                yield null;
              }
              default -> throw new AssertionError("unregistered statement method " + m.getName());
            };
          });
    }

    @Nullable ResultSet row(String label, String name) {
      if (label.equals(nullRowAt)) return null;
      acquired.add(name + ".row");
      int[] index = {-1};
      return proxy(
          ResultSet.class,
          (p, m, a) -> {
            fault(label + "." + m.getName());
            return switch (m.getName()) {
              case "next" -> {
                index[0]++;
                yield index[0] < (label.equals(USER) ? (userExists ? 1 : 0) : active.size());
              }
              case "getString" -> {
                assertEquals("status", a[0]);
                yield status;
              }
              case "getObject" -> {
                assertEquals("id", a[0]);
                assertSame(UUID.class, a[1]);
                yield active.get(index[0]);
              }
              case "close" -> {
                close(name + ".row");
                yield null;
              }
              default -> throw new AssertionError("unregistered row method " + m.getName());
            };
          });
    }

    IssuedContext issue() throws Exception {
      return service.issue(connection(), 7, client(), MESSAGE, CORRELATION, NOW);
    }

    void ownershipAndBuffers() {
      assertEquals(0, ownerChanges);
      assertEquals(acquired.size(), closed.size());
      for (String n : acquired) assertEquals(1, closed.stream().filter(n::equals).count());
      if (rawRandom.last != null) assertArrayEquals(new byte[32], rawRandom.last);
      if (nonceRandom.last != null) assertArrayEquals(new byte[12], nonceRandom.last);
      if (borrowedCiphertext != null) assertArrayEquals(new byte[110], borrowedCiphertext);
    }

    @Override
    public void close() {
      codec.close();
      if (receivedCiphertext != null) Arrays.fill(receivedCiphertext, (byte) 0);
    }
  }

  private static void infra(Fixture f) {
    var failure = assertThrows(AuthenticationInfrastructureException.class, f::issue);
    assertEquals(INFRA_MESSAGE, failure.getMessage());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
    f.ownershipAndBuffers();
  }

  @Test
  void insertsIndependentEnvelopeHashUtcAndEightHourExpiry() throws Exception {
    for (long id : new long[] {1, 7, 999_999_999_999L})
      try (Fixture f = new Fixture()) {
        var out = f.service.issue(f.connection(), id, client(), MESSAGE, CORRELATION, NOW);
        assertEquals(new AuthContextIdentity(SESSION, id), out.identity());
        assertEquals(AuthenticationContext.of("a".repeat(64)), out.context());
        assertEquals(ISSUED, out.issuedAt());
        assertEquals(EXPIRES, out.expiresAt());
        assertEquals("IssuedContext[REDACTED]", out.toString());
        assertEquals(List.of(USER, INSERT, ACTIVE), f.sqlOrder);
        assertEquals(Map.of(1, id), f.bindings.get(0));
        var insert = f.bindings.get(1);
        assertEquals(10, insert.size());
        assertEquals(SESSION, insert.get(1));
        assertEquals(id, insert.get(2));
        assertEquals(PUBLIC_HASH, insert.get(3));
        assertEquals(VERSION, insert.get(5));
        assertEquals(ISSUED.atOffset(ZoneOffset.UTC), insert.get(6));
        assertEquals(insert.get(6), insert.get(7));
        assertEquals(EXPIRES.atOffset(ZoneOffset.UTC), insert.get(8));
        assertEquals("127.0.0.1", insert.get(9));
        assertEquals(MESSAGE, insert.get(10));
        assertArrayEquals(HexFormat.of().parseHex(GOLDEN.get(id)), f.receivedCiphertext);
        assertEquals(Map.of(1, id, 2, ISSUED.atOffset(ZoneOffset.UTC)), f.bindings.get(2));
        f.ownershipAndBuffers();
      }
    try (Fixture f = new Fixture()) {
      var out =
          f.service.issue(
              f.connection(),
              7,
              client(),
              MESSAGE,
              CORRELATION,
              Instant.parse("1582-10-04T01:02:03.123456789Z"));
      assertEquals(Instant.parse("1582-10-04T01:02:03.123456Z"), out.issuedAt());
      assertEquals(Instant.parse("1582-10-04T09:02:03.123456Z"), out.expiresAt());
      f.ownershipAndBuffers();
    }
  }

  @Test
  void dif016RetainsTwoAndReplacesOldestWithAtomicAuditStaging() throws Exception {
    for (List<UUID> rows :
        List.of(
            List.of(SESSION),
            List.of(OLDEST, SESSION),
            List.of(OLDEST, SECOND, SESSION),
            List.of(OLDEST, SECOND, new UUID(0, 3), SESSION)))
      try (Fixture f = new Fixture()) {
        f.active = rows;
        f.issue();
        int revoke = Math.max(0, rows.size() - 2);
        assertEquals(3 + 2 * revoke, f.sqlOrder.size());
        for (int i = 0; i < revoke; i++) {
          int at = 3 + 2 * i;
          assertEquals(REPLACE, f.sqlOrder.get(at));
          assertEquals(AUDIT, f.sqlOrder.get(at + 1));
          assertEquals(
              Map.of(1, ISSUED.atOffset(ZoneOffset.UTC), 2, rows.get(i)), f.bindings.get(at));
          var audit = f.bindings.get(at + 1);
          assertEquals(ISSUED.atOffset(ZoneOffset.UTC), audit.get(1));
          assertEquals(MESSAGE, audit.get(2));
          assertEquals(CORRELATION, audit.get(3));
          assertEquals(7L, audit.get(4));
          assertEquals("127.0.0.1", audit.get(5));
          assertEquals(
              "{\"targetUserId\":7,\"reason\":\"REPLACED\",\"resultCode\":\"0000\"}", audit.get(6));
        }
        f.ownershipAndBuffers();
      }
  }

  @Test
  void publicAndInjectedConstructorsAndApiNullBoundsAreExplicit() throws Exception {
    try (Fixture f = new Fixture()) {
      assertThrows(NullPointerException.class, () -> new AuthSessionService(null, f.codec));
      assertThrows(NullPointerException.class, () -> new AuthSessionService(f.hashes, null));
      assertThrows(
          NullPointerException.class,
          () -> new AuthSessionService(f.hashes, f.codec, null, () -> SESSION));
      assertThrows(
          NullPointerException.class,
          () -> new AuthSessionService(f.hashes, f.codec, f.rawRandom, null));
      assertThrows(
          NullPointerException.class,
          () -> f.service.issue(null, 7, client(), MESSAGE, CORRELATION, NOW));
      assertThrows(
          NullPointerException.class,
          () -> f.service.issue(f.connection(), 7, null, MESSAGE, CORRELATION, NOW));
      assertThrows(
          NullPointerException.class,
          () -> f.service.issue(f.connection(), 7, client(), null, CORRELATION, NOW));
      assertThrows(
          NullPointerException.class,
          () -> f.service.issue(f.connection(), 7, client(), MESSAGE, null, NOW));
      assertThrows(
          NullPointerException.class,
          () -> f.service.issue(f.connection(), 7, client(), MESSAGE, CORRELATION, null));
      for (long id : new long[] {-1, 0, 1_000_000_000_000L})
        assertThrows(
            IllegalArgumentException.class,
            () -> f.service.issue(f.connection(), id, client(), MESSAGE, CORRELATION, NOW));
      assertThrows(
          java.time.DateTimeException.class,
          () -> f.service.issue(f.connection(), 7, client(), MESSAGE, CORRELATION, Instant.MAX));
      assertTrue(f.sqlOrder.isEmpty());
      f.ownershipAndBuffers();
    }
    try (Fixture f = new Fixture()) {
      f.autoCommit = true;
      var ordinary = new AuthSessionService(f.hashes, f.codec);
      assertThrows(
          AuthenticationInfrastructureException.class,
          () -> ordinary.issue(f.connection(), 7, client(), MESSAGE, CORRELATION, NOW));
      assertTrue(f.sqlOrder.isEmpty());
      assertNull(f.rawRandom.last);
      f.ownershipAndBuffers();
    }
  }

  @Test
  void absentDisabledAndMissingColumnsFailBeforeIssuanceOrReplacement() throws Exception {
    try (Fixture f = new Fixture()) {
      f.userExists = false;
      assertThrows(AuthenticationContextException.class, f::issue);
      assertEquals(List.of(USER), f.sqlOrder);
      assertNull(f.rawRandom.last);
      f.ownershipAndBuffers();
    }
    try (Fixture f = new Fixture()) {
      f.status = "DISABLED";
      assertThrows(AuthenticationContextException.class, f::issue);
      assertEquals(List.of(USER), f.sqlOrder);
      f.ownershipAndBuffers();
    }
    try (Fixture f = new Fixture()) {
      f.status = null;
      infra(f);
      assertEquals(List.of(USER), f.sqlOrder);
    }
    try (Fixture f = new Fixture()) {
      f.active = new ArrayList<>();
      f.active.add(null);
      infra(f);
      assertFalse(f.sqlOrder.contains(REPLACE));
    }
  }

  @Test
  void insertReplacementAndAuditRequireExactlyOneAffectedRow() throws Exception {
    for (int invalid : new int[] {0, 2}) {
      try (Fixture f = new Fixture()) {
        f.inserted = invalid;
        infra(f);
        assertEquals(List.of(USER, INSERT), f.sqlOrder);
      }
      try (Fixture f = new Fixture()) {
        f.active = List.of(OLDEST, SECOND, SESSION);
        f.replaced = invalid;
        infra(f);
        assertEquals(List.of(USER, INSERT, ACTIVE, REPLACE), f.sqlOrder);
      }
      try (Fixture f = new Fixture()) {
        f.active = List.of(OLDEST, SECOND, SESSION);
        f.audited = invalid;
        infra(f);
        assertEquals(List.of(USER, INSERT, ACTIVE, REPLACE, AUDIT), f.sqlOrder);
      }
    }
  }

  @Test
  void ordinaryJdbcAndEveryOwnedCloseFailWithFixedRedaction() throws Exception {
    for (String label : List.of(USER, INSERT, ACTIVE, REPLACE, AUDIT)) {
      for (String method :
          List.of(
              "prepare",
              label.equals(USER) || label.equals(ACTIVE) ? "executeQuery" : "executeUpdate"))
        try (Fixture f = new Fixture()) {
          f.active = List.of(OLDEST, SECOND, SESSION);
          f.failAt = label + "." + method;
          infra(f);
        }
    }
    for (String close :
        List.of(
            "user-1.row",
            "user-1.statement",
            "insert-2.statement",
            "active-3.row",
            "active-3.statement",
            "replace-4.statement",
            "audit-5.statement"))
      try (Fixture f = new Fixture()) {
        f.active = List.of(OLDEST, SECOND, SESSION);
        f.badCloses.add(close);
        infra(f);
      }
    for (String point :
        List.of(
            "getAutoCommit",
            "user.next",
            "user.getString",
            "insert.setObject",
            "insert.setLong",
            "insert.setString",
            "insert.setBytes",
            "active.setLong",
            "active.setObject",
            "active.next",
            "active.getObject",
            "replace.setObject",
            "audit.setLong",
            "audit.setString")) {
      try (Fixture f = new Fixture()) {
        f.active = List.of(OLDEST, SECOND, SESSION);
        f.failAt = point;
        infra(f);
      }
    }
    try (Fixture f = new Fixture()) {
      f.userExists = false;
      f.badCloses.add("user-1.row");
      infra(f);
    }
  }

  @Test
  void randomCodecAndUnknownRuntimeFailuresKeepBuffersAndIdentity() throws Exception {
    try (Fixture f = new Fixture()) {
      f.rawRandom.failure = new IllegalStateException(PUBLIC_MARKER);
      assertSame(f.rawRandom.failure, assertThrows(IllegalStateException.class, f::issue));
      assertEquals(List.of(USER), f.sqlOrder);
      f.ownershipAndBuffers();
    }
    try (Fixture f = new Fixture()) {
      f.nonceRandom.failure = new IllegalStateException(PUBLIC_MARKER);
      assertSame(f.nonceRandom.failure, assertThrows(IllegalStateException.class, f::issue));
      f.ownershipAndBuffers();
    }
    try (Fixture f = new Fixture()) {
      f.codec.close();
      assertThrows(IllegalStateException.class, f::issue);
      assertEquals(List.of(USER), f.sqlOrder);
      f.ownershipAndBuffers();
    }
    try (Fixture f = new Fixture()) {
      f.runtimeFailure = new IllegalStateException(PUBLIC_MARKER);
      f.failAt = ACTIVE + ".executeQuery";
      assertSame(f.runtimeFailure, assertThrows(IllegalStateException.class, f::issue));
      f.ownershipAndBuffers();
    }
  }

  @Test
  void parallelPrivateFixturesDoNotShareContextBuffersOrAuditState() throws Exception {
    var workers = Executors.newFixedThreadPool(2);
    try {
      List<Future<Integer>> results = new ArrayList<>();
      for (int i = 0; i < 16; i++) {
        int count = i % 2 == 0 ? 2 : 3;
        results.add(
            workers.submit(
                () -> {
                  try (Fixture f = new Fixture()) {
                    f.active =
                        count == 2 ? List.of(OLDEST, SESSION) : List.of(OLDEST, SECOND, SESSION);
                    f.issue();
                    assertArrayEquals(
                        HexFormat.of().parseHex(GOLDEN.get(7L)), f.receivedCiphertext);
                    f.ownershipAndBuffers();
                    return f.sqlOrder.size();
                  }
                }));
      }
      for (int i = 0; i < results.size(); i++)
        assertEquals(i % 2 == 0 ? 3 : 5, results.get(i).get(5, TimeUnit.SECONDS));
    } finally {
      workers.shutdownNow();
      assertTrue(workers.awaitTermination(10, TimeUnit.SECONDS));
    }
  }

  @Test
  void resource001NullStatementsFailClosedWithoutLeakingOwnedBuffers() throws Exception {
    for (String label : List.of(USER, INSERT, ACTIVE, REPLACE, AUDIT)) {
      try (Fixture f = new Fixture()) {
        f.active = List.of(OLDEST, SECOND, SESSION);
        f.nullStatementAt = label;
        infra(f);
        assertEquals(label, f.sqlOrder.getLast());
        assertEquals(0, f.ownerChanges);
      }
    }
  }

  @Test
  void resource002NullRowsStillCloseTheirStatementExactlyOnce() throws Exception {
    for (String label : List.of(USER, ACTIVE)) {
      try (Fixture f = new Fixture()) {
        f.nullRowAt = label;
        infra(f);
        assertEquals(label, f.sqlOrder.getLast());
        assertEquals(0, f.ownerChanges);
      }
    }
  }
}
