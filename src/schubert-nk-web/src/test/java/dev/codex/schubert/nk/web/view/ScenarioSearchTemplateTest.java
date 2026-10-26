package dev.codex.schubert.nk.web.view;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.head;

import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.layout.common.PagedResponseData;
import dev.codex.schubert.nk.protocol.layout.scenario.GameRecord;
import dev.codex.schubert.nk.protocol.layout.scenario.ScenarioSearchRecord;
import dev.codex.schubert.nk.protocol.layout.scenario.SpeakerRecord;
import dev.codex.schubert.nk.protocol.layout.semantic.AudioId;
import dev.codex.schubert.nk.protocol.layout.semantic.DisplayPath;
import dev.codex.schubert.nk.protocol.layout.semantic.EntryId;
import dev.codex.schubert.nk.protocol.layout.semantic.EntryType;
import dev.codex.schubert.nk.protocol.layout.semantic.GameCode;
import dev.codex.schubert.nk.protocol.layout.semantic.ScriptFileId;
import dev.codex.schubert.nk.protocol.layout.semantic.SpeakerId;
import dev.codex.schubert.nk.protocol.layout.semantic.UserRole;
import dev.codex.schubert.nk.web.config.WebMvcConfiguration;
import dev.codex.schubert.nk.web.form.ScenarioSearchForm;
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
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.stream.Collectors;
import java.util.stream.IntStream;
import org.jsoup.Jsoup;
import org.jsoup.nodes.Document;
import org.junit.jupiter.api.Test;
import org.springframework.mock.web.MockHttpServletRequest;
import org.springframework.mock.web.MockHttpServletResponse;
import org.springframework.mock.web.MockServletContext;
import org.springframework.security.web.csrf.CsrfToken;
import org.springframework.security.web.csrf.DefaultCsrfToken;
import org.springframework.test.web.servlet.setup.MockMvcBuilders;
import org.springframework.web.context.support.AnnotationConfigWebApplicationContext;
import org.springframework.web.servlet.DispatcherServlet;
import org.thymeleaf.spring6.view.ThymeleafViewResolver;

/** Actual templates/resource mapping, independent Current literals; PG202/016007/PT-SCR026..033. */
class ScenarioSearchTemplateTest {
  private static final String READER_USERNAME = "reader";
  private static final String PAGE_KEY = "page";
  private static final String GAME_FIELD_NAME = "game";
  private static final String SPEAKER_FIELD_NAME = "speaker";
  private static final String CHAPTER_FIELD_NAME = "chapter";
  private static final String ENTRY_TYPE_FIELD_NAME = "entry_type";
  private static final String VOICE_FIELD_NAME = "voice";
  private static final String HREF_ATTRIBUTE = "href";
  private static final String QUERY_INPUT_SELECTOR = "input[name=q]";
  private static final String VALUE_ATTRIBUTE = "value";
  private static final String SPEAKER_OPTIONS_SELECTOR = "select[name=speaker] option";
  private static final String RESULT_BODY_SELECTOR = ".result-body > p";
  private static final String AUDIO_SELECTOR = "audio";
  private static final String INVALID_INPUT_MESSAGE = "入力値を確認してください。";
  private static final String SCRIPT_SELECTOR = "script";

  private static SessionPrincipal actor(String name, UserRole role) {
    return new SessionPrincipal(
        name, role, AuthenticationContext.of("a".repeat(64)), Instant.EPOCH);
  }

  private static ScenarioSearchForm form(Map<String, String> fields) {
    return ScenarioSearchForm.bind(
        fields.entrySet().stream()
            .collect(Collectors.toMap(Map.Entry::getKey, e -> List.of(e.getValue()))));
  }

  private static List<GameRecord> games() {
    return List.of(
        new GameRecord(GameCode.NUKITASHI_2, "title2", 1),
        new GameRecord(GameCode.NUKITASHI_1, "title1", 2));
  }

