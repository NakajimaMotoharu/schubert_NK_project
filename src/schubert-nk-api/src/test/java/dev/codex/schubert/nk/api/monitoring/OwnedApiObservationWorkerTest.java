package dev.codex.schubert.nk.api.monitoring;

import static org.junit.jupiter.api.Assertions.*;

import dev.codex.schubert.nk.api.monitoring.ApiOutboxObservationPumpTest.Harness;
import java.io.IOException;
import java.sql.SQLException;
import java.time.Duration;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.ConcurrentLinkedQueue;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.Executors;
import java.util.concurrent.Semaphore;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicReference;
import java.util.function.LongSupplier;
import org.junit.jupiter.api.Test;

/**
 * 1864/OBSOWN001..044: own JVM Threads and fake observation only, no application/runtime admission.
 */
final class OwnedApiObservationWorkerTest {
  private static void raise(Throwable value) {
    if (value instanceof RuntimeException runtime) throw runtime;
    if (value instanceof Error fatal) throw fatal;
    assertNull(value);
  }

  private static void await(CountDownLatch latch) {
    try {
      assertTrue(latch.await(10, TimeUnit.SECONDS), "bounded own-fixture coordination");
    } catch (InterruptedException interrupted) {
      Thread.currentThread().interrupt();
      throw new AssertionError(interrupted);
    }
  }

  private static LongSupplier budget() {
    long deadline = System.nanoTime() + TimeUnit.SECONDS.toNanos(5);
    return () -> Math.max(0, deadline - System.nanoTime());
  }

  static final class Signal extends Semaphore {
    private static final long serialVersionUID = 1L;
    final transient CountDownLatch waiting = new CountDownLatch(1);
    final AtomicInteger releases = new AtomicInteger();
    final AtomicInteger waits = new AtomicInteger();
    transient volatile Runnable beforeWait = () -> {};
    volatile Throwable releaseFault;
    volatile InterruptedException interrupt;
    final AtomicBoolean immediateOnce = new AtomicBoolean();

    Signal() {
      super(0);
    }

    @Override
    public void release() {
      releases.incrementAndGet();
      raise(releaseFault);
      super.release();
    }

    @Override
    public boolean tryAcquire(long timeout, TimeUnit unit) throws InterruptedException {
      assertEquals(1, timeout);
      assertSame(TimeUnit.SECONDS, unit);
      waits.incrementAndGet();
      waiting.countDown();
      beforeWait.run();
      var failure = interrupt;
      interrupt = null;
      if (failure != null) throw failure;
      if (immediateOnce.compareAndSet(true, false)) return false;
      return super.tryAcquire(timeout, unit);
    }
  }

  static final class Fixture implements AutoCloseable {
    final Harness h = new Harness();
    final Signal signal = new Signal();
    final AtomicReference<Thread> actor = new AtomicReference<>();
    final AtomicReference<Throwable> uncaught = new AtomicReference<>();
    final ConcurrentLinkedQueue<Throwable> failures = new ConcurrentLinkedQueue<>();
    final CountDownLatch notified = new CountDownLatch(1);
    final AtomicBoolean interruptSeen = new AtomicBoolean();
    final AtomicInteger starts = new AtomicInteger();
    final List<CountDownLatch> releases = new ArrayList<>();
    volatile Throwable starterFault;
    volatile Throwable afterStartFault;
    volatile Throwable notifierFault;
    volatile Runnable beforeStart = () -> {};
    volatile boolean doNotStart;
    volatile LongSupplier stopNanos = System::nanoTime;
    final OwnedApiObservationWorker worker;

    Fixture() {
      this(false);
    }

    Fixture(boolean publicConstructor) {
      h.configure = f -> actor.compareAndSet(null, Thread.currentThread());
      worker =
          publicConstructor
              ? new OwnedApiObservationWorker(
                  h.pump, this::notifyFailure, () -> stopNanos.getAsLong())
              : new OwnedApiObservationWorker(
                  h.pump, this::notifyFailure, () -> stopNanos.getAsLong(), this::start, signal);
    }

