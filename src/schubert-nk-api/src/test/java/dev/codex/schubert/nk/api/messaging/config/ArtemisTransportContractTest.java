package dev.codex.schubert.nk.api.messaging.config;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.api.messaging.guard.GuardedJmsMessage;
import dev.codex.schubert.nk.api.messaging.guard.JmsMessageGuard;
import dev.codex.schubert.nk.protocol.codec.ExpectedRoute;
import dev.codex.schubert.nk.protocol.codec.FixedWidthDecoder;
import dev.codex.schubert.nk.protocol.codec.PermanentProtocolException;
import dev.codex.schubert.nk.protocol.header.InteractionKind;
import dev.codex.schubert.nk.protocol.header.MessageKind;
import jakarta.jms.BytesMessage;
import jakarta.jms.DeliveryMode;
import jakarta.jms.JMSConsumer;
import jakarta.jms.JMSContext;
import jakarta.jms.JMSException;
import jakarta.jms.MapMessage;
import jakarta.jms.Message;
import jakarta.jms.ObjectMessage;
import jakarta.jms.Queue;
import jakarta.jms.TextMessage;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Arrays;
import java.util.List;
import java.util.Locale;
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

/** PT-JMS-005/006 actual-provider transport matrix with independent SS 321/322 bytes. */
final class ArtemisTransportContractTest {
  private static final String FIXTURE_LOGREQ01_A98AF5F3 = "LOGREQ01";
  private static final String FIXTURE_NK_SYNC_REPLY_WEB_6759A786 = "nk.sync.reply.web";
  private static final String FIXTURE_001_A3FEAA64 = "001";
  private static final UUID MESSAGE_ID = UUID.fromString("00000000-0000-0000-0000-000000000001");
  private static final UUID CORRELATION_ID =
      UUID.fromString("00000000-0000-0000-0000-000000000002");
  private static final JmsMessageGuard GUARD = new JmsMessageGuard();

  @Test
  @DisplayName("PT-JMS-005 request, reply, work and log use exact persistent transport contracts")
  void allFourApplicationRoutesRoundTripAndDecode(@TempDir Path root) throws Exception {
    List<RouteVector> routes =
        List.of(
            new RouteVector(
                "nk.sync.request",
                FIXTURE_LOGREQ01_A98AF5F3,
                MessageKind.REQUEST,
                InteractionKind.SYNCHRONOUS,
                'Q',
                'S',
                0,
                5_000,
                Optional.of(FIXTURE_NK_SYNC_REPLY_WEB_6759A786)),
            new RouteVector(
                FIXTURE_NK_SYNC_REPLY_WEB_6759A786,
                "LOGRSP01",
                MessageKind.RESPONSE,
                InteractionKind.SYNCHRONOUS,
                'S',
                'S',
                24,
                10_000,
                Optional.empty()),
            new RouteVector(
                "nk.async.work",
                "QWKREQ01",
                MessageKind.EVENT,
                InteractionKind.INTERNAL,
                'E',
                'I',
                64,
                0,
                Optional.empty()),
            new RouteVector(
                "nk.web.log",
                "WLGEVT01",
                MessageKind.EVENT,
                InteractionKind.INTERNAL,
                'E',
                'I',
                2_080,
                0,
                Optional.empty()));

    EmbeddedActiveMQ broker = start(root);
    try (ActiveMQConnectionFactory factory = new ActiveMQConnectionFactory("vm://0");
        JMSContext context = factory.createContext(JMSContext.AUTO_ACKNOWLEDGE)) {
      for (RouteVector vector : routes) {
        byte[] body = independentWire(vector);
        BytesMessage outbound = context.createBytesMessage();
        outbound.writeBytes(body);
        setIdentity(outbound, vector.layoutId(), vector.correlationId());
        vector.replyTo().ifPresent(address -> setReplyTo(outbound, new ActiveMQQueue(address)));

        long beforeSend = System.currentTimeMillis();
        Message received =
            roundTrip(
                context,
                vector.address(),
                outbound,
                DeliveryMode.PERSISTENT,
                vector.timeToLiveMillis());
        ExpectedRoute route = vector.expectedRoute();
        GuardedJmsMessage guarded = GUARD.read(received, route);
        var decoded =
            FixedWidthDecoder.standard().decode(guarded.body(), guarded.metadata(), route);

        assertArrayEquals(body, guarded.body());
        assertEquals(vector.layoutId(), decoded.header().layoutId().value());
        assertEquals(vector.messageKind(), decoded.header().messageKind());
        assertEquals(vector.interactionKind(), decoded.header().interactionKind());
        assertEquals(MESSAGE_ID, decoded.header().messageId());
        assertEquals(vector.correlationId(), decoded.header().correlationId());
        assertEquals(DeliveryMode.PERSISTENT, guarded.metadata().deliveryMode());
        assertEquals(vector.address(), guarded.metadata().destinationAddress());
        if (vector.timeToLiveMillis() == 0) {
          assertEquals(0L, guarded.metadata().expirationEpochMillis());
        } else {
          long expiration = guarded.metadata().expirationEpochMillis();
          assertTrue(expiration >= beforeSend + vector.timeToLiveMillis() - 500);
          assertTrue(expiration <= beforeSend + vector.timeToLiveMillis() + 2_000);
        }
      }
    } finally {
      broker.stop();
    }
  }

