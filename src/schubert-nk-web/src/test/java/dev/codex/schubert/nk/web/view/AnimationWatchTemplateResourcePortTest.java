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

/** PT-WATCH-DOM001..003; UI223/235 SS313. Actual resources and independent catalog maps only. */
final class AnimationWatchTemplateResourcePortTest {
  private static final String VIDEO = "video";
  private static final String HREF = "href";
  private static final String USER = "USER";
  private static final String ADMIN = "ADMIN";
  private static final String SYNTHETIC_CSRF = "synthetic-noncredential-csrf";

  private record CatalogRow(
      String title,
      String category,
      String path,
      String backHref,
      String backLabel,
      String mediaHref,
      String requestUri) {}

  private static final List<CatalogRow> CATALOG =
      List.of(
          new CatalogRow(
              "第1話",
              "メインパート",
              "main_part/NUKITASHI_THE_ANIMATION_01.mp4",
              "/animation/main",
              "メインパート一覧",
              "/animation/media/main-01",
              "/animation/videos/main-01"),
          new CatalogRow(
              "第1話 SUBTRACK版",
              "メインパート",
              "main_part/NUKITASHI_THE_ANIMATION_01_SUBTRACK.mp4",
              "/animation/main",
              "メインパート一覧",
              "/animation/media/main-01-subtrack",
              "/animation/videos/main-01-subtrack"),
          new CatalogRow(
              "OVA hinami",
              "OVA",
              "dosukebe_part/hinami.mp4",
              "/animation/ova",
              "OVA一覧",
              "/animation/media/ova-hinami",
              "/animation/videos/ova-hinami"),
          new CatalogRow(
              "オープニング映像",
              "オープニング",
              "op.mp4",
              "/animation",
              "アニメ視聴",
              "/animation/media/opening",
              "/animation/opening"));

  private static Map<String, Object> values(CatalogRow row, String role) {
    return Map.of(
        "title",
        row.title(),
        "category",
        row.category(),
        "displayPath",
        row.path(),
        "backHref",
        row.backHref(),
        "backLabel",
        row.backLabel(),
        "mediaHref",
        row.mediaHref(),
        "topBar",
        Map.of("username", "public-reader", "role", role));
  }

  private static Document render(String id, Map<String, Object> p, String requestUri)
      throws IOException {
    var servlet = new MockServletContext();
    var req = new MockHttpServletRequest(servlet);
    req.setMethod("GET");
    req.setRequestURI(requestUri);
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
            "page",
            Map.of("values", p),
            "_csrf",
            Map.of("parameterName", "_csrf", "token", SYNTHETIC_CSRF));
    var d =
        Jsoup.parse(
            engine.process("animation-watch", new WebContext(exchange, Locale.JAPAN, vars)));
    assertTrue(d.select("[th\\:text],[th\\:src],[th\\:replace],[th\\:href]").isEmpty());
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
  void approvedCatalogKindsHaveFixedPlaybackControlsAndBacklinks() throws IOException {
    for (int i = 0; i < CATALOG.size(); i++) {
      var row = CATALOG.get(i);
      var role = i % 2 == 0 ? USER : ADMIN;
      var d = render("WV001-" + i, values(row, role), row.requestUri());
      assertEquals(row.title(), d.title());
      assertEquals(row.title(), d.select("h1").text());
      assertEquals(row.category() + " / " + row.path(), d.select(".subtitle").text());
      assertEquals(role, d.select(".login-role").text());
      assertEquals(1, d.select("video[controls][preload=metadata][playsinline]").size());
      assertEquals(row.mediaHref(), d.select(VIDEO).attr("src"));
      assertFalse(d.select(VIDEO).hasAttr("autoplay"));
      assertFalse(d.select(VIDEO).hasAttr("loop"));
      assertEquals(
          List.of("/animation", row.backHref()),
          d.select(".video-page > header > .topbar-actions > nav.nav-links a").eachAttr(HREF));
      assertEquals(
          List.of("アニメ視聴", row.backLabel()),
          d.select(".video-page > header > .topbar-actions > nav.nav-links a").eachText());
      assertEquals("/css/schubert.css", d.select("link[rel=stylesheet]").attr(HREF));
      assertEquals(1, d.select(".video-page .video-shell > video").size());
      assertTrue(d.select("script,a.download,iframe").isEmpty());
    }
  }

  @Test
  void displayTextIsEscapedWhilePlayerAndNavigationStayStructural() throws IOException {
    var row = CATALOG.getFirst();
    var p = new HashMap<>(values(row, USER));
    var literal = "<script>fixture</script>&日本語";
    p.put("title", literal);
    p.put("category", literal);
    p.put("displayPath", literal);
    p.put("backLabel", literal);
    p.put("topBar", Map.of("username", literal, "role", USER));
    var d = render("WV002", p, row.requestUri());
    assertEquals(literal, d.title());
    assertEquals(literal, d.select("h1").getFirst().wholeText());
    assertEquals(literal + " / " + literal, d.select(".subtitle").getFirst().wholeText());
    assertEquals(literal, d.select(".login-user").text());
    assertEquals(literal, d.select("a[href='/animation/main']").text());
    assertEquals(row.mediaHref(), d.select(VIDEO).attr("src"));
    assertTrue(d.select("script,iframe").isEmpty());
  }

  @Test
  void boundedConcurrentViewsKeepEachTitleAndStreamSeparate()
      throws InterruptedException, ExecutionException, TimeoutException {
    var executor = Executors.newFixedThreadPool(2);
    try {
      List<Future<?>> futures = new ArrayList<>();
      for (int i = 0; i < 8; i++) {
        final int n = i;
        futures.add(
            executor.submit(
                () -> {
                  var row = CATALOG.get(n % CATALOG.size());
                  var p = new HashMap<>(values(row, USER));
                  var title = "concurrent-" + n;
                  p.put("title", title);
                  var d = render("WV003-" + n, p, row.requestUri());
                  assertEquals(title, d.title());
                  assertEquals(title, d.select("h1").text());
                  assertEquals(row.mediaHref(), d.select(VIDEO).attr("src"));
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
