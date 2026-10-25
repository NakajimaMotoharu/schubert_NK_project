package dev.codex.schubert.nk.api.application.question;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.api.error.TemporaryInfrastructureException;
import dev.codex.schubert.nk.api.idempotency.FingerprintKeyRing;
import dev.codex.schubert.nk.api.idempotency.JdbcInboxCoordinator;
import dev.codex.schubert.nk.api.idempotency.ResponseSnapshotCodec;
import dev.codex.schubert.nk.api.idempotency.ResultBoundResponseSnapshotCodec;
import dev.codex.schubert.nk.api.logging.ApiLogDatabaseFixture;
import dev.codex.schubert.nk.api.messaging.outbound.JdbcOutboxRepository;
import dev.codex.schubert.nk.api.messaging.outbound.OutboxDispatcher;
import dev.codex.schubert.nk.api.messaging.outbound.OutboxJmsSender;
import dev.codex.schubert.nk.api.messaging.outbound.OwnedOutboxDispatcher;
import dev.codex.schubert.nk.api.security.AuthenticationContextVerifier;
import dev.codex.schubert.nk.api.security.ContextHash;
import dev.codex.schubert.nk.protocol.codec.PermanentProtocolException;
import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.header.CommonHeader;
import dev.codex.schubert.nk.protocol.header.InteractionKind;
import dev.codex.schubert.nk.protocol.header.MessageKind;
import dev.codex.schubert.nk.protocol.layout.FixedPayload;
import dev.codex.schubert.nk.protocol.layout.LayoutId;
import dev.codex.schubert.nk.protocol.layout.WireMessage;
import jakarta.jms.BytesMessage;
import jakarta.jms.DeliveryMode;
import jakarta.jms.JMSContext;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.lang.reflect.Proxy;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.security.MessageDigest;
import java.sql.Connection;
import java.sql.SQLException;
import java.time.Clock;
import java.time.Instant;
import java.time.ZoneId;
import java.time.ZoneOffset;
import java.time.format.DateTimeFormatter;
import java.util.Arrays;
import java.util.HexFormat;
import java.util.List;
import java.util.Locale;
import java.util.Objects;
import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicLong;
import javax.sql.DataSource;
import org.apache.activemq.artemis.core.config.Configuration;
import org.apache.activemq.artemis.core.deployers.impl.FileConfigurationParser;
import org.apache.activemq.artemis.core.server.embedded.EmbeddedActiveMQ;
import org.apache.activemq.artemis.jms.client.ActiveMQConnectionFactory;
import org.apache.activemq.artemis.jms.client.ActiveMQQueue;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** Real PG18 and Artemis, literal UI236 offsets; no production-generated expected wire. */
class QuestionSubmissionServiceTest {
  @TempDir static Path root;
  static ApiLogDatabaseFixture db;
  static final Instant NOW = Instant.parse("2026-10-01T00:00:00.123456Z");
  static final UUID M0 = new UUID(701, 1);
  static final UUID TOKEN = new UUID(702, 1);
  static final String RECEIPT = "0".repeat(26);
  static final String CONTEXT = "b".repeat(64);

  @BeforeAll
  static void start() throws Exception {
    db = new ApiLogDatabaseFixture(root);
  }

  @AfterAll
  static void stop() throws Exception {
    if (db != null) db.stop();
  }

