package dev.codex.schubert.nk.web.session;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNotSame;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.web.logging.WebLogDatabaseFixture;
import dev.codex.schubert.nk.web.logging.WebSecurityAudit;
import dev.codex.schubert.nk.web.security.WebRequestContext;
import dev.codex.schubert.nk.web.security.WebSecurityFilterFactory;
import dev.codex.schubert.nk.web.session.EmbeddedWebSecurityTest.Server;
import jakarta.servlet.http.HttpServletRequest;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Duration;
import java.time.Instant;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Objects;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.Callable;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;
import org.springframework.mock.web.MockFilterConfig;
import org.springframework.mock.web.MockHttpServletRequest;
import org.springframework.mock.web.MockHttpServletResponse;
import org.springframework.security.core.context.SecurityContextHolder;

/**
 * NK-WEB-001/PT-WEB-131..136; FUN-001..013/AUT-001..004/MON-004; UI221/226;
 * SS311/313/314/342/351/352; PG-D-113.
 */
class WebSecurityChainTest {
  private static final String FIXTURE_0000_876EEFE0 = "0000";
  private static final String FIXTURE_USER_2DED8884 = "USER";
  private static final String FIXTURE_GET_04F32A7E = "GET";
  private static final String FIXTURE_LOGIN_F843C044 = "/login";
  private static final String FIXTURE_ADMIN_C4BB3010 = "ADMIN";
  private static final String FIXTURE_LOCATION_1D147FF5 = "location";
  private static final String FIXTURE_TOKEN_190FC7FC = "TOKEN:";
  private static final String FIXTURE_POST_E46D3AE9 = "POST";
  private static final String FIXTURE_READER_F734AAEA = "reader";
  private static final String FIXTURE_0106_EF3D3B45 = "0106";
  private static final String FIXTURE_CSRF_2949BEA6 = "CSRF";
  private static final String FIXTURE_SEARCH_F32C67A7 = "/search";
  private static WebLogDatabaseFixture db;
  @TempDir Path root;

