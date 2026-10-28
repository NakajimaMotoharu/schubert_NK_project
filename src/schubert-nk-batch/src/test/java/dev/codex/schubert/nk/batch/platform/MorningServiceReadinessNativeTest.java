package dev.codex.schubert.nk.batch.platform;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.sun.net.httpserver.HttpServer;
import java.io.IOException;
import java.net.InetSocketAddress;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/**
 * READY428010..012: actual host proc/owned sockets/HTTP, component only, not native Main
 * acceptance.
 */
final class MorningServiceReadinessNativeTest {
  private static final String FIXTURE_ACTUATOR_INFO_37B10116 = "/actuator/info";
  @TempDir Path directory;

  @Test
  void native428010RealOwnedFixedLoopbackListenerAndBoundedHttp() throws Exception {
    var io = new MorningServiceReadiness.NativeIo(ProcessHandle.current().pid(), 8091);
    assertTrue(new String(io.status(), StandardCharsets.US_ASCII).contains("Uid:"));
    assertTrue(io.command().length > 0);
    var code = new AtomicInteger(200);
    var body = new java.util.concurrent.atomic.AtomicReference<>("{\"status\":\"UP\"}");
    var server = HttpServer.create(new InetSocketAddress("127.0.0.1", 8091), 0);
    server.createContext(
        "/",
        exchange -> {
          try (exchange) {
            byte[] bytes = body.get().getBytes(StandardCharsets.US_ASCII);
            exchange.sendResponseHeaders(code.get(), bytes.length);
            exchange.getResponseBody().write(bytes);
          }
        });
    try {
      server.start();
      assertFalse(io.sockets().isEmpty());
      var actual = io.get("/actuator/health/readiness");
      assertEquals(200, actual.status());
      assertEquals("{\"status\":\"UP\"}", actual.body());
      body.set("{\"commit\":\"golden\"}");
      assertEquals(body.get(), io.get(FIXTURE_ACTUATOR_INFO_37B10116).body());
      code.set(503);
      assertEquals(
          new MorningServiceReadiness.Response(503, ""), io.get(FIXTURE_ACTUATOR_INFO_37B10116));
      code.set(302);
      assertEquals(302, io.get(FIXTURE_ACTUATOR_INFO_37B10116).status());
      code.set(200);
      body.set("x".repeat(4097));
      assertThrows(IOException.class, () -> io.get(FIXTURE_ACTUATOR_INFO_37B10116));
      body.set("\0");
      assertThrows(IOException.class, () -> io.get(FIXTURE_ACTUATOR_INFO_37B10116));
      assertThrows(IllegalArgumentException.class, () -> io.get("/wrong"));
    } finally {
      server.stop(0);
    }
    assertThrows(IOException.class, () -> io.get(FIXTURE_ACTUATOR_INFO_37B10116));
  }

  @Test
  void native428011NoFollowAndByteLimitCloseBeforeFailure() throws Exception {
    var file = directory.resolve("literal");
    Files.write(file, new byte[] {1, 2, 3});
    assertArrayEquals(new byte[] {1, 2, 3}, MorningServiceReadiness.NativeIo.read(file, 3));
    assertThrows(IOException.class, () -> MorningServiceReadiness.NativeIo.read(file, 2));
    var link = directory.resolve("link");
    Files.createSymbolicLink(link, file);
    assertThrows(IOException.class, () -> MorningServiceReadiness.NativeIo.read(link, 3));
    Files.delete(file);
    assertThrows(IOException.class, () -> MorningServiceReadiness.NativeIo.read(file, 3));
  }

  @Test
  void native428012ValidatedPidAndOnlyTwoFixedPorts() throws Exception {
    for (long pid : new long[] {0, 1, -1, 2147483648L})
      assertThrows(
          IllegalArgumentException.class, () -> new MorningServiceReadiness.NativeIo(pid, 8091));
    assertThrows(
        IllegalArgumentException.class, () -> new MorningServiceReadiness.NativeIo(2, 8080));
    assertNotNull(new MorningServiceReadiness.NativeIo(2, 8081));
    var f = new RootStartupContextTest.LaunchFixture();
    var root = f.context();
    var morning = root.capture(RootStartupContext.Service.MORNING);
    assertThrows(
        IllegalArgumentException.class,
        () ->
            MorningServiceReadiness.create(
                root, morning, morning, MorningServiceReadinessTest.INFO));
  }
}
