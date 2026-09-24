package dev.codex.schubert.nk.web.logging;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.api.logging.WebLogIngestService;
import dev.codex.schubert.nk.api.messaging.inbound.WebLogConsumers;
import dev.codex.schubert.nk.api.messaging.inbound.WebLogListener;
import jakarta.jms.JMSContext;
import jakarta.jms.JMSRuntimeException;
import java.lang.reflect.Proxy;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.sql.Connection;
import java.sql.SQLException;
import java.time.Clock;
import java.time.Instant;
import java.time.ZoneId;
import java.time.ZoneOffset;
import java.util.Arrays;
import java.util.UUID;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicReference;
import javax.sql.DataSource;
import org.apache.activemq.artemis.jms.client.ActiveMQConnectionFactory;
import org.apache.activemq.artemis.jms.client.ActiveMQQueue;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** PT-IDEM-016: real Web retry → Artemis → API projection, not a full NK process/CHR capture. */
final class WebApiLogReplayIntegrationTest {
  private static final Instant NOW = Instant.parse("2026-09-06T00:00:00Z");
  private static final UUID MESSAGE = UUID.fromString("00000000-0000-0000-0000-000000000012");
  private static final UUID CORRELATION = UUID.fromString("00000000-0000-0000-0000-000000000015");
  @TempDir Path root;

  @Test
  void idem016WebOutboxRetriesIntoApiProjectionExactlyOnce() throws Exception {
    var db = new WebLogDatabaseFixture(Files.createDirectory(root.resolve("database")));
    var broker = WebLogMessageSenderTest.broker(Files.createDirectory(root.resolve("broker")));
    try (var factory = new ActiveMQConnectionFactory("vm://0");
        var codec = new WebLogPayloadCodec("test", new byte[32], null, null)) {
      var identity = new WebLogPayloadIdentity(MESSAGE, CORRELATION);
      var repository = new WebLogOutboxRepository(() -> 0);
      try (Connection connection = db.web()) {
        connection.setAutoCommit(false);
        assertTrue(
            repository.enqueue(
                connection, identity, codec.encrypt(identity, ingestibleWire()), NOW));
        connection.commit();
      }
      AtomicReference<Instant> time = new AtomicReference<>(NOW);
      Clock clock = clock(time);
      var failed =
          new WebLogDispatcher(
              source(db::web),
              repository,
              new WebLogMessageSender(
                  codec,
                  () -> {
                    throw new JMSRuntimeException("synthetic first transport failure");
                  }),
              clock);
      assertEquals(new WebLogDispatcher.Report(1, 0, 1, 0), failed.dispatch("web-log-worker", 1));
      assertOutbox(db, "ERROR", 1, "JMS_SEND_FAILURE", NOW.plusSeconds(1));
      assertEquals(0, appLogCount(db));

      CountDownLatch processed = new CountDownLatch(2);
      AtomicInteger terminals = new AtomicInteger();
      AtomicInteger received = new AtomicInteger();
      AtomicReference<String> ingestFailure = new AtomicReference<>("none");
      var ingest = new WebLogIngestService(source(db::api));
      try (var consumer =
          WebLogConsumers.start(
              () -> factory.createContext(JMSContext.SESSION_TRANSACTED),
              new WebLogListener(
                  event -> {
                    received.incrementAndGet();
                    try {
                      ingest.process(event);
                      processed.countDown();
                    } catch (RuntimeException failure) {
                      ingestFailure.set(failure.getClass().getSimpleName());
                      throw failure;
                    }
                  },
                  clock),
              ignored -> terminals.incrementAndGet())) {
        assertTrue(consumer.ready());
        time.set(NOW.plusSeconds(1).minusNanos(1_000));
        var successful =
            new WebLogDispatcher(
                source(db::web),
                repository,
                new WebLogMessageSender(
                    codec, () -> factory.createContext(JMSContext.SESSION_TRANSACTED)),
                clock);
        assertEquals(new WebLogDispatcher.Report(0, 0, 0, 0), successful.dispatch("before-due", 1));
        time.set(NOW.plusSeconds(1));
        assertEquals(
            new WebLogDispatcher.Report(1, 1, 0, 0), successful.dispatch("retry-worker", 1));
        assertOutbox(db, "SENT", 1, null, NOW.plusSeconds(1));
        sendDuplicate(factory);
        assertTrue(
            processed.await(5, TimeUnit.SECONDS),
            "received="
                + received.get()
                + " terminal="
                + terminals.get()
                + " ingest="
                + ingestFailure.get());
        assertEquals(1, appLogCount(db));
        assertEquals("WEB|REQUEST|HTTP_REQUEST_COMPLETED", appLogProjection(db));
        assertEquals(0, terminals.get());
        assertFalse(consumer.terminalFailureObserved());
      }
    } finally {
      broker.stop();
      db.stop();
    }
  }

