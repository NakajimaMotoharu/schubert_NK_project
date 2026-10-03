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
import java.time.Duration;
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
import org.springframework.mock.web.MockHttpServletRequest;

/** PT-IDEM-016: real Web retry → Artemis → API projection, not a full NK process/CHR capture. */
final class WebApiLogReplayIntegrationTest {
  private static final Instant NOW = Instant.parse("2026-09-06T00:00:00Z");
  private static final UUID MESSAGE = UUID.fromString("00000000-0000-0000-0000-000000000012");
  private static final UUID CORRELATION = UUID.fromString("00000000-0000-0000-0000-000000000015");
  @TempDir Path root;

  @Test
  void req015NewProducerUsesExistingWorkerRetryBrokerAndApiUk() throws Exception {
    var database = new WebLogDatabaseFixture(Files.createDirectory(root.resolve("database")));
    var broker = WebLogMessageSenderTest.broker(Files.createDirectory(root.resolve("broker")));
    try (var factory = new ActiveMQConnectionFactory("vm://0");
        var fixture = new WebRequestLogProducerTest.Fixture(source(database::web))) {
      var request = new MockHttpServletRequest();
      var trace = WebRequestTraceTest.trace(request, 77);
      trace.captureRoute("/login");
      var contexts = new AtomicInteger();
      fixture.producer.complete(
          trace, 200, 12999999, 3, "GET", java.util.Optional.of("203.0.113.7"));
      assertEquals(0, contexts.get());
      assertEquals(0, appLogCount(database, trace.eventId()));
      assertEquals(
          0,
          broker
              .getActiveMQServer()
              .locateQueue(org.apache.activemq.artemis.api.core.SimpleString.of("nk.web.log.q"))
              .getMessageCount());
      byte[] envelope;
      try (var connection = database.web();
          var statement = connection.createStatement();
          var rows =
              statement.executeQuery(
                  "select payload_ciphertext from schubert_web_session.web_log_outbox")) {
        assertTrue(rows.next());
        envelope = rows.getBytes(1);
        assertFalse(rows.next());
      }
      byte[] wire =
          WebRequestLogProducerTest.independentDecrypt(trace.eventId(), trace.eventId(), envelope);
      var time =
          new AtomicReference<>(
              WebRequestLogProducerTest.NOW.truncatedTo(java.time.temporal.ChronoUnit.MILLIS));
      Clock clock = clock(time);
      var received = new AtomicInteger();
      var terminals = new AtomicInteger();
      var processed = new CountDownLatch(2);
      var ingest = new WebLogIngestService(source(database::api));
      var dispatcher =
          new WebLogDispatcher(
              source(database::web),
              new WebLogOutboxRepository(() -> 0),
              new WebLogMessageSender(
                  fixture.codec,
                  () -> {
                    if (contexts.getAndIncrement() == 0)
                      throw new JMSRuntimeException("synthetic-first-send");
                    return factory.createContext(JMSContext.SESSION_TRANSACTED);
                  }),
              clock);
      try (var consumer =
              WebLogConsumers.start(
                  () -> factory.createContext(JMSContext.SESSION_TRANSACTED),
                  new WebLogListener(
                      event -> {
                        ingest.process(event);
                        received.incrementAndGet();
                        processed.countDown();
                      },
                      clock),
                  ignored -> terminals.incrementAndGet());
          var worker =
              WebLogReplayWorker.start(
                  dispatcher, "request-log-worker", 100, Duration.ofMillis(10))) {
        assertTrue(consumer.ready());
        assertTrue(worker.running());
        long deadline = System.nanoTime() + TimeUnit.SECONDS.toNanos(10);
        while (contexts.get() == 0 && System.nanoTime() < deadline) Thread.sleep(5);
        // First send has already opened its isolated JMS attempt; await persisted retry state.
        boolean retry = false;
        while (!retry && System.nanoTime() < deadline) {
          try (var connection = database.web();
              var statement = connection.createStatement();
              var rows =
                  statement.executeQuery(
                      "select status,attempt_count from schubert_web_session.web_log_outbox")) {
            assertTrue(rows.next());
            retry = rows.getString(1).equals("ERROR") && rows.getInt(2) == 1;
          }
          if (!retry) Thread.sleep(5);
        }
        assertTrue(retry);
        time.set(time.get().plusSeconds(1));
        while (received.get() < 1 && System.nanoTime() < deadline) Thread.sleep(5);
        assertEquals(1, received.get());
        try (JMSContext context = factory.createContext(JMSContext.SESSION_TRANSACTED)) {
          var duplicate = context.createBytesMessage();
          duplicate.writeBytes(wire);
          duplicate.setJMSCorrelationID(trace.eventId().toString());
          duplicate.setStringProperty("NKMessageID", trace.eventId().toString());
          duplicate.setStringProperty("NKLayoutID", "WLGEVT01");
          duplicate.setStringProperty("NKProtocolVersion", "001");
          context.createProducer().send(new ActiveMQQueue("nk.web.log::nk.web.log.q"), duplicate);
          context.commit();
        }
        assertTrue(processed.await(5, TimeUnit.SECONDS));
        assertEquals(2, received.get());
        assertEquals(0, terminals.get());
        assertFalse(consumer.terminalFailureObserved());
        assertEquals(1, appLogCount(database, trace.eventId()));
        try (var connection = database.api();
            var statement = connection.createStatement();
            var rows =
                statement.executeQuery(
                    "select service,category,action,http_method,request_uri,status_code,duration_ms,details,source_message_id,correlation_id from schubert.app_logs")) {
          assertTrue(rows.next());
          assertEquals("WEB", rows.getString(1));
          assertEquals("REQUEST", rows.getString(2));
          assertEquals("HTTP_REQUEST_COMPLETED", rows.getString(3));
          assertEquals("GET", rows.getString(4));
          assertEquals("/login", rows.getString(5));
          assertEquals(200, rows.getInt(6));
          assertEquals(12, rows.getLong(7));
          assertEquals(
              com.google.gson.JsonParser.parseString(
                  "{\"responseBytes\":3,\"projectionStatus\":\"PENDING\"}"),
              com.google.gson.JsonParser.parseString(rows.getString(8)));
          assertEquals(trace.eventId(), rows.getObject(9, UUID.class));
          assertEquals(trace.eventId(), rows.getObject(10, UUID.class));
          assertFalse(rows.next());
        }
      }
      assertEquals(2, contexts.get());
    } finally {
      broker.stop();
      database.stop();
    }
  }

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
    return appLogCount(db, MESSAGE);
  }

  private static int appLogCount(WebLogDatabaseFixture db, UUID sourceMessage) throws SQLException {
    try (Connection connection = db.api();
        var statement =
            connection.prepareStatement(
                "select count(*) from schubert.app_logs where source_message_id=?")) {
      statement.setObject(1, sourceMessage);
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
