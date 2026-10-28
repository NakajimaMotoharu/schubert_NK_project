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
  private static final String FIXTURE_READER_F734AAEA = "reader";
  private static final String FIXTURE_0000_876EEFE0 = "0000";
  private static final String FIXTURE_SCENARIOS_26111785 = "/scenarios";
  private static final String FIXTURE_PAGE_861424BC = "page";
  private static final String FIXTURE_NUKITASHI1_F97F2EAE = "NUKITASHI1";
  private static final String FIXTURE_SCENARIOS_NUKITASHI1_CE816CE5 = "/scenarios/NUKITASHI1";
  private static final String FIXTURE_USER_2DED8884 = "USER";
  private static final String FIXTURE_ADMIN_C4BB3010 = "ADMIN";
  private static final String FIXTURE_NUKITASHI2_3B3D052F = "NUKITASHI2";
  private static final String FIXTURE_RTE_F939614A = "RTE";
  private static final String FIXTURE_SCF_AC95C8D1 = "SCF";
  private static final String FIXTURE_0102_C967CE66 = "0102";
  private static final String FIXTURE_GAM_5BC4EFCF = "GAM";
  private static final String FIXTURE_SCENARIO_LINK_DB6222B8 = ".scenario-link";
  private static final String FIXTURE_GET_04F32A7E = "GET";
  private static final String FIXTURE_LOGIN_F843C044 = "/login";
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
        FIXTURE_READER_F734AAEA,
        role,
        AuthenticationContext.of("a".repeat(64)),
        Instant.parse("2026-09-19T00:00:00Z"));
  }

  @Test
  void screens001GamesSuccess() throws Exception {
    try (var f = new Fixture()) {
      for (var role : UserRole.values())
        for (String code : List.of(FIXTURE_0000_876EEFE0, "0200"))
          for (int count : new int[] {0, 2, 10}) {
            f.code = code;
            f.count = count;
            int before = f.sent.get();
            var model = new ExtendedModelMap();
            var response = new MockHttpServletResponse();
            assertEquals(
                "scenarios",
                f.controller.games(
                    actor(role), model, f.request(FIXTURE_SCENARIOS_26111785), response));
            var page = assertInstanceOf(GameListViewModel.class, model.get(FIXTURE_PAGE_861424BC));
            assertEquals(Set.of(FIXTURE_PAGE_861424BC), model.keySet());
            assertEquals(count, page.getGames().size());
            if (count > 0) {
              assertEquals(FIXTURE_NUKITASHI1_F97F2EAE, page.getGames().getFirst().getCode());
              assertEquals("NUKITASHI", page.getGames().getFirst().getTitle());
              assertEquals(
                  FIXTURE_SCENARIOS_NUKITASHI1_CE816CE5, page.getGames().getFirst().getHref());
            }
            assertEquals(
                switch (role) {
                  case USER -> FIXTURE_USER_2DED8884;
                  case ADMIN -> FIXTURE_ADMIN_C4BB3010;
                },
                page.getTopBar().getRole());
            assertEquals(200, response.getStatus());
            assertEquals(before + 1, f.sent.get());
            f.erased();
          }
    }
  }

  @Test
  void screens002RoutesSuccess() throws Exception {
    try (var f = new Fixture()) {
      for (String game : List.of(FIXTURE_NUKITASHI1_F97F2EAE, FIXTURE_NUKITASHI2_3B3D052F))
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
          var page = assertInstanceOf(RouteListViewModel.class, m.get(FIXTURE_PAGE_861424BC));
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
                FIXTURE_NUKITASHI1_F97F2EAE,
                actor(UserRole.USER),
                model,
                f.request(FIXTURE_SCENARIOS_NUKITASHI1_CE816CE5),
                new MockHttpServletResponse()));
        var page = assertInstanceOf(RouteListViewModel.class, model.get(FIXTURE_PAGE_861424BC));
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
      for (String game : List.of(FIXTURE_NUKITASHI1_F97F2EAE, FIXTURE_NUKITASHI2_3B3D052F))
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
            var page =
                assertInstanceOf(ScenarioFileListViewModel.class, m.get(FIXTURE_PAGE_861424BC));
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
      for (String type : List.of(FIXTURE_RTE_F939614A, FIXTURE_SCF_AC95C8D1)) {
        var m = new ExtendedModelMap();
        var s = new MockHttpServletResponse();
        assertNull(f.call(type, actor(UserRole.USER), m, f.request(path(type)), s));
        assertEquals(404, s.getStatus());
        assertTrue(m.isEmpty());
        assertNull(s.getErrorMessage());
      }
      try (var context = f.mvc()) {
        var result =
            mock(context)
                .perform(pageRequest(FIXTURE_SCENARIOS_26111785, actor(UserRole.USER)))
                .andReturn();
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
      FIXTURE_0000_876EEFE0,
      "0100",
      "0101",
      FIXTURE_0102_C967CE66,
      "0103",
      "0104",
      "0105",
      "0106",
      "0107",
      "0200",
      "9000",
      "9001"
    };
    int[] expected = {200, 400, 401, 302, 403, 404, 409, 429, 409, 200, 503, 503};
    try (var f = new Fixture()) {
      for (String type : List.of(FIXTURE_GAM_5BC4EFCF, FIXTURE_RTE_F939614A, FIXTURE_SCF_AC95C8D1))
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
            assertEquals(Set.of(FIXTURE_PAGE_861424BC), m.keySet());
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
      f.code = FIXTURE_0102_C967CE66;
      for (boolean ajax : List.of(false, true)) {
        var p = actor(UserRole.USER);
        var session = f.security.authenticated(p);
        var r = raw(FIXTURE_SCENARIOS_26111785);
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
              if (selected == 1) put(bytes, 256, 12, FIXTURE_NUKITASHI2_3B3D052F);
              if (selected == 2) number(bytes, 268, 2, 99);
              if (selected == 3) throw new IllegalStateException("private transport");
              return bytes;
            };
        var m = new ExtendedModelMap();
        var s = new MockHttpServletResponse();
        assertNull(
            f.call(
                FIXTURE_SCF_AC95C8D1,
                actor(UserRole.USER),
                m,
                f.request(path(FIXTURE_SCF_AC95C8D1)),
                s));
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
      for (String type :
          List.of(FIXTURE_GAM_5BC4EFCF, FIXTURE_RTE_F939614A, FIXTURE_SCF_AC95C8D1)) {
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
      var r = f.request(FIXTURE_SCENARIOS_26111785);
      var s = new MockHttpServletResponse();
      assertThrows(NullPointerException.class, () -> f.controller.routes(null, p, m, r, s));
      assertThrows(NullPointerException.class, () -> f.controller.files(null, "01", p, m, r, s));
      assertThrows(
          NullPointerException.class,
          () -> f.controller.files(FIXTURE_NUKITASHI1_F97F2EAE, null, p, m, r, s));
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
          405,
          mvc.perform(post(FIXTURE_SCENARIOS_26111785).principal(p))
              .andReturn()
              .getResponse()
              .getStatus());
      var result =
          mvc.perform(
                  pageRequest(FIXTURE_SCENARIOS_26111785, p)
                      .param("role", FIXTURE_ADMIN_C4BB3010)
                      .param("context", "forged"))
              .andReturn();
      assertEquals(
          FIXTURE_USER_2DED8884,
          Jsoup.parse(result.getResponse().getContentAsString()).select(".login-role").text());
      assertThrows(
          IllegalArgumentException.class,
          () ->
              f.controller.routes(
                  "unknown",
                  p,
                  new ExtendedModelMap(),
                  f.request(FIXTURE_SCENARIOS_26111785),
                  new MockHttpServletResponse()));
      for (String bad : List.of("1", "001", "-1", "０１", "a1", " 1"))
        assertThrows(
            IllegalArgumentException.class,
            () ->
                f.controller.files(
                    FIXTURE_NUKITASHI1_F97F2EAE,
                    bad,
                    p,
                    new ExtendedModelMap(),
                    f.request(FIXTURE_SCENARIOS_26111785),
                    new MockHttpServletResponse()));
    }
  }

  @Test
  void screens010RealTemplatesAndNavigation() throws Exception {
    try (var f = new Fixture();
        var context = f.mvc()) {
      var mvc = mock(context);
      for (var role : UserRole.values())
        for (String type :
            List.of(FIXTURE_GAM_5BC4EFCF, FIXTURE_RTE_F939614A, FIXTURE_SCF_AC95C8D1)) {
          var result = mvc.perform(pageRequest(path(type), actor(role))).andReturn();
          assertEquals(200, result.getResponse().getStatus());
          String html = result.getResponse().getContentAsString();
          var dom = Jsoup.parse(html);
          assertEquals("ja", dom.selectFirst("html").attr("lang"));
          assertEquals(
              type.equals(FIXTURE_GAM_5BC4EFCF)
                  ? "Scenario Games"
                  : type.equals(FIXTURE_RTE_F939614A) ? FIXTURE_NUKITASHI1_F97F2EAE : "01: 共通ルート",
              dom.select("h1").text());
          assertEquals(
              type.equals(FIXTURE_GAM_5BC4EFCF)
                  ? "Scenario Games"
                  : type.equals(FIXTURE_RTE_F939614A)
                      ? "NUKITASHI1 Routes"
                      : "NUKITASHI1 01: 共通ルート",
              dom.title());
          assertEquals(FIXTURE_READER_F734AAEA, dom.select(".login-user").text());
          assertEquals(
              switch (role) {
                case USER -> FIXTURE_USER_2DED8884;
                case ADMIN -> FIXTURE_ADMIN_C4BB3010;
              },
              dom.select(".login-role").text());
          assertEquals(1, dom.select("a[href='/']").size());
          assertEquals(1, dom.select("a[href='/notifications']").size());
          assertEquals(1, dom.select("a[href='/search']").size());
          assertEquals(
              type.equals(FIXTURE_GAM_5BC4EFCF)
                  ? "検索"
                  : type.equals(FIXTURE_RTE_F939614A) ? "ゲーム選択 検索" : "ゲーム選択 ルート選択 検索",
              dom.select("nav[aria-label='Scenarioナビゲーション']").text());
          assertEquals("post", dom.select("form.logout-form").attr("method"));
          assertEquals("/logout", dom.select("form.logout-form").attr("action"));
          assertEquals("b".repeat(64), dom.select("input[name='_csrf']").attr("value"));
          assertTrue(dom.select("script,[onclick],[onchange]").isEmpty());
          assertFalse(html.contains("a".repeat(64)));
          assertEquals(
              2,
              dom.select(
                      type.equals(FIXTURE_GAM_5BC4EFCF)
                          ? ".menu-item"
                          : FIXTURE_SCENARIO_LINK_DB6222B8)
                  .size());
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
            if (type.equals(FIXTURE_GAM_5BC4EFCF)) put(bytes, 277, 256, canary);
            if (type.equals(FIXTURE_RTE_F939614A)) put(bytes, 267, 64, canary);
            if (type.equals(FIXTURE_SCF_AC95C8D1)) {
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
      for (String type :
          List.of(FIXTURE_GAM_5BC4EFCF, FIXTURE_RTE_F939614A, FIXTURE_SCF_AC95C8D1)) {
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
              mvc.perform(pageRequest(FIXTURE_SCENARIOS_26111785, p))
                  .andReturn()
                  .getResponse()
                  .getContentAsString());
      assertEquals(
          List.of("NUKITASHI1 NUKITASHI", "NUKITASHI2 NUKITASHI2"),
          games.select(".menu-item").eachText());
      var routes =
          Jsoup.parse(
              mvc.perform(pageRequest(FIXTURE_SCENARIOS_NUKITASHI1_CE816CE5, p))
                  .andReturn()
                  .getResponse()
                  .getContentAsString());
      assertEquals(
          List.of("01: 共通ルート NUKITASHI1 7 files", "02: 未分類 NUKITASHI1 8 files"),
          routes.select(FIXTURE_SCENARIO_LINK_DB6222B8).eachText());
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
          files.select(FIXTURE_SCENARIO_LINK_DB6222B8).eachText());
      assertEquals(
          List.of("/scenarios/1", "/scenarios/2"),
          files.select(FIXTURE_SCENARIO_LINK_DB6222B8).eachAttr("href"));
      Path directory = Path.of("target/scenario-screen-traces");
      Files.createDirectories(directory);
      Files.writeString(
          directory.resolve("PT-SCR-012.txt"),
          "cases=CHR-S05|CHR-S06\n"
              + "fixture=public-synthetic\n"
              + "games=2\n"
              + "routes=2\n"
              + "files=2\n"
              + "orderAndText=PASS\n"
              + "actualNkGate=false\n",
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
                  String type =
                      List.of(FIXTURE_GAM_5BC4EFCF, FIXTURE_RTE_F939614A, FIXTURE_SCF_AC95C8D1)
                          .get(n % 3);
                  var p =
                      new SessionPrincipal(
                          FIXTURE_READER_F734AAEA + n,
                          UserRole.USER,
                          AuthenticationContext.of(String.format(Locale.ROOT, "%064x", n + 1)),
                          actor(UserRole.USER).loginAt());
                  var m = new ExtendedModelMap();
                  assertNotNull(f.call(type, p, m, raw(path(type)), new MockHttpServletResponse()));
                  Object page = m.get(FIXTURE_PAGE_861424BC);
                  String name =
                      page instanceof GameListViewModel g
                          ? g.getTopBar().getUsername()
                          : page instanceof RouteListViewModel r
                              ? r.getTopBar().getUsername()
                              : ((ScenarioFileListViewModel) page).getTopBar().getUsername();
                  assertEquals(FIXTURE_READER_F734AAEA + n, name);
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
                      FIXTURE_GAM_5BC4EFCF,
                      actor(UserRole.USER),
                      broken,
                      f.request(FIXTURE_SCENARIOS_26111785),
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
                      FIXTURE_GAM_5BC4EFCF,
                      actor(UserRole.USER),
                      new ExtendedModelMap(),
                      f.request(FIXTURE_SCENARIOS_26111785),
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
                      FIXTURE_GAM_5BC4EFCF,
                      actor(UserRole.USER),
                      new ExtendedModelMap(),
                      f.request(FIXTURE_SCENARIOS_26111785),
                      new MockHttpServletResponse())));
      f.responder = f::standard;
      f.code = FIXTURE_0102_C967CE66;
      var r = f.request(FIXTURE_SCENARIOS_26111785);
      r.setAttribute(SessionRepositoryFilter.SESSION_REPOSITORY_ATTR, new Object());
      setActor(actor(UserRole.USER));
      assertThrows(
          SessionStoreException.class,
          () ->
              f.call(
                  FIXTURE_GAM_5BC4EFCF,
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
    for (String role : List.of(FIXTURE_USER_2DED8884, FIXTURE_ADMIN_C4BB3010)) {
      reset();
      var loginApi =
          new SessionFormLoginTest.Api(FIXTURE_0000_876EEFE0, role, FIXTURE_0000_876EEFE0, 0);
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
        var anonymous =
            server.send(FIXTURE_GET_04F32A7E, FIXTURE_SCENARIOS_26111785, null, null, true);
        assertEquals(302, anonymous.statusCode());
        assertEquals(
            FIXTURE_LOGIN_F843C044, anonymous.headers().firstValue("location").orElseThrow());
        assertEquals(0, f.sent.get());
        var first = server.send(FIXTURE_GET_04F32A7E, FIXTURE_LOGIN_F843C044, null, null, true);
        String initial = first.headers().firstValue("set-cookie").orElseThrow().split(";", 2)[0];
        var login =
            server.send(
                "POST",
                FIXTURE_LOGIN_F843C044,
                initial,
                "_csrf=" + first.body().substring(6) + "&username=reader&password=p",
                true);
        assertEquals(302, login.statusCode());
        String cookie = login.headers().firstValue("set-cookie").orElseThrow().split(";", 2)[0];
        for (String path :
            List.of(
                FIXTURE_SCENARIOS_26111785,
                FIXTURE_SCENARIOS_NUKITASHI1_CE816CE5,
                "/scenarios/NUKITASHI1/01")) {
          var response = server.send(FIXTURE_GET_04F32A7E, path, cookie, null, true);
          assertEquals(200, response.statusCode());
          var dom = Jsoup.parse(response.body());
          assertEquals(role, dom.select(".login-role").text());
          assertEquals(1, dom.select("input[name='_csrf']").size());
          assertTrue(
              response.headers().firstValue("cache-control").orElseThrow().contains("no-store"));
          assertEquals(
              "nosniff", response.headers().firstValue("x-content-type-options").orElseThrow());
        }
        f.code = FIXTURE_0102_C967CE66;
        int before = f.sent.get();
        var expired =
            server.send(FIXTURE_GET_04F32A7E, FIXTURE_SCENARIOS_26111785, cookie, null, true);
        assertEquals(302, expired.statusCode());
        assertEquals(
            "/login?session-expired", expired.headers().firstValue("location").orElseThrow());
        assertTrue(expired.headers().firstValue("set-cookie").orElseThrow().contains("Max-Age=0"));
        assertEquals(before + 1, f.sent.get());
        var next =
            server.send(FIXTURE_GET_04F32A7E, FIXTURE_SCENARIOS_26111785, cookie, null, true);
        assertEquals(302, next.statusCode());
        assertEquals(FIXTURE_LOGIN_F843C044, next.headers().firstValue("location").orElseThrow());
        assertEquals(before + 1, f.sent.get());
        assertEquals(0, server.context.getManager().getActiveSessions());
        f.erased();
        loginApi.erased();
      }
    }
  }

  private static MockHttpServletRequest raw(String path) {
    var r = new MockHttpServletRequest(FIXTURE_GET_04F32A7E, path);
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
      case FIXTURE_GAM_5BC4EFCF -> FIXTURE_SCENARIOS_26111785;
      case FIXTURE_RTE_F939614A -> FIXTURE_SCENARIOS_NUKITASHI1_CE816CE5;
      case FIXTURE_SCF_AC95C8D1 -> "/scenarios/NUKITASHI1/01";
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
    volatile String code = FIXTURE_0000_876EEFE0;
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
                    case FIXTURE_GAM_5BC4EFCF -> 0;
                    case FIXTURE_RTE_F939614A -> 12;
                    case FIXTURE_SCF_AC95C8D1 -> 14;
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
      return security.mock(FIXTURE_GET_04F32A7E, path);
    }

    String call(String type, Principal p, Model m, HttpServletRequest r, HttpServletResponse s)
        throws IOException {
      return switch (type) {
        case FIXTURE_GAM_5BC4EFCF -> controller.games(p, m, r, s);
        case FIXTURE_RTE_F939614A -> controller.routes(FIXTURE_NUKITASHI1_F97F2EAE, p, m, r, s);
        case FIXTURE_SCF_AC95C8D1 ->
            controller.files(FIXTURE_NUKITASHI1_F97F2EAE, "01", p, m, r, s);
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
      String game =
          type.equals(FIXTURE_GAM_5BC4EFCF)
              ? FIXTURE_NUKITASHI1_F97F2EAE
              : ascii(request, 256, 12).stripTrailing();
      int prefix = type.equals(FIXTURE_SCF_AC95C8D1) ? Integer.parseInt(ascii(request, 268, 2)) : 1;
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
    boolean success = code.equals(FIXTURE_0000_876EEFE0) || code.equals("0200");
    int count = success ? requestedCount : 0;
    int data = type.equals(FIXTURE_SCF_AC95C8D1) ? 88 : 9;
    int record =
        switch (type) {
          case FIXTURE_GAM_5BC4EFCF -> 272;
          case FIXTURE_RTE_F939614A -> 72;
          case FIXTURE_SCF_AC95C8D1 -> 800;
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
    if (type.equals(FIXTURE_SCF_AC95C8D1)) {
      put(bytes, 256, 12, success ? game : "");
      number(bytes, 268, 2, success ? prefix : 0);
      put(bytes, 270, 64, success ? "共通ルート" : "");
      number(bytes, 334, 9, count);
    } else number(bytes, 256, 9, count);
    for (int n = 0; n < count; n++) {
      int offset = 256 + data + n * record;
      switch (type) {
        case FIXTURE_GAM_5BC4EFCF -> {
          put(
              bytes,
              offset,
              12,
              n % 2 == 0 ? FIXTURE_NUKITASHI1_F97F2EAE : FIXTURE_NUKITASHI2_3B3D052F);
          put(bytes, offset + 12, 256, n % 2 == 0 ? "NUKITASHI" : FIXTURE_NUKITASHI2_3B3D052F);
          number(bytes, offset + 268, 3, n + 1);
        }
        case FIXTURE_RTE_F939614A -> {
          number(bytes, offset, 2, n + 1);
          put(bytes, offset + 2, 64, n == 0 ? "共通ルート" : "未分類");
          number(bytes, offset + 66, 6, n + 7);
        }
        case FIXTURE_SCF_AC95C8D1 -> {
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
