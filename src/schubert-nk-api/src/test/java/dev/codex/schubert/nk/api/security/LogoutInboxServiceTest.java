package dev.codex.schubert.nk.api.security;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assertions.fail;

import dev.codex.schubert.nk.api.idempotency.EncryptedResponseSnapshot;
import dev.codex.schubert.nk.api.idempotency.FingerprintKeyRing;
import dev.codex.schubert.nk.api.idempotency.InboxCompletion;
import dev.codex.schubert.nk.api.idempotency.InboxCompletionState;
import dev.codex.schubert.nk.api.idempotency.InboxResultReference;
import dev.codex.schubert.nk.api.idempotency.JdbcInboxCoordinator;
import dev.codex.schubert.nk.api.idempotency.ResponseSnapshotCodec;
import dev.codex.schubert.nk.api.idempotency.ResponseSnapshotIdentity;
import dev.codex.schubert.nk.api.logging.ApiLogDatabaseFixture;
import dev.codex.schubert.nk.protocol.codec.PermanentProtocolException;
import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.header.CommonHeader;
import dev.codex.schubert.nk.protocol.header.InteractionKind;
import dev.codex.schubert.nk.protocol.header.MessageKind;
import dev.codex.schubert.nk.protocol.header.ResultCode;
import dev.codex.schubert.nk.protocol.layout.FixedPayload;
import dev.codex.schubert.nk.protocol.layout.LayoutId;
import dev.codex.schubert.nk.protocol.layout.WireMessage;
import java.io.ByteArrayOutputStream;
import java.io.DataOutputStream;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.lang.reflect.Proxy;
import java.nio.charset.StandardCharsets;
import java.nio.file.Path;
import java.security.MessageDigest;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.time.Clock;
import java.time.Instant;
import java.time.ZoneId;
import java.time.ZoneOffset;
import java.time.temporal.ChronoUnit;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashSet;
import java.util.HexFormat;
import java.util.List;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicLong;
import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.function.Executable;
import org.junit.jupiter.api.io.TempDir;

/**
 * PT-AUT-LOGOUT-INBOX-001..007; independent UI232/234 280-byte, JCA/LP-HMAC and real SQL oracles.
 */
final class LogoutInboxServiceTest {
  @TempDir static Path root;
  private static ApiLogDatabaseFixture database;
  private static ContextHash hashes;
  private static FingerprintKeyRing keys;
  private static ResponseSnapshotCodec snapshots;
  private static LogoutReplayService responses;
  private static AuthSessionRevocationService revocations;
  private static final Instant NOW = Instant.parse("2026-09-08T01:00:00.123456Z");
  private static final String STAMP = "20260908100000123";
  private static final UUID REQUEST = new UUID(0, 101);
  private static final UUID SESSION = new UUID(0, 1);
  private static final AuthenticationContext RAW = AuthenticationContext.of("a".repeat(64));
  private final AtomicLong ids = new AtomicLong(1000);

  @BeforeAll
  static void start() throws Exception {
    database = new ApiLogDatabaseFixture(root);
    hashes = new ContextHash();
    keys = new FingerprintKeyRing("f1", key(7), null, null);
    snapshots = new ResponseSnapshotCodec("s1", key(3), null, null);
    responses = new LogoutReplayService(snapshots, hashes);
    revocations = new AuthSessionRevocationService(hashes);
  }

  @AfterAll
  static void stop() throws Exception {
    if (snapshots != null) snapshots.close();
    if (keys != null) keys.close();
    if (database != null) database.stop();
  }

  @BeforeEach
  void seed() throws Exception {
    sql("delete from schubert.request_inbox");
    sql("delete from schubert.app_logs");
    sql("delete from schubert.auth_sessions");
    sql("delete from schubert.app_users");
    sql(
        "insert into schubert.app_users(id,username,username_key,password_hash,role,status,password_changed_at,created_at,updated_at)"
            + " values(7,'logout-user','logout-user','unused-fixture','USER','ACTIVE','2026-09-08','2026-09-08','2026-09-08'),"
            + "(8,'other-user','other-user','unused-fixture','USER','ACTIVE','2026-09-08','2026-09-08','2026-09-08')");
    try (var c = database.api();
        var s =
            c.prepareStatement(
                "insert into schubert.auth_sessions(id,user_id,context_hash,context_ciphertext,key_version,issued_at,last_accessed_at,expires_at,client_address,created_message_id)"
                    + " values(?,?,?,?,'a1','2026-09-08T00:00:00Z','2026-09-08T00:00:00Z','2026-09-08T08:00:00Z','192.0.2.99',?)")) {
      for (int i = 1; i <= 3; i++) {
        s.setObject(1, new UUID(0, i));
        s.setLong(2, i == 3 ? 8 : 7);
        String raw = (i == 1 ? "a" : i == 2 ? "c" : "b").repeat(64);
        s.setString(
            3,
            HexFormat.of()
                .formatHex(
                    MessageDigest.getInstance("SHA-256")
                        .digest(raw.getBytes(StandardCharsets.US_ASCII))));
        s.setBytes(4, new byte[29]);
        s.setObject(5, new UUID(0, i + 10));
        s.executeUpdate();
      }
    }
    ids.set(1000);
  }

