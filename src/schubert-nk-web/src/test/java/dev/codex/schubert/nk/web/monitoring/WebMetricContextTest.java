package dev.codex.schubert.nk.web.monitoring;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import io.micrometer.core.instrument.Gauge;
import io.micrometer.core.instrument.Meter;
import io.micrometer.core.instrument.MeterRegistry;
import io.micrometer.core.instrument.simple.SimpleMeterRegistry;
import io.micrometer.prometheusmetrics.PrometheusConfig;
import io.micrometer.prometheusmetrics.PrometheusMeterRegistry;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicReference;
import java.util.function.Function;
import org.junit.jupiter.api.Test;

/** 1815 WEBMCTX001..026: SDK ownership only, no external service or opaque data oracle. */
class WebMetricContextTest {
  private static final String READY_ONE =
      "# TYPE schubert_nk_web_ready gauge\nschubert_nk_web_ready 1\n";
  private static final String READY_ZERO =
      "# TYPE schubert_nk_web_ready gauge\nschubert_nk_web_ready 0\n";
  private static final String STANDARD =
      "# TYPE system_cpu_count gauge\nsystem_cpu_count{service=\"WEB\"} 42.0\n";
  private static final String UNCONFIRMED = "metric context close unconfirmed";

  private static <T> T raise(Throwable failure) {
    if (failure instanceof RuntimeException runtime) throw runtime;
    throw (Error) failure;
  }

  private static void await(CountDownLatch latch) {
    try {
      assertTrue(latch.await(30, TimeUnit.SECONDS));
    } catch (InterruptedException interrupted) {
      Thread.currentThread().interrupt();
      throw new IllegalStateException("owned fixture interrupted");
    }
  }

  private static final class Custom extends SimpleMeterRegistry
      implements OverflowSafeDurationSupport {
    final List<String> order;
    final AtomicInteger closes = new AtomicInteger();
    Optional<Throwable> closeFailure = Optional.empty();
    Optional<Throwable> readFailure = Optional.empty();
    Optional<Runnable> onRead = Optional.empty();

    Custom(List<String> order) {
      this.order = order;
    }

    @Override
    public List<Meter> getMeters() {
      onRead.ifPresent(Runnable::run);
      if (readFailure.isPresent()) return raise(readFailure.orElseThrow());
      return super.getMeters();
    }

    @Override
    public void close() {
      closes.incrementAndGet();
      order.add("C");
      if (closeFailure.isPresent()) raise(closeFailure.orElseThrow());
      super.close();
    }
  }

  private static final class Standard extends PrometheusMeterRegistry {
    final List<String> order;
    final AtomicInteger closes = new AtomicInteger();
    final AtomicInteger scrapes = new AtomicInteger();
    Optional<Throwable> closeFailure = Optional.empty();
    Optional<Throwable> readFailure = Optional.empty();
    boolean nullText;

    Standard(List<String> order) {
      super(PrometheusConfig.DEFAULT);
      this.order = order;
    }

    @Override
    public String scrape() {
      scrapes.incrementAndGet();
      if (readFailure.isPresent()) return raise(readFailure.orElseThrow());
      return nullText ? null : STANDARD;
    }

    @Override
    public void close() {
      closes.incrementAndGet();
      order.add("S");
      if (closeFailure.isPresent()) raise(closeFailure.orElseThrow());
      super.close();
    }
  }

  private static final class Harness<T> implements AutoCloseable {
    final List<String> order = new ArrayList<>();
    final Custom custom = new Custom(order);
    final Standard standard = new Standard(order);
    final AtomicInteger customCreates = new AtomicInteger();
    final AtomicInteger standardCreates = new AtomicInteger();
    final AtomicInteger setups = new AtomicInteger();
    Optional<Throwable> customAcquireFailure = Optional.empty();
    Optional<Throwable> standardAcquireFailure = Optional.empty();
    Optional<Runnable> beforeCustom = Optional.empty();
    Optional<Runnable> beforeStandard = Optional.empty();
    Optional<Runnable> beforeSetup = Optional.empty();
    boolean nullCustom;
    boolean nullStandard;
    final WebMetricContext<T> context;

