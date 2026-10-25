package dev.codex.schubert.nk.api.security;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.api.logging.ApiLogDatabaseFixture;
import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import java.io.ByteArrayOutputStream;
import java.io.DataOutputStream;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.lang.reflect.Proxy;
import java.net.InetAddress;
import java.nio.charset.StandardCharsets;
import java.nio.file.Path;
import java.security.MessageDigest;
import java.security.SecureRandom;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HexFormat;
import java.util.List;
import java.util.UUID;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.atomic.AtomicLong;
import javax.crypto.Cipher;
import javax.crypto.spec.GCMParameterSpec;
import javax.crypto.spec.SecretKeySpec;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/**
 * PT-AUT-005-I/006: real DB state and independent cryptography, never production-derived expected.
 */
final class AuthSessionServiceTest {
  @TempDir static Path root;
  private static ApiLogDatabaseFixture database;
  private static ContextHash hashes;
  private static AuthContextCodec codec;
  private static InetAddress client;
  private static final Instant NOW = Instant.parse("2026-09-07T01:00:00Z");
  private static final UUID MESSAGE = UUID.fromString("b1000000-0000-0000-0000-000000000001");
  private static final UUID ID = UUID.fromString("b2000000-0000-0000-0000-000000000001");

  @BeforeAll
  static void start() throws Exception {
    database = new ApiLogDatabaseFixture(root);
    hashes = new ContextHash();
    codec = new AuthContextCodec("v1", new byte[32], null, null);
    client = InetAddress.getByAddress(new byte[] {127, 0, 0, 1});
  }

  @AfterAll
  static void stop() throws Exception {
    if (codec != null) codec.close();
    if (database != null) database.stop();
  }

  @BeforeEach
  void seed() throws SQLException {
    execute("delete from schubert.app_logs");
    execute("delete from schubert.auth_sessions");
    execute("delete from schubert.app_users");
    execute(
        "insert into"
            + " schubert.app_users(id,username,username_key,password_hash,role,status,password_changed_at,created_at,updated_at)"
            + " values(7,'session-user','session-user','unusable-fixture-hash','USER','ACTIVE','2026-09-07','2026-09-07','2026-09-07'),"
            + "(8,'other-user','other-user','unusable-fixture-hash','USER','ACTIVE','2026-09-07','2026-09-07','2026-09-07')");
  }

  @Test
  void issuancePersistsOnlyHashAndBoundCipherInCallerTransaction() throws Exception {
    var random = new FixedRandom();
    var service = new AuthSessionService(hashes, codec, random, () -> ID);
    try (Connection connection = database.transaction()) {
      var issued = service.issue(connection, 7, client, MESSAGE, MESSAGE, NOW.plusNanos(123456789));
      assertEquals(new AuthContextIdentity(ID, 7), issued.identity());
      assertEquals("IssuedContext[REDACTED]", issued.toString());
      assertEquals(NOW.plusNanos(123456000), issued.issuedAt());
      assertEquals(Instant.parse("2026-09-07T09:00:00.123456Z"), issued.expiresAt());
      byte[] raw = new byte[32];
      for (int i = 0; i < raw.length; i++) raw[i] = (byte) i;
      String expected = HexFormat.of().formatHex(raw);
      assertEquals(expected, issued.context().wireValue());
      assertArrayEquals(new byte[32], random.last);
      assertEquals(0, count("true"));
      try (var statement = connection.createStatement();
          var row = statement.executeQuery("select * from schubert.auth_sessions")) {
        assertTrue(row.next());
        assertEquals(
            HexFormat.of()
                .formatHex(
                    MessageDigest.getInstance("SHA-256")
                        .digest(expected.getBytes(StandardCharsets.US_ASCII))),
            row.getString("context_hash"));
        assertArrayEquals(
            expected.getBytes(StandardCharsets.US_ASCII),
            independentlyDecrypt(row.getBytes("context_ciphertext"), ID, 7));
        assertEquals("v1", row.getString("key_version"));
        assertEquals("127.0.0.1", row.getString("client_address"));
        assertEquals(MESSAGE, row.getObject("created_message_id", UUID.class));
        assertEquals(
            NOW.plusNanos(123456000),
            row.getObject("issued_at", java.time.OffsetDateTime.class).toInstant());
        assertEquals(
            NOW.plusNanos(123456000),
            row.getObject("last_accessed_at", java.time.OffsetDateTime.class).toInstant());
        assertEquals(
            Instant.parse("2026-09-07T09:00:00.123456Z"),
            row.getObject("expires_at", java.time.OffsetDateTime.class).toInstant());
        assertFalse(row.getBoolean("revoked"));
        assertNull(row.getObject("revoked_at", java.time.OffsetDateTime.class));
        assertNull(row.getString("revoke_reason"));
        assertFalse(row.next());
      }
      connection.rollback();
      assertEquals(0, count("true"));
      byte[] ipv6 = new byte[16];
      ipv6[15] = 1;
      service.issue(connection, 7, InetAddress.getByAddress(ipv6), MESSAGE, MESSAGE, NOW);
      connection.commit();
      assertFalse(connection.isClosed());
      assertFalse(connection.getAutoCommit());
    }
    assertEquals(1, count("client_address='::1'::inet"));
  }