  @Test
  void initialReplayAndNewMessageKeepOneOriginalRevocation() throws Exception {
    var input = request(RAW, REQUEST);
    try (var c = database.transaction()) {
      assertArrayEquals(
          golden("0000", RAW, REQUEST, new UUID(0, 1000), STAMP),
          service(NOW).execute(c, input, NOW.minusSeconds(1)));
      effects(0, 0, 0);
      c.rollback();
    }
    effects(0, 0, 0);
    assertArrayEquals(
        golden("0000", RAW, REQUEST, new UUID(0, 1001), STAMP),
        call(service(NOW), input, NOW.minusSeconds(1)));
    assertArrayEquals(
        golden("0200", RAW, REQUEST, new UUID(0, 1002), STAMP), call(service(NOW), input, NOW));
    effects(1, 1, 1);
    assertEquals(1, count("select count(*) from schubert.app_logs where remote_address is null"));
    try (var c = database.api();
        var s = c.createStatement();
        var r =
            s.executeQuery(
                "select owner_user_id,operation_token,request_fingerprint_hmac,completed_at,expires_at from schubert.request_inbox")) {
      assertTrue(r.next());
      assertEquals(7, r.getLong(1));
      assertNull(r.getObject(2));
      assertEquals(fingerprint(), r.getString(3));
      assertEquals(NOW, r.getObject(4, java.time.OffsetDateTime.class).toInstant());
      assertEquals(
          Instant.parse("2026-09-15T01:00:00.123456Z"),
          r.getObject(5, java.time.OffsetDateTime.class).toInstant());
      assertFalse(r.next());
    }
    var another = AuthenticationContext.of("c".repeat(64));
    assertArrayEquals(
        golden("0200", another, REQUEST, new UUID(0, 1003), STAMP),
        call(service(NOW), request(another, REQUEST), NOW));
    effects(1, 1, 1); // Header context excluded from HMAC; do not revoke the second session.
    assertPermanent(
        () -> call(service(NOW), request(AuthenticationContext.of("b".repeat(64)), REQUEST), NOW));
    UUID next = new UUID(0, 102);
    byte[] later = call(service(NOW.plusSeconds(60)), request(RAW, next), NOW.plusSeconds(60));
    assertArrayEquals(golden("0200", RAW, next, new UUID(0, 1005), "20260908100100123"), later);
    effects(2, 1, 2);
    assertEquals(
        1,
        count(
            "select count(*) from schubert.auth_sessions where id='"
                + SESSION
                + "' and revoked_at='2026-09-08T01:00:00.123456Z' and last_accessed_at='2026-09-08T00:00:00Z' and expires_at='2026-09-08T08:00:00Z'"));
  }

  @Test
  void invalidAndExpiredContextsNeverGainAuthority() throws Exception {
    var unknown = AuthenticationContext.of("f".repeat(64));
    assertArrayEquals(
        golden("0102", unknown, REQUEST, new UUID(0, 1000), STAMP),
        call(service(NOW), request(unknown, REQUEST), NOW));
    effects(0, 0, 0);
    for (String mutation :
        List.of(
            "update schubert.app_users set status='DISABLED' where id=7",
            "update schubert.auth_sessions set expires_at='2026-09-08T01:00:00.123456Z'",
            "update schubert.auth_sessions set expires_at='2026-09-08T01:00:00.123455Z'")) {
      seed();
      sql(mutation);
      boolean expired = mutation.contains("expires_at");
      assertArrayEquals(
          golden("0102", RAW, REQUEST, new UUID(0, 1000), STAMP),
          call(service(NOW), request(RAW, REQUEST), NOW));
      effects(1, expired ? 1 : 0, expired ? 1 : 0);
      assertEquals(
          1,
          count(
              "select count(*) from schubert.request_inbox where processing_state='ERROR' and result_ref_type='NONE'"));
      sql("update schubert.app_users set status='ACTIVE'");
      sql("update schubert.auth_sessions set expires_at='2026-09-08T08:00:00Z'");
      assertArrayEquals(
          golden("0102", RAW, REQUEST, new UUID(0, 1001), STAMP),
          call(service(NOW), request(RAW, REQUEST), NOW));
      effects(1, expired ? 1 : 0, expired ? 1 : 0);
      UUID next = new UUID(0, 103);
      assertArrayEquals(
          golden(expired ? "0200" : "0000", RAW, next, new UUID(0, 1002), STAMP),
          call(service(NOW), request(RAW, next), NOW));
      effects(2, 1, expired ? 2 : 1);
      sql("update schubert.app_users set status='DISABLED' where id=7");
      sql("update schubert.auth_sessions set expires_at='2026-09-08T00:00:01Z'");
      assertEquals(
          "0200",
          text(
              call(service(NOW.plusSeconds(60)), request(RAW, next), NOW.plusSeconds(60)), 208, 4));
      effects(2, 1, expired ? 2 : 1);
    }
  }

  @Test
  void concurrentRedeliveryRevokesAndAuditsOnce() throws Exception {
    var service = service(NOW);
    var input = request(RAW, REQUEST);
    try (var pool = Executors.newFixedThreadPool(16)) {
      List<Future<byte[]>> calls = new ArrayList<>();
      for (int i = 0; i < 100; i++) calls.add(pool.submit(() -> call(service, input, NOW)));
      int initial = 0;
      int replay = 0;
      Set<UUID> emitted = new HashSet<>();
      for (var future : calls) {
        byte[] body = future.get();
        String code = text(body, 208, 4);
        UUID id = UUID.fromString(text(body, 24, 36));
        if (code.equals("0000")) initial++;
        else if (code.equals("0200")) replay++;
        else fail("unexpected Logout result");
        assertTrue(emitted.add(id));
        assertArrayEquals(golden(code, RAW, REQUEST, id, STAMP), body);
      }
      assertEquals(1, initial);
      assertEquals(99, replay);
    }
    effects(1, 1, 1);
    assertEquals(
        1,
        count(
            "select count(*) from schubert.app_logs where remote_address is null and actor_user_id=7"));
  }

