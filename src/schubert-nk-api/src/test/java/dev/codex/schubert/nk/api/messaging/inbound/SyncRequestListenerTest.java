package dev.codex.schubert.nk.api.messaging.inbound;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.api.messaging.outbound.DlqSender;
import dev.codex.schubert.nk.api.messaging.outbound.FatalDlqMetadata;
import dev.codex.schubert.nk.protocol.header.InteractionKind;
import dev.codex.schubert.nk.protocol.header.MessageKind;
import dev.codex.schubert.nk.protocol.transport.BrokerTopology;
import jakarta.jms.BytesMessage;
import jakarta.jms.DeliveryMode;
import jakarta.jms.Destination;
import jakarta.jms.JMSConsumer;
import jakarta.jms.JMSContext;
import jakarta.jms.JMSException;
import jakarta.jms.JMSProducer;
import jakarta.jms.JMSRuntimeException;
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
import java.util.Arrays;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicInteger;
import org.apache.activemq.artemis.core.config.Configuration;
import org.apache.activemq.artemis.core.deployers.impl.FileConfigurationParser;
import org.apache.activemq.artemis.core.server.embedded.EmbeddedActiveMQ;
import org.apache.activemq.artemis.jms.client.ActiveMQConnectionFactory;
import org.apache.activemq.artemis.jms.client.ActiveMQQueue;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** PT-JMS-005/006/007/009 synchronous API listener transaction matrix. */
final class SyncRequestListenerTest {
  private static final String FIXTURE_VM_0_0C76084A = "vm://0";
  private static final String FIXTURE_QSBREQ01_F9A27626 = "QSBREQ01";
  private static final String FIXTURE_NKLAYOUTID_EB6996DB = "NKLayoutID";
  private static final String FIXTURE_NKMESSAGEID_1B669E52 = "NKMessageID";
  private static final String FIXTURE_LOGREQ01_A98AF5F3 = "LOGREQ01";
  private static final String FIXTURE_001_A3FEAA64 = "001";
  private static final String FIXTURE_UNAVAILABLE_30F591F0 = "UNAVAILABLE";
  private static final String FIXTURE_NKDELIVERYCOUNT_6AE5C7CF = "NKDeliveryCount";
  private static final String FIXTURE_ID_1_9FB5E8A2 = "ID:1";
  private static final UUID REQUEST_ID = UUID.fromString("00000000-0000-0000-0000-000000000001");
  private static final UUID RESPONSE_ID = UUID.fromString("00000000-0000-0000-0000-000000000002");
  private static final Instant NOW = Instant.parse("2026-09-03T00:00:00Z");
  private static final Clock CLOCK = Clock.fixed(NOW, ZoneOffset.UTC);

