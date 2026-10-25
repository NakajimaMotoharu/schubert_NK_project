package dev.codex.schubert.nk.api.messaging.inbound;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertSame;
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
import java.util.function.Supplier;
import org.junit.jupiter.api.Test;

/** SS321/354 SSC333; PT-JMS-CLEAN333001..004. No broker, DB, native or external owner. */
final class ConsumerCleanup333Test {
  @Test
  void clean333001SyncStartupSecondaryAfterEveryOwnedClose() {
    startupCases(0);
  }

  @Test
  void clean333002WebLogStartupSecondaryAfterOwnedClose() {
    startupCases(1);
  }

  @Test
  void clean333003QuestionStartupSecondaryAfterOwnedClose() {
    startupCases(2);
  }

  private static void startupCases(int kind) {
    controls(kind);
    for (int point = 0; point < 2; point++) {
      for (int edge = 0; edge < 4; edge++) {
        Error fatal = new AssertionError("PRIVATE_fixture_only");
        Throwable secondary = graph(edge, fatal);
        var f = new Fixture(kind, new NoSuppRuntime(), point == 0 ? secondary : null);
        if (point == 1) Arrays.fill(f.closeFaults, secondary);
        Throwable observed = capture(() -> f.open());
        f.proveStartup();
        assertTrue(observed == fatal, "CONS333-" + kind + " startup secondary after all closes");
      }
    }
  }

  private static void controls(int kind) {
    var ordinary = new NoSuppRuntime();
    var normal = new Fixture(kind, ordinary, null);
    Throwable first = capture(() -> normal.open());
    normal.proveStartup();
    assertEquals(IllegalStateException.class, first.getClass());
    assertSame(ordinary, first.getCause());
    assertEquals(0, ordinary.getSuppressed().length);
    assertEquals(startupMessage(kind), first.getMessage());

    var primary = new IllegalStateException("primary");
    var notification = new IllegalStateException("notification");
    var closing = new IllegalStateException("closing");
    var retained = new Fixture(kind, primary, notification);
    Arrays.fill(retained.closeFaults, closing);
    Throwable second = capture(() -> retained.open());
    retained.proveStartup();
    assertEquals(IllegalStateException.class, second.getClass());
    assertSame(primary, second.getCause());
    assertEquals(2, primary.getSuppressed().length);
    assertSame(notification, primary.getSuppressed()[0]);
    assertEquals(closeMessage(kind), primary.getSuppressed()[1].getMessage());
    assertSame(closing, primary.getSuppressed()[1].getCause());

    for (boolean same : new boolean[] {false, true}) {
      Error direct = new AssertionError("primary fatal");
      Error notifyFatal = new AssertionError("notify fatal");
      Error closeFatal = same ? direct : new AssertionError("close fatal");
      var directCase = new Fixture(kind, direct, notifyFatal);
      Arrays.fill(directCase.closeFaults, closeFatal);
      Throwable third = capture(() -> directCase.open());
      directCase.proveStartup();
      assertSame(direct, third);
      assertArrayEquals(
          same ? new Throwable[] {notifyFatal} : new Throwable[] {notifyFatal, closeFatal},
          direct.getSuppressed());
    }
    Error directClose = new AssertionError("direct close");
    var closePriority = new Fixture(kind, new NoSuppRuntime(), null);
    Arrays.fill(closePriority.closeFaults, directClose);
    Throwable fourth = capture(() -> closePriority.open());
    closePriority.proveStartup();
    assertSame(directClose, fourth);
  }

  @Test
  void clean333004SyncMultiClosePreservesDeferredFatalAndSuccessfulPhases() {
    for (int edge = 0; edge < 4; edge++) {
      var f = new Fixture(0, null, null);
      Error fatal = new AssertionError("secondary close fatal");
      f.closeFaults[0] = new NoSuppRuntime();
      f.closeFaults[1] = graph(edge, fatal);
      var owner = (SyncRequestConsumers) f.open();
      assertEquals(4, f.opens);
      assertEquals(4, f.starts);
      Throwable observed = capture(owner::close);
      assertEquals(List.of(0, 1, 2, 3), f.closeOrder);
      assertArrayEquals(new int[] {1, 1, 1, 1}, f.closeCounts);
      assertEquals(0, f.signals);
      assertEquals(0, f.business);
      assertTrue(observed == fatal, "CONS333-4 deferred fatal after four closes");
      assertFalse(owner.ready());
      Arrays.fill(f.closeFaults, null);
      owner.close();
      assertArrayEquals(new int[] {2, 2, 1, 1}, f.closeCounts);
      assertEquals(List.of(0, 1, 2, 3, 0, 1), f.closeOrder);
      owner.close();
      assertArrayEquals(new int[] {2, 2, 1, 1}, f.closeCounts);
    }
  }

