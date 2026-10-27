package dev.codex.schubert.nk.api.monitoring;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNotSame;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.api.monitoring.DbPoolMetricObservationTest.Fixture;
import io.micrometer.core.instrument.MeterRegistry;
import io.micrometer.core.instrument.simple.SimpleMeterRegistry;
import java.util.List;
import java.util.Set;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicReference;
import org.junit.jupiter.api.Test;

/** 1825 APIPOOLB001..010: public typed getter fixtures only, no actual pool/DB. */
final class ApiDbPoolMetricBindingTest {
  private static final int FATAL_SUPPLIER_CASE = 1;
  private static final String ACTIVE_STATE = "active";
  private static final String POOL_METRIC_NAME = "nk_db_pool_connections";
  private static final String SERVICE_TAG = "service";
  private static final String SERVICE_VALUE = "API";
  private static final String STATE_TAG = "state";
  private static final String DEBUG_MODE = "DEBUG";
  private static final String EIGHT_VALUE = "8.0";
  private static final String ZERO_VALUE = "0.0";
  private static final String POOL_SUPPLIER = "pool";
  private static final String CONFIG_SUPPLIER = "config";

  private static final class Registry extends SimpleMeterRegistry implements AutoCloseable {
    @Override
    public void close() {
      super.close();
    }
  }

  private static final List<String> POINTS = List.of(ACTIVE_STATE, "idle", "pending", "max");

  private static Fixture fixture() {
    var f = new Fixture();
    f.active = 3;
    f.idle = 5;
    f.pending = 2;
    f.maximum = 8;
    return f;
  }

  private static ApiDbPoolMetricBinding binding(Fixture f, MeterRegistry registry, String mode) {
    return new ApiDbPoolMetricBinding(f.pool(), f.config(), registry, mode);
  }

  private static void known(
      ApiDbPoolMetricBinding binding, long active, long idle, long pending, long maximum) {
    var counts = binding.snapshot().orElseThrow();
    assertEquals(active, counts.active());
    assertEquals(idle, counts.idle());
    assertEquals(pending, counts.pending());
    assertEquals(maximum, counts.maximum());
  }

  private static void missing(ApiDbPoolMetricBinding binding, MeterRegistry registry) {
    assertTrue(binding.snapshot().isEmpty());
    assertEquals(4, registry.getMeters().size());
    for (String state : POINTS)
      assertTrue(
          Double.isNaN(
              registry
                  .get(POOL_METRIC_NAME)
                  .tags(SERVICE_TAG, SERVICE_VALUE, STATE_TAG, state)
                  .gauge()
                  .value()));
  }

  private static void text(
      String body, String active, String idle, String pending, String maximum) {
    var actual = body.lines().filter(line -> line.startsWith("nk_db_pool_connections{")).toList();
    assertEquals(4, actual.size());
    assertEquals(
        Set.of(
            "nk_db_pool_connections{service=\"API\",state=\"active\"} " + active,
            "nk_db_pool_connections{service=\"API\",state=\"idle\"} " + idle,
            "nk_db_pool_connections{service=\"API\",state=\"pending\"} " + pending,
            "nk_db_pool_connections{service=\"API\",state=\"max\"} " + maximum),
        Set.copyOf(actual));
  }

  @Test
  void apipoolb001NullAndUnknownModeNeverReadBorrowedGetters() {
    var f = fixture();
    try (var registry = new Registry()) {
      assertThrows(
          NullPointerException.class,
          () -> new ApiDbPoolMetricBinding(null, f.config(), registry, DEBUG_MODE));
      assertThrows(
          NullPointerException.class,
          () -> new ApiDbPoolMetricBinding(f.pool(), null, registry, DEBUG_MODE));
      assertThrows(
          NullPointerException.class,
          () -> new ApiDbPoolMetricBinding(f.pool(), f.config(), null, DEBUG_MODE));
      assertThrows(
          NullPointerException.class,
          () -> new ApiDbPoolMetricBinding(f.pool(), f.config(), registry, null));
      assertThrows(IllegalArgumentException.class, () -> binding(f, registry, "debug"));
      assertTrue(f.calls.isEmpty());
      assertTrue(registry.getMeters().isEmpty());
    }
  }

  @Test
  void apipoolb002ConstructorRegistersMetadataWithoutSamplingThenPublishesExactValues() {
    var f = fixture();
    try (var registry = new Registry()) {
      var binding = binding(f, registry, DEBUG_MODE);
      assertTrue(f.calls.isEmpty());
      missing(binding, registry);
      binding.refresh();
      f.complete();
      known(binding, 3, 5, 2, 8);
      assertEquals(
          3.0,
          registry
              .get(POOL_METRIC_NAME)
              .tags(SERVICE_TAG, SERVICE_VALUE, STATE_TAG, ACTIVE_STATE)
              .gauge()
              .value());
    }
  }