  private static List<SpeakerRecord> speakers() {
    return List.of(
        new SpeakerRecord(new SpeakerId(7), "乙", 9), new SpeakerRecord(new SpeakerId(3), "甲", 2));
  }

  private static ScenarioSearchRecord row(int id, boolean audio, String body) {
    return new ScenarioSearchRecord(
        new EntryId(id),
        new ScriptFileId(23),
        GameCode.NUKITASHI_1,
        audio ? Optional.of("章<&>") : Optional.empty(),
        id,
        audio ? EntryType.DIALOGUE : EntryType.NARRATION,
        audio ? Optional.of("話者<img>") : Optional.empty(),
        body,
        audio,
        audio ? Optional.of(new AudioId(71)) : Optional.empty(),
        DisplayPath.of("文章/23.txt"),
        audio ? Optional.of(DisplayPath.of("音声/71.ogg")) : Optional.empty());
  }

  private static PagedResponseData data(int page, int total) {
    return new PagedResponseData(
        page,
        100,
        total,
        Math.max(1, (total + 99) / 100),
        total == 0 ? 0 : (page - 1L) * 100 + 1,
        Math.min(page * 100L, total));
  }

  private static List<ScenarioSearchRecord> rows(int page, int total) {
    return IntStream.rangeClosed(1, Math.min(100, Math.max(0, total - (page - 1) * 100)))
        .mapToObj(i -> row(i, false, "本文" + i))
        .toList();
  }

  private static ScenarioSearchViewModel page(
      String name,
      UserRole role,
      Map<String, String> fields,
      int page,
      int total,
      List<ScenarioSearchRecord> rows) {
    return ScenarioSearchViewModel.success(
        actor(name, role), form(fields), games(), speakers(), data(page, total), rows);
  }

  private static ScenarioSearchViewModel page(Map<String, String> fields, int page, int total) {
    return page(READER_USERNAME, UserRole.USER, fields, page, total, rows(page, total));
  }

  private static AnnotationConfigWebApplicationContext context() {
    var context = new AnnotationConfigWebApplicationContext();
    context.setServletContext(new MockServletContext());
    context.register(WebMvcConfiguration.class);
    context.refresh();
    return context;
  }

  private static Document render(
      AnnotationConfigWebApplicationContext context,
      ScenarioSearchViewModel page,
      String csrf,
      int status)
      throws Exception {
    var view = context.getBean(ThymeleafViewResolver.class).resolveViewName("search", Locale.JAPAN);
    assertNotNull(view);
    var request = new MockHttpServletRequest(context.getServletContext());
    request.setAttribute(DispatcherServlet.WEB_APPLICATION_CONTEXT_ATTRIBUTE, context);
    request.setMethod("GET");
    request.setRequestURI("/search");
    request.setScheme("https");
    request.setSecure(true);
    request.setAttribute(CsrfToken.class.getName(), new DefaultCsrfToken("unused", "_csrf", csrf));
    var response = new MockHttpServletResponse();
    response.setStatus(status);
    view.render(Map.of(PAGE_KEY, page), request, response);
    assertEquals(status, response.getStatus());
    assertEquals("UTF-8", response.getCharacterEncoding());
    return Jsoup.parse(response.getContentAsString());
  }

  private static Document render(
      AnnotationConfigWebApplicationContext context, ScenarioSearchViewModel page)
      throws Exception {
    return render(context, page, "public-csrf", 200);
  }

