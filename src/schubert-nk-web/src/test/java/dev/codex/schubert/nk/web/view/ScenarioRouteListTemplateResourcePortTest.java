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

/** SCR005, FUN-004, UI223/234 and SS313. PT-WEB-SCR005-RSRC-001 and 002. */
final class ScenarioRouteListTemplateResourcePortTest {
  private static final String GAME_CODE = "NUKITASHI1";
  private static final String GAME_ROUTE = "/scenarios/NUKITASHI1";
  private static final String HREF = "href";
  private static final String ROUTE_CARDS = ".scenario-list a.scenario-link";

  private static Map<String, Object> route(String prefix, String title, int count) {
    return Map.of(HREF, GAME_ROUTE + "/" + prefix, "title", title, "fileCount", count);
  }

  private static Document render(List<Map<String, Object>> routes) {
    var servlet = new MockServletContext();
    var request = new MockHttpServletRequest(servlet);
    request.setMethod("GET");
    request.setRequestURI(GAME_ROUTE);
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
        Map.of("game", GAME_CODE, "upHref", "/scenarios", "topBar", topBar, "routes", routes);
    return Jsoup.parse(
        engine.process(
            "scenario-routes", new WebContext(exchange, Locale.JAPAN, Map.of("page", page))));
  }

  @Test
  void rendersApprovedHeadingRoutesAndFileCounts() {
    var document = render(List.of(route("03", "03: 前 <注> & 声", 3), route("09", "09: 後", 5)));

    assertEquals("NUKITASHI1 Routes", document.title());
    assertEquals(GAME_CODE, document.select("h1").text());
    assertEquals("シナリオルート選択", document.select(".subtitle").text());
    assertEquals(List.of("/scenarios", "/search"), document.select("main > nav a").eachAttr(HREF));
    var cards = document.select(ROUTE_CARDS);
    assertEquals(
        List.of("/scenarios/NUKITASHI1/03", "/scenarios/NUKITASHI1/09"), cards.eachAttr(HREF));
    assertEquals(List.of("03: 前 <注> & 声", "09: 後"), cards.select(".scenario-title").eachText());
    assertEquals(
        List.of(GAME_CODE, "3 files"), cards.get(0).select(".scenario-meta > span").eachText());
    assertEquals(
        List.of(GAME_CODE, "5 files"), cards.get(1).select(".scenario-meta > span").eachText());
    assertTrue(cards.select(".scenario-title > *").isEmpty());
  }

  @Test
  void rendersEmptyAndFiftyRoutesWithoutExtraNavigation() {
    var empty = render(List.of());
    assertEquals(1, empty.select(".scenario-list").size());
    assertTrue(empty.select(ROUTE_CARDS).isEmpty());
    var routes =
        IntStream.range(0, 50)
            .mapToObj(
                number -> {
                  var prefix = String.format(Locale.ROOT, "%02d", number);
                  return route(prefix, prefix + ": 章", 1);
                })
            .toList();

    var maximum = render(routes);
    var cards = maximum.select(ROUTE_CARDS);
    assertEquals(50, cards.size());
    assertEquals("/scenarios/NUKITASHI1/00", cards.get(0).attr(HREF));
    assertEquals("/scenarios/NUKITASHI1/49", cards.get(49).attr(HREF));
    assertTrue(maximum.select(".pagination, a[rel=prev], a[rel=next]").isEmpty());
  }
}
