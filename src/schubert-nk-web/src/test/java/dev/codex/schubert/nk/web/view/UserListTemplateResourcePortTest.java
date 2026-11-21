package dev.codex.schubert.nk.web.view;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Optional;
import java.util.stream.IntStream;
import java.util.stream.Stream;
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

/** SCR015, FUN-009, UI225/236 and SS313. PT-WEB-SCR015-RSRC-001 to 003. */
final class UserListTemplateResourcePortTest {
  private static final String USERS_PATH = "/admin/users";
  private static final String HREF = "href";
  private static final String USERNAME = "username";
  private static final String ROLE = "role";
  private static final String STATE = "state";
  private static final String ISSUES = "issues";
  private static final String VALUE = "value";
  private static final String PREV = "/admin/users?role=ADMIN&state=ACTIVE&page=1";
  private static final String NEXT = "/admin/users?role=ADMIN&state=ACTIVE&page=3";
  private static final String ADMIN = "ADMIN";
  private static final String ACTIVE = "ACTIVE";
  private static final String USERNAME_VALUE = "利用者 <表示> & 確認";
  private static final String QUERY_ERRORS = "#user-errors";
  private static final String RESULT_SECTION = "table,.count,.empty-results,.previous,.next";

  private static Document render(
      Map<String, ?> filters,
      Optional<Map<String, Integer>> counts,
      List<Map<String, String>> rows,
      Optional<String> previous,
      Optional<String> next) {
    var servlet = new MockServletContext();
    var request = new MockHttpServletRequest(servlet);
    request.setMethod("GET");
    request.setRequestURI(USERS_PATH);
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
    var topBar = Map.of("brand", "schubert NK", USERNAME, "sample-operator", ROLE, ADMIN);
    var page =
        Map.of(
            "topBar", topBar,
            "filters", filters,
            "page", counts,
            "rows", rows,
            "previousHref", previous,
            "nextHref", next);
    return Jsoup.parse(
        engine.process(
            "admin/user-list", new WebContext(exchange, Locale.JAPAN, Map.of("page", page))));
  }

  private static Map<String, String> row(String username, String role, String detailHref) {
    return Map.of(
        USERNAME,
        username,
        ROLE,
        role,
        STATE,
        ACTIVE,
        "lockedUntil",
        "",
        "lastLogin",
        "",
        "createdAt",
        "2026-11-22 00:00:00.000",
        "updatedAt",
        "2026-11-22 00:01:00.000",
        "detailHref",
        detailHref);
  }

  @Test
  void rendersFixedColumnsSearchInputsAndBothPageLinks() {
    var document =
        render(
            Map.of(USERNAME, "", ROLE, ADMIN, STATE, ACTIVE, ISSUES, Map.of()),
            Optional.of(Map.of("totalCount", 121, "effectivePage", 2, "totalPages", 3)),
            Stream.concat(
                    IntStream.rangeClosed(51, 98)
                        .mapToObj(
                            id ->
                                row(
                                    String.format(Locale.ROOT, "fixture-%02d", id),
                                    ADMIN,
                                    USERS_PATH + "/" + id)),
                    Stream.of(
                        row("reader", ADMIN, "/admin/users/99"),
                        row(USERNAME_VALUE, ADMIN, "/admin/users/100")))
                .toList(),
            Optional.of(PREV),
            Optional.of(NEXT));

    assertEquals("Users", document.title());
    assertEquals(
        List.of("/admin/users/new"), document.select("main > nav:first-of-type a").eachAttr(HREF));
    var search = document.select("form[method=get]");
    assertEquals(USERS_PATH, search.attr("action"));
    assertEquals(List.of(USERNAME, ROLE, STATE), search.select("input,select").eachAttr("name"));
    assertEquals(
        List.of("", "USER", ADMIN), search.select("select[name=role] option").eachAttr(VALUE));
    assertEquals(
        List.of("", ACTIVE, "DISABLED", "LOCKED"),
        search.select("select[name=state] option").eachAttr(VALUE));
    assertEquals(List.of(ADMIN, ACTIVE), search.select("option[selected]").eachAttr(VALUE));
    assertTrue(document.select(QUERY_ERRORS).hasAttr("hidden"));
    assertEquals("121 users / page 2 of 3", document.select(".count").text());
    assertEquals(PREV, document.select(".previous").attr(HREF));
    assertEquals(NEXT, document.select(".next").attr(HREF));
    assertEquals(
        List.of("Username", "Role", "状態", "Lock終了日時", "最終Login日時", "作成日時", "更新日時", "詳細"),
        document.select("thead th").eachText());
    var names = document.select(".user-row .username").eachText();
    assertEquals(50, names.size());
    assertEquals("fixture-51", names.getFirst());
    assertEquals(List.of("reader", USERNAME_VALUE), names.subList(48, 50));
    assertTrue(document.select(".user-row .username > *").isEmpty());
    var detailLinks = document.select(".user-row a.detail").eachAttr(HREF);
    assertEquals(50, detailLinks.size());
    assertEquals(List.of("/admin/users/99", "/admin/users/100"), detailLinks.subList(48, 50));
  }

  @Test
  void rendersZeroCountWithoutRowsOrNavigation() {
    var document =
        render(
            Map.of(USERNAME, "", ROLE, "", STATE, "", ISSUES, Map.of()),
            Optional.of(Map.of("totalCount", 0, "effectivePage", 1, "totalPages", 1)),
            List.of(),
            Optional.empty(),
            Optional.empty());

    assertEquals("0 users / page 1 of 1", document.select(".count").text());
    assertEquals("該当するデータはありません", document.select(".empty-results").text());
    assertTrue(document.select("table,.previous,.next").isEmpty());
  }

  @Test
  void rendersInvalidInputAndErrorWithoutInventingSearchResults() {
    String error = "入力を確認 <表示> & 続行";
    var document =
        render(
            Map.of(USERNAME, USERNAME_VALUE, ROLE, "", STATE, "", ISSUES, Map.of(USERNAME, error)),
            Optional.empty(),
            List.of(),
            Optional.empty(),
            Optional.empty());

    assertEquals(USERNAME_VALUE, document.select("input[name=username]").attr(VALUE));
    assertFalse(document.select(QUERY_ERRORS).hasAttr("hidden"));
    assertEquals(error, document.select("#error-username").text());
    assertTrue(document.select("#error-username > *").isEmpty());
    assertTrue(document.select(RESULT_SECTION).isEmpty());
  }
}
