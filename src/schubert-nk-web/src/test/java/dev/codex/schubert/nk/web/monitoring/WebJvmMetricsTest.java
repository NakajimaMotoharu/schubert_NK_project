package dev.codex.schubert.nk.web.monitoring;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import io.micrometer.core.instrument.MockClock;
import io.micrometer.core.instrument.binder.MeterBinder;
import io.micrometer.core.instrument.simple.SimpleConfig;
import io.micrometer.core.instrument.simple.SimpleMeterRegistry;
import java.lang.management.ManagementFactory;
import java.util.ArrayList;
import java.util.List;
import java.util.Set;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.Test;

/** WEBJVM001..014/1781: own JVM public observations and independent binder ports, no target IO. */
class WebJvmMetricsTest {
  private final WebJvmMetrics installer = new WebJvmMetrics();

  private static class Registry extends SimpleMeterRegistry implements AutoCloseable {
    final AtomicInteger reads = new AtomicInteger();
    final AtomicInteger closes = new AtomicInteger();

    Registry() {
      super(SimpleConfig.DEFAULT, new MockClock());
    }

    public boolean isClosed() {
      reads.incrementAndGet();
      return super.isClosed();
    }

    public List<io.micrometer.core.instrument.Meter> getMeters() {
      reads.incrementAndGet();
      return super.getMeters();
    }

    public void close() {
      closes.incrementAndGet();
      super.close();
    }
  }

  private static List<MeterBinder> four(MeterBinder action) {
    return List.of(action, action, action, action);
  }

  private static void namespaces(Registry source) {
    var names =
        source.getMeters().stream()
            .map(m -> m.getId().getName())
            .collect(java.util.stream.Collectors.toSet());
    assertTrue(
        names.containsAll(
            Set.of(
                "jvm.classes.loaded.count",
                "jvm.classes.loaded",
                "jvm.classes.unloaded",
                "jvm.memory.used",
                "jvm.threads.states",
                "process.start.time",
                "process.uptime")));
    assertFalse(names.stream().anyMatch(n -> n.startsWith("nk_")));
    for (var meter : source.getMeters()) assertEquals("WEB", meter.getId().getTag("service"));
    assertTrue(source.get("jvm.classes.loaded.count").functionCounter().count() >= 0);
    assertTrue(source.get("jvm.classes.loaded").gauge().value() >= 0);
    assertTrue(source.get("jvm.classes.unloaded").functionCounter().count() >= 0);
    assertFalse(source.get("jvm.memory.used").gauges().isEmpty());
    for (var gauge : source.get("jvm.threads.states").gauges()) assertTrue(gauge.value() >= 0);
  }

  @Test
  void webjvm001ActualFourStandardBindersWithIndependentRuntimeClock() {
    try (var source = new Registry()) {
      installer.bind(source, "DEBUG");
      namespaces(source);
      var runtime = ManagementFactory.getRuntimeMXBean();
      assertEquals(
          runtime.getStartTime() / 1000.0,
          source.get("process.start.time").timeGauge().value(TimeUnit.SECONDS),
          1e-6);
      long before = runtime.getUptime();
      double actual = source.get("process.uptime").timeGauge().value(TimeUnit.MILLISECONDS);
      long after = runtime.getUptime();
      assertTrue(actual >= before - 1 && actual <= after + 1);
      assertFalse(source.isClosed());
      assertEquals(0, source.closes.get());
    }
  }

  @Test
  void webjvm002StandardIsLazyAndDoesNotReadRegistry() {
    try (var source = new Registry()) {
      var calls = new AtomicInteger();
      source.reads.set(0);
      WebJvmMetrics.install(
          source,
          "STANDARD",
          () -> {
            calls.incrementAndGet();
            throw new AssertionError("not constructed");
          });
      installer.bind(source, "STANDARD");
      assertEquals(0, calls.get());
      assertEquals(0, source.reads.get());
      assertEquals(0, source.closes.get());
    }
  }

