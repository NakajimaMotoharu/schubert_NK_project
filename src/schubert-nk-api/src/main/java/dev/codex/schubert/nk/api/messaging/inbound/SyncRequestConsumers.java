package dev.codex.schubert.nk.api.messaging.inbound;

import dev.codex.schubert.nk.api.error.TemporaryInfrastructureException;
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
import java.util.function.Consumer;
import java.util.function.Supplier;
import org.apache.activemq.artemis.jms.client.ActiveMQQueue;
import org.jspecify.annotations.Nullable;

/**
 * Establishes the four independent transacted API sync consumers before declaring readiness. Each
 * provider callback uses only its own JMS context; the caller owns the factory and must arrange a
 * nonzero process exit after the terminal callback. Trace: NK-MSG-001; RD MQ-003/008/010; UI 231;
 * SS 311/321 sections 6-7; PG224/PT-JMS-013.
 */
public final class SyncRequestConsumers implements InboundConsumerGroup {
  public static final int CONCURRENCY = 4;

  private final List<JMSContext> contexts;
  private final Consumer<Throwable> onUnconfirmed;
  private final AtomicBoolean terminal = new AtomicBoolean();
  private final AtomicBoolean halted = new AtomicBoolean();
  private final Object closeLock = new Object();
  private final boolean[] contextClosed = new boolean[CONCURRENCY];
  // SSC333: allocated before acquisition; private per-close scratch, cleared even on failure.
  private final @Nullable Throwable[] closeFailures = new Throwable[CONCURRENCY];
  private boolean closed;

  private SyncRequestConsumers(List<JMSContext> contexts, Consumer<Throwable> onUnconfirmed) {
    this.contexts = contexts;
    this.onUnconfirmed = onUnconfirmed;
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
    return start(factory, listener, onTerminal, onFatal, ignored -> {});
  }

  // SSC316: only the complete native parent chooses true; ordinary component contracts stay false.
  static SyncRequestConsumers start(
      Supplier<JMSContext> factory,
      SyncRequestListener listener,
      Consumer<CommittedFatalInboundException> onTerminal,
      Runnable onFatal,
      Consumer<Throwable> onUnconfirmed) {
    Objects.requireNonNull(factory, "factory");
    Objects.requireNonNull(listener, "listener");
    Objects.requireNonNull(onTerminal, "onTerminal");
    Objects.requireNonNull(onFatal, "fatal signal");
    Objects.requireNonNull(onUnconfirmed, "unconfirmed close policy");
    List<JMSContext> opened = new ArrayList<>(CONCURRENCY);
    SyncRequestConsumers runtime = new SyncRequestConsumers(opened, onUnconfirmed);
    try {
      for (int index = 0; index < CONCURRENCY; index++) {
        // SSC319: distinct per-context state/ports exist before its factory acquires a context.
        var rollbackAttempted = new AtomicBoolean();
        var rollbackConfirmed = new AtomicBoolean();
        Runnable attemptingRollback = () -> rollbackAttempted.set(true);
        Runnable confirmingRollback = () -> rollbackConfirmed.set(true);
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
              rollbackAttempted.set(false);
              rollbackConfirmed.set(false);
              try {
                listener.onMessage(context, message, attemptingRollback, confirmingRollback);
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
                  if (fatal instanceof Error && rollbackAttempted.compareAndSet(false, true)) {
                    try {
                      context.rollback();
                    } catch (RuntimeException | Error unconfirmed) {
                      // Fatal/unconfirmed remains nonzero; owner closes the context, never ACKs.
                    }
                  }
                  onFatal.run();
                }
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
                  if (runtime.terminal.compareAndSet(false, true)) onFatal.run();
                }
                // Only this delivery's confirmed rollback permits broker-controlled retry.
              }
            });
      }
      for (JMSContext context : opened) {
        context.start();
      }
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
      Throwable closingFailure = runtime.closeAfterFailure(retained);
      if (retained instanceof Error fatal) throw fatal;
      if (closingFailure instanceof Error fatal) throw fatal;
      TemporaryInfrastructureException.preserveFatal(retained);
      if (notificationFailure != null)
        TemporaryInfrastructureException.preserveFatal(notificationFailure);
      if (closingFailure != null) TemporaryInfrastructureException.preserveFatal(closingFailure);
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
  public void stopDelivery() {
    halted.set(true);
  }

  @Override
  public void close() {
    stopDelivery();
    synchronized (closeLock) {
      if (closed) return;
      try {
        Throwable failure = null;
        for (int index = 0; index < contexts.size(); index++) {
          if (contextClosed[index]) continue;
          try {
            contexts.get(index).close();
            contextClosed[index] = true;
          } catch (RuntimeException | Error closing) {
            closeFailures[index] = closing;
            if (failure == null || closing instanceof Error && !(failure instanceof Error)) {
              failure = closing;
            } else if (closing != failure) {
              failure.addSuppressed(closing);
            }
          }
        }
        if (failure != null) onUnconfirmed.accept(failure);
        if (failure instanceof Error fatal) throw fatal;
        if (failure != null) {
          // No graph accessor runs until all required close attempts/UNKNOWN handoff finish.
          TemporaryInfrastructureException.preserveFatal(failure);
          for (Throwable closing : closeFailures) {
            if (closing != null) TemporaryInfrastructureException.preserveFatal(closing);
          }
          throw new IllegalStateException("API sync consumer close failed", failure);
        }
        closed = true;
      } finally {
        java.util.Arrays.fill(closeFailures, null);
      }
    }
  }

  private @Nullable Throwable closeAfterFailure(Throwable startupFailure) {
    try {
      close();
    } catch (RuntimeException | Error closing) {
      if (closing instanceof Error fatal && !(startupFailure instanceof Error)) return fatal;
      if (closing != startupFailure) startupFailure.addSuppressed(closing);
      return closing;
    }
    return null;
  }
}
