package dev.codex.schubert.nk.web.messaging;

import static org.junit.jupiter.api.Assertions.assertAll;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

import jakarta.jms.JMSConsumer;
import jakarta.jms.JMSContext;
import jakarta.jms.JMSException;
import jakarta.jms.JMSRuntimeException;
import jakarta.jms.Message;
import jakarta.jms.MessageListener;
import java.lang.reflect.Proxy;
import java.time.Clock;
import java.time.Instant;
import java.time.ZoneOffset;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.Test;

/** SS322§11; BUG1494/YKT1254; PT-JMS-ISO007..008. Independent fixture, no provider/DB. */
final class ReplyFatalIsolationContractTest {
  @Test
  void iso007ReplyCheckedIsolationFailureStopsWithoutAck() {
    verify(true);
  }

  @Test
  void iso008ReplyRuntimeIsolationFailureStopsWithoutAck() {
    verify(false);
  }

  private static void verify(boolean checked) {
    var fixture = new Fixture(checked);
    var fatal = new AtomicInteger();
    var committed = new AtomicInteger();
    var clock = Clock.fixed(Instant.parse("2026-10-20T00:00:00Z"), ZoneOffset.UTC);
    try (var runtime =
        ArtemisReplyConsumers.start(
            fixture::context,
            new ArtemisReplyConsumer(
                new JmsRequestReplyClient(),
                new JmsReplyDecoder(),
                new ArtemisReplyDlqSender(clock)),
            ignored -> committed.incrementAndGet(),
            fatal::incrementAndGet)) {
      assertTrue(runtime.ready());
      fixture.deliver();
      assertAll(
          () -> assertFalse(runtime.ready(), "permanent reply isolation failure must stop"),
          () -> assertTrue(runtime.terminalFailureObserved()),
          () -> assertEquals(1, fatal.get()),
          () -> assertEquals(0, committed.get()),
          () -> assertEquals(1, fixture.metadataReads()),
          () -> assertEquals(1, fixture.rollbacks()),
          () -> assertEquals(0, fixture.commits()),
          () -> assertEquals(0, fixture.unexpectedCalls()));
      fixture.deliver();
      assertEquals(1, fixture.metadataReads());
      assertEquals(1, fixture.rollbacks());
      assertEquals(1, fatal.get());
      assertEquals(0, fixture.closes());
    }
    assertEquals(1, fixture.closes());
  }

  private static final class Fixture {
    private final Exception failure;
    private MessageListener listener;
    private int reads;
    private int rollbacks;
    private int commits;
    private int closes;
    private int unexpected;

    Fixture(boolean checked) {
      failure =
          checked
              ? new JMSException("synthetic checked isolation read")
              : new JMSRuntimeException("synthetic runtime isolation read");
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
                          throw unexpected();
                        });
                  case "rollback":
                    rollbacks++;
                    return null;
                  case "commit":
                    commits++;
                    return null;
                  case "close":
                    closes++;
                    return null;
                  default:
                    throw unexpected();
                }
              });
    }

    void deliver() {
      assertNotNull(listener);
      listener.onMessage(
          (Message)
              Proxy.newProxyInstance(
                  Message.class.getClassLoader(),
                  new Class<?>[] {Message.class},
                  (proxy, method, args) -> {
                    if (method.getName().equals("getJMSMessageID")) {
                      reads++;
                      throw failure;
                    }
                    throw unexpected();
                  }));
    }

    private AssertionError unexpected() {
      unexpected++;
      return new AssertionError("unexpected finite reply fixture operation");
    }

    int metadataReads() {
      return reads;
    }

    int rollbacks() {
      return rollbacks;
    }

    int commits() {
      return commits;
    }

    int closes() {
      return closes;
    }

    int unexpectedCalls() {
      return unexpected;
    }
  }
}