  @Test
  void thirdSessionRevokesOldestAccessAndUuidTieOnly() throws Exception {
    var sequence = new AtomicLong(10);
    var service =
        new AuthSessionService(
            hashes, codec, new SecureRandom(), () -> new UUID(0, sequence.getAndIncrement()));
    issue(service, 7, NOW.minusSeconds(120));
    issue(service, 7, NOW.minusSeconds(60));
    execute(
        "update schubert.auth_sessions set last_accessed_at='2026-09-07T00:59:30Z' where"
            + " id='00000000-0000-0000-0000-00000000000a'");
    issue(service, 7, NOW);
    assertEquals(
        1,
        count(
            "id='00000000-0000-0000-0000-00000000000b' and revoked and revoke_reason='REPLACED' and"
                + " revoked_at='2026-09-07T01:00:00Z'"));
    assertEquals(2, count("not revoked"));
    seed();
    for (UUID id :
        List.of(
            UUID.fromString("80000000-0000-0000-0000-000000000000"),
            UUID.fromString("00000000-0000-0000-0000-000000000001"),
            UUID.fromString("ffffffff-ffff-ffff-ffff-ffffffffffff"))) {
      issue(new AuthSessionService(hashes, codec, new SecureRandom(), () -> id), 7, NOW);
    }
    assertEquals(1, count("id='00000000-0000-0000-0000-000000000001' and revoked"));
    assertEquals(2, count("not revoked"));
    seed();
    var equalExpiry = issue(service, 7, NOW.minusSeconds(30000));
    var pastExpiry = issue(service, 7, NOW.minusSeconds(29900));
    issue(service, 7, NOW.minusSeconds(100));
    execute(
        "update schubert.auth_sessions set"
            + " revoked=true,revoked_at='2026-09-07T00:59:00Z',revoke_reason='LOGOUT' where"
            + " expires_at>'2026-09-07T01:00:00Z'");
    execute(
        "update schubert.auth_sessions set expires_at='2026-09-07T01:00:00Z' where id='"
            + equalExpiry.identity().sessionId()
            + "'");
    execute(
        "update schubert.auth_sessions set expires_at='2026-09-07T00:59:59Z' where id='"
            + pastExpiry.identity().sessionId()
            + "'");
    issue(service, 8, NOW);
    issue(service, 7, NOW);
    issue(service, 7, NOW);
    assertEquals(5, count("user_id=7"));
    assertEquals(2, count("user_id=7 and not revoked and expires_at>'2026-09-07T01:00:00Z'"));
    assertEquals(0, count("revoke_reason='REPLACED'"));
    assertEquals(1, count("user_id=8 and not revoked"));
    assertEquals(1, count("revoke_reason='LOGOUT'"));
  }

  @Test
  void oneHundredConcurrentIssuesKeepOnlyTwoActive() throws Exception {
    var service = new AuthSessionService(hashes, codec);
    try (var executor = Executors.newFixedThreadPool(16)) {
      var results = new ArrayList<Future<IssuedContext>>();
      for (int i = 0; i < 100; i++) results.add(executor.submit(() -> issue(service, 7, NOW)));
      var ids = new java.util.HashSet<UUID>();
      var contexts = new java.util.HashSet<AuthenticationContext>();
      for (var result : results) {
        var issued = result.get();
        assertEquals(7, issued.identity().userId());
        ids.add(issued.identity().sessionId());
        contexts.add(issued.context());
      }
      assertEquals(100, ids.size());
      assertEquals(100, contexts.size());
    }
    assertEquals(100, count("true"));
    assertEquals(2, count("not revoked"));
    assertEquals(98, count("revoked and revoke_reason='REPLACED'"));
    try (Connection connection = database.api();
        var statement = connection.createStatement();
        var row =
            statement.executeQuery(
                "select bool_and(not revoked) from (select revoked from schubert.auth_sessions"
                    + " order by last_accessed_at desc,id desc limit 2) x")) {
      assertTrue(row.next());
      assertTrue(row.getBoolean(1));
    }
    var sql = new ArrayList<String>();
    try (Connection connection = database.transaction()) {
      service.issue(intercept(connection, "observe", sql), 7, client, MESSAGE, MESSAGE, NOW);
      connection.rollback();
    }
    assertEquals(5, sql.size());
    assertTrue(sql.get(0).startsWith("select status from schubert.app_users"));
    assertTrue(sql.get(1).startsWith("insert into schubert.auth_sessions"));
    assertTrue(sql.get(2).endsWith("order by last_accessed_at,id for update"));
    assertTrue(sql.get(3).contains("revoke_reason='REPLACED'"));
    assertEquals(100, count("true"));
  }

