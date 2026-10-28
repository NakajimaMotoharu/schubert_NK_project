package dev.codex.schubert.nk.web.session;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.layout.semantic.UserRole;
import dev.codex.schubert.nk.web.logging.WebLogDatabaseFixture;
import dev.codex.schubert.nk.web.security.EncryptedSessionCsrfTokenRepository;
import dev.codex.schubert.nk.web.security.FormCsrfTokenRequestHandler;
import dev.codex.schubert.nk.web.security.WebCsrfFilterFactory;
import dev.codex.schubert.nk.web.session.EncryptedWebSessionRepositoryTest.Fixture;
import jakarta.servlet.FilterChain;
import jakarta.servlet.http.Cookie;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import jakarta.servlet.http.HttpSession;
import java.nio.file.Path;
import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.Objects;
import java.util.concurrent.Callable;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;
import org.springframework.mock.web.MockHttpServletRequest;
import org.springframework.mock.web.MockHttpServletResponse;
import org.springframework.mock.web.MockHttpSession;
import org.springframework.security.web.csrf.CsrfToken;
import org.springframework.security.web.csrf.DefaultCsrfToken;

/** NK-WEB-001/PT-WEB-050..053; FUN-001/AUT-001..004; UI226; SS313/314/351/352; PG-D-100. */
class WebCsrfIntegrationTest {
  private static final String FIXTURE_CSRF_A082304B = "_csrf";
  private static final String FIXTURE_X_CSRF_TOKEN_E54F0E3F = "X-CSRF-TOKEN";
  private static final String FIXTURE_CSRFTOKEN_CF3CFD11 = "csrfToken";
  private static final String FIXTURE_QUESTIONS_NEW_F89B3C4E = "/questions/new";
  private static final String FIXTURE_POST_E46D3AE9 = "POST";
  private static WebLogDatabaseFixture db;
  private static final String TOKEN = "02".repeat(32);
  private static final SessionPrincipal PRINCIPAL =
      new SessionPrincipal(
          "reader",
          UserRole.USER,
          AuthenticationContext.of("b".repeat(64)),
          Instant.parse("2026-09-08T00:00:00Z"));

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

  @Test
  void web050RepositoryPersistsGeneratesAndInvalidates() throws Exception {
    var csrf = new EncryptedSessionCsrfTokenRepository();
    try (var f = fixture()) {
      var repository = adapter(f);
      var filter = new WebSessionFilterFactory().create(repository);
      filter.doFilter(
          request("GET", "/login", null, null),
          new MockHttpServletResponse(),
          (req, res) -> {
            var r = (HttpServletRequest) req;
            var s = (HttpServletResponse) res;
            assertNull(csrf.loadToken(r));
            var token = csrf.generateToken(r);
            assertEquals(TOKEN, token.getToken());
            assertEquals(FIXTURE_CSRF_A082304B, token.getParameterName());
            assertEquals(FIXTURE_X_CSRF_TOKEN_E54F0E3F, token.getHeaderName());
            csrf.saveToken(token, r, s);
            String firstId = r.getSession().getId();
            assertEquals(TOKEN, Objects.requireNonNull(csrf.loadToken(r)).getToken());
            for (CsrfToken bad :
                List.of(
                    new DefaultCsrfToken("wrong", FIXTURE_CSRF_A082304B, TOKEN),
                    new DefaultCsrfToken(FIXTURE_X_CSRF_TOKEN_E54F0E3F, "wrong", TOKEN),
                    new DefaultCsrfToken(
                        FIXTURE_X_CSRF_TOKEN_E54F0E3F, FIXTURE_CSRF_A082304B, "03".repeat(32))))
              unavailable(() -> csrf.saveToken(bad, r, s));
            var rotated = csrf.generateToken(r);
            assertEquals("04".repeat(32), rotated.getToken());
            assertNotEquals(firstId, r.getSession().getId());
            csrf.saveToken(rotated, r, s);
            r.getSession().setAttribute("principal", PRINCIPAL);
            var afterLogin = csrf.generateToken(r);
            assertEquals("08".repeat(32), afterLogin.getToken());
            assertEquals(PRINCIPAL, r.getSession().getAttribute("principal"));
            csrf.saveToken(null, r, s);
            assertNull(r.getSession(false));
            assertNull(csrf.loadToken(r));
            csrf.saveToken(null, r, s);
            unavailable(() -> csrf.saveToken(afterLogin, r, s));
          });
      assertEquals(0, count());
    }
    var r = new MockHttpServletRequest();
    var s = new MockHttpServletResponse();
    assertThrows(NullPointerException.class, () -> csrf.generateToken(null));
    assertThrows(NullPointerException.class, () -> csrf.loadToken(null));
    assertThrows(NullPointerException.class, () -> csrf.saveToken(null, null, s));
    assertThrows(NullPointerException.class, () -> csrf.saveToken(null, r, null));
    assertNull(csrf.loadToken(r));
    r.getSession().setAttribute(FIXTURE_CSRFTOKEN_CF3CFD11, List.of("bad"));
    unavailable(() -> csrf.loadToken(r));
    r.getSession().setAttribute(FIXTURE_CSRFTOKEN_CF3CFD11, "bad");
    unavailable(() -> csrf.loadToken(r));
    unavailable(() -> csrf.generateToken(r));
    r.getSession().removeAttribute(FIXTURE_CSRFTOKEN_CF3CFD11);
    assertNull(csrf.loadToken(r));
    unavailable(() -> csrf.generateToken(r));
    var nullSession =
        new MockHttpServletRequest() {
          @Override
          public HttpSession getSession(boolean create) {
            return null;
          }
        };
    assertThrows(NullPointerException.class, () -> csrf.generateToken(nullSession));
  }

