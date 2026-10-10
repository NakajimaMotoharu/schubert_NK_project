package dev.codex.schubert.nk.web.view;

import static org.junit.jupiter.api.Assertions.*;

import java.util.HashMap;
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

/** P016-21/UI224/SS313: literal closed state display fixtures, no controller/token registry. */
class NotificationDetailDisplayContractTest {
  private static Document render(String state, boolean deleted, Map<String, String> issues) {
    var values = new HashMap<String, Object>();
    values.put("id", 7);
    values.put("receiptId", "01PUBLICFIXTURE0123456789AB");
    values.put("state", state);
    values.put("stateLabel", Map.of("RECEIVED", "受付中", "PROCESSING", "処理中", "COMPLETED", "処理完了", "ERROR", "エラー", "CANCELLED", "取消済み").get(state));
    values.put("submittedAt", "2026-10-11 08:00:00");
    for (String name : List.of("startedAt", "completedAt", "errorAt", "cancelledAt")) values.put(name, "");
    values.put("deleted", deleted);
    values.put("question", " 質問<img> & 本文");
    values.put("answerAvailable", state.equals("COMPLETED") && !deleted);
    values.put("answer", "回答<script> & 本文");
    values.put("questionHref", "/questions/9");
    values.put("errorCode", "E-SYNTHETIC");
    values.put("userFacingError", "現在処理できません。");
    var page = Map.of("topBar", Map.of("brand", "schubert NK", "username", "fixture-user", "role", "USER"), "values", values);
    // Stale action is intentional: the display layer must still respect the closed state.
    var action = Map.of("fields", Map.of("id", 7, "operation_token", "12345678-1234-4234-8234-123456789abc", "confirm", false), "issues", issues);
    var resolver = new FileTemplateResolver();
    resolver.setPrefix("src/schubert-nk-web/src/main/resources/templates/");
    resolver.setSuffix(".html");
    resolver.setCharacterEncoding("UTF-8");
    resolver.setCacheable(false);
    var engine = new SpringTemplateEngine();
    engine.setTemplateResolver(resolver);
    var servlet = new MockServletContext();
    var request = new MockHttpServletRequest(servlet);
    request.setRequestURI("/notifications/7");
    var exchange = JakartaServletWebApplication.buildApplication(servlet).buildExchange(request, new MockHttpServletResponse());
    return Jsoup.parse(engine.process("notifications/detail", new WebContext(exchange, Locale.JAPAN,
        Map.of("page", page, "action", action, "notice", "", "_csrf", Map.of("parameterName", "_csrf", "token", "public-csrf-fixture")))));
  }

  @Test
  void onlyReceivedStateDisplaysCancelControlsEvenWithStaleAction() {
    for (String state : List.of("RECEIVED", "PROCESSING", "COMPLETED", "ERROR", "CANCELLED")) {
      var dom = render(state, false, Map.of());
      assertEquals(state.equals("RECEIVED") ? 1 : 0, dom.select("form.cancel-form").size(), state);
      assertEquals(state.equals("COMPLETED") ? 1 : 0, dom.select(".answer-body").size());
      assertEquals(state.equals("ERROR") ? 1 : 0, dom.select(".error-detail").size());
      assertEquals("/notifications", dom.select("a.back").attr("href"));
      assertEquals(0, dom.select("img,script,[data-token],[data-session]").size());
      assertEquals(" 質問<img> & 本文", dom.select(".question-body").getFirst().wholeText());
    }
  }

  @Test
  void receivedConfirmationShowsRequiredIndicatorAndResolvableSummary() {
    var dom = render("RECEIVED", false, Map.of("confirm", "確認してください。", "form", "入力項目を確認してください。"));
    assertEquals(1, dom.select("#notification-cancel-confirm[name=confirm][required]").size());
    assertTrue(dom.select("label[for=notification-cancel-confirm]").text().contains("必須"));
    assertEquals(2, dom.select(".operation-errors a").size());
    for (var anchor : dom.select(".operation-errors a")) assertEquals(1, dom.select(anchor.attr("href")).size());
    assertEquals("/notifications/7", dom.select("#notification-cancel-form").attr("action"));
    assertEquals("post", dom.select("#notification-cancel-form").attr("method"));
    assertEquals(1, dom.select("#notification-cancel-form input[name=_csrf][type=hidden]").size());
    assertFalse(dom.text().contains("public-csrf-fixture"));
  }

  @Test
  void deletedCompletedNoticeHidesBodiesAndAnswerNavigation() {
    var dom = render("COMPLETED", true, Map.of());
    assertEquals("質問・回答は削除済みです。", dom.select(".deleted").text());
    assertEquals(0, dom.select(".question-body,.answer-body,.question-detail,form.cancel-form").size());
  }
}
