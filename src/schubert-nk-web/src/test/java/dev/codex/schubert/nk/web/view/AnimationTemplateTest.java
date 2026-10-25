package dev.codex.schubert.nk.web.view;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.layout.media.AnimationListResponseData;
import dev.codex.schubert.nk.protocol.layout.media.AnimationMenuResponseData;
import dev.codex.schubert.nk.protocol.layout.media.AnimationRecord;
import dev.codex.schubert.nk.protocol.layout.semantic.AnimationCategory;
import dev.codex.schubert.nk.protocol.layout.semantic.AnimationListCategory;
import dev.codex.schubert.nk.protocol.layout.semantic.DisplayPath;
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
import java.util.Optional;
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

/** NK-WEB002/SCR008,009/FUN006/UI222,223,235/SS313/PG205/PT-SCR046..053. */
class AnimationTemplateTest {
  private static SessionPrincipal actor(String name, UserRole role) {
    return new SessionPrincipal(
        name,
        role,
        AuthenticationContext.of("a".repeat(64)),
        Instant.parse("2026-09-19T00:00:00Z"));
  }

  private static AnimationRecord record(
      String id, AnimationCategory category, Optional<String> parent, long bytes, int order) {
    return new AnimationRecord(
        id, "Title " + id, category, DisplayPath.of("video/" + id + ".mp4"), bytes, parent, order);
  }

  private static AnimationListViewModel list(
      String name, AnimationListCategory category, List<AnimationRecord> records) {
    return AnimationListViewModel.from(
        actor(name, UserRole.USER),
        category,
        new AnimationListResponseData(records.size()),
        records);
  }