    void start(Thread thread) {
      starts.incrementAndGet();
      actor.set(thread);
      var original = thread.getUncaughtExceptionHandler();
      thread.setUncaughtExceptionHandler(
          (failed, failure) -> {
            uncaught.set(failure);
            original.uncaughtException(failed, failure);
          });
      beforeStart.run();
      raise(starterFault);
      if (!doNotStart) thread.start();
      raise(afterStartFault);
    }

    void notifyFailure(Throwable failure) {
      interruptSeen.set(Thread.currentThread().isInterrupted());
      failures.add(failure);
      notified.countDown();
      raise(notifierFault);
    }

    CountDownLatch blockQuery() {
      var entered = new CountDownLatch(1);
      var release = new CountDownLatch(1);
      releases.add(release);
      h.configure =
          f ->
              f.query.beforeStatementClose =
                  () -> {
                    entered.countDown();
                    await(release);
                  };
      return entered;
    }

    void releaseAll() {
      releases.forEach(CountDownLatch::countDown);
    }

    void idle() {
      worker.start();
      await(signal.waiting);
    }

    @Override
    public void close() {
      signal.releaseFault = null;
      releaseAll();
      worker.requestStop();
      Thread thread = actor.get();
      boolean interrupted = Thread.interrupted();
      try {
        if (thread != null && thread.getState() != Thread.State.NEW) {
          long end = System.nanoTime() + TimeUnit.SECONDS.toNanos(5);
          while (thread.isAlive()) {
            long remaining = end - System.nanoTime();
            assertTrue(remaining > 0, "own test worker must be recovered");
            try {
              thread.join(Duration.ofNanos(remaining));
            } catch (InterruptedException ignored) {
              interrupted = true;
            }
          }
        }
      } finally {
        if (interrupted) Thread.currentThread().interrupt();
      }
    }
  }

  private static void asynchronous(
      Throwable primary, Throwable diagnostic, Throwable expectedUncaught) throws Exception {
    try (var f = new Fixture()) {
      f.h.configure = row -> row.faults.put("query", primary);
      f.notifierFault = diagnostic;
      f.worker.start();
      await(f.notified);
      f.worker.awaitStopped(budget());
      assertSame(primary, f.failures.peek());
      assertSame(expectedUncaught, f.uncaught.get());
      assertTrue(f.h.pump.get().isEmpty());
      assertTrue(f.h.pump.isQuiescent());
      if (diagnostic != null)
        assertArrayEquals(new Throwable[] {diagnostic}, primary.getSuppressed());
    }
  }

  @Test
  void obsOwn001() {
    try (var f = new Fixture()) {
      assertThrows(
          NullPointerException.class,
          () -> new OwnedApiObservationWorker(null, f::notifyFailure, System::nanoTime));
      assertThrows(
          NullPointerException.class,
          () -> new OwnedApiObservationWorker(f.h.pump, null, System::nanoTime));
      assertThrows(
          NullPointerException.class,
          () -> new OwnedApiObservationWorker(f.h.pump, f::notifyFailure, null));
      assertThrows(
          NullPointerException.class,
          () ->
              new OwnedApiObservationWorker(
                  f.h.pump, f::notifyFailure, System::nanoTime, null, f.signal));
      assertThrows(
          NullPointerException.class,
          () ->
              new OwnedApiObservationWorker(
                  f.h.pump, f::notifyFailure, System::nanoTime, f::start, null));
      assertEquals(0, f.h.factoryReads);
      assertEquals(0, f.starts.get());
    }
  }

  @Test
  void obsOwn002() {
    try (var f = new Fixture()) {
      assertEquals(0, f.starts.get());
      assertEquals(0, f.h.clockReads);
      assertEquals(0, f.h.factoryReads);
      assertNull(f.actor.get());
      assertThrows(NullPointerException.class, () -> f.worker.awaitStopped(null));
    }
  }