    Harness(String mode, Function<MeterRegistry, T> setup) {
      var standardOwner = new WebStandardMetricSource(this::standard, (registry, gc) -> {});
      context =
          new WebMetricContext<T>(
              mode,
              registry -> {
                setups.incrementAndGet();
                beforeSetup.ifPresent(Runnable::run);
                return setup.apply(registry);
              },
              this::custom,
              standardOwner);
    }

    private MeterRegistry custom() {
      customCreates.incrementAndGet();
      beforeCustom.ifPresent(Runnable::run);
      if (customAcquireFailure.isPresent()) return raise(customAcquireFailure.orElseThrow());
      return nullCustom ? null : custom;
    }

    private PrometheusMeterRegistry standard() {
      standardCreates.incrementAndGet();
      beforeStandard.ifPresent(Runnable::run);
      if (standardAcquireFailure.isPresent()) return raise(standardAcquireFailure.orElseThrow());
      return nullStandard ? null : standard;
    }

    @Override
    public void close() {
      custom.onRead = Optional.empty();
      custom.readFailure = Optional.empty();
      custom.closeFailure = Optional.empty();
      standard.closeFailure = Optional.empty();
      context.close();
      // Only unused fixture candidates remain owned by the fixture, never by the context.
      if (!custom.isClosed()) custom.close();
      if (!standard.isClosed()) standard.close();
    }
  }

  @Test
  void webmctx001StandardHandshakeReadsNoFactoryOrSetup() {
    try (var h =
        new Harness<String>(
            "STANDARD",
            registry -> {
              throw new AssertionError("unexpected setup");
            })) {
      assertEquals(0, h.customCreates.get());
      assertEquals(0, h.standardCreates.get());
      h.context.initialize();
      assertEquals(READY_ONE, h.context.render(true));
      assertEquals(READY_ZERO, h.context.render(false));
      assertTrue(h.context.bindings().isEmpty());
      assertEquals(0, h.customCreates.get());
      assertEquals(0, h.standardCreates.get());
      assertEquals(0, h.setups.get());
    }
  }

  @Test
  void webmctx002DefaultSourceRetainsBindingsAndOfficialSdkGolden() {
    var supplied = new AtomicReference<double[]>();
    try (var context =
        new WebMetricContext<double[]>(
            "DEBUG",
            registry -> {
              double[] value = {7.5};
              supplied.set(value);
              Gauge.builder("nk_db_pool_connections", value, state -> state[0])
                  .tags("service", "WEB", "state", "active")
                  .register(registry);
              return value;
            })) {
      context.initialize();
      double[] value = context.bindings().orElseThrow();
      assertSame(supplied.get(), value);
      String first =
          READY_ONE
              + "# TYPE nk_db_pool_connections gauge\nnk_db_pool_connections{service=\"WEB\",state=\"active\"} 7.5\n";
      String actual = context.render(true);
      assertTrue(actual.startsWith(first));
      String cpu =
          "system_cpu_count{service=\"WEB\"} "
              + (double) Runtime.getRuntime().availableProcessors();
      assertTrue(actual.lines().anyMatch(cpu::equals));
      value[0] = 9.5;
      assertTrue(
          context
              .render(false)
              .startsWith(
                  READY_ZERO
                      + "# TYPE nk_db_pool_connections gauge\nnk_db_pool_connections{service=\"WEB\",state=\"active\"} 9.5\n"));
    }
  }

  @Test
  void webmctx003UninitializedAndClosedBeforeInitNeverAcquire() {
    try (var h = new Harness<String>("DEBUG", registry -> "binding")) {
      assertThrows(IllegalStateException.class, () -> h.context.render(true));
      assertThrows(IllegalStateException.class, h.context::bindings);
      h.context.close();
      assertThrows(IllegalStateException.class, h.context::initialize);
      assertEquals(0, h.customCreates.get());
      assertEquals(0, h.standardCreates.get());
    }
  }

