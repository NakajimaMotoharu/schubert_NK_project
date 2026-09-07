package dev.codex.schubert.nk.api.messaging.outbound;

import dev.codex.schubert.nk.api.messaging.guard.GuardedJmsMessage;
import dev.codex.schubert.nk.protocol.transport.BrokerTopology;
import jakarta.jms.BytesMessage;
import jakarta.jms.DeliveryMode;
import jakarta.jms.JMSContext;
import jakarta.jms.JMSException;
import jakarta.jms.Message;
import java.util.Objects;
import java.util.UUID;
import java.util.function.Predicate;
import org.apache.activemq.artemis.jms.client.ActiveMQQueue;
import org.jspecify.annotations.Nullable;

/**
 * Stages a body-preserving fatal message in the fixed DLQ within the receiver transaction.
 *
 * <p>Trace: NK-MSG-001; RD MQ-008/MQ-010; UI 231/251; SS 312 sections 3/9 and 321 sections 7/11.
 */
public final class DlqSender {
  private static final String UNAVAILABLE = "UNAVAILABLE";
  private static final Predicate<String> UUID_VALUE = DlqSender::isCanonicalUuid;
  private static final Predicate<String> LAYOUT_VALUE = value -> value.matches("[A-Z0-9]{8}");

  /** Sends without commit so the caller can atomically commit the original message ACK. */
  public void send(JMSContext context, GuardedJmsMessage rejected, FatalDlqMetadata fatal)
      throws JMSException {
    Objects.requireNonNull(context, "context");
    Objects.requireNonNull(rejected, "rejected");
    Objects.requireNonNull(fatal, "fatal");
    if (context.getSessionMode() != JMSContext.SESSION_TRANSACTED) {
      throw new IllegalStateException("JMS DLQ context must be transacted");
    }
    BytesMessage dlq = FatalDlqMessageWriter.INSTANCE.create(context, rejected, fatal);
    context
        .createProducer()
        .setDeliveryMode(DeliveryMode.PERSISTENT)
        .setTimeToLive(BrokerTopology.DEAD_LETTER.timeToLiveMillis())
        .send(new ActiveMQQueue(BrokerTopology.DEAD_LETTER.fullyQualifiedQueue()), dlq);
  }

  /**
   * Stages an untrusted original message without reading or changing its body/JMS type. Arbitrary
   * properties are replaced by the bounded SS 321 section 11 allowlist.
   */
  public void sendUntrusted(
      JMSContext context,
      Message rejected,
      BrokerTopology originalDestination,
      FatalDlqMetadata fatal)
      throws JMSException {
    Objects.requireNonNull(context, "context");
    Objects.requireNonNull(rejected, "rejected");
    Objects.requireNonNull(originalDestination, "originalDestination");
    Objects.requireNonNull(fatal, "fatal");
    if (context.getSessionMode() != JMSContext.SESSION_TRANSACTED) {
      throw new IllegalStateException("JMS DLQ context must be transacted");
    }
    if (originalDestination == BrokerTopology.DEAD_LETTER
        || originalDestination == BrokerTopology.EXPIRY) {
      throw new IllegalArgumentException("an administrative queue cannot be a DLQ source");
    }

    String originalTransportId =
        safeValue(rejected.getJMSMessageID(), 128, DlqSender::isPrintableAscii);
    String messageId = safeValue(rejected.getStringProperty("NKMessageID"), 36, UUID_VALUE);
    String correlationId = safeValue(rejected.getJMSCorrelationID(), 36, UUID_VALUE);
    String layoutId = safeValue(rejected.getStringProperty("NKLayoutID"), 8, LAYOUT_VALUE);
    int deliveryCount = safeDeliveryCount(rejected);

    rejected.clearProperties();
    rejected.setJMSCorrelationID(correlationId);
    rejected.setJMSReplyTo(null);
    rejected.setJMSType(null);
    rejected.setStringProperty("_AMQ_ORIG_ADDRESS", originalDestination.address());
    rejected.setStringProperty("_AMQ_ORIG_QUEUE", originalDestination.queue());
    rejected.setStringProperty("NKOriginalTransportID", originalTransportId);
    rejected.setStringProperty("NKMessageID", messageId);
    rejected.setStringProperty("NKCorrelationID", correlationId);
    rejected.setStringProperty("NKLayoutID", layoutId);
    rejected.setIntProperty("NKDeliveryCount", deliveryCount);
    rejected.setStringProperty("NKErrorCode", fatal.errorCode());
    rejected.setStringProperty("NKDetectedBy", fatal.detectedBy().name());
    rejected.setStringProperty("NKDetectedAt", fatal.detectedAt().toString());
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
