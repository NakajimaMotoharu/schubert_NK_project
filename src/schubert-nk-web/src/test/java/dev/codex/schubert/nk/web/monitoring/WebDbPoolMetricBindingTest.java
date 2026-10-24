package dev.codex.schubert.nk.web.monitoring;

import static org.junit.jupiter.api.Assertions.*;

import dev.codex.schubert.nk.web.monitoring.WebDbPoolMetricObservationTest.Fixture;
import io.micrometer.core.instrument.MeterRegistry;
import io.micrometer.core.instrument.simple.SimpleMeterRegistry;
import java.util.List;
import java.util.Set;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicReference;
import org.junit.jupiter.api.Test;

/** 1825 WEBPOOLB001..010: public typed getter fixtures only, no actual pool/DB. */
final class WebDbPoolMetricBindingTest {
  private static final class Registry extends SimpleMeterRegistry implements AutoCloseable {
    @Override
    public void close() {
      super.close();
    }
  }

  private static final List<String> POINTS = List.of("active", "idle", "pending", "max");

  private static Fixture fixture() {
    var f = new Fixture();
    f.active = 1;
    f.idle = 1;
    f.pending = 0;
    f.maximum = 2;
    return f;
  }

  private static WebDbPoolMetricBinding binding(Fixture f, MeterRegistry registry, String mode) {
    return new WebDbPoolMetricBinding(f.pool(), f.config(), registry, mode);
  }

  private static void known(
      WebDbPoolMetricBinding binding, long active, long idle, long pending, long maximum) {
    var counts = binding.snapshot().orElseThrow();
    assertEquals(active, counts.active());
    assertEquals(idle, counts.idle());
    assertEquals(pending, counts.pending());
    assertEquals(maximum, counts.maximum());
  }

  private static void missing(WebDbPoolMetricBinding binding, MeterRegistry registry) {
    assertTrue(binding.snapshot().isEmpty());
    assertEquals(4, registry.getMeters().size());
    for (String state : POINTS)
      assertTrue(
          Double.isNaN(
              registry
                  .get("nk_db_pool_connections")
                  .tags("service", "WEB", "state", state)
                  .gauge()
                  .value()));
  }

  private static void text(
      String body, String active, String idle, String pending, String maximum) {
    var actual = body.lines().filter(line -> line.startsWith("nk_db_pool_connections{")).toList();
    assertEquals(4, actual.size());
    assertEquals(
        Set.of(
            "nk_db_pool_connections{service=\"WEB\",state=\"active\"} " + active,
            "nk_db_pool_connections{service=\"WEB\",state=\"idle\"} " + idle,
            "nk_db_pool_connections{service=\"WEB\",state=\"pending\"} " + pending,
            "nk_db_pool_connections{service=\"WEB\",state=\"max\"} " + maximum),
        Set.copyOf(actual));
  }

  @Test
  void webpoolb001NullAndUnknownModeNeverReadBorrowedGetters() {
    var f = fixture();
    try (var registry = new Registry()) {
      assertThrows(
          NullPointerException.class,
          () -> new WebDbPoolMetricBinding(null, f.config(), registry, "DEBUG"));
      assertThrows(
          NullPointerException.class,
          () -> new WebDbPoolMetricBinding(f.pool(), null, registry, "DEBUG"));
      assertThrows(
          NullPointerException.class,
          () -> new WebDbPoolMetricBinding(f.pool(), f.config(), null, "DEBUG"));
      assertThrows(
          NullPointerException.class,
          () -> new WebDbPoolMetricBinding(f.pool(), f.config(), registry, null));
      assertThrows(IllegalArgumentException.class, () -> binding(f, registry, "debug"));
      assertTrue(f.calls.isEmpty());
      assertTrue(registry.getMeters().isEmpty());
    }
  }

  @Test
  void webpoolb002ConstructorRegistersMetadataWithoutSamplingThenPublishesExactValues() {
    var f = fixture();
    try (var registry = new Registry()) {
      var binding = binding(f, registry, "DEBUG");
      assertTrue(f.calls.isEmpty());
      missing(binding, registry);
      binding.refresh();
      f.complete();
      known(binding, 1, 1, 0, 2);
      assertEquals(
          1.0,
          registry
              .get("nk_db_pool_connections")
              .tags("service", "WEB", "state", "active")
              .gauge()
              .value());
    }
  }

  @Test
  void webpoolb003InvalidObservationClearsAndTrueZeroRecoversWithoutSeriesGrowth() {
    var f = fixture();
    try (var registry = new Registry()) {
      var binding = binding(f, registry, "DEBUG");
      binding.refresh();
      known(binding, 1, 1, 0, 2);
      f.calls.clear();
      f.maximum = 0;
      binding.refresh();
      f.complete();
      missing(binding, registry);
      f.calls.clear();
      f.active = 0;
      f.idle = 0;
      f.pending = 0;
      f.maximum = 2;
      binding.refresh();
      f.complete();
      known(binding, 0, 0, 0, 2);
      assertEquals(
          0.0,
          registry
              .get("nk_db_pool_connections")
              .tags("service", "WEB", "state", "active")
              .gauge()
              .value());
      assertEquals(4, registry.getMeters().size());
    }
  }

