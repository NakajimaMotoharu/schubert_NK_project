package dev.codex.schubert.nk.web.view;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.protocol.layout.common.PagedResponseData;
import java.util.HashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Optional;
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

/** PT-WEB-PAGER001..003; SCR015/020/022, UI222 section 6, SS313 section 6.1. */
final class FiftyItemListPaginationTemplateTest {
  private static final String PREVIOUS = ".previous";
  private static final String NEXT = ".next";
  private static final String RANGE = ".pagination-range";
  private static final String HREF = "href";
  private static final String KEEP_FILTER = "?fixture=retained&page=";

  private record Screen(String template, String path) {}

  private static final List<Screen> SCREENS =
      List.of(
          new Screen("admin/user-list", "/admin/users"),
          new Screen("notifications/list", "/notifications"),
          new Screen("questions/list", "/questions"));

  @Test
  void middlePageHasMatchingLinksAndRangeAboveAndBelowTheRows() {
    var page = new PagedResponseData(2, 50, 121, 3, 51, 100);
    for (var screen : SCREENS) {
      var document = render(screen, Optional.of(page));
      assertEquals(List.of("51 - 100 / 121", "51 - 100 / 121"), document.select(RANGE).eachText());
      assertEquals(List.of("前の50件", "前の50件"), document.select("a" + PREVIOUS).eachText());
      assertEquals(List.of("次の50件", "次の50件"), document.select("a" + NEXT).eachText());
      String previous = screen.path() + KEEP_FILTER + 1;
      String next = screen.path() + KEEP_FILTER + 3;
      assertEquals(List.of(previous, previous), document.select("a" + PREVIOUS).eachAttr(HREF));
      assertEquals(List.of(next, next), document.select("a" + NEXT).eachAttr(HREF));
      assertEquals(1, document.select("nav:has(" + RANGE + ") + section:has(table)").size());
      assertEquals(1, document.select("section:has(table) + nav:has(" + RANGE + ")").size());
      assertEquals(50, document.select("tbody tr").size());
    }
  }

  @Test
  void firstAndLastPageDisableOnlyTheirUnavailableLinks() {
    for (var screen : SCREENS) {
      var first = render(screen, Optional.of(new PagedResponseData(1, 50, 51, 2, 1, 50)));
      var last = render(screen, Optional.of(new PagedResponseData(2, 50, 51, 2, 51, 51)));
      assertEquals(List.of("1 - 50 / 51", "1 - 50 / 51"), first.select(RANGE).eachText());
      assertEquals(List.of("51 - 51 / 51", "51 - 51 / 51"), last.select(RANGE).eachText());
      assertTrue(first.select("a" + PREVIOUS).isEmpty());
      assertEquals(2, first.select("a" + NEXT).size());
      assertEquals(2, last.select("a" + PREVIOUS).size());
      assertTrue(last.select("a" + NEXT).isEmpty());
    }
  }

  @Test
  void emptyAndInvalidResponsesNeverRenderPageControls() {
    for (var screen : SCREENS) {
      var empty = render(screen, Optional.of(new PagedResponseData(1, 50, 0, 1, 0, 0)));
      assertEquals("該当するデータはありません", empty.select(".empty-results").text());
      assertTrue(empty.select("table,a" + PREVIOUS + ",a" + NEXT + "," + RANGE).isEmpty());
      var invalid = render(screen, Optional.empty());
      assertTrue(invalid.select("table,.empty-results," + RANGE).isEmpty());
    }
  }

  private static Document render(Screen screen, Optional<PagedResponseData> data) {
    var servlet = new MockServletContext();
    var request = new MockHttpServletRequest(servlet);
    request.setMethod("GET");
    request.setRequestURI(screen.path());
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
    var previous =
        data.filter(summary -> summary.effectivePage() > 1)
            .map(summary -> screen.path() + KEEP_FILTER + (summary.effectivePage() - 1));
    var next =
        data.filter(summary -> summary.effectivePage() < summary.totalPages())
            .map(summary -> screen.path() + KEEP_FILTER + (summary.effectivePage() + 1));
    var rows =
        data.filter(summary -> summary.totalCount() > 0)
            .map(
                summary ->
                    IntStream.rangeClosed((int) summary.firstResult(), (int) summary.lastResult())
                        .mapToObj(id -> row(screen.path() + "/" + id))
                        .toList())
            .orElseGet(List::of);
    var page =
        Map.of(
            "topBar",
            Map.of("username", "fixture-reader", "role", "USER"),
            "filters",
            filters(),
            "page",
            data.map(summary -> PageViewModel.from(summary, 50)),
            "previousHref",
            previous,
            "nextHref",
            next,
            "rows",
            rows);
    return Jsoup.parse(
        engine.process(
            screen.template(), new WebContext(exchange, Locale.JAPAN, Map.of("page", page))));
  }

  private static Map<String, String> row(String href) {
    var values = new HashMap<String, String>();
    for (var field :
        List.of(
            "username", "role", "state", "lockedUntil", "lastLogin", "createdAt", "updatedAt",
            "type", "receiptId", "submittedAt", "lastUpdatedAt", "summary", "stateLabel",
            "answeredAt")) {
      values.put(field, "fixture");
    }
    values.put("detailHref", href);
    values.put("deleteHref", href + "/delete");
    return values;
  }

  private static Map<String, Object> filters() {
    return Map.of(
        "issues", Map.of(),
        "values", Map.of("type", "", "from", "", "to", "", "keyword", "", "state", ""),
        "admin", false,
        "username", "",
        "state", "",
        "role", "");
  }
}
