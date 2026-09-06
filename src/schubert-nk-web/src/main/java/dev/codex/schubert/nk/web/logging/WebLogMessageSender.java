package dev.codex.schubert.nk.web.logging;

import dev.codex.schubert.nk.protocol.transport.BrokerTopology;
import dev.codex.schubert.nk.web.messaging.JmsContextFactory;
import jakarta.jms.BytesMessage;
import jakarta.jms.DeliveryMode;
import jakarta.jms.JMSContext;
import jakarta.jms.JMSException;
import java.util.ArrayDeque;
import java.util.Arrays;
import java.util.Collections;
import java.util.IdentityHashMap;
import java.util.Objects;
import java.util.Set;
import org.apache.activemq.artemis.api.core.ActiveMQDuplicateIdException;
import org.apache.activemq.artemis.jms.client.ActiveMQQueue;

/**
 * Authenticates Web-local storage before committing one persistent WLGEVT01 message.
 * Trace: NK-MSG-002; RD MON-003/MQ-008; UI 231/242; SS 324 section 9, SSC-007;
 * PT-IDEM-012, YKT-009. Does not open a database transaction or access API keys/tables.
 */
public final class WebLogMessageSender {
  private final WebLogPayloadCodec codec;
  private final JmsContextFactory contexts;

  public WebLogMessageSender(WebLogPayloadCodec codec, JmsContextFactory contexts) {
    this.codec = Objects.requireNonNull(codec, "codec");
    this.contexts = Objects.requireNonNull(contexts, "contexts");
  }

  /** Current/previous key authentication and full wire decode precede JMS context acquisition. */
  public void send(ClaimedWebLog row) throws WebLogSendException {
    Objects.requireNonNull(row, "row");
    byte[] wire = codec.decrypt(row.identity(), row.payload());
    try (JMSContext context = Objects.requireNonNull(contexts.open(), "JMS context")) {
      if (context.getSessionMode() != JMSContext.SESSION_TRANSACTED) {
        throw new WebLogSendException("web log JMS context is not transacted");
      }
      try {
        BytesMessage message = context.createBytesMessage();
        message.writeBytes(wire);
        message.setJMSCorrelationID(row.identity().correlationId().toString());
        message.setStringProperty("NKMessageID", row.identity().messageId().toString());
        message.setStringProperty("NKLayoutID", "WLGEVT01");
        message.setStringProperty("NKProtocolVersion", "001");
        message.setStringProperty("_AMQ_DUPL_ID", row.identity().messageId().toString());
        context.createProducer().setDeliveryMode(DeliveryMode.PERSISTENT).setTimeToLive(0)
            .send(new ActiveMQQueue(BrokerTopology.WEB_LOG.fullyQualifiedQueue()), message);
      } catch (JMSException | RuntimeException failure) {
        rollback(context, failure);
        throw new WebLogSendException("web log JMS send was not confirmed", failure);
      }
      try {
        context.commit();
      } catch (RuntimeException failure) {
        rollback(context, failure);
        if (!duplicateConfirmed(failure)) {
          throw new WebLogSendException("web log JMS commit was not confirmed", failure);
        }
      }
    } catch (WebLogSendException failure) {
      throw failure;
    } catch (RuntimeException failure) {
      throw new WebLogSendException("web log JMS lifecycle failed", failure);
    } finally {
      Arrays.fill(wire, (byte) 0);
    }
  }

  private static void rollback(JMSContext context, Throwable failure) {
    try {
      context.rollback();
    } catch (RuntimeException rollbackFailure) {
      failure.addSuppressed(rollbackFailure);
    }
  }

  /** Handles the provider's cause/linked-exception graph, including cycles, without text matching. */
  static boolean duplicateConfirmed(Throwable failure) {
    Objects.requireNonNull(failure, "failure");
    ArrayDeque<Throwable> pending = new ArrayDeque<>();
    Set<Throwable> seen = Collections.newSetFromMap(new IdentityHashMap<>());
    pending.add(failure);
    while (!pending.isEmpty()) {
      Throwable candidate = pending.remove();
      if (!seen.add(candidate)) {
        continue;
      }
      if (candidate instanceof ActiveMQDuplicateIdException) {
        return true;
      }
      Throwable cause = candidate.getCause();
      if (cause != null) {
        pending.add(cause);
      }
      if (candidate instanceof JMSException jms && jms.getLinkedException() != null) {
        pending.add(jms.getLinkedException());
      }
    }
    return false;
  }
}
