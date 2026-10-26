package dev.codex.schubert.nk.api.security;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.api.domain.Role;
import dev.codex.schubert.nk.api.idempotency.EncryptedResponseSnapshot;
import dev.codex.schubert.nk.api.idempotency.InboxCompletion;
import dev.codex.schubert.nk.api.idempotency.InboxCompletionState;
import dev.codex.schubert.nk.api.idempotency.InboxResultReference;
import dev.codex.schubert.nk.api.idempotency.ResponseSnapshotCodec;
import dev.codex.schubert.nk.api.idempotency.ResponseSnapshotIdentity;
import dev.codex.schubert.nk.api.logging.ApiLogDatabaseFixture;
import dev.codex.schubert.nk.protocol.header.ResultCode;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.lang.reflect.Proxy;
import java.net.InetAddress;
import java.nio.charset.StandardCharsets;
import java.nio.file.Path;
import java.security.SecureRandom;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.function.Executable;
import org.junit.jupiter.api.io.TempDir;

/** PT-AUT-REPLAY-001..005. Independent UI232/234 byte vectors and real limited-role PostgreSQL. */
final class LoginReplayServiceTest {
  private static final String FIXTURE_LOGIN_RESPONSE = "LGNRSP01";
  private static final String FIXTURE_LAYOUT_VERSION = "001";
  private static final String FIXTURE_SUCCESS_CODE = "0000";
  private static final String FIXTURE_REPLAY_CODE = "0200";

  @TempDir static Path root;
  private static ApiLogDatabaseFixture database;
  private static AuthContextCodec contexts;
  private static ResponseSnapshotCodec snapshots;
  private static ContextHash hashes;
  private static LoginReplayService service;
  private static final Instant NOW = Instant.parse("2026-09-08T01:02:03.456789Z");
  private static final UUID REQUEST = new UUID(0, 101);
  private static final UUID RESPONSE = new UUID(0, 102);
  private static final UUID REPLAY = new UUID(0, 103);
  private static final UUID SESSION = new UUID(0, 104);
  private static final String RAW = "55".repeat(32);
  private static final String FIRST_STAMP = "20260908100203456";
  private static final String LATER_STAMP = "20260909100203456";

  @BeforeAll
  static void start() throws Exception {
    database = new ApiLogDatabaseFixture(root);
    contexts = new AuthContextCodec("a1", new byte[32], null, null);
    snapshots = new ResponseSnapshotCodec("s1", snapshotKey(), null, null);
    hashes = new ContextHash();
    service = new LoginReplayService(snapshots, contexts, hashes);
  }

  @AfterAll
  static void stop() throws Exception {
    if (contexts != null) contexts.close();
    if (snapshots != null) snapshots.close();
    if (database != null) database.stop();
  }

  @BeforeEach
  void seed() throws Exception {
    try (Connection c = database.api();
        var s = c.createStatement()) {
      s.execute("delete from schubert.app_logs");
      s.execute("delete from schubert.auth_sessions");
      s.execute("delete from schubert.app_users");
      s.execute(
          "insert into"
              + " schubert.app_users(id,username,username_key,password_hash,role,status,password_changed_at,created_at,updated_at)"
              + " values(7,'利用者','利用者','synthetic-unused',"
              + "'USER','ACTIVE','2026-09-08','2026-09-08','2026-09-08')");
    }
  }

