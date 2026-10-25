package dev.codex.schubert.nk.web.revocation;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.api.idempotency.FingerprintKeyRing;
import dev.codex.schubert.nk.api.idempotency.ResponseSnapshotCodec;
import dev.codex.schubert.nk.api.security.LogoutApplicationAssembly;
import dev.codex.schubert.nk.protocol.codec.ExpectedRoute;
import dev.codex.schubert.nk.protocol.codec.FixedWidthDecoder;
import dev.codex.schubert.nk.protocol.codec.TransportBodyType;
import dev.codex.schubert.nk.protocol.codec.TransportMetadata;
import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.header.InteractionKind;
import dev.codex.schubert.nk.protocol.header.MessageKind;
import dev.codex.schubert.nk.protocol.layout.LayoutId;
import dev.codex.schubert.nk.web.logging.WebLogDatabaseFixture;
import dev.codex.schubert.nk.web.messaging.JmsRequestReplyClient;
import dev.codex.schubert.nk.web.messaging.LogoutWireClient;
import dev.codex.schubert.nk.web.messaging.ReplyCorrelationRegistry;
import jakarta.jms.JMSException;
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
import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicLong;
import java.util.concurrent.atomic.AtomicReference;
import javax.sql.DataSource;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** RERUN005: independent UI wire/SQL, real API participants; transport fixture, not VM/IT/ST. */
final class RevocationRetryCoordinatorTest {
  private static final Instant REQUESTED = Instant.parse("2026-09-08T00:00:00.123456Z");
  private static final AuthenticationContext AUTH = AuthenticationContext.of("a".repeat(64));
  private static final byte[] KEY = new byte[32]; // Public synthetic vector, never deployed.
  private static WebLogDatabaseFixture db;

  @BeforeAll
  static void start(@TempDir Path root) throws Exception {
    db = new WebLogDatabaseFixture(root);
  }

  @AfterAll
  static void stop() throws Exception {
    if (db != null) db.stop();
  }

  @BeforeEach
  void reset() throws Exception {
    sql("delete from schubert_web_session.pending_context_revocations", true);
    for (String table : List.of("request_inbox", "app_logs", "auth_sessions", "app_users"))
      sql("delete from schubert." + table, false);
  }

  @Test
  void rerun005aRealApiNormalAndExpiredFenceFreshMessageProof() throws Exception {
    for (boolean expired : List.of(false, true)) {
      reset();
      seedApi(expired);
      try (var f = new Fixture()) {
        f.realApi = true;
        f.enqueue(1);
        assertEquals(
            expired
                ? RevocationRetryCoordinator.Outcome.RETAINED
                : RevocationRetryCoordinator.Outcome.CONFIRMED,
            f.coordinator().dispatchOne());
        try (var c = db.api();
            var s = c.createStatement();
            var r =
                s.executeQuery(
                    "select revoked_at,revoke_reason from schubert.auth_sessions where id='00000000-0000-0000-0000-000000000001'")) {
          assertTrue(r.next());
          assertEquals(REQUESTED.plusSeconds(5), r.getObject(1, OffsetDateTime.class).toInstant());
          assertEquals(expired ? "EXPIRED" : "LOGOUT", r.getString(2));
        }
        assertEquals(
            expired ? 1 : 0,
            count("select count(*) from schubert_web_session.pending_context_revocations", true));
        assertEquals(1, count("select count(*) from schubert.request_inbox", false));
        assertEquals(1, count("select count(*) from schubert.app_logs", false));
        if (expired) {
          state(1, REQUESTED.plusSeconds(35), "SESSION_INVALID");
          f.clock.set(REQUESTED.plusSeconds(35));
          f.expectedStamp = "20260908090035123";
          assertEquals(RevocationRetryCoordinator.Outcome.CONFIRMED, f.coordinator().dispatchOne());
          assertEquals(
              0,
              count("select count(*) from schubert_web_session.pending_context_revocations", true));
          assertEquals(2, count("select count(*) from schubert.request_inbox", false));
          assertEquals(2, count("select count(*) from schubert.app_logs", false));
          assertNotEquals(f.ids.get(0), f.ids.get(1));
        }
        f.erased();
        assertEquals(0, f.active.get());
      }
    }
  }

