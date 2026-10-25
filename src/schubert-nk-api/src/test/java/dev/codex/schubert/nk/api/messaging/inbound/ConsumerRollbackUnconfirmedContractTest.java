package dev.codex.schubert.nk.api.messaging.inbound;

import static org.junit.jupiter.api.Assertions.assertAll;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

import jakarta.jms.BytesMessage;
import jakarta.jms.JMSConsumer;
import jakarta.jms.JMSContext;
import jakarta.jms.JMSRuntimeException;
import jakarta.jms.MessageListener;
import java.lang.reflect.Proxy;
import java.time.Clock;
import java.time.Instant;
import java.time.ZoneOffset;
import java.util.ArrayList;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.Test;

/** SS321§7/352; BUG1489/YKT1249; UNC001..003; no broker/DB/VM. */
final class ConsumerRollbackUnconfirmedContractTest {
  private static final Clock CLOCK =
      Clock.fixed(Instant.parse("2026-10-20T00:00:00Z"), ZoneOffset.UTC);

  @Test
  void syncRollbackUnconfirmedStopsAllFourContexts() throws Exception {
    verify(0, 4, true);
  }

  @Test
  void questionRollbackUnconfirmedStopsFurtherWork() throws Exception {
    verify(1, 1, true);
  }

  @Test
  void webLogRollbackUnconfirmedStopsFurtherLogs() throws Exception {
    verify(2, 1, true);
  }

  @Test
  void syncConfirmedRollbackKeepsAllFourContextsRetryReady() throws Exception {
    verify(0, 4, false);
  }

  @Test
  void questionConfirmedRollbackKeepsRetryReady() throws Exception {
    verify(1, 1, false);
  }

  @Test
  void webLogConfirmedRollbackKeepsRetryReady() throws Exception {
    verify(2, 1, false);
  }

  private static void verify(int kind, int count, boolean unconfirmed) throws Exception {
    var contexts = new ArrayList<Fixture>();
    var fatal = new AtomicInteger();
    var committedFatal = new AtomicInteger();
    java.util.function.Supplier<JMSContext> factory =
        () -> {
          var fixture = new Fixture(unconfirmed);
          contexts.add(fixture);
          return fixture.context();
        };
    AutoCloseable owner;
    java.util.function.BooleanSupplier ready;
    switch (kind) {
      case 0 -> {
        var runtime =
            SyncRequestConsumers.start(
                factory,
                new SyncRequestListener(ignored -> new byte[0], CLOCK),
                ignored -> committedFatal.incrementAndGet(),
                fatal::incrementAndGet);
        owner = runtime;
        ready = runtime::ready;
      }
      case 1 -> {
        var runtime =
            QuestionWorkConsumers.start(
                factory,
                new QuestionWorkListener(event -> {}, CLOCK),
                ignored -> committedFatal.incrementAndGet(),
                fatal::incrementAndGet);
        owner = runtime;
        ready = runtime::ready;
      }
      case 2 -> {
        var runtime =
            WebLogConsumers.start(
                factory,
                new WebLogListener(event -> {}, CLOCK),
                ignored -> committedFatal.incrementAndGet(),
                fatal::incrementAndGet);
        owner = runtime;
        ready = runtime::ready;
      }
      default -> throw new AssertionError("finite three groups");
    }
    try (owner) {
      assertEquals(count, contexts.size());
      assertTrue(ready.getAsBoolean());
      contexts.getFirst().deliver();
      assertAll(
          () -> assertEquals(!unconfirmed, ready.getAsBoolean()),
          () -> assertEquals(unconfirmed ? 1 : 0, fatal.get()),
          () -> assertEquals(0, committedFatal.get()),
          () -> assertEquals(1, contexts.getFirst().rollbacks));
      for (var context : contexts) context.deliver();
      assertEquals(unconfirmed ? 1 : count + 1, contexts.stream().mapToInt(c -> c.reads).sum());
      assertEquals(unconfirmed ? 1 : 0, fatal.get());
      assertEquals(0, contexts.stream().mapToInt(c -> c.commits).sum());
      assertEquals(0, contexts.stream().mapToInt(c -> c.closes).sum());
    }
    assertEquals(count, contexts.stream().mapToInt(c -> c.closes).sum());
  }

  private static final class Fixture {
    private final boolean unconfirmed;
    private MessageListener listener;
    private int reads;
    private int rollbacks;
    private int commits;
    private int closes;

    Fixture(boolean unconfirmed) {
      this.unconfirmed = unconfirmed;
    }

    JMSContext context() {
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
                            listener = (MessageListener) a[0];
                            return null;
                          }
                          throw new AssertionError("unexpected consumer method");
                        });
                  case "rollback":
                    rollbacks++;
                    if (unconfirmed)
                      throw new JMSRuntimeException("synthetic unconfirmed rollback");
                    return null;
                  case "commit":
                    commits++;
                    return null;
                  case "close":
                    closes++;
                    return null;
                  default:
                    throw new AssertionError("unexpected context method");
                }
              });
    }

    void deliver() {
      assertNotNull(listener);
      listener.onMessage(
          (BytesMessage)
              Proxy.newProxyInstance(
                  BytesMessage.class.getClassLoader(),
                  new Class<?>[] {BytesMessage.class},
                  (proxy, method, args) -> {
                    if (method.getName().equals("getBodyLength")) {
                      reads++;
                      throw new JMSRuntimeException("synthetic read failure");
                    }
                    throw new AssertionError("unexpected message method");
                  }));
    }
  }
}
