package dev.codex.schubert.nk.web.bootstrap;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import jakarta.servlet.AsyncContext;
import jakarta.servlet.http.HttpServletRequest;
import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.file.Path;
import java.time.Duration;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicReference;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** Independent ownership counts and real Tomcat/ASYNC terminal, NATIVE-STOP001..003. */
final class WebHttpAdmissionTest {
  private static final String FIXTURE_LOGIN_F843C044 = "/login";
  @TempDir Path root;

  @Test
  void stop005OwnerTermRefusesImmediatelyWithoutWaitingForOwnerPolling() throws Exception {
    assertThrows(NullPointerException.class, () -> new WebHttpAdmission(null));
    var stopping = new java.util.concurrent.atomic.AtomicBoolean();
    var gate = new WebHttpAdmission(stopping::get);
    gate.admit();
    assertTrue(gate.accepting());
    assertTrue(gate.acquire());
    stopping.set(true);
    assertFalse(gate.accepting());
    assertFalse(gate.acquire());
    gate.completed();
    gate.drain(Duration.ZERO);
    var stoppedBeforeReady = new WebHttpAdmission(() -> true);
    assertThrows(IOException.class, stoppedBeforeReady::admit);
    assertFalse(stoppedBeforeReady.accepting());
    assertFalse(stoppedBeforeReady.acquire());
  }

  @Test
  void stop001002BoundaryInterruptAndConcurrentCompletion() throws Exception {
    var gate = new WebHttpAdmission();
    assertFalse(gate.accepting());
    assertFalse(gate.acquire());
    assertThrows(IllegalStateException.class, gate::completed);
    assertThrows(NullPointerException.class, () -> gate.drain(null));
    assertThrows(IllegalArgumentException.class, () -> gate.drain(Duration.ofNanos(-1)));
    assertThrows(IllegalArgumentException.class, () -> gate.drain(Duration.ofSeconds(31)));
    gate.admit();
    assertTrue(gate.accepting());
    assertThrows(IOException.class, gate::admit);
    assertTrue(gate.acquire());
    assertTrue(gate.acquire());
    gate.refuse();
    assertFalse(gate.acquire());
    assertFalse(gate.accepting());
    assertThrows(IOException.class, () -> gate.drain(Duration.ZERO));
    Thread.currentThread().interrupt();
    try {
      assertThrows(IOException.class, () -> gate.drain(Duration.ofSeconds(1)));
      assertTrue(Thread.currentThread().isInterrupted());
    } finally {
      assertTrue(Thread.interrupted());
    }
    gate.completed();
    try (var executor = Executors.newSingleThreadExecutor()) {
      var waiting =
          executor.submit(
              () -> {
                gate.drain(Duration.ofSeconds(3));
                return true;
              });
      gate.completed();
      assertTrue(waiting.get(3, TimeUnit.SECONDS));
    }
    gate.drain(Duration.ZERO);
    gate.refuse();
    assertThrows(IOException.class, gate::admit);
    var empty = new WebHttpAdmission();
    empty.drain(Duration.ZERO);
    assertThrows(IOException.class, empty::admit);
  }

  @Test
  void stop003ActualAsyncRemainsOwnedAfterServletReturns() throws Exception {
    var gate = new WebHttpAdmission();
    var async = new AtomicReference<AsyncContext>();
    var entered = new CountDownLatch(1);
    var server =
        WebHttpServer.start(
            root,
            0,
            (request, response, chain) -> {
              if (((HttpServletRequest) request).getRequestURI().equals("/test/async")) {
                var context = request.startAsync();
                context.setTimeout(10_000);
                async.set(context);
                entered.countDown();
              } else chain.doFilter(request, response);
            },
            Map.of(WebHttpAdmission.class, gate));
    try (var client = HttpClient.newBuilder().connectTimeout(Duration.ofSeconds(3)).build()) {
      String base = "http://127.0.0.1:" + server.port();
      assertEquals(Set.of("/", FIXTURE_LOGIN_F843C044, "/error"), server.mappedPaths());
      assertEquals(503, get(client, base + FIXTURE_LOGIN_F843C044).statusCode());
      gate.admit();
      assertEquals(200, get(client, base + FIXTURE_LOGIN_F843C044).statusCode());
      var waiting =
          client.sendAsync(
              HttpRequest.newBuilder(URI.create(base + "/test/async"))
                  .timeout(Duration.ofSeconds(5))
                  .build(),
              HttpResponse.BodyHandlers.ofString());
      assertTrue(entered.await(3, TimeUnit.SECONDS));
      gate.refuse();
      assertEquals(503, get(client, base + FIXTURE_LOGIN_F843C044).statusCode());
      assertThrows(IOException.class, () -> gate.drain(Duration.ZERO));
      var owned = async.get();
      assertNotNull(owned);
      owned
          .getResponse()
          .getOutputStream()
          .write("done".getBytes(java.nio.charset.StandardCharsets.UTF_8));
      owned.complete();
      var result = waiting.get(3, TimeUnit.SECONDS);
      assertEquals(200, result.statusCode());
      assertEquals("done", result.body());
      gate.drain(Duration.ofSeconds(3));
      server.close();
      assertThrows(IllegalStateException.class, server::mappedPaths);
      assertThrows(IllegalStateException.class, server::port);
    } finally {
      var owned = async.get();
      if (owned != null) {
        try {
          owned.complete();
        } catch (IllegalStateException completed) {
          /* Already complete. */
        }
      }
      server.close();
    }
  }

  private static HttpResponse<String> get(HttpClient client, String uri) throws Exception {
    return client.send(
        HttpRequest.newBuilder(URI.create(uri)).timeout(Duration.ofSeconds(3)).build(),
        HttpResponse.BodyHandlers.ofString());
  }
}
