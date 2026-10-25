package dev.codex.schubert.nk.web.session;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assertions.fail;

import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.layout.semantic.UserRole;
import dev.codex.schubert.nk.web.logging.WebLogDatabaseFixture;
import dev.codex.schubert.nk.web.logging.WebSecurityAudit;
import dev.codex.schubert.nk.web.security.CaddyClientAddressResolver;
import dev.codex.schubert.nk.web.security.CaddyTransportContextFilter;
import dev.codex.schubert.nk.web.security.EncryptedSessionCsrfTokenRepository;
import dev.codex.schubert.nk.web.security.EncryptedSessionSecurityContextRepository;
import dev.codex.schubert.nk.web.security.WebCsrfDeniedHandler;
import dev.codex.schubert.nk.web.security.WebCsrfFilterFactory;
import dev.codex.schubert.nk.web.security.WebRequestContext;
import dev.codex.schubert.nk.web.security.WebSecurityHeaderFilterFactory;
import dev.codex.schubert.nk.web.session.EncryptedWebSessionRepositoryTest.Fixture;
import jakarta.servlet.DispatcherType;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.ServletRequest;
import jakarta.servlet.ServletResponse;
import jakarta.servlet.http.Cookie;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletRequestWrapper;
import jakarta.servlet.http.HttpServletResponse;
import jakarta.servlet.http.HttpSession;
import java.io.IOException;
import java.lang.System.Logger;
import java.lang.System.Logger.Level;
import java.lang.reflect.Proxy;
import java.nio.file.Path;
import java.time.Clock;
import java.time.Instant;
import java.time.ZoneOffset;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.ResourceBundle;
import java.util.UUID;
import java.util.concurrent.Callable;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.CopyOnWriteArrayList;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;
import org.springframework.mock.web.MockHttpServletRequest;
import org.springframework.mock.web.MockHttpServletResponse;
import org.springframework.mock.web.MockHttpSession;
import org.springframework.security.access.AccessDeniedException;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.web.context.SecurityContextHolderFilter;

/** NK-WEB-001/PT-WEB-101..108; FUN-001/AUT-004/MON-004; UI222/226/252; SS313/314/342/351/352. */
class WebRequestSecurityTest {
  private static final UUID ID = new UUID(0, 123);
  private static final String ATTRIBUTE = WebRequestContext.class.getName();
  private static final Clock CLOCK =
      Clock.fixed(Instant.parse("2026-09-09T00:00:00Z"), ZoneOffset.UTC);
  private static WebLogDatabaseFixture db;

  @BeforeAll
  static void start(@TempDir Path root) throws Exception {
    db = new WebLogDatabaseFixture(root);
  }

  @AfterAll
  static void stop() throws Exception {
    if (db != null) db.stop();
  }

  @AfterEach
  void clear() {
    SecurityContextHolder.clearContext();
  }

  @Test
  void web101ServerIdentityAndTrustedAddressReachOnlyCurrentRequest() throws Exception {
    var log = new Log();
    var filter = filter(log);
    var request = untouched();
    request.addHeader("X-Request-ID", "untrusted-header");
    var response = new MockHttpServletResponse();
    var calls = new AtomicInteger();
    filter.doFilter(
        request,
        response,
        (r, s) -> {
          calls.incrementAndGet();
          assertSame(request, r);
          assertSame(response, s);
          var context = WebRequestContext.require((HttpServletRequest) r);
          assertEquals(ID, context.requestId());
          assertEquals("203.0.113.1", context.clientAddress().value());
          assertEquals("WebRequestContext[REDACTED]", context.toString());
        });
    assertEquals(1, calls.get());
    assertEquals(200, response.getStatus());
    assertFalse(response.containsHeader("X-Request-ID"));
    assertTrue(log.entries.isEmpty());
    assertThrows(IllegalStateException.class, () -> WebRequestContext.require(untouched()));
  }