  @Test
  void webmctx004ModeNullAndUnknownFailBeforeSdkAcquisition() {
    assertThrows(
        NullPointerException.class,
        () -> new WebMetricContext<String>(null, registry -> "binding"));
    assertEquals(
        "invalid monitoring mode",
        assertThrows(
                IllegalArgumentException.class,
                () -> new WebMetricContext<String>("unknown", registry -> "binding"))
            .getMessage());
  }

  @Test
  void webmctx005ConstructorPortsAreNonNull() {
    var standard = new WebStandardMetricSource();
    try {
      assertThrows(
          NullPointerException.class,
          () -> new WebMetricContext<String>("DEBUG", null, SimpleMeterRegistry::new, standard));
      assertThrows(
          NullPointerException.class,
          () -> new WebMetricContext<String>("DEBUG", registry -> "binding", null, standard));
      assertThrows(
          NullPointerException.class,
          () ->
              new WebMetricContext<String>(
                  "DEBUG", registry -> "binding", SimpleMeterRegistry::new, null));
    } finally {
      standard.close();
    }
  }

  @Test
  void webmctx006CustomFactoryRuntimePreservesIdentityAndOneAttempt() {
    var failure = new IllegalArgumentException("custom factory fixture");
    try (var h = new Harness<String>("DEBUG", registry -> "binding")) {
      h.customAcquireFailure = Optional.of(failure);
      assertSame(failure, assertThrows(IllegalArgumentException.class, h.context::initialize));
      assertThrows(IllegalStateException.class, h.context::initialize);
      assertThrows(IllegalStateException.class, () -> h.context.render(true));
      assertThrows(IllegalStateException.class, h.context::bindings);
      assertEquals(1, h.customCreates.get());
      assertEquals(0, h.setups.get());
      assertEquals(0, h.standardCreates.get());
    }
  }

  @Test
  void webmctx007CustomFactoryErrorIsNeverNormalized() {
    var failure = new AssertionError("custom factory fatal fixture");
    try (var h = new Harness<String>("DEBUG", registry -> "binding")) {
      h.customAcquireFailure = Optional.of(failure);
      assertSame(failure, assertThrows(AssertionError.class, h.context::initialize));
      assertEquals(0, h.standardCreates.get());
    }
  }

  @Test
  void webmctx008NullCustomRegistryNeverBecomesSuccess() {
    try (var h = new Harness<String>("DEBUG", registry -> "binding")) {
      h.nullCustom = true;
      assertThrows(NullPointerException.class, h.context::initialize);
      assertThrows(IllegalStateException.class, () -> h.context.render(true));
      assertEquals(0, h.setups.get());
      assertEquals(0, h.standardCreates.get());
    }
  }

  @Test
  void webmctx009ClosedCustomCandidateIsRetainedForExplicitCleanup() {
    try (var h = new Harness<String>("DEBUG", registry -> "binding")) {
      h.custom.close();
      assertThrows(IllegalStateException.class, h.context::initialize);
      assertEquals(1, h.custom.closes.get());
      assertEquals(0, h.setups.get());
      h.context.close();
      assertEquals(2, h.custom.closes.get());
      assertEquals(0, h.standardCreates.get());
    }
  }

  @Test
  void webmctx010SetupRuntimeLeavesCustomOwnedAndStandardUnstarted() {
    var failure = new IllegalArgumentException("setup fixture");
    try (var h =
        new Harness<String>(
            "DEBUG",
            registry -> {
              throw failure;
            })) {
      assertSame(failure, assertThrows(IllegalArgumentException.class, h.context::initialize));
      assertFalse(h.custom.isClosed());
      assertEquals(0, h.standardCreates.get());
      h.context.close();
      assertTrue(h.custom.isClosed());
    }
  }

  @Test
  void webmctx011SetupErrorPreservesIdentityAndPartialOwner() {
    var failure = new AssertionError("setup fatal fixture");
    try (var h =
        new Harness<String>(
            "DEBUG",
            registry -> {
              throw failure;
            })) {
      assertSame(failure, assertThrows(AssertionError.class, h.context::initialize));
      assertFalse(h.custom.isClosed());
      assertEquals(0, h.standardCreates.get());
    }
  }

