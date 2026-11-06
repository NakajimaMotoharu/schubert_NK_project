package dev.codex.schubert.nk.api.messaging.inbound;

import dev.codex.schubert.nk.api.error.TemporaryInfrastructureException;
import dev.codex.schubert.nk.protocol.transport.BrokerTopology;
import dev.codex.schubert.nk.protocol.transport.FailedJmsIsolationException;
import dev.codex.schubert.nk.protocol.transport.UnconfirmedJmsRollbackException;
import jakarta.jms.JMSContext;
import jakarta.jms.JMSException;
import java.util.Objects;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.function.Consumer;
import java.util.function.Supplier;
import org.apache.activemq.artemis.jms.client.ActiveMQQueue;

/**
 * Single FIFO ASYNC/window0 context. Existing QuestionWorkListener owns ACK/rollback/DLQ.
 * NK-ASY-001/MSG-002; ASY001..009/MQ006..010; UI213231; SS312321342/SSC156;
 * PG-D333/PT-JMS-CORE-001..006. Outer owner signals stop before draining this context.
 */
public final class QuestionWorkConsumers implements InboundConsumerGroup {
  private final JMSContext context;
  private final Consumer<Throwable> onUnconfirmed;
  private final Object lock = new Object();
  private final AtomicBoolean halted = new AtomicBoolean();
  private boolean closed;

  private QuestionWorkConsumers(Supplier<JMSContext> factory, Consumer<Throwable> onUnconfirmed) {
    this.onUnconfirmed = onUnconfirmed;
    // BUG1537: initialize this owner/lock/flags before acquiring its only external resource.
    this.context = Objects.requireNonNull(factory.get(), "async context");
  }

  public static QuestionWorkConsumers start(
      Supplier<JMSContext> factory,
      QuestionWorkListener listener,
      Consumer<CommittedFatalInboundException> onTerminal,
      Runnable onFatal) {
    return start(factory, listener, onTerminal, onFatal, ignored -> {});
  }

  static QuestionWorkConsumers start(
      Supplier<JMSContext> factory,
      QuestionWorkListener listener,
      Consumer<CommittedFatalInboundException> onTerminal,
      Runnable onFatal,
      Consumer<Throwable> onUnconfirmed) {
    Objects.requireNonNull(factory, "async factory");
    Objects.requireNonNull(listener, "work listener");
    Objects.requireNonNull(onTerminal, "terminal signal");
    Objects.requireNonNull(onFatal, "fatal signal");
    Objects.requireNonNull(onUnconfirmed, "unconfirmed close policy");
    var rollbackAttempted = new AtomicBoolean();
    var rollbackConfirmed = new AtomicBoolean();
    Runnable attemptingRollback = () -> rollbackAttempted.set(true);
    Runnable confirmingRollback = () -> rollbackConfirmed.set(true);
    var result = new QuestionWorkConsumers(factory, onUnconfirmed);
    var context = result.context;
    try {
      context.setAutoStart(false);
      if (context.getSessionMode() != JMSContext.SESSION_TRANSACTED)
        throw new IllegalStateException("API Question consumer must be transacted");
      var consumer =
          Objects.requireNonNull(
              context.createConsumer(
                  new ActiveMQQueue(BrokerTopology.ASYNC_WORK.fullyQualifiedQueue())),
              "async consumer");
      consumer.setMessageListener(
          message -> {
            if (result.halted.get()) return;
            rollbackAttempted.set(false);
            rollbackConfirmed.set(false);
            try {
              listener.onMessage(context, message, attemptingRollback, confirmingRollback);
            } catch (CommittedFatalInboundException fatal) {
              result.halted.set(true);
              // This dedicated session serializes callbacks; halt excludes later deliveries.
              onTerminal.accept(fatal);
            } catch (FailedJmsIsolationException | UnconfirmedJmsRollbackException | Error fatal) {
              result.halted.set(true);
              if (fatal instanceof Error && rollbackAttempted.compareAndSet(false, true)) {
                try {
                  context.rollback();
                } catch (RuntimeException | Error unconfirmed) {
                  // Keep fatal stop/unconfirmed rollback distinct from committed protocol DLQ.
                }
              }
              onFatal.run();
            } catch (JMSException | RuntimeException retryable) {
              boolean fatalGraph = false;
              try {
                TemporaryInfrastructureException.preserveFatal(retryable);
              } catch (Error fatal) {
                // SSC332: API direct-fatal policy is halt/notify, not rethrow after notification.
                fatalGraph = true;
              }
              if (fatalGraph || !rollbackConfirmed.get()) {
                result.halted.set(true);
                onFatal.run();
              }
              // Only this delivery's confirmed rollback permits broker-controlled retry.
            }
          });
      context.start();
      return result;
    } catch (RuntimeException | Error failure) {
      Throwable retained = failure;
      Throwable notificationFailure = null;
      try {
        onFatal.run();
      } catch (RuntimeException | Error notification) {
        notificationFailure = notification;
        if (notification instanceof Error && !(failure instanceof Error)) {
          retained = notification;
          // Error notification and non-Error failure cannot be the same object (PG-D379).
          notification.addSuppressed(failure);
        } else if (notification != failure) failure.addSuppressed(notification);
      }
      Throwable closingFailure = null;
      try {
        result.close();
      } catch (RuntimeException | Error closing) {
        closingFailure = closing;
        if (closing instanceof Error fatal && !(retained instanceof Error)) throw fatal;
        if (closing != retained) retained.addSuppressed(closing);
      }
      if (retained instanceof Error fatal) throw fatal;
      TemporaryInfrastructureException.preserveFatal(retained);
      if (notificationFailure != null)
        TemporaryInfrastructureException.preserveFatal(notificationFailure);
      if (closingFailure != null) TemporaryInfrastructureException.preserveFatal(closingFailure);
      throw new IllegalStateException("API Question consumer startup failed", retained);
    }
  }

  public boolean ready() {
    return !halted.get();
  }

  @Override
  public void stopDelivery() {
    halted.set(true);
  }

  @Override
  public void close() {
    stopDelivery();
    synchronized (lock) {
      if (closed) return;
      try {
        context.close();
      } catch (RuntimeException | Error failure) {
        onUnconfirmed.accept(failure);
        if (failure instanceof Error fatal) throw fatal;
        throw new IllegalStateException("API Question consumer close failed", failure);
      }
      closed = true;
    }
  }
}