  @Test
  void web102RedispatchReusesIdentityButRevalidatesTransport() throws Exception {
    var ids = new AtomicInteger();
    var log = new Log();
    var filter =
        new CaddyTransportContextFilter(
            () -> new UUID(0, ids.incrementAndGet()), new CaddyClientAddressResolver(), audit(log));
    var request = untouched();
    for (DispatcherType dispatch :
        List.of(
            DispatcherType.REQUEST,
            DispatcherType.ERROR,
            DispatcherType.ASYNC,
            DispatcherType.FORWARD)) {
      request.setDispatcherType(dispatch);
      filter.doFilter(
          request,
          new MockHttpServletResponse(),
          (r, s) ->
              assertEquals(
                  new UUID(0, 1), WebRequestContext.require((HttpServletRequest) r).requestId()));
    }
    assertEquals(1, ids.get());
    var existing = WebRequestContext.require(request);
    var another = untouched();
    filter.doFilter(
        another,
        new MockHttpServletResponse(),
        (r, s) ->
            assertEquals(
                new UUID(0, 2), WebRequestContext.require((HttpServletRequest) r).requestId()));
    assertEquals(2, ids.get());
    request.removeHeader("X-Forwarded-For");
    request.addHeader("X-Forwarded-For", "203.0.113.2");
    var rejected = new MockHttpServletResponse();
    filter.doFilter(request, rejected, (r, s) -> fail("changed client must not continue"));
    assertEquals(403, rejected.getStatus());
    assertSame(existing, WebRequestContext.require(request));
    assertEquals(new UUID(0, 1).toString(), log.entries.getLast().get("requestId").getAsString());
    request.removeHeader("X-Forwarded-Proto");
    filter.doFilter(
        request, new MockHttpServletResponse(), (r, s) -> fail("redispatch must revalidate"));
    assertEquals(2, ids.get());
  }

  @Test
  void web103UntrustedProxyNeverTouchesSessionOrBusiness() throws Exception {
    var log = new Log();
    var filter = filter(log);
    for (String invalid : List.of("PEER", "MISSING", "DUPLICATE", "FORWARDED")) {
      var request = untouched();
      switch (invalid) {
        case "PEER" -> request.setRemoteAddr("203.0.113.9");
        case "MISSING" -> request.removeHeader("X-Forwarded-For");
        case "DUPLICATE" -> request.addHeader("X-Forwarded-For", "203.0.113.2");
        default -> request.addHeader("Forwarded", "synthetic-secret");
      }
      var response = new MockHttpServletResponse();
      new WebSecurityHeaderFilterFactory()
          .create()
          .doFilter(
              request,
              response,
              (r, s) -> filter.doFilter(r, s, (x, y) -> fail("invalid transport")));
      assertEquals(403, response.getStatus());
      assertEquals("no-store", response.getHeader("Cache-Control"));
      assertEquals("DENY", response.getHeader("X-Frame-Options"));
      assertNull(request.getAttribute(ATTRIBUTE));
      assertNull(response.getErrorMessage());
      var event = log.entries.getLast();
      assertEquals("AUTHORIZATION_DENIED", event.get("action").getAsString());
      assertEquals("PROXY", event.getAsJsonObject("details").get("reason").getAsString());
      assertEquals("/**", event.getAsJsonObject("details").get("route").getAsString());
      assertEquals(
          "HTTP_REQUEST", event.getAsJsonObject("details").get("targetType").getAsString());
      assertFalse(event.has("remoteAddress"));
      assertFalse(event.has("actorUsername"));
      assertFalse(event.toString().contains("synthetic-secret"));
    }
    assertEquals(4, log.entries.size());
  }

