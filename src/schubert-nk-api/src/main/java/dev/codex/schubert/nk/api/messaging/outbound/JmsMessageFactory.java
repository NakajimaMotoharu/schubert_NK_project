package dev.codex.schubert.nk.api.messaging.outbound;

import dev.codex.schubert.nk.protocol.codec.HeaderCodec;
import dev.codex.schubert.nk.protocol.header.CommonHeader;
import dev.codex.schubert.nk.protocol.header.MessageKind;
import dev.codex.schubert.nk.protocol.transport.BrokerTopology;
import jakarta.jms.BytesMessage;
import jakarta.jms.JMSContext;
import jakarta.jms.JMSException;
import java.util.Objects;

/**
 * Creates outbound JMS messages from a complete, already encoded fixed-width wire body.
 *
 * <p>Trace: NK-MSG-001; RD MQ-003/MQ-008; UI 231 section 5; SS 311 and 321 section 8.
 */
public enum JmsMessageFactory {
  INSTANCE;

  /** Creates a registry-valid S/S or QSB S/A reply (SS321/SSC151/BUG421). */
  public BytesMessage createReply(JMSContext context, byte[] encodedBody) throws JMSException {
    Objects.requireNonNull(context, "context");
    Objects.requireNonNull(encodedBody, "encodedBody");
    CommonHeader header = HeaderCodec.standard().peek(encodedBody);
    if (encodedBody.length > BrokerTopology.SYNC_REPLY_WEB.maximumBodyLength()
        || header.messageKind() != MessageKind.RESPONSE
        || header.totalLength() != encodedBody.length) {
      throw new IllegalArgumentException("encoded outbound reply identity is inconsistent");
    }

    BytesMessage reply = context.createBytesMessage();
    reply.writeBytes(encodedBody);
    reply.setJMSCorrelationID(header.correlationId().toString());
    reply.setStringProperty("NKMessageID", header.messageId().toString());
    reply.setStringProperty("NKLayoutID", header.layoutId().value());
    reply.setStringProperty("NKProtocolVersion", "001");
    return reply;
  }
}
