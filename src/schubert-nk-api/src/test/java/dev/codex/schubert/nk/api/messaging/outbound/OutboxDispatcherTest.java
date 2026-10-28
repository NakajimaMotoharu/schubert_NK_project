package dev.codex.schubert.nk.api.messaging.outbound;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import jakarta.jms.BytesMessage;
import jakarta.jms.DeliveryMode;
import jakarta.jms.JMSConsumer;
import jakarta.jms.JMSContext;
import jakarta.jms.JMSException;
import jakarta.jms.JMSProducer;
import jakarta.jms.JMSRuntimeException;
import java.io.IOException;
import java.io.InputStream;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Proxy;
import java.net.InetAddress;
import java.net.ServerSocket;
import java.net.URI;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.time.Clock;
import java.time.Duration;
import java.time.Instant;
import java.time.ZoneId;
import java.time.ZoneOffset;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashSet;
import java.util.List;
import java.util.Locale;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicReference;
import org.apache.activemq.artemis.api.core.ActiveMQDuplicateIdException;
import org.apache.activemq.artemis.core.config.Configuration;
import org.apache.activemq.artemis.core.deployers.impl.FileConfigurationParser;
import org.apache.activemq.artemis.core.server.embedded.EmbeddedActiveMQ;
import org.apache.activemq.artemis.jms.client.ActiveMQConnectionFactory;
import org.apache.activemq.artemis.jms.client.ActiveMQQueue;
import org.flywaydb.core.Flyway;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Timeout;
import org.junit.jupiter.api.io.TempDir;

/** PostgreSQL 18 and Artemis component PT for PT-IDEM-009..011. */
final class OutboxDispatcherTest {
  private static final String FIXTURE_TOSTRING_5F8C6B3F = "toString";
  private static final String FIXTURE_DLQ_ORIGINAL_MESSAGE_ID_7D1CCCBA = "dlq_original_message_id";
  private static final String FIXTURE_DLQ_DELIVERY_COUNT_E5C288A9 = "dlq_delivery_count";
  private static final String FIXTURE_GETOBJECT_B6112877 = "getObject";
  private static final String FIXTURE_HASHCODE_613EE961 = "hashCode";
  private static final String FIXTURE_EQUALS_7778BDDB = "equals";
  private static final String FIXTURE_STATUS_CFC31BCC = "status";
  private static final String FIXTURE_ATTEMPT_COUNT_87388C12 = "attempt_count";
  private static final String FIXTURE_LAST_ERROR_CODE_BF1A4C63 = "last_error_code";
  private static final String FIXTURE_NEXT_ATTEMPT_AT_BFB0B802 = "next_attempt_at";
  private static final String FIXTURE_ERROR_F717E7D8 = "ERROR";
  private static final String FIXTURE_LEASE_OWNER_6418FA0F = "lease_owner";
  private static final String FIXTURE_COMMIT_5EA9C586 = "commit";
  private static final String FIXTURE_ROLLBACK_3770B198 = "rollback";
  private static final String FIXTURE_CLOSE_97959247 = "close";
  private static final String FIXTURE_GETSESSIONMODE_BF25AD1A = "getSessionMode";
  private static final String FIXTURE_CREATEBYTESMESSAGE_F47217B2 = "createBytesMessage";
  private static final String FIXTURE_VM_0_0C76084A = "vm://0";
  private static final String FIXTURE_NK_ASYNC_WORK_F9720513 = "nk.async.work";
  private static final String FIXTURE_SENT_AT_C13E7660 = "sent_at";
  private static final String FIXTURE_SENT_6C701E27 = "SENT";
  private static final String FIXTURE_QWKREQ01_19741256 = "QWKREQ01";
  private static final String FIXTURE_001_A3FEAA64 = "001";
  private static final String FIXTURE_JMS_FAIL_B8C3E123 = "JMS_FAIL";
  private static final String FIXTURE_SYNTHETIC_COMMIT_FAILURE_D03EA83F =
      "synthetic commit failure";
  private static final String DATABASE = "outbox_pt";
  private static final String ADMIN = "pgpt_admin";
  private static final String MIGRATION = "schubert_migration";
  private static final String APP = "schubert_app";
  private static final Instant NOW = Instant.parse("2026-09-05T00:00:00Z");
  private static final Clock CLOCK = Clock.fixed(NOW, ZoneOffset.UTC);
  private static final UUID MESSAGE = UUID.fromString("81000000-0000-0000-0000-000000000001");
  private static final UUID CORRELATION = UUID.fromString("82000000-0000-0000-0000-000000000001");
  private static final Path MODULE = Path.of("").toAbsolutePath().normalize();

  private static Path pgRoot;
  private static Path clusterRoot;
  private static Path dataDirectory;
  private static int port;
  private static String jdbcUrl;

  @BeforeAll
  static void startPostgreSqlAndMigrate() throws Exception {
    pgRoot = locatePostgreSqlRoot();
    Files.createDirectories(MODULE.resolve("target"));
    clusterRoot = Files.createTempDirectory(MODULE.resolve("target"), "outbox-postgresql-18-");
    dataDirectory = clusterRoot.resolve("data");
    port = availablePort();
    run(
        pgBinary("initdb"),
        "-D",
        dataDirectory.toString(),
        "-L",
        pgRoot.resolve("share/postgresql/18").toString(),
        "--no-locale",
        "--encoding=UTF8",
        "--auth=trust",
        "--username=" + ADMIN);
    run(
        pgBinary("pg_ctl"),
        "-D",
        dataDirectory.toString(),
        "-l",
        clusterRoot.resolve("postgresql.log").toString(),
        "-o",
        serverOptions(),
        "start");
    run(
        pgBinary("createdb"),
        "-h",
        "127.0.0.1",
        "-p",
        Integer.toString(port),
        "-U",
        ADMIN,
        DATABASE);
    jdbcUrl = "jdbc:postgresql://127.0.0.1:" + port + "/" + DATABASE;
    executeResourceAsAdmin("db/provisioning/001_roles.sql");
    Flyway.configure()
        .dataSource(jdbcUrl, MIGRATION, "")
        .defaultSchema("schubert_meta")
        .schemas("schubert_meta")
        .createSchemas(true)
        .initSql("SET ROLE nk_owner")
        .table("flyway_schema_history")
        .locations("classpath:db/migration")
        .validateOnMigrate(true)
        .outOfOrder(false)
        .baselineOnMigrate(false)
        .cleanDisabled(true)
        .load()
        .migrate();
  }

  @AfterAll
  static void stopPostgreSql() throws Exception {
    if (dataDirectory != null && Files.exists(dataDirectory.resolve("postmaster.pid"))) {
      run(pgBinary("pg_ctl"), "-D", dataDirectory.toString(), "stop", "-m", "fast");
    }
  }

  @BeforeEach
  void resetDatabase() throws SQLException {
    executeApp("delete from schubert.mq_outbox");
  }

  @Test
  @Timeout(value = 10, threadMode = Timeout.ThreadMode.SEPARATE_THREAD)
  void cause3404TypedGraphTerminatesCyclesAndVisitsBothProviderEdges() {
    assertThrows(NullPointerException.class, () -> OutboxJmsSender.isDuplicateConfirmation(null));
    RuntimeException first = new RuntimeException("synthetic first");
    RuntimeException second = new RuntimeException("synthetic second", first);
    first.initCause(second);
    assertFalse(OutboxJmsSender.isDuplicateConfirmation(first));
    JMSException mixed = new JMSException("synthetic mixed");
    RuntimeException peer = new RuntimeException("synthetic peer", mixed);
    mixed.setLinkedException(peer);
    assertFalse(OutboxJmsSender.isDuplicateConfirmation(mixed));
    var duplicate = new ActiveMQDuplicateIdException("synthetic duplicate");
    mixed.initCause(duplicate);
    assertTrue(OutboxJmsSender.isDuplicateConfirmation(mixed));
    JMSException alternate = new JMSException("synthetic alternate");
    alternate.initCause(duplicate);
    alternate.setLinkedException(new RuntimeException("synthetic ordinary"));
    assertTrue(OutboxJmsSender.isDuplicateConfirmation(alternate));
    JMSException shared = new JMSException("synthetic shared");
    shared.initCause(first);
    shared.setLinkedException(first);
    assertFalse(OutboxJmsSender.isDuplicateConfirmation(shared));
    RuntimeException suppressed = new RuntimeException("AMQ229035 duplicate id synthetic");
    suppressed.addSuppressed(duplicate);
    assertFalse(OutboxJmsSender.isDuplicateConfirmation(suppressed));
    var equalRoot = new IdentityOnlyFailure();
    equalRoot.initCause(new IdentityOnlyFailure());
    assertFalse(OutboxJmsSender.isDuplicateConfirmation(equalRoot));
  }

  @Test
  @Timeout(value = 15, threadMode = Timeout.ThreadMode.SEPARATE_THREAD)
  void graph322002NestedFatalNeverMarksOrdinaryFailureAndNonfatalCycleStillRetries()
      throws Exception {
    for (int kind = 0; kind < 7; kind++) {
      resetDatabase();
      var repository = new JdbcOutboxRepository(() -> 0);
      long id = enqueue(repository, uuid(2300 + kind), NOW);
      var fatal = new LinkageError("synthetic graph fatal");
      Throwable leaf = kind == 6 ? new SQLException("synthetic ordinary leaf") : fatal;
      var graph = OwnedOutboxDispatcherTest.graph322(leaf, kind == 6 ? 4 : kind);
      var opens = new AtomicInteger();
      var jms = new AtomicInteger();
      var dispatch =
          new OutboxDispatcher(
              () -> {
                opens.incrementAndGet();
                return appConnection();
              },
              () -> {
                jms.incrementAndGet();
                throw new IllegalStateException("synthetic provider boundary", graph);
              },
              repository,
              new OutboxJmsSender(),
              CLOCK);
      if (kind < 6) {
        assertSame(fatal, assertThrows(Error.class, () -> dispatch.dispatch("graph", 1)));
        assertEquals(1, opens.get(), "only committed claim; no ordinary mark transaction");
        assertEquals("PENDING", text(id, FIXTURE_STATUS_CFC31BCC));
        assertEquals("0", text(id, FIXTURE_ATTEMPT_COUNT_87388C12));
        assertNull(text(id, FIXTURE_LAST_ERROR_CODE_BF1A4C63));
        assertEquals(NOW, timestamp(id, FIXTURE_NEXT_ATTEMPT_AT_BFB0B802));
      } else {
        assertEquals(new OutboxDispatchReport(1, 0, 1, 0), dispatch.dispatch("graph", 1));
        assertEquals(2, opens.get());
        assertEquals(FIXTURE_ERROR_F717E7D8, text(id, FIXTURE_STATUS_CFC31BCC));
        assertEquals("1", text(id, FIXTURE_ATTEMPT_COUNT_87388C12));
        assertEquals("JMS_SEND_FAILURE", text(id, FIXTURE_LAST_ERROR_CODE_BF1A4C63));
        assertEquals(NOW.plusSeconds(1), timestamp(id, FIXTURE_NEXT_ATTEMPT_AT_BFB0B802));
      }
      assertEquals(1, jms.get());
      if (kind < 6) {
        assertEquals("graph", text(id, FIXTURE_LEASE_OWNER_6418FA0F));
        assertEquals(NOW.plusSeconds(10), timestamp(id, "lease_until"));
      }
    }
  }

