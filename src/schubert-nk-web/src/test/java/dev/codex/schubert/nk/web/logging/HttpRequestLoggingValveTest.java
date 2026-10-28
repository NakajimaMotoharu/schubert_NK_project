package dev.codex.schubert.nk.web.logging;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.web.bootstrap.WebHttpServer;
import dev.codex.schubert.nk.web.security.CaddyClientAddressResolver;
import dev.codex.schubert.nk.web.security.CaddyTransportContextFilter;
import dev.codex.schubert.nk.web.security.WebRequestContext;
import jakarta.servlet.AsyncEvent;
import jakarta.servlet.AsyncListener;
import jakarta.servlet.Filter;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.net.Socket;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;
import java.nio.file.Path;
import java.sql.SQLException;
import java.time.Duration;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import org.apache.catalina.connector.Connector;
import org.apache.catalina.connector.Request;
import org.apache.catalina.connector.Response;
import org.apache.catalina.valves.ValveBase;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** Native terminal HTTP observations, not synthetic Servlet-finally success; REQ001..006/016. */
final class HttpRequestLoggingValveTest {
  private static final String FIXTURE_GET_04F32A7E = "GET";
  private static final String FIXTURE_LOGIN_F843C044 = "/login";
  private static final String FIXTURE_POST_E46D3AE9 = "POST";
  private static final String FIXTURE_STATUS_CFC31BCC = "status";
  private static final String FIXTURE_PATH_D070C7EC = "path";
  private static final String FIXTURE_DETAILS_521BCB5E = "details";
  private static final String FIXTURE_RESPONSEBYTES_0785275F = "responseBytes";
  private static WebLogDatabaseFixture db;
  @TempDir Path root;

  @BeforeAll
  static void start(@TempDir Path root) throws Exception {
    db = new WebLogDatabaseFixture(root);
  }

  @AfterAll
  static void stop() throws Exception {
    if (db != null) db.stop();
  }

  @BeforeEach
  void reset() throws Exception {
    db.reset();
  }

  @Test
  void req001002004006RealGetHeadRedirectErrorAndUntrustedPeer() throws Exception {
    try (var fixture =
            new WebRequestLogProducerTest.Fixture(WebRequestLogProducerTest.source(db::web));
        var server =
            WebHttpServer.start(
                root, 0, filter(), Map.of(WebRequestLogProducer.class, fixture.producer));
        var client = HttpClient.newBuilder().connectTimeout(Duration.ofSeconds(3)).build()) {
      int port = server.port();
      var login =
          send(client, port, FIXTURE_GET_04F32A7E, "/login?password=synthetic-secret-canary", true);
      assertEquals(200, login.statusCode());
      assertTrue(login.body().contains("schubert NK"));
      var head = send(client, port, "HEAD", FIXTURE_LOGIN_F843C044, true);
      assertEquals(200, head.statusCode());
      assertEquals("", head.body());
      var redirect = send(client, port, FIXTURE_POST_E46D3AE9, "/login?case=redirect", true);
      assertEquals(302, redirect.statusCode());
      assertEquals("/", redirect.headers().firstValue("Location").orElseThrow());
      var rejected = send(client, port, FIXTURE_POST_E46D3AE9, "/login?case=rejected", true);
      assertEquals(403, rejected.statusCode());
      var error = send(client, port, FIXTURE_POST_E46D3AE9, "/login?case=error", true);
      assertEquals(500, error.statusCode());
      var missing =
          send(
              client,
              port,
              FIXTURE_GET_04F32A7E,
              "/private-canary?token=synthetic-secret-canary",
              true);
      assertEquals(404, missing.statusCode());
      var untrusted =
          send(client, port, FIXTURE_GET_04F32A7E, "/login?cookie=synthetic-secret-canary", false);
      assertEquals(403, untrusted.statusCode());
      awaitEntries(
          fixture, 8); // Six trusted REQUEST, then PENDING/FAILED for untrusted IP absence.
      int[] statuses = {200, 200, 302, 403, 500, 404, 403, 403};
      var ids = new HashSet<String>();
      for (int i = 0; i < 8; i++) {
        var json = fixture.logger.entries.get(i).json();
        assertEquals(statuses[i], json.get(FIXTURE_STATUS_CFC31BCC).getAsInt());
        assertEquals(
            i >= 5 ? "/**" : FIXTURE_LOGIN_F843C044, json.get(FIXTURE_PATH_D070C7EC).getAsString());
        assertTrue(json.get("elapsedMs").getAsLong() >= 0);
        assertFalse(json.toString().contains("canary"));
        assertFalse(json.toString().contains("case="));
        assertEquals(json.get("messageId"), json.get("correlationId"));
        if (i < 7) assertTrue(ids.add(json.get("messageId").getAsString()));
      }
      assertEquals(
          login.body().getBytes(StandardCharsets.UTF_8).length,
          fixture
              .logger
              .entries
              .getFirst()
              .json()
              .getAsJsonObject(FIXTURE_DETAILS_521BCB5E)
              .get(FIXTURE_RESPONSEBYTES_0785275F)
              .getAsLong());
      assertEquals(
          0,
          fixture
              .logger
              .entries
              .get(1)
              .json()
              .getAsJsonObject(FIXTURE_DETAILS_521BCB5E)
              .get(FIXTURE_RESPONSEBYTES_0785275F)
              .getAsLong());
      assertEquals(6, count());
      assertEquals(
          "FAILED",
          fixture
              .logger
              .entries
              .getLast()
              .json()
              .getAsJsonObject(FIXTURE_DETAILS_521BCB5E)
              .get("projectionStatus")
              .getAsString());
      // No producer-owned JDBC/JMS/key close: caller can still decrypt/query after HTTP owner
      // closes.
    }
  }

