package dev.codex.schubert.nk.web.messaging;

import dev.codex.schubert.nk.protocol.transport.BrokerTopology;
import jakarta.jms.DeliveryMode;
import jakarta.jms.JMSContext;
import jakarta.jms.JMSException;
import jakarta.jms.Message;
import java.time.Clock;
import java.util.Objects;
import java.util.UUID;
import java.util.function.Predicate;
import org.apache.activemq.artemis.jms.client.ActiveMQQueue;
import org.jspecify.annotations.Nullable;

/**
 * Re-sends an invalid reply to the fixed DLQ without reading or changing its body or JMS type.
 *
 * <p>Trace: NK-MSG-001; RD MQ-008/MQ-010; UI 231/251; SS 321 sections 7/10-11.
 */
public final class ArtemisReplyDlqSender {
  private static final String UNAVAILABLE = "UNAVAILABLE";
  private static final Predicate<String> UUID_VALUE = ArtemisReplyDlqSender::isCanonicalUuid;
  private static final Predicate<String> LAYOUT_VALUE = value -> value.matches("[A-Z0-9]{8}");
  private final Clock clock;

  public ArtemisReplyDlqSender(Clock clock) {
    this.clock = Objects.requireNonNull(clock, "clock");
  }

  /** Stages a property-sanitized original message; caller owns commit/rollback. */
  public void send(JMSContext context, Message rejected) throws JMSException {
    Objects.requireNonNull(context, "context");
    Objects.requireNonNull(rejected, "rejected");
    if (context.getSessionMode() != JMSContext.SESSION_TRANSACTED) {
      throw new IllegalStateException("JMS reply DLQ context must be transacted");
    }

    String originalTransportId =
        safeValue(rejected.getJMSMessageID(), 128, ArtemisReplyDlqSender::isPrintableAscii);
    String messageId = safeValue(rejected.getStringProperty("NKMessageID"), 36, UUID_VALUE);
    String correlationId = safeValue(rejected.getJMSCorrelationID(), 36, UUID_VALUE);
    String layoutId = safeValue(rejected.getStringProperty("NKLayoutID"), 8, LAYOUT_VALUE);
    int deliveryCount = safeDeliveryCount(rejected);

    rejected.clearProperties();
    rejected.setJMSCorrelationID(correlationId);
    rejected.setJMSReplyTo(null);
    rejected.setJMSType(null);
    rejected.setStringProperty("_AMQ_ORIG_ADDRESS", BrokerTopology.SYNC_REPLY_WEB.address());
    rejected.setStringProperty("_AMQ_ORIG_QUEUE", BrokerTopology.SYNC_REPLY_WEB.queue());
    rejected.setStringProperty("NKOriginalTransportID", originalTransportId);
    rejected.setStringProperty("NKMessageID", messageId);
    rejected.setStringProperty("NKCorrelationID", correlationId);
    rejected.setStringProperty("NKLayoutID", layoutId);
    rejected.setIntProperty("NKDeliveryCount", deliveryCount);
    rejected.setStringProperty("NKErrorCode", "PROTOCOL_INVALID");
    rejected.setStringProperty("NKDetectedBy", "WEB_REPLY");
    rejected.setStringProperty("NKDetectedAt", clock.instant().toString());
    context
        .createProducer()
        .setDeliveryMode(DeliveryMode.PERSISTENT)
        .setTimeToLive(BrokerTopology.DEAD_LETTER.timeToLiveMillis())
        .send(new ActiveMQQueue(BrokerTopology.DEAD_LETTER.fullyQualifiedQueue()), rejected);
  }

  private static int safeDeliveryCount(Message message) throws JMSException {
    if (!message.propertyExists("JMSXDeliveryCount")) {
      return 1;
    }
    int count = message.getIntProperty("JMSXDeliveryCount");
    return count < 1 ? 1 : count;
  }

  private static String safeValue(
      @Nullable String value, int maximumLength, Predicate<String> allowed) {
    if (value == null
        || value.isBlank()
        || value.length() > maximumLength
        || !allowed.test(value)) {
      return UNAVAILABLE;
    }
    return value;
  }

  private static boolean isPrintableAscii(String value) {
    return value.chars().allMatch(character -> character >= 0x20 && character <= 0x7e);
  }

  private static boolean isCanonicalUuid(String value) {
    try {
      return UUID.fromString(value).toString().equals(value);
    } catch (IllegalArgumentException exception) {
      return false;
    }
  }
}
