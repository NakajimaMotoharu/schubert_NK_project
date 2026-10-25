package dev.codex.schubert.nk.api.bootstrap;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.sun.net.httpserver.HttpContext;
import com.sun.net.httpserver.HttpHandler;
import com.sun.net.httpserver.HttpServer;
import java.io.IOException;
import java.net.InetSocketAddress;
import java.time.Duration;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.Executor;
import java.util.concurrent.ThreadPoolExecutor;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicReference;
import java.util.function.BooleanSupplier;
import org.junit.jupiter.api.Test;

/** SSC313/PG-D462/PT-API-STOP001..004; owned loopback component, not native admission. */
final class ApiManagementStopTest {
  private static final Map<String, String> INFO =
      Map.of(
          "commit",
          "b".repeat(40),
          "app",
          "0.1.0",
          "config",
          "1",
          "schema",
          "025",
          "protocol",
          "001");

  @Test
  void apiStop001FailedStopNeverMakesLaterCloseAFalseSuccess() throws Exception {
    for (Throwable marker :
        java.util.List.of(
            new IllegalStateException("synthetic first stop"),
            new AssertionError("synthetic first stop"))) {
      var captured = new AtomicReference<StopFailureServer>();
      try {
        var server = open(captured, Optional.of(marker), false);
        var releases = new AtomicInteger();
        server.promote(releases::incrementAndGet);
        assertTrue(server.ready());
        assertSame(marker, assertThrows(marker.getClass(), server::close));
        assertFalse(server.ready());
        assertThrows(IOException.class, () -> server.promote(releases::incrementAndGet));
        assertEquals(1, releases.get());
        server.close();
        assertEquals(
            2, captured.get().stops.get(), "failed stop must be retried by retained owner");
        assertTrue(captured.get().executor().isTerminated());
        server.close();
        assertEquals(2, captured.get().stops.get());
      } finally {
        var fixture = captured.get();
        if (fixture != null) fixture.dispose();
      }
    }
  }

  @Test
  void apiStop002InvalidBudgetsLeaveReadyOwnerUntouched() throws Exception {
    var captured = new AtomicReference<StopFailureServer>();
    try {
      var server = open(captured, Optional.empty(), false);
      server.promote(() -> {});
      assertThrows(NullPointerException.class, () -> server.closeWithin(null));
      assertThrows(IllegalArgumentException.class, () -> server.closeWithin(Duration.ofNanos(-1)));
      assertThrows(
          IllegalArgumentException.class,
          () -> server.closeWithin(Duration.ofSeconds(30).plusNanos(1)));
      assertTrue(server.ready());
      assertEquals(0, captured.get().stops.get());
      server.closeWithin(Duration.ofSeconds(5));
      assertFalse(server.ready());
      assertEquals(1, captured.get().stops.get());
      server.closeWithin(Duration.ZERO);
      assertEquals(1, captured.get().stops.get());
    } finally {
      var fixture = captured.get();
      if (fixture != null) fixture.dispose();
    }
  }

  @Test
  void apiStop003LockDeadlineAndNewInterruptNeverDuplicateStop() throws Exception {
    var captured = new AtomicReference<StopFailureServer>();
    var firstFailure = new AtomicReference<Throwable>();
    var secondFailure = new AtomicReference<Throwable>();
    var secondInterrupted = new java.util.concurrent.atomic.AtomicBoolean();
    Thread first = null;
    Thread second = null;
    try {
      var server = open(captured, Optional.empty(), true);
      server.promote(() -> {});
      first =
          new Thread(
              () ->
                  closeObserved(
                      server, firstFailure, new java.util.concurrent.atomic.AtomicBoolean()));
      first.start();
      assertTrue(captured.get().stopEntered.await(5, TimeUnit.SECONDS));
      assertFalse(server.ready());
      assertThrows(IllegalStateException.class, () -> server.closeWithin(Duration.ZERO));
      assertEquals(1, captured.get().stops.get());
      second = new Thread(() -> closeObserved(server, secondFailure, secondInterrupted));
      second.start();
      Thread waiting = second;
      await(() -> waiting.getState() == Thread.State.TIMED_WAITING);
      second.interrupt();
      second.join(5000);
      assertFalse(second.isAlive());
      assertInstanceOf(IllegalStateException.class, secondFailure.get());
      assertEquals("API management stop unconfirmed", secondFailure.get().getMessage());
      assertTrue(secondInterrupted.get());
      assertEquals(1, captured.get().stops.get());
      captured.get().releaseStop.countDown();
      first.join(5000);
      assertFalse(first.isAlive());
      assertNull(firstFailure.get());
      server.closeWithin(Duration.ZERO);
      assertEquals(1, captured.get().stops.get());
      assertTrue(captured.get().executor().isTerminated());
    } finally {
      var fixture = captured.get();
      if (fixture != null) fixture.releaseStop.countDown();
      try {
        try {
          if (first != null) first.join(5000);
        } finally {
          if (second != null) second.join(5000);
        }
      } finally {
        if (fixture != null) fixture.dispose();
      }
      if (first != null) assertFalse(first.isAlive());
      if (second != null) assertFalse(second.isAlive());
    }
  }