  @Test
  void asub001ActualAcceptanceDedicatedSendAndFrozenSameAndNewMessageReplay(
      @TempDir Path brokerRoot) throws Exception {
    var broker = broker(brokerRoot);
    try (var h = new Fixture();
        var factory = new ActiveMQConnectionFactory("vm://0");
        var receiving = factory.createContext(JMSContext.SESSION_TRANSACTED);
        var consumer =
            receiving.createConsumer(new ActiveMQQueue("nk.async.work::nk.async.work.q"))) {
      AtomicLong sendingThread = new AtomicLong();
      var dispatcher =
          new OutboxDispatcher(
              db::api,
              () -> {
                sendingThread.set(Thread.currentThread().threadId());
                return factory.createContext(JMSContext.SESSION_TRANSACTED);
              },
              new JdbcOutboxRepository(() -> 0),
              new OutboxJmsSender(),
              h.clock);
      try (var owned = OwnedOutboxDispatcher.start(dispatcher, "qst-pt")) {
        h.signal =
            () -> {
              assertEquals(0, h.live.get());
              owned.wake();
            };
        var initial = request("Public fixture", M0, TOKEN, NOW, CONTEXT);
        assertArrayEquals(
            response(M0, new UUID(700, 3), "0000", RECEIPT, 1, NOW), h.service.process(initial));
        assertNotEquals(Thread.currentThread().threadId(), sendingThread.get());
        BytesMessage message = (BytesMessage) consumer.receive(2000);
        assertNotNull(message);
        byte[] actual = new byte[(int) message.getBodyLength()];
        assertEquals(320, message.readBytes(actual));
        assertArrayEquals(work(new UUID(700, 1), M0, RECEIPT, 1, 1, NOW), actual);
        assertEquals(new UUID(700, 1).toString(), message.getStringProperty("NKMessageID"));
        assertEquals(M0.toString(), message.getJMSCorrelationID());
        assertEquals(DeliveryMode.PERSISTENT, message.getJMSDeliveryMode());
        assertEquals(0, message.getJMSExpiration());
        receiving.commit();
        String frozen =
            h.text(
                "select md5(response_body_encrypted)||':'||completed_at::text||':'||expires_at::text from schubert.request_inbox");
        assertArrayEquals(
            response(M0, new UUID(700, 4), "0200", RECEIPT, 1, NOW), h.service.process(initial));
        UUID retry = new UUID(701, 2);
        assertArrayEquals(
            response(retry, new UUID(700, 5), "0200", RECEIPT, 1, NOW),
            h.service.process(request("Public fixture", retry, TOKEN, NOW, CONTEXT)));
        assertEquals(
            frozen,
            h.text(
                "select md5(response_body_encrypted)||':'||completed_at::text||':'||expires_at::text from schubert.request_inbox"));
        assertEquals(1, h.scalar("select count(*) from schubert.questions"));
        assertEquals(
            1,
            h.scalar(
                "select count(*) from schubert.async_jobs where state='RECEIVED' and message_id='"
                    + M0
                    + "' and correlation_id=message_id"));
        assertEquals(
            1,
            h.scalar(
                "select count(*) from schubert.notifications where notification_type='ACCEPTED' and state='RECEIVED'"));
        assertEquals(
            1,
            h.scalar(
                "select count(*) from schubert.mq_outbox where status='SENT' and sent_at is not null and lease_owner is null and lease_until is null"));
        assertEquals(
            604800,
            h.scalar(
                "select extract(epoch from expires_at-completed_at)::bigint from schubert.request_inbox"));
        assertEquals("Public fixture", h.text("select body from schubert.questions"));
        assertEquals(
            1,
            h.scalar(
                "select count(*) from schubert.app_logs where action='QUESTION_SUBMITTED' and details->>'resultCode'='0000' and details->>'state'='RECEIVED' and details->>'receiptId'='"
                    + RECEIPT
                    + "' and details->>'jobId'='1' and details->>'questionId'='1'"));
        assertEquals(
            2, h.scalar("select count(*) from schubert.app_logs where action='INBOX_REPLAYED'"));
        assertEquals(
            0,
            h.scalar(
                "select count(*) from schubert.app_logs where details::text like '%Public fixture%' or details::text like '%"
                    + TOKEN
                    + "%' or details::text like '%"
                    + CONTEXT
                    + "%'"));
        assertNull(consumer.receiveNoWait());
      }
    } finally {
      broker.stop();
    }
  }

