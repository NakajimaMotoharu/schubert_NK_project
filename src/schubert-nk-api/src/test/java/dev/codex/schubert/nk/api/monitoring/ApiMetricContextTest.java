package dev.codex.schubert.nk.api.monitoring;

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

/** 1815 APIMCTX001..026: SDK ownership only, no external service or opaque data oracle. */
class ApiMetricContextTest {
  private static final String DEBUG_MODE = "DEBUG";
  private static final String FIXTURE_BINDING = "binding";
  private static final String READY_ONE =
      "# TYPE schubert_nk_api_ready gauge\nschubert_nk_api_ready 1\n";
  private static final String READY_ZERO =
      "# TYPE schubert_nk_api_ready gauge\nschubert_nk_api_ready 0\n";
  private static final String STANDARD =
      "# TYPE system_cpu_count gauge\nsystem_cpu_count{service=\"API\"} 42.0\n";
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

  private static final class Custom extends SimpleMeterRegistry implements ExactDurationSupport {
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
    final Custom customRegistry = new Custom(order);
    final Standard standardRegistry = new Standard(order);
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
    final ApiMetricContext<T> context;

    Harness(String mode, Function<MeterRegistry, T> setup) {
      var standardOwner = new ApiStandardMetricSource(this::standard, (registry, gc) -> {});
      context =
          new ApiMetricContext<T>(
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
      return nullCustom ? null : customRegistry;
    }

    private PrometheusMeterRegistry standard() {
      standardCreates.incrementAndGet();
      beforeStandard.ifPresent(Runnable::run);
      if (standardAcquireFailure.isPresent()) return raise(standardAcquireFailure.orElseThrow());
      return nullStandard ? null : standardRegistry;
    }

    @Override
    public void close() {
      customRegistry.onRead = Optional.empty();
      customRegistry.readFailure = Optional.empty();
      customRegistry.closeFailure = Optional.empty();
      standardRegistry.closeFailure = Optional.empty();
      context.close();
      // Only unused fixture candidates remain owned by the fixture, never by the context.
      if (!customRegistry.isClosed()) customRegistry.close();
      if (!standardRegistry.isClosed()) standardRegistry.close();
    }
  }

