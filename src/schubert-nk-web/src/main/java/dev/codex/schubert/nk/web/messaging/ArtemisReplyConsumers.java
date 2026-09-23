package dev.codex.schubert.nk.web.messaging;

import dev.codex.schubert.nk.protocol.transport.BrokerTopology;
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
  private volatile boolean closed;

  private ArtemisReplyConsumers(JMSContext context) {
    this.context = context;
  }

  /** Installs the listener before delivery starts; a failed startup releases its session. */
  public static ArtemisReplyConsumers start(
      JmsContextFactory factory,
      ArtemisReplyConsumer reply,
      Consumer<CommittedFatalReplyException> onTerminal) {
    Objects.requireNonNull(factory, "factory");
    Objects.requireNonNull(reply, "reply");
    Objects.requireNonNull(onTerminal, "onTerminal");
    JMSContext opened = Objects.requireNonNull(factory.open(), "JMS context");
    ArtemisReplyConsumers runtime = new ArtemisReplyConsumers(opened);
    try {
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
            try {
              reply.onMessage(opened, message);
            } catch (CommittedFatalReplyException fatal) {
              if (runtime.terminal.compareAndSet(false, true)) {
                onTerminal.accept(fatal);
              }
            } catch (JMSException | RuntimeException retryable) {
              // ArtemisReplyConsumer rolled back; the broker controls redelivery.
            }
          });
      opened.start();
      return runtime;
    } catch (RuntimeException failure) {
      try {
        runtime.close();
      } catch (RuntimeException closing) {
        failure.addSuppressed(closing);
      }
      throw new IllegalStateException("Web reply consumer startup failed", failure);
    }
  }

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
    try {
      context.close();
    } catch (RuntimeException failure) {
      throw new IllegalStateException("Web reply consumer close failed", failure);
    }
  }
}
