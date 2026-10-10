package dev.codex.schubert.nk.web.view;

import static org.junit.jupiter.api.Assertions.*;

import java.util.HashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import org.jsoup.Jsoup;
import org.jsoup.nodes.Document;
import org.junit.jupiter.api.Test;
import org.springframework.mock.web.MockHttpServletRequest;
import org.springframework.mock.web.MockHttpServletResponse;
import org.springframework.mock.web.MockServletContext;
import org.thymeleaf.context.WebContext;
import org.thymeleaf.spring6.SpringTemplateEngine;
import org.thymeleaf.templateresolver.FileTemplateResolver;
import org.thymeleaf.web.servlet.JakartaServletWebApplication;

/** P015-07/UI222 section6/SS313: shared fifty-row literal navigation fixture. */
class FiftyPaginationContractTest {
  private static Document render(Map<String, Object> page, boolean bottom) {
    var resolver = new FileTemplateResolver();
    resolver.setPrefix("src/schubert-nk-web/src/main/resources/templates/");
    resolver.setSuffix(".html");
    resolver.setCharacterEncoding("UTF-8");
    resolver.setCacheable(false);
    var engine = new SpringTemplateEngine();
    engine.setTemplateResolver(resolver);
    var servlet = new MockServletContext();
    var request = new MockHttpServletRequest(servlet);
    request.setRequestURI("/deputy-fixture");
    var exchange = JakartaServletWebApplication.buildApplication(servlet).buildExchange(request, new MockHttpServletResponse());
    return Jsoup.parse(engine.process("fragments/pagination", Set.of("fifty"),
        new WebContext(exchange, Locale.JAPAN, Map.of("page", page, "bottom", bottom))));
  }

  @Test
  void firstMiddleLastPreserveLiteralRangeAndTopBottomLinks() {
    for (boolean bottom : new boolean[] {false, true}) {
      for (var row : new int[][] {{1,50,101,0,2}, {51,100,101,1,3}, {101,101,101,2,0}}) {
        var page = new HashMap<String, Object>();
        page.put("page", Optional.of(Map.of("empty", false, "firstResult", row[0], "lastResult", row[1], "totalCount", row[2])));
        page.put("previousHref", row[3] == 0 ? Optional.empty() : Optional.of("/fixture?keyword=a%20%26&page=" + row[3]));
        page.put("nextHref", row[4] == 0 ? Optional.empty() : Optional.of("/fixture?keyword=a%20%26&page=" + row[4]));
        var dom = render(page, bottom);
        assertEquals(1, dom.select("nav.pagination.fifty").size());
        assertEquals(bottom, dom.select("nav").hasClass("bottom-nav"));
        assertEquals(row[0] + " - " + row[1] + " / 101", dom.select("nav > div").text());
        assertEquals("前の50件", dom.select("nav > a,nav > span").getFirst().text());
        assertEquals("次の50件", dom.select("nav > a,nav > span").getLast().text());
        if (row[3] != 0) assertEquals("/fixture?keyword=a%20%26&page=" + row[3], dom.select("a.previous").attr("href"));
        if (row[4] != 0) assertEquals("/fixture?keyword=a%20%26&page=" + row[4], dom.select("a.next").attr("href"));
      }
    }
  }

  @Test
  void emptyAndUnsearchedProduceNoPagination() {
    for (boolean bottom : new boolean[] {false, true}) {
      for (Optional<?> page : List.of(Optional.empty(), Optional.of(Map.of("empty", true)))) {
        assertEquals(0, render(Map.of("page", page), bottom).select("nav.pagination").size());
      }
    }
  }
}
