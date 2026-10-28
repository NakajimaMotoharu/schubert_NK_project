package dev.codex.schubert.nk.api.messaging.inbound;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.api.messaging.outbound.FatalDlqMetadata;
import dev.codex.schubert.nk.protocol.header.InteractionKind;
import dev.codex.schubert.nk.protocol.header.MessageKind;
import dev.codex.schubert.nk.protocol.transport.BrokerTopology;
import jakarta.jms.BytesMessage;
import jakarta.jms.DeliveryMode;
import jakarta.jms.JMSConsumer;
import jakarta.jms.JMSContext;
import jakarta.jms.Message;
import jakarta.jms.Queue;
import jakarta.jms.TextMessage;
import java.io.InputStream;
import java.lang.reflect.Proxy;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Clock;
import java.time.Instant;
import java.time.ZoneOffset;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.UUID;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicReference;
import org.apache.activemq.artemis.core.config.Configuration;
import org.apache.activemq.artemis.core.deployers.impl.FileConfigurationParser;
import org.apache.activemq.artemis.core.server.embedded.EmbeddedActiveMQ;
import org.apache.activemq.artemis.jms.client.ActiveMQConnectionFactory;
import org.apache.activemq.artemis.jms.client.ActiveMQQueue;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** PT-JMS-005/006/007/009 async-work and Web-log listener route matrix. */
final class InternalEventListenerTest {
  private static final String FIXTURE_VM_0_0C76084A = "vm://0";
  private static final String FIXTURE_QWKREQ01_19741256 = "QWKREQ01";
  private static final String FIXTURE_WLGEVT01_31AD1E1D = "WLGEVT01";
  private static final String FIXTURE_001_A3FEAA64 = "001";
  private static final UUID EVENT_ID = UUID.fromString("00000000-0000-0000-0000-000000000003");
  private static final UUID CORRELATION_ID =
      UUID.fromString("00000000-0000-0000-0000-000000000001");
  private static final Instant NOW = Instant.parse("2026-09-03T00:00:00Z");
  private static final Clock CLOCK = Clock.fixed(NOW, ZoneOffset.UTC);

  @Test
  @DisplayName("PT-JMS-EVENT-DELIVERY: actual guarded broker redeliveries 1 through 4")
  void deliveryAwareWorkerReceivesActualCountAndOriginalTransport(@TempDir Path root)
      throws Exception {
    var broker = start(root);
    try (var factory = new ActiveMQConnectionFactory(FIXTURE_VM_0_0C76084A);
        var producer = factory.createContext(JMSContext.AUTO_ACKNOWLEDGE);
        var receiving = factory.createContext(JMSContext.SESSION_TRANSACTED);
        var work = receiving.createConsumer(queue(BrokerTopology.ASYNC_WORK))) {
      var observed = new ArrayList<DeliveryMetadata>();
      var lastEvent =
          new AtomicReference<
              dev.codex.schubert.nk.protocol.layout.WireMessage<
                  dev.codex.schubert.nk.protocol.layout.FixedPayload>>();
      var failure = new IllegalStateException("synthetic temporary worker failure");
      InternalEventProcessor processor =
          new InternalEventProcessor() {
            @Override
            public void process(
                dev.codex.schubert.nk.protocol.layout.WireMessage<
                        dev.codex.schubert.nk.protocol.layout.FixedPayload>
                    event) {
              throw new AssertionError("delivery-aware entry was bypassed");
            }

            @Override
            public void process(
                dev.codex.schubert.nk.protocol.layout.WireMessage<
                        dev.codex.schubert.nk.protocol.layout.FixedPayload>
                    event,
                DeliveryMetadata delivery) {
              assertEquals(FIXTURE_QWKREQ01_19741256, event.header().layoutId().value());
              lastEvent.set(event);
              observed.add(delivery);
              if (delivery.deliveryCount() < 4) throw failure;
            }
          };
      var listener = new QuestionWorkListener(processor, CLOCK);
      sendEvent(producer, BrokerTopology.ASYNC_WORK, eventWire(FIXTURE_QWKREQ01_19741256, 64));
      String transport = null;
      for (int count = 1; count <= 4; count++) {
        // SS321/QA041: actual delays are 1s, 5s, 25s. Keep the approved broker profile.
        Message actual = required(work.receive(35000));
        assertEquals(count, actual.getIntProperty("JMSXDeliveryCount"));
        if (transport == null) transport = actual.getJMSMessageID();
        assertEquals(transport, actual.getJMSMessageID());
        if (count < 4)
          assertSame(
              failure,
              assertThrows(
                  IllegalStateException.class, () -> listener.onMessage(receiving, actual)));
        else listener.onMessage(receiving, actual);
        assertEquals(count, observed.size());
        assertEquals(count, observed.get(count - 1).deliveryCount());
        assertEquals(transport, observed.get(count - 1).transportMessageId());
        assertEquals(NOW, observed.get(count - 1).receivedAt());
      }
      assertEquals(
          List.of(1, 2, 3, 4), observed.stream().map(DeliveryMetadata::deliveryCount).toList());
      assertNull(work.receive(100));
      InternalEventProcessor legacy =
          event -> {
            throw new AssertionError("null reached legacy");
          };
      assertThrows(NullPointerException.class, () -> legacy.process(null, observed.getFirst()));
      assertThrows(NullPointerException.class, () -> legacy.process(lastEvent.get(), null));
    } finally {
      broker.stop();
    }
  }