  @Test
  void web104NullConfigurationAttributeAndResponseFaultsFailClosed() throws Exception {
    var log = new Log();
    var audit = audit(log);
    assertThrows(
        NullPointerException.class,
        () -> new CaddyTransportContextFilter(null, new CaddyClientAddressResolver(), audit));
    assertThrows(
        NullPointerException.class, () -> new CaddyTransportContextFilter(() -> ID, null, audit));
    assertThrows(
        NullPointerException.class,
        () -> new CaddyTransportContextFilter(() -> ID, new CaddyClientAddressResolver(), null));
    var filter = filter(log);
    FilterChain never = (r, s) -> fail("fault must not continue");
    assertThrows(
        NullPointerException.class,
        () -> filter.doFilter(null, new MockHttpServletResponse(), never));
    assertThrows(NullPointerException.class, () -> filter.doFilter(untouched(), null, never));
    assertThrows(
        NullPointerException.class,
        () -> filter.doFilter(untouched(), new MockHttpServletResponse(), null));
    assertThrows(NullPointerException.class, () -> WebRequestContext.require(null));
    var nullId =
        new CaddyTransportContextFilter(() -> null, new CaddyClientAddressResolver(), audit);
    assertThrows(
        NullPointerException.class,
        () -> nullId.doFilter(untouched(), new MockHttpServletResponse(), never));
    var failedId =
        new CaddyTransportContextFilter(
            () -> {
              throw new IllegalStateException("synthetic id failure");
            },
            new CaddyClientAddressResolver(),
            audit);
    assertThrows(
        IllegalStateException.class,
        () -> failedId.doFilter(untouched(), new MockHttpServletResponse(), never));
    ServletRequest notHttp =
        (ServletRequest)
            Proxy.newProxyInstance(
                getClass().getClassLoader(),
                new Class<?>[] {ServletRequest.class},
                (p, m, a) -> {
                  throw new AssertionError("not called");
                });
    ServletResponse notResponse =
        (ServletResponse)
            Proxy.newProxyInstance(
                getClass().getClassLoader(),
                new Class<?>[] {ServletResponse.class},
                (p, m, a) -> {
                  throw new AssertionError("not called");
                });
    assertThrows(
        ServletException.class,
        () -> filter.doFilter(notHttp, new MockHttpServletResponse(), never));
    assertThrows(ServletException.class, () -> filter.doFilter(untouched(), notResponse, never));
    var wrong = untouched();
    wrong.setAttribute(ATTRIBUTE, ID);
    unavailable(() -> WebRequestContext.require(wrong));
    unavailable(() -> filter.doFilter(wrong, new MockHttpServletResponse(), never));
    for (boolean set : new boolean[] {false, true})
      for (boolean state : new boolean[] {false, true}) {
        var request =
            new HttpServletRequestWrapper(untouched()) {
              @Override
              public Object getAttribute(String name) {
                if (!set) {
                  if (state) throw new IllegalStateException("private attribute");
                  throw new IllegalArgumentException("private attribute");
                }
                return super.getAttribute(name);
              }

              @Override
              public void setAttribute(String name, Object value) {
                if (state) throw new IllegalStateException("private attribute");
                throw new IllegalArgumentException("private attribute");
              }
            };
        unavailable(() -> filter.doFilter(request, new MockHttpServletResponse(), never));
      }
    var chainFailure = new ServletException("synthetic downstream");
    assertSame(
        chainFailure,
        assertThrows(
            ServletException.class,
            () ->
                filter.doFilter(
                    untouched(),
                    new MockHttpServletResponse(),
                    (r, s) -> {
                      throw chainFailure;
                    })));
    var bad = untouched();
    bad.setRemoteAddr("203.0.113.9");
    var statusFailure = new IllegalStateException("synthetic status failure");
    var broken =
        new MockHttpServletResponse() {
          @Override
          public void setStatus(int status) {
            throw statusFailure;
          }
        };
    assertSame(
        statusFailure,
        assertThrows(IllegalStateException.class, () -> filter.doFilter(bad, broken, never)));
    assertEquals(200, broken.getStatus());
    log.fail = true;
    var failedResponse = new MockHttpServletResponse();
    assertThrows(IllegalStateException.class, () -> filter.doFilter(bad, failedResponse, never));
    assertEquals(403, failedResponse.getStatus());
  }

