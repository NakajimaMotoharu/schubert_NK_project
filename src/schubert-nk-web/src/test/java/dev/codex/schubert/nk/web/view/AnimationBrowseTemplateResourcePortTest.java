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

/** PT-ABROWSE-DOM001..008; UI223235/SS313. Related menu/list resources only. */
final class AnimationBrowseTemplateResourcePortTest {
  private static final String MENU = "animation";
  private static final String LIST = "animation-list";
  private static final String MAIN = "main";
  private static final String OVA = "ova";
  private static final String CATEGORY_OVA = "OVA";
  private static final String TITLE = "title";
  private static final String SECTION = "section";
  private static final String VIDEOS = "videos";
  private static final String ROWS = "rows";
  private static final String TOPBAR = "topBar";
  private static final String USER = "USER";
  private static final String ADMIN = "ADMIN";
  private static final String HREF = "href";
  private static final String SOURCE_TITLE = ".scenario-title";
  private static final String META = ".scenario-meta";
  private static final String LOCAL_NAV = "nav[aria-label='Animationナビゲーション'] a";
  private static final String SYNTHETIC_CSRF = "synthetic-noncredential-csrf";

  private static Map<String, Object> clip(
      String id, String title, String category, String path, long bytes) {
    return Map.of(
        TITLE,
        title,
        "category",
        category,
        "displayPath",
        path,
        "byteSize",
        bytes,
        HREF,
        "/animation/videos/" + id);
  }

  private static Map<String, Object> mainClip() {
    return clip("main-01", "第1話", "メインパート", "main_part/NUKITASHI_THE_ANIMATION_01.mp4", 1048576);
  }

  private static Map<String, Object> subClip() {
    return clip(
        "main-01-subtrack",
        "第1話 SUBTRACK版",
        "メインパート",
        "main_part/NUKITASHI_THE_ANIMATION_01_SUBTRACK.mp4",
        1048576);
  }

  private static Map<String, Object> ovaClip() {
    return clip("ova-hinami", "OVA hinami", CATEGORY_OVA, "dosukebe_part/hinami.mp4", 1048576);
  }

  private static Map<String, Object> pair(boolean subtrack) {
    return Map.of(
        MAIN, mainClip(), "subtrack", subtrack ? Optional.of(subClip()) : Optional.empty());
  }

  private static Map<String, Object> menuPage(String role, int main, int ova) {
    return Map.of(
        TOPBAR,
        Map.of("username", "public-reader", "role", role),
        "mainCount",
        main,
        "ovaCount",
        ova);
  }

  private static Map<String, Object> listPage(
      String section, int total, List<Map<String, Object>> videos, List<Map<String, Object>> rows) {
    var p = new HashMap<String, Object>();
    p.put(TITLE, "Animation fixture");
    p.put(SECTION, section);
    p.put("totalCount", total);
    p.put(VIDEOS, videos);
    p.put(ROWS, rows);
    p.put(TOPBAR, Map.of("username", "public-reader", "role", USER));
    return p;
  }