  @Test
  void rerun005bActualApiCommitThenLostReplyRetainsAndFresh0200Closes() throws Exception {
    seedApi(false);
    try (var f = new Fixture()) {
      f.realApi = true;
      f.loseReply = true;
      f.enqueue(1);
      assertEquals(RevocationRetryCoordinator.Outcome.RETAINED, f.coordinator().dispatchOne());
      state(1, REQUESTED.plusSeconds(35), "UNAVAILABLE");
      assertEquals(
          1,
          count("select count(*) from schubert.auth_sessions where revoke_reason='LOGOUT'", false));
      assertEquals(1, count("select count(*) from schubert.app_logs", false));
      f.loseReply = false;
      f.clock.set(REQUESTED.plusSeconds(35));
      f.expectedStamp = "20260908090035123";
      assertEquals(RevocationRetryCoordinator.Outcome.CONFIRMED, f.coordinator().dispatchOne());
      assertEquals(
          0, count("select count(*) from schubert_web_session.pending_context_revocations", true));
      assertEquals(2, count("select count(*) from schubert.app_logs", false));
      assertNotEquals(f.ids.get(0), f.ids.get(1));
      f.erased();
    }
  }

  @Test
  void rerun005cGeneral0102ErrorWrongWireAndTimeoutKeepOriginalRow() throws Exception {
    for (String mode : List.of("0102", "9000", "wrong-context", "wrong-correlation", "timeout")) {
      reset();
      try (var f = new Fixture()) {
        f.enqueue(1);
        if (mode.equals("0102") || mode.equals("9000")) f.code = mode;
        else f.replyFault = mode;
        assertEquals(RevocationRetryCoordinator.Outcome.RETAINED, f.coordinator().dispatchOne());
        String warning =
            mode.equals("0102")
                ? "SESSION_INVALID"
                : mode.equals("9000")
                    ? "API_REJECTED"
                    : mode.equals("timeout") ? "UNAVAILABLE" : "INVALID_RESPONSE";
        state(1, REQUESTED.plusSeconds(35), warning);
        assertEquals(1, f.ids.size());
        f.erased();
        assertEquals(0, f.active.get());
      }
    }
  }

  @Test
  void rerun005dUnknownKeyBadTagAndOversizedNeverGenerateOrSendContext() throws Exception {
    for (String mode : List.of("unknown-key", "tag", "oversized")) {
      reset();
      try (var f = new Fixture()) {
        if (mode.equals("unknown-key")) {
          var identity = new RevocationPayloadIdentity(new UUID(0, 1), REQUESTED);
          try (var old = new RevocationPayloadCodec("old", KEY, null, null);
              var c = db.transaction()) {
            new PendingRevocationRepository()
                .enqueue(
                    c,
                    identity,
                    old.encrypt(identity, AUTH),
                    null,
                    RevocationFailureCode.UNAVAILABLE);
            c.commit();
          }
        } else {
          f.enqueue(1);
          sql(
              mode.equals("tag")
                  ? "update schubert_web_session.pending_context_revocations set context_ciphertext=set_byte(context_ciphertext,103,get_byte(context_ciphertext,103)#1)"
                  : "update schubert_web_session.pending_context_revocations set context_ciphertext=decode(repeat('00',117),'hex')",
              true);
        }
        assertEquals(RevocationRetryCoordinator.Outcome.RETAINED, f.coordinator().dispatchOne());
        state(
            1,
            REQUESTED.plusSeconds(35),
            mode.equals("unknown-key") ? "KEY_UNAVAILABLE" : "PAYLOAD_INVALID");
        assertTrue(f.ids.isEmpty());
        assertEquals(0, f.active.get());
      }
    }
  }

  @Test
  void rerun005eLeaseWaitBudgetAndLateReplyCannotMutateExpiredClaim() throws Exception {
    for (boolean failure : List.of(false, true)) {
      reset();
      try (var f = new Fixture()) {
        f.enqueue(1);
        f.code = failure ? "0102" : "0000";
        f.afterReply = () -> f.clock.set(REQUESTED.plusSeconds(15));
        assertEquals(RevocationRetryCoordinator.Outcome.STALE, f.coordinator().dispatchOne());
        assertEquals(
            1,
            count("select count(*) from schubert_web_session.pending_context_revocations", true));
        assertEquals(1, f.ids.size());
        f.erased();
      }
    }
    reset();
    try (var f = new Fixture()) {
      assertEquals(RevocationRetryCoordinator.Outcome.EMPTY, f.coordinator().dispatchOne());
      f.enqueue(1);
      f.acquisitions.set(0);
      f.afterFirstClose = () -> f.clock.set(REQUESTED.plusSeconds(13));
      assertEquals(RevocationRetryCoordinator.Outcome.STALE, f.coordinator().dispatchOne());
      assertTrue(f.ids.isEmpty());
      assertEquals(
          1, count("select count(*) from schubert_web_session.pending_context_revocations", true));
    }
  }

