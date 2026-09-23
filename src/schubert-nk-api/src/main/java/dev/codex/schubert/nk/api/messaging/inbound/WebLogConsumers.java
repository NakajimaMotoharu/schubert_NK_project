package dev.codex.schubert.nk.api.messaging.inbound;

import dev.codex.schubert.nk.protocol.transport.BrokerTopology;
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
public final class WebLogConsumers implements AutoCloseable {
  private final JMSContext context;
  private final AtomicBoolean terminal = new AtomicBoolean();
  private volatile boolean closed;

  private WebLogConsumers(JMSContext context) {
    this.context = context;
  }

  /** Installs the callback before delivery starts; failed startup always releases its session. */
  public static WebLogConsumers start(
      Supplier<JMSContext> factory,
      WebLogListener listener,
      Consumer<CommittedFatalInboundException> onTerminal) {
    Objects.requireNonNull(factory, "factory");
    Objects.requireNonNull(listener, "listener");
    Objects.requireNonNull(onTerminal, "onTerminal");
    JMSContext opened = Objects.requireNonNull(factory.get(), "JMS context");
    WebLogConsumers runtime = new WebLogConsumers(opened);
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
            try {
              listener.onMessage(opened, message);
            } catch (CommittedFatalInboundException fatal) {
              if (runtime.terminal.compareAndSet(false, true)) {
                onTerminal.accept(fatal);
              }
            } catch (JMSException | RuntimeException retryable) {
              // WebLogListener rolled back; Artemis owns redelivery and delivery-count policy.
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
      throw new IllegalStateException("API Web log consumer startup failed", failure);
    }
  }

  /** Liveness of this one Queue, not full API broker-management readiness. */
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
      throw new IllegalStateException("API Web log consumer close failed", failure);
    }
  }
}