  @Test
  void missingDisabledDuplicateAndDatabaseFaultsRollbackWithoutLeaks() throws Exception {
    var service = new AuthSessionService(hashes, codec);
    try (Connection connection = database.transaction()) {
      assertThrows(
          AuthenticationContextException.class,
          () -> service.issue(connection, 99, client, MESSAGE, MESSAGE, NOW));
      connection.rollback();
      execute("update schubert.app_users set status='DISABLED' where id=7");
      var failure =
          assertThrows(
              AuthenticationContextException.class,
              () -> service.issue(connection, 7, client, MESSAGE, MESSAGE, NOW));
      assertNull(failure.getCause());
      assertEquals(0, failure.getSuppressed().length);
      connection.rollback();
    }
    seed();
    try (Connection connection = database.transaction()) {
      service.issue(connection, 7, client, MESSAGE, MESSAGE, NOW);
      connection.commit();
      assertInfrastructure(() -> service.issue(connection, 7, client, MESSAGE, MESSAGE, NOW));
      connection.rollback();
    }
    assertEquals(1, count("true"));
    for (String fault :
        List.of(
            "getAutoCommit",
            "prepareStatement",
            "setLong",
            "setBytes",
            "executeQuery",
            "nullStatus",
            "nullId",
            "zeroInsert",
            "zeroReplace",
            "insertAfter",
            "replaceAfter",
            "rowClose",
            "statementClose")) {
      seed();
      issue(service, 7, NOW.minusSeconds(2));
      issue(service, 7, NOW.minusSeconds(1));
      try (Connection connection = database.transaction()) {
        assertInfrastructure(
            () ->
                service.issue(
                    intercept(connection, fault, new ArrayList<>()),
                    7,
                    client,
                    MESSAGE,
                    MESSAGE,
                    NOW));
        assertFalse(connection.isClosed());
        connection.rollback();
      }
      assertEquals(2, count("true"));
      assertEquals(2, count("not revoked"));
    }
    try (Connection connection = database.transaction()) {
      assertInfrastructure(
          () ->
              service.issue(
                  intercept(connection, "rowClose", new ArrayList<>()),
                  99,
                  client,
                  MESSAGE,
                  MESSAGE,
                  NOW));
      connection.rollback();
    }
  }

  @Test
  void replacementAuditIsAtomicBoundedAndCarriesRequestIdentity() throws Exception {
    var service = new AuthSessionService(hashes, codec);
    UUID correlation = UUID.fromString("c1000000-0000-0000-0000-000000000001");
    issue(service, 7, NOW.minusSeconds(2));
    issue(service, 7, NOW.minusSeconds(1));
    try (Connection connection = database.transaction()) {
      service.issue(connection, 7, client, MESSAGE, correlation, NOW);
      try (var statement = connection.createStatement();
          var row = statement.executeQuery("select * from schubert.app_logs")) {
        assertTrue(row.next());
        assertEquals("API", row.getString("service"));
        assertEquals("SECURITY", row.getString("category"));
        assertEquals("INFO", row.getString("level"));
        assertEquals("SESSION_REVOKED", row.getString("action"));
        assertEquals("SESSION_REVOKED", row.getString("message"));
        assertEquals(7, row.getLong("actor_user_id"));
        assertEquals("127.0.0.1", row.getString("remote_address"));
        assertEquals(MESSAGE, row.getObject("message_id", UUID.class));
        assertEquals(correlation, row.getObject("correlation_id", UUID.class));
        assertEquals(NOW, row.getObject("logged_at", java.time.OffsetDateTime.class).toInstant());
        assertNull(row.getObject("request_id"));
        assertNull(row.getObject("source_message_id"));
        assertEquals(
            com.google.gson.JsonParser.parseString(
                "{\"targetUserId\":7,\"reason\":\"REPLACED\",\"resultCode\":\"0000\"}"),
            com.google.gson.JsonParser.parseString(row.getString("details")));
        assertFalse(row.next());
      }
      connection.rollback();
    }
    assertEquals(2, count("not revoked"));
    for (String fault : List.of("auditPrepare", "zeroAudit", "auditAfter", "auditClose")) {
      try (Connection connection = database.transaction()) {
        assertInfrastructure(
            () ->
                service.issue(
                    intercept(connection, fault, new ArrayList<>()),
                    7,
                    client,
                    MESSAGE,
                    correlation,
                    NOW));
        connection.rollback();
      }
      assertEquals(2, count("true"));
      assertEquals(2, count("not revoked"));
      try (Connection connection = database.api();
          var statement = connection.createStatement();
          var row = statement.executeQuery("select count(*) from schubert.app_logs")) {
        assertTrue(row.next());
        assertEquals(0, row.getInt(1));
      }
    }
    try (Connection connection = database.transaction()) {
      assertThrows(
          NullPointerException.class,
          () -> service.issue(connection, 7, client, MESSAGE, null, NOW));
    }
  }

