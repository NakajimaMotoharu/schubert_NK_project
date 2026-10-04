package dev.codex.schubert.nk.web.bootstrap;

import static org.junit.jupiter.api.Assertions.*;

import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;
import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.Test;

/**
 * Independent actual HTTP status/JSON literals, not a native startup admission. WEB-READY001..003.
 */
final class WebManagementServerTest {
  @Test
  void ready003StartupFailureKeepsInterruptedCleanupSeparate() throws Exception {
    var captured = new java.util.concurrent.atomic.AtomicReference<PartiallyStartedServer>();
    try {
      var failure =
          assertThrows(
              IllegalStateException.class,
              () ->
                  WebManagementServer.open(
                      INFO,
                      () -> true,
                      0,
                      (address, backlog) -> {
                        var server = new PartiallyStartedServer(address, backlog);
                        captured.set(server);
                        return server;
                      }));
      assertTrue(Thread.currentThread().isInterrupted());
      assertEquals(1, failure.getSuppressed().length);
      assertInstanceOf(IOException.class, failure.getSuppressed()[0]);
      assertEquals("Web management stop unconfirmed", failure.getSuppressed()[0].getMessage());
      assertFalse(captured.get().executor().isTerminated());
    } finally {
      Thread.interrupted();
      var server = captured.get();
      if (server != null) {
        server.release.countDown();
        server.stop(0);
        assertTrue(server.executor().awaitTermination(3, java.util.concurrent.TimeUnit.SECONDS));
      }
    }
  }

  /** Real server/executor; the vendor start failure occurs with an actual live setup callback. */
  private static final class PartiallyStartedServer extends com.sun.net.httpserver.HttpServer {
    private final com.sun.net.httpserver.HttpServer actual;
    private final java.util.concurrent.CountDownLatch entered =
        new java.util.concurrent.CountDownLatch(1);
    private final java.util.concurrent.CountDownLatch release =
        new java.util.concurrent.CountDownLatch(1);

    PartiallyStartedServer(java.net.InetSocketAddress address, int backlog) throws IOException {
      actual = com.sun.net.httpserver.HttpServer.create(address, backlog);
    }

    java.util.concurrent.ThreadPoolExecutor executor() {
      return (java.util.concurrent.ThreadPoolExecutor) actual.getExecutor();
    }

    @Override
    public void start() {
      actual.start();
      executor()
          .execute(
              () -> {
                entered.countDown();
                boolean waiting = true;
                while (waiting) {
                  try {
                    release.await();
                    waiting = false;
                  } catch (InterruptedException notification) {
                    /* Deliberate uncooperative vendor callback. */
                  }
                }
              });
      try {
        if (!entered.await(3, java.util.concurrent.TimeUnit.SECONDS))
          throw new IllegalStateException("fixture callback not started");
      } catch (InterruptedException interrupted) {
        Thread.currentThread().interrupt();
        throw new IllegalStateException("fixture setup interrupted");
      }
      Thread.currentThread().interrupt();
      throw new IllegalStateException("synthetic post-start failure");
    }

    @Override
    public void bind(java.net.InetSocketAddress a, int b) throws IOException {
      actual.bind(a, b);
    }

    @Override
    public void setExecutor(java.util.concurrent.Executor executor) {
      actual.setExecutor(executor);
    }

    @Override
    public java.util.concurrent.Executor getExecutor() {
      return actual.getExecutor();
    }

    @Override
    public void stop(int delay) {
      actual.stop(delay);
    }

    @Override
    public com.sun.net.httpserver.HttpContext createContext(
        String p, com.sun.net.httpserver.HttpHandler h) {
      return actual.createContext(p, h);
    }

    @Override
    public com.sun.net.httpserver.HttpContext createContext(String p) {
      return actual.createContext(p);
    }

    @Override
    public void removeContext(String p) {
      actual.removeContext(p);
    }

    @Override
    public void removeContext(com.sun.net.httpserver.HttpContext c) {
      actual.removeContext(c);
    }

    @Override
    public java.net.InetSocketAddress getAddress() {
      return actual.getAddress();
    }
  }

