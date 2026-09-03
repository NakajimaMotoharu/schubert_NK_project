package dev.codex.schubert.nk.web.messaging;

import dev.codex.schubert.nk.protocol.codec.HeaderCodec;
import dev.codex.schubert.nk.protocol.header.CommonHeader;
import dev.codex.schubert.nk.protocol.header.InteractionKind;
import dev.codex.schubert.nk.protocol.header.MessageKind;
import jakarta.jms.BytesMessage;
import jakarta.jms.DeliveryMode;
import jakarta.jms.JMSContext;
import jakarta.jms.JMSException;
import java.util.Objects;
import java.util.UUID;
import org.apache.activemq.artemis.jms.client.ActiveMQQueue;

/** Production Web request adapter for the closed Artemis request/reply topology. */
public final class ArtemisRequestSender implements JmsRequestSender {
  public static final long REQUEST_TIME_TO_LIVE_MILLIS = 5_000;
  private static final String REQUEST_FQQN = "nk.sync.request::nk.sync.request.q";
  private static final String REPLY_ADDRESS = "nk.sync.reply.web";

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
    if (header.messageKind() != MessageKind.REQUEST
        || header.interactionKind() != InteractionKind.SYNCHRONOUS
        || !header.correlationId().equals(correlationId)
        || header.totalLength() != encodedBody.length) {
      throw new IllegalArgumentException("encoded outbound request identity is inconsistent");
    }

    try (JMSContext context = Objects.requireNonNull(contexts.open(), "JMS context")) {
      if (context.getSessionMode() != JMSContext.SESSION_TRANSACTED) {
        throw new IllegalStateException("JMS request context must be transacted");
      }
      try {
        BytesMessage request = context.createBytesMessage();
        request.writeBytes(encodedBody);
        request.setJMSCorrelationID(correlationId.toString());
        request.setJMSReplyTo(new ActiveMQQueue(REPLY_ADDRESS));
        request.setStringProperty("NKMessageID", header.messageId().toString());
        request.setStringProperty("NKLayoutID", header.layoutId().value());
        request.setStringProperty("NKProtocolVersion", "001");
        context
            .createProducer()
            .setDeliveryMode(DeliveryMode.PERSISTENT)
            .setTimeToLive(REQUEST_TIME_TO_LIVE_MILLIS)
            .send(new ActiveMQQueue(REQUEST_FQQN), request);
        context.commit();
      } catch (JMSException | RuntimeException exception) {
        rollbackAfterFailure(context, exception);
        throw exception;
      }
    }
  }

  private static void rollbackAfterFailure(JMSContext context, Throwable failure) {
    try {
      context.rollback();
    } catch (RuntimeException rollbackFailure) {
      failure.addSuppressed(rollbackFailure);
    }
  }
}