  @Test
  void web051OnlySingleBodyParameterResolves() {
    var handler = new FormCsrfTokenRequestHandler();
    var token = new DefaultCsrfToken(FIXTURE_X_CSRF_TOKEN_E54F0E3F, FIXTURE_CSRF_A082304B, TOKEN);
    var r = new MockHttpServletRequest();
    var s = new MockHttpServletResponse();
    var calls = new AtomicInteger();
    handler.handle(
        r,
        s,
        () -> {
          calls.incrementAndGet();
          return token;
        });
    assertEquals(0, calls.get());
    assertSame(r.getAttribute(FIXTURE_CSRF_A082304B), r.getAttribute(CsrfToken.class.getName()));
    assertEquals(TOKEN, ((CsrfToken) r.getAttribute(FIXTURE_CSRF_A082304B)).getToken());
    assertEquals(1, calls.get());
    assertThrows(NullPointerException.class, () -> handler.handle(null, s, () -> token));
    assertThrows(NullPointerException.class, () -> handler.handle(r, null, () -> token));
    assertThrows(NullPointerException.class, () -> handler.handle(r, s, null));
    assertThrows(NullPointerException.class, () -> handler.resolveCsrfTokenValue(null, token));
    assertThrows(NullPointerException.class, () -> handler.resolveCsrfTokenValue(r, null));
    assertNull(handler.resolveCsrfTokenValue(r, token));
    r.addHeader(FIXTURE_X_CSRF_TOKEN_E54F0E3F, TOKEN);
    assertNull(handler.resolveCsrfTokenValue(r, token));
    for (String value : List.of("a".repeat(64), "z".repeat(128))) {
      r.setParameter(FIXTURE_CSRF_A082304B, value);
      assertEquals(value, handler.resolveCsrfTokenValue(r, token));
    }
    for (String value :
        List.of("", "a".repeat(63), "a".repeat(129), "!".repeat(64), "日本語", "a".repeat(63) + " ")) {
      r.setParameter(FIXTURE_CSRF_A082304B, value);
      assertNull(handler.resolveCsrfTokenValue(r, token));
    }
    for (String[] values :
        List.of(new String[0], new String[] {null}, new String[] {TOKEN, TOKEN})) {
      var malformed =
          new MockHttpServletRequest() {
            @Override
            public String[] getParameterValues(String name) {
              return values;
            }
          };
      assertNull(handler.resolveCsrfTokenValue(malformed, token));
    }
    r.setParameter(FIXTURE_CSRF_A082304B, TOKEN);
    for (String query : List.of("_csrf=x", "x=1&_csrf", "%5Fcsrf=x", "_c%73rf=x", "%GG=x", "%=x")) {
      r.setQueryString(query);
      assertNull(handler.resolveCsrfTokenValue(r, token));
    }
    for (String query :
        List.of("", "&&", "q=_csrf", "q=../", "q=%GG", "+_csrf=x", "_CSRF=x", "q=a+b")) {
      r.setQueryString(query);
      assertEquals(TOKEN, handler.resolveCsrfTokenValue(r, token));
      assertEquals(query, r.getQueryString());
    }
  }