  @Test
  void graph322003NullProviderEdgesKeepOrdinaryFailureAndExactRetryPostconditions()
      throws Exception {
    var repository = new JdbcOutboxRepository(() -> 0);
    long id = enqueue(repository, uuid(2400), NOW);
    var sql = new SQLException("synthetic null next");
    sql.addSuppressed(new JMSException("synthetic null linked"));
    var opens = new AtomicInteger();
    var dispatch =
        new OutboxDispatcher(
            () -> {
              opens.incrementAndGet();
              return appConnection();
            },
            () -> {
              throw new IllegalStateException("synthetic ordinary graph", sql);
            },
            repository,
            new OutboxJmsSender(),
            CLOCK);
    assertEquals(new OutboxDispatchReport(1, 0, 1, 0), dispatch.dispatch("graph-null", 1));
    assertEquals(2, opens.get());
    assertEquals(FIXTURE_ERROR_F717E7D8, text(id, FIXTURE_STATUS_CFC31BCC));
    assertEquals("1", text(id, FIXTURE_ATTEMPT_COUNT_87388C12));
    assertEquals("JMS_SEND_FAILURE", text(id, FIXTURE_LAST_ERROR_CODE_BF1A4C63));
    assertEquals(NOW.plusSeconds(1), timestamp(id, FIXTURE_NEXT_ATTEMPT_AT_BFB0B802));
    assertNull(text(id, FIXTURE_LEASE_OWNER_6418FA0F));
  }

  @Test
  @Timeout(value = 10, threadMode = Timeout.ThreadMode.SEPARATE_THREAD)
  void cause3404UnconfirmedCommitAlwaysRollsBackClosesAndPreservesOriginalGraph() {
    for (boolean mixed : List.of(false, true)) {
      RuntimeException failure = new RuntimeException("synthetic commit");
      if (mixed) {
        JMSException checked = new JMSException("synthetic checked");
        failure.initCause(checked);
        checked.setLinkedException(failure);
      } else {
        RuntimeException peer = new RuntimeException("synthetic peer", failure);
        failure.initCause(peer);
      }
      // A secondary rollback duplicate is never confirmation of the original commit.
      var rollback = new jakarta.jms.JMSRuntimeException("synthetic rollback");
      rollback.initCause(new ActiveMQDuplicateIdException("synthetic secondary duplicate"));
      var closing = new jakarta.jms.JMSRuntimeException("synthetic close");
      List<String> order = new ArrayList<>();
      OutboxSendException result =
          assertThrows(
              OutboxSendException.class,
              () ->
                  new OutboxJmsSender()
                      .send(() -> graphContext(failure, rollback, closing, order), sample()));
      assertEquals("outbox JMS commit was not confirmed", result.getMessage());
      assertSame(failure, result.getCause());
      assertArrayEquals(new Throwable[] {rollback}, failure.getSuppressed());
      assertArrayEquals(new Throwable[] {closing}, result.getSuppressed());
      assertEquals(
          List.of(FIXTURE_COMMIT_5EA9C586, FIXTURE_ROLLBACK_3770B198, FIXTURE_CLOSE_97959247),
          order);
    }
  }

  @Test
  @Timeout(value = 10, threadMode = Timeout.ThreadMode.SEPARATE_THREAD)
  void cause3404ReachableTypedDuplicateConfirmsOnlyAfterRollbackAndStillCloses() throws Exception {
    JMSException branched = new JMSException("synthetic branched");
    branched.setLinkedException(new RuntimeException("synthetic peer", branched));
    branched.initCause(new ActiveMQDuplicateIdException("synthetic confirmed duplicate"));
    var failure = new jakarta.jms.JMSRuntimeException("synthetic commit", null, branched);
    List<String> order = new ArrayList<>();
    new OutboxJmsSender().send(() -> graphContext(failure, null, null, order), sample());
    assertEquals(
        List.of(FIXTURE_COMMIT_5EA9C586, FIXTURE_ROLLBACK_3770B198, FIXTURE_CLOSE_97959247), order);
    assertEquals(0, failure.getSuppressed().length);
  }

  private static JMSContext graphContext(
      RuntimeException failure,
      RuntimeException rollback,
      RuntimeException closing,
      List<String> order) {
    BytesMessage message =
        (BytesMessage)
            Proxy.newProxyInstance(
                BytesMessage.class.getClassLoader(),
                new Class<?>[] {BytesMessage.class},
                (proxy, method, arguments) -> {
                  if (method.getName().equals("writeBytes") || method.getName().startsWith("set"))
                    return null;
                  throw new AssertionError("unexpected message call " + method.getName());
                });
    JMSProducer producer =
        (JMSProducer)
            Proxy.newProxyInstance(
                JMSProducer.class.getClassLoader(),
                new Class<?>[] {JMSProducer.class},
                (proxy, method, arguments) -> {
                  if (Set.of("setDeliveryMode", "setTimeToLive", "send").contains(method.getName()))
                    return proxy;
                  throw new AssertionError("unexpected producer call " + method.getName());
                });
    return (JMSContext)
        Proxy.newProxyInstance(
            JMSContext.class.getClassLoader(),
            new Class<?>[] {JMSContext.class},
            (proxy, method, arguments) -> {
              switch (method.getName()) {
                case FIXTURE_GETSESSIONMODE_BF25AD1A:
                  return JMSContext.SESSION_TRANSACTED;
                case FIXTURE_CREATEBYTESMESSAGE_F47217B2:
                  return message;
                case "createProducer":
                  return producer;
                case FIXTURE_COMMIT_5EA9C586:
                  order.add(FIXTURE_COMMIT_5EA9C586);
                  throw failure;
                case FIXTURE_ROLLBACK_3770B198:
                  order.add(FIXTURE_ROLLBACK_3770B198);
                  if (rollback != null) throw rollback;
                  return null;
                case FIXTURE_CLOSE_97959247:
                  order.add(FIXTURE_CLOSE_97959247);
                  if (closing != null) throw closing;
                  return null;
                default:
                  throw new AssertionError("unexpected context call " + method.getName());
              }
            });
  }

  private static final class IdentityOnlyFailure extends RuntimeException {
    private static final long serialVersionUID = 1L;

    @Override
    public boolean equals(Object other) {
      throw new AssertionError("value equality must not run");
    }

    @Override
    public int hashCode() {
      throw new AssertionError("value hash must not run");
    }
  }

  @Test
  void resultTimesFollowTheObservedJmsFailureAndCommitAfterElapsedSendTime(@TempDir Path root)
      throws Exception {
    EmbeddedActiveMQ broker = startBroker(root);
    try (ActiveMQConnectionFactory factory = new ActiveMQConnectionFactory(FIXTURE_VM_0_0C76084A);
        JMSContext observer = factory.createContext(JMSContext.AUTO_ACKNOWLEDGE);
        JMSConsumer work = observer.createConsumer(queue(FIXTURE_NK_ASYNC_WORK_F9720513))) {
      JdbcOutboxRepository repository = new JdbcOutboxRepository(() -> 100);
      long id = enqueue(repository, MESSAGE, NOW);
      AtomicReference<Instant> observedTime = new AtomicReference<>(NOW);
      Clock clock = observingClock(observedTime);
      OutboxDispatcher failedSend =
          new OutboxDispatcher(
              OutboxDispatcherTest::appConnection,
              () -> {
                observedTime.set(Instant.parse("2026-09-05T00:00:03Z"));
                return failingJmsContext(false);
              },
              repository,
              new OutboxJmsSender(),
              clock);
      assertEquals(new OutboxDispatchReport(1, 0, 1, 0), failedSend.dispatch("slow-send", 1));
      assertEquals(FIXTURE_ERROR_F717E7D8, text(id, FIXTURE_STATUS_CFC31BCC));
      assertEquals("1", text(id, FIXTURE_ATTEMPT_COUNT_87388C12));
      // Independent oracle: failure at 00:00:03 + first base 1s + 10% = 00:00:04.100.
      assertEquals(
          Instant.parse("2026-09-05T00:00:04.100Z"),
          timestamp(id, FIXTURE_NEXT_ATTEMPT_AT_BFB0B802));
      assertNull(textNullable(id, FIXTURE_SENT_AT_C13E7660));
      assertNull(work.receive(250));

      observedTime.set(Instant.parse("2026-09-05T00:00:04.099Z"));
      assertEquals(new OutboxDispatchReport(0, 0, 0, 0), failedSend.dispatch("too-early", 1));
      observedTime.set(Instant.parse("2026-09-05T00:00:04.100Z"));
      AtomicInteger commits = new AtomicInteger();
      OutboxDispatcher successfulRetry =
          new OutboxDispatcher(
              OutboxDispatcherTest::appConnection,
              () ->
                  afterCommit(
                      factory.createContext(JMSContext.SESSION_TRANSACTED),
                      () -> observedTime.set(Instant.parse("2026-09-05T00:00:07.100Z")),
                      commits),
              repository,
              new OutboxJmsSender(),
              clock);
      assertEquals(
          new OutboxDispatchReport(1, 1, 0, 0), successfulRetry.dispatch("slow-success", 1));
      assertEquals(1, commits.get());
      assertEquals(FIXTURE_SENT_6C701E27, text(id, FIXTURE_STATUS_CFC31BCC));
      assertEquals(
          Instant.parse("2026-09-05T00:00:07.100Z"), timestamp(id, FIXTURE_SENT_AT_C13E7660));
      assertNull(textNullable(id, FIXTURE_LEASE_OWNER_6418FA0F));
      assertNull(textNullable(id, FIXTURE_LAST_ERROR_CODE_BF1A4C63));
      assertMessage(
          assertInstanceOf(BytesMessage.class, work.receive(5_000)),
          MESSAGE,
          eventWire(MESSAGE, CORRELATION));
      assertNull(work.receive(250));
    } finally {
      broker.stop();
    }
  }

  @Test
  void initialReceiptSendKeepsItsExactDueTimeWithoutSamplingRetryJitter(@TempDir Path root)
      throws Exception {
    EmbeddedActiveMQ broker = startBroker(root);
    AtomicInteger jitterCalls = new AtomicInteger();
    JdbcOutboxRepository repository =
        new JdbcOutboxRepository(
            () -> {
              jitterCalls.incrementAndGet();
              throw new AssertionError("initial receipt send must not sample retry jitter");
            });
    try (ActiveMQConnectionFactory factory = new ActiveMQConnectionFactory(FIXTURE_VM_0_0C76084A);
        JMSContext observer = factory.createContext(JMSContext.AUTO_ACKNOWLEDGE);
        JMSConsumer work = observer.createConsumer(queue(FIXTURE_NK_ASYNC_WORK_F9720513))) {
      long id =
          enqueue(
              repository,
              new OutboxRequest(
                  MESSAGE,
                  CORRELATION,
                  OutboxDestination.ASYNC_WORK,
                  FIXTURE_QWKREQ01_19741256,
                  FIXTURE_001_A3FEAA64,
                  eventWire(MESSAGE, CORRELATION),
                  NOW,
                  NOW));
      assertEquals(NOW, timestamp(id, FIXTURE_NEXT_ATTEMPT_AT_BFB0B802));
      OutboxDispatcher dispatcher =
          dispatcher(repository, () -> factory.createContext(JMSContext.SESSION_TRANSACTED));
      assertEquals(new OutboxDispatchReport(1, 1, 0, 0), dispatcher.dispatch("receipt", 1));
      assertEquals(0, jitterCalls.get());
      assertEquals(NOW, timestamp(id, FIXTURE_SENT_AT_C13E7660));
      assertInstanceOf(BytesMessage.class, work.receive(5_000));
    } finally {
      broker.stop();
    }
  }