  @Test
  void apiStop004WorkerTimeoutInterruptAndActualRejoinRemainDistinct() throws Exception {
    var captured = new AtomicReference<StopFailureServer>();
    var entered = new CountDownLatch(1);
    var release = new CountDownLatch(1);
    var failure = new AtomicReference<Throwable>();
    var interrupted = new java.util.concurrent.atomic.AtomicBoolean();
    Thread closer = null;
    try {
      var server = open(captured, Optional.empty(), false);
      server.promote(() -> {});
      var executor = captured.get().executor();
      executor.execute(
          () -> {
            entered.countDown();
            while (release.getCount() != 0) {
              try {
                release.await();
              } catch (InterruptedException notification) {
                /* Held fixture work; only the owning test's release ends it. */
              }
            }
          });
      assertTrue(entered.await(5, TimeUnit.SECONDS));
      assertThrows(IllegalStateException.class, () -> server.closeWithin(Duration.ZERO));
      assertFalse(server.ready());
      assertTrue(executor.isShutdown());
      assertFalse(executor.isTerminated());
      assertEquals(1, captured.get().stops.get());
      closer = new Thread(() -> closeObserved(server, failure, interrupted));
      closer.start();
      Thread waiting = closer;
      await(() -> waiting.getState() == Thread.State.TIMED_WAITING);
      closer.interrupt();
      closer.join(5000);
      assertFalse(closer.isAlive());
      assertInstanceOf(IllegalStateException.class, failure.get());
      assertTrue(interrupted.get());
      assertFalse(executor.isTerminated());
      release.countDown();
      assertTrue(executor.awaitTermination(5, TimeUnit.SECONDS));
      server.closeWithin(Duration.ofSeconds(5));
      assertEquals(1, captured.get().stops.get());
      assertTrue(executor.isTerminated());
    } finally {
      release.countDown();
      var fixture = captured.get();
      try {
        if (closer != null) closer.join(5000);
      } finally {
        if (fixture != null) fixture.dispose();
      }
      if (closer != null) assertFalse(closer.isAlive());
    }
  }

  private static ApiManagementServer open(
      AtomicReference<StopFailureServer> captured, Optional<Throwable> failure, boolean holdStop)
      throws IOException {
    return ApiManagementServer.open(
        INFO,
        () -> true,
        0,
        (address, backlog) -> {
          assertEquals("127.0.0.1", address.getAddress().getHostAddress());
          assertEquals(0, address.getPort());
          assertEquals(32, backlog);
          var fixture = new StopFailureServer(address, backlog, failure, holdStop);
          captured.set(fixture);
          return fixture;
        });
  }

  private static void closeObserved(
      ApiManagementServer server,
      AtomicReference<Throwable> failure,
      java.util.concurrent.atomic.AtomicBoolean interrupted) {
    try {
      server.closeWithin(Duration.ofSeconds(30));
    } catch (Throwable outcome) {
      failure.set(outcome);
    } finally {
      interrupted.set(Thread.currentThread().isInterrupted());
    }
  }

  private static void await(BooleanSupplier condition) throws InterruptedException {
    long deadline = System.nanoTime() + TimeUnit.SECONDS.toNanos(5);
    while (!condition.getAsBoolean() && System.nanoTime() - deadline < 0) Thread.sleep(1);
    assertTrue(condition.getAsBoolean());
  }

  static class StopFailureServer extends HttpServer {
    private final AtomicInteger stops = new AtomicInteger();
    private final CountDownLatch stopEntered = new CountDownLatch(1);
    private final CountDownLatch releaseStop;
    private final Optional<Throwable> failure;
    private final HttpServer actual;

    StopFailureServer(
        InetSocketAddress address, int backlog, Optional<Throwable> failure, boolean holdStop)
        throws IOException {
      this.failure = failure;
      this.releaseStop = new CountDownLatch(holdStop ? 1 : 0);
      this.actual = HttpServer.create(address, backlog);
    }

    ThreadPoolExecutor executor() {
      return (ThreadPoolExecutor) Objects.requireNonNull(actual.getExecutor());
    }

    void dispose() throws InterruptedException {
      actual.stop(0);
      executor().shutdownNow();
      assertTrue(executor().awaitTermination(3, TimeUnit.SECONDS));
    }

    @Override
    public void stop(int delay) {
      if (stops.incrementAndGet() == 1 && failure.isPresent()) {
        var marker = failure.orElseThrow();
        if (marker instanceof RuntimeException runtime) throw runtime;
        throw (Error) marker;
      }
      stopEntered.countDown();
      try {
        if (!releaseStop.await(5, TimeUnit.SECONDS))
          throw new AssertionError("fixture stop was not released");
      } catch (InterruptedException unexpected) {
        Thread.currentThread().interrupt();
        throw new AssertionError("fixture stop interrupted", unexpected);
      }
      actual.stop(delay);
    }

    @Override
    public void bind(InetSocketAddress address, int backlog) throws IOException {
      actual.bind(address, backlog);
    }

    @Override
    public void start() {
      actual.start();
    }

    @Override
    public void setExecutor(Executor executor) {
      actual.setExecutor(executor);
    }

    @Override
    public Executor getExecutor() {
      return actual.getExecutor();
    }

    @Override
    public HttpContext createContext(String path, HttpHandler handler) {
      return actual.createContext(path, handler);
    }

    @Override
    public HttpContext createContext(String path) {
      return actual.createContext(path);
    }

    @Override
    public void removeContext(String path) {
      actual.removeContext(path);
    }

    @Override
    public void removeContext(HttpContext context) {
      actual.removeContext(context);
    }

    @Override
    public InetSocketAddress getAddress() {
      return actual.getAddress();
    }
  }
}
