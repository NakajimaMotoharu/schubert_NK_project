package dev.codex.schubert.nk.api.security;

import dev.codex.schubert.nk.protocol.header.ResultCode;
import java.time.Instant;
import java.util.Objects;

/**
 * Logout result, never an authorization principal. NK-AUT-001; AUT-004; UI234 §4; SS312 §4.2/314
 * §6.3; PT-AUT-008-R01/R04.
 */
public record RevokedContext(
    AuthContextIdentity identity, Instant revokedAt, ResultCode resultCode) {
  public RevokedContext {
    Objects.requireNonNull(identity, "identity");
    Objects.requireNonNull(revokedAt, "revokedAt");
    Objects.requireNonNull(resultCode, "resultCode");
    if (resultCode != ResultCode.SUCCESS && resultCode != ResultCode.IDEMPOTENT_SUCCESS)
      throw new IllegalArgumentException("invalid logout result");
  }

  @Override
  public String toString() {
    return "RevokedContext[REDACTED]";
  }
}
