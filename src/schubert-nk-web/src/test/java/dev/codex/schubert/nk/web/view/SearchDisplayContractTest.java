package dev.codex.schubert.nk.web.view;

import static org.junit.jupiter.api.Assertions.*;

import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.layout.common.PagedResponseData;
import dev.codex.schubert.nk.protocol.layout.semantic.UserRole;
import dev.codex.schubert.nk.web.form.ScenarioSearchForm;
import dev.codex.schubert.nk.web.session.SessionPrincipal;
import java.time.Instant;
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
import org.thymeleaf.templateresolver.FileTemplateResolver;
import org.thymeleaf.web.servlet.JakartaServletWebApplication;

/** P016-03/UI222,223/SS313: independent actual template expectations, no MVC/DB/service. */
class SearchDisplayContractTest {
  private static SessionPrincipal actor() {
    return new SessionPrincipal(
        "fixture-user", UserRole.USER, AuthenticationContext.of("a".repeat(64)), Instant.EPOCH);
  }

  private static Document render(ScenarioSearchViewModel page) {
    var resolver = new FileTemplateResolver();
    resolver.setPrefix("src/schubert-nk-web/src/main/resources/templates/");
    resolver.setSuffix(".html");
    resolver.setCharacterEncoding("UTF-8");
    resolver.setCacheable(false);
    var engine = new SpringTemplateEngine();
    engine.setTemplateResolver(resolver);
    var servlet = new MockServletContext();
    var request = new MockHttpServletRequest(servlet);
    request.setRequestURI("/search");
    var exchange =
        JakartaServletWebApplication.buildApplication(servlet)
            .buildExchange(request, new MockHttpServletResponse());
    return Jsoup.parse(
        engine.process("search", new WebContext(exchange, Locale.JAPAN, Map.of("page", page))));
  }

  @Test
  void invalidValuesAreEscapedAndEverySummaryAnchorResolvesToItsControl() {
    String rawQ = "<script>" + "x".repeat(257);
    var form =
        ScenarioSearchForm.bind(
            Map.of(
                "q",
                List.of(rawQ),
                "game",
                List.of("<unknown-game>"),
                "speaker",
                List.of("<img>&"),
                "chapter",
                List.of("章<&>"),
                "entry_type",
                List.of("<unknown-type>"),
                "voice",
                List.of("<unknown-voice>"),
                "page",
                List.of("+1"),
                "owner",
                List.of("do-not-reflect")));
    assertFalse(form.isValid());
    assertThrows(IllegalStateException.class, form::toRequest);
    var dom = render(ScenarioSearchViewModel.invalid(actor(), form));
    assertEquals(
        List.of(
            "#search-filters",
            "#search-q",
            "#search-game",
            "#search-entry_type",
            "#search-voice",
            "#search-filters"),
        dom.select("#search-errors li a").eachAttr("href"));
    for (var anchor : dom.select("#search-errors li a")) {
      assertEquals(1, dom.select(anchor.attr("href")).size());
    }
    assertEquals("本文はUTF-8で256 byte以内にしてください。", dom.select("#error-q").text());
    assertEquals(rawQ, dom.select("input[name=q]").val());
    assertEquals("<unknown-game>", dom.select("select[name=game] option[selected]").val());
    assertEquals("<img>&", dom.select("select[name=speaker] option[selected]").val());
    assertEquals("章<&>", dom.select("input[name=chapter]").val());
    assertEquals("<unknown-type>", dom.select("select[name=entry_type] option[selected]").val());
    assertEquals("<unknown-voice>", dom.select("select[name=voice] option[selected]").val());
    assertEquals(0, dom.select("img,iframe,unknown-game,unknown-type,unknown-voice").size());
    assertEquals(1, dom.select("script[src='/js/search-speaker-submit.js'][defer]").size());
    assertFalse(dom.outerHtml().contains("do-not-reflect"));
    assertEquals(0, dom.select("nav.pagination").size());
  }

  @Test
  void emptyResultsPreserveInputOrderAndLabelControlAssociation() {
    var page =
        ScenarioSearchViewModel.success(
            actor(),
            ScenarioSearchForm.bind(Map.of()),
            List.of(),
            List.of(),
            new PagedResponseData(1, 100, 0, 1, 0, 0),
            List.of());
    var dom = render(page);
    assertEquals("ja", dom.select("html").attr("lang"));
    assertEquals("schubert NK - 検索", dom.title());
    assertEquals(
        List.of("q", "game", "speaker", "chapter", "entry_type", "voice"),
        dom.select("form.filters input,form.filters select").eachAttr("name"));
    for (String name : List.of("q", "game", "speaker", "chapter", "entry_type", "voice")) {
      var control = dom.selectFirst("[name=" + name + "]");
      assertNotNull(control);
      assertEquals("search-" + name, control.id());
      assertNotNull(control.closest("label"));
    }
    assertEquals("get", dom.select("form.filters").attr("method"));
    assertEquals("/search", dom.select("form.filters").attr("action"));
    assertTrue(dom.select("#search-errors").hasAttr("hidden"));
    assertEquals("該当するデータはありません", dom.select(".empty-results").text());
    assertEquals(0, dom.select("nav.pagination").size());
  }
}
