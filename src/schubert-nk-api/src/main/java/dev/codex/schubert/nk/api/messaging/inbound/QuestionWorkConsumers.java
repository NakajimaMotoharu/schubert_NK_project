package dev.codex.schubert.nk.api.messaging.inbound;

import dev.codex.schubert.nk.protocol.transport.BrokerTopology;
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
public final class QuestionWorkConsumers implements AutoCloseable {
  private final JMSContext context;
  private final Object lock = new Object();
  private final AtomicBoolean terminal = new AtomicBoolean();
  private final AtomicBoolean halted = new AtomicBoolean();
  private boolean closed;

  private QuestionWorkConsumers(JMSContext context) {
    this.context = context;
  }

  public static QuestionWorkConsumers start(
      Supplier<JMSContext> factory,
      QuestionWorkListener listener,
      Consumer<CommittedFatalInboundException> onTerminal,
      Runnable onFatal) {
    Objects.requireNonNull(factory, "async factory");
    Objects.requireNonNull(listener, "work listener");
    Objects.requireNonNull(onTerminal, "terminal signal");
    Objects.requireNonNull(onFatal, "fatal signal");
    var context = Objects.requireNonNull(factory.get(), "async context");
    var result = new QuestionWorkConsumers(context);
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
            try {
              listener.onMessage(context, message);
            } catch (CommittedFatalInboundException fatal) {
              if (result.terminal.compareAndSet(false, true)) onTerminal.accept(fatal);
            } catch (JMSException | RuntimeException retryable) {
              // Listener rolled back. Real Artemis delivery metadata and fixed max4 govern retry.
            } catch (Error fatal) {
              result.halted.set(true);
              if (result.terminal.compareAndSet(false, true)) {
                try {
                  context.rollback();
                } catch (RuntimeException | Error unconfirmed) {
                  // Keep fatal stop/unconfirmed rollback distinct from committed protocol DLQ.
                }
                onFatal.run();
              }
            }
          });
      context.start();
      return result;
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
        result.close();
      } catch (RuntimeException | Error closing) {
        if (closing instanceof Error fatal && !(retained instanceof Error)) throw fatal;
        if (closing != retained) retained.addSuppressed(closing);
      }
      if (retained instanceof Error fatal) throw fatal;
      throw new IllegalStateException("API Question consumer startup failed", retained);
    }
  }

  public boolean ready() {
    synchronized (lock) {
      return !closed && !terminal.get();
    }
  }

  @Override
  public void close() {
    synchronized (lock) {
      if (closed) return;
      closed = true;
      try {
        context.close();
      } catch (RuntimeException failure) {
        throw new IllegalStateException("API Question consumer close failed", failure);
      }
    }
  }
}
