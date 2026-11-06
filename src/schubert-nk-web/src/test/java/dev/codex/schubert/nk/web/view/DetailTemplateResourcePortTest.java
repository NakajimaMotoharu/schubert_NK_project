package dev.codex.schubert.nk.web.view;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.util.HashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.UUID;
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

/** UI236/SS313332/PT-WEB-DDOM001..014, local exact templates, synthetic form fields only. */
final class DetailTemplateResourcePortTest {
  private static final String KEY_USERNAME = "username";
  private static final String CONFIRM_ERROR = "確認してください <b>再入力</b>";
  private static final String QUESTION_PATH = "/questions/12";
  private static final String STATE_SELECTOR = ".state";
  private static final String NOTICE_TEXT = "表示 <b>通知</b>";
  private static final String NOTICE_SELECTOR = ".operation-notice";
  private static final int NOTICE_TEXT_INDEX = 2;

  private static final String QUESTIONS = "questions/detail";
  private static final String NOTIFICATIONS = "notifications/detail";
  private static final String READER = "reader";
  private static final String BODY = "<img src=x onerror='example'> & 質問";
  private static final String ANSWER = "<b>回答</b> & 本文";
  private static final String RECEIPT = "0".repeat(26);
  private static final String JST = "2026-11-01 09:00:00";
  private static final String JST_NEXT = "2026-11-01 09:00:01";
  private static final String UNANSWERED = "UNANSWERED";
  private static final String ANSWERED = "ANSWERED";
  private static final String ERROR = "ERROR";
  private static final String RECEIVED = "RECEIVED";
  private static final String PROCESSING = "PROCESSING";
  private static final String COMPLETED = "COMPLETED";
  private static final String CANCELLED = "CANCELLED";
  private static final String KEY_PAGE = "page";
  private static final String KEY_VALUES = "values";
  private static final String KEY_ACTION = "action";
  private static final String KEY_NOTICE = "notice";
  private static final String KEY_STATE = "state";
  private static final String KEY_ANSWER = "answer";
  private static final String KEY_CONFIRM = "confirm";
  private static final String ATTR_VALUE = "value";
  private static final String ATTR_HREF = "href";
  private static final String ATTR_CHECKED = "checked";
  private static final String ATTR_ACTION = "action";
  private static final String QUESTION_BODY = ".question-body";
  private static final String ANSWER_BODY = ".answer-body";
  private static final String SYNTHETIC_TOKEN = new UUID(0, 1).toString();
  private static final String SYNTHETIC_CSRF = "synthetic-noncredential-csrf";
  private static final String SENSITIVE_INPUTS = "input[name=operation_token],input[name=_csrf]";
  private static final String REDACTED = "[REDACTED-SYNTHETIC]";

  private static Map<String, Object> question(boolean admin, String state, String answer) {
    var v =
        Map.ofEntries(
            Map.entry("id", 12L),
            Map.entry("receiptId", RECEIPT),
            Map.entry("admin", admin),
            Map.entry(KEY_USERNAME, READER),
            Map.entry(KEY_STATE, state),
            Map.entry(
                "stateLabel", Map.of(UNANSWERED, "未回答", ANSWERED, "回答済み", ERROR, "エラー").get(state)),
            Map.entry("submittedAt", JST),
            Map.entry("answeredAt", state.equals(ANSWERED) ? JST_NEXT : ""),
            Map.entry("question", BODY),
            Map.entry("summary", BODY),
            Map.entry(KEY_ANSWER, answer),
            Map.entry("answerAvailable", state.equals(ANSWERED)));
    return Map.of(
        "topBar", Map.of(KEY_USERNAME, READER, "role", admin ? "ADMIN" : "USER"), KEY_VALUES, v);
  }

