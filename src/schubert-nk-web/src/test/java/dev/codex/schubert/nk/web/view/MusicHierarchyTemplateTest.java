package dev.codex.schubert.nk.web.view;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.layout.media.MusicCategoryRecord;
import dev.codex.schubert.nk.protocol.layout.media.MusicCategoryResponseData;
import dev.codex.schubert.nk.protocol.layout.media.MusicSectionRecord;
import dev.codex.schubert.nk.protocol.layout.media.MusicSectionResponseData;
import dev.codex.schubert.nk.protocol.layout.semantic.UserRole;
import dev.codex.schubert.nk.web.config.WebMvcConfiguration;
import dev.codex.schubert.nk.web.session.SessionPrincipal;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import org.jsoup.Jsoup;
import org.jsoup.nodes.Document;
import org.junit.jupiter.api.Test;
import org.springframework.mock.web.MockHttpServletRequest;
import org.springframework.mock.web.MockHttpServletResponse;
import org.springframework.mock.web.MockServletContext;
import org.springframework.security.web.csrf.CsrfToken;
import org.springframework.security.web.csrf.DefaultCsrfToken;
import org.springframework.web.context.support.AnnotationConfigWebApplicationContext;
import org.springframework.web.servlet.DispatcherServlet;
import org.thymeleaf.spring6.view.ThymeleafViewResolver;

/** SCR011/012/FUN007/UI222,223,235/SS313,352/PG209/PT-SCR066..071. */
class MusicHierarchyTemplateTest {
  private static SessionPrincipal actor(String name, UserRole role) {
    return new SessionPrincipal(
        name,
        role,
        AuthenticationContext.of("a".repeat(64)),
        Instant.parse("2026-09-19T00:00:00Z"));
  }

  private static MusicCategoryViewModel categories(
      String name, UserRole role, List<MusicCategoryRecord> r) {
    return MusicCategoryViewModel.from(
        actor(name, role), new MusicCategoryResponseData(r.size()), r);
  }

  private static MusicSectionViewModel sections(
      String name, UserRole role, String category, List<MusicSectionRecord> r) {
    return MusicSectionViewModel.from(
        actor(name, role), category, new MusicSectionResponseData(r.size()), r);
  }

  private static AnnotationConfigWebApplicationContext context() {
    var c = new AnnotationConfigWebApplicationContext();
    c.setServletContext(new MockServletContext());
    c.register(WebMvcConfiguration.class);
    c.refresh();
    return c;
  }

  private static Document render(
      AnnotationConfigWebApplicationContext context, String name, Object page, String csrf)
      throws Exception {
    var view = context.getBean(ThymeleafViewResolver.class).resolveViewName(name, Locale.JAPAN);
    assertNotNull(view);
    var request = new MockHttpServletRequest(context.getServletContext());
    request.setAttribute(DispatcherServlet.WEB_APPLICATION_CONTEXT_ATTRIBUTE, context);
    request.setMethod("GET");
    request.setRequestURI("/music");
    request.setScheme("https");
    request.setSecure(true);
    request.setPreferredLocales(List.of(Locale.JAPAN));
    request.setAttribute(CsrfToken.class.getName(), new DefaultCsrfToken("unused", "_csrf", csrf));
    var response = new MockHttpServletResponse();
    view.render(Map.of("page", page), request, response);
    assertEquals(200, response.getStatus());
    assertEquals("UTF-8", response.getCharacterEncoding());
    return Jsoup.parse(response.getContentAsString());
  }

  @Test
  void music066CategoryMenu() throws Exception {
    try (var c = context()) {
      for (var role : UserRole.values()) {
        var page =
            categories(
                "reader",
                role,
                List.of(
                    new MusicCategoryRecord("曲", 29),
                    new MusicCategoryRecord("BGM", 99),
                    new MusicCategoryRecord("その他", 1)));
        var dom = render(c, "music", page, "public-csrf");
        assertEquals("Music", dom.title());
        assertEquals("Music", dom.select("h1").text());
        assertEquals("129曲", dom.select(".subtitle").text());
        assertEquals(List.of("曲", "BGM", "その他"), dom.select(".menu-item strong").eachText());
        assertEquals(
            List.of("分類を選択する", "分類を選択する", "分類を選択する"), dom.select(".menu-item span").eachText());
        assertEquals(
            List.of("/music/%E6%9B%B2", "/music/BGM", "/music/%E3%81%9D%E3%81%AE%E4%BB%96"),
            dom.select(".menu-item").eachAttr("href"));
        assertEquals(
            List.of("/scenarios", "/search", "/animation"),
            dom.select("nav[aria-label=Musicナビゲーション] a").eachAttr("href"));
        assertEquals(role.wireValue(), dom.select(".login-role").text());
        common(dom, "reader", "public-csrf");
      }
    }
  }