  @Test
  void web054RotationResultMustMatchNewObservedSession() {
    var csrf = new EncryptedSessionCsrfTokenRepository();
    for (int variant = 0; variant < 4; variant++) {
      int fault = variant;
      var original = new MockHttpSession(null, "independent-old-id");
      original.setAttribute(FIXTURE_CSRFTOKEN_CF3CFD11, TOKEN);
      var rotated = new MockHttpSession(null, "independent-new-id");
      rotated.setAttribute(FIXTURE_CSRFTOKEN_CF3CFD11, TOKEN);
      var request =
          new MockHttpServletRequest() {
            private boolean called;

            @Override
            public HttpSession getSession(boolean create) {
              if (!called) return original;
              return fault == 1 ? null : fault == 3 ? original : rotated;
            }

            @Override
            public String changeSessionId() {
              called = true;
              return fault == 0
                  ? null
                  : fault == 2
                      ? "independent-other-id"
                      : fault == 3 ? "independent-old-id" : "independent-new-id";
            }
          };
      unavailable(() -> csrf.generateToken(request));
      assertEquals(TOKEN, original.getAttribute(FIXTURE_CSRFTOKEN_CF3CFD11));
      assertEquals(TOKEN, rotated.getAttribute(FIXTURE_CSRFTOKEN_CF3CFD11));
    }
    var unknown = new AssertionError("rotation unknown");
    var request =
        new MockHttpServletRequest() {
          @Override
          public String changeSessionId() {
            throw unknown;
          }
        };
    request.getSession().setAttribute(FIXTURE_CSRFTOKEN_CF3CFD11, TOKEN);
    assertSame(unknown, assertThrows(AssertionError.class, () -> csrf.generateToken(request)));
  }

  @Test
  void web052EveryPostRejectsBeforeBusinessWithoutCsrf() throws Exception {
    try (var f = fixture()) {
      var repo = adapter(f);
      var initial = repo.createSession();
      var cookie = new Cookie("SCHUBERT_NK_SESSION", initial.getId());
      for (String target :
          List.of(
              "/login",
              "/logout",
              "/admin/users/new",
              "/admin/users/1?STATUS",
              "/admin/users/1?ROLE",
              "/admin/users/1?PASSWORD",
              "/admin/users/1?UNLOCK",
              FIXTURE_QUESTIONS_NEW_F89B3C4E,
              "/notifications/1?CANCEL",
              "/questions/1?DELETE")) {
        String[] parts = target.split("\\?", 2);
        for (int variant = 0; variant < 7; variant++) {
          var request =
              request(
                  FIXTURE_POST_E46D3AE9,
                  parts[0],
                  cookie,
                  variant == 0
                      ? new String[] {TOKEN}
                      : variant == 1
                          ? null
                          : variant == 2
                              ? new String[] {"03".repeat(32)}
                              : variant == 3
                                  ? new String[] {TOKEN, TOKEN}
                                  : variant == 4 ? new String[] {""} : new String[] {TOKEN});
          if (parts.length == 2) request.setParameter("operation", parts[1]);
          if (variant == 1) request.addHeader(FIXTURE_X_CSRF_TOKEN_E54F0E3F, TOKEN);
          if (variant == 5) request.setQueryString("_csrf=" + TOKEN);
          if (variant == 6) request.setQueryString("%5fcsrf=" + TOKEN);
          verify(f, request, variant == 0);
        }
      }
      for (String method : List.of("GET", "HEAD", "OPTIONS", "TRACE"))
        verify(f, request(method, "/logs", cookie, null), true);
      for (String method : List.of("PUT", "DELETE", "PATCH"))
        verify(f, request(method, "/questions/1", cookie, null), false);
      assertEquals(1, count());
      var factory = new WebCsrfFilterFactory();
      assertThrows(NullPointerException.class, () -> factory.create(null, (r, s, e) -> {}));
      assertThrows(
          NullPointerException.class,
          () -> factory.create(new EncryptedSessionCsrfTokenRepository(), null));
    }
  }

