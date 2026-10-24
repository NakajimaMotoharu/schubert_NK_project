package dev.codex.schubert.nk.web.monitoring;

import static org.junit.jupiter.api.Assertions.*;

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
            "STANDARD",
            () -> {
              calls.incrementAndGet();
              throw new AssertionError("not read");
            }));
    assertEquals(0, calls.get());
  }

  @Test
  void webpay002StandardDownPreservesLiteralWithoutSupplierRead() {
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
    for (String mode : List.of("", "debug", "DEBUG ", "UNKNOWN"))
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
                            throw new AssertionError("not read");
                          }))
              .getMessage());
    assertEquals(0, calls.get());
  }

  @Test
  void webpay006NullModeAndSupplierFailBeforeResolution() {
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
  void webpay007NullResolvedSourceNeverFallsBackToReadyOnly() {
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
  void webpay008ProviderRuntimeAndErrorKeepIdentity() {
    for (Throwable failure :
        List.of(new IllegalStateException("fixture"), new AssertionError("fixture")))
      assertSame(
          failure,
          assertThrows(
              failure.getClass(), () -> payload.render(true, "DEBUG", () -> fail(failure))));
  }

  @Test
  void webpay009IncompatibleSourceNeverReturnsReadyOnly() {
    class Plain extends SimpleMeterRegistry implements AutoCloseable {}
    try (var source = new Plain()) {
      assertThrows(
          IllegalArgumentException.class, () -> payload.render(true, "DEBUG", () -> source));
      assertFalse(source.isClosed());
    }
  }

  @Test
  void webpay010FormatterRuntimeAndErrorKeepBorrowedOwner() {
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
  void webpay011ClosedSourceIsNotReopenedOrClosedAgain() {
    var source = new Borrowed();
    source.close();
    assertThrows(IllegalStateException.class, () -> payload.render(true, "DEBUG", () -> source));
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
}