  @Test
  void search026CommonLayoutAndInputs() throws Exception {
    try (var context = context()) {
      for (UserRole role : UserRole.values())
        for (boolean first : List.of(true, false)) {
          var fields =
              Map.of(
                  "q",
                  "本文",
                  GAME_FIELD_NAME,
                  first ? "NUKITASHI1" : "NUKITASHI2",
                  SPEAKER_FIELD_NAME,
                  first ? "甲" : "乙",
                  CHAPTER_FIELD_NAME,
                  "章",
                  ENTRY_TYPE_FIELD_NAME,
                  first ? "dialogue" : "narration",
                  VOICE_FIELD_NAME,
                  first ? "with" : "without");
          var dom =
              render(
                  context, page(READER_USERNAME, role, fields, 1, 1, List.of(row(1, false, "本文"))));
          assertEquals("schubert NK - 検索", dom.title());
          assertEquals("schubert NK - 検索", dom.select("h1").text());
          assertEquals("ja", dom.select("html").attr("lang"));
          assertEquals(READER_USERNAME, dom.select(".login-user").text());
          assertEquals(role.name(), dom.select(".login-role").text());
          assertEquals(
              List.of("/", "/notifications", "/scenarios"),
              dom.select(".nav-links a").eachAttr(HREF_ATTRIBUTE));
          assertEquals(List.of("メニュー", "通知", "一覧"), dom.select(".nav-links a").eachText());
          assertEquals("1 results / page 1 of 1", dom.select(".count").text());
          var form = dom.selectFirst("form.filters");
          assertEquals("get", form.attr("method"));
          assertEquals("/search", form.attr("action"));
          assertEquals(
              List.of("本文", "ゲーム", "話者", "章タイトル", "形態", "音声"),
              form.select("label > span").eachText());
          assertEquals(
              List.of(
                  "q",
                  GAME_FIELD_NAME,
                  SPEAKER_FIELD_NAME,
                  CHAPTER_FIELD_NAME,
                  ENTRY_TYPE_FIELD_NAME,
                  VOICE_FIELD_NAME),
              form.select("input,select").eachAttr("name"));
          assertEquals("本文", form.select(QUERY_INPUT_SELECTOR).attr(VALUE_ATTRIBUTE));
          assertEquals("章", form.select("input[name=chapter]").attr(VALUE_ATTRIBUTE));
          assertEquals(
              List.of("", "NUKITASHI2", "NUKITASHI1"),
              form.select("select[name=game] option").eachAttr(VALUE_ATTRIBUTE));
          assertEquals(List.of("すべて", "乙", "甲"), form.select(SPEAKER_OPTIONS_SELECTOR).eachText());
          for (String field :
              List.of(GAME_FIELD_NAME, SPEAKER_FIELD_NAME, ENTRY_TYPE_FIELD_NAME, VOICE_FIELD_NAME))
            assertEquals(
                fields.get(field),
                form.select("select[name=" + field + "] option[selected]").attr(VALUE_ATTRIBUTE));
          assertEquals(
              List.of("すべて", "セリフ", "ナレーション"),
              form.select("select[name=entry_type] option").eachText());
          assertEquals(
              List.of("すべて", "あり", "なし"), form.select("select[name=voice] option").eachText());
          assertTrue(
              form.select("input[type=hidden],input[name=page],input[name=_csrf]").isEmpty());
          assertEquals("post", dom.select("form.logout-form").attr("method"));
          assertEquals("/logout", dom.select("form.logout-form").attr("action"));
          assertEquals(1, dom.select("input[name=_csrf]").size());
          assertEquals("public-csrf", dom.select("input[name=_csrf]").attr(VALUE_ATTRIBUTE));
          assertEquals("検索", form.select("button[type=submit]").text());
          assertTrue(dom.select("#search-errors").hasAttr("hidden"));
        }
      var blank = render(context, page(Map.of(), 1, 0));
      for (String field :
          List.of(GAME_FIELD_NAME, SPEAKER_FIELD_NAME, ENTRY_TYPE_FIELD_NAME, VOICE_FIELD_NAME))
        assertEquals(
            "", blank.select("select[name=" + field + "] option[selected]").attr(VALUE_ATTRIBUTE));
    }
  }

