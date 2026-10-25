package dev.codex.schubert.nk.web.session;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;

import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.layout.semantic.UserRole;
import dev.codex.schubert.nk.web.config.ScenarioMvcConfiguration;
import dev.codex.schubert.nk.web.controller.ScenarioController;
import dev.codex.schubert.nk.web.logging.WebLogDatabaseFixture;
import dev.codex.schubert.nk.web.messaging.JmsRequestReplyClient;
import dev.codex.schubert.nk.web.messaging.ReplyCorrelationRegistry;
import dev.codex.schubert.nk.web.messaging.ScenarioWireClient;
import dev.codex.schubert.nk.web.security.ApiSessionInvalidHandler;
import dev.codex.schubert.nk.web.view.GameListViewModel;
import dev.codex.schubert.nk.web.view.RouteListViewModel;
import dev.codex.schubert.nk.web.view.ScenarioFileListViewModel;
import jakarta.servlet.http.Cookie;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.security.Principal;
import java.time.Clock;
import java.time.Duration;
import java.time.Instant;
import java.time.ZoneOffset;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Locale;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.CopyOnWriteArrayList;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.function.BiFunction;
import org.jsoup.Jsoup;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;
import org.springframework.mock.web.MockHttpServletRequest;
import org.springframework.mock.web.MockHttpServletResponse;
import org.springframework.mock.web.MockServletContext;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.web.csrf.CsrfToken;
import org.springframework.security.web.csrf.DefaultCsrfToken;
import org.springframework.session.web.http.SessionRepositoryFilter;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.setup.MockMvcBuilders;
import org.springframework.ui.ExtendedModelMap;
import org.springframework.ui.Model;
import org.springframework.web.context.support.AnnotationConfigWebApplicationContext;
import org.thymeleaf.spring6.view.ThymeleafViewResolver;

/**
 * NK-WEB-002/SCR004..006; FUN004/AUT/SYS006/TST; UI221..223/234; SS313/314;
 * SSC071/PG194/PT-SCR-001..016.
 */
class ScenarioControllerTest {
  private static WebLogDatabaseFixture db;
  @TempDir Path root;
  private static final Clock CLOCK =
      Clock.fixed(Instant.parse("2026-09-20T00:00:00Z"), ZoneOffset.UTC);

  @BeforeAll
  static void start(@TempDir Path path) throws Exception {
    db = new WebLogDatabaseFixture(path);
  }

  @AfterAll
  static void stop() throws Exception {
    if (db != null) db.stop();
  }

  @BeforeEach
  void reset() throws Exception {
    try (var c = db.web();
        var s = c.createStatement()) {
      s.executeUpdate("DELETE FROM schubert_web_session.web_http_sessions");
    }
  }

  @AfterEach
  void clear() {
    SecurityContextHolder.clearContext();
  }

  private static SessionPrincipal actor(UserRole role) {
    return new SessionPrincipal(
        "reader",
        role,
        AuthenticationContext.of("a".repeat(64)),
        Instant.parse("2026-09-19T00:00:00Z"));
  }

  @Test
  void screens001GamesSuccess() throws Exception {
    try (var f = new Fixture()) {
      for (var role : UserRole.values())
        for (String code : List.of("0000", "0200"))
          for (int count : new int[] {0, 2, 10}) {
            f.code = code;
            f.count = count;
            int before = f.sent.get();
            var model = new ExtendedModelMap();
            var response = new MockHttpServletResponse();
            assertEquals(
                "scenarios",
                f.controller.games(actor(role), model, f.request("/scenarios"), response));
            var page = assertInstanceOf(GameListViewModel.class, model.get("page"));
            assertEquals(Set.of("page"), model.keySet());
            assertEquals(count, page.getGames().size());
            if (count > 0) {
              assertEquals("NUKITASHI1", page.getGames().getFirst().getCode());
              assertEquals("NUKITASHI", page.getGames().getFirst().getTitle());
              assertEquals("/scenarios/NUKITASHI1", page.getGames().getFirst().getHref());
            }
            assertEquals(role.wireValue(), page.getTopBar().getRole());
            assertEquals(200, response.getStatus());
            assertEquals(before + 1, f.sent.get());
            f.erased();
          }
    }
  }

