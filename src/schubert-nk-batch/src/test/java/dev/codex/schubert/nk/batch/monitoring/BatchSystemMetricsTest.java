package dev.codex.schubert.nk.batch.monitoring;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertNotNull;
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

/**
 * BATCHSYS001..014/1791: own JVM public observations and independent binder ports, no target IO.
 */
class BatchSystemMetricsTest {
  private final BatchSystemMetrics installer = new BatchSystemMetrics();

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

  private static List<MeterBinder> two(MeterBinder action) {
    return List.of(action, action);
  }

  private static void namespaces(Registry source) {
    var names =
        source.getMeters().stream()
            .map(m -> m.getId().getName())
            .collect(java.util.stream.Collectors.toSet());
    assertTrue(
        names.containsAll(
            Set.of(
                "system.cpu.count",
                "process.cpu.usage",
                "process.cpu.time",
                "process.files.open",
                "process.files.max")));
    assertFalse(names.stream().anyMatch(n -> n.startsWith("nk_") || n.startsWith("jvm.")));
    for (var meter : source.getMeters()) assertEquals("BATCH", meter.getId().getTag("service"));
    assertEquals(
        Runtime.getRuntime().availableProcessors(), source.get("system.cpu.count").gauge().value());
    assertNotNull(source.get("process.cpu.usage").gauge());
    assertTrue(source.get("process.cpu.time").functionCounter().count() >= 0);
    assertTrue(source.get("process.files.open").gauge().value() >= 0);
    var os =
        assertInstanceOf(
            com.sun.management.UnixOperatingSystemMXBean.class,
            ManagementFactory.getOperatingSystemMXBean());
    assertEquals(os.getMaxFileDescriptorCount(), source.get("process.files.max").gauge().value());
    assertTrue(source.get("process.files.open").gauge().value() <= os.getMaxFileDescriptorCount());
  }

  @Test
  void batchsys001ActualStandardCpuFdAndIndependentCpuTimeBracket() {
    try (var source = new Registry()) {
      installer.bind(source, "DEBUG");
      namespaces(source);
      var os =
          assertInstanceOf(
              com.sun.management.OperatingSystemMXBean.class,
              ManagementFactory.getOperatingSystemMXBean());
      long before = os.getProcessCpuTime();
      double actual = source.get("process.cpu.time").functionCounter().count();
      long after = os.getProcessCpuTime();
      assertTrue(actual >= before && actual <= after);
      assertEquals("ns", source.get("process.cpu.time").functionCounter().getId().getBaseUnit());
      assertFalse(source.isClosed());
      assertEquals(0, source.closes.get());
    }
  }

