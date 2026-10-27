package dev.codex.schubert.nk.api.monitoring;

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

/** APISYS001..014/1789: own JVM public observations and independent binder ports, no target IO. */
class ApiSystemMetricsTest {
  private static final int FIRST_BINDER_ORDER = 1;
  private static final String PROCESS_CPU_TIME = "process.cpu.time";
  private static final String DEBUG_MODE = "DEBUG";
  private static final String STANDARD_MODE = "STANDARD";
  private static final String FAILURE_FIXTURE = "fixture";
  private final ApiSystemMetrics installer = new ApiSystemMetrics();

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
                PROCESS_CPU_TIME,
                "process.files.open",
                "process.files.max")));
    assertFalse(names.stream().anyMatch(n -> n.startsWith("nk_") || n.startsWith("jvm.")));
    for (var meter : source.getMeters()) assertEquals("API", meter.getId().getTag("service"));
    assertEquals(
        Runtime.getRuntime().availableProcessors(), source.get("system.cpu.count").gauge().value());
    assertNotNull(source.get("process.cpu.usage").gauge());
    assertTrue(source.get(PROCESS_CPU_TIME).functionCounter().count() >= 0);
    assertTrue(source.get("process.files.open").gauge().value() >= 0);
    var os =
        assertInstanceOf(
            com.sun.management.UnixOperatingSystemMXBean.class,
            ManagementFactory.getOperatingSystemMXBean());
    assertEquals(os.getMaxFileDescriptorCount(), source.get("process.files.max").gauge().value());
    assertTrue(source.get("process.files.open").gauge().value() <= os.getMaxFileDescriptorCount());
  }

  @Test
  void apisys001ActualStandardCpuFdAndIndependentCpuTimeBracket() {
    try (var source = new Registry()) {
      installer.bind(source, DEBUG_MODE);
      namespaces(source);
      var os =
          assertInstanceOf(
              com.sun.management.OperatingSystemMXBean.class,
              ManagementFactory.getOperatingSystemMXBean());
      long before = os.getProcessCpuTime();
      double actual = source.get(PROCESS_CPU_TIME).functionCounter().count();
      long after = os.getProcessCpuTime();
      assertTrue(actual >= before && actual <= after);
      assertEquals("ns", source.get(PROCESS_CPU_TIME).functionCounter().getId().getBaseUnit());
      assertFalse(source.isClosed());
      assertEquals(0, source.closes.get());
    }
  }

  @Test
  void apisys002StandardIsLazyAndDoesNotReadRegistry() {
    try (var source = new Registry()) {
      var calls = new AtomicInteger();
      source.reads.set(0);
      ApiSystemMetrics.install(
          source,
          STANDARD_MODE,
          () -> {
            calls.incrementAndGet();
            throw new AssertionError("not constructed");
          });
      installer.bind(source, STANDARD_MODE);
      assertEquals(0, calls.get());
      assertEquals(0, source.reads.get());
      assertEquals(0, source.closes.get());
    }
  }

  @Test
  void apisys003ExactlyTwoOrderedPortsSeeSameBorrowedOwner() {
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
              if (order == FIRST_BINDER_ORDER) binders.clear();
            });
      }
      ApiSystemMetrics.install(
          source,
          DEBUG_MODE,
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
  void apisys004NullBoundariesRejectWithoutBinding() {
    assertThrows(NullPointerException.class, () -> installer.bind(null, STANDARD_MODE));
    try (var source = new Registry()) {
      assertThrows(NullPointerException.class, () -> installer.bind(source, null));
      assertThrows(
          NullPointerException.class, () -> ApiSystemMetrics.install(source, DEBUG_MODE, null));
      assertEquals(0, source.closes.get());
    }
  }

  @Test
  void apisys005UnknownModesNeverReadSourceOrFactory() {
    try (var source = new Registry()) {
      var factories = new AtomicInteger();
      source.reads.set(0);
      for (String mode : List.of("", "debug", "DEBUG ", "UNKNOWN")) {
        var failure =
            assertThrows(
                IllegalArgumentException.class,
                () ->
                    ApiSystemMetrics.install(
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
  void apisys006ClosedDebugFailsBeforeFactoryAndDoesNotReopen() {
    var source = new Registry();
    source.close();
    int before = source.closes.get();
    var factories = new AtomicInteger();
    assertThrows(
        IllegalStateException.class,
        () ->
            ApiSystemMetrics.install(
                source,
                DEBUG_MODE,
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
  void apisys007NullFactoryListOrElementFailsBeforeAnyBinding() {
    try (var source = new Registry()) {
      var bound = new AtomicInteger();
      assertThrows(
          NullPointerException.class,
          () -> ApiSystemMetrics.install(source, DEBUG_MODE, () -> null));
      var list = new ArrayList<MeterBinder>(two(actual -> bound.incrementAndGet()));
      list.set(1, null);
      assertThrows(
          NullPointerException.class,
          () -> ApiSystemMetrics.install(source, DEBUG_MODE, () -> list));
      assertEquals(0, bound.get());
      assertFalse(source.isClosed());
    }
  }

  @Test
  void apisys008WrongBinderCountIsNotPartialSuccess() {
    try (var source = new Registry()) {
      var bound = new AtomicInteger();
      for (int size : new int[] {0, 1, 3, 4}) {
        var list = new ArrayList<MeterBinder>();
        for (int i = 0; i < size; i++) list.add(actual -> bound.incrementAndGet());
        assertEquals(
            "invalid system binder count",
            assertThrows(
                    IllegalArgumentException.class,
                    () -> ApiSystemMetrics.install(source, DEBUG_MODE, () -> list))
                .getMessage());
      }
      assertEquals(0, bound.get());
      assertFalse(source.isClosed());
    }
  }

  @Test
  void apisys009FactoryRuntimeAndErrorKeepIdentity() {
    try (var source = new Registry()) {
      var failure = new IllegalStateException(FAILURE_FIXTURE);
      var fatal = new AssertionError(FAILURE_FIXTURE);
      assertSame(
          failure,
          assertThrows(
              IllegalStateException.class,
              () ->
                  ApiSystemMetrics.install(
                      source,
                      DEBUG_MODE,
                      () -> {
                        throw failure;
                      })));
      assertSame(
          fatal,
          assertThrows(
              AssertionError.class,
              () ->
                  ApiSystemMetrics.install(
                      source,
                      DEBUG_MODE,
                      () -> {
                        throw fatal;
                      })));
      assertFalse(source.isClosed());
      assertEquals(0, source.closes.get());
    }
  }

  @Test
  void apisys010EachBinderRuntimeStopsLaterPortsAndKeepsPartialOwner() {
    for (int index = 0; index < 2; index++) {
      final int failed = index;
      try (var source = new Registry()) {
        var events = new ArrayList<Integer>();
        var binders = new ArrayList<MeterBinder>();
        var failure = new IllegalStateException(FAILURE_FIXTURE);
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
                () -> ApiSystemMetrics.install(source, DEBUG_MODE, () -> binders)));
        assertEquals(java.util.stream.IntStream.rangeClosed(0, failed).boxed().toList(), events);
        assertFalse(source.isClosed());
        assertEquals(0, source.closes.get());
      }
    }
  }

  @Test
  void apisys011EachBinderErrorIsNeverNormalized() {
    for (int index = 0; index < 2; index++) {
      final int failed = index;
      try (var source = new Registry()) {
        var events = new ArrayList<Integer>();
        var binders = new ArrayList<MeterBinder>();
        var failure = new AssertionError(FAILURE_FIXTURE);
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
                () -> ApiSystemMetrics.install(source, DEBUG_MODE, () -> binders)));
        assertEquals(java.util.stream.IntStream.rangeClosed(0, failed).boxed().toList(), events);
        assertFalse(source.isClosed());
        assertEquals(0, source.closes.get());
      }
    }
  }

  @Test
  void apisys012StandardOnClosedOwnerDoesNotInspectOrCloseAgain() {
    var source = new Registry();
    source.close();
    int closes = source.closes.get();
    source.reads.set(0);
    var factories = new AtomicInteger();
    ApiSystemMetrics.install(
        source,
        STANDARD_MODE,
        () -> {
          factories.incrementAndGet();
          return two(
              actual -> {
                throw new AssertionError("no binding");
              });
        });
    installer.bind(source, STANDARD_MODE);
    assertEquals(0, factories.get());
    assertEquals(0, source.reads.get());
    assertEquals(closes, source.closes.get());
  }

  @Test
  void apisys013SameInstanceUsesDistinctRegistryOwners() {
    var first = new Registry();
    try (var other = new Registry()) {
      installer.bind(first, DEBUG_MODE);
      installer.bind(other, DEBUG_MODE);
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
  void apisys014FiniteConcurrentPortsDoNotShareSourceState() throws Exception {
    try (var workers = Executors.newFixedThreadPool(4)) {
      var jobs = new ArrayList<Future<?>>();
      var total = new AtomicInteger();
      for (int i = 0; i < 64; i++)
        jobs.add(
            workers.submit(
                () -> {
                  try (var source = new Registry()) {
                    var local = new AtomicInteger();
                    ApiSystemMetrics.install(
                        source,
                        DEBUG_MODE,
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
