package dev.codex.schubert.nk.api.bootstrap;

import static org.junit.jupiter.api.Assertions.*;

import com.sun.net.httpserver.HttpContext;
import com.sun.net.httpserver.HttpHandler;
import com.sun.net.httpserver.HttpServer;
import java.io.IOException;
import java.net.InetSocketAddress;
import java.util.Map;
import java.util.Objects;
import java.util.concurrent.Executor;
import java.util.concurrent.ThreadPoolExecutor;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicReference;
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
    var marker = new IllegalStateException("synthetic first stop");
    var captured = new AtomicReference<StopFailureServer>();
    try {
      var server =
          ApiManagementServer.open(
              INFO,
              () -> true,
              0,
              (address, backlog) -> {
                assertEquals("127.0.0.1", address.getAddress().getHostAddress());
                assertEquals(0, address.getPort());
                assertEquals(32, backlog);
                var fixture = new StopFailureServer(address, backlog, marker);
                captured.set(fixture);
                return fixture;
              });
      var releases = new AtomicInteger();
      server.promote(releases::incrementAndGet);
      assertTrue(server.ready());
      assertSame(marker, assertThrows(IllegalStateException.class, server::close));
      assertFalse(server.ready());
      assertThrows(IOException.class, () -> server.promote(releases::incrementAndGet));
      assertEquals(1, releases.get());
      server.close();
      assertEquals(2, captured.get().stops.get(), "failed stop must be retried by retained owner");
      assertTrue(captured.get().executor().isTerminated());
      server.close();
      assertEquals(2, captured.get().stops.get());
    } finally {
      var fixture = captured.get();
      if (fixture != null) fixture.dispose();
    }
  }

  private static final class StopFailureServer extends HttpServer {
    private final AtomicInteger stops = new AtomicInteger();
    private final RuntimeException failure;
    private final HttpServer actual;

    StopFailureServer(InetSocketAddress address, int backlog, RuntimeException failure)
        throws IOException {
      this.failure = failure;
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
      if (stops.incrementAndGet() == 1) throw failure;
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