  @Test
  void rerun001ExpiryFaultsRollbackFenceAuditAndInboxTogether() throws Exception {
    for (String point :
        List.of(
            "update schubert.auth_sessions",
            "insert into schubert.app_logs",
            "update schubert.request_inbox",
            "close:select s.id",
            "close:update schubert.auth_sessions",
            "close:insert into schubert.app_logs",
            "close:update schubert.request_inbox")) {
      seed();
      sql("update schubert.auth_sessions set expires_at='" + NOW + "' where id='" + SESSION + "'");
      try (var connection = database.transaction()) {
        assertInfrastructure(
            () -> service(NOW).execute(fault(connection, point), request(RAW, REQUEST), NOW));
        assertFalse(connection.isClosed());
        connection.rollback();
      }
      effects(0, 0, 0);
      assertEquals(
          1,
          count(
              "select count(*) from schubert.auth_sessions where id='"
                  + SESSION
                  + "' and not revoked and revoked_at is null and revoke_reason is null"));
    }
  }

  @Test
  void rerun001PriorTouchIsCurrentAndLateVerifierCannotUndoFence() throws Exception {
    sql("update schubert.auth_sessions set expires_at='" + NOW + "' where id='" + SESSION + "'");
    var verifier = new AuthenticationContextVerifier(hashes);
    try (var connection = database.transaction()) {
      assertEquals(7, verifier.verify(connection, RAW, NOW.minusSeconds(1)).userId());
      connection.commit();
    }
    assertArrayEquals(
        golden("0000", RAW, REQUEST, new UUID(0, 1000), STAMP),
        call(service(NOW), request(RAW, REQUEST), NOW));
    effects(1, 1, 1);
    assertEquals(
        1,
        count(
            "select count(*) from schubert.auth_sessions where id='"
                + SESSION
                + "' and revoke_reason='LOGOUT' and expires_at='2026-09-08T08:59:59.123456Z'"));

    seed();
    sql("update schubert.auth_sessions set expires_at='" + NOW + "' where id='" + SESSION + "'");
    var waiting = new CountDownLatch(1);
    try (var connection = database.transaction();
        var pool = Executors.newSingleThreadExecutor()) {
      assertArrayEquals(
          golden("0102", RAW, REQUEST, new UUID(0, 1000), STAMP),
          service(NOW).execute(connection, request(RAW, REQUEST), NOW));
      var delayed =
          pool.submit(
              () -> {
                try (var other = database.transaction()) {
                  Connection wrapped =
                      (Connection)
                          Proxy.newProxyInstance(
                              getClass().getClassLoader(),
                              new Class<?>[] {Connection.class},
                              (p, m, a) -> {
                                if (m.getName().equals("prepareStatement")
                                    && a[0] instanceof String query
                                    && query.startsWith("select u.id")) waiting.countDown();
                                return invoke(other, m, a);
                              });
                  assertThrows(
                      AuthenticationContextException.class,
                      () -> verifier.verify(wrapped, RAW, NOW.minusSeconds(1)));
                  other.rollback();
                  return true;
                }
              });
      try {
        assertTrue(waiting.await(10, TimeUnit.SECONDS));
        assertFalse(delayed.isDone());
      } finally {
        connection.commit();
      }
      assertTrue(delayed.get(10, TimeUnit.SECONDS));
    }
    effects(1, 1, 1);
    assertEquals(
        1,
        count(
            "select count(*) from schubert.auth_sessions where id='"
                + SESSION
                + "' and revoke_reason='EXPIRED' and expires_at='"
                + NOW
                + "' and last_accessed_at='2026-09-08T00:00:00Z'"));
  }

  @Test
  void rerun001ExpiryBoundaryFencesAtomicallyAndPreservesErrorReplay() throws Exception {
    for (int micros : new int[] {-1, 0, 1}) {
      seed();
      Instant expiry = NOW.plusNanos(micros * 1000L);
      sql(
          "update schubert.auth_sessions set expires_at='"
              + expiry
              + "' where id='"
              + SESSION
              + "'");
      boolean expired = micros <= 0;
      assertArrayEquals(
          golden(expired ? "0102" : "0000", RAW, REQUEST, new UUID(0, 1000), STAMP),
          call(service(NOW), request(RAW, REQUEST), NOW));
      effects(1, 1, 1);
      assertEquals(
          1,
          count(
              "select count(*) from schubert.app_logs where action='SESSION_REVOKED'"
                  + " and details->>'reason'='"
                  + (expired ? "EXPIRED" : "LOGOUT")
                  + "' and details->>'resultCode'='"
                  + (expired ? "0102" : "0000")
                  + "'"));
      assertEquals(
          1,
          count(
              "select count(*) from schubert.auth_sessions where id='"
                  + SESSION
                  + "' and revoked and revoked_at='"
                  + NOW
                  + "' and revoke_reason='"
                  + (expired ? "EXPIRED" : "LOGOUT")
                  + "'"));
      assertEquals(
          1,
          count(
              "select count(*) from schubert.request_inbox where processing_state='"
                  + (expired ? "ERROR" : "COMPLETED")
                  + "'"));
      assertArrayEquals(
          golden(expired ? "0102" : "0200", RAW, REQUEST, new UUID(0, 1001), STAMP),
          call(service(NOW), request(RAW, REQUEST), NOW));
      effects(1, 1, 1);
      UUID fresh = new UUID(0, 102);
      assertArrayEquals(
          golden("0200", RAW, fresh, new UUID(0, 1002), STAMP),
          call(service(NOW), request(RAW, fresh), NOW));
      effects(2, 1, 2);
    }
  }

