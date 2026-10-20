package dev.codex.schubert.nk.api.messaging.inbound;

import dev.codex.schubert.nk.api.messaging.outbound.DlqSender;
import dev.codex.schubert.nk.api.messaging.outbound.FatalDlqMetadata;
import dev.codex.schubert.nk.protocol.codec.PermanentProtocolException;
import dev.codex.schubert.nk.protocol.transport.BrokerTopology;
import dev.codex.schubert.nk.protocol.transport.FailedJmsIsolationException;
import dev.codex.schubert.nk.protocol.transport.UnconfirmedJmsRollbackException;
import jakarta.jms.JMSContext;
import jakarta.jms.JMSException;
import jakarta.jms.Message;
import java.time.Clock;

/**
 * Shared API-local fatal isolation and rollback mechanics for transacted listeners.
 *
 * <p>Trace: NK-MSG-001; RD MQ-008/MQ-010; UI 231/251; SS 312 section 9 and 321 section 7;
 * PT-JMS-006/007/009.
 */
enum InboundTransactions {
  ;

  private static final DlqSender DLQ = new DlqSender();

  static void isolateFatal(
      JMSContext context,
      Message message,
      BrokerTopology originalDestination,
      FatalDlqMetadata.DetectedBy detectedBy,
      Clock clock,
      PermanentProtocolException protocolFailure) {
    try {
      FatalDlqMetadata fatal =
          new FatalDlqMetadata("PROTOCOL_INVALID", detectedBy, clock.instant());
      DLQ.sendUntrusted(context, message, originalDestination, fatal);
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

  static void rollbackAfterFailure(JMSContext context, Throwable failure) {
    try {
      context.rollback();
    } catch (RuntimeException rollbackFailure) {
      if (failure != rollbackFailure) {
        failure.addSuppressed(rollbackFailure);
      }
      throw new UnconfirmedJmsRollbackException(failure, rollbackFailure);
    }
  }
}
