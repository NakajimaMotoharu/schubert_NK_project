package dev.codex.schubert.nk.web.messaging;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

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
import org.apache.activemq.artemis.core.config.Configuration;
import org.apache.activemq.artemis.core.deployers.impl.FileConfigurationParser;
import org.apache.activemq.artemis.core.server.embedded.EmbeddedActiveMQ;
import org.apache.activemq.artemis.jms.client.ActiveMQConnectionFactory;
import org.apache.activemq.artemis.jms.client.ActiveMQQueue;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** PT-JMS-006/007/008/009 reply consumer transaction, late and fatal isolation matrix. */
final class ArtemisReplyConsumerTest {
  private static final String FIXTURE_NOT_A_UUID_C87A7FE1 = "not-a-uuid";
  private static final String FIXTURE_NKMESSAGEID_1B669E52 = "NKMessageID";
  private static final String FIXTURE_NKLAYOUTID_EB6996DB = "NKLayoutID";
  private static final String FIXTURE_UNAVAILABLE_30F591F0 = "UNAVAILABLE";
  private static final String FIXTURE_NKDELIVERYCOUNT_6AE5C7CF = "NKDeliveryCount";
  private static final String FIXTURE_ID_1_9FB5E8A2 = "ID:1";
  private static final String FIXTURE_LOGRSP01_BEEB0A2B = "LOGRSP01";
  private static final String FIXTURE_001_A3FEAA64 = "001";
  private static final UUID REQUEST_ID = UUID.fromString("00000000-0000-0000-0000-000000000001");
  private static final UUID RESPONSE_ID = UUID.fromString("00000000-0000-0000-0000-000000000002");
  private static final Instant NOW = Instant.parse("2026-09-03T00:00:00Z");

  @Test
  @DisplayName("PT-JMS-007/008 valid active and late replies commit exactly once")
  void validActiveAndLateRepliesAreCommittedAfterValidation(@TempDir Path root) throws Exception {
    EmbeddedActiveMQ broker = start(root);
    try (ActiveMQConnectionFactory factory = new ActiveMQConnectionFactory("vm://0");
        JMSContext producer = factory.createContext(JMSContext.AUTO_ACKNOWLEDGE);
        JMSContext receiver = factory.createContext(JMSContext.SESSION_TRANSACTED);
        JMSConsumer replyQueue = receiver.createConsumer(queue(BrokerTopology.SYNC_REPLY_WEB))) {
      ReplyCorrelationRegistry registry = new ReplyCorrelationRegistry();
      PendingReply pending = registry.register(REQUEST_ID, NOW.plusSeconds(2), NOW).orElseThrow();
      ArtemisReplyConsumer consumer = consumer(registry);
      byte[] body = responseWire();

      sendReply(producer, body);
      assertTrue(consumer.onMessage(receiver, required(replyQueue.receive(5_000))));
      assertArrayEquals(body, pending.completion().toCompletableFuture().join());
      assertEquals(0, registry.pendingCount());

      sendReply(producer, body);
      assertFalse(consumer.onMessage(receiver, required(replyQueue.receive(5_000))));
      assertEquals(1L, registry.lateResponseCount());
      assertNull(replyQueue.receive(250));
    } finally {
      broker.stop();
    }
  }