  @Test
  @DisplayName("PT-JMS-QSB-A-API: independent Q/A and S/A golden bytes on actual sync queues")
  void questionAcceptanceUsesExistingPhysicalSyncQueues(@TempDir Path root) throws Exception {
    var broker = start(root);
    try (var factory = new ActiveMQConnectionFactory(FIXTURE_VM_0_0C76084A);
        var producer = factory.createContext(JMSContext.AUTO_ACKNOWLEDGE);
        var receiving = factory.createContext(JMSContext.SESSION_TRANSACTED);
        var observing = factory.createContext(JMSContext.AUTO_ACKNOWLEDGE);
        var requests = receiving.createConsumer(queue(BrokerTopology.SYNC_REQUEST));
        var replies = observing.createConsumer(queue(BrokerTopology.SYNC_REPLY_WEB));
        var dlq = observing.createConsumer(queue(BrokerTopology.DEAD_LETTER))) {
      byte[] input = wire('Q', FIXTURE_QSBREQ01_F9A27626, REQUEST_ID, REQUEST_ID, 4144, false);
      input[23] = 'A';
      ascii(input, 256, "independent question");
      ascii(input, 4352, "00000000-0000-0000-0000-000000000004");
      byte[] expected = wire('S', "QSBRSP01", RESPONSE_ID, REQUEST_ID, 64, true);
      expected[23] = 'A';
      ascii(expected, 256, "0".repeat(26));
      ascii(expected, 282, "000000000001");
      ascii(expected, 294, "20260903120000000");
      var calls = new AtomicInteger();
      var listener =
          new SyncRequestListener(
              request -> {
                calls.incrementAndGet();
                assertEquals(FIXTURE_QSBREQ01_F9A27626, request.header().layoutId().value());
                assertEquals(InteractionKind.ASYNC_ACCEPTANCE, request.header().interactionKind());
                assertArrayEquals(
                    Arrays.copyOfRange(input, 256, 4400), request.payload().copyData());
                return expected;
              },
              CLOCK);
      sendRequest(producer, input, FIXTURE_QSBREQ01_F9A27626);
      listener.onMessage(receiving, required(requests.receive(5000)));
      var reply = assertInstanceOf(BytesMessage.class, replies.receive(5000));
      assertArrayEquals(expected, body(reply));
      assertEquals("QSBRSP01", reply.getStringProperty(FIXTURE_NKLAYOUTID_EB6996DB));
      assertEquals(RESPONSE_ID.toString(), reply.getStringProperty(FIXTURE_NKMESSAGEID_1B669E52));
      assertEquals(REQUEST_ID.toString(), reply.getJMSCorrelationID());
      assertEquals(DeliveryMode.PERSISTENT, reply.getJMSDeliveryMode());
      assertTrue(reply.getJMSExpiration() > System.currentTimeMillis());
      assertNull(requests.receive(100));
      assertEquals(1, calls.get());
      for (char wrong : new char[] {'S', 'I'}) {
        byte[] invalid = input.clone();
        invalid[23] = (byte) wrong;
        sendRequest(producer, invalid, FIXTURE_QSBREQ01_F9A27626);
        assertThrows(
            CommittedFatalInboundException.class,
            () -> listener.onMessage(receiving, required(requests.receive(5000))));
        assertNotNull(dlq.receive(5000));
      }
      sendRequest(producer, input, FIXTURE_LOGREQ01_A98AF5F3);
      assertThrows(
          CommittedFatalInboundException.class,
          () -> listener.onMessage(receiving, required(requests.receive(5000))));
      assertNotNull(dlq.receive(5000));
      byte[] wrongA = requestWire();
      wrongA[23] = 'A';
      sendRequest(producer, wrongA);
      assertThrows(
          CommittedFatalInboundException.class,
          () -> listener.onMessage(receiving, required(requests.receive(5000))));
      assertNotNull(dlq.receive(5000));
      assertEquals(1, calls.get());
      assertNull(replies.receive(100));
    } finally {
      broker.stop();
    }
  }

  @Test
  @DisplayName("PT-JMS-005/007 request ACK and reply become visible in one caller commit")
  void validRequestDispatchesAndCommitsReplyWithOriginalAck(@TempDir Path root) throws Exception {
    EmbeddedActiveMQ broker = start(root);
    try (ActiveMQConnectionFactory factory = new ActiveMQConnectionFactory(FIXTURE_VM_0_0C76084A);
        JMSContext producer = factory.createContext(JMSContext.AUTO_ACKNOWLEDGE);
        JMSContext listenerContext = factory.createContext(JMSContext.SESSION_TRANSACTED);
        JMSContext observer = factory.createContext(JMSContext.AUTO_ACKNOWLEDGE);
        JMSConsumer requests = listenerContext.createConsumer(queue(BrokerTopology.SYNC_REQUEST));
        JMSConsumer replies = observer.createConsumer(queue(BrokerTopology.SYNC_REPLY_WEB))) {
      byte[] requestBody = requestWire();
      byte[] responseBody = responseWire();
      AtomicInteger dispatches = new AtomicInteger();
      SyncRequestListener listener =
          new SyncRequestListener(
              request -> {
                dispatches.incrementAndGet();
                assertEquals(FIXTURE_LOGREQ01_A98AF5F3, request.header().layoutId().value());
                assertEquals(MessageKind.REQUEST, request.header().messageKind());
                assertEquals(InteractionKind.SYNCHRONOUS, request.header().interactionKind());
                assertEquals(0, request.payload().dataLength());
                return responseBody;
              },
              CLOCK);

      sendRequest(producer, requestBody);
      listener.onMessage(listenerContext, required(requests.receive(5_000)));

      assertEquals(1, dispatches.get());
      assertNull(requests.receive(250));
      BytesMessage reply = assertInstanceOf(BytesMessage.class, replies.receive(5_000));
      assertArrayEquals(responseBody, body(reply));
      assertEquals(REQUEST_ID.toString(), reply.getJMSCorrelationID());
      assertEquals(RESPONSE_ID.toString(), reply.getStringProperty(FIXTURE_NKMESSAGEID_1B669E52));
      assertEquals("LOGRSP01", reply.getStringProperty(FIXTURE_NKLAYOUTID_EB6996DB));
      assertEquals(FIXTURE_001_A3FEAA64, reply.getStringProperty("NKProtocolVersion"));
      assertEquals(DeliveryMode.PERSISTENT, reply.getJMSDeliveryMode());
    } finally {
      broker.stop();
    }
  }