  private static Document render(String id, String template, Map<String, Object> p)
      throws Exception {
    var servlet = new MockServletContext();
    var req = new MockHttpServletRequest(servlet);
    req.setMethod("GET");
    req.setRequestURI(template.equals(MENU) ? "/animation" : "/animation/" + p.get(SECTION));
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
    var d = Jsoup.parse(engine.process(template, new WebContext(exchange, Locale.JAPAN, vars)));
    assertTrue(d.select("[th\\:text],[th\\:if],[th\\:each],[th\\:href],[th\\:replace]").isEmpty());
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
  void menuKeepsThreeApprovedCardsCountsAndRoleDisplay() throws Exception {
    for (var role : List.of(USER, ADMIN)) {
      var d = render("AB001-" + role, MENU, menuPage(role, 15, 4));
      assertEquals("Animation", d.title());
      assertEquals(role, d.select(".login-role").text());
      assertEquals(
          List.of("メインパート一覧", "OVA一覧", "オープニング映像"), d.select(".menu-grid strong").eachText());
      assertEquals(List.of("15本の映像", "4本の映像", "OP映像を再生する"), d.select(".menu-grid span").eachText());
      assertEquals(
          List.of("/animation/main", "/animation/ova", "/animation/opening"),
          d.select(".menu-grid a").eachAttr(HREF));
      assertEquals(List.of("/scenarios", "/search"), d.select(LOCAL_NAV).eachAttr(HREF));
      assertTrue(d.select("video,audio").isEmpty());
    }
  }

  @Test
  void zeroCountDisplayDoesNotInventNumericCatalogCounts() throws Exception {
    var d = render("AB002", MENU, menuPage(USER, 0, 0));
    assertEquals(List.of("0本の映像", "0本の映像", "OP映像を再生する"), d.select(".menu-grid span").eachText());
    assertEquals(3, d.select(".menu-item").size());
  }

  @Test
  void ovaCardsKeepFourStoredPositionsAndExplicitMetadata() throws Exception {
    var clips =
        List.of(
            ovaClip(),
            clip("ova-humino", "OVA humino", CATEGORY_OVA, "dosukebe_part/humino.mp4", 2097152),
            clip("ova-misaki", "OVA misaki", CATEGORY_OVA, "dosukebe_part/misaki.mp4", 3145728),
            clip("ova-nanase", "OVA nanase", CATEGORY_OVA, "dosukebe_part/nanase.mp4", 4194304));
    var d = render("AB003", LIST, listPage(OVA, 4, clips, List.of()));
    assertEquals(
        List.of("OVA hinami", "OVA humino", "OVA misaki", "OVA nanase"),
        d.select(SOURCE_TITLE).eachText());
    assertEquals(
        List.of(
            "/animation/videos/ova-hinami",
            "/animation/videos/ova-humino",
            "/animation/videos/ova-misaki",
            "/animation/videos/ova-nanase"),
        d.select(".animation-list > a").eachAttr(HREF));
    assertEquals(
        List.of(
            "OVA dosukebe_part/hinami.mp4 1.0 MB",
            "OVA dosukebe_part/humino.mp4 2.0 MB",
            "OVA dosukebe_part/misaki.mp4 3.0 MB",
            "OVA dosukebe_part/nanase.mp4 4.0 MB"),
        d.select(META).eachText());
    assertEquals("4本", d.select(".subtitle").text());
    assertTrue(d.select(".animation-row,.subtrack-link,.subtrack-placeholder,video").isEmpty());
  }

  @Test
  void mainPairPresenceUsesOneLinkOrOneEmptyPlaceholder() throws Exception {
    for (boolean subtrack : List.of(false, true)) {
      var p = listPage(MAIN, subtrack ? 2 : 1, List.of(), List.of(pair(subtrack)));
      var d = render("AB004-" + subtrack, LIST, p);
      assertEquals(1, d.select(".animation-row").size());
      assertEquals("/animation/videos/main-01", d.select(".animation-main-link").attr(HREF));
      assertEquals("第1話", d.select(SOURCE_TITLE).text());
      assertEquals(subtrack ? 1 : 0, d.select(".subtrack-link").size());
      assertEquals(subtrack ? 0 : 1, d.select(".subtrack-placeholder").size());
      if (subtrack) {
        assertEquals("/animation/videos/main-01-subtrack", d.select(".subtrack-link").attr(HREF));
        assertEquals("SUBTRACK", d.select(".subtrack-link").text());
      } else assertTrue(d.select(".subtrack-placeholder").text().isEmpty());
      assertEquals(subtrack ? "2本" : "1本", d.select(".subtitle").text());
    }
  }

  @Test
  void emptySectionsNeverReadInactiveNullCollectionsOrInventCards() throws Exception {
    for (String section : List.of(MAIN, OVA)) {
      var p = listPage(section, 0, List.of(), List.of());
      p.put(section.equals(MAIN) ? VIDEOS : ROWS, null);
      var d = render("AB005-" + section, LIST, p);
      assertEquals(1, d.select("section.animation-list").size());
      assertTrue(
          d.select(".scenario-link,.animation-row,.subtrack-link,.subtrack-placeholder").isEmpty());
      assertEquals("0本", d.select(".subtitle").text());
      assertEquals(List.of("/animation", "/search"), d.select(LOCAL_NAV).eachAttr(HREF));
    }
  }

  @Test
  void textMetadataAndTitlesEscapeWithoutExtraMarkupOrChangedHref() throws Exception {
    var literal = "<script>fixture</script>&";
    var clip = new HashMap<>(ovaClip());
    clip.put(TITLE, literal);
    clip.put("displayPath", literal);
    var p = listPage(OVA, 1, List.of(clip), List.of());
    p.put(TITLE, literal);
    var d = render("AB006", LIST, p);
    assertEquals(literal, d.title());
    assertEquals(literal, d.select("h1").text());
    assertEquals(literal, d.select(SOURCE_TITLE).text());
    assertEquals(literal, d.select(META + " span").get(1).text());
    assertEquals("/animation/videos/ova-hinami", d.select(".animation-list > a").attr(HREF));
    assertTrue(d.select("script,iframe").isEmpty());
  }

  @Test
  void byteFormattingKeepsZeroOneAndFractionalMegabyteBoundaries() throws Exception {
    long[] sizes = {0, 1, 1572864};
    String[] labels = {"0.0 MB", "0.0 MB", "1.5 MB"};
    for (int i = 0; i < sizes.length; i++) {
      var clip = new HashMap<>(ovaClip());
      clip.put("byteSize", sizes[i]);
      var d = render("AB007-" + i, LIST, listPage(OVA, 1, List.of(clip), List.of()));
      assertEquals(labels[i], d.select(META + " span").getLast().text());
    }
  }

  @Test
  void boundedConcurrentListsKeepBranchTitleAndRowsIsolated() throws Exception {
    try (var executor = Executors.newFixedThreadPool(2)) {
      List<Future<?>> futures = new ArrayList<>();
      for (int i = 0; i < 8; i++) {
        final int n = i;
        futures.add(
            executor.submit(
                () -> {
                  boolean main = n % 2 == 0;
                  var p =
                      listPage(
                          main ? MAIN : OVA,
                          1,
                          main ? List.of() : List.of(ovaClip()),
                          main ? List.of(pair(false)) : List.of());
                  var title = "independent-" + n;
                  p.put(TITLE, title);
                  var d = render("AB008-" + n, LIST, p);
                  assertEquals(title, d.title());
                  assertEquals(main ? "第1話" : "OVA hinami", d.select(SOURCE_TITLE).text());
                  assertEquals(main ? 1 : 0, d.select(".animation-row").size());
                  return null;
                }));
      }
      for (var f : futures) f.get(10, TimeUnit.SECONDS);
    }
  }
}