  @Test
  void webmctx012NullBindingIsRejectedBeforeStandard() {
    try (var h = new Harness<String>("DEBUG", registry -> null)) {
      assertThrows(NullPointerException.class, h.context::initialize);
      assertFalse(h.custom.isClosed());
      assertEquals(0, h.standardCreates.get());
    }
  }

  @Test
  void webmctx013StandardFactoryRuntimeKeepsCustomAndBindingsUnpublished() {
    var failure = new IllegalArgumentException("standard factory fixture");
    try (var h = new Harness<String>("DEBUG", registry -> "binding")) {
      h.standardAcquireFailure = Optional.of(failure);
      assertSame(failure, assertThrows(IllegalArgumentException.class, h.context::initialize));
      assertEquals(1, h.setups.get());
      assertFalse(h.custom.isClosed());
      assertThrows(IllegalStateException.class, h.context::bindings);
      h.context.close();
      assertTrue(h.custom.isClosed());
    }
  }

  @Test
  void webmctx014StandardFactoryErrorIsPrimary() {
    var failure = new AssertionError("standard factory fatal fixture");
    try (var h = new Harness<String>("DEBUG", registry -> "binding")) {
      h.standardAcquireFailure = Optional.of(failure);
      assertSame(failure, assertThrows(AssertionError.class, h.context::initialize));
      assertFalse(h.custom.isClosed());
      assertEquals(1, h.setups.get());
    }
  }

  @Test
  void webmctx015NullStandardFactoryResultRetainsCustom() {
    try (var h = new Harness<String>("DEBUG", registry -> "binding")) {
      h.nullStandard = true;
      assertThrows(NullPointerException.class, h.context::initialize);
      assertFalse(h.custom.isClosed());
      assertEquals(1, h.setups.get());
    }
  }

  @Test
  void webmctx016StandardCloseFailureRetainsCustomAndDeniesNewAccess() {
    var failure = new IllegalStateException("standard close fixture");
    try (var h = new Harness<String>("DEBUG", registry -> "binding")) {
      h.context.initialize();
      h.standard.closeFailure = Optional.of(failure);
      assertSame(failure, assertThrows(IllegalStateException.class, h.context::close));
      assertFalse(h.custom.isClosed());
      assertEquals(List.of("S"), h.order);
      assertThrows(IllegalStateException.class, () -> h.context.render(true));
      assertThrows(IllegalStateException.class, h.context::bindings);
      h.standard.closeFailure = Optional.empty();
      h.context.close();
      assertEquals(List.of("S", "S", "C"), h.order);
    }
  }

  @Test
  void webmctx017CustomCloseFailureDoesNotRepeatConfirmedStandardClose() {
    var failure = new IllegalStateException("custom close fixture");
    try (var h = new Harness<String>("DEBUG", registry -> "binding")) {
      h.context.initialize();
      h.custom.closeFailure = Optional.of(failure);
      assertSame(failure, assertThrows(IllegalStateException.class, h.context::close));
      assertTrue(h.standard.isClosed());
      assertFalse(h.custom.isClosed());
      h.custom.closeFailure = Optional.empty();
      h.context.close();
      h.context.close();
      assertEquals(List.of("S", "C", "C"), h.order);
    }
  }

  @Test
  void webmctx018CallerCapturePrecedesEverySdkFactory() {
    var captured = new AtomicReference<WebMetricContext<String>>();
    try (var h = new Harness<String>("DEBUG", registry -> "binding")) {
      assertEquals(0, h.customCreates.get());
      assertEquals(0, h.standardCreates.get());
      assertEquals(0, h.setups.get());
      h.beforeCustom = Optional.of(() -> assertSame(h.context, captured.get()));
      h.beforeStandard = Optional.of(() -> assertSame(h.context, captured.get()));
      captured.set(h.context);
      h.context.initialize();
      assertEquals("binding", h.context.bindings().orElseThrow());
      assertEquals(1, h.customCreates.get());
      assertEquals(1, h.standardCreates.get());
    }
  }

