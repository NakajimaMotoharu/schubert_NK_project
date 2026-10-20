package dev.codex.schubert.nk.api.messaging.inbound;

import dev.codex.schubert.nk.protocol.transport.BrokerTopology;
import dev.codex.schubert.nk.protocol.transport.FailedJmsIsolationException;
import dev.codex.schubert.nk.protocol.transport.UnconfirmedJmsRollbackException;
import jakarta.jms.JMSConsumer;
import jakarta.jms.JMSContext;
import jakarta.jms.JMSException;
import java.util.ArrayList;
import java.util.List;
import java.util.Objects;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.locks.ReentrantLock;
import java.util.function.Consumer;
import java.util.function.Supplier;
import org.apache.activemq.artemis.jms.client.ActiveMQQueue;

/**
 * Establishes the four independent transacted API sync consumers before declaring readiness. Each
 * provider callback uses only its own JMS context; the caller owns the factory and must arrange a
 * nonzero process exit after the terminal callback. Trace: NK-MSG-001; RD MQ-003/008/010; UI 231;
 * SS 311/321 sections 6-7; PG224/PT-JMS-013.
 */
public final class SyncRequestConsumers implements AutoCloseable {
  public static final int CONCURRENCY = 4;

  private final List<JMSContext> contexts;
  private final AtomicBoolean terminal = new AtomicBoolean();
  private final AtomicBoolean halted = new AtomicBoolean();
  private final ReentrantLock closeLock = new ReentrantLock();
  private final boolean[] contextClosed = new boolean[CONCURRENCY];
  private boolean closed;

  private SyncRequestConsumers(List<JMSContext> contexts) {
    this.contexts = contexts;
  }

  /** Opens all sessions and listeners before starting delivery; partial startup is closed. */
  public static SyncRequestConsumers start(
      Supplier<JMSContext> factory,
      SyncRequestListener listener,
      Consumer<CommittedFatalInboundException> onTerminal) {
    return start(factory, listener, onTerminal, () -> {});
  }

  public static SyncRequestConsumers start(
      Supplier<JMSContext> factory,
      SyncRequestListener listener,
      Consumer<CommittedFatalInboundException> onTerminal,
      Runnable onFatal) {
    Objects.requireNonNull(factory, "factory");
    Objects.requireNonNull(listener, "listener");
    Objects.requireNonNull(onTerminal, "onTerminal");
    Objects.requireNonNull(onFatal, "fatal signal");
    List<JMSContext> opened = new ArrayList<>(CONCURRENCY);
    SyncRequestConsumers runtime = new SyncRequestConsumers(opened);
    try {
      for (int index = 0; index < CONCURRENCY; index++) {
        JMSContext context = Objects.requireNonNull(factory.get(), "JMS context");
        opened.add(context);
        context.setAutoStart(false);
        if (context.getSessionMode() != JMSContext.SESSION_TRANSACTED) {
          throw new IllegalStateException("API sync consumer must be transacted");
        }
        JMSConsumer consumer =
            Objects.requireNonNull(
                context.createConsumer(
                    new ActiveMQQueue(BrokerTopology.SYNC_REQUEST.fullyQualifiedQueue())),
                "JMS consumer");
        consumer.setMessageListener(
            message -> {
              if (runtime.halted.get()) return;
              try {
                listener.onMessage(context, message);
              } catch (CommittedFatalInboundException fatal) {
                runtime.halted.set(true);
                if (runtime.terminal.compareAndSet(false, true)) {
                  onTerminal.accept(fatal);
                }
              } catch (FailedJmsIsolationException
                  | UnconfirmedJmsRollbackException
                  | Error fatal) {
                runtime.halted.set(true);
                if (runtime.terminal.compareAndSet(false, true)) {
                  if (fatal instanceof Error) {
                    try {
                      context.rollback();
                    } catch (RuntimeException | Error unconfirmed) {
                      // Fatal/unconfirmed remains nonzero; owner closes the context, never ACKs.
                    }
                  }
                  onFatal.run();
                }
              } catch (JMSException | RuntimeException retryable) {
                // Only a confirmed rollback reaches ordinary broker-controlled redelivery.
              }
            });
      }
      for (JMSContext context : opened) {
        context.start();
      }
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
      runtime.closeAfterFailure(retained);
      if (retained instanceof Error fatal) throw fatal;
      throw new IllegalStateException("API sync consumer startup failed", retained);
    }
  }

  /** A terminal protocol error makes readiness false even before the owner exits nonzero. */
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
      Throwable failure = null;
      for (int index = 0; index < contexts.size(); index++) {
        if (contextClosed[index]) continue;
        try {
          contexts.get(index).close();
          contextClosed[index] = true;
        } catch (RuntimeException | Error closing) {
          if (failure == null || closing instanceof Error && !(failure instanceof Error)) {
            failure = closing;
          } else if (closing != failure) {
            failure.addSuppressed(closing);
          }
        }
      }
      if (failure instanceof Error fatal) throw fatal;
      if (failure != null) {
        throw new IllegalStateException("API sync consumer close failed", failure);
      }
      closed = true;
    } finally {
      closeLock.unlock();
    }
  }

  private void closeAfterFailure(Throwable startupFailure) {
    try {
      close();
    } catch (RuntimeException | Error closing) {
      if (closing instanceof Error fatal && !(startupFailure instanceof Error)) throw fatal;
      if (closing == startupFailure) return;
      startupFailure.addSuppressed(closing);
    }
  }
}