  @Test
  void obsOwn003() throws Exception {
    try (var f = new Fixture(true)) {
      var entered = f.blockQuery();
      f.h.configure =
          row -> {
            f.actor.set(Thread.currentThread());
            row.query.beforeStatementClose =
                () -> {
                  entered.countDown();
                  await(f.releases.getFirst());
                };
          };
      f.worker.start();
      await(entered);
      assertEquals("nk-api-observation", f.actor.get().getName());
      assertFalse(f.actor.get().isDaemon());
      f.worker.requestStop();
      f.releaseAll();
      f.worker.awaitStopped(budget());
      assertFalse(f.actor.get().isAlive());
      assertTrue(f.h.pump.get().isEmpty());
      f.h.fixtures.getFirst().cleanup(1, 1);
    }
  }

  @Test
  void obsOwn004() throws Exception {
    try (var f = new Fixture()) {
      f.idle();
      assertThrows(IllegalStateException.class, f.worker::start);
      f.worker.awaitStopped(budget());
      assertEquals(1, f.starts.get());
    }
  }

  @Test
  void obsOwn005() throws Exception {
    try (var f = new Fixture()) {
      f.worker.requestStop();
      assertThrows(IllegalStateException.class, f.worker::start);
      f.worker.awaitStopped(
          () -> {
            throw new AssertionError("no active start/worker");
          });
      assertEquals(0, f.starts.get());
    }
  }

  @Test
  void obsOwn006() throws Exception {
    try (var f = new Fixture()) {
      var primary = new IllegalStateException("starter");
      f.starterFault = primary;
      assertSame(primary, assertThrows(IllegalStateException.class, f.worker::start));
      assertThrows(IllegalStateException.class, f.worker::start);
      f.worker.awaitStopped(
          () -> {
            throw new AssertionError("not started");
          });
      assertEquals(0, f.h.factoryReads);
    }
  }

  @Test
  void obsOwn007() throws Exception {
    try (var f = new Fixture()) {
      var fatal = new AssertionError("starter");
      f.starterFault = fatal;
      assertSame(fatal, assertThrows(AssertionError.class, f.worker::start));
      f.worker.awaitStopped(
          () -> {
            throw new AssertionError("not started");
          });
      assertEquals(0, f.h.factoryReads);
    }
  }

  @Test
  void obsOwn008() throws Exception {
    try (var f = new Fixture()) {
      f.doNotStart = true;
      assertThrows(IllegalStateException.class, f.worker::start);
      f.worker.awaitStopped(
          () -> {
            throw new AssertionError("NEW thread");
          });
      assertEquals(0, f.h.factoryReads);
    }
  }

  @Test
  void obsOwn009() throws Exception {
    try (var f = new Fixture()) {
      var entered = f.blockQuery();
      var primary = new IllegalStateException("after synchronous start");
      f.afterStartFault = primary;
      assertSame(primary, assertThrows(IllegalStateException.class, f.worker::start));
      await(entered);
      f.worker.requestStop();
      f.releaseAll();
      f.worker.awaitStopped(budget());
      assertFalse(f.actor.get().isAlive());
      f.h.fixtures.getFirst().cleanup(1, 1);
    }
  }

  @Test
  void obsOwn010() throws Exception {
    try (var f = new Fixture()) {
      var primary = new InterruptedException("idle");
      f.signal.interrupt = primary;
      f.worker.start();
      await(f.notified);
      f.worker.awaitStopped(budget());
      assertSame(primary, f.failures.peek());
      assertTrue(f.interruptSeen.get());
      assertNull(f.uncaught.get());
    }
  }

  @Test
  void obsOwn011() throws Exception {
    try (var f = new Fixture()) {
      var second = new CountDownLatch(1);
      var attempts = new AtomicInteger();
      f.h.configure =
          row -> {
            if (attempts.incrementAndGet() == 1)
              row.faults.put("query", new SQLException("temporary"));
            else row.query.beforeStatementClose = second::countDown;
          };
      f.signal.immediateOnce.set(true);
      f.signal.beforeWait = () -> f.h.now = 15_000_000_000L;
      f.worker.start();
      await(second);
      f.worker.awaitStopped(budget());
      assertEquals(2, f.h.factoryReads);
      assertTrue(f.failures.isEmpty());
      for (var row : f.h.fixtures) row.cleanup(1, 1);
    }
  }

