package dev.codex.schubert.nk.web.view;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.stream.IntStream;
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

/** SCR006, FUN-004, UI223/234 and SS313. PT-WEB-SCR006-RSRC-001 through 003. */
final class ScenarioFileListTemplateResourcePortTest {
  private static final String HREF = "href";
  private static final String FILE_CARDS = ".scenario-list a.scenario-link";

  private static Map<String, Object> row(String href, String title, String path, int count) {
    return Map.of(HREF, href, "displayTitle", title, "displayPath", path, "entryCount", count);
  }

  private static Document render(List<Map<String, Object>> files) {
    var servlet = new MockServletContext();
    var request = new MockHttpServletRequest(servlet);
    request.setMethod("GET");
    request.setRequestURI("/scenarios/NUKITASHI1/05");
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

    var topBar = Map.of("brand", "schubert NK", "username", "reader", "role", "USER");
    var page =
        Map.of(
            "title", "05: ルート",
            "game", "NUKITASHI1",
            "upHref", "/scenarios/NUKITASHI1",
            "topBar", topBar,
            "files", files);
    return Jsoup.parse(
        engine.process(
            "scenario-files", new WebContext(exchange, Locale.JAPAN, Map.of("page", page))));
  }

  @Test
  void displaysRouteHeadingAndApprovedNavigation() {
    var document = render(List.of(row("/scenarios/91", "前章", "script/first.txt", 12)));

    assertEquals("NUKITASHI1 05: ルート", document.title());
    assertEquals("05: ルート", document.select("h1").text());
    assertEquals("NUKITASHI1", document.select(".subtitle").text());
    assertEquals("schubert NK", document.select(".brand").text());
    assertEquals("reader", document.select(".login-user").text());
    assertEquals("USER", document.select(".login-role").text());
    assertEquals(
        List.of("/scenarios", "/scenarios/NUKITASHI1", "/search"),
        document.select("main > nav a").eachAttr(HREF));
    assertEquals(
        List.of("/", "/notifications"), document.select(".topbar-actions nav a").eachAttr(HREF));
    assertEquals(1, document.select("form.logout-form[action=/logout][method=post]").size());
  }

  @Test
  void retainsOrderAndOnlyUsesTheGivenNumericLinks() {
    var document =
        render(
            List.of(
                row("/scenarios/91", "前章 <注> & 声", "script/<chapter>&.txt", 12),
                row("/scenarios/17", "後章", "script/end.txt", 3)));

    var cards = document.select(FILE_CARDS);
    assertEquals(List.of("/scenarios/91", "/scenarios/17"), cards.eachAttr(HREF));
    assertEquals(List.of("前章 <注> & 声", "後章"), cards.select(".scenario-title").eachText());
    assertEquals(
        List.of("NUKITASHI1", "script/<chapter>&.txt", "12 entries"),
        cards.get(0).select(".scenario-meta > span").eachText());
    assertEquals(
        List.of("NUKITASHI1", "script/end.txt", "3 entries"),
        cards.get(1).select(".scenario-meta > span").eachText());
    assertTrue(cards.select(".scenario-title > *, .scenario-meta > span > *").isEmpty());
  }

  @Test
  void rendersBothEmptyAndFiveHundredRowsWithoutPagination() {
    var empty = render(List.of());
    assertEquals(1, empty.select(".scenario-list").size());
    assertTrue(empty.select(FILE_CARDS).isEmpty());

    var rows =
        IntStream.rangeClosed(1, 500)
            .mapToObj(id -> row("/scenarios/" + id, "章 " + id, "script/chapter.txt", 1))
            .toList();
    var maximum = render(rows);
    var cards = maximum.select(FILE_CARDS);
    assertEquals(500, cards.size());
    assertEquals("/scenarios/1", cards.get(0).attr(HREF));
    assertEquals("/scenarios/500", cards.get(499).attr(HREF));
    assertTrue(maximum.select(".pagination, a[rel=prev], a[rel=next]").isEmpty());
  }
}
