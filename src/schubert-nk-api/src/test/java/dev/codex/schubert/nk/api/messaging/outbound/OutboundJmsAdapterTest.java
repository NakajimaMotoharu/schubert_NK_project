package dev.codex.schubert.nk.api.messaging.outbound;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.api.messaging.guard.GuardedJmsMessage;
import dev.codex.schubert.nk.protocol.codec.PermanentProtocolException;
import dev.codex.schubert.nk.protocol.codec.TransportBodyType;
import dev.codex.schubert.nk.protocol.codec.TransportMetadata;
import dev.codex.schubert.nk.protocol.layout.LayoutId;
import dev.codex.schubert.nk.protocol.transport.BrokerTopology;
import jakarta.jms.BytesMessage;
import jakarta.jms.DeliveryMode;
import jakarta.jms.JMSConsumer;
import jakarta.jms.JMSContext;
import jakarta.jms.Queue;
import java.io.InputStream;
import java.lang.reflect.Proxy;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Instant;
import java.util.Arrays;
import java.util.Optional;
import java.util.UUID;
import org.apache.activemq.artemis.core.config.Configuration;
import org.apache.activemq.artemis.core.deployers.impl.FileConfigurationParser;
import org.apache.activemq.artemis.core.server.embedded.EmbeddedActiveMQ;
import org.apache.activemq.artemis.jms.client.ActiveMQConnectionFactory;
import org.apache.activemq.artemis.jms.client.ActiveMQQueue;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** PT-JMS-005/007/009 production Reply/DLQ adapters and listener-owned transaction. */
final class OutboundJmsAdapterTest {
  private static final String FIXTURE_001_A3FEAA64 = "001";
  private static final UUID REQUEST_ID = UUID.fromString("00000000-0000-0000-0000-000000000001");
  private static final UUID RESPONSE_ID = UUID.fromString("00000000-0000-0000-0000-000000000002");
  private static final Instant DETECTED_AT = Instant.parse("2026-09-03T00:00:00Z");

  @Test
  @DisplayName("PT-JMS-005/007/009 reply and DLQ remain invisible until caller commit")
  void actualBrokerPreservesReplyAndDlqPropertiesAcrossRollbackAndCommit(@TempDir Path root)
      throws Exception {
    byte[] replyBody = responseWire('S', "LOGRSP01", 24);
    byte[] rejectedBody = requestWire();
    EmbeddedActiveMQ broker = start(root);
    try (ActiveMQConnectionFactory connectionFactory = new ActiveMQConnectionFactory("vm://0");
        JMSContext transaction = connectionFactory.createContext(JMSContext.SESSION_TRANSACTED);
        JMSContext observer = connectionFactory.createContext(JMSContext.AUTO_ACKNOWLEDGE);
        JMSConsumer replyConsumer = observer.createConsumer(queue(BrokerTopology.SYNC_REPLY_WEB));
        JMSConsumer dlqConsumer = observer.createConsumer(queue(BrokerTopology.DEAD_LETTER))) {
      ReplySender replySender = new ReplySender();
      long beforeReply = System.currentTimeMillis();
      replySender.send(transaction, replyBody);
      assertNull(replyConsumer.receive(250));
      transaction.rollback();
      assertNull(replyConsumer.receive(250));

      replySender.send(transaction, replyBody);
      transaction.commit();
      BytesMessage reply = assertInstanceOf(BytesMessage.class, replyConsumer.receive(5_000));
      assertNotNull(reply);
      assertArrayEquals(replyBody, body(reply));
      assertEquals(REQUEST_ID.toString(), reply.getJMSCorrelationID());
      assertEquals(RESPONSE_ID.toString(), reply.getStringProperty("NKMessageID"));
      assertEquals("LOGRSP01", reply.getStringProperty("NKLayoutID"));
      assertEquals(FIXTURE_001_A3FEAA64, reply.getStringProperty("NKProtocolVersion"));
      assertNull(reply.getJMSReplyTo());
      assertEquals(DeliveryMode.PERSISTENT, reply.getJMSDeliveryMode());
      assertTrue(
          reply.getJMSExpiration()
              >= beforeReply + BrokerTopology.SYNC_REPLY_WEB.timeToLiveMillis() - 500);
      assertTrue(
          reply.getJMSExpiration()
              <= beforeReply + BrokerTopology.SYNC_REPLY_WEB.timeToLiveMillis() + 2_000);

      GuardedJmsMessage rejected = rejected(rejectedBody);
      FatalDlqMetadata fatal =
          new FatalDlqMetadata(
              "PROTOCOL_INVALID", FatalDlqMetadata.DetectedBy.API_SYNC, DETECTED_AT);
      DlqSender dlqSender = new DlqSender();
      dlqSender.send(transaction, rejected, fatal);
      assertNull(dlqConsumer.receive(250));
      transaction.rollback();
      assertNull(dlqConsumer.receive(250));

      dlqSender.send(transaction, rejected, fatal);
      transaction.commit();
      BytesMessage dlq = assertInstanceOf(BytesMessage.class, dlqConsumer.receive(5_000));
      assertArrayEquals(rejectedBody, body(dlq));
      assertEquals(REQUEST_ID.toString(), dlq.getJMSCorrelationID());
      assertEquals("nk.sync.request", dlq.getStringProperty("_AMQ_ORIG_ADDRESS"));
      assertEquals("nk.sync.request.q", dlq.getStringProperty("_AMQ_ORIG_QUEUE"));
      assertEquals("ID:provider-1", dlq.getStringProperty("NKOriginalTransportID"));
      assertEquals("PROTOCOL_INVALID", dlq.getStringProperty("NKErrorCode"));
      assertEquals("API_SYNC", dlq.getStringProperty("NKDetectedBy"));
      assertEquals(DETECTED_AT.toString(), dlq.getStringProperty("NKDetectedAt"));
      assertEquals(4, dlq.getIntProperty("NKDeliveryCount"));
      assertEquals(DeliveryMode.PERSISTENT, dlq.getJMSDeliveryMode());
      assertEquals(0L, dlq.getJMSExpiration());
      assertFalse(dlq.propertyExists("Password"));
      assertFalse(dlq.propertyExists("BodyHash"));
    } finally {
      broker.stop();
    }
  }

