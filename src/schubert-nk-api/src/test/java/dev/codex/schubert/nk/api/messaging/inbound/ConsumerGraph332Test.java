package dev.codex.schubert.nk.api.messaging.inbound;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import jakarta.jms.BytesMessage;
import jakarta.jms.JMSConsumer;
import jakarta.jms.JMSContext;
import jakarta.jms.JMSException;
import jakarta.jms.MessageListener;
import java.lang.reflect.Proxy;
import java.sql.SQLException;
import java.time.Clock;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.Test;

/** PT-JMS-CONS332001..004: independent finite interface fixtures, SS321/354 SSC332. */
final class ConsumerGraph332Test {
  @Test
  void cons332001SyncCannotRetryConfirmedRollbackWithFatalGraph() throws Exception {
    graphCases(0);
  }

  @Test
  void cons332002WebLogCannotRetryConfirmedRollbackWithFatalGraph() throws Exception {
    graphCases(1);
  }

  @Test
  void cons332003QuestionCannotRetryConfirmedRollbackWithFatalGraph() throws Exception {
    graphCases(2);
  }

  private static void graphCases(int kind) throws Exception {
    for (int edge = 0; edge < 4; edge++) {
      var fatal = new AssertionError("PRIVATE_fixture_only");
      Throwable failure = graph(edge, fatal);
      try (var f = new Fixture(kind, failure)) {
        assertDoesNotThrow(() -> f.listeners.getFirst().onMessage(f.message));
        assertEquals(1, f.reads.get());
        assertEquals(1, f.rollbacks.get());
        assertEquals(0, f.commits.get());
        assertEquals(0, f.business.get());
        assertTrue(!f.ready() && f.signals.get() == 1);
        for (MessageListener listener : f.listeners) listener.onMessage(f.message);
        assertEquals(1, f.reads.get());
        assertEquals(1, f.rollbacks.get());
        assertEquals(1, f.signals.get());
      }
    }
  }

  @Test
  void cons332004OrdinaryCyclesRetryAndDirectFatalKeepsApiNotificationPolicy() throws Exception {
    for (int kind = 0; kind < 3; kind++) {
      var first = new IllegalStateException("ordinary");
      var second = new IllegalStateException("cycle");
      first.initCause(second);
      second.initCause(first);
      first.addSuppressed(second);
      try (var f = new Fixture(kind, first)) {
        f.listeners.getFirst().onMessage(f.message);
        f.listeners.getFirst().onMessage(f.message);
        assertTrue(f.ready());
        assertEquals(0, f.signals.get());
        assertEquals(2, f.reads.get());
        assertEquals(2, f.rollbacks.get());
        assertEquals(0, f.commits.get());
        assertEquals(0, f.business.get());
      }
      try (var f = new Fixture(kind, new AssertionError("direct"))) {
        assertDoesNotThrow(() -> f.listeners.getFirst().onMessage(f.message));
        assertFalse(f.ready());
        assertEquals(1, f.signals.get());
        assertEquals(1, f.rollbacks.get());
        assertEquals(0, f.commits.get());
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

  private static final class Fixture implements AutoCloseable {
    final List<MessageListener> listeners = new ArrayList<>();
    final AtomicInteger reads = new AtomicInteger();
    final AtomicInteger rollbacks = new AtomicInteger();
    final AtomicInteger commits = new AtomicInteger();
    final AtomicInteger business = new AtomicInteger();
    final AtomicInteger signals = new AtomicInteger();
    final AtomicInteger closes = new AtomicInteger();
    final BytesMessage message;
    final AutoCloseable owner;
    final int kind;

    Fixture(int kind, Throwable failure) {
      this.kind = kind;
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
      java.util.function.Supplier<JMSContext> factory =
          () ->
              (JMSContext)
                  Proxy.newProxyInstance(
                      JMSContext.class.getClassLoader(),
                      new Class<?>[] {JMSContext.class},
                      (p, m, a) ->
                          switch (m.getName()) {
                            case "getSessionMode" -> JMSContext.SESSION_TRANSACTED;
                            case "setAutoStart", "start" -> null;
                            case "createConsumer" ->
                                Proxy.newProxyInstance(
                                    JMSConsumer.class.getClassLoader(),
                                    new Class<?>[] {JMSConsumer.class},
                                    (q, n, b) -> {
                                      if (n.getName().equals("setMessageListener")) {
                                        listeners.add((MessageListener) b[0]);
                                        return null;
                                      }
                                      throw new AssertionError(
                                          "unexpected consumer " + n.getName());
                                    });
                            case "rollback" -> {
                              rollbacks.incrementAndGet();
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
                            default ->
                                throw new AssertionError("unexpected context " + m.getName());
                          });
      Clock clock = Clock.fixed(java.time.Instant.EPOCH, java.time.ZoneOffset.UTC);
      owner =
          switch (kind) {
            case 0 ->
                SyncRequestConsumers.start(
                    factory,
                    new SyncRequestListener(
                        ignored -> {
                          business.incrementAndGet();
                          throw new AssertionError("business");
                        },
                        clock),
                    ignored -> {
                      throw new AssertionError("DLQ");
                    },
                    signals::incrementAndGet);
            case 1 ->
                WebLogConsumers.start(
                    factory,
                    new WebLogListener(ignored -> business.incrementAndGet(), clock),
                    ignored -> {
                      throw new AssertionError("DLQ");
                    },
                    signals::incrementAndGet);
            case 2 ->
                QuestionWorkConsumers.start(
                    factory,
                    new QuestionWorkListener(ignored -> business.incrementAndGet(), clock),
                    ignored -> {
                      throw new AssertionError("DLQ");
                    },
                    signals::incrementAndGet);
            default -> throw new AssertionError("fixture kind");
          };
      assertEquals(kind == 0 ? 4 : 1, listeners.size());
    }

    boolean ready() {
      return switch (kind) {
        case 0 -> ((SyncRequestConsumers) owner).ready();
        case 1 -> ((WebLogConsumers) owner).ready();
        default -> ((QuestionWorkConsumers) owner).ready();
      };
    }

    @Override
    public void close() {
      switch (kind) {
        case 0 -> ((SyncRequestConsumers) owner).close();
        case 1 -> ((WebLogConsumers) owner).close();
        default -> ((QuestionWorkConsumers) owner).close();
      }
      assertEquals(kind == 0 ? 4 : 1, closes.get());
    }
  }
}