  @Test
  void rerun005fNullContractsAndCommitCloseUnknownNeverReleaseClaimToRemote() throws Exception {
    try (var f = new Fixture()) {
      var facade =
          new LogoutWireClient(
              f.replies, f::send, f.clock, UUID::randomUUID, Duration.ofMillis(50));
      assertThrows(
          NullPointerException.class,
          () -> new RevocationRetryCoordinator(null, f.codec, facade, f.clock));
      assertThrows(
          NullPointerException.class,
          () -> new RevocationRetryCoordinator(f.source(), null, facade, f.clock));
      assertThrows(
          NullPointerException.class,
          () -> new RevocationRetryCoordinator(f.source(), f.codec, null, f.clock));
      assertThrows(
          NullPointerException.class,
          () -> new RevocationRetryCoordinator(f.source(), f.codec, facade, null));
    }
    for (String phase :
        List.of(
            "acquire",
            "null",
            "setAutoCommit",
            "setReadOnly",
            "setTransactionIsolation",
            "prepareStatement",
            "commit",
            "commit-after",
            "close")) {
      reset();
      try (var f = new Fixture()) {
        f.enqueue(1);
        f.fault = phase;
        fixed(() -> f.coordinator().dispatchOne());
        assertTrue(f.ids.isEmpty());
        assertEquals(0, f.active.get());
        assertEquals(
            1,
            count("select count(*) from schubert_web_session.pending_context_revocations", true));
        if (phase.equals("commit-after") || phase.equals("close")) {
          f.fault = "";
          f.clock.set(REQUESTED.plusSeconds(15));
          f.expectedStamp = "20260908090015123";
          assertEquals(RevocationRetryCoordinator.Outcome.CONFIRMED, f.coordinator().dispatchOne());
        }
      }
    }
    for (String code : List.of("0000", "0102")) {
      reset();
      try (var f = new Fixture()) {
        f.enqueue(1);
        f.code = code;
        f.fault = "acquire";
        f.faultAcquisition = 2;
        fixed(() -> f.coordinator().dispatchOne());
        assertEquals(1, f.ids.size());
        assertEquals(0, f.active.get());
        assertEquals(
            1,
            count("select count(*) from schubert_web_session.pending_context_revocations", true));
        f.erased();
      }
    }
  }

  @Test
  void rerun005gFatalIdentityNestedCyclicFailuresAndResourceAfterconditions() throws Exception {
    for (String phase : List.of("acquire", "setReadOnly", "close")) {
      reset();
      try (var f = new Fixture()) {
        f.enqueue(1);
        f.fault = phase;
        var fatal = new AssertionError("private-direct-fatal-marker");
        f.primaryFault = fatal;
        f.fatal = fatal;
        assertSame(fatal, assertThrows(AssertionError.class, () -> f.coordinator().dispatchOne()));
        assertEquals(0, f.active.get());
        assertTrue(f.ids.isEmpty());
      }
    }
    for (int variant = 0; variant < 4; variant++) {
      reset();
      try (var f = new Fixture()) {
        f.enqueue(1);
        f.fault = "prepareStatement";
        SQLException primary = new SQLException("private-primary-marker");
        SQLException peer = new SQLException("private-peer-marker");
        var fatal = new AssertionError("private-nested-fatal-marker");
        primary.addSuppressed(peer);
        peer.addSuppressed(primary);
        if (variant == 1) peer.addSuppressed(fatal);
        if (variant == 2) primary.initCause(fatal);
        if (variant == 3) f.closeFault = new IllegalStateException("private-runtime-close", fatal);
        else f.closeFault = new SQLException("private-secondary-close");
        f.primaryFault = primary;
        f.rollbackFault = primary;
        if (variant == 0) fixed(() -> f.coordinator().dispatchOne());
        else
          assertSame(
              fatal, assertThrows(AssertionError.class, () -> f.coordinator().dispatchOne()));
        assertEquals(0, f.active.get());
        assertTrue(f.ids.isEmpty());
        assertEquals(
            1,
            count("select count(*) from schubert_web_session.pending_context_revocations", true));
      }
    }
    reset();
    try (var f = new Fixture()) {
      f.enqueue(1);
      f.fault = "setReadOnly";
      f.primaryFault = new IllegalStateException("private-runtime-primary");
      f.rollbackFault = new SQLException("private-rollback-secondary");
      fixed(() -> f.coordinator().dispatchOne());
      assertEquals(0, f.active.get());
      assertTrue(f.ids.isEmpty());
    }
  }