  @Test
  void asub002TotalDeadlineCommitRemainsAndLaterReplayRequiresOriginalSent() throws Exception {
    try (var h = new Fixture()) {
      h.nanoStep = 750_000_000;
      var input = request("Public fixture", M0, TOKEN, NOW, CONTEXT);
      assertArrayEquals(
          response(M0, new UUID(700, 1), "9000", "", 0, NOW), h.service.process(input));
      assertEquals(0, h.scalar("select count(*) from schubert.questions"));
      h.nanoStep = 0;
      h.ids.set(0);
      h.nanos.set(0);
      h.signal =
          () -> {
            assertEquals(0, h.live.get());
            h.nanos.set(2_000_000_000);
          };
      assertArrayEquals(
          response(M0, new UUID(700, 3), "9000", "", 0, NOW), h.service.process(input));
      assertEquals(1, h.scalar("select count(*) from schubert.questions"));
      assertEquals("COMPLETED", h.text("select processing_state from schubert.request_inbox"));
      assertEquals("PENDING", h.text("select status from schubert.mq_outbox"));
      var frozen =
          h.text(
              "select md5(response_body_encrypted)||':'||expires_at::text from schubert.request_inbox");
      h.nanos.set(0);
      h.signal =
          () -> {
            assertEquals(0, h.live.get());
            h.sql(
                "update schubert.mq_outbox set status='SENT',sent_at='2026-10-01T00:00:00.123456Z'");
          };
      assertArrayEquals(
          response(M0, new UUID(700, 4), "0200", RECEIPT, 1, NOW), h.service.process(input));
      assertEquals(
          frozen,
          h.text(
              "select md5(response_body_encrypted)||':'||expires_at::text from schubert.request_inbox"));
      h.ids.set(0);
      assertArrayEquals(
          response(new UUID(701, 3), new UUID(700, 1), "9000", "", 0, NOW),
          h.service.process(
              request("late", new UUID(701, 3), new UUID(702, 3), NOW.minusSeconds(2), CONTEXT)));
      assertEquals(1, h.scalar("select count(*) from schubert.questions"));
    }
  }

  @Test
  void asub003AuthConflictAndPurgedInboxNeverCreateAliasOrDuplicate() throws Exception {
    try (var h = new Fixture()) {
      byte[] denied = response(M0, new UUID(700, 1), "0102", "", 0, NOW);
      put(denied, 113, "c".repeat(64));
      assertArrayEquals(
          denied, h.service.process(request("Public fixture", M0, TOKEN, NOW, "c".repeat(64))));
      assertEquals(0, h.scalar("select count(*) from schubert.request_inbox"));
      h.ids.set(0);
      h.confirmOnSignal();
      h.service.process(request("Public fixture", M0, TOKEN, NOW, CONTEXT));
      assertArrayEquals(
          response(new UUID(701, 2), new UUID(700, 4), "0105", "", 0, NOW),
          h.service.process(request("different", new UUID(701, 2), TOKEN, NOW, CONTEXT)));
      assertThrows(
          PermanentProtocolException.class,
          () -> h.service.process(request("different", M0, TOKEN, NOW, CONTEXT)));
      h.sql("delete from schubert.request_inbox");
      assertArrayEquals(
          response(new UUID(701, 3), new UUID(700, 5), "9000", "", 0, NOW),
          h.service.process(request("Public fixture", new UUID(701, 3), TOKEN, NOW, CONTEXT)));
      assertArrayEquals(
          response(new UUID(701, 4), new UUID(700, 6), "0105", "", 0, NOW),
          h.service.process(request("different", new UUID(701, 4), TOKEN, NOW, CONTEXT)));
      assertEquals(0, h.scalar("select count(*) from schubert.request_inbox"));
      assertEquals(1, h.scalar("select count(*) from schubert.questions"));
      assertEquals(1, h.scalar("select count(*) from schubert.mq_outbox"));
      assertEquals(
          2,
          h.scalar(
              "select count(*) from schubert.app_logs where action='QUESTION_SUBMITTED' and details->>'resultCode'='0105'"));
      assertEquals(
          1,
          h.scalar(
              "select count(*) from schubert.app_logs where action='PROTOCOL_REJECTED' and details->>'step'='MESSAGE_IDENTITY'"));
      h.fault = "rollback";
      assertThrows(
          TemporaryInfrastructureException.class,
          () -> h.service.process(request("different", new UUID(701, 5), TOKEN, NOW, CONTEXT)));
      h.fault = "none";
      h.prepareFault = "insert into schubert.app_logs";
      assertThrows(
          TemporaryInfrastructureException.class,
          () ->
              h.service.process(request("Public fixture", new UUID(701, 6), TOKEN, NOW, CONTEXT)));
      assertEquals(0, h.live.get());
    }
  }