  @Test
  @DisplayName("PT-JMS-007 temporary processor failure rolls back the request delivery")
  void processorFailureRollsBackAndRequestIsRedelivered(@TempDir Path root) throws Exception {
    EmbeddedActiveMQ broker = start(root);
    try (ActiveMQConnectionFactory factory = new ActiveMQConnectionFactory(FIXTURE_VM_0_0C76084A);
        JMSContext producer = factory.createContext(JMSContext.AUTO_ACKNOWLEDGE);
        JMSContext listenerContext = factory.createContext(JMSContext.SESSION_TRANSACTED);
        JMSConsumer requests = listenerContext.createConsumer(queue(BrokerTopology.SYNC_REQUEST))) {
      IllegalStateException failure = new IllegalStateException("synthetic temporary failure");
      SyncRequestListener listener =
          new SyncRequestListener(
              ignored -> {
                throw failure;
              },
              CLOCK);
      sendRequest(producer, requestWire());
      Message first = required(requests.receive(5_000));
      assertEquals(1, first.getIntProperty("JMSXDeliveryCount"));
      assertSame(
          failure,
          assertThrows(
              IllegalStateException.class, () -> listener.onMessage(listenerContext, first)));

      Message redelivered = required(requests.receive(3_000));
      assertEquals(2, redelivered.getIntProperty("JMSXDeliveryCount"));
      listenerContext.commit();
    } finally {
      broker.stop();
    }
  }

