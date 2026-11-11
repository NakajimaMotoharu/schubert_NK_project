package dev.codex.schubert.nk.web.messaging;

import dev.codex.schubert.nk.protocol.codec.ExpectedRoute;
import dev.codex.schubert.nk.protocol.codec.FixedWidthDecoder;
import dev.codex.schubert.nk.protocol.codec.HeaderCodec;
import dev.codex.schubert.nk.protocol.codec.PermanentProtocolException;
import dev.codex.schubert.nk.protocol.codec.TransportBodyType;
import dev.codex.schubert.nk.protocol.codec.TransportMetadata;
import dev.codex.schubert.nk.protocol.header.InteractionKind;
import dev.codex.schubert.nk.protocol.header.MessageKind;
import dev.codex.schubert.nk.protocol.layout.LayoutId;
import dev.codex.schubert.nk.protocol.layout.WireMessage;
import dev.codex.schubert.nk.protocol.transport.BrokerTopology;
import jakarta.jms.BytesMessage;
import jakarta.jms.Destination;
import jakarta.jms.JMSException;
import jakarta.jms.Message;
import java.util.Objects;
import java.util.Optional;
import java.util.UUID;
import org.apache.activemq.artemis.jms.client.ActiveMQDestination;
import org.jspecify.annotations.Nullable;

/**
 * Copies and validates one untrusted Web reply before correlation dispatch.
 *
 * <p>Trace: NK-MSG-001; RD MQ-004/MQ-005/MQ-008; UI 231; SS 321 sections 8-9 and 322 section 5.
 */
public final class JmsReplyDecoder {
  private static final int MINIMUM_DELIVERY_COUNT = 1;
  private static final String MALFORMED_IDENTITY = "reply transport identity is malformed";

  private static final String PROPERTY_MESSAGE_ID = "NKMessageID";
  private static final String PROPERTY_LAYOUT_ID = "NKLayoutID";
  private static final String PROPERTY_PROTOCOL_VERSION = "NKProtocolVersion";
  private static final String PROPERTY_DELIVERY_COUNT = "JMSXDeliveryCount";
  private static final ExpectedRoute REPLY_ROUTE =
      new ExpectedRoute(
          MessageKind.RESPONSE,
          InteractionKind.SYNCHRONOUS,
          BrokerTopology.SYNC_REPLY_WEB.address(),
          Optional.empty(),
          true);

  /** Returns an immutable body only after all provider, metadata and wire checks pass. */
  public ValidatedReply decode(Message message) throws JMSException {
    Objects.requireNonNull(message, "message");
    if (!(message instanceof BytesMessage bytesMessage)) {
      throw rejection("transport body is not a BytesMessage");
    }
    long bodyLength = bytesMessage.getBodyLength();
    if (bodyLength < 0 || bodyLength > BrokerTopology.SYNC_REPLY_WEB.maximumBodyLength()) {
      throw rejection("transport body length is outside the reply limit");
    }
    byte[] body = bytesMessage.getBody(byte[].class);
    if (body == null || body.length != bodyLength) {
      throw rejection("transport body length changed while it was copied");
    }

    String destinationAddress = requiredArtemisAddress(message.getJMSDestination());
    if (!destinationAddress.equals(BrokerTopology.SYNC_REPLY_WEB.address())) {
      throw rejection("reply was received on an unexpected destination");
    }
    if (message.getJMSReplyTo() != null) {
      throw rejection("a reply must not declare another reply-to destination");
    }

    // BUG2659/YKT2339: provider failures are not proof of malformed returned metadata.
    // Keep acquisition/validation order; only pure value parsing belongs to conversion catches.
    String transportId = requiredText(message.getJMSMessageID());
    UUID correlationId = parseUuid(requiredText(message.getJMSCorrelationID()));
    long expiration = message.getJMSExpiration();
    int deliveryMode = message.getJMSDeliveryMode();
    int deliveryCount = requiredDeliveryCount(message);
    UUID messageId = parseUuid(requiredProperty(message, PROPERTY_MESSAGE_ID));
    LayoutId layoutId = parseLayoutId(requiredProperty(message, PROPERTY_LAYOUT_ID));
    String protocolVersion = requiredProperty(message, PROPERTY_PROTOCOL_VERSION);
    try {
      TransportMetadata metadata =
          new TransportMetadata(
              TransportBodyType.BYTES,
              transportId,
              correlationId,
              Optional.empty(),
              expiration,
              deliveryMode,
              deliveryCount,
              messageId,
              layoutId,
              protocolVersion,
              destinationAddress);
      // SSC151/BUG421: registry-valid QSB S/A shares this physical reply route.
      ExpectedRoute registeredRoute =
          new ExpectedRoute(
              REPLY_ROUTE.messageKind(),
              HeaderCodec.standard().peek(body).interactionKind(),
              REPLY_ROUTE.destinationAddress(),
              REPLY_ROUTE.requiredReplyToAddress(),
              REPLY_ROUTE.expirationRequired());
      WireMessage<?> decoded = FixedWidthDecoder.standard().decode(body, metadata, registeredRoute);
      return new ValidatedReply(decoded.header().correlationId(), body);
    } catch (IllegalArgumentException exception) {
      throw rejection(MALFORMED_IDENTITY, exception);
    }
  }