  @Test
  void batchsys002StandardIsLazyAndDoesNotReadRegistry() {
    try (var source = new Registry()) {
      var calls = new AtomicInteger();
      source.reads.set(0);
      BatchSystemMetrics.install(
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
  void batchsys003ExactlyTwoOrderedPortsSeeSameBorrowedOwner() {
    try (var source = new Registry()) {
      var calls = new ArrayList<Integer>();
      var factories = new AtomicInteger();
      var binders = new ArrayList<MeterBinder>();
      for (int i = 1; i <= 2; i++) {
        final int order = i;
        binders.add(
            actual -> {
              assertSame(source, actual);
              calls.add(order);
              if (order == 1) binders.clear();
            });
      }
      BatchSystemMetrics.install(
          source,
          "DEBUG",
          () -> {
            factories.incrementAndGet();
            return binders;
          });
      assertEquals(List.of(1, 2), calls);
      assertTrue(binders.isEmpty());
      assertEquals(1, factories.get());
      assertFalse(source.isClosed());
      assertEquals(0, source.closes.get());
    }
  }

  @Test
  void batchsys004NullBoundariesRejectWithoutBinding() {
    assertThrows(NullPointerException.class, () -> installer.bind(null, "STANDARD"));
    try (var source = new Registry()) {
      assertThrows(NullPointerException.class, () -> installer.bind(source, null));
      assertThrows(
          NullPointerException.class, () -> BatchSystemMetrics.install(source, "DEBUG", null));
      assertEquals(0, source.closes.get());
    }
  }

  @Test
  void batchsys005UnknownModesNeverReadSourceOrFactory() {
    try (var source = new Registry()) {
      var factories = new AtomicInteger();
      source.reads.set(0);
      for (String mode : List.of("", "debug", "DEBUG ", "UNKNOWN")) {
        var failure =
            assertThrows(
                IllegalArgumentException.class,
                () ->
                    BatchSystemMetrics.install(
                        source,
                        mode,
                        () -> {
                          factories.incrementAndGet();
                          return two(
                              actual -> {
                                throw new AssertionError("no binding");
                              });
                        }));
        assertEquals("CONFIG_INVALID", failure.getMessage());
      }
      assertEquals(0, factories.get());
      assertEquals(0, source.reads.get());
    }
  }

  @Test
  void batchsys006ClosedDebugFailsBeforeFactoryAndDoesNotReopen() {
    var source = new Registry();
    source.close();
    int before = source.closes.get();
    var factories = new AtomicInteger();
    assertThrows(
        IllegalStateException.class,
        () ->
            BatchSystemMetrics.install(
                source,
                "DEBUG",
                () -> {
                  factories.incrementAndGet();
                  return two(
                      actual -> {
                        throw new AssertionError("not bind");
                      });
                }));
    assertEquals(0, factories.get());
    assertEquals(before, source.closes.get());
    assertTrue(source.isClosed());
  }

  @Test
  void batchsys007NullFactoryListOrElementFailsBeforeAnyBinding() {
    try (var source = new Registry()) {
      var bound = new AtomicInteger();
      assertThrows(
          NullPointerException.class,
          () -> BatchSystemMetrics.install(source, "DEBUG", () -> null));
      var list = new ArrayList<MeterBinder>(two(actual -> bound.incrementAndGet()));
      list.set(1, null);
      assertThrows(
          NullPointerException.class,
          () -> BatchSystemMetrics.install(source, "DEBUG", () -> list));
      assertEquals(0, bound.get());
      assertFalse(source.isClosed());
    }
  }

  @Test
  void batchsys008WrongBinderCountIsNotPartialSuccess() {
    try (var source = new Registry()) {
      var bound = new AtomicInteger();
      for (int size : new int[] {0, 1, 3, 4}) {
        var list = new ArrayList<MeterBinder>();
        for (int i = 0; i < size; i++) list.add(actual -> bound.incrementAndGet());
        assertEquals(
            "invalid system binder count",
            assertThrows(
                    IllegalArgumentException.class,
                    () -> BatchSystemMetrics.install(source, "DEBUG", () -> list))
                .getMessage());
      }
      assertEquals(0, bound.get());
      assertFalse(source.isClosed());
    }
  }

  @Test
  void batchsys009FactoryRuntimeAndErrorKeepIdentity() {
    try (var source = new Registry()) {
      var failure = new IllegalStateException("fixture");
      var fatal = new AssertionError("fixture");
      assertSame(
          failure,
          assertThrows(
              IllegalStateException.class,
              () ->
                  BatchSystemMetrics.install(
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
                  BatchSystemMetrics.install(
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
  void batchsys010EachBinderRuntimeStopsLaterPortsAndKeepsPartialOwner() {
    for (int index = 0; index < 2; index++) {
      final int failed = index;
      try (var source = new Registry()) {
        var events = new ArrayList<Integer>();
        var binders = new ArrayList<MeterBinder>();
        var failure = new IllegalStateException("fixture");
        for (int n = 0; n < 2; n++) {
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
                () -> BatchSystemMetrics.install(source, "DEBUG", () -> binders)));
        assertEquals(java.util.stream.IntStream.rangeClosed(0, failed).boxed().toList(), events);
        assertFalse(source.isClosed());
        assertEquals(0, source.closes.get());
      }
    }
  }

  @Test
  void batchsys011EachBinderErrorIsNeverNormalized() {
    for (int index = 0; index < 2; index++) {
      final int failed = index;
      try (var source = new Registry()) {
        var events = new ArrayList<Integer>();
        var binders = new ArrayList<MeterBinder>();
        var failure = new AssertionError("fixture");
        for (int n = 0; n < 2; n++) {
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
                AssertionError.class,
                () -> BatchSystemMetrics.install(source, "DEBUG", () -> binders)));
        assertEquals(java.util.stream.IntStream.rangeClosed(0, failed).boxed().toList(), events);
        assertFalse(source.isClosed());
        assertEquals(0, source.closes.get());
      }
    }
  }

  @Test
  void batchsys012StandardOnClosedOwnerDoesNotInspectOrCloseAgain() {
    var source = new Registry();
    source.close();
    int closes = source.closes.get();
    source.reads.set(0);
    var factories = new AtomicInteger();
    BatchSystemMetrics.install(
        source,
        "STANDARD",
        () -> {
          factories.incrementAndGet();
          return two(
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
  void batchsys013SameInstanceUsesDistinctRegistryOwners() {
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
  void batchsys014FiniteConcurrentPortsDoNotShareSourceState() throws Exception {
    try (var workers = Executors.newFixedThreadPool(4)) {
      var jobs = new ArrayList<Future<?>>();
      var total = new AtomicInteger();
      for (int i = 0; i < 64; i++)
        jobs.add(
            workers.submit(
                () -> {
                  try (var source = new Registry()) {
                    var local = new AtomicInteger();
                    BatchSystemMetrics.install(
                        source,
                        "DEBUG",
                        () ->
                            two(
                                actual -> {
                                  assertSame(source, actual);
                                  local.incrementAndGet();
                                  total.incrementAndGet();
                                }));
                    assertEquals(2, local.get());
                    assertFalse(source.isClosed());
                    assertEquals(0, source.closes.get());
                  }
                }));
      for (var job : jobs) job.get(10, TimeUnit.SECONDS);
      assertEquals(128, total.get());
    }
  }
}
