package dev.codex.schubert.nk.web.logging;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.web.messaging.JmsContextFactory;
import jakarta.jms.JMSContext;
import jakarta.jms.JMSRuntimeException;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Proxy;
import java.nio.file.Files;
import java.nio.file.Path;
import java.sql.Connection;
import java.sql.SQLException;
import java.time.Clock;
import java.time.Instant;
import java.time.ZoneId;
import java.time.ZoneOffset;
import java.util.UUID;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicReference;
import javax.sql.DataSource;
import org.apache.activemq.artemis.jms.client.ActiveMQConnectionFactory;
import org.apache.activemq.artemis.jms.client.ActiveMQQueue;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/**
 * PT-IDEM-012: real DB/broker, independent SQL after-conditions, controlled time/failure oracles.
 */
final class WebLogDispatcherTest {
  private static final String FIXTURE_PENDING_B11DB31F = "PENDING";
  private static final String FIXTURE_STATUS_CFC31BCC = "status";
  private static final String FIXTURE_ATTEMPT_COUNT_87388C12 = "attempt_count";
  private static final String FIXTURE_LAST_ERROR_CODE_BF1A4C63 = "last_error_code";
  private static final String FIXTURE_LEASE_OWNER_6418FA0F = "lease_owner";
  private static final String FIXTURE_WORKER_1636F9EC = "worker";
  private static final String FIXTURE_SENT_AT_C13E7660 = "sent_at";
  private static final String FIXTURE_SETAUTOCOMMIT_17F7C6FD = "setAutoCommit";
  private static final String FIXTURE_ROLLBACK_3770B198 = "rollback";
  private static final String FIXTURE_CLOSE_97959247 = "close";
  private static final Instant NOW = Instant.parse("2026-09-06T00:00:00Z");
  private static final WebLogPayloadIdentity IDENTITY =
      new WebLogPayloadIdentity(
          UUID.fromString("00000000-0000-0000-0000-000000000012"),
          UUID.fromString("00000000-0000-0000-0000-000000000015"));
  @TempDir static Path root;
  private static WebLogDatabaseFixture db;
  private final WebLogOutboxRepository repository = new WebLogOutboxRepository(() -> 100);

  @BeforeAll
  static void start() throws Exception {
    db = new WebLogDatabaseFixture(root);
  }

  @AfterAll
  static void stop() throws Exception {
    if (db != null) {
      db.stop();
    }
  }

  @BeforeEach
  void reset() throws SQLException {
    db.reset();
  }

  @Test
  void graph323002ProviderFatalNeverMarksOrdinaryFailureAndNullEdgesStillRetry() throws Exception {
    try (var codec = codec()) {
      for (int kind = 0; kind < 4; kind++) {
        db.reset();
        enqueue(codec);
        var fatal = new LinkageError("synthetic provider fatal");
        Throwable leaf = kind == 3 ? new SQLException("synthetic ordinary") : fatal;
        var graph = WebLogReplayWorkerTest.providerGraph323(leaf, kind);
        var opens = new AtomicInteger();
        var jms = new AtomicInteger();
        var dispatch =
            new WebLogDispatcher(
                source(
                    () -> {
                      opens.incrementAndGet();
                      return db.web();
                    }),
                repository,
                new WebLogMessageSender(
                    codec,
                    () -> {
                      jms.incrementAndGet();
                      throw graph;
                    }),
                Clock.fixed(NOW, ZoneOffset.UTC));
        if (kind < 3) {
          assertSame(fatal, assertThrows(Error.class, () -> dispatch.dispatch("graph", 1)));
          assertEquals(1, opens.get());
          assertEquals(FIXTURE_PENDING_B11DB31F, column(FIXTURE_STATUS_CFC31BCC));
          assertEquals("0", column(FIXTURE_ATTEMPT_COUNT_87388C12));
          assertNull(column(FIXTURE_LAST_ERROR_CODE_BF1A4C63));
          assertEquals(NOW, timestamp("next_attempt_at"));
          assertEquals("graph", column(FIXTURE_LEASE_OWNER_6418FA0F));
          assertEquals(NOW.plusSeconds(10), timestamp("lease_until"));
        } else {
          assertEquals(new WebLogDispatcher.Report(1, 0, 1, 0), dispatch.dispatch("graph", 1));
          assertEquals(2, opens.get());
          assertEquals("ERROR", column(FIXTURE_STATUS_CFC31BCC));
          assertEquals("1", column(FIXTURE_ATTEMPT_COUNT_87388C12));
          assertEquals("JMS_SEND_FAILURE", column(FIXTURE_LAST_ERROR_CODE_BF1A4C63));
          assertEquals(NOW.plusMillis(1100), timestamp("next_attempt_at"));
          assertNull(column(FIXTURE_LEASE_OWNER_6418FA0F));
        }
        assertEquals(1, jms.get());
      }
    }
  }