  @Test
  @DisplayName("PT-JMS-006/009 invalid request type is committed to DLQ before fatal signal")
  void invalidRequestIsSanitizedAckedAndCommittedToDlq(@TempDir Path root) throws Exception {
    EmbeddedActiveMQ broker = start(root);
    try (ActiveMQConnectionFactory factory = new ActiveMQConnectionFactory(FIXTURE_VM_0_0C76084A);
        JMSContext producer = factory.createContext(JMSContext.AUTO_ACKNOWLEDGE);
        JMSContext listenerContext = factory.createContext(JMSContext.SESSION_TRANSACTED);
        JMSContext observer = factory.createContext(JMSContext.AUTO_ACKNOWLEDGE);
        JMSConsumer requests = listenerContext.createConsumer(queue(BrokerTopology.SYNC_REQUEST));
        JMSConsumer dlq = observer.createConsumer(queue(BrokerTopology.DEAD_LETTER))) {
      TextMessage invalid = producer.createTextMessage("opaque synthetic invalid request");
      invalid.setJMSCorrelationID("invalid-correlation");
      invalid.setStringProperty(FIXTURE_NKMESSAGEID_1B669E52, "invalid-message");
      invalid.setStringProperty(FIXTURE_NKLAYOUTID_EB6996DB, "bad");
      invalid.setStringProperty("NKProtocolVersion", "999");
      invalid.setStringProperty("UnapprovedSecret", "must-not-be-copied");
      producer
          .createProducer()
          .setDeliveryMode(DeliveryMode.PERSISTENT)
          .setTimeToLive(5_000)
          .send(queue(BrokerTopology.SYNC_REQUEST), invalid);
      AtomicBoolean dispatched = new AtomicBoolean();
      SyncRequestListener listener =
          new SyncRequestListener(
              ignored -> {
                dispatched.set(true);
                return responseWire();
              },
              CLOCK);

      CommittedFatalInboundException failure =
          assertThrows(
              CommittedFatalInboundException.class,
              () -> listener.onMessage(listenerContext, required(requests.receive(5_000))));
      assertNotNull(failure.getCause());
      assertEquals(
          "invalid inbound JMS message was committed to the fatal DLQ", failure.getMessage());
      assertFalse(dispatched.get());
      assertNull(requests.receive(250));

      TextMessage isolated = assertInstanceOf(TextMessage.class, dlq.receive(5_000));
      assertEquals("opaque synthetic invalid request", isolated.getText());
      assertEquals(FIXTURE_UNAVAILABLE_30F591F0, isolated.getJMSCorrelationID());
      assertEquals(
          FIXTURE_UNAVAILABLE_30F591F0, isolated.getStringProperty(FIXTURE_NKMESSAGEID_1B669E52));
      assertEquals(FIXTURE_UNAVAILABLE_30F591F0, isolated.getStringProperty("NKCorrelationID"));
      assertEquals(
          FIXTURE_UNAVAILABLE_30F591F0, isolated.getStringProperty(FIXTURE_NKLAYOUTID_EB6996DB));
      assertEquals("nk.sync.request", isolated.getStringProperty("_AMQ_ORIG_ADDRESS"));
      assertEquals("nk.sync.request.q", isolated.getStringProperty("_AMQ_ORIG_QUEUE"));
      assertEquals("PROTOCOL_INVALID", isolated.getStringProperty("NKErrorCode"));
      assertEquals("API_SYNC", isolated.getStringProperty("NKDetectedBy"));
      assertEquals(NOW.toString(), isolated.getStringProperty("NKDetectedAt"));
      assertEquals(1, isolated.getIntProperty(FIXTURE_NKDELIVERYCOUNT_6AE5C7CF));
      assertFalse(isolated.propertyExists("UnapprovedSecret"));
    } finally {
      broker.stop();
    }
  }

  @Test
  void constructorAndListenerBoundaryDenyNullAndWrongSessionMode() {
    SyncRequestProcessor processor = ignored -> responseWire();
    assertThrows(NullPointerException.class, () -> new SyncRequestListener(null, CLOCK));
    assertThrows(NullPointerException.class, () -> new SyncRequestListener(processor, null));
    SyncRequestListener listener = new SyncRequestListener(processor, CLOCK);
    Message message = textMessage();
    assertThrows(NullPointerException.class, () -> listener.onMessage(null, message));
    assertThrows(
        NullPointerException.class,
        () -> listener.onMessage(context(JMSContext.SESSION_TRANSACTED), null));
    assertThrows(
        IllegalStateException.class,
        () -> listener.onMessage(context(JMSContext.AUTO_ACKNOWLEDGE), message));
  }