  @Test
  void screens002RoutesSuccess() throws Exception {
    try (var f = new Fixture()) {
      for (String game : List.of("NUKITASHI1", "NUKITASHI2"))
        for (int count : new int[] {1, 50}) {
          f.count = count;
          var m = new ExtendedModelMap();
          assertEquals(
              "scenario-routes",
              f.controller.routes(
                  game,
                  actor(UserRole.USER),
                  m,
                  f.request("/scenarios/" + game),
                  new MockHttpServletResponse()));
          var page = assertInstanceOf(RouteListViewModel.class, m.get("page"));
          assertEquals(game, page.getGame());
          assertEquals(count, page.getRoutes().size());
          assertEquals("01: 共通ルート", page.getRoutes().getFirst().getTitle());
          assertEquals("/scenarios/" + game + "/01", page.getRoutes().getFirst().getHref());
          assertEquals(7, page.getRoutes().getFirst().getFileCount());
          f.erased();
        }
      f.count = 1;
      for (int prefix : new int[] {0, 99}) {
        f.responder =
            (id, request) -> {
              byte[] bytes = f.standard(id, request);
              number(bytes, 265, 2, prefix);
              put(bytes, 267, 64, "未分類");
              return bytes;
            };
        var model = new ExtendedModelMap();
        assertEquals(
            "scenario-routes",
            f.controller.routes(
                "NUKITASHI1",
                actor(UserRole.USER),
                model,
                f.request("/scenarios/NUKITASHI1"),
                new MockHttpServletResponse()));
        var page = assertInstanceOf(RouteListViewModel.class, model.get("page"));
        assertEquals(prefix == 0 ? "00: 未分類" : "99: 未分類", page.getRoutes().getFirst().getTitle());
        assertEquals(
            prefix == 0 ? "/scenarios/NUKITASHI1/00" : "/scenarios/NUKITASHI1/99",
            page.getRoutes().getFirst().getHref());
      }
    }
  }

  @Test
  void screens003FilesSuccess() throws Exception {
    try (var f = new Fixture()) {
      for (String game : List.of("NUKITASHI1", "NUKITASHI2"))
        for (String prefix : List.of("01", "99"))
          for (int count : new int[] {1, 500}) {
            f.count = count;
            var m = new ExtendedModelMap();
            assertEquals(
                "scenario-files",
                f.controller.files(
                    game,
                    prefix,
                    actor(UserRole.ADMIN),
                    m,
                    f.request("/scenarios/" + game + "/" + prefix),
                    new MockHttpServletResponse()));
            var page = assertInstanceOf(ScenarioFileListViewModel.class, m.get("page"));
            assertEquals(game, page.getGame());
            assertEquals(prefix, page.getPrefix());
            assertEquals("共通ルート", page.getRouteName());
            assertEquals(count, page.getFiles().size());
            assertEquals("Chapter1", page.getFiles().getFirst().getDisplayTitle());
            assertEquals("game/1.txt", page.getFiles().getFirst().getDisplayPath());
            assertEquals(1, page.getFiles().getFirst().getEntryCount());
            assertEquals("/scenarios/1", page.getFiles().getFirst().getHref());
            f.erased();
          }
    }
  }

  @Test
  void screens004EmptyHierarchy() throws Exception {
    try (var f = new Fixture()) {
      f.count = 0;
      for (String type : List.of("RTE", "SCF")) {
        var m = new ExtendedModelMap();
        var s = new MockHttpServletResponse();
        assertNull(f.call(type, actor(UserRole.USER), m, f.request(path(type)), s));
        assertEquals(404, s.getStatus());
        assertTrue(m.isEmpty());
        assertNull(s.getErrorMessage());
      }
      try (var context = f.mvc()) {
        var result =
            mock(context).perform(pageRequest("/scenarios", actor(UserRole.USER))).andReturn();
        assertEquals(200, result.getResponse().getStatus());
        assertEquals(
            "該当するデータはありません",
            Jsoup.parse(result.getResponse().getContentAsString()).select(".empty").text());
        assertTrue(
            Jsoup.parse(result.getResponse().getContentAsString()).select(".menu-item").isEmpty());
      }
    }
  }

  @Test
  void screens005AllResultCodes() throws Exception {
    String[] codes = {
      "0000", "0100", "0101", "0102", "0103", "0104", "0105", "0106", "0107", "0200", "9000", "9001"
    };
    int[] expected = {200, 400, 401, 302, 403, 404, 409, 429, 409, 200, 503, 503};
    try (var f = new Fixture()) {
      for (String type : List.of("GAM", "RTE", "SCF"))
        for (int i = 0; i < codes.length; i++) {
          f.code = codes[i];
          var m = new ExtendedModelMap();
          var r = f.request(path(type));
          var s = new MockHttpServletResponse();
          setActor(actor(UserRole.USER));
          int before = f.sent.get();
          String view = f.call(type, actor(UserRole.USER), m, r, s);
          assertEquals(expected[i], s.getStatus(), type + "/" + codes[i]);
          assertEquals(before + 1, f.sent.get());
          if (expected[i] == 200) {
            assertNotNull(view);
            assertEquals(Set.of("page"), m.keySet());
          } else {
            assertNull(view);
            assertTrue(m.isEmpty());
            assertNull(s.getErrorMessage());
          }
          f.erased();
        }
    }
  }

