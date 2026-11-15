package dev.codex.schubert.nk.web.security;

import dev.codex.schubert.nk.web.session.SessionPrincipal;
import dev.codex.schubert.nk.web.session.SessionStoreException;
import java.util.List;
import java.util.Optional;
import org.jspecify.annotations.Nullable;
import org.springframework.security.authentication.AnonymousAuthenticationToken;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.authority.SimpleGrantedAuthority;

/**
 * Closed internal projection only, not an HTTP binding. NK-WEB-001; FUN-001/AUT-001..004; UI226;
 * SS314 §7.2.6; SSC-044/PG-D-103/PT-WEB-068..075.
 */
interface ClosedWebAuthentication {
  static Authentication authenticated(SessionPrincipal principal) {
    return UsernamePasswordAuthenticationToken.authenticated(
        principal,
        null,
        List.of(new SimpleGrantedAuthority("ROLE_" + principal.role().wireValue())));
  }

  static Optional<SessionPrincipal> principal(@Nullable Authentication authentication) {
    if (authentication == null || authentication instanceof AnonymousAuthenticationToken)
      return Optional.empty();
    if (authentication.getClass() != UsernamePasswordAuthenticationToken.class
        || !authentication.isAuthenticated()
        || !(authentication.getPrincipal() instanceof SessionPrincipal principal)
        || authentication.getCredentials() != null
        || authentication.getDetails() != null
        || authentication.getAuthorities().size() != 1
        || !("ROLE_" + principal.role().wireValue())
            .equals(authentication.getAuthorities().iterator().next().getAuthority()))
      throw new SessionStoreException();
    return Optional.of(principal);
  }
}
