package dev.codex.schubert.nk.api.security;

import static org.junit.jupiter.api.Assertions.*;

import dev.codex.schubert.nk.api.domain.Role;
import dev.codex.schubert.nk.api.idempotency.*;
import dev.codex.schubert.nk.api.logging.ApiLogDatabaseFixture;
import dev.codex.schubert.nk.protocol.codec.PermanentProtocolException;
import dev.codex.schubert.nk.protocol.header.*;
import dev.codex.schubert.nk.protocol.layout.*;
import java.io.ByteArrayOutputStream;
import java.io.DataOutputStream;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.lang.reflect.Proxy;
import java.net.InetAddress;
import java.nio.charset.StandardCharsets;
import java.nio.file.Path;
import java.security.SecureRandom;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.SQLException;
import java.time.Clock;
import java.time.Instant;
import java.time.ZoneOffset;
import java.time.temporal.ChronoUnit;
import java.util.*;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicLong;
import java.util.concurrent.atomic.AtomicReference;
import javax.crypto.Mac;
import javax.crypto.SecretKeyFactory;
import javax.crypto.spec.PBEKeySpec;
import javax.crypto.spec.SecretKeySpec;
import org.junit.jupiter.api.*;
import org.junit.jupiter.api.function.Executable;
import org.junit.jupiter.api.io.TempDir;

/** PT-AUT-INBOX-001..006: real PBKDF2, PostgreSQL and independent wire/LP-HMAC/SQL oracles. */
final class LoginInboxServiceTest {
  @TempDir static Path root;
  private static ApiLogDatabaseFixture database;
  private static AuthContextCodec contexts;
  private static ResponseSnapshotCodec snapshots;
  private static FingerprintKeyRing keys;
  private static ContextHash hashes;
  private static AuthSessionService sessions;
  private static String fixtureHash;
  private static final Instant NOW = Instant.parse("2026-09-08T01:02:03.456789Z");
  private static final UUID REQUEST = new UUID(0, 101), SESSION = new UUID(0, 104);
  private static final String PASSWORD = "synthetic-password";
  private static final String FIRST_STAMP = "20260908100203456", LATER_STAMP = "20260908100303456";
  private final AtomicInteger passwordChecks = new AtomicInteger();
  private final AtomicReference<char[]> observedPassword = new AtomicReference<>();
  private final AtomicLong ids = new AtomicLong(1000);

  @BeforeAll
  static void start() throws Exception {
    database = new ApiLogDatabaseFixture(root);
    contexts = new AuthContextCodec("a1", new byte[32], null, null);
    snapshots = new ResponseSnapshotCodec("s1", key(3), null, null);
    keys = new FingerprintKeyRing("f1", key(7), null, null);
    hashes = new ContextHash();
    var deterministic =
        new SecureRandom() {
          private static final long serialVersionUID = 1L;

          @Override
          public void nextBytes(byte[] bytes) {
            Arrays.fill(bytes, (byte) 0x55);
          }
        };
    sessions = new AuthSessionService(hashes, contexts, deterministic, () -> SESSION);
    byte[] salt = new byte[16];
    Arrays.fill(salt, (byte) 17);
    var specification = new PBEKeySpec(PASSWORD.toCharArray(), salt, 310000, 256);
    try {
      fixtureHash =
          "{pbkdf2-v1}"
              + HexFormat.of().formatHex(salt)
              + HexFormat.of()
                  .formatHex(
                      SecretKeyFactory.getInstance("PBKDF2WithHmacSHA256")
                          .generateSecret(specification)
                          .getEncoded());
    } finally {
      specification.clearPassword();
    }
  }

  @AfterAll
  static void stop() throws Exception {
    contexts.close();
    snapshots.close();
    keys.close();
    database.stop();
  }

  @BeforeEach
  void seed() throws Exception {
    sql("delete from schubert.request_inbox");
    sql("delete from schubert.app_logs");
    sql("delete from schubert.auth_sessions");
    sql("delete from schubert.login_ip_attempts");
    sql("delete from schubert.app_users");
    try (Connection c = database.api();
        var s =
            c.prepareStatement(
                "insert into schubert.app_users(id,username,username_key,password_hash,role,status,password_changed_at,created_at,updated_at)"
                    + " values(7,'利用者','利用者',?,'USER','ACTIVE','2026-09-08','2026-09-08','2026-09-08')")) {
      s.setString(1, fixtureHash);
      s.executeUpdate();
    }
    passwordChecks.set(0);
    observedPassword.set(null);
    ids.set(1000);
  }

