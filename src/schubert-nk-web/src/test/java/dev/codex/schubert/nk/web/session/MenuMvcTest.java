package dev.codex.schubert.nk.web.session;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;

import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.layout.semantic.UserRole;
import dev.codex.schubert.nk.web.config.WebMvcConfiguration;
import dev.codex.schubert.nk.web.controller.MenuController;
import dev.codex.schubert.nk.web.logging.WebLogDatabaseFixture;
import dev.codex.schubert.nk.web.session.EmbeddedWebSecurityTest.Server;
import dev.codex.schubert.nk.web.view.MenuCard;
import dev.codex.schubert.nk.web.view.MenuViewModel;
import dev.codex.schubert.nk.web.view.TopBarViewModel;
import java.net.URLEncoder;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.security.Principal;
import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;
import java.util.Optional;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import org.jsoup.Jsoup;
import org.jsoup.nodes.Document;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;
import org.springframework.mock.web.MockServletContext;
import org.springframework.security.web.csrf.CsrfToken;
import org.springframework.security.web.csrf.DefaultCsrfToken;
import org.springframework.security.web.servlet.support.csrf.CsrfRequestDataValueProcessor;
import org.springframework.test.web.servlet.setup.MockMvcBuilders;
import org.springframework.ui.ExtendedModelMap;
import org.springframework.web.context.support.AnnotationConfigWebApplicationContext;
import org.thymeleaf.spring6.SpringTemplateEngine;
import org.thymeleaf.spring6.templateresolver.SpringResourceTemplateResolver;
import org.thymeleaf.spring6.view.ThymeleafViewResolver;
import org.thymeleaf.templatemode.TemplateMode;

/**
 * NK-WEB-001/PT-WEB-142..147; FUN-002/AUT-001..003/SYS-006/TST-001..005; UI221..223/226;
 * SS313/314/352; PG-D-115.
 */
class MenuMvcTest {
  // Independent Current/UI223 oracle: never generated from production MenuCard or Model.
  private static final List<String> TITLES =
      List.of("シナリオ閲覧", "検索", "アニメ視聴", "音楽", "質問する", "通知", "質問回答", "ログ照会", "User管理");
  private static final List<String> DESCRIPTIONS =
      List.of(
          "シナリオ一覧から本文を読む",
          "本文、話者、章タイトル、音声有無で探す",
          "メインパート、OVA、オープニング映像を見る",
          "BGMや曲を一覧から再生する",
          "質問を送信する",
          "自分への通知を確認する",
          "質問と回答を確認する",
          "操作ログとリクエストログを検索する",
          "ユーザーを作成・管理する");
  private static final List<String> URLS =
      List.of(
          "/scenarios",
          "/search",
          "/animation",
          "/music",
          "/questions/new",
          "/notifications",
          "/questions",
          "/logs",
          "/admin/users");
  private static WebLogDatabaseFixture db;
  @TempDir Path root;

  @BeforeAll
  static void database(@TempDir Path path) throws Exception {
    db = new WebLogDatabaseFixture(path);
  }

  @AfterAll
  static void stop() throws Exception {
    if (db != null) db.stop();
  }

  @BeforeEach
  void reset() throws Exception {
    try (var c = db.web();
        var statement = c.createStatement()) {
      statement.executeUpdate("DELETE FROM schubert_web_session.web_http_sessions");
    }
  }

  @Test
  void web142MenuModelsPreserveRoleOrderAndClosedFields() {
    for (String role : List.of("USER", "ADMIN")) {
      var page = MenuViewModel.from(principal("reader", role));
      int count = role.equals("USER") ? 7 : 9;
      assertEquals(
          TITLES.subList(0, count), page.getCards().stream().map(MenuCard::getTitle).toList());
      assertEquals(
          DESCRIPTIONS.subList(0, count),
          page.getCards().stream().map(MenuCard::getDescription).toList());
      assertEquals(
          URLS.subList(0, count), page.getCards().stream().map(MenuCard::getHref).toList());
      assertThrows(UnsupportedOperationException.class, () -> page.getCards().clear());
      assertEquals("schubert NK", page.getTopBar().getBrand());
      assertEquals("reader", page.getTopBar().getUsername());
      assertEquals(role, page.getTopBar().getRole());
      assertEquals("MenuViewModel[REDACTED]", page.toString());
      assertEquals("TopBarViewModel[REDACTED]", page.getTopBar().toString());
      var model = new ExtendedModelMap();
      assertEquals("menu", new MenuController().show(principal("reader", role), model));
      assertEquals(Set.of("page"), model.keySet());
      assertInstanceOf(MenuViewModel.class, model.get("page"));
    }
  }