  @Test
  void rawDlqSenderAllowsOnlyApplicationSourceAndBoundedMetadata() throws Exception {
    DlqSender sender = new DlqSender();
    FatalDlqMetadata fatal =
        new FatalDlqMetadata("PROTOCOL_INVALID", FatalDlqMetadata.DetectedBy.API_SYNC, NOW);
    ContextState context = new ContextState();
    MessageState valid =
        messageState(
            "ID:provider-1",
            REQUEST_ID.toString(),
            REQUEST_ID.toString(),
            FIXTURE_LOGREQ01_A98AF5F3,
            2);

    sender.sendUntrusted(context.proxy(), valid.message, BrokerTopology.SYNC_REQUEST, fatal);
    assertEquals("ID:provider-1", valid.strings.get("NKOriginalTransportID"));
    assertEquals(REQUEST_ID.toString(), valid.strings.get(FIXTURE_NKMESSAGEID_1B669E52));
    assertEquals(REQUEST_ID.toString(), valid.strings.get("NKCorrelationID"));
    assertEquals(FIXTURE_LOGREQ01_A98AF5F3, valid.strings.get(FIXTURE_NKLAYOUTID_EB6996DB));
    assertEquals(2, valid.integers.get(FIXTURE_NKDELIVERYCOUNT_6AE5C7CF));
    assertEquals("API_SYNC", valid.strings.get("NKDetectedBy"));
    assertEquals(DeliveryMode.PERSISTENT, context.deliveryMode);
    assertEquals(0L, context.timeToLive);
    assertEquals(
        BrokerTopology.DEAD_LETTER.fullyQualifiedQueue(),
        ((ActiveMQQueue) context.destination).getAddress());
    assertSame(valid.message, context.message);

    assertThrows(
        NullPointerException.class,
        () -> sender.sendUntrusted(null, valid.message, BrokerTopology.SYNC_REQUEST, fatal));
    assertThrows(
        NullPointerException.class,
        () -> sender.sendUntrusted(context.proxy(), null, BrokerTopology.SYNC_REQUEST, fatal));
    assertThrows(
        NullPointerException.class,
        () -> sender.sendUntrusted(context.proxy(), valid.message, null, fatal));
    assertThrows(
        NullPointerException.class,
        () ->
            sender.sendUntrusted(
                context.proxy(), valid.message, BrokerTopology.SYNC_REQUEST, null));
    assertThrows(
        IllegalStateException.class,
        () ->
            sender.sendUntrusted(
                context(JMSContext.AUTO_ACKNOWLEDGE),
                valid.message,
                BrokerTopology.SYNC_REQUEST,
                fatal));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            sender.sendUntrusted(
                context.proxy(), valid.message, BrokerTopology.DEAD_LETTER, fatal));
    assertThrows(
        IllegalArgumentException.class,
        () -> sender.sendUntrusted(context.proxy(), valid.message, BrokerTopology.EXPIRY, fatal));

    assertSanitizedTransport(sender, context, fatal, null);
    assertSanitizedTransport(sender, context, fatal, " ");
    assertSanitizedTransport(sender, context, fatal, "A".repeat(129));
    assertSanitizedTransport(sender, context, fatal, "ID:\u001f");
    assertSanitizedTransport(sender, context, fatal, "ID:\u007f");

    MessageState uppercase =
        messageState(
            FIXTURE_ID_1_9FB5E8A2,
            "AAAAAAAA-AAAA-AAAA-AAAA-AAAAAAAAAAAA",
            REQUEST_ID.toString(),
            FIXTURE_LOGREQ01_A98AF5F3,
            1);
    sender.sendUntrusted(context.proxy(), uppercase.message, BrokerTopology.SYNC_REQUEST, fatal);
    assertEquals(FIXTURE_UNAVAILABLE_30F591F0, uppercase.strings.get(FIXTURE_NKMESSAGEID_1B669E52));

    MessageState malformed =
        messageState(FIXTURE_ID_1_9FB5E8A2, "not-a-uuid", "not-a-uuid", "bad", null);
    sender.sendUntrusted(context.proxy(), malformed.message, BrokerTopology.SYNC_REQUEST, fatal);
    assertEquals(FIXTURE_UNAVAILABLE_30F591F0, malformed.strings.get(FIXTURE_NKMESSAGEID_1B669E52));
    assertEquals(FIXTURE_UNAVAILABLE_30F591F0, malformed.strings.get("NKCorrelationID"));
    assertEquals(FIXTURE_UNAVAILABLE_30F591F0, malformed.strings.get(FIXTURE_NKLAYOUTID_EB6996DB));
    assertEquals(1, malformed.integers.get(FIXTURE_NKDELIVERYCOUNT_6AE5C7CF));

