package dev.codex.schubert.nk.api.monitoring;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assertions.fail;

import dev.codex.schubert.nk.api.monitoring.OutboxObservationRepositoryTest.Row;
import io.micrometer.core.instrument.simple.SimpleMeterRegistry;
import java.io.IOException;
import java.time.Clock;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.concurrent.ConcurrentLinkedQueue;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicReference;
import java.util.function.LongSupplier;
import org.junit.jupiter.api.Test;

/** 1868/OBSCTX001..026: real assembly lifecycle, own JVM/fake JDBC, no application main. */
final class ApiObservationContextTest {
  private static final String FIXTURE_DEBUG_B6DFBABB = "DEBUG";
  private static final String FIXTURE_SDK_CLOSE_7E75EA88 = "SDK close";
  private static final String UNKNOWN = "API observation context close unconfirmed";

  private static void raise(Throwable value) {
    if (value instanceof RuntimeException runtime) throw runtime;
    if (value instanceof Error fatal) throw fatal;
    assertNull(value);
  }

  private static void await(CountDownLatch latch) {
    try {
      assertTrue(latch.await(10, TimeUnit.SECONDS));
    } catch (InterruptedException interrupted) {
      Thread.currentThread().interrupt();
      throw new AssertionError(interrupted);
    }
  }

  private static final class Registry extends SimpleMeterRegistry {
    final AtomicInteger closes = new AtomicInteger();
    volatile Throwable failure;
    volatile Runnable beforeClose = () -> {};

    @Override
    public void close() {
      closes.incrementAndGet();
      beforeClose.run();
      raise(failure);
      super.close();
    }
  }

  private static final class Fixture implements AutoCloseable {
    final OwnedApiObservationWorkerTest.Fixture w = new OwnedApiObservationWorkerTest.Fixture();
    final Registry registry = new Registry();
    final AtomicInteger setups = new AtomicInteger();
    final AtomicInteger budgetReads = new AtomicInteger();
    final ConcurrentLinkedQueue<Throwable> unknown = new ConcurrentLinkedQueue<>();
    volatile Throwable setupFault;
    volatile Throwable policyFault;
    volatile Runnable setup = () -> {};
    volatile LongSupplier remaining = () -> TimeUnit.SECONDS.toNanos(5);
    final ApiMetricContext<String> metrics;
    final ApiObservationContext owner;

    Fixture(boolean worker) {
      metrics =
          new ApiMetricContext<>(
              FIXTURE_DEBUG_B6DFBABB,
              ignored -> {
                setups.incrementAndGet();
                setup.run();
                raise(setupFault);
                return "owned";
              },
              () -> registry,
              new ApiStandardMetricSource());
      owner =
          new ApiObservationContext(
              metrics,
              worker ? Optional.of(w.worker) : Optional.empty(),
              () -> {
                budgetReads.incrementAndGet();
                return remaining.getAsLong();
              },
              failure -> {
                unknown.add(failure);
                raise(policyFault);
              });
    }

    @Override
    public void close() {
      w.close();
      registry.failure = null;
      registry.beforeClose = () -> {};
      metrics.close();
    }
  }

  @Test
  void obsCtx001() {
    var f = new ApiReadOnlyObservationAttemptTest.Fixture();
    var beans = new DbPoolMetricObservationTest.Fixture();
    for (int missing = 0; missing < 9; missing++) {
      final int index = missing;
      assertThrows(
          NullPointerException.class,
          () ->
              ApiObservationContext.prepare(
                  index == 0 ? null : FIXTURE_DEBUG_B6DFBABB,
                  index == 1 ? null : f.pool(),
                  index == 2 ? null : beans::pool,
                  index == 3 ? null : beans::config,
                  index == 4 ? null : Clock.systemUTC(),
                  index == 5 ? null : System::nanoTime,
                  index == 6 ? null : () -> 1,
                  index == 7 ? null : ignored -> fail("unexpected failure"),
                  index == 8 ? null : ignored -> fail("unexpected unknown")));
    }
    assertTrue(f.calls.isEmpty());
    assertTrue(beans.calls.isEmpty());
  }

  @Test
  void obsCtx002() {
    var f = new ApiReadOnlyObservationAttemptTest.Fixture();
    var beans = new DbPoolMetricObservationTest.Fixture();
    for (String mode : List.of("", "debug", "UNKNOWN", " DEBUG"))
      assertThrows(
          IllegalArgumentException.class,
          () ->
              ApiObservationContext.prepare(
                  mode,
                  f.pool(),
                  beans::pool,
                  beans::config,
                  f.clock(),
                  System::nanoTime,
                  () -> 1,
                  ignored -> fail("unexpected failure"),
                  ignored -> fail("unexpected unknown")));
    assertTrue(f.calls.isEmpty());
  }