  private static Map<String, Object> notification(String state, boolean deleted, String answer) {
    var v =
        Map.ofEntries(
            Map.entry("id", 12L),
            Map.entry("receiptId", RECEIPT),
            Map.entry(KEY_STATE, state),
            Map.entry(
                "stateLabel",
                Map.of(
                        RECEIVED,
                        "受付中",
                        PROCESSING,
                        "処理中",
                        COMPLETED,
                        "処理完了",
                        ERROR,
                        "エラー",
                        CANCELLED,
                        "取消済み")
                    .get(state)),
            Map.entry("submittedAt", JST),
            Map.entry(
                "startedAt", List.of(PROCESSING, COMPLETED, ERROR).contains(state) ? JST : ""),
            Map.entry("completedAt", state.equals(COMPLETED) ? JST_NEXT : ""),
            Map.entry("errorAt", state.equals(ERROR) ? JST_NEXT : ""),
            Map.entry("cancelledAt", state.equals(CANCELLED) ? JST_NEXT : ""),
            Map.entry("deleted", deleted),
            Map.entry("question", deleted ? "" : BODY),
            Map.entry(KEY_ANSWER, answer),
            Map.entry("answerAvailable", state.equals(COMPLETED) && !deleted),
            Map.entry("questionHref", state.equals(COMPLETED) && !deleted ? "/questions/27" : ""),
            Map.entry("errorCode", state.equals(ERROR) ? "SYSTEM_UNAVAIL" : ""),
            Map.entry("userFacingError", state.equals(ERROR) ? "処理を完了できませんでした。" : ""));
    return Map.of("topBar", Map.of(KEY_USERNAME, READER, "role", "USER"), KEY_VALUES, v);
  }

  private static Map<String, Object> action(boolean confirmed, boolean invalid) {
    return Map.of(
        "fields",
        Map.of("id", "12", "operation_token", SYNTHETIC_TOKEN, KEY_CONFIRM, confirmed),
        "issues",
        invalid ? Map.of(KEY_CONFIRM, CONFIRM_ERROR) : Map.of());
  }

  private static Document render(
      String id, String template, Map<String, Object> page, Map<String, Object> extras)
      throws Exception {
    var servlet = new MockServletContext();
    var req = new MockHttpServletRequest(servlet);
    req.setMethod("GET");
    req.setRequestURI(template.equals(QUESTIONS) ? QUESTION_PATH : "/notifications/12");
    var exchange =
        JakartaServletWebApplication.buildApplication(servlet)
            .buildExchange(req, new MockHttpServletResponse());
    var resolver = new ClassLoaderTemplateResolver();
    resolver.setPrefix("templates/");
    resolver.setSuffix(".html");
    resolver.setTemplateMode("HTML");
    resolver.setCharacterEncoding("UTF-8");
    resolver.setCacheable(false);
    var engine = new SpringTemplateEngine();
    engine.setTemplateResolver(resolver);
    var context = new HashMap<String, Object>(extras);
    context.put(KEY_PAGE, page);
    if (extras.containsKey(KEY_ACTION))
      context.put("_csrf", Map.of("parameterName", "_csrf", "token", SYNTHETIC_CSRF));
    var dom =
        Jsoup.parse(engine.process(template, new WebContext(exchange, Locale.JAPAN, context)));
    assertTrue(dom.select("[th\\:text],[th\\:if],[th\\:replace]").isEmpty());
    var saved = dom.clone();
    saved.select(SENSITIVE_INPUTS).attr(ATTR_VALUE, REDACTED);
    assertTrue(
        saved.select(SENSITIVE_INPUTS).eachAttr(ATTR_VALUE).stream().allMatch(REDACTED::equals));
    String safe = saved.outerHtml();
    assertFalse(safe.contains(SYNTHETIC_TOKEN));
    assertFalse(safe.contains(SYNTHETIC_CSRF));
    Files.writeString(
        Path.of(System.getProperty("owned.output"), id + ".html"),
        safe,
        StandardOpenOption.CREATE_NEW);
    return dom;
  }

  private static Document render(String id, String template, Map<String, Object> page)
      throws Exception {
    return render(id, template, page, Map.of());
  }

  private static void form(
      Document d, String selector, String path, String operation, boolean checked) {
    assertEquals(path, d.select(selector).attr(ATTR_ACTION));
    assertEquals("post", d.select(selector).attr("method"));
    assertEquals(operation, d.select(selector + " input[name=operation]").attr(ATTR_VALUE));
    assertEquals("12", d.select(selector + " input[name=id]").attr(ATTR_VALUE));
    assertEquals(
        SYNTHETIC_TOKEN, d.select(selector + " input[name=operation_token]").attr(ATTR_VALUE));
    assertEquals(SYNTHETIC_CSRF, d.select(selector + " input[name=_csrf]").attr(ATTR_VALUE));
    assertEquals(checked, d.select(selector + " input[name=confirm]").hasAttr(ATTR_CHECKED));
    assertTrue(d.select(selector + " input[name=confirm]").hasAttr("required"));
  }

