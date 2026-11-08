package dev.codex.schubert.nk.web.view;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.util.ArrayList;
import java.util.HashMap;
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
import org.thymeleaf.context.WebContext;
import org.thymeleaf.spring6.SpringTemplateEngine;
import org.thymeleaf.templateresolver.ClassLoaderTemplateResolver;
import org.thymeleaf.web.servlet.JakartaServletWebApplication;

/** PT-SEARCH-DOM001..008; UI222/223/234, SS313. Independent maps; no application Java. */
final class SearchTemplateResourcePortTest {
  private static final int FIRST_PAGE = 1;
  private static final String CHAPTER = "chapter";
  private static final String GAME_ONE = "NUKITASHI1";
  private static final String PAGE_PREFIX = "/search?q=fixed&page=";
  private static final String RESULTS = "results";
  private static final String FILTERS = "filters";
  private static final String ERRORS = "errors";
  private static final String ENTRY = "entryType";
  private static final String VOICE = "voice";
  private static final String GAME = "game";
  private static final String SPEAKER = "speaker";
  private static final String BODY = "body";
  private static final String HREF = "href";
  private static final String VALUE = "value";
  private static final String QUERY = "input[name=q]";
  private static final String ROW = ".result";
  private static final String CONTENT = ".result-body > p";
  private static final String NAV = ".pagination";
  private static final String AUDIO = "audio";
  private static final String SYNTHETIC_CSRF = "synthetic-noncredential-csrf";
  private static final String USER = "USER";
  private static final String ADMIN = "ADMIN";
  private static final String READER = "fixture-reader";
  private static final String FIRST = "first";
  private static final String LAST = "last";

  private static Map<String, Object> page() {
    var p = new HashMap<String, Object>();
    p.put("topBar", Map.of("username", READER, "role", USER));
    p.put(FILTERS, Map.of("q", "", GAME, "", SPEAKER, "", CHAPTER, "", ENTRY, "", VOICE, ""));
    p.put("games", List.of("NUKITASHI2", GAME_ONE));
    p.put("speakers", List.of("乙", "甲"));
    p.put(ERRORS, List.of());
    p.put(RESULTS, Optional.empty());
    p.put("previousHref", Optional.empty());
    p.put("nextHref", Optional.empty());
    return p;
  }

  private static Map<String, Object> resultRow(String body, boolean audio) {
    return Map.of(
        GAME,
        GAME_ONE,
        "chapterTitle",
        CHAPTER,
        "entryTypeLabel",
        "セリフ",
        SPEAKER,
        "speaker",
        "scriptDisplayPath",
        "script/one.txt",
        "lineNumber",
        7,
        BODY,
        body,
        "scenarioHref",
        "/scenarios/17#entry-9",
        AUDIO,
        audio
            ? Optional.of(
                Map.of(
                    "displayPath",
                    "voice/one.ogg",
                    HREF,
                    "/audio/71",
                    "downloadHref",
                    "/audio/71/download"))
            : Optional.empty());
  }

  private static void setResults(
      Map<String, Object> p, int total, int effective, List<Map<String, Object>> rows) {
    int pages = Math.max(1, (total + 99) / 100);
    var counts =
        Map.of(
            "empty",
            total == 0,
            "totalCount",
            total,
            "effectivePage",
            effective,
            "totalPages",
            pages,
            "firstResult",
            total == 0 ? 0 : (effective - 1) * 100 + 1,
            "lastResult",
            Math.min(effective * 100, total));
    p.put(RESULTS, Optional.of(Map.of("page", counts, "rows", rows)));
    p.put(
        "previousHref",
        effective > 1 ? Optional.of(PAGE_PREFIX + (effective - 1)) : Optional.empty());
    p.put(
        "nextHref",
        effective < pages ? Optional.of(PAGE_PREFIX + (effective + 1)) : Optional.empty());
  }

  private static Document render(String id, Map<String, Object> p) throws Exception {
    var servlet = new MockServletContext();
    var request = new MockHttpServletRequest(servlet);
    request.setMethod("GET");
    request.setRequestURI("/search");
    var exchange =
        JakartaServletWebApplication.buildApplication(servlet)
            .buildExchange(request, new MockHttpServletResponse());
    var resolver = new ClassLoaderTemplateResolver();
    resolver.setPrefix("templates/");
    resolver.setSuffix(".html");
    resolver.setTemplateMode("HTML");
    resolver.setCharacterEncoding("UTF-8");
    resolver.setCacheable(false);
    var engine = new SpringTemplateEngine();
    engine.setTemplateResolver(resolver);
    var variables =
        Map.<String, Object>of(
            "page", p, "_csrf", Map.of("parameterName", "_csrf", "token", SYNTHETIC_CSRF));
    var dom =
        Jsoup.parse(engine.process("search", new WebContext(exchange, Locale.JAPAN, variables)));
    assertTrue(dom.select("[th\\:text],[th\\:if],[th\\:replace],[th\\:each]").isEmpty());
    var saved = dom.clone();
    saved.select("input[name=_csrf]").attr(VALUE, "[REDACTED-SYNTHETIC]");
    var safe = saved.outerHtml();
    assertFalse(safe.contains(SYNTHETIC_CSRF));
    Files.writeString(
        Path.of(System.getProperty("owned.output"), id + ".html"),
        safe,
        StandardOpenOption.CREATE_NEW);
    return dom;
  }