  @Test
  void webmctx019SingleInitializeAndIdempotentClose() {
    try (var h = new Harness<String>("DEBUG", registry -> "binding")) {
      h.context.initialize();
      assertEquals(READY_ONE + STANDARD, h.context.render(true));
      assertThrows(IllegalStateException.class, h.context::initialize);
      assertEquals(1, h.customCreates.get());
      assertEquals(1, h.standardCreates.get());
      assertEquals(1, h.setups.get());
      h.context.close();
      h.context.close();
      assertEquals(List.of("S", "C"), h.order);
      assertThrows(IllegalStateException.class, () -> h.context.render(false));
      assertThrows(IllegalStateException.class, h.context::bindings);
    }
  }

  @Test
  void webmctx020RenderFailureKeepsOwnerAndDoesNotReacquire() {
    var failure = new IllegalArgumentException("custom read fixture");
    try (var h = new Harness<String>("DEBUG", registry -> "binding")) {
      h.context.initialize();
      h.custom.readFailure = Optional.of(failure);
      assertSame(
          failure, assertThrows(IllegalArgumentException.class, () -> h.context.render(true)));
      assertEquals("binding", h.context.bindings().orElseThrow());
      assertFalse(h.custom.isClosed());
      h.custom.readFailure = Optional.empty();
      assertEquals(READY_ZERO + STANDARD, h.context.render(false));
      assertEquals(1, h.customCreates.get());
      assertEquals(1, h.standardCreates.get());
    }
  }

  @Test
  void webmctx021ContendedCloseIsUnconfirmedWithoutFreeingInFlightSources() throws Exception {
    var entered = new CountDownLatch(1);
    var release = new CountDownLatch(1);
    try (var h = new Harness<String>("DEBUG", registry -> "binding")) {
      h.context.initialize();
      h.custom.onRead =
          Optional.of(
              () -> {
                entered.countDown();
                await(release);
              });
      var executor = Executors.newSingleThreadExecutor();
      try {
        var active = executor.submit(() -> h.context.render(true));
        assertTrue(entered.await(30, TimeUnit.SECONDS));
        assertEquals(
            UNCONFIRMED, assertThrows(IllegalStateException.class, h.context::close).getMessage());
        assertFalse(h.custom.isClosed());
        assertFalse(h.standard.isClosed());
        release.countDown();
        assertEquals(READY_ONE + STANDARD, active.get(30, TimeUnit.SECONDS));
        assertThrows(IllegalStateException.class, () -> h.context.render(true));
        assertThrows(IllegalStateException.class, h.context::bindings);
        h.custom.onRead = Optional.empty();
        h.context.close();
        assertEquals(List.of("S", "C"), h.order);
      } finally {
        release.countDown();
        executor.shutdownNow();
        assertTrue(executor.awaitTermination(30, TimeUnit.SECONDS));
      }
    }
  }

  @Test
  void webmctx022StandardRenderRuntimeErrorAndNullKeepStructuralOwnership() {
    try (var h = new Harness<String>("DEBUG", registry -> "binding")) {
      h.context.initialize();
      for (Throwable failure :
          List.of(
              new IllegalArgumentException("standard read"),
              new AssertionError("standard fatal read"))) {
        h.standard.readFailure = Optional.of(failure);
        assertSame(failure, assertThrows(Throwable.class, () -> h.context.render(true)));
        assertEquals("binding", h.context.bindings().orElseThrow());
        assertFalse(h.standard.isClosed());
        assertFalse(h.custom.isClosed());
      }
      h.standard.readFailure = Optional.empty();
      h.standard.nullText = true;
      assertThrows(NullPointerException.class, () -> h.context.render(true));
      h.standard.nullText = false;
      assertEquals(READY_ONE + STANDARD, h.context.render(true));
      assertEquals(1, h.standardCreates.get());
    }
  }

