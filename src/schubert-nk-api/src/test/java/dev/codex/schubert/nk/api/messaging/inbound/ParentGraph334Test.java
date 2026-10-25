package dev.codex.schubert.nk.api.messaging.inbound;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

import jakarta.jms.JMSConsumer;
import jakarta.jms.JMSContext;
import java.lang.reflect.Proxy;
import java.sql.SQLException;
import java.time.Clock;
import java.time.Instant;
import java.time.ZoneOffset;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import org.junit.jupiter.api.Test;

/** PT-JMS-FACT334005, SS321/354. Public ordinary assembly, all contexts are interface proxies. */
final class ParentGraph334Test {
  @Test
  void fact334005ParentNotificationAndGroupCloseAfterCleanup() {
    for (int edge = 0; edge < 4; edge++) {
      var f = new Fixture();
      var primary = new NoSuppRuntime();
      Error fatal = new AssertionError("notification fatal");
      Throwable notification = graph(edge, fatal);
      Throwable observed =
          capture(
              () ->
                  ApiMessagingRuntime.start(
                      () -> f.context(),
                      () -> {
                        f.logAcquires++;
                        throw primary;
                      },
                      () -> {
                        f.asyncAcquires++;
                        throw new AssertionError("not acquired");
                      },
                      ignored -> {
                        f.business++;
                        throw new AssertionError("business");
                      },
                      ignored -> {
                        f.business++;
                      },
                      ignored -> {
                        f.business++;
                      },
                      clock(),
                      ignored -> {
                        throw new AssertionError("DLQ");
                      },
                      () -> {
                        f.signals++;
                        raise(notification);
                      }));
      assertEquals(4, f.created);
      assertEquals(4, f.started);
      assertEquals(1, f.logAcquires);
      assertEquals(0, f.asyncAcquires);
      assertEquals(1, f.signals);
      assertEquals(0, f.business);
      assertEquals(List.of(0, 1, 2, 3), f.closeOrder);
      assertTrue(observed == fatal, "FACT334005 parent notification after cleanup");
    }
    for (int edge = 0; edge < 4; edge++) {
      var f = new Fixture();
      Error fatal = new AssertionError("late group fatal");
      var owner =
          ApiMessagingRuntime.start(
              () -> f.context(),
              () -> f.context(),
              () -> f.context(),
              ignored -> {
                f.business++;
                throw new AssertionError("business");
              },
              ignored -> {
                f.business++;
              },
              ignored -> {
                f.business++;
              },
              clock(),
              ignored -> {
                throw new AssertionError("DLQ");
              },
              () -> f.signals++);
      f.closeFaults[5] = new NoSuppRuntime();
      f.closeFaults[4] = graph(edge, fatal);
      Throwable observed = capture(owner::close);
      assertEquals(6, f.created);
      assertEquals(6, f.started);
      assertEquals(0, f.signals);
      assertEquals(0, f.business);
      assertEquals(List.of(5, 4, 0, 1, 2, 3), f.closeOrder);
      assertFalse(owner.ready());
      Arrays.fill(f.closeFaults, null);
      owner.close();
      owner.close();
      assertEquals(List.of(5, 4, 0, 1, 2, 3, 5, 4), f.closeOrder);
      assertTrue(observed == fatal, "FACT334005 late group graph after all owned close");
    }
  }

  private static Clock clock() {
    return Clock.fixed(Instant.EPOCH, ZoneOffset.UTC);
  }

  private static RuntimeException graph(int edge, Error fatal) {
    return switch (edge) {
      case 0 -> new IllegalStateException("cause", fatal);
      case 1 -> {
        var e = new IllegalStateException("suppressed");
        e.addSuppressed(fatal);
        yield e;
      }
      case 2 -> {
        var e = new jakarta.jms.JMSException("linked");
        e.setLinkedException(new IllegalStateException("fatal", fatal));
        yield new IllegalStateException("provider", e);
      }
      case 3 -> {
        var e = new SQLException("sql");
        e.setNextException(new SQLException("next", fatal));
        yield new IllegalStateException("sql graph", e);
      }
      default -> throw new AssertionError("fixture edge");
    };
  }

  private static void raise(Throwable failure) {
    if (failure instanceof RuntimeException r) throw r;
    throw (Error) failure;
  }

  private static Throwable capture(Runnable task) {
    try {
      task.run();
      return null;
    } catch (RuntimeException | Error failure) {
      return failure;
    }
  }

  private static final class NoSuppRuntime extends RuntimeException {
    @java.io.Serial private static final long serialVersionUID = 1L;

    NoSuppRuntime() {
      super("public synthetic fixture", null, false, false);
    }
  }

  private static final class Fixture {
    final List<Integer> closeOrder = new ArrayList<>();
    final Throwable[] closeFaults = new Throwable[6];
    int created;
    int started;
    int logAcquires;
    int asyncAcquires;
    int signals;
    int business;

    JMSContext context() {
      int index = created++;
      return (JMSContext)
          Proxy.newProxyInstance(
              JMSContext.class.getClassLoader(),
              new Class<?>[] {JMSContext.class},
              (p, m, a) ->
                  switch (m.getName()) {
                    case "getSessionMode" -> 0;
                    case "setAutoStart" -> null;
                    case "createConsumer" ->
                        Proxy.newProxyInstance(
                            JMSConsumer.class.getClassLoader(),
                            new Class<?>[] {JMSConsumer.class},
                            (q, n, b) -> {
                              if (n.getName().equals("setMessageListener")) {
                                assertNotNull(b[0]);
                                return null;
                              }
                              throw new AssertionError("unexpected consumer " + n.getName());
                            });
                    case "start" -> {
                      started++;
                      yield null;
                    }
                    case "close" -> {
                      closeOrder.add(index);
                      if (closeFaults[index] != null) raise(closeFaults[index]);
                      yield null;
                    }
                    default -> throw new AssertionError("unexpected context " + m.getName());
                  });
    }
  }
}