  @Test
  void unsearchedPageRetainsSixGetControlsWithoutInventedResults() throws Exception {
    var d = render("SDOM001", page());
    assertEquals("schubert NK - 検索", d.title());
    assertEquals("ja", d.select("html").attr("lang"));
    assertEquals(READER, d.select(".login-user").text());
    assertEquals(USER, d.select(".login-role").text());
    var f = d.select("form.filters");
    assertEquals("get", f.attr("method"));
    assertEquals("/search", f.attr("action"));
    assertEquals(
        List.of("q", GAME, SPEAKER, CHAPTER, "entry_type", VOICE),
        f.select("input,select").eachAttr("name"));
    assertEquals(
        List.of("すべて", "NUKITASHI2", GAME_ONE), d.select("select[name=game] option").eachText());
    assertEquals(List.of("すべて", "乙", "甲"), d.select("select[name=speaker] option").eachText());
    assertTrue(d.select("#search-errors").hasAttr("hidden"));
    assertTrue(d.select(".results,.count,.pagination").isEmpty());
    assertEquals("/js/search-speaker-submit.js", d.select("script[defer]").attr("src"));
  }

  @Test
  void successfulEmptyPageShowsZeroCountAndNoPagination() throws Exception {
    var p = page();
    setResults(p, 0, 1, List.of());
    var d = render("SDOM002", p);
    assertEquals("0 results / page 1 of 1", d.select(".count").text());
    assertEquals("該当するデータはありません", d.select(".empty-results").text());
    assertTrue(d.select(".result,.pagination,audio").isEmpty());
  }

  @Test
  void bothPaginationCopiesRespectSingleFirstMiddleAndLastBoundaries() throws Exception {
    int[] totals = {1, 201, 201, 201};
    int[] pages = {1, 1, 2, 3};
    String[] ranges = {"1 - 1 / 1", "1 - 100 / 201", "101 - 200 / 201", "201 - 201 / 201"};
    for (int i = 0; i < totals.length; i++) {
      var p = page();
      setResults(p, totals[i], pages[i], List.of(resultRow("fixed", false)));
      var d = render("SDOM003-" + i, p);
      var navs = d.select(NAV);
      assertEquals(2, navs.size());
      assertFalse(navs.getFirst().hasClass("bottom-nav"));
      assertTrue(navs.getLast().hasClass("bottom-nav"));
      for (var n : navs) {
        assertEquals(ranges[i], n.select("div").text());
        var first = n.children().getFirst();
        var last = n.children().getLast();
        assertEquals("前の100件", first.text());
        assertEquals("次の100件", last.text());
        assertEquals(pages[i] > 1 ? "a" : "span", first.tagName());
        assertEquals(i == 1 || i == 2 ? "a" : "span", last.tagName());
        if (pages[i] > FIRST_PAGE) assertEquals(PAGE_PREFIX + (pages[i] - 1), first.attr(HREF));
        if (i == 1 || i == 2) assertEquals(PAGE_PREFIX + (pages[i] + 1), last.attr(HREF));
      }
    }
  }

  @Test
  void allKnownAndUnknownEnumFiltersRedisplayWithExplicitSelection() throws Exception {
    String[] entries = {"", "dialogue", "narration", "<unknown-entry>"};
    String[] voices = {"", "with", "without", "<unknown-voice>"};
    for (int i = 0; i < entries.length; i++) {
      var p = page();
      p.put(
          FILTERS,
          Map.of(
              "q",
              "本文",
              GAME,
              GAME_ONE,
              SPEAKER,
              "甲",
              CHAPTER,
              "章",
              ENTRY,
              entries[i],
              VOICE,
              voices[i]));
      p.put("topBar", Map.of("username", READER, "role", ADMIN));
      var d = render("SDOM004-" + i, p);
      assertEquals("本文", d.select(QUERY).attr(VALUE));
      assertEquals("章", d.select("input[name=chapter]").attr(VALUE));
      for (var choice :
          Map.of(GAME, GAME_ONE, SPEAKER, "甲", "entry_type", entries[i], VOICE, voices[i])
              .entrySet()) {
        var selected = d.select("select[name=" + choice.getKey() + "] option[selected]");
        assertEquals(1, selected.size());
        assertEquals(choice.getValue(), selected.attr(VALUE));
      }
      assertEquals(ADMIN, d.select(".login-role").text());
      assertTrue(d.select("unknown-entry,unknown-voice").isEmpty());
    }
  }

