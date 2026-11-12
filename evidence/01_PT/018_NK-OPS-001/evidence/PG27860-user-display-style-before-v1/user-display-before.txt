package dev.codex.schubert.nk.web.view;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.layout.admin.UserDetailResponseData;
import dev.codex.schubert.nk.protocol.layout.admin.UserRecord;
import dev.codex.schubert.nk.protocol.layout.common.PagedResponseData;
import dev.codex.schubert.nk.protocol.layout.semantic.UserId;
import dev.codex.schubert.nk.protocol.layout.semantic.UserRole;
import dev.codex.schubert.nk.protocol.layout.semantic.UserState;
import dev.codex.schubert.nk.web.form.UserSearchForm;
import dev.codex.schubert.nk.web.session.SessionPrincipal;
import java.time.DateTimeException;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Optional;
import org.junit.jupiter.api.Test;

/** UI225/236, SS313/332; USER-DISPLAY001..008. No DB/authentication/authority installation. */
final class UserDisplayContractTest {
  private static final Instant TIME = Instant.parse("2026-11-01T00:00:00.123Z");
  private static final PagedResponseData EMPTY = new PagedResponseData(1, 50, 0, 1, 0, 0);
  private static final PagedResponseData ONE = new PagedResponseData(1, 50, 1, 1, 1, 1);
  private static final PagedResponseData TWO = new PagedResponseData(1, 50, 2, 1, 1, 2);

  private static SessionPrincipal actor(UserRole role) {
    return new SessionPrincipal("PUBLIC_DISPLAY", role,
        AuthenticationContext.of("a".repeat(64)), TIME);
  }

  private static UserSearchForm form(String page) {
    return UserSearchForm.bind(Map.of("page", List.of(page)));
  }

  private static UserRecord row(long id, String name, boolean withTimes) {
    return new UserRecord(new UserId(id), name,
        withTimes ? UserRole.ADMIN : UserRole.USER,
        withTimes ? UserState.LOCKED : UserState.ACTIVE,
        withTimes ? Optional.of(TIME.plusSeconds(60)) : Optional.empty(),
        withTimes ? Optional.of(TIME) : Optional.empty(),
        TIME.minusSeconds(1), TIME.plusSeconds(1), 0);
  }

  private static UserDetailResponseData detail(String name, UserRole role, UserState state,
      int count, long version, Instant passwordChanged) {
    return new UserDetailResponseData(new UserId(12), name, role, state,
        state == UserState.LOCKED ? Optional.of(TIME.plusSeconds(60)) : Optional.empty(),
        count == 0 ? Optional.empty() : Optional.of(TIME),
        passwordChanged, TIME.minusSeconds(1), TIME.plusSeconds(1),
        count, version, "PUBLIC_CREATOR", "PUBLIC_UPDATER");
  }

  @Test
  void userDisplay001EmptyListRetainsOnlyClosedDisplayAndNoNavigation() {
    var filters = form("1");
    var page = UserListViewModel.success(actor(UserRole.ADMIN), filters, EMPTY, List.of());
    assertSame(filters, page.getFilters());
    assertEquals("PUBLIC_DISPLAY", page.getTopBar().getUsername());
    assertEquals("ADMIN", page.getTopBar().getRole());
    assertTrue(page.getPage().orElseThrow().isEmpty());
    assertTrue(page.getRows().isEmpty());
    assertTrue(page.getPreviousHref().isEmpty());
    assertTrue(page.getNextHref().isEmpty());
    assertEquals("UserListViewModel[REDACTED]", page.toString());
    assertThrows(UnsupportedOperationException.class, () -> page.getRows().clear());
  }