  private static void sendDuplicate(ActiveMQConnectionFactory factory) throws Exception {
    try (JMSContext context = factory.createContext(JMSContext.SESSION_TRANSACTED)) {
      var message = context.createBytesMessage();
      message.writeBytes(ingestibleWire());
      message.setJMSCorrelationID(CORRELATION.toString());
      message.setStringProperty("NKMessageID", MESSAGE.toString());
      message.setStringProperty("NKLayoutID", "WLGEVT01");
      message.setStringProperty("NKProtocolVersion", "001");
      context.createProducer().send(new ActiveMQQueue("nk.web.log::nk.web.log.q"), message);
      context.commit();
    }
  }

  private static byte[] ingestibleWire() {
    byte[] wire = WebLogPayloadCodecTest.goldenWire();
    // UI235 Action is DATA byte 42..105 (absolute 297..360); API SS312 accepts this fixed action.
    Arrays.fill(wire, 297, 361, (byte) ' ');
    byte[] action = "HTTP_REQUEST_COMPLETED".getBytes(StandardCharsets.US_ASCII);
    System.arraycopy(action, 0, wire, 297, action.length);
    // UI235 Details is DATA byte 1044..2067 (absolute 1299..2322); SS351 allowlist is narrower.
    Arrays.fill(wire, 1299, 2323, (byte) ' ');
    byte[] details = "{\"projectionStatus\":\"PENDING\"}".getBytes(StandardCharsets.US_ASCII);
    System.arraycopy(details, 0, wire, 1299, details.length);
    return wire;
  }

  private static void assertOutbox(
      WebLogDatabaseFixture db, String status, int attempts, String error, Instant due)
      throws SQLException {
    try (Connection connection = db.web();
        var statement = connection.createStatement();
        var rows =
            statement.executeQuery(
                "select status,attempt_count,last_error_code,next_attempt_at "
                    + "from schubert_web_session.web_log_outbox")) {
      assertTrue(rows.next());
      assertEquals(status, rows.getString(1));
      assertEquals(attempts, rows.getInt(2));
      assertEquals(error, rows.getString(3));
      assertEquals(due, rows.getObject(4, java.time.OffsetDateTime.class).toInstant());
      assertFalse(rows.next());
    }
  }

  private static int appLogCount(WebLogDatabaseFixture db) throws SQLException {
    try (Connection connection = db.api();
        var statement =
            connection.prepareStatement(
                "select count(*) from schubert.app_logs where source_message_id=?")) {
      statement.setObject(1, MESSAGE);
      try (var rows = statement.executeQuery()) {
        assertTrue(rows.next());
        return rows.getInt(1);
      }
    }
  }

  private static String appLogProjection(WebLogDatabaseFixture db) throws SQLException {
    try (Connection connection = db.api();
        var statement =
            connection.prepareStatement(
                "select service,category,action from schubert.app_logs where source_message_id=?")) {
      statement.setObject(1, MESSAGE);
      try (var rows = statement.executeQuery()) {
        assertTrue(rows.next());
        String value = rows.getString(1) + "|" + rows.getString(2) + "|" + rows.getString(3);
        assertFalse(rows.next());
        return value;
      }
    }
  }

  private static Clock clock(AtomicReference<Instant> now) {
    return new Clock() {
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
  }

  private static DataSource source(SqlConnection connection) {
    return (DataSource)
        Proxy.newProxyInstance(
            DataSource.class.getClassLoader(),
            new Class<?>[] {DataSource.class},
            (ignored, method, arguments) -> {
              if (method.getName().equals("getConnection")) return connection.open();
              throw new AssertionError(method.getName());
            });
  }

  @FunctionalInterface
  private interface SqlConnection {
    Connection open() throws SQLException;
  }
}
