package dev.codex.schubert.nk.web.session;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
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
import dev.codex.schubert.nk.web.logging.WebRequestTrace;
import dev.codex.schubert.nk.web.logging.WebSecurityAudit;
import dev.codex.schubert.nk.web.security.CaddyClientAddressResolver;
import dev.codex.schubert.nk.web.security.CaddyRequestRejectedException;
import dev.codex.schubert.nk.web.security.CaddyTransportContextFilter;
import dev.codex.schubert.nk.web.security.EncryptedSessionCsrfTokenRepository;
import dev.codex.schubert.nk.web.security.EncryptedSessionRequestCache;
import dev.codex.schubert.nk.web.security.EncryptedSessionSecurityContextRepository;
import dev.codex.schubert.nk.web.security.LoginFormRejectedException;
import dev.codex.schubert.nk.web.security.MqFormLoginFilterFactory;
import dev.codex.schubert.nk.web.security.MqLoginFailureHandler;
import dev.codex.schubert.nk.web.security.MqLoginLockedException;
import dev.codex.schubert.nk.web.security.MqLoginSuccessHandler;
import dev.codex.schubert.nk.web.security.WebCsrfDeniedHandler;
import dev.codex.schubert.nk.web.security.WebCsrfFilterFactory;
import dev.codex.schubert.nk.web.security.WebRequestContext;
import dev.codex.schubert.nk.web.security.WebSecurityHeaderFilterFactory;
import dev.codex.schubert.nk.web.session.EncryptedWebSessionRepositoryTest.Fixture;
import jakarta.servlet.FilterChain;
import jakarta.servlet.http.Cookie;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletRequestWrapper;
import jakarta.servlet.http.HttpServletResponse;
import jakarta.servlet.http.HttpSession;
import java.io.IOException;
import java.lang.System.Logger;
import java.lang.System.Logger.Level;
import java.nio.charset.StandardCharsets;
import java.nio.file.Path;
import java.time.Clock;
import java.time.Instant;
import java.time.ZoneOffset;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Base64;
import java.util.List;
import java.util.Objects;
import java.util.ResourceBundle;
import java.util.UUID;
import java.util.concurrent.Callable;
import java.util.concurrent.CopyOnWriteArrayList;
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
import org.springframework.mock.web.MockHttpSession;
import org.springframework.security.authentication.AnonymousAuthenticationToken;
import org.springframework.security.authentication.AuthenticationServiceException;
import org.springframework.security.authentication.BadCredentialsException;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.AuthenticationException;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.web.authentication.session.SessionAuthenticationException;
import org.springframework.security.web.context.SecurityContextHolderFilter;
import org.springframework.session.web.http.SessionRepositoryFilter;

/**
 * NK-WEB-001/PT-WEB-113..120; FUN-001/AUT-001..004/MON-004; UI226/232; SS313/314/351/352; SSC-046.
 */
