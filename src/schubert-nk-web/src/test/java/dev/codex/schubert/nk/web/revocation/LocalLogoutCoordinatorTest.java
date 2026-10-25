package dev.codex.schubert.nk.web.revocation;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.layout.semantic.UserRole;
import dev.codex.schubert.nk.web.logging.WebLogDatabaseFixture;
import dev.codex.schubert.nk.web.messaging.JmsRequestReplyClient;
import dev.codex.schubert.nk.web.messaging.LogoutWireClient;
import dev.codex.schubert.nk.web.messaging.ReplyCorrelationRegistry;
import dev.codex.schubert.nk.web.session.EncryptedWebSessionRepository;
import dev.codex.schubert.nk.web.session.SessionPayloadCodec;
import dev.codex.schubert.nk.web.session.SessionPrincipal;
import dev.codex.schubert.nk.web.session.SessionStoreException;
import dev.codex.schubert.nk.web.session.WebSessionId;
import jakarta.jms.JMSException;
import java.io.ByteArrayOutputStream;
import java.io.DataOutputStream;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.lang.reflect.Proxy;
import java.nio.charset.StandardCharsets;
import java.nio.file.Path;
import java.security.MessageDigest;
import java.sql.Connection;
import java.sql.SQLException;
import java.time.Clock;
import java.time.Duration;
import java.time.Instant;
import java.time.OffsetDateTime;
import java.time.ZoneId;
import java.time.ZoneOffset;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.HashSet;
import java.util.HexFormat;
import java.util.List;
import java.util.UUID;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicLong;
import javax.crypto.Cipher;
import javax.crypto.spec.GCMParameterSpec;
import javax.crypto.spec.SecretKeySpec;
import javax.sql.DataSource;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** RERUN006A..G: literal UI/independent JCA/SQL; borrowed local DB/key owners, not native. */
final class LocalLogoutCoordinatorTest {
  private static final Instant NOW = Instant.parse("2026-09-08T00:00:00.123456Z");
  private static final AuthenticationContext AUTH = AuthenticationContext.of("b".repeat(64));
  private static final SessionPrincipal PRINCIPAL =
      new SessionPrincipal("reader", UserRole.USER, AUTH, NOW);
  private static WebLogDatabaseFixture db;

  @BeforeAll
  static void start(@TempDir Path path) throws Exception {
    db = new WebLogDatabaseFixture(path);
  }

  @AfterAll
  static void stop() throws Exception {
    if (db != null) db.stop();
  }

  @BeforeEach
  void reset() throws Exception {
    try (var c = db.web();
        var s = c.createStatement()) {
      s.executeUpdate("delete from schubert_web_session.pending_context_revocations");
      s.executeUpdate("delete from schubert_web_session.web_http_sessions");
    }
  }

  @Test
  void rerun006aConfirmedAndIdempotentDeleteOnlyOldSessionNeverQueue() throws Exception {
    for (String code : List.of("0000", "0200")) {
      reset();
      try (var f = new Fixture()) {
        var id = f.authenticated();
        var newer = f.sessions.create().sessionId();
        f.code = code;
        assertEquals(LocalLogoutCoordinator.Outcome.CONFIRMED, f.coordinator().logout(id, AUTH));
        assertFalse(exists(id));
        assertTrue(exists(newer));
        assertEquals(0, pending());
        assertEquals(1, f.ids.size());
        f.resources();
      }
    }
  }

  @Test
  void rerun006bFailedWireAtomicRetainDestroyUnknownExpiryAndIndependentCipher() throws Exception {
    for (String mode :
        List.of("0102", "9000", "bad-context", "bad-correlation", "timeout", "lost")) {
      reset();
      try (var f = new Fixture()) {
        var id = f.authenticated();
        f.mode = mode;
        assertEquals(LocalLogoutCoordinator.Outcome.QUEUED, f.coordinator().logout(id, AUTH));
        assertFalse(exists(id));
        assertEquals(1, pending());
        assertEquals(1, f.ids.size());
        String reason =
            mode.equals("0102")
                ? "SESSION_INVALID"
                : mode.equals("9000")
                    ? "API_REJECTED"
                    : mode.startsWith("bad-") ? "INVALID_RESPONSE" : "UNAVAILABLE";
        verifyRetained(reason);
        assertTrue(f.sessions.find(id).isEmpty());
        assertEquals(0, count("select count(*) from schubert_web_session.web_http_sessions"));
        f.resources();
      }
    }
  }