  @Test
  void music067SectionMenu() throws Exception {
    try (var c = context()) {
      for (var role : UserRole.values()) {
        var page =
            sections(
                "reader",
                role,
                "曲",
                List.of(
                    new MusicSectionRecord("ゲーム", 10),
                    new MusicSectionRecord("アニメ", 15),
                    new MusicSectionRecord("キャラクターソング", 4)));
        var dom = render(c, "music-sections", page, "public-csrf");
        assertEquals("曲", dom.title());
        assertEquals("曲", dom.select("h1").text());
        assertEquals("29曲", dom.select(".subtitle").text());
        assertEquals(
            List.of("ゲーム", "アニメ", "キャラクターソング"), dom.select(".menu-item strong").eachText());
        assertEquals(List.of("10曲", "15曲", "4曲"), dom.select(".menu-item span").eachText());
        assertEquals(
            "/music/%E6%9B%B2/%E3%82%B2%E3%83%BC%E3%83%A0",
            dom.select(".menu-item").getFirst().attr("href"));
        assertEquals(
            List.of("/music", "/search"),
            dom.select("nav[aria-label=Musicナビゲーション] a").eachAttr("href"));
        assertEquals(role.wireValue(), dom.select(".login-role").text());
        common(dom, "reader", "public-csrf");
      }
    }
  }

  @Test
  void music068EmptyAndMaximum() throws Exception {
    try (var c = context()) {
      for (var dom :
          List.of(
              render(c, "music", categories("reader", UserRole.USER, List.of()), "public-csrf"),
              render(
                  c,
                  "music-sections",
                  sections("reader", UserRole.USER, "BGM", List.of()),
                  "public-csrf"))) {
        assertEquals("0曲", dom.select(".subtitle").text());
        assertTrue(dom.select(".menu-grid").text().isEmpty());
        assertTrue(dom.select(".menu-item,.empty-results").isEmpty());
        assertFalse(dom.text().contains("該当するデータはありません"));
      }
      var categories = new ArrayList<MusicCategoryRecord>();
      for (int i = 0; i < 20; i++) categories.add(new MusicCategoryRecord("cat" + i, 999999));
      var a = render(c, "music", categories("reader", UserRole.USER, categories), "public-csrf");
      assertEquals("19999980曲", a.select(".subtitle").text());
      assertEquals(20, a.select(".menu-item").size());
      assertEquals("/music/cat0", a.select(".menu-item").getFirst().attr("href"));
      assertEquals("/music/cat19", a.select(".menu-item").getLast().attr("href"));
      var sections = new ArrayList<MusicSectionRecord>();
      for (int i = 0; i < 100; i++) sections.add(new MusicSectionRecord("sec" + i, 999999));
      var b =
          render(
              c,
              "music-sections",
              sections("reader", UserRole.USER, "BGM", sections),
              "public-csrf");
      assertEquals("99999900曲", b.select(".subtitle").text());
      assertEquals(100, b.select(".menu-item").size());
      assertEquals("/music/BGM/sec0", b.select(".menu-item").getFirst().attr("href"));
      assertEquals("/music/BGM/sec99", b.select(".menu-item").getLast().attr("href"));
    }
  }

  @Test
  void music069EscapingAndCsrf() throws Exception {
    try (var c = context()) {
      String text = "<b>&";
      var a =
          render(
              c,
              "music",
              categories(text, UserRole.ADMIN, List.of(new MusicCategoryRecord(text, 1))),
              "public<&csrf");
      var b =
          render(
              c,
              "music-sections",
              sections(text, UserRole.ADMIN, text, List.of(new MusicSectionRecord(text, 1))),
              "public<&csrf");
      for (var dom : List.of(a, b)) {
        common(dom, text, "public<&csrf");
        assertEquals(text, dom.select(".menu-item strong").text());
        assertTrue(dom.select("b,img,script,[onerror],[onclick],[style]").isEmpty());
        assertFalse(dom.outerHtml().contains("a".repeat(64)));
      }
      assertEquals(text, b.title());
      assertEquals(text, b.select("h1").text());
      assertEquals("/music/%3Cb%3E%26", a.select(".menu-item").attr("href"));
      assertEquals("/music/%3Cb%3E%26/%3Cb%3E%26", b.select(".menu-item").attr("href"));
    }
  }

