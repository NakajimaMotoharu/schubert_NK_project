package dev.codex.schubert.nk.web.monitoring;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import io.micrometer.core.instrument.Counter;
import io.micrometer.core.instrument.Gauge;
import io.micrometer.core.instrument.Meter;
import io.micrometer.core.instrument.MockClock;
import io.micrometer.core.instrument.simple.SimpleMeterRegistry;
import java.lang.ref.Reference;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.Test;

/** WEBPAY001..013/1800: independent readiness/custom wire literals, supplier/source ownership. */
class WebCustomMetricPayloadTest {
  private static final String DEBUG_MODE = "DEBUG";
  private static final String STANDARD_MODE = "STANDARD";
  private static final String UNEXPECTED_PROVIDER_MESSAGE = "not read";
  private static final String FAILURE_FIXTURE_MESSAGE = "fixture";
  private static final String READY_ONE =
      "# TYPE schubert_nk_web_ready gauge\nschubert_nk_web_ready 1\n";
  private static final String READY_ZERO =
      "# TYPE schubert_nk_web_ready gauge\nschubert_nk_web_ready 0\n";
  private static final String CUSTOM =
      "# TYPE nk_db_pool_connections gauge\nnk_db_pool_connections{service=\"WEB\",state=\"active\"} 7.5\n# TYPE nk_http_requests_total counter\nnk_http_requests_total{method=\"GET\",route=\"/login\",service=\"WEB\",status_class=\"2xx\"} 2.5\n";
  private final WebCustomMetricPayload payload = new WebCustomMetricPayload();

  private static final class Bundle implements AutoCloseable {
    final OverflowSafeHttpMeterRegistry source = new OverflowSafeHttpMeterRegistry(new MockClock());
    final double[] value = {7.5};

    Bundle() {
      Gauge.builder("nk_db_pool_connections", value, a -> a[0])
          .tags("service", "WEB", "state", "active")
          .register(source);
      Counter.builder("nk_http_requests_total")
          .tags("method", "GET", "route", "/login", "service", "WEB", "status_class", "2xx")
          .register(source)
          .increment(2.5);
    }

