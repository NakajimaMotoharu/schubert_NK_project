package dev.codex.schubert.nk.api.messaging.outbound;

import dev.codex.schubert.nk.api.messaging.guard.GuardedJmsMessage;
import dev.codex.schubert.nk.protocol.transport.BrokerTopology;
import jakarta.jms.BytesMessage;
import jakarta.jms.DeliveryMode;
import jakarta.jms.JMSContext;
import jakarta.jms.JMSException;
import java.util.Objects;
import org.apache.activemq.artemis.jms.client.ActiveMQQueue;

/**
 * Stages a body-preserving fatal message in the fixed DLQ within the receiver transaction.
 *
 * <p>Trace: NK-MSG-001; RD MQ-008/MQ-010; UI 231/251; SS 312 sections 3/9 and 321
 * sections 7/11.
 */
public final class DlqSender {
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
}