  @Test
  @DisplayName("PT-JMS-006 actual providers, limits, values, mode and reply-to deny closed")
  void actualProviderAndMetadataViolationsAreRejectedBeforeBusinessHandling(@TempDir Path root)
      throws Exception {
    RouteVector request =
        new RouteVector(
            "nk.sync.request",
            FIXTURE_LOGREQ01_A98AF5F3,
            MessageKind.REQUEST,
            InteractionKind.SYNCHRONOUS,
            'Q',
            'S',
            0,
            5_000,
            Optional.of(FIXTURE_NK_SYNC_REPLY_WEB_6759A786));
    ExpectedRoute route = request.expectedRoute();
    byte[] validBody = independentWire(request);

    EmbeddedActiveMQ broker = start(root);
    try (ActiveMQConnectionFactory factory = new ActiveMQConnectionFactory("vm://0");
        JMSContext context = factory.createContext(JMSContext.AUTO_ACKNOWLEDGE)) {
      TextMessage text = context.createTextMessage("synthetic non-business text");
      MapMessage map = context.createMapMessage();
      map.setString("synthetic", "non-business-map");
      ObjectMessage object = context.createObjectMessage("synthetic non-business object");
      for (Message wrongType : List.of(text, map, object)) {
        setRequestIdentity(
            wrongType,
            FIXTURE_LOGREQ01_A98AF5F3,
            new ActiveMQQueue(FIXTURE_NK_SYNC_REPLY_WEB_6759A786));
        Message received =
            roundTrip(
                context,
                request.address(),
                wrongType,
                DeliveryMode.PERSISTENT,
                request.timeToLiveMillis());
        assertThrows(PermanentProtocolException.class, () -> GUARD.read(received, route));
      }

      assertRouteBodyLimit(
          context,
          request.address(),
          FIXTURE_LOGREQ01_A98AF5F3,
          MESSAGE_ID,
          1_000_000,
          5_000,
          Optional.of(FIXTURE_NK_SYNC_REPLY_WEB_6759A786),
          route);

      ExpectedRoute replyRoute =
          new ExpectedRoute(
              MessageKind.RESPONSE,
              InteractionKind.SYNCHRONOUS,
              FIXTURE_NK_SYNC_REPLY_WEB_6759A786,
              Optional.empty(),
              true);
      assertRouteBodyLimit(
          context,
          FIXTURE_NK_SYNC_REPLY_WEB_6759A786,
          "LOGRSP01",
          CORRELATION_ID,
          1_000_000,
          10_000,
          Optional.empty(),
          replyRoute);

      ExpectedRoute workRoute =
          new ExpectedRoute(
              MessageKind.EVENT,
              InteractionKind.INTERNAL,
              "nk.async.work",
              Optional.empty(),
              false);
      assertRouteBodyLimit(
          context,
          "nk.async.work",
          "QWKREQ01",
          CORRELATION_ID,
          1_000,
          0,
          Optional.empty(),
          workRoute);

      ExpectedRoute webLogRoute =
          new ExpectedRoute(
              MessageKind.EVENT, InteractionKind.INTERNAL, "nk.web.log", Optional.empty(), false);
      assertRouteBodyLimit(
          context,
          "nk.web.log",
          "WLGEVT01",
          CORRELATION_ID,
          10_000,
          0,
          Optional.empty(),
          webLogRoute);

      BytesMessage shortBody = bytes(context, new byte[255]);
      setRequestIdentity(
          shortBody,
          FIXTURE_LOGREQ01_A98AF5F3,
          new ActiveMQQueue(FIXTURE_NK_SYNC_REPLY_WEB_6759A786));
      assertDecodeRejected(
          roundTrip(
              context,
              request.address(),
              shortBody,
              DeliveryMode.PERSISTENT,
              request.timeToLiveMillis()),
          route);

      BytesMessage nonPersistent = bytes(context, validBody);
      setRequestIdentity(
          nonPersistent,
          FIXTURE_LOGREQ01_A98AF5F3,
          new ActiveMQQueue(FIXTURE_NK_SYNC_REPLY_WEB_6759A786));
      assertDecodeRejected(
          roundTrip(
              context,
              request.address(),
              nonPersistent,
              DeliveryMode.NON_PERSISTENT,
              request.timeToLiveMillis()),
          route);

      BytesMessage missingLayout = bytes(context, validBody);
      missingLayout.setJMSCorrelationID(MESSAGE_ID.toString());
      missingLayout.setJMSReplyTo(new ActiveMQQueue(FIXTURE_NK_SYNC_REPLY_WEB_6759A786));
      missingLayout.setStringProperty("NKMessageID", MESSAGE_ID.toString());
      missingLayout.setStringProperty("NKProtocolVersion", FIXTURE_001_A3FEAA64);
      Message missingReceived =
          roundTrip(
              context,
              request.address(),
              missingLayout,
              DeliveryMode.PERSISTENT,
              request.timeToLiveMillis());
      assertThrows(PermanentProtocolException.class, () -> GUARD.read(missingReceived, route));

      BytesMessage unknownLayout = bytes(context, validBody);
      setRequestIdentity(
          unknownLayout, "ZZZREQ01", new ActiveMQQueue(FIXTURE_NK_SYNC_REPLY_WEB_6759A786));
      assertDecodeRejected(
          roundTrip(
              context,
              request.address(),
              unknownLayout,
              DeliveryMode.PERSISTENT,
              request.timeToLiveMillis()),
          route);

      BytesMessage unknownProtocol = bytes(context, validBody);
      setRequestIdentity(
          unknownProtocol,
          FIXTURE_LOGREQ01_A98AF5F3,
          new ActiveMQQueue(FIXTURE_NK_SYNC_REPLY_WEB_6759A786));
      unknownProtocol.setStringProperty("NKProtocolVersion", "999");
      assertDecodeRejected(
          roundTrip(
              context,
              request.address(),
              unknownProtocol,
              DeliveryMode.PERSISTENT,
              request.timeToLiveMillis()),
          route);

      BytesMessage dynamicReply = bytes(context, validBody);
      setRequestIdentity(
          dynamicReply, FIXTURE_LOGREQ01_A98AF5F3, new ActiveMQQueue("nk.unapproved.reply"));
      Message dynamicReceived =
          roundTrip(
              context,
              request.address(),
              dynamicReply,
              DeliveryMode.PERSISTENT,
              request.timeToLiveMillis());
      assertThrows(PermanentProtocolException.class, () -> GUARD.read(dynamicReceived, route));
    } finally {
      broker.stop();
    }
  }

