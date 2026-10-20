package dev.codex.schubert.nk.api.bootstrap;

import static org.junit.jupiter.api.Assertions.*;

import com.sun.net.httpserver.HttpContext;
import com.sun.net.httpserver.HttpHandler;
import com.sun.net.httpserver.HttpServer;
import dev.codex.schubert.nk.api.file.OwnedRetentionProcess;
import dev.codex.schubert.nk.api.file.ServiceProcessResources;
import dev.codex.schubert.nk.storage.ResourceScope;
import java.io.IOException;
import java.net.InetSocketAddress;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.Executor;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicReference;
import org.junit.jupiter.api.Test;

/** SS316/PT-NHOLD316004: self-owned loopback bind/start, never native admission. */
final class ApiManagementBindTest {
  private static final Map<String, String> INFO =
      Map.of(
          "commit",
          "c".repeat(40),
          "app",
          "0.1.0",
          "config",
          "1",
          "schema",
          "025",
          "protocol",
          "001");

  @Test
  void bind316001BoundOnlyNeverReleasesAdmissionOrAdvertisesReady() throws Exception {
    var healthy = new AtomicBoolean(true);
    var releases = new AtomicInteger();
    var server = ApiManagementServer.bind(INFO, healthy::get, 0, HttpServer::create);
    try {
      assertFalse(server.ready());
      assertThrows(IOException.class, () -> server.promote(releases::incrementAndGet));
      assertEquals(0, releases.get());
      server.start();
      assertFalse(server.ready());
      server.promote(releases::incrementAndGet);
      assertEquals(1, releases.get());
      assertTrue(server.ready());
      assertThrows(IllegalStateException.class, server::start);
      healthy.set(false);
      assertFalse(server.ready());
      healthy.set(true);
      assertTrue(server.ready());
    } finally {
      server.close();
    }
    assertFalse(server.ready());
    assertThrows(IllegalStateException.class, server::start);
    assertThrows(IOException.class, () -> server.promote(releases::incrementAndGet));
    assertEquals(1, releases.get());
  }

  @Test
  void bind316002UnstartedOwnerClosesAndInvalidInputsPrecedeFactory() throws Exception {
    int port;
    var server = ApiManagementServer.bind(INFO, () -> true, 0, HttpServer::create);
    try {
      port = server.port();
    } finally {
      server.close();
    }
    assertThrows(IllegalStateException.class, server::start);
    try (var rebound = ApiManagementServer.open(INFO, () -> true, port)) {
      assertEquals(port, rebound.port());
      assertFalse(rebound.ready());
    }
    var acquired = new AtomicInteger();
    ApiManagementServer.Factory forbidden =
        (address, backlog) -> {
          acquired.incrementAndGet();
          throw new AssertionError("invalid input cannot acquire");
        };
    assertThrows(
        NullPointerException.class, () -> ApiManagementServer.bind(null, () -> true, 0, forbidden));
    assertThrows(
        NullPointerException.class, () -> ApiManagementServer.bind(INFO, null, 0, forbidden));
    assertThrows(
        NullPointerException.class, () -> ApiManagementServer.bind(INFO, () -> true, 0, null));
    assertThrows(
        IllegalArgumentException.class,
        () -> ApiManagementServer.bind(Map.of(), () -> true, 0, forbidden));
    assertEquals(0, acquired.get());
  }

  @Test
  void bind316003EverySetupFailureLeavesTheCapturedOwnerClosableWithoutStartRetry()
      throws Exception {
    for (int phase = 0; phase < 3; phase++) {
      for (Throwable marker :
          List.of(
              new IllegalStateException("fixture start"), new AssertionError("fixture start"))) {
        int failAt = phase;
        var captured = new AtomicReference<SetupFailureServer>();
        try {
          var server =
              ApiManagementServer.bind(
                  INFO,
                  () -> true,
                  0,
                  (address, backlog) -> {
                    var fixture = new SetupFailureServer(address, backlog, failAt, marker);
                    captured.set(fixture);
                    return fixture;
                  });
          assertSame(marker, assertThrows(marker.getClass(), server::start));
          assertFalse(server.ready());
          assertThrows(IllegalStateException.class, server::start);
          server.close();
          assertTrue(captured.get().executor().isTerminated());
          try (var rebound = ApiManagementServer.open(INFO, () -> true, server.port())) {
            assertFalse(rebound.ready());
          }
        } finally {
          var fixture = captured.get();
          if (fixture != null) fixture.dispose();
        }
      }
    }
  }

