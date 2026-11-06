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

/** PT-MUSIC-DOM001..008; actual resource only, independent literal map, no application Java. */
final class MusicListTemplateResourcePortTest {
  private static final String TITLE = "title";
  private static final String TRACKS = "tracks";
  private static final String PAIRS = "pairs";
  private static final String PLAYER = "audio";
  private static final String ROW = ".music-row";
  private static final String STRONG = ".music-info strong";
  private static final String SUBTITLE = ".subtitle";
  private static final String HREF = "href";
  private static final String META = ".scenario-meta";
  private static final String MUSIC = "Music";
  private static final String CATEGORY = "BGM";
  private static final String READER = "fixture-reader";
  private static final String USER = "USER";
  private static final String ADMIN = "ADMIN";
  private static final String SYNTHETIC_CSRF = "synthetic-noncredential-csrf";

  private static Map<String, Object> track(String title, long bytes) {
    return Map.of(
        TITLE,
        title,
        "displayPath",
        "album/" + title,
        "byteSize",
        bytes,
        "mediaHref",
        "/music/media/" + title,
        "downloadHref",
        "/music/download/" + title);
  }

  private static Map<String, Object> pair(
      String title,
      Optional<Map<String, Object>> main,
      Optional<Map<String, Object>> instrumental) {
    return Map.of(TITLE, title, "main", main, "instrumental", instrumental);
  }

  private static Map<String, Object> page(
      boolean songs, List<Map<String, Object>> tracks, List<Map<String, Object>> pairs) {
    var values = new HashMap<String, Object>();
    values.put(TITLE, MUSIC);
    values.put("trackCount", tracks.size());
    values.put("songs", songs);
    values.put(TRACKS, tracks);
    values.put(PAIRS, pairs);
    values.put("category", CATEGORY);
    values.put("categoryHref", "/music/BGM");
    values.put("topBar", Map.of("username", READER, "role", USER));
    return values;
  }

  private static Document render(String id, Map<String, Object> values) throws Exception {
    var servlet = new MockServletContext();
    var req = new MockHttpServletRequest(servlet);
    req.setMethod("GET");
    req.setRequestURI("/music/BGM/album");
    var exchange =
        JakartaServletWebApplication.buildApplication(servlet)
            .buildExchange(req, new MockHttpServletResponse());
    var resolver = new ClassLoaderTemplateResolver();
    resolver.setPrefix("templates/");
    resolver.setSuffix(".html");
    resolver.setTemplateMode("HTML");
    resolver.setCharacterEncoding("UTF-8");
    resolver.setCacheable(false);
    var engine = new SpringTemplateEngine();
    engine.setTemplateResolver(resolver);
    var context =
        Map.<String, Object>of(
            "page",
            Map.of("values", values),
            "_csrf",
            Map.of("parameterName", "_csrf", "token", SYNTHETIC_CSRF));
    var dom =
        Jsoup.parse(engine.process("music-list", new WebContext(exchange, Locale.JAPAN, context)));
    assertTrue(dom.select("[th\\:text],[th\\:if],[th\\:replace],[th\\:each]").isEmpty());
    var saved = dom.clone();
    saved.select("input[name=_csrf]").attr("value", "[REDACTED-SYNTHETIC]");
    String safe = saved.outerHtml();
    assertFalse(safe.contains(SYNTHETIC_CSRF));
    Files.writeString(
        Path.of(System.getProperty("owned.output"), id + ".html"),
        safe,
        StandardOpenOption.CREATE_NEW);
    return dom;
  }

  @Test
  void ordinaryRowsKeepStoredOrderAndLiteralPlaybackMetadata() throws Exception {
    var d =
        render(
            "MDOM001",
            page(false, List.of(track("first", 1048576), track("second", 2097152)), List.of()));
    assertEquals(List.of("first", "second"), d.select(STRONG).eachText());
    assertEquals(List.of("album/first 1.0 MB", "album/second 2.0 MB"), d.select(META).eachText());
    assertEquals(
        List.of("/music/media/first", "/music/media/second"), d.select(PLAYER).eachAttr("src"));
    assertEquals(
        List.of("/music/download/first", "/music/download/second"),
        d.select("a.download").eachAttr(HREF));
    assertEquals(2, d.select("audio[controls][preload=none]").size());
    assertTrue(d.select(".song-row,.song-player-placeholder,script").isEmpty());
  }

  @Test
  void bothEmptyCollectionsProduceNoInventedPlayers() throws Exception {
    var first = render("MDOM002-a", page(false, List.of(), List.of()));
    var second = render("MDOM002-b", page(true, List.of(), List.of()));
    for (var d : List.of(first, second)) {
      assertEquals("0曲", d.select(SUBTITLE).text());
      assertTrue(d.select("audio,.music-row,.song-player-placeholder").isEmpty());
    }
  }

