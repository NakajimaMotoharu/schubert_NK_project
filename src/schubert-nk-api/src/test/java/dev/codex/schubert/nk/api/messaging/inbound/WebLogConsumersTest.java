package dev.codex.schubert.nk.api.messaging.inbound;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.protocol.transport.BrokerTopology;
import jakarta.jms.BytesMessage;
import jakarta.jms.DeliveryMode;
import jakarta.jms.JMSConsumer;
import jakarta.jms.JMSContext;
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

/** PG228/PT-JMS-015: actual Artemis Web-log projection consumer, not full API bootstrap. */
final class WebLogConsumersTest {
  private static final String FIXTURE_VM_0_0C76084A = "vm://0";

  @Test
  void jmsown002AcquisitionFailureAndNullKeepIdentityWithoutFatalNotification() {
    for (Throwable failure :
        new Throwable[] {
          new IllegalArgumentException("public factory argument"),
          new IllegalStateException("public factory state"),
          new NullPointerException("public factory null"),
          new AssertionError("public factory fatal")
        }) {
      var calls = new AtomicInteger();
      var signals = new AtomicInteger();
      assertSame(
          failure,
          assertThrows(
              Throwable.class,
              () ->
                  WebLogConsumers.start(
                      () -> {
                        calls.incrementAndGet();
                        if (failure instanceof RuntimeException runtime) throw runtime;
                        throw (Error) failure;
                      },
                      new WebLogListener(ignored -> {}, Clock.systemUTC()),
                      ignored -> {},
                      signals::incrementAndGet)));
      assertEquals(1, calls.get());
      assertEquals(0, signals.get());
    }
    var calls = new AtomicInteger();
    var signals = new AtomicInteger();
    assertThrows(
        NullPointerException.class,
        () ->
            WebLogConsumers.start(
                () -> {
                  calls.incrementAndGet();
                  return null;
                },
                new WebLogListener(ignored -> {}, Clock.systemUTC()),
                ignored -> {},
                signals::incrementAndGet));
    assertEquals(1, calls.get());
    assertEquals(0, signals.get());
  }

  private static final Clock CLOCK =
      Clock.fixed(Instant.parse("2026-09-03T00:00:00Z"), ZoneOffset.UTC);
  private static final UUID EVENT_ID = UUID.fromString("00000000-0000-0000-0000-000000000003");
  private static final UUID CORRELATION_ID =
      UUID.fromString("00000000-0000-0000-0000-000000000001");

  @Test
  void oneConsumerCommitsValidatedWebLog(@TempDir Path root) throws Exception {
    EmbeddedActiveMQ broker = startBroker(root);
    try (var factory = new ActiveMQConnectionFactory(FIXTURE_VM_0_0C76084A);
        JMSContext producer = factory.createContext(JMSContext.AUTO_ACKNOWLEDGE)) {
      var processed = new AtomicInteger();
      var done = new CountDownLatch(1);
      try (var runtime =
          WebLogConsumers.start(
              () -> factory.createContext(JMSContext.SESSION_TRANSACTED),
              new WebLogListener(
                  event -> {
                    assertEquals("WLGEVT01", event.header().layoutId().value());
                    assertEquals(2_080, event.payload().dataLength());
                    processed.incrementAndGet();
                    done.countDown();
                  },
                  CLOCK),
              failure -> {
                throw new AssertionError(failure);
              })) {
        assertTrue(runtime.ready());
        assertFalse(runtime.terminalFailureObserved());
        assertEquals(1, consumerCount(broker));
        sendValid(producer);
        assertTrue(done.await(5, TimeUnit.SECONDS));
        awaitEmpty(broker);
        assertEquals(1, processed.get());
      }
      assertEquals(0, consumerCount(broker));
    } finally {
      broker.stop();
    }
  }

  @Test
  void temporaryProcessorFailureRollsBackAndRedelivers(@TempDir Path root) throws Exception {
    EmbeddedActiveMQ broker = startBroker(root);
    try (var factory = new ActiveMQConnectionFactory(FIXTURE_VM_0_0C76084A);
        JMSContext producer = factory.createContext(JMSContext.AUTO_ACKNOWLEDGE)) {
      var attempts = new AtomicInteger();
      var done = new CountDownLatch(1);
      try (var runtime =
          WebLogConsumers.start(
              () -> factory.createContext(JMSContext.SESSION_TRANSACTED),
              new WebLogListener(
                  event -> {
                    if (attempts.incrementAndGet() == 1) {
                      throw new IllegalStateException("synthetic temporary failure");
                    }
                    done.countDown();
                  },
                  CLOCK),
              failure -> {
                throw new AssertionError(failure);
              })) {
        sendValid(producer);
        assertTrue(done.await(5, TimeUnit.SECONDS));
        awaitEmpty(broker);
        assertEquals(2, attempts.get());
        assertTrue(runtime.ready());
      }
    } finally {
      broker.stop();
    }
  }