  @Test
  void successSnapshotFreezesOriginalFieldsAndRebuildsOnlyResponseHeader() throws Exception {
    LoginResult.Success success = issue();
    for (Role role : Role.values()) {
      var result =
          new LoginResult.Success(new AuthenticatedActor(7, "利用者", role), success.issued());
      var stored = service.capture(result, REQUEST, RESPONSE, NOW);
      assertEquals(InboxCompletionState.COMPLETED, stored.state());
      assertEquals(InboxResultReference.authSession(SESSION), stored.resultReference());
      assertEquals(NOW, stored.completedAt());
      assertEquals(FIXTURE_LOGIN_RESPONSE, stored.responseLayoutId());
      assertEquals(FIXTURE_LAYOUT_VERSION, stored.responseVersion());
      byte[] original = snapshots.decrypt(identity(), stored.responseSnapshot().orElseThrow());
      assertArrayEquals(golden(role, FIXTURE_SUCCESS_CODE, RESPONSE, FIRST_STAMP, 0), original);
      assertFalse(stored.toString().contains(RAW));
      assertFalse(stored.responseSnapshot().orElseThrow().toString().contains(RAW));
      try (Connection c = database.transaction()) {
        assertArrayEquals(
            golden(role, FIXTURE_SUCCESS_CODE, REPLAY, LATER_STAMP, 0),
            service.restore(c, stored, REQUEST, REPLAY, NOW.plusSeconds(86400), false));
        assertArrayEquals(
            golden(role, FIXTURE_REPLAY_CODE, REPLAY, LATER_STAMP, 0),
            service.restore(c, stored, REQUEST, REPLAY, NOW.plusSeconds(86400), true));
        try (var s = c.createStatement()) {
          s.execute(
              "update schubert.app_users set username='Changed',role='ADMIN',status='DISABLED'");
          s.execute(
              "update schubert.auth_sessions set last_accessed_at=issued_at+interval '1"
                  + " hour',expires_at=issued_at+interval '9"
                  + " hours',revoked=true,revoked_at=issued_at+interval '2"
                  + " hours',revoke_reason='ADMIN'");
        }
        assertArrayEquals(
            golden(role, FIXTURE_REPLAY_CODE, REPLAY, LATER_STAMP, 0),
            service.restore(c, stored, REQUEST, REPLAY, NOW.plusSeconds(86400), true));
        c.rollback();
      }
      assertUnchanged();
    }
  }

  @Test
  void failureSnapshotKeepsOriginalCodeRetryAndMessage() throws Exception {
    for (int retry : new int[] {0, 1, 900}) {
      var code = retry == 0 ? ResultCode.AUTHENTICATION_FAILED : ResultCode.LOCKED;
      var stored = service.capture(new LoginResult.Failure(code, retry), REQUEST, RESPONSE, NOW);
      assertEquals(InboxCompletionState.ERROR, stored.state());
      assertEquals(InboxResultReference.none(), stored.resultReference());
      assertArrayEquals(
          golden(Role.USER, oracleResultCode(code), RESPONSE, FIRST_STAMP, retry),
          snapshots.decrypt(identity(), stored.responseSnapshot().orElseThrow()));
      try (Connection c = database.transaction()) {
        for (boolean replay : new boolean[] {false, true}) {
          assertArrayEquals(
              golden(Role.USER, oracleResultCode(code), REPLAY, LATER_STAMP, retry),
              service.restore(c, stored, REQUEST, REPLAY, NOW.plusSeconds(86400), replay));
        }
        try (var s = c.createStatement();
            var row = s.executeQuery("select count(*) from schubert.auth_sessions")) {
          assertTrue(row.next());
          assertEquals(0, row.getInt(1));
        }
        c.rollback();
      }
    }
  }