  @Test
  void questionUserUnansweredReadOnly() throws Exception {
    var d = render("DDOM001", QUESTIONS, question(false, UNANSWERED, ""));
    assertEquals("質問回答明細", d.title());
    assertEquals(RECEIPT, d.select(".receipt").text());
    assertEquals("未回答", d.select(STATE_SELECTOR).text());
    assertEquals(BODY, d.select(QUESTION_BODY).text());
    assertTrue(
        d.select(".owner," + ANSWER_BODY + ",.answered-at,#delete-confirm,.operation-notice")
            .isEmpty());
    assertTrue(d.select("img,[onerror],script:not([src])").isEmpty());
  }

  @Test
  void questionAdminEmptyAnswer() throws Exception {
    var d = render("DDOM002", QUESTIONS, question(true, ANSWERED, ""));
    assertEquals(READER, d.select(".owner").text());
    assertEquals("（空の回答）", d.select(ANSWER_BODY).text());
    assertEquals("回答済み", d.select(STATE_SELECTOR).text());
    assertEquals(JST_NEXT, d.select(".answered-at").text());
  }

  @Test
  void questionAnswerEscapesText() throws Exception {
    var d = render("DDOM003", QUESTIONS, question(false, ANSWERED, ANSWER));
    assertEquals(ANSWER, d.select(ANSWER_BODY).text());
    assertTrue(d.select(ANSWER_BODY + " b,img,[onerror]").isEmpty());
  }

  @Test
  void questionErrorHidesAnswer() throws Exception {
    var d = render("DDOM004", QUESTIONS, question(false, ERROR, ""));
    assertEquals("エラー", d.select(STATE_SELECTOR).text());
    assertTrue(d.select(ANSWER_BODY + ",.answered-at").isEmpty());
  }

  @Test
  void questionConfirmationUncheckedAndErrorsEscape() throws Exception {
    var d =
        render(
            "DDOM005",
            QUESTIONS,
            question(false, UNANSWERED, ""),
            Map.of(KEY_ACTION, action(false, true)));
    form(d, ".delete-form", QUESTION_PATH, "DELETE", false);
    assertEquals(CONFIRM_ERROR, d.select(".operation-errors p").text());
    assertTrue(d.select(".operation-errors b").isEmpty());
    assertEquals(BODY, d.select(".delete-summary").text());
  }

  @Test
  void questionConfirmationCheckedAndNotice() throws Exception {
    var d =
        render(
            "DDOM006",
            QUESTIONS,
            question(false, UNANSWERED, ""),
            Map.of(KEY_ACTION, action(true, false), KEY_NOTICE, NOTICE_TEXT));
    form(d, ".delete-form", QUESTION_PATH, "DELETE", true);
    assertEquals(NOTICE_TEXT, d.select(NOTICE_SELECTOR).text());
    assertTrue(d.select(".operation-notice b,.operation-errors p").isEmpty());
  }

  @Test
  void notificationReceivedAndProcessingTimestamps() throws Exception {
    for (String state : List.of(RECEIVED, PROCESSING)) {
      var d = render("DDOM007-" + state, NOTIFICATIONS, notification(state, false, ""));
      assertEquals("通知明細", d.title());
      assertEquals(BODY, d.select(QUESTION_BODY).text());
      assertEquals(state.equals(RECEIVED) ? "受付中" : "処理中", d.select(STATE_SELECTOR).text());
      assertEquals(state.equals(PROCESSING) ? JST : "", d.select(".started-at").text());
      assertTrue(
          d.select(ANSWER_BODY + ",.completed-at,.error-at,.cancelled-at,.cancel-confirm,.deleted")
              .isEmpty());
    }
  }

