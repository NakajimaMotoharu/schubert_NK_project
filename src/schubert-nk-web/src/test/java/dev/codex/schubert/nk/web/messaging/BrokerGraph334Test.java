package dev.codex.schubert.nk.web.messaging;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import jakarta.jms.ConnectionFactory;
import java.lang.reflect.Proxy;
import java.sql.SQLException;
import org.junit.jupiter.api.Test;

/** PT-JMS-FACT334006..008, SS321/354. Public synthetic copy, no connection/session opened. */
final class BrokerGraph334Test {
  @Test
  void fact334006WebOpenPreRedactionAndCopyCleanup() {
    for (boolean supplier : new boolean[] {true, false}) {
      fixed(observeOpen(cycle(), supplier), "Web broker context unavailable");
      Error direct = new AssertionError("direct");
      assertSame(direct, observeOpen(direct, supplier));
    }
    for (boolean supplier : new boolean[] {true, false})
      for (int edge = 0; edge < 4; edge++) {
        Error fatal = new AssertionError("PRIVATE_fixture");
        Throwable observed = observeOpen(graph(edge, fatal), supplier);
        assertTrue(observed == fatal, "FACT334006 fatal before Web redaction");
      }
  }

  private static Throwable observeOpen(Throwable fault, boolean supplierFailure) {
    var copy = new char[] {'P', 'T'};
    int[] reads = {0};
    int[] creates = {0};
    int[] closes = {0};
    int[] arity = {0};
    int[] unexpected = {0};
    Object[] roleAndMode = new Object[2];
    ConnectionFactory factory =
        (ConnectionFactory)
            Proxy.newProxyInstance(
                ConnectionFactory.class.getClassLoader(),
                new Class<?>[] {ConnectionFactory.class},
                (p, m, a) -> {
                  if (m.getName().equals("createContext")) {
                    creates[0]++;
                    arity[0] = a == null ? 0 : a.length;
                    roleAndMode[0] = a != null && a.length > 0 ? a[0] : null;
                    roleAndMode[1] = a != null && a.length > 2 ? a[2] : null;
                    raise(fault);
                    throw new AssertionError("thrower must not return");
                  }
                  unexpected[0]++;
                  throw new AssertionError("unexpected factory " + m.getName());
                });
    Throwable observed;
    try (var owner =
        new WebBrokerContexts(
            () -> {
              reads[0]++;
              if (supplierFailure) raise(fault);
              return copy;
            },
            factory,
            () -> closes[0]++)) {
      observed = capture(() -> owner.contexts().open());
      assertEquals(1, reads[0]);
      assertEquals(supplierFailure ? 0 : 1, creates[0]);
      assertEquals(0, unexpected[0]);
      if (!supplierFailure) {
        assertEquals(3, arity[0]);
        assertEquals("nk_web", roleAndMode[0]);
        assertEquals(0, roleAndMode[1]);
      }
      assertArrayEquals(supplierFailure ? new char[] {'P', 'T'} : new char[] {0, 0}, copy);
      assertEquals(0, closes[0]);
    }
    assertEquals(1, closes[0]);
    return observed;
  }

  @Test
  void fact334007WebCloseTraversesLinkedGraphAndRetainsRetryPhase() {
    fixed(observeClose(cycle()), "Web broker factory close failed");
    for (int edge = 0; edge < 4; edge++) {
      Error fatal = new AssertionError("close fatal");
      Throwable observed = observeClose(graph(edge, fatal));
      assertTrue(observed == fatal, "FACT334007 Web linked graph after owned close");
    }
  }

  private static Throwable observeClose(Throwable failure) {
    int[] reads = {0};
    int[] closes = {0};
    Throwable[] fault = {failure};
    ConnectionFactory factory =
        (ConnectionFactory)
            Proxy.newProxyInstance(
                ConnectionFactory.class.getClassLoader(),
                new Class<?>[] {ConnectionFactory.class},
                (p, m, a) -> {
                  throw new AssertionError("no factory I/O " + m.getName());
                });
    var owner =
        new WebBrokerContexts(
            () -> {
              reads[0]++;
              throw new AssertionError("no credential access");
            },
            factory,
            () -> {
              closes[0]++;
              if (fault[0] != null) raise(fault[0]);
            });
    Throwable observed = capture(owner::close);
    assertEquals(1, closes[0]);
    fixed(
        assertThrows(IllegalStateException.class, () -> owner.contexts().open()),
        "Web broker context unavailable");
    assertEquals(0, reads[0]);
    fault[0] = null;
    owner.close();
    owner.close();
    assertEquals(2, closes[0]);
    return observed;
  }

  @Test
  void fact334008WebFactoryNoSuppSecondaryAfterOwnedClose() {
    for (int edge = 0; edge < 4; edge++) {
      var probe = new WebBrokerFactoryOwnershipTest.ProbeFactory();
      try {
        Error fatal = new AssertionError("factory close fatal");
        probe.failAt = 1;
        probe.primary = new NoSuppRuntime();
        probe.closeFailure = graph(edge, fatal);
        Throwable observed = capture(() -> WebBrokerContexts.configureOwned(() -> probe));
        assertEquals(java.util.List.of("callTimeout=2000"), probe.settings);
        assertEquals(1, probe.closes);
        assertTrue(observed == fatal, "FACT334008 Web factory graph after owned close");
      } finally {
        probe.dispose();
      }
    }
  }

  private static RuntimeException graph(int edge, Error fatal) {
    return switch (edge) {
      case 0 -> new IllegalStateException("PRIVATE_cause", fatal);
      case 1 -> {
        var e = new IllegalStateException("PRIVATE_suppressed");
        e.addSuppressed(fatal);
        yield e;
      }
      case 2 -> {
        var e = new jakarta.jms.JMSException("PRIVATE_linked");
        e.setLinkedException(new IllegalStateException("fatal", fatal));
        yield new IllegalStateException("provider", e);
      }
      case 3 -> {
        var e = new SQLException("PRIVATE_sql");
        e.setNextException(new SQLException("next", fatal));
        yield new IllegalStateException("sql graph", e);
      }
      default -> throw new AssertionError("fixture edge");
    };
  }

  private static RuntimeException cycle() {
    var e = new IllegalStateException("PRIVATE_cycle");
    e.initCause(new IllegalStateException("cycle", e));
    return e;
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

  private static void fixed(Throwable observed, String message) {
    assertEquals(IllegalStateException.class, observed.getClass());
    assertEquals(message, observed.getMessage());
    assertNull(observed.getCause());
    assertEquals(0, observed.getSuppressed().length);
  }

  private static final class NoSuppRuntime extends RuntimeException {
    @java.io.Serial private static final long serialVersionUID = 1L;

    NoSuppRuntime() {
      super("public synthetic fixture", null, false, false);
    }
  }
}
