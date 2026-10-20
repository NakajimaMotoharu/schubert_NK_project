package dev.codex.schubert.nk.web.messaging;

import dev.codex.schubert.nk.protocol.codec.PermanentProtocolException;
import dev.codex.schubert.nk.protocol.transport.FailedJmsIsolationException;
import dev.codex.schubert.nk.protocol.transport.UnconfirmedJmsRollbackException;
import jakarta.jms.JMSContext;
import jakarta.jms.JMSException;
import jakarta.jms.Message;
import java.util.Objects;

/**
 * Validates and correlates one reply under a caller-owned, transacted consumer context.
 *
 * <p>Trace: NK-MSG-001; RD MQ-004/MQ-005/MQ-008; UI 212/231; SS 312 section 3.2 and 321 sections
 * 7/9.
 */
public final class ArtemisReplyConsumer {
  private final JmsRequestReplyClient client;
  private final JmsReplyDecoder decoder;
  private final ArtemisReplyDlqSender fatalSender;

  public ArtemisReplyConsumer(
      JmsRequestReplyClient client, JmsReplyDecoder decoder, ArtemisReplyDlqSender fatalSender) {
    this.client = Objects.requireNonNull(client, "client");
    this.decoder = Objects.requireNonNull(decoder, "decoder");
    this.fatalSender = Objects.requireNonNull(fatalSender, "fatalSender");
  }

  /** Returns true for an active waiter and false for a valid late reply. */
  public boolean onMessage(JMSContext context, Message message) throws JMSException {
    Objects.requireNonNull(context, "context");
    Objects.requireNonNull(message, "message");
    if (context.getSessionMode() != JMSContext.SESSION_TRANSACTED) {
      throw new IllegalStateException("JMS reply consumer context must be transacted");
    }
    try {
      ValidatedReply reply = decoder.decode(message);
      boolean completed = client.onReply(reply.correlationId(), reply.body());
      context.commit();
      return completed;
    } catch (PermanentProtocolException protocolFailure) {
      isolateFatal(context, message, protocolFailure);
      throw new CommittedFatalReplyException(protocolFailure);
    } catch (JMSException | RuntimeException failure) {
      rollbackAfterFailure(context, failure);
      throw failure;
    }
  }

  private void isolateFatal(
      JMSContext context, Message message, PermanentProtocolException protocolFailure) {
    try {
      fatalSender.send(context, message);
      context.commit();
    } catch (JMSException | RuntimeException isolationFailure) {
      if (isolationFailure != protocolFailure) {
        isolationFailure.addSuppressed(protocolFailure);
      }
      try {
        rollbackAfterFailure(context, isolationFailure);
      } catch (UnconfirmedJmsRollbackException unconfirmed) {
        throw new FailedJmsIsolationException(unconfirmed, protocolFailure);
      }
      throw new FailedJmsIsolationException(isolationFailure, protocolFailure);
    }
  }

  private static void rollbackAfterFailure(JMSContext context, Throwable failure) {
    try {
      context.rollback();
    } catch (RuntimeException rollbackFailure) {
      if (rollbackFailure != failure) {
        failure.addSuppressed(rollbackFailure);
      }
      throw new UnconfirmedJmsRollbackException(failure, rollbackFailure);
    }
  }
}
