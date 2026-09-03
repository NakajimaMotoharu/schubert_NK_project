package dev.codex.schubert.nk.api.messaging.outbound;

import dev.codex.schubert.nk.protocol.transport.BrokerTopology;
import jakarta.jms.BytesMessage;
import jakarta.jms.DeliveryMode;
import jakarta.jms.JMSContext;
import jakarta.jms.JMSException;
import java.util.Objects;
import org.apache.activemq.artemis.jms.client.ActiveMQQueue;

/**
 * Sends a reply in the listener-owned local JMS transaction without committing it.
 *
 * <p>Trace: NK-MSG-001; RD MQ-003/MQ-008; UI 212/231; SS 312 section 3 and 321
 * sections 7-8.
 */
public final class ReplySender {
  /** Stages one persistent reply; the listener commits it together with the request ACK. */
  public void send(JMSContext context, byte[] encodedReply) throws JMSException {
    Objects.requireNonNull(context, "context");
    Objects.requireNonNull(encodedReply, "encodedReply");
    if (context.getSessionMode() != JMSContext.SESSION_TRANSACTED) {
      throw new IllegalStateException("JMS reply context must be transacted");
    }
    BytesMessage reply = JmsMessageFactory.INSTANCE.createReply(context, encodedReply);
    context
        .createProducer()
        .setDeliveryMode(DeliveryMode.PERSISTENT)
        .setTimeToLive(BrokerTopology.SYNC_REPLY_WEB.timeToLiveMillis())
        .send(new ActiveMQQueue(BrokerTopology.SYNC_REPLY_WEB.fullyQualifiedQueue()), reply);
  }
}
