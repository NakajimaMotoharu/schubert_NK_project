package dev.codex.schubert.nk.web.messaging;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import jakarta.jms.BytesMessage;
import jakarta.jms.JMSConsumer;
import jakarta.jms.JMSContext;
import jakarta.jms.JMSException;
import jakarta.jms.MessageListener;
import java.lang.reflect.Proxy;
import java.sql.SQLException;
import java.time.Clock;
import java.time.Instant;
import java.time.ZoneOffset;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicReference;
import org.junit.jupiter.api.Test;

/** PT-JMS-CONS332005..008; owned pure fixtures, independent counters/identity, SS321/354. */
final class ReplyConsumerGraph332Test {
  @Test
  void cons332005WrappedFatalSignalsThenRethrowsOriginalWithoutSecondRollback() throws Exception {
    for (int edge = 0; edge < 4; edge++) {
      Error fatal = new AssertionError("PRIVATE_fixture");
      try (var f = new Fixture(graph(edge, fatal), null, null)) {
        Throwable observed = capture(() -> f.listener.get().onMessage(f.message));
        assertEquals(1, f.reads.get());
        assertEquals(1, f.rollbacks.get());
        assertEquals(0, f.commits.get());
        assertTrue(observed == fatal && f.signals.get() == 1 && !f.owner.ready());
        assertTrue(f.owner.terminalFailureObserved());
        f.listener.get().onMessage(f.message);
        assertEquals(1, f.reads.get());
      }
    }
  }

  @Test
  void cons332006PreflightIsNotConfirmedAndStateResetsPerDelivery() throws Exception {
    for (boolean nullMessage : new boolean[] {true, false}) {
      try (var f = new Fixture(new IllegalStateException("ordinary"), null, null)) {
        f.listener.get().onMessage(f.message);
        assertTrue(f.owner.ready());
        assertEquals(1, f.rollbacks.get());
        if (!nullMessage) f.mode = JMSContext.AUTO_ACKNOWLEDGE;
        f.listener.get().onMessage(nullMessage ? null : f.message);
        assertEquals(1, f.reads.get());
        assertEquals(1, f.rollbacks.get());
        assertTrue(!f.owner.ready() && f.signals.get() == 1);
        assertEquals(0, f.commits.get());
      }
    }
  }

  @Test
  void cons332007RollbackFatalIsNeverReissuedAndNotificationCannotMaskIt() throws Exception {
    for (Throwable notification :
        new Throwable[] {
          new IllegalStateException("notification"), new AssertionError("notification"), null
        }) {
      Error fatal = new AssertionError("rollback original");
      try (var f = new Fixture(new IllegalStateException("ordinary"), fatal, notification)) {
        Throwable observed = capture(() -> f.listener.get().onMessage(f.message));
        assertEquals(1, f.reads.get());
        assertTrue(f.rollbacks.get() == 1 && observed == fatal && f.signals.get() == 1);
        assertFalse(f.owner.ready());
        assertEquals(0, f.commits.get());
        f.listener.get().onMessage(f.message);
        assertEquals(1, f.reads.get());
      }
    }
  }

  @Test
  void cons332008OrdinaryCycleDirectFatalAndPublicListenerContractsRemain() throws Exception {
    var ordinary = new IllegalStateException("ordinary");
    ordinary.initCause(new IllegalStateException("cycle", ordinary));
    try (var f = new Fixture(ordinary, null, null)) {
      f.listener.get().onMessage(f.message);
      f.listener.get().onMessage(f.message);
      assertTrue(f.owner.ready());
      assertEquals(2, f.rollbacks.get());
      assertEquals(0, f.signals.get());
      assertSame(
          ordinary,
          assertThrows(IllegalStateException.class, () -> f.reply.onMessage(f.context, f.message)));
      assertEquals(3, f.rollbacks.get());
      assertEquals(0, f.commits.get());
      assertThrows(NullPointerException.class, () -> f.reply.onMessage(f.context, null));
      assertEquals(3, f.rollbacks.get());
    }
    for (Throwable notification :
        new Throwable[] {new IllegalStateException("notify"), new AssertionError("notify"), null}) {
      Error fatal = new AssertionError("direct original");
      try (var f = new Fixture(fatal, null, notification)) {
        Throwable observed = capture(() -> f.listener.get().onMessage(f.message));
        assertEquals(1, f.rollbacks.get());
        assertEquals(1, f.signals.get());
        assertTrue(observed == fatal);
        assertFalse(f.owner.ready());
      }
    }
  }