  @Test
  void apipoolb003InvalidObservationClearsAndTrueZeroRecoversWithoutSeriesGrowth() {
    var f = fixture();
    try (var registry = new Registry()) {
      var binding = binding(f, registry, DEBUG_MODE);
      binding.refresh();
      known(binding, 3, 5, 2, 8);
      f.calls.clear();
      f.maximum = 0;
      binding.refresh();
      f.complete();
      missing(binding, registry);
      f.calls.clear();
      f.active = 0;
      f.idle = 0;
      f.pending = 0;
      f.maximum = 8;
      binding.refresh();
      f.complete();
      known(binding, 0, 0, 0, 8);
      assertEquals(
          0.0,
          registry
              .get(POOL_METRIC_NAME)
              .tags(SERVICE_TAG, SERVICE_VALUE, STATE_TAG, ACTIVE_STATE)
              .gauge()
              .value());
      assertEquals(4, registry.getMeters().size());
    }
  }

  @Test
  void apipoolb004StandardNeverReadsEvenFailingGetterAndCreatesNoSeries() {
    var f = fixture();
    f.faults.put(ACTIVE_STATE, new AssertionError("must not read"));
    try (var registry = new Registry()) {
      var binding = binding(f, registry, "STANDARD");
      binding.refresh();
      assertTrue(binding.snapshot().isEmpty());
      assertTrue(f.calls.isEmpty());
      assertTrue(registry.getMeters().isEmpty());
    }
  }

  @Test
  void apipoolb005EveryRuntimeGetterFailureClearsPreservesIdentityAndDoesNotRetry() {
    for (int point = 0; point < POINTS.size(); point++) {
      var f = fixture();
      var failure = new IllegalStateException("fixed getter failure");
      try (var registry = new Registry()) {
        var binding = binding(f, registry, DEBUG_MODE);
        binding.refresh();
        f.calls.clear();
        f.faults.put(POINTS.get(point), failure);
        assertSame(failure, assertThrows(IllegalStateException.class, binding::refresh));
        assertEquals(POINTS.subList(0, point + 1), f.calls);
        missing(binding, registry);
        f.calls.clear();
        f.faults.clear();
        binding.refresh();
        f.complete();
        known(binding, 3, 5, 2, 8);
      }
    }
  }

  @Test
  void apipoolb006DirectGetterErrorRemainsFatalAndMissing() {
    var f = fixture();
    var failure = new AssertionError("fixed getter fatal");
    try (var registry = new Registry()) {
      var binding = binding(f, registry, DEBUG_MODE);
      binding.refresh();
      f.calls.clear();
      f.faults.put(ACTIVE_STATE, failure);
      assertSame(failure, assertThrows(AssertionError.class, binding::refresh));
      assertEquals(List.of(ACTIVE_STATE), f.calls);
      missing(binding, registry);
    }
  }

  @Test
  void apipoolb007LastSnapshotIsImmutableNotLiveGetterOrFreshnessAuthority() {
    var f = fixture();
    try (var registry = new Registry()) {
      var binding = binding(f, registry, DEBUG_MODE);
      binding.refresh();
      var first = binding.snapshot().orElseThrow();
      f.calls.clear();
      f.active = 0;
      f.idle = 0;
      f.pending = 4;
      known(binding, 3, 5, 2, 8);
      assertTrue(f.calls.isEmpty());
      binding.refresh();
      f.complete();
      known(binding, 0, 0, 4, 8);
      assertNotSame(first, binding.snapshot().orElseThrow());
      assertEquals(3L, first.active());
      assertEquals(5L, first.idle());
    }
  }

  @Test
  void apipoolb008RealContextRefreshOwnsSdkButNeverControlsOrClosesBorrowedBean() {
    var f = fixture();
    var registry = new AtomicReference<MeterRegistry>();
    try (var context =
        new ApiMetricContext<ApiDbPoolMetricBinding>(
            DEBUG_MODE,
            supplied -> {
              registry.set(supplied);
              return binding(f, supplied, DEBUG_MODE);
            },
            ApiDbPoolMetricBinding::refresh)) {
      context.initialize();
      assertTrue(f.calls.isEmpty());
      assertTrue(context.bindings().orElseThrow().snapshot().isEmpty());
      var first = context.render(true);
      assertTrue(first.startsWith("# TYPE schubert_nk_api_ready gauge\nschubert_nk_api_ready 1\n"));
      text(first, "3.0", "5.0", "2.0", EIGHT_VALUE);
      f.complete();
      f.calls.clear();
      f.active = 0;
      f.idle = 0;
      f.pending = 4;
      text(context.render(false), ZERO_VALUE, ZERO_VALUE, "4.0", EIGHT_VALUE);
      f.complete();
      assertFalse(registry.get().isClosed());
    }
    assertTrue(registry.get().isClosed());
    f.complete();
  }

