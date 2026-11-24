package dev.codex.schubert.nk.web.view;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.layout.question.NotificationDetailResponseData;
import dev.codex.schubert.nk.protocol.layout.semantic.NotificationErrorCode;
import dev.codex.schubert.nk.protocol.layout.semantic.NotificationId;
import dev.codex.schubert.nk.protocol.layout.semantic.NotificationState;
import dev.codex.schubert.nk.protocol.layout.semantic.NotificationType;
import dev.codex.schubert.nk.protocol.layout.semantic.QuestionId;
import dev.codex.schubert.nk.protocol.layout.semantic.UserRole;
import dev.codex.schubert.nk.web.session.SessionPrincipal;
import java.time.Instant;
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

/** PT-WEB-NDETAIL-DOM001..003; SCR021, UI224/236, SS313. Read-only display. */
final class NotificationDetailRenderingTest {
  private static final String STATE = "dd.state";
  private static final String NO_CANCEL = "form.cancel-form";
  private static final String RECEIPT = "0".repeat(26);
  private static final String QUESTION = "公開の合成質問";
  private static final String ERROR_TEXT = "処理を完了できませんでした。";
  private static final NotificationId ID = new NotificationId(12);
  private static final Instant AT = Instant.parse("2026-11-01T00:00:00Z");

  @Test
  void completedEmptyAnswerHasItsLiteralAndExactDetailLink() {
    var document = render(completed(false));
    assertEquals("処理完了", document.select(STATE).text());
    assertEquals("2026-11-01 09:00:02", document.select("dd.completed-at").text());
    assertEquals(QUESTION, document.select(".question-body").text());
    assertEquals("（空の回答）", document.select(".answer-body").text());
    assertEquals("/questions/99", document.select("a.question-detail").attr("href"));
    assertTrue(document.select(NO_CANCEL).isEmpty());
  }

  @Test
  void logicallyDeletedRecordOmitsQuestionAnswerAndTheLink() {
    var document = render(completed(true));
    assertEquals("処理完了", document.select(STATE).text());
    assertEquals("質問・回答は削除済みです。", document.select("p.deleted").text());
    assertTrue(document.select(".question-body,.answer-body,.question-detail").isEmpty());
    assertTrue(document.select(NO_CANCEL).isEmpty());
  }

  @Test
  void errorShowsItsFixedPublicCodeAndMessageWithoutAnswerControls() {
    var input =
        new NotificationDetailResponseData(
            ID,
            RECEIPT,
            NotificationType.ERROR,
            NotificationState.ERROR,
            AT,
            Optional.of(AT.plusSeconds(1)),
            Optional.empty(),
            Optional.of(AT.plusSeconds(3)),
            Optional.empty(),
            false,
            Optional.of(QUESTION),
            Optional.empty(),
            Optional.of(NotificationErrorCode.SYSTEM_UNAVAILABLE),
            Optional.of(ERROR_TEXT),
            Optional.of(new QuestionId(99)));
    var document = render(input);
    assertEquals("エラー", document.select(STATE).text());
    assertEquals("2026-11-01 09:00:03", document.select("dd.error-at").text());
    assertEquals("SYSTEM_UNAVAIL", document.select(".error-code").text());
    assertEquals(ERROR_TEXT, document.select(".user-facing-error").text());
    assertTrue(document.select(".answer-body,.question-detail").isEmpty());
    assertTrue(document.select(NO_CANCEL).isEmpty());
  }

  private static NotificationDetailResponseData completed(boolean deleted) {
    return new NotificationDetailResponseData(
        ID,
        RECEIPT,
        NotificationType.COMPLETED,
        NotificationState.COMPLETED,
        AT,
        Optional.of(AT.plusSeconds(1)),
        Optional.of(AT.plusSeconds(2)),
        Optional.empty(),
        Optional.empty(),
        deleted,
        deleted ? Optional.empty() : Optional.of(QUESTION),
        deleted ? Optional.empty() : Optional.of(""),
        Optional.empty(),
        Optional.empty(),
        deleted ? Optional.empty() : Optional.of(new QuestionId(99)));
  }

  private static Document render(NotificationDetailResponseData data) {
    var actor =
        new SessionPrincipal(
            "fixture-reader", UserRole.USER, AuthenticationContext.of("12".repeat(32)), AT);
    var servlet = new MockServletContext();
    var request = new MockHttpServletRequest(servlet);
    request.setMethod("GET");
    request.setRequestURI("/notifications/12");
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
    var page = NotificationDetailViewModel.from(actor, ID, data);
    return Jsoup.parse(
        engine.process(
            "notifications/detail", new WebContext(exchange, Locale.JAPAN, Map.of("page", page))));
  }
}