  @Test
  void search027ResultsAndAudio() throws Exception {
    try (var context = context()) {
      var dom =
          render(
              context,
              page(
                  READER_USERNAME,
                  UserRole.USER,
                  Map.of(),
                  1,
                  2,
                  List.of(row(9, true, "最初<&>"), row(3, false, "最後"))));
      assertEquals(2, dom.select(".result").size());
      assertEquals(List.of("最初<&>", "最後"), dom.select(RESULT_BODY_SELECTOR).eachText());
      assertEquals(
          "NUKITASHI1 章<&> セリフ 話者<img> 文章/23.txt:9 音声/71.ogg", dom.select(".meta").first().text());
      assertEquals("NUKITASHI1 ナレーション 文章/23.txt:3", dom.select(".meta").last().text());
      assertEquals(
          List.of("/scenarios/23#entry-9", "/scenarios/23#entry-3"),
          dom.select(".scenario-open").eachAttr(HREF_ATTRIBUTE));
      assertEquals(List.of("開く", "開く"), dom.select(".scenario-open").eachText());
      assertEquals(1, dom.select(AUDIO_SELECTOR).size());
      assertEquals("/audio/71", dom.select(AUDIO_SELECTOR).attr("src"));
      assertEquals("none", dom.select(AUDIO_SELECTOR).attr("preload"));
      assertTrue(dom.select(AUDIO_SELECTOR).hasAttr("controls"));
      assertEquals("/audio/71/download", dom.select(".download").attr(HREF_ATTRIBUTE));
      assertEquals("DL", dom.select(".download").text());
      assertTrue(dom.select(".result").last().select(".audio").isEmpty());
    }
  }

  @Test
  void search028PaginationAndEmpty() throws Exception {
    try (var context = context()) {
      var empty = render(context, page(Map.of(), 1, 0));
      assertEquals("該当するデータはありません", empty.select(".empty-results").text());
      assertTrue(empty.select(".pagination,.result").isEmpty());
      assertEquals("0 results / page 1 of 1", empty.select(".count").text());
      String prefix = "/search?q=&game=&speaker=&chapter=&entry_type=&voice=&page=";
      for (int[] fixture : new int[][] {{1, 1}, {1, 100}, {1, 101}, {2, 201}, {3, 201}}) {
        int p = fixture[0];
        int total = fixture[1];
        var dom = render(context, page(Map.of(PAGE_KEY, "" + p), p, total));
        var navs = dom.select(".pagination");
        assertEquals(2, navs.size());
        assertEquals(
            List.of("search pagination", "search pagination bottom"), navs.eachAttr("aria-label"));
        assertTrue(navs.last().hasClass("bottom-nav"));
        assertFalse(navs.first().hasClass("bottom-nav"));
        String range =
            p == 1
                ? (total == 1 ? "1 - 1 / 1" : "1 - 100 / " + total)
                : p == 2 ? "101 - 200 / 201" : "201 - 201 / 201";
        for (var nav : navs) {
          assertEquals(range, nav.children().get(1).text());
          assertEquals("前の100件", nav.children().first().text());
          assertEquals("次の100件", nav.children().last().text());
          if (p > 1) assertEquals(prefix + (p - 1), nav.children().first().attr(HREF_ATTRIBUTE));
          else assertEquals("span", nav.children().first().tagName());
          if ((p == 1 && total > 100) || p == 2)
            assertEquals(prefix + (p + 1), nav.children().last().attr(HREF_ATTRIBUTE));
          else assertEquals("span", nav.children().last().tagName());
        }
        assertTrue(dom.select(".empty-results").isEmpty());
      }
      var encoded = render(context, page(Map.of("q", "a &+", PAGE_KEY, "2"), 2, 201));
      assertEquals(
          List.of(
              "/search?q=a%20%26%2B&game=&speaker=&chapter=&entry_type=&voice=&page=1",
              "/search?q=a%20%26%2B&game=&speaker=&chapter=&entry_type=&voice=&page=3"),
          encoded.select(".pagination").first().select("a").eachAttr(HREF_ATTRIBUTE));
    }
  }

