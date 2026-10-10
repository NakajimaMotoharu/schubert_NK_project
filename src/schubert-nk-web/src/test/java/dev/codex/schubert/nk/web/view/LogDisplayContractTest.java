package dev.codex.schubert.nk.web.view;

import static org.junit.jupiter.api.Assertions.*;

import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.layout.common.PagedResponseData;
import dev.codex.schubert.nk.protocol.layout.semantic.UserRole;
import dev.codex.schubert.nk.web.form.LogSearchForm;
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

/** P016-14/UI222,225/SS313: closed actual Log DOM fixture, no controller/DB/JMS. */
class LogDisplayContractTest {
  private static SessionPrincipal actor(UserRole role) {
    return new SessionPrincipal(
        "fixture-admin", role, AuthenticationContext.of("a".repeat(64)), Instant.EPOCH);
  }

  private static Document render(LogSearchViewModel page) {
    var resolver = new FileTemplateResolver();
    resolver.setPrefix("src/schubert-nk-web/src/main/resources/templates/");
    resolver.setSuffix(".html");
    resolver.setCharacterEncoding("UTF-8");
    resolver.setCacheable(false);
    var engine = new SpringTemplateEngine();
    engine.setTemplateResolver(resolver);
    var servlet = new MockServletContext();
    var request = new MockHttpServletRequest(servlet);
    request.setRequestURI("/logs");
    var exchange =
        JakartaServletWebApplication.buildApplication(servlet)
            .buildExchange(request, new MockHttpServletResponse());
    return Jsoup.parse(
        engine.process("logs", new WebContext(exchange, Locale.JAPAN, Map.of("page", page))));
  }

  @Test
  void logSummaryAnchorsResolveAndUnknownValuesStayEscaped() {
    String q = "<script>" + "x".repeat(257);
    var form =
        LogSearchForm.bind(
            Map.of(
                "q",
                List.of(q),
                "log_type",
                List.of("<unknown-log>"),
                "action",
                List.of("a".repeat(65)),
                "path",
                List.of("p".repeat(257)),
                "level",
                List.of("<unknown-level>"),
                "from",
                List.of("bad-from"),
                "to",
                List.of("bad-to"),
                "page",
                List.of("+1"),
                "owner",
                List.of("not-public")));
    assertFalse(form.isValid());
    assertThrows(IllegalStateException.class, form::toRequest);
    var dom = render(LogSearchViewModel.invalid(actor(UserRole.ADMIN), form));
    assertEquals(
        List.of(
            "#log-filters",
            "#log-q",
            "#log-log_type",
            "#log-action",
            "#log-path",
            "#log-level",
            "#log-from",
            "#log-to",
            "#log-filters"),
        dom.select("#log-errors li a").eachAttr("href"));
    for (var anchor : dom.select("#log-errors li a"))
      assertEquals(1, dom.select(anchor.attr("href")).size());
    assertEquals(q, dom.select("input[name=q]").val());
    assertEquals("<unknown-log>", dom.select("select[name=log_type] option[selected]").val());
    assertEquals("<unknown-level>", dom.select("select[name=level] option[selected]").val());
    assertEquals("メッセージはUTF-8で256 byte以内にしてください。", dom.select("#error-q").text());
    assertEquals("アクションはUTF-8で64 byte以内にしてください。", dom.select("#error-action").text());
    assertEquals("パスはUTF-8で256 byte以内にしてください。", dom.select("#error-path").text());
    assertEquals(0, dom.select("unknown-log,unknown-level,script:not([src])").size());
    assertFalse(dom.outerHtml().contains("not-public"));
    assertEquals(0, dom.select("nav.pagination").size());
  }

  @Test
  void adminEmptyLogKeepsDatePrecisionInputOrderAndFixedControlIds() {
    var form =
        LogSearchForm.bind(
            Map.of(
                "from",
                List.of("2026-10-01T00:00:00.123"),
                "to",
                List.of("2026-11-01T00:00:00.123")));
    assertTrue(form.isValid()); // Exact 31-day boundary from SSC073, no rounding.
    var page =
        LogSearchViewModel.success(
            actor(UserRole.ADMIN), form, new PagedResponseData(1, 100, 0, 1, 0, 0), List.of());
    var dom = render(page);
    assertEquals("schubert NK - Logs", dom.title());
    assertEquals(
        List.of("q", "log_type", "action", "path", "level", "from", "to"),
        dom.select("form.log-filters input,form.log-filters select").eachAttr("name"));
    for (String name : List.of("q", "log_type", "action", "path", "level", "from", "to")) {
      var control = dom.selectFirst("[name=" + name + "]");
      assertNotNull(control);
      assertEquals("log-" + name, control.id());
      assertNotNull(control.closest("label"));
    }
    for (String name : List.of("from", "to")) {
      var control = dom.selectFirst("[name=" + name + "]");
      assertNotNull(control);
      assertEquals("datetime-local", control.attr("type"));
      assertEquals("0.001", control.attr("step"));
    }
    assertTrue(dom.select("#log-errors").hasAttr("hidden"));
    assertEquals("該当するデータはありません", dom.select(".empty-results").text());
    assertEquals(0, dom.select("nav.pagination").size());
    assertThrows(
        IllegalArgumentException.class,
        () ->
            LogSearchViewModel.success(
                actor(UserRole.USER), form, new PagedResponseData(1, 100, 0, 1, 0, 0), List.of()));
  }
}
