package dev.codex.schubert.nk.api.bootstrap;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

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

/** Independent actual HTTP status/JSON literals, not a native startup admission. READY001..003. */
final class ApiManagementServerTest {
  private static final String FIXTURE_SYNTHETIC_ACQUISITION_5736B45C = "synthetic acquisition";
  private static final String FIXTURE_ACTUATOR_HEALTH_286D1BF0 = "/actuator/health";
  private static final String FIXTURE_APP_4E5EF144 = "app";
  private static final String FIXTURE_ACTUATOR_HEALTH_READINESS_5BC040D5 =
      "/actuator/health/readiness";

  /** SS342/SSC312/PG-D461/PT-HTTP-OWN001: acquisition failure never becomes an owner. */
  @Test
  void httpOwn001FactoryFailureIdentityAndNullAreNotStarted() {
    for (Throwable primary :
        java.util.List.of(
            new IOException(FIXTURE_SYNTHETIC_ACQUISITION_5736B45C),
            new IllegalArgumentException(FIXTURE_SYNTHETIC_ACQUISITION_5736B45C),
            new IllegalStateException(FIXTURE_SYNTHETIC_ACQUISITION_5736B45C),
            new NullPointerException(FIXTURE_SYNTHETIC_ACQUISITION_5736B45C),
            new AssertionError(FIXTURE_SYNTHETIC_ACQUISITION_5736B45C))) {
      var calls = new AtomicInteger();
      assertSame(
          primary,
          assertThrows(
              primary.getClass(),
              () ->
                  ApiManagementServer.open(
                      INFO,
                      () -> true,
                      0,
                      (address, backlog) -> {
                        assertEquals(1, calls.incrementAndGet());
                        assertEquals("127.0.0.1", address.getAddress().getHostAddress());
                        assertEquals(0, address.getPort());
                        assertEquals(32, backlog);
                        if (primary instanceof IOException checked) throw checked;
                        if (primary instanceof RuntimeException unchecked) throw unchecked;
                        throw (Error) primary;
                      })));
      assertEquals(1, calls.get());
    }
    var nullCalls = new AtomicInteger();
    assertEquals(
        "management server",
        assertThrows(
                NullPointerException.class,
                () ->
                    ApiManagementServer.open(
                        INFO,
                        () -> true,
                        0,
                        (address, backlog) -> {
                          nullCalls.incrementAndGet();
                          return null;
                        }))
            .getMessage());
    assertEquals(1, nullCalls.get());
  }