  @Test
  void resultTimeRetryAndNoDatabaseLockDuringJms() throws Exception {
    var broker = WebLogMessageSenderTest.broker(Files.createDirectory(root.resolve("time-broker")));
    try (var factory = new ActiveMQConnectionFactory("vm://0");
        var codec = codec();
        var observer = factory.createContext(JMSContext.AUTO_ACKNOWLEDGE);
        var consumer = observer.createConsumer(new ActiveMQQueue("nk.web.log::nk.web.log.q"))) {
      enqueue(codec);
      AtomicReference<Instant> now = new AtomicReference<>(NOW);
      JmsContextFactory failed =
          () -> {
            unlocked(FIXTURE_WORKER_1636F9EC);
            now.set(NOW.plusSeconds(3));
            throw new JMSRuntimeException("synthetic transport failure");
          };
      assertEquals(
          new WebLogDispatcher.Report(1, 0, 1, 0),
          dispatcher(codec, failed, now).dispatch(FIXTURE_WORKER_1636F9EC, 1));
      assertEquals("ERROR", column(FIXTURE_STATUS_CFC31BCC));
      assertEquals("JMS_SEND_FAILURE", column(FIXTURE_LAST_ERROR_CODE_BF1A4C63));
      assertEquals("1", column(FIXTURE_ATTEMPT_COUNT_87388C12));
      assertEquals(NOW.plusMillis(4100), timestamp("next_attempt_at"));
      assertNull(column(FIXTURE_LEASE_OWNER_6418FA0F));
      assertNull(column(FIXTURE_SENT_AT_C13E7660));
      now.set(NOW.plusMillis(4099));
      assertEquals(
          new WebLogDispatcher.Report(0, 0, 0, 0),
          dispatcher(codec, failed, now).dispatch("early", 1));
      now.set(NOW.plusMillis(4100));
      JmsContextFactory success =
          () -> {
            unlocked(FIXTURE_WORKER_1636F9EC);
            now.set(NOW.plusMillis(7100));
            return factory.createContext(JMSContext.SESSION_TRANSACTED);
          };
      var report = dispatcher(codec, success, now).dispatch(FIXTURE_WORKER_1636F9EC, 1);
      assertEquals(1, report.claimed());
      assertEquals(1, report.sent());
      assertEquals(0, report.failed());
      assertEquals(0, report.leaseLost());
      assertEquals("SENT", column(FIXTURE_STATUS_CFC31BCC));
      assertEquals(NOW.plusMillis(7100), timestamp(FIXTURE_SENT_AT_C13E7660));
      assertNull(column(FIXTURE_LAST_ERROR_CODE_BF1A4C63));
      assertNotNull(consumer.receive(5000));
      assertNull(consumer.receive(100));
    } finally {
      broker.stop();
    }
  }

  @Test
  void confirmedSendThenMarkFailureRecoversAfterLeaseWithoutDuplicate() throws Exception {
    var broker =
        WebLogMessageSenderTest.broker(Files.createDirectory(root.resolve("crash-broker")));
    try (var factory = new ActiveMQConnectionFactory("vm://0");
        var codec = codec();
        var observer = factory.createContext(JMSContext.AUTO_ACKNOWLEDGE);
        var consumer = observer.createConsumer(new ActiveMQQueue("nk.web.log::nk.web.log.q"))) {
      enqueue(codec);
      AtomicInteger connections = new AtomicInteger();
      DataSource broken =
          source(
              () -> {
                if (connections.incrementAndGet() == 2) {
                  throw new SQLException("synthetic mark unavailable", "08006");
                }
                return db.web();
              });
      var sender =
          new WebLogMessageSender(
              codec, () -> factory.createContext(JMSContext.SESSION_TRANSACTED));
      assertEquals(
          "08006",
          assertThrows(
                  SQLException.class,
                  () ->
                      new WebLogDispatcher(
                              broken, repository, sender, Clock.fixed(NOW, ZoneOffset.UTC))
                          .dispatch("crashed", 1))
              .getSQLState());
      assertEquals(FIXTURE_PENDING_B11DB31F, column(FIXTURE_STATUS_CFC31BCC));
      assertEquals("crashed", column(FIXTURE_LEASE_OWNER_6418FA0F));
      assertNull(column(FIXTURE_SENT_AT_C13E7660));
      AtomicReference<Instant> now = new AtomicReference<>(NOW.plusSeconds(10));
      var recovered =
          dispatcher(codec, () -> factory.createContext(JMSContext.SESSION_TRANSACTED), now);
      assertEquals(new WebLogDispatcher.Report(0, 0, 0, 0), recovered.dispatch("recovery", 1));
      now.set(NOW.plusSeconds(10).plusNanos(1000));
      assertEquals(new WebLogDispatcher.Report(1, 1, 0, 0), recovered.dispatch("recovery", 1));
      assertEquals("SENT", column(FIXTURE_STATUS_CFC31BCC));
      assertEquals(now.get(), timestamp(FIXTURE_SENT_AT_C13E7660));
      assertNotNull(consumer.receive(5000));
      assertNull(consumer.receive(100));
    } finally {
      broker.stop();
    }
  }