  @Test
  @DisplayName("PT-JMS-EVENT-DELIVERY: unbounded transport metadata is isolated before business")
  void invalidDeliveryMetadataCannotReachBusiness(@TempDir Path root) throws Exception {
    var broker = start(root);
    try (var factory = new ActiveMQConnectionFactory(FIXTURE_VM_0_0C76084A);
        var producer = factory.createContext(JMSContext.AUTO_ACKNOWLEDGE);
        var receiving = factory.createContext(JMSContext.SESSION_TRANSACTED);
        var observing = factory.createContext(JMSContext.AUTO_ACKNOWLEDGE);
        var work = receiving.createConsumer(queue(BrokerTopology.ASYNC_WORK));
        var dlq = observing.createConsumer(queue(BrokerTopology.DEAD_LETTER))) {
      var calls = new AtomicInteger();
      var listener = new QuestionWorkListener(event -> calls.incrementAndGet(), CLOCK);
      sendEvent(producer, BrokerTopology.ASYNC_WORK, eventWire(FIXTURE_QWKREQ01_19741256, 64));
      var original = required(work.receive(5000));
      var malformed =
          (BytesMessage)
              Proxy.newProxyInstance(
                  BytesMessage.class.getClassLoader(),
                  new Class<?>[] {BytesMessage.class},
                  (proxy, method, args) -> {
                    if (method.getName().equals("getJMSMessageID")) return "!".repeat(129);
                    try {
                      return method.invoke(original, args);
                    } catch (java.lang.reflect.InvocationTargetException failure) {
                      throw failure.getCause();
                    }
                  });
      assertThrows(
          CommittedFatalInboundException.class, () -> listener.onMessage(receiving, malformed));
      assertEquals(0, calls.get());
      var isolated = required(dlq.receive(5000));
      assertEquals("UNAVAILABLE", isolated.getStringProperty("NKOriginalTransportID"));
      assertEquals("PROTOCOL_INVALID", isolated.getStringProperty("NKErrorCode"));
      assertNull(work.receive(100));
    } finally {
      broker.stop();
    }
  }