  @Test
  void obsOwn012() throws Exception {
    try (var f = new Fixture()) {
      var fatal = new AssertionError("linked");
      var sql = new SQLException("query", fatal);
      f.h.configure = row -> row.faults.put("query", sql);
      f.worker.start();
      await(f.notified);
      f.worker.awaitStopped(budget());
      assertSame(fatal, f.failures.peek());
      assertSame(fatal, f.uncaught.get());
    }
  }

  @Test
  void obsOwn013() throws Exception {
    var primary = new IllegalStateException("query");
    asynchronous(primary, null, primary);
  }

  @Test
  void obsOwn014() throws Exception {
    var primary = new AssertionError("query");
    asynchronous(primary, null, primary);
  }

  @Test
  void obsOwn015() throws Exception {
    var primary = new IllegalStateException("query");
    asynchronous(primary, new IllegalStateException("notification"), primary);
  }

  @Test
  void obsOwn016() throws Exception {
    var primary = new IllegalStateException("query");
    var fatal = new AssertionError("notification");
    asynchronous(primary, fatal, fatal);
  }

  @Test
  void obsOwn017() throws Exception {
    try (var f = new Fixture()) {
      var primary = new InterruptedException("idle");
      var secondary = new IllegalStateException("notification");
      f.signal.interrupt = primary;
      f.notifierFault = secondary;
      f.worker.start();
      await(f.notified);
      f.worker.awaitStopped(budget());
      assertSame(primary, f.failures.peek());
      assertSame(secondary, f.uncaught.get());
      assertArrayEquals(new Throwable[] {secondary}, primary.getSuppressed());
      assertTrue(f.interruptSeen.get());
    }
  }

  @Test
  void obsOwn018() throws Exception {
    try (var f = new Fixture()) {
      var primary = new InterruptedException("idle");
      var fatal = new AssertionError("notification");
      f.signal.interrupt = primary;
      f.notifierFault = fatal;
      f.worker.start();
      await(f.notified);
      f.worker.awaitStopped(budget());
      assertSame(fatal, f.uncaught.get());
      assertArrayEquals(new Throwable[] {fatal}, primary.getSuppressed());
    }
  }

  @Test
  void obsOwn019() throws Exception {
    try (var f = new Fixture()) {
      f.signal.beforeWait = f.worker::requestStop;
      f.signal.interrupt = new InterruptedException("expected stop");
      f.worker.start();
      await(f.signal.waiting);
      f.worker.awaitStopped(budget());
      assertTrue(f.failures.isEmpty());
      assertNull(f.uncaught.get());
    }
  }

  @Test
  void obsOwn020() throws Exception {
    try (var f = new Fixture()) {
      f.idle();
      f.worker.awaitStopped(budget());
      assertFalse(f.actor.get().isAlive());
      assertTrue(f.h.pump.isQuiescent());
    }
  }

  @Test
  void obsOwn021() throws Exception {
    try (var f = new Fixture()) {
      var entered = f.blockQuery();
      f.worker.start();
      await(entered);
      f.worker.requestStop();
      assertFalse(f.h.pump.isQuiescent());
      f.releaseAll();
      f.worker.awaitStopped(budget());
      assertTrue(f.h.pump.isQuiescent());
      f.h.fixtures.getFirst().cleanup(1, 1);
    }
  }

  @Test
  void obsOwn022() throws Exception {
    try (var f = new Fixture()) {
      var closed = new CountDownLatch(1);
      f.h.configure =
          row -> {
            row.faults.put("close", new SQLException("unknown"));
          };
      f.signal.beforeWait = closed::countDown;
      f.worker.start();
      await(closed);
      assertThrows(IOException.class, () -> f.worker.awaitStopped(budget()));
      assertFalse(f.h.pump.isQuiescent());
      assertTrue(f.h.pump.get().isEmpty());
    }
  }