  @Test
  void successfulLoginAndReplayShareOneAtomicInboxTransaction() throws Exception {
    var service = service(NOW);
    try (Connection c = database.transaction()) {
      byte[] result =
          service.execute(c, request("利用者", PASSWORD, "127.0.0.1", REQUEST), NOW.minusSeconds(1));
      assertArrayEquals(expected("0000", new UUID(0, 1000), FIRST_STAMP, 0), result);
      assertEffects(0, 0, 0); // Separate connection cannot see uncommitted effects.
      assertInbox(c, "COMPLETED", "AUTH_SESSION", "利用者", PASSWORD, "127.0.0.1");
      c.rollback();
    }
    assertEffects(0, 0, 0);
    byte[] first =
        call(service, request("利用者", PASSWORD, "127.0.0.1", REQUEST), NOW.minusSeconds(1));
    assertArrayEquals(expected("0000", new UUID(0, 1001), FIRST_STAMP, 0), first);
    byte[] replay =
        call(
            service(NOW.plusSeconds(60)),
            request("利用者", PASSWORD, "127.0.0.1", REQUEST),
            NOW.plusSeconds(60));
    assertArrayEquals(expected("0200", new UUID(0, 1002), LATER_STAMP, 0), replay);
    assertEquals(2, passwordChecks.get()); // Rolled-back attempt plus exactly one committed Login.
    assertArrayEquals(new char[PASSWORD.length()], observedPassword.get());
    assertEffects(1, 1, 1);
    try (Connection c = database.transaction()) {
      assertInbox(c, "COMPLETED", "AUTH_SESSION", "利用者", PASSWORD, "127.0.0.1");
      c.rollback();
    }
    assertEquals(0, scalar("select failed_count from schubert.app_users"));
  }

  @Test
  void failuresAndLocksReplayWithoutRehashingOrIncrementingCounters() throws Exception {
    for (int retry : new int[] {0, 1, 900}) {
      seed();
      if (retry != 0)
        sql(
            "update schubert.app_users set failed_count=5,failure_window_started_at='2026-09-08T01:02:03Z',"
                + "locked_until='2026-09-08T01:02:03.456789Z'::timestamptz+interval '"
                + retry
                + " seconds'");
      String code = retry == 0 ? "0101" : "0106";
      var request = request("利用者", "synthetic-wrong", "127.0.0.1", REQUEST);
      assertArrayEquals(
          expected(code, new UUID(0, 1000), FIRST_STAMP, retry),
          call(service(NOW), request, NOW.minusSeconds(1)));
      assertArrayEquals(
          expected(code, new UUID(0, 1001), LATER_STAMP, retry),
          call(service(NOW.plusSeconds(60)), request, NOW.plusSeconds(60)));
      assertEquals(retry == 0 ? 1 : 0, passwordChecks.get());
      assertEquals(retry == 0 ? 1 : 5, scalar("select failed_count from schubert.app_users"));
      assertEffects(1, 0, 1);
      try (Connection c = database.transaction()) {
        assertInbox(c, "ERROR", "NONE", "利用者", "synthetic-wrong", "127.0.0.1");
        c.rollback();
      }
    }
    seed();
    call(service(NOW), request("利用者", "cafe\u0301", "2001:db8::1", REQUEST), NOW.minusSeconds(1));
    byte[] same = call(service(NOW), request("利用者", "café", "2001:0db8:0:0:0:0:0:1", REQUEST), NOW);
    assertEquals("0101", text(same, 208, 4));
    assertEquals(1, passwordChecks.get());
    try (Connection c = database.transaction()) {
      assertInbox(c, "ERROR", "NONE", "利用者", "café", "2001:db8:0:0:0:0:0:1");
      c.rollback();
    }
    for (var altered :
        List.of(
            request("別名", "café", "2001:db8::1", REQUEST),
            request("利用者", "different", "2001:db8::1", REQUEST),
            request("利用者", "café", "2001:db8::2", REQUEST))) {
      assertPermanent(() -> call(service(NOW), altered, NOW));
    }
    seed();
    call(service(NOW), request("UnknownA", PASSWORD, "127.0.0.1", REQUEST), NOW.minusSeconds(1));
    assertPermanent(
        () -> call(service(NOW), request("Unknowna", PASSWORD, "127.0.0.1", REQUEST), NOW));
    assertEquals(1, passwordChecks.get());
    assertEffects(1, 0, 1);
  }