  @Test
  void lostLeaseProtectsNewOwnerAndInvalidCipherNeverSends() throws Exception {
    try (var codec = codec()) {
      for (boolean fail : new boolean[] {false, true}) {
        db.reset();
        enqueue(codec);
        JmsContextFactory provider =
            () -> {
              try (var connection = db.web();
                  var statement = connection.createStatement()) {
                assertEquals(
                    1,
                    statement.executeUpdate(
                        "update schubert_web_session.web_log_outbox set lease_owner='new-owner'"));
              } catch (SQLException error) {
                throw new AssertionError(error);
              }
              if (fail) {
                throw new JMSRuntimeException("synthetic failure after takeover");
              }
              return WebLogMessageSenderTest.fakeContext(
                  "ok", new AtomicInteger(), new AtomicReference<>());
            };
        assertEquals(
            new WebLogDispatcher.Report(1, 0, 0, 1),
            dispatcher(codec, provider, new AtomicReference<>(NOW)).dispatch("old", 1));
        assertEquals("new-owner", column(FIXTURE_LEASE_OWNER_6418FA0F));
        assertEquals(FIXTURE_PENDING_B11DB31F, column(FIXTURE_STATUS_CFC31BCC));
        assertEquals("0", column(FIXTURE_ATTEMPT_COUNT_87388C12));
      }
      db.reset();
      try (var connection = db.transaction()) {
        assertTrue(
            repository.enqueue(
                connection, IDENTITY, new EncryptedWebLogPayload("test", new byte[64]), NOW));
        connection.commit();
      }
      assertEquals(
          new WebLogDispatcher.Report(1, 0, 1, 0),
          dispatcher(
                  codec,
                  () -> {
                    throw new AssertionError("invalid ciphertext opened JMS");
                  },
                  new AtomicReference<>(NOW))
              .dispatch("invalid", 1));
      assertEquals("WEB_LOG_PAYLOAD_INVALID", column(FIXTURE_LAST_ERROR_CODE_BF1A4C63));
      assertEquals("ERROR", column(FIXTURE_STATUS_CFC31BCC));
    }
  }