  @Test
  void screens006InvalidSessionTerminal() throws Exception {
    try (var f = new Fixture()) {
      f.code = "0102";
      for (boolean ajax : List.of(false, true)) {
        var p = actor(UserRole.USER);
        var session = f.security.authenticated(p);
        var r = raw("/scenarios");
        r.setCookies(new Cookie("SCHUBERT_NK_SESSION", session.sessionId().cookieValue()));
        if (ajax) r.addHeader("X-Requested-With", "XMLHttpRequest");
        var s = new MockHttpServletResponse();
        var model = new ExtendedModelMap();
        var calls = new AtomicInteger();
        f.security.run(
            r,
            s,
            (request, response) -> {
              calls.incrementAndGet();
              var http = (HttpServletRequest) request;
              assertNull(
                  f.controller.games(
                      http.getUserPrincipal(), model, http, (HttpServletResponse) response));
              assertNull(http.getSession(false));
              assertNull(SecurityContextHolder.getContext().getAuthentication());
            });
        assertEquals(ajax ? 401 : 302, s.getStatus());
        assertEquals(1, calls.get());
        assertTrue(model.isEmpty());
        assertTrue(f.security.f.repository.find(session.sessionId()).isEmpty());
        assertTrue(s.getHeader("Set-Cookie").contains("Max-Age=0"));
      }
    }
  }

  @Test
  void screens007WireAndBindingFailure() throws Exception {
    try (var f = new Fixture()) {
      for (int variant = 0; variant < 4; variant++) {
        final int selected = variant;
        f.responder =
            (id, request) -> {
              var bytes = f.standard(id, request);
              if (selected == 0) bytes[0] = 'X';
              if (selected == 1) put(bytes, 256, 12, "NUKITASHI2");
              if (selected == 2) number(bytes, 268, 2, 99);
              if (selected == 3) throw new IllegalStateException("private transport");
              return bytes;
            };
        var m = new ExtendedModelMap();
        var s = new MockHttpServletResponse();
        assertNull(f.call("SCF", actor(UserRole.USER), m, f.request(path("SCF")), s));
        assertEquals(503, s.getStatus());
        assertTrue(m.isEmpty());
        assertNull(s.getErrorMessage());
        f.erased();
      }
    }
  }

  @Test
  void screens008NullAndForeignPrincipal() throws Exception {
    try (var f = new Fixture()) {
      assertThrows(
          NullPointerException.class, () -> new ScenarioController(null, f.security.handler));
      assertThrows(NullPointerException.class, () -> new ScenarioController(f.client, null));
      for (String type : List.of("GAM", "RTE", "SCF")) {
        var p = actor(UserRole.USER);
        var m = new ExtendedModelMap();
        var r = f.request(path(type));
        var s = new MockHttpServletResponse();
        assertThrows(NullPointerException.class, () -> f.call(type, null, m, r, s));
        assertThrows(NullPointerException.class, () -> f.call(type, p, null, r, s));
        assertThrows(NullPointerException.class, () -> f.call(type, p, m, null, s));
        assertThrows(NullPointerException.class, () -> f.call(type, p, m, r, null));
        Principal foreign =
            () -> {
              throw new AssertionError("foreign identity read");
            };
        assertThrows(SessionStoreException.class, () -> f.call(type, foreign, m, r, s));
      }
      var p = actor(UserRole.USER);
      var m = new ExtendedModelMap();
      var r = f.request("/scenarios");
      var s = new MockHttpServletResponse();
      assertThrows(NullPointerException.class, () -> f.controller.routes(null, p, m, r, s));
      assertThrows(NullPointerException.class, () -> f.controller.files(null, "01", p, m, r, s));
      assertThrows(
          NullPointerException.class, () -> f.controller.files("NUKITASHI1", null, p, m, r, s));
      assertEquals(0, f.sent.get());
    }
  }