  @Test
  @DisplayName("PT-JMS-006/009 invalid reply type is atomically ACKed into sanitized DLQ")
  void invalidReplyIsPreservedSanitizedCommittedAndSignalledFatal(@TempDir Path root)
      throws Exception {
    EmbeddedActiveMQ broker = start(root);
    try (ActiveMQConnectionFactory factory = new ActiveMQConnectionFactory("vm://0");
        JMSContext producer = factory.createContext(JMSContext.AUTO_ACKNOWLEDGE);
        JMSContext receiver = factory.createContext(JMSContext.SESSION_TRANSACTED);
        JMSContext observer = factory.createContext(JMSContext.AUTO_ACKNOWLEDGE);
        JMSConsumer replyQueue = receiver.createConsumer(queue(BrokerTopology.SYNC_REPLY_WEB));
        JMSConsumer dlqQueue = observer.createConsumer(queue(BrokerTopology.DEAD_LETTER))) {
      TextMessage invalid = producer.createTextMessage("opaque synthetic invalid body");
      invalid.setJMSCorrelationID(FIXTURE_NOT_A_UUID_C87A7FE1);
      invalid.setStringProperty(FIXTURE_NKMESSAGEID_1B669E52, FIXTURE_NOT_A_UUID_C87A7FE1);
      invalid.setStringProperty(FIXTURE_NKLAYOUTID_EB6996DB, "bad");
      invalid.setStringProperty("NKProtocolVersion", "999");
      invalid.setStringProperty("UnapprovedSecret", "must-not-be-copied");
      producer
          .createProducer()
          .setDeliveryMode(DeliveryMode.PERSISTENT)
          .setTimeToLive(10_000)
          .send(queue(BrokerTopology.SYNC_REPLY_WEB), invalid);

      ArtemisReplyConsumer consumer = consumer(new ReplyCorrelationRegistry());
      CommittedFatalReplyException failure =
          assertThrows(
              CommittedFatalReplyException.class,
              () -> consumer.onMessage(receiver, required(replyQueue.receive(5_000))));
      assertNotNull(failure.getCause());
      assertEquals("invalid JMS reply was committed to the fatal DLQ", failure.getMessage());
      assertNull(replyQueue.receive(250));

      TextMessage isolated = assertInstanceOf(TextMessage.class, dlqQueue.receive(5_000));
      assertEquals("opaque synthetic invalid body", isolated.getText());
      assertEquals(FIXTURE_UNAVAILABLE_30F591F0, isolated.getJMSCorrelationID());
      assertEquals(
          FIXTURE_UNAVAILABLE_30F591F0, isolated.getStringProperty(FIXTURE_NKMESSAGEID_1B669E52));
      assertEquals(FIXTURE_UNAVAILABLE_30F591F0, isolated.getStringProperty("NKCorrelationID"));
      assertEquals(
          FIXTURE_UNAVAILABLE_30F591F0, isolated.getStringProperty(FIXTURE_NKLAYOUTID_EB6996DB));
      assertEquals("PROTOCOL_INVALID", isolated.getStringProperty("NKErrorCode"));
      assertEquals("WEB_REPLY", isolated.getStringProperty("NKDetectedBy"));
      assertEquals(NOW.toString(), isolated.getStringProperty("NKDetectedAt"));
      assertEquals("nk.sync.reply.web", isolated.getStringProperty("_AMQ_ORIG_ADDRESS"));
      assertEquals("nk.sync.reply.web.q", isolated.getStringProperty("_AMQ_ORIG_QUEUE"));
      assertEquals(1, isolated.getIntProperty(FIXTURE_NKDELIVERYCOUNT_6AE5C7CF));
      assertFalse(isolated.propertyExists("UnapprovedSecret"));
      assertEquals(DeliveryMode.PERSISTENT, isolated.getJMSDeliveryMode());
      assertEquals(0L, isolated.getJMSExpiration());
    } finally {
      broker.stop();
    }
  }

  @Test
  void constructorAndConsumerBoundaryDenyNullAndNonTransactedContext() {
    JmsRequestReplyClient client =
        new JmsRequestReplyClient(
            new ReplyCorrelationRegistry(), Clock.fixed(NOW, ZoneOffset.UTC), 1);
    JmsReplyDecoder decoder = new JmsReplyDecoder();
    ArtemisReplyDlqSender sender = new ArtemisReplyDlqSender(Clock.fixed(NOW, ZoneOffset.UTC));
    assertThrows(NullPointerException.class, () -> new ArtemisReplyConsumer(null, decoder, sender));
    assertThrows(NullPointerException.class, () -> new ArtemisReplyConsumer(client, null, sender));
    assertThrows(NullPointerException.class, () -> new ArtemisReplyConsumer(client, decoder, null));
    assertThrows(NullPointerException.class, () -> new ArtemisReplyDlqSender(null));

    ArtemisReplyConsumer consumer = new ArtemisReplyConsumer(client, decoder, sender);
    Message text = textMessage("getJMSMessageID", FIXTURE_ID_1_9FB5E8A2);
    assertThrows(NullPointerException.class, () -> consumer.onMessage(null, text));
    assertThrows(
        NullPointerException.class,
        () -> consumer.onMessage(context(JMSContext.SESSION_TRANSACTED), null));
    assertThrows(
        IllegalStateException.class,
        () -> consumer.onMessage(context(JMSContext.AUTO_ACKNOWLEDGE), text));
    assertThrows(NullPointerException.class, () -> sender.send(null, text));
    assertThrows(
        NullPointerException.class,
        () -> sender.send(context(JMSContext.SESSION_TRANSACTED), null));
    assertThrows(
        IllegalStateException.class, () -> sender.send(context(JMSContext.AUTO_ACKNOWLEDGE), text));
  }

