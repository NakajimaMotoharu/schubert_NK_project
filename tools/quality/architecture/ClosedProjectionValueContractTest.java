package dev.codex.schubert.nk.web.security;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.layout.semantic.UserRole;
import dev.codex.schubert.nk.web.session.SessionPrincipal;
import dev.codex.schubert.nk.web.session.SessionStoreException;
import java.time.Instant;
import java.util.List;
import org.junit.jupiter.api.Test;
import org.springframework.security.authentication.AnonymousAuthenticationToken;
import org.springframework.security.authentication.TestingAuthenticationToken;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.GrantedAuthority;
import org.springframework.security.core.authority.SimpleGrantedAuthority;

/** SS314 7.2.6 DTO validation only; never installed in a context, session or authentication flow. */
final class ClosedProjectionValueContractTest {
  private static final String PUBLIC_VALUE = "PUBLIC_SYNTHETIC_VALUE";

  @Test
  void closedProjection001AbsentAndAnonymousValuesHaveNoPrincipal() {
    assertTrue(ClosedWebAuthentication.principal(null).isEmpty());
    var anonymous =
        new AnonymousAuthenticationToken(
            "PUBLIC_FIXED_LABEL", "anonymous", List.of(new SimpleGrantedAuthority("ROLE_ANONYMOUS")));
    assertTrue(ClosedWebAuthentication.principal(anonymous).isEmpty());
  }

  @Test
  void closedProjection002BothClosedRolesRetainOnlyTheDeclaredSnapshot() {
    for (var role : List.of(UserRole.USER, UserRole.ADMIN)) {
      var principal = snapshot(role);
      var result = ClosedWebAuthentication.authenticated(principal);
      assertSame(UsernamePasswordAuthenticationToken.class, result.getClass());
      assertSame(principal, result.getPrincipal());
      assertTrue(result.isAuthenticated());
      assertNull(result.getCredentials());
      assertNull(result.getDetails());
      assertEquals(1, result.getAuthorities().size());
      assertEquals(
          role == UserRole.USER ? "ROLE_USER" : "ROLE_ADMIN",
          result.getAuthorities().iterator().next().getAuthority());
      assertSame(principal, ClosedWebAuthentication.principal(result).orElseThrow());
    }
    assertThrows(NullPointerException.class, () -> ClosedWebAuthentication.authenticated(null));
  }

  @Test
  void closedProjection003ForeignTypesStateAndPrincipalAreRejected() {
    var principal = snapshot(UserRole.USER);
    rejected(new TestingAuthenticationToken(principal, null, "ROLE_USER"));
    rejected(new ProjectionSubclass(principal));
    rejected(UsernamePasswordAuthenticationToken.unauthenticated(principal, null));
    rejected(
        UsernamePasswordAuthenticationToken.authenticated(
            PUBLIC_VALUE, null, List.of(new SimpleGrantedAuthority("ROLE_USER"))));
    rejected(
        UsernamePasswordAuthenticationToken.authenticated(
            null, null, List.of(new SimpleGrantedAuthority("ROLE_USER"))));
  }

  @Test
  void closedProjection004CredentialsAndDetailsAreNotSilentlyDiscarded() {
    var withCredentials =
        UsernamePasswordAuthenticationToken.authenticated(
            snapshot(UserRole.USER), PUBLIC_VALUE, List.of(new SimpleGrantedAuthority("ROLE_USER")));
    rejected(withCredentials);
    assertEquals(PUBLIC_VALUE, withCredentials.getCredentials());
    var withDetails = ClosedWebAuthentication.authenticated(snapshot(UserRole.USER));
    var details = new Object();
    ((UsernamePasswordAuthenticationToken) withDetails).setDetails(details);
    rejected(withDetails);
    assertSame(details, withDetails.getDetails());
  }

  @Test
  void closedProjection005ExactlyOneMatchingAuthorityIsRequired() {
    var principal = snapshot(UserRole.USER);
    for (List<GrantedAuthority> authorities :
        List.of(
            List.<GrantedAuthority>of(),
            List.<GrantedAuthority>of(
                new SimpleGrantedAuthority("ROLE_USER"), new SimpleGrantedAuthority("ROLE_ADMIN")),
            List.<GrantedAuthority>of(new SimpleGrantedAuthority("ROLE_ADMIN")),
            List.<GrantedAuthority>of(new SimpleGrantedAuthority("ROLE_UNKNOWN")),
            List.<GrantedAuthority>of(() -> null))) {
      var token = UsernamePasswordAuthenticationToken.authenticated(principal, null, authorities);
      rejected(token);
      assertEquals(authorities, token.getAuthorities());
      assertTrue(token.isAuthenticated());
    }
  }

  @Test
  void closedProjection006EveryReadChecksCurrentDtoWithoutCachingAnEarlierGrant() {
    var principal = snapshot(UserRole.USER);
    var token = (UsernamePasswordAuthenticationToken) ClosedWebAuthentication.authenticated(principal);
    assertSame(principal, ClosedWebAuthentication.principal(token).orElseThrow());
    token.setDetails(PUBLIC_VALUE);
    rejected(token);
    token.setDetails(null);
    assertSame(principal, ClosedWebAuthentication.principal(token).orElseThrow());
    token.setAuthenticated(false);
    rejected(token);
    assertFalse(token.isAuthenticated());
  }

  private static SessionPrincipal snapshot(UserRole role) {
    return new SessionPrincipal(
        "Display_User",
        role,
        AuthenticationContext.of("a".repeat(64)),
        Instant.parse("2026-11-01T00:00:00Z"));
  }

  private static void rejected(Authentication value) {
    var failure =
        assertThrows(SessionStoreException.class, () -> ClosedWebAuthentication.principal(value));
    assertEquals("session storage is unavailable", failure.getMessage());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
  }

  private static final class ProjectionSubclass extends UsernamePasswordAuthenticationToken {
    private static final long serialVersionUID = 1L;

    ProjectionSubclass(SessionPrincipal principal) {
      super(principal, null, List.of(new SimpleGrantedAuthority("ROLE_USER")));
    }
  }
}
