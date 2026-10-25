package dev.codex.schubert.nk.api.security;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assertions.fail;

import dev.codex.schubert.nk.api.dispatch.ApiLogPathApplicationRuntime;
import dev.codex.schubert.nk.api.dispatch.JdbcSyncRequestProcessor;
import dev.codex.schubert.nk.api.domain.Role;
import dev.codex.schubert.nk.api.error.TemporaryInfrastructureException;
import dev.codex.schubert.nk.api.idempotency.CanonicalField;
import dev.codex.schubert.nk.api.idempotency.FingerprintKeyRing;
import dev.codex.schubert.nk.api.idempotency.JdbcInboxCoordinator;
import dev.codex.schubert.nk.api.idempotency.OperationFingerprint;
import dev.codex.schubert.nk.api.idempotency.ResponseSnapshotCodec;
import dev.codex.schubert.nk.api.logging.ApiLogDatabaseFixture;
import dev.codex.schubert.nk.api.messaging.inbound.SyncRequestListener;
import dev.codex.schubert.nk.protocol.codec.PermanentProtocolException;
import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.header.CommonHeader;
import dev.codex.schubert.nk.protocol.header.InteractionKind;
import dev.codex.schubert.nk.protocol.header.MessageKind;
import dev.codex.schubert.nk.protocol.layout.FixedPayload;
import dev.codex.schubert.nk.protocol.layout.LayoutId;
import dev.codex.schubert.nk.protocol.layout.WireMessage;
import dev.codex.schubert.nk.protocol.transport.BrokerTopology;
import jakarta.jms.BytesMessage;
import jakarta.jms.DeliveryMode;
import jakarta.jms.JMSContext;
import jakarta.jms.JMSException;
import jakarta.jms.JMSRuntimeException;
import jakarta.jms.Message;
import java.io.ByteArrayOutputStream;
import java.io.DataOutputStream;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.lang.reflect.Proxy;
import java.net.InetAddress;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.security.SecureRandom;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.SQLException;
import java.time.Clock;
import java.time.Instant;
import java.time.ZoneOffset;
import java.time.temporal.ChronoUnit;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashSet;
import java.util.HexFormat;
import java.util.List;
import java.util.Locale;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicLong;
import java.util.concurrent.atomic.AtomicReference;
import javax.crypto.Mac;
import javax.crypto.SecretKeyFactory;
import javax.crypto.spec.PBEKeySpec;
import javax.crypto.spec.SecretKeySpec;
import javax.sql.DataSource;
import org.apache.activemq.artemis.core.config.Configuration;
import org.apache.activemq.artemis.core.deployers.impl.FileConfigurationParser;
import org.apache.activemq.artemis.core.server.embedded.EmbeddedActiveMQ;
import org.apache.activemq.artemis.jms.client.ActiveMQConnectionFactory;
import org.apache.activemq.artemis.jms.client.ActiveMQQueue;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
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
  private static final UUID REQUEST = new UUID(0, 101);
  private static final UUID SESSION = new UUID(0, 104);
  private static final String PASSWORD = "synthetic-password";
  private static final String FIRST_STAMP = "20260908100203456";
  private static final String LATER_STAMP = "20260908100303456";
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
    if (contexts != null) contexts.close();
    if (snapshots != null) snapshots.close();
    if (keys != null) keys.close();
    if (database != null) database.stop();
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
  void productionAssemblyAuthenticatesWithRealInboxSessionAndAudit() throws Exception {
    var login =
        LoginApplicationAssembly.create(
            keys, contexts, snapshots, Clock.fixed(NOW, ZoneOffset.UTC));
    byte[] response =
        call(login, request("利用者", PASSWORD, "127.0.0.1", REQUEST), NOW.minusSeconds(1));
    assertEquals(688, response.length);
    assertEquals("SCHBNK01", text(response, 0, 8));
    assertEquals("LGNRSP01", text(response, 11, 8));
    assertEquals("0000", text(response, 208, 4));
    assertEquals(REQUEST.toString(), text(response, 60, 36));
    assertEquals(FIRST_STAMP, text(response, 96, 17));
    assertEquals("利用者", text(response, 256, 64).stripTrailing());
    assertEquals("USER ", text(response, 320, 5));
    assertNotEquals(REQUEST, UUID.fromString(text(response, 24, 36)));
    assertEquals(64, text(response, 325, 64).stripTrailing().length());
    assertEffects(1, 1, 1);
    assertEquals(0, scalar("select failed_count from schubert.app_users where id=7"));
    assertEquals(
        1,
        scalar(
            "select count(*) from schubert.request_inbox where message_id='00000000-0000-0000-0000-000000000065'"
                + " and processing_state='COMPLETED' and result_ref_type='AUTH_SESSION'"));
  }

  @Test
  void productionAssemblyFailedLoginReplaysWithoutSecondAttempt() throws Exception {
    assertThrows(
        NullPointerException.class,
        () -> LoginApplicationAssembly.create(null, contexts, snapshots, Clock.systemUTC()));
    assertThrows(
        NullPointerException.class,
        () -> LoginApplicationAssembly.create(keys, null, snapshots, Clock.systemUTC()));
    assertThrows(
        NullPointerException.class,
        () -> LoginApplicationAssembly.create(keys, contexts, null, Clock.systemUTC()));
    assertThrows(
        NullPointerException.class,
        () -> LoginApplicationAssembly.create(keys, contexts, snapshots, null));
    assertEffects(0, 0, 0);
    var login =
        LoginApplicationAssembly.create(
            keys, contexts, snapshots, Clock.fixed(NOW, ZoneOffset.UTC));
    var input = request("利用者", "synthetic-wrong", "127.0.0.1", REQUEST);
    byte[] first = call(login, input, NOW.minusSeconds(1));
    byte[] replay = call(login, input, NOW);
    assertEquals("0101", text(first, 208, 4));
    assertEquals("0101", text(replay, 208, 4));
    assertEquals("LGNRSP01", text(first, 11, 8));
    assertEquals("LGNRSP01", text(replay, 11, 8));
    assertEquals(FIRST_STAMP, text(first, 96, 17));
    assertEquals(0, scalar("select count(*) from schubert.auth_sessions"));
    assertEquals(1, scalar("select failed_count from schubert.app_users where id=7"));
    assertEquals(1, scalar("select count(*) from schubert.request_inbox"));
    assertEquals(1, scalar("select count(*) from schubert.app_logs"));
  }

  @Test
  void productionApiReceiveGroupConsumesRealBrokerLoginAndReplay(@TempDir Path brokerRoot)
      throws Exception {
    Configuration configuration;
    try (var file = Files.newInputStream(Path.of(System.getProperty("broker.template")))) {
      configuration = new FileConfigurationParser().parseMainConfig(file);
    }
    configuration
        .setPagingDirectory(brokerRoot.resolve("paging").toString())
        .setBindingsDirectory(brokerRoot.resolve("bindings").toString())
        .setJournalDirectory(brokerRoot.resolve("journal").toString())
        .setLargeMessagesDirectory(brokerRoot.resolve("large").toString())
        .setSecurityEnabled(false)
        .clearAcceptorConfigurations()
        .addAcceptorConfiguration("component", "vm://0");
    var broker = new EmbeddedActiveMQ().setConfiguration(configuration).start();
    var terminal = new AtomicInteger();
    try (var factory = new ActiveMQConnectionFactory("vm://0");
        var producer = factory.createContext(JMSContext.AUTO_ACKNOWLEDGE);
        var observer = factory.createContext(JMSContext.AUTO_ACKNOWLEDGE);
        var replies =
            observer.createConsumer(
                new ActiveMQQueue(BrokerTopology.SYNC_REPLY_WEB.fullyQualifiedQueue()));
        var runtime =
            ApiLogPathApplicationRuntime.startWithLogin(
                () -> factory.createContext(JMSContext.SESSION_TRANSACTED),
                () -> factory.createContext(JMSContext.SESSION_TRANSACTED),
                source(database::api),
                keys,
                contexts,
                snapshots,
                ignored -> {
                  throw new AssertionError("game route is not part of Login PT");
                },
                ignored -> {
                  throw new AssertionError("log route is not part of Login PT");
                },
                Clock.fixed(NOW, ZoneOffset.UTC),
                ignored -> terminal.incrementAndGet())) {
      assertTrue(runtime.ready());
      sendLogin(producer, new ActiveMQQueue(BrokerTopology.SYNC_REQUEST.fullyQualifiedQueue()));
      assertBrokerLoginReply(replies.receive(5_000), "0000");
      assertEffects(1, 1, 1);
      sendLogin(producer, new ActiveMQQueue(BrokerTopology.SYNC_REQUEST.fullyQualifiedQueue()));
      assertBrokerLoginReply(replies.receive(5_000), "0200");
      assertEffects(1, 1, 1);
      assertEquals(0, terminal.get());
      assertTrue(runtime.ready());
    } finally {
      broker.stop();
    }
  }

  private static void assertBrokerLoginReply(Message message, String result) throws JMSException {
    assertNotNull(message);
    assertTrue(message instanceof BytesMessage);
    var bytesMessage = (BytesMessage) message;
    assertEquals(688, bytesMessage.getBodyLength());
    byte[] body = new byte[688];
    try {
      assertEquals(688, bytesMessage.readBytes(body));
      assertEquals("SCHBNK01", text(body, 0, 8));
      assertEquals("LGNRSP01", text(body, 11, 8));
      assertEquals(REQUEST.toString(), text(body, 60, 36));
      assertEquals(result, text(body, 208, 4));
      UUID.fromString(text(body, 24, 36));
    } finally {
      Arrays.fill(body, (byte) 0);
    }
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
    var normalizedAtSender = request("利用者", "cafe\u0301", "2001:db8::1", REQUEST);
    assertEquals("café", text(normalizedAtSender.payload().copyData(), 64, 5));
    call(service(NOW), normalizedAtSender, NOW.minusSeconds(1));
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
      int initial = 0;
      int replay = 0;
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
      // Raw non-NFC receiver bytes remain invalid; never normalize these in the receiver fixture.
      for (int offset : new int[] {0, 64}) {
        byte[] nonCanonical = input.payload().copyData();
        Arrays.fill(nonCanonical, offset, offset == 0 ? 64 : 320, (byte) ' ');
        put(nonCanonical, offset, "cafe\u0301");
        assertPermanent(
            () ->
                service.execute(
                    c,
                    new WireMessage<>(input.header(), new FixedPayload(nonCanonical, 0, List.of())),
                    NOW));
      }
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

  @Test
  void movingClockSeparatesBusinessCompletionAndReplyTimes() throws Exception {
    var ticks = new AtomicInteger();
    var clock =
        new Clock() {
          @Override
          public java.time.ZoneId getZone() {
            return ZoneOffset.UTC;
          }

          @Override
          public Clock withZone(java.time.ZoneId zone) {
            throw new UnsupportedOperationException("fixed fixture zone");
          }

          @Override
          public Instant instant() {
            return NOW.plusSeconds(ticks.incrementAndGet());
          }
        };
    var service =
        new LoginInboxService(
            new JdbcInboxCoordinator(keys),
            authentication(),
            responses(),
            clock,
            () -> new UUID(0, ids.getAndIncrement()));
    var input = request("利用者", PASSWORD, "127.0.0.1", REQUEST);
    byte[] expected =
        LoginReplayServiceTest.golden(Role.USER, "0000", new UUID(0, 1000), "20260908100206456", 0);
    put(expected, 389, "20260908100204456");
    put(expected, 406, "20260908180204456");
    assertArrayEquals(expected, call(service, input, NOW));
    assertEquals(3, ticks.get());
    assertEquals(
        1,
        scalar(
            "select count(*) from schubert.auth_sessions where issued_at='2026-09-08T01:02:04.456789Z' and last_accessed_at=issued_at and expires_at='2026-09-08T09:02:04.456789Z'"));
    assertEquals(
        1,
        scalar(
            "select count(*) from schubert.app_users where last_login_at='2026-09-08T01:02:04.456789Z'"));
    assertEquals(
        1,
        scalar(
            "select count(*) from schubert.app_logs where logged_at='2026-09-08T01:02:04.456789Z'"));
    assertEquals(
        1,
        scalar(
            "select count(*) from schubert.request_inbox where created_at='2026-09-08T01:02:03.456789Z' and completed_at='2026-09-08T01:02:05.456789Z' and expires_at='2026-09-15T01:02:05.456789Z'"));
    put(expected, 24, new UUID(0, 1001).toString());
    put(expected, 96, "20260908100207456");
    put(expected, 208, "0200");
    assertArrayEquals(expected, call(service, input, NOW.plusSeconds(60)));
    assertEquals(4, ticks.get());
    assertEquals(1, passwordChecks.get());
    assertEffects(1, 1, 1);
    assertEquals(
        1,
        scalar(
            "select count(*) from schubert.request_inbox where expires_at='2026-09-15T01:02:05.456789Z'"));
  }

  @Test
  void jdbcOwnerCommitsOnlyCompleteBusinessResults() throws Exception {
    for (boolean valid : new boolean[] {true, false}) {
      seed();
      String password = valid ? PASSWORD : "synthetic-wrong";
      String initial = valid ? "0000" : "0101";
      String repeated = valid ? "0200" : "0101";
      var connection = database.api();
      var processor =
          new JdbcSyncRequestProcessor(
              source(() -> connection),
              (c, request, received) -> {
                assertFalse(c.getAutoCommit());
                assertEquals(NOW, received);
                byte[] response = service(NOW).execute(c, request, received);
                assertEffects(0, 0, 0);
                return response;
              },
              Clock.fixed(NOW, ZoneOffset.UTC));
      var input = request("利用者", password, "127.0.0.1", REQUEST);
      assertArrayEquals(
          expected(initial, new UUID(0, 1000), FIRST_STAMP, 0), processor.process(input));
      assertTrue(connection.isClosed());
      assertEffects(1, valid ? 1 : 0, 1);
      assertEquals(valid ? 0 : 1, scalar("select failed_count from schubert.app_users"));
      assertArrayEquals(
          expected(repeated, new UUID(0, 1001), LATER_STAMP, 0),
          processor(NOW.plusSeconds(60)).process(input));
      assertEquals(1, passwordChecks.get());
      assertEffects(1, valid ? 1 : 0, 1);
    }
  }

  @Test
  void jdbcLifecycleFaultsRemainRetryableAndRedacted() throws Exception {
    var input = request("利用者", PASSWORD, "127.0.0.1", REQUEST);
    for (String point :
        List.of(
            "open",
            "begin",
            "handler-sql",
            "handler-runtime",
            "handler-null",
            "commit-before",
            "commit-after",
            "close",
            "rollback",
            "rollback-close",
            "connection-null")) {
      seed();
      var commits = new AtomicInteger();
      var rollbacks = new AtomicInteger();
      var closes = new AtomicInteger();
      var connection = new AtomicReference<Connection>();
      DataSource provider =
          source(
              () -> {
                if (point.equals("open")) throw new SQLException("synthetic-sensitive-connect");
                if (point.equals("connection-null")) return null;
                Connection opened = database.api();
                connection.set(opened);
                return lifecycle(opened, point, commits, rollbacks, closes);
              });
      var processor =
          new JdbcSyncRequestProcessor(
              provider,
              (c, request, received) -> {
                byte[] result = service(NOW).execute(c, request, received);
                if (point.equals("handler-runtime"))
                  throw new IllegalStateException("synthetic-sensitive-application");
                if (point.equals("handler-null")) return null;
                if (point.equals("handler-sql") || point.startsWith("rollback"))
                  throw new SQLException("synthetic-sensitive-handler");
                return result;
              },
              Clock.fixed(NOW, ZoneOffset.UTC));
      assertTemporary(() -> processor.process(input));
      boolean committed = point.equals("commit-after") || point.equals("close");
      assertEffects(committed ? 1 : 0, committed ? 1 : 0, committed ? 1 : 0);
      boolean opened = !point.equals("open") && !point.equals("connection-null");
      assertEquals(opened ? 1 : 0, closes.get());
      if (opened) assertTrue(connection.get().isClosed());
      assertEquals(
          List.of("commit-before", "commit-after", "close").contains(point) ? 1 : 0, commits.get());
      assertEquals(
          opened && !point.equals("begin") && !point.equals("close") ? 1 : 0, rollbacks.get());
      if (observedPassword.get() != null)
        assertArrayEquals(new char[PASSWORD.length()], observedPassword.get());
      int checksBeforeRetry = passwordChecks.get();
      byte[] retry = processor(NOW).process(input);
      assertEquals(committed ? "0200" : "0000", text(retry, 208, 4));
      assertEffects(1, 1, 1);
      assertEquals(checksBeforeRetry + (committed ? 0 : 1), passwordChecks.get());
    }
    var source = source(database::api);
    var login = service(NOW);
    var clock = Clock.fixed(NOW, ZoneOffset.UTC);
    assertThrows(
        NullPointerException.class,
        () -> new JdbcSyncRequestProcessor(null, login::execute, clock));
    assertThrows(
        NullPointerException.class, () -> new JdbcSyncRequestProcessor(source, null, clock));
    assertThrows(
        NullPointerException.class,
        () -> new JdbcSyncRequestProcessor(source, login::execute, null));
    assertThrows(NullPointerException.class, () -> processor(NOW).process(null));
  }

  @Test
  void permanentProtocolNeedsConfirmedRollbackAndClose() throws Exception {
    var input = request("利用者", PASSWORD, "localhost", REQUEST);
    for (String point : List.of("none", "rollback", "close", "rollback-close")) {
      var commits = new AtomicInteger();
      var rollbacks = new AtomicInteger();
      var closes = new AtomicInteger();
      var connection = database.api();
      var processor =
          new JdbcSyncRequestProcessor(
              source(() -> lifecycle(connection, point, commits, rollbacks, closes)),
              service(NOW)::execute,
              Clock.fixed(NOW, ZoneOffset.UTC));
      if (point.equals("none")) {
        var error = assertThrows(PermanentProtocolException.class, () -> processor.process(input));
        assertEquals("request transaction rejected invalid protocol", error.getMessage());
        assertNull(error.getCause());
        assertEquals(0, error.getSuppressed().length);
      } else assertTemporary(() -> processor.process(input));
      assertTrue(connection.isClosed());
      assertEquals(0, commits.get());
      assertEquals(1, rollbacks.get());
      assertEquals(1, closes.get());
      assertEffects(0, 0, 0);
      assertEquals(0, passwordChecks.get());
    }
  }

  @Test
  void brokerRedeliveryReplaysCommittedLoginWithoutDuplicateEffects(@TempDir Path brokerRoot)
      throws Exception {
    Configuration configuration;
    try (var file = Files.newInputStream(Path.of(System.getProperty("broker.template")))) {
      configuration = new FileConfigurationParser().parseMainConfig(file);
    }
    configuration
        .setPagingDirectory(brokerRoot.resolve("paging").toString())
        .setBindingsDirectory(brokerRoot.resolve("bindings").toString())
        .setJournalDirectory(brokerRoot.resolve("journal").toString())
        .setLargeMessagesDirectory(brokerRoot.resolve("large").toString())
        .setSecurityEnabled(false)
        .clearAcceptorConfigurations()
        .addAcceptorConfiguration("component", "vm://0");
    var broker = new EmbeddedActiveMQ().setConfiguration(configuration).start();
    var requestQueue = new ActiveMQQueue(BrokerTopology.SYNC_REQUEST.fullyQualifiedQueue());
    var replyQueue = new ActiveMQQueue(BrokerTopology.SYNC_REPLY_WEB.fullyQualifiedQueue());
    var clock = Clock.fixed(NOW, ZoneOffset.UTC);
    try (var factory = new ActiveMQConnectionFactory("vm://0");
        var producer = factory.createContext(JMSContext.AUTO_ACKNOWLEDGE);
        var receiver = factory.createContext(JMSContext.SESSION_TRANSACTED);
        var observer = factory.createContext(JMSContext.AUTO_ACKNOWLEDGE);
        var requests = receiver.createConsumer(requestQueue);
        var replies = observer.createConsumer(replyQueue)) {
      for (String point : List.of("createProducer", "commit")) {
        seed();
        var listener = new SyncRequestListener(processor(NOW), clock);
        var failing =
            (JMSContext)
                Proxy.newProxyInstance(
                    JMSContext.class.getClassLoader(),
                    new Class<?>[] {JMSContext.class},
                    (p, m, a) -> {
                      if (m.getName().equals(point)) {
                        assertEffects(1, 1, 1); // Independent connection: DB already committed.
                        throw new JMSRuntimeException("synthetic transport boundary failure");
                      }
                      return invoke(receiver, m, a);
                    });
        sendLogin(producer, requestQueue);
        Message first = requests.receive(5000);
        assertNotNull(first);
        assertEquals(1, first.getIntProperty("JMSXDeliveryCount"));
        assertThrows(JMSRuntimeException.class, () -> listener.onMessage(failing, first));
        assertNull(replies.receive(250));
        assertEffects(1, 1, 1);
        assertEquals(1, passwordChecks.get());
        Message retry = requests.receive(5000);
        assertNotNull(retry);
        assertEquals(2, retry.getIntProperty("JMSXDeliveryCount"));
        listener.onMessage(receiver, retry);
        assertReply(replies.receive(5000), "0200", new UUID(0, 1001));
        assertEffects(1, 1, 1);
        assertEquals(1, passwordChecks.get());
        // Independent second send, not broker redelivery and no duplicate-cache property.
        sendLogin(producer, requestQueue);
        Message duplicate = requests.receive(5000);
        assertNotNull(duplicate);
        assertEquals(1, duplicate.getIntProperty("JMSXDeliveryCount"));
        listener.onMessage(receiver, duplicate);
        assertReply(replies.receive(5000), "0200", new UUID(0, 1002));
        assertEffects(1, 1, 1);
        assertEquals(1, passwordChecks.get());
        assertNull(requests.receive(250));
      }
      seed();
      var unavailable =
          new SyncRequestListener(
              new JdbcSyncRequestProcessor(
                  source(
                      () -> {
                        throw new SQLException("synthetic-sensitive-outage");
                      }),
                  service(NOW)::execute,
                  clock),
              clock);
      sendLogin(producer, requestQueue);
      Message beforeDb = requests.receive(5000);
      assertNotNull(beforeDb);
      assertTemporary(() -> unavailable.onMessage(receiver, beforeDb));
      assertEffects(0, 0, 0);
      assertEquals(0, passwordChecks.get());
      assertNull(replies.receive(250));
      Message retry = requests.receive(5000);
      assertNotNull(retry);
      assertEquals(2, retry.getIntProperty("JMSXDeliveryCount"));
      new SyncRequestListener(processor(NOW), clock).onMessage(receiver, retry);
      assertReply(replies.receive(5000), "0000", new UUID(0, 1000));
      assertEffects(1, 1, 1);
      assertEquals(1, passwordChecks.get());
      assertNull(requests.receive(250));
      assertNull(replies.receive(250));
    } finally {
      broker.stop();
    }
  }

  private static void sendLogin(JMSContext context, ActiveMQQueue queue) throws JMSException {
    // Independent UI232 header plus UI234 DATA offsets; no production encoder constructs input.
    byte[] body = new byte[640];
    Arrays.fill(body, (byte) ' ');
    put(body, 0, "SCHBNK01001LGNREQ01001QS");
    put(body, 24, REQUEST.toString());
    put(body, 60, REQUEST.toString());
    put(body, 96, FIRST_STAMP);
    put(body, 177, "0256000384000000000000000000640");
    put(body, 256, "利用者");
    put(body, 320, PASSWORD);
    put(body, 576, "127.0.0.1");
    var message = context.createBytesMessage();
    message.writeBytes(body);
    message.setJMSCorrelationID(REQUEST.toString());
    message.setJMSReplyTo(new ActiveMQQueue(BrokerTopology.SYNC_REPLY_WEB.fullyQualifiedQueue()));
    message.setStringProperty("NKMessageID", REQUEST.toString());
    message.setStringProperty("NKLayoutID", "LGNREQ01");
    message.setStringProperty("NKProtocolVersion", "001");
    context
        .createProducer()
        .setDeliveryMode(DeliveryMode.PERSISTENT)
        .setTimeToLive(5000)
        .send(queue, message);
    Arrays.fill(body, (byte) 0);
  }

  private static void assertReply(Message received, String code, UUID id) throws JMSException {
    var response = assertInstanceOf(BytesMessage.class, received);
    assertEquals(688, response.getBodyLength());
    byte[] body = new byte[688];
    assertEquals(688, response.readBytes(body));
    assertArrayEquals(expected(code, id, FIRST_STAMP, 0), body);
    assertEquals(REQUEST.toString(), response.getJMSCorrelationID());
    assertEquals(id.toString(), response.getStringProperty("NKMessageID"));
    assertEquals("LGNRSP01", response.getStringProperty("NKLayoutID"));
    assertEquals("001", response.getStringProperty("NKProtocolVersion"));
    assertEquals(DeliveryMode.PERSISTENT, response.getJMSDeliveryMode());
    Arrays.fill(body, (byte) 0);
  }

  private JdbcSyncRequestProcessor processor(Instant at) {
    return new JdbcSyncRequestProcessor(
        source(database::api), service(at)::execute, Clock.fixed(at, ZoneOffset.UTC));
  }

  private static void assertTemporary(Executable action) {
    var error = assertThrows(TemporaryInfrastructureException.class, action);
    assertEquals("request transaction is unavailable", error.getMessage());
    assertNull(error.getCause());
    assertEquals(0, error.getSuppressed().length);
  }

  private static DataSource source(SqlOpen provider) {
    return (DataSource)
        Proxy.newProxyInstance(
            DataSource.class.getClassLoader(),
            new Class<?>[] {DataSource.class},
            (p, m, a) -> {
              if (m.getName().equals("getConnection")) return provider.open();
              throw new UnsupportedOperationException(m.getName());
            });
  }

  @FunctionalInterface
  private interface SqlOpen {
    Connection open() throws SQLException;
  }

  private static Connection lifecycle(
      Connection connection,
      String point,
      AtomicInteger commits,
      AtomicInteger rollbacks,
      AtomicInteger closes) {
    return (Connection)
        Proxy.newProxyInstance(
            Connection.class.getClassLoader(),
            new Class<?>[] {Connection.class},
            (p, m, a) -> {
              String operation = m.getName();
              if (operation.equals("setAutoCommit") && point.equals("begin"))
                throw new SQLException("synthetic-sensitive-begin");
              if (operation.equals("commit")) {
                commits.incrementAndGet();
                if (point.equals("commit-before"))
                  throw new SQLException("synthetic-sensitive-commit");
              }
              if (operation.equals("rollback")) rollbacks.incrementAndGet();
              if (operation.equals("close")) closes.incrementAndGet();
              Object result = invoke(connection, m, a);
              if ((operation.equals("commit") && point.equals("commit-after"))
                  || (operation.equals("rollback") && point.startsWith("rollback"))
                  || (operation.equals("close") && point.endsWith("close")))
                throw new SQLException("synthetic-sensitive-lifecycle");
              return result;
            });
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
    // Independent sender-stage fixture: SS322 requires NFC before putting bytes on the wire.
    put(data, 0, java.text.Normalizer.normalize(name, java.text.Normalizer.Form.NFC));
    put(data, 64, java.text.Normalizer.normalize(password, java.text.Normalizer.Form.NFC));
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
      assertEquals(NOW, row.getObject(11, java.time.OffsetDateTime.class).toInstant());
      assertEquals(
          Instant.parse("2026-09-15T01:02:03.456789Z"),
          row.getObject(12, java.time.OffsetDateTime.class).toInstant());
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