  @Test
  void dlqMetadataUsesOnlyBoundedIdentifiersAndSafeDeliveryCount() throws Exception {
    ArtemisReplyDlqSender sender = new ArtemisReplyDlqSender(Clock.fixed(NOW, ZoneOffset.UTC));
    ContextState context = new ContextState();

    MessageState valid =
        messageState(
            "ID:provider-1",
            RESPONSE_ID.toString(),
            REQUEST_ID.toString(),
            FIXTURE_LOGRSP01_BEEB0A2B,
            2);
    sender.send(context.proxy(), valid.message);
    assertEquals("ID:provider-1", valid.strings.get("NKOriginalTransportID"));
    assertEquals(RESPONSE_ID.toString(), valid.strings.get(FIXTURE_NKMESSAGEID_1B669E52));
    assertEquals(REQUEST_ID.toString(), valid.strings.get("NKCorrelationID"));
    assertEquals(FIXTURE_LOGRSP01_BEEB0A2B, valid.strings.get(FIXTURE_NKLAYOUTID_EB6996DB));
    assertEquals(2, valid.integers.get(FIXTURE_NKDELIVERYCOUNT_6AE5C7CF));
    assertEquals(DeliveryMode.PERSISTENT, context.deliveryMode);
    assertEquals(0L, context.timeToLive);
    assertEquals(
        BrokerTopology.DEAD_LETTER.fullyQualifiedQueue(),
        ((ActiveMQQueue) context.destination).getAddress());
    assertEquals(valid.message, context.message);

    assertSanitizedTransport(sender, context, null);
    assertSanitizedTransport(sender, context, " ");
    assertSanitizedTransport(sender, context, "A".repeat(129));
    assertSanitizedTransport(sender, context, "ID:\u001f");
    assertSanitizedTransport(sender, context, "ID:\u007f");

    MessageState uppercase =
        messageState(
            FIXTURE_ID_1_9FB5E8A2,
            "AAAAAAAA-AAAA-AAAA-AAAA-AAAAAAAAAAAA",
            REQUEST_ID.toString(),
            FIXTURE_LOGRSP01_BEEB0A2B,
            1);
    sender.send(context.proxy(), uppercase.message);
    assertEquals(FIXTURE_UNAVAILABLE_30F591F0, uppercase.strings.get(FIXTURE_NKMESSAGEID_1B669E52));

    MessageState malformed =
        messageState(
            FIXTURE_ID_1_9FB5E8A2,
            FIXTURE_NOT_A_UUID_C87A7FE1,
            FIXTURE_NOT_A_UUID_C87A7FE1,
            "bad",
            null);
    sender.send(context.proxy(), malformed.message);
    assertEquals(FIXTURE_UNAVAILABLE_30F591F0, malformed.strings.get(FIXTURE_NKMESSAGEID_1B669E52));
    assertEquals(FIXTURE_UNAVAILABLE_30F591F0, malformed.strings.get("NKCorrelationID"));
    assertEquals(FIXTURE_UNAVAILABLE_30F591F0, malformed.strings.get(FIXTURE_NKLAYOUTID_EB6996DB));
    assertEquals(1, malformed.integers.get(FIXTURE_NKDELIVERYCOUNT_6AE5C7CF));

    MessageState zero =
        messageState(
            FIXTURE_ID_1_9FB5E8A2,
            RESPONSE_ID.toString(),
            REQUEST_ID.toString(),
            FIXTURE_LOGRSP01_BEEB0A2B,
            0);
    sender.send(context.proxy(), zero.message);
    assertEquals(1, zero.integers.get(FIXTURE_NKDELIVERYCOUNT_6AE5C7CF));
  }

