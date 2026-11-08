package dev.codex.schubert.nk.batch.monitoring;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNotSame;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import io.micrometer.core.instrument.MockClock;
import io.micrometer.core.instrument.binder.jvm.JvmGcMetrics;
import io.micrometer.core.instrument.simple.SimpleConfig;
import io.micrometer.core.instrument.simple.SimpleMeterRegistry;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.Test;

/** BATCHSTD001..013/1795: fixed phase order and owner lifetime, fresh own JVM only. */
class BatchStandardMetricsTest {
  private static final String REGISTRY_CLOSE_EVENT = "REGISTRY_CLOSE";
  private static final String GC_CLOSE_EVENT = "GC_CLOSE";
  private static final String DEBUG_MODE = "DEBUG";
  private static final String UNEXPECTED_PHASE_ACCESS = "not invoke";
  private static final String STANDARD_MODE = "STANDARD";
  private static final String FAILURE_FIXTURE = "fixture";
  private final BatchStandardMetrics assembly = new BatchStandardMetrics();

  private static final class Registry extends SimpleMeterRegistry implements AutoCloseable {
    final List<String> events;
    final AtomicInteger reads = new AtomicInteger();
    final AtomicInteger closes = new AtomicInteger();

    Registry() {
      this(new ArrayList<>());
    }

    Registry(List<String> events) {
      super(SimpleConfig.DEFAULT, new MockClock());
      this.events = events;
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
      events.add(REGISTRY_CLOSE_EVENT);
      closes.incrementAndGet();
      super.close();
    }
  }

  private static final class Owner implements AutoCloseable {
    final List<JvmGcMetrics> resources = new ArrayList<>();
    final List<String> events;
    int closes;

    Owner(List<String> events) {
      this.events = events;
    }

    boolean retain(JvmGcMetrics resource) {
      return resources.add(resource);
    }

    public void close() {
      events.add(GC_CLOSE_EVENT);
      closes++;
      resources.forEach(JvmGcMetrics::close);
    }
  }

  private static void runFailure(Throwable failure) {
    if (failure instanceof RuntimeException runtime) throw runtime;
    throw (Error) failure;
  }

  @Test
  void batchstd001RealSdkThreePhasesWithCallerGcCloseBeforeRegistry() {
    var events = new ArrayList<String>();
    var source = new Registry(events);
    var owner = new Owner(events);
    try (source;
        owner) {
      assembly.bind(source, DEBUG_MODE, owner::retain);
      assertEquals(1, owner.resources.size());
      assertEquals(0, owner.closes);
      assertEquals(0, source.closes.get());
      assertTrue(source.get("jvm.classes.loaded").gauge().value() >= 0);
      assertEquals(
          Runtime.getRuntime().availableProcessors(),
          source.get("system.cpu.count").gauge().value());
      assertNotNull(source.get("process.files.max").gauge());
      for (var meter : source.getMeters()) assertEquals("BATCH", meter.getId().getTag("service"));
      assertTrue(events.isEmpty());
    }
    assertEquals(List.of(GC_CLOSE_EVENT, REGISTRY_CLOSE_EVENT), events);
    assertEquals(1, owner.closes);
    assertEquals(1, source.closes.get());
  }

  @Test
  void batchstd002StandardDoesNotInvokeAnyPortOrOwner() {
    try (var source = new Registry()) {
      Runnable forbidden =
          () -> {
            throw new AssertionError(UNEXPECTED_PHASE_ACCESS);
          };
      source.reads.set(0);
      BatchStandardMetrics.install(
          source,
          STANDARD_MODE,
          resource -> {
            throw new AssertionError("not own");
          },
          forbidden,
          forbidden,
          forbidden);
      assembly.bind(
          source,
          STANDARD_MODE,
          resource -> {
            throw new AssertionError("not own");
          });
      assertEquals(0, source.reads.get());
      assertEquals(0, source.closes.get());
    }
  }

