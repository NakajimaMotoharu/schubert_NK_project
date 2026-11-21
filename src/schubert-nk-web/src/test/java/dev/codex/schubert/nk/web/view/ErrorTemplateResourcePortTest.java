package dev.codex.schubert.nk.web.view;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

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

/** SCR090, UI221/222 and SS313. PT-WEB-SCR090-RSRC-001 and 002. */
final class ErrorTemplateResourcePortTest {
  private static final String NOT_FOUND = "対象が見つかりません。";
  private static final String FORBIDDEN = "この操作を実行する権限がありません。";
  private static final String REQUEST_ID = "00000000-0000-0000-0000-000000000027";
  private static final String DISPLAY_NAME = "利用者 <表示> & 確認";
  private static final String NAV = "header.topbar nav a";

  private static Document render(int status, String message, Optional<Map<String, String>> topBar) {
    var servlet = new MockServletContext();
    var request = new MockHttpServletRequest(servlet);
    request.setMethod("GET");
    request.setRequestURI("/error");
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
    var page =
        Map.of("topBar", topBar, "status", status, "message", message, "requestId", REQUEST_ID);
    return Jsoup.parse(
        engine.process(
            "error/error", new WebContext(exchange, Locale.JAPAN, Map.of("page", page))));
  }

  @Test
  void displaysOnlyAnonymousNavigationAndFixedErrorText() {
    var document = render(404, NOT_FOUND, Optional.empty());

    assertEquals("エラー - schubert NK", document.title());
    assertEquals("ja", document.select("html").attr("lang"));
    assertEquals("schubert NK", document.select("header.topbar h1").text());
    assertEquals(List.of("メニュー", "ログイン"), document.select(NAV).eachText());
    assertEquals(List.of("/", "/login"), document.select(NAV).eachAttr("href"));
    assertEquals("エラー", document.select("section[role=alert] #error-title").text());
    assertEquals("404", document.select(".error-status").text());
    assertEquals(NOT_FOUND, document.select(".error-message").text());
    assertEquals(REQUEST_ID, document.select(".request-id").text());
    assertTrue(document.select(".login-user,.login-role,.logout-form").isEmpty());
  }

  @Test
  void displaysEscapedIdentityAndLogoutForEitherDisplayRole() {
    for (String role : List.of("USER", "ADMIN")) {
      var topBar = Map.of("brand", "schubert NK", "username", DISPLAY_NAME, "role", role);
      var document = render(403, FORBIDDEN, Optional.of(topBar));

      assertEquals(List.of("/", "/notifications"), document.select(NAV).eachAttr("href"));
      assertEquals(List.of("メニュー", "通知"), document.select(NAV).eachText());
      assertEquals(List.of(DISPLAY_NAME), document.select(".login-user").eachText());
      assertTrue(document.select(".login-user > *").isEmpty());
      assertEquals(List.of(role), document.select(".login-role").eachText());
      assertEquals(
          List.of("/logout"), document.select(".logout-form[method=post]").eachAttr("action"));
      assertEquals("ログアウト", document.select(".logout-form button").text());
      assertEquals(1, document.select("section[role=alert]").size());
      assertEquals("403", document.select(".error-status").text());
      assertEquals(FORBIDDEN, document.select(".error-message").text());
      assertEquals(REQUEST_ID, document.select(".request-id").text());
    }
  }
}