  @Test
  void screens009ClosedRoutesAndRequests() throws Exception {
    try (var f = new Fixture();
        var context = f.mvc()) {
      var mvc = mock(context);
      var p = actor(UserRole.USER);
      for (String bad :
          List.of(
              "/scenarios/unknown",
              "/scenarios/1",
              "/scenarios/NUKITASHI1/1",
              "/scenarios/NUKITASHI1/001",
              "/scenarios/NUKITASHI1/xx",
              "/scenarios/NUKITASHI1/０１")) {
        int before = f.sent.get();
        assertEquals(404, mvc.perform(pageRequest(bad, p)).andReturn().getResponse().getStatus());
        assertEquals(before, f.sent.get());
      }
      assertEquals(
          405, mvc.perform(post("/scenarios").principal(p)).andReturn().getResponse().getStatus());
      var result =
          mvc.perform(
                  pageRequest("/scenarios", p).param("role", "ADMIN").param("context", "forged"))
              .andReturn();
      assertEquals(
          "USER",
          Jsoup.parse(result.getResponse().getContentAsString()).select(".login-role").text());
      assertThrows(
          IllegalArgumentException.class,
          () ->
              f.controller.routes(
                  "unknown",
                  p,
                  new ExtendedModelMap(),
                  f.request("/scenarios"),
                  new MockHttpServletResponse()));
      for (String bad : List.of("1", "001", "-1", "０１", "a1", " 1"))
        assertThrows(
            IllegalArgumentException.class,
            () ->
                f.controller.files(
                    "NUKITASHI1",
                    bad,
                    p,
                    new ExtendedModelMap(),
                    f.request("/scenarios"),
                    new MockHttpServletResponse()));
    }
  }

  @Test
  void screens010RealTemplatesAndNavigation() throws Exception {
    try (var f = new Fixture();
        var context = f.mvc()) {
      var mvc = mock(context);
      for (var role : UserRole.values())
        for (String type : List.of("GAM", "RTE", "SCF")) {
          var result = mvc.perform(pageRequest(path(type), actor(role))).andReturn();
          assertEquals(200, result.getResponse().getStatus());
          String html = result.getResponse().getContentAsString();
          var dom = Jsoup.parse(html);
          assertEquals("ja", dom.selectFirst("html").attr("lang"));
          assertEquals(
              type.equals("GAM")
                  ? "Scenario Games"
                  : type.equals("RTE") ? "NUKITASHI1" : "01: 共通ルート",
              dom.select("h1").text());
          assertEquals(
              type.equals("GAM")
                  ? "Scenario Games"
                  : type.equals("RTE") ? "NUKITASHI1 Routes" : "NUKITASHI1 01: 共通ルート",
              dom.title());
          assertEquals("reader", dom.select(".login-user").text());
          assertEquals(role.wireValue(), dom.select(".login-role").text());
          assertEquals(1, dom.select("a[href='/']").size());
          assertEquals(1, dom.select("a[href='/notifications']").size());
          assertEquals(1, dom.select("a[href='/search']").size());
          assertEquals(
              type.equals("GAM") ? "検索" : type.equals("RTE") ? "ゲーム選択 検索" : "ゲーム選択 ルート選択 検索",
              dom.select("nav[aria-label='Scenarioナビゲーション']").text());
          assertEquals("post", dom.select("form.logout-form").attr("method"));
          assertEquals("/logout", dom.select("form.logout-form").attr("action"));
          assertEquals("b".repeat(64), dom.select("input[name='_csrf']").attr("value"));
          assertTrue(dom.select("script,[onclick],[onchange]").isEmpty());
          assertFalse(html.contains("a".repeat(64)));
          assertEquals(2, dom.select(type.equals("GAM") ? ".menu-item" : ".scenario-link").size());
        }
    }
  }

  @Test
  void screens011HtmlEscaping() throws Exception {
    try (var f = new Fixture();
        var context = f.mvc()) {
      String canary = "<img src=x onerror=alert(1)>";
      f.count = 1;
      f.responder =
          (id, request) -> {
            byte[] bytes = f.standard(id, request);
            String type = ascii(request, 11, 3);
            if (type.equals("GAM")) put(bytes, 277, 256, canary);
            if (type.equals("RTE")) put(bytes, 267, 64, canary);
            if (type.equals("SCF")) {
              put(bytes, 270, 64, canary);
              put(bytes, 356, 256, canary);
              put(bytes, 612, 512, "folder/<img>.txt");
            }
            return bytes;
          };
      var p =
          new SessionPrincipal(
              canary,
              UserRole.USER,
              AuthenticationContext.of("a".repeat(64)),
              actor(UserRole.USER).loginAt());
      for (String type : List.of("GAM", "RTE", "SCF")) {
        var result = mock(context).perform(pageRequest(path(type), p)).andReturn();
        assertEquals(200, result.getResponse().getStatus());
        var dom = Jsoup.parse(result.getResponse().getContentAsString());
        assertEquals(canary, dom.select(".login-user").text());
        assertTrue(dom.select("img,script,[onerror]").isEmpty());
        assertTrue(dom.text().contains(canary));
        assertFalse(result.getResponse().getContentAsString().contains("a".repeat(64)));
      }
    }
  }