  private static Throwable graph(int edge, Error fatal) {
    return switch (edge) {
      case 0 -> new IllegalStateException("cause", fatal);
      case 1 -> {
        var e = new IllegalStateException("suppressed");
        e.addSuppressed(fatal);
        yield e;
      }
      case 2 -> {
        var e = new JMSException("linked");
        e.setLinkedException(new IllegalStateException("fatal", fatal));
        yield e;
      }
      case 3 -> {
        var e = new SQLException("sql");
        e.setNextException(new SQLException("next", fatal));
        yield new IllegalStateException("sql graph", e);
      }
      default -> throw new AssertionError("fixture edge");
    };
  }

  private static Throwable capture(Runnable task) {
    try {
      task.run();
      return null;
    } catch (RuntimeException | Error observed) {
      return observed;
    }
  }

  private static final class Fixture implements AutoCloseable {
    final AtomicInteger reads = new AtomicInteger();
    final AtomicInteger rollbacks = new AtomicInteger();
    final AtomicInteger commits = new AtomicInteger();
    final AtomicInteger signals = new AtomicInteger();
    final AtomicInteger closes = new AtomicInteger();
    final AtomicReference<MessageListener> listener = new AtomicReference<>();
    final JMSContext context;
    final BytesMessage message;
    final ArtemisReplyConsumer reply;
    final ArtemisReplyConsumers owner;
    int mode = JMSContext.SESSION_TRANSACTED;

    Fixture(Throwable failure, Throwable rollbackFailure, Throwable notificationFailure) {
      context =
          (JMSContext)
              Proxy.newProxyInstance(
                  JMSContext.class.getClassLoader(),
                  new Class<?>[] {JMSContext.class},
                  (p, m, a) ->
                      switch (m.getName()) {
                        case "getSessionMode" -> mode;
                        case "setAutoStart", "start" -> null;
                        case "createConsumer" ->
                            Proxy.newProxyInstance(
                                JMSConsumer.class.getClassLoader(),
                                new Class<?>[] {JMSConsumer.class},
                                (q, n, b) -> {
                                  if (n.getName().equals("setMessageListener")) {
                                    listener.set((MessageListener) b[0]);
                                    return null;
                                  }
                                  throw new AssertionError("unexpected consumer " + n.getName());
                                });
                        case "rollback" -> {
                          rollbacks.incrementAndGet();
                          if (rollbackFailure != null) throw rollbackFailure;
                          yield null;
                        }
                        case "commit" -> {
                          commits.incrementAndGet();
                          yield null;
                        }
                        case "close" -> {
                          closes.incrementAndGet();
                          yield null;
                        }
                        default -> throw new AssertionError("unexpected context " + m.getName());
                      });
      message =
          (BytesMessage)
              Proxy.newProxyInstance(
                  BytesMessage.class.getClassLoader(),
                  new Class<?>[] {BytesMessage.class},
                  (p, m, a) -> {
                    if (m.getName().equals("getBodyLength")) {
                      reads.incrementAndGet();
                      throw failure;
                    }
                    throw new AssertionError("unexpected message " + m.getName());
                  });
      Clock clock = Clock.fixed(Instant.EPOCH, ZoneOffset.UTC);
      reply =
          new ArtemisReplyConsumer(
              new JmsRequestReplyClient(new ReplyCorrelationRegistry(), clock, 1),
              new JmsReplyDecoder(),
              new ArtemisReplyDlqSender(clock));
      owner =
          ArtemisReplyConsumers.start(
              () -> context,
              reply,
              ignored -> {
                throw new AssertionError("DLQ");
              },
              () -> {
                signals.incrementAndGet();
                if (notificationFailure instanceof RuntimeException runtime) throw runtime;
                if (notificationFailure instanceof Error error) throw error;
              });
      assertNotNull(listener.get());
    }

    @Override
    public void close() {
      owner.close();
      assertEquals(1, closes.get());
    }
  }
}