  @Test
  void databaseFailuresRollbackAndCloseWithoutInventingSuccessfulMarks() throws Exception {
    try (var codec = codec()) {
      enqueue(codec);
      var sender =
          new WebLogMessageSender(
              codec,
              () -> {
                throw new AssertionError("claim failure must not send");
              });
      for (String point :
          new String[] {
            FIXTURE_SETAUTOCOMMIT_17F7C6FD,
            "prepareStatement",
            "commit",
            FIXTURE_ROLLBACK_3770B198,
            FIXTURE_CLOSE_97959247
          }) {
        AtomicInteger closed = new AtomicInteger();
        AtomicInteger rolledBack = new AtomicInteger();
        DataSource failing = source(() -> faultConnection(db.web(), point, closed, rolledBack));
        SQLException failure =
            assertThrows(
                SQLException.class,
                () ->
                    new WebLogDispatcher(
                            failing, repository, sender, Clock.fixed(NOW, ZoneOffset.UTC))
                        .dispatch("failed-claim", 1));
        assertEquals("PT001", failure.getSQLState());
        assertEquals(1, closed.get());
        assertEquals(
            point.equals(FIXTURE_SETAUTOCOMMIT_17F7C6FD) || point.equals(FIXTURE_CLOSE_97959247)
                ? 0
                : 1,
            rolledBack.get());
        if (point.equals(FIXTURE_ROLLBACK_3770B198)) {
          assertEquals(1, failure.getSuppressed().length);
        }
        assertEquals(FIXTURE_PENDING_B11DB31F, column(FIXTURE_STATUS_CFC31BCC));
        if (!point.equals(FIXTURE_CLOSE_97959247)) {
          assertNull(column(FIXTURE_LEASE_OWNER_6418FA0F));
        }
      }
      for (boolean sendFails : new boolean[] {false, true}) {
        db.reset();
        enqueue(codec);
        AtomicInteger opened = new AtomicInteger();
        AtomicInteger closed = new AtomicInteger();
        AtomicInteger rolledBack = new AtomicInteger();
        DataSource brokenMark =
            source(
                () ->
                    opened.incrementAndGet() == 1
                        ? db.web()
                        : faultConnection(db.web(), "commit", closed, rolledBack));
        var actualSender =
            new WebLogMessageSender(
                codec,
                () -> {
                  if (sendFails) {
                    throw new JMSRuntimeException("synthetic send failure");
                  }
                  return WebLogMessageSenderTest.fakeContext(
                      "ok", new AtomicInteger(), new AtomicReference<>());
                });
        assertThrows(
            SQLException.class,
            () ->
                new WebLogDispatcher(
                        brokenMark, repository, actualSender, Clock.fixed(NOW, ZoneOffset.UTC))
                    .dispatch("mark-failed", 1));
        assertEquals(1, rolledBack.get());
        assertEquals(1, closed.get());
        assertEquals(FIXTURE_PENDING_B11DB31F, column(FIXTURE_STATUS_CFC31BCC));
        assertEquals("mark-failed", column(FIXTURE_LEASE_OWNER_6418FA0F));
        assertNull(column(FIXTURE_SENT_AT_C13E7660));
        assertEquals("0", column(FIXTURE_ATTEMPT_COUNT_87388C12));
      }
    }
  }

  @Test
  void idem012r02SameJdbcFailureAtClaimRollbackAndClosePreservesPrimary() throws Exception {
    try (var codec = codec()) {
      SQLException primary = new SQLException("synthetic shared JDBC failure", "PT002");
      AtomicInteger rolledBack = new AtomicInteger();
      AtomicInteger closed = new AtomicInteger();
      DataSource failing =
          source(
              () ->
                  (Connection)
                      Proxy.newProxyInstance(
                          Connection.class.getClassLoader(),
                          new Class<?>[] {Connection.class},
                          (ignored, method, args) -> {
                            if (method.getName().equals("prepareStatement")) throw primary;
                            if (method.getName().equals(FIXTURE_ROLLBACK_3770B198)) {
                              rolledBack.incrementAndGet();
                              throw primary;
                            }
                            if (method.getName().equals(FIXTURE_CLOSE_97959247)) {
                              closed.incrementAndGet();
                              throw primary;
                            }
                            if (method.getName().equals(FIXTURE_SETAUTOCOMMIT_17F7C6FD))
                              return null;
                            if (method.getName().equals("getAutoCommit")) return false;
                            throw new AssertionError(method.getName());
                          }));
      var sender =
          new WebLogMessageSender(
              codec,
              () -> {
                throw new AssertionError("claim failure must not send");
              });
      SQLException observed =
          assertThrows(
              SQLException.class,
              () ->
                  new WebLogDispatcher(
                          failing, repository, sender, Clock.fixed(NOW, ZoneOffset.UTC))
                      .dispatch(FIXTURE_WORKER_1636F9EC, 1));
      assertSame(primary, observed);
      assertEquals(0, observed.getSuppressed().length);
      assertEquals(1, rolledBack.get());
      assertEquals(1, closed.get());
    }
  }

  @Test
  void idem012r03DistinctRollbackAndCloseFailuresRemainSecondary() throws Exception {
    try (var codec = codec()) {
      SQLException primary = new SQLException("claim", "PT003");
      SQLException rollback = new SQLException(FIXTURE_ROLLBACK_3770B198, "PT004");
      SQLException close = new SQLException(FIXTURE_CLOSE_97959247, "PT005");
      AtomicInteger rolledBack = new AtomicInteger();
      AtomicInteger closed = new AtomicInteger();
      SQLException observed =
          assertThrows(
              SQLException.class,
              () ->
                  new WebLogDispatcher(
                          source(
                              () ->
                                  failingConnection(primary, rollback, close, rolledBack, closed)),
                          repository,
                          unreachableSender(codec),
                          Clock.fixed(NOW, ZoneOffset.UTC))
                      .dispatch(FIXTURE_WORKER_1636F9EC, 1));
      assertSame(primary, observed);
      assertArrayEquals(new Throwable[] {rollback, close}, observed.getSuppressed());
      assertEquals(1, rolledBack.get());
      assertEquals(1, closed.get());
    }
  }

