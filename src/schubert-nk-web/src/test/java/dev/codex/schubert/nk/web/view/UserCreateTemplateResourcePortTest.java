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

/** PT-UCREATE-DOM001..008; UI225236/SS313314. Fixed display maps only; no user operation. */
final class UserCreateTemplateResourcePortTest {
  private static final String USERNAME = "username";
  private static final String ROLE = "role";
  private static final String ENABLED = "enabled";
  private static final String FIELDS = "fields";
  private static final String ISSUES = "issues";
  private static final String MESSAGE = "message";
  private static final String USER = "USER";
  private static final String ADMIN = "ADMIN";
  private static final String FORM = "form[data-operation-submit]";
  private static final String VALUE = "value";
  private static final String HREF = "href";
  private static final String SUMMARY = ".validation-summary li";
  private static final String USERNAME_INPUT = "input[name=username]";
  private static final String ROLE_SELECTED = "select[name=role] option[selected]";
  private static final String ENABLED_SELECTED = "select[name=enabled] option[selected]";
  private static final String PASSWORD_INPUT = "input[type=password]";
  private static final String SYNTHETIC_CSRF = "synthetic-noncredential-csrf";
  private static final String SYNTHETIC_OPERATION = new java.util.UUID(0, 77).toString();
  private static final String FORBIDDEN_REDISPLAY_MARKER = "synthetic-unmapped-display-marker";

  private static Map<String, Object> formValues(String name, String role, boolean enabled) {
    return Map.of(USERNAME, name, ROLE, role, ENABLED, enabled);
  }

  private static Map<String, Object> page() {
    var p = new HashMap<String, Object>();
    p.put("topBar", Map.of(USERNAME, "public-admin", ROLE, ADMIN));
    p.put(FIELDS, formValues("", USER, true));
    p.put(ISSUES, Map.of());
    p.put(MESSAGE, "");
    p.put("token", SYNTHETIC_OPERATION);
    return p;
  }

  private static Document render(String id, Map<String, Object> values) throws Exception {
    var servlet = new MockServletContext();
    var req = new MockHttpServletRequest(servlet);
    req.setMethod("GET");
    req.setRequestURI("/admin/users/new");
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
    var variables =
        Map.<String, Object>of(
            "page",
            Map.of("values", values),
            "_csrf",
            Map.of("parameterName", "_csrf", "token", SYNTHETIC_CSRF));
    var d =
        Jsoup.parse(
            engine.process("admin/user-new", new WebContext(exchange, Locale.JAPAN, variables)));
    assertTrue(d.select("[th\\:text],[th\\:if],[th\\:replace],[th\\:each]").isEmpty());
    var saved = d.clone();
    saved
        .select("input[name=_csrf],input[name=operation_token]")
        .attr(VALUE, "[REDACTED-SYNTHETIC]");
    String safe = saved.outerHtml();
    assertFalse(safe.contains(SYNTHETIC_CSRF));
    assertFalse(safe.contains(SYNTHETIC_OPERATION));
    Files.writeString(
        Path.of(System.getProperty("owned.output"), id + ".html"),
        safe,
        StandardOpenOption.CREATE_NEW);
    return d;
  }

  private static void passwordsAbsent(Document d) {
    assertEquals(2, d.select(PASSWORD_INPUT).size());
    for (var input : d.select(PASSWORD_INPUT)) {
      assertFalse(input.hasAttr(VALUE));
      assertTrue(input.val().isEmpty());
      assertTrue(input.hasAttr("required"));
      assertEquals("new-password", input.attr("autocomplete"));
    }
  }

  @Test
  void initialFormHasApprovedEmptyValuesAndDefaults() throws Exception {
    var d = render("UDOM001", page());
    assertEquals("User追加", d.title());
    assertEquals("User追加", d.select("h1").text());
    assertEquals("public-admin", d.select(".login-user").text());
    assertEquals(ADMIN, d.select(".login-role").text());
    assertEquals("", d.select(USERNAME_INPUT).attr(VALUE));
    assertEquals(USER, d.select(ROLE_SELECTED).attr(VALUE));
    assertEquals("true", d.select(ENABLED_SELECTED).attr(VALUE));
    assertTrue(d.select(".validation-summary,.field-error,p[role=alert]").isEmpty());
    passwordsAbsent(d);
  }

  @Test
  void everyRoleAndEnabledCombinationRetainsExactlyOneSelection() throws Exception {
    int n = 0;
    for (String role : List.of(USER, ADMIN))
      for (boolean enabled : List.of(true, false)) {
        var p = page();
        p.put(FIELDS, formValues("sample", role, enabled));
        var d = render("UDOM002-" + n, p);
        n++;
        assertEquals(1, d.select(ROLE_SELECTED).size());
        assertEquals(role, d.select(ROLE_SELECTED).attr(VALUE));
        assertEquals(1, d.select(ENABLED_SELECTED).size());
        assertEquals(Boolean.toString(enabled), d.select(ENABLED_SELECTED).attr(VALUE));
        assertEquals(List.of(USER, ADMIN), d.select("select[name=role] option").eachAttr(VALUE));
        assertEquals(
            List.of("true", "false"), d.select("select[name=enabled] option").eachAttr(VALUE));
      }
  }

