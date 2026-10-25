package dev.codex.schubert.nk.web.session;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.fail;

import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.layout.semantic.UserRole;
import dev.codex.schubert.nk.web.logging.WebLogDatabaseFixture;
import dev.codex.schubert.nk.web.security.CaddyClientAddressResolver;
import dev.codex.schubert.nk.web.security.CaddyTransportContextFilter;
import dev.codex.schubert.nk.web.security.EncryptedSessionCsrfTokenRepository;
import dev.codex.schubert.nk.web.security.EncryptedSessionRequestCache;
import dev.codex.schubert.nk.web.security.EncryptedSessionSecurityContextRepository;
import dev.codex.schubert.nk.web.security.MqFormLoginFilterFactory;
import dev.codex.schubert.nk.web.security.MqLoginFailureHandler;
import dev.codex.schubert.nk.web.security.MqLoginSuccessHandler;
import dev.codex.schubert.nk.web.security.WebAccessExceptionFilterFactory;
import dev.codex.schubert.nk.web.security.WebAccessFailureHandler;
import dev.codex.schubert.nk.web.security.WebAuthorizationFilterFactory;
import dev.codex.schubert.nk.web.security.WebCsrfDeniedHandler;
import dev.codex.schubert.nk.web.security.WebCsrfFilterFactory;
import dev.codex.schubert.nk.web.security.WebRequestContext;
import dev.codex.schubert.nk.web.security.WebSecurityHeaderFilterFactory;
import jakarta.servlet.Filter;
import jakarta.servlet.FilterChain;
import jakarta.servlet.http.Cookie;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletRequestWrapper;
import jakarta.servlet.http.HttpServletResponse;
import jakarta.servlet.http.HttpSession;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Path;
import java.time.Clock;
import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.Objects;
import java.util.UUID;
import java.util.concurrent.Callable;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;
import org.springframework.mock.web.MockHttpServletRequest;
import org.springframework.mock.web.MockHttpServletResponse;
import org.springframework.security.access.AccessDeniedException;
import org.springframework.security.authentication.BadCredentialsException;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.web.context.SecurityContextHolderFilter;

/**
 * NK-WEB-001/PT-WEB-125..130; FUN-001..013/AUT-001..004/MON-004; UI221/226; SS313/314/351/352;
 * PG-D-112.
 */
