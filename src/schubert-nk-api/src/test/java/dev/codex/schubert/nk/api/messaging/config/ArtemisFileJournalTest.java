package dev.codex.schubert.nk.api.messaging.config;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.api.messaging.guard.GuardedJmsMessage;
import dev.codex.schubert.nk.api.messaging.guard.JmsMessageGuard;
import dev.codex.schubert.nk.api.messaging.outbound.FatalDlqMessageWriter;
import dev.codex.schubert.nk.api.messaging.outbound.FatalDlqMetadata;
import dev.codex.schubert.nk.protocol.codec.ExpectedRoute;
import dev.codex.schubert.nk.protocol.codec.TransportBodyType;
import dev.codex.schubert.nk.protocol.codec.TransportMetadata;
import dev.codex.schubert.nk.protocol.header.InteractionKind;
import dev.codex.schubert.nk.protocol.header.MessageKind;
import dev.codex.schubert.nk.protocol.layout.LayoutId;
import jakarta.jms.BytesMessage;
import jakarta.jms.DeliveryMode;
import jakarta.jms.JMSConsumer;
import jakarta.jms.JMSContext;
import jakarta.jms.Message;
import jakarta.jms.Queue;
import jakarta.jms.QueueBrowser;
import java.io.InputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Enumeration;
import java.util.List;
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

/** PT-JMS-010 actual NIO File Journal restart and persistent duplicate-cache test. */
final class ArtemisFileJournalTest {
  private static final String FIXTURE_VM_0_0C76084A = "vm://0";
  private static final String FIXTURE_NK_DEAD_LETTER_6588D12C = "nk.dead.letter";
  private static final String FIXTURE_NK_SYNC_REQUEST_422EE207 = "nk.sync.request";
  private static final String FIXTURE_NK_EXPIRY_41CB6B4A = "nk.expiry";
  private static final String FIXTURE_NK_ASYNC_WORK_NK_ASYNC_WORK_Q_5AB7EE46 =
      "nk.async.work::nk.async.work.q";
  private static final byte[] GOLDEN_BODY = {
    0x53, 0x43, 0x48, 0x55, 0x42, 0x45, 0x52, 0x54, 0x2d, 0x4e, 0x4b
  };
  private static final String DUPLICATE_ID = "pt-jms-010-duplicate-001";
  private static final byte[] DLQ_BODY = {0x44, 0x4c, 0x51};
  private static final byte[] EXPIRY_BODY = {0x45, 0x58, 0x50};

  @Test
  @DisplayName("PT-JMS-010 persistent BytesMessage and duplicate ID survive File Journal restart")
  void persistentMessageAndDuplicateCacheSurviveRestart(@TempDir Path root) throws Exception {
    Configuration configuration = isolatedProductionConfiguration(root);
    EmbeddedActiveMQ broker = start(configuration);
    try {
      sendPersistentDuplicatePair();
    } finally {
      broker.stop();
    }

    assertTrue(hasNonEmptyJournalFile(root.resolve("journal")));

    broker = start(configuration);
    try {
      receiveOnePersistentMessageAndNoDuplicate();
    } finally {
      broker.stop();
    }
  }