  @Test
  void tamperedMetadataWireAndSessionReferencesFailClosed() throws Exception {
    var stored = service.capture(issue(), REQUEST, RESPONSE, NOW);
    List<InboxCompletion> bad = new ArrayList<>();
    bad.add(
        copy(
            stored,
            InboxCompletionState.ERROR,
            stored.resultReference(),
            FIXTURE_LOGIN_RESPONSE,
            FIXTURE_LAYOUT_VERSION,
            stored.responseSnapshot()));
    bad.add(
        copy(
            stored,
            stored.state(),
            InboxResultReference.none(),
            FIXTURE_LOGIN_RESPONSE,
            FIXTURE_LAYOUT_VERSION,
            stored.responseSnapshot()));
    bad.add(
        copy(
            stored,
            stored.state(),
            InboxResultReference.authSession(new UUID(0, 999)),
            FIXTURE_LOGIN_RESPONSE,
            FIXTURE_LAYOUT_VERSION,
            stored.responseSnapshot()));
    bad.add(
        copy(
            stored,
            stored.state(),
            stored.resultReference(),
            "LOGRSP01",
            FIXTURE_LAYOUT_VERSION,
            stored.responseSnapshot()));
    bad.add(
        copy(
            stored,
            stored.state(),
            stored.resultReference(),
            FIXTURE_LOGIN_RESPONSE,
            "002",
            stored.responseSnapshot()));
    bad.add(
        copy(
            stored,
            stored.state(),
            stored.resultReference(),
            FIXTURE_LOGIN_RESPONSE,
            FIXTURE_LAYOUT_VERSION,
            Optional.empty()));
    var error =
        service.capture(new LoginResult.Failure(ResultCode.LOCKED, 900), REQUEST, RESPONSE, NOW);
    bad.add(
        copy(
            error,
            InboxCompletionState.COMPLETED,
            error.resultReference(),
            FIXTURE_LOGIN_RESPONSE,
            FIXTURE_LAYOUT_VERSION,
            error.responseSnapshot()));
    bad.add(
        copy(
            error,
            error.state(),
            stored.resultReference(),
            FIXTURE_LOGIN_RESPONSE,
            FIXTURE_LAYOUT_VERSION,
            error.responseSnapshot()));
    byte[] cipher = stored.responseSnapshot().orElseThrow().ciphertext();
    bad.add(
        copy(
            stored,
            stored.state(),
            stored.resultReference(),
            FIXTURE_LOGIN_RESPONSE,
            FIXTURE_LAYOUT_VERSION,
            Optional.of(new EncryptedResponseSnapshot("unknown", cipher))));
    cipher[cipher.length - 1] ^= 1;
    bad.add(
        copy(
            stored,
            stored.state(),
            stored.resultReference(),
            FIXTURE_LOGIN_RESPONSE,
            FIXTURE_LAYOUT_VERSION,
            Optional.of(new EncryptedResponseSnapshot("s1", cipher))));
    try (Connection c = database.transaction()) {
      for (var item : bad) rejected(() -> service.restore(c, item, REQUEST, REPLAY, NOW, true));
      rejected(() -> service.restore(c, stored, new UUID(0, 999), REPLAY, NOW, true));
      c.rollback();
    }
    List<byte[]> corrupt = new ArrayList<>();
    byte[] good = golden(Role.USER, FIXTURE_SUCCESS_CODE, RESPONSE, FIRST_STAMP, 0);
    corrupt.add(new byte[0]);
    corrupt.add(Arrays.copyOf(good, 687));
    corrupt.add(Arrays.copyOf(good, 689));
    for (var mutation :
        List.of(
            new String[] {"0", "INVALID!"},
            new String[] {"60", REPLAY.toString()},
            new String[] {"208", FIXTURE_REPLAY_CODE},
            new String[] {"208", "9000"},
            new String[] {"320", "OTHER"},
            new String[] {"325", "66".repeat(32)},
            new String[] {"389", "20260908100203457"},
            new String[] {"406", "20260908180203457"},
            new String[] {"423", "000001"},
            new String[] {"256", "\n"})) {
      byte[] body = good.clone();
      put(body, Integer.parseInt(mutation[0]), mutation[1]);
      corrupt.add(body);
    }
    // Valid different layout header with 688 physical bytes: peek alone does not bind the route.
    byte[] other = good.clone();
    put(other, 11, "LOGRSP01");
    put(other, 113, RAW);
    put(other, 181, "000024");
    put(other, 199, "000000280");
    corrupt.add(other);
    for (byte[] body : corrupt) {
      var item =
          copy(
              stored,
              stored.state(),
              stored.resultReference(),
              FIXTURE_LOGIN_RESPONSE,
              FIXTURE_LAYOUT_VERSION,
              Optional.of(snapshots.encrypt(identity(), body)));
      try (Connection c = database.transaction()) {
        rejected(() -> service.restore(c, item, REQUEST, REPLAY, NOW, true));
        c.rollback();
      }
    }
    // Error wire can be syntactically valid yet not a deterministic stored Login result.
    byte[] wrongCode = golden(Role.USER, "0101", RESPONSE, FIRST_STAMP, 0);
    put(wrongCode, 208, "9000");
    var item =
        copy(
            error,
            error.state(),
            error.resultReference(),
            FIXTURE_LOGIN_RESPONSE,
            FIXTURE_LAYOUT_VERSION,
            Optional.of(snapshots.encrypt(identity(), wrongCode)));
    try (Connection c = database.transaction()) {
      rejected(() -> service.restore(c, item, REQUEST, REPLAY, NOW, true));
      c.rollback();
    }
    for (String change :
        List.of(
            "created_message_id='00000000-0000-0000-0000-000000000999'",
            "context_hash=repeat('6',64)",
            "issued_at=issued_at-interval '1 second'")) {
      try (Connection c = database.transaction();
          var s = c.createStatement()) {
        s.executeUpdate("update schubert.auth_sessions set " + change);
        rejected(() -> service.restore(c, stored, REQUEST, REPLAY, NOW, true));
        c.rollback();
      }
    }
    assertUnchanged();
  }