class SessionLoginHandlerTest {
  private static final String FIXTURE_USER_2DED8884 = "USER";
  private static final String FIXTURE_READER_F734AAEA = "reader";
  private static final String FIXTURE_LOCATION_FB077BAD = "Location";
  private static final String FIXTURE_RETRY_AFTER_7F197FF6 = "Retry-After";
  private static final String FIXTURE_PRINCIPAL_590C90CB = "principal";
  private static final String FIXTURE_SAVEDREQUEST_50131C2B = "savedRequest";
  private static final String FIXTURE_ACTORUSERNAME_538489F0 = "actorUsername";
  private static final String FIXTURE_0000_876EEFE0 = "0000";
  private static final String FIXTURE_0106_EF3D3B45 = "0106";
  private static final String FIXTURE_SCHUBERT_NK_SESSION_DD9EE5FF = "SCHUBERT_NK_SESSION";
  private static WebLogDatabaseFixture db;
  private static final Instant NOW = Instant.parse("2026-09-09T00:00:00Z");

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
  void web113SuccessRedirectsOnlyToClosedSavedGet() throws Exception {
    try (var h = new Harness()) {
      for (String role : List.of(FIXTURE_USER_2DED8884, "ADMIN")) {
        for (String saved : Arrays.asList(null, "/search?q=a%20b")) {
          h.log.events.clear();
          var p = principal(FIXTURE_READER_F734AAEA, role);
          var r = h.request(p, saved);
          var trace = WebRequestTrace.ensure(r, UUID::randomUUID);
          r.addParameter("target", "//untrusted.invalid/");
          r.addHeader("Referer", "https://untrusted.invalid/");
          var s = new MockHttpServletResponse();
          h.success.onAuthenticationSuccess(r, s, auth(p));
          assertEquals(302, s.getStatus());
          assertEquals(saved == null ? "/" : saved, s.getHeader(FIXTURE_LOCATION_FB077BAD));
          assertEquals("", s.getContentAsString());
          assertNull(s.getHeader(FIXTURE_RETRY_AFTER_7F197FF6));
          assertSame(p, r.getSession(false).getAttribute(FIXTURE_PRINCIPAL_590C90CB));
          assertEquals(saved, r.getSession(false).getAttribute(FIXTURE_SAVEDREQUEST_50131C2B));
          assertEquals(1, h.log.events.size());
          var event = h.log.events.getFirst();
          assertEquals("LOGIN_SUCCEEDED", event.get("action").getAsString());
          assertEquals(
              FIXTURE_READER_F734AAEA, event.get(FIXTURE_ACTORUSERNAME_538489F0).getAsString());
          assertEquals(role, event.get("actorRole").getAsString());
          assertEquals(FIXTURE_READER_F734AAEA, trace.actor().orElseThrow().getUsername());
          assertEquals(role, trace.actor().orElseThrow().getRole());
          assertEquals(WebRequestContext.require(r).requestId(), trace.requestId());
          assertEquals("203.0.113.1", event.get("remoteAddress").getAsString());
          assertEquals(
              WebRequestContext.require(r).requestId().toString(),
              event.get("requestId").getAsString());
          assertEquals("/login", event.getAsJsonObject("details").get("route").getAsString());
          assertFalse(event.toString().contains("untrusted"));
        }
      }
      assertEquals(0, rows());
    }
  }

  @Test
  void web114SuccessRejectsUnpersistedOrInvalidIdentity() throws Exception {
    try (var h = new Harness()) {
      var p = principal(FIXTURE_READER_F734AAEA, FIXTURE_USER_2DED8884);
      var anonymous =
          new AnonymousAuthenticationToken(
              "synthetic", "anonymous", List.of(new SimpleGrantedAuthority("ROLE_ANONYMOUS")));
      for (Authentication candidate :
          List.of(
              anonymous,
              UsernamePasswordAuthenticationToken.unauthenticated(
                  FIXTURE_READER_F734AAEA, "synthetic"),
              auth(principal("other", FIXTURE_USER_2DED8884)))) {
        var s = new MockHttpServletResponse();
        assertThrows(
            SessionStoreException.class,
            () -> h.success.onAuthenticationSuccess(h.request(p, null), s, candidate));
        assertNull(s.getHeader(FIXTURE_LOCATION_FB077BAD));
      }
      for (String kind : List.of("ABSENT", "MARKER", "PRINCIPAL", "SAVED", "CLOSED")) {
        var r = h.request(kind.equals("ABSENT") ? null : p, null);
        if (kind.equals("MARKER"))
          r.removeAttribute(SessionRepositoryFilter.SESSION_REPOSITORY_ATTR);
        if (kind.equals("PRINCIPAL"))
          r.getSession().setAttribute(FIXTURE_PRINCIPAL_590C90CB, "private");
        if (kind.equals("SAVED"))
          r.getSession().setAttribute(FIXTURE_SAVEDREQUEST_50131C2B, "//untrusted.invalid/");
        if (kind.equals("CLOSED")) r.getSession().invalidate();
        var s = new MockHttpServletResponse();
        assertThrows(
            SessionStoreException.class, () -> h.success.onAuthenticationSuccess(r, s, auth(p)));
        assertNull(s.getHeader(FIXTURE_LOCATION_FB077BAD));
      }
      assertTrue(h.log.events.isEmpty());
      assertEquals(0, rows());
    }
  }