  @Test
  void retryJitterReachesTheDatabaseAtEveryBaseAndContinuesAtTheAttemptCap() throws Exception {
    assertThrows(NullPointerException.class, () -> new JdbcOutboxRepository(null));
    int[] previousAttempts = {0, 1, 2, 3, 4, 99, 100};
    int[] persistedAttempts = {1, 2, 3, 4, 5, 100, 100};
    long[][] expectedMillis = {
      {900, 1_000, 1_100},
      {4_500, 5_000, 5_500},
      {27_000, 30_000, 33_000},
      {54_000, 60_000, 66_000},
      {270_000, 300_000, 330_000},
      {270_000, 300_000, 330_000},
      {270_000, 300_000, 330_000}
    };
    int[] jitter = {-100, 0, 100};
    for (int attempt = 0; attempt < previousAttempts.length; attempt++) {
      for (int boundary = 0; boundary < jitter.length; boundary++) {
        int injectedJitter = jitter[boundary];
        JdbcOutboxRepository repository = new JdbcOutboxRepository(() -> injectedJitter);
        long id = enqueue(repository, uuid(1_500 + attempt * 3L + boundary), NOW);
        executeApp(
            "update schubert.mq_outbox set attempt_count="
                + previousAttempts[attempt]
                + " where id="
                + id);
        try (Connection connection = transaction()) {
          OutboxEntry claimed = repository.claim(connection, "jitter", NOW, 1).getFirst();
          assertEquals(id, claimed.id());
          assertTrue(
              repository.markFailure(
                  connection, claimed, NOW, FIXTURE_JMS_FAIL_B8C3E123, "redacted"));
          connection.commit();
        }
        assertEquals(
            Integer.toString(persistedAttempts[attempt]), text(id, FIXTURE_ATTEMPT_COUNT_87388C12));
        assertEquals(
            NOW.plusMillis(expectedMillis[attempt][boundary]),
            timestamp(id, FIXTURE_NEXT_ATTEMPT_AT_BFB0B802));
        assertEquals(FIXTURE_ERROR_F717E7D8, text(id, FIXTURE_STATUS_CFC31BCC));
      }
    }
    JdbcOutboxRepository randomRepository = new JdbcOutboxRepository();
    long randomId = enqueue(randomRepository, uuid(1_600), NOW);
    try (Connection connection = transaction()) {
      OutboxEntry claimed = randomRepository.claim(connection, "random-jitter", NOW, 1).getFirst();
      assertEquals(randomId, claimed.id());
      assertTrue(
          randomRepository.markFailure(
              connection, claimed, NOW, FIXTURE_JMS_FAIL_B8C3E123, "redacted"));
      connection.commit();
    }
    Instant randomDue = timestamp(randomId, FIXTURE_NEXT_ATTEMPT_AT_BFB0B802);
    assertFalse(randomDue.isBefore(Instant.parse("2026-09-05T00:00:00.900Z")));
    assertFalse(randomDue.isAfter(Instant.parse("2026-09-05T00:00:01.100Z")));
  }

  private static Clock observingClock(AtomicReference<Instant> observedTime) {
    return new Clock() {
      @Override
      public ZoneId getZone() {
        return ZoneOffset.UTC;
      }

      @Override
      public Clock withZone(ZoneId zone) {
        return Clock.fixed(instant(), zone);
      }

      @Override
      public Instant instant() {
        return observedTime.get();
      }
    };
  }

  @Test
  void claimsOnlyDueExpiredRowsWithTenSecondLeaseLimitAndNoDispatcherOverlap() throws Exception {
    JdbcOutboxRepository repository = new JdbcOutboxRepository(() -> 0);
    long duePending = enqueue(repository, uuid(1), NOW.minusSeconds(2));
    long dueError = enqueue(repository, uuid(2), NOW.minusSeconds(1));
    long future = enqueue(repository, uuid(3), NOW.plusSeconds(1));
    long activeLease = enqueue(repository, uuid(4), NOW.minusSeconds(3));
    long expiredLease = enqueue(repository, uuid(5), NOW.minusSeconds(4));
    long boundaryLease = enqueue(repository, uuid(6), NOW.minusSeconds(5));
    executeApp("update schubert.mq_outbox set status='ERROR',attempt_count=2 where id=" + dueError);
    lease(activeLease, "active", NOW.plusSeconds(1));
    lease(expiredLease, "expired", NOW.minusMillis(1));
    lease(boundaryLease, "boundary", NOW);

    try (Connection first = transaction();
        Connection second = transaction()) {
      List<OutboxEntry> firstClaims = repository.claim(first, "worker-a", NOW, 2);
      List<OutboxEntry> secondClaims = repository.claim(second, "worker-b", NOW, 100);
      assertEquals(
          List.of(expiredLease, duePending), firstClaims.stream().map(OutboxEntry::id).toList());
      assertEquals(List.of(dueError), secondClaims.stream().map(OutboxEntry::id).toList());
      assertTrue(disjoint(firstClaims, secondClaims));
      assertEquals(NOW.plusSeconds(10), firstClaims.getFirst().leaseUntil());
      assertEquals("worker-a", firstClaims.getFirst().leaseOwner());
      first.commit();
      second.commit();
    }
    assertEquals("PENDING", text(future, FIXTURE_STATUS_CFC31BCC));
    assertEquals("active", text(activeLease, FIXTURE_LEASE_OWNER_6418FA0F));
    assertEquals("boundary", text(boundaryLease, FIXTURE_LEASE_OWNER_6418FA0F));

    resetDatabase();
    for (int index = 0; index < 102; index++) {
      enqueue(repository, uuid(100 + index), NOW);
    }
    try (Connection connection = transaction()) {
      assertEquals(100, repository.claim(connection, "worker-max", NOW, 100).size());
      connection.commit();
    }
    try (Connection connection = transaction()) {
      assertEquals(2, repository.claim(connection, "worker-rest", NOW, 100).size());
      connection.commit();
    }
  }

  @Test
  void markSentAndFailureRequireLeaseAndUseExactBoundedRetryState() throws Exception {
    JdbcOutboxRepository repository = new JdbcOutboxRepository(() -> 0);
    long id = enqueue(repository, MESSAGE, NOW);
    OutboxEntry claimed;
    try (Connection connection = transaction()) {
      claimed = repository.claim(connection, "worker-a", NOW, 1).getFirst();
      connection.commit();
    }
    try (Connection connection = transaction()) {
      assertFalse(repository.markSent(connection, withWorker(claimed, "wrong"), NOW));
      assertFalse(
          repository.markFailure(
              connection,
              withWorker(claimed, "wrong"),
              NOW,
              FIXTURE_JMS_FAIL_B8C3E123,
              "public detail"));
      connection.commit();
    }
    try (Connection connection = transaction()) {
      assertTrue(
          repository.markFailure(
              connection, claimed, NOW, FIXTURE_JMS_FAIL_B8C3E123, "public detail"));
      connection.commit();
    }
    assertEquals(FIXTURE_ERROR_F717E7D8, text(id, FIXTURE_STATUS_CFC31BCC));
    assertEquals("1", text(id, FIXTURE_ATTEMPT_COUNT_87388C12));
    assertEquals(NOW.plusSeconds(1), timestamp(id, FIXTURE_NEXT_ATTEMPT_AT_BFB0B802));
    assertNull(textNullable(id, FIXTURE_LEASE_OWNER_6418FA0F));
    assertEquals(FIXTURE_JMS_FAIL_B8C3E123, text(id, FIXTURE_LAST_ERROR_CODE_BF1A4C63));

    try (Connection connection = transaction()) {
      OutboxEntry retry =
          repository.claim(connection, "worker-b", NOW.plusSeconds(1), 1).getFirst();
      assertTrue(repository.markSent(connection, retry, NOW.plusSeconds(2)));
      connection.commit();
    }
    assertEquals(FIXTURE_SENT_6C701E27, text(id, FIXTURE_STATUS_CFC31BCC));
    assertEquals(NOW.plusSeconds(2), timestamp(id, FIXTURE_SENT_AT_C13E7660));
    assertNull(textNullable(id, FIXTURE_LAST_ERROR_CODE_BF1A4C63));
    assertNull(textNullable(id, "last_error_detail"));

    long capped = enqueue(repository, uuid(500), NOW);
    executeApp("update schubert.mq_outbox set status='ERROR',attempt_count=100 where id=" + capped);
    try (Connection connection = transaction()) {
      OutboxEntry retry = repository.claim(connection, "worker-cap", NOW, 1).getFirst();
      assertTrue(repository.markFailure(connection, retry, NOW, "CAP", "bounded"));
      connection.commit();
    }
    assertEquals("100", text(capped, FIXTURE_ATTEMPT_COUNT_87388C12));
    assertEquals(NOW.plusSeconds(300), timestamp(capped, FIXTURE_NEXT_ATTEMPT_AT_BFB0B802));
  }

  @Test
  void dispatcherPersistsBothDestinationsAndArtemisSuppressesSendMarkCrashDuplicate(
      @TempDir Path root) throws Exception {
    EmbeddedActiveMQ broker = startBroker(root);
    try (ActiveMQConnectionFactory factory = new ActiveMQConnectionFactory(FIXTURE_VM_0_0C76084A);
        JMSContext observer = factory.createContext(JMSContext.AUTO_ACKNOWLEDGE);
        JMSConsumer work = observer.createConsumer(queue(FIXTURE_NK_ASYNC_WORK_F9720513));
        JMSConsumer dlq = observer.createConsumer(queue("nk.dead.letter"))) {
      JdbcOutboxRepository repository = new JdbcOutboxRepository(() -> 0);
      enqueue(
          repository,
          request(MESSAGE, OutboxDestination.ASYNC_WORK, eventWire(MESSAGE, CORRELATION)));
      UUID dlqId = uuid(700);
      enqueue(repository, dlqRequest(dlqId));
      OutboxDispatcher dispatcher =
          dispatcher(repository, () -> factory.createContext(JMSContext.SESSION_TRANSACTED));
      OutboxDispatchReport report = dispatcher.dispatch("worker-send", 100);
      assertEquals(new OutboxDispatchReport(2, 2, 0, 0), report);
      assertEquals(new OutboxDispatchReport(0, 0, 0, 0), dispatcher.dispatch("worker-empty", 100));

      BytesMessage workMessage = assertInstanceOf(BytesMessage.class, work.receive(5_000));
      BytesMessage dlqMessage = assertInstanceOf(BytesMessage.class, dlq.receive(5_000));
      assertMessage(workMessage, MESSAGE, eventWire(MESSAGE, CORRELATION));
      assertDlqMessage(dlqMessage, dlqId);
      assertNull(work.receive(250));
      assertNull(dlq.receive(250));

      resetDatabase();
      UUID crashId = uuid(701);
      long crashRow =
          enqueue(
              repository,
              request(crashId, OutboxDestination.ASYNC_WORK, eventWire(crashId, CORRELATION)));
      AtomicInteger commits = new AtomicInteger();
      TransactedJmsContextProvider crashAfterSend =
          () ->
              afterCommit(
                  factory.createContext(JMSContext.SESSION_TRANSACTED),
                  () -> lease(crashRow, "worker-recovery", NOW.minusSeconds(1)),
                  commits);
      OutboxDispatchReport crash =
          dispatcher(repository, crashAfterSend).dispatch("worker-crash", 1);
      assertEquals(new OutboxDispatchReport(1, 0, 0, 1), crash);
      assertEquals(1, commits.get());
      OutboxDispatchReport recovered =
          dispatcher(repository, () -> factory.createContext(JMSContext.SESSION_TRANSACTED))
              .dispatch("worker-recovery", 1);
      assertEquals(new OutboxDispatchReport(1, 1, 0, 0), recovered);
      BytesMessage one = assertInstanceOf(BytesMessage.class, work.receive(5_000));
      assertEquals(crashId.toString(), one.getStringProperty("_AMQ_DUPL_ID"));
      assertNull(work.receive(500));
      assertEquals(FIXTURE_SENT_6C701E27, text(crashRow, FIXTURE_STATUS_CFC31BCC));

      resetDatabase();
      UUID markId = uuid(702);
      long markRow =
          enqueue(
              repository,
              request(markId, OutboxDestination.ASYNC_WORK, eventWire(markId, CORRELATION)));
      AtomicInteger opens = new AtomicInteger();
      OutboxDispatcher markCommitFailure =
          new OutboxDispatcher(
              () ->
                  opens.getAndIncrement() == 0
                      ? appConnection()
                      : commitFailureConnection(appConnection(), false),
              () -> factory.createContext(JMSContext.SESSION_TRANSACTED),
              repository,
              new OutboxJmsSender(),
              CLOCK);
      assertThrows(SQLException.class, () -> markCommitFailure.dispatch("worker-mark", 1));
      assertEquals("PENDING", text(markRow, FIXTURE_STATUS_CFC31BCC));
      assertInstanceOf(BytesMessage.class, work.receive(5_000));

      OutboxSendException commitFailure =
          assertThrows(
              OutboxSendException.class,
              () ->
                  new OutboxJmsSender()
                      .send(
                          () ->
                              commitFailureJmsContext(
                                  factory.createContext(JMSContext.SESSION_TRANSACTED)),
                          sample()));
      assertEquals("outbox JMS commit was not confirmed", commitFailure.getMessage());
      assertEquals(
          FIXTURE_SYNTHETIC_COMMIT_FAILURE_D03EA83F, commitFailure.getCause().getMessage());
      assertNull(work.receive(250));
    } finally {
      broker.stop();
    }
  }