  @Test
  void rerun006cAcquisitionEnqueueDeleteCommitAndCloseFailuresAttemptIndependentDestruction()
      throws Exception {
    for (String mode :
        List.of(
            "acquire",
            "null",
            "setAutoCommit",
            "setReadOnly",
            "enqueue",
            "delete",
            "commit",
            "commit-after",
            "close")) {
      reset();
      try (var f = new Fixture()) {
        var id = f.authenticated();
        f.mode = "9000";
        f.fault = mode;
        f.acquisitions.set(0);
        fixed(() -> f.coordinator().logout(id, AUTH));
        assertFalse(exists(id));
        assertEquals(1, f.ids.size());
        assertEquals(mode.equals("commit-after") || mode.equals("close") ? 1 : 0, pending());
        assertEquals(0, f.active.get());
        f.resources();
      }
    }
    reset();
    try (var f = new Fixture()) {
      var id = f.authenticated();
      f.code = "0000";
      f.fault = "delete";
      f.acquisitions.set(0);
      fixed(() -> f.coordinator().logout(id, AUTH));
      assertFalse(exists(id));
      assertEquals(0, pending());
      f.resources();
    }
  }

  @Test
  void rerun006dClosedCodecMissingClockAndDoubleFailureNeverFakeCompletion() throws Exception {
    for (boolean closedCodec : List.of(false, true)) {
      reset();
      try (var f = new Fixture()) {
        var id = f.authenticated();
        f.mode = "9000";
        if (closedCodec) f.revoke.close();
        else f.clock.at = null;
        fixed(() -> f.coordinator().logout(id, AUTH));
        assertFalse(exists(id));
        assertEquals(0, pending());
        assertEquals(0, f.active.get());
      }
    }
    reset();
    try (var f = new Fixture()) {
      var id = f.authenticated();
      f.mode = "9000";
      f.fault = "acquire";
      f.always = true;
      f.acquisitions.set(0);
      fixed(() -> f.coordinator().logout(id, AUTH));
      assertTrue(exists(id));
      assertEquals(0, pending());
      assertEquals(2, f.acquisitions.get());
      assertEquals(0, f.active.get());
      f.resources();
    }
  }

  @Test
  void rerun006eFatalWireAndFatalSuppressedDbClosePreserveIdentityAfterLocalCleanup()
      throws Exception {
    for (String mode : List.of("wire", "same-fatal", "db-close", "cleanup-close")) {
      reset();
      try (var f = new Fixture()) {
        var id = f.authenticated();
        var fatal = new AssertionError("private-fatal-marker");
        f.mode = "9000";
        f.acquisitions.set(0);
        if (mode.equals("wire")) f.wireFatal = fatal;
        else if (mode.equals("same-fatal")) {
          f.wireFatal = fatal;
          f.closeFatal = fatal;
        } else if (mode.equals("db-close")) {
          f.fault = "enqueue";
          f.closeFatal = fatal;
        } else {
          f.fault = "acquire";
          f.closeFatal = fatal;
          f.fatalIndex = 2;
        }
        assertSame(
            fatal, assertThrows(AssertionError.class, () -> f.coordinator().logout(id, AUTH)));
        assertFalse(exists(id));
        assertEquals(0, f.active.get());
        assertEquals(0, pending());
        f.resources();
      }
    }
  }

  @Test
  void rerun006hRollbackAndCyclicProviderFailuresPreserveFatalAndFixedRedaction() throws Exception {
    for (int variant = 0; variant < 5; variant++) {
      reset();
      try (var f = new Fixture()) {
        var id = f.authenticated();
        f.mode = "9000";
        f.fault = "setReadOnly";
        f.acquisitions.set(0);
        var primary = new SQLException("private-primary");
        var peer = new SQLException("private-peer");
        primary.addSuppressed(peer);
        peer.addSuppressed(primary);
        var fatal = new AssertionError("private-fatal-marker");
        f.primaryFault = primary;
        if (variant == 1) peer.initCause(fatal);
        if (variant == 2) f.rollbackFault = fatal;
        if (variant == 3) f.rollbackFault = primary;
        if (variant == 4) f.rollbackFault = new IllegalStateException("private-rollback-runtime");
        if (variant == 1 || variant == 2)
          assertSame(
              fatal, assertThrows(AssertionError.class, () -> f.coordinator().logout(id, AUTH)));
        else fixed(() -> f.coordinator().logout(id, AUTH));
        assertFalse(exists(id));
        assertEquals(0, pending());
        f.resources();
      }
    }
  }