    MessageState zero =
        messageState(
            FIXTURE_ID_1_9FB5E8A2,
            REQUEST_ID.toString(),
            REQUEST_ID.toString(),
            FIXTURE_LOGREQ01_A98AF5F3,
            0);
    sender.sendUntrusted(context.proxy(), zero.message, BrokerTopology.SYNC_REQUEST, fatal);
    assertEquals(1, zero.integers.get(FIXTURE_NKDELIVERYCOUNT_6AE5C7CF));
  }

  @Test
  void readAndFatalIsolationFailuresRollbackAndRetainPrimaryCause() throws Exception {
    SyncRequestListener listener = new SyncRequestListener(ignored -> responseWire(), CLOCK);

    ContextState readContext = new ContextState();
    JMSException readFailure = new JMSException("synthetic-read-failure");
    assertSame(
        readFailure,
        assertThrows(
            JMSException.class,
            () -> listener.onMessage(readContext.proxy(), failingBytes(readFailure))));
    assertEquals(1, readContext.rollbacks);
    assertEquals(0, readContext.commits);

    // SS322§11 / PG-D442: even confirmed rollback cannot make failed permanent isolation retryable.
    // Original isolation identity remains the cause; unconfirmed rollback is retained separately.
    ContextState confirmedIsolationContext = new ContextState();
    MessageState confirmedMessage =
        messageState(
            FIXTURE_ID_1_9FB5E8A2,
            REQUEST_ID.toString(),
            REQUEST_ID.toString(),
            FIXTURE_LOGREQ01_A98AF5F3,
            1);
    JMSException confirmedIsolationFailure = new JMSException("synthetic-confirmed-DLQ-read");
    confirmedMessage.transportReadFailure = confirmedIsolationFailure;
    assertSame(
        confirmedIsolationFailure,
        assertThrows(
                dev.codex.schubert.nk.protocol.transport.FailedJmsIsolationException.class,
                () ->
                    listener.onMessage(confirmedIsolationContext.proxy(), confirmedMessage.message))
            .getCause());
    assertEquals(1, confirmedIsolationContext.rollbacks);
    assertEquals(0, confirmedIsolationContext.commits);
    assertEquals(1, confirmedIsolationFailure.getSuppressed().length);
    assertInstanceOf(
        dev.codex.schubert.nk.protocol.codec.PermanentProtocolException.class,
        confirmedIsolationFailure.getSuppressed()[0]);

    ContextState checkedIsolationContext = new ContextState();
    JMSRuntimeException rollbackFailure = new JMSRuntimeException("synthetic-rollback-failure");
    checkedIsolationContext.rollbackFailure = rollbackFailure;
    MessageState checkedMessage =
        messageState(
            FIXTURE_ID_1_9FB5E8A2,
            REQUEST_ID.toString(),
            REQUEST_ID.toString(),
            FIXTURE_LOGREQ01_A98AF5F3,
            1);
    JMSException isolationFailure = new JMSException("synthetic-DLQ-read-failure");
    checkedMessage.transportReadFailure = isolationFailure;
    var failedIsolation =
        assertThrows(
            dev.codex.schubert.nk.protocol.transport.FailedJmsIsolationException.class,
            () -> listener.onMessage(checkedIsolationContext.proxy(), checkedMessage.message));
    var unconfirmed =
        assertInstanceOf(
            dev.codex.schubert.nk.protocol.transport.UnconfirmedJmsRollbackException.class,
            failedIsolation.getCause());
    assertInstanceOf(
        dev.codex.schubert.nk.protocol.codec.PermanentProtocolException.class,
        failedIsolation.getSuppressed()[0]);
    Throwable checkedObserved = unconfirmed.getCause();
    assertSame(rollbackFailure, unconfirmed.getSuppressed()[0]);
    assertSame(isolationFailure, checkedObserved);
    assertEquals(1, checkedIsolationContext.rollbacks);
    assertTrue(
        Arrays.stream(checkedObserved.getSuppressed())
            .anyMatch(
                dev.codex.schubert.nk.protocol.codec.PermanentProtocolException.class::isInstance));
    assertTrue(Arrays.asList(checkedObserved.getSuppressed()).contains(rollbackFailure));

    ContextState commitIsolationContext = new ContextState();
    JMSRuntimeException commitFailure = new JMSRuntimeException("synthetic-DLQ-commit-failure");
    commitIsolationContext.commitFailure = commitFailure;
    MessageState commitMessage =
        messageState(
            FIXTURE_ID_1_9FB5E8A2,
            REQUEST_ID.toString(),
            REQUEST_ID.toString(),
            FIXTURE_LOGREQ01_A98AF5F3,
            1);
    Throwable runtimeObserved =
        assertThrows(
                dev.codex.schubert.nk.protocol.transport.FailedJmsIsolationException.class,
                () -> listener.onMessage(commitIsolationContext.proxy(), commitMessage.message))
            .getCause();
    assertSame(commitFailure, runtimeObserved);
    assertEquals(1, commitIsolationContext.rollbacks);
    assertTrue(
        Arrays.stream(runtimeObserved.getSuppressed())
            .anyMatch(
                dev.codex.schubert.nk.protocol.codec.PermanentProtocolException.class::isInstance));
  }

  private static Message required(Message message) {
    assertNotNull(message);
    return message;
  }

  private static void assertSanitizedTransport(
      DlqSender sender, ContextState context, FatalDlqMetadata fatal, String transportId)
      throws Exception {
    MessageState state =
        messageState(
            transportId,
            REQUEST_ID.toString(),
            REQUEST_ID.toString(),
            FIXTURE_LOGREQ01_A98AF5F3,
            1);
    sender.sendUntrusted(context.proxy(), state.message, BrokerTopology.SYNC_REQUEST, fatal);
    assertEquals(FIXTURE_UNAVAILABLE_30F591F0, state.strings.get("NKOriginalTransportID"));
  }

  private static byte[] body(BytesMessage message) throws Exception {
    byte[] body = new byte[Math.toIntExact(message.getBodyLength())];
    assertEquals(body.length, message.readBytes(body));
    return body;
  }

  private static Queue queue(BrokerTopology destination) {
    return new ActiveMQQueue(destination.fullyQualifiedQueue());
  }

  private static void sendRequest(JMSContext context, byte[] body) throws Exception {
    sendRequest(context, body, FIXTURE_LOGREQ01_A98AF5F3);
  }

  private static void sendRequest(JMSContext context, byte[] body, String layout) throws Exception {
    BytesMessage request = context.createBytesMessage();
    request.writeBytes(body);
    request.setJMSCorrelationID(REQUEST_ID.toString());
    request.setJMSReplyTo(new ActiveMQQueue(BrokerTopology.SYNC_REPLY_WEB.address()));
    request.setStringProperty(FIXTURE_NKMESSAGEID_1B669E52, REQUEST_ID.toString());
    request.setStringProperty(FIXTURE_NKLAYOUTID_EB6996DB, layout);
    request.setStringProperty("NKProtocolVersion", FIXTURE_001_A3FEAA64);
    context
        .createProducer()
        .setDeliveryMode(DeliveryMode.PERSISTENT)
        .setTimeToLive(5_000)
        .send(queue(BrokerTopology.SYNC_REQUEST), request);
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

  private static BytesMessage failingBytes(Throwable failure) {
    return (BytesMessage)
        Proxy.newProxyInstance(
            BytesMessage.class.getClassLoader(),
            new Class<?>[] {BytesMessage.class},
            (proxy, method, arguments) -> {
              if (method.getName().equals("getBodyLength")) {
                throw failure;
              }
              return objectMethod(proxy, method.getName(), arguments);
            });
  }

  private static MessageState messageState(
      String transportId,
      String messageId,
      String correlationId,
      String layoutId,
      Integer deliveryCount) {
    MessageState state = new MessageState();
    state.transportId = transportId;
    state.correlationId = correlationId;
    state.strings.put(FIXTURE_NKMESSAGEID_1B669E52, messageId);
    state.strings.put(FIXTURE_NKLAYOUTID_EB6996DB, layoutId);
    if (deliveryCount != null) {
      state.integers.put("JMSXDeliveryCount", deliveryCount);
    }
    return state;
  }

  private static Object objectMethod(Object proxy, String method, Object[] arguments) {
    return switch (method) {
      case "toString" -> "SyntheticJmsBoundary";
      case "hashCode" -> System.identityHashCode(proxy);
      case "equals" -> proxy == arguments[0];
      default -> throw new UnsupportedOperationException(method);
    };
  }

  private static final class MessageState {
    private final Map<String, String> strings = new HashMap<>();
    private final Map<String, Integer> integers = new HashMap<>();
    private final TextMessage message = proxy();
    private String transportId;
    private String correlationId;
    private Throwable transportReadFailure;

    private TextMessage proxy() {
      return (TextMessage)
          Proxy.newProxyInstance(
              TextMessage.class.getClassLoader(),
              new Class<?>[] {TextMessage.class},
              (proxy, method, arguments) -> {
                String name = method.getName();
                if (name.equals("getJMSMessageID")) {
                  if (transportReadFailure != null) {
                    throw transportReadFailure;
                  }
                  return transportId;
                }
                if (name.equals("getJMSCorrelationID")) {
                  return correlationId;
                }
                if (name.equals("getStringProperty")) {
                  return strings.get((String) arguments[0]);
                }
                if (name.equals("propertyExists")) {
                  String property = (String) arguments[0];
                  return strings.containsKey(property) || integers.containsKey(property);
                }
                if (name.equals("getIntProperty")) {
                  return integers.get((String) arguments[0]);
                }
                if (name.equals("clearProperties")) {
                  strings.clear();
                  integers.clear();
                  return null;
                }
                if (name.equals("setJMSCorrelationID")) {
                  correlationId = (String) arguments[0];
                  return null;
                }
                if (name.equals("setJMSReplyTo") || name.equals("setJMSType")) {
                  return null;
                }
                if (name.equals("setStringProperty")) {
                  strings.put((String) arguments[0], (String) arguments[1]);
                  return null;
                }
                if (name.equals("setIntProperty")) {
                  integers.put((String) arguments[0], (Integer) arguments[1]);
                  return null;
                }
                return objectMethod(proxy, name, arguments);
              });
    }
  }

  private static final class ContextState {
    private final JMSProducer producer = producer();
    private RuntimeException commitFailure;
    private RuntimeException rollbackFailure;
    private int commits;
    private int rollbacks;
    private int deliveryMode;
    private long timeToLive;
    private Destination destination;
    private Message message;

    private JMSContext proxy() {
      return (JMSContext)
          Proxy.newProxyInstance(
              JMSContext.class.getClassLoader(),
              new Class<?>[] {JMSContext.class},
              (proxy, method, arguments) -> {
                switch (method.getName()) {
                  case "getSessionMode" -> {
                    return JMSContext.SESSION_TRANSACTED;
                  }
                  case "createProducer" -> {
                    return producer;
                  }
                  case "commit" -> {
                    commits++;
                    if (commitFailure != null) {
                      throw commitFailure;
                    }
                    return null;
                  }
                  case "rollback" -> {
                    rollbacks++;
                    if (rollbackFailure != null) {
                      throw rollbackFailure;
                    }
                    return null;
                  }
                  default -> {
                    return objectMethod(proxy, method.getName(), arguments);
                  }
                }
              });
    }

    private JMSProducer producer() {
      return (JMSProducer)
          Proxy.newProxyInstance(
              JMSProducer.class.getClassLoader(),
              new Class<?>[] {JMSProducer.class},
              (proxy, method, arguments) -> {
                switch (method.getName()) {
                  case "setDeliveryMode" -> {
                    deliveryMode = (Integer) arguments[0];
                    return proxy;
                  }
                  case "setTimeToLive" -> {
                    timeToLive = (Long) arguments[0];
                    return proxy;
                  }
                  case "send" -> {
                    destination = (Destination) arguments[0];
                    message = (Message) arguments[1];
                    return null;
                  }
                  default -> {
                    return objectMethod(proxy, method.getName(), arguments);
                  }
                }
              });
    }
  }

  private static byte[] requestWire() {
    return wire('Q', FIXTURE_LOGREQ01_A98AF5F3, REQUEST_ID, REQUEST_ID, 0, false);
  }

  private static byte[] responseWire() {
    return wire('S', "LOGRSP01", RESPONSE_ID, REQUEST_ID, 24, true);
  }

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
    ascii(body, 8, FIXTURE_001_A3FEAA64);
    ascii(body, 11, layout);
    ascii(body, 19, FIXTURE_001_A3FEAA64);
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