  @Test
  void asub004EveryAtomicParticipantFaultRollsBackAndRetainsNoSecrets() throws Exception {
    for (String fault :
        List.of(
            "open",
            "null",
            "setAutoCommit",
            "setReadOnly",
            "insert into schubert.questions",
            "insert into schubert.async_jobs",
            "insert into schubert.notifications",
            "insert into schubert.mq_outbox",
            "insert into schubert.app_logs",
            "update schubert.request_inbox",
            "commit")) {
      try (var h = new Fixture()) {
        h.fault = fault;
        var failure =
            assertThrows(
                TemporaryInfrastructureException.class,
                () -> h.service.process(request("Public fixture", M0, TOKEN, NOW, CONTEXT)),
                fault);
        assertFalse(failure.toString().contains("private"));
        for (String table :
            List.of("questions", "async_jobs", "notifications", "mq_outbox", "request_inbox"))
          assertEquals(0, h.scalar("select count(*) from schubert." + table), fault + "/" + table);
        assertEquals(0, h.live.get(), fault);
      }
    }
    for (String fault : List.of("close", "rollback"))
      try (var h = new Fixture()) {
        h.fault = fault;
        if (fault.equals("rollback")) h.prepareFault = "insert into schubert.notifications";
        assertThrows(
            TemporaryInfrastructureException.class,
            () -> h.service.process(request("Public fixture", M0, TOKEN, NOW, CONTEXT)));
        assertEquals(
            fault.equals("close") ? 1 : 0, h.scalar("select count(*) from schubert.questions"));
        assertEquals(0, h.live.get());
      }
  }

  @Test
  void asub005SnapshotAndExactWorkProofRejectCorruptionWithoutFreshBusiness() throws Exception {
    for (String mutation :
        List.of(
            "update schubert.request_inbox set processing_state='PROCESSING',completed_at=null,result_ref_type=null,result_ref_id=null,response_layout_id=null,response_version=null,response_body_encrypted=null,response_key_version=null",
            "update schubert.request_inbox set processing_state='ERROR'",
            "update schubert.request_inbox set response_layout_id='QDLRSP01'",
            "update schubert.request_inbox set response_version='002'",
            "update schubert.request_inbox set response_body_encrypted=decode(repeat('00',40),'hex')",
            "delete from schubert.mq_outbox",
            "update schubert.mq_outbox set body=set_byte(body,282,57)",
            "update schubert.mq_outbox set message_id='00000000-0000-0000-0000-000000000001'",
            "update schubert.mq_outbox set created_at=created_at+interval '1 microsecond'",
            "update schubert.mq_outbox set sent_at=sent_at-interval '1 microsecond'",
            "update schubert.mq_outbox set lease_owner='other',lease_until=sent_at+interval '1 second'",
            "update schubert.async_jobs set owner_user_id=2",
            "update schubert.async_jobs set correlation_id='00000000-0000-0000-0000-000000000002'",
            "update schubert.questions set receipt_id=repeat('1',26)")) {
      try (var h = new Fixture()) {
        h.confirmOnSignal();
        h.service.process(request("Public fixture", M0, TOKEN, NOW, CONTEXT));
        h.sql(mutation);
        assertThrows(
            TemporaryInfrastructureException.class,
            () ->
                h.service.process(request("Public fixture", new UUID(701, 2), TOKEN, NOW, CONTEXT)),
            mutation);
        assertEquals(1, h.scalar("select count(*) from schubert.questions"));
        assertEquals(1, h.scalar("select count(*) from schubert.request_inbox"));
        assertEquals(0, h.live.get());
      }
    }
  }

