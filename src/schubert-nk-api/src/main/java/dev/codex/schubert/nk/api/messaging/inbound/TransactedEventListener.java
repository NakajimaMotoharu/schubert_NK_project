package dev.codex.schubert.nk.api.messaging.inbound;

import dev.codex.schubert.nk.api.messaging.guard.GuardedJmsMessage;
import dev.codex.schubert.nk.api.messaging.guard.JmsMessageGuard;
import dev.codex.schubert.nk.api.messaging.outbound.FatalDlqMetadata;
import dev.codex.schubert.nk.protocol.codec.ExpectedRoute;
import dev.codex.schubert.nk.protocol.codec.FixedWidthDecoder;
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
 * Common transaction boundary for the single-threaded internal event consumers.
 *
 * <p>Trace: NK-MSG-001; RD MQ-006～010; UI 213/231; SS 312 sections 8-9 and 321 sections 6-8;
 * PT-JMS-005～007/009.
 */
final class TransactedEventListener {
  private final BrokerTopology destination;
  private final FatalDlqMetadata.DetectedBy detectedBy;
  private final InternalEventProcessor processor;
  private final Clock clock;
  private final ExpectedRoute route;
  private final JmsMessageGuard guard = new JmsMessageGuard();
  private final FixedWidthDecoder decoder = FixedWidthDecoder.standard();

  TransactedEventListener(
      BrokerTopology destination,
      FatalDlqMetadata.DetectedBy detectedBy,
      InternalEventProcessor processor,
      Clock clock) {
    this.destination = Objects.requireNonNull(destination, "destination");
    this.detectedBy = Objects.requireNonNull(detectedBy, "detectedBy");
    this.processor = Objects.requireNonNull(processor, "processor");
    this.clock = Objects.requireNonNull(clock, "clock");
    if (destination != BrokerTopology.ASYNC_WORK && destination != BrokerTopology.WEB_LOG) {
      throw new IllegalArgumentException("event listener destination is not an application event");
    }
    route =
        new ExpectedRoute(
            MessageKind.EVENT,
            InteractionKind.INTERNAL,
            destination.address(),
            Optional.empty(),
            false);
  }

  void onMessage(JMSContext context, Message message) throws JMSException {
    Objects.requireNonNull(context, "context");
    Objects.requireNonNull(message, "message");
    if (context.getSessionMode() != JMSContext.SESSION_TRANSACTED) {
      throw new IllegalStateException("JMS event listener context must be transacted");
    }
    try {
      GuardedJmsMessage guarded = guard.read(message, route);
      WireMessage<FixedPayload> event = decoder.decode(guarded.body(), guarded.metadata(), route);
      processor.process(event);
      context.commit();
    } catch (PermanentProtocolException protocolFailure) {
      InboundTransactions.isolateFatal(
          context, message, destination, detectedBy, clock, protocolFailure);
      throw new CommittedFatalInboundException(protocolFailure);
    } catch (JMSException | RuntimeException failure) {
      InboundTransactions.rollbackAfterFailure(context, failure);
      throw failure;
    }
  }
}