  @Test
  void web053FixationExpiryFaultsAndConcurrentRequestsStayBound() throws Exception {
    try (var f = fixture();
        var pool = Executors.newFixedThreadPool(10)) {
      var repo = adapter(f);
      var original = repo.createSession();
      var cookie = new Cookie("SCHUBERT_NK_SESSION", original.getId());
      var another = repo.createSession();
      verify(
          f,
          request(FIXTURE_POST_E46D3AE9, "/logout", cookie, new String[] {"04".repeat(32)}),
          false);
      original.setAttribute("principal", PRINCIPAL);
      var authenticated = new Cookie("SCHUBERT_NK_SESSION", original.getId());
      verify(
          f,
          request(
              FIXTURE_POST_E46D3AE9,
              FIXTURE_QUESTIONS_NEW_F89B3C4E,
              authenticated,
              new String[] {TOKEN}),
          false);
      verify(
          f,
          request(
              FIXTURE_POST_E46D3AE9,
              FIXTURE_QUESTIONS_NEW_F89B3C4E,
              authenticated,
              new String[] {"06".repeat(32)}),
          true);
      var jobs = new ArrayList<Callable<Void>>();
      for (int i = 0; i < 100; i++)
        jobs.add(
            () -> {
              verify(
                  f,
                  request(
                      FIXTURE_POST_E46D3AE9,
                      FIXTURE_QUESTIONS_NEW_F89B3C4E,
                      authenticated,
                      new String[] {"06".repeat(32)}),
                  true);
              return null;
            });
      for (var future : pool.invokeAll(jobs)) future.get(30, TimeUnit.SECONDS);
      assertEquals(
          List.of(),
          Objects.requireNonNull(repo.findById(original.getId())).getAttribute("operationTokens"));
      for (String fault : List.of("open", "connection.commit", "connection.close")) {
        f.failure = fault;
        unavailable(
            () ->
                verify(
                    f,
                    request(
                        FIXTURE_POST_E46D3AE9,
                        FIXTURE_QUESTIONS_NEW_F89B3C4E,
                        authenticated,
                        new String[] {"06".repeat(32)}),
                    true));
        f.failure = "";
      }
      f.clock.value = Instant.now().plusSeconds(28801);
      verify(
          f,
          request(
              FIXTURE_POST_E46D3AE9,
              FIXTURE_QUESTIONS_NEW_F89B3C4E,
              authenticated,
              new String[] {"06".repeat(32)}),
          false);
      assertNull(repo.findById(original.getId()));
      repo.deleteById(another.getId());
      f.codec.close();
      unavailable(() -> verify(f, request(FIXTURE_POST_E46D3AE9, "/login", null, null), false));
    }
  }

  private static Fixture fixture() {
    var f = new Fixture(db);
    f.clock.value = Instant.now();
    return f;
  }

  private static SpringEncryptedSessionRepository adapter(Fixture f) {
    return new SpringEncryptedSessionRepository(f.repository, f.clock);
  }

  private static MockHttpServletRequest request(
      String method, String path, Cookie cookie, String[] values) {
    var r = new MockHttpServletRequest(method, path);
    r.setSecure(true);
    r.setContentType("application/x-www-form-urlencoded");
    if (cookie != null) r.setCookies(cookie);
    if (values != null) r.setParameter(FIXTURE_CSRF_A082304B, values);
    return r;
  }

  private static void verify(Fixture f, MockHttpServletRequest request, boolean allowed)
      throws Exception {
    var business = new AtomicInteger();
    var denied = new AtomicInteger();
    var response = new MockHttpServletResponse();
    var csrf =
        new WebCsrfFilterFactory()
            .create(
                new EncryptedSessionCsrfTokenRepository(),
                (r, s, e) -> {
                  denied.incrementAndGet();
                  s.setStatus(403);
                  s.getWriter().write("CSRF rejected");
                });
    FilterChain terminal = (r, s) -> business.incrementAndGet();
    new WebSessionFilterFactory()
        .create(adapter(f))
        .doFilter(request, response, (r, s) -> csrf.doFilter(r, s, terminal));
    assertEquals(allowed ? 1 : 0, business.get());
    assertEquals(allowed ? 0 : 1, denied.get());
    assertEquals(allowed ? 200 : 403, response.getStatus());
    assertEquals(allowed ? "" : "CSRF rejected", response.getContentAsString());
  }

  private static int count() throws Exception {
    try (var c = db.web();
        var s = c.createStatement();
        var r = s.executeQuery("select count(*) from schubert_web_session.web_http_sessions")) {
      assertTrue(r.next());
      return r.getInt(1);
    }
  }

  private static void unavailable(org.junit.jupiter.api.function.Executable action) {
    var error = assertThrows(SessionStoreException.class, action);
    assertEquals("session storage is unavailable", error.getMessage());
    assertNull(error.getCause());
    assertEquals(0, error.getSuppressed().length);
  }
}