  @Test
  void dispatcherTurnsJmsAndStoredWireFailuresIntoRedactedRetryWithoutSend(@TempDir Path root)
      throws Exception {
    EmbeddedActiveMQ broker = startBroker(root);
    try (ActiveMQConnectionFactory factory = new ActiveMQConnectionFactory(FIXTURE_VM_0_0C76084A);
        JMSContext observer = factory.createContext(JMSContext.AUTO_ACKNOWLEDGE);
        JMSConsumer work = observer.createConsumer(queue(FIXTURE_NK_ASYNC_WORK_F9720513))) {
      JdbcOutboxRepository repository = new JdbcOutboxRepository(() -> 0);
      long jmsFailure = enqueue(repository, MESSAGE, NOW);
      OutboxDispatcher broken = dispatcher(repository, () -> failingJmsContext(false));
      assertEquals(new OutboxDispatchReport(1, 0, 1, 0), broken.dispatch("worker-jms", 1));
      assertEquals("JMS_SEND_FAILURE", text(jmsFailure, FIXTURE_LAST_ERROR_CODE_BF1A4C63));
      assertEquals("outbox send was not confirmed", text(jmsFailure, "last_error_detail"));
      assertFalse(text(jmsFailure, "last_error_detail").contains(MESSAGE.toString()));
      assertNull(work.receive(250));

      resetDatabase();
      long stolen = enqueue(repository, uuid(750), NOW);
      OutboxDispatcher leaseLost =
          dispatcher(
              repository,
              () -> {
                leaseUnchecked(stolen, "other-worker", NOW.plusSeconds(10));
                return failingJmsContext(false);
              });
      assertEquals(new OutboxDispatchReport(1, 0, 0, 1), leaseLost.dispatch("worker-stolen", 1));
      assertEquals("other-worker", text(stolen, FIXTURE_LEASE_OWNER_6418FA0F));

      resetDatabase();
      enqueue(repository, uuid(751), NOW);
      AtomicInteger opens = new AtomicInteger();
      OutboxDispatcher retryCommitFailure =
          new OutboxDispatcher(
              () ->
                  opens.getAndIncrement() == 0
                      ? appConnection()
                      : commitFailureConnection(appConnection(), false),
              () -> failingJmsContext(false),
              repository,
              new OutboxJmsSender(),
              CLOCK);
      assertThrows(SQLException.class, () -> retryCommitFailure.dispatch("worker-retry-mark", 1));

      resetDatabase();
      byte[] damaged = eventWire(MESSAGE, CORRELATION);
      damaged[0] = 'X';
      long integrity = enqueue(repository, request(MESSAGE, OutboxDestination.ASYNC_WORK, damaged));
      OutboxDispatcher dispatcher =
          dispatcher(repository, () -> factory.createContext(JMSContext.SESSION_TRANSACTED));
      assertEquals(
          new OutboxDispatchReport(1, 0, 1, 0), dispatcher.dispatch("worker-integrity", 1));
      assertEquals("OUTBOX_INTEGRITY", text(integrity, FIXTURE_LAST_ERROR_CODE_BF1A4C63));
      assertNull(work.receive(250));
    } finally {
      broker.stop();
    }
  }

  @Test
  void publicBoundariesRejectNullModesBoundsErrorsAndEveryWireIdentityMutation() throws Exception {
    JdbcOutboxRepository repository = new JdbcOutboxRepository(() -> 0);
    OutboxRequest request =
        request(MESSAGE, OutboxDestination.ASYNC_WORK, eventWire(MESSAGE, CORRELATION));
    assertThrows(NullPointerException.class, () -> repository.enqueue(null, request));
    try (Connection autoCommit = appConnection()) {
      assertThrows(IllegalStateException.class, () -> repository.enqueue(autoCommit, request));
      assertThrows(IllegalStateException.class, () -> repository.claim(autoCommit, "w", NOW, 1));
      assertThrows(
          IllegalStateException.class, () -> repository.markSent(autoCommit, sample(), NOW));
      assertThrows(
          IllegalStateException.class,
          () -> repository.markFailure(autoCommit, sample(), NOW, "E", "D"));
    }
    try (Connection connection = transaction()) {
      assertThrows(NullPointerException.class, () -> repository.enqueue(connection, null));
      assertThrows(NullPointerException.class, () -> repository.claim(connection, null, NOW, 1));
      assertThrows(IllegalArgumentException.class, () -> repository.claim(connection, " ", NOW, 1));
      assertThrows(
          IllegalArgumentException.class,
          () -> repository.claim(connection, "x".repeat(65), NOW, 1));
      assertThrows(NullPointerException.class, () -> repository.claim(connection, "w", null, 1));
      assertThrows(IllegalArgumentException.class, () -> repository.claim(connection, "w", NOW, 0));
      assertThrows(
          IllegalArgumentException.class, () -> repository.claim(connection, "w", NOW, 101));
      assertThrows(NullPointerException.class, () -> repository.markSent(connection, null, NOW));
      assertThrows(
          NullPointerException.class, () -> repository.markSent(connection, sample(), null));
      assertThrows(
          NullPointerException.class,
          () -> repository.markFailure(connection, null, NOW, "E", "D"));
      assertThrows(
          NullPointerException.class,
          () -> repository.markFailure(connection, sample(), null, "E", "D"));
      assertThrows(
          NullPointerException.class,
          () -> repository.markFailure(connection, sample(), NOW, null, "D"));
      assertThrows(
          IllegalArgumentException.class,
          () -> repository.markFailure(connection, sample(), NOW, " ", "D"));
      assertThrows(
          IllegalArgumentException.class,
          () -> repository.markFailure(connection, sample(), NOW, "x".repeat(65), "D"));
      assertThrows(
          IllegalArgumentException.class,
          () -> repository.markFailure(connection, sample(), NOW, "X\n", "D"));
      assertThrows(
          NullPointerException.class,
          () -> repository.markFailure(connection, sample(), NOW, "E", null));
      assertThrows(
          IllegalArgumentException.class,
          () -> repository.markFailure(connection, sample(), NOW, "E", " "));
      assertThrows(
          IllegalArgumentException.class,
          () -> repository.markFailure(connection, sample(), NOW, "E", "x".repeat(257)));
      assertThrows(
          IllegalArgumentException.class,
          () -> repository.markFailure(connection, sample(), NOW, "E", "X\n"));
      connection.rollback();
    }

    OutboxJmsSender sender = new OutboxJmsSender();
    OutboxEntry valid = sample();
    assertThrows(NullPointerException.class, () -> sender.send(null, valid));
    assertThrows(
        NullPointerException.class, () -> sender.send(() -> failingJmsContext(false), null));
    assertThrows(OutboxSendException.class, () -> sender.send(() -> null, valid));
    assertThrows(
        OutboxSendException.class,
        () -> sender.send(() -> jmsContext(JMSContext.AUTO_ACKNOWLEDGE), valid));

    assertIntegrity(
        sender,
        withIdentity(
            valid,
            uuid(900),
            CORRELATION,
            FIXTURE_QWKREQ01_19741256,
            FIXTURE_001_A3FEAA64,
            valid.body(),
            OutboxDestination.ASYNC_WORK));
    assertIntegrity(
        sender,
        withIdentity(
            valid,
            MESSAGE,
            uuid(901),
            FIXTURE_QWKREQ01_19741256,
            FIXTURE_001_A3FEAA64,
            valid.body(),
            OutboxDestination.ASYNC_WORK));
    assertIntegrity(
        sender,
        withIdentity(
            valid,
            MESSAGE,
            CORRELATION,
            "WLGEVT01",
            FIXTURE_001_A3FEAA64,
            valid.body(),
            OutboxDestination.ASYNC_WORK));
    assertIntegrity(
        sender,
        withIdentity(
            valid,
            MESSAGE,
            CORRELATION,
            FIXTURE_QWKREQ01_19741256,
            "002",
            valid.body(),
            OutboxDestination.ASYNC_WORK));
    assertIntegrity(
        sender,
        withIdentity(
            valid,
            MESSAGE,
            CORRELATION,
            FIXTURE_QWKREQ01_19741256,
            FIXTURE_001_A3FEAA64,
            Arrays.copyOf(valid.body(), 321),
            OutboxDestination.ASYNC_WORK));
    assertIntegrity(
        sender,
        withIdentity(
            valid,
            MESSAGE,
            CORRELATION,
            "LGSRSP01",
            FIXTURE_001_A3FEAA64,
            largeWire(),
            OutboxDestination.ASYNC_WORK));
    byte[] syncRequest = smallRequestWire();
    assertIntegrity(
        sender,
        withIdentity(
            valid,
            MESSAGE,
            MESSAGE,
            "LOGREQ01",
            FIXTURE_001_A3FEAA64,
            syncRequest,
            OutboxDestination.ASYNC_WORK));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            withIdentity(
                valid,
                MESSAGE,
                MESSAGE,
                "LOGREQ01",
                FIXTURE_001_A3FEAA64,
                syncRequest,
                OutboxDestination.DLQ));

    OutboxSendException sendFailure =
        assertThrows(
            OutboxSendException.class, () -> sender.send(() -> failingJmsContext(true), valid));
    assertEquals("outbox JMS send was not confirmed", sendFailure.getMessage());
    assertEquals(1, sendFailure.getCause().getSuppressed().length);
    assertInstanceOf(JMSRuntimeException.class, sendFailure.getCause().getSuppressed()[0]);