  @Test
  void asub006ReceiptOnlyCollisionRetryAndClosedBoundary() throws Exception {
    try (var h = new Fixture()) {
      h.confirmOnSignal();
      h.service.process(request("Public fixture", M0, TOKEN, NOW, CONTEXT));
      AtomicInteger index = new AtomicInteger();
      h.receipts = new QuestionReceiptIdGenerator(bound -> index.getAndIncrement() < 26 ? 0 : 1);
      h.ids.set(100);
      var service = h.build();
      byte[] result =
          service.process(request("second", new UUID(701, 2), new UUID(702, 2), NOW, CONTEXT));
      assertArrayEquals(
          response(new UUID(701, 2), new UUID(700, 103), "0000", "1".repeat(26), 3, NOW), result);
      assertEquals(2, h.scalar("select count(*) from schubert.questions"));
      assertThrows(
          TemporaryInfrastructureException.class,
          () ->
              h.service.process(
                  request("third", new UUID(701, 3), new UUID(702, 3), NOW, CONTEXT)));
      assertEquals(2, h.scalar("select count(*) from schubert.questions"));
      assertEquals(2, h.scalar("select count(*) from schubert.request_inbox"));
      assertThrows(NullPointerException.class, () -> h.service.process(null));
      var wrong = request("valid", M0, TOKEN, NOW, CONTEXT);
      byte[] invalid = wrong.payload().copyData();
      invalid[4143] = 'X';
      assertThrows(
          PermanentProtocolException.class,
          () ->
              h.service.process(
                  new WireMessage<>(wrong.header(), new FixedPayload(invalid, 0, List.of()))));
    }
  }

  @Test
  void asub007ProductionConstructorAndMissingConfigurationAreFailClosed() throws Exception {
    try (var h = new Fixture()) {
      var authentication = new AuthenticationContextVerifier(new ContextHash());
      var inbox = new JdbcInboxCoordinator(h.fingerprints);
      var snapshots = new ResultBoundResponseSnapshotCodec(h.snapshots);
      var service =
          new QuestionSubmissionService(
              h.source, authentication, inbox, snapshots, () -> {}, h.clock);
      byte[] actual = service.process(request("late", M0, TOKEN, NOW.minusSeconds(2), CONTEXT));
      UUID fresh = UUID.fromString(new String(actual, 24, 36, StandardCharsets.US_ASCII));
      assertEquals(4, fresh.version());
      assertNotEquals(M0, fresh);
      assertArrayEquals(response(M0, fresh, "9000", "", 0, NOW), actual);
      assertEquals(0, h.scalar("select count(*) from schubert.questions"));
      for (int i = 0; i < 9; i++) {
        int missing = i;
        assertThrows(
            NullPointerException.class,
            () ->
                new QuestionSubmissionService(
                    missing == 0 ? null : h.source,
                    missing == 1 ? null : authentication,
                    missing == 2 ? null : inbox,
                    missing == 3 ? null : snapshots,
                    missing == 4 ? null : () -> {},
                    missing == 5 ? null : h.clock,
                    missing == 6 ? null : h.receipts,
                    missing == 7 ? null : UUID::randomUUID,
                    missing == 8 ? null : System::nanoTime));
      }
    }
  }

  static final class Fixture implements AutoCloseable {
    final ApiLogDatabaseFixture database;
    final AtomicInteger live = new AtomicInteger();
    final AtomicInteger ids = new AtomicInteger();
    final AtomicLong nanos = new AtomicLong();
    long nanoStep;
    final Clock clock = Clock.fixed(NOW, ZoneOffset.UTC);
    final FingerprintKeyRing fingerprints =
        new FingerprintKeyRing("test", new byte[32], null, null);
    final ResponseSnapshotCodec snapshots =
        new ResponseSnapshotCodec("test", new byte[32], null, null);
    QuestionReceiptIdGenerator receipts = new QuestionReceiptIdGenerator(bound -> 0);
    String fault = "none";
    String prepareFault = "none";
    Runnable signal = () -> {};
    final DataSource source;
    final QuestionSubmissionService service;