  @Test
  void batchstd003ForwardOrderAndNoImplicitCleanup() {
    try (var source = new Registry()) {
      var order = new ArrayList<String>();
      BatchStandardMetrics.install(
          source,
          DEBUG_MODE,
          resource -> true,
          () -> order.add("JVM"),
          () -> order.add("SYSTEM"),
          () -> order.add("GC"));
      assertEquals(List.of("JVM", "SYSTEM", "GC"), order);
      assertFalse(source.isClosed());
      assertEquals(0, source.closes.get());
    }
  }

  @Test
  void batchstd004AllNullBoundariesFailBeforeActions() {
    Runnable forbidden =
        () -> {
          throw new AssertionError(UNEXPECTED_PHASE_ACCESS);
        };
    assertThrows(
        NullPointerException.class, () -> assembly.bind(null, STANDARD_MODE, resource -> true));
    try (var source = new Registry()) {
      source.reads.set(0);
      assertThrows(NullPointerException.class, () -> assembly.bind(source, null, resource -> true));
      assertThrows(NullPointerException.class, () -> assembly.bind(source, STANDARD_MODE, null));
      assertThrows(
          NullPointerException.class,
          () ->
              BatchStandardMetrics.install(
                  source, DEBUG_MODE, resource -> true, null, forbidden, forbidden));
      assertThrows(
          NullPointerException.class,
          () ->
              BatchStandardMetrics.install(
                  source, DEBUG_MODE, resource -> true, forbidden, null, forbidden));
      assertThrows(
          NullPointerException.class,
          () ->
              BatchStandardMetrics.install(
                  source, DEBUG_MODE, resource -> true, forbidden, forbidden, null));
      assertEquals(0, source.reads.get());
      assertEquals(0, source.closes.get());
    }
  }

  @Test
  void batchstd005UnknownModesReadNoSourceAndExecuteNoPhase() {
    try (var source = new Registry()) {
      Runnable forbidden =
          () -> {
            throw new AssertionError(UNEXPECTED_PHASE_ACCESS);
          };
      source.reads.set(0);
      for (String mode : List.of("", "debug", "DEBUG ", "UNKNOWN"))
        assertEquals(
            "CONFIG_INVALID",
            assertThrows(
                    IllegalArgumentException.class,
                    () ->
                        BatchStandardMetrics.install(
                            source, mode, resource -> true, forbidden, forbidden, forbidden))
                .getMessage());
      assertEquals(0, source.reads.get());
    }
  }

  @Test
  void batchstd006ClosedDebugFailsBeforeAnyPhase() {
    var source = new Registry();
    source.close();
    Runnable forbidden =
        () -> {
          throw new AssertionError(UNEXPECTED_PHASE_ACCESS);
        };
    assertThrows(
        IllegalStateException.class,
        () ->
            BatchStandardMetrics.install(
                source, DEBUG_MODE, resource -> true, forbidden, forbidden, forbidden));
    assertThrows(
        IllegalStateException.class, () -> assembly.bind(source, DEBUG_MODE, resource -> true));
    assertEquals(1, source.closes.get());
  }

  @Test
  void batchstd007EachRuntimeFailureStopsOnlyLaterPhases() {
    phaseFailures(new IllegalStateException(FAILURE_FIXTURE));
  }

  @Test
  void batchstd008EachErrorKeepsIdentityWithoutCleanup() {
    phaseFailures(new AssertionError(FAILURE_FIXTURE));
  }

  private void phaseFailures(Throwable failure) {
    for (int failed = 0; failed < 3; failed++) {
      try (var source = new Registry()) {
        var order = new ArrayList<Integer>();
        var actions = new ArrayList<Runnable>();
        final int failureIndex = failed;
        for (int i = 0; i < 3; i++) {
          final int index = i;
          actions.add(
              () -> {
                order.add(index);
                if (index == failureIndex) runFailure(failure);
              });
        }
        assertSame(
            failure,
            assertThrows(
                failure.getClass(),
                () ->
                    BatchStandardMetrics.install(
                        source,
                        DEBUG_MODE,
                        resource -> true,
                        actions.get(0),
                        actions.get(1),
                        actions.get(2))));
        assertEquals(java.util.stream.IntStream.rangeClosed(0, failed).boxed().toList(), order);
        assertFalse(source.isClosed());
        assertEquals(0, source.closes.get());
      }
    }
  }