  @Test
  void outboundFactoriesRejectNullWrongModeAndEveryReplyIdentityMismatch() throws Exception {
    ReplySender replySender = new ReplySender();
    DlqSender dlqSender = new DlqSender();
    byte[] reply = responseWire('S', "LOGRSP01", 24);
    GuardedJmsMessage rejected = rejected(requestWire());
    FatalDlqMetadata fatal =
        new FatalDlqMetadata("INVALID", FatalDlqMetadata.DetectedBy.API_SYNC, DETECTED_AT);
    JMSContext transacted = context(JMSContext.SESSION_TRANSACTED);
    JMSContext autoAcknowledge = context(JMSContext.AUTO_ACKNOWLEDGE);

    assertThrows(NullPointerException.class, () -> replySender.send(null, reply));
    assertThrows(NullPointerException.class, () -> replySender.send(transacted, null));
    assertThrows(IllegalStateException.class, () -> replySender.send(autoAcknowledge, reply));
    assertThrows(NullPointerException.class, () -> dlqSender.send(null, rejected, fatal));
    assertThrows(NullPointerException.class, () -> dlqSender.send(transacted, null, fatal));
    assertThrows(NullPointerException.class, () -> dlqSender.send(transacted, rejected, null));
    assertThrows(
        IllegalStateException.class, () -> dlqSender.send(autoAcknowledge, rejected, fatal));

    assertThrows(
        NullPointerException.class, () -> JmsMessageFactory.INSTANCE.createReply(null, reply));
    assertThrows(
        NullPointerException.class, () -> JmsMessageFactory.INSTANCE.createReply(transacted, null));
    assertThrows(
        PermanentProtocolException.class,
        () -> JmsMessageFactory.INSTANCE.createReply(transacted, new byte[0]));
    assertThrows(
        IllegalArgumentException.class,
        () -> JmsMessageFactory.INSTANCE.createReply(transacted, Arrays.copyOf(reply, 1_000_001)));
    assertThrows(
        IllegalArgumentException.class,
        () -> JmsMessageFactory.INSTANCE.createReply(transacted, requestWire()));
    assertThrows(
        PermanentProtocolException.class,
        () ->
            JmsMessageFactory.INSTANCE.createReply(transacted, responseWire('S', "QSBRSP01", 64)));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            JmsMessageFactory.INSTANCE.createReply(
                transacted, Arrays.copyOf(reply, reply.length + 1)));
    assertEquals(1, JmsMessageFactory.values().length);
    assertEquals(JmsMessageFactory.INSTANCE, JmsMessageFactory.valueOf("INSTANCE"));
  }

  private static GuardedJmsMessage rejected(byte[] body) {
    return new GuardedJmsMessage(
        body,
        new TransportMetadata(
            TransportBodyType.BYTES,
            "ID:provider-1",
            REQUEST_ID,
            Optional.of("nk.sync.reply.web"),
            1_000,
            DeliveryMode.PERSISTENT,
            4,
            REQUEST_ID,
            new LayoutId("LOGREQ01"),
            FIXTURE_001_A3FEAA64,
            "nk.sync.request"));
  }

  private static byte[] body(BytesMessage message) throws Exception {
    byte[] body = new byte[Math.toIntExact(message.getBodyLength())];
    assertEquals(body.length, message.readBytes(body));
    return body;
  }

  private static Queue queue(BrokerTopology destination) {
    return new ActiveMQQueue(destination.fullyQualifiedQueue());
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

  private static byte[] requestWire() {
    return wire('Q', 'S', "LOGREQ01", REQUEST_ID, REQUEST_ID, 0, false);
  }

  private static byte[] responseWire(char interaction, String layout, int dataLength) {
    return wire('S', interaction, layout, RESPONSE_ID, REQUEST_ID, dataLength, true);
  }

  private static byte[] wire(
      char kind,
      char interaction,
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
    body[23] = (byte) interaction;
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
        .addAcceptorConfiguration("component", "vm://0");
    return new EmbeddedActiveMQ().setConfiguration(configuration).start();
  }
}
