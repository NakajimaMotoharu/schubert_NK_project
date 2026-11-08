package dev.codex.schubert.nk.web.view;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
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

/** PT-QST-DOM001..008/BUG2341/YKT2086; actual resource, independent UI221 root oracle. */
final class QuestionFormReturnResourcePortTest {
  private static final String VIEW_NEW = "questions/new";
  private static final String VIEW_ACCEPTED = "questions/accepted";
  private static final String HREF = "href";
  private static final String VALUE = "value";
  private static final String TEXTAREA = "#question";
  private static final String QUESTION_BODY = ".question-body";
  private static final String READER = "fixture-reader";
  private static final String USER = "USER";
  private static final String ADMIN = "ADMIN";
  private static final String RECEIPT = "10000000-0000-0000-0000-000000000001";
  private static final String JST = "2026-11-06 12:34:56";
  private static final String SYNTHETIC_OPERATION = "00000000-0000-0000-0000-000000000001";
  private static final String OPERATION_FIELD = "input[name=operation_token]";
  private static final String ESCAPED_BODY = "質問<&><script> 日本";
  private static final String ISSUE = "入力項目を確認してください。";

  private static Map<String, Object> topBar(String role) {
    return Map.of("username", READER, "role", role);
  }

  private static Map<String, Object> inputPage(
      String questionText, String role, String notice, Map<String, String> issues) {
    return Map.of(
        "topBar",
        topBar(role),
        "notice",
        notice,
        "issues",
        issues,
        "values",
        Map.of("operationToken", SYNTHETIC_OPERATION, "question", questionText));
  }

  private static Map<String, Object> receiptPage(String questionText) {
    return Map.of(
        "topBar",
        topBar(USER),
        "values",
        Map.of("receiptId", RECEIPT, "submittedAt", JST, "question", questionText));
  }

  private static Document render(String id, String template, Map<String, Object> page)
      throws Exception {
    var servlet = new MockServletContext();
    var req = new MockHttpServletRequest(servlet);
    req.setMethod("GET");
    req.setRequestURI(template.equals(VIEW_NEW) ? "/questions/new" : "/questions/accepted/fixture");
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
    var dom =
        Jsoup.parse(
            engine.process(template, new WebContext(exchange, Locale.JAPAN, Map.of("page", page))));
    assertTrue(
        dom.select("[th\\:text],[th\\:if],[th\\:replace],[th\\:each],[th\\:href]").isEmpty());
    var saved = dom.clone();
    saved.select(OPERATION_FIELD + ",input[name=_csrf]").attr(VALUE, "[REDACTED-SYNTHETIC]");
    String safe = saved.outerHtml();
    assertFalse(safe.contains(SYNTHETIC_OPERATION));
    Files.writeString(
        Path.of(System.getProperty("owned.output"), id + ".html"),
        safe,
        StandardOpenOption.CREATE_NEW);
    return dom;
  }

  private static String actualText(Document document, String selector) {
    var elements = document.select(selector);
    assertEquals(1, elements.size());
    return elements.getFirst().wholeText();
  }

  @Test
  void newPageMenuHrefUsesApprovedCanonicalPath() throws Exception {
    var d = render("QRETURN001", VIEW_NEW, inputPage("", USER, "", Map.of()));
    assertEquals("メニュー", d.select("main > a").text());
    assertEquals("/", d.select("main > a").attr(HREF));
  }

  @Test
  void acceptedPageNavigationUsesApprovedTargets() throws Exception {
    var d = render("QRETURN002", VIEW_ACCEPTED, receiptPage("質問"));
    assertEquals(List.of("通知を確認", "続けて質問", "メニュー"), d.select("main > nav a").eachText());
    assertEquals(
        List.of("/notifications", "/questions/new", "/"), d.select("main > nav a").eachAttr(HREF));
  }