  @Test
  void req003AsyncCompletionAndTwoDispatchCyclesHaveOneTerminalObservation() throws Exception {
    try (var fixture =
            new WebRequestLogProducerTest.Fixture(WebRequestLogProducerTest.source(db::web));
        var server =
            WebHttpServer.start(
                root, 0, filter(), Map.of(WebRequestLogProducer.class, fixture.producer));
        var client = HttpClient.newBuilder().connectTimeout(Duration.ofSeconds(3)).build()) {
      var response = send(client, server.port(), FIXTURE_POST_E46D3AE9, "/login?case=async", true);
      assertEquals(202, response.statusCode());
      assertEquals("完了", response.body());
      awaitEntries(fixture, 1);
      assertEquals(
          202, fixture.logger.entries.getFirst().json().get(FIXTURE_STATUS_CFC31BCC).getAsInt());
      assertEquals(
          6,
          fixture
              .logger
              .entries
              .getFirst()
              .json()
              .getAsJsonObject(FIXTURE_DETAILS_521BCB5E)
              .get(FIXTURE_RESPONSEBYTES_0785275F)
              .getAsLong());
      var redispatch =
          send(client, server.port(), FIXTURE_GET_04F32A7E, "/login?case=dispatch", true);
      assertEquals(200, redispatch.statusCode());
      assertTrue(redispatch.body().contains("schubert NK"));
      awaitEntries(fixture, 2);
      assertEquals(2, count());
      assertEquals(
          FIXTURE_LOGIN_F843C044,
          fixture.logger.entries.getLast().json().get(FIXTURE_PATH_D070C7EC).getAsString());
      assertEquals(2, fixture.logger.entries.size());
    }
  }

  @Test
  void req005NativeMalformedCallbacksDuplicateAndOverrideContract() throws Exception {
    try (var fixture =
        new WebRequestLogProducerTest.Fixture(WebRequestLogProducerTest.source(db::web))) {
      var valve = new HttpRequestLoggingValve(fixture.producer);
      assertThrows(NullPointerException.class, () -> new HttpRequestLoggingValve(null));
      assertFalse(valve.getRequestAttributesEnabled());
      valve.setRequestAttributesEnabled(false);
      assertThrows(IllegalArgumentException.class, () -> valve.setRequestAttributesEnabled(true));
      var coyote = new org.apache.coyote.Request();
      var request = new Request(new Connector(), coyote);
      var response = new Response(new org.apache.coyote.Response());
      valve.log(null, null, 0);
      valve.log(request, null, 0);
      valve.log(request, response, 0);
      var trace = WebRequestTrace.ensure(request, UUID::randomUUID);
      valve.log(request, response, 0); // Null method, still UNKNOWN, not completion-claimed.
      request.setAttribute(WebRequestTrace.class.getName(), "wrong-trace");
      valve.log(request, response, 0);
      request.setAttribute(WebRequestTrace.class.getName(), trace);
      coyote.setMethod(FIXTURE_GET_04F32A7E);
      request.setAttribute(WebRequestContext.class.getName(), "wrong-context");
      valve.log(request, response, 0);
      assertEquals(6, fixture.logger.entries.size());
      for (var entry : fixture.logger.entries) {
        assertEquals("UNKNOWN", entry.json().get("outcome").getAsString());
        assertFalse(entry.json().has(FIXTURE_STATUS_CFC31BCC));
      }
      valve.log(request, response, 0);
      assertEquals(6, fixture.logger.entries.size()); // Already claimed.
      assertEquals(0, count());
      assertThrows(NullPointerException.class, () -> valve.invoke(null, response));
      assertThrows(NullPointerException.class, () -> valve.invoke(request, null));
    }
  }

