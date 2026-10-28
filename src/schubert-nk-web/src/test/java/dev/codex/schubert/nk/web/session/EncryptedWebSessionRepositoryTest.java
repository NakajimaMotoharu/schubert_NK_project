package dev.codex.schubert.nk.web.session;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.layout.semantic.UserRole;
import dev.codex.schubert.nk.web.logging.WebLogDatabaseFixture;
import dev.codex.schubert.nk.web.security.SavedRequestTarget;
import java.io.ByteArrayOutputStream;
import java.io.DataOutputStream;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Proxy;
import java.nio.ByteBuffer;
import java.nio.charset.StandardCharsets;
import java.nio.file.Path;
import java.security.MessageDigest;
import java.security.ProviderException;
import java.security.SecureRandom;
import java.security.Security;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.time.Clock;
import java.time.Instant;
import java.time.ZoneId;
import java.time.ZoneOffset;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Base64;
import java.util.HashSet;
import java.util.HexFormat;
import java.util.List;
import java.util.Objects;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.Callable;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ConcurrentMap;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.Executors;
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

/**
 * NK-WEB-001/PT-WEB-036..043; FUN-001/AUT-001..004; UI226; SS314/331/352;
 * SSC-041/PG-D-098/BUG-057/YKT-052. Isolated synthetic DB and public JDBC fault boundaries.
 */
