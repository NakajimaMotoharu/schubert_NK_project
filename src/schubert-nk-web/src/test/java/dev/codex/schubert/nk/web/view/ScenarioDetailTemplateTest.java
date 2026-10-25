package dev.codex.schubert.nk.web.view;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.layout.scenario.ScenarioDetailResponseData;
import dev.codex.schubert.nk.protocol.layout.scenario.ScenarioEntryRecord;
import dev.codex.schubert.nk.protocol.layout.semantic.AudioId;
import dev.codex.schubert.nk.protocol.layout.semantic.DeliveryMode;
import dev.codex.schubert.nk.protocol.layout.semantic.DisplayPath;
import dev.codex.schubert.nk.protocol.layout.semantic.EntryId;
import dev.codex.schubert.nk.protocol.layout.semantic.EntryType;
import dev.codex.schubert.nk.protocol.layout.semantic.GameCode;
import dev.codex.schubert.nk.protocol.layout.semantic.RelativePath;
import dev.codex.schubert.nk.protocol.layout.semantic.ScriptFileId;
import dev.codex.schubert.nk.protocol.layout.semantic.Sha256Hex;
import dev.codex.schubert.nk.protocol.layout.semantic.UserRole;
import dev.codex.schubert.nk.web.config.WebMvcConfiguration;
import dev.codex.schubert.nk.web.session.SessionPrincipal;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Instant;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;
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
import org.thymeleaf.spring6.view.ThymeleafViewResolver;

/** Production template PT, not a registered detail endpoint: UI223,234/SS313/PG196/SCR017..024. */
class ScenarioDetailTemplateTest {
  private static ScenarioEntryRecord entry(long id, int sequence, int audio, String body) {
    return new ScenarioEntryRecord(
        new EntryId(id),
        sequence,
        sequence + 10,
        audio == 0 ? EntryType.NARRATION : EntryType.DIALOGUE,
        audio == 0 ? Optional.empty() : Optional.of("話者<img>"),
        body,
        audio,
        audio == 0 ? Optional.empty() : Optional.of(new AudioId(id * 1000 + audio)),
        audio == 0
            ? Optional.empty()
            : Optional.of(DisplayPath.of("音声/" + id + "-" + audio + ".ogg")));
  }

  private static List<ScenarioEntryRecord> entries() {
    return List.of(
        entry(9, 1, 0, "地の文"),
        entry(3, 2, 1, "本文<&>"),
        entry(3, 2, 2, "本文<&>"),
        entry(7, 3, 1, "最後"));
  }

  private static ScenarioDetailViewModel page(
      String name,
      UserRole role,
      GameCode game,
      boolean previous,
      boolean next,
      List<ScenarioEntryRecord> records) {
    boolean file = records.size() > 200;
    var data =
        new ScenarioDetailResponseData(
            new ScriptFileId(23),
            game,
            "章<script>",
            DisplayPath.of("文章/01.txt"),
            previous ? Optional.of(new ScriptFileId(1)) : Optional.empty(),
            previous ? Optional.of("前章<&>") : Optional.empty(),
            next ? Optional.of(new ScriptFileId(999999999999L)) : Optional.empty(),
            next ? Optional.of("次章") : Optional.empty(),
            file ? DeliveryMode.FILE : DeliveryMode.INLINE,
            file
                ? Optional.of(UUID.fromString("12345678-1234-4234-8234-123456789abc"))
                : Optional.empty(),
            file
                ? Optional.of(
                    RelativePath.of("20260920/12345678-1234-4234-8234-123456789abc.ready"))
                : Optional.empty(),
            file ? 4800L * records.size() : 0,
            file ? Optional.of(Sha256Hex.of("f".repeat(64))) : Optional.empty(),
            file ? 4800 : 0,
            file ? records.size() : 0);
    return ScenarioDetailViewModel.from(
        new SessionPrincipal(name, role, AuthenticationContext.of("a".repeat(64)), Instant.EPOCH),
        data,
        records);
  }

  private static ScenarioDetailViewModel page(List<ScenarioEntryRecord> records) {
    return page("reader", UserRole.USER, GameCode.NUKITASHI_1, true, true, records);
  }

  private static AnnotationConfigWebApplicationContext context() {
    var context = new AnnotationConfigWebApplicationContext();
    context.setServletContext(new MockServletContext());
    context.register(WebMvcConfiguration.class);
    context.refresh();
    return context;
  }

