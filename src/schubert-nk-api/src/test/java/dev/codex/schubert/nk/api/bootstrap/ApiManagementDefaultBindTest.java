package dev.codex.schubert.nk.api.bootstrap;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.net.InetSocketAddress;
import java.net.ServerSocket;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;
import java.util.Map;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.Test;

/** SS342/SSC158312313; PT-API-MGMT-NORM-001. Owned loopback only, never native admission. */
final class ApiManagementDefaultBindTest {
  @Test
  void apiMgmt001DefaultBindUsesFixedLoopbackAndOwnedReadinessLifecycle() throws Exception {
    var information =
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
    var releases = new AtomicInteger();
    try (var client = HttpClient.newBuilder().connectTimeout(Duration.ofSeconds(3)).build()) {
      var owner = ApiManagementServer.bind(information, () -> true);
      try (owner) {
        owner.start();
        assertEquals(8091, owner.port());
        assertFalse(owner.ready());
        var down = get(client, "/actuator/health/readiness");
        assertEquals(503, down.statusCode());
        assertEquals("{\"status\":\"DOWN\"}", down.body());
        assertEquals("no-store", down.headers().firstValue("Cache-Control").orElseThrow());
        owner.promote(releases::incrementAndGet);
        assertEquals(1, releases.get());
        assertTrue(owner.ready());
        var up = get(client, "/actuator/health");
        assertEquals(200, up.statusCode());
        assertEquals("{\"status\":\"UP\"}", up.body());
        var info = get(client, "/actuator/info");
        assertEquals(200, info.statusCode());
        assertEquals(
            "{\"commit\":\""
                + "7".repeat(40)
                + "\",\"app\":\"0.1.0\",\"config\":\"1\",\"schema\":\"025\",\"protocol\":\"001\"}",
            info.body());
      }
      assertFalse(owner.ready());
      owner.close();
      assertEquals(1, releases.get());
      try (var released = new ServerSocket()) {
        released.setReuseAddress(true);
        released.bind(new InetSocketAddress("127.0.0.1", 8091));
        assertEquals(8091, released.getLocalPort());
      }
    }
  }

  private static HttpResponse<String> get(HttpClient client, String path) throws Exception {
    return client.send(
        HttpRequest.newBuilder(URI.create("http://127.0.0.1:8091" + path))
            .timeout(Duration.ofSeconds(3))
            .GET()
            .build(),
        HttpResponse.BodyHandlers.ofString());
  }
}