  @Test
  void temporaryReadCommitAndRollbackFailuresPreservePrimaryFailure() throws Exception {
    ArtemisReplyConsumer consumer = consumer(new ReplyCorrelationRegistry());

    ContextState checkedContext = new ContextState();
    JMSException checked = new JMSException("synthetic-read-failure");
    assertEquals(
        checked,
        assertThrows(
            JMSException.class,
            () -> consumer.onMessage(checkedContext.proxy(), failingBytes(checked))));
    assertEquals(1, checkedContext.rollbacks);
    assertEquals(0, checkedContext.commits);

    ContextState runtimeContext = new ContextState();
    IllegalStateException runtime = new IllegalStateException("synthetic-read-runtime");
    assertEquals(
        runtime,
        assertThrows(
            IllegalStateException.class,
            () -> consumer.onMessage(runtimeContext.proxy(), failingBytes(runtime))));
    assertEquals(1, runtimeContext.rollbacks);

    ContextState commitContext = new ContextState();
    JMSRuntimeException commitFailure = new JMSRuntimeException("synthetic-commit-failure");
    commitContext.commitFailure = commitFailure;
    assertEquals(
        commitFailure,
        assertThrows(
            JMSRuntimeException.class,
            () -> consumer.onMessage(commitContext.proxy(), validReplyBytes())));
    assertEquals(1, commitContext.commits);
    assertEquals(1, commitContext.rollbacks);

    ContextState rollbackContext = new ContextState();
    JMSRuntimeException rollbackFailure = new JMSRuntimeException("synthetic-rollback-failure");
    rollbackContext.rollbackFailure = rollbackFailure;
    JMSException primary = new JMSException("synthetic-primary-failure");
    var unconfirmed =
        assertThrows(
            dev.codex.schubert.nk.protocol.transport.UnconfirmedJmsRollbackException.class,
            () -> consumer.onMessage(rollbackContext.proxy(), failingBytes(primary)));
    Throwable observed = unconfirmed.getCause();
    assertEquals(primary, observed);
    assertArrayEquals(new Throwable[] {rollbackFailure}, observed.getSuppressed());
    assertArrayEquals(new Throwable[] {rollbackFailure}, unconfirmed.getSuppressed());
  }

  @Test
  void jms021SameProviderFailureOnCommitAndRollbackPreservesPrimaryIdentity() throws Exception {
    ArtemisReplyConsumer consumer = consumer(new ReplyCorrelationRegistry());
    ContextState context = new ContextState();
    JMSRuntimeException primary = new JMSRuntimeException("synthetic-shared-provider-failure");
    context.commitFailure = primary;
    context.rollbackFailure = primary;
    var unconfirmed =
        assertThrows(
            dev.codex.schubert.nk.protocol.transport.UnconfirmedJmsRollbackException.class,
            () -> consumer.onMessage(context.proxy(), validReplyBytes()));
    assertSame(primary, unconfirmed.getCause());
    assertEquals(0, unconfirmed.getSuppressed().length);
    assertEquals(1, context.commits);
    assertEquals(1, context.rollbacks);
    assertEquals(0, primary.getSuppressed().length);
  }