  @Test
  void rerun001CurrentClockIsReadAfterSessionLock() throws Exception {
    var now = new java.util.concurrent.atomic.AtomicReference<>(NOW);
    var locks = new java.util.concurrent.atomic.AtomicInteger();
    Clock clock =
        new Clock() {
          @Override
          public ZoneId getZone() {
            return ZoneOffset.UTC;
          }

          @Override
          public Clock withZone(ZoneId zone) {
            return Clock.fixed(now.get(), zone);
          }

          @Override
          public Instant instant() {
            return now.get();
          }
        };
    var service =
        new LogoutInboxService(
            new JdbcInboxCoordinator(keys),
            revocations,
            responses,
            hashes,
            clock,
            () -> new UUID(0, ids.getAndIncrement()));
    sql(
        "update schubert.auth_sessions set expires_at='2026-09-08T01:00:00.123457Z' where id='"
            + SESSION
            + "'");
    try (var connection = database.transaction()) {
      Connection wrapped =
          (Connection)
              Proxy.newProxyInstance(
                  getClass().getClassLoader(),
                  new Class<?>[] {Connection.class},
                  (p, m, a) -> {
                    Object value = invoke(connection, m, a);
                    if (m.getName().equals("prepareStatement")
                        && a[0] instanceof String query
                        && query.startsWith("select s.id,s.user_id,s.revoked")) {
                      return Proxy.newProxyInstance(
                          getClass().getClassLoader(),
                          new Class<?>[] {PreparedStatement.class},
                          (sp, sm, sa) -> {
                            Object result = invoke(value, sm, sa);
                            if (sm.getName().equals("executeQuery")) {
                              locks.incrementAndGet();
                              now.set(Instant.parse("2026-09-08T01:00:00.123458Z"));
                            }
                            return result;
                          });
                    }
                    return value;
                  });
      assertArrayEquals(
          golden("0102", RAW, REQUEST, new UUID(0, 1000), STAMP),
          service.execute(wrapped, request(RAW, REQUEST), NOW));
      connection.commit();
    }
    assertEquals(1, locks.get());
    effects(1, 1, 1);
    assertEquals(
        1,
        count(
            "select count(*) from schubert.auth_sessions where id='"
                + SESSION
                + "' and revoked_at='2026-09-08T01:00:00.123458Z' and revoke_reason='EXPIRED'"));
  }

  @Test
  void movingClockKeepsRevocationAndAuditTogetherButExpiresFromCompletion() throws Exception {
    var ticks = new java.util.concurrent.atomic.AtomicInteger();
    var clock =
        new Clock() {
          @Override
          public ZoneId getZone() {
            return ZoneOffset.UTC;
          }

          @Override
          public Clock withZone(ZoneId zone) {
            throw new UnsupportedOperationException("fixed fixture zone");
          }

          @Override
          public Instant instant() {
            return NOW.plusSeconds(ticks.incrementAndGet());
          }
        };
    var service =
        new LogoutInboxService(
            new JdbcInboxCoordinator(keys),
            revocations,
            responses,
            hashes,
            clock,
            () -> new UUID(0, ids.getAndIncrement()));
    var input = request(RAW, REQUEST);
    byte[] expected = golden("0000", RAW, REQUEST, new UUID(0, 1000), "20260908100003123");
    put(expected, 256, "20260908100001123");
    assertArrayEquals(expected, call(service, input, NOW));
    assertEquals(3, ticks.get());
    assertEquals(
        1,
        count(
            "select count(*) from schubert.auth_sessions where revoked and revoked_at='2026-09-08T01:00:01.123456Z'"));
    assertEquals(
        1,
        count(
            "select count(*) from schubert.app_logs where logged_at='2026-09-08T01:00:01.123456Z' and remote_address is null"));
    assertEquals(
        1,
        count(
            "select count(*) from schubert.request_inbox where created_at='2026-09-08T01:00:00.123456Z' and completed_at='2026-09-08T01:00:02.123456Z' and expires_at='2026-09-15T01:00:02.123456Z'"));
    put(expected, 24, new UUID(0, 1001).toString());
    put(expected, 96, "20260908100004123");
    put(expected, 208, "0200");
    assertArrayEquals(expected, call(service, input, NOW.plusSeconds(60)));
    assertEquals(4, ticks.get());
    effects(1, 1, 1);
    assertEquals(
        1,
        count(
            "select count(*) from schubert.request_inbox where expires_at='2026-09-15T01:00:02.123456Z'"));
  }