  @Test
  void obsOwn023() throws Exception {
    try (var f = new Fixture()) {
      var entered = f.blockQuery();
      f.worker.start();
      await(entered);
      assertThrows(IOException.class, () -> f.worker.awaitStopped(() -> 0));
      assertTrue(f.actor.get().isAlive());
      assertFalse(f.h.pump.isQuiescent());
      f.releaseAll();
    }
  }

  @Test
  void obsOwn024() throws Exception {
    try (var f = new Fixture()) {
      var entered = f.blockQuery();
      f.worker.start();
      await(entered);
      assertThrows(IOException.class, () -> f.worker.awaitStopped(() -> -1));
      f.releaseAll();
    }
  }

  @Test
  void obsOwn025() throws Exception {
    try (var f = new Fixture()) {
      var entered = f.blockQuery();
      f.worker.start();
      await(entered);
      var clock = new AtomicInteger();
      var limits = new AtomicInteger();
      f.stopNanos = () -> TimeUnit.MILLISECONDS.toNanos(clock.getAndIncrement());
      assertThrows(
          IOException.class,
          () ->
              f.worker.awaitStopped(
                  () ->
                      limits.getAndIncrement() == 0
                          ? TimeUnit.MILLISECONDS.toNanos(2)
                          : TimeUnit.SECONDS.toNanos(50)));
      assertTrue(clock.get() >= 3);
      assertTrue(f.actor.get().isAlive());
      f.releaseAll();
    }
  }

  @Test
  void obsOwn026() throws Exception {
    try (var f = new Fixture()) {
      var entered = f.blockQuery();
      f.worker.start();
      await(entered);
      var clock = new AtomicInteger();
      f.stopNanos = () -> clock.getAndIncrement() == 0 ? 1 : 0;
      assertThrows(
          IOException.class, () -> f.worker.awaitStopped(() -> TimeUnit.SECONDS.toNanos(5)));
      f.releaseAll();
    }
  }

  @Test
  void obsOwn027() throws Exception {
    try (var f = new Fixture()) {
      var entered = f.blockQuery();
      f.worker.start();
      await(entered);
      var primary = new IllegalStateException("budget");
      assertSame(
          primary,
          assertThrows(
              IllegalStateException.class,
              () ->
                  f.worker.awaitStopped(
                      () -> {
                        throw primary;
                      })));
      f.releaseAll();
    }
  }

  @Test
  void obsOwn028() throws Exception {
    try (var f = new Fixture()) {
      var entered = f.blockQuery();
      f.worker.start();
      await(entered);
      var fatal = new AssertionError("budget");
      assertSame(
          fatal,
          assertThrows(
              AssertionError.class,
              () ->
                  f.worker.awaitStopped(
                      () -> {
                        throw fatal;
                      })));
      f.releaseAll();
    }
  }

  @Test
  void obsOwn029() throws Exception {
    try (var f = new Fixture()) {
      var entered = f.blockQuery();
      f.worker.start();
      await(entered);
      var primary = new IllegalStateException("nano");
      f.stopNanos =
          () -> {
            throw primary;
          };
      assertSame(
          primary,
          assertThrows(
              IllegalStateException.class,
              () -> f.worker.awaitStopped(() -> TimeUnit.SECONDS.toNanos(5))));
      f.releaseAll();
    }
  }

  @Test
  void obsOwn030() throws Exception {
    try (var f = new Fixture()) {
      var entered = f.blockQuery();
      f.worker.start();
      await(entered);
      var fatal = new AssertionError("nano");
      f.stopNanos =
          () -> {
            throw fatal;
          };
      assertSame(
          fatal,
          assertThrows(
              AssertionError.class,
              () -> f.worker.awaitStopped(() -> TimeUnit.SECONDS.toNanos(5))));
      f.releaseAll();
    }
  }

