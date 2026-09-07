package dev.codex.schubert.nk.api.messaging.inbound;

import dev.codex.schubert.nk.api.messaging.outbound.FatalDlqMetadata;
import dev.codex.schubert.nk.protocol.transport.BrokerTopology;
import jakarta.jms.JMSContext;
import jakarta.jms.JMSException;
import jakarta.jms.Message;
import java.time.Clock;

/**
 * Transacted single-consumer listener for best-effort Web request log projection.
 *
 * <p>Trace: NK-MSG-001; RD MQ-006～010/MON-005; UI 212/231/251; SS 312 section 11 and 321 section 6;
 * PT-JMS-005/007.
 */
public final class WebLogListener {
  private final TransactedEventListener delegate;

  public WebLogListener(InternalEventProcessor processor, Clock clock) {
    delegate =
        new TransactedEventListener(
            BrokerTopology.WEB_LOG, FatalDlqMetadata.DetectedBy.API_WEB_LOG, processor, clock);
  }

  public void onMessage(JMSContext context, Message message) throws JMSException {
    delegate.onMessage(context, message);
  }
}
