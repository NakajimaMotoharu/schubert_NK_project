package dev.codex.schubert.nk.api.messaging.inbound;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import jakarta.jms.BytesMessage;
import jakarta.jms.DeliveryMode;
import jakarta.jms.JMSConsumer;
import jakarta.jms.JMSContext;
import jakarta.jms.Message;
import jakarta.jms.TextMessage;
import java.io.InputStream;
import java.lang.reflect.Proxy;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Clock;
import java.time.Instant;
import java.time.ZoneOffset;
import java.util.Arrays;
import java.util.UUID;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicReference;
import org.apache.activemq.artemis.api.core.SimpleString;
import org.apache.activemq.artemis.core.config.Configuration;
import org.apache.activemq.artemis.core.deployers.impl.FileConfigurationParser;
import org.apache.activemq.artemis.core.server.embedded.EmbeddedActiveMQ;
import org.apache.activemq.artemis.jms.client.ActiveMQConnectionFactory;
import org.apache.activemq.artemis.jms.client.ActiveMQQueue;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** PT-JMS-013: real four-consumer startup, transaction, fatal path, and partial-start rollback. */
final class SyncRequestConsumersTest {
  private static final String FIXTURE_VM_0_0C76084A = "vm://0";
  private static final String FIXTURE_NK_SYNC_REQUEST_NK_SYNC_REQUEST_Q_D0778F85 =
      "nk.sync.request::nk.sync.request.q";
  private static final UUID REQUEST_ID = UUID.fromString("00000000-0000-0000-0000-000000000001");
  private static final UUID RESPONSE_ID = UUID.fromString("00000000-0000-0000-0000-000000000002");
  private static final Clock CLOCK =
      Clock.fixed(Instant.parse("2026-09-03T00:00:00Z"), ZoneOffset.UTC);

  @Test
  void fourConsumersReceiveAndCommitOneReply(@TempDir Path root) throws Exception {
    EmbeddedActiveMQ broker = start(root);
    try (ActiveMQConnectionFactory factory = new ActiveMQConnectionFactory(FIXTURE_VM_0_0C76084A);
        JMSContext producer = factory.createContext(JMSContext.AUTO_ACKNOWLEDGE);
        JMSContext observer = factory.createContext(JMSContext.AUTO_ACKNOWLEDGE);
        var replies =
            observer.createConsumer(new ActiveMQQueue("nk.sync.reply.web::nk.sync.reply.web.q"))) {
      AtomicInteger processed = new AtomicInteger();
      byte[] goldenReply = wire('S', "LOGRSP01", RESPONSE_ID, REQUEST_ID, 24, true);
      try (SyncRequestConsumers consumers =
          SyncRequestConsumers.start(
              () -> factory.createContext(JMSContext.SESSION_TRANSACTED),
              new SyncRequestListener(
                  request -> {
                    assertEquals("LOGREQ01", request.header().layoutId().value());
                    processed.incrementAndGet();
                    return goldenReply;
                  },
                  CLOCK),
              failure -> {
                throw new AssertionError(failure);
              })) {
        assertTrue(consumers.ready());
        assertFalse(consumers.terminalFailureObserved());
        assertEquals(
            4,
            broker
                .getActiveMQServer()
                .locateQueue(SimpleString.of("nk.sync.request.q"))
                .getConsumerCount());
        sendRequest(producer);
        BytesMessage reply = (BytesMessage) replies.receive(5_000);
        assertNotNull(reply);
        byte[] actual = new byte[Math.toIntExact(reply.getBodyLength())];
        assertEquals(actual.length, reply.readBytes(actual));
        assertArrayEquals(goldenReply, actual);
        assertEquals(1, processed.get());
      }
      assertEquals(
          0,
          broker
              .getActiveMQServer()
              .locateQueue(SimpleString.of("nk.sync.request.q"))
              .getConsumerCount());
    } finally {
      broker.stop();
    }
  }

