package dev.codex.schubert.nk.web.messaging;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assertions.fail;

import jakarta.jms.BytesMessage;
import jakarta.jms.JMSConsumer;
import jakarta.jms.JMSContext;
import jakarta.jms.JMSProducer;
import jakarta.jms.JMSRuntimeException;
import jakarta.jms.Message;
import jakarta.jms.MessageListener;
import java.lang.reflect.Proxy;
import java.time.Clock;
import java.time.Instant;
import java.time.ZoneOffset;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.Test;

/** SS321§7/352; PG-D441/BUG1489; UNC012..016. No provider, DB, or external owner. */
final class ReplyRollbackSignalContractTest {
  @Test
  void unconfirmedRollbackSignalsInfrastructureOnceAndNeverCommittedFatal() {
    var fixture = new Fixture();
    fixture.rollbackFailure = new JMSRuntimeException("synthetic rollback");
    try (var runtime = fixture.open()) {
      fixture.deliver();
      assertFalse(runtime.ready());
      assertTrue(runtime.terminalFailureObserved());
      assertEquals(1, fixture.fatal.get());
      assertEquals(0, fixture.committed.get());
      assertEquals(1, fixture.rollbacks);
      fixture.deliver();
      assertEquals(1, fixture.reads);
      assertEquals(0, fixture.commits);
      assertEquals(0, fixture.closes);
    }
    assertEquals(1, fixture.closes);
  }

  @Test
  void confirmedRollbackRemainsRetryReadyWithoutFatalSignal() {
    var fixture = new Fixture();
    try (var runtime = fixture.open()) {
      fixture.deliver();
      fixture.deliver();
      assertTrue(runtime.ready());
      assertFalse(runtime.terminalFailureObserved());
      assertEquals(2, fixture.reads);
      assertEquals(2, fixture.rollbacks);
      assertEquals(0, fixture.fatal.get());
      assertEquals(0, fixture.commits);
    }
  }

  @Test
  void errorIdentitySurvivesConfirmedOrUnconfirmedRollbackAndOwnerStaysHalted() {
    for (int mode = 0; mode < 3; mode++) {
      var fixture = new Fixture();
      var error = new AssertionError("synthetic read fatal");
      fixture.readFailure = error;
      fixture.rollbackFailure =
          switch (mode) {
            case 0 -> null;
            case 1 -> new JMSRuntimeException("synthetic rollback");
            default -> new AssertionError("synthetic rollback fatal");
          };
      try (var runtime = fixture.open()) {
        assertSame(error, assertThrows(AssertionError.class, fixture::deliver));
        assertFalse(runtime.ready());
        assertTrue(runtime.terminalFailureObserved());
        assertEquals(1, fixture.fatal.get());
        assertEquals(1, fixture.rollbacks);
        fixture.deliver();
        assertEquals(1, fixture.reads);
        assertEquals(0, fixture.commits);
      }
    }
  }

  @Test
  void priorProtocolTerminalIsNeverRenotifiedOrReclassifiedAsUnconfirmedCommit() {
    for (boolean fatalError : new boolean[] {false, true}) {
      var fixture = new Fixture();
      try (var runtime = fixture.open()) {
        fixture.listener.onMessage(fixture.invalidMessage());
        assertFalse(runtime.ready());
        assertEquals(1, fixture.committed.get());
        assertEquals(1, fixture.commits);
        fixture.rollbackFailure = new JMSRuntimeException("synthetic rollback");
        if (fatalError) {
          var error = new AssertionError("synthetic later fatal");
          fixture.readFailure = error;
          fixture.deliver(); // SS322: a decided terminal admits no later provider input.
          assertEquals(0, fixture.rollbacks);
        } else {
          fixture.deliver();
          assertEquals(0, fixture.rollbacks);
        }
        fixture.deliver();
        assertEquals(0, fixture.reads);
        assertEquals(0, fixture.fatal.get());
        assertEquals(1, fixture.committed.get());
        assertEquals(1, fixture.commits); // Only the independently staged protocol DLQ was ACKed.
      }
    }
  }