    Fixture() throws Exception {
      this(db);
    }

    Fixture(ApiLogDatabaseFixture database) throws Exception {
      this.database = Objects.requireNonNull(database);
      try (var c = database.admin();
          var s = c.createStatement()) {
        s.execute(
            "truncate schubert.app_users,schubert.mq_outbox,schubert.app_logs restart identity cascade");
      }
      sql(
          "insert into schubert.app_users(id,username,username_key,password_hash,role,status,password_changed_at,created_at,updated_at) select i,'u'||i,'u'||i,'unusable-synthetic','USER','ACTIVE','2026-10-01T00:00:00Z','2026-10-01T00:00:00Z','2026-10-01T00:00:00Z' from (values(1),(2))n(i)");
      try (var c = database.api();
          var s =
              c.prepareStatement(
                  """
          insert into schubert.auth_sessions(id,user_id,context_hash,context_ciphertext,key_version,
          issued_at,last_accessed_at,expires_at,client_address,created_message_id)
          values (?,1,?,decode(repeat('00',29),'hex'),'test','2026-10-01T00:00:00Z',
          '2026-10-01T00:00:00Z','2026-10-01T08:00:00Z','127.0.0.1',?)
          """)) {
        s.setObject(1, new UUID(703, 1));
        s.setString(
            2,
            HexFormat.of()
                .formatHex(
                    MessageDigest.getInstance("SHA-256")
                        .digest(CONTEXT.getBytes(StandardCharsets.US_ASCII))));
        s.setObject(3, new UUID(703, 2));
        assertEquals(1, s.executeUpdate());
      }
      source =
          (DataSource)
              Proxy.newProxyInstance(
                  DataSource.class.getClassLoader(),
                  new Class<?>[] {DataSource.class},
                  (p, m, a) -> {
                    assertEquals("getConnection", m.getName());
                    if (fault.equals("open")) throw new SQLException("private-provider");
                    if (fault.equals("null")) return null;
                    Connection actual = database.api();
                    live.incrementAndGet();
                    return Proxy.newProxyInstance(
                        Connection.class.getClassLoader(),
                        new Class<?>[] {Connection.class},
                        (cp, cm, ca) -> {
                          String name = cm.getName();
                          if (name.equals(fault) && !name.equals("close"))
                            throw new SQLException("private-provider");
                          if (name.equals("prepareStatement")
                              && (ca[0].toString().stripLeading().startsWith(fault)
                                  || ca[0].toString().stripLeading().startsWith(prepareFault)))
                            throw new SQLException("private-SQL");
                          Object value = invoke(actual, cm, ca);
                          if (name.equals("close")) {
                            live.decrementAndGet();
                            if (fault.equals("close")) throw new SQLException("private-close");
                          }
                          return value;
                        });
                  });
      service = build();
    }

    QuestionSubmissionService build() throws Exception {
      return new QuestionSubmissionService(
          source,
          new AuthenticationContextVerifier(new ContextHash()),
          new JdbcInboxCoordinator(fingerprints),
          new ResultBoundResponseSnapshotCodec(snapshots),
          () -> signal.run(),
          clock,
          receipts,
          () -> new UUID(700, ids.incrementAndGet()),
          () -> nanos.getAndAdd(nanoStep));
    }

    void confirmOnSignal() {
      signal =
          () -> {
            assertEquals(0, live.get());
            sql(
                "update schubert.mq_outbox set status='SENT',sent_at='2026-10-01T00:00:00.123456Z' where status<>'SENT'");
          };
    }

    void sql(String query) {
      try (var c = database.api();
          var s = c.createStatement()) {
        s.executeUpdate(query);
      } catch (SQLException e) {
        throw new AssertionError(e);
      }
    }

    long scalar(String query) throws SQLException {
      try (var c = database.api();
          var s = c.createStatement();
          var r = s.executeQuery(query)) {
        assertTrue(r.next());
        return r.getLong(1);
      }
    }

