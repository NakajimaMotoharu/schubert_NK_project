package dev.codex.schubert.nk.web.session;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.header.ResultCode;
import dev.codex.schubert.nk.protocol.layout.semantic.UserRole;
import dev.codex.schubert.nk.web.error.WebResultMapper;
import dev.codex.schubert.nk.web.logging.WebLogDatabaseFixture;
import dev.codex.schubert.nk.web.logging.WebSecurityAudit;
import dev.codex.schubert.nk.web.security.ApiSessionInvalidHandler;
import dev.codex.schubert.nk.web.security.CaddyClientAddressResolver;
import dev.codex.schubert.nk.web.security.CaddyTransportContextFilter;
import dev.codex.schubert.nk.web.security.SavedRequestTarget;
import dev.codex.schubert.nk.web.security.WebDisplayContext;
import dev.codex.schubert.nk.web.security.WebDisplayContextFilter;
import dev.codex.schubert.nk.web.security.WebRequestContext;
import dev.codex.schubert.nk.web.security.WebSecurityFilterFactory;
import dev.codex.schubert.nk.web.session.EncryptedWebSessionRepositoryTest.Fixture;
import jakarta.servlet.FilterChain;
import jakarta.servlet.http.Cookie;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletRequestWrapper;
import jakarta.servlet.http.HttpServletResponse;
import jakarta.servlet.http.HttpSession;
import java.io.IOException;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;
import java.nio.file.Path;
import java.time.Clock;
import java.time.Duration;
import java.time.Instant;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicReference;
import org.jsoup.Jsoup;
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
import org.springframework.security.web.csrf.DefaultCsrfToken;
import org.springframework.session.web.http.SessionRepositoryFilter;

