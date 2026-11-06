package dev.codex.schubert.nk.web.view;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.util.ArrayList;
import java.util.HashMap;
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

/** PT-UDETAIL-DOM001..008; UI225236/SS313314. Display forms only, no user mutation. */
final class UserDetailTemplateResourcePortTest {
  private static final String USERNAME = "username";
  private static final String ROLE = "role";
  private static final String ENABLED = "enabled";
  private static final String FIELDS = "fields";
  private static final String ISSUES = "issues";
  private static final String TOKEN = "token";
  private static final String OPERATION = "operation";
  private static final String ID = "id";
  private static final String VERSION = "expected_version";
  private static final String VALUE = "value";
  private static final String STATUS = "STATUS";
  private static final String ROLE_OPERATION = "ROLE";
  private static final String PASSWORD = "PASSWORD";
  private static final String UNLOCK = "UNLOCK";
  private static final String USER = "USER";
  private static final String ADMIN = "ADMIN";
  private static final String OPERATIONS = ".user-operations form";
  private static final String PASSWORD_INPUT = "input[type=password]";
  private static final String SYNTHETIC_CSRF = "synthetic-noncredential-csrf";
  private static final String SYNTHETIC_OPERATION = new java.util.UUID(0, 77).toString();
  private static final String MARKER = "synthetic-unmapped-display-marker";
  private static final List<String> DATE_KEYS =
      List.of("lockedUntil", "lastLogin", "passwordChangedAt", "createdAt", "updatedAt");
  private static final String DATE_SELECTOR =
      ".locked-until,.last-login,.password-changed-at,.created-at,.updated-at";

  private static Map<String, Object> model(String username) {
    var v = new HashMap<String, Object>();
    v.put(ID, 17L);
    v.put(USERNAME, username);
    v.put(ROLE, USER);
    v.put("state", "有効");
    v.put("lockReason", "手動確認");
    v.put("lockedUntil", "2026-11-06 09:30:00");
    v.put("lastLogin", "2026-11-05 08:01:02");
    v.put("activeSessionCount", 2);
    v.put("passwordChangedAt", "2026-10-01 01:02:03");
    v.put("createdAt", "2026-09-01 04:05:06");
    v.put("updatedAt", "2026-11-06 07:08:09");
    v.put("createdBy", "creator");
    v.put("updatedBy", "updater");
    return Map.of("topBar", Map.of(USERNAME, "public-admin", ROLE, ADMIN), "values", v);
  }

  private static Map<String, Object> operationForm(
      String operation, boolean enabled, String role, Map<String, String> issues) {
    return Map.of(
        OPERATION,
        operation,
        FIELDS,
        Map.of(
            ID,
            17L,
            VERSION,
            3L,
            ENABLED,
            enabled,
            ROLE,
            role,
            "password",
            MARKER,
            "password_confirmation",
            MARKER),
        ISSUES,
        issues,
        TOKEN,
        SYNTHETIC_OPERATION);
  }

  private static List<Map<String, Object>> allForms(boolean enabled, String role) {
    return List.of(
        operationForm(STATUS, enabled, role, Map.of()),
        operationForm(ROLE_OPERATION, enabled, role, Map.of()),
        operationForm(PASSWORD, enabled, role, Map.of()),
        operationForm(UNLOCK, enabled, role, Map.of()));
  }

  private static Document render(
      String id,
      Map<String, Object> page,
      Optional<List<Map<String, Object>>> forms,
      Optional<String> message)
      throws Exception {
    var servlet = new MockServletContext();
    var req = new MockHttpServletRequest(servlet);
    req.setMethod("GET");
    req.setRequestURI("/admin/users/17");
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
    var variables = new HashMap<String, Object>();
    variables.put("page", page);
    variables.put("_csrf", Map.of("parameterName", "_csrf", "token", SYNTHETIC_CSRF));
    forms.ifPresent(v -> variables.put("forms", v));
    message.ifPresent(v -> variables.put("message", v));
    var d =
        Jsoup.parse(
            engine.process("admin/user-detail", new WebContext(exchange, Locale.JAPAN, variables)));
    assertTrue(d.select("[th\\:text],[th\\:if],[th\\:replace],[th\\:each]").isEmpty());
    var saved = d.clone();
    saved
        .select("input[name=_csrf],input[name=operation_token]")
        .attr(VALUE, "[REDACTED-SYNTHETIC]");
    var safe = saved.outerHtml();
    assertFalse(safe.contains(SYNTHETIC_CSRF));
    assertFalse(safe.contains(SYNTHETIC_OPERATION));
    assertFalse(safe.contains(MARKER));
    Files.writeString(
        Path.of(System.getProperty("owned.output"), id + ".html"),
        safe,
        StandardOpenOption.CREATE_NEW);
    return d;
  }