  @Test
  void rerun005hHundredConcurrentClaimsReachRealApiWithNoDuplicateRowOwnership() throws Exception {
    seedApi(false);
    try (var f = new Fixture()) {
      f.parallel = true;
      f.realApi = true;
      for (int i = 1; i <= 100; i++) f.enqueue(i);
      try (var pool = Executors.newFixedThreadPool(12)) {
        var results = new ArrayList<Future<RevocationRetryCoordinator.Outcome>>();
        for (int i = 0; i < 100; i++) results.add(pool.submit(() -> f.coordinator().dispatchOne()));
        for (var result : results)
          assertEquals(
              RevocationRetryCoordinator.Outcome.CONFIRMED, result.get(60, TimeUnit.SECONDS));
      }
      assertEquals(100, f.ids.size());
      assertEquals(100, new HashSet<>(f.ids).size());
      assertEquals(100, count("select count(*) from schubert.request_inbox", false));
      assertEquals(100, count("select count(*) from schubert.app_logs", false));
      assertEquals(
          0, count("select count(*) from schubert_web_session.pending_context_revocations", true));
      assertEquals(0, f.active.get());
      f.erased();
    }
  }

  private static void fixed(org.junit.jupiter.api.function.Executable action) {
    var error = assertThrows(RevocationRetryException.class, action);
    assertEquals("retained revocation retry infrastructure unavailable", error.getMessage());
    assertNull(error.getCause());
    assertEquals(0, error.getSuppressed().length);
  }

  private static void seedApi(boolean expired) throws Exception {
    sql(
        "insert into schubert.app_users(id,username,username_key,password_hash,role,status,password_changed_at,created_at,updated_at) values(7,'logout-user','logout-user','unused-fixture','USER','ACTIVE','2026-09-08','2026-09-08','2026-09-08')",
        false);
    try (var c = db.api();
        var s =
            c.prepareStatement(
                "insert into schubert.auth_sessions(id,user_id,context_hash,context_ciphertext,key_version,issued_at,last_accessed_at,expires_at,client_address,created_message_id) values('00000000-0000-0000-0000-000000000001',7,?,?,'test','2026-09-08','2026-09-08',?,'192.0.2.99','00000000-0000-0000-0000-000000000010')")) {
      s.setString(
          1,
          HexFormat.of()
              .formatHex(
                  MessageDigest.getInstance("SHA-256")
                      .digest("a".repeat(64).getBytes(StandardCharsets.US_ASCII))));
      s.setBytes(2, new byte[29]);
      s.setObject(
          3,
          (expired ? REQUESTED.plusSeconds(1) : REQUESTED.plusSeconds(28800))
              .atOffset(ZoneOffset.UTC));
      s.executeUpdate();
    }
  }

  private static int count(String query, boolean web) throws Exception {
    try (var c = web ? db.web() : db.api();
        var s = c.createStatement();
        var r = s.executeQuery(query)) {
      assertTrue(r.next());
      return r.getInt(1);
    }
  }

  private static void sql(String query, boolean web) throws Exception {
    try (var c = web ? db.web() : db.api();
        var s = c.createStatement()) {
      s.executeUpdate(query);
    }
  }

  private static void state(int attempt, Instant due, String code) throws Exception {
    try (var c = db.web();
        var s = c.createStatement();
        var r =
            s.executeQuery(
                "select attempt_count,next_attempt_at,last_error_code,expires_at,lease_owner,lease_until from schubert_web_session.pending_context_revocations")) {
      assertTrue(r.next());
      assertEquals(attempt, r.getInt(1));
      assertEquals(due, r.getObject(2, OffsetDateTime.class).toInstant());
      assertEquals(code, r.getString(3));
      assertNull(r.getObject(4));
      assertNull(r.getObject(5));
      assertNull(r.getObject(6));
      assertFalse(r.next());
    }
  }