  @Test
  void invalidMessageCommitsToDlqAndSignalsTerminal(@TempDir Path root) throws Exception {
    EmbeddedActiveMQ broker = start(root);
    try (ActiveMQConnectionFactory factory = new ActiveMQConnectionFactory(FIXTURE_VM_0_0C76084A);
        JMSContext producer = factory.createContext(JMSContext.AUTO_ACKNOWLEDGE);
        JMSContext observer = factory.createContext(JMSContext.AUTO_ACKNOWLEDGE);
        var dlq = observer.createConsumer(new ActiveMQQueue("nk.dead.letter::nk.dead.letter.q"))) {
      AtomicReference<CommittedFatalInboundException> terminal = new AtomicReference<>();
      AtomicInteger signals = new AtomicInteger();
      var notified = new CountDownLatch(1);
      try (SyncRequestConsumers consumers =
          SyncRequestConsumers.start(
              () -> factory.createContext(JMSContext.SESSION_TRANSACTED),
              new SyncRequestListener(
                  ignored -> wire('S', "LOGRSP01", RESPONSE_ID, REQUEST_ID, 24, true), CLOCK),
              failure -> {
                terminal.set(failure);
                signals.incrementAndGet();
                notified.countDown();
              })) {
        TextMessage bad = producer.createTextMessage("synthetic-invalid");
        bad.setStringProperty("NKLayoutID", "invalid");
        producer
            .createProducer()
            .setDeliveryMode(DeliveryMode.PERSISTENT)
            .send(new ActiveMQQueue(FIXTURE_NK_SYNC_REQUEST_NK_SYNC_REQUEST_Q_D0778F85), bad);
        Message isolated = dlq.receive(5_000);
        assertNotNull(isolated);
        assertTrue(notified.await(5, TimeUnit.SECONDS));
        producer
            .createProducer()
            .setDeliveryMode(DeliveryMode.PERSISTENT)
            .send(
                new ActiveMQQueue(FIXTURE_NK_SYNC_REQUEST_NK_SYNC_REQUEST_Q_D0778F85),
                producer.createTextMessage("second-unacknowledged"));
        assertNull(dlq.receive(200));
        assertNotNull(terminal.get());
        assertEquals(1, signals.get());
        assertFalse(consumers.ready());
        assertTrue(consumers.terminalFailureObserved());
      }
      try (var pending =
          observer.createConsumer(
              new ActiveMQQueue(FIXTURE_NK_SYNC_REQUEST_NK_SYNC_REQUEST_Q_D0778F85))) {
        var returned = pending.receive(10_000);
        assertNotNull(returned);
        assertEquals("second-unacknowledged", returned.getBody(String.class));
        assertNull(pending.receiveNoWait());
      }
    } finally {
      broker.stop();
    }
  }

  @Test
  void temporaryBusinessFailureRollsBackAndRedelivers(@TempDir Path root) throws Exception {
    EmbeddedActiveMQ broker = start(root);
    try (ActiveMQConnectionFactory factory = new ActiveMQConnectionFactory(FIXTURE_VM_0_0C76084A);
        JMSContext producer = factory.createContext(JMSContext.AUTO_ACKNOWLEDGE);
        JMSContext observer = factory.createContext(JMSContext.AUTO_ACKNOWLEDGE);
        var replies =
            observer.createConsumer(new ActiveMQQueue("nk.sync.reply.web::nk.sync.reply.web.q"))) {
      AtomicInteger attempts = new AtomicInteger();
      try (SyncRequestConsumers consumers =
          SyncRequestConsumers.start(
              () -> factory.createContext(JMSContext.SESSION_TRANSACTED),
              new SyncRequestListener(
                  ignored -> {
                    if (attempts.incrementAndGet() == 1) {
                      throw new IllegalStateException("synthetic temporary failure");
                    }
                    return wire('S', "LOGRSP01", RESPONSE_ID, REQUEST_ID, 24, true);
                  },
                  CLOCK),
              failure -> {
                throw new AssertionError(failure);
              })) {
        sendRequest(producer);
        assertNotNull(replies.receive(5_000));
        assertEquals(2, attempts.get());
        assertTrue(consumers.ready());
      }
    } finally {
      broker.stop();
    }
  }