  @Test
  void webpoolb004StandardNeverReadsEvenFailingGetterAndCreatesNoSeries() {
    var f = fixture();
    f.faults.put("active", new AssertionError("must not read"));
    try (var registry = new Registry()) {
      var binding = binding(f, registry, "STANDARD");
      binding.refresh();
      assertTrue(binding.snapshot().isEmpty());
      assertTrue(f.calls.isEmpty());
      assertTrue(registry.getMeters().isEmpty());
    }
  }

  @Test
  void webpoolb005EveryRuntimeGetterFailureClearsPreservesIdentityAndDoesNotRetry() {
    for (int point = 0; point < POINTS.size(); point++) {
      var f = fixture();
      var failure = new IllegalStateException("fixed getter failure");
      try (var registry = new Registry()) {
        var binding = binding(f, registry, "DEBUG");
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
        known(binding, 1, 1, 0, 2);
      }
    }
  }

  @Test
  void webpoolb006DirectGetterErrorRemainsFatalAndMissing() {
    var f = fixture();
    var failure = new AssertionError("fixed getter fatal");
    try (var registry = new Registry()) {
      var binding = binding(f, registry, "DEBUG");
      binding.refresh();
      f.calls.clear();
      f.faults.put("active", failure);
      assertSame(failure, assertThrows(AssertionError.class, binding::refresh));
      assertEquals(List.of("active"), f.calls);
      missing(binding, registry);
    }
  }

  @Test
  void webpoolb007LastSnapshotIsImmutableNotLiveGetterOrFreshnessAuthority() {
    var f = fixture();
    try (var registry = new Registry()) {
      var binding = binding(f, registry, "DEBUG");
      binding.refresh();
      var first = binding.snapshot().orElseThrow();
      f.calls.clear();
      f.active = 0;
      f.idle = 0;
      f.pending = 4;
      known(binding, 1, 1, 0, 2);
      assertTrue(f.calls.isEmpty());
      binding.refresh();
      f.complete();
      known(binding, 0, 0, 4, 2);
      assertNotSame(first, binding.snapshot().orElseThrow());
      assertEquals(1L, first.active());
      assertEquals(1L, first.idle());
    }
  }

  @Test
  void webpoolb008RealContextRefreshOwnsSdkButNeverControlsOrClosesBorrowedBean() {
    var f = fixture();
    var registry = new AtomicReference<MeterRegistry>();
    try (var context =
        new WebMetricContext<WebDbPoolMetricBinding>(
            "DEBUG",
            supplied -> {
              registry.set(supplied);
              return binding(f, supplied, "DEBUG");
            },
            WebDbPoolMetricBinding::refresh)) {
      context.initialize();
      assertTrue(f.calls.isEmpty());
      assertTrue(context.bindings().orElseThrow().snapshot().isEmpty());
      var first = context.render(true);
      assertTrue(first.startsWith("# TYPE schubert_nk_web_ready gauge\nschubert_nk_web_ready 1\n"));
      text(first, "1.0", "1.0", "0.0", "2.0");
      f.complete();
      f.calls.clear();
      f.active = 0;
      f.idle = 0;
      f.pending = 4;
      text(context.render(false), "0.0", "0.0", "4.0", "2.0");
      f.complete();
      assertFalse(registry.get().isClosed());
    }
    assertTrue(registry.get().isClosed());
    f.complete();
  }

  @Test
  void webpoolb009MaximumIntegerStatisticsWidenExactlyWithoutClampOrWrap() {
    var f = fixture();
    f.active = Integer.MAX_VALUE;
    f.idle = Integer.MAX_VALUE;
    f.pending = Integer.MAX_VALUE;
    f.maximum = Integer.MAX_VALUE;
    try (var registry = new Registry()) {
      var binding = binding(f, registry, "DEBUG");
      binding.refresh();
      f.complete();
      known(binding, 2147483647L, 2147483647L, 2147483647L, 2147483647L);
      assertEquals(
          2147483647.0,
          registry
              .get("nk_db_pool_connections")
              .tags("service", "WEB", "state", "active")
              .gauge()
              .value());
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
  void webpoolb010OneRetainedCollectorSerializesBothOwnedRefreshes() throws Exception {
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
      var binding = binding(f, registry, "DEBUG");
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
        assertEquals(List.of("active"), f.calls);
        release.countDown();
        first.get(30, TimeUnit.SECONDS);
        second.get(30, TimeUnit.SECONDS);
        assertEquals(
            List.of("active", "idle", "pending", "max", "active", "idle", "pending", "max"),
            f.calls);
        known(binding, 1, 1, 0, 2);
        assertEquals(4, registry.getMeters().size());
      } finally {
        release.countDown();
        workers.shutdownNow();
        assertTrue(workers.awaitTermination(30, TimeUnit.SECONDS));
      }
    }
  }
}
