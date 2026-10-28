package dev.codex.schubert.nk.web.session;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.layout.semantic.UserRole;
import dev.codex.schubert.nk.web.bootstrap.WebHttpServer;
import dev.codex.schubert.nk.web.config.LogoutMvcConfiguration;
import dev.codex.schubert.nk.web.controller.LogoutController;
import dev.codex.schubert.nk.web.logging.WebLogDatabaseFixture;
import dev.codex.schubert.nk.web.logging.WebSecurityAudit;
import dev.codex.schubert.nk.web.messaging.JmsRequestReplyClient;
import dev.codex.schubert.nk.web.messaging.LogoutWireClient;
import dev.codex.schubert.nk.web.messaging.ReplyCorrelationRegistry;
import dev.codex.schubert.nk.web.revocation.LocalLogoutCoordinator;
import dev.codex.schubert.nk.web.revocation.RevocationPayloadCodec;
import dev.codex.schubert.nk.web.security.LocalLogoutHandler;
import dev.codex.schubert.nk.web.security.WebSecurityFilterFactory;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletRequestWrapper;
import java.io.IOException;
import java.lang.reflect.Proxy;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Clock;
import java.time.Duration;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicLong;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;
import org.springframework.mock.web.MockHttpServletRequest;
import org.springframework.mock.web.MockHttpServletResponse;
import org.springframework.mock.web.MockHttpSession;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.web.csrf.CsrfToken;
import org.springframework.session.web.http.SessionRepositoryFilter;