  @Test
  void missingFormsAndMessageKeepDisplayMetadataWithoutInventedOperations() throws Exception {
    var d = render("UDTL001", model("public-target"), Optional.empty(), Optional.empty());
    assertEquals("User詳細", d.title());
    assertEquals("User詳細", d.select("h1").text());
    assertEquals("public-admin", d.select(".login-user").text());
    assertEquals(
        List.of(
            "Username",
            "Role",
            "状態",
            "Lock理由",
            "Lock終了日時",
            "最終Login日時",
            "Active session数",
            "最終Password変更日時",
            "作成日時",
            "更新日時",
            "作成actor",
            "更新actor"),
        d.select("dt").eachText());
    assertEquals(
        List.of(
            "public-target",
            USER,
            "有効",
            "手動確認",
            "2026-11-06 09:30:00",
            "2026-11-05 08:01:02",
            "2",
            "2026-10-01 01:02:03",
            "2026-09-01 04:05:06",
            "2026-11-06 07:08:09",
            "creator",
            "updater"),
        d.select("dd").eachText());
    assertTrue(d.select(".user-operations,p[role=alert]").isEmpty());
  }

  @Test
  void emptyFormsCreateNoMutationControlsAndRetainStaticNavigation() throws Exception {
    var d = render("UDTL002", model("sample"), Optional.of(List.of()), Optional.of(""));
    assertEquals(1, d.select(".user-operations").size());
    assertTrue(d.select(OPERATIONS).isEmpty());
    assertTrue(
        d.select("input[name=operation],input[name=operation_token],p[role=alert]").isEmpty());
    assertTrue(d.select("nav a").eachAttr("href").contains("/admin/users"));
    assertEquals("/js/operation-post-submit.js", d.select("script[defer]").attr("src"));
  }

  @Test
  void absentEmptyAndMarkupMessagesHaveExplicitNullAndEscapeBranches() throws Exception {
    List<Optional<String>> messages =
        List.of(Optional.empty(), Optional.of(""), Optional.of("<script>fixture</script>&"));
    List<List<String>> expected =
        List.of(List.of(), List.of(), List.of("<script>fixture</script>&"));
    for (int i = 0; i < messages.size(); i++) {
      var d = render("UDTL003-" + i, model("sample"), Optional.empty(), messages.get(i));
      assertEquals(expected.get(i), d.select("p[role=alert]").eachText());
      assertTrue(d.select("script:not([src])").isEmpty());
    }
  }

  @Test
  void allOperationKindsAndRoleEnabledVariantsKeepSeparateControlShapes() throws Exception {
    int n = 0;
    for (boolean enabled : List.of(true, false))
      for (String role : List.of(USER, ADMIN)) {
        var d =
            render(
                "UDTL004-" + n,
                model("sample"),
                Optional.of(allForms(enabled, role)),
                Optional.empty());
        n++;
        var forms = d.select(OPERATIONS);
        assertEquals(4, forms.size());
        assertEquals(
            List.of(STATUS, ROLE_OPERATION, PASSWORD, UNLOCK), forms.eachAttr("data-operation"));
        var status = forms.get(0);
        assertEquals(Boolean.toString(enabled), status.select("input[name=enabled]").attr(VALUE));
        assertEquals(enabled ? "有効化" : "無効化", status.select("div span").text());
        assertTrue(status.select("select,input[type=password]").isEmpty());
        var roles = forms.get(1);
        assertEquals(1, roles.select("option[selected]").size());
        assertEquals(role, roles.select("option[selected]").attr(VALUE));
        assertEquals(List.of(USER, ADMIN), roles.select("option").eachAttr(VALUE));
        assertTrue(roles.select("input[name=enabled],input[type=password]").isEmpty());
        assertEquals(2, forms.get(2).select(PASSWORD_INPUT).size());
        assertEquals("Lock解除", forms.get(3).select("span").text());
        assertTrue(
            forms.get(3).select("input[name=enabled],select,input[type=password]").isEmpty());
      }
  }