  @Test
  @DisplayName("PT-JMS-010 DLQ and Expiry remain durable and unpurged across restart")
  void persistentDlqAndExpirySurviveRestartWithoutPurge(@TempDir Path root) throws Exception {
    Configuration configuration = isolatedProductionConfiguration(root);
    EmbeddedActiveMQ broker = start(configuration);
    try (ActiveMQConnectionFactory factory = new ActiveMQConnectionFactory(FIXTURE_VM_0_0C76084A);
        JMSContext context = factory.createContext(JMSContext.AUTO_ACKNOWLEDGE)) {
      sendPersistent(context, FIXTURE_NK_DEAD_LETTER_6588D12C, DLQ_BODY, 0);
      sendPersistent(context, FIXTURE_NK_SYNC_REQUEST_422EE207, EXPIRY_BODY, 100);
      Thread.sleep(250);

      Queue request = new ActiveMQQueue("nk.sync.request::nk.sync.request.q");
      try (JMSConsumer consumer = context.createConsumer(request)) {
        assertNull(consumer.receive(1_000));
      }
      assertEquals(1, browseCount(context, FIXTURE_NK_DEAD_LETTER_6588D12C));
      assertEquals(1, browseCount(context, FIXTURE_NK_EXPIRY_41CB6B4A));
    } finally {
      broker.stop();
    }

    broker = start(configuration);
    try (ActiveMQConnectionFactory factory = new ActiveMQConnectionFactory(FIXTURE_VM_0_0C76084A);
        JMSContext context = factory.createContext(JMSContext.AUTO_ACKNOWLEDGE)) {
      assertEquals(1, browseCount(context, FIXTURE_NK_DEAD_LETTER_6588D12C));
      assertEquals(1, browseCount(context, FIXTURE_NK_EXPIRY_41CB6B4A));
      assertArrayEquals(DLQ_BODY, receiveBody(context, FIXTURE_NK_DEAD_LETTER_6588D12C));
      assertArrayEquals(EXPIRY_BODY, receiveBody(context, FIXTURE_NK_EXPIRY_41CB6B4A));
      assertEquals(0, browseCount(context, FIXTURE_NK_DEAD_LETTER_6588D12C));
      assertEquals(0, browseCount(context, FIXTURE_NK_EXPIRY_41CB6B4A));
    } finally {
      broker.stop();
    }
  }

  @Test
  @DisplayName("PT-JMS-004 broker redelivers after 1/5/25 seconds then routes to DLQ")
  void rollbackUsesApprovedTimelineAndFourthFailureRoutesToDlq(@TempDir Path root)
      throws Exception {
    Configuration configuration = isolatedProductionConfiguration(root);
    EmbeddedActiveMQ broker = start(configuration);
    try {
      List<Long> receivedAt = new ArrayList<>();
      List<Integer> deliveryCounts = new ArrayList<>();
      try (ActiveMQConnectionFactory factory =
              new ActiveMQConnectionFactory(FIXTURE_VM_0_0C76084A);
          JMSContext context = factory.createContext(JMSContext.SESSION_TRANSACTED)) {
        Queue work = new ActiveMQQueue(FIXTURE_NK_ASYNC_WORK_NK_ASYNC_WORK_Q_5AB7EE46);
        BytesMessage outbound = context.createBytesMessage();
        outbound.writeBytes(GOLDEN_BODY);
        context.createProducer().setDeliveryMode(DeliveryMode.PERSISTENT).send(work, outbound);
        context.commit();

        try (JMSConsumer consumer = context.createConsumer(work)) {
          long[] timeouts = {5_000L, 6_000L, 10_000L, 30_000L};
          for (long timeout : timeouts) {
            Message delivery = consumer.receive(timeout);
            assertNotNull(delivery);
            receivedAt.add(System.nanoTime());
            deliveryCounts.add(delivery.getIntProperty("JMSXDeliveryCount"));
            context.rollback();
          }
          assertNull(consumer.receive(500));
        }
      }

      assertEquals(List.of(1, 2, 3, 4), deliveryCounts);
      assertDelayBetween(receivedAt, 0, 800, 3_000);
      assertDelayBetween(receivedAt, 1, 4_000, 8_000);
      assertDelayBetween(receivedAt, 2, 20_000, 30_000);
      receiveDlqBodyAndNoDuplicate();
    } finally {
      broker.stop();
    }
  }

