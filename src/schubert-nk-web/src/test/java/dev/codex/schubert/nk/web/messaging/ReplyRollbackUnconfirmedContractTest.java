package dev.codex.schubert.nk.web.messaging;

import static org.junit.jupiter.api.Assertions.assertAll;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
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
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicReference;
import org.junit.jupiter.api.Test;

/** SS321§7/352; BUG1489/YKT1249; UNC004; finite memory proxies only. */
final class ReplyRollbackUnconfirmedContractTest {
  @Test
  void rollbackUnconfirmedMakesReplyOwnerUnreadyAndStopsFurtherDecode() {
    var listener = new AtomicReference<MessageListener>();
    var reads = new AtomicInteger();
    var rollbacks = new AtomicInteger();
    var commits = new AtomicInteger();
    var closes = new AtomicInteger();
    var committedFatal = new AtomicInteger();
    var context =
        (JMSContext)
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
                            throw new AssertionError("unexpected consumer method");
                          });
                    case "rollback":
                      rollbacks.incrementAndGet();
                      throw new JMSRuntimeException("synthetic unconfirmed rollback");
                    case "commit":
                      commits.incrementAndGet();
                      return null;
                    case "close":
                      closes.incrementAndGet();
                      return null;
                    default:
                      throw new AssertionError("unexpected context method");
                  }
                });
    var message =
        (BytesMessage)
            Proxy.newProxyInstance(
                BytesMessage.class.getClassLoader(),
                new Class<?>[] {BytesMessage.class},
                (proxy, method, args) -> {
                  if (method.getName().equals("getBodyLength")) {
                    reads.incrementAndGet();
                    throw new JMSRuntimeException("synthetic read failure");
                  }
                  throw new AssertionError("unexpected message method");
                });
    var clock = Clock.fixed(Instant.parse("2026-10-20T00:00:00Z"), ZoneOffset.UTC);
    try (var runtime =
        ArtemisReplyConsumers.start(
            () -> context,
            new ArtemisReplyConsumer(
                new JmsRequestReplyClient(),
                new JmsReplyDecoder(),
                new ArtemisReplyDlqSender(clock)),
            ignored -> committedFatal.incrementAndGet())) {
      assertTrue(runtime.ready());
      assertNotNull(listener.get());
      listener.get().onMessage(message);
      assertAll(
          () -> assertFalse(runtime.ready(), "unconfirmed rollback is not retry-ready"),
          () -> assertTrue(runtime.terminalFailureObserved()),
          () -> assertEquals(1, rollbacks.get()),
          () -> assertEquals(0, committedFatal.get()));
      listener.get().onMessage(message);
      assertEquals(1, reads.get());
      assertEquals(0, commits.get());
      assertEquals(0, closes.get());
    }
    assertEquals(1, closes.get());
  }
}