  @Test
  void webjvm003ExactlyFourOrderedPortsSeeSameBorrowedOwner() {
    try (var source = new Registry()) {
      var calls = new ArrayList<Integer>();
      var factories = new AtomicInteger();
      var binders = new ArrayList<MeterBinder>();
      for (int i = 1; i <= 4; i++) {
        final int order = i;
        binders.add(
            actual -> {
              assertSame(source, actual);
              calls.add(order);
              if (order == 1) binders.clear();
            });
      }
      WebJvmMetrics.install(
          source,
          "DEBUG",
          () -> {
            factories.incrementAndGet();
            return binders;
          });
      assertEquals(List.of(1, 2, 3, 4), calls);
      assertTrue(binders.isEmpty());
      assertEquals(1, factories.get());
      assertFalse(source.isClosed());
      assertEquals(0, source.closes.get());
    }
  }

  @Test
  void webjvm004NullBoundariesRejectWithoutBinding() {
    assertThrows(NullPointerException.class, () -> installer.bind(null, "STANDARD"));
    try (var source = new Registry()) {
      assertThrows(NullPointerException.class, () -> installer.bind(source, null));
      assertThrows(NullPointerException.class, () -> WebJvmMetrics.install(source, "DEBUG", null));
      assertEquals(0, source.closes.get());
    }
  }

  @Test
  void webjvm005UnknownModesNeverReadSourceOrFactory() {
    try (var source = new Registry()) {
      var factories = new AtomicInteger();
      source.reads.set(0);
      for (String mode : List.of("", "debug", "DEBUG ", "UNKNOWN")) {
        var failure =
            assertThrows(
                IllegalArgumentException.class,
                () ->
                    WebJvmMetrics.install(
                        source,
                        mode,
                        () -> {
                          factories.incrementAndGet();
                          return four(
                              actual -> {
                                throw new AssertionError("no binding");
                              });
                        }));
        assertEquals("invalid monitoring mode", failure.getMessage());
      }
      assertEquals(0, factories.get());
      assertEquals(0, source.reads.get());
    }
  }

  @Test
  void webjvm006ClosedDebugFailsBeforeFactoryAndDoesNotReopen() {
    var source = new Registry();
    source.close();
    int before = source.closes.get();
    var factories = new AtomicInteger();
    assertThrows(
        IllegalStateException.class,
        () ->
            WebJvmMetrics.install(
                source,
                "DEBUG",
                () -> {
                  factories.incrementAndGet();
                  return four(
                      actual -> {
                        throw new AssertionError("not bind");
                      });
                }));
    assertEquals(0, factories.get());
    assertEquals(before, source.closes.get());
    assertTrue(source.isClosed());
  }

  @Test
  void webjvm007NullFactoryListOrElementFailsBeforeAnyBinding() {
    try (var source = new Registry()) {
      var bound = new AtomicInteger();
      assertThrows(
          NullPointerException.class, () -> WebJvmMetrics.install(source, "DEBUG", () -> null));
      var list = new ArrayList<MeterBinder>(four(actual -> bound.incrementAndGet()));
      list.set(3, null);
      assertThrows(
          NullPointerException.class, () -> WebJvmMetrics.install(source, "DEBUG", () -> list));
      assertEquals(0, bound.get());
      assertFalse(source.isClosed());
    }
  }

  @Test
  void webjvm008WrongBinderCountIsNotPartialSuccess() {
    try (var source = new Registry()) {
      var bound = new AtomicInteger();
      for (int size : new int[] {0, 1, 3, 5}) {
        var list = new ArrayList<MeterBinder>();
        for (int i = 0; i < size; i++) list.add(actual -> bound.incrementAndGet());
        assertEquals(
            "invalid JVM binder count",
            assertThrows(
                    IllegalArgumentException.class,
                    () -> WebJvmMetrics.install(source, "DEBUG", () -> list))
                .getMessage());
      }
      assertEquals(0, bound.get());
      assertFalse(source.isClosed());
    }
  }

  @Test
  void webjvm009FactoryRuntimeAndErrorKeepIdentity() {
    try (var source = new Registry()) {
      var failure = new IllegalStateException("fixture");
      var fatal = new AssertionError("fixture");
      assertSame(
          failure,
          assertThrows(
              IllegalStateException.class,
              () ->
                  WebJvmMetrics.install(
                      source,
                      "DEBUG",
                      () -> {
                        throw failure;
                      })));
      assertSame(
          fatal,
          assertThrows(
              AssertionError.class,
              () ->
                  WebJvmMetrics.install(
                      source,
                      "DEBUG",
                      () -> {
                        throw fatal;
                      })));
      assertFalse(source.isClosed());
      assertEquals(0, source.closes.get());
    }
  }