  private static String render(
      AnnotationConfigWebApplicationContext context, ScenarioDetailViewModel page, String csrf)
      throws Exception {
    var view =
        context.getBean(ThymeleafViewResolver.class).resolveViewName("scenario", Locale.JAPAN);
    assertNotNull(view);
    var request = new MockHttpServletRequest(context.getServletContext());
    request.setAttribute(
        org.springframework.web.servlet.DispatcherServlet.WEB_APPLICATION_CONTEXT_ATTRIBUTE,
        context);
    request.setMethod("GET");
    request.setRequestURI("/scenarios/23");
    request.setScheme("https");
    request.setSecure(true);
    request.setAttribute(CsrfToken.class.getName(), new DefaultCsrfToken("unused", "_csrf", csrf));
    var response = new MockHttpServletResponse();
    view.render(Map.of("page", page), request, response);
    assertEquals("UTF-8", response.getCharacterEncoding());
    assertEquals(200, response.getStatus());
    return response.getContentAsString();
  }

  @Test
  void detail017HeaderAndCommonLayout() throws Exception {
    try (var context = context()) {
      for (var role : UserRole.values())
        for (var game : GameCode.values()) {
          var dom =
              Jsoup.parse(
                  render(
                      context,
                      page("reader", role, game, false, false, entries()),
                      "synthetic-csrf"));
          assertEquals("ja", dom.select("html").attr("lang"));
          assertEquals("章<script>", dom.title());
          assertEquals("章<script>", dom.select("h1").text());
          assertEquals(
              (game == GameCode.NUKITASHI_1 ? "NUKITASHI1" : "NUKITASHI2") + " / 文章/01.txt",
              dom.select(".subtitle").text());
          assertEquals("schubert NK", dom.select(".brand").text());
          assertEquals("reader", dom.select(".login-user").text());
          assertEquals(role == UserRole.USER ? "USER" : "ADMIN", dom.select(".login-role").text());
          assertEquals(
              List.of("/", "/notifications", "/scenarios", "/search"),
              dom.select(".nav-links a").eachAttr("href"));
          assertEquals(List.of("メニュー", "通知", "一覧", "検索"), dom.select(".nav-links a").eachText());
          assertEquals("post", dom.select("form.logout-form").attr("method"));
          assertEquals("/logout", dom.select("form").attr("action"));
          assertEquals(1, dom.select("input").size());
          assertEquals("hidden", dom.select("input").attr("type"));
          assertEquals("_csrf", dom.select("input").attr("name"));
          assertEquals("synthetic-csrf", dom.select("input").attr("value"));
          assertEquals("/css/schubert.css", dom.select("link[rel=stylesheet]").attr("href"));
          assertEquals(1, dom.select("main.page.scenario-page").size());
        }
    }
  }

  @Test
  void detail018PreviousNext() throws Exception {
    try (var context = context()) {
      for (boolean previous : List.of(false, true))
        for (boolean next : List.of(false, true)) {
          var dom =
              Jsoup.parse(
                  render(
                      context,
                      page(
                          "reader", UserRole.USER, GameCode.NUKITASHI_1, previous, next, List.of()),
                      "csrf"));
          var navs = dom.select(".scenario-nav");
          assertEquals(2, navs.size());
          assertEquals(
              List.of("scenario navigation", "scenario navigation bottom"),
              navs.eachAttr("aria-label"));
          for (var nav : navs) {
            assertEquals(2, nav.childrenSize());
            assertEquals(previous ? "前: 前章<&>" : "前: なし", nav.child(0).text());
            assertEquals(next ? "次: 次章" : "次: なし", nav.child(1).text());
            assertEquals(previous ? "a" : "span", nav.child(0).tagName());
            assertEquals(next ? "a" : "span", nav.child(1).tagName());
            assertEquals(previous ? "/scenarios/1" : "", nav.child(0).attr("href"));
            assertEquals(next ? "/scenarios/999999999999" : "", nav.child(1).attr("href"));
          }
          assertTrue(navs.get(1).hasClass("bottom-nav"));
        }
    }
  }