    OutboxSendException checked =
        assertThrows(
            OutboxSendException.class,
            () -> sender.send(OutboxDispatcherTest::checkedFailingJmsContext, valid));
    assertEquals("synthetic checked failure", checked.getCause().getMessage());

    assertTrue(
        OutboxJmsSender.isDuplicateConfirmation(
            new ActiveMQDuplicateIdException("synthetic duplicate")));
    JMSException linked = new JMSException("linked wrapper");
    linked.setLinkedException(new ActiveMQDuplicateIdException("synthetic linked duplicate"));
    assertTrue(
        OutboxJmsSender.isDuplicateConfirmation(
            new JMSRuntimeException("runtime wrapper", null, linked)));
    assertFalse(OutboxJmsSender.isDuplicateConfirmation(new JMSException("no link")));
    assertFalse(OutboxJmsSender.isDuplicateConfirmation(new SelfLinkedJmsException()));
    assertFalse(OutboxJmsSender.isDuplicateConfirmation(new SelfCausedRuntimeException()));

    try (Connection connection = transaction()) {
      assertThrows(
          OutboxIntegrityException.class,
          () -> JdbcOutboxRepository.read(invalidDestinationResult()));
      assertThrows(
          OutboxIntegrityException.class,
          () -> repository.enqueue(emptyInsertConnection(connection), request));
      connection.rollback();
    }

    assertThrows(
        NullPointerException.class,
        () -> new OutboxDispatcher(null, () -> jmsContext(0), repository, sender, CLOCK));
    assertThrows(
        NullPointerException.class,
        () ->
            new OutboxDispatcher(
                OutboxDispatcherTest::appConnection, null, repository, sender, CLOCK));
    assertThrows(
        NullPointerException.class,
        () ->
            new OutboxDispatcher(
                OutboxDispatcherTest::appConnection, () -> jmsContext(0), null, sender, CLOCK));
    assertThrows(
        NullPointerException.class,
        () ->
            new OutboxDispatcher(
                OutboxDispatcherTest::appConnection, () -> jmsContext(0), repository, null, CLOCK));
    OutboxDispatcher dispatcher =
        dispatcher(repository, () -> jmsContext(JMSContext.SESSION_TRANSACTED));
    assertThrows(NullPointerException.class, () -> dispatcher.dispatch(null, 1));
    assertThrows(
        NullPointerException.class,
        () ->
            new OutboxDispatcher(
                OutboxDispatcherTest::appConnection,
                () -> jmsContext(0),
                repository,
                sender,
                null));
    assertThrows(
        NullPointerException.class,
        () ->
            new OutboxDispatcher(
                    () -> null,
                    () -> jmsContext(JMSContext.SESSION_TRANSACTED),
                    repository,
                    sender,
                    CLOCK)
                .dispatch("w", 1));
    SQLException setupFailure =
        assertThrows(
            SQLException.class,
            () ->
                new OutboxDispatcher(
                        OutboxDispatcherTest::setAutoCommitAndCloseFailure,
                        () -> jmsContext(JMSContext.SESSION_TRANSACTED),
                        repository,
                        sender,
                        CLOCK)
                    .dispatch("w", 1));
    assertEquals(1, setupFailure.getSuppressed().length);
    assertEquals("synthetic setup failure", setupFailure.getMessage());
    Connection closeNormally = appConnection();
    IllegalStateException original = new IllegalStateException("synthetic original");
    OutboxDispatcher.closeAfterSetupFailure(closeNormally, original);
    assertTrue(closeNormally.isClosed());
    assertEquals(0, original.getSuppressed().length);