  @Test
  @DisplayName("PT-JMS-005/007 work and Web-log events validate and commit on exact queues")
  void bothInternalEventRoutesProcessAndCommit(@TempDir Path root) throws Exception {
    EmbeddedActiveMQ broker = start(root);
    try (ActiveMQConnectionFactory factory = new ActiveMQConnectionFactory(FIXTURE_VM_0_0C76084A);
        JMSContext producer = factory.createContext(JMSContext.AUTO_ACKNOWLEDGE);
        JMSContext listenerContext = factory.createContext(JMSContext.SESSION_TRANSACTED);
        JMSConsumer workQueue = listenerContext.createConsumer(queue(BrokerTopology.ASYNC_WORK));
        JMSConsumer logQueue = listenerContext.createConsumer(queue(BrokerTopology.WEB_LOG))) {
      AtomicInteger workCount = new AtomicInteger();
      AtomicInteger logCount = new AtomicInteger();
      QuestionWorkListener work =
          new QuestionWorkListener(
              event -> {
                workCount.incrementAndGet();
                assertEquals(FIXTURE_QWKREQ01_19741256, event.header().layoutId().value());
                assertEquals(MessageKind.EVENT, event.header().messageKind());
                assertEquals(InteractionKind.INTERNAL, event.header().interactionKind());
                assertEquals(64, event.payload().dataLength());
              },
              CLOCK);
      WebLogListener log =
          new WebLogListener(
              event -> {
                logCount.incrementAndGet();
                assertEquals(FIXTURE_WLGEVT01_31AD1E1D, event.header().layoutId().value());
                assertEquals(2_080, event.payload().dataLength());
              },
              CLOCK);

      sendEvent(producer, BrokerTopology.ASYNC_WORK, eventWire(FIXTURE_QWKREQ01_19741256, 64));
      work.onMessage(listenerContext, required(workQueue.receive(5_000)));
      sendEvent(producer, BrokerTopology.WEB_LOG, eventWire(FIXTURE_WLGEVT01_31AD1E1D, 2_080));
      log.onMessage(listenerContext, required(logQueue.receive(5_000)));

      var rollbackPhases = new AtomicInteger();
      sendEvent(producer, BrokerTopology.ASYNC_WORK, eventWire(FIXTURE_QWKREQ01_19741256, 64));
      work.onMessage(
          listenerContext,
          required(workQueue.receive(5_000)),
          rollbackPhases::incrementAndGet,
          rollbackPhases::incrementAndGet);
      sendEvent(producer, BrokerTopology.WEB_LOG, eventWire(FIXTURE_WLGEVT01_31AD1E1D, 2_080));
      log.onMessage(
          listenerContext,
          required(logQueue.receive(5_000)),
          rollbackPhases::incrementAndGet,
          rollbackPhases::incrementAndGet);
      assertEquals(0, rollbackPhases.get(), "successful commits never publish rollback phases");
      assertEquals(2, workCount.get());
      assertEquals(2, logCount.get());
      assertNull(workQueue.receive(250));
      assertNull(logQueue.receive(250));
    } finally {
      broker.stop();
    }
  }

  @Test
  @DisplayName("PT-JMS-007 event processor failure rolls back for broker redelivery")
  void eventProcessorFailureRollsBackForRedelivery(@TempDir Path root) throws Exception {
    EmbeddedActiveMQ broker = start(root);
    try (ActiveMQConnectionFactory factory = new ActiveMQConnectionFactory(FIXTURE_VM_0_0C76084A);
        JMSContext producer = factory.createContext(JMSContext.AUTO_ACKNOWLEDGE);
        JMSContext listenerContext = factory.createContext(JMSContext.SESSION_TRANSACTED);
        JMSConsumer workQueue = listenerContext.createConsumer(queue(BrokerTopology.ASYNC_WORK))) {
      IllegalStateException failure = new IllegalStateException("synthetic worker failure");
      QuestionWorkListener listener =
          new QuestionWorkListener(
              ignored -> {
                throw failure;
              },
              CLOCK);
      sendEvent(producer, BrokerTopology.ASYNC_WORK, eventWire(FIXTURE_QWKREQ01_19741256, 64));
      Message first = required(workQueue.receive(5_000));
      assertEquals(1, first.getIntProperty("JMSXDeliveryCount"));
      assertSame(
          failure,
          assertThrows(
              IllegalStateException.class, () -> listener.onMessage(listenerContext, first)));

      Message redelivered = required(workQueue.receive(3_000));
      assertEquals(2, redelivered.getIntProperty("JMSXDeliveryCount"));
      listenerContext.commit();
    } finally {
      broker.stop();
    }
  }