  @Test
  void web105CsrfDeniedHandlerIgnoresSecretExceptionsAndPreservesSession() throws Exception {
    var log = new Log();
    var handler = new WebCsrfDeniedHandler(audit(log));
    for (String role : List.of("ANONYMOUS", "USER", "ADMIN")) {
      SecurityContextHolder.clearContext();
      var request = trusted(new MockHttpServletRequest("POST", "/questions/new"));
      var session = new MockHttpSession();
      session.setAttribute("csrfToken", "02".repeat(32));
      request.setSession(session);
      var response = new MockHttpServletResponse();
      filter(log)
          .doFilter(
              request,
              response,
              (r, s) -> {
                if (!role.equals("ANONYMOUS"))
                  SecurityContextHolder.getContext().setAuthentication(authentication(role));
                handler.handle((HttpServletRequest) r, (HttpServletResponse) s, secretException());
              });
      assertEquals(403, response.getStatus());
      assertFalse(session.isInvalid());
      assertEquals("02".repeat(32), session.getAttribute("csrfToken"));
      assertNull(response.getCookie("SCHUBERT_NK_SESSION"));
      assertNull(response.getErrorMessage());
      var event = log.entries.getLast();
      assertEquals("CSRF", event.getAsJsonObject("details").get("reason").getAsString());
      assertEquals("AUTHORIZATION_DENIED", event.get("action").getAsString());
      assertEquals(ID.toString(), event.get("requestId").getAsString());
      assertEquals("203.0.113.1", event.get("remoteAddress").getAsString());
      if (role.equals("ANONYMOUS")) assertFalse(event.has("actorUsername"));
      else {
        assertEquals("reader", event.get("actorUsername").getAsString());
        assertEquals(role, event.get("actorRole").getAsString());
      }
      for (String secret :
          List.of("02".repeat(32), "ab".repeat(32), "private", "cookie", "password"))
        assertFalse(event.toString().contains(secret));
    }
  }

  @Test
  void web106ActualCsrfFilterUsesProductionDeniedAudit() throws Exception {
    for (String role : List.of("ANONYMOUS", "USER", "ADMIN")) {
      try (var c = db.web();
          var s = c.createStatement()) {
        s.executeUpdate("delete from schubert_web_session.web_http_sessions");
      }
      try (var f = new Fixture(db)) {
        f.clock.value = Instant.now();
        var adapter = new SpringEncryptedSessionRepository(f.repository, f.clock);
        var initial = adapter.createSession();
        if (!role.equals("ANONYMOUS")) initial.setAttribute("principal", principal(role));
        String token = role.equals("ANONYMOUS") ? "02".repeat(32) : "04".repeat(32);
        var log = new Log();
        var ids = new AtomicInteger();
        var transport =
            new CaddyTransportContextFilter(
                () -> new UUID(0, ids.incrementAndGet()),
                new CaddyClientAddressResolver(),
                audit(log));
        var sessions = new WebSessionFilterFactory().create(adapter);
        var holder =
            new SecurityContextHolderFilter(new EncryptedSessionSecurityContextRepository(adapter));
        var csrf =
            new WebCsrfFilterFactory()
                .create(
                    new EncryptedSessionCsrfTokenRepository(),
                    new WebCsrfDeniedHandler(audit(log)));
        for (boolean valid : new boolean[] {false, true}) {
          var request = trusted(new MockHttpServletRequest("POST", "/questions/new"));
          request.setCookies(new Cookie("SCHUBERT_NK_SESSION", initial.getId()));
          request.setContentType("application/x-www-form-urlencoded");
          request.setParameter("_csrf", valid ? token : "ff".repeat(32));
          var response = new MockHttpServletResponse();
          var business = new AtomicInteger();
          new WebSecurityHeaderFilterFactory()
              .create()
              .doFilter(
                  request,
                  response,
                  (r, s) ->
                      transport.doFilter(
                          r,
                          s,
                          (a, b) ->
                              sessions.doFilter(
                                  a,
                                  b,
                                  (c, d) ->
                                      holder.doFilter(
                                          c,
                                          d,
                                          (e, g) ->
                                              csrf.doFilter(
                                                  e, g, (x, y) -> business.incrementAndGet())))));
          assertEquals(valid ? 1 : 0, business.get());
          assertEquals(valid ? 200 : 403, response.getStatus());
          assertEquals("no-store", response.getHeader("Cache-Control"));
          assertNull(SecurityContextHolder.getContext().getAuthentication());
          assertEquals(1, log.entries.size());
          assertEquals(
              new UUID(0, 1).toString(), log.entries.getFirst().get("requestId").getAsString());
          assertEquals(token, adapter.findById(initial.getId()).getAttribute("csrfToken"));
        }
        assertEquals(2, ids.get());
      }
    }
  }

