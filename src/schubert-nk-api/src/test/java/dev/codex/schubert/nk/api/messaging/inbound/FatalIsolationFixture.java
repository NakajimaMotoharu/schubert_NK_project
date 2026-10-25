package dev.codex.schubert.nk.api.messaging.inbound;

import static org.junit.jupiter.api.Assertions.assertNotNull;

import jakarta.jms.JMSConsumer;
import jakarta.jms.JMSContext;
import jakarta.jms.JMSException;
import jakarta.jms.JMSProducer;
import jakarta.jms.JMSRuntimeException;
import jakarta.jms.Message;
import jakarta.jms.MessageListener;
import java.lang.reflect.Proxy;
import java.util.concurrent.atomic.AtomicReference;

/** SS322§11; ISO001..006/TERM001..003. API-local fixture, no test-jar/module crossing. */
public final class FatalIsolationFixture {
  private final Exception isolationFailure;
  private final boolean failIsolation;
  private final AtomicReference<MessageListener> listener = new AtomicReference<>();
  private int readCount;
  private int rollbackCount;
  private int commitCount;
  private int closeCount;
  private int unexpectedCount;
  private int sendCount;
  private Runnable firstCommit = () -> {};
  private Runnable firstRollback = () -> {};

  public FatalIsolationFixture(boolean checked) {
    this(checked, true);
  }

  public FatalIsolationFixture(boolean checked, boolean failIsolation) {
    this.failIsolation = failIsolation;
    isolationFailure =
        checked
            ? new JMSException("synthetic checked isolation read")
            : new JMSRuntimeException("synthetic runtime isolation read");
  }

  public JMSContext context() {
    return (JMSContext)
        Proxy.newProxyInstance(
            JMSContext.class.getClassLoader(),
            new Class<?>[] {JMSContext.class},
            (proxy, method, args) -> {
              switch (method.getName()) {
                case "getSessionMode":
                  return JMSContext.SESSION_TRANSACTED;
                case "setAutoStart", "start":
                  return null;
                case "createConsumer":
                  return Proxy.newProxyInstance(
                      JMSConsumer.class.getClassLoader(),
                      new Class<?>[] {JMSConsumer.class},
                      (p, m, a) -> {
                        if (m.getName().equals("setMessageListener")) {
                          listener.set((MessageListener) a[0]);
                          return null;
                        }
                        throw unexpected();
                      });
                case "rollback":
                  rollbackCount++;
                  if (rollbackCount == 1) firstRollback.run();
                  return null; // Rollback is deliberately CONFIRMED, not the BUG1489 fixture.
                case "createProducer":
                  return Proxy.newProxyInstance(
                      JMSProducer.class.getClassLoader(),
                      new Class<?>[] {JMSProducer.class},
                      (p, m, a) -> {
                        if (m.getName().equals("send")) {
                          sendCount++;
                          return p;
                        }
                        if (m.getName().equals("setDeliveryMode")
                            || m.getName().equals("setTimeToLive")) return p;
                        throw unexpected();
                      });
                case "commit":
                  commitCount++;
                  if (commitCount == 1) firstCommit.run();
                  return null;
                case "close":
                  closeCount++;
                  return null;
                default:
                  throw unexpected();
              }
            });
  }

  public void deliver() {
    assertNotNull(listener.get());
    listener
        .get()
        .onMessage(
            (Message)
                Proxy.newProxyInstance(
                    Message.class.getClassLoader(),
                    new Class<?>[] {Message.class},
                    (proxy, method, args) -> {
                      if (method.getName().equals("getJMSMessageID")) {
                        readCount++;
                        if (failIsolation) throw isolationFailure;
                        return null;
                      }
                      if (method.getName().equals("getStringProperty")
                          || method.getName().equals("getJMSCorrelationID")) return null;
                      if (method.getName().equals("propertyExists")) return false;
                      if (java.util.Set.of(
                              "clearProperties",
                              "setJMSCorrelationID",
                              "setJMSReplyTo",
                              "setJMSType",
                              "setStringProperty",
                              "setIntProperty")
                          .contains(method.getName())) return null;
                      throw unexpected();
                    }));
  }

  private AssertionError unexpected() {
    unexpectedCount++;
    return new AssertionError("unexpected finite isolation fixture operation");
  }

  public int metadataReads() {
    return readCount;
  }

  public int rollbacks() {
    return rollbackCount;
  }

  public int commits() {
    return commitCount;
  }

  public int closes() {
    return closeCount;
  }

  public int unexpectedCalls() {
    return unexpectedCount;
  }

  public int sends() {
    return sendCount;
  }

  public void onFirstCommit(Runnable rendezvous) {
    firstCommit = java.util.Objects.requireNonNull(rendezvous);
  }

  public void onFirstRollback(Runnable rendezvous) {
    firstRollback = java.util.Objects.requireNonNull(rendezvous);
  }
}