  @Test
  void permanentInvalidEventsCommitDlqAndSignalTerminalOnce(@TempDir Path root) throws Exception {
    EmbeddedActiveMQ broker = startBroker(root);
    try (var factory = new ActiveMQConnectionFactory(FIXTURE_VM_0_0C76084A);
        JMSContext producer = factory.createContext(JMSContext.AUTO_ACKNOWLEDGE);
        JMSContext observer = factory.createContext(JMSContext.AUTO_ACKNOWLEDGE);
        var dlq = observer.createConsumer(queue(BrokerTopology.DEAD_LETTER))) {
      var processed = new AtomicInteger();
      var signals = new AtomicInteger();
      var terminal = new AtomicReference<CommittedFatalInboundException>();
      var notified = new CountDownLatch(1);
      try (var runtime =
          WebLogConsumers.start(
              () -> factory.createContext(JMSContext.SESSION_TRANSACTED),
              new WebLogListener(ignored -> processed.incrementAndGet(), CLOCK),
              failure -> {
                terminal.set(failure);
                signals.incrementAndGet();
                notified.countDown();
              })) {
        sendInvalid(producer);
        assertNotNull(dlq.receive(5_000));
        assertTrue(notified.await(5, TimeUnit.SECONDS));
        producer
            .createProducer()
            .setDeliveryMode(DeliveryMode.PERSISTENT)
            .send(
                queue(BrokerTopology.WEB_LOG), producer.createTextMessage("second-unacknowledged"));
        assertNull(dlq.receive(200));
        assertEquals(0, processed.get());
        assertEquals(1, signals.get());
        assertNotNull(terminal.get());
        assertTrue(runtime.terminalFailureObserved());
        assertFalse(runtime.ready());
      }
      try (var pending = observer.createConsumer(queue(BrokerTopology.WEB_LOG))) {
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
  void startupRejectsNullAndWrongModeBeforeDelivery(@TempDir Path root) throws Exception {
    EmbeddedActiveMQ broker = startBroker(root);
    try (var factory = new ActiveMQConnectionFactory(FIXTURE_VM_0_0C76084A)) {
      var listener = new WebLogListener(ignored -> {}, CLOCK);
      assertThrows(
          NullPointerException.class, () -> WebLogConsumers.start(null, listener, ignored -> {}));
      assertThrows(
          NullPointerException.class,
          () ->
              WebLogConsumers.start(
                  () -> factory.createContext(JMSContext.SESSION_TRANSACTED), null, ignored -> {}));
      assertThrows(
          NullPointerException.class,
          () ->
              WebLogConsumers.start(
                  () -> factory.createContext(JMSContext.SESSION_TRANSACTED), listener, null));
      assertThrows(
          NullPointerException.class,
          () -> WebLogConsumers.start(() -> null, listener, ignored -> {}));
      var failure =
          assertThrows(
              IllegalStateException.class,
              () ->
                  WebLogConsumers.start(
                      () -> factory.createContext(JMSContext.AUTO_ACKNOWLEDGE),
                      listener,
                      ignored -> {}));
      assertEquals("API Web log consumer startup failed", failure.getMessage());
      assertEquals(0, consumerCount(broker));
    } finally {
      broker.stop();
    }
  }

  @Test
  void closeIsIdempotentAndStartupPreservesCloseFailure() {
    var closes = new AtomicInteger();
    var listener = new WebLogListener(ignored -> {}, CLOCK);
    var runtime =
        WebLogConsumers.start(() -> syntheticContext(closes, false, true), listener, ignored -> {});
    assertTrue(runtime.ready());
    var closeFailure = assertThrows(IllegalStateException.class, runtime::close);
    assertEquals("API Web log consumer close failed", closeFailure.getMessage());
    assertEquals(1, closes.get());
    assertFalse(runtime.ready());
    // SSC314/BUG1554: a permanent provider fault cannot turn into a normal no-op.
    assertThrows(IllegalStateException.class, runtime::close);
    assertEquals(2, closes.get());

    closes.set(0);
    var startupFailure =
        assertThrows(
            IllegalStateException.class,
            () ->
                WebLogConsumers.start(
                    () -> syntheticContext(closes, true, true), listener, ignored -> {}));
    assertEquals("API Web log consumer startup failed", startupFailure.getMessage());
    assertEquals(1, closes.get());
    assertEquals(1, startupFailure.getCause().getSuppressed().length);
    assertEquals(
        "API Web log consumer close failed",
        startupFailure.getCause().getSuppressed()[0].getMessage());
  }

  private static JMSContext syntheticContext(
      AtomicInteger closes, boolean failStart, boolean failClose) {
    JMSConsumer consumer =
        (JMSConsumer)
            Proxy.newProxyInstance(
                JMSConsumer.class.getClassLoader(),
                new Class<?>[] {JMSConsumer.class},
                (ignored, method, arguments) -> {
                  if (method.getName().equals("setMessageListener")) return null;
                  throw new AssertionError("unexpected consumer call " + method.getName());
                });
    return (JMSContext)
        Proxy.newProxyInstance(
            JMSContext.class.getClassLoader(),
            new Class<?>[] {JMSContext.class},
            (ignored, method, arguments) -> {
              return switch (method.getName()) {
                case "setAutoStart" -> null;
                case "getSessionMode" -> JMSContext.SESSION_TRANSACTED;
                case "createConsumer" -> consumer;
                case "start" -> {
                  if (failStart) throw new IllegalStateException("synthetic start failure");
                  yield null;
                }
                case "close" -> {
                  closes.incrementAndGet();
                  if (failClose) throw new IllegalStateException("synthetic close failure");
                  yield null;
                }
                default -> throw new AssertionError("unexpected context call " + method.getName());
              };
            });
  }

  private static void sendValid(JMSContext producer) throws Exception {
    BytesMessage message = producer.createBytesMessage();
    message.writeBytes(validWire());
    message.setJMSCorrelationID(CORRELATION_ID.toString());
    message.setStringProperty("NKMessageID", EVENT_ID.toString());
    message.setStringProperty("NKLayoutID", "WLGEVT01");
    message.setStringProperty("NKProtocolVersion", "001");
    producer
        .createProducer()
        .setDeliveryMode(DeliveryMode.PERSISTENT)
        .send(queue(BrokerTopology.WEB_LOG), message);
  }

  private static void sendInvalid(JMSContext producer) {
    TextMessage message = producer.createTextMessage("synthetic-invalid");
    producer
        .createProducer()
        .setDeliveryMode(DeliveryMode.PERSISTENT)
        .send(queue(BrokerTopology.WEB_LOG), message);
  }

  private static byte[] validWire() {
    byte[] body = new byte[2_336];
    Arrays.fill(body, (byte) ' ');
    ascii(body, 0, "SCHBNK01");
    ascii(body, 8, "001");
    ascii(body, 11, "WLGEVT01");
    ascii(body, 19, "001");
    body[22] = 'E';
    body[23] = 'I';
    ascii(body, 24, EVENT_ID.toString());
    ascii(body, 60, CORRELATION_ID.toString());
    ascii(body, 96, "20260903120000000");
    ascii(body, 177, "0256");
    ascii(body, 181, "002080");
    ascii(body, 187, "000000");
    ascii(body, 193, "000000");
    ascii(body, 199, "000002336");
    return body;
  }

  private static void ascii(byte[] target, int offset, String value) {
    byte[] source = value.getBytes(StandardCharsets.US_ASCII);
    System.arraycopy(source, 0, target, offset, source.length);
  }

  private static ActiveMQQueue queue(BrokerTopology destination) {
    return new ActiveMQQueue(destination.fullyQualifiedQueue());
  }

  private static long consumerCount(EmbeddedActiveMQ broker) {
    return broker
        .getActiveMQServer()
        .locateQueue(SimpleString.of(BrokerTopology.WEB_LOG.queue()))
        .getConsumerCount();
  }

  private static void awaitEmpty(EmbeddedActiveMQ broker) throws Exception {
    long deadline = System.nanoTime() + TimeUnit.SECONDS.toNanos(5);
    while (broker
            .getActiveMQServer()
            .locateQueue(SimpleString.of(BrokerTopology.WEB_LOG.queue()))
            .getMessageCount()
        != 0) {
      assertTrue(System.nanoTime() < deadline, "Web log Queue did not commit before deadline");
      Thread.sleep(10);
    }
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
}