  @Test
  void web107DeniedHandlerNullContextAndLoggerFaultsNeverGrant() throws Exception {
    var log = new Log();
    assertThrows(NullPointerException.class, () -> new WebCsrfDeniedHandler(null));
    var handler = new WebCsrfDeniedHandler(audit(log));
    var r = untouched();
    var s = new MockHttpServletResponse();
    assertThrows(NullPointerException.class, () -> handler.handle(null, s, secretException()));
    assertThrows(NullPointerException.class, () -> handler.handle(r, null, secretException()));
    assertThrows(NullPointerException.class, () -> handler.handle(r, s, null));
    unavailable(() -> handler.handle(r, s, secretException()));
    r.setAttribute(ATTRIBUTE, "private context");
    unavailable(() -> handler.handle(r, s, secretException()));
    r.removeAttribute(ATTRIBUTE);
    filter(log).doFilter(r, s, (a, b) -> {});
    SecurityContextHolder.getContext()
        .setAuthentication(
            UsernamePasswordAuthenticationToken.unauthenticated("reader", "private"));
    assertThrows(SessionStoreException.class, () -> handler.handle(r, s, secretException()));
    SecurityContextHolder.clearContext();
    log.fail = true;
    assertThrows(IllegalStateException.class, () -> handler.handle(r, s, secretException()));
    assertEquals(403, s.getStatus());
    assertTrue(log.entries.isEmpty());
    log.fail = false;
    var fault = new IOException("synthetic send failure");
    var broken =
        new MockHttpServletResponse() {
          @Override
          public void sendError(int status) throws IOException {
            throw fault;
          }
        };
    assertSame(
        fault, assertThrows(IOException.class, () -> handler.handle(r, broken, secretException())));
    assertEquals(403, broken.getStatus());
    assertEquals(1, log.entries.size());
  }

  @Test
  void web108ConcurrentSecurityRequestsDoNotShareContextOrAudit() throws Exception {
    var log = new Log();
    var ids = new AtomicInteger();
    var filter =
        new CaddyTransportContextFilter(
            () -> new UUID(0, ids.incrementAndGet()), new CaddyClientAddressResolver(), audit(log));
    var handler = new WebCsrfDeniedHandler(audit(log));
    var expected = new ConcurrentHashMap<UUID, String>();
    try (var pool = Executors.newFixedThreadPool(8)) {
      var jobs = new ArrayList<Callable<Void>>();
      for (int i = 0; i < 100; i++) {
        String ip = "203.0.113." + i;
        jobs.add(
            () -> {
              SecurityContextHolder.clearContext();
              try {
                var request = untouched();
                request.removeHeader("X-Forwarded-For");
                request.addHeader("X-Forwarded-For", ip);
                var response = new MockHttpServletResponse();
                filter.doFilter(
                    request,
                    response,
                    (r, s) -> {
                      expected.put(
                          WebRequestContext.require((HttpServletRequest) r).requestId(), ip);
                      SecurityContextHolder.getContext().setAuthentication(authentication("USER"));
                      handler.handle(
                          (HttpServletRequest) r, (HttpServletResponse) s, secretException());
                    });
                assertEquals(403, response.getStatus());
                request.setDispatcherType(DispatcherType.ERROR);
                filter.doFilter(
                    request,
                    new MockHttpServletResponse(),
                    (r, s) ->
                        assertEquals(
                            ip,
                            WebRequestContext.require((HttpServletRequest) r)
                                .clientAddress()
                                .value()));
              } finally {
                SecurityContextHolder.clearContext();
              }
              assertNull(SecurityContextHolder.getContext().getAuthentication());
              return null;
            });
      }
      synchronized (filter) {
        synchronized (handler) {
          for (var job : pool.invokeAll(jobs)) job.get(10, TimeUnit.SECONDS);
        }
      }
    }
    assertEquals(100, ids.get());
    assertEquals(100, expected.size());
    assertEquals(100, log.entries.size());
    var seen = new HashSet<UUID>();
    for (var event : log.entries) {
      UUID id = UUID.fromString(event.get("requestId").getAsString());
      assertTrue(seen.add(id));
      assertEquals(expected.get(id), event.get("remoteAddress").getAsString());
      assertEquals("USER", event.get("actorRole").getAsString());
      assertEquals("CSRF", event.getAsJsonObject("details").get("reason").getAsString());
    }
  }