  @Test
  void constructorsNullBoundsAndUnavailableCryptoFailBeforeCommit() throws Exception {
    assertThrows(NullPointerException.class, () -> new AuthSessionService(null, codec));
    assertThrows(NullPointerException.class, () -> new AuthSessionService(hashes, null));
    assertThrows(
        NullPointerException.class, () -> new AuthSessionService(hashes, codec, null, () -> ID));
    assertThrows(
        NullPointerException.class,
        () -> new AuthSessionService(hashes, codec, new SecureRandom(), null));
    var service = new AuthSessionService(hashes, codec);
    try (Connection connection = database.api()) {
      assertInfrastructure(() -> service.issue(connection, 7, client, MESSAGE, MESSAGE, NOW));
    }
    var random = new FixedRandom();
    var closed = new AuthContextCodec("v1", new byte[32], null, null);
    closed.close();
    try (Connection connection = database.transaction()) {
      assertThrows(
          NullPointerException.class, () -> service.issue(null, 7, client, MESSAGE, MESSAGE, NOW));
      assertThrows(
          NullPointerException.class,
          () -> service.issue(connection, 7, null, MESSAGE, MESSAGE, NOW));
      assertThrows(
          NullPointerException.class,
          () -> service.issue(connection, 7, client, null, MESSAGE, NOW));
      assertThrows(
          NullPointerException.class,
          () -> service.issue(connection, 7, client, MESSAGE, MESSAGE, null));
      for (long id : new long[] {0, -1, 1_000_000_000_000L})
        assertThrows(
            IllegalArgumentException.class,
            () -> service.issue(connection, id, client, MESSAGE, MESSAGE, NOW));
      for (long id : new long[] {1, 999_999_999_999L})
        assertThrows(
            AuthenticationContextException.class,
            () -> service.issue(connection, id, client, MESSAGE, MESSAGE, NOW));
      assertThrows(
          NullPointerException.class,
          () ->
              new AuthSessionService(hashes, codec, random, () -> null)
                  .issue(connection, 7, client, MESSAGE, MESSAGE, NOW));
      assertThrows(
          IllegalStateException.class,
          () ->
              new AuthSessionService(hashes, closed, random, () -> ID)
                  .issue(connection, 7, client, MESSAGE, MESSAGE, NOW));
      assertArrayEquals(new byte[32], random.last);
      connection.rollback();
    }
    var identity = new AuthContextIdentity(ID, 7);
    var raw = AuthenticationContext.of("a".repeat(64));
    assertThrows(
        NullPointerException.class, () -> new IssuedContext(null, raw, NOW, NOW.plusSeconds(1)));
    assertThrows(
        NullPointerException.class,
        () -> new IssuedContext(identity, null, NOW, NOW.plusSeconds(1)));
    assertThrows(NullPointerException.class, () -> new IssuedContext(identity, raw, null, NOW));
    assertThrows(NullPointerException.class, () -> new IssuedContext(identity, raw, NOW, null));
    assertThrows(IllegalArgumentException.class, () -> new IssuedContext(identity, raw, NOW, NOW));
    assertThrows(
        IllegalArgumentException.class,
        () -> new IssuedContext(identity, raw, NOW, NOW.minusSeconds(1)));
    assertEquals(0, count("true"));
  }

  private static IssuedContext issue(AuthSessionService service, long user, Instant now)
      throws Exception {
    try (Connection connection = database.transaction()) {
      var issued =
          service.issue(connection, user, client, UUID.randomUUID(), UUID.randomUUID(), now);
      connection.commit();
      return issued;
    }
  }

