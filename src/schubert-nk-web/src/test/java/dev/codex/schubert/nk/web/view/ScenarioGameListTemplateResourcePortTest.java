package dev.codex.schubert.nk.web.view;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.util.List;
import java.util.Locale;
import java.util.Map;
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

/** SCR004, FUN-004, UI223/234 and SS313. PT-WEB-SCR004-RSRC-001 and 002. */
final class ScenarioGameListTemplateResourcePortTest {
  private static final String HREF = "href";
  private static final String CARDS = ".menu-grid a.menu-item";
  private static final String FIRST_GAME = "NUKITASHI1";
  private static final String SECOND_GAME = "NUKITASHI2";
  private static final String TITLE = "Scenario Games";

  private static Document render(List<Map<String, String>> games) {
    var servlet = new MockServletContext();
    var request = new MockHttpServletRequest(servlet);
    request.setMethod("GET");
    request.setRequestURI("/scenarios");
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
    var page = Map.of("topBar", topBar, "games", games);
    return Jsoup.parse(
        engine.process("scenarios", new WebContext(exchange, Locale.JAPAN, Map.of("page", page))));
  }

  @Test
  void displaysGameCardsAndSearchInApprovedOrder() {
    var document =
        render(
            List.of(
                Map.of("code", FIRST_GAME, "title", "作品1 <章> & 音", HREF, "/scenarios/NUKITASHI1"),
                Map.of("code", SECOND_GAME, "title", "作品2", HREF, "/scenarios/NUKITASHI2")));

    assertEquals(TITLE, document.title());
    assertEquals(TITLE, document.select("h1").text());
    assertEquals(List.of("/search"), document.select("main > nav a").eachAttr(HREF));
    var cards = document.select(CARDS);
    assertEquals(List.of("/scenarios/NUKITASHI1", "/scenarios/NUKITASHI2"), cards.eachAttr(HREF));
    assertEquals(List.of(FIRST_GAME, SECOND_GAME), cards.select("strong").eachText());
    assertEquals(List.of("作品1 <章> & 音", "作品2"), cards.select("span").eachText());
    assertTrue(cards.select("span > *").isEmpty());
    assertTrue(document.select("p.empty").isEmpty());
  }

  @Test
  void rendersTheEmptyMessageWithoutInventingCards() {
    var document = render(List.of());

    assertEquals("該当するデータはありません", document.select("p.empty").text());
    assertEquals(List.of("/search"), document.select("main > nav a").eachAttr(HREF));
    assertTrue(document.select(CARDS).isEmpty());
  }
}