  @Test
  void processingIdentityReuseAndUnavailableKeysHaveDistinctOutcomes() throws Exception {
    var input = request("利用者", "wrong", "127.0.0.1", REQUEST);
    call(service(NOW), input, NOW.minusSeconds(1));
    try (Connection c = database.transaction();
        var s = c.createStatement()) {
      s.executeUpdate(
          "update schubert.request_inbox set processing_state='PROCESSING',result_ref_type=null,result_ref_id=null,"
              + "result_ref_uuid=null,response_layout_id=null,response_version=null,response_body_encrypted=null,response_key_version=null,completed_at=null");
      byte[] response = service(NOW).execute(c, input, NOW);
      assertArrayEquals(expected("9000", new UUID(0, 1001), FIRST_STAMP, 0), response);
      c.rollback();
    }
    assertEquals(1, passwordChecks.get());
    for (String change :
        List.of(
            "fingerprint_key_version='unknown'",
            "response_key_version='unknown'",
            "response_body_encrypted=set_byte(response_body_encrypted,0,0)")) {
      try (Connection c = database.transaction();
          var s = c.createStatement()) {
        s.executeUpdate("update schubert.request_inbox set " + change);
        assertInfrastructure(() -> service(NOW).execute(c, input, NOW));
        c.rollback();
      }
    }
    assertPermanent(() -> call(service(NOW), request("利用者", "changed", "127.0.0.1", REQUEST), NOW));
    assertEffects(1, 0, 1);
    assertEquals(1, passwordChecks.get());
  }

  @Test
  void databaseAndAuditFailpointsRollbackAllEffectsAndConsumeSecrets() throws Exception {
    for (String point :
        List.of(
            "select correlation_id",
            "insert into schubert.request_inbox",
            "insert into schubert.login_ip_attempts",
            "insert into schubert.auth_sessions",
            "insert into schubert.app_logs",
            "update schubert.request_inbox",
            "select user_id,created_message_id",
            "close:select correlation_id")) {
      seed();
      try (Connection c = database.transaction()) {
        assertInfrastructure(
            () ->
                service(NOW)
                    .execute(
                        fault(c, point),
                        request("利用者", PASSWORD, "127.0.0.1", REQUEST),
                        NOW.minusSeconds(1)));
        assertFalse(c.isClosed());
        assertFalse(c.getAutoCommit());
        c.rollback();
      }
      assertEffects(0, 0, 0);
      assertEquals(0, scalar("select count(*) from schubert.login_ip_attempts"));
      if (observedPassword.get() != null)
        assertArrayEquals(new char[PASSWORD.length()], observedPassword.get());
    }
    seed();
    var closedSnapshot = new ResponseSnapshotCodec("s1", key(3), null, null);
    closedSnapshot.close();
    var unavailable =
        new LoginInboxService(
            new JdbcInboxCoordinator(keys),
            authentication(),
            new LoginReplayService(closedSnapshot, contexts, hashes),
            Clock.fixed(NOW, ZoneOffset.UTC));
    try (Connection c = database.transaction()) {
      assertInfrastructure(
          () ->
              unavailable.execute(
                  c, request("利用者", PASSWORD, "127.0.0.1", REQUEST), NOW.minusSeconds(1)));
      c.rollback();
    }
    assertEffects(0, 0, 0);
    assertArrayEquals(new char[PASSWORD.length()], observedPassword.get());
    var closedKeys = new FingerprintKeyRing("f1", key(7), null, null);
    closedKeys.close();
    var noKeys =
        new LoginInboxService(
            new JdbcInboxCoordinator(closedKeys),
            authentication(),
            responses(),
            Clock.fixed(NOW, ZoneOffset.UTC));
    try (Connection c = database.transaction()) {
      assertInfrastructure(
          () -> noKeys.execute(c, request("利用者", PASSWORD, "127.0.0.1", REQUEST), NOW));
      c.rollback();
    }
    assertEffects(0, 0, 0);
    char[] owned = PASSWORD.toCharArray();
    var canonical =
        LoginInboxService.canonical(
            new LoginUsername("利用者"), owned, InetAddress.ofLiteral("127.0.0.1"));
    try (canonical) {
      assertArrayEquals(
          independentFingerprint("利用者", PASSWORD, "127.0.0.1"),
          OperationFingerprint.INSTANCE.calculate(canonical, key(7)));
    }
    for (CanonicalField field : canonical.fields())
      assertArrayEquals(new byte[field.value().length], field.value());
    assertArrayEquals(PASSWORD.toCharArray(), owned);
    Arrays.fill(owned, '\0');
  }