  @Test
  void web115FailureAndLockPreserveCurrentRedirectContract() throws Exception {
    try (var h = new Harness()) {
      for (int retry : new int[] {-1, 0, 1, 900}) {
        h.log.events.clear();
        var r = h.request(null, null);
        r.addParameter("username", "private-user");
        r.addParameter("password", "private-password");
        var s = new MockHttpServletResponse();
        h.failure.onAuthenticationFailure(
            r, s, retry < 0 ? secretBadCredentials() : new MqLoginLockedException(retry));
        assertEquals(302, s.getStatus());
        assertEquals(
            retry < 0 ? "/login?error" : "/login?locked", s.getHeader(FIXTURE_LOCATION_FB077BAD));
        assertEquals(
            retry < 0 ? null : Integer.toString(retry), s.getHeader(FIXTURE_RETRY_AFTER_7F197FF6));
        assertEquals("", s.getContentAsString());
        assertNull(r.getSession(false));
        assertEquals(1, h.log.events.size());
        var event = h.log.events.getFirst();
        assertEquals(
            retry < 0 ? "LOGIN_FAILED" : "LOGIN_LOCKED", event.get("action").getAsString());
        assertFalse(event.has(FIXTURE_ACTORUSERNAME_538489F0));
        assertFalse(event.toString().contains("private"));
        if (retry >= 0)
          assertEquals(retry, event.getAsJsonObject("details").get("retryAfterSeconds").getAsInt());
        assertNull(r.getAttribute("SPRING_SECURITY_LAST_EXCEPTION"));
      }
      assertEquals(0, rows());
    }
  }

  @Test
  void web116InputServiceAndUnknownFailuresStayDistinct() throws Exception {
    try (var h = new Harness()) {
      List<AuthenticationException> failures =
          List.of(
              new LoginFormRejectedException(),
              new CaddyRequestRejectedException(),
              new AuthenticationServiceException("private-service"),
              new SessionAuthenticationException("private-store"),
              new AuthenticationException("private-unknown") {
                @Override
                public String getMessage() {
                  throw new AssertionError("diagnostic read");
                }

                @Override
                public Throwable getCause() {
                  throw new AssertionError("cause read");
                }
              });
      for (int i = 0; i < failures.size(); i++) {
        h.log.events.clear();
        var r = h.request(null, null);
        var s = new MockHttpServletResponse();
        h.failure.onAuthenticationFailure(r, s, failures.get(i));
        assertEquals(i == 0 ? 400 : i == 1 ? 403 : 503, s.getStatus());
        assertNull(s.getHeader(FIXTURE_LOCATION_FB077BAD));
        assertNull(s.getErrorMessage());
        assertNull(r.getSession(false));
        assertEquals(i == 1 ? 1 : 0, h.log.events.size());
        if (i == 1) {
          var event = h.log.events.getFirst();
          assertEquals("AUTHORIZATION_DENIED", event.get("action").getAsString());
          assertEquals("PROXY", event.getAsJsonObject("details").get("reason").getAsString());
          assertFalse(event.has("remoteAddress"));
        }
      }
      assertEquals(0, rows());
    }
  }