  @Test
  void req008InvocationFailureReleasesLexicalCorrelationAndPostRouteOnlyIsFixed() throws Exception {
    try (var fixture =
        new WebRequestLogProducerTest.Fixture(WebRequestLogProducerTest.source(db::web))) {
      var valve = new HttpRequestLoggingValve(fixture.producer);
      var coyote = new org.apache.coyote.Request();
      coyote.setMethod(FIXTURE_POST_E46D3AE9);
      coyote.requestURI().setString(FIXTURE_LOGIN_F843C044);
      var request = new Request(new Connector(), coyote);
      var response = new Response(new org.apache.coyote.Response());
      var firstMessage = new UUID(2, 88);
      valve.setNext(
          new ValveBase(true) {
            @Override
            public void invoke(Request req, Response res) throws IOException {
              WebRequestTrace.businessIdentifiers(() -> firstMessage).get();
              throw new IOException("synthetic IO");
            }
          });
      assertThrows(IOException.class, () -> valve.invoke(request, response));
      var trace = WebRequestTrace.existing(request).orElseThrow();
      assertEquals(FIXTURE_LOGIN_F843C044, trace.route());
      assertEquals(firstMessage, trace.correlationId());
      WebRequestTrace.businessIdentifiers(() -> new UUID(2, 89)).get();
      assertEquals(firstMessage, trace.correlationId());
      coyote.setMethod(FIXTURE_POST_E46D3AE9);
      coyote.requestURI().setString("/not-login");
      var other = new Request(new Connector(), coyote);
      valve.setNext(null);
      assertThrows(NullPointerException.class, () -> valve.invoke(other, response));
      assertEquals("/**", WebRequestTrace.existing(other).orElseThrow().route());
    }
  }

  @Test
  void req003ActualAsyncTimeoutAndErrorCompleteWithFinal503OnlyOnce() throws Exception {
    try (var fixture =
            new WebRequestLogProducerTest.Fixture(WebRequestLogProducerTest.source(db::web));
        var server =
            WebHttpServer.start(
                root, 0, filter(), Map.of(WebRequestLogProducer.class, fixture.producer));
        var client = HttpClient.newBuilder().connectTimeout(Duration.ofSeconds(3)).build()) {
      for (String mode : List.of("timeout", "async-error")) {
        var response =
            send(client, server.port(), FIXTURE_POST_E46D3AE9, "/login?case=" + mode, true);
        assertEquals(503, response.statusCode());
        assertEquals("", response.body());
      }
      awaitEntries(fixture, 2);
      assertEquals(2, count());
      for (var entry : fixture.logger.entries) {
        assertEquals(503, entry.json().get(FIXTURE_STATUS_CFC31BCC).getAsInt());
        assertEquals("FAILURE", entry.json().get("outcome").getAsString());
        assertEquals(
            0,
            entry
                .json()
                .getAsJsonObject(FIXTURE_DETAILS_521BCB5E)
                .get(FIXTURE_RESPONSEBYTES_0785275F)
                .getAsLong());
        assertFalse(entry.json().toString().contains("canary"));
      }
    }
  }