  @BeforeAll
  static void start(@TempDir Path database) throws Exception {
    db = new WebLogDatabaseFixture(database);
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
  void web131FactoryNullAndClosedComposition() throws Exception {
    try (var f = new EncryptedWebSessionRepositoryTest.Fixture(db)) {
      f.clock.value = Instant.now();
      var adapter = new SpringEncryptedSessionRepository(f.repository, f.clock);
      var api =
          new SessionFormLoginTest.Api(
              FIXTURE_0000_876EEFE0, FIXTURE_USER_2DED8884, FIXTURE_0000_876EEFE0, 0);
      var audit = new WebSecurityAudit(new SessionLoginHandlerTest.Log(), f.clock, "pt", "pt");
      var factory = new WebSecurityFilterFactory();
      assertThrows(
          NullPointerException.class,
          () -> factory.create(null, api.provider, audit, UUID::randomUUID));
      assertThrows(
          NullPointerException.class, () -> factory.create(adapter, null, audit, UUID::randomUUID));
      assertThrows(
          NullPointerException.class,
          () -> factory.create(adapter, api.provider, null, UUID::randomUUID));
      assertThrows(
          NullPointerException.class, () -> factory.create(adapter, api.provider, audit, null));
      var filter = factory.create(adapter, api.provider, audit, UUID::randomUUID);
      assertNotSame(filter, factory.create(adapter, api.provider, audit, UUID::randomUUID));
      filter.init(new MockFilterConfig("businessSecurity"));
      try {
        var r = new MockHttpServletRequest(FIXTURE_GET_04F32A7E, FIXTURE_LOGIN_F843C044);
        r.setRemoteAddr("127.0.0.1");
        r.addHeader("X-Forwarded-For", "203.0.113.1");
        r.addHeader("X-Forwarded-Proto", "https");
        var s = new MockHttpServletResponse();
        var calls = new AtomicInteger();
        filter.doFilter(
            r,
            s,
            (x, y) -> {
              calls.incrementAndGet();
              assertEquals("UTF-8", x.getCharacterEncoding());
              assertNotNull(WebRequestContext.require((HttpServletRequest) x));
              assertNull(SecurityContextHolder.getContext().getAuthentication());
            });
        assertEquals(1, calls.get());
        assertEquals("no-store", s.getHeader("Cache-Control"));
        assertNull(s.getCookie("JSESSIONID"));
        assertEquals(0, api.sends.get());
        assertNull(SecurityContextHolder.getContext().getAuthentication());
      } finally {
        filter.destroy();
        SecurityContextHolder.clearContext();
      }
      api.erased();
    }
  }

  @Test
  void web132RealHttpLoginReturnsToSavedScreen() throws Exception {
    for (String role : List.of(FIXTURE_USER_2DED8884, FIXTURE_ADMIN_C4BB3010))
      for (String code : List.of(FIXTURE_0000_876EEFE0, "0200")) {
        reset();
        var api = new SessionFormLoginTest.Api(code, role, FIXTURE_0000_876EEFE0, 0);
        try (var server = server(api, false)) {
          var first = server.send(FIXTURE_GET_04F32A7E, "/search?q=abc", null, null, true);
          assertEquals(302, first.statusCode());
          assertEquals(
              FIXTURE_LOGIN_F843C044,
              first.headers().firstValue(FIXTURE_LOCATION_1D147FF5).orElseThrow());
          String anonymous = cookie(first);
          var login =
              server.send(FIXTURE_GET_04F32A7E, FIXTURE_LOGIN_F843C044, anonymous, null, true);
          assertEquals(200, login.statusCode());
          assertEquals(FIXTURE_TOKEN_190FC7FC + "02".repeat(32), login.body());
          var success =
              server.send(
                  FIXTURE_POST_E46D3AE9,
                  FIXTURE_LOGIN_F843C044,
                  anonymous,
                  body("02".repeat(32), FIXTURE_READER_F734AAEA, "p"),
                  true);
          assertEquals(302, success.statusCode());
          assertEquals(
              "/search?q=abc",
              success.headers().firstValue(FIXTURE_LOCATION_1D147FF5).orElseThrow());
          String current = cookie(success);
          assertNotEquals(anonymous, current);
          var adapter = new SpringEncryptedSessionRepository(server.f.repository, server.f.clock);
          assertNull(adapter.findById(value(anonymous)));
          SessionPrincipal principal =
              Objects.requireNonNull(adapter.findById(value(current))).getAttribute("principal");
          assertEquals(FIXTURE_READER_F734AAEA, principal.username());
          assertEquals(role, principal.role().wireValue());
          var restored = server.send(FIXTURE_GET_04F32A7E, "/search?q=abc", current, null, true);
          assertEquals(200, restored.statusCode());
          assertEquals(FIXTURE_TOKEN_190FC7FC + "04".repeat(32), restored.body());
          assertNull(
              Objects.requireNonNull(adapter.findById(value(current)))
                  .getAttribute("savedRequest"));
          for (var response : List.of(first, login, success, restored)) headers(response);
          assertEquals(1, rows());
          assertEquals(0, server.context.getManager().getActiveSessions());
          assertEquals(1, api.sends.get());
          assertEquals(code.equals("0200") ? 1 : 0, api.probes.get());
          assertEquals(0, server.converted.get());
          assertEquals(0, server.posts.get());
          assertEquals(
              List.of("UNAUTHENTICATED", "AUTHENTICATED"),
              server.log.events.stream()
                  .map(e -> e.getAsJsonObject("details").get("reason").getAsString())
                  .toList());
        }
        api.erased();
      }
  }

  @Test
  void web133RealHttpFailuresNeverGrantAuthentication() throws Exception {
    for (String code :
        List.of("0101", FIXTURE_0106_EF3D3B45, "9000", "JMS", FIXTURE_CSRF_2949BEA6)) {
      reset();
      var api =
          new SessionFormLoginTest.Api(
              code.equals(FIXTURE_CSRF_2949BEA6) ? FIXTURE_0000_876EEFE0 : code,
              FIXTURE_USER_2DED8884,
              FIXTURE_0000_876EEFE0,
              code.equals(FIXTURE_0106_EF3D3B45) ? 123 : 0);
      try (var server = server(api, false)) {
        var page = server.send(FIXTURE_GET_04F32A7E, FIXTURE_LOGIN_F843C044, null, null, true);
        String anonymous = cookie(page);
        var failed =
            server.send(
                FIXTURE_POST_E46D3AE9,
                FIXTURE_LOGIN_F843C044,
                anonymous,
                body(
                    code.equals(FIXTURE_CSRF_2949BEA6) ? "ff".repeat(32) : "02".repeat(32),
                    FIXTURE_READER_F734AAEA,
                    "p"),
                true);
        int status =
            code.equals("0101") || code.equals(FIXTURE_0106_EF3D3B45)
                ? 302
                : code.equals(FIXTURE_CSRF_2949BEA6) ? 403 : 503;
        assertEquals(status, failed.statusCode());
        headers(failed);
        assertEquals(
            code.equals(FIXTURE_0106_EF3D3B45) ? Optional.of("123") : Optional.empty(),
            failed.headers().firstValue("retry-after"));
        assertEquals(
            code.equals("0101")
                ? Optional.of("/login?error")
                : code.equals(FIXTURE_0106_EF3D3B45)
                    ? Optional.of("/login?locked")
                    : Optional.empty(),
            failed.headers().firstValue(FIXTURE_LOCATION_1D147FF5));
        if (status != 302) assertEquals("error:" + status, failed.body());
        else assertEquals("", failed.body());
        assertTrue(failed.headers().allValues("set-cookie").isEmpty());
        assertNull(
            Objects.requireNonNull(
                    new SpringEncryptedSessionRepository(server.f.repository, server.f.clock)
                        .findById(value(anonymous)))
                .getAttribute("principal"));
        assertEquals(code.equals(FIXTURE_CSRF_2949BEA6) ? 0 : 1, api.sends.get());
        assertEquals(0, server.context.getManager().getActiveSessions());
        assertEquals(code.equals("9000") || code.equals("JMS") ? 0 : 1, server.log.events.size());
      }
      api.erased();
    }
  }

  @Test
  void web134RealHttpRoleAndErrorDispatchRemainBound() throws Exception {
    for (String role : List.of(FIXTURE_USER_2DED8884, FIXTURE_ADMIN_C4BB3010)) {
      reset();
      var api = new SessionFormLoginTest.Api(FIXTURE_0000_876EEFE0, role, FIXTURE_0000_876EEFE0, 0);
      try (var server = server(api, false)) {
        var media = server.send(FIXTURE_GET_04F32A7E, "/audio/1", null, null, true);
        assertEquals(403, media.statusCode());
        assertEquals("error:403", media.body());
        assertTrue(media.headers().allValues(FIXTURE_LOCATION_1D147FF5).isEmpty());
        var ajax =
            server.client.send(
                HttpRequest.newBuilder(server.base.resolve(FIXTURE_SEARCH_F32C67A7))
                    .timeout(Duration.ofSeconds(5))
                    .header("X-Forwarded-For", "203.0.113.1")
                    .header("X-Forwarded-Proto", "https")
                    .header("X-Requested-With", "XMLHttpRequest")
                    .GET()
                    .build(),
                HttpResponse.BodyHandlers.ofString());
        assertEquals(403, ajax.statusCode());
        assertTrue(ajax.headers().allValues(FIXTURE_LOCATION_1D147FF5).isEmpty());
        var get = server.send(FIXTURE_GET_04F32A7E, FIXTURE_LOGIN_F843C044, null, null, true);
        String anonymous = cookie(get);
        var invalidMethod =
            server.send(
                "PUT",
                FIXTURE_LOGIN_F843C044,
                anonymous,
                body("02".repeat(32), FIXTURE_READER_F734AAEA, "p"),
                true);
        assertEquals(403, invalidMethod.statusCode());
        assertEquals(0, api.sends.get());
        var login =
            server.send(
                FIXTURE_POST_E46D3AE9,
                FIXTURE_LOGIN_F843C044,
                anonymous,
                body("02".repeat(32), FIXTURE_READER_F734AAEA, "p"),
                true);
        String current = cookie(login);
        for (String path : List.of("/admin/users", "/logs")) {
          var response = server.send(FIXTURE_GET_04F32A7E, path, current, null, true);
          headers(response);
          assertEquals(role.equals(FIXTURE_USER_2DED8884) ? 403 : 200, response.statusCode());
          if (role.equals(FIXTURE_USER_2DED8884)) {
            assertEquals("error:403", response.body());
            assertEquals(
                server.log.events.getLast().get("requestId").getAsString(),
                server.errorIds.getLast().toString());
          }
        }
        assertEquals(role.equals(FIXTURE_USER_2DED8884) ? 6 : 4, server.log.events.size());
        assertEquals(role.equals(FIXTURE_USER_2DED8884) ? 5 : 3, server.errorCalls.get());
        assertEquals(7, server.ids.get());
        assertEquals(0, server.context.getManager().getActiveSessions());
      }
      api.erased();
    }
  }

  @Test
  void web135FirewallRejectionRetainsSafeHeaders() throws Exception {
    var api =
        new SessionFormLoginTest.Api(
            FIXTURE_0000_876EEFE0, FIXTURE_USER_2DED8884, FIXTURE_0000_876EEFE0, 0);
    try (var server = server(api, false)) {
      var proxy = server.send(FIXTURE_GET_04F32A7E, FIXTURE_SEARCH_F32C67A7, null, null, false);
      assertEquals(403, proxy.statusCode());
      assertEquals("", proxy.body());
      headers(proxy);
      assertEquals(1, server.log.events.size());
      assertEquals(1, server.ids.get());
      for (String path : List.of("/search;session=private", "/login;private=value", "/admin/%25")) {
        var rejected = server.send(FIXTURE_GET_04F32A7E, path, null, null, true);
        assertEquals(400, rejected.statusCode());
        assertEquals("error:400", rejected.body());
        headers(rejected);
        assertFalse(rejected.body().contains("private"));
        assertFalse(rejected.body().contains("Tomcat"));
      }
      assertEquals(4, server.ids.get());
      assertEquals(3, server.errorCalls.get());
      assertEquals(
          Set.of(new UUID(0, 2), new UUID(0, 3), new UUID(0, 4)), new HashSet<>(server.errorIds));
      assertEquals(1, server.log.events.size());
      assertEquals(0, rows());
      assertEquals(0, api.sends.get());
    }
    api.erased();
  }

  @Test
  void web136ConcurrentHttpChainsKeepSessionsAndAuditIsolated() throws Exception {
    var api =
        new SessionFormLoginTest.Api(FIXTURE_0000_876EEFE0, "DYNAMIC", FIXTURE_0000_876EEFE0, 0);
    try (var server = server(api, true);
        var pool = Executors.newFixedThreadPool(8)) {
      var currentIds = ConcurrentHashMap.<String>newKeySet();
      var jobs = new ArrayList<Callable<Void>>();
      for (int i = 0; i < 100; i++) {
        int n = i;
        jobs.add(
            () -> {
              var page =
                  server.send(FIXTURE_GET_04F32A7E, FIXTURE_LOGIN_F843C044, null, null, true);
              assertEquals(200, page.statusCode());
              String anonymous = cookie(page);
              String csrf = page.body().substring(6);
              var login =
                  server.send(
                      FIXTURE_POST_E46D3AE9,
                      FIXTURE_LOGIN_F843C044,
                      anonymous,
                      body(csrf, "user" + n, "password-user" + n),
                      true);
              assertEquals(302, login.statusCode());
              assertEquals(
                  "/", login.headers().firstValue(FIXTURE_LOCATION_1D147FF5).orElseThrow());
              String current = cookie(login);
              assertNotEquals(anonymous, current);
              assertTrue(currentIds.add(current));
              var get =
                  server.send(FIXTURE_GET_04F32A7E, FIXTURE_SEARCH_F32C67A7, current, null, true);
              assertEquals(200, get.statusCode());
              assertNotEquals(FIXTURE_TOKEN_190FC7FC + csrf, get.body());
              var role = server.send(FIXTURE_GET_04F32A7E, "/admin/users", current, null, true);
              assertEquals(n % 2 == 0 ? 403 : 200, role.statusCode());
              headers(role);
              SessionPrincipal p =
                  Objects.requireNonNull(
                          new SpringEncryptedSessionRepository(server.f.repository, server.f.clock)
                              .findById(value(current)))
                      .getAttribute("principal");
              assertEquals("user" + n, p.username());
              assertEquals(
                  n % 2 == 0 ? FIXTURE_USER_2DED8884 : FIXTURE_ADMIN_C4BB3010,
                  p.role().wireValue());
              return null;
            });
      }
      for (var job : pool.invokeAll(jobs)) job.get(30, TimeUnit.SECONDS);
      assertEquals(100, currentIds.size());
      assertEquals(100, rows());
      assertEquals(100, api.sends.get());
      assertEquals(400, server.ids.get());
      assertEquals(150, server.log.events.size());
      assertEquals(50, server.errorCalls.get());
      assertEquals(0, server.context.getManager().getActiveSessions());
      assertEquals(0, server.converted.get());
      var names = new HashSet<String>();
      for (var event : server.log.events)
        if (event.get("action").getAsString().equals("LOGIN_SUCCEEDED"))
          assertTrue(names.add(event.get("actorUsername").getAsString()));
      assertEquals(100, names.size());
    }
    api.erased();
  }

  @Test
  void web137ServletPrincipalAndProgrammaticAuthStayClosed() throws Exception {
    for (String role : List.of(FIXTURE_USER_2DED8884, FIXTURE_ADMIN_C4BB3010)) {
      reset();
      var api = new SessionFormLoginTest.Api(FIXTURE_0000_876EEFE0, role, FIXTURE_0000_876EEFE0, 0);
      try (var server = server(api, false)) {
        var first = server.send(FIXTURE_GET_04F32A7E, FIXTURE_LOGIN_F843C044, null, null, true);
        var login =
            server.send(
                FIXTURE_POST_E46D3AE9,
                FIXTURE_LOGIN_F843C044,
                cookie(first),
                body("02".repeat(32), FIXTURE_READER_F734AAEA, "p"),
                true);
        var response =
            server.send(FIXTURE_GET_04F32A7E, "/fixture-principal", cookie(login), null, true);
        assertEquals(200, response.statusCode());
        assertEquals(FIXTURE_READER_F734AAEA, response.body());
        var programmatic =
            server.send(FIXTURE_GET_04F32A7E, "/fixture-programmatic", cookie(login), null, true);
        assertEquals(200, programmatic.statusCode());
        assertEquals(
            role.equals(FIXTURE_USER_2DED8884)
                ? "reader:FORM:true:false:true:false:false"
                : "reader:FORM:false:true:false:true:false",
            programmatic.body());
        var stillAuthenticated =
            server.send(FIXTURE_GET_04F32A7E, FIXTURE_SEARCH_F32C67A7, cookie(login), null, true);
        assertEquals(200, stillAuthenticated.statusCode());
        assertEquals(FIXTURE_TOKEN_190FC7FC + "04".repeat(32), stillAuthenticated.body());
        assertTrue(programmatic.headers().allValues("set-cookie").isEmpty());
        assertEquals(1, rows());
        assertEquals(0, server.context.getManager().getActiveSessions());
        assertEquals(1, api.sends.get());
      }
      api.erased();
    }
  }

  private Server server(SessionFormLoginTest.Api api, boolean random) throws Exception {
    return new Server(
        Files.createTempDirectory(root, "http-"), random, db, Optional.of(api.provider));
  }

  private static String body(String csrf, String username, String password) {
    return "_csrf=" + csrf + "&username=" + username + "&password=" + password;
  }

  private static String cookie(HttpResponse<String> response) {
    String set = response.headers().firstValue("set-cookie").orElseThrow();
    assertTrue(set.startsWith("SCHUBERT_NK_SESSION="));
    assertTrue(set.contains("Secure"));
    assertTrue(set.contains("HttpOnly"));
    assertTrue(set.contains("SameSite=Lax"));
    assertFalse(set.contains("JSESSIONID"));
    return set.split(";", 2)[0];
  }

  private static String value(String cookie) {
    return cookie.substring("SCHUBERT_NK_SESSION=".length());
  }

  private static void headers(HttpResponse<String> response) {
    assertEquals(List.of("no-store"), response.headers().allValues("cache-control"));
    assertEquals(List.of("DENY"), response.headers().allValues("x-frame-options"));
    assertEquals(List.of("nosniff"), response.headers().allValues("x-content-type-options"));
    assertEquals(
        List.of("max-age=31536000"), response.headers().allValues("strict-transport-security"));
    assertTrue(response.headers().allValues("x-request-id").isEmpty());
    assertFalse(response.body().contains("Exception"));
    assertFalse(response.body().contains("Tomcat"));
  }

  private static long rows() throws Exception {
    try (var c = db.web();
        var s = c.createStatement();
        var r = s.executeQuery("select count(*) from schubert_web_session.web_http_sessions")) {
      assertTrue(r.next());
      return r.getLong(1);
    }
  }
}