  @Test
  void screens012CompatibilityObservations() throws Exception {
    try (var f = new Fixture();
        var context = f.mvc()) {
      var mvc = mock(context);
      var p = actor(UserRole.USER);
      var games =
          Jsoup.parse(
              mvc.perform(pageRequest("/scenarios", p))
                  .andReturn()
                  .getResponse()
                  .getContentAsString());
      assertEquals(
          List.of("NUKITASHI1 NUKITASHI", "NUKITASHI2 NUKITASHI2"),
          games.select(".menu-item").eachText());
      var routes =
          Jsoup.parse(
              mvc.perform(pageRequest("/scenarios/NUKITASHI1", p))
                  .andReturn()
                  .getResponse()
                  .getContentAsString());
      assertEquals(
          List.of("01: 共通ルート NUKITASHI1 7 files", "02: 未分類 NUKITASHI1 8 files"),
          routes.select(".scenario-link").eachText());
      var files =
          Jsoup.parse(
              mvc.perform(pageRequest("/scenarios/NUKITASHI1/01", p))
                  .andReturn()
                  .getResponse()
                  .getContentAsString());
      assertEquals(
          List.of(
              "Chapter1 NUKITASHI1 game/1.txt 1 entries",
              "Chapter2 NUKITASHI1 game/2.txt 2 entries"),
          files.select(".scenario-link").eachText());
      assertEquals(
          List.of("/scenarios/1", "/scenarios/2"), files.select(".scenario-link").eachAttr("href"));
      Path directory = Path.of("target/scenario-screen-traces");
      Files.createDirectories(directory);
      Files.writeString(
          directory.resolve("PT-SCR-012.txt"),
          "cases=CHR-S05|CHR-S06\nfixture=public-synthetic\ngames=2\nroutes=2\nfiles=2\norderAndText=PASS\nactualNkGate=false\n",
          StandardCharsets.US_ASCII);
    }
  }

  @Test
  void screens013ConcurrentQueries() throws Exception {
    try (var f = new Fixture();
        var executor = Executors.newFixedThreadPool(8)) {
      var tasks = new ArrayList<Future<?>>();
      for (int i = 0; i < 100; i++) {
        final int n = i;
        tasks.add(
            executor.submit(
                () -> {
                  String type = List.of("GAM", "RTE", "SCF").get(n % 3);
                  var p =
                      new SessionPrincipal(
                          "reader" + n,
                          UserRole.USER,
                          AuthenticationContext.of(String.format(Locale.ROOT, "%064x", n + 1)),
                          actor(UserRole.USER).loginAt());
                  var m = new ExtendedModelMap();
                  assertNotNull(f.call(type, p, m, raw(path(type)), new MockHttpServletResponse()));
                  Object page = m.get("page");
                  String name =
                      page instanceof GameListViewModel g
                          ? g.getTopBar().getUsername()
                          : page instanceof RouteListViewModel r
                              ? r.getTopBar().getUsername()
                              : ((ScenarioFileListViewModel) page).getTopBar().getUsername();
                  assertEquals("reader" + n, name);
                  return null;
                }));
      }
      for (var task : tasks) task.get(10, TimeUnit.SECONDS);
      assertEquals(100, f.sent.get());
      assertEquals(100, f.contexts.size());
      assertEquals(100, f.correlations.size());
      f.erased();
    }
  }