  @Test
  void req003ActualClientResetNeverClaimsTheUnwrittenStreamAsFullBody() throws Exception {
    var resume = new CountDownLatch(1);
    var interruptedWrite = new AtomicInteger();
    try (var fixture =
            new WebRequestLogProducerTest.Fixture(WebRequestLogProducerTest.source(db::web));
        var server =
            WebHttpServer.start(
                root,
                0,
                filter(resume, interruptedWrite),
                Map.of(WebRequestLogProducer.class, fixture.producer))) {
      try (var socket = new Socket("127.0.0.1", server.port())) {
        socket.setSoTimeout(10000);
        socket.setSoLinger(true, 0);
        socket
            .getOutputStream()
            .write(
                ("POST /login?case=disconnect HTTP/1.1\r\nHost: localhost\r\n"
                        + "X-Forwarded-Proto: https\r\nX-Forwarded-For: 203.0.113.7\r\nContent-Length: 0\r\n\r\n")
                    .getBytes(StandardCharsets.US_ASCII));
        socket.getOutputStream().flush();
        byte[] observed = socket.getInputStream().readNBytes(512);
        assertEquals(512, observed.length);
        assertTrue(new String(observed, StandardCharsets.US_ASCII).startsWith("HTTP/1.1 200 "));
      } finally {
        resume.countDown();
      }
      awaitEntries(fixture, 1);
      assertEquals(1, interruptedWrite.get());
      var json = fixture.logger.entries.getFirst().json();
      // Installed CoyoteAdapter async failure sets native final 500; the received header stays 200.
      assertEquals(500, json.get(FIXTURE_STATUS_CFC31BCC).getAsInt());
      assertEquals("FAILURE", json.get("outcome").getAsString());
      assertEquals("ERROR", json.get("level").getAsString());
      long bytes =
          json.getAsJsonObject(FIXTURE_DETAILS_521BCB5E)
              .get(FIXTURE_RESPONSEBYTES_0785275F)
              .getAsLong();
      assertTrue(bytes >= 1024);
      assertTrue(bytes < 1024 + 4194304L);
      assertEquals(1, count());
      assertEquals(FIXTURE_LOGIN_F843C044, json.get(FIXTURE_PATH_D070C7EC).getAsString());
    }
  }

  @Test
  void req008HundredRealRequestsKeepCorrelationAndEventIdentitySeparated() throws Exception {
    String url;
    try (var connection = db.web()) {
      url = connection.getMetaData().getURL();
    }
    try (var pool = new com.zaxxer.hikari.HikariDataSource()) {
      pool.setJdbcUrl(url);
      pool.setUsername("schubert_web_session");
      pool.setMaximumPoolSize(8);
      pool.setConnectionTimeout(5000);
      try (var fixture = new WebRequestLogProducerTest.Fixture(pool);
          var server =
              WebHttpServer.start(
                  root, 0, filter(), Map.of(WebRequestLogProducer.class, fixture.producer));
          var client = HttpClient.newBuilder().connectTimeout(Duration.ofSeconds(3)).build();
          var tasks = Executors.newVirtualThreadPerTaskExecutor()) {
        var responses = new ArrayList<Future<HttpResponse<String>>>();
        for (int i = 1; i <= 100; i++) {
          final int owner = i;
          responses.add(
              tasks.submit(
                  () ->
                      send(
                          client,
                          server.port(),
                          FIXTURE_POST_E46D3AE9,
                          "/login?case=parallel&owner=" + owner,
                          true)));
        }
        for (int i = 0; i < responses.size(); i++) {
          var response = responses.get(i).get(15, TimeUnit.SECONDS);
          assertEquals(200, response.statusCode());
          assertEquals("owner-" + (i + 1), response.body());
        }
        awaitEntries(fixture, 100);
        assertEquals(100, count());
        var events = new HashSet<String>();
        var requests = new HashSet<String>();
        var correlations = new HashSet<UUID>();
        for (var entry : fixture.logger.entries) {
          var json = entry.json();
          assertTrue(events.add(json.get("messageId").getAsString()));
          assertTrue(requests.add(json.get("requestId").getAsString()));
          assertTrue(correlations.add(UUID.fromString(json.get("correlationId").getAsString())));
          assertEquals(FIXTURE_LOGIN_F843C044, json.get(FIXTURE_PATH_D070C7EC).getAsString());
          assertFalse(json.toString().contains("owner="));
        }
        var expected = new HashSet<UUID>();
        for (int i = 1; i <= 100; i++) expected.add(new UUID(2, i));
        assertEquals(expected, correlations);
      }
    }
  }