  @Test
  void rerun006fNullContractsAndAbsentOldIdentityDoNotCreateSession() throws Exception {
    try (var f = new Fixture()) {
      var wire = f.wire();
      assertThrows(
          NullPointerException.class,
          () -> new LocalLogoutCoordinator(null, f.revoke, wire, f.clock));
      assertThrows(
          NullPointerException.class,
          () -> new LocalLogoutCoordinator(f.sessions, null, wire, f.clock));
      assertThrows(
          NullPointerException.class,
          () -> new LocalLogoutCoordinator(f.sessions, f.revoke, null, f.clock));
      assertThrows(
          NullPointerException.class,
          () -> new LocalLogoutCoordinator(f.sessions, f.revoke, wire, null));
      var id = f.authenticated();
      assertThrows(NullPointerException.class, () -> f.coordinator().logout(null, AUTH));
      assertThrows(NullPointerException.class, () -> f.coordinator().logout(id, null));
      var identity = new RevocationPayloadIdentity(UUID.randomUUID(), NOW);
      var payload = f.revoke.encrypt(identity, AUTH);
      assertThrows(
          NullPointerException.class,
          () ->
              f.sessions.invalidateAndRetain(
                  null, identity, payload, RevocationFailureCode.UNAVAILABLE));
      assertThrows(
          NullPointerException.class,
          () ->
              f.sessions.invalidateAndRetain(id, null, payload, RevocationFailureCode.UNAVAILABLE));
      assertThrows(
          NullPointerException.class,
          () ->
              f.sessions.invalidateAndRetain(
                  id, identity, null, RevocationFailureCode.UNAVAILABLE));
      assertThrows(
          NullPointerException.class,
          () -> f.sessions.invalidateAndRetain(id, identity, payload, null));
      assertTrue(exists(id));
      assertEquals(0, pending());
      assertTrue(f.ids.isEmpty());
      f.sessions.invalidate(id);
      f.mode = "0102";
      assertEquals(LocalLogoutCoordinator.Outcome.QUEUED, f.coordinator().logout(id, AUTH));
      assertFalse(exists(id));
      assertEquals(1, pending());
      verifyRetained("SESSION_INVALID");
      f.resources();
    }
  }

  @Test
  void rerun006gHundredConcurrentLocalLogoutsRetainDurablyWithoutSessionResurrection()
      throws Exception {
    try (var f = new Fixture()) {
      var ids = new ArrayList<WebSessionId>();
      for (int i = 0; i < 100; i++) ids.add(f.authenticated());
      f.mode = "9000";
      try (var pool = Executors.newFixedThreadPool(12)) {
        var futures = new ArrayList<Future<LocalLogoutCoordinator.Outcome>>();
        for (var id : ids) futures.add(pool.submit(() -> f.coordinator().logout(id, AUTH)));
        for (var result : futures)
          assertEquals(LocalLogoutCoordinator.Outcome.QUEUED, result.get(60, TimeUnit.SECONDS));
      }
      assertEquals(0, count("select count(*) from schubert_web_session.web_http_sessions"));
      assertEquals(100, pending());
      assertEquals(100, new HashSet<>(f.ids).size());
      assertEquals(
          100,
          count(
              "select count(distinct id) from schubert_web_session.pending_context_revocations where expires_at is null and attempt_count=0 and last_error_code='API_REJECTED'"));
      f.resources();
    }
  }

  private static void fixed(org.junit.jupiter.api.function.Executable action) {
    var failure = assertThrows(SessionStoreException.class, action);
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
  }

  private static boolean exists(WebSessionId id) throws Exception {
    String hash =
        HexFormat.of()
            .formatHex(
                MessageDigest.getInstance("SHA-256")
                    .digest(id.cookieValue().getBytes(StandardCharsets.US_ASCII)));
    try (var c = db.web();
        var s =
            c.prepareStatement(
                "select count(*) from schubert_web_session.web_http_sessions where session_id_hash=?")) {
      s.setString(1, hash);
      try (var r = s.executeQuery()) {
        assertTrue(r.next());
        return r.getInt(1) == 1;
      }
    }
  }

  private static int pending() throws Exception {
    return count("select count(*) from schubert_web_session.pending_context_revocations");
  }

  private static int count(String sql) throws Exception {
    try (var c = db.web();
        var s = c.createStatement();
        var r = s.executeQuery(sql)) {
      assertTrue(r.next());
      return r.getInt(1);
    }
  }