  @Test
  void validationAndHiddenIdentityStayScopedToEachSuppliedForm() throws Exception {
    List<Map<String, String>> issues = List.of(Map.of(), Map.of("confirm", "確認してください"));
    List<List<String>> expected = List.of(List.of(), List.of("確認してください"));
    for (int i = 0; i < issues.size(); i++) {
      var d =
          render(
              "UDTL005-" + i,
              model("sample"),
              Optional.of(List.of(operationForm(STATUS, false, USER, issues.get(i)))),
              Optional.empty());
      var f = d.select(OPERATIONS);
      assertEquals(1, f.size());
      assertEquals("post", f.attr("method"));
      assertEquals("/admin/users/17", f.attr("action"));
      assertEquals(STATUS, f.select("input[name=operation]").attr(VALUE));
      assertEquals("17", f.select("input[name=id]").attr(VALUE));
      assertEquals("3", f.select("input[name=expected_version]").attr(VALUE));
      assertEquals(SYNTHETIC_OPERATION, f.select("input[name=operation_token]").attr(VALUE));
      assertEquals(expected.get(i), f.select(".validation-summary li").eachText());
      assertEquals(1, f.select("input[type=checkbox][name=confirm][required]").size());
      assertEquals("true", f.select("input[name=confirm]").attr(VALUE));
      assertEquals("実行", f.select("button[type=submit]").text());
    }
  }

  @Test
  void metadataEscapesMarkupAndEmptyDateValuesRemainEmpty() throws Exception {
    var literal = "<script>fixture</script>&";
    var p = model(literal);
    var d = render("UDTL006-escaped", p, Optional.empty(), Optional.empty());
    assertEquals(literal, d.select("dd.username").text());
    assertTrue(d.select("script:not([src])").isEmpty());
    var empty = new HashMap<String, Object>();
    var raw = Map.class.cast(p.get("values"));
    for (var entry : raw.entrySet()) {
      var item = Map.Entry.class.cast(entry);
      empty.put(String.class.cast(item.getKey()), item.getValue());
    }
    for (var key : DATE_KEYS) empty.put(key, "");
    var p2 = Map.<String, Object>of("topBar", p.get("topBar"), "values", empty);
    var d2 = render("UDTL006-empty", p2, Optional.empty(), Optional.empty());
    assertEquals(5, d2.select(DATE_SELECTOR).size());
    for (var date : d2.select(DATE_SELECTOR)) assertTrue(date.text().isEmpty());
  }

  @Test
  void passwordControlsNeverRetainUnmappedFieldValues() throws Exception {
    var d =
        render(
            "UDTL007",
            model("sample"),
            Optional.of(List.of(operationForm(PASSWORD, false, USER, Map.of()))),
            Optional.empty());
    assertEquals(2, d.select(PASSWORD_INPUT).size());
    assertEquals(
        List.of("password", "password_confirmation"), d.select(PASSWORD_INPUT).eachAttr("name"));
    for (var input : d.select(PASSWORD_INPUT)) {
      assertFalse(input.hasAttr(VALUE));
      assertTrue(input.val().isEmpty());
      assertTrue(input.hasAttr("required"));
      assertEquals("new-password", input.attr("autocomplete"));
    }
    assertFalse(d.outerHtml().contains(MARKER));
  }

  @Test
  void ownedConcurrentDetailPagesKeepTargetNamesAndFormsIsolated() throws Exception {
    try (var executor = Executors.newFixedThreadPool(2)) {
      List<Future<?>> futures = new ArrayList<>();
      for (int i = 0; i < 8; i++) {
        final int n = i;
        futures.add(
            executor.submit(
                () -> {
                  var name = "public-" + n;
                  var d =
                      render(
                          "UDTL008-" + n,
                          model(name),
                          Optional.of(List.of(operationForm(UNLOCK, false, USER, Map.of()))),
                          Optional.empty());
                  assertEquals(name, d.select("dd.username").text());
                  assertEquals(List.of(UNLOCK), d.select(OPERATIONS).eachAttr("data-operation"));
                  return null;
                }));
      }
      for (var future : futures) future.get(10, TimeUnit.SECONDS);
    }
  }
}
