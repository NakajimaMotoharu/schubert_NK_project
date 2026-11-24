package dev.codex.schubert.nk.web.view;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.layout.admin.UserRecord;
import dev.codex.schubert.nk.protocol.layout.common.PagedResponseData;
import dev.codex.schubert.nk.protocol.layout.question.NotificationRecord;
import dev.codex.schubert.nk.protocol.layout.question.QuestionSummaryRecord;
import dev.codex.schubert.nk.protocol.layout.semantic.AnswerState;
import dev.codex.schubert.nk.protocol.layout.semantic.NotificationId;
import dev.codex.schubert.nk.protocol.layout.semantic.NotificationState;
import dev.codex.schubert.nk.protocol.layout.semantic.NotificationType;
import dev.codex.schubert.nk.protocol.layout.semantic.QuestionId;
import dev.codex.schubert.nk.protocol.layout.semantic.UserId;
import dev.codex.schubert.nk.protocol.layout.semantic.UserRole;
import dev.codex.schubert.nk.protocol.layout.semantic.UserState;
import dev.codex.schubert.nk.web.form.NotificationSearchForm;
import dev.codex.schubert.nk.web.form.QuestionSearchForm;
import dev.codex.schubert.nk.web.form.UserSearchForm;
import dev.codex.schubert.nk.web.session.SessionPrincipal;
import java.time.Instant;
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

/** SCR015/020/022, UI222 §6, SS313 §6.1, PT-WEB-PAGER-DOM001..003. */
final class FiftyItemListRenderingTest {
  private static final PagedResponseData LAST_PAGE = new PagedResponseData(2, 50, 51, 2, 51, 51);
  private static final Instant AT = Instant.parse("2026-11-01T00:00:00Z");
  private static final String OWNER = "fixture-reader";
  private static final String RECEIPT = "0".repeat(26);
  private static final String HREF = "href";

  @Test
  void userDirectoryRendersTheTypedAccountAndRetainsFiltersInBothPreviousLinks() {
    var filters =
        UserSearchForm.bind(
            Map.of(
                "username", List.of("fixture"), "state", List.of("ACTIVE"), "page", List.of("2")));
    var record =
        new UserRecord(
            new UserId(12),
            OWNER,
            UserRole.USER,
            UserState.ACTIVE,
            Optional.empty(),
            Optional.empty(),
            AT,
            AT,
            1);
    var view =
        UserListViewModel.success(actor(UserRole.ADMIN), filters, LAST_PAGE, List.of(record));
    var document = render("admin/user-list", "/admin/users", view);
    assertLastPage(document, "/admin/users?username=fixture&role=&state=ACTIVE&page=1");
    assertEquals(OWNER, document.select("tr.user-row td:first-child").text());
    assertEquals("/admin/users/12", document.select("tr.user-row a").attr(HREF));
  }

  @Test
  void notificationsRenderTheTypedStateLabelAndRetainDateAndTypeFilters() {
    var filters =
        NotificationSearchForm.bind(
            Map.of(
                "type", List.of("ACCEPTED"), "from", List.of("2026-11-01"), "page", List.of("2")));
    var record =
        new NotificationRecord(
            new NotificationId(12),
            RECEIPT,
            NotificationType.ACCEPTED,
            NotificationState.RECEIVED,
            AT,
            AT.plusSeconds(1),
            "受付の概要",
            false);
    var view =
        NotificationListViewModel.success(
            actor(UserRole.USER), filters, LAST_PAGE, List.of(record));
    var document = render("notifications/list", "/notifications", view);
    assertLastPage(document, "/notifications?type=ACCEPTED&from=2026-11-01&to=&page=1");
    assertEquals("受付通知", document.select("td.type").text());
    assertEquals(RECEIPT, document.select("td.receipt").text());
    assertEquals("/notifications/12", document.select("a.detail").attr(HREF));
  }

  @Test
  void questionsRenderTheTypedRecordAndRetainTheEncodedKeyword() {
    var filters =
        QuestionSearchForm.bind(
            Map.of(
                "keyword", List.of("A & B"), "state", List.of("UNANSWERED"), "page", List.of("2")),
            UserRole.USER);
    var record =
        new QuestionSummaryRecord(
            new QuestionId(12),
            RECEIPT,
            OWNER,
            "A & B",
            AnswerState.UNANSWERED,
            AT,
            Optional.empty());
    var view =
        QuestionListViewModel.success(actor(UserRole.USER), filters, LAST_PAGE, List.of(record));
    var document = render("questions/list", "/questions", view);
    assertLastPage(document, "/questions?keyword=A%20%26%20B&state=UNANSWERED&from=&to=&page=1");
    assertEquals("A & B", document.select("td.question-summary").text());
    assertEquals("未回答", document.select("td.state").text());
    assertEquals("/questions/12", document.select("a.detail").attr(HREF));
    assertTrue(document.select("td.owner").isEmpty());
  }

  private static void assertLastPage(Document document, String previous) {
    assertEquals(1, document.select("tbody tr").size());
    assertEquals(
        List.of("51 - 51 / 51", "51 - 51 / 51"), document.select(".pagination-range").eachText());
    assertEquals(List.of(previous, previous), document.select("a.previous").eachAttr(HREF));
    assertTrue(document.select("a.next").isEmpty());
  }

  private static SessionPrincipal actor(UserRole role) {
    return new SessionPrincipal(OWNER, role, AuthenticationContext.of("12".repeat(32)), AT);
  }

  private static Document render(String template, String path, Object page) {
    var servlet = new MockServletContext();
    var request = new MockHttpServletRequest(servlet);
    request.setMethod("GET");
    request.setRequestURI(path);
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
    return Jsoup.parse(
        engine.process(template, new WebContext(exchange, Locale.JAPAN, Map.of("page", page))));
  }
}
