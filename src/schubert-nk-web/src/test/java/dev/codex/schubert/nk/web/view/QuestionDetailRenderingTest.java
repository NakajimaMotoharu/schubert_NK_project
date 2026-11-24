package dev.codex.schubert.nk.web.view;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.layout.question.QuestionDetailResponseData;
import dev.codex.schubert.nk.protocol.layout.semantic.AnswerState;
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

/** SCR023, UI224/236, SS313, PT-WEB-QDETAIL-DOM001..003. Read-only rendering. */
final class QuestionDetailRenderingTest {
  private static final String OWNER = "fixture-owner";
  private static final String QUESTION = "質問 A & B";
  private static final String RECEIPT = "0".repeat(26);
  private static final String STATE = "dd.state";
  private static final String ANSWER_BODY = "dd.answer-body";
  private static final String ANSWER_TIME = "dd.answered-at";
  private static final String DELETE_CONFIRM = "#delete-confirm";
  private static final QuestionId ID = new QuestionId(12);
  private static final Instant SUBMITTED = Instant.parse("2026-11-01T00:00:00Z");

  @Test
  void unansweredOwnerSeesQuestionAndNoAnswer() {
    var document =
        render(UserRole.USER, AnswerState.UNANSWERED, Optional.empty(), Optional.empty());
    assertEquals("質問回答明細", document.title());
    assertEquals(RECEIPT, document.select("dd.receipt").text());
    assertEquals("2026-11-01 09:00:00", document.select("dd.submitted-at").text());
    assertEquals("未回答", document.select(STATE).text());
    assertEquals(QUESTION, document.select("dd.question-body").text());
    assertEquals("/questions", document.select("a.back").attr("href"));
    assertTrue(document.select("dd.owner").isEmpty());
    assertTrue(document.select(ANSWER_BODY + "," + ANSWER_TIME + "," + DELETE_CONFIRM).isEmpty());
  }

  @Test
  void adminSeesOwnerAndTheEmptyAnswerLiteral() {
    var document =
        render(
            UserRole.ADMIN,
            AnswerState.ANSWERED,
            Optional.of(""),
            Optional.of(SUBMITTED.plusSeconds(2)));
    assertEquals(OWNER, document.select("dd.owner").text());
    assertEquals("回答済み", document.select(STATE).text());
    assertEquals("（空の回答）", document.select(ANSWER_BODY).text());
    assertEquals("2026-11-01 09:00:02", document.select(ANSWER_TIME).text());
    assertTrue(document.select(DELETE_CONFIRM).isEmpty());
  }

  @Test
  void errorRendersItsLabelWithoutAnswerOrDeleteConfirmation() {
    var document = render(UserRole.USER, AnswerState.ERROR, Optional.empty(), Optional.empty());
    assertEquals("エラー", document.select(STATE).text());
    assertEquals(QUESTION, document.select("dd.question-body").text());
    assertTrue(document.select(ANSWER_BODY + "," + ANSWER_TIME + "," + DELETE_CONFIRM).isEmpty());
  }

  private static Document render(
      UserRole role, AnswerState state, Optional<String> answer, Optional<Instant> answeredAt) {
    var actor =
        new SessionPrincipal(
            role == UserRole.USER ? OWNER : "fixture-admin",
            role,
            AuthenticationContext.of("12".repeat(32)),
            SUBMITTED);
    var response =
        new QuestionDetailResponseData(
            ID, RECEIPT, OWNER, state, QUESTION, answer, SUBMITTED, answeredAt);
    var servlet = new MockServletContext();
    var request = new MockHttpServletRequest(servlet);
    request.setMethod("GET");
    request.setRequestURI("/questions/12");
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
    var page = QuestionDetailViewModel.from(actor, ID, response);
    return Jsoup.parse(
        engine.process(
            "questions/detail", new WebContext(exchange, Locale.JAPAN, Map.of("page", page))));
  }
}