  @Test
  void rowMetadataAndAudioPresenceDoNotCreateEmptyPlayers() throws Exception {
    for (int i = 0; i < 2; i++) {
      var p = page();
      var r = new HashMap<>(resultRow("literal", i == 0));
      if (i != 0) {
        r.put("chapterTitle", "");
        r.put(SPEAKER, "");
        r.put("entryTypeLabel", "ナレーション");
      }
      setResults(p, 1, 1, List.of(r));
      var d = render("SDOM005-" + i, p);
      assertEquals(
          i == 0
              ? "NUKITASHI1 chapter セリフ speaker script/one.txt:7 voice/one.ogg"
              : "NUKITASHI1 ナレーション script/one.txt:7",
          d.select(".meta").text());
      assertEquals("/scenarios/17#entry-9", d.select(".scenario-open").attr(HREF));
      assertEquals(i == 0 ? 1 : 0, d.select(AUDIO).size());
      if (i == 0) {
        assertEquals("/audio/71", d.select(AUDIO).attr("src"));
        assertEquals("none", d.select(AUDIO).attr("preload"));
        assertTrue(d.select(AUDIO).hasAttr("controls"));
        assertEquals("/audio/71/download", d.select("a.download").attr(HREF));
      } else assertTrue(d.select(".audio,a.download").isEmpty());
    }
  }

  @Test
  void errorsInputAndMultilineBodyEscapeWithoutExecutableMarkup() throws Exception {
    var p = page();
    var literal = "<script>fixture</script>\nA&B";
    p.put(ERRORS, List.of(Map.of("name", "q", "message", literal)));
    p.put(
        FILTERS,
        Map.of("q", literal, GAME, "", SPEAKER, "", CHAPTER, literal, ENTRY, "", VOICE, ""));
    setResults(p, 1, 1, List.of(resultRow(literal, false)));
    var d = render("SDOM006", p);
    assertFalse(d.select("#search-errors").hasAttr("hidden"));
    assertEquals(literal, d.select("#error-q").getFirst().wholeText());
    assertEquals(literal, d.select(QUERY).attr(VALUE));
    assertEquals(literal, d.select(CONTENT).getFirst().wholeText());
    assertTrue(d.select("script:not([src])").isEmpty());
    assertEquals(
        List.of("/", "/notifications", "/scenarios"), d.select(".nav-links a").eachAttr(HREF));
  }

  @Test
  void fullHundredRowPageKeepsEveryStoredPositionAndBoundaryBody() throws Exception {
    var rows = new ArrayList<Map<String, Object>>();
    for (int i = 0; i < 100; i++)
      rows.add(resultRow(i == 0 ? FIRST : i == 99 ? LAST : "row-" + i, false));
    var p = page();
    setResults(p, 100, 1, rows);
    var d = render("SDOM007", p);
    assertEquals(100, d.select(ROW).size());
    assertEquals(FIRST, d.select(CONTENT).getFirst().text());
    assertEquals(LAST, d.select(CONTENT).getLast().text());
    for (int i = 1; i < 99; i++) assertEquals("row-" + i, d.select(CONTENT).get(i).text());
    assertEquals("100 results / page 1 of 1", d.select(".count").text());
    assertTrue(d.select(".pagination a,audio").isEmpty());
  }

  @Test
  void ownedConcurrentRenderersNeverShareFiltersOrRows() throws Exception {
    var executor = Executors.newFixedThreadPool(2);
    try {
      List<Future<?>> futures = new ArrayList<>();
      for (int i = 0; i < 8; i++) {
        final int number = i;
        futures.add(
            executor.submit(
                () -> {
                  var p = page();
                  var value = "isolated-" + number;
                  p.put(
                      FILTERS,
                      Map.of("q", value, GAME, "", SPEAKER, "", CHAPTER, "", ENTRY, "", VOICE, ""));
                  setResults(p, 1, 1, List.of(resultRow(value, false)));
                  var d = render("SDOM008-" + number, p);
                  assertEquals(value, d.select(QUERY).attr(VALUE));
                  assertEquals(value, d.select(CONTENT).text());
                  return null;
                }));
      }
      for (var future : futures) future.get(10, TimeUnit.SECONDS);
    } finally {
      executor.shutdownNow();
      assertTrue(executor.awaitTermination(10, TimeUnit.SECONDS));
    }
  }
}
