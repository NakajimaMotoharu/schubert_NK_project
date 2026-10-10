package dev.codex.schubert.nk.web.view;

import static org.junit.jupiter.api.Assertions.*;

import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.layout.admin.UserDetailResponseData;
import dev.codex.schubert.nk.protocol.layout.semantic.UserId;
import dev.codex.schubert.nk.protocol.layout.semantic.UserRole;
import dev.codex.schubert.nk.protocol.layout.semantic.UserState;
import dev.codex.schubert.nk.web.session.SessionPrincipal;
import java.time.Instant;
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

/** P016-17/UI222,225/SS313: pure display and supplied closed operation fixtures only. */
class UserDetailDisplayContractTest {
  private static UserDetailViewModel page() {
    var actor =
        new SessionPrincipal(
            "fixture-admin",
            UserRole.ADMIN,
            AuthenticationContext.of("a".repeat(64)),
            Instant.EPOCH);
    var data =
        new UserDetailResponseData(
            new UserId(5),
            "target<img>",
            UserRole.USER,
            UserState.ACTIVE,
            Optional.empty(),
            Optional.empty(),
            Instant.EPOCH,
            Instant.EPOCH,
            Instant.EPOCH,
            2,
            0,
            "creator<script>",
            "updater<&>");
    return UserDetailViewModel.from(actor, new UserId(5), data);
  }

  private static Document render(List<Map<String, Object>> forms) {
    var resolver = new FileTemplateResolver();
    resolver.setPrefix("src/schubert-nk-web/src/main/resources/templates/");
    resolver.setSuffix(".html");
    resolver.setCharacterEncoding("UTF-8");
    resolver.setCacheable(false);
    var engine = new SpringTemplateEngine();
    engine.setTemplateResolver(resolver);
    var servlet = new MockServletContext();
    var request = new MockHttpServletRequest(servlet);
    request.setRequestURI("/admin/users/5");
    var exchange =
        JakartaServletWebApplication.buildApplication(servlet)
            .buildExchange(request, new MockHttpServletResponse());
    return Jsoup.parse(
        engine.process(
            "admin/user-detail",
            new WebContext(
                exchange, Locale.JAPAN, Map.of("page", page(), "forms", forms, "message", ""))));
  }

  private static Map<String, Object> operation(String operation, Map<String, String> issues) {
    return Map.of(
        "operation",
        operation,
        "fields",
        Map.of("id", 5, "expected_version", 0, "enabled", true, "role", "USER"),
        "token",
        "12345678-1234-4234-8234-123456789abc",
        "issues",
        issues);
  }

  @Test
  void suppliedOperationFormsHaveUniqueRequiredControlsAndLabels() {
    var dom =
        render(
            List.of(
                operation("STATUS", Map.of()),
                operation("ROLE", Map.of()),
                operation("PASSWORD", Map.of()),
                operation("UNLOCK", Map.of())));
    assertEquals(4, dom.select(".user-operations form").size());
    for (String op : List.of("STATUS", "ROLE", "PASSWORD", "UNLOCK")) {
      var form = dom.selectFirst("#user-" + op + "-form");
      assertNotNull(form);
      assertEquals("post", form.attr("method"));
      assertEquals("/admin/users/5", form.attr("action"));
      var confirm = form.selectFirst("[name=confirm]");
      assertNotNull(confirm);
      assertEquals("user-" + op + "-confirm", confirm.id());
      assertTrue(confirm.hasAttr("required"));
      assertTrue(form.select("label[for=" + confirm.id() + "]").text().contains("必須"));
    }
    for (String id :
        List.of(
            "user-ROLE-role", "user-PASSWORD-password", "user-PASSWORD-password_confirmation")) {
      var control = dom.selectFirst("#" + id);
      assertNotNull(control);
      assertTrue(control.hasAttr("required"));
      assertTrue(dom.select("label[for=" + id + "]").text().contains("必須"));
    }
    assertEquals(
        dom.select("[id]").size(),
        dom.select("[id]").stream().map(node -> node.id()).distinct().count());
    assertTrue(dom.select("input[type=password]").stream().allMatch(node -> node.val().isEmpty()));
  }

  @Test
  void operationErrorsPointToOnlyExistingControlsOrTheirForm() {
    var dom =
        render(
            List.of(
                operation(
                    "STATUS", Map.of("confirm", "確認してください。", "expected_version", "入力項目を確認してください。")),
                operation("ROLE", Map.of("role", "入力項目を確認してください。", "confirm", "確認してください。")),
                operation(
                    "PASSWORD",
                    Map.of(
                        "password", "入力項目を確認してください。", "password_confirmation", "入力項目を確認してください。")),
                operation("UNLOCK", Map.of("form", "入力項目を確認してください。"))));
    assertEquals(7, dom.select(".validation-summary a").size());
    for (var anchor : dom.select(".validation-summary a"))
      assertEquals(1, dom.select(anchor.attr("href")).size());
    assertEquals(
        "#user-STATUS-form",
        dom.select("#user-STATUS-form .validation-summary a").stream()
            .filter(node -> node.text().equals("入力項目を確認してください。"))
            .findFirst()
            .orElseThrow()
            .attr("href"));
    assertEquals(
        "#user-UNLOCK-form", dom.select("#user-UNLOCK-form .validation-summary a").attr("href"));
  }

  @Test
  void detailsEscapeDisplayFieldsAndRespectSuppliedDisplaySubset() {
    var dom = render(List.of(operation("PASSWORD", Map.of())));
    assertEquals("target<img>", dom.select(".username").text());
    assertEquals("creator<script>", dom.select(".created-by").text());
    assertEquals("updater<&>", dom.select(".updated-by").text());
    assertEquals("1970-01-01 09:00:00.000", dom.select(".password-changed-at").text());
    assertEquals("2", dom.select(".active-sessions").text());
    assertEquals("", dom.select(".lock-reason").text());
    assertEquals(1, dom.select(".user-operations form").size());
    assertEquals("PASSWORD", dom.select(".user-operations form").attr("data-operation"));
    assertEquals(0, dom.select("img,script,[data-token],[data-session],[data-password]").size());
    assertEquals(0, render(List.of()).select(".user-operations form").size());
  }
}