  private static List<AnimationRecord> main() {
    return List.of(
        record("m1", AnimationCategory.MAIN, Optional.empty(), 1048576, 1),
        record("s1", AnimationCategory.SUBTRACK, Optional.of("m1"), 2097152, 2),
        record("m2", AnimationCategory.MAIN, Optional.empty(), 3145728, 3),
        record("m3", AnimationCategory.MAIN, Optional.empty(), 4194304, 4),
        record("s3", AnimationCategory.SUBTRACK, Optional.of("m3"), 5242880, 5));
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
    request.setRequestURI("/animation");
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
  void animation046Menu() throws Exception {
    try (var c = context()) {
      for (var role : UserRole.values())
        for (boolean populated : new boolean[] {false, true}) {
          var page =
              AnimationMenuViewModel.from(
                  actor("reader", role),
                  new AnimationMenuResponseData(
                      populated ? 15 : 0, populated ? 4 : 0, populated, populated ? 20 : 0));
          var dom = render(c, "animation", page, "public-csrf");
          assertEquals("Animation", dom.title());
          assertEquals("Animation", dom.select("h1").text());
          assertEquals("ja", dom.select("html").attr("lang"));
          assertEquals(
              List.of("メインパート一覧", "OVA一覧", "オープニング映像"), dom.select(".menu-item strong").eachText());
          assertEquals(
              List.of(populated ? "15本の映像" : "0本の映像", populated ? "4本の映像" : "0本の映像", "OP映像を再生する"),
              dom.select(".menu-item span").eachText());
          assertEquals(
              List.of("/animation/main", "/animation/ova", "/animation/opening"),
              dom.select(".menu-item").eachAttr("href"));
          assertEquals(
              List.of("/", "/notifications", "/scenarios", "/search"),
              dom.select(".nav-links a").eachAttr("href"));
          assertEquals(role.wireValue(), dom.select(".login-role").text());
          common(dom, "reader", "public-csrf");
        }
    }
  }

  @Test
  void animation047MainRows() throws Exception {
    try (var c = context()) {
      var dom =
          render(
              c,
              "animation-list",
              list("reader", AnimationListCategory.MAIN, main()),
              "public-csrf");
      assertEquals("メインパート一覧", dom.title());
      assertEquals("メインパート一覧", dom.select("h1").text());
      assertEquals("5本", dom.select(".subtitle").text());
      assertEquals(3, dom.select(".animation-row").size());
      assertEquals(
          List.of("Title m1", "Title m2", "Title m3"), dom.select(".scenario-title").eachText());
      assertEquals(
          List.of("/animation/videos/m1", "/animation/videos/m2", "/animation/videos/m3"),
          dom.select(".animation-main-link").eachAttr("href"));
      assertEquals(
          List.of("/animation/videos/s1", "/animation/videos/s3"),
          dom.select(".subtrack-link").eachAttr("href"));
      assertEquals(List.of("SUBTRACK", "SUBTRACK"), dom.select(".subtrack-link").eachText());
      assertEquals(1, dom.select(".animation-row").get(1).select(".subtrack-placeholder").size());
      assertEquals(
          List.of(
              "メインパート video/m1.mp4 1.0 MB",
              "メインパート video/m2.mp4 3.0 MB",
              "メインパート video/m3.mp4 4.0 MB"),
          dom.select(".scenario-meta").eachText());
      assertEquals(
          List.of("/", "/notifications", "/animation", "/search"),
          dom.select(".nav-links a").eachAttr("href"));
      common(dom, "reader", "public-csrf");
    }
  }

  @Test
  void animation048OvaRows() throws Exception {
    try (var c = context()) {
      var records =
          List.of(
              record("ova-hinami", AnimationCategory.OVA, Optional.empty(), 1048576, 1),
              record("ova-humino", AnimationCategory.OVA, Optional.empty(), 2097152, 2),
              record("ova-misaki", AnimationCategory.OVA, Optional.empty(), 3145728, 3),
              record("ova-nanase", AnimationCategory.OVA, Optional.empty(), 4194304, 4));
      var dom =
          render(
              c,
              "animation-list",
              list("reader", AnimationListCategory.OVA, records),
              "public-csrf");
      assertEquals("OVA一覧", dom.title());
      assertEquals("4本", dom.select(".subtitle").text());
      assertEquals(
          List.of("Title ova-hinami", "Title ova-humino", "Title ova-misaki", "Title ova-nanase"),
          dom.select(".scenario-title").eachText());
      assertEquals(
          List.of(
              "/animation/videos/ova-hinami",
              "/animation/videos/ova-humino",
              "/animation/videos/ova-misaki",
              "/animation/videos/ova-nanase"),
          dom.select("a.scenario-link").eachAttr("href"));
      assertEquals(
          List.of(
              "OVA video/ova-hinami.mp4 1.0 MB",
              "OVA video/ova-humino.mp4 2.0 MB",
              "OVA video/ova-misaki.mp4 3.0 MB",
              "OVA video/ova-nanase.mp4 4.0 MB"),
          dom.select(".scenario-meta").eachText());
      assertTrue(dom.select(".animation-row,.subtrack-link,.subtrack-placeholder").isEmpty());
      common(dom, "reader", "public-csrf");
    }
  }

  @Test
  void animation049EmptyAndMaximum() throws Exception {
    try (var c = context()) {
      for (var category : AnimationListCategory.values()) {
        var empty = render(c, "animation-list", list("reader", category, List.of()), "public-csrf");
        assertEquals("0本", empty.select(".subtitle").text());
        assertEquals(1, empty.select("section.animation-list").size());
        assertTrue(empty.select("section.animation-list").text().isEmpty());
        assertFalse(empty.text().contains("該当するデータはありません"));
        var records = new ArrayList<AnimationRecord>();
        for (int i = 0; i < 50; i++) {
          boolean sub = category == AnimationListCategory.MAIN && i % 2 == 1;
          records.add(
              record(
                  "v" + i,
                  category == AnimationListCategory.OVA
                      ? AnimationCategory.OVA
                      : sub ? AnimationCategory.SUBTRACK : AnimationCategory.MAIN,
                  sub ? Optional.of("v" + (i - 1)) : Optional.empty(),
                  i + 1,
                  i + 1));
        }
        var dom = render(c, "animation-list", list("reader", category, records), "public-csrf");
        assertEquals("50本", dom.select(".subtitle").text());
        assertEquals(50, dom.select("section a").size());
        assertEquals("/animation/videos/v0", dom.select("section a").getFirst().attr("href"));
        assertEquals("/animation/videos/v49", dom.select("section a").getLast().attr("href"));
        assertEquals(
            category == AnimationListCategory.MAIN ? 25 : 0, dom.select(".animation-row").size());
      }
    }
  }

  @Test
  void animation050MegabyteRounding() throws Exception {
    try (var c = context()) {
      long[] sizes = {1, 996147, 996148, 1048576, 1572864, 10485760};
      var records = new ArrayList<AnimationRecord>();
      for (int i = 0; i < sizes.length; i++)
        records.add(record("v" + i, AnimationCategory.OVA, Optional.empty(), sizes[i], i + 1));
      var dom =
          render(
              c,
              "animation-list",
              list("reader", AnimationListCategory.OVA, records),
              "public-csrf");
      assertEquals(
          List.of("0.0 MB", "0.9 MB", "1.0 MB", "1.0 MB", "1.5 MB", "10.0 MB"),
          dom.select(".scenario-meta > span:last-child").eachText());
    }
  }

  @Test
  void animation051EscapingAndCsrf() throws Exception {
    try (var c = context()) {
      String text = "<img src=x onerror=alert(1)>";
      var p = actor(text, UserRole.ADMIN);
      var menu = AnimationMenuViewModel.from(p, new AnimationMenuResponseData(0, 0, false, 0));
      var record =
          new AnimationRecord(
              "v1",
              text,
              AnimationCategory.OVA,
              DisplayPath.of("folder/<img>.mp4"),
              1,
              Optional.empty(),
              1);
      var list =
          AnimationListViewModel.from(
              p, AnimationListCategory.OVA, new AnimationListResponseData(1), List.of(record));
      var a = render(c, "animation", menu, "public-csrf");
      var b = render(c, "animation-list", list, "public-csrf");
      for (var dom : List.of(a, b)) {
        common(dom, text, "public-csrf");
        assertTrue(dom.select("img,script,[onclick],[onerror],[onchange],[style]").isEmpty());
        assertFalse(dom.outerHtml().contains("a".repeat(64)));
      }
      assertEquals(text, b.select(".scenario-title").text());
      assertTrue(b.select(".scenario-meta").text().contains("folder/<img>.mp4"));
      var special =
          new AnimationRecord(
              "v?x&y",
              text,
              AnimationCategory.OVA,
              DisplayPath.of("folder/a.mp4"),
              1,
              Optional.empty(),
              1);
      var dom =
          render(
              c,
              "animation-list",
              AnimationListViewModel.from(
                  p, AnimationListCategory.OVA, new AnimationListResponseData(1), List.of(special)),
              "public-csrf");
      assertEquals("/animation/videos/v%3Fx%26y", dom.select("a.scenario-link").attr("href"));
    }
  }

  @Test
  void animation052CssAndViewBoundary() throws Exception {
    try (var c = context()) {
      var resolver = c.getBean(ThymeleafViewResolver.class);
      for (String name : List.of("animation", "animation-list"))
        assertNotNull(resolver.resolveViewName(name, Locale.JAPAN));
      for (String name :
          List.of("animation-private", "../animation", "redirect:https://invalid.example"))
        assertNull(resolver.resolveViewName(name, Locale.JAPAN));
      String css = Files.readString(Path.of("src/main/resources/static/css/schubert.css"));
      int start = css.indexOf("/* PG205/");
      int end = css.indexOf("/* End PG205 Animation styles. */", start);
      assertTrue(start >= 0);
      assertTrue(end > start);
      String block = css.substring(start, end);
      String[] rules = {
        ".animation-page .animation-main-link, .animation-page .subtrack-link { color: #1f6feb; text-decoration: none; font-weight: 700; }",
        ".animation-page .animation-main-link:hover .scenario-title, .animation-page .subtrack-link:hover { text-decoration: underline; }",
        ".animation-page .animation-list .scenario-title { font-size: 17px; }",
        ".animation-page .animation-row { grid-template-columns: minmax(0, 1fr) 110px; align-items: center; gap: 14px; }",
        ".animation-page .animation-main-link { display: grid; gap: 7px; min-width: 0; color: inherit; }",
        ".animation-page .subtrack-link, .animation-page .subtrack-placeholder { display: inline-grid; place-items: center; min-height: 34px; }",
        ".animation-page .subtrack-link { border: 1px solid #c9ced6; border-radius: 6px; background: #fff; font-size: 12px; }",
        "@media (max-width: 900px) {",
        ".animation-page .animation-row { grid-template-columns: minmax(0, 1fr) 94px; }"
      };
      int previous = -1;
      for (String rule : rules) {
        int index = block.indexOf(rule);
        assertTrue(index > previous, rule);
        previous = index;
      }
      assertEquals(9, block.chars().filter(ch -> ch == '{').count());
    }
  }

  @Test
  void animation053ConcurrentRendering() throws Exception {
    try (var c = context();
        var executor = Executors.newFixedThreadPool(8)) {
      var tasks = new ArrayList<Future<?>>();
      for (int i = 0; i < 64; i++) {
        final int n = i;
        tasks.add(
            executor.submit(
                () -> {
                  String username = "reader" + n;
                  String token = "public-csrf-" + n;
                  if (n % 2 == 0) {
                    var menu =
                        AnimationMenuViewModel.from(
                            actor(username, UserRole.USER),
                            new AnimationMenuResponseData(n, 0, false, n));
                    var dom = render(c, "animation", menu, token);
                    common(dom, username, token);
                    assertEquals(n + "本の映像", dom.select(".menu-item span").getFirst().text());
                  } else {
                    var dom =
                        render(
                            c,
                            "animation-list",
                            list(username, AnimationListCategory.MAIN, main()),
                            token);
                    common(dom, username, token);
                    assertEquals("5本", dom.select(".subtitle").text());
                    assertEquals(3, dom.select(".animation-row").size());
                  }
                  return null;
                }));
      }
      for (var task : tasks) task.get(10, TimeUnit.SECONDS);
      Path directory = Path.of("target/scenario-screen-traces");
      Files.createDirectories(directory);
      Files.writeString(
          directory.resolve("PT-SCR-053.txt"),
          "templates=animation|animation-list\nfixture=public-synthetic\nconcurrentRenders=64\nmaximumRecords=50\nactualNkGate=false\n",
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
  }
}