  @Test
  @DisplayName("PT-JMS-005 persistent request properties, TTL and body pass the production guard")
  void requestPropertiesTtlAndBodyRoundTripThroughActualBroker(@TempDir Path root)
      throws Exception {
    Configuration configuration = isolatedProductionConfiguration(root);
    EmbeddedActiveMQ broker = start(configuration);
    try (ActiveMQConnectionFactory factory = new ActiveMQConnectionFactory(FIXTURE_VM_0_0C76084A);
        JMSContext context = factory.createContext(JMSContext.AUTO_ACKNOWLEDGE)) {
      Queue requestAddress = new ActiveMQQueue("nk.sync.request::nk.sync.request.q");
      BytesMessage outbound = context.createBytesMessage();
      outbound.writeBytes(GOLDEN_BODY);
      outbound.setJMSCorrelationID("00000000-0000-0000-0000-000000000002");
      outbound.setJMSReplyTo(new ActiveMQQueue("nk.sync.reply.web"));
      outbound.setStringProperty("NKMessageID", "00000000-0000-0000-0000-000000000001");
      outbound.setStringProperty("NKLayoutID", "LOGREQ01");
      outbound.setStringProperty("NKProtocolVersion", "001");
      long sentBefore = System.currentTimeMillis();
      context
          .createProducer()
          .setDeliveryMode(DeliveryMode.PERSISTENT)
          .setTimeToLive(5_000)
          .send(requestAddress, outbound);

      try (JMSConsumer consumer =
          context.createConsumer(new ActiveMQQueue("nk.sync.request::nk.sync.request.q"))) {
        Message received = consumer.receive(5_000);
        assertNotNull(received);
        GuardedJmsMessage guarded =
            new JmsMessageGuard()
                .read(
                    received,
                    new ExpectedRoute(
                        MessageKind.REQUEST,
                        InteractionKind.SYNCHRONOUS,
                        FIXTURE_NK_SYNC_REQUEST_422EE207,
                        Optional.of("nk.sync.reply.web"),
                        true));
        assertArrayEquals(GOLDEN_BODY, guarded.body());
        assertTrue(guarded.metadata().expirationEpochMillis() >= sentBefore + 4_000);
        assertTrue(guarded.metadata().expirationEpochMillis() <= sentBefore + 6_000);
        assertEquals(DeliveryMode.PERSISTENT, guarded.metadata().deliveryMode());
        assertEquals(1, guarded.metadata().deliveryCount());
      }
    } finally {
      broker.stop();
    }
  }

  @Test
  @DisplayName("PT-JMS-007 transacted send/receive is controlled only by rollback and commit")
  void transactedSendAndReceiveRespectRollbackAndCommit(@TempDir Path root) throws Exception {
    Configuration configuration = isolatedProductionConfiguration(root);
    EmbeddedActiveMQ broker = start(configuration);
    try (ActiveMQConnectionFactory factory = new ActiveMQConnectionFactory(FIXTURE_VM_0_0C76084A);
        JMSContext context = factory.createContext(JMSContext.SESSION_TRANSACTED)) {
      Queue work = new ActiveMQQueue(FIXTURE_NK_ASYNC_WORK_NK_ASYNC_WORK_Q_5AB7EE46);
      BytesMessage rolledBack = context.createBytesMessage();
      rolledBack.writeBytes(new byte[] {0x11});
      context.createProducer().setDeliveryMode(DeliveryMode.PERSISTENT).send(work, rolledBack);
      context.rollback();

      try (JMSConsumer consumer = context.createConsumer(work)) {
        assertNull(consumer.receive(500));
        BytesMessage committed = context.createBytesMessage();
        committed.writeBytes(new byte[] {0x22});
        context.createProducer().setDeliveryMode(DeliveryMode.PERSISTENT).send(work, committed);
        context.commit();

        Message first = consumer.receive(5_000);
        assertNotNull(first);
        assertEquals(1, first.getIntProperty("JMSXDeliveryCount"));
        context.rollback();
        Message redelivered = consumer.receive(3_000);
        assertNotNull(redelivered);
        assertEquals(2, redelivered.getIntProperty("JMSXDeliveryCount"));
        context.commit();
        assertNull(consumer.receive(500));
      }
    } finally {
      broker.stop();
    }
  }

