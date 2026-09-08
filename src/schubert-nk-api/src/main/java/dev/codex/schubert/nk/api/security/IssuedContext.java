package dev.codex.schubert.nk.api.security;

import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import java.time.Instant;
import java.util.Objects;

/** Login-only secret result. NK-AUT-001; AUT-001; UI226; SS312 §4/314 §6; PT-AUT-005-I. */
public record IssuedContext(
    AuthContextIdentity identity,
    AuthenticationContext context,
    Instant issuedAt,
    Instant expiresAt) {
  public IssuedContext {
    Objects.requireNonNull(identity, "identity");
    Objects.requireNonNull(context, "context");
    Objects.requireNonNull(issuedAt, "issuedAt");
    Objects.requireNonNull(expiresAt, "expiresAt");
    if (!expiresAt.isAfter(issuedAt)) {
      throw new IllegalArgumentException("issued context expiry must follow issue time");
    }
  }

  @Override
  public String toString() {
    return "IssuedContext[REDACTED]";
  }
}