  @Test
  void notificationCompletedAnswersAndLink() throws Exception {
    for (String answer : List.of("", ANSWER)) {
      var d =
          render(
              "DDOM008-" + (answer.isEmpty() ? "EMPTY" : "TEXT"),
              NOTIFICATIONS,
              notification(COMPLETED, false, answer));
      assertEquals("処理完了", d.select(STATE_SELECTOR).text());
      assertEquals(JST_NEXT, d.select(".completed-at").text());
      assertEquals(answer.isEmpty() ? "（空の回答）" : ANSWER, d.select(ANSWER_BODY).text());
      assertEquals("/questions/27", d.select("a.question-detail").attr(ATTR_HREF));
      assertTrue(d.select(ANSWER_BODY + " b,img,[onerror],.error-at,.cancelled-at").isEmpty());
    }
  }

  @Test
  void notificationErrorFields() throws Exception {
    var d = render("DDOM009", NOTIFICATIONS, notification(ERROR, false, ""));
    assertEquals(JST_NEXT, d.select(".error-at").text());
    assertEquals("SYSTEM_UNAVAIL", d.select(".error-code").text());
    assertEquals("処理を完了できませんでした。", d.select(".user-facing-error").text());
    assertTrue(d.select(ANSWER_BODY + ",a.question-detail,.completed-at,.cancelled-at").isEmpty());
  }

  @Test
  void notificationCancelledFields() throws Exception {
    var d = render("DDOM010", NOTIFICATIONS, notification(CANCELLED, false, ""));
    assertEquals("取消済み", d.select(STATE_SELECTOR).text());
    assertEquals(JST_NEXT, d.select(".cancelled-at").text());
    assertTrue(
        d.select(ANSWER_BODY + ",.started-at,.completed-at,.error-at,.error-detail").isEmpty());
  }

  @Test
  void notificationDeletedMasksBodiesAndAnswerLink() throws Exception {
    var d = render("DDOM011", NOTIFICATIONS, notification(COMPLETED, true, ""));
    assertEquals("質問・回答は削除済みです。", d.select(".deleted").text());
    assertTrue(
        d.select(QUESTION_BODY + "," + ANSWER_BODY + ",a.question-detail,.error-detail").isEmpty());
  }

  @Test
  void notificationConfirmationBothValues() throws Exception {
    for (boolean checked : List.of(false, true)) {
      var d =
          render(
              "DDOM012-" + checked,
              NOTIFICATIONS,
              notification(RECEIVED, false, ""),
              Map.of(KEY_ACTION, action(checked, !checked)));
      form(d, ".cancel-form", "/notifications/12", "CANCEL", checked);
      assertEquals(checked ? "" : CONFIRM_ERROR, d.select(".operation-errors p").text());
      assertTrue(d.select(".operation-errors b").isEmpty());
    }
  }

  @Test
  void optionalNoticesNullEmptyAndText() throws Exception {
    for (String template : List.of(QUESTIONS, NOTIFICATIONS))
      for (int i = 0; i < 3; i++) {
        var extras = new HashMap<String, Object>();
        extras.put(KEY_NOTICE, i == 0 ? null : i == 1 ? "" : NOTICE_TEXT);
        var page =
            template.equals(QUESTIONS)
                ? question(false, UNANSWERED, "")
                : notification(RECEIVED, false, "");
        var d =
            render(
                "DDOM013-" + (template.equals(QUESTIONS) ? "Q" : "N") + i, template, page, extras);
        assertEquals(i == 2 ? 1 : 0, d.select(NOTICE_SELECTOR).size());
        if (i == NOTICE_TEXT_INDEX) assertEquals(NOTICE_TEXT, d.select(NOTICE_SELECTOR).text());
        assertTrue(d.select(".operation-notice b").isEmpty());
      }
  }

  @Test
  void backLinksAndDeferredOperationScript() throws Exception {
    for (String template : List.of(QUESTIONS, NOTIFICATIONS)) {
      var d =
          render(
              "DDOM014-" + (template.equals(QUESTIONS) ? "Q" : "N"),
              template,
              template.equals(QUESTIONS)
                  ? question(false, UNANSWERED, "")
                  : notification(RECEIVED, false, ""));
      assertEquals(
          template.equals(QUESTIONS) ? "/questions" : "/notifications",
          d.select("a.back").attr(ATTR_HREF));
      assertEquals(1, d.select("script[src='/js/operation-post-submit.js'][defer]").size());
      assertTrue(d.select("script:not([src]),img,[onerror]").isEmpty());
    }
  }
}