  @Test
  void obsOwn031() throws Exception {
    try (var f = new Fixture()) {
      var entered = f.blockQuery();
      f.worker.start();
      await(entered);
      var budgetEntered = new CountDownLatch(1);
      var budgetReads = new AtomicInteger();
      try (var waiter = Executors.newSingleThreadExecutor()) {
        var result =
            waiter.submit(
                () -> {
                  Thread.currentThread().interrupt();
                  f.worker.awaitStopped(
                      () -> {
                        if (budgetReads.incrementAndGet() >= 3) budgetEntered.countDown();
                        return TimeUnit.SECONDS.toNanos(5);
                      });
                  return Thread.interrupted();
                });
        try {
          await(budgetEntered);
        } finally {
          f.releaseAll();
        }
        assertTrue(result.get(10, TimeUnit.SECONDS));
        assertTrue(budgetReads.get() >= 3);
      }
    }
  }

  @Test
  void obsOwn032() throws Exception {
    try (var f = new Fixture()) {
      var entered = f.blockQuery();
      f.worker.start();
      await(entered);
      var ticks = new AtomicInteger();
      f.stopNanos = () -> TimeUnit.MILLISECONDS.toNanos(ticks.getAndIncrement());
      try (var waiter = Executors.newSingleThreadExecutor()) {
        var result =
            waiter.submit(
                () -> {
                  Thread.currentThread().interrupt();
                  assertThrows(
                      IOException.class,
                      () -> f.worker.awaitStopped(() -> TimeUnit.MILLISECONDS.toNanos(2)));
                  return Thread.interrupted();
                });
        try {
          assertTrue(result.get(10, TimeUnit.SECONDS));
        } finally {
          f.releaseAll();
        }
      }
    }
  }

  @Test
  void obsOwn033() throws Exception {
    try (var f = new Fixture()) {
      var entering = new CountDownLatch(1);
      var release = new CountDownLatch(1);
      f.beforeStart =
          () -> {
            entering.countDown();
            await(release);
          };
      try (var starter = Executors.newSingleThreadExecutor()) {
        var pending = starter.submit(f.worker::start);
        try {
          await(entering);
          assertEquals(Thread.State.NEW, f.actor.get().getState());
          assertThrows(
              IOException.class,
              () -> f.worker.awaitStopped(() -> TimeUnit.MILLISECONDS.toNanos(1)));
        } finally {
          release.countDown();
        }
        pending.get(10, TimeUnit.SECONDS);
      }
      assertEquals(0, f.h.factoryReads);
    }
  }

  @Test
  void obsOwn034() throws Exception {
    try (var f = new Fixture()) {
      var entering = new CountDownLatch(1);
      var release = new CountDownLatch(1);
      var waiting = new CountDownLatch(1);
      f.beforeStart =
          () -> {
            entering.countDown();
            await(release);
          };
      try (var executor = Executors.newFixedThreadPool(2)) {
        var started = executor.submit(f.worker::start);
        try {
          await(entering);
          var stopped =
              executor.submit(
                  () -> {
                    f.worker.awaitStopped(
                        () -> {
                          waiting.countDown();
                          return TimeUnit.SECONDS.toNanos(5);
                        });
                    return true;
                  });
          await(waiting);
          release.countDown();
          started.get(10, TimeUnit.SECONDS);
          assertTrue(stopped.get(10, TimeUnit.SECONDS));
        } finally {
          release.countDown();
        }
      }
      assertEquals(0, f.h.factoryReads);
    }
  }

  @Test
  void obsOwn035() throws Exception {
    try (var f = new Fixture()) {
      var self = new AtomicReference<Throwable>();
      f.signal.beforeWait =
          () -> {
            self.set(assertThrows(IOException.class, () -> f.worker.awaitStopped(() -> 1)));
          };
      f.worker.start();
      await(f.signal.waiting);
      // Join using the private fixture handle, not a false successful owner await.
      f.actor.get().join(Duration.ofSeconds(5));
      assertInstanceOf(IOException.class, self.get());
      assertThrows(IOException.class, () -> f.worker.awaitStopped(budget()));
    }
  }