class SessionAccessFailureTest {
  private static WebLogDatabaseFixture db;

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
      s.executeUpdate("delete from schubert_web_session.web_http_sessions");
    }
  }

  @AfterEach
  void clear() {
    SecurityContextHolder.clearContext();
  }

  @Test
  void web125AnonymousGetReturnsToLoginWithOnlySafeSavedRequest() throws Exception {
    try (var a = new Harness()) {
      for (String location :
          List.of(
              "/search?q=abc",
              "/scenarios/game/file",
              "/unknown",
              "/search?password=private",
              "/search?token=private")) {
        a.log.events.clear();
        var r = a.mock("GET", location);
        var s = new MockHttpServletResponse();
        a.handler.commence(r, s, secretAuth());
        assertEquals(302, s.getStatus());
        assertEquals("/login", s.getHeader("Location"));
        var saved = a.cache.getRequest(r, s);
        if (location.equals("/search?q=abc") || location.equals("/scenarios/game/file"))
          assertEquals(location, Objects.requireNonNull(saved).getRedirectUrl());
        else {
          assertNull(saved);
          assertNull(r.getSession(false));
        }
        assertEquals(1, a.log.events.size());
        var event = a.log.events.getFirst();
        assertEquals("AUTHORIZATION_DENIED", event.get("action").getAsString());
        assertEquals(
            "UNAUTHENTICATED", event.getAsJsonObject("details").get("reason").getAsString());
        assertFalse(event.has("actorUsername"));
        assertFalse(event.toString().contains("private"));
        assertEquals(
            WebRequestContext.require(r).requestId().toString(),
            event.get("requestId").getAsString());
      }
    }
  }

  @Test
  void web126PostAjaxAndMediaNeverRedirectOrReplay() throws Exception {
    try (var a = new Harness()) {
      for (String method : List.of("POST", "HEAD", "PUT", "PATCH", "DELETE", "OPTIONS")) {
        var r = a.mock(method, "/search");
        r.addParameter("private-body", "synthetic");
        assertForbidden(a, r);
      }
      for (String path :
          List.of(
              "/audio/1",
              "/audio/1/download",
              "/animation/media/1",
              "/music/media/1",
              "/music/download/1",
              "/%61udio/1")) assertForbidden(a, a.mock("GET", path));
      for (String ajax : List.of("XMLHttpRequest", "xmlhttprequest")) {
        var r = a.mock("GET", "/search");
        r.addHeader("X-Requested-With", ajax);
        assertForbidden(a, r);
      }
      for (String path : List.of("/animation/videos/1", "/music/1", "/audiox/1")) {
        var r = a.mock("GET", path);
        r.addHeader("X-Requested-With", "ordinary");
        var s = new MockHttpServletResponse();
        a.handler.commence(r, s, secretAuth());
        assertEquals(302, s.getStatus());
        assertEquals("/login", s.getHeader("Location"));
      }
    }
  }

  @Test
  void web127RoleDenialKeepsPrincipalAndRedactsException() throws Exception {
    try (var a = new Harness()) {
      for (UserRole role : UserRole.values()) {
        a.log.events.clear();
        var p = principal(role, "reader");
        setPrincipal(p);
        var r = a.mock("GET", "/admin/users");
        r.getSession().setAttribute("principal", p);
        r.getSession().setAttribute("csrfToken", "02".repeat(32));
        var s = new MockHttpServletResponse();
        a.handler.handle(r, s, secretDenied());
        assertEquals(403, s.getStatus());
        assertNull(s.getHeader("Location"));
        assertNull(s.getErrorMessage());
        assertSame(p, r.getSession(false).getAttribute("principal"));
        assertEquals("02".repeat(32), r.getSession(false).getAttribute("csrfToken"));
        var event = a.log.events.getFirst();
        assertEquals(1, a.log.events.size());
        assertEquals("ROLE", event.getAsJsonObject("details").get("reason").getAsString());
        assertEquals("/**", event.getAsJsonObject("details").get("route").getAsString());
        assertEquals("reader", event.get("actorUsername").getAsString());
        assertEquals(role.wireValue(), event.get("actorRole").getAsString());
        assertFalse(event.toString().contains("private"));
      }
      SecurityContextHolder.clearContext();
      a.handler.handle(
          a.mock("POST", "/admin/users"), new MockHttpServletResponse(), secretDenied());
      assertFalse(a.log.events.getLast().has("actorUsername"));
    }
  }

  @Test
  void web128NullStorageLoggerAndResponseFaultsRemainFailures() throws Exception {
    try (var a = new Harness()) {
      var r = a.mock("GET", "/search");
      var s = new MockHttpServletResponse();
      assertThrows(NullPointerException.class, () -> new WebAccessFailureHandler(null, a.audit));
      assertThrows(NullPointerException.class, () -> new WebAccessFailureHandler(a.cache, null));
      assertThrows(
          NullPointerException.class, () -> new WebAccessExceptionFilterFactory().create(null));
      assertThrows(NullPointerException.class, () -> a.handler.commence(null, s, secretAuth()));
      assertThrows(NullPointerException.class, () -> a.handler.commence(r, null, secretAuth()));
      assertThrows(NullPointerException.class, () -> a.handler.commence(r, s, null));
      assertThrows(NullPointerException.class, () -> a.handler.handle(null, s, secretDenied()));
      assertThrows(NullPointerException.class, () -> a.handler.handle(r, null, secretDenied()));
      assertThrows(NullPointerException.class, () -> a.handler.handle(r, s, null));
      assertThrows(
          IllegalStateException.class,
          () -> a.handler.commence(new MockHttpServletRequest(), s, secretAuth()));
      assertThrows(
          IllegalStateException.class,
          () -> a.handler.handle(new MockHttpServletRequest(), s, secretDenied()));
      var corrupt = a.mock("GET", "/search");
      corrupt.setAttribute(WebRequestContext.class.getName(), "private");
      assertThrows(IllegalStateException.class, () -> a.handler.commence(corrupt, s, secretAuth()));
      var wrong =
          UsernamePasswordAuthenticationToken.authenticated(
              "private", "private", List.of(new SimpleGrantedAuthority("ROLE_ADMIN")));
      SecurityContextHolder.getContext().setAuthentication(wrong);
      assertThrows(SessionStoreException.class, () -> a.handler.handle(r, s, secretDenied()));
      SecurityContextHolder.clearContext();
      a.log.fail = true;
      assertThrows(IllegalStateException.class, () -> a.handler.commence(r, s, secretAuth()));
      assertEquals(403, s.getStatus());
      assertNull(s.getHeader("Location"));
      assertThrows(IllegalStateException.class, () -> a.handler.handle(r, s, secretDenied()));
      a.log.fail = false;
      var io = new IOException("synthetic-send");
      var broken =
          new MockHttpServletResponse() {
            @Override
            public void sendError(int code) throws IOException {
              throw io;
            }
          };
      assertSame(
          io,
          assertThrows(
              IOException.class,
              () -> a.handler.commence(a.mock("POST", "/search"), broken, secretAuth())));
      assertSame(
          io, assertThrows(IOException.class, () -> a.handler.handle(r, broken, secretDenied())));
      var brokenHeader =
          new MockHttpServletResponse() {
            @Override
            public void setHeader(String name, String value) {
              throw new IllegalStateException("synthetic-header");
            }
          };
      assertThrows(
          IllegalStateException.class, () -> a.handler.commence(r, brokenHeader, secretAuth()));
      assertEquals(403, brokenHeader.getStatus());
      var attr =
          new HttpServletRequestWrapper(r) {
            @Override
            public HttpSession getSession() {
              throw new IllegalStateException("private");
            }
          };
      assertThrows(SessionStoreException.class, () -> a.handler.commence(attr, s, secretAuth()));
      a.f.failure = "open";
      assertThrows(
          SessionStoreException.class,
          () ->
              a.run(
                  raw("GET", "/search", null, null),
                  new MockHttpServletResponse(),
                  (x, y) -> fail("no business")));
      a.f.failure = "";
      assertNull(SecurityContextHolder.getContext().getAuthentication());
    }
  }

  @Test
  void web129ActualExceptionTranslationUsesEncryptedCacheAndRoleGate() throws Exception {
    try (var a = new Harness()) {
      var first = new MockHttpServletResponse();
      a.run(raw("GET", "/search?q=abc", null, null), first, (r, s) -> fail("protected"));
      assertEquals(302, first.getStatus());
      assertEquals("/login", first.getHeader("Location"));
      var anonymous = Objects.requireNonNull(first.getCookie("SCHUBERT_NK_SESSION"));
      var stored = Objects.requireNonNull(a.adapter.findById(anonymous.getValue()));
      assertEquals("/search?q=abc", stored.getAttribute("savedRequest"));
      assertEquals("02".repeat(32), stored.getAttribute("csrfToken"));
      var denied = new MockHttpServletResponse();
      a.run(
          raw("POST", "/notifications/1/cancel", anonymous, "02".repeat(32)),
          denied,
          (r, s) -> fail("no replay"));
      assertEquals(403, denied.getStatus());
      assertNull(denied.getHeader("Location"));
      assertEquals(
          "/search?q=abc",
          Objects.requireNonNull(a.adapter.findById(anonymous.getValue()))
              .getAttribute("savedRequest"));
      var loggedIn = new MockHttpServletResponse();
      a.run(
          raw("POST", "/login", anonymous, "02".repeat(32)),
          loggedIn,
          (r, s) -> fail("Login handler"));
      assertEquals(302, loggedIn.getStatus());
      assertEquals("/search?q=abc", loggedIn.getHeader("Location"));
      var user = Objects.requireNonNull(loggedIn.getCookie("SCHUBERT_NK_SESSION"));
      assertNull(a.adapter.findById(anonymous.getValue()));
      var count = new AtomicInteger();
      a.run(
          raw("GET", "/search?q=abc", user, null),
          new MockHttpServletResponse(),
          (r, s) -> {
            assertEquals(
                "reader", SecurityContextHolder.getContext().getAuthentication().getName());
            count.incrementAndGet();
            assertSame(
                r, a.cache.getMatchingRequest((HttpServletRequest) r, (HttpServletResponse) s));
          });
      var forbidden = new MockHttpServletResponse();
      a.run(raw("GET", "/admin/users", user, null), forbidden, (r, s) -> fail("USER cannot enter"));
      assertEquals(403, forbidden.getStatus());
      var admin = a.adapter.createSession();
      admin.setAttribute("principal", principal(UserRole.ADMIN, "administrator"));
      a.run(
          raw("GET", "/admin/users", new Cookie("SCHUBERT_NK_SESSION", admin.getId()), null),
          new MockHttpServletResponse(),
          (r, s) -> count.incrementAndGet());
      assertEquals(2, count.get());
      assertEquals(1, a.api.sends.get());
      a.api.erased();
      assertEquals(4, a.log.events.size());
      assertEquals(
          List.of("UNAUTHENTICATED", "UNAUTHENTICATED", "AUTHENTICATED", "ROLE"),
          a.log.events.stream()
              .map(e -> e.getAsJsonObject("details").get("reason").getAsString())
              .toList());
      assertNull(SecurityContextHolder.getContext().getAuthentication());
    }
  }

  @Test
  void web130ConcurrentDenialsKeepRequestAndActorSeparate() throws Exception {
    try (var a = new Harness();
        var pool = Executors.newFixedThreadPool(8)) {
      var jobs = new ArrayList<Callable<Void>>();
      for (int i = 0; i < 100; i++) {
        int n = i;
        jobs.add(
            () -> {
              try {
                var r = a.mock(n % 3 == 0 ? "GET" : "POST", "/admin/users");
                var s = new MockHttpServletResponse();
                if (n % 3 == 2) {
                  setPrincipal(principal(UserRole.USER, "reader" + n));
                  a.handler.handle(r, s, secretDenied());
                } else a.handler.commence(r, s, secretAuth());
                assertEquals(n % 3 == 0 ? 302 : 403, s.getStatus());
                assertEquals(n % 3 == 0 ? "/login" : null, s.getHeader("Location"));
                String id = WebRequestContext.require(r).requestId().toString();
                var events =
                    a.log.events.stream()
                        .filter(e -> e.get("requestId").getAsString().equals(id))
                        .toList();
                assertEquals(1, events.size());
                if (n % 3 == 2)
                  assertEquals("reader" + n, events.getFirst().get("actorUsername").getAsString());
                else assertFalse(events.getFirst().has("actorUsername"));
              } finally {
                SecurityContextHolder.clearContext();
              }
              return null;
            });
      }
      synchronized (a.handler) {
        for (var future : pool.invokeAll(jobs)) future.get(30, TimeUnit.SECONDS);
      }
      assertEquals(100, a.log.events.size());
      assertNull(SecurityContextHolder.getContext().getAuthentication());
    }
  }

  private static void assertForbidden(Harness a, MockHttpServletRequest r) throws Exception {
    var s = new MockHttpServletResponse();
    a.handler.commence(r, s, secretAuth());
    assertEquals(403, s.getStatus());
    assertNull(s.getHeader("Location"));
    assertNull(s.getErrorMessage());
    assertNull(r.getSession(false));
  }

  private static BadCredentialsException secretAuth() {
    return new BadCredentialsException("private") {
      @Override
      public String getMessage() {
        throw new AssertionError("diagnostic");
      }

      @Override
      public Throwable getCause() {
        throw new AssertionError("cause");
      }
    };
  }

  private static AccessDeniedException secretDenied() {
    return new AccessDeniedException("private") {
      @Override
      public String getMessage() {
        throw new AssertionError("diagnostic");
      }

      @Override
      public Throwable getCause() {
        throw new AssertionError("cause");
      }
    };
  }

  private static SessionPrincipal principal(UserRole role, String name) {
    return new SessionPrincipal(
        name,
        role,
        AuthenticationContext.of("a".repeat(64)),
        Instant.parse("2026-09-09T00:00:00Z"));
  }

  private static void setPrincipal(SessionPrincipal p) {
    SecurityContextHolder.getContext()
        .setAuthentication(
            UsernamePasswordAuthenticationToken.authenticated(
                p, null, List.of(new SimpleGrantedAuthority("ROLE_" + p.role().wireValue()))));
  }

  private static MockHttpServletRequest raw(
      String method, String location, Cookie cookie, String csrf) {
    String[] parts = location.split("\\?", 2);
    var r = new MockHttpServletRequest(method, parts[0]);
    if (parts.length == 2) r.setQueryString(parts[1]);
    r.setRemoteAddr("127.0.0.1");
    r.addHeader("X-Forwarded-For", "203.0.113.1");
    r.addHeader("X-Forwarded-Proto", "https");
    r.setCharacterEncoding(StandardCharsets.UTF_8);
    r.setContentType("application/x-www-form-urlencoded");
    if (cookie != null) r.setCookies(cookie);
    if (csrf != null) r.addParameter("_csrf", csrf);
    if (location.equals("/login")) {
      r.addParameter("username", "reader");
      r.addParameter("password", "p");
    }
    return r;
  }

  private static final class Harness implements AutoCloseable {
    final EncryptedWebSessionRepositoryTest.Fixture f =
        new EncryptedWebSessionRepositoryTest.Fixture(db);
    final SpringEncryptedSessionRepository adapter;
    final EncryptedSessionSecurityContextRepository contexts;
    final EncryptedSessionRequestCache cache;
    final SessionLoginHandlerTest.Log log = new SessionLoginHandlerTest.Log();
    final dev.codex.schubert.nk.web.logging.WebSecurityAudit audit =
        new dev.codex.schubert.nk.web.logging.WebSecurityAudit(log, Clock.systemUTC(), "pt", "pt");
    final AtomicInteger ids = new AtomicInteger();
    final CaddyTransportContextFilter transport =
        new CaddyTransportContextFilter(
            () -> new UUID(0, ids.incrementAndGet()), new CaddyClientAddressResolver(), audit);
    final WebAccessFailureHandler handler;
    final SessionFormLoginTest.Api api = new SessionFormLoginTest.Api("0000", "USER", "0000", 0);

    Harness() {
      f.clock.value = Instant.now();
      adapter = new SpringEncryptedSessionRepository(f.repository, f.clock);
      contexts = new EncryptedSessionSecurityContextRepository(adapter);
      cache = new EncryptedSessionRequestCache(adapter);
      handler = new WebAccessFailureHandler(cache, audit);
    }

    MockHttpServletRequest mock(String method, String location) throws Exception {
      var r = raw(method, location, null, null);
      r.setAttribute(
          org.springframework.session.web.http.SessionRepositoryFilter.SESSION_REPOSITORY_ATTR,
          adapter);
      transport.doFilter(r, new MockHttpServletResponse(), (x, y) -> {});
      return r;
    }

    void run(MockHttpServletRequest r, MockHttpServletResponse s, FilterChain end)
        throws Exception {
      var login =
          new MqFormLoginFilterFactory()
              .create(
                  api.provider,
                  contexts,
                  new MqLoginSuccessHandler(contexts, cache, audit),
                  new MqLoginFailureHandler(audit));
      var filters =
          List.<Filter>of(
              new WebSecurityHeaderFilterFactory().create(),
              transport,
              new WebSessionFilterFactory().create(adapter),
              new SecurityContextHolderFilter(contexts),
              new WebCsrfFilterFactory()
                  .create(
                      new EncryptedSessionCsrfTokenRepository(), new WebCsrfDeniedHandler(audit)),
              login,
              new WebAccessExceptionFilterFactory().create(handler),
              new WebAuthorizationFilterFactory().create());
      chain(filters, 0, end).doFilter(r, s);
    }

    private static FilterChain chain(List<Filter> filters, int at, FilterChain end) {
      return at == filters.size()
          ? end
          : (r, s) -> filters.get(at).doFilter(r, s, chain(filters, at + 1, end));
    }

    @Override
    public void close() {
      f.close();
    }
  }
}