    SQLException claimFailure =
        assertThrows(
            SQLException.class,
            () ->
                new OutboxDispatcher(
                        () -> commitFailureConnection(appConnection(), false),
                        () -> jmsContext(JMSContext.SESSION_TRANSACTED),
                        repository,
                        sender,
                        CLOCK)
                    .dispatch("worker-claim-failure", 1));
    assertEquals(FIXTURE_SYNTHETIC_COMMIT_FAILURE_D03EA83F, claimFailure.getMessage());
    SQLException rollbackFailure =
        assertThrows(
            SQLException.class,
            () ->
                new OutboxDispatcher(
                        () -> commitFailureConnection(appConnection(), true),
                        () -> jmsContext(JMSContext.SESSION_TRANSACTED),
                        repository,
                        sender,
                        CLOCK)
                    .dispatch("worker-rollback-failure", 1));
    assertEquals(1, rollbackFailure.getSuppressed().length);
  }

  @Test
  void idem010r01SameProviderFailureOnStageAndRollbackKeepsOriginalCause() {
    JMSRuntimeException primary = new JMSRuntimeException("synthetic-shared-provider-failure");
    AtomicInteger rollbacks = new AtomicInteger();
    AtomicInteger closes = new AtomicInteger();
    JMSContext context =
        (JMSContext)
            Proxy.newProxyInstance(
                JMSContext.class.getClassLoader(),
                new Class<?>[] {JMSContext.class},
                (ignored, method, args) ->
                    switch (method.getName()) {
                      case FIXTURE_GETSESSIONMODE_BF25AD1A -> JMSContext.SESSION_TRANSACTED;
                      case FIXTURE_CREATEBYTESMESSAGE_F47217B2 -> throw primary;
                      case FIXTURE_ROLLBACK_3770B198 -> {
                        rollbacks.incrementAndGet();
                        throw primary;
                      }
                      case FIXTURE_CLOSE_97959247 -> {
                        closes.incrementAndGet();
                        yield null;
                      }
                      default -> throw new AssertionError(method.getName());
                    });
    OutboxSendException failure =
        assertThrows(
            OutboxSendException.class, () -> new OutboxJmsSender().send(() -> context, sample()));
    assertEquals("outbox JMS send was not confirmed", failure.getMessage());
    assertSame(primary, failure.getCause());
    assertEquals(0, primary.getSuppressed().length);
    assertEquals(1, rollbacks.get());
    assertEquals(1, closes.get());
  }

  @Test
  void idem010r02SameProviderFailureOnSessionModeAndCloseKeepsOriginalCause() {
    JMSRuntimeException primary = new JMSRuntimeException("synthetic-shared-provider-failure");
    AtomicInteger closes = new AtomicInteger();
    JMSContext context =
        (JMSContext)
            Proxy.newProxyInstance(
                JMSContext.class.getClassLoader(),
                new Class<?>[] {JMSContext.class},
                (ignored, method, args) ->
                    switch (method.getName()) {
                      case FIXTURE_GETSESSIONMODE_BF25AD1A -> throw primary;
                      case FIXTURE_CLOSE_97959247 -> {
                        closes.incrementAndGet();
                        throw primary;
                      }
                      case FIXTURE_TOSTRING_5F8C6B3F -> "synthetic-context";
                      default -> throw new AssertionError(method.getName());
                    });
    OutboxSendException failure =
        assertThrows(
            OutboxSendException.class, () -> new OutboxJmsSender().send(() -> context, sample()));
    assertEquals("outbox JMS context lifecycle failed", failure.getMessage());
    assertSame(primary, failure.getCause());
    assertEquals(0, primary.getSuppressed().length);
    assertEquals(1, closes.get());
  }

  @Test
  void idem010r03DistinctSessionModeAndCloseFailuresKeepFixedPrimary() {
    JMSRuntimeException primary = new JMSRuntimeException("synthetic-mode-failure");
    JMSRuntimeException secondary = new JMSRuntimeException("synthetic-close-failure");
    AtomicInteger closes = new AtomicInteger();
    JMSContext context =
        (JMSContext)
            Proxy.newProxyInstance(
                JMSContext.class.getClassLoader(),
                new Class<?>[] {JMSContext.class},
                (ignored, method, args) ->
                    switch (method.getName()) {
                      case FIXTURE_GETSESSIONMODE_BF25AD1A -> throw primary;
                      case FIXTURE_CLOSE_97959247 -> {
                        closes.incrementAndGet();
                        throw secondary;
                      }
                      case FIXTURE_TOSTRING_5F8C6B3F -> "synthetic-context";
                      default -> throw new AssertionError(method.getName());
                    });
    OutboxSendException failure =
        assertThrows(
            OutboxSendException.class, () -> new OutboxJmsSender().send(() -> context, sample()));
    assertEquals("outbox JMS context lifecycle failed", failure.getMessage());
    assertSame(primary, failure.getCause());
    assertEquals(1, failure.getSuppressed().length);
    assertSame(secondary, failure.getSuppressed()[0]);
    assertEquals(1, closes.get());
  }

  @Test
  void idem010r04FatalSessionModeAndCloseKeepFatalIdentity() {
    AssertionError primary = new AssertionError("synthetic-fatal-mode");
    for (boolean same : new boolean[] {true, false}) {
      AssertionError secondary = same ? primary : new AssertionError("synthetic-fatal-close");
      AtomicInteger closes = new AtomicInteger();
      JMSContext context =
          (JMSContext)
              Proxy.newProxyInstance(
                  JMSContext.class.getClassLoader(),
                  new Class<?>[] {JMSContext.class},
                  (ignored, method, args) ->
                      switch (method.getName()) {
                        case FIXTURE_GETSESSIONMODE_BF25AD1A -> throw primary;
                        case FIXTURE_CLOSE_97959247 -> {
                          closes.incrementAndGet();
                          throw secondary;
                        }
                        case FIXTURE_TOSTRING_5F8C6B3F -> "synthetic-context";
                        default -> throw new AssertionError(method.getName());
                      });
      assertSame(
          primary,
          assertThrows(
              AssertionError.class, () -> new OutboxJmsSender().send(() -> context, sample())));
      assertEquals(1, closes.get());
      assertEquals(same ? 0 : 1, primary.getSuppressed().length);
      if (!same) assertSame(secondary, primary.getSuppressed()[0]);
    }
  }

  @Test
  void idem010r05CommittedSendCloseRuntimeAndFatalNeverReturnSuccess(@TempDir Path root)
      throws Exception {
    EmbeddedActiveMQ broker = startBroker(root);
    try (ActiveMQConnectionFactory factory = new ActiveMQConnectionFactory(FIXTURE_VM_0_0C76084A)) {
      JMSRuntimeException runtime = new JMSRuntimeException("synthetic-close-after-commit");
      JMSContext first =
          closingContext(factory.createContext(JMSContext.SESSION_TRANSACTED), runtime);
      OutboxSendException failure =
          assertThrows(
              OutboxSendException.class, () -> new OutboxJmsSender().send(() -> first, sample()));
      assertEquals("outbox JMS context lifecycle failed", failure.getMessage());
      assertSame(runtime, failure.getCause());
      AssertionError fatal = new AssertionError("synthetic-fatal-close-after-commit");
      UUID next = uuid(902);
      OutboxEntry second =
          withIdentity(
              sample(),
              next,
              CORRELATION,
              FIXTURE_QWKREQ01_19741256,
              FIXTURE_001_A3FEAA64,
              eventWire(next, CORRELATION),
              OutboxDestination.ASYNC_WORK);
      JMSContext after =
          closingContext(factory.createContext(JMSContext.SESSION_TRANSACTED), fatal);
      assertSame(
          fatal,
          assertThrows(
              AssertionError.class, () -> new OutboxJmsSender().send(() -> after, second)));
    } finally {
      broker.stop();
    }
  }

  private static JMSContext closingContext(JMSContext delegate, Throwable closing) {
    return (JMSContext)
        Proxy.newProxyInstance(
            JMSContext.class.getClassLoader(),
            new Class<?>[] {JMSContext.class},
            (ignored, method, args) -> {
              if (method.getName().equals(FIXTURE_CLOSE_97959247)) {
                delegate.close();
                if (closing instanceof Error fatal) throw fatal;
                throw closing;
              }
              return invoke(delegate, method, args);
            });
  }

  @Test
  void persistedQwkPayloadIsFullyDecodedBeforeOpeningJms() {
    // PT-IDEM-011 / BUG-010: expected offsets and values come directly from SS 323.
    OutboxEntry valid = sample();
    byte[] golden = valid.body();
    assertEquals(320, golden.length);
    assertEquals(
        "01ARZ3NDEKTSV4RRFFQ69G5FAV", new String(golden, 256, 26, StandardCharsets.US_ASCII));
    assertEquals(
        "000000000001000000000002", new String(golden, 282, 24, StandardCharsets.US_ASCII));
    assertEquals(" ".repeat(14), new String(golden, 306, 14, StandardCharsets.US_ASCII));
    OutboxJmsSender.validateWireIdentity(valid);
    List<byte[]> invalid = new ArrayList<>();
    byte[] blank = golden.clone();
    Arrays.fill(blank, 256, 320, (byte) ' ');
    invalid.add(blank);
    for (int offset : new int[] {256, 282, 294}) {
      byte[] missing = golden.clone();
      Arrays.fill(missing, offset, offset + (offset == 256 ? 26 : 12), (byte) ' ');
      invalid.add(missing);
    }
    for (int offset : new int[] {282, 294}) {
      byte[] zeroId = golden.clone();
      ascii(zeroId, offset, "000000000000");
      invalid.add(zeroId);
      byte[] nonNumeric = golden.clone();
      nonNumeric[offset] = 'X';
      invalid.add(nonNumeric);
    }
    for (int[] mutation :
        new int[][] {{256, 'I'}, {256, 0}, {256, 0xff}, {256, '\n'}, {306, 'X'}, {319, 0}}) {
      byte[] altered = golden.clone();
      altered[mutation[0]] = (byte) mutation[1];
      invalid.add(altered);
    }
    for (OutboxDestination destination : OutboxDestination.values()) {
      for (byte[] body : invalid) {
        assertIntegrity(
            new OutboxJmsSender(),
            destination == OutboxDestination.DLQ
                ? new OutboxEntry(
                    1,
                    uuid(801),
                    CORRELATION,
                    destination,
                    FIXTURE_QWKREQ01_19741256,
                    FIXTURE_001_A3FEAA64,
                    body,
                    0,
                    NOW,
                    NOW.minusSeconds(30),
                    "worker",
                    NOW.plusSeconds(10),
                    dlqRequest(uuid(801)).dlqMetadata())
                : withIdentity(
                    valid,
                    MESSAGE,
                    CORRELATION,
                    FIXTURE_QWKREQ01_19741256,
                    FIXTURE_001_A3FEAA64,
                    body,
                    destination));
      }
    }
  }

  private static OutboxDispatcher dispatcher(
      JdbcOutboxRepository repository, TransactedJmsContextProvider jms) {
    return new OutboxDispatcher(
        OutboxDispatcherTest::appConnection, jms, repository, new OutboxJmsSender(), CLOCK);
  }

  private static long enqueue(JdbcOutboxRepository repository, UUID message, Instant due)
      throws SQLException {
    // BUG-128: independent accepted questions need independent root correlations (UI231/232).
    UUID rootRequest =
        message.equals(MESSAGE)
            ? CORRELATION
            : new UUID(
                message.getMostSignificantBits() ^ 0x4000000000000000L,
                message.getLeastSignificantBits());
    return enqueue(
        repository,
        new OutboxRequest(
            message,
            rootRequest,
            OutboxDestination.ASYNC_WORK,
            FIXTURE_QWKREQ01_19741256,
            FIXTURE_001_A3FEAA64,
            eventWire(message, rootRequest),
            due,
            NOW.minusSeconds(30)));
  }

  private static long enqueue(JdbcOutboxRepository repository, OutboxRequest request)
      throws SQLException {
    try (Connection connection = transaction()) {
      long id = repository.enqueue(connection, request);
      connection.commit();
      return id;
    }
  }

  private static OutboxRequest request(UUID message, OutboxDestination destination, byte[] body) {
    return request(message, destination, body, NOW);
  }

  private static OutboxRequest request(
      UUID message, OutboxDestination destination, byte[] body, Instant due) {
    return new OutboxRequest(
        message,
        CORRELATION,
        destination,
        FIXTURE_QWKREQ01_19741256,
        FIXTURE_001_A3FEAA64,
        body,
        due,
        NOW.minusSeconds(30));
  }

  private static OutboxEntry sample() {
    return new OutboxEntry(
        1,
        MESSAGE,
        CORRELATION,
        OutboxDestination.ASYNC_WORK,
        FIXTURE_QWKREQ01_19741256,
        FIXTURE_001_A3FEAA64,
        eventWire(MESSAGE, CORRELATION),
        0,
        NOW,
        NOW.minusSeconds(30),
        "worker",
        NOW.plusSeconds(10));
  }

  private static OutboxRequest dlqRequest(UUID dispatchId) {
    return new OutboxRequest(
        dispatchId,
        CORRELATION,
        OutboxDestination.DLQ,
        FIXTURE_QWKREQ01_19741256,
        FIXTURE_001_A3FEAA64,
        eventWire(MESSAGE, CORRELATION),
        NOW,
        NOW.minusSeconds(30),
        Optional.of(
            new OutboxDlqMetadata(
                MESSAGE, "ID:independent-original", 4, "QUESTION_RETRY_EXHAUSTED", NOW)));
  }

  private static void assertDlqMessage(BytesMessage message, UUID dispatchId) throws Exception {
    assertArrayEquals(eventWire(MESSAGE, CORRELATION), body(message));
    assertEquals(MESSAGE.toString(), message.getStringProperty("NKMessageID"));
    assertEquals(dispatchId.toString(), message.getStringProperty("_AMQ_DUPL_ID"));
    assertEquals(CORRELATION.toString(), message.getJMSCorrelationID());
    assertEquals(CORRELATION.toString(), message.getStringProperty("NKCorrelationID"));
    assertEquals(FIXTURE_QWKREQ01_19741256, message.getStringProperty("NKLayoutID"));
    assertEquals(FIXTURE_001_A3FEAA64, message.getStringProperty("NKProtocolVersion"));
    assertEquals(FIXTURE_NK_ASYNC_WORK_F9720513, message.getStringProperty("_AMQ_ORIG_ADDRESS"));
    assertEquals("nk.async.work.q", message.getStringProperty("_AMQ_ORIG_QUEUE"));
    assertEquals("ID:independent-original", message.getStringProperty("NKOriginalTransportID"));
    assertEquals(4, message.getIntProperty("NKDeliveryCount"));
    assertEquals("QUESTION_RETRY_EXHAUSTED", message.getStringProperty("NKErrorCode"));
    assertEquals("API_WORK", message.getStringProperty("NKDetectedBy"));
    assertEquals("2026-09-05T00:00:00Z", message.getStringProperty("NKDetectedAt"));
    assertEquals(DeliveryMode.PERSISTENT, message.getJMSDeliveryMode());
    assertEquals(0L, message.getJMSExpiration());
  }

  @Test
  void dbResultBoundaryRejectsIncompleteOrMalformedDlqMetadataRatherThanDefaulting()
      throws Exception {
    var repository = new JdbcOutboxRepository(() -> 0);
    long id = enqueue(repository, dlqRequest(uuid(802)));
    lease(id, "worker", NOW.plusSeconds(10));
    try (var connection = appConnection();
        var statement =
            connection.prepareStatement(
                "select id,message_id,correlation_id,destination,layout_id,layout_version,body,attempt_count,"
                    + "next_attempt_at,created_at,lease_owner,lease_until,dlq_original_message_id,"
                    + "dlq_original_transport_id,dlq_delivery_count,dlq_error_code,dlq_detected_at "
                    + "from schubert.mq_outbox where id=?")) {
      statement.setLong(1, id);
      try (var result = statement.executeQuery()) {
        assertTrue(result.next());
        assertEquals(
            4, JdbcOutboxRepository.read(result).dlqMetadata().orElseThrow().deliveryCount());
        for (String column :
            List.of(
                FIXTURE_DLQ_ORIGINAL_MESSAGE_ID_7D1CCCBA,
                "dlq_original_transport_id",
                FIXTURE_DLQ_DELIVERY_COUNT_E5C288A9,
                "dlq_error_code",
                "dlq_detected_at")) {
          ResultSet absent =
              (ResultSet)
                  Proxy.newProxyInstance(
                      ResultSet.class.getClassLoader(),
                      new Class<?>[] {ResultSet.class},
                      (proxy, method, args) -> {
                        if ((method.getName().equals(FIXTURE_GETOBJECT_B6112877)
                                || method.getName().equals("getString"))
                            && args != null
                            && column.equals(args[0])) return null;
                        return invoke(result, method, args);
                      });
          if (column.equals(FIXTURE_DLQ_ORIGINAL_MESSAGE_ID_7D1CCCBA))
            assertThrows(OutboxIntegrityException.class, () -> JdbcOutboxRepository.read(absent));
          else
            assertEquals(
                "22004",
                assertThrows(SQLException.class, () -> JdbcOutboxRepository.read(absent))
                    .getSQLState());
        }
        ResultSet malformed =
            (ResultSet)
                Proxy.newProxyInstance(
                    ResultSet.class.getClassLoader(),
                    new Class<?>[] {ResultSet.class},
                    (proxy, method, args) -> {
                      if (method.getName().equals(FIXTURE_GETOBJECT_B6112877)
                          && args != null
                          && FIXTURE_DLQ_DELIVERY_COUNT_E5C288A9.equals(args[0])) return 0;
                      return invoke(result, method, args);
                    });
        assertThrows(OutboxIntegrityException.class, () -> JdbcOutboxRepository.read(malformed));
        List<String> dlqColumns =
            List.of(
                "dlq_original_transport_id",
                FIXTURE_DLQ_DELIVERY_COUNT_E5C288A9,
                "dlq_error_code",
                "dlq_detected_at");
        for (int visible = 0; visible <= dlqColumns.size(); visible++) {
          String visibleColumn = visible < dlqColumns.size() ? dlqColumns.get(visible) : "";
          ResultSet partial =
              (ResultSet)
                  Proxy.newProxyInstance(
                      ResultSet.class.getClassLoader(),
                      new Class<?>[] {ResultSet.class},
                      (proxy, method, args) -> {
                        if (method.getName().equals(FIXTURE_GETOBJECT_B6112877)
                            && args != null
                            && (FIXTURE_DLQ_ORIGINAL_MESSAGE_ID_7D1CCCBA.equals(args[0])
                                || dlqColumns.contains(args[0]) && !visibleColumn.equals(args[0])))
                          return null;
                        return invoke(result, method, args);
                      });
          assertThrows(OutboxIntegrityException.class, () -> JdbcOutboxRepository.read(partial));
        }
      }
    }
  }

  @Test
  void dlqDispatchCrashUsesNewStableDuplicateIdWithoutChangingOriginalWork(@TempDir Path root)
      throws Exception {
    EmbeddedActiveMQ broker = startBroker(root);
    try (ActiveMQConnectionFactory factory = new ActiveMQConnectionFactory(FIXTURE_VM_0_0C76084A);
        JMSContext observer = factory.createContext(JMSContext.AUTO_ACKNOWLEDGE);
        JMSConsumer dlq = observer.createConsumer(queue("nk.dead.letter"))) {
      JdbcOutboxRepository repository = new JdbcOutboxRepository(() -> 0);
      UUID dispatchId = uuid(800);
      long row = enqueue(repository, dlqRequest(dispatchId));
      AtomicInteger commits = new AtomicInteger();
      var crashing =
          dispatcher(
              repository,
              () ->
                  afterCommit(
                      factory.createContext(JMSContext.SESSION_TRANSACTED),
                      () -> lease(row, "dlq-recovery", NOW.minusSeconds(1)),
                      commits));
      assertEquals(new OutboxDispatchReport(1, 0, 0, 1), crashing.dispatch("dlq-crash", 1));
      assertEquals(1, commits.get());
      assertEquals(
          new OutboxDispatchReport(1, 1, 0, 0),
          dispatcher(repository, () -> factory.createContext(JMSContext.SESSION_TRANSACTED))
              .dispatch("dlq-recovery", 1));
      assertDlqMessage(assertInstanceOf(BytesMessage.class, dlq.receive(5000)), dispatchId);
      assertNull(dlq.receive(500));
      assertEquals(FIXTURE_SENT_6C701E27, text(row, FIXTURE_STATUS_CFC31BCC));
      assertEquals("ID:independent-original", text(row, "dlq_original_transport_id"));
      assertEquals("4", text(row, FIXTURE_DLQ_DELIVERY_COUNT_E5C288A9));
      assertEquals(MESSAGE.toString(), text(row, FIXTURE_DLQ_ORIGINAL_MESSAGE_ID_7D1CCCBA));
    } finally {
      broker.stop();
    }
  }

  private static OutboxEntry withWorker(OutboxEntry entry, String worker) {
    return withIdentity(
        entry,
        entry.messageId(),
        entry.correlationId(),
        entry.layoutId(),
        entry.layoutVersion(),
        entry.body(),
        entry.destination(),
        worker);
  }

  private static OutboxEntry withIdentity(
      OutboxEntry source,
      UUID message,
      UUID correlation,
      String layout,
      String version,
      byte[] body,
      OutboxDestination destination) {
    return withIdentity(
        source, message, correlation, layout, version, body, destination, source.leaseOwner());
  }

  private static OutboxEntry withIdentity(
      OutboxEntry source,
      UUID message,
      UUID correlation,
      String layout,
      String version,
      byte[] body,
      OutboxDestination destination,
      String worker) {
    return new OutboxEntry(
        source.id(),
        message,
        correlation,
        destination,
        layout,
        version,
        body,
        source.attemptCount(),
        source.nextAttemptAt(),
        source.createdAt(),
        worker,
        source.leaseUntil());
  }

  private static void assertIntegrity(OutboxJmsSender sender, OutboxEntry entry) {
    AtomicInteger opened = new AtomicInteger();
    assertThrows(
        OutboxIntegrityException.class,
        () ->
            sender.send(
                () -> {
                  opened.incrementAndGet();
                  return jmsContext(JMSContext.SESSION_TRANSACTED);
                },
                entry));
    assertEquals(
        0, opened.get(), "invalid persisted wire must fail before JMS context acquisition");
  }

  private static boolean disjoint(List<OutboxEntry> first, List<OutboxEntry> second) {
    Set<Long> ids = new HashSet<>(first.stream().map(OutboxEntry::id).toList());
    return second.stream().map(OutboxEntry::id).noneMatch(ids::contains);
  }

  private static void assertMessage(BytesMessage message, UUID id, byte[] expected)
      throws Exception {
    assertNotNull(message);
    assertArrayEquals(expected, body(message));
    assertEquals(CORRELATION.toString(), message.getJMSCorrelationID());
    assertEquals(id.toString(), message.getStringProperty("NKMessageID"));
    assertEquals(FIXTURE_QWKREQ01_19741256, message.getStringProperty("NKLayoutID"));
    assertEquals(FIXTURE_001_A3FEAA64, message.getStringProperty("NKProtocolVersion"));
    assertEquals(id.toString(), message.getStringProperty("_AMQ_DUPL_ID"));
    assertEquals(DeliveryMode.PERSISTENT, message.getJMSDeliveryMode());
    assertEquals(0L, message.getJMSExpiration());
  }

  private static byte[] body(BytesMessage message) throws JMSException {
    message.reset();
    byte[] result = new byte[Math.toIntExact(message.getBodyLength())];
    assertEquals(result.length, message.readBytes(result));
    return result;
  }

  private static JMSContext failingJmsContext(boolean rollbackFails) {
    return (JMSContext)
        Proxy.newProxyInstance(
            JMSContext.class.getClassLoader(),
            new Class<?>[] {JMSContext.class},
            (proxy, method, arguments) -> {
              return switch (method.getName()) {
                case FIXTURE_GETSESSIONMODE_BF25AD1A -> JMSContext.SESSION_TRANSACTED;
                case FIXTURE_CREATEBYTESMESSAGE_F47217B2 ->
                    throw new JMSRuntimeException("synthetic public failure");
                case FIXTURE_ROLLBACK_3770B198 -> {
                  if (rollbackFails) {
                    throw new JMSRuntimeException("synthetic rollback failure");
                  }
                  yield null;
                }
                case FIXTURE_CLOSE_97959247 -> null;
                case FIXTURE_TOSTRING_5F8C6B3F -> "FailingJmsContext";
                case FIXTURE_HASHCODE_613EE961 -> System.identityHashCode(proxy);
                case FIXTURE_EQUALS_7778BDDB -> proxy == arguments[0];
                default -> throw new UnsupportedOperationException(method.getName());
              };
            });
  }

  private static JMSContext checkedFailingJmsContext() {
    BytesMessage message =
        (BytesMessage)
            Proxy.newProxyInstance(
                BytesMessage.class.getClassLoader(),
                new Class<?>[] {BytesMessage.class},
                (proxy, method, arguments) -> {
                  return switch (method.getName()) {
                    case "writeBytes" -> throw new JMSException("synthetic checked failure");
                    case FIXTURE_TOSTRING_5F8C6B3F -> "CheckedFailingMessage";
                    case FIXTURE_HASHCODE_613EE961 -> System.identityHashCode(proxy);
                    case FIXTURE_EQUALS_7778BDDB -> proxy == arguments[0];
                    default -> throw new UnsupportedOperationException(method.getName());
                  };
                });
    return (JMSContext)
        Proxy.newProxyInstance(
            JMSContext.class.getClassLoader(),
            new Class<?>[] {JMSContext.class},
            (proxy, method, arguments) -> {
              return switch (method.getName()) {
                case FIXTURE_GETSESSIONMODE_BF25AD1A -> JMSContext.SESSION_TRANSACTED;
                case FIXTURE_CREATEBYTESMESSAGE_F47217B2 -> message;
                case FIXTURE_ROLLBACK_3770B198, FIXTURE_CLOSE_97959247 -> null;
                case FIXTURE_TOSTRING_5F8C6B3F -> "CheckedFailingJmsContext";
                case FIXTURE_HASHCODE_613EE961 -> System.identityHashCode(proxy);
                case FIXTURE_EQUALS_7778BDDB -> proxy == arguments[0];
                default -> throw new UnsupportedOperationException(method.getName());
              };
            });
  }

  private static JMSContext jmsContext(int mode) {
    return (JMSContext)
        Proxy.newProxyInstance(
            JMSContext.class.getClassLoader(),
            new Class<?>[] {JMSContext.class},
            (proxy, method, arguments) -> {
              return switch (method.getName()) {
                case FIXTURE_GETSESSIONMODE_BF25AD1A -> mode;
                case FIXTURE_CLOSE_97959247 -> null;
                case FIXTURE_TOSTRING_5F8C6B3F -> "SyntheticJmsContext";
                case FIXTURE_HASHCODE_613EE961 -> System.identityHashCode(proxy);
                case FIXTURE_EQUALS_7778BDDB -> proxy == arguments[0];
                default -> throw new UnsupportedOperationException(method.getName());
              };
            });
  }

  private static Connection emptyInsertConnection(Connection delegate) {
    return (Connection)
        Proxy.newProxyInstance(
            Connection.class.getClassLoader(),
            new Class<?>[] {Connection.class},
            (proxy, method, arguments) -> {
              if (method.getName().equals("prepareStatement")
                  && arguments != null
                  && arguments[0] instanceof String sql
                  && sql.startsWith("insert into schubert.mq_outbox")) {
                ResultSet empty =
                    (ResultSet)
                        Proxy.newProxyInstance(
                            ResultSet.class.getClassLoader(),
                            new Class<?>[] {ResultSet.class},
                            (resultProxy, resultMethod, resultArguments) ->
                                switch (resultMethod.getName()) {
                                  case "next" -> false;
                                  case FIXTURE_CLOSE_97959247 -> null;
                                  case FIXTURE_TOSTRING_5F8C6B3F -> "EmptyResult";
                                  case FIXTURE_HASHCODE_613EE961 ->
                                      System.identityHashCode(resultProxy);
                                  case FIXTURE_EQUALS_7778BDDB -> resultProxy == resultArguments[0];
                                  default ->
                                      throw new UnsupportedOperationException(
                                          resultMethod.getName());
                                });
                return Proxy.newProxyInstance(
                    PreparedStatement.class.getClassLoader(),
                    new Class<?>[] {PreparedStatement.class},
                    (statementProxy, statementMethod, statementArguments) ->
                        switch (statementMethod.getName()) {
                          case "setObject",
                              "setString",
                              "setBytes",
                              "setNull",
                              FIXTURE_CLOSE_97959247 ->
                              null;
                          case "executeQuery" -> empty;
                          case FIXTURE_TOSTRING_5F8C6B3F -> "EmptyInsert";
                          case FIXTURE_HASHCODE_613EE961 -> System.identityHashCode(statementProxy);
                          case FIXTURE_EQUALS_7778BDDB -> statementProxy == statementArguments[0];
                          default ->
                              throw new UnsupportedOperationException(statementMethod.getName());
                        });
              }
              return invoke(delegate, method, arguments);
            });
  }

  private static ResultSet invalidDestinationResult() {
    return (ResultSet)
        Proxy.newProxyInstance(
            ResultSet.class.getClassLoader(),
            new Class<?>[] {ResultSet.class},
            (proxy, method, arguments) -> {
              String column =
                  arguments == null || arguments.length == 0 ? "" : String.valueOf(arguments[0]);
              return switch (method.getName()) {
                case "getLong" -> 1L;
                case FIXTURE_GETOBJECT_B6112877 ->
                    column.equals("message_id") ? MESSAGE : CORRELATION;
                case "getString" -> "unapproved.address";
                case FIXTURE_TOSTRING_5F8C6B3F -> "InvalidDestinationResult";
                case FIXTURE_HASHCODE_613EE961 -> System.identityHashCode(proxy);
                case FIXTURE_EQUALS_7778BDDB -> proxy == arguments[0];
                default -> throw new UnsupportedOperationException(method.getName());
              };
            });
  }

  private static Connection setAutoCommitAndCloseFailure() {
    return (Connection)
        Proxy.newProxyInstance(
            Connection.class.getClassLoader(),
            new Class<?>[] {Connection.class},
            (proxy, method, arguments) ->
                switch (method.getName()) {
                  case "setAutoCommit" -> throw new SQLException("synthetic setup failure");
                  case FIXTURE_CLOSE_97959247 -> throw new SQLException("synthetic close failure");
                  case FIXTURE_TOSTRING_5F8C6B3F -> "SetupFailingConnection";
                  case FIXTURE_HASHCODE_613EE961 -> System.identityHashCode(proxy);
                  case FIXTURE_EQUALS_7778BDDB -> proxy == arguments[0];
                  default -> throw new UnsupportedOperationException(method.getName());
                });
  }

  private static JMSContext afterCommit(
      JMSContext delegate, SqlAction action, AtomicInteger commits) {
    return (JMSContext)
        Proxy.newProxyInstance(
            JMSContext.class.getClassLoader(),
            new Class<?>[] {JMSContext.class},
            (proxy, method, arguments) -> {
              Object result = invoke(delegate, method, arguments);
              if (method.getName().equals(FIXTURE_COMMIT_5EA9C586)) {
                commits.incrementAndGet();
                action.run();
              }
              return result;
            });
  }

  private static JMSContext commitFailureJmsContext(JMSContext delegate) {
    return (JMSContext)
        Proxy.newProxyInstance(
            JMSContext.class.getClassLoader(),
            new Class<?>[] {JMSContext.class},
            (proxy, method, arguments) -> {
              if (method.getName().equals(FIXTURE_COMMIT_5EA9C586)) {
                throw new JMSRuntimeException(FIXTURE_SYNTHETIC_COMMIT_FAILURE_D03EA83F);
              }
              return invoke(delegate, method, arguments);
            });
  }

  private static Connection commitFailureConnection(Connection delegate, boolean rollbackFails) {
    return (Connection)
        Proxy.newProxyInstance(
            Connection.class.getClassLoader(),
            new Class<?>[] {Connection.class},
            (proxy, method, arguments) -> {
              if (method.getName().equals(FIXTURE_COMMIT_5EA9C586)) {
                throw new SQLException(FIXTURE_SYNTHETIC_COMMIT_FAILURE_D03EA83F);
              }
              if (rollbackFails && method.getName().equals(FIXTURE_ROLLBACK_3770B198)) {
                throw new SQLException("synthetic rollback failure");
              }
              return invoke(delegate, method, arguments);
            });
  }

  private static Object invoke(Object target, java.lang.reflect.Method method, Object[] arguments)
      throws Throwable {
    try {
      return method.invoke(target, arguments);
    } catch (InvocationTargetException exception) {
      throw exception.getCause();
    }
  }

  private static byte[] eventWire(UUID message, UUID correlation) {
    byte[] body = wire(FIXTURE_QWKREQ01_19741256, message, correlation, 64, 0, 0, false);
    // Independent SS 323 QWKREQ01 oracle: data offsets 0/26/38/50, lengths 26/12/12/14.
    ascii(body, 256, "01ARZ3NDEKTSV4RRFFQ69G5FAV");
    ascii(body, 282, "000000000001");
    ascii(body, 294, "000000000002");
    return body;
  }

  private static byte[] largeWire() {
    return wire("LGSRSP01", MESSAGE, CORRELATION, 48, 2_088, 1, true);
  }

  private static byte[] smallRequestWire() {
    byte[] body = new byte[256];
    Arrays.fill(body, (byte) ' ');
    ascii(body, 0, "SCHBNK01");
    ascii(body, 8, FIXTURE_001_A3FEAA64);
    ascii(body, 11, "LOGREQ01");
    ascii(body, 19, FIXTURE_001_A3FEAA64);
    body[22] = 'Q';
    body[23] = 'S';
    ascii(body, 24, MESSAGE.toString());
    ascii(body, 60, MESSAGE.toString());
    ascii(body, 96, "20260905120000000");
    ascii(body, 113, "a".repeat(64));
    ascii(body, 177, "0256");
    ascii(body, 181, "000000");
    ascii(body, 187, "000000");
    ascii(body, 193, "000000");
    ascii(body, 199, "000000256");
    return body;
  }

  private static byte[] wire(
      String layout,
      UUID message,
      UUID correlation,
      int dataLength,
      int recordLength,
      int recordCount,
      boolean response) {
    int total = 256 + dataLength + recordLength * recordCount;
    byte[] body = new byte[total];
    Arrays.fill(body, (byte) ' ');
    ascii(body, 0, "SCHBNK01");
    ascii(body, 8, FIXTURE_001_A3FEAA64);
    ascii(body, 11, layout);
    ascii(body, 19, FIXTURE_001_A3FEAA64);
    body[22] = response ? (byte) 'S' : (byte) 'E';
    body[23] = response ? (byte) 'S' : (byte) 'I';
    ascii(body, 24, message.toString());
    ascii(body, 60, correlation.toString());
    ascii(body, 96, "20260905120000000");
    if (response) {
      ascii(body, 113, "a".repeat(64));
    }
    ascii(body, 177, "0256");
    ascii(body, 181, String.format(Locale.ROOT, "%06d", dataLength));
    ascii(body, 187, String.format(Locale.ROOT, "%06d", recordLength));
    ascii(body, 193, String.format(Locale.ROOT, "%06d", recordCount));
    ascii(body, 199, String.format(Locale.ROOT, "%09d", total));
    if (response) {
      ascii(body, 208, "0000");
    }
    return body;
  }

  private static void ascii(byte[] target, int offset, String value) {
    byte[] source = value.getBytes(StandardCharsets.US_ASCII);
    System.arraycopy(source, 0, target, offset, source.length);
  }

  private static EmbeddedActiveMQ startBroker(Path root) throws Exception {
    Configuration configuration;
    try (InputStream input = Files.newInputStream(Path.of(System.getProperty("broker.template")))) {
      configuration = new FileConfigurationParser().parseMainConfig(input);
    }
    configuration
        .setPagingDirectory(root.resolve("paging").toString())
        .setBindingsDirectory(root.resolve("bindings").toString())
        .setJournalDirectory(root.resolve("journal").toString())
        .setLargeMessagesDirectory(root.resolve("large-messages").toString())
        .setSecurityEnabled(false)
        .clearAcceptorConfigurations()
        .addAcceptorConfiguration("component", FIXTURE_VM_0_0C76084A);
    return new EmbeddedActiveMQ().setConfiguration(configuration).start();
  }

  private static ActiveMQQueue queue(String address) {
    return new ActiveMQQueue(address + "::" + address + ".q");
  }

  private static void lease(long id, String owner, Instant until) throws SQLException {
    try (Connection connection = appConnection();
        PreparedStatement statement =
            connection.prepareStatement(
                "update schubert.mq_outbox set lease_owner=?,lease_until=? where id=?")) {
      statement.setString(1, owner);
      statement.setObject(2, until.atOffset(java.time.ZoneOffset.UTC));
      statement.setLong(3, id);
      assertEquals(1, statement.executeUpdate());
    }
  }

  private static void leaseUnchecked(long id, String owner, Instant until) {
    try {
      lease(id, owner, until);
    } catch (SQLException exception) {
      throw new IllegalStateException("synthetic lease update failed", exception);
    }
  }

  private static String text(long id, String column) throws SQLException {
    return textNullable(id, column);
  }

  private static String textNullable(long id, String column) throws SQLException {
    try (Connection connection = appConnection();
        Statement statement = connection.createStatement();
        ResultSet result =
            statement.executeQuery(
                "select " + column + "::text from schubert.mq_outbox where id=" + id)) {
      assertTrue(result.next());
      return result.getString(1);
    }
  }

  private static Instant timestamp(long id, String column) throws SQLException {
    try (Connection connection = appConnection();
        Statement statement = connection.createStatement();
        ResultSet result =
            statement.executeQuery(
                "select " + column + " from schubert.mq_outbox where id=" + id)) {
      assertTrue(result.next());
      return result.getObject(1, java.time.OffsetDateTime.class).toInstant();
    }
  }

  private static void executeApp(String sql) throws SQLException {
    try (Connection connection = appConnection();
        Statement statement = connection.createStatement()) {
      statement.execute(sql);
    }
  }

  private static Connection transaction() throws SQLException {
    Connection connection = appConnection();
    connection.setAutoCommit(false);
    return connection;
  }

  private static Connection appConnection() throws SQLException {
    return DriverManager.getConnection(jdbcUrl, APP, "");
  }

  private static UUID uuid(long suffix) {
    return new UUID(0x8300000000000000L, suffix);
  }

  private static Path locatePostgreSqlRoot() {
    String configured = System.getenv("SCHUBERT_PG_ROOT");
    Path candidate =
        configured == null || configured.isBlank()
            ? Path.of("/home/mini/codex/project1/work/characterization-tools/root/usr")
            : Path.of(configured);
    assertTrue(
        Files.isExecutable(candidate.resolve("lib/postgresql/18/bin/postgres")),
        "PostgreSQL 18 root not found: " + candidate);
    return candidate.toAbsolutePath().normalize();
  }

  private static String pgBinary(String name) {
    return pgRoot.resolve("lib/postgresql/18/bin").resolve(name).toString();
  }

  private static String serverOptions() {
    return "-p "
        + port
        + " -h 127.0.0.1 -k /tmp -c extension_control_path="
        + pgRoot.resolve("share/postgresql/18")
        + " -c dynamic_library_path="
        + pgRoot.resolve("lib/postgresql/18/lib")
        + " -c timezone=UTC";
  }

  private static int availablePort() throws IOException {
    try (ServerSocket socket = new ServerSocket(0, 1, InetAddress.getLoopbackAddress())) {
      return socket.getLocalPort();
    }
  }

  private static void run(String... command) throws IOException, InterruptedException {
    ProcessBuilder builder = new ProcessBuilder(command);
    builder.redirectErrorStream(true);
    builder.redirectOutput(
        ProcessBuilder.Redirect.appendTo(clusterRoot.resolve("process.log").toFile()));
    builder
        .environment()
        .put(
            "LD_LIBRARY_PATH",
            pgRoot.resolve("lib/x86_64-linux-gnu") + ":" + pgRoot.resolve("lib/postgresql/18/lib"));
    Process process = builder.start();
    boolean finished = process.waitFor(Duration.ofSeconds(30));
    assertTrue(finished, "command timed out: " + command[0]);
    assertEquals(0, process.exitValue(), "command failed: " + String.join(" ", command));
  }

  private static void executeResourceAsAdmin(String resource) throws Exception {
    var url = OutboxDispatcherTest.class.getClassLoader().getResource(resource);
    assertNotNull(url, "missing resource " + resource);
    URI uri = url.toURI();
    String sql = Files.readString(Path.of(uri), StandardCharsets.UTF_8);
    try (Connection connection = DriverManager.getConnection(jdbcUrl, ADMIN, "");
        Statement statement = connection.createStatement()) {
      statement.execute(sql);
    }
  }

  @FunctionalInterface
  private interface SqlAction {
    void run() throws SQLException;
  }

  private static final class SelfCausedRuntimeException extends RuntimeException {
    private static final long serialVersionUID = 1L;

    @Override
    public synchronized Throwable getCause() {
      return this;
    }
  }

  private static final class SelfLinkedJmsException extends JMSException {
    private static final long serialVersionUID = 1L;

    private SelfLinkedJmsException() {
      super("self-linked");
    }

    @Override
    public Exception getLinkedException() {
      return this;
    }
  }
}