  @Test
  void obsCtx003() {
    try (var f = new Fixture(false)) {
      assertThrows(
          NullPointerException.class,
          () -> new ApiObservationContext(null, Optional.empty(), () -> 1, ignored -> {}));
      assertThrows(
          NullPointerException.class,
          () -> new ApiObservationContext(f.metrics, null, () -> 1, ignored -> {}));
      assertThrows(
          NullPointerException.class,
          () -> new ApiObservationContext(f.metrics, Optional.empty(), null, ignored -> {}));
      assertThrows(
          NullPointerException.class,
          () -> new ApiObservationContext(f.metrics, Optional.empty(), () -> 1, null));
      assertEquals(0, f.setups.get());
    }
  }

  @Test
  void obsCtx004() throws IOException {
    var f = new ApiReadOnlyObservationAttemptTest.Fixture();
    try (var owner =
        ApiObservationContext.prepare(
            "STANDARD",
            f.pool(),
            () -> {
              throw new AssertionError("pool bean");
            },
            () -> {
              throw new AssertionError("config bean");
            },
            f.clock(),
            () -> {
              throw new AssertionError("nano clock");
            },
            () -> {
              throw new AssertionError("stop budget");
            },
            ignored -> fail("failure"),
            ignored -> fail("unknown"))) {
      owner.initialize();
      assertFalse(owner.metrics().render(true).contains("nk_outbox_"));
      assertTrue(owner.metrics().bindings().isEmpty());
    }
    assertTrue(f.calls.isEmpty());
  }

  @Test
  void obsCtx005() throws IOException {
    var f = new ApiReadOnlyObservationAttemptTest.Fixture();
    var beans = new DbPoolMetricObservationTest.Fixture();
    try (var owner =
        ApiObservationContext.prepare(
            FIXTURE_DEBUG_B6DFBABB,
            f.pool(),
            beans::pool,
            beans::config,
            f.clock(),
            System::nanoTime,
            () -> TimeUnit.SECONDS.toNanos(5),
            ignored -> fail("failure"),
            ignored -> fail("unknown"))) {
      assertSame(owner.metrics(), owner.metrics());
      assertThrows(IllegalStateException.class, () -> owner.metrics().render(true));
      assertTrue(f.calls.isEmpty());
      assertTrue(beans.calls.isEmpty());
    }
  }

  @Test
  void obsCtx006() throws Exception {
    var f =
        new ApiReadOnlyObservationAttemptTest.Fixture(
            Row.row("ERROR", 7, 6), Row.row("PENDING", 3, 2), Row.row("SENT", 5, 4));
    var beans = new DbPoolMetricObservationTest.Fixture();
    List<Throwable> unknown = new ArrayList<>();
    try (var owner =
        ApiObservationContext.prepare(
            FIXTURE_DEBUG_B6DFBABB,
            f.pool(),
            beans::pool,
            beans::config,
            f.clock(),
            System::nanoTime,
            () -> TimeUnit.SECONDS.toNanos(5),
            ignored -> fail("failure"),
            unknown::add)) {
      owner.initialize();
      long deadline = System.nanoTime() + TimeUnit.SECONDS.toNanos(10);
      String body;
      do {
        body = owner.metrics().render(true);
        if (body.contains("nk_outbox_rows{status=\"PENDING\",store=\"API\"} 3.0")) break;
        assertTrue(deadline - System.nanoTime() > 0, "own producer publication bound");
        Thread.sleep(1);
      } while (true);
      for (String line :
          List.of(
              "nk_outbox_rows{status=\"PENDING\",store=\"API\"} 3.0",
              "nk_outbox_rows{status=\"SENT\",store=\"API\"} 5.0",
              "nk_outbox_rows{status=\"ERROR\",store=\"API\"} 7.0",
              "nk_outbox_oldest_seconds{status=\"PENDING\",store=\"API\"} 2.0",
              "nk_outbox_oldest_seconds{status=\"SENT\",store=\"API\"} 4.0",
              "nk_outbox_oldest_seconds{status=\"ERROR\",store=\"API\"} 6.0"))
        assertTrue(body.lines().anyMatch(line::equals));
    }
    f.cleanup(1, 1);
    assertTrue(unknown.isEmpty());
  }

  @Test
  void obsCtx007() throws IOException {
    var f = new ApiReadOnlyObservationAttemptTest.Fixture();
    var beans = new DbPoolMetricObservationTest.Fixture();
    var primary = new IllegalStateException("fixture query");
    f.faults.put("query", primary);
    var notified = new CountDownLatch(1);
    var seen = new AtomicReference<Throwable>();
    try (var owner =
        ApiObservationContext.prepare(
            FIXTURE_DEBUG_B6DFBABB,
            f.pool(),
            beans::pool,
            beans::config,
            f.clock(),
            System::nanoTime,
            () -> TimeUnit.SECONDS.toNanos(5),
            failure -> {
              seen.set(failure);
              notified.countDown();
            },
            ignored -> fail("unknown"))) {
      owner.initialize();
      await(notified);
    }
    assertSame(primary, seen.get());
    f.cleanup(1, 1);
  }