  private static String requiredArtemisAddress(Destination destination) {
    if (!(destination instanceof ActiveMQDestination artemisDestination)
        || artemisDestination.isTemporary()) {
      throw rejection("reply destination is not a permanent Artemis destination");
    }
    String address = artemisDestination.getAddress();
    if (address == null || address.isBlank()) {
      throw rejection("reply destination address is missing");
    }
    int separator = address.indexOf("::");
    if (separator < 0) {
      return address;
    }
    String unqualified = address.substring(0, separator);
    String queue = address.substring(separator + 2);
    if (unqualified.isBlank() || !queue.equals(unqualified + ".q")) {
      throw rejection("reply queue-qualified destination is outside the approved topology");
    }
    return unqualified;
  }

  private static int requiredDeliveryCount(Message message) throws JMSException {
    if (!message.propertyExists(PROPERTY_DELIVERY_COUNT)) {
      throw rejection("reply delivery count is missing");
    }
    int count = message.getIntProperty(PROPERTY_DELIVERY_COUNT);
    if (count < MINIMUM_DELIVERY_COUNT) {
      throw rejection("reply delivery count is outside its range");
    }
    return count;
  }

  private static String requiredProperty(Message message, String property) throws JMSException {
    if (!message.propertyExists(property)) {
      throw rejection("required reply identity property is missing");
    }
    return requiredText(message.getStringProperty(property));
  }

  private static String requiredText(@Nullable String value) {
    if (value == null || value.isBlank()) {
      throw rejection("required reply transport value is missing");
    }
    return value;
  }

  private static UUID parseUuid(String value) {
    try {
      UUID parsed = UUID.fromString(value);
      // BUG2263/YKT2008: UI232 §6 requires exact text, before UUID normalization loses it.
      if (!parsed.toString().equals(value)) {
        throw new IllegalArgumentException("transport UUID is not lowercase canonical form");
      }
      return parsed;
    } catch (IllegalArgumentException exception) {
      throw rejection(MALFORMED_IDENTITY, exception);
    }
  }

  private static LayoutId parseLayoutId(String value) {
    try {
      return new LayoutId(value);
    } catch (IllegalArgumentException exception) {
      throw rejection(MALFORMED_IDENTITY, exception);
    }
  }

  private static PermanentProtocolException rejection(String message) {
    return new PermanentProtocolException(message);
  }

  private static PermanentProtocolException rejection(String message, Throwable cause) {
    return new PermanentProtocolException(message, cause);
  }
}
