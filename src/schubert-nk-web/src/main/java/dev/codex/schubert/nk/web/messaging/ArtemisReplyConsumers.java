package dev.codex.schubert.nk.web.messaging;

import dev.codex.schubert.nk.protocol.transport.BrokerTopology;
import dev.codex.schubert.nk.protocol.transport.FailedJmsIsolationException;
import dev.codex.schubert.nk.protocol.transport.UnconfirmedJmsRollbackException;
import dev.codex.schubert.nk.web.bootstrap.WebStartupException;
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
  // All ports/state exist before factory.open; this one session serializes deliveries.
  private final AtomicBoolean rollbackAttempted = new AtomicBoolean();
  private final AtomicBoolean rollbackConfirmed = new AtomicBoolean();
  private final Runnable attemptingRollback = () -> rollbackAttempted.set(true);
  private final Runnable confirmingRollback = () -> rollbackConfirmed.set(true);
  private boolean closed;
  private volatile boolean stopping;
  private boolean startAttempted;
  private volatile boolean started;
  private final java.util.concurrent.locks.ReentrantLock stateLock =
      new java.util.concurrent.locks.ReentrantLock();

  private ArtemisReplyConsumers(JmsContextFactory factory) {
    // BUG1537: field initialization is complete before acquiring the dedicated context.
    this.context = Objects.requireNonNull(factory.open(), "JMS context");
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
    return new ArtemisReplyConsumers(factory);
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
            rollbackAttempted.set(false);
            rollbackConfirmed.set(false);
            try {
              reply.onMessage(opened, message, attemptingRollback, confirmingRollback);
            } catch (CommittedFatalReplyException fatal) {
              halted.set(true);
              // This dedicated session serializes callbacks; halt excludes later deliveries.
              terminal.set(true);
              onTerminal.accept(fatal);
            } catch (JMSException | RuntimeException | Error failure) {
              deliveryFailure(failure, onFatal);
            }
          });
      opened.start();
      started = true;
    } finally {
      stateLock.unlock();
    }
  }

  private void deliveryFailure(Throwable failure, Runnable onFatal) {
    Error selectedFatal = null;
    try {
      WebStartupException.preserveFatal(failure);
    } catch (Error fatal) {
      selectedFatal = fatal;
    }
    if (selectedFatal == null
        && !(failure instanceof FailedJmsIsolationException)
        && !(failure instanceof UnconfirmedJmsRollbackException)
        && rollbackConfirmed.get()) {
      return; // Confirmed, nonfatal rollback only: broker-controlled retry.
    }
    halted.set(true);
    terminal.set(true);
    if (selectedFatal != null && rollbackAttempted.compareAndSet(false, true)) {
      try {
        context.rollback();
      } catch (RuntimeException | Error unconfirmed) {
        // Selected fatal retains identity; no second rollback/ACK, owner retains cleanup.
      }
    }
    try {
      onFatal.run();
    } finally {
      // SSC332: notification cannot mask the selected Error. No owned cleanup is skipped here.
      if (selectedFatal != null) throw selectedFatal;
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