  @Test
  void idem012r04RollbackFatalAndSameCloseFatalRemainFatal() throws Exception {
    try (var codec = codec()) {
      SQLException primary = new SQLException("claim", "PT006");
      AssertionError fatal = new AssertionError("rollback fatal");
      AtomicInteger rolledBack = new AtomicInteger();
      AtomicInteger closed = new AtomicInteger();
      AssertionError observed =
          assertThrows(
              AssertionError.class,
              () ->
                  new WebLogDispatcher(
                          source(
                              () -> failingConnection(primary, fatal, fatal, rolledBack, closed)),
                          repository,
                          unreachableSender(codec),
                          Clock.fixed(NOW, ZoneOffset.UTC))
                      .dispatch(FIXTURE_WORKER_1636F9EC, 1));
      assertSame(fatal, observed);
      assertArrayEquals(new Throwable[] {primary}, observed.getSuppressed());
      assertEquals(1, rolledBack.get());
      assertEquals(1, closed.get());
    }
  }

  @Test
  void idem012r05CloseFatalAfterClaimFailureDoesNotHidePrimary() throws Exception {
    try (var codec = codec()) {
      SQLException primary = new SQLException("claim", "PT007");
      AssertionError fatal = new AssertionError("close fatal");
      AtomicInteger rolledBack = new AtomicInteger();
      AtomicInteger closed = new AtomicInteger();
      AssertionError observed =
          assertThrows(
              AssertionError.class,
              () ->
                  new WebLogDispatcher(
                          source(() -> failingConnection(primary, null, fatal, rolledBack, closed)),
                          repository,
                          unreachableSender(codec),
                          Clock.fixed(NOW, ZoneOffset.UTC))
                      .dispatch(FIXTURE_WORKER_1636F9EC, 1));
      assertSame(fatal, observed);
      assertArrayEquals(new Throwable[] {primary}, observed.getSuppressed());
      assertEquals(1, rolledBack.get());
      assertEquals(1, closed.get());
    }
  }

  @Test
  void nullContractsAndReportInvariantsRejectInvalidInput() throws Exception {
    try (var codec = codec()) {
      DataSource source = source(db::web);
      var sender =
          new WebLogMessageSender(
              codec,
              () -> {
                throw new AssertionError();
              });
      Clock clock = Clock.fixed(NOW, ZoneOffset.UTC);
      assertThrows(
          NullPointerException.class, () -> new WebLogDispatcher(null, repository, sender, clock));
      assertThrows(
          NullPointerException.class, () -> new WebLogDispatcher(source, null, sender, clock));
      assertThrows(
          NullPointerException.class, () -> new WebLogDispatcher(source, repository, null, clock));
      assertThrows(
          NullPointerException.class, () -> new WebLogDispatcher(source, repository, sender, null));
      var dispatcher = new WebLogDispatcher(source, repository, sender, clock);
      assertThrows(NullPointerException.class, () -> dispatcher.dispatch(null, 1));
      assertThrows(IllegalArgumentException.class, () -> dispatcher.dispatch("bad worker", 1));
      assertThrows(
          IllegalArgumentException.class, () -> dispatcher.dispatch(FIXTURE_WORKER_1636F9EC, 0));
      assertThrows(
          IllegalArgumentException.class, () -> dispatcher.dispatch(FIXTURE_WORKER_1636F9EC, 101));
      assertThrows(
          NullPointerException.class,
          () ->
              new WebLogDispatcher(source(() -> null), repository, sender, clock)
                  .dispatch(FIXTURE_WORKER_1636F9EC, 1));
      for (int[] counts :
          new int[][] {
            {-1, 0, 0, 0},
            {101, 101, 0, 0},
            {0, -1, 0, 0},
            {0, 0, -1, 0},
            {0, 0, 0, -1},
            {0, 1, 0, 0},
            {1, Integer.MAX_VALUE, Integer.MAX_VALUE, 3}
          }) {
        assertThrows(
            IllegalArgumentException.class,
            () -> new WebLogDispatcher.Report(counts[0], counts[1], counts[2], counts[3]));
      }
      assertEquals(100, new WebLogDispatcher.Report(100, 40, 30, 30).claimed());
    }
  }

