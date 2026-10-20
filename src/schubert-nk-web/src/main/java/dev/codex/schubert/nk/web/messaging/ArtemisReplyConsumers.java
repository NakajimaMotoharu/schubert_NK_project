package dev.codex.schubert.nk.web.messaging;

import dev.codex.schubert.nk.protocol.transport.BrokerTopology;
import dev.codex.schubert.nk.protocol.transport.FailedJmsIsolationException;
import dev.codex.schubert.nk.protocol.transport.UnconfirmedJmsRollbackException;
import jakarta.jms.JMSConsumer;
import jakarta.jms.JMSContext;
import jakarta.jms.JMSException;
import java.util.Objects;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.function.Consumer;
import org.apache.activemq.artemis.jms.client.ActiveMQQueue;

/**
 * The one dedicated, transacted Web reply session. The owner must exit nonzero after a committed
 * fatal reply and must close this runtime before closing the shared broker connection. Trace:
 * NK-MSG-001; RD MQ-004/005/008; UI212/231; SS321 sections 6-9; PT-JMS-014.
 */
public final class ArtemisReplyConsumers implements AutoCloseable {
  private final JMSContext context;
  private final AtomicBoolean terminal = new AtomicBoolean();
  private final AtomicBoolean halted = new AtomicBoolean();
  private volatile boolean closed;
  private volatile boolean stopping;
  private boolean startAttempted;
  private volatile boolean started;
  private final java.util.concurrent.locks.ReentrantLock stateLock =
      new java.util.concurrent.locks.ReentrantLock();

  private ArtemisReplyConsumers(JMSContext context) {
    this.context = context;
  }

  /** Installs the listener before delivery starts; a failed startup releases its session. */
  public static ArtemisReplyConsumers start(
      JmsContextFactory factory,
      ArtemisReplyConsumer reply,
      Consumer<CommittedFatalReplyException> onTerminal) {
    return start(factory, reply, onTerminal, () -> {});
  }

  /** Fatal infrastructure notification is distinct from a committed protocol-DLQ result. */
  public static ArtemisReplyConsumers start(
      JmsContextFactory factory,
      ArtemisReplyConsumer reply,
      Consumer<CommittedFatalReplyException> onTerminal,
      Runnable onFatal) {
    Objects.requireNonNull(factory, "factory");
    Objects.requireNonNull(reply, "reply");
    Objects.requireNonNull(onTerminal, "onTerminal");
    Objects.requireNonNull(onFatal, "onFatal");
    ArtemisReplyConsumers runtime = bind(factory);
    try {
      runtime.start(reply, onTerminal, onFatal);
      return runtime;
    } catch (RuntimeException | Error failure) {
      try {
        runtime.close();
      } catch (RuntimeException | Error closing) {
        if (failure != closing) failure.addSuppressed(closing);
      }
      dev.codex.schubert.nk.web.session.SessionStoreException.preserveFatal(failure);
      throw new IllegalStateException("Web reply consumer startup failed", failure);
    }
  }

  /** Native caller captures this owner before listener setup or delivery can fail. */
  public static ArtemisReplyConsumers bind(JmsContextFactory factory) {
    Objects.requireNonNull(factory, "factory");
    return new ArtemisReplyConsumers(Objects.requireNonNull(factory.open(), "JMS context"));
  }

  public void start(ArtemisReplyConsumer reply, Consumer<CommittedFatalReplyException> onTerminal) {
    start(reply, onTerminal, () -> {});
  }

  public void start(
      ArtemisReplyConsumer reply,
      Consumer<CommittedFatalReplyException> onTerminal,
      Runnable onFatal) {
    Objects.requireNonNull(reply, "reply");
    Objects.requireNonNull(onTerminal, "onTerminal");
    Objects.requireNonNull(onFatal, "onFatal");
    stateLock.lock();
    try {
      if (stopping || startAttempted)
        throw new IllegalStateException("Web reply start unavailable");
      startAttempted = true;
      JMSContext opened = context;
      opened.setAutoStart(false);
      if (opened.getSessionMode() != JMSContext.SESSION_TRANSACTED) {
        throw new IllegalStateException("Web reply consumer must be transacted");
      }
      JMSConsumer consumer =
          Objects.requireNonNull(
              opened.createConsumer(
                  new ActiveMQQueue(BrokerTopology.SYNC_REPLY_WEB.fullyQualifiedQueue())),
              "JMS consumer");
      consumer.setMessageListener(
          message -> {
            if (halted.get()) return;
            try {
              reply.onMessage(opened, message);
            } catch (CommittedFatalReplyException fatal) {
              halted.set(true);
              // This dedicated session serializes callbacks; halt excludes later deliveries.
              terminal.set(true);
              onTerminal.accept(fatal);
            } catch (FailedJmsIsolationException | UnconfirmedJmsRollbackException | Error fatal) {
              halted.set(true);
              terminal.set(true);
              if (fatal instanceof Error) {
                try {
                  opened.rollback();
                } catch (RuntimeException | Error unconfirmed) {
                  // Never ACK or re-open this transaction; the outer owner retains cleanup.
                }
              }
              onFatal.run();
              if (fatal instanceof Error error) throw error;
            } catch (JMSException | RuntimeException retryable) {
              // Confirmed rollback only; the broker controls redelivery.
            }
          });
      opened.start();
      started = true;
    } finally {
      stateLock.unlock();
    }
  }

  public boolean ready() {
    return !stopping && started && !terminal.get();
  }

  public boolean terminalFailureObserved() {
    return terminal.get();
  }

  @Override
  public void close() {
    stateLock.lock();
    try {
      if (closed) return;
      stopping = true;
      try {
        context.close();
      } catch (RuntimeException failure) {
        dev.codex.schubert.nk.web.session.SessionStoreException.preserveFatal(failure);
        throw new IllegalStateException("Web reply consumer close failed", failure);
      }
      closed = true;
    } finally {
      stateLock.unlock();
    }
  }
}