/** NK-WEB-001/PT-WEB-158..165; UI221/222/226/232; SS313/314/351/352; SSC-048/PG-D-117. */
class ApiSessionInvalidTest {
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
      s.executeUpdate("delete from schubert_web_session.web_http_sessions");
    }
  }

  @AfterEach
  void clear() {
    SecurityContextHolder.clearContext();
  }

  @Test
  void web158ResultCodesHaveIndependentHttpClassification() {
    var mapper = new WebResultMapper();
    String[] codes = {
      "0000", "0100", "0101", "0102", "0103", "0104", "0105", "0106", "0107", "0200", "9000", "9001"
    };
    int[] statuses = {200, 400, 401, 401, 403, 404, 409, 429, 409, 200, 503, 503};
    assertEquals(codes.length, ResultCode.values().length);
    for (int i = 0; i < codes.length; i++)
      assertEquals(statuses[i], mapper.httpStatus(ResultCode.fromWire(codes[i])));
    assertThrows(NullPointerException.class, () -> mapper.httpStatus(null));
  }

  @Test
  void web159InvalidHandlerBoundariesNeverUseNativeSession() throws Exception {
    try (var h = new Harness()) {
      var r = h.mock("GET", "/search");
      var s = new MockHttpServletResponse();
      assertThrows(NullPointerException.class, () -> new ApiSessionInvalidHandler(null, h.audit));
      assertThrows(NullPointerException.class, () -> new ApiSessionInvalidHandler(h.adapter, null));
      assertThrows(NullPointerException.class, () -> h.handler.handle(null, s));
      assertThrows(NullPointerException.class, () -> h.handler.handle(r, null));
      assertThrows(
          IllegalStateException.class, () -> h.handler.handle(new MockHttpServletRequest(), s));
      for (Object marker : new Object[] {null, new Object()}) {
        r.setAttribute(SessionRepositoryFilter.SESSION_REPOSITORY_ATTR, marker);
        var guarded =
            new HttpServletRequestWrapper(r) {
              @Override
              public HttpSession getSession(boolean create) {
                throw new AssertionError("native");
              }
            };
        setActor(actor("reader", UserRole.USER));
        assertThrows(SessionStoreException.class, () -> h.handler.handle(guarded, s));
        assertNull(SecurityContextHolder.getContext().getAuthentication());
      }
      r.setAttribute(SessionRepositoryFilter.SESSION_REPOSITORY_ATTR, h.adapter);
      SecurityContextHolder.getContext()
          .setAuthentication(
              UsernamePasswordAuthenticationToken.authenticated(
                  "private-foreign", null, List.of(new SimpleGrantedAuthority("ROLE_ADMIN"))));
      assertThrows(SessionStoreException.class, () -> h.handler.handle(r, s));
      assertNull(SecurityContextHolder.getContext().getAuthentication());
      for (RuntimeException fault :
          List.of(new IllegalStateException("private"), new IllegalArgumentException("private"))) {
        var broken =
            new HttpServletRequestWrapper(r) {
              @Override
              public HttpSession getSession(boolean create) {
                throw fault;
              }
            };
        var rejected = assertThrows(SessionStoreException.class, () -> h.handler.handle(broken, s));
        assertNull(rejected.getCause());
        assertEquals(0, rejected.getSuppressed().length);
        var session =
            new MockHttpSession() {
              @Override
              public void invalidate() {
                throw fault;
              }
            };
        r.setSession(session);
        assertThrows(SessionStoreException.class, () -> h.handler.handle(r, s));
      }
      r.setSession(null);
      var npe = new NullPointerException("private");
      var broken =
          new HttpServletRequestWrapper(r) {
            @Override
            public HttpSession getSession(boolean create) {
              throw npe;
            }
          };
      assertSame(npe, assertThrows(NullPointerException.class, () -> h.handler.handle(broken, s)));
      var attrs =
          new HttpServletRequestWrapper(r) {
            @Override
            public Object getAttribute(String name) {
              if (name.equals(SessionRepositoryFilter.SESSION_REPOSITORY_ATTR))
                throw new IllegalStateException("private");
              return super.getAttribute(name);
            }
          };
      assertThrows(IllegalStateException.class, () -> h.handler.handle(attrs, s));
      assertTrue(h.log.events.isEmpty());
    }
  }

  @Test
  void web160InvalidHandlerUsesClosedNavigationAndAudit() throws Exception {
    try (var h = new Harness()) {
      for (String method : List.of("GET", "HEAD", "POST", "PUT", "PATCH", "DELETE", "OPTIONS")) {
        for (String path :
            List.of(
                "/search",
                "/audio/1",
                "/audio/1/download",
                "/animation/media/1",
                "/music/media/1",
                "/music/download/1",
                "/%61udio/1")) {
          for (String ajax : new String[] {null, "XMLHttpRequest", "xmlhttprequest", "ordinary"}) {
            var r = h.mock(method, path);
            if (ajax != null) r.addHeader("X-Requested-With", ajax);
            var p = actor("reader", UserRole.USER);
            setActor(p);
            snapshot(r, p);
            var session = new MockHttpSession();
            r.setSession(session);
            var s = new MockHttpServletResponse();
            var guarded =
                new HttpServletRequestWrapper(r) {
                  @Override
                  public HttpSession getSession() {
                    throw new AssertionError("create");
                  }

                  @Override
                  public java.security.Principal getUserPrincipal() {
                    throw new AssertionError("native");
                  }

                  @Override
                  public String getQueryString() {
                    throw new AssertionError("query");
                  }

                  @Override
                  public String getParameter(String name) {
                    throw new AssertionError("body");
                  }
                };
            h.handler.handle(guarded, s);
            boolean navigate =
                method.equals("GET")
                    && path.equals("/search")
                    && (ajax == null || ajax.equals("ordinary"));
            assertEquals(navigate ? 302 : 401, s.getStatus());
            assertEquals(navigate ? "/login?session-expired" : null, s.getHeader("Location"));
            assertNull(s.getErrorMessage());
            assertTrue(session.isInvalid());
            cleared(r);
            var event = h.log.events.getLast();
            assertEquals("SESSION_EXPIRED", event.get("action").getAsString());
            assertEquals("INFO", event.get("level").getAsString());
            assertEquals("DENIED", event.get("outcome").getAsString());
            assertEquals("reader", event.get("actorUsername").getAsString());
            assertEquals("USER", event.get("actorRole").getAsString());
            assertEquals(
                "API_SESSION_INVALID",
                event.getAsJsonObject("details").get("reason").getAsString());
            assertEquals("/**", event.getAsJsonObject("details").get("route").getAsString());
            assertEquals(
                WebRequestContext.require(r).requestId().toString(),
                event.get("requestId").getAsString());
            assertFalse(event.toString().contains("a".repeat(64)));
          }
        }
      }
      var absent = h.mock("GET", "/search");
      h.handler.handle(absent, new MockHttpServletResponse());
      assertNull(absent.getSession(false));
      assertFalse(h.log.events.getLast().has("actorUsername"));
    }
  }

  @Test
  void web161InvalidationClearsEncryptedSessionAndDisplay() throws Exception {
    try (var h = new Harness()) {
      var p = actor("reader", UserRole.USER);
      var original = h.authenticated(p);
      h.f.repository.mutate(
          original.sessionId(),
          a ->
              new SessionAttributes(
                  a.principal(),
                  a.csrfToken(),
                  Optional.of(SavedRequestTarget.fromGet("GET", "/search")),
                  List.of(new SessionOperationToken("QSBREQ01", new UUID(0, 1), Instant.now()))));
      var neighbour = h.f.repository.create();
      var r = raw("GET", "/private", original.sessionId().cookieValue());
      var s = new MockHttpServletResponse();
      h.run(
          r,
          s,
          (req, res) -> {
            var request = (HttpServletRequest) req;
            assertTrue(WebDisplayContext.existing(request).isPresent());
            h.handler.handle(request, (HttpServletResponse) res);
            cleared(request);
            assertNull(request.getSession(false));
          });
      assertEquals(302, s.getStatus());
      assertEquals("/login?session-expired", s.getHeader("Location"));
      expiredCookie(s.getHeader("Set-Cookie"));
      assertTrue(h.f.repository.find(original.sessionId()).isEmpty());
      assertEquals(
          neighbour.row().identity(),
          h.f.repository.find(neighbour.sessionId()).orElseThrow().row().identity());
      assertEquals(1, count("web_http_sessions"));
      assertEquals(0, count("pending_context_revocations"));
      assertEquals(0, h.api.sends.get());
    }
  }

  @Test
  void web162RealHttpExpiredGetReturnsToLogin() throws Exception {
    var api = new SessionFormLoginTest.Api("0000", "USER", "0000", 0);
    try (var server = server(api, false)) {
      var login = login(server, "reader", "p");
      var expired =
          server.send(
              "GET", "/fixture-expired?code=0000&password=private", login.cookie(), null, true);
      assertEquals(302, expired.statusCode());
      assertEquals(
          "/login?session-expired", expired.headers().firstValue("location").orElseThrow());
      expiredCookie(expired.headers().firstValue("set-cookie").orElseThrow());
      assertEquals(0, count("web_http_sessions"));
      assertEquals(0, count("pending_context_revocations"));
      var audit = server.log.events.getLast();
      assertEquals("SESSION_EXPIRED", audit.get("action").getAsString());
      assertEquals(new UUID(0, 3).toString(), audit.get("requestId").getAsString());
      assertEquals(2, server.log.events.size());
      var next = server.send("GET", "/", login.cookie(), null, true);
      assertEquals(302, next.statusCode());
      assertEquals("/login", next.headers().firstValue("location").orElseThrow());
      assertEquals(1, api.sends.get());
      assertEquals(0, server.context.getManager().getActiveSessions());
      api.erased();
    }
  }

  @Test
  void web163RealHttpPostAjaxAndMediaNeverReplay() throws Exception {
    var api = new SessionFormLoginTest.Api("0000", "USER", "0000", 0);
    try (var server = server(api, true)) {
      for (String variant :
          List.of(
              "POST",
              "HEAD",
              "AJAX",
              "/audio/pt-expired",
              "/animation/media/pt-expired",
              "/music/media/pt-expired",
              "/music/download/pt-expired")) {
        var login = login(server, "reader", "p");
        HttpResponse<String> response;
        if (variant.equals("AJAX")) {
          response =
              server.client.send(
                  HttpRequest.newBuilder(server.base.resolve("/fixture-expired"))
                      .header("X-Forwarded-For", "203.0.113.1")
                      .header("X-Forwarded-Proto", "https")
                      .header("Cookie", login.cookie())
                      .header("X-Requested-With", "XMLHttpRequest")
                      .timeout(Duration.ofSeconds(5))
                      .GET()
                      .build(),
                  HttpResponse.BodyHandlers.ofString(StandardCharsets.UTF_8));
        } else {
          response =
              server.send(
                  variant.startsWith("/") ? "GET" : variant,
                  variant.startsWith("/") ? variant : "/fixture-expired",
                  login.cookie(),
                  variant.equals("POST") ? "_csrf=" + login.csrf() + "&private-body=canary" : null,
                  true);
        }
        assertEquals(401, response.statusCode());
        assertTrue(response.headers().firstValue("location").isEmpty());
        expiredCookie(response.headers().firstValue("set-cookie").orElseThrow());
        assertEquals("no-store", response.headers().firstValue("cache-control").orElseThrow());
        assertEquals(
            "nosniff", response.headers().firstValue("x-content-type-options").orElseThrow());
        if (!variant.equals("HEAD")) anonymousError(response.body(), 401);
        else assertEquals("", response.body());
        assertEquals(0, count("web_http_sessions"));
      }
      assertEquals(7, api.sends.get());
      assertEquals(14, server.log.events.size());
      assertEquals(0, server.posts.get());
      assertEquals(0, server.context.getManager().getActiveSessions());
      api.erased();
    }
  }

  @Test
  void web164InvalidationFaultsNeverClaimSuccessfulLogout() throws Exception {
    try (var h = new Harness()) {
      var r = h.mock("GET", "/search");
      var session = new MockHttpSession();
      r.setSession(session);
      setActor(actor("reader", UserRole.USER));
      snapshot(r, actor("reader", UserRole.USER));
      h.log.fail = true;
      var failed = new MockHttpServletResponse();
      assertThrows(IllegalStateException.class, () -> h.handler.handle(r, failed));
      assertTrue(session.isInvalid());
      assertEquals(401, failed.getStatus());
      assertNull(failed.getHeader("Location"));
      cleared(r);
      h.log.fail = false;
      var committed = new MockHttpServletResponse();
      committed.setCommitted(true);
      var r2 = h.mock("GET", "/search");
      var old = new MockHttpSession();
      r2.setSession(old);
      assertEquals(
          "session-invalid response already committed",
          assertThrows(IOException.class, () -> h.handler.handle(r2, committed)).getMessage());
      assertTrue(old.isInvalid());
      assertNull(committed.getHeader("Location"));
      var io = new IOException("private");
      var send =
          new MockHttpServletResponse() {
            @Override
            public void sendError(int code) throws IOException {
              throw io;
            }
          };
      assertSame(
          io,
          assertThrows(IOException.class, () -> h.handler.handle(h.mock("POST", "/search"), send)));
      var header =
          new MockHttpServletResponse() {
            @Override
            public void setHeader(String n, String v) {
              throw new IllegalStateException("private");
            }
          };
      assertThrows(
          IllegalStateException.class, () -> h.handler.handle(h.mock("GET", "/search"), header));
      var status =
          new MockHttpServletResponse() {
            @Override
            public void setStatus(int n) {
              throw new IllegalStateException("private");
            }
          };
      assertThrows(
          IllegalStateException.class, () -> h.handler.handle(h.mock("GET", "/search"), status));
      var secondStatus =
          new MockHttpServletResponse() {
            @Override
            public void setStatus(int value) {
              if (value == 302) throw new IllegalStateException("private");
              super.setStatus(value);
            }
          };
      assertThrows(
          IllegalStateException.class,
          () -> h.handler.handle(h.mock("GET", "/search"), secondStatus));
      var committedGetter =
          new MockHttpServletResponse() {
            @Override
            public boolean isCommitted() {
              throw new IllegalStateException("private");
            }
          };
      assertThrows(
          IllegalStateException.class,
          () -> h.handler.handle(h.mock("GET", "/search"), committedGetter));
      for (String field : List.of("method", "header", "uri")) {
        var requestFault =
            new HttpServletRequestWrapper(h.mock("GET", "/search")) {
              @Override
              public String getMethod() {
                if (field.equals("method")) throw new IllegalStateException("private");
                return super.getMethod();
              }

              @Override
              public String getHeader(String name) {
                if (field.equals("header")) throw new IllegalStateException("private");
                return super.getHeader(name);
              }

              @Override
              public String getRequestURI() {
                if (field.equals("uri")) throw new IllegalStateException("private");
                return super.getRequestURI();
              }
            };
        assertThrows(
            IllegalStateException.class,
            () -> h.handler.handle(requestFault, new MockHttpServletResponse()));
      }
      var clear =
          new HttpServletRequestWrapper(h.mock("GET", "/search")) {
            @Override
            public void removeAttribute(String n) {
              throw new IllegalStateException("private");
            }
          };
      setActor(actor("reader", UserRole.ADMIN));
      assertThrows(
          IllegalStateException.class,
          () -> h.handler.handle(clear, new MockHttpServletResponse()));
      assertNull(SecurityContextHolder.getContext().getAuthentication());
    }
    for (String failure : List.of("open", "connection.commit")) {
      reset();
      var api = new SessionFormLoginTest.Api("0000", "USER", "0000", 0);
      try (var server = server(api, false)) {
        var login = login(server, "reader", "p");
        server.invalidationFailure = failure;
        var response = server.send("GET", "/fixture-expired", login.cookie(), null, true);
        assertEquals(503, response.statusCode());
        anonymousError(response.body(), 503);
        assertEquals(1, count("web_http_sessions"));
        assertEquals(1, server.log.events.size());
        assertEquals(0, count("pending_context_revocations"));
        assertEquals(1, api.sends.get());
        server.f.failure = "";
      }
    }
  }

  @Test
  void web165ConcurrentAndStaleInvalidationCannotDeleteNewLogin() throws Exception {
    var api = new SessionFormLoginTest.Api("0000", "DYNAMIC", "0000", 0);
    try (var server = server(api, true);
        var pool = Executors.newFixedThreadPool(8)) {
      var jobs = new ArrayList<Future<?>>();
      for (int n = 0; n < 100; n++) {
        int id = n;
        jobs.add(
            pool.submit(
                () -> {
                  var login = login(server, "user" + id, "password-user" + id);
                  var response = server.send("GET", "/fixture-expired", login.cookie(), null, true);
                  assertEquals(302, response.statusCode());
                  assertEquals(
                      "/login?session-expired",
                      response.headers().firstValue("location").orElseThrow());
                  expiredCookie(response.headers().firstValue("set-cookie").orElseThrow());
                  return null;
                }));
      }
      for (var job : jobs) job.get(30, TimeUnit.SECONDS);
      var users = new HashSet<String>();
      var ids = new HashSet<String>();
      for (var event : server.log.events)
        if (event.get("action").getAsString().equals("SESSION_EXPIRED")) {
          String user = event.get("actorUsername").getAsString();
          int n = Integer.parseInt(user.substring(4));
          assertEquals(n % 2 == 0 ? "USER" : "ADMIN", event.get("actorRole").getAsString());
          assertTrue(users.add(user));
          assertTrue(ids.add(event.get("requestId").getAsString()));
        }
      assertEquals(100, users.size());
      for (int n = 0; n < 100; n++) assertTrue(users.contains("user" + n));
      assertEquals(200, server.log.events.size());
      assertEquals(300, server.ids.get());
      assertEquals(100, api.sends.get());
      assertEquals(0, count("web_http_sessions"));
      assertEquals(0, server.context.getManager().getActiveSessions());
      api.erased();
    }
    try (var h = new Harness()) {
      var old = h.authenticated(actor("reader", UserRole.USER));
      var replacement = new AtomicReference<WebSessionSnapshot>();
      var r = raw("GET", "/private", old.sessionId().cookieValue());
      var s = new MockHttpServletResponse();
      h.run(
          r,
          s,
          (req, res) -> {
            replacement.set(
                h.f
                    .repository
                    .authenticate(old.sessionId(), actor("fresh", UserRole.ADMIN))
                    .orElseThrow());
            h.handler.handle((HttpServletRequest) req, (HttpServletResponse) res);
          });
      assertEquals(302, s.getStatus());
      assertTrue(h.f.repository.find(old.sessionId()).isEmpty());
      var fresh = h.f.repository.find(replacement.get().sessionId()).orElseThrow();
      assertEquals("fresh", fresh.attributes().principal().orElseThrow().username());
      assertEquals(UserRole.ADMIN, fresh.attributes().principal().orElseThrow().role());
      assertEquals(1, count("web_http_sessions"));
      assertEquals(0, count("pending_context_revocations"));
    }
  }

  private EmbeddedWebSecurityTest.Server server(SessionFormLoginTest.Api api, boolean random)
      throws Exception {
    return new EmbeddedWebSecurityTest.Server(
        java.nio.file.Files.createTempDirectory(root, "http-"),
        random,
        db,
        Optional.of(api.provider),
        true,
        true);
  }

  private record Login(String cookie, String csrf) {
    @Override
    public String toString() {
      return "Login[REDACTED]";
    }
  }

  private static Login login(EmbeddedWebSecurityTest.Server server, String user, String password)
      throws Exception {
    var first = server.send("GET", "/login", null, null, true);
    var response =
        server.send(
            "POST",
            "/login",
            first.headers().firstValue("set-cookie").orElseThrow().split(";", 2)[0],
            "_csrf=" + first.body().substring(6) + "&username=" + user + "&password=" + password,
            true);
    assertEquals(302, response.statusCode());
    String cookie = response.headers().firstValue("set-cookie").orElseThrow().split(";", 2)[0];
    // Read the already persisted CSRF solely as input to the next POST, never as its expected
    // oracle.
    var stored =
        server.f.repository.find(WebSessionId.parse(cookie.split("=", 2)[1])).orElseThrow();
    return new Login(cookie, stored.attributes().csrfToken().orElseThrow());
  }

  private static void expiredCookie(String value) {
    assertNotNull(value);
    assertTrue(value.startsWith("SCHUBERT_NK_SESSION=;"));
    assertTrue(value.contains("Max-Age=0"));
    assertTrue(value.contains("Path=/"));
    assertTrue(value.contains("Secure"));
    assertTrue(value.contains("HttpOnly"));
    assertTrue(value.contains("SameSite=Lax"));
    assertFalse(value.contains("JSESSIONID"));
  }

  private static void anonymousError(String html, int status) {
    var document = Jsoup.parse(html);
    assertEquals(Integer.toString(status), document.selectFirst(".error-status").text());
    assertEquals(
        status == 401 ? "再度ログインしてください。" : "現在処理できません。しばらくしてから再操作してください。",
        document.selectFirst(".error-message").text());
    assertTrue(document.select("form,input,.user-info").isEmpty());
    assertTrue(document.select("a[href='/login']").size() == 1);
    assertFalse(html.contains("reader"));
    assertFalse(html.contains("private"));
    assertFalse(html.contains("a".repeat(64)));
  }

  private static long count(String table) throws Exception {
    assertTrue(Set.of("web_http_sessions", "pending_context_revocations").contains(table));
    try (var c = db.web();
        var s = c.createStatement();
        var rows = s.executeQuery("select count(*) from schubert_web_session." + table)) {
      assertTrue(rows.next());
      return rows.getLong(1);
    }
  }

  private static void cleared(HttpServletRequest r) {
    assertTrue(WebDisplayContext.existing(r).isEmpty());
    assertNull(r.getAttribute(CsrfToken.class.getName()));
    assertNull(r.getAttribute("_csrf"));
    assertNull(SecurityContextHolder.getContext().getAuthentication());
  }

  private static void snapshot(MockHttpServletRequest r, SessionPrincipal p) throws Exception {
    r.setUserPrincipal(p);
    var token = new DefaultCsrfToken("X-CSRF-TOKEN", "_csrf", "b".repeat(64));
    r.setAttribute(CsrfToken.class.getName(), token);
    r.setAttribute("_csrf", token);
    new WebDisplayContextFilter().doFilter(r, new MockHttpServletResponse(), (x, y) -> {});
  }

  private static SessionPrincipal actor(String name, UserRole role) {
    return new SessionPrincipal(
        name,
        role,
        AuthenticationContext.of("a".repeat(64)),
        Instant.parse("2026-09-09T00:00:00Z"));
  }

  private static void setActor(SessionPrincipal p) {
    SecurityContextHolder.getContext()
        .setAuthentication(
            UsernamePasswordAuthenticationToken.authenticated(
                p, null, List.of(new SimpleGrantedAuthority("ROLE_" + p.role().wireValue()))));
  }

  private static MockHttpServletRequest raw(String method, String path, String cookie) {
    var r = new MockHttpServletRequest(method, path);
    r.setRemoteAddr("127.0.0.1");
    r.addHeader("X-Forwarded-For", "203.0.113.1");
    r.addHeader("X-Forwarded-Proto", "https");
    if (cookie != null) r.setCookies(new Cookie("SCHUBERT_NK_SESSION", cookie));
    return r;
  }

  // PG194: shared test-only security harness with explicit database ownership.
  @Test
  void biz007VerifiedSelfResetIsNotSyntheticSessionInvalid() throws Exception {
    try (var h = new Harness()) {
      var r = h.mock("POST", "/admin/users/1");
      var p = actor("admin", UserRole.ADMIN);
      setActor(p);
      snapshot(r, p);
      var session = new MockHttpSession();
      r.setSession(session);
      var response = new MockHttpServletResponse();
      h.handler.handleVerifiedSelfReset(r, response);
      assertTrue(session.isInvalid());
      assertEquals(302, response.getStatus());
      assertEquals("/login", response.getHeader("Location"));
      cleared(r);
      assertTrue(h.log.events.isEmpty());
      assertThrows(
          NullPointerException.class, () -> h.handler.handleVerifiedSelfReset(null, response));
      assertThrows(NullPointerException.class, () -> h.handler.handleVerifiedSelfReset(r, null));
      assertThrows(
          IllegalStateException.class,
          () -> h.handler.handleVerifiedSelfReset(new MockHttpServletRequest(), response));
      final var absentActor = h.mock("POST", "/admin/users/1");
      assertThrows(
          SessionStoreException.class,
          () -> h.handler.handleVerifiedSelfReset(absentActor, response));
      setActor(p);
      final var absentSession = h.mock("POST", "/admin/users/1");
      assertThrows(
          SessionStoreException.class,
          () -> h.handler.handleVerifiedSelfReset(absentSession, response));
      setActor(p);
      final var foreign = h.mock("POST", "/admin/users/1");
      foreign.setAttribute(SessionRepositoryFilter.SESSION_REPOSITORY_ATTR, new Object());
      assertThrows(
          SessionStoreException.class, () -> h.handler.handleVerifiedSelfReset(foreign, response));
      setActor(p);
      final var committedRequest = h.mock("POST", "/admin/users/1");
      var committedSession = new MockHttpSession();
      committedRequest.setSession(committedSession);
      var committed = new MockHttpServletResponse();
      committed.flushBuffer();
      assertThrows(
          IOException.class, () -> h.handler.handleVerifiedSelfReset(committedRequest, committed));
      assertTrue(committedSession.isInvalid());
      assertTrue(h.log.events.isEmpty());
      var fatal = new AssertionError("private-self-terminal-fatal");
      final var fatalRequest = h.mock("POST", "/admin/users/1");
      fatalRequest.setSession(
          new MockHttpSession() {
            @Override
            public void invalidate() {
              throw fatal;
            }
          });
      setActor(p);
      assertSame(
          fatal,
          assertThrows(
              AssertionError.class,
              () -> h.handler.handleVerifiedSelfReset(fatalRequest, response)));
      assertNull(SecurityContextHolder.getContext().getAuthentication());
    }
  }

  static final class Harness implements AutoCloseable {
    final Fixture f;
    final SpringEncryptedSessionRepository adapter;
    final SessionLoginHandlerTest.Log log = new SessionLoginHandlerTest.Log();
    final WebSecurityAudit audit = new WebSecurityAudit(log, Clock.systemUTC(), "pt", "pt");
    final AtomicInteger ids = new AtomicInteger();
    final CaddyTransportContextFilter transport =
        new CaddyTransportContextFilter(
            () -> new UUID(0, ids.incrementAndGet()), new CaddyClientAddressResolver(), audit);
    final ApiSessionInvalidHandler handler;
    final SessionFormLoginTest.Api api = new SessionFormLoginTest.Api("0000", "USER", "0000", 0);

    Harness() {
      this(db);
    }

    Harness(WebLogDatabaseFixture database) {
      f = new Fixture(database);
      f.clock.value = Instant.now();
      adapter = new SpringEncryptedSessionRepository(f.repository, f.clock);
      handler = new ApiSessionInvalidHandler(adapter, audit);
    }

    MockHttpServletRequest mock(String method, String path) throws Exception {
      var r = raw(method, path, null);
      r.setAttribute(SessionRepositoryFilter.SESSION_REPOSITORY_ATTR, adapter);
      transport.doFilter(r, new MockHttpServletResponse(), (x, y) -> {});
      return r;
    }

    WebSessionSnapshot authenticated(SessionPrincipal p) {
      return f.repository.authenticate(f.repository.create().sessionId(), p).orElseThrow();
    }

    void run(MockHttpServletRequest r, MockHttpServletResponse s, FilterChain terminal)
        throws Exception {
      var filter =
          new WebSecurityFilterFactory()
              .create(adapter, api.provider, audit, () -> new UUID(0, ids.incrementAndGet()));
      try {
        filter.doFilter(r, s, terminal);
      } finally {
        filter.destroy();
      }
    }

    @Override
    public void close() {
      f.close();
    }
  }
}
