package dev.codex.schubert.nk.web.view;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.layout.admin.UserRecord;
import dev.codex.schubert.nk.protocol.layout.common.PagedResponseData;
import dev.codex.schubert.nk.protocol.layout.semantic.UserId;
import dev.codex.schubert.nk.protocol.layout.semantic.UserRole;
import dev.codex.schubert.nk.protocol.layout.semantic.UserState;
import dev.codex.schubert.nk.web.form.UserSearchForm;
import dev.codex.schubert.nk.web.session.SessionPrincipal;
import java.time.Instant;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Optional;
import java.util.stream.IntStream;
import org.junit.jupiter.api.Test;

/** UI225 §3 and SS313, PT-WEB-SCR015-VM001 through VM005. */
final class UserListDisplayValueTest {
  private static final String FIXTURE_REVIEWER = "fixture-reviewer";
  private static final String ALPHA = "alpha";
  private static final String BETA = "beta";

  @Test
  void displaysIndependentTimestampsAndLeavesMissingValuesBlank() {
    var actor = actor(UserRole.ADMIN);
    var form = UserSearchForm.bind(Map.of());
    var page = new PagedResponseData(1, 50, 2, 1, 1, 2);
    var locked =
        new UserRecord(
            new UserId(17),
            ALPHA,
            UserRole.USER,
            UserState.LOCKED,
            Optional.of(Instant.parse("2026-10-02T15:02:03.004Z")),
            Optional.of(Instant.parse("2026-10-01T22:04:05.678Z")),
            Instant.parse("2026-09-01T06:01:02.123Z"),
            Instant.parse("2026-10-02T04:05:06.007Z"),
            1);
    var disabled =
        new UserRecord(
            new UserId(23),
            BETA,
            UserRole.ADMIN,
            UserState.DISABLED,
            Optional.empty(),
            Optional.empty(),
            Instant.parse("2026-08-31T16:01:02Z"),
            Instant.parse("2026-10-01T23:25:26.001Z"),
            2);

    List<UserListViewModel.Row> rows =
        UserListViewModel.success(actor, form, page, List.of(locked, disabled)).getRows();
    assertEquals(List.of(ALPHA, BETA), rows.stream().map(UserListViewModel.Row::getUsername).toList());
    var first = rows.getFirst();
    assertEquals(17, first.getId());
    assertEquals("/admin/users/17", first.getDetailHref());
    assertEquals("USER", first.getRole());
    assertEquals("LOCKED", first.getState());
    assertEquals("2026-10-03 00:02:03.004", first.getLockedUntil());
    assertEquals("2026-10-02 07:04:05.678", first.getLastLogin());
    assertEquals("2026-09-01 15:01:02.123", first.getCreatedAt());
    assertEquals("2026-10-02 13:05:06.007", first.getUpdatedAt());
    assertEquals("UserListRow[REDACTED]", first.toString());

    var second = rows.getLast();
    assertEquals("/admin/users/23", second.getDetailHref());
    assertEquals("ADMIN", second.getRole());
    assertEquals("DISABLED", second.getState());
    assertEquals("", second.getLockedUntil());
    assertEquals("", second.getLastLogin());
    assertEquals("2026-09-01 01:01:02.000", second.getCreatedAt());
    assertEquals("2026-10-02 08:25:26.001", second.getUpdatedAt());
  }

  @Test
  void retainsFiltersAndBothLinksOnTheMiddlePage() {
    var form =
        UserSearchForm.bind(
            Map.of(
                "page", List.of("2"),
                "username", List.of("query"),
                "role", List.of("USER"),
                "state", List.of("ACTIVE")));
    var page = new PagedResponseData(2, 50, 101, 3, 51, 100);
    List<UserRecord> rows =
        IntStream.rangeClosed(51, 100)
            .mapToObj(id -> row(id, String.format(Locale.ROOT, "query-%03d", id)))
            .toList();
    var model = UserListViewModel.success(actor(UserRole.ADMIN), form, page, rows);
    assertEquals(FIXTURE_REVIEWER, model.getTopBar().getUsername());
    assertEquals("query", model.getFilters().getUsername());
    assertEquals(51, model.getPage().orElseThrow().getFirstResult());
    assertEquals(100, model.getPage().orElseThrow().getLastResult());
    assertEquals(
        "/admin/users?username=query&role=USER&state=ACTIVE&page=1",
        model.getPreviousHref().orElseThrow());
    assertEquals(
        "/admin/users?username=query&role=USER&state=ACTIVE&page=3",
        model.getNextHref().orElseThrow());
    assertEquals("query-051", model.getRows().getFirst().getUsername());
    assertEquals("query-100", model.getRows().getLast().getUsername());
    assertThrows(UnsupportedOperationException.class, () -> model.getRows().removeFirst());
    assertEquals("UserListViewModel[REDACTED]", model.toString());
  }