  @Test
  void jdbcNullFaultsAndInvalidArgumentsNeverLeakOrMutate() throws Exception {
    var result = issue();
    var stored = service.capture(result, REQUEST, RESPONSE, NOW);
    for (String point :
        List.of(
            "getAutoCommit",
            "prepareStatement",
            "setObject",
            "executeQuery",
            "next",
            "statementClose",
            "rowClose",
            "missing",
            "badOwner",
            "badCipher",
            "badKey",
            "null:user_id",
            "null:created_message_id",
            "null:context_hash",
            "null:context_ciphertext",
            "null:key_version",
            "null:issued_at")) {
      try (Connection c = database.transaction()) {
        rejected(() -> service.restore(fault(c, point), stored, REQUEST, REPLAY, NOW, true));
        assertFalse(c.isClosed());
        assertFalse(c.getAutoCommit());
        c.rollback();
      }
    }
    try (Connection c = database.api()) {
      rejected(() -> service.restore(c, stored, REQUEST, REPLAY, NOW, true));
    }
    assertThrows(NullPointerException.class, () -> new LoginReplayService(null, contexts, hashes));
    assertThrows(NullPointerException.class, () -> new LoginReplayService(snapshots, null, hashes));
    assertThrows(
        NullPointerException.class, () -> new LoginReplayService(snapshots, contexts, null));
    assertThrows(NullPointerException.class, () -> service.capture(null, REQUEST, RESPONSE, NOW));
    assertThrows(NullPointerException.class, () -> service.capture(result, null, RESPONSE, NOW));
    assertThrows(NullPointerException.class, () -> service.capture(result, REQUEST, null, NOW));
    assertThrows(
        NullPointerException.class, () -> service.capture(result, REQUEST, RESPONSE, null));
    try (Connection c = database.transaction()) {
      assertThrows(
          NullPointerException.class,
          () -> service.restore(null, stored, REQUEST, REPLAY, NOW, true));
      assertThrows(
          NullPointerException.class, () -> service.restore(c, null, REQUEST, REPLAY, NOW, true));
      assertThrows(
          NullPointerException.class, () -> service.restore(c, stored, null, REPLAY, NOW, true));
      assertThrows(
          NullPointerException.class, () -> service.restore(c, stored, REQUEST, null, NOW, true));
      assertThrows(
          NullPointerException.class,
          () -> service.restore(c, stored, REQUEST, REPLAY, null, true));
      c.rollback();
    }
    var closed = new ResponseSnapshotCodec("s1", snapshotKey(), null, null);
    var closedService = new LoginReplayService(closed, contexts, hashes);
    closed.close();
    rejected(() -> closedService.capture(result, REQUEST, RESPONSE, NOW));
    try (Connection c = database.transaction()) {
      rejected(() -> closedService.restore(c, stored, REQUEST, REPLAY, NOW, true));
      c.rollback();
    }
    assertUnchanged();
  }