  @Test
  void savedMetadataCiphertextAndReferencesFailClosed() throws Exception {
    call(service(NOW), request(RAW, REQUEST), NOW);
    InboxCompletion saved = saved();
    List<InboxCompletion> invalid =
        List.of(
            copy(
                saved,
                InboxCompletionState.ERROR,
                saved.resultReference(),
                "LOGRSP01",
                "001",
                saved.responseSnapshot()),
            copy(
                saved,
                saved.state(),
                InboxResultReference.none(),
                "LOGRSP01",
                "001",
                saved.responseSnapshot()),
            copy(
                saved,
                saved.state(),
                saved.resultReference(),
                "GAMRSP01",
                "001",
                saved.responseSnapshot()),
            copy(
                saved,
                saved.state(),
                saved.resultReference(),
                "LOGRSP01",
                "002",
                saved.responseSnapshot()),
            copy(
                saved, saved.state(), saved.resultReference(), "LOGRSP01", "001", Optional.empty()),
            copy(
                saved,
                saved.state(),
                InboxResultReference.authSession(new UUID(0, 99)),
                "LOGRSP01",
                "001",
                saved.responseSnapshot()),
            copy(
                saved,
                saved.state(),
                InboxResultReference.authSession(new UUID(0, 3)),
                "LOGRSP01",
                "001",
                saved.responseSnapshot()),
            copy(
                saved,
                saved.state(),
                InboxResultReference.authSession(new UUID(0, 2)),
                "LOGRSP01",
                "001",
                saved.responseSnapshot()));
    try (var c = database.transaction()) {
      for (var bad : invalid) assertInfrastructure(() -> restore(c, bad, 7));
      for (long owner : new long[] {0, 8, 1_000_000_000_000L})
        assertInfrastructure(() -> restore(c, saved, owner));
      for (String mutation :
          List.of("revoked_at='2026-09-08T01:00:00.124456Z'", "context_hash=repeat('f',64)")) {
        var save = c.setSavepoint();
        try (var s = c.createStatement()) {
          s.executeUpdate(
              "update schubert.auth_sessions set " + mutation + " where id='" + SESSION + "'");
        }
        assertInfrastructure(() -> restore(c, saved, 7));
        c.rollback(save);
      }
      for (var change :
          List.of(
              new String[] {"0", "BADMAGIC"},
              new String[] {"11", "LGNRSP01"},
              new String[] {"60", new UUID(0, 999).toString()},
              new String[] {"113", "f".repeat(64)},
              new String[] {"256", "20260908100000124"},
              new String[] {"256", "00000000000000000"},
              new String[] {"273", "x"})) {
        byte[] body = golden("0000", RAW, REQUEST, new UUID(0, 1000), STAMP);
        put(body, Integer.parseInt(change[0]), change[1]);
        var bad = withBody(saved, body);
        assertInfrastructure(() -> restore(c, bad, 7));
      }
      for (int size : new int[] {279, 281}) {
        var bad =
            withBody(
                saved, Arrays.copyOf(golden("0000", RAW, REQUEST, new UUID(0, 1000), STAMP), size));
        assertInfrastructure(() -> restore(c, bad, 7));
      }
      for (String code : List.of("0101", "9000")) {
        var bad =
            copy(
                saved,
                InboxCompletionState.ERROR,
                InboxResultReference.none(),
                "LOGRSP01",
                "001",
                Optional.of(
                    snapshots.encrypt(
                        identity(7), golden(code, RAW, REQUEST, new UUID(0, 1000), STAMP))));
        assertInfrastructure(() -> restore(c, bad, 7));
      }
      var denied = responses.captureDenied(7, RAW, REQUEST, new UUID(0, 900), NOW);
      assertInfrastructure(
          () ->
              restore(
                  c,
                  copy(
                      denied,
                      InboxCompletionState.COMPLETED,
                      denied.resultReference(),
                      "LOGRSP01",
                      "001",
                      denied.responseSnapshot()),
                  7));
      assertInfrastructure(
          () ->
              restore(
                  c,
                  copy(
                      denied,
                      denied.state(),
                      saved.resultReference(),
                      "LOGRSP01",
                      "001",
                      denied.responseSnapshot()),
                  7));
      byte[] cipher = saved.responseSnapshot().orElseThrow().ciphertext();
      cipher[cipher.length - 1] ^= 1;
      var tampered =
          copy(
              saved,
              saved.state(),
              saved.resultReference(),
              "LOGRSP01",
              "001",
              Optional.of(new EncryptedResponseSnapshot("s1", cipher)));
      assertInfrastructure(() -> restore(c, tampered, 7));
      var unknown =
          copy(
              saved,
              saved.state(),
              saved.resultReference(),
              "LOGRSP01",
              "001",
              Optional.of(
                  new EncryptedResponseSnapshot(
                      "unknown", saved.responseSnapshot().orElseThrow().ciphertext())));
      assertInfrastructure(() -> restore(c, unknown, 7));
      c.rollback();
    }
    for (String mutation :
        List.of("fingerprint_key_version='unknown'", "response_key_version='unknown'")) {
      try (var c = database.transaction();
          var s = c.createStatement()) {
        s.executeUpdate("update schubert.request_inbox set " + mutation);
        assertInfrastructure(() -> service(NOW).execute(c, request(RAW, REQUEST), NOW));
        c.rollback();
      }
    }
    try (var c = database.transaction();
        var s = c.createStatement()) {
      s.executeUpdate(
          "update schubert.request_inbox set processing_state='PROCESSING',result_ref_type=null,result_ref_id=null,result_ref_uuid=null,response_layout_id=null,response_version=null,response_body_encrypted=null,response_key_version=null,completed_at=null");
      byte[] result = service(NOW).execute(c, request(RAW, REQUEST), NOW);
      assertArrayEquals(
          golden("9000", RAW, REQUEST, UUID.fromString(text(result, 24, 36)), STAMP), result);
      c.rollback();
    }
    effects(1, 1, 1);
  }

