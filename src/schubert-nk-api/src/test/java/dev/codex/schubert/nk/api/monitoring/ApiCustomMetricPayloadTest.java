package dev.codex.schubert.nk.api.monitoring;

import static org.junit.jupiter.api.Assertions.*;

import io.micrometer.core.instrument.Counter;
import io.micrometer.core.instrument.Gauge;
import io.micrometer.core.instrument.Meter;
import io.micrometer.core.instrument.MockClock;
import io.micrometer.core.instrument.simple.SimpleConfig;
import io.micrometer.core.instrument.simple.SimpleMeterRegistry;
import java.lang.ref.Reference;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.Test;

/** APIPAY001..013/1800: independent readiness/custom wire literals, supplier/source ownership. */
class ApiCustomMetricPayloadTest {
  private static final String READY_ONE =
      "# TYPE schubert_nk_api_ready gauge\nschubert_nk_api_ready 1\n";
  private static final String READY_ZERO =
      "# TYPE schubert_nk_api_ready gauge\nschubert_nk_api_ready 0\n";
  private static final String CUSTOM =
      "# TYPE nk_db_pool_connections gauge\nnk_db_pool_connections{service=\"API\",state=\"active\"} 7.5\n# TYPE nk_inbox_replays_total counter\nnk_inbox_replays_total{layout=\"LGNREQ01\",result=\"0000\"} 2.5\n";
  private final ApiCustomMetricPayload payload = new ApiCustomMetricPayload();

  private static final class Bundle implements AutoCloseable {
    final ExactDurationMeterRegistry source =
        new ExactDurationMeterRegistry(SimpleConfig.DEFAULT, new MockClock());
    final double[] value = {7.5};

    Bundle() {
      Gauge.builder("nk_db_pool_connections", value, a -> a[0])
          .tags("service", "API", "state", "active")
          .register(source);
      Counter.builder("nk_inbox_replays_total")
          .tags("layout", "LGNREQ01", "result", "0000")
          .register(source)
          .increment(2.5);
    }

    String render(ApiCustomMetricPayload renderer, boolean ready, AtomicInteger calls) {
      try {
        return renderer.render(
            ready,
            "DEBUG",
            () -> {
              calls.incrementAndGet();
              return source;
            });
      } finally {
        Reference.reachabilityFence(this);
      }
    }

    public void close() {
      source.close();
    }
  }

  private static class Borrowed extends SimpleMeterRegistry
      implements ExactDurationSupport, AutoCloseable {
    final AtomicInteger closes = new AtomicInteger();

    public void close() {
      closes.incrementAndGet();
      super.close();
    }
  }

  private static final class Broken extends Borrowed {
    final Throwable failure;

    Broken(Throwable failure) {
      this.failure = failure;
    }

    public List<Meter> getMeters() {
      return fail(failure);
    }
  }

  private static <T> T fail(Throwable failure) {
    if (failure instanceof RuntimeException runtime) throw runtime;
    throw (Error) failure;
  }

  @Test
  void apipay001StandardReadyPreservesLiteralWithoutSupplierRead() {
    var calls = new AtomicInteger();
    assertEquals(
        READY_ONE,
        payload.render(
            true,
            "STANDARD",
            () -> {
              calls.incrementAndGet();
              throw new AssertionError("not read");
            }));
    assertEquals(0, calls.get());
  }

  @Test
  void apipay002StandardDownPreservesLiteralWithoutSupplierRead() {
    assertEquals(
        READY_ZERO,
        payload.render(
            false,
            "STANDARD",
            () -> {
              throw new AssertionError("not read");
            }));
  }

  @Test
  void apipay003DebugReadyAppendsIndependentCustomAndReadsSupplierOnce() {
    try (var bundle = new Bundle()) {
      var calls = new AtomicInteger();
      assertEquals(READY_ONE + CUSTOM, bundle.render(payload, true, calls));
      assertEquals(1, calls.get());
      assertFalse(bundle.source.isClosed());
    }
  }