/** RERUN007: literal HTTP/SQL/256+280 byte oracles, real security/Servlet/MVC, not native. */
final class LogoutControllerTest {
  private static final String FIXTURE_0000_876EEFE0 = "0000";
  private static final String FIXTURE_POST_E46D3AE9 = "POST";
  private static final String FIXTURE_LOGOUT_AD6C492E = "/logout";
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
    try (var c = db.web();
        var s = c.createStatement()) {
      s.executeUpdate("delete from schubert_web_session.pending_context_revocations");
      s.executeUpdate("delete from schubert_web_session.web_http_sessions");
    }
  }

  @AfterEach
  void clear() {
    SecurityContextHolder.clearContext();
  }

  @Test
  void rerun007aActualHttpConfirmedAndQueuedDestroyCookieAndOnlyCurrentRow() throws Exception {
    for (String code : List.of(FIXTURE_0000_876EEFE0, "0200", "0102", "9000", "lost", "timeout")) {
      reset();
      try (var f = new Fixture()) {
        f.code = code;
        var old = f.authenticated();
        var newer = f.authenticated();
        try (var server = f.server(root.resolve(code))) {
          var reply =
              f.send(
                  server, FIXTURE_POST_E46D3AE9, old, old.attributes().csrfToken().orElseThrow());
          assertEquals(302, reply.statusCode());
          assertEquals("/login?logout", reply.headers().firstValue("location").orElseThrow());
          String cookie = reply.headers().firstValue("set-cookie").orElseThrow();
          assertTrue(cookie.startsWith("SCHUBERT_NK_SESSION=;"));
          for (String part : List.of("Max-Age=0", "Path=/", "Secure", "HttpOnly", "SameSite=Lax"))
            assertTrue(cookie.contains(part));
          assertFalse(cookie.contains("JSESSIONID"));
          assertTrue(f.sessions.find(old.sessionId()).isEmpty());
          assertTrue(f.sessions.find(newer.sessionId()).isPresent());
          boolean confirmed = code.equals(FIXTURE_0000_876EEFE0) || code.equals("0200");
          assertEquals(confirmed ? 0 : 1, pending());
          var event = f.h.log.events.getLast();
          assertEquals(
              confirmed ? "LOGOUT_SUCCEEDED" : "LOGOUT_REVOCATION_QUEUED",
              event.get("action").getAsString());
          assertEquals("reader", event.get("actorUsername").getAsString());
          assertEquals(
              FIXTURE_LOGOUT_AD6C492E, event.getAsJsonObject("details").get("route").getAsString());
          assertFalse(event.toString().contains("b".repeat(64)));
          assertEquals(1, f.calls.get());
          if (!confirmed) {
            try (var c = db.web();
                var s = c.createStatement();
                var r =
                    s.executeQuery(
                        "select expires_at,attempt_count,next_attempt_at-requested_at,context_ciphertext from schubert_web_session.pending_context_revocations")) {
              assertTrue(r.next());
              assertNull(r.getObject(1));
              assertEquals(0, r.getInt(2));
              assertEquals("00:00:05", r.getString(3));
              assertFalse(
                  new String(r.getBytes(4), StandardCharsets.US_ASCII).contains("b".repeat(64)));
              assertFalse(r.next());
            }
          }
        }
      }
    }
  }

  @Test
  void rerun007bActualGetHeadCsrfAndAnonymousNeverRevoke() throws Exception {
    try (var f = new Fixture();
        var server = f.server(root)) {
      var old = f.authenticated();
      assertEquals(405, f.send(server, "GET", old, "").statusCode());
      assertEquals(405, f.send(server, "HEAD", old, "").statusCode());
      assertEquals(403, f.send(server, FIXTURE_POST_E46D3AE9, old, "wrong").statusCode());
      assertEquals(0, f.calls.get());
      assertEquals(0, pending());
      assertTrue(f.sessions.find(old.sessionId()).isPresent());
      var anonymous = f.sessions.create();
      assertEquals(
          403,
          f.send(
                  server,
                  FIXTURE_POST_E46D3AE9,
                  anonymous,
                  anonymous.attributes().csrfToken().orElseThrow())
              .statusCode());
      assertEquals(0, f.calls.get());
      assertEquals(0, pending());
    }
  }

  @Test
  void rerun007cConstructorNullAndUntrustedBoundariesFailClosed() throws Exception {
    try (var f = new Fixture()) {
      assertThrows(
          NullPointerException.class, () -> new LocalLogoutHandler(null, f.coordinator, f.h.audit));
      assertThrows(
          NullPointerException.class, () -> new LocalLogoutHandler(f.adapter, null, f.h.audit));
      assertThrows(
          NullPointerException.class, () -> new LocalLogoutHandler(f.adapter, f.coordinator, null));
      assertThrows(NullPointerException.class, () -> new LogoutController(null));
      assertThrows(
          NullPointerException.class, () -> f.handler.handle(null, new MockHttpServletResponse()));
      assertThrows(
          NullPointerException.class,
          () -> f.handler.handle(f.h.mock(FIXTURE_POST_E46D3AE9, FIXTURE_LOGOUT_AD6C492E), null));
      for (String fault : List.of("anonymous", "marker", "session", "transport", "identity")) {
        var request = f.direct();
        if (fault.equals("anonymous")) SecurityContextHolder.clearContext();
        if (fault.equals("marker"))
          request.removeAttribute(SessionRepositoryFilter.SESSION_REPOSITORY_ATTR);
        if (fault.equals("session")) request.setSession(null);
        if (fault.equals("identity")) request.setSession(new MockHttpSession(null, "invalid"));
        HttpServletRequest input =
            fault.equals("transport") ? new MockHttpServletRequest() : request;
        assertThrows(
            SessionStoreException.class,
            () -> f.handler.handle(input, new MockHttpServletResponse()));
        assertNull(SecurityContextHolder.getContext().getAuthentication());
        assertNull(input.getAttribute(CsrfToken.class.getName()));
      }
      assertEquals(0, f.calls.get());
    }
  }

  @Test
  void rerun007dStorageAndServletInvalidationFailuresNeverShowSuccess() throws Exception {
    try (var f = new Fixture()) {
      for (boolean beforeWire : List.of(true, false)) {
        var request = f.direct();
        f.h.f.failure = beforeWire ? "open" : "";
        if (!beforeWire)
          request.setSession(
              new MockHttpSession(null, request.getSession(false).getId()) {
                @Override
                public void invalidate() {
                  throw new IllegalStateException("private invalidation");
                }
              });
        var response = new MockHttpServletResponse();
        assertThrows(SessionStoreException.class, () -> f.handler.handle(request, response));
        assertNull(response.getHeader("Location"));
        assertTrue(f.h.log.events.isEmpty());
        assertNull(SecurityContextHolder.getContext().getAuthentication());
        f.h.f.failure = "";
      }
      assertEquals(0, pending());
    }
  }

  @Test
  void rerun007eFatalWireAndSecondaryInvalidationPreserveOriginalIdentity() throws Exception {
    try (var f = new Fixture()) {
      Error original = new AssertionError("private wire fatal");
      f.fatal = original;
      for (Throwable secondary :
          new Throwable[] {
            null,
            new IllegalStateException("private cleanup"),
            original,
            new AssertionError("secondary")
          }) {
        var request = f.direct();
        if (secondary != null)
          request.setSession(
              new MockHttpSession(null, request.getSession(false).getId()) {
                @Override
                public void invalidate() {
                  if (secondary instanceof Error e) throw e;
                  throw (RuntimeException) secondary;
                }
              });
        assertSame(
            original,
            assertThrows(
                Error.class, () -> f.handler.handle(request, new MockHttpServletResponse())));
        assertNull(SecurityContextHolder.getContext().getAuthentication());
        assertTrue(f.h.log.events.isEmpty());
      }
    }
  }

  @Test
  void rerun007fCommittedResponseAndAuditFailureAreNotLogoutSuccess() throws Exception {
    try (var f = new Fixture()) {
      var request = f.direct();
      var response = new MockHttpServletResponse();
      response.flushBuffer();
      assertThrows(IOException.class, () -> f.handler.handle(request, response));
      assertNull(response.getHeader("Location"));
      assertNull(SecurityContextHolder.getContext().getAuthentication());
      var failingLogger =
          (System.Logger)
              Proxy.newProxyInstance(
                  System.Logger.class.getClassLoader(),
                  new Class<?>[] {System.Logger.class},
                  (p, m, a) -> {
                    throw new IllegalStateException("private logger");
                  });
      var failingAudit = new WebSecurityAudit(failingLogger, Clock.systemUTC(), "pt", "pt");
      var handler = new LocalLogoutHandler(f.adapter, f.coordinator, failingAudit);
      var next = f.direct();
      assertThrows(
          SessionStoreException.class, () -> handler.handle(next, new MockHttpServletResponse()));
      assertNull(SecurityContextHolder.getContext().getAuthentication());
    }
  }

  @Test
  void rerun007gClearFailureAlwaysClearsSecurityAndPreservesFatal() throws Exception {
    try (var f = new Fixture()) {
      for (String mode : List.of("success", "runtime", "fatal", "same", "committed")) {
        var original = new AssertionError("private primary");
        f.fatal = mode.equals("fatal") || mode.equals("same") ? original : null;
        var request = f.direct();
        var response = new MockHttpServletResponse();
        if (mode.equals("committed")) response.flushBuffer();
        if (mode.equals("runtime")) request.setSession(null);
        var wrapped =
            new HttpServletRequestWrapper(request) {
              @Override
              public void removeAttribute(String name) {
                if (mode.equals("same")) throw original;
                throw new IllegalStateException("private attributes");
              }
            };
        if (f.fatal != null)
          assertSame(
              original, assertThrows(Error.class, () -> f.handler.handle(wrapped, response)));
        else assertThrows(SessionStoreException.class, () -> f.handler.handle(wrapped, response));
        assertNull(SecurityContextHolder.getContext().getAuthentication());
      }
    }
  }

  @Test
  void rerun007hHundredHttpLogoutsIndependentRowsAndRequestAudit() throws Exception {
    try (var f = new Fixture();
        var server = f.server(root);
        var pool = Executors.newFixedThreadPool(12)) {
      f.code = "9000";
      var inputs = new ArrayList<WebSessionSnapshot>();
      for (int i = 0; i < 100; i++) inputs.add(f.authenticated());
      var futures = new ArrayList<Future<HttpResponse<String>>>();
      for (var input : inputs)
        futures.add(
            pool.submit(
                () ->
                    f.send(
                        server,
                        FIXTURE_POST_E46D3AE9,
                        input,
                        input.attributes().csrfToken().orElseThrow())));
      for (var result : futures) assertEquals(302, result.get(60, TimeUnit.SECONDS).statusCode());
      assertEquals(100, f.calls.get());
      assertEquals(100, pending());
      assertEquals(100, f.h.log.events.size());
      assertEquals(
          100,
          f.h.log.events.stream().map(e -> e.get("requestId").getAsString()).distinct().count());
      try (var c = db.web();
          var s = c.createStatement();
          var r = s.executeQuery("select count(*) from schubert_web_session.web_http_sessions")) {
        assertTrue(r.next());
        assertEquals(0, r.getInt(1));
      }
    }
  }

  private static SessionPrincipal actor() {
    return new SessionPrincipal(
        "reader", UserRole.USER, AuthenticationContext.of("b".repeat(64)), Instant.now());
  }

  private static int pending() throws Exception {
    try (var c = db.web();
        var s = c.createStatement();
        var r =
            s.executeQuery(
                "select count(*) from schubert_web_session.pending_context_revocations")) {
      assertTrue(r.next());
      return r.getInt(1);
    }
  }

  private static final class Fixture implements AutoCloseable {
    final ApiSessionInvalidTest.Harness h = new ApiSessionInvalidTest.Harness(db);
    final EncryptedWebSessionRepository sessions =
        new EncryptedWebSessionRepository(h.f.source, h.f.codec, h.f.clock);
    final SpringEncryptedSessionRepository adapter =
        new SpringEncryptedSessionRepository(sessions, h.f.clock);
    final RevocationPayloadCodec revoke =
        new RevocationPayloadCodec("revoke", new byte[32], null, null);
    final JmsRequestReplyClient replies =
        new JmsRequestReplyClient(new ReplyCorrelationRegistry(), h.f.clock, 12);
    final AtomicLong calls = new AtomicLong();
    final AtomicLong ids = new AtomicLong(1000);
    volatile String code = FIXTURE_0000_876EEFE0;
    volatile Error fatal;
    final LogoutWireClient wire =
        new LogoutWireClient(
            replies,
            (id, request) -> {
              calls.incrementAndGet();
              assertEquals(256, request.length);
              assertEquals("LOGREQ01", new String(request, 11, 8, StandardCharsets.US_ASCII));
              assertEquals("b".repeat(64), new String(request, 113, 64, StandardCharsets.US_ASCII));
              if (fatal != null) throw fatal;
              if (code.equals("lost")) throw new jakarta.jms.JMSException("private lost reply");
              if (code.equals("timeout")) return;
              byte[] response = new byte[280];
              Arrays.fill(response, (byte) ' ');
              put(response, 0, "SCHBNK01001LOGRSP01001SS");
              put(response, 24, new UUID(1, id.getLeastSignificantBits()).toString());
              put(response, 60, id.toString());
              put(response, 96, "20261004090000000");
              put(response, 113, "b".repeat(64));
              put(response, 177, "0256000024000000000000000000280" + code);
              put(
                  response,
                  256,
                  code.equals(FIXTURE_0000_876EEFE0) || code.equals("0200")
                      ? "20261004090000000"
                      : "00000000000000000");
              assertTrue(replies.onReply(id, response));
              Arrays.fill(response, (byte) 0);
            },
            h.f.clock,
            () -> new UUID(0, ids.incrementAndGet()),
            Duration.ofMillis(50));
    final LocalLogoutCoordinator coordinator =
        new LocalLogoutCoordinator(sessions, revoke, wire, h.f.clock);
    final LocalLogoutHandler handler = new LocalLogoutHandler(adapter, coordinator, h.audit);
    final HttpClient client =
        HttpClient.newBuilder()
            .followRedirects(HttpClient.Redirect.NEVER)
            .connectTimeout(Duration.ofSeconds(2))
            .build();

    MockHttpServletRequest direct() throws Exception {
      var snapshot = authenticated();
      var request = h.mock(FIXTURE_POST_E46D3AE9, FIXTURE_LOGOUT_AD6C492E);
      request.setAttribute(SessionRepositoryFilter.SESSION_REPOSITORY_ATTR, adapter);
      request.setSession(new MockHttpSession(null, snapshot.sessionId().cookieValue()));
      SecurityContextHolder.getContext()
          .setAuthentication(
              UsernamePasswordAuthenticationToken.authenticated(
                  actor(), null, List.of(new SimpleGrantedAuthority("ROLE_USER"))));
      return request;
    }

    WebHttpServer server(Path path) throws Exception {
      Files.createDirectories(path);
      return WebHttpServer.start(
          path,
          0,
          new WebSecurityFilterFactory().create(adapter, h.api.provider, h.audit, UUID::randomUUID),
          Map.of(LocalLogoutHandler.class, handler),
          LogoutMvcConfiguration.class);
    }

    HttpResponse<String> send(
        WebHttpServer server, String method, WebSessionSnapshot input, String csrf)
        throws Exception {
      var body =
          method.equals(FIXTURE_POST_E46D3AE9)
              ? HttpRequest.BodyPublishers.ofString("_csrf=" + csrf)
              : HttpRequest.BodyPublishers.noBody();
      return client.send(
          HttpRequest.newBuilder(
                  URI.create("http://127.0.0.1:" + server.port() + FIXTURE_LOGOUT_AD6C492E))
              .timeout(Duration.ofSeconds(10))
              .header("X-Forwarded-For", "203.0.113.1")
              .header("X-Forwarded-Proto", "https")
              .header("Cookie", "SCHUBERT_NK_SESSION=" + input.sessionId().cookieValue())
              .header("Content-Type", "application/x-www-form-urlencoded")
              .method(method, body)
              .build(),
          HttpResponse.BodyHandlers.ofString());
    }

    @Override
    public void close() {
      assertEquals(0, replies.pendingCount());
      revoke.close();
      h.close();
    }

    WebSessionSnapshot authenticated() {
      return sessions.authenticate(sessions.create().sessionId(), actor()).orElseThrow();
    }
  }

  private static void put(byte[] target, int offset, String text) {
    System.arraycopy(text.getBytes(StandardCharsets.US_ASCII), 0, target, offset, text.length());
  }
}