    String text(String query) throws SQLException {
      try (var c = database.api();
          var s = c.createStatement();
          var r = s.executeQuery(query)) {
        assertTrue(r.next());
        return r.getString(1);
      }
    }

    @Override
    public void close() {
      assertEquals(0, live.get());
      snapshots.close();
      fingerprints.close();
    }
  }

  static Object invoke(Object target, Method method, Object[] args) throws Throwable {
    try {
      return method.invoke(target, args);
    } catch (InvocationTargetException e) {
      throw e.getCause();
    }
  }

  static WireMessage<FixedPayload> request(
      String text, UUID message, UUID token, Instant time, String context) {
    byte[] payload = new byte[4144];
    Arrays.fill(payload, (byte) 32);
    put(payload, 0, text);
    put(payload, 4096, token.toString());
    var header =
        new CommonHeader(
            "SCHBNK01",
            1,
            new LayoutId("QSBREQ01"),
            1,
            MessageKind.REQUEST,
            InteractionKind.ASYNC_ACCEPTANCE,
            message,
            message,
            time.truncatedTo(java.time.temporal.ChronoUnit.MILLIS),
            Optional.of(AuthenticationContext.of(context)),
            256,
            4144,
            0,
            0,
            4400,
            Optional.empty());
    return new WireMessage<>(header, new FixedPayload(payload, 0, List.of()));
  }

  static byte[] response(
      UUID correlation, UUID response, String code, String receipt, long question, Instant time) {
    byte[] bytes = header("QSBRSP01", "SA", response, correlation, time, CONTEXT, code);
    if (code.equals("0000") || code.equals("0200")) {
      put(bytes, 256, receipt);
      put(bytes, 282, String.format(Locale.ROOT, "%012d", question));
      put(bytes, 294, date(time));
    } else put(bytes, 282, "00000000000000000000000000000");
    return bytes;
  }

  static byte[] work(
      UUID work, UUID source, String receipt, long question, long job, Instant time) {
    byte[] bytes = header("QWKREQ01", "EI", work, source, time, "", "    ");
    put(bytes, 256, receipt);
    put(bytes, 282, String.format(Locale.ROOT, "%012d%012d", question, job));
    return bytes;
  }

  static byte[] header(
      String layout,
      String kinds,
      UUID id,
      UUID correlation,
      Instant time,
      String context,
      String code) {
    byte[] bytes = new byte[320];
    Arrays.fill(bytes, (byte) 32);
    put(bytes, 0, "SCHBNK01001");
    put(bytes, 11, layout);
    put(bytes, 19, "001" + kinds);
    put(bytes, 24, id.toString());
    put(bytes, 60, correlation.toString());
    put(bytes, 96, date(time));
    put(bytes, 113, context);
    put(bytes, 177, "0256000064000000000000000000320");
    put(bytes, 208, code);
    return bytes;
  }

  static String date(Instant time) {
    return DateTimeFormatter.ofPattern("uuuuMMddHHmmssSSS", Locale.ROOT)
        .withZone(ZoneId.of("Asia/Tokyo"))
        .format(time);
  }

  static void put(byte[] bytes, int offset, String text) {
    byte[] input = text.getBytes(StandardCharsets.UTF_8);
    System.arraycopy(input, 0, bytes, offset, input.length);
  }

  static EmbeddedActiveMQ broker(Path root) throws Exception {
    Configuration c;
    try (var input = Files.newInputStream(Path.of(System.getProperty("broker.template")))) {
      c = new FileConfigurationParser().parseMainConfig(input);
    }
    c.setPagingDirectory(root.resolve("paging").toString())
        .setBindingsDirectory(root.resolve("bindings").toString())
        .setJournalDirectory(root.resolve("journal").toString())
        .setLargeMessagesDirectory(root.resolve("large").toString())
        .setSecurityEnabled(false)
        .clearAcceptorConfigurations()
        .addAcceptorConfiguration("component", "vm://0");
    return new EmbeddedActiveMQ().setConfiguration(c).start();
  }
}