  @Test
  void apipay004DebugDownDoesNotInventHealthyReadiness() {
    try (var bundle = new Bundle()) {
      var calls = new AtomicInteger();
      assertEquals(READY_ZERO + CUSTOM, bundle.render(payload, false, calls));
      assertEquals(1, calls.get());
      assertFalse(bundle.source.isClosed());
    }
  }

  @Test
  void apipay005UnknownModesNeverResolveSource() {
    var calls = new AtomicInteger();
    for (String mode : List.of("", "debug", "DEBUG ", "UNKNOWN"))
      assertEquals(
          "CONFIG_INVALID",
          assertThrows(
                  IllegalArgumentException.class,
                  () ->
                      payload.render(
                          true,
                          mode,
                          () -> {
                            calls.incrementAndGet();
                            throw new AssertionError("not read");
                          }))
              .getMessage());
    assertEquals(0, calls.get());
  }

  @Test
  void apipay006NullModeAndSupplierFailBeforeResolution() {
    assertThrows(NullPointerException.class, () -> payload.render(true, "STANDARD", null));
    var calls = new AtomicInteger();
    assertThrows(
        NullPointerException.class,
        () ->
            payload.render(
                false,
                null,
                () -> {
                  calls.incrementAndGet();
                  throw new AssertionError("not read");
                }));
    assertEquals(0, calls.get());
  }

  @Test
  void apipay007NullResolvedSourceNeverFallsBackToReadyOnly() {
    var calls = new AtomicInteger();
    assertThrows(
        NullPointerException.class,
        () ->
            payload.render(
                true,
                "DEBUG",
                () -> {
                  calls.incrementAndGet();
                  return null;
                }));
    assertEquals(1, calls.get());
  }

  @Test
  void apipay008ProviderRuntimeAndErrorKeepIdentity() {
    for (Throwable failure :
        List.of(new IllegalStateException("fixture"), new AssertionError("fixture")))
      assertSame(
          failure,
          assertThrows(
              failure.getClass(), () -> payload.render(true, "DEBUG", () -> fail(failure))));
  }

  @Test
  void apipay009IncompatibleSourceNeverReturnsReadyOnly() {
    class Plain extends SimpleMeterRegistry implements AutoCloseable {}
    try (var source = new Plain()) {
      assertThrows(
          IllegalArgumentException.class, () -> payload.render(true, "DEBUG", () -> source));
      assertFalse(source.isClosed());
    }
  }

  @Test
  void apipay010FormatterRuntimeAndErrorKeepBorrowedOwner() {
    for (Throwable failure :
        List.of(new IllegalStateException("fixture"), new AssertionError("fixture"))) {
      try (var source = new Broken(failure)) {
        assertSame(
            failure,
            assertThrows(failure.getClass(), () -> payload.render(false, "DEBUG", () -> source)));
        assertEquals(0, source.closes.get());
        assertFalse(source.isClosed());
      }
    }
  }

  @Test
  void apipay011ClosedSourceIsNotReopenedOrClosedAgain() {
    var source = new Borrowed();
    source.close();
    assertThrows(IllegalStateException.class, () -> payload.render(true, "DEBUG", () -> source));
    assertEquals(1, source.closes.get());
    assertTrue(source.isClosed());
  }

  @Test
  void apipay012SameRendererDoesNotRetainOneOfTwoSources() {
    try (var first = new Bundle();
        var other = new Bundle()) {
      var calls = new AtomicInteger();
      assertEquals(READY_ONE + CUSTOM, first.render(payload, true, calls));
      assertEquals(READY_ZERO + CUSTOM, other.render(payload, false, calls));
      assertEquals(2, calls.get());
      assertFalse(first.source.isClosed());
      assertFalse(other.source.isClosed());
    }
  }

