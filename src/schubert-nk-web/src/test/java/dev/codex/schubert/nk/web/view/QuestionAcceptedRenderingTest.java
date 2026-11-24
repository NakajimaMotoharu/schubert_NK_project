package dev.codex.schubert.nk.web.view;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.layout.question.QuestionDetailResponseData;
import dev.codex.schubert.nk.protocol.layout.semantic.AnswerState;
import dev.codex.schubert.nk.protocol.layout.semantic.QuestionId;
import dev.codex.schubert.nk.protocol.layout.semantic.UserRole;
import dev.codex.schubert.nk.web.receipt.ReceiptReference;
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

/** SCR019, UI224 §3, SS313, PT-WEB-SCR019-DOM001. */
final class QuestionAcceptedRenderingTest {
  private static final String OWNER = "fixture-reader";
  private static final String RECEIPT = "0".repeat(26);
  private static final QuestionId QUESTION_ID = new QuestionId(19);
  private static final Instant SUBMITTED = Instant.parse("2026-11-24T15:04:05.123Z");

  @Test
  void typedReceiptKeepsCodePointBoundaryTimeAndReadOnlyNavigation() {
    String expectedSummary = "a".repeat(195) + " & <𠮷";
    var answer =
        new QuestionDetailResponseData(
            QUESTION_ID,
            RECEIPT,
            OWNER,
            AnswerState.UNANSWERED,
            expectedSummary + ">は表示しない",
            Optional.empty(),
            SUBMITTED,
            Optional.empty());
    var actor =
        new SessionPrincipal(
            OWNER, UserRole.USER, AuthenticationContext.of("12".repeat(32)), SUBMITTED);
    var reference = new ReceiptReference(RECEIPT, 19, SUBMITTED);
    var document = render(QuestionAcceptedViewModel.from(actor, reference, answer));
    assertEquals("質問を受け付けました。", document.select("p.accepted-message").text());
    assertEquals(RECEIPT, document.select("dd.receipt").text());
    assertEquals("2026-11-25 00:04:05", document.select("dd.submitted-at").text());
    assertEquals(expectedSummary, document.select("dd.question-body").text());
    assertTrue(document.select("dd.question-body > *").isEmpty());
    assertEquals(
        List.of("/notifications", "/questions/new", "/"),
        document.select("main > nav a").eachAttr("href"));
    assertTrue(document.select("form.question-input").isEmpty());
  }

  private static Document render(QuestionAcceptedViewModel page) {
    var servlet = new MockServletContext();
    var request = new MockHttpServletRequest(servlet);
    request.setMethod("GET");
    request.setRequestURI("/questions/accepted/" + RECEIPT);
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
        engine.process(
            "questions/accepted", new WebContext(exchange, Locale.JAPAN, Map.of("page", page))));
  }
}