  @Test
  void nullFatalSignalIsRejectedBeforeAcquisitionOrListenerStart() {
    var fixture = new Fixture();
    var opens = new AtomicInteger();
    assertThrows(
        NullPointerException.class,
        () ->
            ArtemisReplyConsumers.start(
                () -> {
                  opens.incrementAndGet();
                  return fixture.context();
                },
                fixture.reply(),
                ignored -> {},
                null));
    assertEquals(0, opens.get());
    try (var owner = ArtemisReplyConsumers.bind(fixture::context)) {
      assertThrows(
          NullPointerException.class, () -> owner.start(fixture.reply(), ignored -> {}, null));
      assertFalse(owner.ready());
      assertNull(fixture.listener);
    }
    // The legacy owned-start overload has no signal argument; its local terminal/ready contract
    // must still stop a provider whose rollback is unconfirmed, not silently resume delivery.
    var legacy = new Fixture();
    try (var owner = ArtemisReplyConsumers.bind(legacy::context)) {
      owner.start(legacy.reply(), ignored -> fail("not a committed DLQ"));
      legacy.rollbackFailure = new JMSRuntimeException("synthetic rollback");
      legacy.deliver();
      assertFalse(owner.ready());
      assertTrue(owner.terminalFailureObserved());
      legacy.deliver();
      assertEquals(1, legacy.reads);
      assertEquals(0, legacy.commits);
    }
  }

  private static final class Fixture {
    private MessageListener listener;
    private Throwable readFailure = new JMSRuntimeException("synthetic read failure");
    private Throwable rollbackFailure;
    private final AtomicInteger fatal = new AtomicInteger();
    private final AtomicInteger committed = new AtomicInteger();
    private int reads;
    private int rollbacks;
    private int commits;
    private int closes;

    ArtemisReplyConsumer reply() {
      return new ArtemisReplyConsumer(
          new JmsRequestReplyClient(),
          new JmsReplyDecoder(),
          new ArtemisReplyDlqSender(
              Clock.fixed(Instant.parse("2026-10-20T00:00:00Z"), ZoneOffset.UTC)));
    }

    ArtemisReplyConsumers open() {
      return ArtemisReplyConsumers.start(
          this::context, reply(), ignored -> committed.incrementAndGet(), fatal::incrementAndGet);
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
                  case "createProducer":
                    return Proxy.newProxyInstance(
                        JMSProducer.class.getClassLoader(),
                        new Class<?>[] {JMSProducer.class},
                        (p, m, a) -> {
                          if (m.getName().equals("setDeliveryMode")
                              || m.getName().equals("setTimeToLive")
                              || m.getName().equals("send")) return p;
                          throw new AssertionError("unexpected producer method");
                        });
                  case "rollback":
                    rollbacks++;
                    if (rollbackFailure != null) throw rollbackFailure;
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
                      throw readFailure;
                    }
                    throw new AssertionError("unexpected message method");
                  }));
    }

    Message invalidMessage() {
      return (Message)
          Proxy.newProxyInstance(
              Message.class.getClassLoader(),
              new Class<?>[] {Message.class},
              (proxy, method, args) -> {
                switch (method.getName()) {
                  case "getJMSMessageID":
                    return "ID:synthetic";
                  case "getJMSCorrelationID":
                  case "getStringProperty":
                    return "00000000-0000-0000-0000-000000000001";
                  case "propertyExists":
                    return false;
                  case "clearProperties",
                  "setJMSCorrelationID",
                  "setJMSReplyTo",
                  "setJMSType",
                  "setStringProperty",
                  "setIntProperty":
                    return null;
                  default:
                    throw new AssertionError("unexpected rejected message method");
                }
              });
    }
  }
}
