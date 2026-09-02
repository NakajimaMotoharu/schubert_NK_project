package dev.codex.schubert.nk.api.messaging.config;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

import jakarta.jms.BytesMessage;
import jakarta.jms.DeliveryMode;
import jakarta.jms.JMSContext;
import jakarta.jms.JMSConsumer;
import jakarta.jms.Message;
import jakarta.jms.Queue;
import java.io.InputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
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
  private static final byte[] GOLDEN_BODY = {
    0x53, 0x43, 0x48, 0x55, 0x42, 0x45, 0x52, 0x54, 0x2d, 0x4e, 0x4b
  };
  private static final String DUPLICATE_ID = "pt-jms-010-duplicate-001";

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
  @DisplayName("PT-JMS-004 broker redelivers after 1/5/25 seconds then routes to DLQ")
  void rollbackUsesApprovedTimelineAndFourthFailureRoutesToDlq(@TempDir Path root)
      throws Exception {
    Configuration configuration = isolatedProductionConfiguration(root);
    EmbeddedActiveMQ broker = start(configuration);
    try {
      List<Long> receivedAt = new ArrayList<>();
      List<Integer> deliveryCounts = new ArrayList<>();
      try (ActiveMQConnectionFactory factory = new ActiveMQConnectionFactory("vm://0");
          JMSContext context = factory.createContext(JMSContext.SESSION_TRANSACTED)) {
        Queue work = new ActiveMQQueue("nk.async.work::nk.async.work.q");
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
        .addAcceptorConfiguration("component", "vm://0");
    return configuration;
  }

  private static EmbeddedActiveMQ start(Configuration configuration) throws Exception {
    return new EmbeddedActiveMQ().setConfiguration(configuration).start();
  }

  private static void sendPersistentDuplicatePair() throws Exception {
    try (ActiveMQConnectionFactory factory = new ActiveMQConnectionFactory("vm://0");
        JMSContext context = factory.createContext(JMSContext.AUTO_ACKNOWLEDGE)) {
      Queue destination = new ActiveMQQueue("nk.async.work::nk.async.work.q");
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
    try (ActiveMQConnectionFactory factory = new ActiveMQConnectionFactory("vm://0");
        JMSContext context = factory.createContext(JMSContext.AUTO_ACKNOWLEDGE);
        JMSConsumer consumer =
            context.createConsumer(
                new ActiveMQQueue("nk.async.work::nk.async.work.q"))) {
      BytesMessage received = (BytesMessage) consumer.receive(5_000);
      byte[] body = new byte[Math.toIntExact(received.getBodyLength())];
      received.readBytes(body);
      assertArrayEquals(GOLDEN_BODY, body);
      assertNull(consumer.receive(500));
    }
  }

  private static void receiveDlqBodyAndNoDuplicate() throws Exception {
    try (ActiveMQConnectionFactory factory = new ActiveMQConnectionFactory("vm://0");
        JMSContext context = factory.createContext(JMSContext.AUTO_ACKNOWLEDGE);
        JMSConsumer consumer =
            context.createConsumer(
                new ActiveMQQueue("nk.dead.letter::nk.dead.letter.q"))) {
      BytesMessage received = (BytesMessage) consumer.receive(5_000);
      assertNotNull(received);
      byte[] body = new byte[Math.toIntExact(received.getBodyLength())];
      received.readBytes(body);
      assertArrayEquals(GOLDEN_BODY, body);
      assertNull(consumer.receive(500));
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
