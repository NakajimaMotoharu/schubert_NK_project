package dev.codex.schubert.nk.api.messaging.guard;

import dev.codex.schubert.nk.protocol.codec.ExpectedRoute;
import dev.codex.schubert.nk.protocol.codec.PermanentProtocolException;
import dev.codex.schubert.nk.protocol.codec.TransportBodyType;
import dev.codex.schubert.nk.protocol.codec.TransportMetadata;
import dev.codex.schubert.nk.protocol.layout.LayoutId;
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
 * Copies and validates untrusted Artemis/JMS metadata before fixed-width decoding.
 *
 * <p>Trace: NK-MSG-001; RD MQ-003/MQ-008/MQ-040..045; UI 231; SS 321 §4/§8. Rejection messages
 * never contain a body, credential, session, property value or transport ID.
 */
public final class JmsMessageGuard {
  private static final int MINIMUM_DELIVERY_COUNT = 1;

  private static final String PROPERTY_MESSAGE_ID = "NKMessageID";
  private static final String PROPERTY_LAYOUT_ID = "NKLayoutID";
  private static final String PROPERTY_PROTOCOL_VERSION = "NKProtocolVersion";
  private static final String PROPERTY_DELIVERY_COUNT = "JMSXDeliveryCount";

  /** Reads one exact BytesMessage body and a closed metadata snapshot. */
  public GuardedJmsMessage read(Message message, ExpectedRoute route) throws JMSException {
    Objects.requireNonNull(message, "message");
    Objects.requireNonNull(route, "route");
    if (!(message instanceof BytesMessage bytesMessage)) {
      throw rejection("transport body is not a BytesMessage");
    }

    int maximumBodyLength =
        BrokerTopology.requireAddress(route.destinationAddress()).maximumBodyLength();
    long bodyLength = bytesMessage.getBodyLength();
    if (bodyLength < 0 || bodyLength > maximumBodyLength) {
      throw rejection("transport body length is outside the fixed-width limit");
    }
    byte[] body = bytesMessage.getBody(byte[].class);
    if (body == null || body.length != bodyLength) {
      throw rejection("transport body length changed while it was copied");
    }

    String destinationAddress = requiredArtemisAddress(message.getJMSDestination());
    if (!destinationAddress.equals(route.destinationAddress())) {
      throw rejection("message was received on an unexpected destination");
    }
    Optional<String> replyToAddress = optionalReplyTo(message.getJMSReplyTo());
    if (!replyToAddress.equals(route.requiredReplyToAddress())) {
      throw rejection("reply-to destination is absent, dynamic or outside the allowlist");
    }

    try {
      TransportMetadata metadata =
          new TransportMetadata(
              TransportBodyType.BYTES,
              requiredHeader(message.getJMSMessageID()),
              parseUuid(requiredHeader(message.getJMSCorrelationID())),
              replyToAddress,
              message.getJMSExpiration(),
              message.getJMSDeliveryMode(),
              requiredDeliveryCount(message),
              parseUuid(requiredProperty(message, PROPERTY_MESSAGE_ID)),
              new LayoutId(requiredProperty(message, PROPERTY_LAYOUT_ID)),
              requiredProperty(message, PROPERTY_PROTOCOL_VERSION),
              destinationAddress);
      return new GuardedJmsMessage(body, metadata);
    } catch (IllegalArgumentException exception) {
      throw rejection("transport identity property is malformed", exception);
    }
  }

  private static Optional<String> optionalReplyTo(@Nullable Destination destination) {
    if (destination == null) {
      return Optional.empty();
    }
    return Optional.of(requiredArtemisAddress(destination));
  }

  private static String requiredArtemisAddress(Destination destination) {
    if (!(destination instanceof ActiveMQDestination artemisDestination)
        || artemisDestination.isTemporary()) {
      throw rejection("transport destination is not a permanent Artemis destination");
    }
    String address = artemisDestination.getAddress();
    if (address == null || address.isBlank()) {
      throw rejection("transport destination address is missing");
    }
    int separator = address.indexOf("::");
    if (separator < 0) {
      return address;
    }
    String unqualified = address.substring(0, separator);
    String queue = address.substring(separator + 2);
    if (unqualified.isBlank() || !queue.equals(unqualified + ".q")) {
      throw rejection("queue-qualified destination is outside the approved topology");
    }
    return unqualified;
  }

  private static int requiredDeliveryCount(Message message) throws JMSException {
    if (!message.propertyExists(PROPERTY_DELIVERY_COUNT)) {
      throw rejection("transport delivery count is missing");
    }
    int count = message.getIntProperty(PROPERTY_DELIVERY_COUNT);
    if (count < MINIMUM_DELIVERY_COUNT) {
      throw rejection("transport delivery count is outside its range");
    }
    return count;
  }

  private static String requiredProperty(Message message, String property) throws JMSException {
    if (!message.propertyExists(property)) {
      throw rejection("required transport identity property is missing");
    }
    return requiredHeader(message.getStringProperty(property));
  }

  private static String requiredHeader(String value) {
    if (value == null || value.isBlank()) {
      throw rejection("required transport header is missing");
    }
    return value;
  }

  private static UUID parseUuid(String value) {
    UUID parsed = UUID.fromString(value);
    // BUG2263/YKT2008: UI232 §6 requires exact text, before UUID normalization loses it.
    if (!parsed.toString().equals(value)) {
      throw new IllegalArgumentException("transport UUID is not lowercase canonical form");
    }
    return parsed;
  }

  private static PermanentProtocolException rejection(String message) {
    return new PermanentProtocolException(message);
  }

  private static PermanentProtocolException rejection(String message, Throwable cause) {
    return new PermanentProtocolException(message, cause);
  }
}