  @Test
  void search029ValidationErrors() throws Exception {
    try (var context = context()) {
      var invalid =
          form(
              Map.of(
                  "q",
                  "<q>".repeat(86),
                  GAME_FIELD_NAME,
                  "<game>",
                  SPEAKER_FIELD_NAME,
                  "s".repeat(129),
                  CHAPTER_FIELD_NAME,
                  "c".repeat(257),
                  ENTRY_TYPE_FIELD_NAME,
                  "<type>",
                  VOICE_FIELD_NAME,
                  "<voice>",
                  PAGE_KEY,
                  "+1",
                  "unknown-private-name",
                  "x"));
      var dom =
          render(
              context,
              ScenarioSearchViewModel.invalid(actor(READER_USERNAME, UserRole.USER), invalid),
              "csrf",
              400);
      assertFalse(dom.select("#search-errors").hasAttr("hidden"));
      assertEquals("alert", dom.select("#search-errors").attr("role"));
      assertEquals(
          List.of(
              "error-form",
              "error-q",
              "error-game",
              "error-speaker",
              "error-chapter",
              "error-entry_type",
              "error-voice",
              "error-page"),
          dom.select("#search-errors li").eachAttr("id"));
      assertEquals(
          List.of(
              "入力項目を確認してください。",
              "本文はUTF-8で256 byte以内にしてください。",
              INVALID_INPUT_MESSAGE,
              "話者はUTF-8で128 byte以内にしてください。",
              "章タイトルはUTF-8で256 byte以内にしてください。",
              INVALID_INPUT_MESSAGE,
              INVALID_INPUT_MESSAGE,
              INVALID_INPUT_MESSAGE),
          dom.select("#search-errors li").eachText());
      assertEquals("<q>".repeat(86), dom.select(QUERY_INPUT_SELECTOR).attr(VALUE_ATTRIBUTE));
      for (var entry :
          Map.of(
                  GAME_FIELD_NAME,
                  "<game>",
                  SPEAKER_FIELD_NAME,
                  "s".repeat(129),
                  ENTRY_TYPE_FIELD_NAME,
                  "<type>",
                  VOICE_FIELD_NAME,
                  "<voice>")
              .entrySet())
        assertEquals(
            entry.getValue(),
            dom.select("select[name=" + entry.getKey() + "] option[selected]")
                .attr(VALUE_ATTRIBUTE));
      assertTrue(dom.select(".results,.count,.pagination,.empty-results").isEmpty());
      assertFalse(dom.outerHtml().contains("unknown-private-name"));
      assertTrue(dom.select("q,game,type,voice").isEmpty());
      var control =
          render(
              context,
              ScenarioSearchViewModel.invalid(actor("r", UserRole.USER), form(Map.of("q", "\n"))),
              "csrf",
              400);
      assertEquals("", control.select(QUERY_INPUT_SELECTOR).attr(VALUE_ATTRIBUTE));
      assertEquals("使用できない文字が含まれています。", control.select("#search-errors li").text());
    }
  }