  @Test
  void distinguishesEmptySuccessFromInvalidInput() {
    var admin = actor(UserRole.ADMIN);
    var valid = UserSearchForm.bind(Map.of());
    var bad = UserSearchForm.bind(Map.of("role", List.of("other")));
    var emptyPage = new PagedResponseData(1, 50, 0, 1, 0, 0);
    var empty = UserListViewModel.success(admin, valid, emptyPage, List.of());
    assertEquals(0, empty.getPage().orElseThrow().getTotalCount());
    assertTrue(empty.getRows().isEmpty());
    assertTrue(empty.getPreviousHref().isEmpty());
    assertTrue(empty.getNextHref().isEmpty());

    var invalid = UserListViewModel.invalid(admin, bad);
    assertTrue(invalid.getPage().isEmpty());
    assertTrue(invalid.getRows().isEmpty());
    assertTrue(invalid.getPreviousHref().isEmpty());
    assertTrue(invalid.getNextHref().isEmpty());
    assertEquals(
        "invalid successful user form",
        assertThrows(
                IllegalArgumentException.class,
                () -> UserListViewModel.success(admin, bad, emptyPage, List.of()))
            .getMessage());
    assertEquals(
        "valid form used as invalid",
        assertThrows(IllegalArgumentException.class, () -> UserListViewModel.invalid(admin, valid))
            .getMessage());
  }

  @Test
  void rejectsDuplicateIdentityAndIncorrectByteOrTieOrder() {
    var admin = actor(UserRole.ADMIN);
    var form = UserSearchForm.bind(Map.of());
    var page = new PagedResponseData(1, 50, 2, 1, 1, 2);
    var first = row(10, ALPHA);
    var sameName = row(20, ALPHA);
    var model = UserListViewModel.success(admin, form, page, List.of(first, sameName));
    assertEquals(
        List.of(10L, 20L), model.getRows().stream().map(UserListViewModel.Row::getId).toList());
    assertRejectedRows(admin, form, page, List.of(first, row(10, BETA)), "duplicate user identity");
    assertRejectedRows(
        admin, form, page, List.of(row(20, BETA), first), "invalid user display order");
    assertRejectedRows(admin, form, page, List.of(sameName, first), "invalid user display order");
    assertRejectedRows(admin, form, page, List.of(first), "inconsistent user record count");
  }

  @Test
  void rejectsAResponseForTheWrongPageAndANonAdministrator() {
    var admin = actor(UserRole.ADMIN);
    var firstPage = UserSearchForm.bind(Map.of());
    var secondPage = UserSearchForm.bind(Map.of("page", List.of("2")));
    var data = new PagedResponseData(1, 50, 0, 1, 0, 0);
    var unrelatedPage = new PagedResponseData(1, 50, 51, 2, 1, 50);
    assertRejectedRows(
        admin, secondPage, unrelatedPage, List.of(), "user response page does not match request");
    assertRejectedRows(
        actor(UserRole.USER), firstPage, data, List.of(), "user display requires administrator");
    assertThrows(
        NullPointerException.class, () -> UserListViewModel.success(admin, firstPage, data, null));
  }

  private static void assertRejectedRows(
      SessionPrincipal admin,
      UserSearchForm form,
      PagedResponseData page,
      List<UserRecord> rows,
      String expected) {
    assertEquals(
        expected,
        assertThrows(
                IllegalArgumentException.class,
                () -> UserListViewModel.success(admin, form, page, rows))
            .getMessage());
  }

  private static SessionPrincipal actor(UserRole role) {
    return new SessionPrincipal(
        FIXTURE_REVIEWER, role, AuthenticationContext.of("c".repeat(64)), Instant.EPOCH);
  }

  private static UserRecord row(long id, String username) {
    return new UserRecord(
        new UserId(id),
        username,
        UserRole.USER,
        UserState.ACTIVE,
        Optional.empty(),
        Optional.empty(),
        Instant.EPOCH,
        Instant.EPOCH,
        1);
  }
}