  @Test
  void concurrentRedeliveryCreatesOneSessionAndOneAudit() throws Exception {
    var service = service(NOW);
    var input = request("利用者", PASSWORD, "127.0.0.1", REQUEST);
    List<Future<byte[]>> futures = new ArrayList<>();
    try (var executor = Executors.newFixedThreadPool(16)) {
      for (int i = 0; i < 100; i++)
        futures.add(executor.submit(() -> call(service, input, NOW.minusSeconds(1))));
      int initial = 0, replay = 0;
      Set<UUID> responseIds = new HashSet<>();
      for (var future : futures) {
        byte[] body = future.get();
        String code = text(body, 208, 4);
        if (code.equals("0000")) initial++;
        else if (code.equals("0200")) replay++;
        else fail("unexpected Login reply");
        UUID id = UUID.fromString(text(body, 24, 36));
        assertTrue(responseIds.add(id));
        assertArrayEquals(expected(code, id, FIRST_STAMP, 0), body);
      }
      assertEquals(1, initial);
      assertEquals(99, replay);
    }
    assertEquals(1, passwordChecks.get());
    assertEffects(1, 1, 1);
    try (Connection c = database.transaction()) {
      assertInbox(c, "COMPLETED", "AUTH_SESSION", "利用者", PASSWORD, "127.0.0.1");
      c.rollback();
    }
  }

  @Test
  void wireInputNullNfcIpAndClockBoundariesAreValidatedBeforeMutation() throws Exception {
    var inbox = new JdbcInboxCoordinator(keys);
    var auth = authentication();
    var response = responses();
    var clock = Clock.fixed(NOW, ZoneOffset.UTC);
    assertThrows(
        NullPointerException.class, () -> new LoginInboxService(null, auth, response, clock));
    assertThrows(
        NullPointerException.class, () -> new LoginInboxService(inbox, null, response, clock));
    assertThrows(NullPointerException.class, () -> new LoginInboxService(inbox, auth, null, clock));
    assertThrows(
        NullPointerException.class, () -> new LoginInboxService(inbox, auth, response, null));
    assertThrows(
        NullPointerException.class,
        () -> new LoginInboxService(inbox, auth, response, clock, null));
    var input = request("利用者", PASSWORD, "127.0.0.1", REQUEST);
    var service = service(NOW);
    try (Connection c = database.transaction()) {
      assertThrows(NullPointerException.class, () -> service.execute(null, input, NOW));
      assertThrows(NullPointerException.class, () -> service.execute(c, null, NOW));
      assertThrows(NullPointerException.class, () -> service.execute(c, input, null));
      var noId = new LoginInboxService(inbox, auth, response, clock, () -> null);
      assertThrows(NullPointerException.class, () -> noId.execute(c, input, NOW));
      assertThrows(NullPointerException.class, () -> response.temporaryFailure(null, REQUEST, NOW));
      assertThrows(NullPointerException.class, () -> response.temporaryFailure(REQUEST, null, NOW));
      assertThrows(
          NullPointerException.class, () -> response.temporaryFailure(REQUEST, REQUEST, null));
      for (var invalid :
          List.of(
              request("利用者", PASSWORD, "localhost", REQUEST),
              request("利用者", PASSWORD, "fe80::1%1", REQUEST),
              request(" 利用者", PASSWORD, "127.0.0.1", REQUEST),
              request("\u2003", PASSWORD, "127.0.0.1", REQUEST),
              request("利用者", "", "127.0.0.1", REQUEST))) {
        assertPermanent(() -> service.execute(c, invalid, NOW));
      }
      byte[] broken = input.payload().copyData();
      broken[365] = 'x';
      assertPermanent(
          () ->
              service.execute(
                  c,
                  new WireMessage<>(input.header(), new FixedPayload(broken, 0, List.of())),
                  NOW));
      byte[] invalidUtf8 = input.payload().copyData();
      invalidUtf8[0] = (byte) 0xff;
      assertPermanent(
          () ->
              service.execute(
                  c,
                  new WireMessage<>(input.header(), new FixedPayload(invalidUtf8, 0, List.of())),
                  NOW));
      var wrongHeader =
          new CommonHeader(
              "SCHBNK01",
              1,
              new LayoutId("GAMREQ01"),
              1,
              MessageKind.REQUEST,
              InteractionKind.SYNCHRONOUS,
              REQUEST,
              REQUEST,
              NOW.truncatedTo(ChronoUnit.MILLIS),
              Optional.of(AuthenticationContext.of("a".repeat(64))),
              256,
              0,
              0,
              0,
              256,
              Optional.empty());
      assertPermanent(
          () ->
              service.execute(
                  c,
                  new WireMessage<>(wrongHeader, new FixedPayload(new byte[0], 0, List.of())),
                  NOW));
      c.rollback();
    }
    try (Connection c = database.api()) {
      assertInfrastructure(() -> service.execute(c, input, NOW));
    }
    assertEffects(0, 0, 0);
    assertEquals(0, passwordChecks.get());
    try (Connection c = database.transaction()) {
      assertInfrastructure(() -> service.execute(c, input, NOW.plusSeconds(1)));
      c.rollback();
    }
    assertEffects(0, 0, 0);
    assertArrayEquals(new char[PASSWORD.length()], observedPassword.get());
  }

