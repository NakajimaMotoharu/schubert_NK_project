package dev.codex.schubert.nk.api.messaging.inbound;

import dev.codex.schubert.nk.api.messaging.guard.GuardedJmsMessage;
import dev.codex.schubert.nk.api.messaging.guard.JmsMessageGuard;
import dev.codex.schubert.nk.api.messaging.outbound.FatalDlqMetadata;
import dev.codex.schubert.nk.api.messaging.outbound.ReplySender;
import dev.codex.schubert.nk.protocol.codec.ExpectedRoute;
import dev.codex.schubert.nk.protocol.codec.FixedWidthDecoder;
import dev.codex.schubert.nk.protocol.codec.HeaderCodec;
import dev.codex.schubert.nk.protocol.codec.PermanentProtocolException;
import dev.codex.schubert.nk.protocol.header.InteractionKind;
import dev.codex.schubert.nk.protocol.header.MessageKind;
import dev.codex.schubert.nk.protocol.layout.FixedPayload;
import dev.codex.schubert.nk.protocol.layout.WireMessage;
import dev.codex.schubert.nk.protocol.transport.BrokerTopology;
import jakarta.jms.JMSContext;
import jakarta.jms.JMSException;
import jakarta.jms.Message;
import java.time.Clock;
import java.util.Objects;
import java.util.Optional;

/**
 * Owns synchronous API request validation, dispatch, reply stage and local JMS commit.
 *
 * <p>Trace: NK-MSG-001; RD MQ-003/MQ-006/MQ-008; UI 212/231; SS 312 section 3.3 and 321 sections
 * 7-8.
 */
public final class SyncRequestListener {
  private static final Runnable UNOBSERVED_ROLLBACK = () -> {};
  private static final ExpectedRoute REQUEST_ROUTE =
      new ExpectedRoute(
          MessageKind.REQUEST,
          InteractionKind.SYNCHRONOUS,
          BrokerTopology.SYNC_REQUEST.address(),
          Optional.of(BrokerTopology.SYNC_REPLY_WEB.address()),
          true);

  private final SyncRequestProcessor processor;
  private final Clock clock;
  private final JmsMessageGuard guard = new JmsMessageGuard();
  private final FixedWidthDecoder decoder = FixedWidthDecoder.standard();
  private final ReplySender replies = new ReplySender();

  public SyncRequestListener(SyncRequestProcessor processor, Clock clock) {
    this.processor = Objects.requireNonNull(processor, "processor");
    this.clock = Objects.requireNonNull(clock, "clock");
  }

  /** Processes one delivery; no explicit {@code Message.acknowledge()} is performed. */
  public void onMessage(JMSContext context, Message message) throws JMSException {
    onMessage(context, message, UNOBSERVED_ROLLBACK, UNOBSERVED_ROLLBACK);
  }

  // SSC319/PT-JMS-RB319: synchronous non-owning phase ports, never a new transaction.
  void onMessage(JMSContext context, Message message, Runnable attempted, Runnable confirmed)
      throws JMSException {
    Objects.requireNonNull(attempted, "rollback attempt observer");
    Objects.requireNonNull(confirmed, "rollback completion observer");
    Objects.requireNonNull(context, "context");
    Objects.requireNonNull(message, "message");
    if (context.getSessionMode() != JMSContext.SESSION_TRANSACTED) {
      throw new IllegalStateException("JMS sync listener context must be transacted");
    }
    try {
      GuardedJmsMessage guarded = guard.read(message, REQUEST_ROUTE);
      // SSC151/BUG421: the closed registry admits QSB Q/A, not arbitrary A layouts.
      // Physical queue/reply-to/kind remain fixed; exact transport equality is unchanged.
      ExpectedRoute registeredRoute =
          new ExpectedRoute(
              REQUEST_ROUTE.messageKind(),
              HeaderCodec.standard().peek(guarded.body()).interactionKind(),
              REQUEST_ROUTE.destinationAddress(),
              REQUEST_ROUTE.requiredReplyToAddress(),
              REQUEST_ROUTE.expirationRequired());
      WireMessage<FixedPayload> request =
          decoder.decode(guarded.body(), guarded.metadata(), registeredRoute);
      byte[] encodedReply = Objects.requireNonNull(processor.process(request), "encoded reply");
      replies.send(context, encodedReply);
      context.commit();
    } catch (PermanentProtocolException protocolFailure) {
      InboundTransactions.isolateFatal(
          context,
          message,
          BrokerTopology.SYNC_REQUEST,
          FatalDlqMetadata.DetectedBy.API_SYNC,
          clock,
          protocolFailure,
          attempted,
          confirmed);
      throw new CommittedFatalInboundException(protocolFailure);
    } catch (JMSException | RuntimeException failure) {
      InboundTransactions.rollbackAfterFailure(context, failure, attempted, confirmed);
      throw failure;
    }
  }
}