  @Test
  void web117HandlerNullAndPublicFaultsNeverPretendSuccess() throws Exception {
    try (var h = new Harness()) {
      var p = principal(FIXTURE_READER_F734AAEA, FIXTURE_USER_2DED8884);
      var r = h.request(p, null);
      var s = new MockHttpServletResponse();
      assertThrows(
          NullPointerException.class, () -> new MqLoginSuccessHandler(null, h.cache, h.audit));
      assertThrows(
          NullPointerException.class, () -> new MqLoginSuccessHandler(h.contexts, null, h.audit));
      assertThrows(
          NullPointerException.class, () -> new MqLoginSuccessHandler(h.contexts, h.cache, null));
      assertThrows(NullPointerException.class, () -> new MqLoginFailureHandler(null));
      assertThrows(
          NullPointerException.class, () -> h.success.onAuthenticationSuccess(null, s, auth(p)));
      assertThrows(
          NullPointerException.class, () -> h.success.onAuthenticationSuccess(r, null, auth(p)));
      assertThrows(NullPointerException.class, () -> h.success.onAuthenticationSuccess(r, s, null));
      assertThrows(
          NullPointerException.class,
          () -> h.failure.onAuthenticationFailure(null, s, secretBadCredentials()));
      assertThrows(
          NullPointerException.class,
          () -> h.failure.onAuthenticationFailure(r, null, secretBadCredentials()));
      assertThrows(NullPointerException.class, () -> h.failure.onAuthenticationFailure(r, s, null));
      var absent = new MockHttpServletRequest();
      assertThrows(
          IllegalStateException.class, () -> h.success.onAuthenticationSuccess(absent, s, auth(p)));
      assertThrows(
          IllegalStateException.class,
          () -> h.failure.onAuthenticationFailure(absent, s, secretBadCredentials()));
      h.log.fail = true;
      assertThrows(
          IllegalStateException.class, () -> h.success.onAuthenticationSuccess(r, s, auth(p)));
      for (AuthenticationException failure :
          List.of(
              secretBadCredentials(),
              new MqLoginLockedException(1),
              new CaddyRequestRejectedException())) {
        assertThrows(
            IllegalStateException.class,
            () -> h.failure.onAuthenticationFailure(r, new MockHttpServletResponse(), failure));
      }
      assertNull(s.getHeader(FIXTURE_LOCATION_FB077BAD));
      h.log.fail = false;
      var io = new IOException("synthetic-send-error");
      var broken =
          new MockHttpServletResponse() {
            @Override
            public void sendError(int status) throws IOException {
              throw io;
            }
          };
      assertSame(
          io,
          assertThrows(
              IOException.class,
              () ->
                  h.failure.onAuthenticationFailure(r, broken, new LoginFormRejectedException())));
      assertSame(
          io,
          assertThrows(
              IOException.class,
              () ->
                  h.failure.onAuthenticationFailure(
                      r, broken, new AuthenticationServiceException("synthetic"))));
      for (String failedHeader : List.of(FIXTURE_LOCATION_FB077BAD, FIXTURE_RETRY_AFTER_7F197FF6)) {
        var response = brokenHeader(failedHeader);
        assertThrows(
            IllegalStateException.class,
            () -> h.failure.onAuthenticationFailure(r, response, new MqLoginLockedException(2)));
        assertNotEquals(302, response.getStatus());
      }
      var failedStatus =
          new MockHttpServletResponse() {
            @Override
            public void setStatus(int status) {
              throw new IllegalStateException("synthetic-status");
            }
          };
      assertThrows(
          IllegalStateException.class,
          () -> h.success.onAuthenticationSuccess(r, failedStatus, auth(p)));
      assertThrows(
          IllegalStateException.class,
          () -> h.failure.onAuthenticationFailure(r, failedStatus, secretBadCredentials()));
      var attr =
          new HttpServletRequestWrapper(r) {
            @Override
            public HttpSession getSession(boolean create) {
              throw new IllegalStateException("private-session");
            }
          };
      assertThrows(
          SessionStoreException.class, () -> h.success.onAuthenticationSuccess(attr, s, auth(p)));
    }
  }