  @Test
  void webmctx023StopDuringCustomFactoryOrSetupPreventsStandardAcquisition() throws Exception {
    for (boolean duringFactory : List.of(true, false)) {
      var entered = new CountDownLatch(1);
      var release = new CountDownLatch(1);
      try (var h = new Harness<String>("DEBUG", registry -> "binding")) {
        Runnable pause =
            () -> {
              entered.countDown();
              await(release);
            };
        if (duringFactory) h.beforeCustom = Optional.of(pause);
        else h.beforeSetup = Optional.of(pause);
        var executor = Executors.newSingleThreadExecutor();
        try {
          var init = executor.submit(h.context::initialize);
          assertTrue(entered.await(30, TimeUnit.SECONDS));
          assertEquals(
              UNCONFIRMED,
              assertThrows(IllegalStateException.class, h.context::close).getMessage());
          release.countDown();
          var rejected =
              assertThrows(ExecutionException.class, () -> init.get(30, TimeUnit.SECONDS));
          assertEquals(IllegalStateException.class, rejected.getCause().getClass());
          assertEquals(duringFactory ? 0 : 1, h.setups.get());
          assertEquals(0, h.standardCreates.get());
          assertFalse(h.custom.isClosed());
          h.context.close();
          assertTrue(h.custom.isClosed());
        } finally {
          release.countDown();
          executor.shutdownNow();
          assertTrue(executor.awaitTermination(30, TimeUnit.SECONDS));
        }
      }
    }
  }

  @Test
  void webmctx024StopDuringStandardAcquisitionKeepsBothOwnersUnconfirmed() throws Exception {
    var entered = new CountDownLatch(1);
    var release = new CountDownLatch(1);
    try (var h = new Harness<String>("DEBUG", registry -> "binding")) {
      h.beforeStandard =
          Optional.of(
              () -> {
                entered.countDown();
                await(release);
              });
      var executor = Executors.newSingleThreadExecutor();
      try {
        var init = executor.submit(h.context::initialize);
        assertTrue(entered.await(30, TimeUnit.SECONDS));
        assertEquals(
            UNCONFIRMED, assertThrows(IllegalStateException.class, h.context::close).getMessage());
        release.countDown();
        var rejected = assertThrows(ExecutionException.class, () -> init.get(30, TimeUnit.SECONDS));
        assertEquals(IllegalStateException.class, rejected.getCause().getClass());
        assertFalse(h.standard.isClosed());
        assertFalse(h.custom.isClosed());
        assertThrows(IllegalStateException.class, h.context::bindings);
        h.context.close();
        assertEquals(List.of("S", "C"), h.order);
      } finally {
        release.countDown();
        executor.shutdownNow();
        assertTrue(executor.awaitTermination(30, TimeUnit.SECONDS));
      }
    }
  }

  @Test
  void webmctx025ReentrantSetupCloseCannotConfirmOrStartStandard() {
    try (var h = new Harness<String>("DEBUG", registry -> "binding")) {
      h.beforeSetup =
          Optional.of(
              () ->
                  assertEquals(
                      UNCONFIRMED,
                      assertThrows(IllegalStateException.class, h.context::close).getMessage()));
      assertThrows(IllegalStateException.class, h.context::initialize);
      assertFalse(h.custom.isClosed());
      assertEquals(0, h.standardCreates.get());
      h.context.close();
      assertTrue(h.custom.isClosed());
    }
  }

  @Test
  void webmctx026ReentrantRenderClosePropagatesAndRetainsAllResources() {
    try (var h = new Harness<String>("DEBUG", registry -> "binding")) {
      h.context.initialize();
      h.custom.onRead = Optional.of(h.context::close);
      assertEquals(
          UNCONFIRMED,
          assertThrows(IllegalStateException.class, () -> h.context.render(true)).getMessage());
      assertFalse(h.custom.isClosed());
      assertFalse(h.standard.isClosed());
      assertEquals(0, h.standard.scrapes.get());
      h.custom.onRead = Optional.empty();
      h.context.close();
      assertEquals(List.of("S", "C"), h.order);
    }
  }
}
