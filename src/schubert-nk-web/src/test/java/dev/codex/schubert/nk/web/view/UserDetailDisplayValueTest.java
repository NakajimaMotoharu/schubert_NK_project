package dev.codex.schubert.nk.web.view;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.layout.admin.UserDetailResponseData;
import dev.codex.schubert.nk.protocol.layout.semantic.UserId;
import dev.codex.schubert.nk.protocol.layout.semantic.UserRole;
import dev.codex.schubert.nk.protocol.layout.semantic.UserState;
import dev.codex.schubert.nk.web.session.SessionPrincipal;
import java.time.Instant;
import java.util.Map;
import java.util.Optional;
import org.junit.jupiter.api.Test;

/** UI225 §5, SS313, PT-WEB-SCR017-VM001 through VM003. */
final class UserDetailDisplayValueTest {
  private static final UserId ID = new UserId(23);
  private static final String VIEWER = "fixture-reviewer";
  private static final String TARGET = "Fixture-Reviewer";
  private static final String CREATED_BY = "fixture-create";
  private static final String UPDATED_BY = "fixture-update";
  private static final String INVALID = "invalid user detail projection";

  @Test
  void displaysTheFixedDetailColumnsWithSeparateTimestamps() {
    var view =
        UserDetailViewModel.from(
            actor(UserRole.ADMIN), ID, detail(TARGET, UserState.LOCKED, 2));

    assertEquals(
        Map.ofEntries(
            Map.entry("id", 23L),
            Map.entry("username", TARGET),
            Map.entry("role", "USER"),
            Map.entry("state", "LOCKED"),
            Map.entry("lockReason", "ログイン失敗によるロック"),
            Map.entry("lockedUntil", "2026-10-03 00:02:03.004"),
            Map.entry("lastLogin", "2026-10-02 07:04:05.678"),
            Map.entry("passwordChangedAt", "2026-10-01 09:08:07.006"),
            Map.entry("createdAt", "2026-09-01 15:01:02.123"),
            Map.entry("updatedAt", "2026-10-02 13:05:06.007"),
            Map.entry("activeSessionCount", 2),
            Map.entry("version", 0L),
            Map.entry("createdBy", CREATED_BY),
            Map.entry("updatedBy", UPDATED_BY),
            Map.entry("self", true)),
        view.getValues());
    assertEquals(VIEWER, view.getTopBar().getUsername());
    assertEquals("UserDetailViewModel[REDACTED]", view.toString());
    assertThrows(UnsupportedOperationException.class, () -> view.getValues().clear());
  }

  @Test
  void leavesOptionalFieldsBlankForADifferentTarget() {
    var view =
        UserDetailViewModel.from(
            actor(UserRole.ADMIN), ID, detail("other-fixture", UserState.DISABLED, 0));
    var values = view.getValues();
    assertEquals("DISABLED", values.get("state"));
    assertEquals("", values.get("lockReason"));
    assertEquals("", values.get("lockedUntil"));
    assertEquals("", values.get("lastLogin"));
    assertEquals(0, values.get("activeSessionCount"));
    assertEquals(false, values.get("self"));
  }

  @Test
  void rejectsWrongScopeAndMissingProjectionInputs() {
    var admin = actor(UserRole.ADMIN);
    var valid = detail(TARGET, UserState.DISABLED, 0);
    assertRejected(actor(UserRole.USER), ID, valid);
    assertRejected(admin, new UserId(24), valid);
    assertRejected(admin, ID, detail(TARGET, UserState.DISABLED, 3));
    assertThrows(NullPointerException.class, () -> UserDetailViewModel.from(null, ID, valid));
    assertThrows(NullPointerException.class, () -> UserDetailViewModel.from(admin, null, valid));
    assertThrows(NullPointerException.class, () -> UserDetailViewModel.from(admin, ID, null));
  }

  private static void assertRejected(
      SessionPrincipal actor, UserId requested, UserDetailResponseData data) {
    assertEquals(
        INVALID,
        assertThrows(
                IllegalArgumentException.class, () -> UserDetailViewModel.from(actor, requested, data))
            .getMessage());
  }

  private static SessionPrincipal actor(UserRole role) {
    return new SessionPrincipal(VIEWER, role, AuthenticationContext.of("c".repeat(64)), Instant.EPOCH);
  }

  private static UserDetailResponseData detail(String username, UserState state, int sessions) {
    boolean locked = state == UserState.LOCKED;
    return new UserDetailResponseData(
        ID,
        username,
        UserRole.USER,
        state,
        locked ? Optional.of(Instant.parse("2026-10-02T15:02:03.004Z")) : Optional.empty(),
        locked ? Optional.of(Instant.parse("2026-10-01T22:04:05.678Z")) : Optional.empty(),
        Instant.parse("2026-10-01T00:08:07.006Z"),
        Instant.parse("2026-09-01T06:01:02.123Z"),
        Instant.parse("2026-10-02T04:05:06.007Z"),
        sessions,
        0,
        CREATED_BY,
        UPDATED_BY);
  }
}