  @Test
  @DisplayName("PT-JMS-006/009 invalid Web-log type is isolated before processor")
  void invalidWebLogIsCommittedToDlqAndSignalsFatal(@TempDir Path root) throws Exception {
    EmbeddedActiveMQ broker = start(root);
    try (ActiveMQConnectionFactory factory = new ActiveMQConnectionFactory(FIXTURE_VM_0_0C76084A);
        JMSContext producer = factory.createContext(JMSContext.AUTO_ACKNOWLEDGE);
        JMSContext listenerContext = factory.createContext(JMSContext.SESSION_TRANSACTED);
        JMSContext observer = factory.createContext(JMSContext.AUTO_ACKNOWLEDGE);
        JMSConsumer logQueue = listenerContext.createConsumer(queue(BrokerTopology.WEB_LOG));
        JMSConsumer dlq = observer.createConsumer(queue(BrokerTopology.DEAD_LETTER))) {
      TextMessage invalid = producer.createTextMessage("opaque invalid Web log");
      invalid.setJMSCorrelationID(CORRELATION_ID.toString());
      invalid.setStringProperty("NKMessageID", EVENT_ID.toString());
      invalid.setStringProperty("NKLayoutID", FIXTURE_WLGEVT01_31AD1E1D);
      invalid.setStringProperty("NKProtocolVersion", FIXTURE_001_A3FEAA64);
      producer
          .createProducer()
          .setDeliveryMode(DeliveryMode.PERSISTENT)
          .setTimeToLive(0)
          .send(queue(BrokerTopology.WEB_LOG), invalid);
      AtomicBoolean processed = new AtomicBoolean();
      WebLogListener listener = new WebLogListener(ignored -> processed.set(true), CLOCK);

      CommittedFatalInboundException failure =
          assertThrows(
              CommittedFatalInboundException.class,
              () -> listener.onMessage(listenerContext, required(logQueue.receive(5_000))));
      assertNotNull(failure.getCause());
      assertFalse(processed.get());
      assertNull(logQueue.receive(250));

      TextMessage isolated = assertInstanceOf(TextMessage.class, dlq.receive(5_000));
      assertEquals("opaque invalid Web log", isolated.getText());
      assertEquals("nk.web.log", isolated.getStringProperty("_AMQ_ORIG_ADDRESS"));
      assertEquals("nk.web.log.q", isolated.getStringProperty("_AMQ_ORIG_QUEUE"));
      assertEquals("API_WEB_LOG", isolated.getStringProperty("NKDetectedBy"));
      assertEquals(0L, isolated.getJMSExpiration());
    } finally {
      broker.stop();
    }
  }

  @Test
  void eventListenerConstructorsAndBoundariesDenyInvalidInputs() {
    InternalEventProcessor processor = ignored -> {};
    assertThrows(NullPointerException.class, () -> new QuestionWorkListener(null, CLOCK));
    assertThrows(NullPointerException.class, () -> new QuestionWorkListener(processor, null));
    assertThrows(NullPointerException.class, () -> new WebLogListener(null, CLOCK));
    assertThrows(NullPointerException.class, () -> new WebLogListener(processor, null));
    assertThrows(
        NullPointerException.class,
        () ->
            new TransactedEventListener(
                null, FatalDlqMetadata.DetectedBy.API_WORK, processor, CLOCK));
    assertThrows(
        NullPointerException.class,
        () -> new TransactedEventListener(BrokerTopology.ASYNC_WORK, null, processor, CLOCK));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            new TransactedEventListener(
                BrokerTopology.SYNC_REQUEST,
                FatalDlqMetadata.DetectedBy.API_WORK,
                processor,
                CLOCK));

