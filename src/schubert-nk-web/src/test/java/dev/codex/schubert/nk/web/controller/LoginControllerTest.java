package dev.codex.schubert.nk.web.controller;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;

import dev.codex.schubert.nk.web.config.WebMvcConfiguration;
import java.util.List;
import java.util.Locale;
import org.jsoup.Jsoup;
import org.jsoup.nodes.Document;
import org.junit.jupiter.api.Test;
import org.springframework.mock.web.MockServletContext;
import org.springframework.security.web.csrf.CsrfToken;
import org.springframework.security.web.csrf.DefaultCsrfToken;
import org.springframework.test.web.servlet.setup.MockMvcBuilders;
import org.springframework.web.context.support.AnnotationConfigWebApplicationContext;
import org.thymeleaf.spring6.view.ThymeleafViewResolver;

/** PG219/PT-SCR105..108; independent UI222/226/264 and SS313/355 Login oracle. */
class LoginControllerTest {
  private static final String USERNAME_INPUT_SELECTOR = "#login-username";
  private static final String PASSWORD_INPUT_SELECTOR = "#login-password";
  private static final String CSRF = "safe-fixture-csrf";

  private static AnnotationConfigWebApplicationContext context() {
    var context = new AnnotationConfigWebApplicationContext();
    context.setServletContext(new MockServletContext());
    context.register(WebMvcConfiguration.class);
    context.refresh();
    return context;
  }

  private static Document getLogin(AnnotationConfigWebApplicationContext context, String query)
      throws Exception {
    var request =
        get("/login")
            .requestAttr(
                CsrfToken.class.getName(), new DefaultCsrfToken("X-CSRF-TOKEN", "_csrf", CSRF));
    if (query != null) {
      request.param(query, "");
    }
    var response =
        MockMvcBuilders.webAppContextSetup(context)
            .build()
            .perform(request)
            .andReturn()
            .getResponse();
    assertEquals(200, response.getStatus());
    assertEquals("UTF-8", response.getCharacterEncoding());
    return Jsoup.parse(response.getContentAsString());
  }

  @Test
  void scr105ApprovedBrandAndPostCsrf() throws Exception {
    try (var context = context()) {
      var document = getLogin(context, null);
      assertEquals("ja", document.selectFirst("html").attr("lang"));
      assertEquals("schubert NK - ログイン", document.title());
      assertEquals("schubert NK", document.selectFirst("h1").text());
      assertEquals(1, document.select("form[method=post][action=/login]").size());
      assertEquals(1, document.select("form input[name=_csrf][type=hidden]").size());
      assertEquals(CSRF, document.selectFirst("form input[name=_csrf]").attr("value"));
    }
  }

  @Test
  void scr106InputsAndNoLeakedCredentials() throws Exception {
    try (var context = context()) {
      var document = getLogin(context, null);
      assertEquals("ユーザー名", document.selectFirst("label[for=login-username]").text());
      assertEquals("パスワード", document.selectFirst("label[for=login-password]").text());
      assertEquals("username", document.selectFirst(USERNAME_INPUT_SELECTOR).attr("name"));
      assertEquals("username", document.selectFirst(USERNAME_INPUT_SELECTOR).attr("autocomplete"));
      assertTrue(document.selectFirst(USERNAME_INPUT_SELECTOR).hasAttr("required"));
      assertTrue(document.selectFirst(USERNAME_INPUT_SELECTOR).hasAttr("autofocus"));
      assertEquals("password", document.selectFirst(PASSWORD_INPUT_SELECTOR).attr("type"));
      assertEquals(
          "current-password", document.selectFirst(PASSWORD_INPUT_SELECTOR).attr("autocomplete"));
      assertTrue(document.selectFirst(PASSWORD_INPUT_SELECTOR).hasAttr("required"));
      assertEquals("", document.selectFirst(PASSWORD_INPUT_SELECTOR).val());
      assertEquals("ログイン", document.selectFirst("form button").text());
    }
  }

  @Test
  void scr107OnlyMatchingCurrentMessagesAppear() throws Exception {
    var parameters = List.of("error", "locked", "logout", "unknown");
    var messages =
        List.of("ユーザー名またはパスワードが正しくありません。", "ログイン試行回数が上限に達しました。15分ほど待ってから再度お試しください。", "ログアウトしました。");
    try (var context = context()) {
      for (int i = 0; i < parameters.size(); i++) {
        var document = getLogin(context, parameters.get(i));
        var displayed = document.select(".login-message").eachText();
        assertEquals(i < messages.size() ? List.of(messages.get(i)) : List.of(), displayed);
        assertEquals("", document.selectFirst(PASSWORD_INPUT_SELECTOR).val());
      }
      assertTrue(getLogin(context, null).select(".login-message").isEmpty());
    }
  }

  @Test
  void scr108ClosedViewAndControllerBoundary() throws Exception {
    assertEquals("login", new LoginController().login());
    try (var context = context()) {
      var resolver = context.getBean(ThymeleafViewResolver.class);
      assertNotNull(resolver.resolveViewName("login", Locale.JAPAN));
      for (var name :
          List.of("login/fragment", "../login", "redirect:/login", "forward:/login", "unknown")) {
        assertNull(resolver.resolveViewName(name, Locale.JAPAN));
      }
      var response =
          MockMvcBuilders.webAppContextSetup(context)
              .build()
              .perform(
                  org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post(
                      "/login"))
              .andReturn()
              .getResponse();
      assertEquals(405, response.getStatus());
    }
  }
}