  private static void verifyRetained(String reason) throws Exception {
    try (var c = db.web();
        var s = c.createStatement();
        var r =
            s.executeQuery(
                "select id,context_ciphertext,key_version,requested_at,next_attempt_at,attempt_count,expires_at,last_error_code,lease_owner,lease_until from schubert_web_session.pending_context_revocations")) {
      assertTrue(r.next());
      UUID id = r.getObject(1, UUID.class);
      byte[] wire = r.getBytes(2);
      assertEquals("revoke", r.getString(3));
      assertEquals(NOW, r.getObject(4, OffsetDateTime.class).toInstant());
      assertEquals(NOW.plusSeconds(5), r.getObject(5, OffsetDateTime.class).toInstant());
      assertEquals(0, r.getInt(6));
      assertNull(r.getObject(7));
      assertEquals(reason, r.getString(8));
      assertNull(r.getObject(9));
      assertNull(r.getObject(10));
      assertFalse(r.next());
      assertEquals(106, wire.length);
      assertArrayEquals("NKENC1".getBytes(StandardCharsets.US_ASCII), Arrays.copyOf(wire, 6));
      assertEquals(1, wire[6]);
      assertEquals(6, wire[7]);
      assertEquals("revoke", new String(wire, 8, 6, StandardCharsets.US_ASCII));
      var bytes = new ByteArrayOutputStream();
      try (var out = new DataOutputStream(bytes)) {
        for (byte[] field :
            List.of(
                "web-revoke".getBytes(StandardCharsets.US_ASCII),
                "schubert_web_session.pending_context_revocations"
                    .getBytes(StandardCharsets.US_ASCII),
                java.nio.ByteBuffer.allocate(16)
                    .putLong(id.getMostSignificantBits())
                    .putLong(id.getLeastSignificantBits())
                    .array(),
                java.nio.ByteBuffer.allocate(12)
                    .putLong(NOW.getEpochSecond())
                    .putInt(NOW.getNano())
                    .array(),
                new byte[] {1},
                "revoke".getBytes(StandardCharsets.US_ASCII))) {
          out.writeInt(field.length);
          out.write(field);
        }
      }
      var cipher = Cipher.getInstance("AES/GCM/NoPadding");
      cipher.init(
          Cipher.DECRYPT_MODE,
          new SecretKeySpec(new byte[32], "AES"),
          new GCMParameterSpec(128, wire, 14, 12));
      cipher.updateAAD(bytes.toByteArray());
      assertArrayEquals(
          "b".repeat(64).getBytes(StandardCharsets.US_ASCII), cipher.doFinal(wire, 26, 80));
    }
  }

  private static final class MutableClock extends Clock {
    volatile Instant at = NOW;

    public ZoneId getZone() {
      return ZoneOffset.UTC;
    }

    public Clock withZone(ZoneId zone) {
      return this;
    }

    public Instant instant() {
      return at;
    }
  }

  private static final class Fixture implements AutoCloseable {
    final MutableClock clock = new MutableClock();
    final SessionPayloadCodec sessionCodec =
        new SessionPayloadCodec("session", new byte[32], null, null);
    final RevocationPayloadCodec revoke =
        new RevocationPayloadCodec("revoke", new byte[32], null, null);
    final JmsRequestReplyClient replies =
        new JmsRequestReplyClient(new ReplyCorrelationRegistry(), clock, 12);
    final AtomicInteger active = new AtomicInteger();
    final AtomicInteger acquisitions = new AtomicInteger();
    final ThreadLocal<AtomicInteger> owned = ThreadLocal.withInitial(AtomicInteger::new);
    final List<UUID> ids = Collections.synchronizedList(new ArrayList<>());
    final List<byte[]> bodies = Collections.synchronizedList(new ArrayList<>());
    final AtomicLong sequence = new AtomicLong(100);
    final EncryptedWebSessionRepository sessions =
        new EncryptedWebSessionRepository(source(), sessionCodec, clock);
    String code = "0000";
    String mode = "";
    String fault = "";
    boolean always;
    Error wireFatal;
    Error closeFatal;
    Throwable primaryFault;
    Throwable rollbackFault;
    int fatalIndex = 1;

    WebSessionId authenticated() {
      var old = sessions.create();
      return sessions.authenticate(old.sessionId(), PRINCIPAL).orElseThrow().sessionId();
    }

    LocalLogoutCoordinator coordinator() {
      return new LocalLogoutCoordinator(sessions, revoke, wire(), clock);
    }

    LogoutWireClient wire() {
      return new LogoutWireClient(
          replies,
          this::send,
          clock,
          () -> new UUID(0, sequence.incrementAndGet()),
          Duration.ofMillis(50));
    }