  @Test
  void web143MenuBoundaryNullForeignAndModelFaultsReject() {
    var controller = new MenuController();
    var p = principal("reader", "USER");
    var model = new ExtendedModelMap();
    assertThrows(NullPointerException.class, () -> controller.show(null, model));
    assertThrows(NullPointerException.class, () -> controller.show(p, null));
    assertThrows(NullPointerException.class, () -> MenuViewModel.from(null));
    assertThrows(NullPointerException.class, () -> TopBarViewModel.from(null));
    Principal foreign =
        () -> {
          throw new AssertionError("foreign identity read");
        };
    assertThrows(SessionStoreException.class, () -> controller.show(foreign, model));
    assertTrue(model.isEmpty());
    var failure = new IllegalStateException("synthetic model fault");
    var failing =
        new ExtendedModelMap() {
          @Override
          public ExtendedModelMap addAttribute(String key, Object value) {
            throw failure;
          }
        };
    assertSame(
        failure, assertThrows(IllegalStateException.class, () -> controller.show(p, failing)));
  }

  @Test
  void web144MvcConfigurationIsExplicitUtf8AndClosed() throws Exception {
    var config = new WebMvcConfiguration();
    assertThrows(NullPointerException.class, () -> config.templateResolver(null));
    assertThrows(NullPointerException.class, () -> config.templateEngine(null));
    assertThrows(NullPointerException.class, () -> config.thymeleafViewResolver(null));
    assertThrows(NullPointerException.class, () -> config.addResourceHandlers(null));
    assertInstanceOf(CsrfRequestDataValueProcessor.class, config.requestDataValueProcessor());
    assertInstanceOf(MenuController.class, config.menuController());
    try (var context = mvc()) {
      var resolver = context.getBean(SpringResourceTemplateResolver.class);
      assertEquals("classpath:/templates/", resolver.getPrefix());
      assertEquals(".html", resolver.getSuffix());
      assertEquals("UTF-8", resolver.getCharacterEncoding());
      assertEquals(TemplateMode.HTML, resolver.getTemplateMode());
      assertTrue(resolver.isCacheable());
      assertTrue(resolver.getCheckExistence());
      var engine = context.getBean(SpringTemplateEngine.class);
      assertFalse(engine.getEnableSpringELCompiler());
      var views = context.getBean(ThymeleafViewResolver.class);
      assertSame(engine, views.getTemplateEngine());
      assertEquals("UTF-8", views.getCharacterEncoding());
      assertEquals("text/html;charset=UTF-8", views.getContentType());
      assertTrue(views.getForceContentType());
      assertFalse(views.getAlwaysProcessRedirectAndForward());
      assertFalse(views.getProducePartialOutputWhileProcessing());
      for (String name :
          List.of(
              "unknown", "../private", "redirect:https://invalid.example", "forward:/admin/users"))
        assertNull(views.resolveViewName(name, Locale.JAPAN));
      var mock = MockMvcBuilders.webAppContextSetup(context).build();
      var result =
          mock.perform(
                  get("/")
                      .principal(principal("reader", "USER"))
                      .param("role", "ADMIN")
                      .requestAttr(
                          CsrfToken.class.getName(),
                          new DefaultCsrfToken("unused", "_csrf", "b".repeat(64))))
              .andReturn();
      assertEquals(200, result.getResponse().getStatus());
      assertEquals("UTF-8", result.getResponse().getCharacterEncoding());
      verifyHtml(result.getResponse().getContentAsString(), "reader", "USER", "b".repeat(64));
      assertEquals(
          404, mock.perform(get("/not-a-controller")).andReturn().getResponse().getStatus());
    }
  }

