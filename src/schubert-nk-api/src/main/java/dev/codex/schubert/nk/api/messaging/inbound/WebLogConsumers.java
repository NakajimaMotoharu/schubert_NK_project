package dev.codex.schubert.nk.api.messaging.inbound;

import dev.codex.schubert.nk.api.error.TemporaryInfrastructureException;
import dev.codex.schubert.nk.protocol.transport.BrokerTopology;
import dev.codex.schubert.nk.protocol.transport.FailedJmsIsolationException;
import dev.codex.schubert.nk.protocol.transport.UnconfirmedJmsRollbackException;
import jakarta.jms.JMSConsumer;
import jakarta.jms.JMSContext;
import jakarta.jms.JMSException;
import java.util.Objects;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.function.Consumer;
import java.util.function.Supplier;
import org.apache.activemq.artemis.jms.client.ActiveMQQueue;

/**
 * One dedicated, transacted API consumer for Web request-log projection. The owning process must
 * exit nonzero after a committed fatal event and close this runtime before broker shutdown. Trace:
 * NK-MSG-001/002; RD MQ-006/008/010,MON-003/005; UI212/231/251; SS312 section 11,321 sections 6-10;
 * PG228/PT-JMS-015.
 */
public final class WebLogConsumers implements InboundConsumerGroup {
  private final JMSContext context;
  private final Consumer<Throwable> onUnconfirmed;
  private final AtomicBoolean terminal = new AtomicBoolean();
  private final AtomicBoolean halted = new AtomicBoolean();
  private final Object closeLock = new Object();
  private boolean closed;

  private WebLogConsumers(Supplier<JMSContext> factory, Consumer<Throwable> onUnconfirmed) {
    this.onUnconfirmed = onUnconfirmed;
    // BUG1537: all state allocation precedes acquisition; only final storage follows it.
    this.context = Objects.requireNonNull(factory.get(), "JMS context");
  }

  /** Installs the callback before delivery starts; failed startup always releases its session. */
  public static WebLogConsumers start(
      Supplier<JMSContext> factory,
      WebLogListener listener,
      Consumer<CommittedFatalInboundException> onTerminal) {
    return start(factory, listener, onTerminal, () -> {});
  }

  public static WebLogConsumers start(
      Supplier<JMSContext> factory,
      WebLogListener listener,
      Consumer<CommittedFatalInboundException> onTerminal,
      Runnable onFatal) {
    return start(factory, listener, onTerminal, onFatal, ignored -> {});
  }

  static WebLogConsumers start(
      Supplier<JMSContext> factory,
      WebLogListener listener,
      Consumer<CommittedFatalInboundException> onTerminal,
      Runnable onFatal,
      Consumer<Throwable> onUnconfirmed) {
    Objects.requireNonNull(factory, "factory");
    Objects.requireNonNull(listener, "listener");
    Objects.requireNonNull(onTerminal, "onTerminal");
    Objects.requireNonNull(onFatal, "fatal signal");
    Objects.requireNonNull(onUnconfirmed, "unconfirmed close policy");
    var rollbackAttempted = new AtomicBoolean();
    var rollbackConfirmed = new AtomicBoolean();
    Runnable attemptingRollback = () -> rollbackAttempted.set(true);
    Runnable confirmingRollback = () -> rollbackConfirmed.set(true);
    WebLogConsumers runtime = new WebLogConsumers(factory, onUnconfirmed);
    JMSContext opened = runtime.context;
    try {
      opened.setAutoStart(false);
      if (opened.getSessionMode() != JMSContext.SESSION_TRANSACTED) {
        throw new IllegalStateException("API Web log consumer must be transacted");
      }
      JMSConsumer consumer =
          Objects.requireNonNull(
              opened.createConsumer(
                  new ActiveMQQueue(BrokerTopology.WEB_LOG.fullyQualifiedQueue())),
              "JMS consumer");
      consumer.setMessageListener(
          message -> {
            if (runtime.halted.get()) return;
            rollbackAttempted.set(false);
            rollbackConfirmed.set(false);
            try {
              listener.onMessage(opened, message, attemptingRollback, confirmingRollback);
            } catch (CommittedFatalInboundException fatal) {
              runtime.halted.set(true);
              // This dedicated session serializes callbacks; halt excludes later deliveries.
              runtime.terminal.set(true);
              onTerminal.accept(fatal);
            } catch (FailedJmsIsolationException | UnconfirmedJmsRollbackException | Error fatal) {
              runtime.halted.set(true);
              runtime.terminal.set(true);
              if (fatal instanceof Error && rollbackAttempted.compareAndSet(false, true)) {
                try {
                  opened.rollback();
                } catch (RuntimeException | Error unconfirmed) {
                  // Stop remains fatal/unconfirmed; no ACK and no provider text escapes.
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
                runtime.halted.set(true);
                runtime.terminal.set(true);
                onFatal.run();
              }
              // Only this delivery's confirmed rollback permits broker-controlled retry.
            }
          });
      opened.start();
      return runtime;
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
        runtime.close();
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
      throw new IllegalStateException("API Web log consumer startup failed", retained);
    }
  }

  /** Liveness of this one Queue, not full API broker-management readiness. */
  public boolean ready() {
    return !halted.get();
  }

  public boolean terminalFailureObserved() {
    return terminal.get();
  }

  @Override
  public void stopDelivery() {
    halted.set(true);
  }

  @Override
  public void close() {
    stopDelivery();
    synchronized (closeLock) {
      if (closed) return;
      try {
        context.close();
      } catch (RuntimeException | Error failure) {
        onUnconfirmed.accept(failure);
        if (failure instanceof Error fatal) throw fatal;
        throw new IllegalStateException("API Web log consumer close failed", failure);
      }
      closed = true;
    }
  }
}
