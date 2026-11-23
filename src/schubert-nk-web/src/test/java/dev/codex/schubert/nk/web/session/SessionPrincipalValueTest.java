package dev.codex.schubert.nk.web.session;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.layout.semantic.UserRole;
import java.time.Instant;
import java.util.List;
import org.junit.jupiter.api.Test;

/** SS314 §7.2.1 and §7.2.5; direct display-value boundaries only. */
final class SessionPrincipalValueTest {
  private static final String DISPLAY_NAME = "sample-display-name";
  private static final Instant LOGIN_AT = Instant.parse("2026-09-13T02:04:06Z");
  private static final AuthenticationContext CONTEXT = AuthenticationContext.of("0".repeat(64));

  /** PT-WEB-PRINCIPAL001. */
  @Test
  void principal001NormalizesBeforeCheckingTheExactUtf8Width() {
    var value = principal("e\u0301".repeat(32));

    assertEquals("\u00e9".repeat(32), value.getName());
    assertEquals(UserRole.USER, value.role());
    assertSame(CONTEXT, value.authenticationContext());
    assertEquals(LOGIN_AT, value.loginAt());
  }

  /** PT-WEB-PRINCIPAL002. */
  @Test
  void principal002RejectsEachInvalidDisplayNameWithTheFixedDiagnostic() {
    for (String invalid :
        List.of(
            "",
            Character.toString('\ud800'),
            "\u00e9".repeat(32) + "a",
            DISPLAY_NAME + " ",
            "sample\u0001display")) {
      var failure = assertThrows(IllegalArgumentException.class, () -> principal(invalid));
      assertEquals("session principal is invalid", failure.getMessage());
    }
  }

  /** PT-WEB-PRINCIPAL003. */
  @Test
  void principal003EveryMissingFieldFailsAtItsOwnBoundary() {
    assertEquals(
        "username", assertThrows(NullPointerException.class, () -> principal(null)).getMessage());
    assertEquals(
        "role",
        assertThrows(
                NullPointerException.class,
                () -> new SessionPrincipal(DISPLAY_NAME, null, CONTEXT, LOGIN_AT))
            .getMessage());
    assertEquals(
        "authenticationContext",
        assertThrows(
                NullPointerException.class,
                () -> new SessionPrincipal(DISPLAY_NAME, UserRole.USER, null, LOGIN_AT))
            .getMessage());
    assertEquals(
        "loginAt",
        assertThrows(
                NullPointerException.class,
                () -> new SessionPrincipal(DISPLAY_NAME, UserRole.USER, CONTEXT, null))
            .getMessage());
  }

  /** PT-WEB-PRINCIPAL004. */
  @Test
  void principal004FrameworkNameAndRedactedDiagnosticHaveDistinctContracts() {
    var value = principal(DISPLAY_NAME);

    assertEquals(DISPLAY_NAME, value.getName());
    assertEquals(DISPLAY_NAME, value.username());
    assertEquals("SessionPrincipal[REDACTED]", value.toString());
  }

  /** PT-WEB-PRINCIPAL005. */
  @Test
  void principal005EqualValuesHaveStableHashesAndRoleParticipatesInEquality() {
    var first = principal(DISPLAY_NAME);
    var equal = principal(DISPLAY_NAME);
    var admin = new SessionPrincipal(DISPLAY_NAME, UserRole.ADMIN, CONTEXT, LOGIN_AT);

    assertEquals(first, equal);
    assertEquals(first.hashCode(), equal.hashCode());
    assertNotEquals(first, admin);
  }

  private static SessionPrincipal principal(String name) {
    return new SessionPrincipal(name, UserRole.USER, CONTEXT, LOGIN_AT);
  }
}