  @Test
  void web145RealHttpMenuHasExactCardsAndLogoutCsrf() throws Exception {
    for (String role : List.of("USER", "ADMIN")) {
      reset();
      var api = new SessionFormLoginTest.Api("0000", role, "0000", 0);
      try (var server = server(api, false)) {
        var anonymous = server.send("GET", "/", null, null, true);
        assertEquals(302, anonymous.statusCode());
        assertEquals("/login", anonymous.headers().firstValue("location").orElseThrow());
        var first = server.send("GET", "/login", cookie(anonymous), null, true);
        var login =
            server.send(
                "POST",
                "/login",
                cookie(anonymous),
                form(first.body().substring(6), "reader", "p"),
                true);
        assertEquals(302, login.statusCode());
        assertEquals("/", login.headers().firstValue("location").orElseThrow());
        var menu = server.send("GET", "/", cookie(login), null, true);
        assertEquals(200, menu.statusCode());
        verifyHtml(menu.body(), "reader", role, "04".repeat(32));
        safeHeaders(menu);
        assertTrue(menu.headers().allValues("set-cookie").isEmpty());
        assertEquals(0, server.context.getManager().getActiveSessions());
        assertEquals(0, server.posts.get());
        assertEquals(0, server.converted.get());
        assertEquals(1, api.sends.get());
      }
      api.erased();
    }
  }

  @Test
  void web146HtmlEscapesIdentityAndServesOnlySafeResources() throws Exception {
    String username = "<img src=x onerror=alert(1)>";
    var api = new SessionFormLoginTest.Api("0000", "USER", "0000", 0);
    try (var server = server(api, false)) {
      var first = server.send("GET", "/login", null, null, true);
      var login =
          server.send(
              "POST",
              "/login",
              cookie(first),
              form(first.body().substring(6), username, "private-password-canary"),
              true);
      var menu = server.send("GET", "/", cookie(login), null, true);
      assertEquals(200, menu.statusCode());
      verifyHtml(menu.body(), username, "USER", "04".repeat(32));
      assertFalse(menu.body().contains(username));
      assertTrue(menu.body().contains("&lt;img"));
      assertFalse(menu.body().contains("private-password-canary"));
      var css = server.send("GET", "/css/schubert.css", null, null, true);
      assertEquals(200, css.statusCode());
      assertTrue(css.headers().firstValue("content-type").orElseThrow().startsWith("text/css"));
      assertTrue(css.body().contains("@media (max-width: 900px)"));
      assertTrue(css.body().contains("outline: 2px solid #1f6feb"));
      assertTrue(css.body().contains("max-width: 1180px"));
      assertTrue(css.body().contains("grid-template-columns: repeat(2, minmax(220px, 1fr))"));
      assertFalse(css.body().contains("@import"));
      assertFalse(css.body().contains("url("));
      var head = server.send("HEAD", "/css/schubert.css", null, null, true);
      assertEquals(200, head.statusCode());
      assertEquals("", head.body());
      var absent = server.send("GET", "/css/missing.css", cookie(login), null, true);
      assertEquals(404, absent.statusCode());
      assertFalse(absent.body().contains("classpath:"));
      assertEquals(0, server.context.getManager().getActiveSessions());
    }
    api.erased();
  }

  @Test
  void web147ConcurrentMenuRenderingKeepsActorsAndCsrfSeparate() throws Exception {
    var api = new SessionFormLoginTest.Api("0000", "DYNAMIC", "0000", 0);
    try (var server = server(api, true);
        var pool = Executors.newFixedThreadPool(8)) {
      var futures = new ArrayList<Future<Void>>();
      var cookies = ConcurrentHashMap.<String>newKeySet();
      var csrfTokens = ConcurrentHashMap.<String>newKeySet();
      for (int i = 0; i < 100; i++) {
        int n = i;
        futures.add(
            pool.submit(
                () -> {
                  var first = server.send("GET", "/login", null, null, true);
                  var login =
                      server.send(
                          "POST",
                          "/login",
                          cookie(first),
                          form(first.body().substring(6), "user" + n, "password-user" + n),
                          true);
                  assertEquals(302, login.statusCode());
                  String cookie = cookie(login);
                  assertTrue(cookies.add(cookie));
                  var menu = server.send("GET", "/", cookie, null, true);
                  assertEquals(200, menu.statusCode());
                  var document = Jsoup.parse(menu.body());
                  String csrf = document.select("form.logout-form input[name=_csrf]").attr("value");
                  assertEquals(64, csrf.length());
                  assertTrue(csrfTokens.add(csrf));
                  assertNotEquals(first.body().substring(6), csrf);
                  verifyHtml(menu.body(), "user" + n, n % 2 == 0 ? "USER" : "ADMIN", csrf);
                  return null;
                }));
      }
      for (var future : futures) future.get(30, TimeUnit.SECONDS);
      assertEquals(100, cookies.size());
      assertEquals(100, csrfTokens.size());
      assertEquals(100, api.sends.get());
      assertEquals(0, server.context.getManager().getActiveSessions());
      assertEquals(0, server.errorCalls.get());
    }
    api.erased();
  }

