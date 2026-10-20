package dev.codex.schubert.nk.api.messaging.inbound;

import dev.codex.schubert.nk.api.messaging.outbound.FatalDlqMetadata;
import dev.codex.schubert.nk.protocol.transport.BrokerTopology;
import jakarta.jms.JMSContext;
import jakarta.jms.JMSException;
import jakarta.jms.Message;
import java.time.Clock;

/**
 * Transacted FIFO listener for the single async question-work consumer.
 *
 * <p>Trace: NK-MSG-001/NK-ASY-001; RD MQ-006～010/ASY-001～009; UI 213/231; SS 312 sections 8-9 and
 * 321 section 6; PT-JMS-005/007.
 */
public final class QuestionWorkListener {
  private final TransactedEventListener delegate;

  public QuestionWorkListener(InternalEventProcessor processor, Clock clock) {
    delegate =
        new TransactedEventListener(
            BrokerTopology.ASYNC_WORK, FatalDlqMetadata.DetectedBy.API_WORK, processor, clock);
  }

  public void onMessage(JMSContext context, Message message) throws JMSException {
    delegate.onMessage(context, message);
  }

  // SSC319/PT-JMS-RB319: callback confirmation is synchronous and specific to this context.
  void onMessage(JMSContext context, Message message, Runnable attempted, Runnable confirmed)
      throws JMSException {
    delegate.onMessage(context, message, attempted, confirmed);
  }
}
