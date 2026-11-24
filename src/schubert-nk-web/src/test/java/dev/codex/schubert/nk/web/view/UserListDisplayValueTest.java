package dev.codex.schubert.nk.web.view;

import static org.junit.jupiter.api.Assertions.assertEquals;

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
import java.util.Map;
import java.util.Optional;
import org.junit.jupiter.api.Test;

/** UI225 §3 and SS313, PT-WEB-SCR015-VM001. */
final class UserListDisplayValueTest {
  @Test
  void displaysIndependentTimestampsAndLeavesMissingValuesBlank() {
    var actor =
        new SessionPrincipal(
            "fixture-reviewer",
            UserRole.ADMIN,
            AuthenticationContext.of("c".repeat(64)),
            Instant.EPOCH);
    var form = UserSearchForm.bind(Map.of());
    var page = new PagedResponseData(1, 50, 2, 1, 1, 2);
    var locked =
        new UserRecord(
            new UserId(17),
            "alpha",
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
            "beta",
            UserRole.ADMIN,
            UserState.DISABLED,
            Optional.empty(),
            Optional.empty(),
            Instant.parse("2026-08-31T16:01:02Z"),
            Instant.parse("2026-10-01T23:25:26.001Z"),
            2);

    List<UserListViewModel.Row> rows =
        UserListViewModel.success(actor, form, page, List.of(locked, disabled)).getRows();
    assertEquals(
        List.of("alpha", "beta"), rows.stream().map(UserListViewModel.Row::getUsername).toList());
    var first = rows.getFirst();
    assertEquals("/admin/users/17", first.getDetailHref());
    assertEquals("USER", first.getRole());
    assertEquals("LOCKED", first.getState());
    assertEquals("2026-10-03 00:02:03.004", first.getLockedUntil());
    assertEquals("2026-10-02 07:04:05.678", first.getLastLogin());
    assertEquals("2026-09-01 15:01:02.123", first.getCreatedAt());
    assertEquals("2026-10-02 13:05:06.007", first.getUpdatedAt());

    var second = rows.getLast();
    assertEquals("/admin/users/23", second.getDetailHref());
    assertEquals("ADMIN", second.getRole());
    assertEquals("DISABLED", second.getState());
    assertEquals("", second.getLockedUntil());
    assertEquals("", second.getLastLogin());
    assertEquals("2026-09-01 01:01:02.000", second.getCreatedAt());
    assertEquals("2026-10-02 08:25:26.001", second.getUpdatedAt());
  }
}