  @Test
  void webjvm010EachBinderRuntimeStopsLaterPortsAndKeepsPartialOwner() {
    for (int index = 0; index < 4; index++) {
      final int failed = index;
      try (var source = new Registry()) {
        var events = new ArrayList<Integer>();
        var binders = new ArrayList<MeterBinder>();
        var failure = new IllegalStateException("fixture");
        for (int n = 0; n < 4; n++) {
          final int position = n;
          binders.add(
              actual -> {
                assertSame(source, actual);
                events.add(position);
                if (position == failed) throw failure;
              });
        }
        assertSame(
            failure,
            assertThrows(
                IllegalStateException.class,
                () -> WebJvmMetrics.install(source, "DEBUG", () -> binders)));
        assertEquals(java.util.stream.IntStream.rangeClosed(0, failed).boxed().toList(), events);
        assertFalse(source.isClosed());
        assertEquals(0, source.closes.get());
      }
    }
  }

  @Test
  void webjvm011EachBinderErrorIsNeverNormalized() {
    for (int index = 0; index < 4; index++) {
      final int failed = index;
      try (var source = new Registry()) {
        var events = new ArrayList<Integer>();
        var binders = new ArrayList<MeterBinder>();
        var failure = new AssertionError("fixture");
        for (int n = 0; n < 4; n++) {
          final int position = n;
          binders.add(
              actual -> {
                events.add(position);
                if (position == failed) throw failure;
              });
        }
        assertSame(
            failure,
            assertThrows(
                AssertionError.class, () -> WebJvmMetrics.install(source, "DEBUG", () -> binders)));
        assertEquals(java.util.stream.IntStream.rangeClosed(0, failed).boxed().toList(), events);
        assertFalse(source.isClosed());
        assertEquals(0, source.closes.get());
      }
    }
  }

  @Test
  void webjvm012StandardOnClosedOwnerDoesNotInspectOrCloseAgain() {
    var source = new Registry();
    source.close();
    int closes = source.closes.get();
    source.reads.set(0);
    var factories = new AtomicInteger();
    WebJvmMetrics.install(
        source,
        "STANDARD",
        () -> {
          factories.incrementAndGet();
          return four(
              actual -> {
                throw new AssertionError("no binding");
              });
        });
    installer.bind(source, "STANDARD");
    assertEquals(0, factories.get());
    assertEquals(0, source.reads.get());
    assertEquals(closes, source.closes.get());
  }

  @Test
  void webjvm013SameInstanceUsesDistinctRegistryOwners() {
    var first = new Registry();
    try (var other = new Registry()) {
      installer.bind(first, "DEBUG");
      installer.bind(other, "DEBUG");
      namespaces(first);
      namespaces(other);
      assertFalse(first.getMeters().isEmpty());
      assertFalse(other.getMeters().isEmpty());
      first.close();
      assertTrue(first.isClosed());
      namespaces(other);
      assertFalse(other.isClosed());
    } finally {
      first.close();
    }
  }

  @Test
  void webjvm014FiniteConcurrentPortsDoNotShareSourceState() throws Exception {
    try (var workers = Executors.newFixedThreadPool(4)) {
      var jobs = new ArrayList<Future<?>>();
      var total = new AtomicInteger();
      for (int i = 0; i < 64; i++)
        jobs.add(
            workers.submit(
                () -> {
                  try (var source = new Registry()) {
                    var local = new AtomicInteger();
                    WebJvmMetrics.install(
                        source,
                        "DEBUG",
                        () ->
                            four(
                                actual -> {
                                  assertSame(source, actual);
                                  local.incrementAndGet();
                                  total.incrementAndGet();
                                }));
                    assertEquals(4, local.get());
                    assertFalse(source.isClosed());
                    assertEquals(0, source.closes.get());
                  }
                }));
      for (var job : jobs) job.get(10, TimeUnit.SECONDS);
      assertEquals(256, total.get());
    }
  }
}