  private WebLogDispatcher dispatcher(
      WebLogPayloadCodec codec, JmsContextFactory contexts, AtomicReference<Instant> now) {
    Clock clock =
        new Clock() {
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
            return now.get();
          }
        };
    return new WebLogDispatcher(
        source(db::web), repository, new WebLogMessageSender(codec, contexts), clock);
  }

  private static WebLogPayloadCodec codec() {
    return new WebLogPayloadCodec("test", new byte[32], null, null);
  }

  private void enqueue(WebLogPayloadCodec codec) throws SQLException {
    try (Connection connection = db.transaction()) {
      assertTrue(
          repository.enqueue(
              connection,
              IDENTITY,
              codec.encrypt(IDENTITY, WebLogPayloadCodecTest.goldenWire()),
              NOW));
      connection.commit();
    }
  }

  private static String column(String name) throws SQLException {
    try (var connection = db.web();
        var statement = connection.createStatement();
        var result =
            statement.executeQuery(
                "select " + name + " from schubert_web_session.web_log_outbox")) {
      assertTrue(result.next());
      return result.getString(1);
    }
  }

  private static Instant timestamp(String name) throws SQLException {
    try (var connection = db.web();
        var statement = connection.createStatement();
        var result =
            statement.executeQuery(
                "select " + name + " from schubert_web_session.web_log_outbox")) {
      assertTrue(result.next());
      return result.getObject(1, java.time.OffsetDateTime.class).toInstant();
    }
  }

  private static void unlocked(String worker) {
    try (var connection = db.transaction();
        var statement = connection.createStatement();
        var result =
            statement.executeQuery(
                "select lease_owner from schubert_web_session.web_log_outbox for update nowait")) {
      assertTrue(result.next());
      assertEquals(worker, result.getString(1));
      connection.rollback();
    } catch (SQLException error) {
      throw new AssertionError("JMS must observe committed, unlocked DB lease", error);
    }
  }

  @FunctionalInterface
  private interface Connections {
    Connection open() throws SQLException;
  }

  private static DataSource source(Connections connections) {
    return (DataSource)
        Proxy.newProxyInstance(
            DataSource.class.getClassLoader(),
            new Class<?>[] {DataSource.class},
            (proxy, method, args) -> {
              assertEquals("getConnection", method.getName());
              return connections.open();
            });
  }

  private static Connection faultConnection(
      Connection actual, String point, AtomicInteger closed, AtomicInteger rolledBack) {
    return (Connection)
        Proxy.newProxyInstance(
            Connection.class.getClassLoader(),
            new Class<?>[] {Connection.class},
            (proxy, method, args) -> {
              String name = method.getName();
              if (name.equals(FIXTURE_CLOSE_97959247)) {
                closed.incrementAndGet();
                actual.close();
              }
              if (name.equals(FIXTURE_ROLLBACK_3770B198)) {
                rolledBack.incrementAndGet();
              }
              if (point.equals(name)
                  || point.equals(FIXTURE_ROLLBACK_3770B198) && name.equals("commit")) {
                throw new SQLException("synthetic JDBC failure", "PT001");
              }
              try {
                return method.invoke(actual, args);
              } catch (InvocationTargetException wrapped) {
                throw wrapped.getCause();
              }
            });
  }

  private static Connection failingConnection(
      Throwable claim,
      Throwable rollback,
      Throwable close,
      AtomicInteger rolledBack,
      AtomicInteger closed) {
    return (Connection)
        Proxy.newProxyInstance(
            Connection.class.getClassLoader(),
            new Class<?>[] {Connection.class},
            (ignored, method, args) -> {
              return switch (method.getName()) {
                case FIXTURE_SETAUTOCOMMIT_17F7C6FD -> null;
                case "getAutoCommit" -> false;
                case "prepareStatement" -> throw claim;
                case FIXTURE_ROLLBACK_3770B198 -> {
                  rolledBack.incrementAndGet();
                  if (rollback != null) throw rollback;
                  yield null;
                }
                case FIXTURE_CLOSE_97959247 -> {
                  closed.incrementAndGet();
                  if (close != null) throw close;
                  yield null;
                }
                default -> throw new AssertionError(method.getName());
              };
            });
  }

  private static WebLogMessageSender unreachableSender(WebLogPayloadCodec codec) {
    return new WebLogMessageSender(
        codec,
        () -> {
          throw new AssertionError("claim failure must not send");
        });
  }
}
