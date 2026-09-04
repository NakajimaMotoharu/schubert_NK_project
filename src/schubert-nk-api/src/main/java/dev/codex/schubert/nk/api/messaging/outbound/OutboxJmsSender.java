package dev.codex.schubert.nk.api.messaging.outbound;

import dev.codex.schubert.nk.protocol.codec.HeaderCodec;
import dev.codex.schubert.nk.protocol.header.CommonHeader;
import dev.codex.schubert.nk.protocol.transport.BrokerTopology;
import jakarta.jms.BytesMessage;
import jakarta.jms.DeliveryMode;
import jakarta.jms.JMSContext;
import jakarta.jms.JMSException;
import java.util.Locale;
import java.util.Objects;
import org.apache.activemq.artemis.api.core.ActiveMQDuplicateIdException;
import org.apache.activemq.artemis.jms.client.ActiveMQQueue;

/** Validates and commits one persistent outbox message in a local JMS transaction. */
public final class OutboxJmsSender {
  public void send(TransactedJmsContextProvider contextProvider, OutboxEntry entry)
      throws OutboxSendException {
    Objects.requireNonNull(contextProvider, "contextProvider");
    Objects.requireNonNull(entry, "entry");
    validateWireIdentity(entry);
    try (JMSContext context = Objects.requireNonNull(contextProvider.open(), "JMS context")) {
      if (context.getSessionMode() != JMSContext.SESSION_TRANSACTED) {
        throw new OutboxSendException("outbox JMS context is not transacted");
      }
      try {
        stage(context, entry);
      } catch (JMSException | RuntimeException exception) {
        rollback(context, exception);
        throw new OutboxSendException("outbox JMS send was not confirmed", exception);
      }
      try {
        context.commit();
      } catch (RuntimeException exception) {
        rollback(context, exception);
        if (!isDuplicateConfirmation(exception)) {
          throw new OutboxSendException("outbox JMS commit was not confirmed", exception);
        }
      }
    } catch (OutboxSendException exception) {
      throw exception;
    } catch (RuntimeException exception) {
      throw new OutboxSendException("outbox JMS context lifecycle failed", exception);
    }
  }

  private static void stage(JMSContext context, OutboxEntry entry) throws JMSException {
    BytesMessage message = context.createBytesMessage();
    message.writeBytes(entry.body());
    message.setJMSCorrelationID(entry.correlationId().toString());
    message.setStringProperty("NKMessageID", entry.messageId().toString());
    message.setStringProperty("NKLayoutID", entry.layoutId());
    message.setStringProperty("NKProtocolVersion", entry.layoutVersion());
    message.setStringProperty("_AMQ_DUPL_ID", entry.messageId().toString());
    BrokerTopology target = target(entry.destination());
    context
        .createProducer()
        .setDeliveryMode(DeliveryMode.PERSISTENT)
        .setTimeToLive(target.timeToLiveMillis())
        .send(new ActiveMQQueue(target.fullyQualifiedQueue()), message);
  }

  static void validateWireIdentity(OutboxEntry entry) {
    final CommonHeader header;
    try {
      header = HeaderCodec.standard().peek(entry.body());
    } catch (RuntimeException exception) {
      throw new OutboxIntegrityException("outbox wire body failed fixed-width validation", exception);
    }
    BrokerTopology target = target(entry.destination());
    if (!header.messageId().equals(entry.messageId())
        || !header.correlationId().equals(entry.correlationId())
        || !header.layoutId().value().equals(entry.layoutId())
        || !String.format(Locale.ROOT, "%03d", header.layoutVersion()).equals(entry.layoutVersion())
        || header.totalLength() != entry.body().length
        || entry.body().length > target.maximumBodyLength()
        || !entry.layoutId().equals("QWKREQ01")) {
      throw new OutboxIntegrityException("outbox row and wire identity disagree");
    }
  }

  private static BrokerTopology target(OutboxDestination destination) {
    return switch (destination) {
      case ASYNC_WORK -> BrokerTopology.ASYNC_WORK;
      case DLQ -> BrokerTopology.DEAD_LETTER;
    };
  }

  private static void rollback(JMSContext context, Throwable failure) {
    try {
      context.rollback();
    } catch (RuntimeException rollbackFailure) {
      failure.addSuppressed(rollbackFailure);
    }
  }

  static boolean isDuplicateConfirmation(Throwable failure) {
    Throwable candidate = failure;
    while (candidate != null) {
      if (candidate instanceof ActiveMQDuplicateIdException) {
        return true;
      }
      if (candidate instanceof JMSException jmsException
          && jmsException.getLinkedException() != null
          && jmsException.getLinkedException() != candidate) {
        candidate = jmsException.getLinkedException();
      } else if (candidate.getCause() != candidate) {
        candidate = candidate.getCause();
      } else {
        candidate = null;
      }
    }
    return false;
  }
}
