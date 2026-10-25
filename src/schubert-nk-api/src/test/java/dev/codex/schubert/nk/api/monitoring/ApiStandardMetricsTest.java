package dev.codex.schubert.nk.api.monitoring;

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

/** APISTD001..013/1793: fixed phase order and owner lifetime, fresh own JVM only. */
class ApiStandardMetricsTest {
  private final ApiStandardMetrics assembly = new ApiStandardMetrics();

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
      events.add("REGISTRY_CLOSE");
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
      events.add("GC_CLOSE");
      closes++;
      resources.forEach(JvmGcMetrics::close);
    }
  }

  private static void runFailure(Throwable failure) {
    if (failure instanceof RuntimeException runtime) throw runtime;
    throw (Error) failure;
  }

  @Test
  void apistd001RealSdkThreePhasesWithCallerGcCloseBeforeRegistry() {
    var events = new ArrayList<String>();
    var source = new Registry(events);
    var owner = new Owner(events);
    try (source;
        owner) {
      assembly.bind(source, "DEBUG", owner::retain);
      assertEquals(1, owner.resources.size());
      assertEquals(0, owner.closes);
      assertEquals(0, source.closes.get());
      assertTrue(source.get("jvm.classes.loaded").gauge().value() >= 0);
      assertEquals(
          Runtime.getRuntime().availableProcessors(),
          source.get("system.cpu.count").gauge().value());
      assertNotNull(source.get("process.files.max").gauge());
      for (var meter : source.getMeters()) assertEquals("API", meter.getId().getTag("service"));
      assertTrue(events.isEmpty());
    }
    assertEquals(List.of("GC_CLOSE", "REGISTRY_CLOSE"), events);
    assertEquals(1, owner.closes);
    assertEquals(1, source.closes.get());
  }

  @Test
  void apistd002StandardDoesNotInvokeAnyPortOrOwner() {
    try (var source = new Registry()) {
      Runnable forbidden =
          () -> {
            throw new AssertionError("not invoke");
          };
      source.reads.set(0);
      ApiStandardMetrics.install(
          source,
          "STANDARD",
          resource -> {
            throw new AssertionError("not own");
          },
          forbidden,
          forbidden,
          forbidden);
      assembly.bind(
          source,
          "STANDARD",
          resource -> {
            throw new AssertionError("not own");
          });
      assertEquals(0, source.reads.get());
      assertEquals(0, source.closes.get());
    }
  }

  @Test
  void apistd003ForwardOrderAndNoImplicitCleanup() {
    try (var source = new Registry()) {
      var order = new ArrayList<String>();
      ApiStandardMetrics.install(
          source,
          "DEBUG",
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
  void apistd004AllNullBoundariesFailBeforeActions() {
    Runnable forbidden =
        () -> {
          throw new AssertionError("not invoke");
        };
    assertThrows(
        NullPointerException.class, () -> assembly.bind(null, "STANDARD", resource -> true));
    try (var source = new Registry()) {
      source.reads.set(0);
      assertThrows(NullPointerException.class, () -> assembly.bind(source, null, resource -> true));
      assertThrows(NullPointerException.class, () -> assembly.bind(source, "STANDARD", null));
      assertThrows(
          NullPointerException.class,
          () ->
              ApiStandardMetrics.install(
                  source, "DEBUG", resource -> true, null, forbidden, forbidden));
      assertThrows(
          NullPointerException.class,
          () ->
              ApiStandardMetrics.install(
                  source, "DEBUG", resource -> true, forbidden, null, forbidden));
      assertThrows(
          NullPointerException.class,
          () ->
              ApiStandardMetrics.install(
                  source, "DEBUG", resource -> true, forbidden, forbidden, null));
      assertEquals(0, source.reads.get());
      assertEquals(0, source.closes.get());
    }
  }

  @Test
  void apistd005UnknownModesReadNoSourceAndExecuteNoPhase() {
    try (var source = new Registry()) {
      Runnable forbidden =
          () -> {
            throw new AssertionError("not invoke");
          };
      source.reads.set(0);
      for (String mode : List.of("", "debug", "DEBUG ", "UNKNOWN"))
        assertEquals(
            "CONFIG_INVALID",
            assertThrows(
                    IllegalArgumentException.class,
                    () ->
                        ApiStandardMetrics.install(
                            source, mode, resource -> true, forbidden, forbidden, forbidden))
                .getMessage());
      assertEquals(0, source.reads.get());
    }
  }

  @Test
  void apistd006ClosedDebugFailsBeforeAnyPhase() {
    var source = new Registry();
    source.close();
    Runnable forbidden =
        () -> {
          throw new AssertionError("not invoke");
        };
    assertThrows(
        IllegalStateException.class,
        () ->
            ApiStandardMetrics.install(
                source, "DEBUG", resource -> true, forbidden, forbidden, forbidden));
    assertThrows(
        IllegalStateException.class, () -> assembly.bind(source, "DEBUG", resource -> true));
    assertEquals(1, source.closes.get());
  }

  @Test
  void apistd007EachRuntimeFailureStopsOnlyLaterPhases() {
    phaseFailures(new IllegalStateException("fixture"));
  }

  @Test
  void apistd008EachErrorKeepsIdentityWithoutCleanup() {
    phaseFailures(new AssertionError("fixture"));
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
                    ApiStandardMetrics.install(
                        source,
                        "DEBUG",
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
  void apistd009GcOwnerRejectKeepsEarlierBorrowedMetricsAndCallerHandle() {
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
                          "DEBUG",
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
    assertEquals(List.of("GC_CLOSE", "REGISTRY_CLOSE"), events);
  }

  @Test
  void apistd010GcOwnerFailureIsNotNormalizedOrRetried() {
    for (Throwable failure :
        List.of(new IllegalStateException("fixture"), new AssertionError("fixture"))) {
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
                        "DEBUG",
                        resource -> {
                          owner.retain(resource);
                          runFailure(failure);
                          return true;
                        })));
        assertEquals(1, owner.resources.size());
        assertEquals(0, owner.closes);
        assertFalse(source.isClosed());
      }
      assertEquals(List.of("GC_CLOSE", "REGISTRY_CLOSE"), events);
    }
  }

  @Test
  void apistd011ClosedStandardDoesNotReadOrReclose() {
    var source = new Registry();
    source.close();
    source.reads.set(0);
    assembly.bind(
        source,
        "STANDARD",
        resource -> {
          throw new AssertionError("not own");
        });
    assertEquals(0, source.reads.get());
    assertEquals(1, source.closes.get());
  }

  @Test
  void apistd012IndependentDefaultScopesNeverShareGcHandles() {
    var events1 = new ArrayList<String>();
    var events2 = new ArrayList<String>();
    try (var first = new Registry(events1);
        var one = new Owner(events1);
        var other = new Registry(events2);
        var two = new Owner(events2)) {
      assembly.bind(first, "DEBUG", one::retain);
      assembly.bind(other, "DEBUG", two::retain);
      assertEquals(1, one.resources.size());
      assertEquals(1, two.resources.size());
      assertNotSame(one.resources.getFirst(), two.resources.getFirst());
      assertFalse(first.isClosed());
      assertFalse(other.isClosed());
    }
    assertEquals(List.of("GC_CLOSE", "REGISTRY_CLOSE"), events1);
    assertEquals(List.of("GC_CLOSE", "REGISTRY_CLOSE"), events2);
  }

  @Test
  void apistd013FiniteIndependentConcurrentCompositions() throws Exception {
    try (var workers = Executors.newFixedThreadPool(4)) {
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
                    ApiStandardMetrics.install(
                        source, "DEBUG", resource -> true, action, action, action);
                    assertEquals(3, local.get());
                    assertFalse(source.isClosed());
                    assertEquals(0, source.closes.get());
                  }
                }));
      for (var job : jobs) job.get(10, TimeUnit.SECONDS);
      assertEquals(192, total.get());
    }
  }
}
