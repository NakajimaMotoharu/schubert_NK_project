package dev.codex.schubert.nk.web.messaging;

import static org.junit.jupiter.api.Assertions.assertEquals;
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
import java.util.List;
import org.junit.jupiter.api.Test;

/** SS321/354 SSC333; PT-JMS-CLEAN333005..006. Pure local ownership/exception fixtures. */
final class ReplyCleanup333Test {
  @Test
  void clean333005ReplyStartupNoSuppSecondaryAfterSingleClose() {
    for (int edge = 0; edge < 5; edge++) {
      Error fatal = new AssertionError("PRIVATE_fixture_only");
      var f = new Fixture(new NoSuppRuntime(), graph(edge, fatal));
      Throwable observed = capture(f::start);
      f.prove();
      assertTrue(observed == fatal, "CONS333-5 reply secondary after close");
    }
  }

  @Test
  void clean333006ReplyDirectPrimaryCloseAndOrdinaryCatalogRemain() {
    for (int mode = 0; mode < 3; mode++) {
      Error primary = new AssertionError("primary");
      Throwable closing =
          switch (mode) {
            case 0 -> primary;
            case 1 -> new AssertionError("closing");
            default -> new IllegalStateException("closing");
          };
      var f = new Fixture(primary, closing);
      Throwable observed = capture(f::start);
      f.prove();
      assertSame(primary, observed);
      assertEquals(mode == 0 ? 0 : 1, primary.getSuppressed().length);
    }
    var primary = new IllegalStateException("ordinary");
    Error directClose = new AssertionError("close fatal");
    var direct = new Fixture(primary, directClose);
    Throwable observed = capture(direct::start);
    direct.prove();
    assertSame(directClose, observed);
    assertSame(directClose, primary.getSuppressed()[0]);

    for (boolean same : new boolean[] {false, true}) {
      var ordinary = new IllegalStateException("primary ordinary");
      Throwable closing = same ? ordinary : new IllegalStateException("secondary ordinary");
      var f = new Fixture(ordinary, closing);
      Throwable failure = capture(f::start);
      f.prove();
      assertEquals(IllegalStateException.class, failure.getClass());
      assertEquals("Web reply consumer startup failed", failure.getMessage());
      assertSame(ordinary, failure.getCause());
      assertEquals(1, ordinary.getSuppressed().length);
      assertEquals("Web reply consumer close failed", ordinary.getSuppressed()[0].getMessage());
      assertSame(closing, ordinary.getSuppressed()[0].getCause());
    }
    var noSupp = new NoSuppRuntime();
    var disabled = new Fixture(noSupp, new IllegalStateException("ordinary close"));
    Throwable fixed = capture(disabled::start);
    disabled.prove();
    assertEquals("Web reply consumer startup failed", fixed.getMessage());
    assertSame(noSupp, fixed.getCause());
    assertEquals(0, noSupp.getSuppressed().length);
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
      case 4 -> fatal;
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
      super("private fixture", null, false, false);
    }
  }

  private static final class Fixture {
    final List<String> order = new ArrayList<>();
    final Throwable primary;
    final Throwable closing;
    final JMSContext context;
    int opens;
    int starts;
    int closes;
    int signals;

    Fixture(Throwable primary, Throwable closing) {
      this.primary = primary;
      this.closing = closing;
      context =
          (JMSContext)
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
                          order.add("start");
                          throw primary;
                        }
                        case "close" -> {
                          closes++;
                          order.add("close");
                          if (closing != null) throw closing;
                          yield null;
                        }
                        default -> throw new AssertionError("unexpected context " + m.getName());
                      });
    }

    void start() {
      Clock clock = Clock.fixed(Instant.EPOCH, ZoneOffset.UTC);
      var reply =
          new ArtemisReplyConsumer(
              new JmsRequestReplyClient(new ReplyCorrelationRegistry(), clock, 1),
              new JmsReplyDecoder(),
              new ArtemisReplyDlqSender(clock));
      ArtemisReplyConsumers.start(
          () -> {
            opens++;
            return context;
          },
          reply,
          ignored -> {
            throw new AssertionError("DLQ");
          },
          () -> signals++);
    }

    void prove() {
      assertEquals(1, opens);
      assertEquals(1, starts);
      assertEquals(1, closes);
      assertEquals(0, signals);
      assertEquals(List.of("start", "close"), order);
    }
  }
}
