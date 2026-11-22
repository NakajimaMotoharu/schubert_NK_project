package dev.codex.schubert.nk.web.view;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Optional;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;
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

/** PT-SCENE-DOM001..008; UI221223234/SS313333, resource maps only, no file/API operations. */
final class ScenarioDetailTemplateResourcePortTest {
  private static final String TITLE = "title";
  private static final String BODY = "body";
  private static final String HREF = "href";
  private static final String ROW = ".script-entry";
  private static final String CONTENT = ".script-entry > p";
  private static final String NAV = ".scenario-nav";
  private static final String BRAND = "schubert NK";
  private static final String READER = "public-reader";
  private static final String SYNTHETIC_CSRF = "synthetic-noncredential-csrf";
  private static final String CHAPTER = "chapter";

  private static Map<String, Object> audioRow(int id) {
    return Map.of(
        HREF,
        "/audio/" + id,
        "downloadHref",
        "/audio/" + id + "/download",
        "displayPath",
        "voice/" + id + ".ogg");
  }

  private static Map<String, Object> entry(
      int id, boolean dialogue, String speaker, String body, List<Map<String, Object>> audio) {
    return Map.of(
        "anchor",
        "entry-" + id,
        "lineNumber",
        id,
        "dialogue",
        dialogue,
        "speaker",
        speaker,
        BODY,
        body,
        "audio",
        audio);
  }

  private static Map<String, Object> page(List<Map<String, Object>> entries) {
    var p = new HashMap<String, Object>();
    p.put(TITLE, CHAPTER);
    p.put("game", "NUKITASHI1");
    p.put("displayPath", "script/start.txt");
    p.put("topBar", Map.of("username", READER, "role", "USER", "brand", BRAND));
    p.put("entries", entries);
    p.put("previous", Optional.empty());
    p.put("next", Optional.empty());
    return p;
  }

  private static Document render(String id, Map<String, Object> p) throws IOException {
    var servlet = new MockServletContext();
    var req = new MockHttpServletRequest(servlet);
    req.setMethod("GET");
    req.setRequestURI("/scenarios/17");
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
    var vars =
        Map.<String, Object>of(
            "page", p, "_csrf", Map.of("parameterName", "_csrf", "token", SYNTHETIC_CSRF));
    var d = Jsoup.parse(engine.process("scenario", new WebContext(exchange, Locale.JAPAN, vars)));
    assertTrue(
        d.select(
                "[th\\:text],[th\\:if],[th\\:replace],[th\\:each],[th\\:href],[th\\:id],[th\\:classappend]")
            .isEmpty());
    var saved = d.clone();
    saved.select("input[name=_csrf]").attr("value", "[REDACTED-SYNTHETIC]");
    var safe = saved.outerHtml();
    assertFalse(safe.contains(SYNTHETIC_CSRF));
    Files.writeString(
        Path.of(System.getProperty("owned.output"), id + ".html"),
        safe,
        StandardOpenOption.CREATE_NEW);
    return d;
  }

  @Test
  void metadataAndNavigationUseExplicitApprovedDisplayValues() throws IOException {
    var d = render("SCENE001", page(List.of(entry(9, true, "speaker", "text", List.of()))));
    assertEquals(CHAPTER, d.title());
    assertEquals(CHAPTER, d.select("h1").text());
    assertEquals(BRAND, d.select(".brand").text());
    assertEquals("NUKITASHI1 / script/start.txt", d.select(".subtitle").text());
    assertEquals(READER, d.select(".login-user").text());
    assertEquals(
        List.of("/", "/notifications", "/scenarios", "/search"),
        d.select(".nav-links a").eachAttr(HREF));
    assertEquals("entry-9", d.select(ROW).attr("id"));
    assertEquals("9 speaker", d.select(".line-meta").text());
  }

  @Test
  void emptyEntryCollectionHasNoInventedBodyOrAudio() throws IOException {
    var d = render("SCENE002", page(List.of()));
    assertEquals(1, d.select(".script-body").size());
    assertTrue(d.select(".script-entry,audio,.audio,.download").isEmpty());
    assertEquals(2, d.select(NAV).size());
  }