  @Test
  void req016HttpCloseLeavesCallerOwnedDatabaseAndCodecUsable() throws Exception {
    try (var fixture =
        new WebRequestLogProducerTest.Fixture(WebRequestLogProducerTest.source(db::web))) {
      var server =
          WebHttpServer.start(
              root, 0, filter(), Map.of(WebRequestLogProducer.class, fixture.producer));
      try (var client = HttpClient.newBuilder().connectTimeout(Duration.ofSeconds(3)).build()) {
        assertEquals(
            200,
            send(client, server.port(), FIXTURE_GET_04F32A7E, FIXTURE_LOGIN_F843C044, true)
                .statusCode());
        awaitEntries(fixture, 1);
      } finally {
        server.close();
      }
      assertThrows(IllegalStateException.class, server::port);
      assertEquals(1, count());
      var identity =
          new WebLogPayloadIdentity(
              UUID.fromString("00000000-0000-0000-0000-000000000012"),
              UUID.fromString("00000000-0000-0000-0000-000000000015"));
      var encrypted = fixture.codec.encrypt(identity, WebLogPayloadCodecTest.goldenWire());
      assertEquals(2374, encrypted.ciphertext().length);
      assertArrayEquals(
          WebLogPayloadCodecTest.goldenWire(), fixture.codec.decrypt(identity, encrypted));
    }
  }

  @Test
  void req014OwnerSignalFailureIsOnceFixedAndNeverMetadataRetried() throws Exception {
    try (var fixture =
        new WebRequestLogProducerTest.Fixture(WebRequestLogProducerTest.source(db::web))) {
      fixture.logger.enabled = false;
      for (boolean malformed : List.of(false, true)) {
        var calls = new AtomicInteger();
        var producer =
            new WebRequestLogProducer(
                fixture.database,
                fixture.codec,
                new WebLogOutboxRepository(() -> 0),
                fixture.logger,
                WebRequestLogProducerTest.CLOCK,
                UUID::randomUUID,
                "a",
                "b",
                () -> {
                  calls.incrementAndGet();
                  throw new IllegalStateException("synthetic-terminal-private-canary");
                });
        var valve = new HttpRequestLoggingValve(producer);
        var coyote = new org.apache.coyote.Request();
        coyote.setMethod(FIXTURE_GET_04F32A7E);
        var request = new Request(new Connector(), coyote);
        var response = new Response(new org.apache.coyote.Response());
        WebRequestTrace.ensure(request, UUID::randomUUID);
        var failure =
            assertThrows(
                IllegalStateException.class,
                () -> valve.log(malformed ? null : request, response, 0));
        assertEquals("request audit terminal signal failed", failure.getMessage());
        assertNull(failure.getCause());
        assertEquals(0, failure.getSuppressed().length);
        assertEquals(1, calls.get());
        assertTrue(fixture.logger.entries.isEmpty());
        assertEquals(0, count());
        assertEquals(200, response.getStatus());
      }
    }
  }

  private static Filter filter() {
    return filter(new CountDownLatch(0), new AtomicInteger());
  }