  private static byte[] independentlyDecrypt(byte[] stored, UUID id, long user) throws Exception {
    assertArrayEquals("NKENC1".getBytes(StandardCharsets.US_ASCII), Arrays.copyOf(stored, 6));
    assertEquals(1, stored[6]);
    assertEquals(2, stored[7]);
    assertEquals(102, stored.length);
    var aad = new ByteArrayOutputStream();
    try (var data = new DataOutputStream(aad)) {
      for (String field :
          List.of(
              "SCHUBERT-NK-AUTHCTX-v1",
              "schubert.auth_sessions",
              id.toString(),
              Long.toString(user),
              "1",
              "v1")) {
        byte[] value = field.getBytes(StandardCharsets.US_ASCII);
        data.writeInt(value.length);
        data.write(value);
      }
    }
    Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding");
    cipher.init(
        Cipher.DECRYPT_MODE,
        new SecretKeySpec(new byte[32], "AES"),
        new GCMParameterSpec(128, Arrays.copyOfRange(stored, 10, 22)));
    cipher.updateAAD(aad.toByteArray());
    return cipher.doFinal(Arrays.copyOfRange(stored, 22, stored.length));
  }

  private static void execute(String sql) throws SQLException {
    try (Connection connection = database.api();
        var statement = connection.createStatement()) {
      statement.executeUpdate(sql);
    }
  }

  private static int count(String predicate) throws SQLException {
    try (Connection connection = database.api();
        var statement = connection.createStatement();
        var row =
            statement.executeQuery(
                "select count(*) from schubert.auth_sessions where " + predicate)) {
      assertTrue(row.next());
      return row.getInt(1);
    }
  }

  private static void assertInfrastructure(org.junit.jupiter.api.function.Executable action) {
    var failure = assertThrows(AuthenticationInfrastructureException.class, action);
    assertEquals("authentication storage is unavailable", failure.getMessage());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
  }

  private static Connection intercept(Connection real, String fault, List<String> sql) {
    return (Connection)
        Proxy.newProxyInstance(
            Connection.class.getClassLoader(),
            new Class<?>[] {Connection.class},
            (proxy, method, args) -> {
              if (method.getName().equals(fault))
                throw new SQLException("synthetic-sensitive-provider-text");
              if (method.getName().equals("prepareStatement")
                  && fault.equals("auditPrepare")
                  && ((String) args[0]).startsWith("insert into schubert.app_logs"))
                throw new SQLException("synthetic-sensitive-audit");
              Object result = invoke(real, method, args);
              if (!method.getName().equals("prepareStatement")) return result;
              sql.add((String) args[0]);
              int stage = sql.size();
              return Proxy.newProxyInstance(
                  PreparedStatement.class.getClassLoader(),
                  new Class<?>[] {PreparedStatement.class},
                  (sp, sm, sa) -> {
                    if (sm.getName().equals(fault))
                      throw new SQLException("synthetic-sensitive-provider-text");
                    if (sm.getName().equals("executeUpdate")
                        && ((stage == 2 && fault.equals("zeroInsert"))
                            || (stage == 4 && fault.equals("zeroReplace"))
                            || (stage == 5 && fault.equals("zeroAudit")))) return 0;
                    Object sr = invoke(result, sm, sa);
                    if (sm.getName().equals("executeUpdate")
                        && ((stage == 2 && fault.equals("insertAfter"))
                            || (stage == 4 && fault.equals("replaceAfter"))
                            || (stage == 5 && fault.equals("auditAfter"))))
                      throw new SQLException("synthetic-sensitive-after-write");
                    if (sm.getName().equals("close")
                        && (fault.equals("statementClose")
                            || (stage == 5 && fault.equals("auditClose"))))
                      throw new SQLException("synthetic-sensitive-close");
                    if (!sm.getName().equals("executeQuery")) return sr;
                    return Proxy.newProxyInstance(
                        ResultSet.class.getClassLoader(),
                        new Class<?>[] {ResultSet.class},
                        (rp, rm, ra) -> {
                          if (stage == 1
                              && fault.equals("nullStatus")
                              && rm.getName().equals("getString")) return null;
                          if (stage == 3
                              && fault.equals("nullId")
                              && rm.getName().equals("getObject")) return null;
                          Object rr = invoke(sr, rm, ra);
                          if (rm.getName().equals("close") && fault.equals("rowClose"))
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

  private static final class FixedRandom extends SecureRandom {
    private static final long serialVersionUID = 1L;
    byte[] last = new byte[0];

    @Override
    public void nextBytes(byte[] bytes) {
      assertEquals(32, bytes.length);
      for (int i = 0; i < bytes.length; i++) bytes[i] = (byte) i;
      last = bytes;
    }
  }
}