    String render(WebCustomMetricPayload renderer, boolean ready, AtomicInteger calls) {
      try {
        return renderer.render(
            ready,
            DEBUG_MODE,
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
      implements OverflowSafeDurationSupport, AutoCloseable {
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
  void webpay001StandardReadyPreservesLiteralWithoutSupplierRead() {
    var calls = new AtomicInteger();
    assertEquals(
        READY_ONE,
        payload.render(
            true,
            STANDARD_MODE,
            () -> {
              calls.incrementAndGet();
              throw new AssertionError(UNEXPECTED_PROVIDER_MESSAGE);
            }));
    assertEquals(0, calls.get());
  }

  @Test
  void webpay002StandardDownPreservesLiteralWithoutSupplierRead() {
    assertEquals(
        READY_ZERO,
        payload.render(
            false,
            STANDARD_MODE,
            () -> {
              throw new AssertionError(UNEXPECTED_PROVIDER_MESSAGE);
            }));
  }

  @Test
  void webpay003DebugReadyAppendsIndependentCustomAndReadsSupplierOnce() {
    try (var bundle = new Bundle()) {
      var calls = new AtomicInteger();
      assertEquals(READY_ONE + CUSTOM, bundle.render(payload, true, calls));
      assertEquals(1, calls.get());
      assertFalse(bundle.source.isClosed());
    }
  }

  @Test
  void webpay004DebugDownDoesNotInventHealthyReadiness() {
    try (var bundle = new Bundle()) {
      var calls = new AtomicInteger();
      assertEquals(READY_ZERO + CUSTOM, bundle.render(payload, false, calls));
      assertEquals(1, calls.get());
      assertFalse(bundle.source.isClosed());
    }
  }

  @Test
  void webpay005UnknownModesNeverResolveSource() {
    var calls = new AtomicInteger();
    for (String mode : List.of("", "debug", "DEBUG ", "UNKNOWN", "DEBTf", "STANDAQc"))
      assertEquals(
          "invalid monitoring mode",
          assertThrows(
                  IllegalArgumentException.class,
                  () ->
                      payload.render(
                          true,
                          mode,
                          () -> {
                            calls.incrementAndGet();
                            throw new AssertionError(UNEXPECTED_PROVIDER_MESSAGE);
                          }))
              .getMessage());
    assertEquals(0, calls.get());
  }

  @Test
  void webpay006NullModeAndSupplierFailBeforeResolution() {
    assertThrows(NullPointerException.class, () -> payload.render(true, STANDARD_MODE, null));
    var calls = new AtomicInteger();
    assertThrows(
        NullPointerException.class,
        () ->
            payload.render(
                false,
                null,
                () -> {
                  calls.incrementAndGet();
                  throw new AssertionError(UNEXPECTED_PROVIDER_MESSAGE);
                }));
    assertEquals(0, calls.get());
  }

  @Test
  void webpay007NullResolvedSourceNeverFallsBackToReadyOnly() {
    var calls = new AtomicInteger();
    assertThrows(
        NullPointerException.class,
        () ->
            payload.render(
                true,
                DEBUG_MODE,
                () -> {
                  calls.incrementAndGet();
                  return null;
                }));
    assertEquals(1, calls.get());
  }

  @Test
  void webpay008ProviderRuntimeAndErrorKeepIdentity() {
    for (Throwable failure :
        List.of(
            new IllegalStateException(FAILURE_FIXTURE_MESSAGE),
            new AssertionError(FAILURE_FIXTURE_MESSAGE)))
      assertSame(
          failure,
          assertThrows(
              failure.getClass(), () -> payload.render(true, DEBUG_MODE, () -> fail(failure))));
  }

  @Test
  void webpay009IncompatibleSourceNeverReturnsReadyOnly() {
    class Plain extends SimpleMeterRegistry implements AutoCloseable {}
    try (var source = new Plain()) {
      assertThrows(
          IllegalArgumentException.class, () -> payload.render(true, DEBUG_MODE, () -> source));
      assertFalse(source.isClosed());
    }
  }

  @Test
  void webpay010FormatterRuntimeAndErrorKeepBorrowedOwner() {
    for (Throwable failure :
        List.of(
            new IllegalStateException(FAILURE_FIXTURE_MESSAGE),
            new AssertionError(FAILURE_FIXTURE_MESSAGE))) {
      try (var source = new Broken(failure)) {
        assertSame(
            failure,
            assertThrows(
                failure.getClass(), () -> payload.render(false, DEBUG_MODE, () -> source)));
        assertEquals(0, source.closes.get());
        assertFalse(source.isClosed());
      }
    }
  }

  @Test
  void webpay011ClosedSourceIsNotReopenedOrClosedAgain() {
    var source = new Borrowed();
    source.close();
    assertThrows(IllegalStateException.class, () -> payload.render(true, DEBUG_MODE, () -> source));
    assertEquals(1, source.closes.get());
    assertTrue(source.isClosed());
  }

  @Test
  void webpay012SameRendererDoesNotRetainOneOfTwoSources() {
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
  void webpay013FiniteConcurrentIndependentPayloads() throws Exception {
    var workers = Executors.newFixedThreadPool(4);
    try {
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
    } finally {
      workers.shutdownNow();
      assertTrue(workers.awaitTermination(10, TimeUnit.SECONDS));
    }
  }

  private static final String FULL_STANDARD =
      "# TYPE system_cpu_count gauge\nsystem_cpu_count{service=\"WEB\"} 42.0\n";

  private static final class FullProbe
      extends io.micrometer.prometheusmetrics.PrometheusMeterRegistry {
    final AtomicInteger scrapes = new AtomicInteger();
    final AtomicInteger closes = new AtomicInteger();
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

    @Override
    public void close() {
      closes.incrementAndGet();
      super.close();
    }
  }

  private static WebStandardMetricSource fullOwner(FullProbe probe) {
    var owner = new WebStandardMetricSource(() -> probe, (source, gc) -> {});
    boolean transferred = false;
    try {

      owner.bind(DEBUG_MODE);
      transferred = true;
      return owner;

    } finally {
      if (!transferred) owner.close();
    }
  }

  @Test
  void webfull001StandardKeepsLegacyBytesAndNeverAcquiresEitherSource() {
    var factories = new AtomicInteger();
    var calls = new AtomicInteger();
    var standard =
        new WebStandardMetricSource(
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
              STANDARD_MODE,
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
              STANDARD_MODE,
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
  void webfull002LiteralFullOrderAndActualOfficialSdkValue() {
    var probe = new FullProbe();
    try (var bundle = new Bundle();
        var standard = fullOwner(probe)) {
      assertEquals(
          READY_ZERO + CUSTOM + FULL_STANDARD,
          payload.render(false, DEBUG_MODE, () -> bundle.source, standard));
      assertEquals(1, probe.scrapes.get());
      assertFalse(bundle.source.isClosed());
      assertFalse(probe.isClosed());
      Reference.reachabilityFence(bundle);
    }
    try (var bundle = new Bundle();
        var standard = new WebStandardMetricSource()) {
      standard.bind(DEBUG_MODE);
      String actual = payload.render(true, DEBUG_MODE, () -> bundle.source, standard);
      assertTrue(actual.startsWith(READY_ONE + CUSTOM));
      String expected =
          "system_cpu_count{service=\"WEB\"} "
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
  void webfull003UnboundAndClosedStandardNeverBecomePartialSuccess() {
    var calls = new AtomicInteger();
    var standard = new WebStandardMetricSource();
    try (var bundle = new Bundle()) {
      assertThrows(
          IllegalStateException.class,
          () ->
              payload.render(
                  true,
                  DEBUG_MODE,
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
                  DEBUG_MODE,
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
  void webfull004NullAndUnknownBoundariesReadNeitherProvider() {
    var probe = new FullProbe();
    var calls = new AtomicInteger();
    java.util.function.Supplier<io.micrometer.core.instrument.MeterRegistry> source =
        () -> {
          calls.incrementAndGet();
          throw new AssertionError("unexpected provider");
        };
    try (var standard = fullOwner(probe)) {
      assertThrows(
          NullPointerException.class, () -> payload.render(true, DEBUG_MODE, source, null));
      assertThrows(
          NullPointerException.class, () -> payload.render(true, DEBUG_MODE, null, standard));
      assertThrows(NullPointerException.class, () -> payload.render(true, null, source, standard));
      assertThrows(
          IllegalArgumentException.class, () -> payload.render(true, "unknown", source, standard));
      assertEquals(0, calls.get());
      assertEquals(0, probe.scrapes.get());
    }
  }

  @Test
  void webfull005CustomRuntimeWinsBeforeStandardFailure() {
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
                      DEBUG_MODE,
                      () -> {
                        throw failure;
                      },
                      standard)));
      assertEquals(0, probe.scrapes.get());
      assertFalse(probe.isClosed());
    }
  }

  @Test
  void webfull006CustomErrorIdentityIsPreservedWithoutStandardRead() {
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
                      DEBUG_MODE,
                      () -> {
                        throw failure;
                      },
                      standard)));
      assertEquals(0, probe.scrapes.get());
      assertFalse(probe.isClosed());
    }
  }

  @Test
  void webfull007CustomFormatterFailureKeepsBorrowedResources() {
    var probe = new FullProbe();
    var failure = new IllegalStateException("formatter fixture");
    try (var broken = new Broken(failure);
        var standard = fullOwner(probe)) {
      assertSame(
          failure,
          assertThrows(
              IllegalStateException.class,
              () -> payload.render(true, DEBUG_MODE, () -> broken, standard)));
      assertEquals(0, probe.scrapes.get());
      assertEquals(0, broken.closes.get());
      assertFalse(probe.isClosed());
    }
  }

  @Test
  void webfull008StandardRuntimeNeverFallsBackOrClosesBorrowedCustom() {
    var probe = new FullProbe();
    var failure = new IllegalArgumentException("standard fixture");
    probe.failure = java.util.Optional.of(failure);
    try (var bundle = new Bundle();
        var standard = fullOwner(probe)) {
      assertSame(
          failure,
          assertThrows(
              IllegalArgumentException.class,
              () -> payload.render(true, DEBUG_MODE, () -> bundle.source, standard)));
      assertEquals(1, probe.scrapes.get());
      assertFalse(bundle.source.isClosed());
      assertFalse(probe.isClosed());
      Reference.reachabilityFence(bundle);
    }
  }

  @Test
  void webfull009StandardErrorIdentityNeverBecomesReadyOnlySuccess() {
    var probe = new FullProbe();
    var failure = new AssertionError("standard fatal fixture");
    probe.failure = java.util.Optional.of(failure);
    try (var bundle = new Bundle();
        var standard = fullOwner(probe)) {
      assertSame(
          failure,
          assertThrows(
              AssertionError.class,
              () -> payload.render(false, DEBUG_MODE, () -> bundle.source, standard)));
      assertEquals(1, probe.scrapes.get());
      assertFalse(bundle.source.isClosed());
      Reference.reachabilityFence(bundle);
    }
  }

  @Test
  void webfull010ContractViolatingNullTextIsRejectedNotConcatenated() {
    var probe = new FullProbe();
    probe.nullText = true;
    try (var bundle = new Bundle();
        var standard = fullOwner(probe)) {
      assertThrows(
          NullPointerException.class,
          () -> payload.render(true, DEBUG_MODE, () -> bundle.source, standard));
      assertEquals(1, probe.scrapes.get());
      assertFalse(bundle.source.isClosed());
      Reference.reachabilityFence(bundle);
    }
  }

  @Test
  void webfull011ConcurrentFullScrapesKeepIndependentGoldenAndOwnership() throws Exception {
    try (var bundle = new Bundle();
        var standard = new WebStandardMetricSource()) {
      standard.bind(DEBUG_MODE);
      String expected =
          "system_cpu_count{service=\"WEB\"} "
              + (double) Runtime.getRuntime().availableProcessors();
      var executor = Executors.newFixedThreadPool(4);
      try {
        var tasks = new ArrayList<java.util.concurrent.Callable<String>>();
        for (int index = 0; index < 64; index++)
          tasks.add(() -> payload.render(true, DEBUG_MODE, () -> bundle.source, standard));
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
  void webfull012CallerCloseBetweenSourcesCannotReturnPartialText() throws Exception {
    var entered = new java.util.concurrent.CountDownLatch(1);
    var release = new java.util.concurrent.CountDownLatch(1);
    var probe = new FullProbe();
    try (var standard = fullOwner(probe);
        var bundle = new Bundle()) {
      var executor = Executors.newSingleThreadExecutor();
      try {
        var future =
            executor.submit(
                () ->
                    payload.render(
                        true,
                        DEBUG_MODE,
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
      }
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

  @Test
  void webfull013HelperReleasesRejectedCandidateBeforeReturningOwner() {
    var probe = new FullProbe();
    try {
      probe.close();
      assertEquals(1, probe.closes.get());
      var failure = assertThrows(IllegalStateException.class, () -> fullOwner(probe));
      assertEquals("standard metric registry closed", failure.getMessage());
      assertEquals(2, probe.closes.get());
      assertEquals(0, probe.scrapes.get());
      assertTrue(probe.isClosed());
    } finally {
      probe.close();
    }
  }
}