    QuestionWorkListener listener = new QuestionWorkListener(processor, CLOCK);
    Message message = textMessage();
    assertThrows(NullPointerException.class, () -> listener.onMessage(null, message));
    assertThrows(
        NullPointerException.class,
        () -> listener.onMessage(context(JMSContext.SESSION_TRANSACTED), null));
    assertThrows(
        IllegalStateException.class,
        () -> listener.onMessage(context(JMSContext.AUTO_ACKNOWLEDGE), message));
  }

  private static Message required(Message message) {
    assertNotNull(message);
    return message;
  }

  private static Queue queue(BrokerTopology destination) {
    return new ActiveMQQueue(destination.fullyQualifiedQueue());
  }

  static void sendEvent(JMSContext context, BrokerTopology destination, byte[] body)
      throws Exception {
    BytesMessage event = context.createBytesMessage();
    event.writeBytes(body);
    event.setJMSCorrelationID(CORRELATION_ID.toString());
    event.setStringProperty("NKMessageID", EVENT_ID.toString());
    event.setStringProperty(
        "NKLayoutID",
        destination == BrokerTopology.ASYNC_WORK
            ? FIXTURE_QWKREQ01_19741256
            : FIXTURE_WLGEVT01_31AD1E1D);
    event.setStringProperty("NKProtocolVersion", FIXTURE_001_A3FEAA64);
    context
        .createProducer()
        .setDeliveryMode(DeliveryMode.PERSISTENT)
        .setTimeToLive(0)
        .send(queue(destination), event);
  }

  private static JMSContext context(int mode) {
    return (JMSContext)
        Proxy.newProxyInstance(
            JMSContext.class.getClassLoader(),
            new Class<?>[] {JMSContext.class},
            (proxy, method, arguments) -> {
              if (method.getName().equals("getSessionMode")) {
                return mode;
              }
              return objectMethod(proxy, method.getName(), arguments);
            });
  }

  private static TextMessage textMessage() {
    return (TextMessage)
        Proxy.newProxyInstance(
            TextMessage.class.getClassLoader(),
            new Class<?>[] {TextMessage.class},
            (proxy, method, arguments) -> objectMethod(proxy, method.getName(), arguments));
  }

  private static Object objectMethod(Object proxy, String method, Object[] arguments) {
    return switch (method) {
      case "toString" -> "SyntheticJmsBoundary";
      case "hashCode" -> System.identityHashCode(proxy);
      case "equals" -> proxy == arguments[0];
      default -> throw new UnsupportedOperationException(method);
    };
  }

  static byte[] eventWire(String layout, int dataLength) {
    int totalLength = 256 + dataLength;
    byte[] body = new byte[totalLength];
    Arrays.fill(body, (byte) ' ');
    ascii(body, 0, "SCHBNK01");
    ascii(body, 8, FIXTURE_001_A3FEAA64);
    ascii(body, 11, layout);
    ascii(body, 19, FIXTURE_001_A3FEAA64);
    body[22] = 'E';
    body[23] = 'I';
    ascii(body, 24, EVENT_ID.toString());
    ascii(body, 60, CORRELATION_ID.toString());
    ascii(body, 96, "20260903120000000");
    ascii(body, 177, "0256");
    ascii(body, 181, "%06d".formatted(dataLength));
    ascii(body, 187, "000000");
    ascii(body, 193, "000000");
    ascii(body, 199, "%09d".formatted(totalLength));
    return body;
  }

  private static void ascii(byte[] target, int offset, String value) {
    byte[] source = value.getBytes(StandardCharsets.US_ASCII);
    System.arraycopy(source, 0, target, offset, source.length);
  }

  static EmbeddedActiveMQ start(Path root) throws Exception {
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