  private static void assertDecodeRejected(Message received, ExpectedRoute route) throws Exception {
    GuardedJmsMessage guarded = GUARD.read(received, route);
    assertThrows(
        PermanentProtocolException.class,
        () -> FixedWidthDecoder.standard().decode(guarded.body(), guarded.metadata(), route));
  }

  private static void assertRouteBodyLimit(
      JMSContext context,
      String address,
      String layoutId,
      UUID correlationId,
      int maximumLength,
      long timeToLive,
      Optional<String> replyTo,
      ExpectedRoute route)
      throws Exception {
    BytesMessage maximum = bytes(context, new byte[maximumLength]);
    setIdentity(maximum, layoutId, correlationId);
    if (replyTo.isPresent()) {
      maximum.setJMSReplyTo(new ActiveMQQueue(replyTo.orElseThrow()));
    }
    GuardedJmsMessage accepted =
        guardRoundTrip(context, address, maximum, DeliveryMode.PERSISTENT, timeToLive, route);
    assertEquals(maximumLength, accepted.body().length);

    BytesMessage excessive = bytes(context, new byte[maximumLength + 1]);
    setIdentity(excessive, layoutId, correlationId);
    if (replyTo.isPresent()) {
      excessive.setJMSReplyTo(new ActiveMQQueue(replyTo.orElseThrow()));
    }
    assertThrows(
        PermanentProtocolException.class,
        () ->
            guardRoundTrip(
                context, address, excessive, DeliveryMode.PERSISTENT, timeToLive, route));
  }