  @Test
  @DisplayName("PT-JMS-009 fatal DLQ message round-trips body and bounded metadata")
  void fatalDlqMessageRoundTripsThroughActualBroker(@TempDir Path root) throws Exception {
    Configuration configuration = isolatedProductionConfiguration(root);
    EmbeddedActiveMQ broker = start(configuration);
    try (ActiveMQConnectionFactory factory = new ActiveMQConnectionFactory(FIXTURE_VM_0_0C76084A);
        JMSContext context = factory.createContext(JMSContext.AUTO_ACKNOWLEDGE)) {
      GuardedJmsMessage source =
          new GuardedJmsMessage(
              GOLDEN_BODY,
              new TransportMetadata(
                  TransportBodyType.BYTES,
                  "ID:provider-1",
                  UUID.fromString("00000000-0000-0000-0000-000000000002"),
                  Optional.of("nk.sync.reply.web"),
                  1_000,
                  DeliveryMode.PERSISTENT,
                  4,
                  UUID.fromString("00000000-0000-0000-0000-000000000001"),
                  new LayoutId("LOGREQ01"),
                  "001",
                  FIXTURE_NK_SYNC_REQUEST_422EE207));
      BytesMessage dlq =
          FatalDlqMessageWriter.INSTANCE.create(
              context,
              source,
              new FatalDlqMetadata(
                  "PROTOCOL_INVALID",
                  FatalDlqMetadata.DetectedBy.API_SYNC,
                  Instant.parse("2026-09-03T00:00:00Z")));
      Queue destination = new ActiveMQQueue("nk.dead.letter::nk.dead.letter.q");
      context.createProducer().setDeliveryMode(DeliveryMode.PERSISTENT).send(destination, dlq);

      try (JMSConsumer consumer = context.createConsumer(destination)) {
        BytesMessage received = (BytesMessage) consumer.receive(5_000);
        assertNotNull(received);
        byte[] body = new byte[Math.toIntExact(received.getBodyLength())];
        received.readBytes(body);
        assertArrayEquals(GOLDEN_BODY, body);
        assertEquals(
            FIXTURE_NK_SYNC_REQUEST_422EE207, received.getStringProperty("_AMQ_ORIG_ADDRESS"));
        assertEquals("nk.sync.request.q", received.getStringProperty("_AMQ_ORIG_QUEUE"));
        assertEquals("PROTOCOL_INVALID", received.getStringProperty("NKErrorCode"));
        assertEquals("API_SYNC", received.getStringProperty("NKDetectedBy"));
        assertEquals(4, received.getIntProperty("NKDeliveryCount"));
      }
    } finally {
      broker.stop();
    }
  }