  @Test
  void jdbcAndCryptoFaultsRollBackEveryEffect() throws Exception {
    for (String point :
        List.of(
            "select u.id",
            "insert into schubert.request_inbox",
            "select s.id",
            "update schubert.auth_sessions",
            "insert into schubert.app_logs",
            "update schubert.request_inbox",
            "select user_id,context_hash",
            "close:select u.id",
            "null:owner",
            "null:session",
            "null:revoked",
            "null:timestamp",
            "null:hash")) {
      seed();
      try (var c = database.transaction()) {
        assertInfrastructure(
            () -> service(NOW).execute(fault(c, point), request(RAW, REQUEST), NOW));
        assertFalse(c.isClosed());
        c.rollback();
      }
      effects(0, 0, 0);
    }
    seed();
    var closed = new ResponseSnapshotCodec("s1", key(3), null, null);
    closed.close();
    var noSnapshot =
        new LogoutInboxService(
            new JdbcInboxCoordinator(keys),
            revocations,
            new LogoutReplayService(closed, hashes),
            hashes,
            Clock.fixed(NOW, ZoneOffset.UTC));
    try (var c = database.transaction()) {
      assertInfrastructure(() -> noSnapshot.execute(c, request(RAW, REQUEST), NOW));
      c.rollback();
    }
    effects(0, 0, 0);
    var closedKeys = new FingerprintKeyRing("f1", key(7), null, null);
    closedKeys.close();
    var noFingerprint =
        new LogoutInboxService(
            new JdbcInboxCoordinator(closedKeys),
            revocations,
            responses,
            hashes,
            Clock.fixed(NOW, ZoneOffset.UTC));
    try (var c = database.transaction()) {
      assertInfrastructure(() -> noFingerprint.execute(c, request(RAW, REQUEST), NOW));
      c.rollback();
    }
    call(service(NOW), request(RAW, REQUEST), NOW);
    var saved = saved();
    try (var rotated = new ResponseSnapshotCodec("s2", key(4), "s1", key(3));
        var rotatedFingerprint = new FingerprintKeyRing("f2", key(8), "f1", key(7));
        var c = database.transaction()) {
      var rotatedResponse = new LogoutReplayService(rotated, hashes);
      assertArrayEquals(
          golden("0200", RAW, REQUEST, new UUID(0, 5000), STAMP),
          rotatedResponse.restore(c, saved, 7, RAW, REQUEST, new UUID(0, 5000), NOW, true));
      assertEquals(
          "s2",
          rotatedResponse
              .captureSuccess(
                  new RevokedContext(new AuthContextIdentity(SESSION, 7), NOW, ResultCode.SUCCESS),
                  RAW,
                  REQUEST,
                  new UUID(0, 5000),
                  NOW)
              .responseSnapshot()
              .orElseThrow()
              .keyVersion());
      var service =
          new LogoutInboxService(
              new JdbcInboxCoordinator(rotatedFingerprint),
              revocations,
              rotatedResponse,
              hashes,
              Clock.fixed(NOW, ZoneOffset.UTC));
      assertEquals("0200", text(service.execute(c, request(RAW, REQUEST), NOW), 208, 4));
      var unavailable = new LogoutReplayService(closed, hashes);
      assertInfrastructure(
          () -> unavailable.restore(c, saved, 7, RAW, REQUEST, new UUID(0, 5000), NOW, true));
      c.rollback();
    }
    effects(1, 1, 1);
  }

  @Test
  void providerIllegalArgumentOwnerAndCloseRollbackAllEffects() throws Exception {
    // PT-AUT-LOGOUT-INBOX-007/YKT-162: a provider getter fault is not an absent owner.
    try (var c = database.transaction()) {
      assertInfrastructure(
          () ->
              service(NOW)
                  .execute(fault(c, "providerIaeOwnerAndRowClose"), request(RAW, REQUEST), NOW));
      assertFalse(c.isClosed());
      c.rollback();
    }
    effects(0, 0, 0);
  }

  @Test
  void nullAndWireBoundariesAreRejected() throws Exception {
    var inbox = new JdbcInboxCoordinator(keys);
    var clock = Clock.fixed(NOW, ZoneOffset.UTC);
    for (Executable input :
        List.<Executable>of(
            () -> LogoutApplicationAssembly.create(null, snapshots, clock),
            () -> LogoutApplicationAssembly.create(keys, null, clock),
            () -> LogoutApplicationAssembly.create(keys, snapshots, null),
            () -> new LogoutInboxService(null, revocations, responses, hashes, clock),
            () -> new LogoutInboxService(inbox, null, responses, hashes, clock),
            () -> new LogoutInboxService(inbox, revocations, null, hashes, clock),
            () -> new LogoutInboxService(inbox, revocations, responses, null, clock),
            () -> new LogoutInboxService(inbox, revocations, responses, hashes, null),
            () -> new LogoutInboxService(inbox, revocations, responses, hashes, clock, null),
            () -> new LogoutReplayService(null, hashes),
            () -> new LogoutReplayService(snapshots, null)))
      assertThrows(NullPointerException.class, input);
    var input = request(RAW, REQUEST);
    var service = service(NOW);
    var success = new RevokedContext(new AuthContextIdentity(SESSION, 7), NOW, ResultCode.SUCCESS);
    var saved = responses.captureSuccess(success, RAW, REQUEST, new UUID(0, 5000), NOW);
    try (var c = database.transaction()) {
      for (Executable missing :
          List.<Executable>of(
              () -> service.execute(null, input, NOW),
              () -> service.execute(c, null, NOW),
              () -> service.execute(c, input, null),
              () -> responses.captureSuccess(null, RAW, REQUEST, REQUEST, NOW),
              () -> responses.captureSuccess(success, null, REQUEST, REQUEST, NOW),
              () -> responses.captureSuccess(success, RAW, null, REQUEST, NOW),
              () -> responses.captureSuccess(success, RAW, REQUEST, null, NOW),
              () -> responses.captureSuccess(success, RAW, REQUEST, REQUEST, null),
              () -> responses.failure(null, RAW, REQUEST, REQUEST, NOW),
              () -> responses.restore(null, saved, 7, RAW, REQUEST, REQUEST, NOW, true),
              () -> responses.restore(c, null, 7, RAW, REQUEST, REQUEST, NOW, true),
              () -> responses.restore(c, saved, 7, null, REQUEST, REQUEST, NOW, true),
              () -> responses.restore(c, saved, 7, RAW, null, REQUEST, NOW, true),
              () -> responses.restore(c, saved, 7, RAW, REQUEST, null, NOW, true),
              () -> responses.restore(c, saved, 7, RAW, REQUEST, REQUEST, null, true)))
        assertThrows(NullPointerException.class, missing);
      var noId = new LogoutInboxService(inbox, revocations, responses, hashes, clock, () -> null);
      assertThrows(NullPointerException.class, () -> noId.execute(c, input, NOW));
      for (var code : ResultCode.values())
        if (code != ResultCode.SESSION_INVALID && code != ResultCode.TEMPORARY_FAILURE)
          assertThrows(
              IllegalArgumentException.class,
              () -> responses.failure(code, RAW, REQUEST, REQUEST, NOW));
      for (long owner : new long[] {0, 1_000_000_000_000L})
        assertThrows(
            IllegalArgumentException.class,
            () -> responses.captureDenied(owner, RAW, REQUEST, REQUEST, NOW));
      var header = input.header();
      var wrong =
          new CommonHeader(
              "SCHBNK01",
              1,
              new LayoutId("GAMREQ01"),
              1,
              MessageKind.REQUEST,
              InteractionKind.SYNCHRONOUS,
              REQUEST,
              REQUEST,
              header.sentAt(),
              Optional.of(RAW),
              256,
              0,
              0,
              0,
              256,
              Optional.empty());
      assertPermanent(() -> service.execute(c, new WireMessage<>(wrong, input.payload()), NOW));
      assertInfrastructure(() -> service.execute(c, input, NOW.plusNanos(1000)));
      c.rollback();
    }
    effects(0, 0, 0);
    try (var c = database.api()) {
      assertInfrastructure(() -> service.execute(c, input, NOW));
      assertInfrastructure(() -> restore(c, saved, 7));
    }
    var closed = database.api();
    closed.close();
    assertInfrastructure(() -> service.execute(closed, input, NOW));
  }