  @Test
  void search030EscapingAndCsp() throws Exception {
    try (var context = context()) {
      var value =
          ScenarioSearchViewModel.success(
              actor("reader<img>", UserRole.ADMIN),
              form(
                  Map.of(
                      "q",
                      "<script>&\"",
                      SPEAKER_FIELD_NAME,
                      "<img>&",
                      CHAPTER_FIELD_NAME,
                      "<iframe>")),
              games(),
              List.of(new SpeakerRecord(new SpeakerId(1), "<img>&", 1)),
              data(1, 1),
              List.of(row(1, true, "<script>body&\"")));
      var dom = render(context, value);
      assertEquals("reader<img>", dom.select(".login-user").text());
      assertEquals("<script>&\"", dom.select(QUERY_INPUT_SELECTOR).attr(VALUE_ATTRIBUTE));
      assertEquals("<iframe>", dom.select("input[name=chapter]").attr(VALUE_ATTRIBUTE));
      assertEquals("<img>&", dom.select("select[name=speaker] option[selected]").text());
      assertEquals("<script>body&\"", dom.select(RESULT_BODY_SELECTOR).text());
      assertTrue(dom.select("style,img,iframe,object,embed,[style]").isEmpty());
      assertEquals(1, dom.select(SCRIPT_SELECTOR).size());
      assertEquals("", dom.select(SCRIPT_SELECTOR).html());
      assertEquals("/js/search-speaker-submit.js", dom.select(SCRIPT_SELECTOR).attr("src"));
      assertTrue(dom.select(SCRIPT_SELECTOR).hasAttr("defer"));
      for (var element : dom.getAllElements())
        for (var attribute : element.attributes()) {
          assertFalse(attribute.getKey().startsWith("on"));
          assertFalse(attribute.getKey().startsWith("data-"));
          if (Set.of(HREF_ATTRIBUTE, "src", "action").contains(attribute.getKey())) {
            assertTrue(attribute.getValue().startsWith("/"));
            assertFalse(attribute.getValue().startsWith("//"));
          }
        }
      for (String forbidden :
          List.of(
              "a".repeat(64),
              "SessionPrincipal",
              "authenticationContext",
              "operation_token",
              ".ready")) assertFalse(dom.outerHtml().contains(forbidden));
    }
  }

  @Test
  void search031MaximumRowsAndCandidates() throws Exception {
    try (var context = context()) {
      var g = new ArrayList<GameRecord>();
      for (int i = 0; i < 10; i++) g.add(games().get(i % 2));
      var s =
          IntStream.range(0, 500)
              .mapToObj(i -> new SpeakerRecord(new SpeakerId(i + 1), "speaker-" + i, 500 - i))
              .toList();
      var value =
          ScenarioSearchViewModel.success(
              actor("r", UserRole.USER), form(Map.of()), g, s, data(1, 100), rows(1, 100));
      var dom = render(context, value);
      assertEquals(100, dom.select(".result").size());
      assertEquals("本文1", dom.select(RESULT_BODY_SELECTOR).first().text());
      assertEquals("本文100", dom.select(RESULT_BODY_SELECTOR).last().text());
      assertEquals(11, dom.select("select[name=game] option").size());
      assertEquals(501, dom.select(SPEAKER_OPTIONS_SELECTOR).size());
      assertEquals("speaker-0", dom.select(SPEAKER_OPTIONS_SELECTOR).get(1).text());
      assertEquals("speaker-499", dom.select(SPEAKER_OPTIONS_SELECTOR).last().text());
    }
  }

  private static Map<String, String> rules(String input) {
    var result = new LinkedHashMap<String, String>();
    var matcher = java.util.regex.Pattern.compile("([^{}]+)\\{([^{}]*)\\}").matcher(input);
    while (matcher.find()) {
      String key = matcher.group(1).replaceAll("\\s+", " ").trim();
      String value = matcher.group(2).replaceAll("\\s+", " ").trim();
      assertNull(result.put(key, value), "duplicate style selector");
    }
    return result;
  }

  private static void assertRules(Map<String, String> expected, String actual) {
    var parsed = rules(actual);
    assertEquals(expected, parsed);
    assertEquals(new ArrayList<>(expected.keySet()), new ArrayList<>(parsed.keySet()));
  }

