package dev.codex.schubert.nk.web.view;

import static org.junit.jupiter.api.Assertions.*;

import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.layout.question.QuestionDetailResponseData;
import dev.codex.schubert.nk.protocol.layout.semantic.AnswerState;
import dev.codex.schubert.nk.protocol.layout.semantic.QuestionId;
import dev.codex.schubert.nk.protocol.layout.semantic.UserRole;
import dev.codex.schubert.nk.web.session.SessionPrincipal;
import java.time.Instant;
import java.util.HashMap;
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

/** P016-23/UI224/SS313: typed pure owner display projection and request-only delete fixture. */
class QuestionDetailDisplayContractTest {
  private static QuestionDetailResponseData data(String answer) {
    return new QuestionDetailResponseData(new QuestionId(9), "01ARZ3NDEKTSV4RRFFQ69G5FAV", "fixture-owner",
        AnswerState.ANSWERED, " 質問<img> &", Optional.of(answer), Instant.EPOCH, Optional.of(Instant.EPOCH));
  }

  private static SessionPrincipal actor(UserRole role, String username) {
    return new SessionPrincipal(username, role, AuthenticationContext.of("a".repeat(64)), Instant.EPOCH);
  }

  private static Document render(UserRole role, String answer, boolean showAction, Map<String, String> issues) {
    var page = QuestionDetailViewModel.from(actor(role, role == UserRole.USER ? "fixture-owner" : "fixture-admin"), new QuestionId(9), data(answer));
    var variables = new HashMap<String, Object>();
    variables.put("page", page);
    variables.put("notice", "");
    variables.put("_csrf", Map.of("parameterName", "_csrf", "token", "public-csrf-fixture"));
    if (showAction) variables.put("action", Map.of("fields", Map.of("id", 9,
        "operation_token", "12345678-1234-4234-8234-123456789abc", "confirm", false), "issues", issues));
    var resolver = new FileTemplateResolver();
    resolver.setPrefix("src/schubert-nk-web/src/main/resources/templates/");
    resolver.setSuffix(".html");
    resolver.setCharacterEncoding("UTF-8");
    resolver.setCacheable(false);
    var engine = new SpringTemplateEngine();
    engine.setTemplateResolver(resolver);
    var servlet = new MockServletContext();
    var request = new MockHttpServletRequest(servlet);
    request.setRequestURI("/questions/9");
    var exchange = JakartaServletWebApplication.buildApplication(servlet).buildExchange(request, new MockHttpServletResponse());
    return Jsoup.parse(engine.process("questions/detail", new WebContext(exchange, Locale.JAPAN, variables)));
  }

  @Test
  void deleteConfirmationHasVisibleRequiredIndicatorAndResolvableErrors() {
    var dom = render(UserRole.USER, "回答<script>", true,
        Map.of("confirm", "確認してください。", "form", "入力項目を確認してください。"));
    assertEquals(1, dom.select("#question-delete-confirm[name=confirm][required]").size());
    assertTrue(dom.select("label[for=question-delete-confirm]").text().contains("必須"));
    assertEquals(2, dom.select(".operation-errors a").size());
    for (var anchor : dom.select(".operation-errors a")) assertEquals(1, dom.select(anchor.attr("href")).size());
    assertEquals("/questions/9", dom.select("#question-delete-form").attr("action"));
    assertEquals("post", dom.select("#question-delete-form").attr("method"));
    assertEquals(1, dom.select("#question-delete-form input[name=_csrf][type=hidden]").size());
    assertFalse(dom.text().contains("public-csrf-fixture"));
  }

  @Test
  void typedOwnerRoleProjectionEscapesBodiesAndRespectsSuppliedAction() {
    for (UserRole role : UserRole.values()) {
      var dom = render(role, "回答<script>", false, Map.of());
      assertEquals(role == UserRole.ADMIN ? 1 : 0, dom.select(".owner").size());
      assertEquals(" 質問<img> &", dom.select(".question-body").getFirst().wholeText());
      assertEquals("回答<script>", dom.select(".answer-body").text());
      assertEquals(0, dom.select("img,script,[data-token],[data-session],form.delete-form").size());
      assertEquals("/questions", dom.select("a.back").attr("href"));
    }
    assertThrows(IllegalArgumentException.class, () -> QuestionDetailViewModel.from(
        actor(UserRole.USER, "other-user"), new QuestionId(9), data("回答")));
  }

  @Test
  void answeredEmptyBodyUsesApprovedPlaceholder() {
    var dom = render(UserRole.USER, "", false, Map.of());
    assertEquals("（空の回答）", dom.select(".answer-body").text());
    assertEquals("1970-01-01 09:00:00", dom.select(".answered-at").text());
  }
}
