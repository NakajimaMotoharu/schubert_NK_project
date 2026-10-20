package dev.codex.schubert.nk.api.messaging.inbound;

import static org.junit.jupiter.api.Assertions.*;

import jakarta.jms.JMSConsumer;
import jakarta.jms.JMSContext;
import jakarta.jms.JMSException;
import jakarta.jms.JMSRuntimeException;
import jakarta.jms.Message;
import jakarta.jms.MessageListener;
import java.lang.reflect.Proxy;
import java.util.concurrent.atomic.AtomicReference;

/** SS322§11; BUG1494/YKT1254; PT-JMS-ISO001..008. Pure fixture shared via existing test-jar. */
public final class FatalIsolationFixture {
  private final Exception isolationFailure;
  private final AtomicReference<MessageListener> listener = new AtomicReference<>();
  private int readCount;
  private int rollbackCount;
  private int commitCount;
  private int closeCount;
  private int unexpectedCount;

  public FatalIsolationFixture(boolean checked) {
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
                  return null; // Rollback is deliberately CONFIRMED, not the BUG1489 fixture.
                case "commit":
                  commitCount++;
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
                        throw isolationFailure;
                      }
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
}
