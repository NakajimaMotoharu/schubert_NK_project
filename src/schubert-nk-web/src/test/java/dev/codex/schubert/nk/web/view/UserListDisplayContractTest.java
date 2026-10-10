package dev.codex.schubert.nk.web.view;

import static org.junit.jupiter.api.Assertions.*;

import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.layout.admin.UserRecord;
import dev.codex.schubert.nk.protocol.layout.common.PagedResponseData;
import dev.codex.schubert.nk.protocol.layout.semantic.UserId;
import dev.codex.schubert.nk.protocol.layout.semantic.UserRole;
import dev.codex.schubert.nk.protocol.layout.semantic.UserState;
import dev.codex.schubert.nk.web.form.UserSearchForm;
import dev.codex.schubert.nk.web.session.SessionPrincipal;
import java.time.Instant;
import java.util.ArrayList;
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

/** P016-15/UI225/SS313: User-list screen integration with pure ADMIN projection. */
class UserListDisplayContractTest {
  private static SessionPrincipal actor(UserRole role) {
    return new SessionPrincipal(
        "fixture-admin", role, AuthenticationContext.of("a".repeat(64)), Instant.EPOCH);
  }

  private static Document render(UserListViewModel page) {
    var resolver = new FileTemplateResolver();
    resolver.setPrefix("src/schubert-nk-web/src/main/resources/templates/");
    resolver.setSuffix(".html");
    resolver.setCharacterEncoding("UTF-8");
    resolver.setCacheable(false);
    var engine = new SpringTemplateEngine();
    engine.setTemplateResolver(resolver);
    var servlet = new MockServletContext();
    var request = new MockHttpServletRequest(servlet);
    request.setRequestURI("/admin/users");
    var exchange =
        JakartaServletWebApplication.buildApplication(servlet)
            .buildExchange(request, new MockHttpServletResponse());
    return Jsoup.parse(
        engine.process(
            "admin/user-list", new WebContext(exchange, Locale.JAPAN, Map.of("page", page))));
  }

  @Test
  void invalidSummaryAndUnknownRoleStateRemainEscapedWithFixedTargets() {
    var form =
        UserSearchForm.bind(
            Map.of(
                "username",
                List.of("<script>" + "x".repeat(65)),
                "role",
                List.of("<unknown-role>"),
                "state",
                List.of("<unknown-state>"),
                "page",
                List.of("+1"),
                "owner",
                List.of("never-display-owner")));
    assertFalse(form.isValid());
    assertThrows(IllegalArgumentException.class, form::toRequest);
    var dom = render(UserListViewModel.invalid(actor(UserRole.ADMIN), form));
    assertEquals(5, dom.select("#user-errors li a").size());
    for (var anchor : dom.select("#user-errors li a"))
      assertEquals(1, dom.select(anchor.attr("href")).size());
    assertEquals("#user-filters", dom.select("#error-page a").attr("href"));
    assertEquals("<unknown-role>", dom.select("select[name=role] option[selected]").val());
    assertEquals("<unknown-state>", dom.select("select[name=state] option[selected]").val());
    assertEquals(0, dom.select("script,unknown-role,unknown-state").size());
    assertFalse(dom.outerHtml().contains("never-display-owner"));
    assertEquals(0, dom.select("nav.pagination").size());
  }

  @Test
  void middlePageWiresBothFragmentsAndPreservesAdminOrderedTable() {
    var form = UserSearchForm.bind(Map.of("page", List.of("2")));
    var rows = new ArrayList<UserRecord>();
    for (int i = 0; i < 50; i++)
      rows.add(
          new UserRecord(
              new UserId(i + 1),
              String.format(Locale.ROOT, "user%02d<img>", i),
              UserRole.USER,
              UserState.ACTIVE,
              Optional.empty(),
              Optional.empty(),
              Instant.EPOCH,
              Instant.EPOCH,
              0));
    var dom =
        render(
            UserListViewModel.success(
                actor(UserRole.ADMIN), form, new PagedResponseData(2, 50, 101, 3, 51, 100), rows));
    assertEquals(2, dom.select("nav.pagination.fifty").size());
    assertEquals(
        List.of("51 - 100 / 101", "51 - 100 / 101"), dom.select("nav.pagination > div").eachText());
    assertEquals(50, dom.select(".table-scroll table .user-row").size());
    assertEquals(1, dom.select(".table-scroll[tabindex=0][role=region] table thead").size());
    assertEquals("user00<img>", dom.select(".user-row .username").getFirst().text());
    assertEquals("user49<img>", dom.select(".user-row .username").getLast().text());
    assertEquals("/admin/users/1", dom.select("a.detail").getFirst().attr("href"));
    assertEquals(0, dom.select("img").size());
    assertEquals(
        List.of("username", "role", "state"),
        dom.select("#user-filters input,#user-filters select").eachAttr("name"));
  }

  @Test
  void emptyAdminPageHasNoPaginationAndUserCannotProject() {
    var form = UserSearchForm.bind(Map.of());
    var data = new PagedResponseData(1, 50, 0, 1, 0, 0);
    var dom = render(UserListViewModel.success(actor(UserRole.ADMIN), form, data, List.of()));
    assertEquals("該当するデータはありません", dom.select(".empty-results").text());
    assertEquals(0, dom.select("nav.pagination,table").size());
    assertThrows(
        IllegalArgumentException.class,
        () -> UserListViewModel.success(actor(UserRole.USER), form, data, List.of()));
  }
}