  @Test
  void fatalIsolationFailureRollsBackAndRetainsProtocolClassification() throws Exception {
    ArtemisReplyConsumer consumer = consumer(new ReplyCorrelationRegistry());

    MessageState checkedMessage =
        messageState(
            FIXTURE_ID_1_9FB5E8A2,
            RESPONSE_ID.toString(),
            REQUEST_ID.toString(),
            FIXTURE_LOGRSP01_BEEB0A2B,
            1);
    JMSException checked = new JMSException("synthetic-DLQ-read-failure");
    checkedMessage.transportReadFailure = checked;
    ContextState checkedContext = new ContextState();
    Throwable checkedObserved =
        assertThrows(
                dev.codex.schubert.nk.protocol.transport.FailedJmsIsolationException.class,
                () -> consumer.onMessage(checkedContext.proxy(), checkedMessage.message))
            .getCause();
    assertEquals(checked, checkedObserved);
    assertEquals(1, checkedContext.rollbacks);
    assertTrue(
        Arrays.stream(checkedObserved.getSuppressed())
            .anyMatch(
                dev.codex.schubert.nk.protocol.codec.PermanentProtocolException.class::isInstance));

    MessageState commitMessage =
        messageState(
            FIXTURE_ID_1_9FB5E8A2,
            RESPONSE_ID.toString(),
            REQUEST_ID.toString(),
            FIXTURE_LOGRSP01_BEEB0A2B,
            1);
    ContextState commitContext = new ContextState();
    JMSRuntimeException runtime = new JMSRuntimeException("synthetic-DLQ-commit-failure");
    commitContext.commitFailure = runtime;
    Throwable runtimeObserved =
        assertThrows(
                dev.codex.schubert.nk.protocol.transport.FailedJmsIsolationException.class,
                () -> consumer.onMessage(commitContext.proxy(), commitMessage.message))
            .getCause();
    assertEquals(runtime, runtimeObserved);
    assertEquals(1, commitContext.rollbacks);
    assertTrue(
        Arrays.stream(runtimeObserved.getSuppressed())
            .anyMatch(
                dev.codex.schubert.nk.protocol.codec.PermanentProtocolException.class::isInstance));

    // SS322§11 / ISO: keep the isolation phase even when its rollback is also unknown.
    MessageState unknownMessage =
        messageState(
            FIXTURE_ID_1_9FB5E8A2,
            RESPONSE_ID.toString(),
            REQUEST_ID.toString(),
            FIXTURE_LOGRSP01_BEEB0A2B,
            1);
    JMSException unknownIsolation = new JMSException("synthetic-DLQ-unknown-read");
    unknownMessage.transportReadFailure = unknownIsolation;
    ContextState unknownContext = new ContextState();
    JMSRuntimeException rollback = new JMSRuntimeException("synthetic-DLQ-unknown-rollback");
    unknownContext.rollbackFailure = rollback;
    var phase =
        assertThrows(
            dev.codex.schubert.nk.protocol.transport.FailedJmsIsolationException.class,
            () -> consumer.onMessage(unknownContext.proxy(), unknownMessage.message));
    var unknown =
        assertInstanceOf(
            dev.codex.schubert.nk.protocol.transport.UnconfirmedJmsRollbackException.class,
            phase.getCause());
    assertSame(unknownIsolation, unknown.getCause());
    assertArrayEquals(new Throwable[] {rollback}, unknown.getSuppressed());
    assertInstanceOf(
        dev.codex.schubert.nk.protocol.codec.PermanentProtocolException.class,
        phase.getSuppressed()[0]);
    assertEquals(1, unknownContext.rollbacks);
    assertEquals(0, unknownContext.commits);
  }

  private static ArtemisReplyConsumer consumer(ReplyCorrelationRegistry registry) {
    Clock clock = Clock.fixed(NOW, ZoneOffset.UTC);
    return new ArtemisReplyConsumer(
        new JmsRequestReplyClient(registry, clock, 1),
        new JmsReplyDecoder(),
        new ArtemisReplyDlqSender(clock));
  }

  private static Message required(Message message) {
    assertNotNull(message);
    return message;
  }

  private static void assertSanitizedTransport(
      ArtemisReplyDlqSender sender, ContextState context, String transportId) throws Exception {
    MessageState state =
        messageState(
            transportId,
            RESPONSE_ID.toString(),
            REQUEST_ID.toString(),
            FIXTURE_LOGRSP01_BEEB0A2B,
            1);
    sender.send(context.proxy(), state.message);
    assertEquals(FIXTURE_UNAVAILABLE_30F591F0, state.strings.get("NKOriginalTransportID"));
  }

  private static Queue queue(BrokerTopology destination) {
    return new ActiveMQQueue(destination.fullyQualifiedQueue());
  }