  @Test
  void search032CssResourcesAndViewBoundary() throws Exception {
    try (var context = context()) {
      var resolver = context.getBean(ThymeleafViewResolver.class);
      assertNotNull(resolver.resolveViewName("search", Locale.JAPAN));
      for (String name :
          List.of(
              "search-private", "../search", "redirect:https://invalid.example", "forward:/search"))
        assertNull(resolver.resolveViewName(name, Locale.JAPAN));
      var mvc = MockMvcBuilders.webAppContextSetup(context).build();
      var response = mvc.perform(get("/js/search-speaker-submit.js")).andReturn().getResponse();
      assertEquals(200, response.getStatus());
      assertEquals("text/javascript", response.getContentType());
      assertEquals(
          Files.readString(Path.of("src/main/resources/static/js/search-speaker-submit.js")),
          response.getContentAsString(StandardCharsets.UTF_8));
      var head = mvc.perform(head("/js/search-speaker-submit.js")).andReturn().getResponse();
      assertEquals(200, head.getStatus());
      assertEquals(0, head.getContentAsByteArray().length);
      assertEquals(404, mvc.perform(get("/js/missing.js")).andReturn().getResponse().getStatus());
    }
    String css = Files.readString(Path.of("src/main/resources/static/css/schubert.css"));
    String added = css.substring(css.indexOf("/* PG202/"), css.indexOf("/* End PG202"));
    added = added.substring(added.indexOf("*/") + 2);
    int media = added.indexOf("@media (max-width: 900px)");
    assertTrue(media > 0);
    String desktop = added.substring(0, media);
    String mobile = added.substring(added.indexOf('{', media) + 1, added.lastIndexOf('}'));
    // Independent Current declaration inventory, with the approved .search-page scoping.
    var expected = new LinkedHashMap<String, String>();
    expected.put(".search-page .count", "color: #5f6368; font-size: 14px;");
    expected.put(
        ".search-page .filters",
        "display: grid; grid-template-columns: repeat(12, minmax(0, 1fr)); gap: 10px; align-items: end; padding: 14px; background: #fff; border: 1px solid #dde1e6; border-radius: 8px; margin-bottom: 16px;");
    expected.put(".search-page .filters label:nth-child(1)", "grid-column: span 3;");
    expected.put(
        ".search-page .filters label:nth-child(2), .search-page .filters label:nth-child(3), .search-page .filters label:nth-child(4)",
        "grid-column: span 2;");
    expected.put(
        ".search-page .filters label:nth-child(5), .search-page .filters label:nth-child(6), .search-page .filters button",
        "grid-column: span 1;");
    expected.put(
        ".search-page .filters label",
        "display: grid; gap: 5px; font-size: 12px; color: #5f6368; min-width: 0;");
    expected.put(
        ".search-page .filters input, .search-page .filters select, .search-page .filters button",
        "width: 100%; min-width: 0; box-sizing: border-box; min-height: 38px; border: 1px solid #c9ced6; border-radius: 6px; padding: 0 10px; font: inherit; background: #fff; color: #202124;");
    expected.put(
        ".search-page .filters button",
        "border-color: #1f6feb; background: #1f6feb; color: #fff; font-weight: 700; cursor: pointer;");
    expected.put(".search-page .results", "display: grid; gap: 10px;");
    expected.put(
        ".search-page .pagination",
        "display: grid; grid-template-columns: 1fr auto 1fr; align-items: center; gap: 10px; margin-bottom: 12px;");
    expected.put(
        ".search-page .pagination > a, .search-page .pagination > span, .search-page .pagination > div",
        "min-height: 40px; display: flex; align-items: center; padding: 0 12px; background: #fff; border: 1px solid #dde1e6; border-radius: 8px;");
    expected.put(
        ".search-page .pagination > a:last-child, .search-page .pagination > span:last-child",
        "justify-content: flex-end;");
    expected.put(".search-page .pagination > div", "gap: 4px; color: #5f6368; font-size: 13px;");
    expected.put(
        ".search-page .pagination > a, .search-page .scenario-open",
        "color: #1f6feb; text-decoration: none; font-weight: 700;");
    expected.put(".search-page .pagination.bottom-nav", "margin-top: 12px; margin-bottom: 0;");
    expected.put(
        ".search-page .result",
        "display: grid; grid-template-columns: minmax(0, 1fr) 220px; gap: 14px; align-items: start; background: #fff; border: 1px solid #dde1e6; border-radius: 8px; padding: 14px;");
    expected.put(".search-page .result-actions", "display: grid; gap: 8px; justify-items: end;");
    expected.put(
        ".search-page .result-actions .scenario-open",
        "display: inline-grid; place-items: center; width: 54px; min-height: 34px; margin: 0; border: 1px solid #c9ced6; border-radius: 6px; background: #fff; font-size: 13px;");
    expected.put(
        ".search-page .result-actions .audio",
        "display: grid; grid-template-columns: minmax(0, 1fr) auto; align-items: center; gap: 8px; margin: 0; width: 220px; color: #5f6368; font-size: 12px;");
    expected.put(
        ".search-page .result-actions audio", "width: 160px; max-width: 100%; height: 34px;");
    expected.put(".search-page .result-body", "min-width: 0;");
    expected.put(
        ".search-page .meta",
        "display: flex; flex-wrap: wrap; gap: 8px; color: #5f6368; font-size: 12px;");
    expected.put(
        ".search-page .meta span", "padding: 2px 7px; background: #eef1f5; border-radius: 999px;");
    expected.put(
        ".search-page .result-body p",
        "white-space: pre-wrap; line-height: 1.7; margin: 10px 0 0;");
    expected.put(
        ".search-page .download",
        "display: inline-grid; place-items: center; min-width: 34px; height: 30px; padding: 0 8px; border: 1px solid #c9ced6; border-radius: 6px; color: #1f6feb; text-decoration: none; font-weight: 700; background: #fff;");
    assertRules(expected, desktop);
    expected.clear();
    expected.put(".search-page .pagination", "grid-template-columns: 1fr;");
    expected.put(
        ".search-page .pagination > a:last-child, .search-page .pagination > span:last-child",
        "justify-content: flex-start;");
    expected.put(".search-page .result", "grid-template-columns: 1fr;");
    expected.put(
        ".search-page .result-actions",
        "grid-template-columns: auto minmax(0, 1fr); align-items: center; justify-items: stretch;");
    expected.put(".search-page .result-actions audio", "width: 100%;");
    expected.put(".search-page .filters", "grid-template-columns: 1fr 1fr;");
    expected.put(
        ".search-page .filters label:nth-child(n), .search-page .filters label:first-child, .search-page .filters button",
        "grid-column: 1 / -1;");
    assertRules(expected, mobile);
  }