  private static Configuration isolatedProductionConfiguration(Path root) throws Exception {
    Path template = Path.of(System.getProperty("broker.template"));
    Configuration configuration;
    try (InputStream input = Files.newInputStream(template)) {
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
    return configuration;
  }

  private static EmbeddedActiveMQ start(Configuration configuration) throws Exception {
    return new EmbeddedActiveMQ().setConfiguration(configuration).start();
  }

  private static void sendPersistentDuplicatePair() throws Exception {
    try (ActiveMQConnectionFactory factory = new ActiveMQConnectionFactory(FIXTURE_VM_0_0C76084A);
        JMSContext context = factory.createContext(JMSContext.AUTO_ACKNOWLEDGE)) {
      Queue destination = new ActiveMQQueue(FIXTURE_NK_ASYNC_WORK_NK_ASYNC_WORK_Q_5AB7EE46);
      for (int send = 0; send < 2; send++) {
        BytesMessage message = context.createBytesMessage();
        message.writeBytes(GOLDEN_BODY);
        message.setStringProperty("_AMQ_DUPL_ID", DUPLICATE_ID);
        context
            .createProducer()
            .setDeliveryMode(DeliveryMode.PERSISTENT)
            .send(destination, message);
      }
    }
  }

  private static void receiveOnePersistentMessageAndNoDuplicate() throws Exception {
    try (ActiveMQConnectionFactory factory = new ActiveMQConnectionFactory(FIXTURE_VM_0_0C76084A);
        JMSContext context = factory.createContext(JMSContext.AUTO_ACKNOWLEDGE);
        JMSConsumer consumer =
            context.createConsumer(
                new ActiveMQQueue(FIXTURE_NK_ASYNC_WORK_NK_ASYNC_WORK_Q_5AB7EE46))) {
      BytesMessage received = (BytesMessage) consumer.receive(5_000);
      byte[] body = new byte[Math.toIntExact(received.getBodyLength())];
      received.readBytes(body);
      assertArrayEquals(GOLDEN_BODY, body);
      assertNull(consumer.receive(500));
    }
  }

  private static void receiveDlqBodyAndNoDuplicate() throws Exception {
    try (ActiveMQConnectionFactory factory = new ActiveMQConnectionFactory(FIXTURE_VM_0_0C76084A);
        JMSContext context = factory.createContext(JMSContext.AUTO_ACKNOWLEDGE);
        JMSConsumer consumer =
            context.createConsumer(new ActiveMQQueue("nk.dead.letter::nk.dead.letter.q"))) {
      BytesMessage received = (BytesMessage) consumer.receive(5_000);
      assertNotNull(received);
      byte[] body = new byte[Math.toIntExact(received.getBodyLength())];
      received.readBytes(body);
      assertArrayEquals(GOLDEN_BODY, body);
      assertNull(consumer.receive(500));
    }
  }

  private static void sendPersistent(
      JMSContext context, String address, byte[] body, long timeToLive) throws Exception {
    BytesMessage message = context.createBytesMessage();
    message.writeBytes(body);
    context
        .createProducer()
        .setDeliveryMode(DeliveryMode.PERSISTENT)
        .setTimeToLive(timeToLive)
        .send(new ActiveMQQueue(address + "::" + address + ".q"), message);
  }

  private static int browseCount(JMSContext context, String address) throws Exception {
    Queue queue = new ActiveMQQueue(address + "::" + address + ".q");
    int count = 0;
    try (QueueBrowser browser = context.createBrowser(queue)) {
      Enumeration<?> messages = browser.getEnumeration();
      while (messages.hasMoreElements()) {
        messages.nextElement();
        count++;
      }
    }
    return count;
  }

  private static byte[] receiveBody(JMSContext context, String address) throws Exception {
    Queue queue = new ActiveMQQueue(address + "::" + address + ".q");
    try (JMSConsumer consumer = context.createConsumer(queue)) {
      BytesMessage message = (BytesMessage) consumer.receive(5_000);
      assertNotNull(message);
      byte[] body = new byte[Math.toIntExact(message.getBodyLength())];
      message.readBytes(body);
      assertNull(consumer.receive(500));
      return body;
    }
  }

  private static void assertDelayBetween(
      List<Long> receivedAt, int earlierIndex, long minimumMillis, long maximumMillis) {
    long actualMillis =
        java.util.concurrent.TimeUnit.NANOSECONDS.toMillis(
            receivedAt.get(earlierIndex + 1) - receivedAt.get(earlierIndex));
    assertTrue(
        actualMillis >= minimumMillis && actualMillis <= maximumMillis,
        () ->
            "delay at index "
                + earlierIndex
                + " was "
                + actualMillis
                + " ms, expected "
                + minimumMillis
                + ".."
                + maximumMillis);
  }

  private static boolean hasNonEmptyJournalFile(Path journal) throws Exception {
    try (var files = Files.list(journal)) {
      return files.filter(Files::isRegularFile).anyMatch(ArtemisFileJournalTest::isNonEmpty);
    }
  }

  private static boolean isNonEmpty(Path path) {
    try {
      return Files.size(path) > 0;
    } catch (java.io.IOException exception) {
      throw new java.io.UncheckedIOException(exception);
    }
  }
}