  private static void sendReply(JMSContext context, byte[] body) throws Exception {
    BytesMessage reply = context.createBytesMessage();
    reply.writeBytes(body);
    reply.setJMSCorrelationID(REQUEST_ID.toString());
    reply.setStringProperty(FIXTURE_NKMESSAGEID_1B669E52, RESPONSE_ID.toString());
    reply.setStringProperty(FIXTURE_NKLAYOUTID_EB6996DB, FIXTURE_LOGRSP01_BEEB0A2B);
    reply.setStringProperty("NKProtocolVersion", FIXTURE_001_A3FEAA64);
    context
        .createProducer()
        .setDeliveryMode(DeliveryMode.PERSISTENT)
        .setTimeToLive(10_000)
        .send(queue(BrokerTopology.SYNC_REPLY_WEB), reply);
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
              if (method.getName().equals("toString")) {
                return "SyntheticJmsContext";
              }
              if (method.getName().equals("hashCode")) {
                return System.identityHashCode(proxy);
              }
              if (method.getName().equals("equals")) {
                return proxy == arguments[0];
              }
              throw new UnsupportedOperationException(method.getName());
            });
  }

  private static TextMessage textMessage(String supportedMethod, Object result) {
    return (TextMessage)
        Proxy.newProxyInstance(
            TextMessage.class.getClassLoader(),
            new Class<?>[] {TextMessage.class},
            (proxy, method, arguments) -> {
              if (method.getName().equals(supportedMethod)) {
                return result;
              }
              if (method.getName().equals("toString")) {
                return "SyntheticTextMessage";
              }
              if (method.getName().equals("hashCode")) {
                return System.identityHashCode(proxy);
              }
              if (method.getName().equals("equals")) {
                return proxy == arguments[0];
              }
              throw new UnsupportedOperationException(method.getName());
            });
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

  private static BytesMessage validReplyBytes() {
    byte[] body = responseWire();
    return (BytesMessage)
        Proxy.newProxyInstance(
            BytesMessage.class.getClassLoader(),
            new Class<?>[] {BytesMessage.class},
            (proxy, method, arguments) ->
                switch (method.getName()) {
                  case "getBodyLength" -> (long) body.length;
                  case "getBody" -> body.clone();
                  case "getJMSDestination" -> new ActiveMQQueue("nk.sync.reply.web");
                  case "getJMSReplyTo" -> null;
                  case "getJMSMessageID" -> "ID:synthetic";
                  case "getJMSCorrelationID" -> REQUEST_ID.toString();
                  case "getJMSExpiration" -> 1_000L;
                  case "getJMSDeliveryMode" -> DeliveryMode.PERSISTENT;
                  case "propertyExists" -> true;
                  case "getIntProperty" -> 1;
                  case "getStringProperty" ->
                      switch ((String) arguments[0]) {
                        case FIXTURE_NKMESSAGEID_1B669E52 -> RESPONSE_ID.toString();
                        case FIXTURE_NKLAYOUTID_EB6996DB -> FIXTURE_LOGRSP01_BEEB0A2B;
                        case "NKProtocolVersion" -> FIXTURE_001_A3FEAA64;
                        default -> throw new UnsupportedOperationException((String) arguments[0]);
                      };
                  default -> objectMethod(proxy, method.getName(), arguments);
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

  private static byte[] responseWire() {
    byte[] body = new byte[280];
    Arrays.fill(body, (byte) ' ');
    ascii(body, 0, "SCHBNK01");
    ascii(body, 8, FIXTURE_001_A3FEAA64);
    ascii(body, 11, FIXTURE_LOGRSP01_BEEB0A2B);
    ascii(body, 19, FIXTURE_001_A3FEAA64);
    body[22] = 'S';
    body[23] = 'S';
    ascii(body, 24, RESPONSE_ID.toString());
    ascii(body, 60, REQUEST_ID.toString());
    ascii(body, 96, "20260903120000000");
    ascii(body, 113, "a".repeat(64));
    ascii(body, 177, "0256");
    ascii(body, 181, "000024");
    ascii(body, 187, "000000");
    ascii(body, 193, "000000");
    ascii(body, 199, "000000280");
    ascii(body, 208, "0000");
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
        .addAcceptorConfiguration("component", "vm://0");
    return new EmbeddedActiveMQ().setConfiguration(configuration).start();
  }
}
