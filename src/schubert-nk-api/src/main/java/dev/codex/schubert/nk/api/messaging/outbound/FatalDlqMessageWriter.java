package dev.codex.schubert.nk.api.messaging.outbound;

import dev.codex.schubert.nk.api.messaging.guard.GuardedJmsMessage;
import dev.codex.schubert.nk.protocol.codec.TransportMetadata;
import jakarta.jms.BytesMessage;
import jakarta.jms.JMSContext;
import jakarta.jms.JMSException;
import java.util.Objects;

/** Creates the body-preserving, bounded metadata message for a fatal DLQ transaction. */
public enum FatalDlqMessageWriter {
  INSTANCE;

  /** Caller sends the result persistently to the fixed DLQ in the same transacted session. */
  public BytesMessage create(
      JMSContext context, GuardedJmsMessage rejected, FatalDlqMetadata fatal) throws JMSException {
    Objects.requireNonNull(context, "context");
    Objects.requireNonNull(rejected, "rejected");
    Objects.requireNonNull(fatal, "fatal");
    TransportMetadata source = rejected.metadata();
    String originalTransportId = boundedTransportId(source.transportMessageId());

    BytesMessage dlq = context.createBytesMessage();
    dlq.writeBytes(rejected.body());
    dlq.setJMSCorrelationID(source.correlationId().toString());
    dlq.setStringProperty("_AMQ_ORIG_ADDRESS", source.destinationAddress());
    dlq.setStringProperty("_AMQ_ORIG_QUEUE", source.destinationAddress() + ".q");
    dlq.setStringProperty("NKOriginalTransportID", originalTransportId);
    dlq.setStringProperty("NKMessageID", source.nkMessageId().toString());
    dlq.setStringProperty("NKCorrelationID", source.correlationId().toString());
    dlq.setStringProperty("NKLayoutID", source.nkLayoutId().toString());
    dlq.setIntProperty("NKDeliveryCount", source.deliveryCount());
    dlq.setStringProperty("NKErrorCode", fatal.errorCode());
    dlq.setStringProperty("NKDetectedBy", fatal.detectedBy().name());
    dlq.setStringProperty("NKDetectedAt", fatal.detectedAt().toString());
    return dlq;
  }

  private static String boundedTransportId(String value) {
    if (value.length() > 128
        || value.chars().anyMatch(character -> character < 0x20 || character > 0x7e)) {
      throw new IllegalArgumentException("original transport ID is outside its bounded format");
    }
    return value;
  }
}