    void send(UUID id, byte[] body) throws JMSException {
      assertEquals(0, owned.get().get());
      ids.add(id);
      bodies.add(body);
      assertArrayEquals(header(true, "", id), body);
      if (wireFatal != null) throw wireFatal;
      if (mode.equals("lost")) throw new JMSException("private-lost-response");
      if (mode.equals("timeout")) return;
      byte[] response = header(false, mode.equals("0102") || mode.equals("9000") ? mode : code, id);
      if (mode.equals("bad-context")) put(response, 113, "c".repeat(64));
      if (mode.equals("bad-correlation")) put(response, 60, new UUID(0, 999).toString());
      assertTrue(replies.onReply(id, response));
      Arrays.fill(response, (byte) 0);
    }

    DataSource source() {
      return (DataSource)
          Proxy.newProxyInstance(
              DataSource.class.getClassLoader(),
              new Class<?>[] {DataSource.class},
              (proxy, method, args) -> {
                if (!method.getName().equals("getConnection"))
                  throw new UnsupportedOperationException("only fixture getConnection");
                int index = acquisitions.incrementAndGet();
                boolean inject = always || index == 1;
                if (inject && fault.equals("acquire")) throw new SQLException("private-acquire");
                if (inject && fault.equals("null")) return null;
                var real = db.web();
                active.incrementAndGet();
                var caller = owned.get();
                caller.incrementAndGet();
                return Proxy.newProxyInstance(
                    Connection.class.getClassLoader(),
                    new Class<?>[] {Connection.class},
                    (target, call, values) -> {
                      String name = call.getName();
                      if (name.equals("close")) {
                        try {
                          invoke(real, call, values);
                        } finally {
                          active.decrementAndGet();
                          caller.decrementAndGet();
                        }
                        if (index == fatalIndex && closeFatal != null) throw closeFatal;
                        if (inject && fault.equals("close"))
                          throw new SQLException("private-close");
                        return null;
                      }
                      if (inject && name.equals(fault)) {
                        if (primaryFault != null) throw primaryFault;
                        throw new SQLException("private-provider");
                      }
                      if (inject && name.equals("rollback") && rollbackFault != null) {
                        invoke(real, call, values);
                        throw rollbackFault;
                      }
                      if (inject && name.equals("commit") && fault.equals("commit-after")) {
                        invoke(real, call, values);
                        throw new SQLException("private-commit-after");
                      }
                      if (inject
                          && name.equals("prepareStatement")
                          && ((fault.equals("enqueue")
                                  && ((String) values[0])
                                      .startsWith("insert into schubert_web_session.pending"))
                              || (fault.equals("delete")
                                  && ((String) values[0])
                                      .startsWith("delete from schubert_web_session.web_http"))))
                        throw new SQLException("private-statement");
                      return invoke(real, call, values);
                    });
              });
    }

    void resources() {
      assertEquals(0, active.get());
      assertEquals(0, replies.pendingCount());
      bodies.forEach(body -> assertArrayEquals(new byte[body.length], body));
    }

    public void close() {
      sessionCodec.close();
      revoke.close();
    }
  }

  private static Object invoke(Object target, Method method, Object[] args) throws Throwable {
    try {
      return method.invoke(target, args);
    } catch (InvocationTargetException failure) {
      throw failure.getCause();
    }
  }

  private static byte[] header(boolean request, String code, UUID id) {
    byte[] result = new byte[request ? 256 : 280];
    Arrays.fill(result, (byte) ' ');
    put(result, 0, "SCHBNK01");
    put(result, 8, "001");
    put(result, 11, request ? "LOGREQ01" : "LOGRSP01");
    put(result, 19, "001");
    result[22] = (byte) (request ? 'Q' : 'S');
    result[23] = 'S';
    put(result, 24, (request ? id : new UUID(1, id.getLeastSignificantBits())).toString());
    put(result, 60, id.toString());
    put(result, 96, "20260908090000123");
    put(result, 113, "b".repeat(64));
    put(result, 177, "0256");
    put(result, 181, request ? "000000" : "000024");
    put(result, 187, "000000");
    put(result, 193, "000000");
    put(result, 199, request ? "000000256" : "000000280");
    put(result, 208, code);
    if (!request)
      put(
          result,
          256,
          code.equals("0000") || code.equals("0200") ? "20260908090000123" : "00000000000000000");
    return result;
  }

  private static void put(byte[] target, int offset, String text) {
    System.arraycopy(text.getBytes(StandardCharsets.US_ASCII), 0, target, offset, text.length());
  }
}
