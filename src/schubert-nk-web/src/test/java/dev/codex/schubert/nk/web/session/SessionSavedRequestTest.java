package dev.codex.schubert.nk.web.session;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.layout.semantic.UserRole;
import dev.codex.schubert.nk.web.logging.WebLogDatabaseFixture;
import dev.codex.schubert.nk.web.security.EncryptedSessionRequestCache;
import dev.codex.schubert.nk.web.security.SavedScreenTarget;
import dev.codex.schubert.nk.web.session.EncryptedWebSessionRepositoryTest.Fixture;
import jakarta.servlet.http.Cookie;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import java.nio.charset.StandardCharsets;
import java.nio.file.Path;
import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Objects;
import java.util.concurrent.Callable;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.function.Executable;
import org.junit.jupiter.api.io.TempDir;
import org.springframework.mock.web.MockHttpServletRequest;
import org.springframework.mock.web.MockHttpServletResponse;
import org.springframework.mock.web.MockHttpSession;
import org.springframework.session.web.http.SessionRepositoryFilter;

/** NK-WEB-001/PT-WEB-076..081; FUN-001/AUT-001..004; UI221/226; SS313/314/352; PG-D-104. */
class SessionSavedRequestTest {
  private static WebLogDatabaseFixture db;
  private static final List<String> SCREENS =
      List.of(
          "/",
          "/search",
          "/scenarios",
          "/scenarios/NUKITASHI1",
          "/scenarios/NUKITASHI2/SS",
          "/scenarios/123",
          "/animation",
          "/animation/main",
          "/animation/ova",
          "/animation/opening",
          "/animation/videos/main-01",
          "/music",
          "/music/曲",
          "/music/曲/OP",
          "/music/%E6%9B%B2/OP",
          "/logs",
          "/admin/users",
          "/admin/users/new",
          "/admin/users/123",
          "/questions/new",
          "/questions/accepted/00000000-0000-0000-0000-000000000001",
          "/notifications",
          "/notifications/42",
          "/questions",
          "/questions/23");
  private static final SessionPrincipal PRINCIPAL =
      new SessionPrincipal(
          "reader",
          UserRole.USER,
          AuthenticationContext.of("a".repeat(64)),
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
  void web076AllScreenRoutesAndUtf8BoundariesAreExplicit() {
    for (String path : SCREENS) {
      for (String query :
          List.of(
              "",
              "?",
              "?q=日本語&page=2",
              "?q=../x%2Fy%20z&speaker=名前",
              "?=x&&q=token%3Dvalue",
              "?q=a?b;c%3Bd")) {
        var target = SavedScreenTarget.fromGet("GET", path + query);
        assertEquals(path + query, target.location());
        assertEquals("SavedScreenTarget[REDACTED]", target.toString());
      }
    }
    for (int bytes : new int[] {2047, 2048}) {
      String target = "/search?q=あ" + "a".repeat(bytes - 13);
      assertEquals(bytes, target.getBytes(StandardCharsets.UTF_8).length);
      assertEquals(target, SavedScreenTarget.fromGet("GET", target).location());
    }
    invalid("GET", "/search?q=あ" + "a".repeat(2036));
    assertThrows(NullPointerException.class, () -> SavedScreenTarget.fromGet(null, "/"));
    assertThrows(NullPointerException.class, () -> SavedScreenTarget.fromGet("GET", null));
  }

  @Test
  void web077UnsafeMethodsEndpointsAndSecretQueriesNeverSave() throws Exception {
    var invalidTargets =
        List.of(
            "",
            "https://outside/search",
            "//outside/search",
            "/search#fragment",
            "/../search",
            "/scenarios/%2e%2e",
            "/scenarios/%2fanything",
            "/search?q=%GG",
            "/search?q=\uD800",
            "/search?q=\n",
            "/login",
            "/error",
            "/css/schubert.css",
            "/js/search-speaker-submit.js",
            "/js/log-search-validation.js",
            "/actuator/health",
            "/logout",
            "/audio/1",
            "/audio/1/download",
            "/animation/media/1",
            "/music/media/1",
            "/music/download/1",
            "/missing",
            "/scenarios/x;jsessionid=synthetic",
            "/scenarios/x%3Bjsessionid=synthetic",
            "/scenarios/x%3bjsessionid=synthetic",
            "/music/曲/OP;jsessionid=synthetic",
            "/admin/other",
            "/animation/unknown",
            "/scenarios/a/b/c",
            "/questions/accepted/x/y");
    for (String target : invalidTargets) invalid("GET", target);
    for (String method :
        List.of("POST", "HEAD", "PUT", "DELETE", "OPTIONS", "TRACE", "PATCH", "get", ""))
      invalid(method, "/search");
    for (String key :
        List.of(
            "password",
            "PASSWORD",
            "%70assword",
            "PasswordConfirmation",
            "JSESSIONID",
            "j%73essionid",
            "SCHUBERT_NK_SESSION",
            "confirmPassword",
            "_csrf",
            "%5fcsrf",
            "csrf",
            "csrfToken",
            "operationToken",
            "authenticationContext",
            "authenticationContextId",
            "session",
            "sessionId",
            "token")) {
      invalid("GET", "/search?" + key + "=private-value");
      invalid("GET", "/search?q=normal&" + key);
    }
    try (var f = new Fixture(db)) {
      var adapter = adapter(f);
      var cache = new EncryptedSessionRequestCache(adapter);
      for (String target : invalidTargets) {
        var r = marked(adapter, request("GET", target, null));
        cache.saveRequest(r, new MockHttpServletResponse());
        assertNull(r.getSession(false));
      }
      for (String method : List.of("POST", "HEAD", "PUT", "DELETE")) {
        var r = marked(adapter, request(method, "/search", null));
        r.setContent("password=synthetic-not-saved".getBytes(StandardCharsets.UTF_8));
        cache.saveRequest(r, new MockHttpServletResponse());
        assertNull(r.getSession(false));
      }
      var ajax = marked(adapter, request("GET", "/search?q=valid", null));
      ajax.addHeader("X-Requested-With", "XMLHttpRequest");
      cache.saveRequest(ajax, new MockHttpServletResponse());
      assertNull(ajax.getSession(false));
      assertEquals(0, count());
    }
  }

  @Test
  void web078EncryptedCacheContainsOnlyClosedGetProjection() throws Exception {
    try (var f = new Fixture(db)) {
      f.clock.value = Instant.now();
      var adapter = adapter(f);
      var cache = new EncryptedSessionRequestCache(adapter);
      var filter = new WebSessionFilterFactory().create(adapter);
      var response = new MockHttpServletResponse();
      var initial = request("GET", "/search?q=日本語&page=2", null);
      initial.addHeader("Host", "outside.example");
      initial.addHeader("X-Private", "synthetic-header");
      initial.addPreferredLocale(Locale.FRENCH);
      initial.addParameter("q", "日本語");
      initial.setContent("synthetic-body-never-replayed".getBytes(StandardCharsets.UTF_8));
      filter.doFilter(
          initial,
          response,
          (req, res) -> {
            var r = (HttpServletRequest) req;
            var out = (HttpServletResponse) res;
            assertNull(cache.getRequest(r, out));
            cache.saveRequest(r, out);
            assertEquals("/search?q=日本語&page=2", r.getSession().getAttribute("savedRequest"));
            assertNull(r.getSession().getAttribute("SPRING_SECURITY_SAVED_REQUEST"));
            var saved = Objects.requireNonNull(cache.getRequest(r, out));
            assertEquals("GET", saved.getMethod());
            assertEquals("/search?q=日本語&page=2", saved.getRedirectUrl());
            assertEquals(List.of(), saved.getCookies());
            assertEquals(List.of(), saved.getHeaderNames());
            assertEquals(List.of(), saved.getHeaderValues("X-Private"));
            assertEquals(List.of(), saved.getLocales());
            assertNull(saved.getParameterValues("q"));
            assertEquals(Map.of(), saved.getParameterMap());
            assertEquals("SavedGet[REDACTED]", saved.toString());
            assertThrows(NullPointerException.class, () -> saved.getHeaderValues(null));
            assertThrows(NullPointerException.class, () -> saved.getParameterValues(null));
            assertThrows(
                UnsupportedOperationException.class,
                () -> saved.getCookies().add(new Cookie("bad", "bad")));
            assertThrows(
                UnsupportedOperationException.class, () -> saved.getHeaderNames().add("bad"));
            assertThrows(
                UnsupportedOperationException.class, () -> saved.getLocales().add(Locale.ROOT));
            assertThrows(
                UnsupportedOperationException.class,
                () -> saved.getParameterMap().put("q", new String[] {"bad"}));
          });
      var issued = Objects.requireNonNull(response.getCookie("SCHUBERT_NK_SESSION"));
      assertTrue(issued.getSecure());
      assertTrue(issued.isHttpOnly());
      assertEquals("Lax", issued.getAttribute("SameSite"));
      var second = new MockHttpServletResponse();
      filter.doFilter(
          request("POST", "/login", issued),
          second,
          (req, res) -> {
            var r = (HttpServletRequest) req;
            var out = (HttpServletResponse) res;
            r.getSession().setAttribute("principal", PRINCIPAL);
            assertEquals(
                "/search?q=日本語&page=2",
                Objects.requireNonNull(cache.getRequest(r, out)).getRedirectUrl());
            cache.saveRequest(r, out); // POST does not overwrite the prior safe GET.
            assertEquals(
                "/search?q=日本語&page=2",
                Objects.requireNonNull(cache.getRequest(r, out)).getRedirectUrl());
            cache.removeRequest(r, out);
            assertNull(cache.getRequest(r, out));
          });
      assertNotEquals(
          issued.getValue(),
          Objects.requireNonNull(second.getCookie("SCHUBERT_NK_SESSION")).getValue());
      assertNull(adapter.findById(issued.getValue()));
      assertEquals(1, count());
    }
  }

  @Test
  void web079MatchingConsumesOnlyExactCurrentGetWithoutReplay() throws Exception {
    try (var f = new Fixture(db)) {
      f.clock.value = Instant.now();
      var adapter = adapter(f);
      var cache = new EncryptedSessionRequestCache(adapter);
      var initial = adapter.createSession();
      initial.setAttribute("savedRequest", "/search?q=abc&page=2");
      var filter = new WebSessionFilterFactory().create(adapter);
      var cookie = new Cookie("SCHUBERT_NK_SESSION", initial.getId());
      for (String target :
          List.of(
              "/search?q=abc&page=3",
              "/search?page=2&q=abc",
              "/search?q=ABC&page=2",
              "/",
              "/search?q=abc&page=2&",
              "/audio/1")) {
        filter.doFilter(
            request("GET", target, cookie),
            new MockHttpServletResponse(),
            (req, res) -> {
              var r = (HttpServletRequest) req;
              var out = (HttpServletResponse) res;
              assertNull(cache.getMatchingRequest(r, out));
              assertNotNull(cache.getRequest(r, out));
            });
      }
      filter.doFilter(
          request("POST", "/search?q=abc&page=2", cookie),
          new MockHttpServletResponse(),
          (req, res) -> {
            assertNull(
                cache.getMatchingRequest((HttpServletRequest) req, (HttpServletResponse) res));
            assertNotNull(cache.getRequest((HttpServletRequest) req, (HttpServletResponse) res));
          });
      var exact = request("GET", "/search?q=abc&page=2", cookie);
      exact.addHeader("X-Fresh", "fresh");
      exact.addParameter("q", "abc");
      filter.doFilter(
          exact,
          new MockHttpServletResponse(),
          (req, res) -> {
            var r = (HttpServletRequest) req;
            var out = (HttpServletResponse) res;
            var matched = cache.getMatchingRequest(r, out);
            assertSame(r, matched);
            assertEquals("fresh", matched.getHeader("X-Fresh"));
            assertEquals("abc", matched.getParameter("q"));
            assertNull(cache.getRequest(r, out));
            assertNull(cache.getMatchingRequest(r, out));
            cache.removeRequest(r, out);
          });
      assertNull(
          Objects.requireNonNull(adapter.findById(initial.getId())).getAttribute("savedRequest"));
      for (String url : List.of("/search", "/search?")) {
        filter.doFilter(
            request("GET", url, cookie),
            new MockHttpServletResponse(),
            (req, res) -> {
              var r = (HttpServletRequest) req;
              var out = (HttpServletResponse) res;
              cache.saveRequest(r, out);
              assertEquals(url, Objects.requireNonNull(cache.getRequest(r, out)).getRedirectUrl());
              assertSame(r, cache.getMatchingRequest(r, out));
            });
      }
    }
  }

  @Test
  void web080NullInvalidSessionAndStorageFailuresAreRedacted() throws Exception {
    try (var f = new Fixture(db)) {
      var adapter = adapter(f);
      var cache = new EncryptedSessionRequestCache(adapter);
      var r = marked(adapter, request("GET", "/search", null));
      var response = new MockHttpServletResponse();
      assertThrows(NullPointerException.class, () -> new EncryptedSessionRequestCache(null));
      assertThrows(NullPointerException.class, () -> cache.saveRequest(null, response));
      assertThrows(NullPointerException.class, () -> cache.getRequest(null, response));
      assertThrows(NullPointerException.class, () -> cache.removeRequest(null, response));
      assertThrows(NullPointerException.class, () -> cache.getMatchingRequest(null, response));
      assertThrows(NullPointerException.class, () -> cache.saveRequest(r, null));
      assertThrows(NullPointerException.class, () -> cache.getRequest(r, null));
      assertThrows(NullPointerException.class, () -> cache.removeRequest(r, null));
      assertThrows(NullPointerException.class, () -> cache.getMatchingRequest(r, null));
      cache.removeRequest(r, response);
      assertNull(r.getSession(false));
      for (var other :
          List.of(new MockHttpServletRequest(), marked(adapter(f), new MockHttpServletRequest()))) {
        unavailable(() -> cache.saveRequest(other, response));
        unavailable(() -> cache.getRequest(other, response));
        unavailable(() -> cache.removeRequest(other, response));
        unavailable(() -> cache.getMatchingRequest(other, response));
        assertNull(other.getSession(false));
      }
      // Public Servlet fault doubles for corrupted container contracts, not private reflection.
      var session = new MockHttpSession();
      r.setSession(session);
      assertNull(cache.getRequest(r, response));
      for (Object bad :
          List.of(
              42,
              List.of("/search"),
              "//outside",
              "/login",
              "/search?password=synthetic",
              "/scenarios/x;jsessionid=synthetic",
              "/search?JSESSIONID=synthetic",
              "/search?SCHUBERT_NK_SESSION=synthetic")) {
        session.setAttribute("savedRequest", bad);
        unavailable(() -> cache.getRequest(r, response));
      }
      for (boolean state : new boolean[] {false, true}) {
        var faulty =
            new MockHttpSession() {
              private RuntimeException fault() {
                return state
                    ? new IllegalStateException("synthetic-private")
                    : new IllegalArgumentException("synthetic-private");
              }

              @Override
              public Object getAttribute(String name) {
                throw fault();
              }

              @Override
              public void setAttribute(String name, Object value) {
                throw fault();
              }

              @Override
              public void removeAttribute(String name) {
                throw fault();
              }
            };
        var injected = marked(adapter, request("GET", "/search", null));
        injected.setSession(faulty);
        unavailable(() -> cache.saveRequest(injected, response));
        unavailable(() -> cache.getRequest(injected, response));
        unavailable(() -> cache.removeRequest(injected, response));
      }
      assertEquals(0, count());
    }
    for (String fault :
        List.of(
            "open", "statement.executeUpdate", "connection.commit", "connection.close", "key")) {
      reset();
      try (var f = new Fixture(db)) {
        f.clock.value = Instant.now();
        var adapter = adapter(f);
        var cache = new EncryptedSessionRequestCache(adapter);
        var initial = adapter.createSession();
        initial.setAttribute("savedRequest", "/logs");
        var response = new MockHttpServletResponse();
        unavailable(
            () ->
                new WebSessionFilterFactory()
                    .create(adapter)
                    .doFilter(
                        request(
                            "GET", "/search", new Cookie("SCHUBERT_NK_SESSION", initial.getId())),
                        response,
                        (req, res) -> {
                          var r = (HttpServletRequest) req;
                          var out = (HttpServletResponse) res;
                          assertNotNull(r.getSession(false));
                          if (fault.equals("key")) f.codec.close();
                          else f.failure = fault;
                          unavailable(() -> cache.saveRequest(r, out));
                          unavailable(() -> cache.removeRequest(r, out));
                          out.setStatus(503);
                        }));
        assertEquals(503, response.getStatus());
        assertNull(response.getCookie("SCHUBERT_NK_SESSION"));
        f.failure = "";
        assertEquals(1, count());
      }
    }
  }

  @Test
  void web081ConcurrentSessionsAndStaleResponsesStayIsolated() throws Exception {
    try (var f = new Fixture(db);
        var pool = Executors.newFixedThreadPool(8)) {
      f.clock.value = Instant.now();
      var adapter = adapter(f);
      var cache = new EncryptedSessionRequestCache(adapter);
      // Allocate sequentially to keep injected sequence fixture deterministic; HTTP operations
      // parallel.
      var ids = new ArrayList<String>();
      for (int i = 0; i < 100; i++) ids.add(adapter.createSession().getId());
      var jobs = new ArrayList<Callable<Void>>();
      for (int i = 0; i < 100; i++) {
        String id = ids.get(i);
        String location = "/search?q=reader" + i;
        jobs.add(
            () -> {
              new WebSessionFilterFactory()
                  .create(adapter)
                  .doFilter(
                      request("GET", location, new Cookie("SCHUBERT_NK_SESSION", id)),
                      new MockHttpServletResponse(),
                      (req, res) -> {
                        var r = (HttpServletRequest) req;
                        var out = (HttpServletResponse) res;
                        cache.saveRequest(r, out);
                        assertEquals(
                            location,
                            Objects.requireNonNull(cache.getRequest(r, out)).getRedirectUrl());
                      });
              return null;
            });
      }
      synchronized (cache) {
        for (var task : pool.invokeAll(jobs)) task.get(20, TimeUnit.SECONDS);
      }
      for (int i = 0; i < 100; i++)
        assertEquals(
            "/search?q=reader" + i,
            Objects.requireNonNull(adapter.findById(ids.get(i))).getAttribute("savedRequest"));
      assertEquals(100, count());
      String first = ids.getFirst();
      var response = new MockHttpServletResponse();
      unavailable(
          () ->
              new WebSessionFilterFactory()
                  .create(adapter)
                  .doFilter(
                      request("GET", "/search?q=reader0", new Cookie("SCHUBERT_NK_SESSION", first)),
                      response,
                      (req, res) -> {
                        var r = (HttpServletRequest) req;
                        var out = (HttpServletResponse) res;
                        assertNotNull(cache.getRequest(r, out));
                        adapter.deleteById(first);
                        unavailable(() -> cache.saveRequest(r, out));
                        unavailable(() -> cache.removeRequest(r, out));
                      }));
      assertNull(response.getCookie("SCHUBERT_NK_SESSION"));
      assertEquals(99, count());
      var original = Objects.requireNonNull(adapter.findById(ids.get(1)));
      original.setAttribute("operationTokens", SessionAttributeCodecTest.tokens(2));
      original.setAttribute("principal", PRINCIPAL);
      String csrf = original.getAttribute("csrfToken");
      new WebSessionFilterFactory()
          .create(adapter)
          .doFilter(
              request(
                  "GET", "/search?q=reader1", new Cookie("SCHUBERT_NK_SESSION", original.getId())),
              new MockHttpServletResponse(),
              (req, res) -> {
                var r = (HttpServletRequest) req;
                assertSame(r, cache.getMatchingRequest(r, (HttpServletResponse) res));
                assertEquals(PRINCIPAL, r.getSession().getAttribute("principal"));
                assertEquals(csrf, r.getSession().getAttribute("csrfToken"));
                assertEquals(
                    SessionAttributeCodecTest.tokens(2),
                    r.getSession().getAttribute("operationTokens"));
              });
    }
  }

  private static SpringEncryptedSessionRepository adapter(Fixture f) {
    return new SpringEncryptedSessionRepository(f.repository, f.clock);
  }

  private static MockHttpServletRequest marked(
      SpringEncryptedSessionRepository adapter, MockHttpServletRequest r) {
    r.setAttribute(SessionRepositoryFilter.SESSION_REPOSITORY_ATTR, adapter);
    return r;
  }

  private static MockHttpServletRequest request(String method, String target, Cookie cookie) {
    int query = target.indexOf('?');
    var r = new MockHttpServletRequest(method, query < 0 ? target : target.substring(0, query));
    if (query >= 0) r.setQueryString(target.substring(query + 1));
    r.setSecure(true);
    if (cookie != null) r.setCookies(cookie);
    return r;
  }

  private static int count() throws Exception {
    try (var c = db.web();
        var s = c.createStatement();
        var r = s.executeQuery("select count(*) from schubert_web_session.web_http_sessions")) {
      assertTrue(r.next());
      return r.getInt(1);
    }
  }

  private static void unavailable(Executable action) {
    var e = assertThrows(SessionStoreException.class, action);
    assertEquals("session storage is unavailable", e.getMessage());
    assertNull(e.getCause());
    assertEquals(0, e.getSuppressed().length);
  }

  private static void invalid(String method, String value) {
    var e =
        assertThrows(
            IllegalArgumentException.class, () -> SavedScreenTarget.fromGet(method, value));
    assertEquals("saved screen target is invalid", e.getMessage());
    assertNull(e.getCause());
    assertEquals(0, e.getSuppressed().length);
  }
}