  private static String startupMessage(int kind) {
    return switch (kind) {
      case 0 -> "API sync consumer startup failed";
      case 1 -> "API Web log consumer startup failed";
      default -> "API Question consumer startup failed";
    };
  }

  private static String closeMessage(int kind) {
    return switch (kind) {
      case 0 -> "API sync consumer close failed";
      case 1 -> "API Web log consumer close failed";
      default -> "API Question consumer close failed";
    };
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

  private static Throwable capture(Runnable task) {
    try {
      task.run();
      return null;
    } catch (RuntimeException | Error failure) {
      return failure;
    }
  }

  private static final class NoSuppRuntime extends RuntimeException {
    private static final long serialVersionUID = 1L;

    NoSuppRuntime() {
      super("ordinary private fixture", null, false, false);
    }
  }

  private static final class Fixture {
    final int kind;
    final Throwable startupFailure;
    final Throwable notificationFailure;
    final Throwable[] closeFaults;
    final int[] closeCounts;
    final List<Integer> closeOrder = new ArrayList<>();
    int opens;
    int starts;
    int signals;
    int business;

    Fixture(int kind, Throwable startupFailure, Throwable notificationFailure) {
      this.kind = kind;
      this.startupFailure = startupFailure;
      this.notificationFailure = notificationFailure;
      closeFaults = new Throwable[kind == 0 ? 4 : 1];
      closeCounts = new int[closeFaults.length];
    }

    AutoCloseable open() {
      Supplier<JMSContext> factory =
          () -> {
            int index = opens++;
            return (JMSContext)
                Proxy.newProxyInstance(
                    JMSContext.class.getClassLoader(),
                    new Class<?>[] {JMSContext.class},
                    (p, m, a) ->
                        switch (m.getName()) {
                          case "getSessionMode" -> JMSContext.SESSION_TRANSACTED;
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
                            starts++;
                            if (startupFailure != null) throw startupFailure;
                            yield null;
                          }
                          case "close" -> {
                            if (startupFailure != null)
                              assertEquals(1, signals, "startup stop precedes drain");
                            closeOrder.add(index);
                            closeCounts[index]++;
                            if (closeFaults[index] != null) throw closeFaults[index];
                            yield null;
                          }
                          default -> throw new AssertionError("unexpected context " + m.getName());
                        });
          };
      Runnable onFatal =
          () -> {
            signals++;
            if (notificationFailure instanceof RuntimeException runtime) throw runtime;
            if (notificationFailure instanceof Error error) throw error;
          };
      Clock clock = Clock.fixed(Instant.EPOCH, ZoneOffset.UTC);
      return switch (kind) {
        case 0 ->
            SyncRequestConsumers.start(
                factory,
                new SyncRequestListener(
                    ignored -> {
                      business++;
                      throw new AssertionError("business");
                    },
                    clock),
                ignored -> {
                  throw new AssertionError("DLQ");
                },
                onFatal);
        case 1 ->
            WebLogConsumers.start(
                factory,
                new WebLogListener(
                    ignored -> {
                      business++;
                      throw new AssertionError("business");
                    },
                    clock),
                ignored -> {
                  throw new AssertionError("DLQ");
                },
                onFatal);
        case 2 ->
            QuestionWorkConsumers.start(
                factory,
                new QuestionWorkListener(
                    ignored -> {
                      business++;
                      throw new AssertionError("business");
                    },
                    clock),
                ignored -> {
                  throw new AssertionError("DLQ");
                },
                onFatal);
        default -> throw new AssertionError("fixture kind");
      };
    }

    void proveStartup() {
      assertEquals(kind == 0 ? 4 : 1, opens);
      assertEquals(1, starts);
      assertEquals(1, signals);
      assertEquals(0, business);
      assertEquals(kind == 0 ? List.of(0, 1, 2, 3) : List.of(0), closeOrder);
      assertArrayEquals(kind == 0 ? new int[] {1, 1, 1, 1} : new int[] {1}, closeCounts);
    }
  }
}