  @Test
  void apipay013FiniteConcurrentIndependentPayloads() throws Exception {
    try (var workers = Executors.newFixedThreadPool(4)) {
      var jobs = new ArrayList<Future<?>>();
      var total = new AtomicInteger();
      for (int i = 0; i < 64; i++) {
        boolean ready = (i % 2) == 0;
        jobs.add(
            workers.submit(
                () -> {
                  try (var bundle = new Bundle()) {
                    var calls = new AtomicInteger();
                    assertEquals(
                        (ready ? READY_ONE : READY_ZERO) + CUSTOM,
                        bundle.render(payload, ready, calls));
                    assertEquals(1, calls.get());
                    assertFalse(bundle.source.isClosed());
                    total.incrementAndGet();
                  }
                }));
      }
      for (var job : jobs) job.get(10, TimeUnit.SECONDS);
      assertEquals(64, total.get());
    }
  }

  private static final String FULL_STANDARD =
      "# TYPE system_cpu_count gauge\nsystem_cpu_count{service=\"API\"} 42.0\n";

  private static final class FullProbe
      extends io.micrometer.prometheusmetrics.PrometheusMeterRegistry {
    final AtomicInteger scrapes = new AtomicInteger();
    java.util.Optional<Throwable> failure = java.util.Optional.empty();
    boolean nullText;

    FullProbe() {
      super(io.micrometer.prometheusmetrics.PrometheusConfig.DEFAULT);
    }

    @Override
    public String scrape() {
      scrapes.incrementAndGet();
      if (failure.isPresent()) return fail(failure.orElseThrow());
      if (nullText) return null;
      return FULL_STANDARD;
    }
  }

  private static ApiStandardMetricSource fullOwner(FullProbe probe) {
    var owner = new ApiStandardMetricSource(() -> probe, (source, gc) -> {});
    owner.bind("DEBUG");
    return owner;
  }

  @Test
  void apifull001StandardKeepsLegacyBytesAndNeverAcquiresEitherSource() {
    var factories = new AtomicInteger();
    var calls = new AtomicInteger();
    var standard =
        new ApiStandardMetricSource(
            () -> {
              factories.incrementAndGet();
              throw new AssertionError("unexpected source");
            },
            (source, gc) -> {});
    try {
      assertEquals(
          READY_ONE,
          payload.render(
              true,
              "STANDARD",
              () -> {
                calls.incrementAndGet();
                throw new AssertionError("unexpected custom");
              },
              standard));
      standard.close();
      assertEquals(
          READY_ZERO,
          payload.render(
              false,
              "STANDARD",
              () -> {
                calls.incrementAndGet();
                throw new AssertionError("unexpected custom");
              },
              standard));
      assertEquals(0, calls.get());
      assertEquals(0, factories.get());
    } finally {
      standard.close();
    }
  }

  @Test
  void apifull002LiteralFullOrderAndActualOfficialSdkValue() {
    var probe = new FullProbe();
    try (var bundle = new Bundle();
        var standard = fullOwner(probe)) {
      assertEquals(
          READY_ZERO + CUSTOM + FULL_STANDARD,
          payload.render(false, "DEBUG", () -> bundle.source, standard));
      assertEquals(1, probe.scrapes.get());
      assertFalse(bundle.source.isClosed());
      assertFalse(probe.isClosed());
      Reference.reachabilityFence(bundle);
    }
    try (var bundle = new Bundle();
        var standard = new ApiStandardMetricSource()) {
      standard.bind("DEBUG");
      String actual = payload.render(true, "DEBUG", () -> bundle.source, standard);
      assertTrue(actual.startsWith(READY_ONE + CUSTOM));
      String expected =
          "system_cpu_count{service=\"API\"} "
              + (double) Runtime.getRuntime().availableProcessors();
      assertTrue(actual.lines().anyMatch(expected::equals));
      assertTrue(actual.contains("jvm_memory_used_bytes{"));
      var types = actual.lines().filter(line -> line.startsWith("# TYPE ")).toList();
      assertEquals(types.size(), types.stream().distinct().count());
      assertFalse(bundle.source.isClosed());
      Reference.reachabilityFence(bundle);
    }
  }

