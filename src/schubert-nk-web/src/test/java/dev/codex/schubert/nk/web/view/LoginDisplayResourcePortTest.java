package dev.codex.schubert.nk.web.view;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

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

/** PT-LOGIN-DOM001..008; QA055 locked branch held; template-only GET display, no auth or POST. */
final class LoginDisplayResourcePortTest {
  private static final String ERROR = "error";
  private static final String LOGOUT = "logout";
  private static final String FAILURE_MESSAGE = "ユーザー名またはパスワードが正しくありません。";
  private static final String LOGOUT_MESSAGE = "ログアウトしました。";
  private static final String MESSAGES = ".login-message";
  private static final String USERNAME = "#login-username";
  private static final String PASSWORD = "#login-password";
  private static final String VALUE = "value";
  private static final String MARKER = "public-unissued-fixture-marker";

  private static Document render(String id, Map<String, String[]> parameters) throws Exception {
    assertFalse(parameters.containsKey("locked"), "QA055 locked oracle remains held");
    var servlet = new MockServletContext();
    var req = new MockHttpServletRequest(servlet);
    req.setMethod("GET");
    req.setRequestURI("/login");
    parameters.forEach(req::addParameter);
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
        Jsoup.parse(engine.process("login", new WebContext(exchange, Locale.JAPAN, Map.of())));
    assertTrue(dom.select("[th\\:text],[th\\:if],[th\\:action]").isEmpty());
    assertEquals("", dom.select(PASSWORD).attr(VALUE));
    assertFalse(dom.outerHtml().contains(MARKER));
    var saved = dom.clone();
    saved.select("input[name=_csrf]").attr(VALUE, "[REDACTED-SYNTHETIC]");
    Files.writeString(
        Path.of(System.getProperty("owned.output"), id + ".html"),
        saved.outerHtml(),
        StandardOpenOption.CREATE_NEW);
    return dom;
  }

  @Test
  void initialPageKeepsApprovedBrandAndNoMessages() throws Exception {
    var d = render("LOGINDOM001", Map.of());
    assertEquals("schubert NK - ログイン", d.title());
    assertEquals("schubert NK", d.select("h1").text());
    assertTrue(d.select(MESSAGES).isEmpty());
    assertEquals("ユーザー名とパスワードを入力してください。", d.select(".login-description").text());
  }

  @Test
  void errorAndLogoutUseFixedMessagesNotParameterValues() throws Exception {
    var error = render("LOGINDOM002-error", Map.of(ERROR, new String[] {MARKER}));
    assertEquals(FAILURE_MESSAGE, error.select(MESSAGES).text());
    assertEquals(1, error.select(".login-message.error").size());
    assertTrue(error.select(".login-message.success").isEmpty());
    var logout = render("LOGINDOM002-logout", Map.of(LOGOUT, new String[] {MARKER}));
    assertEquals(LOGOUT_MESSAGE, logout.select(MESSAGES).text());
    assertEquals(1, logout.select(".login-message.success").size());
    assertTrue(logout.select(".login-message.error").isEmpty());
  }

  @Test
  void independentErrorAndLogoutConditionsDoNotConsumeEachOther() throws Exception {
    var d = render("LOGINDOM003", Map.of(ERROR, new String[] {""}, LOGOUT, new String[] {""}));
    assertEquals(List.of(FAILURE_MESSAGE, LOGOUT_MESSAGE), d.select(MESSAGES).eachText());
    assertEquals(1, d.select(".login-message.error").size());
    assertEquals(1, d.select(".login-message.success").size());
  }

  @Test
  void unrecognizedParametersNeverBecomeMarkupOrMessages() throws Exception {
    var d = render("LOGINDOM004", Map.of("unknown", new String[] {MARKER + "<img onerror=bad>"}));
    assertTrue(d.select(MESSAGES).isEmpty());
    assertTrue(d.select("img,script,[onerror]").isEmpty());
  }

  @Test
  void formLabelsInputMetadataAndStaticAssetsAreExplicit() throws Exception {
    var d = render("LOGINDOM005", Map.of());
    assertEquals("ja", d.select("html").attr("lang"));
    assertEquals("utf-8", d.select("meta[charset]").attr("charset"));
    assertEquals(
        "width=device-width, initial-scale=1", d.select("meta[name=viewport]").attr("content"));
    assertEquals("/css/schubert.css", d.select("link[rel=stylesheet]").attr("href"));
    assertEquals("login-title", d.select("section.login-card").attr("aria-labelledby"));
    assertEquals(1, d.select("form.login-form[action=/login][method=post]").size());
    assertEquals("ユーザー名", d.select("label[for=login-username]").text());
    assertEquals("パスワード", d.select("label[for=login-password]").text());
    assertEquals("username", d.select(USERNAME).attr("name"));
    assertEquals("text", d.select(USERNAME).attr("type"));
    assertEquals("username", d.select(USERNAME).attr("autocomplete"));
    assertTrue(d.select(USERNAME).hasAttr("required"));
    assertTrue(d.select(USERNAME).hasAttr("autofocus"));
    assertEquals("password", d.select(PASSWORD).attr("name"));
    assertEquals("password", d.select(PASSWORD).attr("type"));
    assertEquals("current-password", d.select(PASSWORD).attr("autocomplete"));
    assertTrue(d.select(PASSWORD).hasAttr("required"));
    assertEquals("ログイン", d.select("button[type=submit]").text());
  }

  @Test
  void submittedLookingQueryValuesNeverRefillUsernameOrPassword() throws Exception {
    var d =
        render(
            "LOGINDOM006",
            Map.of("username", new String[] {MARKER}, "password", new String[] {MARKER}));
    assertEquals("", d.select(USERNAME).attr(VALUE));
    assertEquals("", d.select(PASSWORD).attr(VALUE));
    assertTrue(d.select(MESSAGES).isEmpty());
  }

  @Test
  void errorFlagPresenceWorksWithEmptyFalseAndMultipleValues() throws Exception {
    List<String[]> values =
        List.of(new String[] {""}, new String[] {"false"}, new String[] {"true", "false"});
    for (int i = 0; i < values.size(); i++) {
      var d = render("LOGINDOM007-" + i, Map.of(ERROR, values.get(i)));
      assertEquals(FAILURE_MESSAGE, d.select(MESSAGES).text());
    }
  }

  @Test
  void eightConcurrentRenderingsKeepParameterMessagesSeparate() throws Exception {
    var pool = Executors.newFixedThreadPool(2);
    try {
      var jobs = new ArrayList<Future<List<String>>>();
      for (int i = 0; i < 8; i++) {
        int index = i;
        jobs.add(
            pool.submit(
                () -> {
                  Map<String, String[]> query =
                      switch (index % 3) {
                        case 0 -> Map.of();
                        case 1 -> Map.of(ERROR, new String[] {""});
                        default -> Map.of(LOGOUT, new String[] {""});
                      };
                  return render("LOGINDOM008-" + index, query).select(MESSAGES).eachText();
                }));
      }
      for (int i = 0; i < 8; i++) {
        List<String> expected =
            switch (i % 3) {
              case 0 -> List.of();
              case 1 -> List.of(FAILURE_MESSAGE);
              default -> List.of(LOGOUT_MESSAGE);
            };
        assertEquals(expected, jobs.get(i).get(10, TimeUnit.SECONDS));
      }
    } finally {
      pool.shutdownNow();
      assertTrue(pool.awaitTermination(10, TimeUnit.SECONDS));
    }
  }
}
