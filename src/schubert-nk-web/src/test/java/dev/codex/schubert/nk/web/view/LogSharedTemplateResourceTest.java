package dev.codex.schubert.nk.web.view;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Optional;
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

/** SS313 and UI222/225, PT-WEB-FRAG-001 and PT-WEB-FRAG-002. */
final class LogSharedTemplateResourceTest {
  private static final String LOG_ERRORS = "#log-errors";

  @Test
  void frag001BothPagersKeepTheLogLabelsResultRangeAndLinks() {
    var resultPage =
        Map.of(
            "empty",
            false,
            "effectivePage",
            2,
            "totalPages",
            3,
            "firstResult",
            101,
            "lastResult",
            200,
            "totalCount",
            205);
    var rendered =
        render(
            Optional.of(Map.of("page", resultPage, "rows", List.of())),
            Optional.of("/logs?q=ready&page=1"),
            Optional.of("/logs?q=ready&page=3"),
            List.of());

    assertEquals("205 logs / page 2 of 3", rendered.select(".log-page .count").text());
    assertEquals(
        List.of("log pagination", "log pagination bottom"),
        rendered.select("nav.pagination").eachAttr("aria-label"));
    assertEquals(
        List.of("101 - 200 / 205", "101 - 200 / 205"),
        rendered.select("nav.pagination div").eachText());
    assertEquals(1, rendered.select("nav.pagination.bottom-nav").size());
    for (var pager : rendered.select("nav.pagination")) {
      assertEquals(List.of("前の100件", "次の100件"), pager.select("a").eachText());
      assertEquals(
          List.of("/logs?q=ready&page=1", "/logs?q=ready&page=3"),
          pager.select("a").eachAttr("href"));
    }
    assertEquals(1, rendered.select(LOG_ERRORS + "[hidden][role=alert]").size());
    assertEquals(7, rendered.select("form.log-filters [aria-describedby=log-errors]").size());
  }

  @Test
  void frag002ValidationPreservesLogErrorIdsOrderingAndLiteralText() {
    var rendered =
        render(
            Optional.empty(),
            Optional.empty(),
            Optional.empty(),
            List.of(
                Map.of("name", "from", "message", "先に入力 <A&B>"),
                Map.of("name", "to", "message", "末尾の入力")));

    assertEquals(
        List.of("error-from", "error-to"), rendered.select(LOG_ERRORS + " li").eachAttr("id"));
    assertEquals(List.of("先に入力 <A&B>", "末尾の入力"), rendered.select(LOG_ERRORS + " li").eachText());
    assertTrue(rendered.select(LOG_ERRORS + " li *").isEmpty());
    assertFalse(rendered.select(LOG_ERRORS).hasAttr("hidden"));
    assertTrue(rendered.select("nav.pagination,.log-row").isEmpty());
  }

  private static Document render(
      Optional<Map<String, Object>> results,
      Optional<String> previous,
      Optional<String> next,
      List<Map<String, String>> errors) {
    var servlet = new MockServletContext();
    var request = new MockHttpServletRequest(servlet, "GET", "/logs");
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
    var filters =
        Map.of(
            "q", "ready", "logType", "", "action", "", "path", "", "level", "", "from", "", "to",
            "");
    var topBar = Map.of("username", "reviewer", "role", "ADMIN");
    var page =
        Map.of(
            "filters", filters,
            "topBar", topBar,
            "results", results,
            "previousHref", previous,
            "nextHref", next,
            "errors", errors);
    return Jsoup.parse(
        engine.process("logs", new WebContext(exchange, Locale.JAPAN, Map.of("page", page))));
  }
}