  @Test
  void closeIsIdempotentAndAggregatesAllContextFailures() {
    AtomicInteger closes = new AtomicInteger();
    AtomicInteger created = new AtomicInteger();
    SyncRequestConsumers consumers =
        SyncRequestConsumers.start(
            () -> syntheticContext(created.incrementAndGet(), closes, false),
            new SyncRequestListener(ignored -> new byte[0], CLOCK),
            ignored -> {});
    assertTrue(consumers.ready());
    IllegalStateException failure = assertThrows(IllegalStateException.class, consumers::close);
    assertEquals("API sync consumer close failed", failure.getMessage());
    assertEquals("synthetic-close-1", failure.getCause().getMessage());
    assertEquals(1, failure.getCause().getSuppressed().length);
    assertEquals("synthetic-close-2", failure.getCause().getSuppressed()[0].getMessage());
    assertEquals(4, closes.get());
    assertFalse(consumers.ready());
    // SSC314/BUG1554: only the two failed contexts are retried; healthy contexts stay closed.
    var retried = assertThrows(IllegalStateException.class, consumers::close);
    assertEquals("synthetic-close-1", retried.getCause().getMessage());
    assertEquals(6, closes.get());
  }

  @Test
  void failedStartupPreservesClosingFailureAsSuppressed() {
    AtomicInteger created = new AtomicInteger();
    AtomicInteger closes = new AtomicInteger();
    IllegalStateException failure =
        assertThrows(
            IllegalStateException.class,
            () ->
                SyncRequestConsumers.start(
                    () ->
                        created.incrementAndGet() == 1 ? syntheticContext(1, closes, false) : null,
                    new SyncRequestListener(ignored -> new byte[0], CLOCK),
                    ignored -> {}));
    assertEquals(1, closes.get());
    assertEquals("API sync consumer startup failed", failure.getMessage());
    assertTrue(failure.getCause() instanceof NullPointerException);
    assertEquals(1, failure.getCause().getSuppressed().length);
    assertEquals(
        "API sync consumer close failed", failure.getCause().getSuppressed()[0].getMessage());
    assertEquals(
        "synthetic-close-1", failure.getCause().getSuppressed()[0].getCause().getMessage());
  }

  @Test
  void partialStartupRejectsWrongSessionAndClosesAll(@TempDir Path root) throws Exception {
    EmbeddedActiveMQ broker = start(root);
    try (ActiveMQConnectionFactory factory = new ActiveMQConnectionFactory(FIXTURE_VM_0_0C76084A)) {
      AtomicInteger count = new AtomicInteger();
      assertThrows(
          IllegalStateException.class,
          () ->
              SyncRequestConsumers.start(
                  () ->
                      factory.createContext(
                          count.incrementAndGet() == 3
                              ? JMSContext.AUTO_ACKNOWLEDGE
                              : JMSContext.SESSION_TRANSACTED),
                  new SyncRequestListener(ignored -> new byte[0], CLOCK),
                  ignored -> {}));
      assertEquals(3, count.get());
      assertEquals(
          0,
          broker
              .getActiveMQServer()
              .locateQueue(SimpleString.of("nk.sync.request.q"))
              .getConsumerCount());
      assertThrows(
          NullPointerException.class,
          () ->
              SyncRequestConsumers.start(
                  null, new SyncRequestListener(ignored -> new byte[0], CLOCK), ignored -> {}));
      assertThrows(
          NullPointerException.class,
          () ->
              SyncRequestConsumers.start(
                  () -> factory.createContext(JMSContext.SESSION_TRANSACTED), null, ignored -> {}));
      assertThrows(
          NullPointerException.class,
          () ->
              SyncRequestConsumers.start(
                  () -> factory.createContext(JMSContext.SESSION_TRANSACTED),
                  new SyncRequestListener(ignored -> new byte[0], CLOCK),
                  null));
    } finally {
      broker.stop();
    }
  }