  @Test
  void obsCtx008() {
    try (var f = new Fixture(true)) {
      f.owner.initialize();
      assertThrows(IllegalStateException.class, f.owner::initialize);
      assertEquals(1, f.setups.get());
      assertEquals(1, f.w.starts.get());
    }
  }

  @Test
  void obsCtx009() throws IOException {
    try (var f = new Fixture(true)) {
      f.owner.close();
      assertThrows(IllegalStateException.class, f.owner::initialize);
      assertEquals(0, f.setups.get());
      assertEquals(0, f.w.starts.get());
    }
  }

  @Test
  void obsCtx010() throws IOException {
    try (var f = new Fixture(false)) {
      f.owner.close();
      f.owner.close();
      assertEquals(0, f.registry.closes.get());
      assertEquals(0, f.budgetReads.get());
    }
  }

  @Test
  void obsCtx011() throws IOException {
    try (var f = new Fixture(true)) {
      var primary = new IllegalStateException("setup");
      f.setupFault = primary;
      assertSame(primary, assertThrows(IllegalStateException.class, f.owner::initialize));
      assertEquals(0, f.w.starts.get());
      f.owner.close();
      assertEquals(1, f.registry.closes.get());
    }
  }

  @Test
  void obsCtx012() throws IOException {
    try (var f = new Fixture(true)) {
      var fatal = new AssertionError("setup");
      f.setupFault = fatal;
      assertSame(fatal, assertThrows(AssertionError.class, f.owner::initialize));
      assertEquals(0, f.w.starts.get());
      f.owner.close();
      assertEquals(1, f.registry.closes.get());
    }
  }

  @Test
  void obsCtx013() throws IOException {
    try (var f = new Fixture(true)) {
      var primary = new IllegalStateException("starter");
      f.w.starterFault = primary;
      assertSame(primary, assertThrows(IllegalStateException.class, f.owner::initialize));
      assertEquals(0, f.registry.closes.get());
      f.owner.close();
      assertEquals(1, f.registry.closes.get());
    }
  }

  @Test
  void obsCtx014() throws IOException {
    try (var f = new Fixture(true)) {
      var fatal = new AssertionError("starter");
      f.w.starterFault = fatal;
      assertSame(fatal, assertThrows(AssertionError.class, f.owner::initialize));
      assertEquals(0, f.registry.closes.get());
      f.owner.close();
      assertEquals(1, f.registry.closes.get());
    }
  }

  @Test
  void obsCtx015() throws IOException {
    try (var f = new Fixture(true)) {
      var release = new CountDownLatch(1);
      f.w.releases.add(release);
      f.w.signal.beforeWait = () -> await(release);
      f.remaining =
          () -> {
            release.countDown();
            return TimeUnit.SECONDS.toNanos(5);
          };
      f.registry.beforeClose = () -> assertFalse(f.w.actor.get().isAlive());
      f.owner.initialize();
      await(f.w.signal.waiting);
      f.owner.close();
      assertTrue(f.budgetReads.get() >= 1);
      assertEquals(1, f.registry.closes.get());
      assertTrue(f.unknown.isEmpty());
    }
  }

  @Test
  void obsCtx016() {
    try (var f = new Fixture(true)) {
      var entered = f.w.blockQuery();
      f.owner.initialize();
      await(entered);
      f.remaining = () -> 0;
      var first = assertThrows(IOException.class, f.owner::close);
      assertEquals("observation worker stop unconfirmed", first.getMessage());
      assertSame(first, f.unknown.peek());
      f.w.releaseAll();
      assertEquals(UNKNOWN, assertThrows(IOException.class, f.owner::close).getMessage());
      assertEquals(0, f.registry.closes.get());
      assertEquals(2, f.unknown.size());
    }
  }

  @Test
  void obsCtx017() {
    for (Throwable primary :
        List.of(new IllegalStateException("budget"), new AssertionError("budget"))) {
      try (var f = new Fixture(true)) {
        var entered = f.w.blockQuery();
        f.owner.initialize();
        await(entered);
        f.remaining =
            () -> {
              raise(primary);
              return 1;
            };
        assertSame(primary, assertThrows(primary.getClass(), f.owner::close));
        assertEquals(0, f.registry.closes.get());
        assertSame(primary, f.unknown.peek());
      }
    }
  }

