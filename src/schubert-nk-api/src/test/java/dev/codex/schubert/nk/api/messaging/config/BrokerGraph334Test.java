package dev.codex.schubert.nk.api.messaging.config;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import jakarta.jms.ConnectionFactory;
import java.lang.reflect.Proxy;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import org.junit.jupiter.api.Test;

/** PT-JMS-FACT334001..004; SS321/354. Public synthetic copy and unconnected owned fixtures. */
final class BrokerGraph334Test {
  @Test
  void fact334001ApiOpenPreRedactionAndCopyCleanup() {
    for (boolean supplier : new boolean[] {true, false}) {
      fixed(observeOpen(cycle(), supplier, 0), "API broker context unavailable");
      Error direct = new AssertionError("direct fixture");
      assertSame(direct, observeOpen(direct, supplier, 0));
    }
    for (int profile = 0; profile < 3; profile++)
      for (boolean supplier : new boolean[] {true, false})
        for (int edge = 0; edge < 4; edge++) {
          Error fatal = new AssertionError("PRIVATE_fixture");
          Throwable observed = observeOpen(graph(edge, fatal), supplier, profile);
          assertTrue(observed == fatal, "FACT334001 fatal before API redaction");
        }
  }

  private static Throwable observeOpen(Throwable fault, boolean supplierFailure, int profile) {
    var copy = new char[] {'P', 'T'};
    int[] reads = {0};
    int[] creates = new int[3];
    int[] closes = new int[3];
    int[] arities = new int[3];
    int[] unexpected = {0};
    Object[] roles = new Object[3];
    Object[] modes = new Object[3];
    var order = new ArrayList<Integer>();
    ConnectionFactory[] factories = new ConnectionFactory[3];
    for (int i = 0; i < 3; i++) {
      final int index = i;
      factories[i] =
          (ConnectionFactory)
              Proxy.newProxyInstance(
                  ConnectionFactory.class.getClassLoader(),
                  new Class<?>[] {ConnectionFactory.class},
                  (p, m, a) -> {
                    if (m.getName().equals("createContext")) {
                      creates[index]++;
                      arities[index] = a == null ? 0 : a.length;
                      roles[index] = a != null && a.length > 0 ? a[0] : null;
                      modes[index] = a != null && a.length > 2 ? a[2] : null;
                      raise(fault);
                      throw new AssertionError("thrower must not return");
                    }
                    unexpected[0]++;
                    throw new AssertionError("unexpected factory " + m.getName());
                  });
    }
    Throwable observed;
    try (var owner =
        new ApiBrokerContexts(
            () -> {
              reads[0]++;
              if (supplierFailure) raise(fault);
              return copy;
            },
            factories[0],
            factories[1],
            factories[2],
            () -> {
              closes[0]++;
              order.add(0);
            },
            () -> {
              closes[1]++;
              order.add(1);
            },
            () -> {
              closes[2]++;
              order.add(2);
            })) {
      observed =
          capture(
              () -> {
                switch (profile) {
                  case 0 -> owner.sync().get();
                  case 1 -> owner.webLog().get();
                  case 2 -> owner.async().get();
                  default -> throw new AssertionError("fixture profile");
                }
              });
      assertEquals(1, reads[0]);
      int[] expected = new int[3];
      if (!supplierFailure) expected[profile] = 1;
      assertArrayEquals(expected, creates);
      assertEquals(0, unexpected[0]);
      if (!supplierFailure) {
        assertEquals(3, arities[profile]);
        assertEquals("nk_api", roles[profile]);
        assertEquals(0, modes[profile]);
      }
      assertArrayEquals(supplierFailure ? new char[] {'P', 'T'} : new char[] {0, 0}, copy);
      assertArrayEquals(new int[] {0, 0, 0}, closes);
      assertEquals(List.of(), order);
    }
    assertArrayEquals(new int[] {1, 1, 1}, closes);
    assertEquals(List.of(2, 1, 0), order);
    return observed;
  }

  @Test
  void fact334002ApiMultiOwnerCloseRetainsLateGraphAndSuccessfulPhases() {
    fixed(
        observeClose(cycle(), new IllegalStateException("ordinary")),
        "API broker factory close failed");
    for (int edge = 0; edge < 4; edge++) {
      Error fatal = new AssertionError("late fatal");
      Throwable observed = observeClose(new NoSuppRuntime(), graph(edge, fatal));
      assertTrue(observed == fatal, "FACT334002 late API graph after all close attempts");
    }
  }