  @Test
  void batchstd009GcOwnerRejectKeepsEarlierBorrowedMetricsAndCallerHandle() {
    var events = new ArrayList<String>();
    try (var source = new Registry(events);
        var owner = new Owner(events)) {
      assertEquals(
          "GC binding owner unavailable",
          assertThrows(
                  IllegalStateException.class,
                  () ->
                      assembly.bind(
                          source,
                          DEBUG_MODE,
                          resource -> {
                            owner.retain(resource);
                            return false;
                          }))
              .getMessage());
      assertEquals(1, owner.resources.size());
      assertNotNull(source.get("jvm.classes.loaded").gauge());
      assertNotNull(source.get("system.cpu.count").gauge());
      assertFalse(source.isClosed());
      assertEquals(0, owner.closes);
      assertEquals(0, source.closes.get());
    }
    assertEquals(List.of(GC_CLOSE_EVENT, REGISTRY_CLOSE_EVENT), events);
  }

  @Test
  void batchstd010GcOwnerFailureIsNotNormalizedOrRetried() {
    for (Throwable failure :
        List.of(new IllegalStateException(FAILURE_FIXTURE), new AssertionError(FAILURE_FIXTURE))) {
      var events = new ArrayList<String>();
      try (var source = new Registry(events);
          var owner = new Owner(events)) {
        assertSame(
            failure,
            assertThrows(
                failure.getClass(),
                () ->
                    assembly.bind(
                        source,
                        DEBUG_MODE,
                        resource -> {
                          owner.retain(resource);
                          runFailure(failure);
                          return true;
                        })));
        assertEquals(1, owner.resources.size());
        assertEquals(0, owner.closes);
        assertFalse(source.isClosed());
      }
      assertEquals(List.of(GC_CLOSE_EVENT, REGISTRY_CLOSE_EVENT), events);
    }
  }

  @Test
  void batchstd011ClosedStandardDoesNotReadOrReclose() {
    var source = new Registry();
    source.close();
    source.reads.set(0);
    assembly.bind(
        source,
        STANDARD_MODE,
        resource -> {
          throw new AssertionError("not own");
        });
    assertEquals(0, source.reads.get());
    assertEquals(1, source.closes.get());
  }

  @Test
  void batchstd012IndependentDefaultScopesNeverShareGcHandles() {
    var events1 = new ArrayList<String>();
    var events2 = new ArrayList<String>();
    try (var first = new Registry(events1);
        var one = new Owner(events1);
        var other = new Registry(events2);
        var two = new Owner(events2)) {
      assembly.bind(first, DEBUG_MODE, one::retain);
      assembly.bind(other, DEBUG_MODE, two::retain);
      assertEquals(1, one.resources.size());
      assertEquals(1, two.resources.size());
      assertNotSame(one.resources.getFirst(), two.resources.getFirst());
      assertFalse(first.isClosed());
      assertFalse(other.isClosed());
    }
    assertEquals(List.of(GC_CLOSE_EVENT, REGISTRY_CLOSE_EVENT), events1);
    assertEquals(List.of(GC_CLOSE_EVENT, REGISTRY_CLOSE_EVENT), events2);
  }

  @Test
  void batchstd013FiniteIndependentConcurrentCompositions() throws Exception {
    var workers = Executors.newFixedThreadPool(4);
    try {
      var jobs = new ArrayList<Future<?>>();
      var total = new AtomicInteger();
      for (int i = 0; i < 64; i++)
        jobs.add(
            workers.submit(
                () -> {
                  try (var source = new Registry()) {
                    var local = new AtomicInteger();
                    Runnable action =
                        () -> {
                          local.incrementAndGet();
                          total.incrementAndGet();
                        };
                    BatchStandardMetrics.install(
                        source, DEBUG_MODE, resource -> true, action, action, action);
                    assertEquals(3, local.get());
                    assertFalse(source.isClosed());
                    assertEquals(0, source.closes.get());
                  }
                }));
      for (var job : jobs) job.get(10, TimeUnit.SECONDS);
      assertEquals(192, total.get());
    } finally {
      workers.shutdownNow();
      assertTrue(workers.awaitTermination(10, TimeUnit.SECONDS));
    }
  }
}