  @Test
  void concurrentReplayAndKeyRotationPreserveExactData() throws Exception {
    var stored = service.capture(issue(), REQUEST, RESPONSE, NOW);
    try (var rotatedContexts = new AuthContextCodec("a2", snapshotKey(), "a1", new byte[32]);
        var rotatedSnapshots = new ResponseSnapshotCodec("s2", new byte[32], "s1", snapshotKey());
        var executor = Executors.newFixedThreadPool(16)) {
      var rotated = new LoginReplayService(rotatedSnapshots, rotatedContexts, hashes);
      List<Future<byte[]>> futures = new ArrayList<>();
      for (int i = 0; i < 100; i++) {
        final UUID id = new UUID(0, 1000 + i);
        futures.add(
            executor.submit(
                () -> {
                  try (Connection c = database.transaction()) {
                    byte[] response =
                        rotated.restore(c, stored, REQUEST, id, NOW.plusSeconds(86400), true);
                    c.commit();
                    return response;
                  }
                }));
      }
      for (int i = 0; i < futures.size(); i++)
        assertArrayEquals(
            golden(Role.USER, FIXTURE_REPLAY_CODE, new UUID(0, 1000 + i), LATER_STAMP, 0),
            futures.get(i).get());
    }
    try (var wrong = new AuthContextCodec("a1", snapshotKey(), null, null);
        Connection c = database.transaction()) {
      var invalid = new LoginReplayService(snapshots, wrong, hashes);
      rejected(() -> invalid.restore(c, stored, REQUEST, REPLAY, NOW, true));
      c.rollback();
    }
    assertUnchanged();
  }

  private static LoginResult.Success issue() throws Exception {
    var deterministic =
        new SecureRandom() {
          private static final long serialVersionUID = 1L;

          @Override
          public void nextBytes(byte[] bytes) {
            Arrays.fill(bytes, (byte) 0x55);
          }
        };
    var sessions = new AuthSessionService(hashes, contexts, deterministic, () -> SESSION);
    try (Connection c = database.transaction()) {
      var issued = sessions.issue(c, 7, InetAddress.ofLiteral("127.0.0.1"), REQUEST, REQUEST, NOW);
      c.commit();
      return new LoginResult.Success(new AuthenticatedActor(7, "利用者", Role.USER), issued);
    }
  }

  private static void assertUnchanged() throws SQLException {
    try (Connection c = database.api();
        var s = c.createStatement();
        var row =
            s.executeQuery(
                "select issued_at,last_accessed_at,expires_at,revoked,(select count(*) from"
                    + " schubert.app_logs) logs from schubert.auth_sessions")) {
      assertTrue(row.next());
      assertEquals(NOW, row.getObject(1, java.time.OffsetDateTime.class).toInstant());
      assertEquals(NOW, row.getObject(2, java.time.OffsetDateTime.class).toInstant());
      assertEquals(
          Instant.parse("2026-09-08T09:02:03.456789Z"),
          row.getObject(3, java.time.OffsetDateTime.class).toInstant());
      assertFalse(row.getBoolean(4));
      assertEquals(0, row.getInt(5));
      assertFalse(row.next());
    }
  }

  static byte[] golden(Role role, String code, UUID responseId, String sent, int retry) {
    byte[] body = new byte[688];
    Arrays.fill(body, (byte) ' ');
    // UI232 §3 fields 1..6: response=S, synchronous=S (BUG-026/YKT-023).
    put(body, 0, "SCHBNK01");
    put(body, 8, FIXTURE_LAYOUT_VERSION);
    put(body, 11, FIXTURE_LOGIN_RESPONSE);
    put(body, 19, FIXTURE_LAYOUT_VERSION);
    put(body, 22, "S");
    put(body, 23, "S");
    put(body, 24, responseId.toString());
    put(body, 60, REQUEST.toString());
    put(body, 96, sent);
    put(body, 177, "0256");
    put(body, 181, "000432");
    put(body, 187, "000000");
    put(body, 193, "000000");
    put(body, 199, "000000688");
    put(body, 208, code);
    put(body, 423, retry == 0 ? "000000000" : retry == 1 ? "000001000" : "000900000");
    if (code.equals(FIXTURE_SUCCESS_CODE) || code.equals(FIXTURE_REPLAY_CODE)) {
      put(body, 256, "利用者");
      put(body, 320, role == Role.ADMIN ? "ADMIN" : "USER");
      put(body, 325, RAW);
      put(body, 389, "20260908100203456");
      put(body, 406, "20260908180203456");
    } else {
      put(
          body,
          432,
          code.equals("0101")
              ? "ユーザー名またはパスワードが正しくありません。"
              : "ログイン試行回数が上限に達しました。15分ほど待ってから再度お試しください。");
    }
    return body;
  }

