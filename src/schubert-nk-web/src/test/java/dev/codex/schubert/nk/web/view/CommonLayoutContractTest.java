package dev.codex.schubert.nk.web.view;

import static org.junit.jupiter.api.Assertions.*;

import java.util.HashMap;
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

/** P015-07/UI222/SS313: real fragment rendering with closed fixtures, no MVC/business context. */
class CommonLayoutContractTest {
  private static Document render(String template, String selector, Map<String, Object> values) {
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
    var exchange = JakartaServletWebApplication.buildApplication(servlet)
        .buildExchange(request, new MockHttpServletResponse());
    return Jsoup.parse(engine.process(template, Set.of(selector),
        new WebContext(exchange, Locale.JAPAN, values)));
  }

  @Test
  void commonTitleHasApprovedNkBrandWithoutDuplicatingExistingBrand() {
    for (var row : new String[][] {
        {"Logs", "schubert NK - Logs"}, {"質問要求", "schubert NK - 質問要求"},
        {"schubert NK - 検索", "schubert NK - 検索"},
        {"エラー - schubert NK", "エラー - schubert NK"},
        {"schubert NK", "schubert NK"}}) {
      var dom = render("fragments/layout", "head", Map.of("title", row[0]));
      assertEquals(1, dom.select("title").size());
      assertEquals(row[1], dom.title());
      assertEquals("/css/schubert.css", dom.select("link[rel=stylesheet]").attr("href"));
      assertEquals("utf-8", dom.select("meta[charset]").attr("charset"));
    }
  }

  @Test
  void titleUsesEscapedDisplayText() {
    var dom = render("fragments/layout", "head", Map.of("title", "章<img src=x> & 題"));
    assertEquals("schubert NK - 章<img src=x> & 題", dom.title());
    assertEquals(0, dom.select("img,script").size());
    assertTrue(dom.select("title").html().contains("&lt;img"));
  }

  @Test
  void commonHeaderShowsNkBrandAndEscapedIdentityWithoutChangingNavigation() {
    for (String role : new String[] {"USER", "ADMIN"}) {
      var dom = render("fragments/layout", "userActions", Map.of("topbar",
          Map.of("brand", "schubert NK", "username", "利用者<img src=x>", "role", role)));
      assertEquals("schubert NK", dom.select(".site-brand").text());
      assertEquals("利用者<img src=x>", dom.select(".login-user").text());
      assertEquals(role, dom.select(".login-role").text());
      assertEquals(0, dom.select("img,script,[data-token],[data-session]").size());
      assertEquals(java.util.List.of("/", "/notifications"), dom.select("nav a").eachAttr("href"));
      assertEquals("共通ナビゲーション", dom.select("nav").attr("aria-label"));
      assertEquals("post", dom.select("form.logout-form").attr("method"));
      assertEquals("/logout", dom.select("form.logout-form").attr("action"));
      assertEquals("ログアウト", dom.select("button").text());
    }
  }

  @Test
  void commonPaginationKeepsLiteralFirstMiddleLastAndEmptyContracts() {
    for (String template : new String[] {"fragments/pagination", "fragments/log-pagination"}) {
      String fragment = template.endsWith("log-pagination") ? "logs" : "search";
      for (boolean bottom : new boolean[] {false, true}) {
        for (var expected : new int[][] {{1,100,201,0,2}, {101,200,201,1,3}, {201,201,201,2,0}}) {
          var numbers = Map.of("empty", false, "firstResult", expected[0],
              "lastResult", expected[1], "totalCount", expected[2]);
          var page = new HashMap<String, Object>();
          page.put("results", Optional.of(Map.of("page", numbers)));
          page.put("previousHref", expected[3] == 0 ? Optional.empty() : Optional.of("?page=" + expected[3]));
          page.put("nextHref", expected[4] == 0 ? Optional.empty() : Optional.of("?page=" + expected[4]));
          var dom = render(template, fragment, Map.of("page", page, "bottom", bottom));
          assertEquals(1, dom.select("nav.pagination").size());
          assertEquals(bottom, dom.select("nav").hasClass("bottom-nav"));
          assertEquals(expected[0] + " - " + expected[1] + " / 201", dom.select("nav > div").text());
          assertEquals(1, dom.select("nav > a,nav > span").stream()
              .filter(node -> node.text().equals("前の100件")).count());
          assertEquals(1, dom.select("nav > a,nav > span").stream()
              .filter(node -> node.text().equals("次の100件")).count());
          assertEquals((expected[3] > 0 ? 1 : 0) + (expected[4] > 0 ? 1 : 0), dom.select("nav > a").size());
        }
        for (var results : new Optional<?>[] {
            Optional.empty(), Optional.of(Map.of("page", Map.of("empty", true)))}) {
          var dom = render(template, fragment, Map.of("page", Map.of("results", results), "bottom", bottom));
          assertEquals(0, dom.select("nav.pagination").size());
        }
      }
    }
  }
}
