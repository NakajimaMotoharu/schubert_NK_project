package dev.codex.schubert.nk.web.session;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.layout.semantic.UserRole;
import java.time.Instant;
import java.util.List;
import org.junit.jupiter.api.Test;

/** SS314 7.2.1 display snapshot invariants, never a login/session or JSON decoder qualification. */
final class SessionPrincipalBoundaryContractTest {
  private static final AuthenticationContext PUBLIC_CONTEXT =
      AuthenticationContext.of("a".repeat(64));
  private static final Instant FIXED_LOGIN = Instant.parse("2026-11-01T00:00:00Z");

  @Test
  void principalBoundary001NfcSnapshotAndPrincipalNameUseDisplayIdentity() {
    var principal = value("e" + (char) 0x0301, UserRole.ADMIN);
    assertEquals("é", principal.username());
    assertEquals("é", principal.getName());
    assertSame(UserRole.ADMIN, principal.role());
    assertSame(PUBLIC_CONTEXT, principal.authenticationContext());
    assertSame(FIXED_LOGIN, principal.loginAt());
  }

  @Test
  void principalBoundary002Utf8LimitIsCheckedAfterNfcNotOnComparisonKey() {
    for (String name :
        List.of("a", "a".repeat(64), "é".repeat(32), "😀".repeat(16), "İ".repeat(32))) {
      var principal = value(name, UserRole.USER);
      assertEquals(name, principal.username());
      assertEquals(name, principal.getName());
    }
    assertEquals("é".repeat(32), value(("e" + (char) 0x0301).repeat(32), UserRole.USER).username());
    for (String bad :
        List.of("", "a".repeat(65), "é".repeat(33), "😀".repeat(17),
            ("e" + (char) 0x0301).repeat(33))) {
      rejected(bad);
    }
  }

  @Test
  void principalBoundary003InvalidUnicodeControlAndTrailingAsciiSpaceAreRejected() {
    rejected(String.valueOf((char) 0xd800));
    rejected(String.valueOf((char) 0xdc00));
    rejected("x" + (char) 0xd800 + "x");
    for (int control : new int[] {0, 9, 10, 13, 31, 127, 159}) {
      rejected("x" + (char) control);
    }
    rejected(" ");
    rejected("x ");
  }

  @Test
  void principalBoundary004AllFourRequiredFieldsRejectNullBeforePublication() {
    assertThrows(NullPointerException.class, () -> value(null, UserRole.USER));
    assertThrows(NullPointerException.class, () -> value("public", null));
    assertThrows(
        NullPointerException.class,
        () -> new SessionPrincipal("public", UserRole.USER, null, FIXED_LOGIN));
    assertThrows(
        NullPointerException.class,
        () -> new SessionPrincipal("public", UserRole.USER, PUBLIC_CONTEXT, null));
  }

  @Test
  void principalBoundary005ClosedRoleFieldsAndRedactedDisplayDoNotGrantAuthentication() {
    for (UserRole role : List.of(UserRole.USER, UserRole.ADMIN)) {
      var principal = value("Display_User", role);
      assertEquals("Display_User", principal.username());
      assertEquals("Display_User", principal.getName());
      assertSame(role, principal.role());
      assertSame(PUBLIC_CONTEXT, principal.authenticationContext());
      assertEquals(FIXED_LOGIN, principal.loginAt());
      assertEquals("SessionPrincipal[REDACTED]", principal.toString());
    }
  }

  private static SessionPrincipal value(String username, UserRole role) {
    return new SessionPrincipal(username, role, PUBLIC_CONTEXT, FIXED_LOGIN);
  }

  private static void rejected(String username) {
    var failure =
        assertThrows(IllegalArgumentException.class, () -> value(username, UserRole.USER));
    assertEquals("session principal is invalid", failure.getMessage());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
  }
}