  @Test
  void screens014FailurePropagation() throws Exception {
    try (var f = new Fixture()) {
      var failure = new IllegalStateException("synthetic model failure");
      var broken =
          new ExtendedModelMap() {
            @Override
            public ExtendedModelMap addAttribute(String name, Object value) {
              throw failure;
            }
          };
      assertSame(
          failure,
          assertThrows(
              IllegalStateException.class,
              () ->
                  f.call(
                      "GAM",
                      actor(UserRole.USER),
                      broken,
                      f.request("/scenarios"),
                      new MockHttpServletResponse())));
      var io = new IOException("synthetic response failure");
      var response =
          new MockHttpServletResponse() {
            @Override
            public void sendError(int status) throws IOException {
              throw io;
            }
          };
      f.code = "0100";
      assertSame(
          io,
          assertThrows(
              IOException.class,
              () ->
                  f.call(
                      "GAM",
                      actor(UserRole.USER),
                      new ExtendedModelMap(),
                      f.request("/scenarios"),
                      response)));
      var unknown = new AssertionError("synthetic unknown");
      f.responder =
          (id, bytes) -> {
            throw unknown;
          };
      assertSame(
          unknown,
          assertThrows(
              AssertionError.class,
              () ->
                  f.call(
                      "GAM",
                      actor(UserRole.USER),
                      new ExtendedModelMap(),
                      f.request("/scenarios"),
                      new MockHttpServletResponse())));
      f.responder = f::standard;
      f.code = "0102";
      var r = f.request("/scenarios");
      r.setAttribute(SessionRepositoryFilter.SESSION_REPOSITORY_ATTR, new Object());
      setActor(actor(UserRole.USER));
      assertThrows(
          SessionStoreException.class,
          () ->
              f.call(
                  "GAM",
                  actor(UserRole.USER),
                  new ExtendedModelMap(),
                  r,
                  new MockHttpServletResponse()));
      assertNull(SecurityContextHolder.getContext().getAuthentication());
      f.erased();
    }
  }

  @Test
  void screens015MvcConfiguration() throws Exception {
    try (var f = new Fixture();
        var context = f.mvc()) {
      var configuration = new ScenarioMvcConfiguration();
      assertThrows(
          NullPointerException.class,
          () -> configuration.scenarioController(null, f.security.handler));
      assertThrows(
          NullPointerException.class, () -> configuration.scenarioController(f.client, null));
      assertInstanceOf(ScenarioController.class, context.getBean(ScenarioController.class));
      var resolver = context.getBean(ThymeleafViewResolver.class);
      for (String view :
          List.of(
              "menu",
              "error/error",
              "scenarios",
              "scenario-routes",
              "scenario-files",
              "scenario",
              "search")) assertNotNull(resolver.resolveViewName(view, Locale.JAPAN));
      for (String view :
          List.of(
              "scenario-private",
              "private",
              "../scenarios",
              "redirect:https://invalid.example",
              "forward:/admin/users")) assertNull(resolver.resolveViewName(view, Locale.JAPAN));
    }
  }

  @Test
  void screens016RealHttpSecurityAndTerminal() throws Exception {
    for (String role : List.of("USER", "ADMIN")) {
      reset();
      var loginApi = new SessionFormLoginTest.Api("0000", role, "0000", 0);
      try (var f = new Fixture();
          var server =
              new EmbeddedWebSecurityTest.Server(
                  Files.createTempDirectory(root, "hierarchy-"),
                  false,
                  db,
                  Optional.of(loginApi.provider),
                  true,
                  true,
                  (mvc, invalid) -> configure(mvc, f.client, invalid))) {
        var anonymous = server.send("GET", "/scenarios", null, null, true);
        assertEquals(302, anonymous.statusCode());
        assertEquals("/login", anonymous.headers().firstValue("location").orElseThrow());
        assertEquals(0, f.sent.get());
        var first = server.send("GET", "/login", null, null, true);
        String initial = first.headers().firstValue("set-cookie").orElseThrow().split(";", 2)[0];
        var login =
            server.send(
                "POST",
                "/login",
                initial,
                "_csrf=" + first.body().substring(6) + "&username=reader&password=p",
                true);
        assertEquals(302, login.statusCode());
        String cookie = login.headers().firstValue("set-cookie").orElseThrow().split(";", 2)[0];
        for (String path :
            List.of("/scenarios", "/scenarios/NUKITASHI1", "/scenarios/NUKITASHI1/01")) {
          var response = server.send("GET", path, cookie, null, true);
          assertEquals(200, response.statusCode());
          var dom = Jsoup.parse(response.body());
          assertEquals(role, dom.select(".login-role").text());
          assertEquals(1, dom.select("input[name='_csrf']").size());
          assertTrue(
              response.headers().firstValue("cache-control").orElseThrow().contains("no-store"));
          assertEquals(
              "nosniff", response.headers().firstValue("x-content-type-options").orElseThrow());
        }
        f.code = "0102";
        int before = f.sent.get();
        var expired = server.send("GET", "/scenarios", cookie, null, true);
        assertEquals(302, expired.statusCode());
        assertEquals(
            "/login?session-expired", expired.headers().firstValue("location").orElseThrow());
        assertTrue(expired.headers().firstValue("set-cookie").orElseThrow().contains("Max-Age=0"));
        assertEquals(before + 1, f.sent.get());
        var next = server.send("GET", "/scenarios", cookie, null, true);
        assertEquals(302, next.statusCode());
        assertEquals("/login", next.headers().firstValue("location").orElseThrow());
        assertEquals(before + 1, f.sent.get());
        assertEquals(0, server.context.getManager().getActiveSessions());
        f.erased();
        loginApi.erased();
      }
    }
  }