  @Test
  void web118ActualLoginFilterUsesProductionHandlers() throws Exception {
    for (String code :
        List.of(FIXTURE_0000_876EEFE0, "0200", "0101", FIXTURE_0106_EF3D3B45, "9000", "JMS")) {
      reset();
      try (var h = new Harness()) {
        var initial = h.adapter.createSession();
        initial.setAttribute(FIXTURE_SAVEDREQUEST_50131C2B, "/search?q=abc");
        String old = initial.getId();
        String csrf = initial.getAttribute("csrfToken");
        var api =
            new SessionFormLoginTest.Api(
                code, "ADMIN", FIXTURE_0000_876EEFE0, code.equals(FIXTURE_0106_EF3D3B45) ? 123 : 0);
        var s = new MockHttpServletResponse();
        h.run(
            api,
            form(new Cookie(FIXTURE_SCHUBERT_NK_SESSION_DD9EE5FF, old), csrf),
            s,
            (r1, s1) -> fail("Login should terminate"));
        boolean ok = code.equals(FIXTURE_0000_876EEFE0) || code.equals("0200");
        assertEquals(code.equals("9000") || code.equals("JMS") ? 503 : 302, s.getStatus());
        assertEquals(
            ok
                ? "/search?q=abc"
                : code.equals("0101")
                    ? "/login?error"
                    : code.equals(FIXTURE_0106_EF3D3B45) ? "/login?locked" : null,
            s.getHeader(FIXTURE_LOCATION_FB077BAD));
        assertEquals(
            code.equals(FIXTURE_0106_EF3D3B45) ? "123" : null,
            s.getHeader(FIXTURE_RETRY_AFTER_7F197FF6));
        assertEquals(code.equals("9000") || code.equals("JMS") ? 0 : 1, h.log.events.size());
        assertEquals(1, rows());
        assertEquals(1, api.sends.get());
        assertEquals(code.equals("0200") ? 1 : 0, api.probes.get());
        if (ok) {
          var cookie = Objects.requireNonNull(s.getCookie(FIXTURE_SCHUBERT_NK_SESSION_DD9EE5FF));
          assertNotEquals(old, cookie.getValue());
          assertNull(h.adapter.findById(old));
          var next = form(cookie, null);
          next.setMethod("GET");
          next.setRequestURI("/search");
          next.setQueryString("q=abc");
          h.run(
              api,
              next,
              new MockHttpServletResponse(),
              (r1, s1) -> {
                assertEquals(
                    FIXTURE_READER_F734AAEA,
                    SecurityContextHolder.getContext().getAuthentication().getName());
                assertEquals(
                    List.of("ROLE_ADMIN"),
                    SecurityContextHolder.getContext().getAuthentication().getAuthorities().stream()
                        .map(a -> a.getAuthority())
                        .toList());
                assertSame(
                    r1,
                    h.cache.getMatchingRequest((HttpServletRequest) r1, (HttpServletResponse) s1));
                assertNull(
                    ((HttpServletRequest) r1)
                        .getSession(false)
                        .getAttribute(FIXTURE_SAVEDREQUEST_50131C2B));
              });
          assertEquals(2, h.f.ids.get());
        } else {
          assertNull(s.getCookie(FIXTURE_SCHUBERT_NK_SESSION_DD9EE5FF));
          assertNull(
              Objects.requireNonNull(h.adapter.findById(old))
                  .getAttribute(FIXTURE_PRINCIPAL_590C90CB));
          assertEquals(1, h.f.ids.get());
        }
        assertNull(SecurityContextHolder.getContext().getAuthentication());
        api.erased();
      }
    }
  }

  @Test
  void web119ConcurrentHandlerCallsKeepOutcomesSeparate() throws Exception {
    try (var h = new Harness();
        var pool = Executors.newFixedThreadPool(8)) {
      var jobs = new ArrayList<Callable<Void>>();
      for (int i = 0; i < 100; i++) {
        int n = i;
        jobs.add(
            () -> {
              var p =
                  principal(
                      FIXTURE_READER_F734AAEA + n, n % 2 == 0 ? FIXTURE_USER_2DED8884 : "ADMIN");
              var r = h.request(n % 4 < 2 ? p : null, n % 4 < 2 ? "/search?q=" + n : null);
              var s = new MockHttpServletResponse();
              if (n % 4 < 2) h.success.onAuthenticationSuccess(r, s, auth(p));
              else
                h.failure.onAuthenticationFailure(
                    r, s, n % 4 == 2 ? secretBadCredentials() : new MqLoginLockedException(n));
              assertEquals(302, s.getStatus());
              assertEquals(
                  n % 4 < 2 ? "/search?q=" + n : n % 4 == 2 ? "/login?error" : "/login?locked",
                  s.getHeader(FIXTURE_LOCATION_FB077BAD));
              assertEquals(
                  n % 4 == 3 ? Integer.toString(n) : null,
                  s.getHeader(FIXTURE_RETRY_AFTER_7F197FF6));
              String id = WebRequestContext.require(r).requestId().toString();
              var event =
                  h.log.events.stream()
                      .filter(e -> e.get("requestId").getAsString().equals(id))
                      .toList();
              assertEquals(1, event.size());
              if (n % 4 < 2)
                assertEquals(
                    FIXTURE_READER_F734AAEA + n,
                    event.getFirst().get(FIXTURE_ACTORUSERNAME_538489F0).getAsString());
              else assertFalse(event.getFirst().has(FIXTURE_ACTORUSERNAME_538489F0));
              return null;
            });
      }
      synchronized (h.success) {
        synchronized (h.failure) {
          for (var future : pool.invokeAll(jobs)) future.get(30, TimeUnit.SECONDS);
        }
      }
      assertEquals(100, h.log.events.size());
      assertEquals(100, h.ids.get());
      assertEquals(0, rows());
    }
  }