  @Test
  void assemblyUsesRealRevocationInboxReplayWithoutTakingKeyOwnership() throws Exception {
    // PT-AUT-LOGOUT-ASSEMBLY-001..003. Only generated UUID is read; expected body is UI234 literal.
    var application =
        LogoutApplicationAssembly.create(keys, snapshots, Clock.fixed(NOW, ZoneOffset.UTC));
    var input = request(RAW, REQUEST);
    byte[] initial = call(application, input, NOW);
    var firstId = UUID.fromString(text(initial, 24, 36));
    assertEquals(4, firstId.version());
    assertNotEquals(REQUEST, firstId);
    assertArrayEquals(golden("0000", RAW, REQUEST, firstId, STAMP), initial);
    effects(1, 1, 1);
    byte[] repeated = call(application, input, NOW);
    var secondId = UUID.fromString(text(repeated, 24, 36));
    assertNotEquals(firstId, secondId);
    assertArrayEquals(golden("0200", RAW, REQUEST, secondId, STAMP), repeated);
    effects(1, 1, 1);
    assertEquals(
        1, count("select count(*) from schubert.request_inbox where fingerprint_key_version='f1'"));
  }

  private static byte[] restore(Connection c, InboxCompletion saved, long owner) {
    return responses.restore(c, saved, owner, RAW, REQUEST, new UUID(0, 5000), NOW, true);
  }

  private static ResponseSnapshotIdentity identity(long owner) {
    return ResponseSnapshotIdentity.authenticated(REQUEST, "LOGRSP01", "001", owner);
  }

  private static InboxCompletion saved() throws SQLException {
    try (var c = database.api();
        var s = c.createStatement();
        var r =
            s.executeQuery(
                "select response_body_encrypted,response_key_version from schubert.request_inbox")) {
      assertTrue(r.next());
      return new InboxCompletion(
          InboxCompletionState.COMPLETED,
          InboxResultReference.authSession(SESSION),
          "LOGRSP01",
          "001",
          Optional.of(new EncryptedResponseSnapshot(r.getString(2), r.getBytes(1))),
          NOW);
    }
  }

  private static InboxCompletion copy(
      InboxCompletion old,
      InboxCompletionState state,
      InboxResultReference ref,
      String layout,
      String version,
      Optional<EncryptedResponseSnapshot> snapshot) {
    return new InboxCompletion(state, ref, layout, version, snapshot, old.completedAt());
  }

  private static InboxCompletion withBody(InboxCompletion saved, byte[] body) {
    return copy(
        saved,
        saved.state(),
        saved.resultReference(),
        "LOGRSP01",
        "001",
        Optional.of(snapshots.encrypt(identity(7), body)));
  }

  private static Connection fault(Connection connection, String point) {
    boolean nullValue = point.startsWith("null:");
    boolean close = point.startsWith("close:");
    boolean providerIae = point.equals("providerIaeOwnerAndRowClose");
    String match =
        providerIae
            ? "select u.id"
            : nullValue
                ? (point.equals("null:owner") ? "select u.id" : "select user_id,context_hash")
                : close ? point.substring(6) : point;
    return (Connection)
        Proxy.newProxyInstance(
            Connection.class.getClassLoader(),
            new Class<?>[] {Connection.class},
            (p, m, a) -> {
              if (m.getName().equals("prepareStatement") && ((String) a[0]).contains(match)) {
                if (!nullValue && !close && !providerIae)
                  throw new SQLException("synthetic-sensitive-SQL");
                Object statement = invoke(connection, m, a);
                return Proxy.newProxyInstance(
                    PreparedStatement.class.getClassLoader(),
                    new Class<?>[] {PreparedStatement.class},
                    (sp, sm, sa) -> {
                      Object result = invoke(statement, sm, sa);
                      if (close && sm.getName().equals("close"))
                        throw new SQLException("synthetic-sensitive-close");
                      if ((nullValue || providerIae) && sm.getName().equals("executeQuery"))
                        return Proxy.newProxyInstance(
                            ResultSet.class.getClassLoader(),
                            new Class<?>[] {ResultSet.class},
                            (rp, rm, ra) -> {
                              String column =
                                  switch (point) {
                                    case "null:owner" -> "id";
                                    case "null:session" -> "user_id";
                                    case "null:revoked" -> "revoked";
                                    case "null:timestamp" -> "revoked_at";
                                    default -> "context_hash";
                                  };
                              if (Set.of("getObject", "getString").contains(rm.getName())
                                  && column.equals(ra[0])
                                  && nullValue) return null;
                              if (providerIae
                                  && rm.getName().equals("getObject")
                                  && "id".equals(ra[0]))
                                throw new IllegalArgumentException(
                                    "synthetic-sensitive-provider-identity");
                              Object actual = invoke(result, rm, ra);
                              if (providerIae && rm.getName().equals("close"))
                                throw new SQLException("synthetic-sensitive-row-close");
                              return actual;
                            });
                      return result;
                    });
              }
              return invoke(connection, m, a);
            });
  }