  @Test
  void emptyUsernameAndOtherIssuesHaveIndependentSummaryAndFieldScope() throws Exception {
    List<Map<String, String>> inputs =
        List.of(Map.of(), Map.of(USERNAME, "name invalid"), Map.of("role", "role invalid"));
    List<List<String>> expected =
        List.of(List.of(), List.of("name invalid"), List.of("role invalid"));
    List<List<String>> fieldExpected = List.of(List.of(), List.of("name invalid"), List.of());
    for (int i = 0; i < inputs.size(); i++) {
      var p = page();
      p.put(ISSUES, inputs.get(i));
      var d = render("UDOM003-" + i, p);
      assertEquals(expected.get(i), d.select(SUMMARY).eachText());
      assertEquals(fieldExpected.get(i), d.select(".username-error").eachText());
    }
  }

  @Test
  void alertFieldAndUsernameEscapeLiteralMarkupWithoutNodes() throws Exception {
    var literal = "<script>fixture</script>&\"";
    var p = page();
    p.put(FIELDS, formValues(literal, USER, true));
    p.put(MESSAGE, literal);
    p.put(ISSUES, Map.of(USERNAME, literal));
    var d = render("UDOM004", p);
    assertEquals(literal, d.select(USERNAME_INPUT).attr(VALUE));
    assertEquals(literal, d.select("p[role=alert]").text());
    assertEquals(List.of(literal), d.select(SUMMARY).eachText());
    assertTrue(d.select("script:not([src])").isEmpty());
    passwordsAbsent(d);
  }

  @Test
  void usernameDisplayKeepsExactByteBoundaryWithoutClaimingValidation() throws Exception {
    for (int length : List.of(64, 65)) {
      var name = "x".repeat(length);
      var p = page();
      p.put(FIELDS, formValues(name, USER, true));
      var d = render("UDOM005-" + length, p);
      assertEquals(name, d.select(USERNAME_INPUT).attr(VALUE));
      assertEquals("64", d.select(USERNAME_INPUT).attr("maxlength"));
      assertTrue(d.select(USERNAME_INPUT).hasAttr("required"));
    }
  }

  @Test
  void unmappedPasswordPropertiesAreNeverRedisplayed() throws Exception {
    var p = page();
    var extra = new HashMap<>(formValues("sample", USER, true));
    extra.put("password", FORBIDDEN_REDISPLAY_MARKER);
    extra.put("password_confirmation", FORBIDDEN_REDISPLAY_MARKER);
    p.put(FIELDS, extra);
    var d = render("UDOM006", p);
    passwordsAbsent(d);
    assertFalse(d.outerHtml().contains(FORBIDDEN_REDISPLAY_MARKER));
    assertEquals(
        List.of("password", "password_confirmation"), d.select(PASSWORD_INPUT).eachAttr("name"));
  }

  @Test
  void displayOnlyHiddenFieldPostActionAndStaticNavigationMatchContract() throws Exception {
    var d = render("UDOM007", page());
    var f = d.select(FORM);
    assertEquals(1, f.size());
    assertEquals("post", f.attr("method"));
    assertEquals("/admin/users/new", f.attr("action"));
    assertEquals(SYNTHETIC_OPERATION, f.select("input[name=operation_token]").attr(VALUE));
    assertEquals("作成", f.select("button[type=submit]").text());
    assertTrue(d.select("nav a").eachAttr(HREF).contains("/admin/users"));
    assertEquals("/js/operation-post-submit.js", d.select("script[defer]").attr("src"));
  }

  @Test
  void ownedConcurrentFormsDoNotShareUsernamesOrSelections() throws Exception {
    var executor = Executors.newFixedThreadPool(2);
    try {
      List<Future<?>> futures = new ArrayList<>();
      for (int i = 0; i < 8; i++) {
        final int n = i;
        futures.add(
            executor.submit(
                () -> {
                  var p = page();
                  var name = "public-" + n;
                  p.put(FIELDS, formValues(name, ADMIN, false));
                  var d = render("UDOM008-" + n, p);
                  assertEquals(name, d.select(USERNAME_INPUT).attr(VALUE));
                  assertEquals(ADMIN, d.select(ROLE_SELECTED).attr(VALUE));
                  assertEquals("false", d.select(ENABLED_SELECTED).attr(VALUE));
                  passwordsAbsent(d);
                  return null;
                }));
      }
      for (var future : futures) future.get(10, TimeUnit.SECONDS);
    } finally {
      executor.shutdownNow();
      assertTrue(executor.awaitTermination(10, TimeUnit.SECONDS));
    }
  }
}