  @Test
  void emptyInputHasExplicitFormAndScriptContract() throws Exception {
    var d = render("QRETURN003", VIEW_NEW, inputPage("", USER, "", Map.of()));
    assertEquals("質問要求", d.title());
    assertEquals("質問要求", d.select("h1").text());
    assertEquals(1, d.select("form.question-input[method=post][action='/questions/new']").size());
    assertEquals(SYNTHETIC_OPERATION, d.select(OPERATION_FIELD).attr(VALUE));
    assertEquals("", actualText(d, TEXTAREA));
    assertTrue(d.select(TEXTAREA).hasAttr("required"));
    assertEquals("6", d.select(TEXTAREA).attr("rows"));
    assertEquals("質問", d.select("label[for=question]").text());
    assertEquals("4096", d.select("[data-question-remaining]").text());
    assertEquals(1, d.select("script[src='/js/question-input-validation.js'][defer]").size());
    assertTrue(d.select(".retry-notice,.validation-summary,.field-error").isEmpty());
  }

  @Test
  void noticeValidationAndQuestionTextEscapeWithoutMarkup() throws Exception {
    String notice = "再操作<&>を確認";
    var d =
        render(
            "QRETURN004",
            VIEW_NEW,
            inputPage(ESCAPED_BODY, USER, notice, Map.of("question", ISSUE)));
    assertEquals(notice, d.select(".retry-notice").text());
    assertEquals(ISSUE, d.select(".validation-summary a").text());
    assertEquals("#question", d.select(".validation-summary a").attr(HREF));
    assertEquals(ISSUE, d.select(".field-error").text());
    assertEquals(ESCAPED_BODY, actualText(d, TEXTAREA));
    assertTrue(d.select("script:not([src]),img,[onerror]").isEmpty());
  }

  @Test
  void userAndAdminDisplayValuesStaySeparate() throws Exception {
    int index = 0;
    for (String role : List.of(USER, ADMIN)) {
      var d = render("QRETURN005-" + index, VIEW_NEW, inputPage("質問", role, "", Map.of()));
      index++;
      assertEquals(READER, d.select(".login-user").text());
      assertEquals(role, d.select(".login-role").text());
      assertEquals(
          List.of("/", "/notifications"), d.select("nav[aria-label=共通ナビゲーション] a").eachAttr(HREF));
    }
  }

  @Test
  void acceptedReadonlyDataUsesExplicitReceiptTimeAndEscapedBody() throws Exception {
    var d = render("QRETURN006", VIEW_ACCEPTED, receiptPage(ESCAPED_BODY));
    assertEquals("質問受付完了", d.title());
    assertEquals("質問を受け付けました。", d.select(".accepted-message").text());
    assertEquals(RECEIPT, d.select(".receipt").text());
    assertEquals(JST, d.select(".submitted-at").text());
    assertEquals(ESCAPED_BODY, d.select(QUESTION_BODY).text());
    assertTrue(d.select("main > form," + OPERATION_FIELD + ",script").isEmpty());
  }

  @Test
  void fourThousandNinetySixByteBodyIsNotTruncatedByEitherTemplate() throws Exception {
    String questionText = "a".repeat(4096);
    assertEquals(4096, questionText.getBytes(StandardCharsets.UTF_8).length);
    var input = render("QRETURN007-new", VIEW_NEW, inputPage(questionText, USER, "", Map.of()));
    var accepted = render("QRETURN007-accepted", VIEW_ACCEPTED, receiptPage(questionText));
    assertEquals(questionText, actualText(input, TEXTAREA));
    assertEquals(questionText, accepted.select(QUESTION_BODY).text());
  }

  @Test
  void concurrentInputAndAcceptedPagesKeepValuesSeparate() throws Exception {
    var pool = Executors.newFixedThreadPool(2);
    try {
      var jobs = new ArrayList<Future<String>>();
      for (int i = 0; i < 8; i++) {
        int index = i;
        jobs.add(
            pool.submit(
                () -> {
                  String body = "question-" + index;
                  boolean input = index % 2 == 0;
                  var d =
                      render(
                          "QRETURN008-" + index,
                          input ? VIEW_NEW : VIEW_ACCEPTED,
                          input ? inputPage(body, USER, "", Map.of()) : receiptPage(body));
                  return input ? actualText(d, TEXTAREA) : d.select(QUESTION_BODY).text();
                }));
      }
      for (int i = 0; i < 8; i++)
        assertEquals("question-" + i, jobs.get(i).get(10, TimeUnit.SECONDS));
    } finally {
      pool.shutdownNow();
      assertTrue(pool.awaitTermination(10, TimeUnit.SECONDS));
    }
  }
}
