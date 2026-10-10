package dev.codex.schubert.nk.web.view;

import static org.junit.jupiter.api.Assertions.*;

import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.layout.semantic.UserRole;
import dev.codex.schubert.nk.web.form.QuestionSubmitForm;
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

/** P016-18/UI222,224/SS313: request-only synthetic question display, no real token/session. */
class QuestionInputDisplayContractTest {
  private static final String PUBLIC_TOKEN = "12345678-1234-4234-8234-123456789abc";

  private static Document render(QuestionSubmitForm form) {
    var actor = new SessionPrincipal("fixture-user", UserRole.USER,
        AuthenticationContext.of("a".repeat(64)), Instant.EPOCH);
    var resolver = new FileTemplateResolver();
    resolver.setPrefix("src/schubert-nk-web/src/main/resources/templates/");
    resolver.setSuffix(".html");
    resolver.setCharacterEncoding("UTF-8");
    resolver.setCacheable(false);
    var engine = new SpringTemplateEngine();
    engine.setTemplateResolver(resolver);
    var servlet = new MockServletContext();
    var request = new MockHttpServletRequest(servlet);
    request.setRequestURI("/questions/new");
    var exchange = JakartaServletWebApplication.buildApplication(servlet)
        .buildExchange(request, new MockHttpServletResponse());
    var page = QuestionSubmitViewModel.redisplay(actor, form, "");
    return Jsoup.parse(engine.process("questions/new", new WebContext(exchange, Locale.JAPAN, Map.of("page", page))));
  }

  private static QuestionSubmitForm form(String question) {
    return QuestionSubmitForm.bind(Map.of("question", List.of(question),
        "operation_token", List.of(PUBLIC_TOKEN)));
  }

  @Test
  void requiredQuestionHasVisibleIndicatorAndExplicitLabelAssociation() {
    try (var form = form("質問")) {
      var dom = render(form);
      assertTrue(dom.select("label[for=question]").text().contains("質問"));
      assertTrue(dom.select("label[for=question]").text().contains("必須"));
      assertEquals(1, dom.select("textarea#question[name=question][required][rows=6]").size());
      assertEquals("post", dom.select("form.question-input").attr("method"));
      assertEquals("/questions/new", dom.select("form.question-input").attr("action"));
      assertEquals("送信", dom.select("form.question-input button[type=submit]").text());
      assertEquals(1, dom.select("script[src='/js/question-input-validation.js'][defer]").size());
      assertEquals("4096", dom.select("[data-question-remaining]").text());
    }
  }

  @Test
  void questionAndBoundaryRedisplayStayEscapedWithoutTrimmingOrTruncation() {
    for (String body : List.of(" <script>alert(1)</script>&", "e\u0301", "a".repeat(4096), "a".repeat(4097))) {
      try (var form = form(body)) {
        String expected = body.equals("e\u0301") ? "é" : body;
        var dom = render(form);
        assertEquals(expected, dom.select("textarea#question").getFirst().wholeText());
        assertEquals(body.length() <= 4096, form.isValid());
        assertEquals(0, dom.select("script:not([src]),img,[data-token],[data-operation-token],[data-session]").size());
        assertEquals(1, dom.select("input[type=hidden][name=operation_token]").size());
        assertEquals(PUBLIC_TOKEN, dom.select("input[name=operation_token]").val());
        assertFalse(dom.text().contains(PUBLIC_TOKEN));
        if (body.length() > 4096) {
          assertEquals("入力項目を確認してください。", dom.select(".field-error").text());
          assertEquals(List.of("#question"), dom.select(".validation-summary a").eachAttr("href"));
          assertThrows(IllegalArgumentException.class, form::toRequest);
        }
      }
    }
  }

  @Test
  void missingAndUnknownInputsProduceFixedDisplayErrorsWithoutRawReflection() {
    try (var form = QuestionSubmitForm.bind(Map.of("operation_token", List.of(PUBLIC_TOKEN),
        "unknown", List.of("never-display-this-value")))) {
      assertFalse(form.isValid());
      var dom = render(form);
      assertEquals("", dom.select("textarea#question").getFirst().wholeText());
      assertEquals("入力項目を確認してください。", dom.select(".field-error").text());
      assertEquals(2, dom.select(".validation-summary a[href='#question']").size());
      assertFalse(dom.outerHtml().contains("never-display-this-value"));
      assertThrows(IllegalArgumentException.class, form::toRequest);
    }
  }
}