  private static final class MutableClock extends Clock {
    final AtomicReference<Instant> value = new AtomicReference<>(REQUESTED.plusSeconds(5));

    void set(Instant at) {
      value.set(at);
    }

    @Override
    public ZoneId getZone() {
      return ZoneOffset.UTC;
    }

    @Override
    public Clock withZone(ZoneId zone) {
      assertEquals(ZoneOffset.UTC, zone);
      return this;
    }

    @Override
    public Instant instant() {
      return value.get();
    }
  }

  private static final class Fixture implements AutoCloseable {
    final MutableClock clock = new MutableClock();
    final AtomicInteger active = new AtomicInteger();
    final AtomicInteger acquisitions = new AtomicInteger();
    final ThreadLocal<AtomicInteger> owned = ThreadLocal.withInitial(AtomicInteger::new);
    final RevocationPayloadCodec codec = new RevocationPayloadCodec("test", KEY, null, null);
    final FingerprintKeyRing fingerprints = new FingerprintKeyRing("f1", new byte[32], null, null);
    final ResponseSnapshotCodec snapshots =
        new ResponseSnapshotCodec("s1", new byte[32], null, null);
    final JmsRequestReplyClient replies =
        new JmsRequestReplyClient(new ReplyCorrelationRegistry(), clock, 12);
    final List<UUID> ids = Collections.synchronizedList(new ArrayList<>());
    final List<byte[]> sent = Collections.synchronizedList(new ArrayList<>());
    final AtomicLong sequence = new AtomicLong(100);
    boolean realApi;
    boolean loseReply;
    boolean parallel;
    String code = "0000";
    String expectedStamp = "20260908090005123";
    String replyFault = "";
    String fault = "";
    int faultAcquisition = 1;
    Error fatal;
    Throwable primaryFault;
    Throwable rollbackFault;
    Throwable closeFault;
    Runnable afterReply = () -> {};
    Runnable afterFirstClose = () -> {};

    RevocationRetryCoordinator coordinator() {
      var facade =
          new LogoutWireClient(
              replies,
              this::send,
              clock,
              () -> new UUID(0, sequence.incrementAndGet()),
              Duration.ofMillis(50));
      return new RevocationRetryCoordinator(source(), codec, facade, clock);
    }

    void enqueue(int number) throws Exception {
      var identity = new RevocationPayloadIdentity(new UUID(0, number), REQUESTED);
      try (var c = db.transaction()) {
        new PendingRevocationRepository()
            .enqueue(
                c,
                identity,
                codec.encrypt(identity, AUTH),
                null,
                RevocationFailureCode.UNAVAILABLE);
        c.commit();
      }
    }

    void send(UUID id, byte[] body) throws JMSException {
      assertEquals(0, owned.get().get());
      if (!parallel) assertEquals(0, active.get());
      ids.add(id);
      sent.add(body);
      assertArrayEquals(request(id, expectedStamp), body);
      byte[] response;
      try {
        if (!parallel)
          try (var c = db.admin();
              var s = c.createStatement();
              var r =
                  s.executeQuery(
                      "select count(*) from pg_stat_activity where usename='schubert_web_session' and state in ('active','idle in transaction')")) {
            assertTrue(r.next());
            assertEquals(0, r.getInt(1));
          }
        if (realApi) {
          var api = LogoutApplicationAssembly.create(fingerprints, snapshots, clock);
          var metadata =
              new TransportMetadata(
                  TransportBodyType.BYTES,
                  "ID:synthetic-" + id,
                  id,
                  Optional.of("nk.sync.reply.web"),
                  clock.instant().plusSeconds(5).toEpochMilli(),
                  2,
                  1,
                  id,
                  new LayoutId("LOGREQ01"),
                  "001",
                  "nk.sync.request");
          var route =
              new ExpectedRoute(
                  MessageKind.REQUEST,
                  InteractionKind.SYNCHRONOUS,
                  "nk.sync.request",
                  Optional.of("nk.sync.reply.web"),
                  true);
          try (var c = db.api()) {
            c.setAutoCommit(false);
            response =
                api.execute(
                    c, FixedWidthDecoder.standard().decode(body, metadata, route), clock.instant());
            c.commit();
          }
        } else response = response(id, code);
      } catch (Exception failure) {
        throw new AssertionError(failure);
      }
      if (loseReply) {
        Arrays.fill(response, (byte) 0);
        throw new JMSException("private-lost-reply-marker");
      }
      if (replyFault.equals("timeout")) {
        Arrays.fill(response, (byte) 0);
        return;
      }
      if (replyFault.equals("wrong-context")) put(response, 113, "c".repeat(64));
      if (replyFault.equals("wrong-correlation")) put(response, 60, new UUID(0, 999).toString());
      assertTrue(replies.onReply(id, response));
      Arrays.fill(response, (byte) 0);
      afterReply.run();
    }