  private static Message roundTrip(
      JMSContext context, String address, Message outbound, int deliveryMode, long timeToLive)
      throws JMSException {
    Queue destination = new ActiveMQQueue(address + "::" + address + ".q");
    try (JMSConsumer consumer = context.createConsumer(destination)) {
      context
          .createProducer()
          .setDeliveryMode(deliveryMode)
          .setTimeToLive(timeToLive)
          .send(destination, outbound);
      Message received = consumer.receive(10_000);
      assertNotNull(received);
      return received;
    }
  }

  private static GuardedJmsMessage guardRoundTrip(
      JMSContext context,
      String address,
      Message outbound,
      int deliveryMode,
      long timeToLive,
      ExpectedRoute route)
      throws JMSException {
    Queue destination = new ActiveMQQueue(address + "::" + address + ".q");
    try (JMSConsumer consumer = context.createConsumer(destination)) {
      context
          .createProducer()
          .setDeliveryMode(deliveryMode)
          .setTimeToLive(timeToLive)
          .send(destination, outbound);
      Message received = consumer.receive(10_000);
      assertNotNull(received);
      return GUARD.read(received, route);
    }
  }

  private static BytesMessage bytes(JMSContext context, byte[] body) throws JMSException {
    BytesMessage message = context.createBytesMessage();
    message.writeBytes(body);
    return message;
  }

  private static void setRequestIdentity(Message message, String layoutId, Queue replyTo)
      throws JMSException {
    setIdentity(message, layoutId, MESSAGE_ID);
    message.setJMSReplyTo(replyTo);
  }

  private static void setIdentity(Message message, String layoutId, UUID correlationId)
      throws JMSException {
    message.setJMSCorrelationID(correlationId.toString());
    message.setStringProperty("NKMessageID", MESSAGE_ID.toString());
    message.setStringProperty("NKLayoutID", layoutId);
    message.setStringProperty("NKProtocolVersion", FIXTURE_001_A3FEAA64);
  }

  private static void setReplyTo(Message message, Queue replyTo) {
    try {
      message.setJMSReplyTo(replyTo);
    } catch (JMSException exception) {
      throw new IllegalStateException("synthetic reply-to could not be set", exception);
    }
  }

  private static byte[] independentWire(RouteVector vector) {
    int totalLength = 256 + vector.dataLength();
    byte[] body = new byte[totalLength];
    Arrays.fill(body, (byte) ' ');
    ascii(body, 0, "SCHBNK01");
    ascii(body, 8, FIXTURE_001_A3FEAA64);
    ascii(body, 11, vector.layoutId());
    ascii(body, 19, FIXTURE_001_A3FEAA64);
    body[22] = (byte) vector.messageKindWire();
    body[23] = (byte) vector.interactionKindWire();
    ascii(body, 24, MESSAGE_ID.toString());
    ascii(body, 60, vector.correlationId().toString());
    ascii(body, 96, "20260903120000000");
    if (vector.messageKind() != MessageKind.EVENT) {
      ascii(body, 113, "a".repeat(64));
    }
    ascii(body, 177, "0256");
    ascii(body, 181, sixDigits(vector.dataLength()));
    ascii(body, 187, "000000");
    ascii(body, 193, "000000");
    ascii(body, 199, nineDigits(totalLength));
    if (vector.messageKind() == MessageKind.RESPONSE) {
      ascii(body, 208, "0000");
    }
    return body;
  }

  private static String sixDigits(int value) {
    return String.format(Locale.ROOT, "%06d", value);
  }

  private static String nineDigits(int value) {
    return String.format(Locale.ROOT, "%09d", value);
  }

  private static void ascii(byte[] target, int offset, String value) {
    byte[] source = value.getBytes(StandardCharsets.US_ASCII);
    System.arraycopy(source, 0, target, offset, source.length);
  }

  private static EmbeddedActiveMQ start(Path root) throws Exception {
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
    return new EmbeddedActiveMQ().setConfiguration(configuration).start();
  }

  private record RouteVector(
      String address,
      String layoutId,
      MessageKind messageKind,
      InteractionKind interactionKind,
      char messageKindWire,
      char interactionKindWire,
      int dataLength,
      long timeToLiveMillis,
      Optional<String> replyTo) {

    private UUID correlationId() {
      return messageKind == MessageKind.REQUEST ? MESSAGE_ID : CORRELATION_ID;
    }

    private ExpectedRoute expectedRoute() {
      return new ExpectedRoute(
          messageKind, interactionKind, address, replyTo, timeToLiveMillis > 0);
    }
  }
}
