package dev.codex.schubert.nk.web.view;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

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

/** SCR015/UI225/236/SS313. PT-WEB-SCR015-COUNT-001 uses only local projection values. */
class UserListLastPageCountTest {
  @Test
  void rejectsAnExtraSortedRowOnTheSingleRowLastPage() {
    var actor =
        new SessionPrincipal(
            "fixture-reader",
            UserRole.ADMIN,
            AuthenticationContext.of("c".repeat(64)),
            Instant.EPOCH);
    var form = UserSearchForm.bind(Map.of("page", List.of("2")));
    var data = new PagedResponseData(2, 50, 51, 2, 51, 51);
    var first = row(1, "alpha");
    var second = row(2, "beta");

    var view = UserListViewModel.success(actor, form, data, List.of(first));
    assertEquals(51, view.getPage().orElseThrow().getFirstResult());
    assertEquals(51, view.getPage().orElseThrow().getLastResult());
    assertEquals(
        List.of("alpha"), view.getRows().stream().map(UserListViewModel.Row::getUsername).toList());
    var rejected =
        assertThrows(
            IllegalArgumentException.class,
            () -> UserListViewModel.success(actor, form, data, List.of(first, second)));
    assertEquals("inconsistent user record count", rejected.getMessage());
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