  @Test
  void everyPreviousNextCombinationMatchesBothNavigationCopies() throws IOException {
    int n = 0;
    for (boolean previous : List.of(false, true))
      for (boolean next : List.of(false, true)) {
        var p = page(List.of());
        p.put(
            "previous",
            previous
                ? Optional.of(Map.of(HREF, "/scenarios/16", TITLE, "previous"))
                : Optional.empty());
        p.put(
            "next",
            next ? Optional.of(Map.of(HREF, "/scenarios/18", TITLE, "next")) : Optional.empty());
        var d = render("SCENE003-" + n, p);
        n++;
        var navs = d.select(NAV);
        assertEquals(2, navs.size());
        assertFalse(navs.getFirst().hasClass("bottom-nav"));
        assertTrue(navs.getLast().hasClass("bottom-nav"));
        for (var nav : navs) {
          var first = nav.children().getFirst();
          var last = nav.children().getLast();
          assertEquals(previous ? "a" : "span", first.tagName());
          assertEquals(next ? "a" : "span", last.tagName());
          assertEquals(previous ? "前: previous" : "前: なし", first.text());
          assertEquals(next ? "次: next" : "次: なし", last.text());
          if (previous) assertEquals("/scenarios/16", first.attr(HREF));
          if (next) assertEquals("/scenarios/18", last.attr(HREF));
        }
      }
  }

  @Test
  void dialogueAndSpeakerFlagsRemainIndependentInAllFourCases() throws IOException {
    int n = 0;
    for (boolean dialogue : List.of(false, true))
      for (boolean speaker : List.of(false, true)) {
        var d =
            render(
                "SCENE004-" + n,
                page(List.of(entry(7, dialogue, speaker ? "voice-name" : "", "text", List.of()))));
        n++;
        var row = d.select(ROW);
        assertEquals(dialogue, row.hasClass("dialogue"));
        assertEquals(!dialogue, row.hasClass("narration"));
        assertEquals(speaker ? 2 : 1, row.select(".line-meta span").size());
        assertEquals(speaker ? "7 voice-name" : "7", row.select(".line-meta").text());
      }
  }

  @Test
  void zeroOneAndTwoAudioLinksKeepStoredPlayerAndDownloadOrder() throws IOException {
    var sounds = List.of(audioRow(71), audioRow(72));
    for (int count : List.of(0, 1, 2)) {
      var d =
          render(
              "SCENE005-" + count,
              page(List.of(entry(9, true, "speaker", "text", sounds.subList(0, count)))));
      assertEquals(count, d.select("audio[controls][preload=none]").size());
      assertEquals(
          List.of("/audio/71", "/audio/72").subList(0, count), d.select("audio").eachAttr("src"));
      assertEquals(
          List.of("/audio/71/download", "/audio/72/download").subList(0, count),
          d.select("a.download").eachAttr(HREF));
      assertEquals(
          List.of("voice/71.ogg", "voice/72.ogg").subList(0, count),
          d.select(".audio span").eachText());
    }
  }

  @Test
  void titlesSpeakerAndMultilineBodyEscapeMarkupWithoutTextLoss() throws IOException {
    var literal = "<script>fixture</script>&\n日本語 é";
    var p = page(List.of(entry(9, true, literal, literal, List.of())));
    p.put(TITLE, literal);
    var d = render("SCENE006", p);
    assertEquals(literal, d.select("h1").getFirst().wholeText());
    assertEquals(literal, d.select(CONTENT).getFirst().wholeText());
    assertEquals(literal, d.select(".line-meta span").getLast().wholeText());
    assertTrue(d.select("script").isEmpty());
  }

  @Test
  void hundredEntriesKeepEveryAnchorPositionAndLongFirstBody() throws IOException {
    var records = new ArrayList<Map<String, Object>>();
    var longBody = "x".repeat(4096);
    for (int i = 1; i <= 100; i++)
      records.add(entry(i, true, "", i == 1 ? longBody : "line-" + i, List.of()));
    var d = render("SCENE007", page(records));
    assertEquals(100, d.select(ROW).size());
    assertEquals(longBody, d.select(CONTENT).getFirst().wholeText());
    for (int i = 0; i < 100; i++) {
      assertEquals("entry-" + (i + 1), d.select(ROW).get(i).id());
    }
    assertEquals("line-100", d.select(CONTENT).getLast().wholeText());
    assertTrue(d.select("audio,.download").isEmpty());
  }

  @Test
  void ownedConcurrentPagesKeepTheirBodiesAndTitlesIsolated()
      throws InterruptedException, ExecutionException, TimeoutException {
    var executor = Executors.newFixedThreadPool(2);
    try {
      List<Future<?>> futures = new ArrayList<>();
      for (int i = 0; i < 8; i++) {
        final int n = i;
        futures.add(
            executor.submit(
                () -> {
                  var text = "scene-" + n;
                  var p = page(List.of(entry(9, true, "", text, List.of())));
                  p.put(TITLE, text);
                  var d = render("SCENE008-" + n, p);
                  assertEquals(text, d.title());
                  assertEquals(text, d.select(CONTENT).text());
                  return null;
                }));
      }
      for (var f : futures) f.get(10, TimeUnit.SECONDS);
    } finally {
      executor.shutdownNow();
      assertTrue(executor.awaitTermination(10, TimeUnit.SECONDS));
    }
  }
}
