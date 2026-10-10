package dev.codex.schubert.nk.web.view;

import static org.junit.jupiter.api.Assertions.*;

import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.layout.common.PagedResponseData;
import dev.codex.schubert.nk.protocol.layout.question.NotificationRecord;
import dev.codex.schubert.nk.protocol.layout.semantic.NotificationId;
import dev.codex.schubert.nk.protocol.layout.semantic.NotificationState;
import dev.codex.schubert.nk.protocol.layout.semantic.NotificationType;
import dev.codex.schubert.nk.protocol.layout.semantic.UserRole;
import dev.codex.schubert.nk.web.form.NotificationSearchForm;
import dev.codex.schubert.nk.web.session.SessionPrincipal;
import java.time.Instant;
import java.util.ArrayList;
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

/** P016-20/UI224/SS313: exact notification screen wiring, not actual owner authorization. */
class NotificationListDisplayContractTest {
  private static SessionPrincipal actor(UserRole role) {
    return new SessionPrincipal(
        "fixture-user", role, AuthenticationContext.of("a".repeat(64)), Instant.EPOCH);
  }

  private static Document render(NotificationListViewModel page) {
    var resolver = new FileTemplateResolver();
    resolver.setPrefix("src/schubert-nk-web/src/main/resources/templates/");
    resolver.setSuffix(".html");
    resolver.setCharacterEncoding("UTF-8");
    resolver.setCacheable(false);
    var engine = new SpringTemplateEngine();
    engine.setTemplateResolver(resolver);
    var servlet = new MockServletContext();
    var request = new MockHttpServletRequest(servlet);
    request.setRequestURI("/notifications");
    var exchange =
        JakartaServletWebApplication.buildApplication(servlet)
            .buildExchange(request, new MockHttpServletResponse());
    return Jsoup.parse(
        engine.process(
            "notifications/list", new WebContext(exchange, Locale.JAPAN, Map.of("page", page))));
  }

  @Test
  void invalidTypeAndUnknownOwnerProduceEscapedResolvableSummaryForEitherRole() {
    for (UserRole role : UserRole.values()) {
      var form =
          NotificationSearchForm.bind(
              Map.of(
                  "type",
                  List.of("<unknown-type>"),
                  "from",
                  List.of("bad-from"),
                  "to",
                  List.of("bad-to"),
                  "page",
                  List.of("+1"),
                  "owner",
                  List.of("never-display-owner")));
      assertFalse(form.isValid());
      assertThrows(IllegalArgumentException.class, form::toRequest);
      var dom = render(NotificationListViewModel.invalid(actor(role), form));
      assertEquals(5, dom.select("#notification-errors li a").size());
      for (var anchor : dom.select("#notification-errors li a"))
        assertEquals(1, dom.select(anchor.attr("href")).size());
      assertEquals("#notification-filters", dom.select("#error-page a").attr("href"));
      assertEquals("<unknown-type>", dom.select("select[name=type] option[selected]").val());
      assertEquals(0, dom.select("input[name=owner],input[name=username],unknown-type").size());
      assertFalse(dom.outerHtml().contains("never-display-owner"));
      assertEquals(0, dom.select("nav.pagination").size());
    }
  }

  @Test
  void middlePageWiresSharedNavigationAndRetainsOrderedEscapedTable() {
    var form = NotificationSearchForm.bind(Map.of("page", List.of("2")));
    var rows = new ArrayList<NotificationRecord>();
    for (int i = 0; i < 50; i++)
      rows.add(
          new NotificationRecord(
              new NotificationId(101 - i),
              "01ARZ3NDEKTSV4RRFFQ69G5FAV",
              NotificationType.ACCEPTED,
              NotificationState.RECEIVED,
              Instant.EPOCH.minusSeconds(i),
              Instant.EPOCH.minusSeconds(i),
              " 質問<img>" + i,
              false));
    var dom =
        render(
            NotificationListViewModel.success(
                actor(UserRole.ADMIN), form, new PagedResponseData(2, 50, 101, 3, 51, 100), rows));
    assertEquals(2, dom.select("nav.pagination.fifty").size());
    assertEquals(
        List.of("51 - 100 / 101", "51 - 100 / 101"), dom.select("nav.pagination > div").eachText());
    assertEquals(50, dom.select(".table-scroll table .notification-row").size());
    assertEquals(1, dom.select(".table-scroll[tabindex=0][role=region] table thead").size());
    assertEquals("/notifications/101", dom.select("a.detail").getFirst().attr("href"));
    assertEquals(" 質問<img>0", dom.select(".notification-summary").getFirst().wholeText());
    assertEquals(0, dom.select("img,a.delete,input[name=owner],input[name=username]").size());
    assertEquals(
        List.of("type", "from", "to"),
        dom.select("#notification-filters input,#notification-filters select").eachAttr("name"));
  }

  @Test
  void emptyPageKeepsApprovedMessageWithNoPaginationOrTable() {
    var dom =
        render(
            NotificationListViewModel.success(
                actor(UserRole.USER),
                NotificationSearchForm.bind(Map.of()),
                new PagedResponseData(1, 50, 0, 1, 0, 0),
                List.of()));
    assertEquals("該当するデータはありません", dom.select(".empty-results").text());
    assertEquals(0, dom.select("nav.pagination,table").size());
  }
}