  @Test
  void ready005ActualBlockedHandlerUnknownJoinRetainsOwnerAndRetries() throws Exception {
    var entered = new java.util.concurrent.CountDownLatch(1);
    var release = new java.util.concurrent.CountDownLatch(1);
    var blocked = new AtomicBoolean();
    var server =
        WebManagementServer.open(
            INFO,
            () -> {
              if (blocked.get()) {
                entered.countDown();
                boolean waiting = true;
                while (waiting) {
                  try {
                    release.await();
                    waiting = false;
                  } catch (InterruptedException ignored) {
                    /* Deliberately uncooperative fixture. */
                  }
                }
              }
              return true;
            },
            0);
    try {
      server.promote(() -> {});
      blocked.set(true);
      var response =
          CLIENT.sendAsync(
              HttpRequest.newBuilder(
                      URI.create("http://127.0.0.1:" + server.port() + "/actuator/health"))
                  .timeout(Duration.ofSeconds(3))
                  .GET()
                  .build(),
              HttpResponse.BodyHandlers.ofString());
      assertTrue(entered.await(3, java.util.concurrent.TimeUnit.SECONDS));
      assertThrows(IOException.class, () -> server.closeWithin(Duration.ZERO));
      assertFalse(server.ready());
      assertThrows(IOException.class, () -> server.closeWithin(Duration.ZERO));
      Thread.currentThread().interrupt();
      try {
        assertThrows(IOException.class, server::close);
        assertTrue(Thread.currentThread().isInterrupted());
      } finally {
        assertTrue(Thread.interrupted());
      }
      assertThrows(IOException.class, () -> server.promote(() -> fail("no new admission")));
      release.countDown();
      server.close();
      server.closeWithin(Duration.ZERO);
      assertFalse(server.ready());
      var disconnected =
          assertThrows(
              java.util.concurrent.ExecutionException.class,
              () -> response.get(3, java.util.concurrent.TimeUnit.SECONDS));
      assertInstanceOf(IOException.class, disconnected.getCause());
    } finally {
      release.countDown();
      server.close();
    }
  }

  @Test
  void ready006HeldBindStartOnceAndStopBudgetBoundaries() throws Exception {
    var server = WebManagementServer.bind(INFO, () -> true);
    try {
      assertEquals(8081, server.port());
      assertFalse(server.ready());
      var releases = new AtomicInteger();
      assertThrows(IOException.class, () -> server.promote(releases::incrementAndGet));
      assertEquals(0, releases.get());
      server.start();
      assertEquals(503, get(server, "/actuator/health").statusCode());
      assertThrows(IllegalStateException.class, server::start);
      assertThrows(NullPointerException.class, () -> server.closeWithin(null));
      assertThrows(IllegalArgumentException.class, () -> server.closeWithin(Duration.ofNanos(-1)));
      assertThrows(
          IllegalArgumentException.class, () -> server.closeWithin(Duration.ofSeconds(31)));
      server.close();
      assertThrows(IllegalStateException.class, server::start);
    } finally {
      server.close();
    }
  }

  @Test
  void ready003ActualVendorStartedServerFailureClosesBoundOwner() throws Exception {
    var bound = new AtomicInteger();
    var captured =
        new java.util.concurrent.atomic.AtomicReference<com.sun.net.httpserver.HttpServer>();
    try {
      assertThrows(
          IllegalStateException.class,
          () ->
              WebManagementServer.open(
                  INFO,
                  () -> true,
                  0,
                  (address, backlog) -> {
                    assertEquals("127.0.0.1", address.getAddress().getHostAddress());
                    assertEquals(32, backlog);
                    var actual = com.sun.net.httpserver.HttpServer.create(address, backlog);
                    captured.set(actual);
                    bound.set(actual.getAddress().getPort());
                    actual.start();
                    return actual;
                  }));
      assertTrue(bound.get() > 0);
      try (var reopened = WebManagementServer.open(INFO, () -> true, bound.get())) {
        assertEquals(503, get(reopened, "/actuator/health").statusCode());
      }
      assertThrows(
          NullPointerException.class, () -> WebManagementServer.open(INFO, () -> true, 0, null));
      assertThrows(
          NullPointerException.class,
          () -> WebManagementServer.open(INFO, () -> true, 0, (a, b) -> null));
    } finally {
      var actual = captured.get();
      if (actual != null) actual.stop(0);
    }
  }

  private static final Map<String, String> INFO =
      Map.of(
          "commit",
          "a".repeat(40),
          "app",
          "0.1.0",
          "config",
          "1",
          "schema",
          "027",
          "protocol",
          "001");
  private static final HttpClient CLIENT =
      HttpClient.newBuilder().connectTimeout(Duration.ofSeconds(3)).build();

  private static HttpResponse<String> get(WebManagementServer server, String path)
      throws Exception {
    return CLIENT.send(
        HttpRequest.newBuilder(URI.create("http://127.0.0.1:" + server.port() + path))
            .timeout(Duration.ofSeconds(3))
            .GET()
            .build(),
        HttpResponse.BodyHandlers.ofString());
  }