  @Test
  void apipoolb009MaximumIntegerStatisticsWidenExactlyWithoutClampOrWrap() {
    var f = fixture();
    f.active = Integer.MAX_VALUE;
    f.idle = Integer.MAX_VALUE;
    f.pending = Integer.MAX_VALUE;
    f.maximum = Integer.MAX_VALUE;
    try (var registry = new Registry()) {
      var binding = binding(f, registry, DEBUG_MODE);
      binding.refresh();
      f.complete();
      known(binding, 2147483647L, 2147483647L, 2147483647L, 2147483647L);
      assertEquals(
          2147483647.0,
          registry
              .get(POOL_METRIC_NAME)
              .tags(SERVICE_TAG, SERVICE_VALUE, STATE_TAG, ACTIVE_STATE)
              .gauge()
              .value());
    }
  }

  @Test
  void apipoolb011PreparedStandardNeverAcquiresBorrowedBeanReferences() {
    try (var context =
        ApiDbPoolMetricBinding.prepareContext(
            "STANDARD",
            () -> {
              throw new AssertionError("pool must remain deferred");
            },
            () -> {
              throw new AssertionError("configuration must remain deferred");
            })) {
      context.initialize();
      assertTrue(context.bindings().isEmpty());
      assertEquals(
          "# TYPE schubert_nk_api_ready gauge\nschubert_nk_api_ready 1\n", context.render(true));
    }
  }

  @Test
  void apipoolb012FactoryRejectsNullAndUnknownModeBeforeSupplierRead() {
    var f = fixture();
    assertThrows(
        NullPointerException.class,
        () -> ApiDbPoolMetricBinding.prepareContext(DEBUG_MODE, null, f::config));
    assertThrows(
        NullPointerException.class,
        () -> ApiDbPoolMetricBinding.prepareContext(DEBUG_MODE, f::pool, null));
    assertThrows(
        NullPointerException.class,
        () -> ApiDbPoolMetricBinding.prepareContext(null, f::pool, f::config));
    assertThrows(
        IllegalArgumentException.class,
        () -> ApiDbPoolMetricBinding.prepareContext("debug", f::pool, f::config));
    assertTrue(f.calls.isEmpty());
  }

  @Test
  void apipoolb013CallerCapturesOwnerBeforeDeferredBeanReferencesAndSamplesOnlyAtRender() {
    var f = fixture();
    var calls = new java.util.ArrayList<String>();
    var owner = new AtomicReference<ApiMetricContext<ApiDbPoolMetricBinding>>();
    try (var context =
        ApiDbPoolMetricBinding.prepareContext(
            DEBUG_MODE,
            () -> {
              assertNotNull(owner.get());
              calls.add(POOL_SUPPLIER);
              return f.pool();
            },
            () -> {
              assertNotNull(owner.get());
              calls.add(CONFIG_SUPPLIER);
              return f.config();
            })) {
      owner.set(context);
      assertTrue(calls.isEmpty());
      context.initialize();
      assertEquals(List.of(POOL_SUPPLIER, CONFIG_SUPPLIER), calls);
      assertTrue(f.calls.isEmpty());
      assertTrue(context.bindings().orElseThrow().snapshot().isEmpty());
      text(context.render(true), "3.0", "5.0", "2.0", EIGHT_VALUE);
      f.complete();
      f.calls.clear();
      f.active = 0;
      f.idle = 0;
      f.pending = 4;
      text(context.render(false), ZERO_VALUE, ZERO_VALUE, "4.0", EIGHT_VALUE);
      f.complete();
      assertEquals(List.of(POOL_SUPPLIER, CONFIG_SUPPLIER), calls);
    }
  }