  @Test
  void everyOptionalPairSideHasExplicitPlayerOrPlaceholder() throws Exception {
    var main = track("main", 1);
    var instrumental = track("inst", 1);
    var pairs =
        List.of(
            pair("both", Optional.of(main), Optional.of(instrumental)),
            pair("main-only", Optional.of(main), Optional.empty()),
            pair("inst-only", Optional.empty(), Optional.of(instrumental)),
            pair("neither", Optional.empty(), Optional.empty()));
    var d = render("MDOM003", page(true, List.of(), pairs));
    assertEquals(List.of("both", "main-only", "inst-only", "neither"), d.select(STRONG).eachText());
    assertEquals(4, d.select(PLAYER).size());
    assertEquals(
        List.of("インストなし", "メインなし", "メインなし", "インストなし"),
        d.select(".song-player-placeholder").eachText());
    assertEquals(List.of("メイン", "インスト", "メイン", "インスト"), d.select(".song-player > span").eachText());
    assertTrue(d.select(META).isEmpty());
  }

  @Test
  void textEscapesWithoutInjectingMarkupOrAttributes() throws Exception {
    String value = "曲<script>&\"";
    var t = new HashMap<>(track("plain", 0));
    t.put(TITLE, value);
    t.put("displayPath", "<img onerror=bad> 日本");
    var d = render("MDOM004", page(false, List.of(t), List.of()));
    assertEquals(value, d.select(STRONG).text());
    assertEquals("<img onerror=bad> 日本 0.0 MB", d.select(META).text());
    assertTrue(d.select("script,img,[onerror]").isEmpty());
  }

  @Test
  void pageAndTopbarNavigationUseIndependentLiteralValues() throws Exception {
    int n = 0;
    for (String role : List.of(USER, ADMIN)) {
      var v = page(false, List.of(), List.of());
      v.put(TITLE, "曲<&>");
      v.put("category", "分類<&>");
      v.put("topBar", Map.of("username", READER, "role", role));
      var d = render("MDOM005-" + n, v);
      n++;
      assertEquals("曲<&>", d.title());
      assertEquals("曲<&>", d.select("h1").text());
      assertEquals(
          List.of("音楽", "分類<&>", "検索"), d.select("header nav:not([aria-label]) a").eachText());
      assertEquals(
          List.of("/music", "/music/BGM", "/search"),
          d.select("header nav:not([aria-label]) a").eachAttr(HREF));
      assertEquals(READER, d.select(".login-user").text());
      assertEquals(role, d.select(".login-role").text());
      assertEquals(1, d.select("form[action=/logout][method=post]").size());
    }
  }

  @Test
  void binaryMegabyteFormattingUsesZeroAndFractionalBoundaries() throws Exception {
    var d =
        render(
            "MDOM006",
            page(
                false,
                List.of(track("zero", 0), track("one", 1048576), track("fraction", 1572864)),
                List.of()));
    assertEquals(
        List.of("album/zero 0.0 MB", "album/one 1.0 MB", "album/fraction 1.5 MB"),
        d.select(META).eachText());
    assertEquals(3, d.select(ROW).size());
  }

  @Test
  void inactiveCollectionsAreNotEvaluated() throws Exception {
    var ordinary = page(false, List.of(track("only", 1)), List.of());
    ordinary.put(PAIRS, null);
    var d = render("MDOM007-a", ordinary);
    assertEquals("only", d.select(STRONG).text());
    var songs =
        page(
            true,
            List.of(),
            List.of(pair("pair", Optional.of(track("main", 1)), Optional.empty())));
    songs.put(TRACKS, null);
    var s = render("MDOM007-b", songs);
    assertEquals("pair", s.select(STRONG).text());
    assertEquals("インストなし", s.select(".song-player-placeholder").text());
  }

  @Test
  void concurrentEnginesKeepEightPagesAndOutputsSeparate() throws Exception {
    try (var pool = Executors.newFixedThreadPool(2)) {
      var jobs = new ArrayList<Future<String>>();
      for (int i = 0; i < 8; i++) {
        int index = i;
        jobs.add(
            pool.submit(
                () -> {
                  var v = page(false, List.of(), List.of());
                  v.put(TITLE, "page-" + index);
                  return render("MDOM008-" + index, v).title();
                }));
      }
      for (int i = 0; i < 8; i++) assertEquals("page-" + i, jobs.get(i).get(10, TimeUnit.SECONDS));
    }
  }
}
