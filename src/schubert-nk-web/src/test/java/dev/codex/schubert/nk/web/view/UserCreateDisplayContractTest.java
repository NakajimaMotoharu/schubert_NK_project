package dev.codex.schubert.nk.web.view;

import static org.junit.jupiter.api.Assertions.*;

import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.layout.semantic.UserRole;
import dev.codex.schubert.nk.web.form.UserCreateForm;
import dev.codex.schubert.nk.web.session.SessionPrincipal;
import java.time.Instant;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Set;
import java.util.UUID;
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

/** P016-16/UI222,225/SS313: closed synthetic User-create display; password canaries are public. */
class UserCreateDisplayContractTest {
  private static final UUID PUBLIC_TOKEN = UUID.fromString("12345678-1234-4234-8234-123456789abc");
  private static final List<String> FIELDS =
      List.of("username", "password", "password_confirmation", "role", "enabled");

  private static SessionPrincipal actor() {
    return new SessionPrincipal(
        "fixture-admin", UserRole.ADMIN, AuthenticationContext.of("a".repeat(64)), Instant.EPOCH);
  }

  private static Document render(UserCreateViewModel page) {
    var resolver = new FileTemplateResolver();
    resolver.setPrefix("src/schubert-nk-web/src/main/resources/templates/");
    resolver.setSuffix(".html");
    resolver.setCharacterEncoding("UTF-8");
    resolver.setCacheable(false);
    var engine = new SpringTemplateEngine();
    engine.setTemplateResolver(resolver);
    var servlet = new MockServletContext();
    var request = new MockHttpServletRequest(servlet);
    request.setRequestURI("/admin/users/new");
    var exchange =
        JakartaServletWebApplication.buildApplication(servlet)
            .buildExchange(request, new MockHttpServletResponse());
    return Jsoup.parse(
        engine.process(
            "admin/user-new", new WebContext(exchange, Locale.JAPAN, Map.of("page", page))));
  }

  @Test
  void allMandatoryFieldsHaveVisibleIndicatorsAndNativeRequiredBindings() {
    var dom = render(UserCreateViewModel.newForm(actor(), PUBLIC_TOKEN));
    for (String field : FIELDS) {
      var control = dom.selectFirst("[name=" + field + "]");
      assertNotNull(control);
      assertTrue(control.hasAttr("required"), field);
      assertEquals("user-new-" + field, control.id());
      assertTrue(dom.select("label[for=" + control.id() + "]").text().contains("必須"), field);
    }
    assertEquals("USER", dom.select("select[name=role] option[selected]").val());
    assertEquals("true", dom.select("select[name=enabled] option[selected]").val());
    assertEquals(
        List.of(
            "operation_token", "username", "password", "password_confirmation", "role", "enabled"),
        dom.select("form input,form select").stream()
            .filter(
                node ->
                    !node.attr("name").isEmpty() && !node.closest("form").hasClass("logout-form"))
            .map(node -> node.attr("name"))
            .toList());
    assertEquals("/admin/users/new", dom.select("#user-new-form").attr("action"));
    assertEquals("post", dom.select("#user-new-form").attr("method"));
    assertEquals("", dom.select("input[name=password]").val());
    assertEquals("", dom.select("input[name=password_confirmation]").val());
  }

  @Test
  void invalidUserCreateSummaryTargetsExistingControlsAndNeverRedisplaysPassword() {
    try (var form =
        UserCreateForm.bind(
            Map.of(
                "username",
                List.of("<invalid-user>"),
                "password",
                List.of("short"),
                "password_confirmation",
                List.of("different"),
                "role",
                List.of("OTHER"),
                "enabled",
                List.of("unknown"),
                "operation_token",
                List.of("invalid"),
                "owner",
                List.of("never-reflect-owner")))) {
      assertFalse(form.isValid());
      assertThrows(IllegalArgumentException.class, form::toRequest);
      var dom = render(UserCreateViewModel.redisplay(actor(), form, PUBLIC_TOKEN, "", false));
      assertEquals(7, dom.select(".validation-summary li a").size());
      assertEquals(
          Set.of(
              "#user-new-username",
              "#user-new-password",
              "#user-new-password_confirmation",
              "#user-new-role",
              "#user-new-enabled",
              "#user-new-form"),
          Set.copyOf(dom.select(".validation-summary li a").eachAttr("href")));
      for (var anchor : dom.select(".validation-summary li a"))
        assertEquals(1, dom.select(anchor.attr("href")).size());
      assertEquals("", dom.select("input[name=password]").val());
      assertEquals("", dom.select("input[name=password_confirmation]").val());
      assertFalse(dom.outerHtml().contains("different"));
      assertFalse(dom.outerHtml().contains("never-reflect-owner"));
      assertEquals(0, dom.select("invalid-user,[data-token],[data-password]").size());
    }
  }
}
