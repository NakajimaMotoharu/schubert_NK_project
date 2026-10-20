package dev.codex.schubert.nk.api.messaging.inbound;

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
public final class QuestionWorkConsumers implements AutoCloseable {
  private final JMSContext context;
  private final java.util.concurrent.locks.ReentrantLock lock =
      new java.util.concurrent.locks.ReentrantLock();
  private final AtomicBoolean halted = new AtomicBoolean();
  private boolean closed;

  private QuestionWorkConsumers(Supplier<JMSContext> factory) {
    // BUG1537: initialize this owner/lock/flags before acquiring its only external resource.
    this.context = Objects.requireNonNull(factory.get(), "async context");
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
    var result = new QuestionWorkConsumers(factory);
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
            try {
              listener.onMessage(context, message);
            } catch (CommittedFatalInboundException fatal) {
              result.halted.set(true);
              // This dedicated session serializes callbacks; halt excludes later deliveries.
              onTerminal.accept(fatal);
            } catch (FailedJmsIsolationException | UnconfirmedJmsRollbackException | Error fatal) {
              result.halted.set(true);
              if (fatal instanceof Error) {
                try {
                  context.rollback();
                } catch (RuntimeException | Error unconfirmed) {
                  // Keep fatal stop/unconfirmed rollback distinct from committed protocol DLQ.
                }
              }
              onFatal.run();
            } catch (JMSException | RuntimeException retryable) {
              // Confirmed rollback only; real delivery metadata and max4 still govern retry.
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
    return !halted.get();
  }

  @Override
  public void close() {
    halted.set(true);
    lock.lock();
    try {
      if (closed) return;
      try {
        context.close();
      } catch (RuntimeException failure) {
        throw new IllegalStateException("API Question consumer close failed", failure);
      }
      closed = true;
    } finally {
      lock.unlock();
    }
  }
}