  @Test
  void web120SuccessResponseFailureDoesNotInventRollback() throws Exception {
    try (var h = new Harness()) {
      var initial = h.adapter.createSession();
      String old = initial.getId();
      var api =
          new SessionFormLoginTest.Api(
              FIXTURE_0000_876EEFE0, FIXTURE_USER_2DED8884, FIXTURE_0000_876EEFE0, 0);
      var response = brokenHeader(FIXTURE_LOCATION_FB077BAD);
      assertThrows(
          IllegalStateException.class,
          () ->
              h.run(
                  api,
                  form(
                      new Cookie(FIXTURE_SCHUBERT_NK_SESSION_DD9EE5FF, old),
                      initial.getAttribute("csrfToken")),
                  response,
                  (r, s) -> fail("not reached")));
      assertNotEquals(302, response.getStatus());
      assertNull(h.adapter.findById(old));
      assertEquals(1, rows());
      assertEquals(2, h.f.ids.get());
      // Independent deterministic random fixture: third32-byte allocation is the new cookie.
      byte[] bytes = new byte[32];
      Arrays.fill(bytes, (byte) 3);
      String current = Base64.getUrlEncoder().withoutPadding().encodeToString(bytes);
      var restored = Objects.requireNonNull(h.adapter.findById(current));
      SessionPrincipal p = restored.getAttribute(FIXTURE_PRINCIPAL_590C90CB);
      assertEquals(FIXTURE_READER_F734AAEA, p.username());
      var retry = form(new Cookie(FIXTURE_SCHUBERT_NK_SESSION_DD9EE5FF, current), null);
      retry.setMethod("GET");
      retry.setRequestURI("/");
      var success = new MockHttpServletResponse();
      h.run(
          api,
          retry,
          success,
          (r, s) ->
              h.success.onAuthenticationSuccess(
                  (HttpServletRequest) r,
                  (HttpServletResponse) s,
                  SecurityContextHolder.getContext().getAuthentication()));
      assertEquals(302, success.getStatus());
      assertEquals("/", success.getHeader(FIXTURE_LOCATION_FB077BAD));
      assertEquals(2, h.f.ids.get());
      assertEquals(1, api.sends.get());
      assertEquals(1, rows());
      assertNull(SecurityContextHolder.getContext().getAuthentication());
      api.erased();
    }
  }

  private static MockHttpServletResponse brokenHeader(String name) {
    return new MockHttpServletResponse() {
      @Override
      public void setHeader(String key, String value) {
        if (name.equals(key)) throw new IllegalStateException("synthetic-header");
        super.setHeader(key, value);
      }
    };
  }

  private static SessionPrincipal principal(String name, String role) {
    return new SessionPrincipal(
        name, UserRole.valueOf(role), AuthenticationContext.of("a".repeat(64)), NOW);
  }

  private static Authentication auth(SessionPrincipal p) {
    return UsernamePasswordAuthenticationToken.authenticated(
        p, null, List.of(new SimpleGrantedAuthority("ROLE_" + p.role().wireValue())));
  }

  private static BadCredentialsException secretBadCredentials() {
    return new BadCredentialsException("private-password") {
      @Override
      public String getMessage() {
        throw new AssertionError("diagnostic read");
      }

      @Override
      public Throwable getCause() {
        throw new AssertionError("cause read");
      }
    };
  }

  private static MockHttpServletRequest form(Cookie cookie, String csrf) {
    var r = new MockHttpServletRequest("POST", "/login");
    r.setCharacterEncoding(StandardCharsets.UTF_8);
    r.setContentType("application/x-www-form-urlencoded");
    r.setRemoteAddr("127.0.0.1");
    r.addHeader("X-Forwarded-For", "203.0.113.1");
    r.addHeader("X-Forwarded-Proto", "https");
    r.addParameter("username", FIXTURE_READER_F734AAEA);
    r.addParameter("password", "p");
    if (cookie != null) r.setCookies(cookie);
    if (csrf != null) r.addParameter("_csrf", csrf);
    return r;
  }