  @Test
  void obsOwn036() throws Exception {
    try (var f = new Fixture()) {
      f.worker.requestStop();
      f.worker.requestStop();
      f.worker.awaitStopped(() -> 0);
      assertEquals(1, f.signal.releases.get());
    }
  }

  @Test
  void obsOwn037() throws Exception {
    try (var f = new Fixture()) {
      f.idle();
      f.worker.awaitStopped(budget());
      f.worker.awaitStopped(
          () -> {
            throw new AssertionError("already terminated");
          });
      assertFalse(f.actor.get().isAlive());
    }
  }

  @Test
  void obsOwn038() throws Exception {
    try (var f = new Fixture()) {
      var entered = f.blockQuery();
      f.worker.start();
      await(entered);
      assertThrows(IOException.class, () -> f.worker.awaitStopped(() -> 0));
      f.releaseAll();
      f.actor.get().join(Duration.ofSeconds(5));
      assertFalse(f.actor.get().isAlive());
      assertThrows(
          IOException.class,
          () ->
              f.worker.awaitStopped(
                  () -> {
                    throw new AssertionError("UNKNOWN must not retry wait");
                  }));
    }
  }

  @Test
  void obsOwn039() throws Exception {
    try (var f = new Fixture()) {
      f.h.prepared = () -> null;
      f.worker.start();
      await(f.notified);
      f.worker.awaitStopped(budget());
      assertInstanceOf(NullPointerException.class, f.failures.peek());
      assertSame(f.failures.peek(), f.uncaught.get());
      assertTrue(f.h.fixtures.isEmpty());
    }
  }

  @Test
  void obsOwn040() throws Exception {
    try (var f = new Fixture()) {
      var primary = new IllegalStateException("pump nano");
      f.h.clockFault = primary;
      f.worker.start();
      await(f.notified);
      f.worker.awaitStopped(budget());
      assertSame(primary, f.failures.peek());
      assertSame(primary, f.uncaught.get());
      assertEquals(0, f.h.factoryReads);
    }
  }

  @Test
  void obsOwn041() throws Exception {
    try (var f = new Fixture()) {
      var fatal = new AssertionError("pump nano");
      f.h.clockFault = fatal;
      f.worker.start();
      await(f.notified);
      f.worker.awaitStopped(budget());
      assertSame(fatal, f.failures.peek());
      assertSame(fatal, f.uncaught.get());
      assertEquals(0, f.h.factoryReads);
    }
  }

  @Test
  void obsOwn042() throws Exception {
    for (Throwable primary : List.of(new IllegalStateException("wait"), new AssertionError("wait")))
      try (var f = new Fixture()) {
        f.signal.beforeWait = () -> raise(primary);
        f.worker.start();
        await(f.notified);
        f.worker.awaitStopped(budget());
        assertSame(primary, f.failures.peek());
        assertSame(primary, f.uncaught.get());
      }
  }

  @Test
  void obsOwn043() {
    for (Throwable primary :
        List.of(new IllegalStateException("signal"), new AssertionError("signal")))
      try (var f = new Fixture()) {
        f.signal.releaseFault = primary;
        assertSame(primary, assertThrows(primary.getClass(), () -> f.worker.awaitStopped(() -> 0)));
        f.signal.releaseFault = null;
        assertThrows(
            IOException.class,
            () ->
                f.worker.awaitStopped(
                    () -> {
                      throw new AssertionError("UNKNOWN");
                    }));
      }
  }

  @Test
  void obsOwn044() throws Exception {
    try (var f = new Fixture()) {
      var row = new ApiReadOnlyObservationAttemptTest.Fixture();
      var used = row.attempt();
      used.read();
      f.h.prepared = () -> used;
      f.worker.start();
      await(f.notified);
      f.worker.awaitStopped(budget());
      assertInstanceOf(IllegalStateException.class, f.failures.peek());
      assertSame(f.failures.peek(), f.uncaught.get());
      row.cleanup(1, 1);
    }
  }
}
