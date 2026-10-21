package dev.codex.schubert.nk.web.messaging;

import dev.codex.schubert.nk.protocol.codec.HeaderCodec;
import dev.codex.schubert.nk.protocol.header.CommonHeader;
import dev.codex.schubert.nk.protocol.header.MessageKind;
import dev.codex.schubert.nk.protocol.transport.BrokerTopology;
import jakarta.jms.BytesMessage;
import jakarta.jms.DeliveryMode;
import jakarta.jms.JMSContext;
import jakarta.jms.JMSException;
import java.util.Objects;
import java.util.UUID;
import org.apache.activemq.artemis.jms.client.ActiveMQQueue;
import org.jspecify.annotations.Nullable;

/** Production Web request adapter for the closed Artemis request/reply topology. */
public final class ArtemisRequestSender implements JmsRequestSender {
  public static final long REQUEST_TIME_TO_LIVE_MILLIS =
      BrokerTopology.SYNC_REQUEST.timeToLiveMillis();

  private final JmsContextFactory contexts;

  public ArtemisRequestSender(JmsContextFactory contexts) {
    this.contexts = Objects.requireNonNull(contexts, "contexts");
  }

  /** Validates one complete request wire, sends it once, and commits the local JMS transaction. */
  @Override
  public void send(UUID correlationId, byte[] encodedBody) throws JMSException {
    Objects.requireNonNull(correlationId, "correlationId");
    Objects.requireNonNull(encodedBody, "encodedBody");
    CommonHeader header = HeaderCodec.standard().peek(encodedBody);
    // SSC151/BUG421: HeaderCodec validates the closed layout profile, including QSB Q/A.
    // Internal E/I and falsified A profiles fail the registry/kind boundary, not a S-only gate.
    if (header.messageKind() != MessageKind.REQUEST
        || !header.correlationId().equals(correlationId)
        || header.totalLength() != encodedBody.length) {
      throw new IllegalArgumentException("encoded outbound request identity is inconsistent");
    }

    JMSContext context = Objects.requireNonNull(contexts.open(), "JMS context");
    @Nullable Throwable primary = null;
    try {
      if (context.getSessionMode() != JMSContext.SESSION_TRANSACTED) {
        throw new IllegalStateException("JMS request context must be transacted");
      }
      try {
        BytesMessage request = context.createBytesMessage();
        request.writeBytes(encodedBody);
        request.setJMSCorrelationID(correlationId.toString());
        request.setJMSReplyTo(new ActiveMQQueue(BrokerTopology.SYNC_REPLY_WEB.address()));
        request.setStringProperty("NKMessageID", header.messageId().toString());
        request.setStringProperty("NKLayoutID", header.layoutId().value());
        request.setStringProperty("NKProtocolVersion", "001");
        context
            .createProducer()
            .setDeliveryMode(DeliveryMode.PERSISTENT)
            .setTimeToLive(REQUEST_TIME_TO_LIVE_MILLIS)
            .send(new ActiveMQQueue(BrokerTopology.SYNC_REQUEST.fullyQualifiedQueue()), request);
        context.commit();
      } catch (JMSException | RuntimeException exception) {
        rollbackAfterFailure(context, exception);
        throw exception;
      }
    } catch (JMSException | RuntimeException | Error exception) {
      primary = exception;
      throw exception;
    } finally {
      closeAfterFailure(context, primary);
    }
  }

  private static void rollbackAfterFailure(JMSContext context, Throwable failure) {
    try {
      context.rollback();
    } catch (RuntimeException rollbackFailure) {
      if (rollbackFailure != failure) {
        failure.addSuppressed(rollbackFailure);
      }
    }
  }

  private static void closeAfterFailure(JMSContext context, @Nullable Throwable primary) {
    try {
      context.close();
    } catch (RuntimeException | Error closing) {
      if (primary == null) {
        throw closing;
      }
      // SSC321/PT-IDEM-WEB321001: fatal close cannot become ordinary request failure.
      if (closing instanceof Error fatal && !(primary instanceof Error)) {
        fatal.addSuppressed(primary);
        throw fatal;
      }
      if (closing != primary) {
        primary.addSuppressed(closing);
      }
    }
  }
}
