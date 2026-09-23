package dev.codex.schubert.nk.api.messaging.inbound;

import dev.codex.schubert.nk.protocol.transport.BrokerTopology;
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
  private volatile boolean closed;

  private SyncRequestConsumers(List<JMSContext> contexts) {
    this.contexts = contexts;
  }

  /** Opens all sessions and listeners before starting delivery; partial startup is closed. */
  public static SyncRequestConsumers start(
      Supplier<JMSContext> factory,
      SyncRequestListener listener,
      Consumer<CommittedFatalInboundException> onTerminal) {
    Objects.requireNonNull(factory, "factory");
    Objects.requireNonNull(listener, "listener");
    Objects.requireNonNull(onTerminal, "onTerminal");
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
              try {
                listener.onMessage(context, message);
              } catch (CommittedFatalInboundException fatal) {
                if (runtime.terminal.compareAndSet(false, true)) {
                  onTerminal.accept(fatal);
                }
              } catch (JMSException | RuntimeException retryable) {
                // SyncRequestListener has rolled back. Broker redelivery owns the retry schedule.
              }
            });
      }
      for (JMSContext context : opened) {
        context.start();
      }
      return runtime;
    } catch (RuntimeException failure) {
      runtime.closeAfterFailure(failure);
      throw failure;
    }
  }

  /** A terminal protocol error makes readiness false even before the owner exits nonzero. */
  public boolean ready() {
    return !closed && !terminal.get();
  }

  public boolean terminalFailureObserved() {
    return terminal.get();
  }

  @Override
  public void close() {
    if (closed) {
      return;
    }
    closed = true;
    RuntimeException failure = null;
    for (JMSContext context : contexts) {
      try {
        context.close();
      } catch (RuntimeException closing) {
        if (failure == null) {
          failure = closing;
        } else {
          failure.addSuppressed(closing);
        }
      }
    }
    if (failure != null) {
      throw failure;
    }
  }

  private void closeAfterFailure(RuntimeException startupFailure) {
    try {
      close();
    } catch (RuntimeException closing) {
      startupFailure.addSuppressed(closing);
    }
  }
}