    DataSource source() {
      return (DataSource)
          Proxy.newProxyInstance(
              DataSource.class.getClassLoader(),
              new Class<?>[] {DataSource.class},
              (proxy, method, args) -> {
                if (!method.getName().equals("getConnection"))
                  throw new UnsupportedOperationException("fixture only getConnection");
                int index = acquisitions.incrementAndGet();
                boolean inject = index == faultAcquisition;
                if (inject && fault.equals("acquire")) {
                  if (primaryFault != null) throw primaryFault;
                  throw new SQLException("private-acquire-marker");
                }
                if (inject && fault.equals("null")) return null;
                Connection real = db.web();
                active.incrementAndGet();
                AtomicInteger callerOwned = owned.get();
                callerOwned.incrementAndGet();
                AtomicBoolean closed = new AtomicBoolean();
                return Proxy.newProxyInstance(
                    Connection.class.getClassLoader(),
                    new Class<?>[] {Connection.class},
                    (target, call, values) -> {
                      String name = call.getName();
                      if (name.equals("close")) {
                        try {
                          invoke(real, call, values);
                        } finally {
                          if (closed.compareAndSet(false, true)) {
                            active.decrementAndGet();
                            callerOwned.decrementAndGet();
                          }
                        }
                        if (index == 1) afterFirstClose.run();
                        if (inject && closeFault != null) throw closeFault;
                        if (inject && fault.equals("close")) {
                          if (fatal != null) throw fatal;
                          throw new SQLException("private-close-marker");
                        }
                        return null;
                      }
                      if (inject && name.equals("rollback") && rollbackFault != null)
                        throw rollbackFault;
                      if (inject && name.equals(fault)) {
                        if (primaryFault != null) throw primaryFault;
                        if (fatal != null) throw fatal;
                        throw new SQLException("private-provider-marker");
                      }
                      if (inject && name.equals("commit") && fault.equals("commit-after")) {
                        invoke(real, call, values);
                        throw new SQLException("private-commit-unknown-marker");
                      }
                      return invoke(real, call, values);
                    });
              });
    }

    void erased() {
      assertEquals(0, replies.pendingCount());
      sent.forEach(body -> assertArrayEquals(new byte[body.length], body));
    }

    @Override
    public void close() {
      snapshots.close();
      fingerprints.close();
      codec.close();
    }
  }

  private static Object invoke(Object target, Method method, Object[] args) throws Throwable {
    try {
      return method.invoke(target, args);
    } catch (InvocationTargetException failure) {
      throw failure.getCause();
    }
  }

  private static byte[] request(UUID id, String stamp) {
    byte[] result = header(true, "", id);
    put(result, 96, stamp);
    return result;
  }

  private static byte[] response(UUID id, String code) {
    byte[] result = header(false, code, id);
    put(
        result,
        256,
        code.equals("0000") || code.equals("0200") ? "20260908090005123" : "00000000000000000");
    return result;
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
    put(result, 96, "20260908090005123");
    put(result, 113, "a".repeat(64));
    put(result, 177, "0256");
    put(result, 181, request ? "000000" : "000024");
    put(result, 187, "000000");
    put(result, 193, "000000");
    put(result, 199, request ? "000000256" : "000000280");
    put(result, 208, code);
    return result;
  }

  private static void put(byte[] target, int offset, String value) {
    System.arraycopy(value.getBytes(StandardCharsets.US_ASCII), 0, target, offset, value.length());
  }
}