class EncryptedWebSessionRepositoryTest {
  private static final String FIXTURE_STATEMENT_EXECUTEUPDATE_84172022 = "statement.executeUpdate";
  private static final String FIXTURE_CONNECTION_COMMIT_37C1B216 = "connection.commit";
  private static final String FIXTURE_GET_04F32A7E = "GET";
  private static final String FIXTURE_LOGS_910E2326 = "/logs";
  private static final Instant NOW = Instant.parse("2026-09-08T00:00:00.123456Z");
  private static WebLogDatabaseFixture db;
  private static final SessionPrincipal PRINCIPAL =
      new SessionPrincipal(
          "reader",
          UserRole.ADMIN,
          AuthenticationContext.of("b".repeat(64)),
          Instant.parse("2026-09-08T00:00:00Z"));

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
    try (var c = db.web();
        var s = c.createStatement()) {
      s.executeUpdate("delete from schubert_web_session.web_http_sessions");
    }
  }

  @Test
  void web036CreateReadRestartAndIdleAreEncrypted() throws Exception {
    try (var f = new Fixture()) {
      f.clock.value = NOW.plusNanos(789);
      var created = f.repository.create();
      assertEquals(raw(1), created.sessionId().cookieValue());
      assertEquals(new UUID(0, 1), created.row().identity().id());
      assertEquals(independentHash(raw(1)), created.row().identity().sessionIdHash());
      assertEquals(NOW, created.row().identity().createdAt());
      assertEquals(NOW, created.row().lastAccessedAt());
      assertEquals(NOW.plusSeconds(28800), created.row().expiresAt());
      assertEquals(28800, created.row().maxInactiveSeconds());
      assertEquals(0, created.row().version());
      assertEquals(json(false, "02".repeat(32), null, 0), storedJson(created, new byte[32]));
      assertTrue(created.attributes().principal().isEmpty());
      f.clock.value = NOW.plusSeconds(3600).plusNanos(789);
      var read = f.repository.find(created.sessionId()).orElseThrow();
      assertEquals(NOW.plusSeconds(3600), read.row().lastAccessedAt());
      assertEquals(NOW.plusSeconds(32400), read.row().expiresAt());
      assertEquals(1, read.row().version());
      f.clock.value = NOW.plusSeconds(10);
      var backward = f.repository.find(created.sessionId()).orElseThrow();
      assertEquals(read.row().lastAccessedAt(), backward.row().lastAccessedAt());
      assertEquals(read.row().expiresAt(), backward.row().expiresAt());
      byte[] newKey = new byte[32];
      Arrays.fill(newKey, (byte) 1);
      try (var rotated = new SessionPayloadCodec("v3", newKey, "v2", new byte[32])) {
        var restarted = new EncryptedWebSessionRepository(f.source, rotated, f.clock);
        var restored = restarted.find(created.sessionId()).orElseThrow();
        assertEquals("v3", restored.row().payload().keyVersion());
        assertEquals(created.row().identity(), restored.row().identity());
        assertEquals(json(false, "02".repeat(32), null, 0), storedJson(restored, newKey));
      }
      assertEquals(0, f.live.get());
    }
  }

  @Test
  void web037ExpiryAndCorruptRowsCommitInvalidation() throws Exception {
    try (var fixture = new Fixture()) {
      var created = fixture.repository.create();
      try (var c = db.web();
          var s =
              c.prepareStatement(
                  "update schubert_web_session.web_http_sessions set attributes_ciphertext=? where id=?")) {
        s.setBytes(1, new byte[16437]);
        s.setObject(2, created.row().identity().id());
        assertEquals(1, s.executeUpdate());
      }
      fixture.deleteCount = 0;
      unavailable(() -> fixture.repository.find(created.sessionId()));
      assertEquals(1, count());
      fixture.deleteCount = null;
      for (String fault :
          List.of(FIXTURE_STATEMENT_EXECUTEUPDATE_84172022, FIXTURE_CONNECTION_COMMIT_37C1B216)) {
        fixture.failure = fault;
        unavailable(() -> fixture.repository.find(created.sessionId()));
        assertTrue(fixture.hit);
        assertEquals(1, count());
        fixture.failure = "";
      }
      assertTrue(fixture.repository.find(created.sessionId()).isEmpty());
      assertEquals(0, count());
    }
    for (long offset : new long[] {-1000, 0, 1000}) {
      reset();
      try (var f = new Fixture()) {
        var created = f.repository.create();
        f.clock.value = created.row().expiresAt().plusNanos(offset);
        var read = f.repository.find(created.sessionId());
        assertEquals(offset < 0, read.isPresent());
        assertEquals(offset < 0 ? 1 : 0, count());
        if (read.isPresent())
          assertEquals(f.clock.value.plusSeconds(28800), read.orElseThrow().row().expiresAt());
      }
    }
    for (int corruption = 0; corruption < 6; corruption++) {
      reset();
      try (var f = new Fixture()) {
        var original = f.repository.create();
        var neighbour = f.repository.create();
        byte[] envelope = original.row().payload().ciphertext();
        String version = "v2";
        if (corruption == 0) envelope = new byte[64];
        if (corruption == 1) envelope[envelope.length - 1] ^= 1;
        if (corruption == 2) {
          envelope[9] = '0';
          version = "v0";
        }
        if (corruption == 3)
          envelope =
              independentEnvelope(
                  original,
                  "{\"formatVersion\":1,\"operationTokens\":[],\"password\":\"private-marker\"}");
        if (corruption == 4) f.nullColumn = "key_version";
        try (var c = db.web();
            var s =
                c.prepareStatement(
                    "update schubert_web_session.web_http_sessions set attributes_ciphertext=?,key_version=? where id=?")) {
          s.setBytes(1, envelope);
          s.setString(2, version);
          s.setObject(3, original.row().identity().id());
          assertEquals(1, s.executeUpdate());
        }
        if (corruption == 5) {
          try (var c = db.web();
              var s =
                  c.prepareStatement(
                      "update schubert_web_session.web_http_sessions set created_at=created_at-interval '1 microsecond' where id=?")) {
            s.setObject(1, original.row().identity().id());
            assertEquals(1, s.executeUpdate());
          }
        }
        f.deleteCount = 0;
        unavailable(() -> f.repository.find(original.sessionId()));
        assertEquals(2, count());
        f.deleteCount = null;
        f.failure = FIXTURE_CONNECTION_COMMIT_37C1B216;
        unavailable(() -> f.repository.find(original.sessionId()));
        assertEquals(2, count());
        f.failure = "";
        assertTrue(f.repository.find(original.sessionId()).isEmpty());
        f.nullColumn = "";
        assertEquals(1, count());
        assertTrue(f.repository.find(neighbour.sessionId()).isPresent());
      }
    }
  }

  @Test
  void web295ProviderGetterFailureRollsBackWithoutDeletingSession() throws Exception {
    try (var fixture = new Fixture()) {
      var created = fixture.repository.create();
      fixture.runtimeFailure = "result.getObject";
      unavailable(() -> fixture.repository.find(created.sessionId()));
      assertTrue(fixture.runtimeHit);
      assertEquals(1, fixture.rollbacks.get());
      assertEquals(1, count());
      fixture.runtimeFailure = "";
      assertTrue(fixture.repository.find(created.sessionId()).isPresent());
    }
  }

  @Test
  void web297MalformedRowAndResultCloseFailureRollsBackWithoutDeletingSession() throws Exception {
    try (var fixture = new Fixture()) {
      var created = fixture.repository.create();
      int committedBefore = fixture.commits.get();
      fixture.nullColumn = "id";
      fixture.failure = "result.close";
      unavailable(() -> fixture.repository.find(created.sessionId()));
      assertTrue(fixture.hit);
      assertEquals(1, fixture.rollbacks.get());
      assertEquals(committedBefore, fixture.commits.get());
      assertEquals(1, count());
      fixture.nullColumn = "";
      fixture.failure = "";
      assertTrue(fixture.repository.find(created.sessionId()).isPresent());
    }
  }

  @Test
  void web038MutationPreservesCurrentAttributesAndSecurityIdentity() throws Exception {
    try (var f = new Fixture()) {
      var created = f.repository.create();
      var updated =
          f.repository
              .mutate(
                  created.sessionId(),
                  current ->
                      new SessionAttributes(
                          current.principal(),
                          current.csrfToken(),
                          Optional.of(
                              SavedRequestTarget.fromGet(
                                  FIXTURE_GET_04F32A7E, FIXTURE_LOGS_910E2326)),
                          SessionAttributeCodecTest.tokens(10)))
              .orElseThrow();
      assertEquals(
          json(false, "02".repeat(32), FIXTURE_LOGS_910E2326, 10),
          storedJson(updated, new byte[32]));
      unavailable(() -> f.repository.mutate(created.sessionId(), current -> null));
      unavailable(
          () ->
              f.repository.mutate(
                  created.sessionId(),
                  current ->
                      new SessionAttributes(
                          Optional.of(PRINCIPAL),
                          current.csrfToken(),
                          current.savedRequest(),
                          current.operationTokens())));
      unavailable(
          () ->
              f.repository.mutate(
                  created.sessionId(),
                  current ->
                      new SessionAttributes(
                          current.principal(),
                          Optional.empty(),
                          current.savedRequest(),
                          current.operationTokens())));
      unavailable(
          () ->
              f.repository.mutate(
                  created.sessionId(),
                  current ->
                      new SessionAttributes(
                          current.principal(),
                          current.csrfToken(),
                          current.savedRequest(),
                          SessionAttributeCodecTest.tokens(11))));
      var after = f.repository.find(created.sessionId()).orElseThrow();
      assertEquals(
          json(false, "02".repeat(32), FIXTURE_LOGS_910E2326, 10), storedJson(after, new byte[32]));
      f.repository.invalidate(created.sessionId());
      f.repository.invalidate(created.sessionId());
      assertTrue(
          f.repository
              .mutate(
                  created.sessionId(),
                  current -> {
                    throw new AssertionError("missing row callback");
                  })
              .isEmpty());
      assertTrue(f.repository.authenticate(created.sessionId(), PRINCIPAL).isEmpty());
      assertTrue(f.repository.find(created.sessionId()).isEmpty());
      assertEquals(0, count());
    }
  }

  @Test
  void web039LoginFixationIsAtomicAndPreservesAllowlist() throws Exception {
    try (var f = new Fixture()) {
      var created = f.repository.create();
      f.repository.mutate(
          created.sessionId(),
          current ->
              new SessionAttributes(
                  current.principal(),
                  current.csrfToken(),
                  Optional.of(
                      SavedRequestTarget.fromGet(FIXTURE_GET_04F32A7E, FIXTURE_LOGS_910E2326)),
                  SessionAttributeCodecTest.tokens(2)));
      f.clock.value = NOW.plusSeconds(1);
      var authenticated = f.repository.authenticate(created.sessionId(), PRINCIPAL).orElseThrow();
      assertEquals(raw(3), authenticated.sessionId().cookieValue());
      assertEquals(new UUID(0, 2), authenticated.row().identity().id());
      assertEquals(NOW.plusSeconds(1), authenticated.row().identity().createdAt());
      assertEquals(NOW.plusSeconds(28801), authenticated.row().expiresAt());
      assertEquals(
          json(true, "04".repeat(32), FIXTURE_LOGS_910E2326, 2),
          storedJson(authenticated, new byte[32]));
      assertEquals(PRINCIPAL, authenticated.attributes().principal().orElseThrow());
      assertTrue(f.repository.find(created.sessionId()).isEmpty());
      assertEquals(1, count());
    }
    for (int collision = 0; collision < 4; collision++) {
      reset();
      try (var f = new Fixture()) {
        var original = f.repository.create();
        if (collision == 0) f.random.fixed = 1;
        if (collision == 1) f.ids.set(0);
        if (collision == 2) f.random.fixed = 2;
        if (collision == 3) {
          f.repository.create();
          f.ids.set(1);
        }
        unavailable(() -> f.repository.authenticate(original.sessionId(), PRINCIPAL));
        assertEquals(collision == 3 ? 2 : 1, count());
        assertEquals(json(false, "02".repeat(32), null, 0), storedJson(original, new byte[32]));
      }
    }
    reset();
    try (var f = new Fixture()) {
      var original = f.repository.create();
      try (var c = db.web();
          var s =
              c.prepareStatement(
                  "update schubert_web_session.web_http_sessions set attributes_ciphertext=? where id=?")) {
        s.setBytes(1, independentEnvelope(original, json(false, null, FIXTURE_LOGS_910E2326, 2)));
        s.setObject(2, original.row().identity().id());
        assertEquals(1, s.executeUpdate());
      }
      var authenticated = f.repository.authenticate(original.sessionId(), PRINCIPAL).orElseThrow();
      assertEquals(
          json(true, "04".repeat(32), FIXTURE_LOGS_910E2326, 2),
          storedJson(authenticated, new byte[32]));
      assertTrue(f.repository.find(original.sessionId()).isEmpty());
    }
  }

  @Test
  void web040VersionRolloverPreservesCookieAndRejectsOldPk() throws Exception {
    try (var f = new Fixture()) {
      var original = f.repository.create();
      setVersion(original, 999999999);
      f.ids.set(0);
      unavailable(() -> f.repository.find(original.sessionId()));
      assertEquals(1, count());
      f.ids.set(1);
      var neighbour = f.repository.create();
      f.ids.set(1);
      unavailable(() -> f.repository.find(original.sessionId()));
      assertEquals(2, count());
      assertEquals(json(false, "04".repeat(32), null, 0), storedJson(neighbour, new byte[32]));
      f.repository.invalidate(neighbour.sessionId());
      f.ids.set(1);
      var rollover = f.repository.find(original.sessionId()).orElseThrow();
      assertEquals(new UUID(0, 2), rollover.row().identity().id());
      assertEquals(raw(1), rollover.sessionId().cookieValue());
      assertEquals(NOW, rollover.row().identity().createdAt());
      assertEquals(0, rollover.row().version());
      assertEquals(json(false, "02".repeat(32), null, 0), storedJson(rollover, new byte[32]));
      try (var c = db.transaction()) {
        var old = original.row();
        var stale =
            new WebSessionRow(
                old.identity(), old.payload(), old.lastAccessedAt(), old.expiresAt(), 28800, 1);
        assertFalse(new JdbcWebSessionStore().replace(c, old, stale));
        c.commit();
      }
      assertEquals(1, count());
    }
  }

  @Test
  void web041DatabaseCryptoAndCommitFailuresNeverGrantSession() throws Exception {
    for (int operation = 0; operation < 5; operation++) {
      final int op = operation;
      var methods =
          new ArrayList<>(
              List.of(
                  "open",
                  "connection.setAutoCommit",
                  "connection.setReadOnly",
                  "connection.prepareStatement",
                  "statement.setString",
                  FIXTURE_STATEMENT_EXECUTEUPDATE_84172022,
                  "statement.close",
                  FIXTURE_CONNECTION_COMMIT_37C1B216,
                  "connection.close"));
      if (op > 0 && op < 4)
        methods.addAll(
            List.of("statement.executeQuery", "result.next", "result.getObject", "result.close"));
      for (String method : methods) {
        reset();
        try (var f = new Fixture()) {
          var original = f.repository.create();
          f.failure = method;
          unavailable(() -> lifecycleCall(op, f, original.sessionId()));
          assertTrue(f.hit, method);
          assertEquals(0, f.live.get());
          f.failure = "";
          boolean committedClose = method.equals("connection.close");
          assertEquals(committedClose && op == 0 ? 2 : committedClose && op == 4 ? 0 : 1, count());
          if (op != 3 || !committedClose) {
            assertEquals(
                !(op == 4 && committedClose), f.repository.find(original.sessionId()).isPresent());
          } else assertTrue(f.repository.find(original.sessionId()).isEmpty());
        }
      }
    }
    reset();
    try (var f = new Fixture()) {
      var original = f.repository.create();
      f.nullConnection = true;
      unavailable(f.repository::create);
      f.nullConnection = false;
      f.failure = FIXTURE_STATEMENT_EXECUTEUPDATE_84172022;
      f.rollbackFailure = true;
      unavailable(() -> f.repository.find(original.sessionId()));
      assertTrue(f.rollbackHit);
      assertEquals(1, count());
      f.failure = "";
      f.rollbackFailure = false;
      f.updateCount = 0;
      unavailable(() -> f.repository.find(original.sessionId()));
      unavailable(() -> f.repository.mutate(original.sessionId(), current -> current));
      f.updateCount = null;
      f.deleteCount = 0;
      unavailable(() -> f.repository.authenticate(original.sessionId(), PRINCIPAL));
      setVersion(original, 999999999);
      unavailable(() -> f.repository.find(original.sessionId()));
      f.clock.value = NOW.plusSeconds(28800);
      unavailable(() -> f.repository.find(original.sessionId()));
      f.clock.value = NOW;
      f.deleteCount = null;
      setVersion(original, 0);
      for (int bad : new int[] {-1, 2}) {
        f.deleteCount = bad;
        unavailable(() -> f.repository.invalidate(original.sessionId()));
      }
      f.deleteCount = null;
      f.random.fail = true;
      unavailable(f.repository::create);
      unavailable(() -> f.repository.authenticate(original.sessionId(), PRINCIPAL));
      f.random.fail = false;
      f.clock.value = null;
      unavailable(f.repository::create);
      unavailable(() -> f.repository.find(original.sessionId()));
      f.clock.value = NOW;
      var nullId =
          new EncryptedWebSessionRepository(f.source, f.codec, f.clock, f.random, () -> null);
      unavailable(nullId::create);
      unavailable(() -> nullId.authenticate(original.sessionId(), PRINCIPAL));
      setVersion(original, 999999999);
      unavailable(() -> nullId.find(original.sessionId()));
      setVersion(original, 0);
      var provider = Security.getProvider("SUN");
      int position = Arrays.asList(Security.getProviders()).indexOf(provider) + 1;
      assertTrue(position > 0);
      Security.removeProvider("SUN");
      try {
        unavailable(() -> f.repository.find(original.sessionId()));
      } finally {
        assertNotEquals(-1, Security.insertProviderAt(provider, position));
      }
      f.codec.close();
      unavailable(f.repository::create);
      unavailable(() -> f.repository.find(original.sessionId()));
      assertEquals(1, count());
    }
  }

  @Test
  void web042NullConfigurationAndIdentityInvariants() throws Exception {
    try (var f = new Fixture()) {
      assertThrows(
          NullPointerException.class,
          () -> new EncryptedWebSessionRepository(null, f.codec, f.clock));
      assertThrows(
          NullPointerException.class,
          () -> new EncryptedWebSessionRepository(f.source, null, f.clock));
      assertThrows(
          NullPointerException.class,
          () -> new EncryptedWebSessionRepository(f.source, f.codec, null));
      assertThrows(
          NullPointerException.class,
          () ->
              new EncryptedWebSessionRepository(
                  f.source, f.codec, f.clock, null, UUID::randomUUID));
      assertThrows(
          NullPointerException.class,
          () -> new EncryptedWebSessionRepository(f.source, f.codec, f.clock, f.random, null));
      assertThrows(NullPointerException.class, () -> f.repository.find(null));
      assertThrows(NullPointerException.class, () -> f.repository.mutate(null, current -> current));
      assertThrows(NullPointerException.class, () -> f.repository.authenticate(null, PRINCIPAL));
      assertThrows(NullPointerException.class, () -> f.repository.invalidate(null));
      var original = f.repository.create();
      assertThrows(
          NullPointerException.class, () -> f.repository.mutate(original.sessionId(), null));
      assertThrows(
          NullPointerException.class, () -> f.repository.authenticate(original.sessionId(), null));
      assertThrows(
          NullPointerException.class,
          () -> new WebSessionSnapshot(null, original.row(), original.attributes()));
      assertThrows(
          NullPointerException.class,
          () -> new WebSessionSnapshot(original.sessionId(), null, original.attributes()));
      assertThrows(
          NullPointerException.class,
          () -> new WebSessionSnapshot(original.sessionId(), original.row(), null));
      assertThrows(
          IllegalArgumentException.class,
          () ->
              new WebSessionSnapshot(
                  WebSessionId.parse(raw(2)), original.row(), original.attributes()));
      assertEquals("WebSessionSnapshot[REDACTED]", original.toString());
      var store = new JdbcWebSessionStore();
      assertThrows(NullPointerException.class, () -> store.deleteByHash(null, "a".repeat(64)));
      try (var c = db.transaction()) {
        assertThrows(NullPointerException.class, () -> store.deleteByHash(c, null));
        assertThrows(IllegalArgumentException.class, () -> store.deleteByHash(c, "bad"));
      }
    }
  }

  @Test
  void web043ConcurrentReadMutateInvalidateNeverResurrect() throws Exception {
    try (var f = new Fixture();
        var pool = Executors.newFixedThreadPool(10)) {
      var original = f.repository.create();
      f.repository.mutate(
          original.sessionId(),
          current ->
              new SessionAttributes(
                  current.principal(),
                  current.csrfToken(),
                  Optional.of(SavedRequestTarget.fromGet(FIXTURE_GET_04F32A7E, "/logs?n=0")),
                  current.operationTokens()));
      var jobs = new ArrayList<Callable<Void>>();
      for (int i = 0; i < 100; i++)
        jobs.add(
            () -> {
              assertTrue(
                  f.repository
                      .mutate(
                          original.sessionId(),
                          current -> {
                            int previous =
                                Integer.parseInt(
                                    current.savedRequest().orElseThrow().location().substring(8));
                            return new SessionAttributes(
                                current.principal(),
                                current.csrfToken(),
                                Optional.of(
                                    SavedRequestTarget.fromGet(
                                        FIXTURE_GET_04F32A7E, "/logs?n=" + (previous + 1))),
                                current.operationTokens());
                          })
                      .isPresent());
              return null;
            });
      for (var future : pool.invokeAll(jobs)) future.get(30, TimeUnit.SECONDS);
      var finalState = f.repository.find(original.sessionId()).orElseThrow();
      assertEquals("/logs?n=100", finalState.attributes().savedRequest().orElseThrow().location());
      assertEquals(102, finalState.row().version());
      var tokens = SessionAttributeCodecTest.tokens(10);
      for (boolean add : new boolean[] {true, false}) {
        var tokenJobs = new ArrayList<Callable<Void>>();
        for (var token : tokens)
          tokenJobs.add(
              () -> {
                assertTrue(
                    f.repository
                        .mutate(
                            original.sessionId(),
                            current -> {
                              var changed = new ArrayList<>(current.operationTokens());
                              if (add) changed.add(token);
                              else assertTrue(changed.remove(token));
                              return new SessionAttributes(
                                  current.principal(),
                                  current.csrfToken(),
                                  current.savedRequest(),
                                  changed);
                            })
                        .isPresent());
                return null;
              });
        for (var future : pool.invokeAll(tokenJobs)) future.get(30, TimeUnit.SECONDS);
        var observed = f.repository.find(original.sessionId()).orElseThrow();
        assertEquals(
            add ? new HashSet<>(tokens) : Set.of(),
            new HashSet<>(observed.attributes().operationTokens()));
        assertEquals(add ? 10 : 0, observed.attributes().operationTokens().size());
        assertEquals("/logs?n=100", observed.attributes().savedRequest().orElseThrow().location());
        assertEquals("02".repeat(32), observed.attributes().csrfToken().orElseThrow());
        assertTrue(observed.attributes().principal().isEmpty());
      }
      var racers = new ArrayList<Callable<Void>>();
      for (int i = 0; i < 30; i++) {
        final int n = i;
        racers.add(
            () -> {
              if (n % 3 == 0) f.repository.invalidate(original.sessionId());
              else if (n % 3 == 1) f.repository.find(original.sessionId());
              else f.repository.mutate(original.sessionId(), current -> current);
              return null;
            });
      }
      for (var future : pool.invokeAll(racers)) future.get(30, TimeUnit.SECONDS);
      assertTrue(f.repository.find(original.sessionId()).isEmpty());
      assertEquals(0, count());
    }
  }

  private static String raw(int value) {
    byte[] bytes = new byte[32];
    Arrays.fill(bytes, (byte) value);
    return Base64.getUrlEncoder().withoutPadding().encodeToString(bytes);
  }

  private static String independentHash(String raw) throws Exception {
    return HexFormat.of()
        .formatHex(
            MessageDigest.getInstance("SHA-256").digest(raw.getBytes(StandardCharsets.US_ASCII)));
  }

  private static String json(boolean principal, String csrf, String saved, int tokens) {
    return SessionAttributeCodecTest.json(principal, "reader", "ADMIN", csrf, saved, tokens);
  }

  private static String storedJson(WebSessionSnapshot expected, byte[] key) throws Exception {
    byte[] envelope;
    try (var c = db.web();
        var s =
            c.prepareStatement(
                "select attributes_ciphertext,key_version from schubert_web_session.web_http_sessions where id=?")) {
      s.setObject(1, expected.row().identity().id());
      try (var result = s.executeQuery()) {
        assertTrue(result.next());
        envelope = result.getBytes(1);
        assertEquals(expected.row().payload().keyVersion(), result.getString(2));
        assertFalse(result.next());
      }
    }
    assertArrayEquals(expected.row().payload().ciphertext(), envelope);
    assertEquals("NKENC1", new String(envelope, 0, 6, StandardCharsets.US_ASCII));
    assertEquals(1, envelope[6]);
    int length = Byte.toUnsignedInt(envelope[7]);
    String version = new String(envelope, 8, length, StandardCharsets.US_ASCII);
    Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding");
    cipher.init(
        Cipher.DECRYPT_MODE,
        new SecretKeySpec(key, "AES"),
        new GCMParameterSpec(128, Arrays.copyOfRange(envelope, 8 + length, 20 + length)));
    cipher.updateAAD(independentAad(expected, version));
    return new String(
        cipher.doFinal(envelope, 20 + length, envelope.length - 20 - length),
        StandardCharsets.UTF_8);
  }

  private static byte[] independentAad(WebSessionSnapshot expected, String version)
      throws Exception {
    var identity = expected.row().identity();
    var out = new ByteArrayOutputStream();
    try (var data = new DataOutputStream(out)) {
      for (byte[] field :
          List.of(
              "web-session".getBytes(StandardCharsets.US_ASCII),
              "schubert_web_session.web_http_sessions".getBytes(StandardCharsets.US_ASCII),
              HexFormat.of().parseHex(identity.id().toString().replace("-", "")),
              independentHash(expected.sessionId().cookieValue())
                  .getBytes(StandardCharsets.US_ASCII),
              ByteBuffer.allocate(12)
                  .putLong(identity.createdAt().getEpochSecond())
                  .putInt(identity.createdAt().getNano())
                  .array(),
              new byte[] {1},
              version.getBytes(StandardCharsets.US_ASCII))) {
        data.writeInt(field.length);
        data.write(field);
      }
    }
    return out.toByteArray();
  }

  private static byte[] independentEnvelope(WebSessionSnapshot expected, String json)
      throws Exception {
    Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding");
    byte[] nonce = new byte[12];
    cipher.init(
        Cipher.ENCRYPT_MODE,
        new SecretKeySpec(new byte[32], "AES"),
        new GCMParameterSpec(128, nonce));
    cipher.updateAAD(independentAad(expected, "v2"));
    var out = new ByteArrayOutputStream();
    out.write("NKENC1".getBytes(StandardCharsets.US_ASCII));
    out.write(1);
    out.write(2);
    out.write("v2".getBytes(StandardCharsets.US_ASCII));
    out.write(nonce);
    out.write(cipher.doFinal(json.getBytes(StandardCharsets.UTF_8)));
    return out.toByteArray();
  }

  private static void lifecycleCall(int op, Fixture fixture, WebSessionId id) {
    switch (op) {
      case 0 -> fixture.repository.create();
      case 1 -> fixture.repository.find(id);
      case 2 -> fixture.repository.mutate(id, current -> current);
      case 3 -> fixture.repository.authenticate(id, PRINCIPAL);
      case 4 -> fixture.repository.invalidate(id);
      default -> throw new AssertionError("unknown operation");
    }
  }

  private static void setVersion(WebSessionSnapshot snapshot, long version) throws Exception {
    try (var c = db.web();
        var s =
            c.prepareStatement(
                "update schubert_web_session.web_http_sessions set version=? where id=?")) {
      s.setLong(1, version);
      s.setObject(2, snapshot.row().identity().id());
      assertEquals(1, s.executeUpdate());
    }
  }

  private static int count() throws Exception {
    try (var c = db.web();
        var s = c.createStatement();
        var r = s.executeQuery("select count(*) from schubert_web_session.web_http_sessions")) {
      assertTrue(r.next());
      return r.getInt(1);
    }
  }

  private static void unavailable(org.junit.jupiter.api.function.Executable action) {
    var error = assertThrows(SessionStoreException.class, action);
    assertEquals("session storage is unavailable", error.getMessage());
    assertNull(error.getCause());
    assertEquals(0, error.getSuppressed().length);
  }

  @Test
  void bizOwnership001FixtureDistinguishesSendingThreadFromOtherBorrowers() throws Exception {
    try (var fixture = new Fixture();
        var executor = Executors.newSingleThreadExecutor()) {
      var opened = new CountDownLatch(1);
      var release = new CountDownLatch(1);
      var peer =
          executor.submit(
              () -> {
                try (var connection = fixture.source.getConnection()) {
                  assertFalse(connection.isClosed());
                  assertEquals(1, fixture.threadLive.getOrDefault(Thread.currentThread(), 0));
                  opened.countDown();
                  assertTrue(release.await(10, TimeUnit.SECONDS));
                }
                assertEquals(0, fixture.threadLive.getOrDefault(Thread.currentThread(), 0));
                return null;
              });
      try {
        assertTrue(opened.await(10, TimeUnit.SECONDS));
        assertEquals(1, fixture.live.get());
        assertEquals(0, fixture.threadLive.getOrDefault(Thread.currentThread(), 0));
        try (var connection = fixture.source.getConnection()) {
          assertFalse(connection.isClosed());
          assertEquals(2, fixture.live.get());
          assertEquals(1, fixture.threadLive.getOrDefault(Thread.currentThread(), 0));
        }
        assertEquals(1, fixture.live.get());
        assertEquals(0, fixture.threadLive.getOrDefault(Thread.currentThread(), 0));
      } finally {
        release.countDown();
      }
      peer.get(10, TimeUnit.SECONDS);
      assertEquals(0, fixture.live.get());
      assertTrue(fixture.threadLive.isEmpty());
    }
  }

  static final class Fixture implements AutoCloseable {
    private final WebLogDatabaseFixture database;

    Fixture() {
      this(db);
    }

    Fixture(WebLogDatabaseFixture database) {
      this.database = database;
    }

    final SessionPayloadCodec codec = new SessionPayloadCodec("v2", new byte[32], null, null);
    final MutableClock clock = new MutableClock();
    final SequenceRandom random = new SequenceRandom();
    final AtomicLong ids = new AtomicLong();
    final AtomicInteger live = new AtomicInteger();
    final AtomicInteger commits = new AtomicInteger();
    final AtomicInteger rollbacks = new AtomicInteger();
    final ConcurrentMap<Thread, Integer> threadLive = new ConcurrentHashMap<>();
    volatile String failure = "";
    volatile String runtimeFailure = "";
    String nullColumn = "";
    Integer deleteCount;
    Integer updateCount;
    boolean nullConnection;
    boolean hit;
    boolean rollbackFailure;
    boolean rollbackHit;
    boolean runtimeHit;
    final DataSource source =
        DataSource.class.cast(
            Proxy.newProxyInstance(
                DataSource.class.getClassLoader(),
                new Class<?>[] {DataSource.class},
                (proxy, method, args) -> {
                  if (!method.getName().equals("getConnection"))
                    throw new AssertionError("unexpected DataSource call");
                  if (failure.equals("open")) {
                    hit = true;
                    throw new SQLException("private-open-marker");
                  }
                  if (nullConnection) return null;
                  live.incrementAndGet();
                  threadLive.merge(Thread.currentThread(), 1, Integer::sum);
                  return wrap(Connection.class, openDatabase(), "connection", "");
                }));
    final EncryptedWebSessionRepository repository =
        new EncryptedWebSessionRepository(
            source, codec, clock, random, () -> new java.util.UUID(0, ids.incrementAndGet()));

    private Connection openDatabase() throws Exception {
      return database.web();
    }

    private <T> T wrap(Class<T> type, T target, String kind, String sql) {
      return type.cast(
          Proxy.newProxyInstance(
              type.getClassLoader(),
              new Class<?>[] {type},
              (proxy, method, args) -> {
                String name = kind + "." + method.getName();
                if (name.equals(FIXTURE_CONNECTION_COMMIT_37C1B216)) commits.incrementAndGet();
                if (name.equals("connection.rollback")) rollbacks.incrementAndGet();
                if (name.equals("connection.close")) {
                  live.decrementAndGet();
                  threadLive.compute(
                      Thread.currentThread(),
                      (thread, count) -> {
                        if (count == null)
                          throw new AssertionError("unowned fixture connection close");
                        return count == 1 ? null : count - 1;
                      });
                }
                if (name.equals("connection.rollback") && rollbackFailure) {
                  rollbackHit = true;
                  throw new SQLException("private-rollback-marker");
                }
                if (name.equals(runtimeFailure)) {
                  runtimeHit = true;
                  throw new IllegalArgumentException("private-provider-marker");
                }
                if (name.equals(failure)) {
                  hit = true;
                  if (method.getName().equals("close")) method.invoke(target, args);
                  throw new SQLException("private-jdbc-marker");
                }
                if (name.equals(FIXTURE_STATEMENT_EXECUTEUPDATE_84172022)
                    && sql.startsWith("delete ")
                    && deleteCount != null) return deleteCount;
                if (name.equals(FIXTURE_STATEMENT_EXECUTEUPDATE_84172022)
                    && sql.startsWith("update ")
                    && updateCount != null) return updateCount;
                if (kind.equals("result")
                    && method.getName().startsWith("get")
                    && args != null
                    && args.length > 0
                    && nullColumn.equals(args[0])) return null;
                try {
                  Object value = method.invoke(target, args);
                  if (value instanceof PreparedStatement statement)
                    return wrap(PreparedStatement.class, statement, "statement", (String) args[0]);
                  if (value instanceof ResultSet result)
                    return wrap(ResultSet.class, result, "result", sql);
                  return value;
                } catch (InvocationTargetException failure) {
                  throw Objects.requireNonNull(failure.getCause());
                }
              }));
    }

    @Override
    public void close() {
      codec.close();
      assertEquals(0, live.get());
    }
  }

  static final class MutableClock extends Clock {
    Instant value = NOW;

    @Override
    public ZoneId getZone() {
      return ZoneOffset.UTC;
    }

    @Override
    public Clock withZone(ZoneId zone) {
      return this;
    }

    @Override
    public Instant instant() {
      return value;
    }
  }

  static final class SequenceRandom extends SecureRandom {
    private static final long serialVersionUID = 1L;
    final AtomicInteger sequence = new AtomicInteger();
    Integer fixed;
    boolean fail;

    @Override
    public void nextBytes(byte[] output) {
      java.util.Arrays.fill(output, (byte) (fixed == null ? sequence.incrementAndGet() : fixed));
      if (fail) throw new ProviderException("private-random-marker");
    }
  }
}