  @Test
  void ready001ActualDownUpDownPublicOnlyAndClosedRoutes() throws Exception {
    var healthy = new AtomicBoolean(true);
    var releases = new AtomicInteger();
    var server = WebManagementServer.open(INFO, healthy::get, 0);
    try {
      assertFalse(server.ready());
      for (String path : new String[] {"/actuator/health", "/actuator/health/readiness"}) {
        var down = get(server, path);
        assertEquals(503, down.statusCode());
        assertEquals("{\"status\":\"DOWN\"}", down.body());
        assertEquals("no-store", down.headers().firstValue("Cache-Control").orElseThrow());
      }
      assertEquals(
          "# TYPE schubert_nk_web_ready gauge\nschubert_nk_web_ready 0\n",
          get(server, "/actuator/prometheus").body());
      var info = get(server, "/actuator/info");
      assertEquals(200, info.statusCode());
      assertEquals(
          "{\"commit\":\""
              + "a".repeat(40)
              + "\",\"app\":\"0.1.0\",\"config\":\"1\",\"schema\":\"027\",\"protocol\":\"001\"}",
          info.body());
      for (String path :
          new String[] {
            "/", "/actuator/env", "/actuator/health/extra", "/actuator/%69nfo", "/actuator/shutdown"
          }) assertEquals(404, get(server, path).statusCode());
      var post =
          CLIENT.send(
              HttpRequest.newBuilder(
                      URI.create("http://127.0.0.1:" + server.port() + "/actuator/info"))
                  .timeout(Duration.ofSeconds(3))
                  .POST(HttpRequest.BodyPublishers.noBody())
                  .build(),
              HttpResponse.BodyHandlers.ofString());
      assertEquals(405, post.statusCode());
      server.promote(
          () -> {
            assertFalse(server.ready());
            releases.incrementAndGet();
          });
      assertTrue(server.ready());
      assertEquals(1, releases.get());
      assertEquals(200, get(server, "/actuator/health/readiness").statusCode());
      assertEquals("{\"status\":\"UP\"}", get(server, "/actuator/health").body());
      assertEquals(
          "# TYPE schubert_nk_web_ready gauge\nschubert_nk_web_ready 1\n",
          get(server, "/actuator/prometheus").body());
      assertThrows(IOException.class, () -> server.promote(releases::incrementAndGet));
      healthy.set(false);
      assertFalse(server.ready());
      assertEquals(503, get(server, "/actuator/health").statusCode());
      server.close();
      server.close();
      assertFalse(server.ready());
      assertThrows(IOException.class, () -> server.promote(releases::incrementAndGet));
      assertEquals(1, releases.get());
    } finally {
      server.close();
    }
  }

  @Test
  void ready002HandoffFailureAndConcurrentStopNeverPromote() throws Exception {
    for (int mode = 0; mode < 3; mode++) {
      var healthy = new AtomicBoolean(mode != 0);
      int selected = mode;
      var releases = new AtomicInteger();
      try (var server = WebManagementServer.open(INFO, healthy::get, 0)) {
        assertThrows(
            IOException.class,
            () ->
                server.promote(
                    () -> {
                      releases.incrementAndGet();
                      if (selected == 1) throw new IOException("PRIVATE");
                      healthy.set(false);
                    }));
        assertEquals(mode == 0 ? 0 : 1, releases.get());
        assertFalse(server.ready());
        assertEquals(503, get(server, "/actuator/health/readiness").statusCode());
        healthy.set(true);
        assertThrows(IOException.class, () -> server.promote(releases::incrementAndGet));
      }
    }
  }

  @Test
  void ready004OwnerClosedDuringAdmissionReleaseCannotPublishUp() throws Exception {
    var releases = new AtomicInteger();
    var server = WebManagementServer.open(INFO, () -> true, 0);
    int port = server.port();
    try {
      assertThrows(
          IOException.class,
          () ->
              server.promote(
                  () -> {
                    releases.incrementAndGet();
                    server.close();
                  }));
      assertEquals(1, releases.get());
      assertFalse(server.ready());
      assertThrows(IOException.class, () -> server.promote(releases::incrementAndGet));
      assertEquals(1, releases.get());
      try (var replacement = WebManagementServer.open(INFO, () -> true, port)) {
        assertEquals(503, get(replacement, "/actuator/health/readiness").statusCode());
        assertEquals("{\"status\":\"DOWN\"}", get(replacement, "/actuator/health").body());
      }
    } finally {
      server.close();
    }
  }

  @Test
  void ready003InformationNullUnknownInvalidAndRealBindCollision() throws Exception {
    assertThrows(NullPointerException.class, () -> WebManagementServer.open(null, () -> true, 0));
    assertThrows(NullPointerException.class, () -> WebManagementServer.open(INFO, null, 0));
    assertThrows(
        IllegalArgumentException.class, () -> WebManagementServer.open(Map.of(), () -> true, 0));
    for (String value : new String[] {"", "PRIVATE\"", "a".repeat(129), "x".repeat(40)}) {
      var bad = new HashMap<>(INFO);
      bad.put(value.length() == 40 ? "commit" : "app", value);
      assertThrows(
          IllegalArgumentException.class, () -> WebManagementServer.open(bad, () -> true, 0));
    }
    var missing = new HashMap<>(INFO);
    missing.put("app", null);
    assertThrows(
        NullPointerException.class, () -> WebManagementServer.open(missing, () -> true, 0));
    missing.put("app", "1");
    missing.put("commit", null);
    assertThrows(
        NullPointerException.class, () -> WebManagementServer.open(missing, () -> true, 0));
    try (var server = WebManagementServer.open(INFO, () -> true)) {
      assertEquals(8081, server.port());
      assertThrows(
          IOException.class, () -> WebManagementServer.open(INFO, () -> true, server.port()));
      assertThrows(NullPointerException.class, () -> server.promote(null));
    }
  }
}
