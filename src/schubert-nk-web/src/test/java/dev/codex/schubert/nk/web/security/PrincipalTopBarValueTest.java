package dev.codex.schubert.nk.web.security;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.layout.semantic.UserRole;
import dev.codex.schubert.nk.web.session.SessionPrincipal;
import dev.codex.schubert.nk.web.view.TopBarViewModel;
import java.time.Instant;
import java.util.List;
import java.util.Map;
import org.junit.jupiter.api.Test;

/** PT-WEB-PRINCIPALVALUE001002; UI222226/SS313314: public unissued synthetic values only. */
final class PrincipalTopBarValueTest {
  private static final String USERNAME = "é";
  private static final String OTHER = "other";
  private static final AuthenticationContext PUBLIC_CONTEXT =
      AuthenticationContext.of("a".repeat(64));
  private static final Instant AT = Instant.parse("2026-01-02T03:04:05.123Z");

  @Test
  void principalvalue001AllFourComponentsAndNfcDefineEqualityHashAndMapIdentity() {
    var value = new SessionPrincipal("e\u0301", UserRole.USER, PUBLIC_CONTEXT, AT);
    var equal = new SessionPrincipal(USERNAME, UserRole.USER, PUBLIC_CONTEXT, AT);
    assertEquals(USERNAME, value.username());
    assertEquals(USERNAME, value.getName());
    assertEquals(UserRole.USER, value.role());
    assertEquals(PUBLIC_CONTEXT, value.authenticationContext());
    assertEquals(AT, value.loginAt());
    assertEquals(value, value);
    assertEquals(value, equal);
    assertEquals(equal, value);
    assertEquals(value.hashCode(), equal.hashCode());
    assertEquals(OTHER, Map.of(value, OTHER).get(equal));
    for (var changed :
        List.of(
            new SessionPrincipal(OTHER, UserRole.USER, PUBLIC_CONTEXT, AT),
            new SessionPrincipal(USERNAME, UserRole.ADMIN, PUBLIC_CONTEXT, AT),
            new SessionPrincipal(
                USERNAME, UserRole.USER, AuthenticationContext.of("b".repeat(64)), AT),
            new SessionPrincipal(USERNAME, UserRole.USER, PUBLIC_CONTEXT, AT.plusSeconds(1))))
      assertNotEquals(value, changed);
    assertNotEquals(value, null);
    assertNotEquals(value, OTHER);
    assertEquals("SessionPrincipal[REDACTED]", value.toString());
  }

  @Test
  void principalvalue002TopBarHasLiteralBrandRoleAndNormalizedUsernameOnly() {
    for (var entry : Map.of(UserRole.USER, "USER", UserRole.ADMIN, "ADMIN").entrySet()) {
      var value = new SessionPrincipal("e\u0301", entry.getKey(), PUBLIC_CONTEXT, AT);
      var display = TopBarViewModel.from(value);
      assertEquals("schubert NK", display.getBrand());
      assertEquals(USERNAME, display.getUsername());
      assertEquals(entry.getValue(), display.getRole());
      assertEquals("TopBarViewModel[REDACTED]", display.toString());
    }
    assertThrows(NullPointerException.class, () -> TopBarViewModel.from(null));
  }
}
