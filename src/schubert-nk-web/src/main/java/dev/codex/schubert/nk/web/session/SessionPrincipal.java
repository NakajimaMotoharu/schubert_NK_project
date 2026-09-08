package dev.codex.schubert.nk.web.session;

import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.layout.semantic.UserRole;
import java.nio.charset.StandardCharsets;
import java.text.Normalizer;
import java.time.Instant;
import java.util.Objects;

/**
 * Web display/early-gate snapshot only; API revalidates every business request.
 * NK-WEB-001/NK-AUT-001; FUN-001/AUT-001..004; UI226; SS314 §7.2.1;
 * SSC-038/PG-D-094/PT-WEB-009..015. No password/user entity/session ID is stored.
 */
public record SessionPrincipal(
    String username, UserRole role, AuthenticationContext authenticationContext, Instant loginAt)
    implements java.security.Principal {
  public SessionPrincipal {
    Objects.requireNonNull(username, "username");
    Objects.requireNonNull(role, "role");
    Objects.requireNonNull(authenticationContext, "authenticationContext");
    Objects.requireNonNull(loginAt, "loginAt");
    username = Normalizer.normalize(username, Normalizer.Form.NFC);
    if (!StandardCharsets.UTF_8.newEncoder().canEncode(username)
        || username.isEmpty()
        || username.getBytes(StandardCharsets.UTF_8).length > 64
        || username.endsWith(" ")
        || username.codePoints().anyMatch(Character::isISOControl))
      throw new IllegalArgumentException("session principal is invalid");
  }

  @Override
  public String getName() {
    // SSC-043/PG-D-102/PT-WEB-064: framework identity is username, never redacted toString/context.
    return username;
  }

  @Override
  public String toString() {
    return "SessionPrincipal[REDACTED]";
  }
}