  @Test
  void bind316004ConcurrentStopWaitsForStartAndCannotBeUndoneByLateStart() throws Exception {
    var entered = new CountDownLatch(1);
    var release = new CountDownLatch(1);
    var captured = new AtomicReference<ApiManagementStopTest.StopFailureServer>();
    var failure = new AtomicReference<Throwable>();
    Thread starter = null;
    Thread closer = null;
    try {
      var server =
          ApiManagementServer.bind(
              INFO,
              () -> true,
              0,
              (address, backlog) -> {
                var fixture =
                    new ApiManagementStopTest.StopFailureServer(
                        address, backlog, Optional.empty(), false) {
                      @Override
                      public void start() {
                        entered.countDown();
                        try {
                          if (!release.await(5, TimeUnit.SECONDS))
                            throw new AssertionError("fixture start not released");
                        } catch (InterruptedException interrupted) {
                          Thread.currentThread().interrupt();
                          throw new AssertionError(interrupted);
                        }
                        super.start();
                      }
                    };
                captured.set(fixture);
                return fixture;
              });
      starter =
          new Thread(
              () -> {
                try {
                  server.start();
                } catch (Throwable unexpected) {
                  failure.compareAndSet(null, unexpected);
                }
              });
      starter.start();
      assertTrue(entered.await(5, TimeUnit.SECONDS));
      closer =
          new Thread(
              () -> {
                try {
                  server.close();
                } catch (Throwable unexpected) {
                  failure.compareAndSet(null, unexpected);
                }
              });
      closer.start();
      long deadline = System.nanoTime() + TimeUnit.SECONDS.toNanos(3);
      while (closer.getState() != Thread.State.TIMED_WAITING && System.nanoTime() - deadline < 0)
        Thread.sleep(1);
      assertEquals(Thread.State.TIMED_WAITING, closer.getState());
      assertFalse(server.ready());
      release.countDown();
      starter.join(5000);
      closer.join(5000);
      assertFalse(starter.isAlive());
      assertFalse(closer.isAlive());
      assertNull(failure.get());
      assertFalse(server.ready());
      assertThrows(IllegalStateException.class, server::start);
      assertTrue(captured.get().executor().isTerminated());
    } finally {
      release.countDown();
      try {
        if (starter != null) starter.join(5000);
      } finally {
        try {
          if (closer != null) closer.join(5000);
        } finally {
          var fixture = captured.get();
          if (fixture != null) fixture.dispose();
        }
      }
    }
  }

  @Test
  void bind316005UnconfirmedCleanupRetainsTheBoundOwnerAndOuterFrame() throws Exception {
    for (String kind : List.of("runtime", "error"))
      OwnedRetentionProcess.assertHeld(Driver.class, List.of("START", "STOP"), kind);
  }

  private static class SetupFailureServer extends ApiManagementStopTest.StopFailureServer {
    private final int phase;
    private final Throwable marker;

    SetupFailureServer(InetSocketAddress address, int backlog, int phase, Throwable marker)
        throws IOException {
      super(address, backlog, Optional.empty(), false);
      this.phase = phase;
      this.marker = marker;
    }

    private void fail(int current) {
      if (phase != current) return;
      if (marker instanceof RuntimeException runtime) throw runtime;
      throw (Error) marker;
    }

    @Override
    public void setExecutor(Executor executor) {
      super.setExecutor(executor);
      fail(0);
    }

    @Override
    public HttpContext createContext(String path, HttpHandler handler) {
      var context = super.createContext(path, handler);
      fail(1);
      return context;
    }

    @Override
    public void start() {
      super.start();
      fail(2);
    }
  }

  public static final class Driver {
    public static void main(String[] arguments) throws IOException {
      OwnedRetentionProcess.deadline();
      Throwable marker =
          arguments[0].equals("runtime")
              ? new IllegalStateException("fixture unknown")
              : new AssertionError("fixture unknown");
      try {
        ResourceScope.acquire(
            () ->
                ApiManagementServer.bind(
                    INFO,
                    () -> true,
                    0,
                    (address, backlog) ->
                        new SetupFailureServer(
                            address, backlog, 2, new IllegalStateException("fixture start")) {
                          @Override
                          public void start() {
                            System.out.println("START");
                            super.start();
                          }

                          @Override
                          public void stop(int delay) {
                            System.out.println("STOP");
                            if (marker instanceof RuntimeException runtime) throw runtime;
                            throw (Error) marker;
                          }
                        }),
            ServiceProcessResources.ownedRelease(ApiManagementServer::close, true),
            owner -> {
              owner.start();
              return Boolean.TRUE;
            });
      } finally {
        System.out.println("OUTER_RELEASED");
      }
    }
  }
}