  private static void put(byte[] body, int offset, String value) {
    byte[] bytes = value.getBytes(StandardCharsets.UTF_8);
    System.arraycopy(bytes, 0, body, offset, bytes.length);
  }

  private static byte[] snapshotKey() {
    byte[] bytes = new byte[32];
    Arrays.fill(bytes, (byte) 3);
    return bytes;
  }

  private static ResponseSnapshotIdentity identity() {
    return ResponseSnapshotIdentity.anonymous(
        REQUEST, FIXTURE_LOGIN_RESPONSE, FIXTURE_LAYOUT_VERSION);
  }

  private static InboxCompletion copy(
      InboxCompletion source,
      InboxCompletionState state,
      InboxResultReference reference,
      String layout,
      String version,
      Optional<EncryptedResponseSnapshot> snapshot) {
    return new InboxCompletion(state, reference, layout, version, snapshot, source.completedAt());
  }

  private static void rejected(Executable action) {
    var failure = assertThrows(AuthenticationInfrastructureException.class, action);
    assertEquals("authentication storage is unavailable", failure.getMessage());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
  }

  private static Connection fault(Connection connection, String point) {
    return (Connection)
        Proxy.newProxyInstance(
            Connection.class.getClassLoader(),
            new Class<?>[] {Connection.class},
            (p, m, a) -> {
              if (m.getName().equals(point)) throw new SQLException("synthetic-sensitive-provider");
              Object result = invoke(connection, m, a);
              if (!m.getName().equals("prepareStatement")) return result;
              return Proxy.newProxyInstance(
                  PreparedStatement.class.getClassLoader(),
                  new Class<?>[] {PreparedStatement.class},
                  (sp, sm, sa) -> {
                    if (sm.getName().equals(point))
                      throw new SQLException("synthetic-sensitive-provider");
                    Object sr = invoke(result, sm, sa);
                    if (sm.getName().equals("close") && point.equals("statementClose"))
                      throw new SQLException("synthetic-sensitive-close");
                    if (!sm.getName().equals("executeQuery")) return sr;
                    return Proxy.newProxyInstance(
                        ResultSet.class.getClassLoader(),
                        new Class<?>[] {ResultSet.class},
                        (rp, rm, ra) -> {
                          if (rm.getName().equals(point))
                            throw new SQLException("synthetic-sensitive-provider");
                          if (rm.getName().equals("next") && point.equals("missing")) return false;
                          if (point.startsWith("null:")
                              && ra != null
                              && point.substring(5).equals(ra[0])) return null;
                          if (ra != null && ra.length > 0) {
                            if (point.equals("badOwner") && ra[0].equals("user_id")) return 0L;
                            if (point.equals("badKey") && ra[0].equals("key_version"))
                              return "unknown";
                            if (point.equals("badCipher") && ra[0].equals("context_ciphertext"))
                              return new byte[101];
                          }
                          Object rr = invoke(sr, rm, ra);
                          if (rm.getName().equals("close") && point.equals("rowClose"))
                            throw new SQLException("synthetic-sensitive-close");
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

  /** UI232 section7 literal oracle; never call Production wireValue. */
  private static String oracleResultCode(ResultCode code) {
    return switch (code) {
      case SUCCESS -> FIXTURE_SUCCESS_CODE;
      case VALIDATION_ERROR -> "0100";
      case AUTHENTICATION_FAILED -> "0101";
      case SESSION_INVALID -> "0102";
      case FORBIDDEN -> "0103";
      case NOT_FOUND -> "0104";
      case CONFLICT -> "0105";
      case LOCKED -> "0106";
      case NOT_CANCELLABLE -> "0107";
      case IDEMPOTENT_SUCCESS -> FIXTURE_REPLAY_CODE;
      case TEMPORARY_FAILURE -> "9000";
      case RESOURCE_LIMIT -> "9001";
    };
  }
}