  private AuthenticationService authentication() {
    var hasher = new PasswordHasher();
    return new AuthenticationService(
        new LoginAttemptRepository(),
        (raw, stored) -> {
          passwordChecks.incrementAndGet();
          observedPassword.set(raw);
          return hasher.matches(raw, stored);
        },
        sessions,
        new LoginAuditWriter());
  }

  private static LoginReplayService responses() {
    return new LoginReplayService(snapshots, contexts, hashes);
  }

  private LoginInboxService service(Instant now) {
    return new LoginInboxService(
        new JdbcInboxCoordinator(keys),
        authentication(),
        responses(),
        Clock.fixed(now, ZoneOffset.UTC),
        () -> new UUID(0, ids.getAndIncrement()));
  }

  private static byte[] call(
      LoginInboxService service, WireMessage<FixedPayload> request, Instant received)
      throws Exception {
    try (Connection c = database.transaction()) {
      try {
        byte[] body = service.execute(c, request, received);
        c.commit();
        return body;
      } catch (RuntimeException failure) {
        c.rollback();
        throw failure;
      }
    }
  }

  private static WireMessage<FixedPayload> request(
      String name, String password, String ip, UUID id) {
    byte[] data = new byte[384];
    Arrays.fill(data, (byte) ' ');
    put(data, 0, name);
    put(data, 64, password);
    put(data, 320, ip);
    var header =
        new CommonHeader(
            "SCHBNK01",
            1,
            new LayoutId("LGNREQ01"),
            1,
            MessageKind.REQUEST,
            InteractionKind.SYNCHRONOUS,
            id,
            id,
            NOW.truncatedTo(ChronoUnit.MILLIS),
            Optional.empty(),
            256,
            384,
            0,
            0,
            640,
            Optional.empty());
    return new WireMessage<>(header, new FixedPayload(data, 0, List.of()));
  }

  private static byte[] expected(String code, UUID id, String timestamp, int retry) {
    if (!code.equals("9000"))
      return LoginReplayServiceTest.golden(Role.USER, code, id, timestamp, retry);
    byte[] body = LoginReplayServiceTest.golden(Role.USER, "0101", id, timestamp, 0);
    put(body, 208, "9000");
    Arrays.fill(body, 432, 688, (byte) ' ');
    put(body, 432, "現在処理できません。しばらくしてから再操作してください。");
    return body;
  }

  private static void assertInbox(
      Connection c, String state, String type, String name, String password, String ip)
      throws Exception {
    try (var s = c.createStatement();
        var row =
            s.executeQuery(
                "select message_id,correlation_id,owner_user_id,operation_token,request_fingerprint_hmac,"
                    + "processing_state,result_ref_type,result_ref_uuid,response_body_encrypted,response_key_version,completed_at,expires_at,request_layout_id,request_version"
                    + " from schubert.request_inbox")) {
      assertTrue(row.next());
      assertEquals(REQUEST, row.getObject(1, UUID.class));
      assertEquals(REQUEST, row.getObject(2, UUID.class));
      assertNull(row.getObject(3));
      assertNull(row.getObject(4));
      assertEquals(
          HexFormat.of().formatHex(independentFingerprint(name, password, ip)), row.getString(5));
      assertEquals(state, row.getString(6));
      assertEquals(type, row.getString(7));
      if (type.equals("AUTH_SESSION")) assertEquals(SESSION, row.getObject(8, UUID.class));
      else assertNull(row.getObject(8));
      assertTrue(row.getBytes(9).length >= 29);
      assertEquals("s1", row.getString(10));
      assertEquals(NOW, row.getTimestamp(11).toInstant());
      assertEquals(Instant.parse("2026-09-15T01:02:03.456789Z"), row.getTimestamp(12).toInstant());
      assertEquals("LGNREQ01", row.getString(13));
      assertEquals("001", row.getString(14));
      assertFalse(row.next());
    }
  }