  @Test
  void apipoolb014PoolSupplierFailureOrNullRetainsPartialOwnerAndNeverReadsConfiguration() {
    for (int kind = 0; kind < 3; kind++) {
      final int selected = kind;
      var runtime = new IllegalStateException("fixed pool supplier");
      var fatal = new AssertionError("fixed pool supplier fatal");
      var reads = new java.util.concurrent.atomic.AtomicInteger();
      var f = fixture();
      try (var context =
          ApiDbPoolMetricBinding.prepareContext(
              DEBUG_MODE,
              () -> {
                reads.incrementAndGet();
                if (selected == 0) throw runtime;
                if (selected == FATAL_SUPPLIER_CASE) throw fatal;
                return null;
              },
              () -> {
                throw new AssertionError("configuration must not be reached");
              })) {
        if (selected == 0)
          assertSame(runtime, assertThrows(IllegalStateException.class, context::initialize));
        else if (selected == FATAL_SUPPLIER_CASE)
          assertSame(fatal, assertThrows(AssertionError.class, context::initialize));
        else assertThrows(NullPointerException.class, context::initialize);
        assertEquals(1, reads.get());
        assertThrows(IllegalStateException.class, context::initialize);
        assertThrows(IllegalStateException.class, context::bindings);
        assertThrows(IllegalStateException.class, () -> context.render(true));
        assertTrue(f.calls.isEmpty());
        assertEquals(1, reads.get());
      }
    }
  }

  @Test
  void apipoolb015ConfigurationSupplierFailureOrNullPreservesPrimaryAndNeverReadsStatistics() {
    for (int kind = 0; kind < 3; kind++) {
      final int selected = kind;
      var runtime = new IllegalArgumentException("fixed configuration supplier");
      var fatal = new AssertionError("fixed configuration supplier fatal");
      var order = new java.util.ArrayList<String>();
      var f = fixture();
      try (var context =
          ApiDbPoolMetricBinding.prepareContext(
              DEBUG_MODE,
              () -> {
                order.add(POOL_SUPPLIER);
                return f.pool();
              },
              () -> {
                order.add(CONFIG_SUPPLIER);
                if (selected == 0) throw runtime;
                if (selected == FATAL_SUPPLIER_CASE) throw fatal;
                return null;
              })) {
        if (selected == 0)
          assertSame(runtime, assertThrows(IllegalArgumentException.class, context::initialize));
        else if (selected == FATAL_SUPPLIER_CASE)
          assertSame(fatal, assertThrows(AssertionError.class, context::initialize));
        else assertThrows(NullPointerException.class, context::initialize);
        assertEquals(List.of(POOL_SUPPLIER, CONFIG_SUPPLIER), order);
        assertTrue(f.calls.isEmpty());
        assertThrows(IllegalStateException.class, context::initialize);
        assertThrows(IllegalStateException.class, context::bindings);
        assertEquals(List.of(POOL_SUPPLIER, CONFIG_SUPPLIER), order);
      }
    }
  }

  private static void await(CountDownLatch latch) {
    try {
      assertTrue(latch.await(30, TimeUnit.SECONDS));
    } catch (InterruptedException interrupted) {
      Thread.currentThread().interrupt();
      throw new IllegalStateException("owned fixture interrupted");
    }
  }

  @Test
  void apipoolb010OneRetainedCollectorSerializesBothOwnedRefreshes() throws Exception {
    var f = fixture();
    var entered = new CountDownLatch(1);
    var release = new CountDownLatch(1);
    var secondEntered = new CountDownLatch(1);
    var secondThread = new AtomicReference<Thread>();
    f.beforeActive =
        () -> {
          entered.countDown();
          await(release);
        };
    try (var registry = new Registry()) {
      var binding = binding(f, registry, DEBUG_MODE);
      var workers = Executors.newFixedThreadPool(2);
      try {
        var first = workers.submit(binding::refresh);
        await(entered);
        var second =
            workers.submit(
                () -> {
                  secondThread.set(Thread.currentThread());
                  secondEntered.countDown();
                  binding.refresh();
                });
        await(secondEntered);
        long deadline = System.nanoTime() + TimeUnit.SECONDS.toNanos(30);
        while (secondThread.get().getState() != Thread.State.BLOCKED
            && System.nanoTime() < deadline) Thread.onSpinWait();
        assertEquals(Thread.State.BLOCKED, secondThread.get().getState());
        assertEquals(List.of(ACTIVE_STATE), f.calls);
        release.countDown();
        first.get(30, TimeUnit.SECONDS);
        second.get(30, TimeUnit.SECONDS);
        assertEquals(
            List.of(ACTIVE_STATE, "idle", "pending", "max", ACTIVE_STATE, "idle", "pending", "max"),
            f.calls);
        known(binding, 3, 5, 2, 8);
        assertEquals(4, registry.getMeters().size());
      } finally {
        release.countDown();
        workers.shutdownNow();
        assertTrue(workers.awaitTermination(30, TimeUnit.SECONDS));
      }
    }
  }
}