  @Test
  void apimctx001StandardHandshakeReadsNoFactoryOrSetup() {
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
  void apimctx002DefaultSourceRetainsBindingsAndOfficialSdkGolden() {
    var supplied = new AtomicReference<double[]>();
    try (var context =
        new ApiMetricContext<double[]>(
            DEBUG_MODE,
            registry -> {
              double[] value = {7.5};
              supplied.set(value);
              Gauge.builder("nk_db_pool_connections", value, state -> state[0])
                  .tags("service", "API", "state", "active")
                  .register(registry);
              return value;
            })) {
      context.initialize();
      double[] value = context.bindings().orElseThrow();
      assertSame(supplied.get(), value);
      String first =
          READY_ONE
              + "# TYPE nk_db_pool_connections gauge\nnk_db_pool_connections{service=\"API\",state=\"active\"} 7.5\n";
      String actual = context.render(true);
      assertTrue(actual.startsWith(first));
      String cpu =
          "system_cpu_count{service=\"API\"} "
              + (double) Runtime.getRuntime().availableProcessors();
      assertTrue(actual.lines().anyMatch(cpu::equals));
      value[0] = 9.5;
      assertTrue(
          context
              .render(false)
              .startsWith(
                  READY_ZERO
                      + "# TYPE nk_db_pool_connections gauge\nnk_db_pool_connections{service=\"API\",state=\"active\"} 9.5\n"));
    }
  }

  @Test
  void apimctx003UninitializedAndClosedBeforeInitNeverAcquire() {
    try (var h = new Harness<String>(DEBUG_MODE, registry -> FIXTURE_BINDING)) {
      assertThrows(IllegalStateException.class, () -> h.context.render(true));
      assertThrows(IllegalStateException.class, h.context::bindings);
      h.context.close();
      assertThrows(IllegalStateException.class, h.context::initialize);
      assertEquals(0, h.customCreates.get());
      assertEquals(0, h.standardCreates.get());
    }
  }

  @Test
  void apimctx004ModeNullAndUnknownFailBeforeSdkAcquisition() {
    assertThrows(
        NullPointerException.class,
        () -> new ApiMetricContext<String>(null, registry -> FIXTURE_BINDING));
    for (String mode : List.of("unknown", "DEBTf", "STANDAQc"))
      assertEquals(
          "CONFIG_INVALID",
          assertThrows(
                  IllegalArgumentException.class,
                  () -> new ApiMetricContext<String>(mode, registry -> FIXTURE_BINDING))
              .getMessage());
  }

  @Test
  void apimctx005ConstructorPortsAreNonNull() {
    var standardRegistry = new ApiStandardMetricSource();
    try {
      assertThrows(
          NullPointerException.class,
          () ->
              new ApiMetricContext<String>(
                  DEBUG_MODE, null, SimpleMeterRegistry::new, standardRegistry));
      assertThrows(
          NullPointerException.class,
          () ->
              new ApiMetricContext<String>(
                  DEBUG_MODE, registry -> FIXTURE_BINDING, null, standardRegistry));
      assertThrows(
          NullPointerException.class,
          () ->
              new ApiMetricContext<String>(
                  DEBUG_MODE, registry -> FIXTURE_BINDING, SimpleMeterRegistry::new, null));
    } finally {
      standardRegistry.close();
    }
  }

  @Test
  void apimctx006CustomFactoryRuntimePreservesIdentityAndOneAttempt() {
    var failure = new IllegalArgumentException("custom factory fixture");
    try (var h = new Harness<String>(DEBUG_MODE, registry -> FIXTURE_BINDING)) {
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
  void apimctx007CustomFactoryErrorIsNeverNormalized() {
    var failure = new AssertionError("custom factory fatal fixture");
    try (var h = new Harness<String>(DEBUG_MODE, registry -> FIXTURE_BINDING)) {
      h.customAcquireFailure = Optional.of(failure);
      assertSame(failure, assertThrows(AssertionError.class, h.context::initialize));
      assertEquals(0, h.standardCreates.get());
    }
  }

  @Test
  void apimctx008NullCustomRegistryNeverBecomesSuccess() {
    try (var h = new Harness<String>(DEBUG_MODE, registry -> FIXTURE_BINDING)) {
      h.nullCustom = true;
      assertThrows(NullPointerException.class, h.context::initialize);
      assertThrows(IllegalStateException.class, () -> h.context.render(true));
      assertEquals(0, h.setups.get());
      assertEquals(0, h.standardCreates.get());
    }
  }

  @Test
  void apimctx009ClosedCustomCandidateIsRetainedForExplicitCleanup() {
    try (var h = new Harness<String>(DEBUG_MODE, registry -> FIXTURE_BINDING)) {
      h.customRegistry.close();
      assertThrows(IllegalStateException.class, h.context::initialize);
      assertEquals(1, h.customRegistry.closes.get());
      assertEquals(0, h.setups.get());
      h.context.close();
      assertEquals(2, h.customRegistry.closes.get());
      assertEquals(0, h.standardCreates.get());
    }
  }

  @Test
  void apimctx010SetupRuntimeLeavesCustomOwnedAndStandardUnstarted() {
    var failure = new IllegalArgumentException("setup fixture");
    try (var h =
        new Harness<String>(
            DEBUG_MODE,
            registry -> {
              throw failure;
            })) {
      assertSame(failure, assertThrows(IllegalArgumentException.class, h.context::initialize));
      assertFalse(h.customRegistry.isClosed());
      assertEquals(0, h.standardCreates.get());
      h.context.close();
      assertTrue(h.customRegistry.isClosed());
    }
  }

  @Test
  void apimctx011SetupErrorPreservesIdentityAndPartialOwner() {
    var failure = new AssertionError("setup fatal fixture");
    try (var h =
        new Harness<String>(
            DEBUG_MODE,
            registry -> {
              throw failure;
            })) {
      assertSame(failure, assertThrows(AssertionError.class, h.context::initialize));
      assertFalse(h.customRegistry.isClosed());
      assertEquals(0, h.standardCreates.get());
    }
  }

  @Test
  void apimctx012NullBindingIsRejectedBeforeStandard() {
    try (var h = new Harness<String>(DEBUG_MODE, registry -> null)) {
      assertThrows(NullPointerException.class, h.context::initialize);
      assertFalse(h.customRegistry.isClosed());
      assertEquals(0, h.standardCreates.get());
    }
  }

  @Test
  void apimctx013StandardFactoryRuntimeKeepsCustomAndBindingsUnpublished() {
    var failure = new IllegalArgumentException("standard factory fixture");
    try (var h = new Harness<String>(DEBUG_MODE, registry -> FIXTURE_BINDING)) {
      h.standardAcquireFailure = Optional.of(failure);
      assertSame(failure, assertThrows(IllegalArgumentException.class, h.context::initialize));
      assertEquals(1, h.setups.get());
      assertFalse(h.customRegistry.isClosed());
      assertThrows(IllegalStateException.class, h.context::bindings);
      h.context.close();
      assertTrue(h.customRegistry.isClosed());
    }
  }

  @Test
  void apimctx014StandardFactoryErrorIsPrimary() {
    var failure = new AssertionError("standard factory fatal fixture");
    try (var h = new Harness<String>(DEBUG_MODE, registry -> FIXTURE_BINDING)) {
      h.standardAcquireFailure = Optional.of(failure);
      assertSame(failure, assertThrows(AssertionError.class, h.context::initialize));
      assertFalse(h.customRegistry.isClosed());
      assertEquals(1, h.setups.get());
    }
  }

  @Test
  void apimctx015NullStandardFactoryResultRetainsCustom() {
    try (var h = new Harness<String>(DEBUG_MODE, registry -> FIXTURE_BINDING)) {
      h.nullStandard = true;
      assertThrows(NullPointerException.class, h.context::initialize);
      assertFalse(h.customRegistry.isClosed());
      assertEquals(1, h.setups.get());
    }
  }

  @Test
  void apimctx016StandardCloseFailureRetainsCustomAndDeniesNewAccess() {
    var failure = new IllegalStateException("standard close fixture");
    try (var h = new Harness<String>(DEBUG_MODE, registry -> FIXTURE_BINDING)) {
      h.context.initialize();
      h.standardRegistry.closeFailure = Optional.of(failure);
      assertSame(failure, assertThrows(IllegalStateException.class, h.context::close));
      assertFalse(h.customRegistry.isClosed());
      assertEquals(List.of("S"), h.order);
      assertThrows(IllegalStateException.class, () -> h.context.render(true));
      assertThrows(IllegalStateException.class, h.context::bindings);
      h.standardRegistry.closeFailure = Optional.empty();
      h.context.close();
      assertEquals(List.of("S", "S", "C"), h.order);
    }
  }

  @Test
  void apimctx017CustomCloseFailureDoesNotRepeatConfirmedStandardClose() {
    var failure = new IllegalStateException("custom close fixture");
    try (var h = new Harness<String>(DEBUG_MODE, registry -> FIXTURE_BINDING)) {
      h.context.initialize();
      h.customRegistry.closeFailure = Optional.of(failure);
      assertSame(failure, assertThrows(IllegalStateException.class, h.context::close));
      assertTrue(h.standardRegistry.isClosed());
      assertFalse(h.customRegistry.isClosed());
      h.customRegistry.closeFailure = Optional.empty();
      h.context.close();
      h.context.close();
      assertEquals(List.of("S", "C", "C"), h.order);
    }
  }

  @Test
  void apimctx018CallerCapturePrecedesEverySdkFactory() {
    var captured = new AtomicReference<ApiMetricContext<String>>();
    try (var h = new Harness<String>(DEBUG_MODE, registry -> FIXTURE_BINDING)) {
      assertEquals(0, h.customCreates.get());
      assertEquals(0, h.standardCreates.get());
      assertEquals(0, h.setups.get());
      h.beforeCustom = Optional.of(() -> assertSame(h.context, captured.get()));
      h.beforeStandard = Optional.of(() -> assertSame(h.context, captured.get()));
      captured.set(h.context);
      h.context.initialize();
      assertEquals(FIXTURE_BINDING, h.context.bindings().orElseThrow());
      assertEquals(1, h.customCreates.get());
      assertEquals(1, h.standardCreates.get());
    }
  }

  @Test
  void apimctx019SingleInitializeAndIdempotentClose() {
    try (var h = new Harness<String>(DEBUG_MODE, registry -> FIXTURE_BINDING)) {
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
  void apimctx020RenderFailureKeepsOwnerAndDoesNotReacquire() {
    var failure = new IllegalArgumentException("custom read fixture");
    try (var h = new Harness<String>(DEBUG_MODE, registry -> FIXTURE_BINDING)) {
      h.context.initialize();
      h.customRegistry.readFailure = Optional.of(failure);
      assertSame(
          failure, assertThrows(IllegalArgumentException.class, () -> h.context.render(true)));
      assertEquals(FIXTURE_BINDING, h.context.bindings().orElseThrow());
      assertFalse(h.customRegistry.isClosed());
      h.customRegistry.readFailure = Optional.empty();
      assertEquals(READY_ZERO + STANDARD, h.context.render(false));
      assertEquals(1, h.customCreates.get());
      assertEquals(1, h.standardCreates.get());
    }
  }

  @Test
  void apimctx021ContendedCloseIsUnconfirmedWithoutFreeingInFlightSources() throws Exception {
    var entered = new CountDownLatch(1);
    var release = new CountDownLatch(1);
    try (var h = new Harness<String>(DEBUG_MODE, registry -> FIXTURE_BINDING)) {
      h.context.initialize();
      h.customRegistry.onRead =
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
        assertFalse(h.customRegistry.isClosed());
        assertFalse(h.standardRegistry.isClosed());
        release.countDown();
        assertEquals(READY_ONE + STANDARD, active.get(30, TimeUnit.SECONDS));
        assertThrows(IllegalStateException.class, () -> h.context.render(true));
        assertThrows(IllegalStateException.class, h.context::bindings);
        h.customRegistry.onRead = Optional.empty();
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
  void apimctx022StandardRenderRuntimeErrorAndNullKeepStructuralOwnership() {
    try (var h = new Harness<String>(DEBUG_MODE, registry -> FIXTURE_BINDING)) {
      h.context.initialize();
      for (Throwable failure :
          List.of(
              new IllegalArgumentException("standard read"),
              new AssertionError("standard fatal read"))) {
        h.standardRegistry.readFailure = Optional.of(failure);
        assertSame(failure, assertThrows(Throwable.class, () -> h.context.render(true)));
        assertEquals(FIXTURE_BINDING, h.context.bindings().orElseThrow());
        assertFalse(h.standardRegistry.isClosed());
        assertFalse(h.customRegistry.isClosed());
      }
      h.standardRegistry.readFailure = Optional.empty();
      h.standardRegistry.nullText = true;
      assertThrows(NullPointerException.class, () -> h.context.render(true));
      h.standardRegistry.nullText = false;
      assertEquals(READY_ONE + STANDARD, h.context.render(true));
      assertEquals(1, h.standardCreates.get());
    }
  }

  @Test
  void apimctx023StopDuringCustomFactoryOrSetupPreventsStandardAcquisition() throws Exception {
    for (boolean duringFactory : List.of(true, false)) {
      var entered = new CountDownLatch(1);
      var release = new CountDownLatch(1);
      try (var h = new Harness<String>(DEBUG_MODE, registry -> FIXTURE_BINDING)) {
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
          assertFalse(h.customRegistry.isClosed());
          h.context.close();
          assertTrue(h.customRegistry.isClosed());
        } finally {
          release.countDown();
          executor.shutdownNow();
          assertTrue(executor.awaitTermination(30, TimeUnit.SECONDS));
        }
      }
    }
  }

  @Test
  void apimctx024StopDuringStandardAcquisitionKeepsBothOwnersUnconfirmed() throws Exception {
    var entered = new CountDownLatch(1);
    var release = new CountDownLatch(1);
    try (var h = new Harness<String>(DEBUG_MODE, registry -> FIXTURE_BINDING)) {
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
        assertFalse(h.standardRegistry.isClosed());
        assertFalse(h.customRegistry.isClosed());
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
  void apimctx025ReentrantSetupCloseCannotConfirmOrStartStandard() {
    try (var h = new Harness<String>(DEBUG_MODE, registry -> FIXTURE_BINDING)) {
      h.beforeSetup =
          Optional.of(
              () ->
                  assertEquals(
                      UNCONFIRMED,
                      assertThrows(IllegalStateException.class, h.context::close).getMessage()));
      assertThrows(IllegalStateException.class, h.context::initialize);
      assertFalse(h.customRegistry.isClosed());
      assertEquals(0, h.standardCreates.get());
      h.context.close();
      assertTrue(h.customRegistry.isClosed());
    }
  }

  @Test
  void apimctx026ReentrantRenderClosePropagatesAndRetainsAllResources() {
    try (var h = new Harness<String>(DEBUG_MODE, registry -> FIXTURE_BINDING)) {
      h.context.initialize();
      h.customRegistry.onRead = Optional.of(h.context::close);
      assertEquals(
          UNCONFIRMED,
          assertThrows(IllegalStateException.class, () -> h.context.render(true)).getMessage());
      assertFalse(h.customRegistry.isClosed());
      assertFalse(h.standardRegistry.isClosed());
      assertEquals(0, h.standardRegistry.scrapes.get());
      h.customRegistry.onRead = Optional.empty();
      h.context.close();
      assertEquals(List.of("S", "C"), h.order);
    }
  }

  /** 1823/PG-D620 APIMCTX027..033: own metadata refresh, no connections or I/O. */
  @Test
  void apimctx027RefreshUsesStrongBindingBeforeEachFullRender() {
    var samples = new AtomicInteger();
    double[] value = {7.5};
    try (var context =
        new ApiMetricContext<double[]>(
            DEBUG_MODE,
            registry -> {
              Gauge.builder("nk_db_pool_connections", value, state -> state[0])
                  .tags("service", "API", "state", "active")
                  .register(registry);
              return value;
            },
            binding -> {
              assertSame(value, binding);
              samples.incrementAndGet();
              binding[0] += 2;
            })) {
      assertEquals(0, samples.get());
      context.initialize();
      assertEquals(0, samples.get());
      assertTrue(
          context
              .render(true)
              .startsWith(
                  READY_ONE
                      + "# TYPE nk_db_pool_connections gauge\nnk_db_pool_connections{service=\"API\",state=\"active\"} 9.5\n"));
      assertTrue(
          context
              .render(false)
              .startsWith(
                  READY_ZERO
                      + "# TYPE nk_db_pool_connections gauge\nnk_db_pool_connections{service=\"API\",state=\"active\"} 11.5\n"));
      assertEquals(2, samples.get());
      assertSame(value, context.bindings().orElseThrow());
    }
  }

  @Test
  void apimctx028StandardNeverReadsRefreshOrSetup() {
    try (var context =
        new ApiMetricContext<String>(
            "STANDARD",
            registry -> {
              throw new AssertionError("STD setup");
            },
            binding -> {
              throw new AssertionError("STD refresh");
            })) {
      context.initialize();
      assertEquals(READY_ONE, context.render(true));
      assertEquals(READY_ZERO, context.render(false));
      assertTrue(context.bindings().isEmpty());
    }
  }

  @Test
  void apimctx029NullRefreshRejectedBeforeRegistration() {
    var calls = new AtomicInteger();
    assertThrows(
        NullPointerException.class,
        () ->
            new ApiMetricContext<String>(
                DEBUG_MODE,
                registry -> {
                  calls.incrementAndGet();
                  return FIXTURE_BINDING;
                },
                null));
    assertEquals(0, calls.get());
  }

  @Test
  void apimctx030RefreshRuntimeRetainsSdkAndAllowsOnlyExplicitNextRender() {
    refreshFailure(new IllegalStateException("fixed metadata failure"));
  }

  @Test
  void apimctx031RefreshErrorIdentityIsNotNormalOrFallback() {
    refreshFailure(new AssertionError("fixed metadata fatal"));
  }

  private static void refreshFailure(Throwable failure) {
    var samples = new AtomicInteger();
    var observed = new AtomicReference<MeterRegistry>();
    double[] value = {7.5};
    try (var context =
        new ApiMetricContext<double[]>(
            DEBUG_MODE,
            registry -> {
              observed.set(registry);
              Gauge.builder("nk_db_pool_connections", value, state -> state[0])
                  .tags("service", "API", "state", "active")
                  .register(registry);
              return value;
            },
            binding -> {
              assertSame(value, binding);
              if (samples.getAndIncrement() == 0) raise(failure);
            })) {
      context.initialize();
      assertSame(failure, assertThrows(failure.getClass(), () -> context.render(true)));
      assertEquals(1, samples.get());
      assertFalse(observed.get().isClosed());
      assertSame(value, context.bindings().orElseThrow());
      assertTrue(
          context
              .render(true)
              .startsWith(
                  READY_ONE
                      + "# TYPE nk_db_pool_connections gauge\nnk_db_pool_connections{service=\"API\",state=\"active\"} 7.5\n"));
      assertEquals(2, samples.get());
    }
    assertTrue(observed.get().isClosed());
  }

  @Test
  void apimctx032RefreshReentrantStopCannotProduceDetailedSuccess() {
    var owner = new AtomicReference<ApiMetricContext<String>>();
    var observed = new AtomicReference<MeterRegistry>();
    var calls = new AtomicInteger();
    var context =
        new ApiMetricContext<String>(
            DEBUG_MODE,
            registry -> {
              observed.set(registry);
              return FIXTURE_BINDING;
            },
            binding -> {
              assertEquals(FIXTURE_BINDING, binding);
              calls.incrementAndGet();
              assertEquals(
                  UNCONFIRMED,
                  assertThrows(IllegalStateException.class, () -> owner.get().close())
                      .getMessage());
            });
    owner.set(context);
    try {
      context.initialize();
      assertThrows(IllegalStateException.class, () -> context.render(true));
      assertEquals(1, calls.get());
      assertFalse(observed.get().isClosed());
      assertThrows(IllegalStateException.class, context::bindings);
    } finally {
      context.close();
    }
    assertTrue(observed.get().isClosed());
  }

  @Test
  void apimctx033RefreshContendedStopRetainsUntilSamplerReturns() throws Exception {
    var entered = new CountDownLatch(1);
    var proceed = new CountDownLatch(1);
    var observed = new AtomicReference<MeterRegistry>();
    var context =
        new ApiMetricContext<String>(
            DEBUG_MODE,
            registry -> {
              observed.set(registry);
              return FIXTURE_BINDING;
            },
            binding -> {
              assertEquals(FIXTURE_BINDING, binding);
              entered.countDown();
              await(proceed);
            });
    var worker = Executors.newSingleThreadExecutor();
    try {
      context.initialize();
      var future = worker.submit(() -> context.render(true));
      try {
        await(entered);
        assertEquals(
            UNCONFIRMED, assertThrows(IllegalStateException.class, context::close).getMessage());
        assertFalse(observed.get().isClosed());
      } finally {
        proceed.countDown();
      }
      var failure = assertThrows(ExecutionException.class, () -> future.get(30, TimeUnit.SECONDS));
      assertEquals(IllegalStateException.class, failure.getCause().getClass());
      assertThrows(IllegalStateException.class, context::bindings);
      assertFalse(observed.get().isClosed());
    } finally {
      proceed.countDown();
      worker.shutdownNow();
      assertTrue(worker.awaitTermination(30, TimeUnit.SECONDS));
      context.close();
    }
    assertTrue(observed.get().isClosed());
  }
}