  @Test
  void detail019EntriesAndVoices() throws Exception {
    try (var context = context()) {
      var dom = Jsoup.parse(render(context, page(entries()), "csrf"));
      var articles = dom.select(".script-entry");
      assertEquals(List.of("entry-9", "entry-3", "entry-7"), articles.eachAttr("id"));
      assertEquals(List.of("地の文", "本文<&>", "最後"), dom.select(".script-entry > p").eachText());
      assertTrue(articles.get(0).hasClass("narration"));
      assertTrue(articles.get(1).hasClass("dialogue"));
      assertEquals(List.of("11"), articles.get(0).select(".line-meta span").eachText());
      assertEquals(List.of("12", "話者<img>"), articles.get(1).select(".line-meta span").eachText());
      assertEquals(0, articles.get(0).select(".audio").size());
      assertEquals(2, articles.get(1).select(".audio").size());
      assertEquals(
          List.of("/audio/3001", "/audio/3002", "/audio/7001"),
          dom.select("audio").eachAttr("src"));
      assertEquals(
          List.of("/audio/3001/download", "/audio/3002/download", "/audio/7001/download"),
          dom.select("a.download").eachAttr("href"));
      assertEquals(List.of("DL", "DL", "DL"), dom.select("a.download").eachText());
      assertEquals(
          List.of("音声/3-1.ogg", "音声/3-2.ogg", "音声/7-1.ogg"), dom.select(".audio span").eachText());
      for (var audio : dom.select("audio")) {
        assertTrue(audio.hasAttr("controls"));
        assertEquals("none", audio.attr("preload"));
      }
    }
  }

  @Test
  void detail020EmptyScenario() throws Exception {
    try (var context = context()) {
      var dom = Jsoup.parse(render(context, page(List.of()), "csrf"));
      assertEquals(1, dom.select(".script-body").size());
      assertEquals("", dom.select(".script-body").text());
      assertTrue(dom.select("article,audio,.empty").isEmpty());
      assertEquals(2, dom.select(".scenario-nav").size());
      assertEquals("章<script>", dom.select("h1").text());
    }
  }

  @Test
  void detail021HtmlAndUrlSafety() throws Exception {
    try (var context = context()) {
      var html =
          render(
              context,
              page("reader<img>", UserRole.ADMIN, GameCode.NUKITASHI_2, true, true, entries()),
              "csrf");
      var dom = Jsoup.parse(html);
      assertEquals("reader<img>", dom.select(".login-user").text());
      assertEquals("本文<&>", dom.select(".script-entry > p").get(1).text());
      assertEquals("話者<img>", dom.select(".line-meta span").get(2).text());
      assertTrue(dom.select("script,style,img,iframe,object,embed,[style]").isEmpty());
      for (var element : dom.getAllElements())
        for (var attribute : element.attributes()) {
          assertFalse(attribute.getKey().startsWith("on"));
          assertFalse(attribute.getKey().startsWith("data-"));
          if (Set.of("href", "src", "action").contains(attribute.getKey())) {
            assertTrue(attribute.getValue().startsWith("/"));
            assertFalse(attribute.getValue().startsWith("//"));
          }
        }
      for (String forbidden :
          List.of(
              "a".repeat(64),
              "12345678-1234-4234-8234-123456789abc",
              ".ready",
              "fileRelativePath",
              "authenticationContext",
              "SessionPrincipal")) assertFalse(html.contains(forbidden));
    }
  }

  @Test
  void detail022MaximumRecordsAndVoices() throws Exception {
    try (var context = context()) {
      var records = new ArrayList<ScenarioEntryRecord>();
      for (int i = 1; i <= 10000; i++) records.add(entry(i, i, 0, "本文" + i));
      var dom = Jsoup.parse(render(context, page(records), "csrf"));
      assertEquals(10000, dom.select(".script-entry").size());
      assertEquals("本文1", dom.select(".script-entry > p").first().text());
      assertEquals("本文10000", dom.select(".script-entry > p").last().text());
      assertEquals("entry-10000", dom.select(".script-entry").last().id());
      records.clear();
      for (int i = 1; i <= 999; i++) records.add(entry(7, 1, i, "一つの本文"));
      dom = Jsoup.parse(render(context, page(records), "csrf"));
      assertEquals(1, dom.select(".script-entry > p").size());
      assertEquals("一つの本文", dom.select(".script-entry > p").text());
      assertEquals(999, dom.select("audio").size());
      assertEquals("/audio/7999", dom.select("audio").last().attr("src"));
    }
  }