  private static Filter filter(CountDownLatch resume, AtomicInteger interruptedWrite) {
    var transport =
        new CaddyTransportContextFilter(
            UUID::randomUUID,
            new CaddyClientAddressResolver(),
            new WebSecurityAudit(
                System.getLogger("pt-request-transport"),
                WebRequestLogProducerTest.CLOCK,
                "pt",
                "pt"));
    return (request, response, chain) ->
        transport.doFilter(
            request,
            response,
            (req, res) -> {
              var http = (HttpServletRequest) req;
              var result = (HttpServletResponse) res;
              String mode = http.getParameter("case");
              if ("redirect".equals(mode)) {
                result.setStatus(302);
                result.setHeader("Location", "/");
                return;
              }
              if ("rejected".equals(mode)) {
                result.setStatus(403);
                result.getWriter().write("denied");
                return;
              }
              if ("error".equals(mode))
                throw new ServletException("synthetic-private-error-canary");
              if ("parallel".equals(mode)) {
                int owner = Integer.parseInt(http.getParameter("owner"));
                WebRequestTrace.businessIdentifiers(() -> new UUID(2, owner)).get();
                WebRequestTrace.businessIdentifiers(() -> new UUID(9, owner)).get();
                result.setContentType("text/plain;charset=UTF-8");
                result.getWriter().write("owner-" + owner);
                return;
              }
              if ("timeout".equals(mode) || "async-error".equals(mode)) {
                var async = http.startAsync();
                async.setTimeout(50);
                async.addListener(
                    new AsyncListener() {
                      @Override
                      public void onComplete(AsyncEvent event) {}

                      @Override
                      public void onStartAsync(AsyncEvent event) {
                        event.getAsyncContext().addListener(this);
                      }

                      @Override
                      public void onTimeout(AsyncEvent event) {
                        end(event);
                      }

                      @Override
                      public void onError(AsyncEvent event) {
                        end(event);
                      }

                      private void end(AsyncEvent event) {
                        ((HttpServletResponse) event.getAsyncContext().getResponse())
                            .setStatus(503);
                        event.getAsyncContext().complete();
                      }
                    });
                if ("async-error".equals(mode))
                  async.start(
                      () -> {
                        throw new IllegalStateException("synthetic-async-canary");
                      });
                return;
              }
              if ("disconnect".equals(mode)) {
                var async = http.startAsync();
                async.setTimeout(10000);
                async.start(
                    () -> {
                      try {
                        var output = (HttpServletResponse) async.getResponse();
                        output.setStatus(200);
                        output.getOutputStream().write(new byte[1024]);
                        output.flushBuffer();
                        if (!resume.await(5, TimeUnit.SECONDS))
                          throw new IllegalStateException("synthetic reset timeout");
                        output.getOutputStream().write(new byte[4194304]);
                        output.flushBuffer();
                      } catch (IOException failure) {
                        interruptedWrite.incrementAndGet();
                      } catch (InterruptedException failure) {
                        Thread.currentThread().interrupt();
                        throw new IllegalStateException("synthetic interrupted writer");
                      } finally {
                        async.complete();
                      }
                    });
                return;
              }
              if ("async".equals(mode)) {
                var async = http.startAsync();
                async.start(
                    () -> {
                      try {
                        var output = (HttpServletResponse) async.getResponse();
                        output.setStatus(202);
                        output.setContentType("text/plain;charset=UTF-8");
                        output.getWriter().write("完了");
                      } catch (IOException failure) {
                        throw new IllegalStateException("synthetic writer failure");
                      } finally {
                        async.complete();
                      }
                    });
                return;
              }
              if ("dispatch".equals(mode)) {
                Object old = http.getAttribute("pt.dispatch-count");
                int count = old instanceof Integer value ? value : 0;
                if (count < 2) {
                  http.setAttribute("pt.dispatch-count", count + 1);
                  var async = http.startAsync();
                  async.start(() -> async.dispatch(FIXTURE_LOGIN_F843C044));
                  return;
                }
              }
              chain.doFilter(req, res);
            });
  }

  private static HttpResponse<String> send(
      HttpClient client, int port, String method, String path, boolean trusted) throws Exception {
    var request =
        HttpRequest.newBuilder(URI.create("http://127.0.0.1:" + port + path))
            .timeout(Duration.ofSeconds(10))
            .method(method, HttpRequest.BodyPublishers.noBody());
    if (trusted)
      request.header("X-Forwarded-Proto", "https").header("X-Forwarded-For", "203.0.113.7");
    return client.send(request.build(), HttpResponse.BodyHandlers.ofString(StandardCharsets.UTF_8));
  }

  private static void awaitEntries(WebRequestLogProducerTest.Fixture fixture, int expected)
      throws Exception {
    long deadline = System.nanoTime() + TimeUnit.SECONDS.toNanos(10);
    while (fixture.logger.entries.size() < expected && System.nanoTime() < deadline)
      Thread.sleep(10);
    assertEquals(expected, fixture.logger.entries.size());
    // Callback publishes PENDING before committing; DB assertion must await callback transaction
    // too.
    while (count() < expected - (expected == 8 ? 2 : 0) && System.nanoTime() < deadline)
      Thread.sleep(10);
  }

  private static long count() throws SQLException {
    try (var connection = db.web();
        var statement = connection.createStatement();
        var rows =
            statement.executeQuery("select count(*) from schubert_web_session.web_log_outbox")) {
      assertTrue(rows.next());
      return rows.getLong(1);
    }
  }
}
