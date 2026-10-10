package dev.codex.schubert.nk.web.view;

import static org.junit.jupiter.api.Assertions.*;

import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.layout.common.PagedResponseData;
import dev.codex.schubert.nk.protocol.layout.question.QuestionSummaryRecord;
import dev.codex.schubert.nk.protocol.layout.semantic.AnswerState;
import dev.codex.schubert.nk.protocol.layout.semantic.QuestionId;
import dev.codex.schubert.nk.protocol.layout.semantic.UserRole;
import dev.codex.schubert.nk.web.form.QuestionSearchForm;
import dev.codex.schubert.nk.web.session.SessionPrincipal;
import java.time.Instant;
import java.util.ArrayList;
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
import org.thymeleaf.templateresolver.FileTemplateResolver;
import org.thymeleaf.web.servlet.JakartaServletWebApplication;

/** P016-22/UI224/SS313: screen wiring only; shared pagination is verified once in P015-07. */
class QuestionListDisplayContractTest {
  private static SessionPrincipal actor(UserRole role) {
    return new SessionPrincipal("fixture-owner", role, AuthenticationContext.of("a".repeat(64)), Instant.EPOCH);
  }

  private static Document render(QuestionListViewModel page) {
    var resolver = new FileTemplateResolver();
    resolver.setPrefix("src/schubert-nk-web/src/main/resources/templates/");
    resolver.setSuffix(".html");
    resolver.setCharacterEncoding("UTF-8");
    resolver.setCacheable(false);
    var engine = new SpringTemplateEngine();
    engine.setTemplateResolver(resolver);
    var servlet = new MockServletContext();
    var request = new MockHttpServletRequest(servlet);
    request.setRequestURI("/questions");
    var exchange = JakartaServletWebApplication.buildApplication(servlet).buildExchange(request, new MockHttpServletResponse());
    return Jsoup.parse(engine.process("questions/list", new WebContext(exchange, Locale.JAPAN, Map.of("page", page))));
  }

  @Test
  void invalidSummaryAndUnknownStateRemainEscapedWithRoleSafeTargets() {
    for (UserRole role : UserRole.values()) {
      var form = QuestionSearchForm.bind(Map.of("keyword", List.of("<script>" + "x".repeat(257)),
          "username", List.of("<owner>" + "x".repeat(65)), "state", List.of("<unknown-state>"),
          "from", List.of("bad-from"), "to", List.of("bad-to"), "page", List.of("+1"),
          "owner", List.of("never-display-owner")), role);
      assertFalse(form.isValid());
      assertThrows(IllegalArgumentException.class, form::toRequest);
      var dom = render(QuestionListViewModel.invalid(actor(role), form));
      assertEquals(7, dom.select("#question-errors li a").size());
      for (var anchor : dom.select("#question-errors li a")) assertEquals(1, dom.select(anchor.attr("href")).size());
      assertEquals(role == UserRole.ADMIN ? "#question-owner" : "#question-filters",
          dom.select("#error-username a").attr("href"));
      assertEquals("#question-filters", dom.select("#error-page a").attr("href"));
      assertEquals("<unknown-state>", dom.select("select[name=state] option[selected]").val());
      assertEquals(role == UserRole.ADMIN ? 1 : 0, dom.select("input[name=username]").size());
      assertEquals(0, dom.select("script,owner,unknown-state").size());
      assertFalse(dom.outerHtml().contains("never-display-owner"));
      assertEquals(0, dom.select("nav.pagination").size());
    }
  }

  @Test
  void middlePageWiresBothSharedFragmentsAndRetainsTableHeaders() {
    var form = QuestionSearchForm.bind(Map.of("keyword", List.of("key word"), "page", List.of("2")), UserRole.USER);
    var rows = new ArrayList<QuestionSummaryRecord>();
    for (int i = 0; i < 50; i++) rows.add(new QuestionSummaryRecord(new QuestionId(101 - i),
        "01ARZ3NDEKTSV4RRFFQ69G5FAV", "fixture-owner", "質問<img>" + i,
        AnswerState.UNANSWERED, Instant.EPOCH.minusSeconds(i), Optional.empty()));
    var dom = render(QuestionListViewModel.success(actor(UserRole.USER), form,
        new PagedResponseData(2,50,101,3,51,100), rows));
    assertEquals(2, dom.select("nav.pagination.fifty").size());
    assertEquals(List.of("51 - 100 / 101", "51 - 100 / 101"), dom.select("nav.pagination > div").eachText());
    assertEquals(50, dom.select(".table-scroll table .question-row").size());
    assertEquals(1, dom.select(".table-scroll[tabindex=0][role=region] table thead").size());
    assertEquals(0, dom.select(".owner,.owner-heading,img").size());
    assertEquals("質問<img>0", dom.select(".question-summary").getFirst().text());
    assertEquals("/questions/101#delete-confirm", dom.select("a.delete").getFirst().attr("href"));
    assertEquals(List.of("keyword", "from", "to", "state"), dom.select("#question-filters input,#question-filters select").eachAttr("name"));
  }

  @Test
  void emptyPageKeepsApprovedMessageAndNoTableOrPagination() {
    var form = QuestionSearchForm.bind(Map.of(), UserRole.ADMIN);
    var dom = render(QuestionListViewModel.success(actor(UserRole.ADMIN), form,
        new PagedResponseData(1,50,0,1,0,0), List.of()));
    assertEquals("該当するデータはありません", dom.select(".empty-results").text());
    assertEquals(0, dom.select("nav.pagination,table").size());
    assertEquals(1, dom.select("input[name=username]").size());
  }
}
