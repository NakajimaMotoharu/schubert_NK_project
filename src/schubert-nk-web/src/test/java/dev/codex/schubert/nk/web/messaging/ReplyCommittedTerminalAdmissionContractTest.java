package dev.codex.schubert.nk.web.messaging;

import static org.junit.jupiter.api.Assertions.assertAll;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

import jakarta.jms.JMSConsumer;
import jakarta.jms.JMSContext;
import jakarta.jms.JMSProducer;
import jakarta.jms.Message;
import jakarta.jms.MessageListener;
import java.lang.reflect.Proxy;
import java.time.Clock;
import java.time.Instant;
import java.time.ZoneOffset;
import java.util.Set;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.Test;

/** SS322§11; PG-D444/BUG1501/YKT1261; PT-JMS-TERM004. No broker/DB/runtime operation. */
final class ReplyCommittedTerminalAdmissionContractTest {
  @Test
  void term004ReplyCommitStopsFurtherAdmissions() {
    var fixture = new Fixture();
    var protocol = new AtomicInteger();
    var fatal = new AtomicInteger();
    var clock = Clock.fixed(Instant.parse("2026-10-20T00:00:00Z"), ZoneOffset.UTC);
    try (var runtime =
        ArtemisReplyConsumers.start(
            fixture::context,
            new ArtemisReplyConsumer(
                new JmsRequestReplyClient(),
                new JmsReplyDecoder(),
                new ArtemisReplyDlqSender(clock)),
            ignored -> protocol.incrementAndGet(),
            fatal::incrementAndGet)) {
      assertTrue(runtime.ready());
      fixture.deliver();
      assertFalse(runtime.ready());
      assertTrue(runtime.terminalFailureObserved());
      assertEquals(1, protocol.get());
      assertEquals(0, fatal.get());
      assertEquals(1, fixture.reads);
      assertEquals(1, fixture.sends);
      assertEquals(1, fixture.commits);
      assertEquals(0, fixture.rollbacks);
      assertEquals(0, fixture.unexpected);
      fixture.deliver();
      assertAll(
          () -> assertEquals(1, fixture.reads),
          () -> assertEquals(1, fixture.sends),
          () -> assertEquals(1, fixture.commits),
          () -> assertEquals(0, fixture.rollbacks),
          () -> assertEquals(1, protocol.get()),
          () -> assertEquals(0, fatal.get()),
          () -> assertEquals(0, fixture.unexpected));
      assertEquals(0, fixture.closes);
    }
    assertEquals(1, fixture.closes);
  }

  private static final class Fixture {
    private MessageListener listener;
    private int reads;
    private int sends;
    private int commits;
    private int rollbacks;
    private int closes;
    private int unexpected;

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
                  case "createProducer":
                    return Proxy.newProxyInstance(
                        JMSProducer.class.getClassLoader(),
                        new Class<?>[] {JMSProducer.class},
                        (p, m, a) -> {
                          if (m.getName().equals("send")) {
                            sends++;
                            return p;
                          }
                          if (Set.of("setDeliveryMode", "setTimeToLive").contains(m.getName()))
                            return p;
                          throw unexpected();
                        });
                  case "commit":
                    commits++;
                    return null;
                  case "rollback":
                    rollbacks++;
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
                      return null;
                    }
                    if (Set.of("getStringProperty", "getJMSCorrelationID")
                        .contains(method.getName())) return null;
                    if (method.getName().equals("propertyExists")) return false;
                    if (Set.of(
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
      unexpected++;
      return new AssertionError("unexpected finite terminal fixture operation");
    }
  }
}