  private static byte[] independentFingerprint(String name, String password, String ip)
      throws Exception {
    var bytes = new ByteArrayOutputStream();
    var out = new DataOutputStream(bytes);
    out.write("SCHUBERT-NK-OP1".getBytes(StandardCharsets.US_ASCII));
    for (String text :
        new String[] {
          "ANONYMOUS", "LGNREQ01", "001", "LOGIN:" + name.toLowerCase(Locale.ROOT) + ":" + ip
        }) lp(out, text);
    out.writeInt(3);
    lp(out, "username");
    lp(out, "X1");
    lp(out, name);
    lp(out, "password");
    lp(out, "X1");
    lp(out, password);
    lp(out, "clientAddress");
    lp(out, "X1");
    lp(out, ip);
    var mac = Mac.getInstance("HmacSHA256");
    mac.init(new SecretKeySpec(key(7), "HmacSHA256"));
    return mac.doFinal(bytes.toByteArray());
  }

  private static void lp(DataOutputStream out, String text) throws Exception {
    byte[] bytes = text.getBytes(StandardCharsets.UTF_8);
    out.writeInt(bytes.length);
    out.write(bytes);
  }

  private static void put(byte[] bytes, int offset, String value) {
    byte[] raw = value.getBytes(StandardCharsets.UTF_8);
    System.arraycopy(raw, 0, bytes, offset, raw.length);
  }

  private static String text(byte[] bytes, int offset, int length) {
    return new String(bytes, offset, length, StandardCharsets.UTF_8);
  }

  private static byte[] key(int value) {
    byte[] bytes = new byte[32];
    Arrays.fill(bytes, (byte) value);
    return bytes;
  }

  private static void assertEffects(int inbox, int session, int audit) throws SQLException {
    assertEquals(inbox, scalar("select count(*) from schubert.request_inbox"));
    assertEquals(session, scalar("select count(*) from schubert.auth_sessions"));
    assertEquals(audit, scalar("select count(*) from schubert.app_logs"));
  }

  private static void sql(String sql) throws SQLException {
    try (Connection c = database.api();
        var s = c.createStatement()) {
      s.executeUpdate(sql);
    }
  }

  private static int scalar(String sql) throws SQLException {
    try (Connection c = database.api();
        var s = c.createStatement();
        var row = s.executeQuery(sql)) {
      assertTrue(row.next());
      return row.getInt(1);
    }
  }

  private static void assertInfrastructure(Executable action) {
    var error = assertThrows(AuthenticationInfrastructureException.class, action);
    assertEquals("authentication storage is unavailable", error.getMessage());
    assertNull(error.getCause());
    assertEquals(0, error.getSuppressed().length);
  }

  private static void assertPermanent(Executable action) {
    var error = assertThrows(PermanentProtocolException.class, action);
    assertTrue(
        Set.of(
                "login request fields are invalid",
                "login request payload is invalid",
                "login request identity differs from its saved request")
            .contains(error.getMessage()));
    assertNull(error.getCause());
    assertEquals(0, error.getSuppressed().length);
  }

  private static Connection fault(Connection connection, String point) {
    boolean close = point.startsWith("close:");
    String match = close ? point.substring(6) : point;
    return (Connection)
        Proxy.newProxyInstance(
            Connection.class.getClassLoader(),
            new Class<?>[] {Connection.class},
            (p, m, a) -> {
              if (m.getName().equals("prepareStatement") && ((String) a[0]).contains(match)) {
                if (!close) throw new SQLException("synthetic-sensitive-provider");
                Object statement = invoke(connection, m, a);
                return Proxy.newProxyInstance(
                    PreparedStatement.class.getClassLoader(),
                    new Class<?>[] {PreparedStatement.class},
                    (sp, sm, sa) -> {
                      Object result = invoke(statement, sm, sa);
                      if (sm.getName().equals("close"))
                        throw new SQLException("synthetic-sensitive-close");
                      return result;
                    });
              }
              return invoke(connection, m, a);
            });
  }

  private static Object invoke(Object object, Method method, Object[] args) throws Throwable {
    try {
      return method.invoke(object, args);
    } catch (InvocationTargetException failure) {
      throw failure.getCause();
    }
  }
}