  @Test
  void apifull003UnboundAndClosedStandardNeverBecomePartialSuccess() {
    var calls = new AtomicInteger();
    var standard = new ApiStandardMetricSource();
    try (var bundle = new Bundle()) {
      assertThrows(
          IllegalStateException.class,
          () ->
              payload.render(
                  true,
                  "DEBUG",
                  () -> {
                    calls.incrementAndGet();
                    return bundle.source;
                  },
                  standard));
      standard.close();
      assertThrows(
          IllegalStateException.class,
          () ->
              payload.render(
                  false,
                  "DEBUG",
                  () -> {
                    calls.incrementAndGet();
                    return bundle.source;
                  },
                  standard));
      assertEquals(2, calls.get());
      assertFalse(bundle.source.isClosed());
      Reference.reachabilityFence(bundle);
    } finally {
      standard.close();
    }
  }

  @Test
  void apifull004NullAndUnknownBoundariesReadNeitherProvider() {
    var probe = new FullProbe();
    var calls = new AtomicInteger();
    java.util.function.Supplier<io.micrometer.core.instrument.MeterRegistry> source =
        () -> {
          calls.incrementAndGet();
          throw new AssertionError("unexpected provider");
        };
    try (var standard = fullOwner(probe)) {
      assertThrows(NullPointerException.class, () -> payload.render(true, "DEBUG", source, null));
      assertThrows(NullPointerException.class, () -> payload.render(true, "DEBUG", null, standard));
      assertThrows(NullPointerException.class, () -> payload.render(true, null, source, standard));
      assertThrows(
          IllegalArgumentException.class, () -> payload.render(true, "unknown", source, standard));
      assertEquals(0, calls.get());
      assertEquals(0, probe.scrapes.get());
    }
  }

  @Test
  void apifull005CustomRuntimeWinsBeforeStandardFailure() {
    var probe = new FullProbe();
    probe.failure = java.util.Optional.of(new AssertionError("unreached standard"));
    var failure = new IllegalArgumentException("custom fixture");
    try (var standard = fullOwner(probe)) {
      assertSame(
          failure,
          assertThrows(
              IllegalArgumentException.class,
              () ->
                  payload.render(
                      true,
                      "DEBUG",
                      () -> {
                        throw failure;
                      },
                      standard)));
      assertEquals(0, probe.scrapes.get());
      assertFalse(probe.isClosed());
    }
  }

  @Test
  void apifull006CustomErrorIdentityIsPreservedWithoutStandardRead() {
    var probe = new FullProbe();
    probe.failure = java.util.Optional.of(new IllegalStateException("unreached standard"));
    var failure = new AssertionError("custom fatal fixture");
    try (var standard = fullOwner(probe)) {
      assertSame(
          failure,
          assertThrows(
              AssertionError.class,
              () ->
                  payload.render(
                      false,
                      "DEBUG",
                      () -> {
                        throw failure;
                      },
                      standard)));
      assertEquals(0, probe.scrapes.get());
      assertFalse(probe.isClosed());
    }
  }

  @Test
  void apifull007CustomFormatterFailureKeepsBorrowedResources() {
    var probe = new FullProbe();
    var failure = new IllegalStateException("formatter fixture");
    try (var broken = new Broken(failure);
        var standard = fullOwner(probe)) {
      assertSame(
          failure,
          assertThrows(
              IllegalStateException.class,
              () -> payload.render(true, "DEBUG", () -> broken, standard)));
      assertEquals(0, probe.scrapes.get());
      assertEquals(0, broken.closes.get());
      assertFalse(probe.isClosed());
    }
  }

  @Test
  void apifull008StandardRuntimeNeverFallsBackOrClosesBorrowedCustom() {
    var probe = new FullProbe();
    var failure = new IllegalArgumentException("standard fixture");
    probe.failure = java.util.Optional.of(failure);
    try (var bundle = new Bundle();
        var standard = fullOwner(probe)) {
      assertSame(
          failure,
          assertThrows(
              IllegalArgumentException.class,
              () -> payload.render(true, "DEBUG", () -> bundle.source, standard)));
      assertEquals(1, probe.scrapes.get());
      assertFalse(bundle.source.isClosed());
      assertFalse(probe.isClosed());
      Reference.reachabilityFence(bundle);
    }
  }

