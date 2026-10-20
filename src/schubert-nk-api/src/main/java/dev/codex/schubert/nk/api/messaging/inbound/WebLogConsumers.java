package dev.codex.schubert.nk.api.messaging.inbound;

import dev.codex.schubert.nk.protocol.transport.BrokerTopology;
import dev.codex.schubert.nk.protocol.transport.FailedJmsIsolationException;
import dev.codex.schubert.nk.protocol.transport.UnconfirmedJmsRollbackException;
import jakarta.jms.JMSConsumer;
import jakarta.jms.JMSContext;
import jakarta.jms.JMSException;
import java.util.Objects;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.locks.ReentrantLock;
import java.util.function.Consumer;
import java.util.function.Supplier;
import org.apache.activemq.artemis.jms.client.ActiveMQQueue;

/**
 * One dedicated, transacted API consumer for Web request-log projection. The owning process must
 * exit nonzero after a committed fatal event and close this runtime before broker shutdown. Trace:
 * NK-MSG-001/002; RD MQ-006/008/010,MON-003/005; UI212/231/251; SS312 section 11,321 sections 6-10;
 * PG228/PT-JMS-015.
 */
public final class WebLogConsumers implements AutoCloseable {
  private final JMSContext context;
  private final AtomicBoolean terminal = new AtomicBoolean();
  private final AtomicBoolean halted = new AtomicBoolean();
  private final ReentrantLock closeLock = new ReentrantLock();
  private boolean closed;

  private WebLogConsumers(Supplier<JMSContext> factory) {
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
    Objects.requireNonNull(factory, "factory");
    Objects.requireNonNull(listener, "listener");
    Objects.requireNonNull(onTerminal, "onTerminal");
    Objects.requireNonNull(onFatal, "fatal signal");
    WebLogConsumers runtime = new WebLogConsumers(factory);
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
            try {
              listener.onMessage(opened, message);
            } catch (CommittedFatalInboundException fatal) {
              runtime.halted.set(true);
              // This dedicated session serializes callbacks; halt excludes later deliveries.
              runtime.terminal.set(true);
              onTerminal.accept(fatal);
            } catch (FailedJmsIsolationException | UnconfirmedJmsRollbackException | Error fatal) {
              runtime.halted.set(true);
              runtime.terminal.set(true);
              if (fatal instanceof Error) {
                try {
                  opened.rollback();
                } catch (RuntimeException | Error unconfirmed) {
                  // Stop remains fatal/unconfirmed; no ACK and no provider text escapes.
                }
              }
              onFatal.run();
            } catch (JMSException | RuntimeException retryable) {
              // Confirmed rollback only; Artemis owns redelivery and delivery-count policy.
            }
          });
      opened.start();
      return runtime;
    } catch (RuntimeException | Error failure) {
      Throwable retained = failure;
      try {
        onFatal.run();
      } catch (RuntimeException | Error notification) {
        if (notification instanceof Error && !(failure instanceof Error)) {
          retained = notification;
          // Error notification and non-Error failure cannot be the same object (PG-D379).
          notification.addSuppressed(failure);
        } else if (notification != failure) failure.addSuppressed(notification);
      }
      try {
        runtime.close();
      } catch (RuntimeException | Error closing) {
        if (closing instanceof Error fatal && !(retained instanceof Error)) throw fatal;
        if (closing != retained) retained.addSuppressed(closing);
      }
      if (retained instanceof Error fatal) throw fatal;
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
  public void close() {
    halted.set(true);
    closeLock.lock();
    try {
      if (closed) return;
      try {
        context.close();
      } catch (RuntimeException failure) {
        throw new IllegalStateException("API Web log consumer close failed", failure);
      }
      closed = true;
    } finally {
      closeLock.unlock();
    }
  }
}