  @Test
  void search033ConcurrentRendering() throws Exception {
    try (var context = context();
        var pool = Executors.newFixedThreadPool(8)) {
      var tasks = new ArrayList<Future<?>>();
      for (int i = 1; i <= 64; i++) {
        int n = i;
        tasks.add(
            pool.submit(
                () -> {
                  var dom =
                      render(
                          context,
                          page(
                              "user-" + n,
                              n % 2 == 0 ? UserRole.ADMIN : UserRole.USER,
                              Map.of("q", "q-" + n),
                              1,
                              1,
                              List.of(row(n, false, "body-" + n))),
                          "csrf-" + n,
                          200);
                  assertEquals("user-" + n, dom.select(".login-user").text());
                  assertEquals(n % 2 == 0 ? "ADMIN" : "USER", dom.select(".login-role").text());
                  assertEquals("q-" + n, dom.select(QUERY_INPUT_SELECTOR).attr(VALUE_ATTRIBUTE));
                  assertEquals("body-" + n, dom.select(RESULT_BODY_SELECTOR).text());
                  assertEquals(
                      "csrf-" + n,
                      dom.select("form.logout-form input[name=_csrf]").attr(VALUE_ATTRIBUTE));
                  assertEquals(
                      "/scenarios/23#entry-" + n,
                      dom.select(".scenario-open").attr(HREF_ATTRIBUTE));
                  return null;
                }));
      }
      for (var task : tasks) task.get(20, TimeUnit.SECONDS);
    }
    Path directory = Path.of("target/scenario-screen-traces");
    Files.createDirectories(directory);
    Files.writeString(
        directory.resolve("PT-SCR-033.txt"),
        "template=search\nfixture=public-synthetic\nconcurrentRenders=64\nmaximumRows=100\nmaximumSpeakers=500\nactualNkGate=false\n");
  }
}