  private static MockHttpServletRequest raw(String path) {
    var r = new MockHttpServletRequest("GET", path);
    r.setRemoteAddr("127.0.0.1");
    r.addHeader("X-Forwarded-For", "203.0.113.1");
    r.addHeader("X-Forwarded-Proto", "https");
    return r;
  }

  private static void setActor(SessionPrincipal p) {
    SecurityContextHolder.getContext()
        .setAuthentication(
            UsernamePasswordAuthenticationToken.authenticated(
                p, null, List.of(new SimpleGrantedAuthority("ROLE_" + p.role().wireValue()))));
  }

  private static String path(String type) {
    return switch (type) {
      case "GAM" -> "/scenarios";
      case "RTE" -> "/scenarios/NUKITASHI1";
      case "SCF" -> "/scenarios/NUKITASHI1/01";
      default -> throw new AssertionError();
    };
  }

  private static org.springframework.test.web.servlet.request.MockHttpServletRequestBuilder
      pageRequest(String path, SessionPrincipal p) {
    return get(path)
        .principal(p)
        .requestAttr(
            CsrfToken.class.getName(),
            new DefaultCsrfToken("X-CSRF-TOKEN", "_csrf", "b".repeat(64)));
  }

  private static MockMvc mock(AnnotationConfigWebApplicationContext context) {
    return MockMvcBuilders.webAppContextSetup(context).build();
  }

  private static void configure(
      AnnotationConfigWebApplicationContext context,
      ScenarioWireClient client,
      ApiSessionInvalidHandler invalid) {
    context.register(ScenarioMvcConfiguration.class);
    context.addBeanFactoryPostProcessor(
        factory -> {
          factory.registerSingleton("scenarioWireClient", client);
          factory.registerSingleton("apiSessionInvalidHandler", invalid);
        });
  }

  private static final class Fixture implements AutoCloseable {
    final ApiSessionInvalidTest.Harness security = new ApiSessionInvalidTest.Harness(db);
    final AtomicInteger sent = new AtomicInteger();
    final AtomicInteger ids = new AtomicInteger();
    final Set<String> contexts = ConcurrentHashMap.newKeySet();
    final Set<UUID> correlations = ConcurrentHashMap.newKeySet();
    final List<byte[]> buffers = new CopyOnWriteArrayList<>();
    volatile String code = "0000";
    volatile int count = 2;
    volatile BiFunction<UUID, byte[], byte[]> responder = this::standard;
    final JmsRequestReplyClient wire =
        new JmsRequestReplyClient(new ReplyCorrelationRegistry(), CLOCK, 12);
    final ScenarioWireClient client =
        new ScenarioWireClient(
            wire,
            (id, bytes) -> {
              sent.incrementAndGet();
              buffers.add(bytes);
              assertTrue(correlations.add(id));
              String type = ascii(bytes, 11, 3);
              int length =
                  switch (type) {
                    case "GAM" -> 0;
                    case "RTE" -> 12;
                    case "SCF" -> 14;
                    default -> throw new AssertionError();
                  };
              assertEquals(256 + length, bytes.length);
              assertEquals("Q", ascii(bytes, 22, 1));
              assertEquals("S", ascii(bytes, 23, 1));
              assertEquals(id.toString(), ascii(bytes, 24, 36));
              assertEquals(id.toString(), ascii(bytes, 60, 36));
              assertEquals("20260920090000000", ascii(bytes, 96, 17));
              assertEquals(String.format(Locale.ROOT, "%06d", length), ascii(bytes, 181, 6));
              contexts.add(ascii(bytes, 113, 64));
              assertTrue(wire.onReply(id, responder.apply(id, bytes)));
            },
            CLOCK,
            () -> new UUID(0, ids.incrementAndGet()),
            Duration.ofSeconds(1));
    final ScenarioController controller = new ScenarioController(client, security.handler);

    MockHttpServletRequest request(String path) throws Exception {
      return security.mock("GET", path);
    }