  @Test
  void obsCtx018() {
    try (var f = new Fixture(false)) {
      f.owner.initialize();
      var primary = new IllegalStateException(FIXTURE_SDK_CLOSE_7E75EA88);
      f.registry.failure = primary;
      assertSame(primary, assertThrows(IllegalStateException.class, f.owner::close));
      assertThrows(IOException.class, f.owner::close);
      assertEquals(1, f.registry.closes.get());
      assertSame(primary, f.unknown.peek());
    }
  }

  @Test
  void obsCtx019() {
    try (var f = new Fixture(false)) {
      f.owner.initialize();
      var fatal = new AssertionError(FIXTURE_SDK_CLOSE_7E75EA88);
      f.registry.failure = fatal;
      assertSame(fatal, assertThrows(AssertionError.class, f.owner::close));
      assertSame(fatal, f.unknown.peek());
      assertEquals(1, f.registry.closes.get());
    }
  }

  @Test
  void obsCtx020() {
    try (var f = new Fixture(false)) {
      f.owner.initialize();
      var primary = new IllegalStateException(FIXTURE_SDK_CLOSE_7E75EA88);
      var diagnostic = new IllegalArgumentException("policy");
      f.registry.failure = primary;
      f.policyFault = diagnostic;
      assertSame(primary, assertThrows(IllegalStateException.class, f.owner::close));
      assertArrayEquals(new Throwable[] {diagnostic}, primary.getSuppressed());
    }
  }

  @Test
  void obsCtx021() {
    try (var f = new Fixture(false)) {
      f.owner.initialize();
      var primary = new IllegalStateException(FIXTURE_SDK_CLOSE_7E75EA88);
      var fatal = new AssertionError("policy");
      f.registry.failure = primary;
      f.policyFault = fatal;
      assertSame(fatal, assertThrows(AssertionError.class, f.owner::close));
      assertArrayEquals(new Throwable[] {fatal}, primary.getSuppressed());
      assertSame(primary, f.unknown.peek());
    }
  }

  @Test
  void obsCtx022() throws Exception {
    try (var f = new Fixture(false);
        var executor = Executors.newSingleThreadExecutor()) {
      var entered = new CountDownLatch(1);
      var release = new CountDownLatch(1);
      f.setup =
          () -> {
            entered.countDown();
            await(release);
          };
      var initialize = executor.submit(f.owner::initialize);
      try {
        await(entered);
        assertEquals(UNKNOWN, assertThrows(IOException.class, f.owner::close).getMessage());
        assertEquals(0, f.registry.closes.get());
      } finally {
        release.countDown();
      }
      assertInstanceOf(
          IllegalStateException.class,
          assertThrows(ExecutionException.class, () -> initialize.get(10, TimeUnit.SECONDS))
              .getCause());
      assertThrows(IOException.class, f.owner::close);
      assertEquals(0, f.registry.closes.get());
    }
  }

  @Test
  void obsCtx023() {
    try (var f = new Fixture(false)) {
      f.setup = () -> assertThrows(IOException.class, f.owner::close);
      assertThrows(IllegalStateException.class, f.owner::initialize);
      assertEquals(0, f.registry.closes.get());
      assertEquals(1, f.unknown.size());
    }
  }

  @Test
  void obsCtx024() {
    try (var f = new Fixture(true)) {
      f.w.beforeStart = () -> assertThrows(IOException.class, f.owner::close);
      assertThrows(IllegalStateException.class, f.owner::initialize);
      assertEquals(1, f.w.starts.get());
      assertEquals(0, f.registry.closes.get());
      assertEquals(1, f.unknown.size());
    }
  }

  @Test
  void obsCtx025() throws Exception {
    try (var f = new Fixture(false);
        var executor = Executors.newSingleThreadExecutor()) {
      f.owner.initialize();
      var entered = new CountDownLatch(1);
      var release = new CountDownLatch(1);
      f.registry.beforeClose =
          () -> {
            entered.countDown();
            await(release);
          };
      var close =
          executor.submit(
              () -> {
                f.owner.close();
                return true;
              });
      try {
        await(entered);
        assertThrows(IOException.class, f.owner::close);
      } finally {
        release.countDown();
      }
      assertInstanceOf(
          IOException.class,
          assertThrows(ExecutionException.class, () -> close.get(10, TimeUnit.SECONDS)).getCause());
      assertEquals(1, f.registry.closes.get());
      assertEquals(2, f.unknown.size());
    }
  }

  @Test
  void obsCtx026() {
    try (var f = new Fixture(true)) {
      f.owner.initialize();
      await(f.w.signal.waiting);
      var primary = new IllegalStateException("wake");
      f.w.signal.releaseFault = primary;
      assertSame(primary, assertThrows(IllegalStateException.class, f.owner::close));
      assertEquals(0, f.registry.closes.get());
      assertSame(primary, f.unknown.peek());
    }
  }
}