  private static void sendRequest(JMSContext context) throws Exception {
    BytesMessage request = context.createBytesMessage();
    request.writeBytes(wire('Q', "LOGREQ01", REQUEST_ID, REQUEST_ID, 0, false));
    request.setJMSCorrelationID(REQUEST_ID.toString());
    request.setJMSReplyTo(new ActiveMQQueue("nk.sync.reply.web"));
    request.setStringProperty("NKMessageID", REQUEST_ID.toString());
    request.setStringProperty("NKLayoutID", "LOGREQ01");
    request.setStringProperty("NKProtocolVersion", "001");
    context
        .createProducer()
        .setDeliveryMode(DeliveryMode.PERSISTENT)
        .setTimeToLive(5_000)
        .send(new ActiveMQQueue(FIXTURE_NK_SYNC_REQUEST_NK_SYNC_REQUEST_Q_D0778F85), request);
  }

  /** Independent SS322 byte-offset oracle; production encoder is never used for expected bytes. */
  private static byte[] wire(
      char kind,
      String layout,
      UUID messageId,
      UUID correlationId,
      int dataLength,
      boolean response) {
    int totalLength = 256 + dataLength;
    byte[] body = new byte[totalLength];
    Arrays.fill(body, (byte) ' ');
    ascii(body, 0, "SCHBNK01");
    ascii(body, 8, "001");
    ascii(body, 11, layout);
    ascii(body, 19, "001");
    body[22] = (byte) kind;
    body[23] = 'S';
    ascii(body, 24, messageId.toString());
    ascii(body, 60, correlationId.toString());
    ascii(body, 96, "20260903120000000");
    ascii(body, 113, "a".repeat(64));
    ascii(body, 177, "0256");
    ascii(body, 181, "%06d".formatted(dataLength));
    ascii(body, 187, "000000");
    ascii(body, 193, "000000");
    ascii(body, 199, "%09d".formatted(totalLength));
    if (response) {
      ascii(body, 208, "0000");
    }
    return body;
  }

  private static void ascii(byte[] target, int offset, String value) {
    byte[] source = value.getBytes(StandardCharsets.US_ASCII);
    System.arraycopy(source, 0, target, offset, source.length);
  }

  private static JMSContext syntheticContext(int ordinal, AtomicInteger closes, boolean failStart) {
    JMSConsumer consumer =
        (JMSConsumer)
            Proxy.newProxyInstance(
                JMSConsumer.class.getClassLoader(),
                new Class<?>[] {JMSConsumer.class},
                (proxy, method, arguments) -> {
                  if (method.getName().equals("setMessageListener")) {
                    return null;
                  }
                  throw new UnsupportedOperationException(method.getName());
                });
    return (JMSContext)
        Proxy.newProxyInstance(
            JMSContext.class.getClassLoader(),
            new Class<?>[] {JMSContext.class},
            (proxy, method, arguments) -> {
              return switch (method.getName()) {
                case "setAutoStart" -> null;
                case "getSessionMode" -> JMSContext.SESSION_TRANSACTED;
                case "createConsumer" -> consumer;
                case "start" -> {
                  if (failStart) {
                    throw new IllegalStateException("synthetic-start");
                  }
                  yield null;
                }
                case "close" -> {
                  closes.incrementAndGet();
                  if (ordinal <= 2) {
                    throw new IllegalStateException("synthetic-close-" + ordinal);
                  }
                  yield null;
                }
                default -> throw new UnsupportedOperationException(method.getName());
              };
            });
  }

  private static EmbeddedActiveMQ start(Path root) throws Exception {
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
}