  @Test
  void detail023CssAndViewBoundary() throws Exception {
    try (var context = context()) {
      var resolver = context.getBean(ThymeleafViewResolver.class);
      assertNotNull(resolver.resolveViewName("scenario", Locale.JAPAN));
      for (String name :
          List.of(
              "scenario-private",
              "../scenario",
              "redirect:https://invalid.example",
              "forward:/scenario")) assertNull(resolver.resolveViewName(name, Locale.JAPAN));
    }
    String css = Files.readString(Path.of("src/main/resources/static/css/schubert.css"));
    String added = css.substring(css.indexOf("/* PG196/"), css.indexOf("/* End PG196"));
    // Independent CSS declarations transcribed from Current scenario styles; no browser screenshot
    // claim.
    Map<String, String> declarations = new LinkedHashMap<>();
    declarations.put(
        ".scenario-nav",
        "display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 12px;");
    declarations.put(
        ".scenario-nav a, .scenario-nav span",
        "min-height: 40px; display: flex; align-items: center; padding: 0 12px; background: #fff; border: 1px solid #dde1e6; border-radius: 8px;");
    declarations.put(".scenario-nav a", "color: #1f6feb; text-decoration: none; font-weight: 700;");
    declarations.put(".scenario-nav a:hover", "text-decoration: underline;");
    declarations.put(
        ".scenario-nav a:last-child, .scenario-nav span:last-child", "justify-content: flex-end;");
    declarations.put(
        ".script-body",
        "display: grid; gap: 6px; background: #fff; border: 1px solid #dde1e6; border-radius: 8px; padding: 12px;");
    declarations.put(
        ".script-entry",
        "display: grid; grid-template-columns: 92px minmax(0, 1fr) 220px; gap: 12px; padding: 7px 0; border-bottom: 1px solid #edf0f4;");
    declarations.put(".script-entry:last-child", "border-bottom: 0;");
    declarations.put(
        ".script-entry .audio",
        "grid-column: 3; display: grid; grid-template-columns: minmax(0, 1fr) auto; gap: 8px; justify-items: end; margin-top: 0; align-items: center; color: #5f6368; font-size: 12px;");
    declarations.put(
        ".script-entry .audio span",
        "grid-column: 1 / -1; justify-self: end; overflow-wrap: anywhere; text-align: right;");
    declarations.put(
        ".line-meta",
        "display: flex; flex-direction: column; gap: 4px; color: #5f6368; font-size: 12px;");
    declarations.put(".dialogue .line-meta span:last-child", "color: #202124; font-weight: 700;");
    declarations.put(".narration p", "color: #34383f;");
    declarations.put(".bottom-nav", "margin-top: 12px; margin-bottom: 0;");
    declarations.put(
        ".script-entry:target",
        "margin: 0 -8px; padding: 9px 8px; background: #fff8d8; border: 1px solid #f0d36a; border-radius: 8px;");
    declarations.put(
        ".script-entry p", "white-space: pre-wrap; line-height: 1.7; margin: 10px 0 0;");
    declarations.put(
        ".script-entry .download",
        "display: inline-grid; place-items: center; min-width: 34px; height: 30px; padding: 0 8px; border: 1px solid #c9ced6; border-radius: 6px; color: #1f6feb; text-decoration: none; font-weight: 700; background: #fff;");
    declarations.put(".script-entry audio", "width: 320px; max-width: 100%; height: 34px;");
    var expected = new StringBuilder();
    declarations.forEach(
        (selector, body) -> expected.append(selector).append(" { ").append(body).append(" }\n"));
    expected.append(
        "@media (max-width: 900px) {\n  .scenario-nav { grid-template-columns: 1fr; }\n  .scenario-nav a:last-child, .scenario-nav span:last-child { justify-content: flex-start; }\n  .script-entry { grid-template-columns: 1fr; gap: 4px; }\n  .script-entry .audio { grid-column: 1; justify-items: stretch; }\n  .script-entry .audio span { justify-self: start; text-align: left; }\n}\n");
    assertEquals(expected.toString(), added.substring(added.indexOf("\n") + 1));
  }

  @Test
  void detail024ConcurrentRendering() throws Exception {
    try (var context = context();
        var executor = Executors.newFixedThreadPool(8)) {
      var tasks = new ArrayList<Future<Document>>();
      for (int i = 0; i < 64; i++) {
        final int n = i;
        tasks.add(
            executor.submit(
                () ->
                    Jsoup.parse(
                        render(
                            context,
                            page(
                                "reader" + n,
                                UserRole.USER,
                                GameCode.NUKITASHI_1,
                                false,
                                false,
                                List.of(entry(n + 1, 1, 0, "本文" + n))),
                            "csrf" + n))));
      }
      for (int i = 0; i < 64; i++) {
        var dom = tasks.get(i).get(10, TimeUnit.SECONDS);
        assertEquals("reader" + i, dom.select(".login-user").text());
        assertEquals("本文" + i, dom.select(".script-entry > p").text());
        assertEquals("csrf" + i, dom.select("input[name=_csrf]").attr("value"));
      }
      Path root = Path.of("target/scenario-screen-traces");
      Files.createDirectories(root);
      Files.writeString(
          root.resolve("PT-SCR-024.txt"),
          "template=scenario\nfixture=public-synthetic\nconcurrentRenders=64\nmaximumEntries=10000\nmaximumVoices=999\nactualNkGate=false\n",
          StandardCharsets.US_ASCII);
    }
  }
}