  private static long rows() throws Exception {
    try (var c = db.web();
        var s = c.createStatement();
        var r = s.executeQuery("select count(*) from schubert_web_session.web_http_sessions")) {
      assertTrue(r.next());
      return r.getLong(1);
    }
  }

  private static final class Harness implements AutoCloseable {
    final Fixture f = new Fixture(db);
    final SpringEncryptedSessionRepository adapter;
    final EncryptedSessionSecurityContextRepository contexts;
    final EncryptedSessionRequestCache cache;
    final Log log = new Log();
    final WebSecurityAudit audit =
        new WebSecurityAudit(log, Clock.fixed(NOW, ZoneOffset.UTC), "pt", "pt");
    final AtomicInteger ids = new AtomicInteger();
    final CaddyTransportContextFilter transport =
        new CaddyTransportContextFilter(
            () -> new UUID(0, ids.incrementAndGet()), new CaddyClientAddressResolver(), audit);
    final MqLoginSuccessHandler success;
    final MqLoginFailureHandler failure = new MqLoginFailureHandler(audit);

    Harness() {
      f.clock.value = Instant.now();
      adapter = new SpringEncryptedSessionRepository(f.repository, f.clock);
      contexts = new EncryptedSessionSecurityContextRepository(adapter);
      cache = new EncryptedSessionRequestCache(adapter);
      success = new MqLoginSuccessHandler(contexts, cache, audit);
    }

    MockHttpServletRequest request(SessionPrincipal p, String saved) throws Exception {
      var r = form(null, null);
      r.setAttribute(SessionRepositoryFilter.SESSION_REPOSITORY_ATTR, adapter);
      if (p != null || saved != null) {
        var session = new MockHttpSession();
        if (p != null) session.setAttribute(FIXTURE_PRINCIPAL_590C90CB, p);
        if (saved != null) session.setAttribute(FIXTURE_SAVEDREQUEST_50131C2B, saved);
        r.setSession(session);
      }
      transport.doFilter(r, new MockHttpServletResponse(), (r1, s1) -> {});
      return r;
    }

    void run(
        SessionFormLoginTest.Api api,
        MockHttpServletRequest request,
        MockHttpServletResponse response,
        FilterChain business)
        throws Exception {
      var login = new MqFormLoginFilterFactory().create(api.provider, contexts, success, failure);
      var session = new WebSessionFilterFactory().create(adapter);
      var holder = new SecurityContextHolderFilter(contexts);
      var csrf =
          new WebCsrfFilterFactory()
              .create(new EncryptedSessionCsrfTokenRepository(), new WebCsrfDeniedHandler(audit));
      new WebSecurityHeaderFilterFactory()
          .create()
          .doFilter(
              request,
              response,
              (r1, s1) ->
                  transport.doFilter(
                      r1,
                      s1,
                      (r2, s2) ->
                          session.doFilter(
                              r2,
                              s2,
                              (r3, s3) ->
                                  holder.doFilter(
                                      r3,
                                      s3,
                                      (r4, s4) ->
                                          csrf.doFilter(
                                              r4,
                                              s4,
                                              (r5, s5) -> login.doFilter(r5, s5, business))))));
    }

    @Override
    public void close() {
      f.close();
    }
  }

  static final class Log implements Logger {
    final List<JsonObject> events = new CopyOnWriteArrayList<>();
    boolean fail;

    @Override
    public String getName() {
      return "synthetic.login.security";
    }

    @Override
    public boolean isLoggable(Level level) {
      return true;
    }

    @Override
    public void log(Level level, ResourceBundle bundle, String message, Throwable thrown) {
      fail("secret throwable");
    }

    @Override
    public void log(Level level, ResourceBundle bundle, String format, Object... params) {
      if (fail) throw new IllegalStateException("synthetic-logger");
      assertNull(bundle);
      assertNull(params);
      events.add(JsonParser.parseString(format).getAsJsonObject());
    }
  }
}