    String call(String type, Principal p, Model m, HttpServletRequest r, HttpServletResponse s)
        throws IOException {
      return switch (type) {
        case "GAM" -> controller.games(p, m, r, s);
        case "RTE" -> controller.routes("NUKITASHI1", p, m, r, s);
        case "SCF" -> controller.files("NUKITASHI1", "01", p, m, r, s);
        default -> throw new AssertionError();
      };
    }

    AnnotationConfigWebApplicationContext mvc() {
      var context = new AnnotationConfigWebApplicationContext();
      context.setServletContext(new MockServletContext());
      configure(context, client, security.handler);
      context.refresh();
      return context;
    }

    byte[] standard(UUID id, byte[] request) {
      String type = ascii(request, 11, 3);
      String game = type.equals("GAM") ? "NUKITASHI1" : ascii(request, 256, 12).stripTrailing();
      int prefix = type.equals("SCF") ? Integer.parseInt(ascii(request, 268, 2)) : 1;
      return response(type, code, count, id, ascii(request, 113, 64), game, prefix);
    }

    void erased() {
      assertEquals(0, wire.pendingCount());
      for (byte[] bytes : buffers) assertArrayEquals(new byte[bytes.length], bytes);
    }

    @Override
    public void close() {
      security.close();
    }
  }

  // UI232/234 independent byte offsets; never call Production encoder for fixture/expected.
  private static byte[] response(
      String type,
      String code,
      int requestedCount,
      UUID id,
      String context,
      String game,
      int prefix) {
    boolean success = code.equals("0000") || code.equals("0200");
    int count = success ? requestedCount : 0;
    int data = type.equals("SCF") ? 88 : 9;
    int record =
        switch (type) {
          case "GAM" -> 272;
          case "RTE" -> 72;
          case "SCF" -> 800;
          default -> throw new AssertionError();
        };
    byte[] bytes = new byte[256 + data + record * count];
    Arrays.fill(bytes, (byte) ' ');
    put(bytes, 0, 8, "SCHBNK01");
    put(bytes, 8, 3, "001");
    put(bytes, 11, 8, type + "RSP01");
    put(bytes, 19, 3, "001");
    put(bytes, 22, 1, "S");
    put(bytes, 23, 1, "S");
    put(bytes, 24, 36, new UUID(1, id.getLeastSignificantBits()).toString());
    put(bytes, 60, 36, id.toString());
    put(bytes, 96, 17, "20260920090000000");
    put(bytes, 113, 64, context);
    number(bytes, 177, 4, 256);
    number(bytes, 181, 6, data);
    number(bytes, 187, 6, record);
    number(bytes, 193, 6, count);
    number(bytes, 199, 9, bytes.length);
    put(bytes, 208, 4, code);
    if (type.equals("SCF")) {
      put(bytes, 256, 12, success ? game : "");
      number(bytes, 268, 2, success ? prefix : 0);
      put(bytes, 270, 64, success ? "共通ルート" : "");
      number(bytes, 334, 9, count);
    } else number(bytes, 256, 9, count);
    for (int n = 0; n < count; n++) {
      int offset = 256 + data + n * record;
      switch (type) {
        case "GAM" -> {
          put(bytes, offset, 12, n % 2 == 0 ? "NUKITASHI1" : "NUKITASHI2");
          put(bytes, offset + 12, 256, n % 2 == 0 ? "NUKITASHI" : "NUKITASHI2");
          number(bytes, offset + 268, 3, n + 1);
        }
        case "RTE" -> {
          number(bytes, offset, 2, n + 1);
          put(bytes, offset + 2, 64, n == 0 ? "共通ルート" : "未分類");
          number(bytes, offset + 66, 6, n + 7);
        }
        case "SCF" -> {
          number(bytes, offset, 12, n + 1);
          put(bytes, offset + 12, 256, "Chapter" + (n + 1));
          put(bytes, offset + 268, 512, "game/" + (n + 1) + ".txt");
          number(bytes, offset + 780, 6, n + 1);
        }
        default -> throw new AssertionError();
      }
    }
    return bytes;
  }

  private static String ascii(byte[] bytes, int offset, int length) {
    return new String(bytes, offset, length, StandardCharsets.US_ASCII);
  }

  private static void put(byte[] bytes, int offset, int length, String value) {
    byte[] encoded = value.getBytes(StandardCharsets.UTF_8);
    assertTrue(encoded.length <= length);
    Arrays.fill(bytes, offset, offset + length, (byte) ' ');
    System.arraycopy(encoded, 0, bytes, offset, encoded.length);
  }

  private static void number(byte[] bytes, int offset, int length, long value) {
    put(bytes, offset, length, String.format(Locale.ROOT, "%0" + length + "d", value));
  }
}