  @Test
  void userDisplay002MiddlePageLinksUseIndependentPercentVectorAndRowsAreCopies() {
    String prefix = "A +&あ";
    var filters = UserSearchForm.bind(Map.of("username", List.of(prefix),
        "role", List.of("ADMIN"), "state", List.of("LOCKED"), "page", List.of("2")));
    var caller = new ArrayList<UserRecord>();
    for (int i = 51; i <= 100; i++)
      caller.add(row(i, prefix + String.format(Locale.ROOT, "%06d", i), true));
    var page = UserListViewModel.success(actor(UserRole.ADMIN), filters,
        new PagedResponseData(2, 50, 101, 3, 51, 100), caller);
    caller.clear();
    assertEquals(50, page.getRows().size());
    assertEquals("/admin/users?username=A%20%2B%26%E3%81%82&role=ADMIN&state=LOCKED&page=1",
        page.getPreviousHref().orElseThrow());
    assertEquals("/admin/users?username=A%20%2B%26%E3%81%82&role=ADMIN&state=LOCKED&page=3",
        page.getNextHref().orElseThrow());
    var value = page.getRows().getFirst();
    assertEquals(51, value.getId());
    assertEquals("/admin/users/51", value.getDetailHref());
    assertEquals("A +&あ000051", value.getUsername());
    assertEquals("ADMIN", value.getRole());
    assertEquals("LOCKED", value.getState());
    assertEquals("2026-11-01 09:01:00.123", value.getLockedUntil());
    assertEquals("2026-11-01 09:00:00.123", value.getLastLogin());
    assertEquals("2026-11-01 08:59:59.123", value.getCreatedAt());
    assertEquals("2026-11-01 09:00:01.123", value.getUpdatedAt());
    assertEquals("UserListRow[REDACTED]", value.toString());
    assertEquals("A +&あ000100", page.getRows().getLast().getUsername());
    assertThrows(UnsupportedOperationException.class, () -> page.getRows().clear());
    var clamped = UserListViewModel.success(actor(UserRole.ADMIN), form("999"), ONE,
        List.of(row(1, "a", false)));
    assertEquals(1, clamped.getPage().orElseThrow().getEffectivePage());
    assertTrue(clamped.getPreviousHref().isEmpty());
    assertTrue(clamped.getNextHref().isEmpty());
    assertEquals("", clamped.getRows().getFirst().getLockedUntil());
    assertEquals("", clamped.getRows().getFirst().getLastLogin());
    assertEquals("USER", clamped.getRows().getFirst().getRole());
    assertEquals("ACTIVE", clamped.getRows().getFirst().getState());
    var last = UserListViewModel.success(actor(UserRole.ADMIN), form("2"),
        new PagedResponseData(2, 50, 51, 2, 51, 51), List.of(row(51, "z", false)));
    assertEquals("/admin/users?username=&role=&state=&page=1", last.getPreviousHref().orElseThrow());
    assertTrue(last.getNextHref().isEmpty());
  }

  @Test
  void userDisplay003ByteOrderAndIdTieBreakAreCheckedWithoutRepair() {
    var principal = actor(UserRole.ADMIN);
    var filters = form("1");
    var unicode = UserListViewModel.success(principal, filters, TWO,
        List.of(row(1, "\uE000", false), row(2, "\uD800\uDC00", false)));
    assertEquals(List.of("\uE000", "\uD800\uDC00"),
        unicode.getRows().stream().map(UserListViewModel.Row::getUsername).toList());
    var tie = UserListViewModel.success(principal, filters, TWO,
        List.of(row(1, "same", false), row(2, "same", false)));
    assertEquals(List.of(1L, 2L), tie.getRows().stream().map(UserListViewModel.Row::getId).toList());
    assertEquals("duplicate user identity", assertThrows(IllegalArgumentException.class,
        () -> UserListViewModel.success(principal, filters, TWO,
            List.of(row(1, "a", false), row(1, "b", false)))).getMessage());
    for (var bad : List.of(
        List.of(row(1, "b", false), row(2, "a", false)),
        List.of(row(2, "same", false), row(1, "same", false)))) {
      assertEquals("invalid user display order", assertThrows(IllegalArgumentException.class,
          () -> UserListViewModel.success(principal, filters, TWO, bad)).getMessage());
    }
  }

  @Test
  void userDisplay004SuccessRejectsDamagedPageCountFormAndEveryNullBoundary() {
    var principal = actor(UserRole.ADMIN);
    var filters = form("1");
    var invalid = UserSearchForm.bind(Map.of("role", List.of("UNKNOWN")));
    assertEquals("invalid successful user form", assertThrows(IllegalArgumentException.class,
        () -> UserListViewModel.success(principal, invalid, EMPTY, List.of())).getMessage());
    assertEquals("user response page does not match request", assertThrows(IllegalArgumentException.class,
        () -> UserListViewModel.success(principal, filters,
            new PagedResponseData(2, 50, 51, 2, 51, 51), List.of(row(51, "z", false)))).getMessage());
    for (var data : List.of(EMPTY, TWO)) {
      assertEquals("inconsistent user record count", assertThrows(IllegalArgumentException.class,
          () -> UserListViewModel.success(principal, filters, data,
              List.of(row(1, "a", false)))).getMessage());
    }
    assertThrows(NullPointerException.class,
        () -> UserListViewModel.success(null, filters, EMPTY, List.of()));
    assertThrows(NullPointerException.class,
        () -> UserListViewModel.success(principal, null, EMPTY, List.of()));
    assertThrows(NullPointerException.class,
        () -> UserListViewModel.success(principal, filters, null, List.of()));
    assertThrows(NullPointerException.class,
        () -> UserListViewModel.success(principal, filters, EMPTY, null));
    assertThrows(NullPointerException.class,
        () -> UserListViewModel.success(principal, filters, ONE, Arrays.asList((UserRecord) null)));
  }

  @Test
  void userDisplay005InvalidFormHasNoRowsPageLinksAndRejectsNonAdminDisplay() {
    var principal = actor(UserRole.ADMIN);
    var invalid = UserSearchForm.bind(Map.of("role", List.of("UNKNOWN")));
    var page = UserListViewModel.invalid(principal, invalid);
    assertSame(invalid, page.getFilters());
    assertTrue(page.getPage().isEmpty());
    assertTrue(page.getRows().isEmpty());
    assertTrue(page.getPreviousHref().isEmpty());
    assertTrue(page.getNextHref().isEmpty());
    assertThrows(IllegalArgumentException.class, () -> UserListViewModel.invalid(principal, form("1")));
    assertThrows(NullPointerException.class, () -> UserListViewModel.invalid(principal, null));
    assertThrows(NullPointerException.class, () -> UserListViewModel.invalid(null, invalid));
    assertEquals("user display requires administrator", assertThrows(IllegalArgumentException.class,
        () -> UserListViewModel.invalid(actor(UserRole.USER), invalid)).getMessage());
    assertThrows(IllegalArgumentException.class,
        () -> UserListViewModel.success(actor(UserRole.USER), form("1"), EMPTY, List.of()));
  }