  @Test
  void ready005JdkStopMustPreserveCallerInterruptFlag() throws Exception {
    var server = ApiManagementServer.open(INFO, () -> true, 0);
    try {
      assertEquals(503, get(server, FIXTURE_ACTUATOR_HEALTH_286D1BF0).statusCode());
      Thread.currentThread().interrupt();
      server.close();
      assertTrue(Thread.currentThread().isInterrupted());
      assertFalse(server.ready());
    } finally {
      Thread.interrupted();
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
              ApiManagementServer.open(
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
      try (var reopened = ApiManagementServer.open(INFO, () -> true, bound.get())) {
        assertEquals(503, get(reopened, FIXTURE_ACTUATOR_HEALTH_286D1BF0).statusCode());
      }
      assertThrows(
          NullPointerException.class, () -> ApiManagementServer.open(INFO, () -> true, 0, null));
      assertThrows(
          NullPointerException.class,
          () -> ApiManagementServer.open(INFO, () -> true, 0, (a, b) -> null));
    } finally {
      var actual = captured.get();
      if (actual != null) actual.stop(0);
    }
  }

  private static final Map<String, String> INFO =
      Map.of(
          "commit",
          "a".repeat(40),
          FIXTURE_APP_4E5EF144,
          "0.1.0",
          "config",
          "1",
          "schema",
          "025",
          "protocol",
          "001");
  private static final HttpClient CLIENT =
      HttpClient.newBuilder().connectTimeout(Duration.ofSeconds(3)).build();

  private static HttpResponse<String> get(ApiManagementServer server, String path)
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
    var server = ApiManagementServer.open(INFO, healthy::get, 0);
    try {
      assertFalse(server.ready());
      for (String path :
          new String[] {
            FIXTURE_ACTUATOR_HEALTH_286D1BF0, FIXTURE_ACTUATOR_HEALTH_READINESS_5BC040D5
          }) {
        var down = get(server, path);
        assertEquals(503, down.statusCode());
        assertEquals("{\"status\":\"DOWN\"}", down.body());
        assertEquals("no-store", down.headers().firstValue("Cache-Control").orElseThrow());
      }
      assertEquals(
          "# TYPE schubert_nk_api_ready gauge\nschubert_nk_api_ready 0\n",
          get(server, "/actuator/prometheus").body());
      var info = get(server, "/actuator/info");
      assertEquals(200, info.statusCode());
      assertEquals(
          "{\"commit\":\""
              + "a".repeat(40)
              + "\",\"app\":\"0.1.0\",\"config\":\"1\",\"schema\":\"025\",\"protocol\":\"001\"}",
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
      assertEquals(200, get(server, FIXTURE_ACTUATOR_HEALTH_READINESS_5BC040D5).statusCode());
      assertEquals("{\"status\":\"UP\"}", get(server, FIXTURE_ACTUATOR_HEALTH_286D1BF0).body());
      assertEquals(
          "# TYPE schubert_nk_api_ready gauge\nschubert_nk_api_ready 1\n",
          get(server, "/actuator/prometheus").body());
      assertThrows(IOException.class, () -> server.promote(releases::incrementAndGet));
      healthy.set(false);
      assertFalse(server.ready());
      assertEquals(503, get(server, FIXTURE_ACTUATOR_HEALTH_286D1BF0).statusCode());
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
      try (var server = ApiManagementServer.open(INFO, healthy::get, 0)) {
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
        assertEquals(503, get(server, FIXTURE_ACTUATOR_HEALTH_READINESS_5BC040D5).statusCode());
        healthy.set(true);
        assertThrows(IOException.class, () -> server.promote(releases::incrementAndGet));
      }
    }
  }

  @Test
  void ready004OwnerClosedDuringAdmissionReleaseCannotPublishUp() throws Exception {
    var releases = new AtomicInteger();
    var server = ApiManagementServer.open(INFO, () -> true, 0);
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
      try (var replacement = ApiManagementServer.open(INFO, () -> true, port)) {
        assertEquals(
            503, get(replacement, FIXTURE_ACTUATOR_HEALTH_READINESS_5BC040D5).statusCode());
        assertEquals(
            "{\"status\":\"DOWN\"}", get(replacement, FIXTURE_ACTUATOR_HEALTH_286D1BF0).body());
      }
    } finally {
      server.close();
    }
  }

  @Test
  void ready003InformationNullUnknownInvalidAndRealBindCollision() throws Exception {
    assertThrows(NullPointerException.class, () -> ApiManagementServer.open(null, () -> true, 0));
    assertThrows(NullPointerException.class, () -> ApiManagementServer.open(INFO, null, 0));
    assertThrows(
        IllegalArgumentException.class, () -> ApiManagementServer.open(Map.of(), () -> true, 0));
    for (String value : new String[] {"", "PRIVATE\"", "a".repeat(129), "x".repeat(40)}) {
      var bad = new HashMap<>(INFO);
      bad.put(value.length() == 40 ? "commit" : FIXTURE_APP_4E5EF144, value);
      assertThrows(
          IllegalArgumentException.class, () -> ApiManagementServer.open(bad, () -> true, 0));
    }
    var missing = new HashMap<>(INFO);
    missing.put(FIXTURE_APP_4E5EF144, null);
    assertThrows(
        NullPointerException.class, () -> ApiManagementServer.open(missing, () -> true, 0));
    missing.put(FIXTURE_APP_4E5EF144, "1");
    missing.put("commit", null);
    assertThrows(
        NullPointerException.class, () -> ApiManagementServer.open(missing, () -> true, 0));
    try (var server = ApiManagementServer.open(INFO, () -> true)) {
      assertEquals(8091, server.port());
      assertThrows(
          IOException.class, () -> ApiManagementServer.open(INFO, () -> true, server.port()));
      assertThrows(NullPointerException.class, () -> server.promote(null));
    }
  }
}