  private static void verifyHtml(String html, String name, String role, String csrf) {
    Document document = Jsoup.parse(html);
    assertEquals("ja", document.select("html").attr("lang"));
    assertEquals("schubert NK", document.title());
    assertEquals("schubert NK", document.select("main.page header.topbar h1").text());
    assertEquals(name, document.select(".login-user").text());
    assertEquals(role, document.select(".login-role").text());
    assertEquals(1, document.select("main").size());
    assertEquals(
        List.of("/", "/notifications"), document.select("nav.nav-links a").eachAttr("href"));
    int count = role.equals("USER") ? 7 : 9;
    assertEquals(
        TITLES.subList(0, count), document.select(".menu-grid .menu-item strong").eachText());
    assertEquals(
        DESCRIPTIONS.subList(0, count), document.select(".menu-grid .menu-item span").eachText());
    assertEquals(URLS.subList(0, count), document.select(".menu-grid .menu-item").eachAttr("href"));
    assertEquals("post", document.select("form.logout-form").attr("method"));
    assertEquals("/logout", document.select("form.logout-form").attr("action"));
    assertEquals("ログアウト", document.select("form.logout-form button[type=submit]").text());
    assertEquals(1, document.select("input").size());
    assertEquals("hidden", document.select("input[name=_csrf]").attr("type"));
    assertEquals(csrf, document.select("input[name=_csrf]").attr("value"));
    assertEquals(1, document.select("link[rel=stylesheet]").size());
    assertEquals("/css/schubert.css", document.select("link[rel=stylesheet]").attr("href"));
    assertTrue(document.select("script, style, img, iframe, object, embed, [style]").isEmpty());
    for (var element : document.getAllElements())
      for (var attribute : element.attributes()) {
        assertFalse(attribute.getKey().startsWith("on"));
        assertFalse(attribute.getKey().startsWith("data-"));
      }
    assertFalse(html.contains("a".repeat(64)));
    assertFalse(html.contains("SCHUBERT_NK_SESSION"));
    assertFalse(html.contains("JSESSIONID"));
    assertFalse(html.contains("SessionPrincipal"));
    assertFalse(html.contains("authenticationContext"));
  }

  private static SessionPrincipal principal(String name, String role) {
    return new SessionPrincipal(
        name,
        UserRole.valueOf(role),
        AuthenticationContext.of("a".repeat(64)),
        Instant.parse("2026-09-09T00:00:00Z"));
  }

  private static AnnotationConfigWebApplicationContext mvc() {
    var context = new AnnotationConfigWebApplicationContext();
    context.setServletContext(new MockServletContext());
    context.register(WebMvcConfiguration.class);
    context.refresh();
    return context;
  }

  private Server server(SessionFormLoginTest.Api api, boolean random) throws Exception {
    return new Server(
        Files.createTempDirectory(root, "menu-"), random, db, Optional.of(api.provider), true);
  }

  private static String form(String csrf, String name, String password) {
    return "_csrf="
        + csrf
        + "&username="
        + URLEncoder.encode(name, StandardCharsets.UTF_8)
        + "&password="
        + URLEncoder.encode(password, StandardCharsets.UTF_8);
  }

  private static String cookie(HttpResponse<String> response) {
    return response.headers().firstValue("set-cookie").orElseThrow().split(";", 2)[0];
  }

  private static void safeHeaders(HttpResponse<String> response) {
    assertEquals("no-store", response.headers().firstValue("cache-control").orElseThrow());
    assertEquals("DENY", response.headers().firstValue("x-frame-options").orElseThrow());
    assertEquals("nosniff", response.headers().firstValue("x-content-type-options").orElseThrow());
    assertTrue(
        response
            .headers()
            .firstValue("content-security-policy")
            .orElseThrow()
            .contains("form-action 'self'"));
  }
}