  private static WebSecurityAudit audit(Log log) {
    return new WebSecurityAudit(log, CLOCK, "a", "b");
  }

  private static CaddyTransportContextFilter filter(Log log) {
    return new CaddyTransportContextFilter(() -> ID, new CaddyClientAddressResolver(), audit(log));
  }

  private static MockHttpServletRequest trusted(MockHttpServletRequest r) {
    r.setRemoteAddr("127.0.0.1");
    r.addHeader("X-Forwarded-For", "203.0.113.1");
    r.addHeader("X-Forwarded-Proto", "https");
    r.setSecure(true);
    return r;
  }

  private static MockHttpServletRequest untouched() {
    return trusted(
        new MockHttpServletRequest("POST", "/login") {
          @Override
          public HttpSession getSession(boolean create) {
            throw new AssertionError("session must not be read");
          }

          @Override
          public String getParameter(String name) {
            throw new AssertionError("body must not be read");
          }

          @Override
          public String[] getParameterValues(String name) {
            throw new AssertionError("body must not be read");
          }
        });
  }

  private static SessionPrincipal principal(String role) {
    return new SessionPrincipal(
        "reader",
        UserRole.valueOf(role),
        AuthenticationContext.of("ab".repeat(32)),
        Instant.parse("2026-09-09T00:00:00Z"));
  }

  private static UsernamePasswordAuthenticationToken authentication(String role) {
    return UsernamePasswordAuthenticationToken.authenticated(
        principal(role), null, List.of(new SimpleGrantedAuthority("ROLE_" + role)));
  }

  private static AccessDeniedException secretException() {
    return new AccessDeniedException("private-csrf-value") {
      @Override
      public String getMessage() {
        throw new AssertionError("secret exception must not be read");
      }

      @Override
      public Throwable getCause() {
        throw new AssertionError("secret cause must not be read");
      }
    };
  }

  private static void unavailable(org.junit.jupiter.api.function.Executable action) {
    var ex = assertThrows(IllegalStateException.class, action);
    assertEquals("web request context is unavailable", ex.getMessage());
    assertNull(ex.getCause());
    assertEquals(0, ex.getSuppressed().length);
  }

  private static class Log implements Logger {
    final List<JsonObject> entries = new CopyOnWriteArrayList<>();
    volatile boolean fail;

    @Override
    public String getName() {
      return "synthetic.security";
    }

    @Override
    public boolean isLoggable(Level level) {
      return true;
    }

    @Override
    public void log(Level level, ResourceBundle bundle, String msg, Throwable thrown) {
      fail("Throwable not allowed");
    }

    @Override
    public void log(Level level, ResourceBundle bundle, String format, Object... params) {
      if (fail) throw new IllegalStateException("synthetic logger failure");
      assertEquals(Level.WARNING, level);
      assertNull(bundle);
      assertNull(params);
      entries.add(JsonParser.parseString(format).getAsJsonObject());
    }
  }
}