  @Test
  void music070CssAndViewBoundary() throws Exception {
    try (var c = context()) {
      var resolver = c.getBean(ThymeleafViewResolver.class);
      for (var name : List.of("music", "music-sections"))
        assertNotNull(resolver.resolveViewName(name, Locale.JAPAN));
      for (var name : List.of("music-private", "../music", "redirect:https://invalid.example"))
        assertNull(resolver.resolveViewName(name, Locale.JAPAN));
      var css = Files.readString(Path.of("src/main/resources/static/css/schubert.css"));
      for (var rule :
          List.of(
              ".menu-grid { display: grid; grid-template-columns: repeat(2, minmax(220px, 1fr)); gap: 14px; }",
              ".menu-item { display: grid; gap: 8px; min-height: 132px; align-content: center; padding: 20px; background: #ffffff; border: 1px solid #dde1e6; border-radius: 8px; color: inherit; text-decoration: none; }",
              ".menu-item strong { font-size: 22px; }",
              ".menu-item span { color: #5f6368; line-height: 1.5; }",
              "@media (max-width: 900px)",
              ".menu-grid { grid-template-columns: 1fr; }")) assertTrue(css.contains(rule), rule);
      for (var name : List.of("music", "music-sections")) {
        var html = Files.readString(Path.of("src/main/resources/templates/" + name + ".html"));
        assertFalse(html.contains("<script"));
        assertFalse(html.contains("<style"));
      }
    }
  }

  @Test
  void music071ConcurrentRendering() throws Exception {
    try (var c = context();
        var pool = Executors.newFixedThreadPool(8)) {
      var tasks = new ArrayList<Future<?>>();
      for (int i = 0; i < 64; i++) {
        final int n = i;
        tasks.add(
            pool.submit(
                () -> {
                  String username = "reader" + n;
                  String token = "public-csrf-" + n;
                  Document dom;
                  if (n % 2 == 0) {
                    dom =
                        render(
                            c,
                            "music",
                            categories(
                                username,
                                UserRole.USER,
                                List.of(new MusicCategoryRecord("cat" + n, n))),
                            token);
                    assertEquals("cat" + n, dom.select(".menu-item strong").text());
                    assertEquals("/music/cat" + n, dom.select(".menu-item").attr("href"));
                  } else {
                    dom =
                        render(
                            c,
                            "music-sections",
                            sections(
                                username,
                                UserRole.ADMIN,
                                "cat" + n,
                                List.of(new MusicSectionRecord("sec" + n, n))),
                            token);
                    assertEquals("sec" + n, dom.select(".menu-item strong").text());
                    assertEquals(
                        "/music/cat" + n + "/sec" + n, dom.select(".menu-item").attr("href"));
                  }
                  assertEquals(n + "曲", dom.select(".subtitle").text());
                  common(dom, username, token);
                  return null;
                }));
      }
      for (var task : tasks) task.get(10, TimeUnit.SECONDS);
      var directory = Path.of("target/scenario-screen-traces");
      Files.createDirectories(directory);
      Files.writeString(
          directory.resolve("PT-SCR-071.txt"),
          "templates=music|music-sections\nfixture=public-synthetic\nconcurrentRenders=64\nmaximumCategories=20\nmaximumSections=100\nactualNkGate=false\n",
          StandardCharsets.US_ASCII);
    }
  }

  private static void common(Document dom, String username, String csrf) {
    assertEquals(username, dom.select(".login-user").text());
    assertEquals("post", dom.select("form.logout-form").attr("method"));
    assertEquals("/logout", dom.select("form.logout-form").attr("action"));
    assertEquals(1, dom.select("input[name=_csrf]").size());
    assertEquals(csrf, dom.select("input[name=_csrf]").attr("value"));
    assertEquals(1, dom.select("a[href='/']").size());
    assertEquals(1, dom.select("a[href='/notifications']").size());
    assertEquals("ja", dom.select("html").attr("lang"));
    assertEquals("/css/schubert.css", dom.select("link[rel=stylesheet]").attr("href"));
  }
}