  private static Object invoke(Object target, Method method, Object[] args) throws Throwable {
    try {
      return method.invoke(target, args);
    } catch (InvocationTargetException error) {
      throw error.getCause();
    }
  }

  private LogoutInboxService service(Instant at) {
    return new LogoutInboxService(
        new JdbcInboxCoordinator(keys),
        revocations,
        responses,
        hashes,
        Clock.fixed(at, ZoneOffset.UTC),
        () -> new UUID(0, ids.getAndIncrement()));
  }

  private static byte[] call(
      LogoutInboxService service, WireMessage<FixedPayload> input, Instant at) throws Exception {
    try (var c = database.transaction()) {
      try {
        byte[] result = service.execute(c, input, at);
        c.commit();
        return result;
      } catch (RuntimeException failure) {
        c.rollback();
        throw failure;
      }
    }
  }

  private static WireMessage<FixedPayload> request(AuthenticationContext raw, UUID id) {
    var header =
        new CommonHeader(
            "SCHBNK01",
            1,
            new LayoutId("LOGREQ01"),
            1,
            MessageKind.REQUEST,
            InteractionKind.SYNCHRONOUS,
            id,
            id,
            NOW.truncatedTo(ChronoUnit.MILLIS),
            Optional.of(raw),
            256,
            0,
            0,
            0,
            256,
            Optional.empty());
    return new WireMessage<>(header, new FixedPayload(new byte[0], 0, List.of()));
  }

  private static byte[] golden(
      String code, AuthenticationContext raw, UUID request, UUID response, String sent) {
    byte[] body = new byte[280];
    Arrays.fill(body, (byte) ' ');
    put(body, 0, "SCHBNK01001LOGRSP01001SS");
    put(body, 24, response.toString());
    put(body, 60, request.toString());
    put(body, 96, sent);
    put(body, 113, raw.wireValue());
    put(body, 177, "0256000024000000000000000000280");
    put(body, 208, code);
    put(body, 256, code.equals("0000") || code.equals("0200") ? STAMP : "00000000000000000");
    return body;
  }

  private static String fingerprint() throws Exception {
    var bytes = new ByteArrayOutputStream();
    var out = new DataOutputStream(bytes);
    out.write("SCHUBERT-NK-OP1".getBytes(StandardCharsets.US_ASCII));
    for (String item : List.of("7", "LOGREQ01", "001", "REQUEST:LOGREQ01")) {
      byte[] value = item.getBytes(StandardCharsets.UTF_8);
      out.writeInt(value.length);
      out.write(value);
    }
    out.writeInt(0);
    var mac = Mac.getInstance("HmacSHA256");
    mac.init(new SecretKeySpec(key(7), "HmacSHA256"));
    return HexFormat.of().formatHex(mac.doFinal(bytes.toByteArray()));
  }

  private static void effects(int inbox, int revoked, int audits) throws Exception {
    assertEquals(inbox, count("select count(*) from schubert.request_inbox"));
    assertEquals(revoked, count("select count(*) from schubert.auth_sessions where revoked"));
    assertEquals(audits, count("select count(*) from schubert.app_logs"));
    assertEquals(3, count("select count(*) from schubert.auth_sessions"));
  }

  private static int count(String sql) throws SQLException {
    try (var c = database.api();
        var s = c.createStatement();
        var r = s.executeQuery(sql)) {
      assertTrue(r.next());
      return r.getInt(1);
    }
  }

  private static void sql(String sql) throws SQLException {
    try (var c = database.api();
        var s = c.createStatement()) {
      s.executeUpdate(sql);
    }
  }

  private static byte[] key(int n) {
    byte[] k = new byte[32];
    Arrays.fill(k, (byte) n);
    return k;
  }

  private static void put(byte[] body, int at, String value) {
    byte[] b = value.getBytes(StandardCharsets.UTF_8);
    System.arraycopy(b, 0, body, at, b.length);
  }

  private static String text(byte[] body, int at, int length) {
    return new String(body, at, length, StandardCharsets.UTF_8);
  }

  private static void assertInfrastructure(Executable action) {
    var e = assertThrows(AuthenticationInfrastructureException.class, action);
    assertEquals("authentication storage is unavailable", e.getMessage());
    assertNull(e.getCause());
    assertEquals(0, e.getSuppressed().length);
  }

  private static void assertPermanent(Executable action) {
    var e = assertThrows(PermanentProtocolException.class, action);
    assertTrue(
        Set.of(
                "Logout request layout is invalid",
                "Logout request identity differs from its saved request")
            .contains(e.getMessage()));
    assertNull(e.getCause());
    assertEquals(0, e.getSuppressed().length);
  }
}
