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
  private static final String FIXTURE_SEARCH_Q_ABC_A4D7F62A = "/search?q=abc";
  private static final String EXPECTED_AUTHORITY_USER = "ROLE_USER";
  private static final String EXPECTED_AUTHORITY_ADMIN = "ROLE_ADMIN";

  // SS314 closed Test input identity, never the Production output mapper.
  private static String expectedAuthorityFor(SessionPrincipal principal) {
    return switch (principal.role()) {
      case USER -> EXPECTED_AUTHORITY_USER;
      case ADMIN -> EXPECTED_AUTHORITY_ADMIN;
    };
  }

  private static final String FIXTURE_GET_04F32A7E = "GET";
  private static final String FIXTURE_LOGIN_F843C044 = "/login";
  private static final String FIXTURE_LOCATION_FB077BAD = "Location";
  private static final String FIXTURE_DETAILS_521BCB5E = "details";
  private static final String FIXTURE_ACTORUSERNAME_538489F0 = "actorUsername";
  private static final String FIXTURE_PRIVATE_24ED6504 = "private";
  private static final String FIXTURE_POST_E46D3AE9 = "POST";
  private static final String FIXTURE_SEARCH_F32C67A7 = "/search";
  private static final String FIXTURE_READER_F734AAEA = "reader";
  private static final String FIXTURE_ADMIN_USERS_2C687608 = "/admin/users";
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
              FIXTURE_SEARCH_Q_ABC_A4D7F62A,
              "/scenarios/game/file",
              "/unknown",
              "/search?password=private",
              "/search?token=private")) {
        a.log.events.clear();
        var r = a.mock(FIXTURE_GET_04F32A7E, location);
        var s = new MockHttpServletResponse();
        a.handler.commence(r, s, secretAuth());
        assertEquals(302, s.getStatus());
        assertEquals(FIXTURE_LOGIN_F843C044, s.getHeader(FIXTURE_LOCATION_FB077BAD));
        var saved = a.cache.getRequest(r, s);
        if (location.equals(FIXTURE_SEARCH_Q_ABC_A4D7F62A)
            || location.equals("/scenarios/game/file"))
          assertEquals(location, Objects.requireNonNull(saved).getRedirectUrl());
        else {
          assertNull(saved);
          assertNull(r.getSession(false));
        }
        assertEquals(1, a.log.events.size());
        var event = a.log.events.getFirst();
        assertEquals("AUTHORIZATION_DENIED", event.get("action").getAsString());
        assertEquals(
            "UNAUTHENTICATED",
            event.getAsJsonObject(FIXTURE_DETAILS_521BCB5E).get("reason").getAsString());
        assertFalse(event.has(FIXTURE_ACTORUSERNAME_538489F0));
        assertFalse(event.toString().contains(FIXTURE_PRIVATE_24ED6504));
        assertEquals(
            WebRequestContext.require(r).requestId().toString(),
            event.get("requestId").getAsString());
      }
    }
  }

  @Test
  void web126PostAjaxAndMediaNeverRedirectOrReplay() throws Exception {
    try (var a = new Harness()) {
      for (String method :
          List.of(FIXTURE_POST_E46D3AE9, "HEAD", "PUT", "PATCH", "DELETE", "OPTIONS")) {
        var r = a.mock(method, FIXTURE_SEARCH_F32C67A7);
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
              "/%61udio/1")) assertForbidden(a, a.mock(FIXTURE_GET_04F32A7E, path));
      for (String ajax : List.of("XMLHttpRequest", "xmlhttprequest")) {
        var r = a.mock(FIXTURE_GET_04F32A7E, FIXTURE_SEARCH_F32C67A7);
        r.addHeader("X-Requested-With", ajax);
        assertForbidden(a, r);
      }
      for (String path : List.of("/animation/videos/1", "/music/1", "/audiox/1")) {
        var r = a.mock(FIXTURE_GET_04F32A7E, path);
        r.addHeader("X-Requested-With", "ordinary");
        var s = new MockHttpServletResponse();
        a.handler.commence(r, s, secretAuth());
        assertEquals(302, s.getStatus());
        assertEquals(FIXTURE_LOGIN_F843C044, s.getHeader(FIXTURE_LOCATION_FB077BAD));
      }
    }
  }

  @Test
  void web127RoleDenialKeepsPrincipalAndRedactsException() throws Exception {
    try (var a = new Harness()) {
      for (UserRole role : UserRole.values()) {
        a.log.events.clear();
        var p = principal(role, FIXTURE_READER_F734AAEA);
        setPrincipal(p);
        var r = a.mock(FIXTURE_GET_04F32A7E, FIXTURE_ADMIN_USERS_2C687608);
        r.getSession().setAttribute("principal", p);
        r.getSession().setAttribute("csrfToken", "02".repeat(32));
        var s = new MockHttpServletResponse();
        a.handler.handle(r, s, secretDenied());
        assertEquals(403, s.getStatus());
        assertNull(s.getHeader(FIXTURE_LOCATION_FB077BAD));
        assertNull(s.getErrorMessage());
        assertSame(p, r.getSession(false).getAttribute("principal"));
        assertEquals("02".repeat(32), r.getSession(false).getAttribute("csrfToken"));
        var event = a.log.events.getFirst();
        assertEquals(1, a.log.events.size());
        assertEquals(
            "ROLE", event.getAsJsonObject(FIXTURE_DETAILS_521BCB5E).get("reason").getAsString());
        assertEquals(
            "/**", event.getAsJsonObject(FIXTURE_DETAILS_521BCB5E).get("route").getAsString());
        assertEquals(
            FIXTURE_READER_F734AAEA, event.get(FIXTURE_ACTORUSERNAME_538489F0).getAsString());
        assertEquals(
            switch (role) {
              case USER -> "USER";
              case ADMIN -> "ADMIN";
            },
            event.get("actorRole").getAsString());
        assertFalse(event.toString().contains(FIXTURE_PRIVATE_24ED6504));
      }
      SecurityContextHolder.clearContext();
      a.handler.handle(
          a.mock(FIXTURE_POST_E46D3AE9, FIXTURE_ADMIN_USERS_2C687608),
          new MockHttpServletResponse(),
          secretDenied());
      assertFalse(a.log.events.getLast().has(FIXTURE_ACTORUSERNAME_538489F0));
    }
  }

  @Test
  void web128NullStorageLoggerAndResponseFaultsRemainFailures() throws Exception {
    try (var a = new Harness()) {
      var r = a.mock(FIXTURE_GET_04F32A7E, FIXTURE_SEARCH_F32C67A7);
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
      var corrupt = a.mock(FIXTURE_GET_04F32A7E, FIXTURE_SEARCH_F32C67A7);
      corrupt.setAttribute(WebRequestContext.class.getName(), FIXTURE_PRIVATE_24ED6504);
      assertThrows(IllegalStateException.class, () -> a.handler.commence(corrupt, s, secretAuth()));
      var wrong =
          UsernamePasswordAuthenticationToken.authenticated(
              FIXTURE_PRIVATE_24ED6504,
              FIXTURE_PRIVATE_24ED6504,
              List.of(new SimpleGrantedAuthority(EXPECTED_AUTHORITY_ADMIN)));
      SecurityContextHolder.getContext().setAuthentication(wrong);
      assertThrows(SessionStoreException.class, () -> a.handler.handle(r, s, secretDenied()));
      SecurityContextHolder.clearContext();
      a.log.fail = true;
      assertThrows(IllegalStateException.class, () -> a.handler.commence(r, s, secretAuth()));
      assertEquals(403, s.getStatus());
      assertNull(s.getHeader(FIXTURE_LOCATION_FB077BAD));
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
              () ->
                  a.handler.commence(
                      a.mock(FIXTURE_POST_E46D3AE9, FIXTURE_SEARCH_F32C67A7),
                      broken,
                      secretAuth())));
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
              throw new IllegalStateException(FIXTURE_PRIVATE_24ED6504);
            }
          };
      assertThrows(SessionStoreException.class, () -> a.handler.commence(attr, s, secretAuth()));
      a.f.failure = "open";
      assertThrows(
          SessionStoreException.class,
          () ->
              a.run(
                  raw(FIXTURE_GET_04F32A7E, FIXTURE_SEARCH_F32C67A7, null, null),
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
      a.run(
          raw(FIXTURE_GET_04F32A7E, FIXTURE_SEARCH_Q_ABC_A4D7F62A, null, null),
          first,
          (r, s) -> fail("protected"));
      assertEquals(302, first.getStatus());
      assertEquals(FIXTURE_LOGIN_F843C044, first.getHeader(FIXTURE_LOCATION_FB077BAD));
      var anonymous = Objects.requireNonNull(first.getCookie("SCHUBERT_NK_SESSION"));
      var stored = Objects.requireNonNull(a.adapter.findById(anonymous.getValue()));
      assertEquals(FIXTURE_SEARCH_Q_ABC_A4D7F62A, stored.getAttribute("savedRequest"));
      assertEquals("02".repeat(32), stored.getAttribute("csrfToken"));
      var denied = new MockHttpServletResponse();
      a.run(
          raw(FIXTURE_POST_E46D3AE9, "/notifications/1/cancel", anonymous, "02".repeat(32)),
          denied,
          (r, s) -> fail("no replay"));
      assertEquals(403, denied.getStatus());
      assertNull(denied.getHeader(FIXTURE_LOCATION_FB077BAD));
      assertEquals(
          FIXTURE_SEARCH_Q_ABC_A4D7F62A,
          Objects.requireNonNull(a.adapter.findById(anonymous.getValue()))
              .getAttribute("savedRequest"));
      var loggedIn = new MockHttpServletResponse();
      a.run(
          raw(FIXTURE_POST_E46D3AE9, FIXTURE_LOGIN_F843C044, anonymous, "02".repeat(32)),
          loggedIn,
          (r, s) -> fail("Login handler"));
      assertEquals(302, loggedIn.getStatus());
      assertEquals(FIXTURE_SEARCH_Q_ABC_A4D7F62A, loggedIn.getHeader(FIXTURE_LOCATION_FB077BAD));
      var user = Objects.requireNonNull(loggedIn.getCookie("SCHUBERT_NK_SESSION"));
      assertNull(a.adapter.findById(anonymous.getValue()));
      var count = new AtomicInteger();
      a.run(
          raw(FIXTURE_GET_04F32A7E, FIXTURE_SEARCH_Q_ABC_A4D7F62A, user, null),
          new MockHttpServletResponse(),
          (r, s) -> {
            assertEquals(
                FIXTURE_READER_F734AAEA,
                SecurityContextHolder.getContext().getAuthentication().getName());
            count.incrementAndGet();
            assertSame(
                r, a.cache.getMatchingRequest((HttpServletRequest) r, (HttpServletResponse) s));
          });
      var forbidden = new MockHttpServletResponse();
      a.run(
          raw(FIXTURE_GET_04F32A7E, FIXTURE_ADMIN_USERS_2C687608, user, null),
          forbidden,
          (r, s) -> fail("USER cannot enter"));
      assertEquals(403, forbidden.getStatus());
      var admin = a.adapter.createSession();
      admin.setAttribute("principal", principal(UserRole.ADMIN, "administrator"));
      a.run(
          raw(
              FIXTURE_GET_04F32A7E,
              FIXTURE_ADMIN_USERS_2C687608,
              new Cookie("SCHUBERT_NK_SESSION", admin.getId()),
              null),
          new MockHttpServletResponse(),
          (r, s) -> count.incrementAndGet());
      assertEquals(2, count.get());
      assertEquals(1, a.api.sends.get());
      a.api.erased();
      assertEquals(4, a.log.events.size());
      assertEquals(
          List.of("UNAUTHENTICATED", "UNAUTHENTICATED", "AUTHENTICATED", "ROLE"),
          a.log.events.stream()
              .map(e -> e.getAsJsonObject(FIXTURE_DETAILS_521BCB5E).get("reason").getAsString())
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
                var r =
                    a.mock(
                        n % 3 == 0 ? FIXTURE_GET_04F32A7E : FIXTURE_POST_E46D3AE9,
                        FIXTURE_ADMIN_USERS_2C687608);
                var s = new MockHttpServletResponse();
                if (n % 3 == 2) {
                  setPrincipal(principal(UserRole.USER, FIXTURE_READER_F734AAEA + n));
                  a.handler.handle(r, s, secretDenied());
                } else a.handler.commence(r, s, secretAuth());
                assertEquals(n % 3 == 0 ? 302 : 403, s.getStatus());
                assertEquals(
                    n % 3 == 0 ? FIXTURE_LOGIN_F843C044 : null,
                    s.getHeader(FIXTURE_LOCATION_FB077BAD));
                String id = WebRequestContext.require(r).requestId().toString();
                var events =
                    a.log.events.stream()
                        .filter(e -> e.get("requestId").getAsString().equals(id))
                        .toList();
                assertEquals(1, events.size());
                if (n % 3 == 2)
                  assertEquals(
                      FIXTURE_READER_F734AAEA + n,
                      events.getFirst().get(FIXTURE_ACTORUSERNAME_538489F0).getAsString());
                else assertFalse(events.getFirst().has(FIXTURE_ACTORUSERNAME_538489F0));
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
    assertNull(s.getHeader(FIXTURE_LOCATION_FB077BAD));
    assertNull(s.getErrorMessage());
    assertNull(r.getSession(false));
  }

  private static BadCredentialsException secretAuth() {
    return new BadCredentialsException(FIXTURE_PRIVATE_24ED6504) {
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
    return new AccessDeniedException(FIXTURE_PRIVATE_24ED6504) {
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
                p, null, List.of(new SimpleGrantedAuthority(expectedAuthorityFor(p)))));
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
    if (location.equals(FIXTURE_LOGIN_F843C044)) {
      r.addParameter("username", FIXTURE_READER_F734AAEA);
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