  @Test
  void apifull009StandardErrorIdentityNeverBecomesReadyOnlySuccess() {
    var probe = new FullProbe();
    var failure = new AssertionError("standard fatal fixture");
    probe.failure = java.util.Optional.of(failure);
    try (var bundle = new Bundle();
        var standard = fullOwner(probe)) {
      assertSame(
          failure,
          assertThrows(
              AssertionError.class,
              () -> payload.render(false, "DEBUG", () -> bundle.source, standard)));
      assertEquals(1, probe.scrapes.get());
      assertFalse(bundle.source.isClosed());
      Reference.reachabilityFence(bundle);
    }
  }

  @Test
  void apifull010ContractViolatingNullTextIsRejectedNotConcatenated() {
    var probe = new FullProbe();
    probe.nullText = true;
    try (var bundle = new Bundle();
        var standard = fullOwner(probe)) {
      assertThrows(
          NullPointerException.class,
          () -> payload.render(true, "DEBUG", () -> bundle.source, standard));
      assertEquals(1, probe.scrapes.get());
      assertFalse(bundle.source.isClosed());
      Reference.reachabilityFence(bundle);
    }
  }

  @Test
  void apifull011ConcurrentFullScrapesKeepIndependentGoldenAndOwnership() throws Exception {
    try (var bundle = new Bundle();
        var standard = new ApiStandardMetricSource()) {
      standard.bind("DEBUG");
      String expected =
          "system_cpu_count{service=\"API\"} "
              + (double) Runtime.getRuntime().availableProcessors();
      var executor = Executors.newFixedThreadPool(4);
      try {
        var tasks = new ArrayList<java.util.concurrent.Callable<String>>();
        for (int index = 0; index < 64; index++)
          tasks.add(() -> payload.render(true, "DEBUG", () -> bundle.source, standard));
        for (var future : executor.invokeAll(tasks, 30, TimeUnit.SECONDS)) {
          String actual = future.get(30, TimeUnit.SECONDS);
          assertTrue(actual.startsWith(READY_ONE + CUSTOM));
          assertTrue(actual.lines().anyMatch(expected::equals));
        }
        assertFalse(bundle.source.isClosed());
      } finally {
        executor.shutdownNow();
        assertTrue(executor.awaitTermination(30, TimeUnit.SECONDS));
      }
      Reference.reachabilityFence(bundle);
    }
  }

  @Test
  void apifull012CallerCloseBetweenSourcesCannotReturnPartialText() throws Exception {
    var entered = new java.util.concurrent.CountDownLatch(1);
    var release = new java.util.concurrent.CountDownLatch(1);
    var probe = new FullProbe();
    var standard = fullOwner(probe);
    var executor = Executors.newSingleThreadExecutor();
    try (var bundle = new Bundle()) {
      var future =
          executor.submit(
              () ->
                  payload.render(
                      true,
                      "DEBUG",
                      () -> {
                        entered.countDown();
                        awaitFull(release);
                        return bundle.source;
                      },
                      standard));
      assertTrue(entered.await(30, TimeUnit.SECONDS));
      standard.close();
      release.countDown();
      var failure =
          assertThrows(
              java.util.concurrent.ExecutionException.class,
              () -> future.get(30, TimeUnit.SECONDS));
      assertInstanceOf(IllegalStateException.class, failure.getCause());
      assertEquals(0, probe.scrapes.get());
      assertFalse(bundle.source.isClosed());
      Reference.reachabilityFence(bundle);
    } finally {
      release.countDown();
      executor.shutdownNow();
      assertTrue(executor.awaitTermination(30, TimeUnit.SECONDS));
      standard.close();
    }
  }

  private static void awaitFull(java.util.concurrent.CountDownLatch release) {
    try {
      assertTrue(release.await(30, TimeUnit.SECONDS));
    } catch (InterruptedException interrupted) {
      Thread.currentThread().interrupt();
      throw new IllegalStateException("owned full fixture interrupted");
    }
  }
}
