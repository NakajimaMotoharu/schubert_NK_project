package dev.codex.schubert.nk.web.bootstrap;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assertions.fail;

import com.sun.net.httpserver.HttpContext;
import com.sun.net.httpserver.HttpHandler;
import com.sun.net.httpserver.HttpServer;
import java.io.IOException;
import java.net.InetSocketAddress;
import java.net.ServerSocket;
import java.time.Duration;
import java.util.Map;
import java.util.Objects;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.Executor;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicReference;
import org.junit.jupiter.api.Test;

/** SS342/354SSC335; PT-WEB-MGMT335001..003. Owned finite component only, never a live unit. */
final class WebManagementDeadlineTest {
  private static final Map<String, String> INFO =
      Map.of(
          "commit",
          "7".repeat(40),
          "app",
          "0.1.0",
          "config",
          "1",
          "schema",
          "025",
          "protocol",
          "001");

  private enum Hold {
    STOP,
    START
  }

  private enum Notification {
    NONE,
    DURING_LOCK,
    BEFORE_CALL
  }

  private record Outcome(IOException failure, boolean interrupted) {}

  @Test
  void webMgmt335001ZeroBudgetDoesNotWaitForOtherCloseOwner() throws Exception {
    exercise(Hold.STOP, Notification.NONE);
  }

  @Test
  void webMgmt335002InterruptDuringLockReturnsUnknownWithNotification() throws Exception {
    exercise(Hold.STOP, Notification.DURING_LOCK);
  }

  @Test
  void webMgmt335003PreInterruptDuringStartContentionRefusesLatePromotion() throws Exception {
    exercise(Hold.START, Notification.BEFORE_CALL);
  }

  private static void exercise(Hold hold, Notification notification) throws Exception {
    var fixture = new HeldServer(hold);
    var owner =
        WebManagementServer.bind(
            INFO,
            () -> true,
            0,
            (address, backlog) -> {
              fixture.bind(address, backlog);
              return fixture;
            });
    int port = owner.port();
    var workers = Executors.newFixedThreadPool(2);
    Future<Void> first = null;
    try {
      if (hold == Hold.STOP) owner.start();
      first =
          workers.submit(
              () -> {
                if (hold == Hold.STOP) owner.closeWithin(Duration.ofSeconds(10));
                else owner.start();
                return null;
              });
      assertTrue(fixture.entered.await(3, TimeUnit.SECONDS));
      var waiter = new AtomicReference<Thread>();
      var entered = new CountDownLatch(1);
      var second =
          workers.submit(
              () -> {
                Thread thread = Thread.currentThread();
                if (notification == Notification.BEFORE_CALL) thread.interrupt();
                waiter.set(thread);
                entered.countDown();
                try {
                  var failure =
                      assertThrows(
                          IOException.class,
                          () ->
                              owner.closeWithin(
                                  notification == Notification.DURING_LOCK
                                      ? Duration.ofSeconds(10)
                                      : Duration.ZERO));
                  return new Outcome(failure, thread.isInterrupted());
                } finally {
                  Thread
                      .interrupted(); // Restore this test worker for its pool, after observing the
                  // flag.
                }
              });
      assertTrue(entered.await(3, TimeUnit.SECONDS));
      if (notification == Notification.DURING_LOCK) {
        Thread thread = Objects.requireNonNull(waiter.get());
        awaitLockWait(thread);
        thread.interrupt();
      }
      // The first owner is still held. Success cannot be inferred merely from an elapsed duration.
      Outcome actual = second.get(3, TimeUnit.SECONDS);
      assertEquals("Web management stop unconfirmed", actual.failure().getMessage());
      assertNull(actual.failure().getCause());
      assertEquals(0, actual.failure().getSuppressed().length);
      assertEquals(notification != Notification.NONE, actual.interrupted());
      assertEquals(1L, fixture.release.getCount());
      assertEquals(hold == Hold.STOP ? 1 : 0, fixture.stops.get());
      assertFalse(owner.ready());
    } finally {
      fixture.release.countDown();
      try {
        if (first != null) first.get(3, TimeUnit.SECONDS);
        if (hold == Hold.START) {
          var promotions = new AtomicInteger();
          var unavailable =
              assertThrows(
                  IOException.class,
                  () ->
                      owner.promote(
                          () -> {
                            promotions.incrementAndGet();
                          }));
          assertEquals("Web readiness unavailable", unavailable.getMessage());
          assertEquals(0, promotions.get());
        }
      } finally {
        try {
          owner.closeWithin(Duration.ofSeconds(3));
          owner.closeWithin(Duration.ZERO);
          assertEquals(1, fixture.stops.get());
          assertFalse(owner.ready());
        } finally {
          workers.shutdownNow();
          assertTrue(workers.awaitTermination(3, TimeUnit.SECONDS));
          try (var released = new ServerSocket()) {
            released.setReuseAddress(true);
            released.bind(new InetSocketAddress("127.0.0.1", port));
          }
        }
      }
    }
  }

  private static void awaitLockWait(Thread thread) throws InterruptedException {
    long deadline = System.nanoTime() + Duration.ofSeconds(3).toNanos();
    while (thread.getState() != Thread.State.WAITING
        && thread.getState() != Thread.State.TIMED_WAITING) {
      if (System.nanoTime() >= deadline) fail("owned contender did not enter its lock wait");
      Thread.sleep(1);
    }
  }

  /** Prepare all fixture control before its factory acquires an ordinary ephemeral JDK server. */
  private static final class HeldServer extends HttpServer {
    private final Hold hold;
    private final CountDownLatch entered = new CountDownLatch(1);
    private final CountDownLatch release = new CountDownLatch(1);
    private final AtomicInteger stops = new AtomicInteger();
    private final AtomicReference<HttpServer> delegate = new AtomicReference<>();

    HeldServer(Hold hold) {
      this.hold = hold;
    }

    private HttpServer actual() {
      return Objects.requireNonNull(delegate.get(), "fixture not bound");
    }

    private void hold() {
      entered.countDown();
      try {
        if (!release.await(12, TimeUnit.SECONDS))
          throw new AssertionError("owned fixture watchdog");
      } catch (InterruptedException interrupted) {
        Thread.currentThread().interrupt();
        throw new AssertionError("owned fixture holder unexpectedly interrupted");
      }
    }

    @Override
    public void bind(InetSocketAddress address, int backlog) throws IOException {
      if (delegate.get() != null) throw new IOException("fixture already bound");
      delegate.set(HttpServer.create(address, backlog));
    }

    @Override
    public void start() {
      actual().start();
      if (hold == Hold.START) hold();
    }

    @Override
    public void stop(int delay) {
      assertEquals(0, delay);
      stops.incrementAndGet();
      if (hold == Hold.STOP) hold();
      actual().stop(delay);
    }

    @Override
    public void setExecutor(Executor executor) {
      actual().setExecutor(executor);
    }

    @Override
    public Executor getExecutor() {
      return actual().getExecutor();
    }

    @Override
    public InetSocketAddress getAddress() {
      return actual().getAddress();
    }

    @Override
    public HttpContext createContext(String path, HttpHandler handler) {
      return actual().createContext(path, handler);
    }

    @Override
    public HttpContext createContext(String path) {
      return actual().createContext(path);
    }

    @Override
    public void removeContext(String path) {
      actual().removeContext(path);
    }

    @Override
    public void removeContext(HttpContext context) {
      actual().removeContext(context);
    }
  }
}