  private static Throwable observeClose(Throwable first, Throwable second) {
    int[] closes = new int[3];
    int[] reads = {0};
    var order = new ArrayList<Integer>();
    Throwable[] faults = {null, second, first};
    var owner =
        new ApiBrokerContexts(
            () -> {
              reads[0]++;
              throw new AssertionError("no copy acquired");
            },
            inertFactory(),
            inertFactory(),
            inertFactory(),
            () -> {
              closes[0]++;
              order.add(0);
              if (faults[0] != null) raise(faults[0]);
            },
            () -> {
              closes[1]++;
              order.add(1);
              if (faults[1] != null) raise(faults[1]);
            },
            () -> {
              closes[2]++;
              order.add(2);
              if (faults[2] != null) raise(faults[2]);
            });
    Throwable observed = capture(owner::close);
    assertArrayEquals(new int[] {1, 1, 1}, closes);
    assertEquals(List.of(2, 1, 0), order);
    fixed(
        assertThrows(IllegalStateException.class, () -> owner.sync().get()),
        "API broker context unavailable");
    assertEquals(0, reads[0]);
    Arrays.fill(faults, null);
    owner.close();
    owner.close();
    assertArrayEquals(new int[] {1, 2, 2}, closes);
    assertEquals(List.of(2, 1, 0, 2, 1), order);
    return observed;
  }

  private static ConnectionFactory inertFactory() {
    return (ConnectionFactory)
        Proxy.newProxyInstance(
            ConnectionFactory.class.getClassLoader(),
            new Class<?>[] {ConnectionFactory.class},
            (p, m, a) -> {
              throw new AssertionError("no factory I/O " + m.getName());
            });
  }

  @Test
  void fact334003ApiPartialConstructionClassifiesOnlyUnretainedSecondaryAfterAllClose() {
    var primary = new IllegalStateException("raw primary");
    var log = new AssertionError("direct close");
    var sync = new IllegalStateException("second close");
    assertSame(primary, partial(primary, log, sync));
    assertArrayEquals(new Throwable[] {log, sync}, primary.getSuppressed());
    var same = new NoSuppRuntime();
    assertSame(same, partial(same, same, same));
    assertEquals(0, same.getSuppressed().length);
    for (int edge = 0; edge < 4; edge++) {
      Error first = new AssertionError("first reverse close");
      Error second = new AssertionError("later close");
      Throwable observed = partial(new NoSuppRuntime(), graph(edge, first), graph(edge, second));
      assertTrue(observed == first, "FACT334003 unretained graph after reverse partial close");
    }
  }

  private static Throwable partial(Throwable primary, Throwable logFailure, Throwable syncFailure) {
    var order = new ArrayList<Integer>();
    var sync = new OrderedProbe(0, order);
    var log = new OrderedProbe(1, order);
    sync.closeFailure = syncFailure;
    log.closeFailure = logFailure;
    int[] reads = {0};
    var profiles = new ArrayList<ArtemisConnectionFactoryProvider.ConsumerProfile>();
    var endpoints = new ArrayList<String>();
    try {
      Throwable observed =
          capture(
              () ->
                  ApiBrokerContexts.createOwned(
                      () -> {
                        reads[0]++;
                        throw new AssertionError("no credential access");
                      },
                      "tcp://127.0.0.1:61616",
                      (profile, endpoint) -> {
                        endpoints.add(endpoint);
                        profiles.add(profile);
                        if (profiles.size() == 1) return sync;
                        if (profiles.size() == 2) return log;
                        raise(primary);
                        throw new AssertionError("thrower must not return");
                      },
                      false));
      assertEquals(
          List.of(
              ArtemisConnectionFactoryProvider.ConsumerProfile.SYNC,
              ArtemisConnectionFactoryProvider.ConsumerProfile.WEB_LOG,
              ArtemisConnectionFactoryProvider.ConsumerProfile.ASYNC),
          profiles);
      assertEquals(java.util.Collections.nCopies(3, "tcp://127.0.0.1:61616"), endpoints);
      assertEquals(0, reads[0]);
      assertEquals(1, sync.closes);
      assertEquals(1, log.closes);
      assertEquals(List.of(1, 0), order);
      return observed;
    } finally {
      sync.dispose();
      log.dispose();
    }
  }

  @Test
  void fact334004ApiFactoryNoSuppSecondaryAfterOwnedClose() {
    for (int edge = 0; edge < 4; edge++) {
      var probe = new ApiFactoryOwnershipTest.ProbeFactory();
      try {
        Error fatal = new AssertionError("factory close fatal");
        probe.failAt = 1;
        probe.primary = new NoSuppRuntime();
        probe.closeFailure = graph(edge, fatal);
        Throwable observed =
            capture(
                () ->
                    ArtemisConnectionFactoryProvider.configureOwned(
                        ArtemisConnectionFactoryProvider.ConsumerProfile.SYNC, () -> probe));
        assertEquals(List.of("callTimeout=2000"), probe.settings);
        assertEquals(1, probe.closes);
        assertTrue(observed == fatal, "FACT334004 API factory graph after owned close");
      } finally {
        probe.dispose();
      }
    }
  }

  private static final class OrderedProbe extends ApiFactoryOwnershipTest.ProbeFactory {
    @java.io.Serial private static final long serialVersionUID = 1L;
    final int index;
    final transient List<Integer> order;

    public OrderedProbe() {
      this(0, new ArrayList<>());
    }

    OrderedProbe(int index, List<Integer> order) {
      this.index = index;
      this.order = order;
    }

    @Override
    public void close() {
      order.add(index);
      super.close();
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