  @Test
  void userDisplay006DetailRetainsOnlyApprovedFieldsForStatesCountsVersionsAndSelf() {
    for (UserRole role : List.of(UserRole.USER, UserRole.ADMIN)) {
      for (UserState state : List.of(UserState.ACTIVE, UserState.DISABLED, UserState.LOCKED)) {
        for (int count : new int[] {0, 1, 2}) {
          for (long version : new long[] {0, 999_999_999L}) {
            String name = version == 0 ? "public_display" : "OTHER";
            var page = UserDetailViewModel.from(actor(UserRole.ADMIN), new UserId(12),
                detail(name, role, state, count, version, TIME));
            assertEquals(Map.ofEntries(
                Map.entry("id", 12L), Map.entry("username", name),
                Map.entry("role", role == UserRole.ADMIN ? "ADMIN" : "USER"),
                Map.entry("state", state == UserState.ACTIVE ? "ACTIVE"
                    : state == UserState.DISABLED ? "DISABLED" : "LOCKED"),
                Map.entry("lockReason", state == UserState.LOCKED ? "ログイン失敗によるロック" : ""),
                Map.entry("lockedUntil", state == UserState.LOCKED ? "2026-11-01 09:01:00.123" : ""),
                Map.entry("lastLogin", count == 0 ? "" : "2026-11-01 09:00:00.123"),
                Map.entry("passwordChangedAt", "2026-11-01 09:00:00.123"),
                Map.entry("createdAt", "2026-11-01 08:59:59.123"),
                Map.entry("updatedAt", "2026-11-01 09:00:01.123"),
                Map.entry("activeSessionCount", count), Map.entry("version", version),
                Map.entry("createdBy", "PUBLIC_CREATOR"), Map.entry("updatedBy", "PUBLIC_UPDATER"),
                Map.entry("self", version == 0)), page.getValues());
            assertEquals("PUBLIC_DISPLAY", page.getTopBar().getUsername());
            assertEquals("ADMIN", page.getTopBar().getRole());
            assertEquals("UserDetailViewModel[REDACTED]", page.toString());
            assertFalse(page.getValues().containsKey("password"));
            assertThrows(UnsupportedOperationException.class, () -> page.getValues().clear());
          }
        }
      }
    }
  }

  @Test
  void userDisplay007DetailRejectsEachRoleTargetAndSessionCountMismatch() {
    var good = detail("PUBLIC_DISPLAY", UserRole.USER, UserState.ACTIVE, 0, 0, TIME);
    assertEquals("invalid user detail projection", assertThrows(IllegalArgumentException.class,
        () -> UserDetailViewModel.from(actor(UserRole.USER), new UserId(12), good)).getMessage());
    assertEquals("invalid user detail projection", assertThrows(IllegalArgumentException.class,
        () -> UserDetailViewModel.from(actor(UserRole.ADMIN), new UserId(13), good)).getMessage());
    for (int count : new int[] {3, 999}) {
      assertEquals("invalid user detail projection", assertThrows(IllegalArgumentException.class,
          () -> UserDetailViewModel.from(actor(UserRole.ADMIN), new UserId(12),
              detail("PUBLIC_DISPLAY", UserRole.USER, UserState.ACTIVE, count, 0, TIME))).getMessage());
    }
  }

  @Test
  void userDisplay008NullAndUnrepresentableDateNeverPublishARepairedDisplay() {
    var principal = actor(UserRole.ADMIN);
    var good = detail("PUBLIC_DISPLAY", UserRole.USER, UserState.ACTIVE, 0, 0, TIME);
    assertThrows(NullPointerException.class, () -> UserDetailViewModel.from(null, new UserId(12), good));
    assertThrows(NullPointerException.class, () -> UserDetailViewModel.from(principal, null, good));
    assertThrows(NullPointerException.class, () -> UserDetailViewModel.from(principal, new UserId(12), null));
    assertThrows(DateTimeException.class,
        () -> UserDetailViewModel.from(principal, new UserId(12),
            detail("PUBLIC_DISPLAY", UserRole.USER, UserState.ACTIVE, 0, 0, Instant.MAX)));
    var caller = new ArrayList<UserRecord>();
    caller.add(new UserRecord(new UserId(1), "PUBLIC", UserRole.USER, UserState.ACTIVE,
        Optional.empty(), Optional.empty(), Instant.MAX, TIME, 0));
    assertThrows(DateTimeException.class,
        () -> UserListViewModel.success(principal, form("1"), ONE, caller));
    assertEquals(1, caller.size());
  }
}
