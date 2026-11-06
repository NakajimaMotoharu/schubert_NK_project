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

/** PT-LOCK-DOM001..004; QA055 approved fixed text; owned template GET only, no auth or POST. */
final class LockedLoginDisplayResourcePortTest {
  private static final String LOCKED = "locked";
  private static final String LOCK_MESSAGE = "ログイン試行回数が上限に達しました。15分ほど待ってから再度お試しください。";
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
  void approvedLockedMessageDependsOnFlagPresenceNotItsValues() throws Exception {
    List<String[]> flags =
        List.of(new String[] {""}, new String[] {"false"}, new String[] {MARKER, "false"});
    for (int index = 0; index < flags.size(); index++) {
      var dom = render("LOCKDOM001-" + index, Map.of(LOCKED, flags.get(index)));
      assertEquals(List.of(LOCK_MESSAGE), dom.select(MESSAGES).eachText());
      assertEquals(1, dom.select(".login-message.error").size());
      assertEquals("", dom.select(PASSWORD).attr(VALUE));
      assertEquals("/login", dom.select("form.log-in-form, form[method=post]").attr("action"));
    }
  }

  @Test
  void independentErrorLockedLogoutFlagsKeepCurrentOrderAndFixedText() throws Exception {
    for (int mask = 0; mask < 4; mask++) {
      var query = new java.util.HashMap<String, String[]>();
      query.put(LOCKED, new String[] {MARKER});
      var expected = new ArrayList<String>();
      if ((mask & 1) != 0) {
        query.put(ERROR, new String[] {MARKER});
        expected.add(FAILURE_MESSAGE);
      }
      expected.add(LOCK_MESSAGE);
      if ((mask & 2) != 0) {
        query.put(LOGOUT, new String[] {MARKER});
        expected.add(LOGOUT_MESSAGE);
      }
      var dom = render("LOCKDOM002-" + mask, query);
      assertEquals(expected, dom.select(MESSAGES).eachText());
      assertTrue(dom.select("script,[onerror],[onload]").isEmpty());
    }
  }

  @Test
  void allegedRemainingSecondsAndCredentialsNeverBecomeDynamicDisplay() throws Exception {
    var seconds = List.of("0", "1", "899", "900", "99999", MARKER + "<img onerror=bad>");
    for (int index = 0; index < seconds.size(); index++) {
      var dom =
          render(
              "LOCKDOM003-" + index,
              Map.of(
                  LOCKED,
                  new String[] {""},
                  "remaining_seconds",
                  new String[] {seconds.get(index)},
                  "retry_after",
                  new String[] {seconds.get(index)},
                  "username",
                  new String[] {MARKER},
                  "password",
                  new String[] {MARKER}));
      assertEquals(List.of(LOCK_MESSAGE), dom.select(MESSAGES).eachText());
      assertTrue(
          dom.select("input[name=remaining_seconds],input[name=retry_after],script,img").isEmpty());
      assertEquals("", dom.select(USERNAME).attr(VALUE));
      assertEquals("", dom.select(PASSWORD).attr(VALUE));
      assertFalse(dom.text().contains("残り"));
    }
  }

  @Test
  void parallelLockedAndUnlockedRenderingsKeepTheirOwnFlags() throws Exception {
    try (var pool = Executors.newFixedThreadPool(2)) {
      var jobs = new ArrayList<Future<List<String>>>();
      for (int index = 0; index < 8; index++) {
        int own = index;
        jobs.add(
            pool.submit(
                () ->
                    render(
                            "LOCKDOM004-" + own,
                            own % 2 == 0 ? Map.of(LOCKED, new String[] {MARKER}) : Map.of())
                        .select(MESSAGES)
                        .eachText()));
      }
      for (int index = 0; index < jobs.size(); index++) {
        assertEquals(
            index % 2 == 0 ? List.of(LOCK_MESSAGE) : List.of(),
            jobs.get(index).get(10, TimeUnit.SECONDS));
      }
    }
  }
}
