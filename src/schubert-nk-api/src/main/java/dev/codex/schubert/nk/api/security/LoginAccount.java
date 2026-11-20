package dev.codex.schubert.nk.api.security;

import java.nio.charset.StandardCharsets;
import java.util.Objects;

/** Locked DB identity, not proof of password authentication. NK-AUT-001; SS314 §5; PT-AUT-003-D. */
public record LoginAccount(
    AuthenticatedActor identity, boolean active, String passwordHash, LoginAttemptState attempts) {
  public LoginAccount {
    Objects.requireNonNull(identity, "identity");
    Objects.requireNonNull(passwordHash, "passwordHash");
    Objects.requireNonNull(attempts, "attempts");
    if (passwordHash.isEmpty()
        || !StandardCharsets.UTF_8.newEncoder().canEncode(passwordHash)
        || passwordHash.getBytes(StandardCharsets.UTF_8).length > 255
        || attempts.kind() != LoginAttemptKind.USER) {
      throw new IllegalArgumentException("login account storage invariant is invalid");
    }
  }

  @Override
  public String toString() {
    return "LoginAccount[REDACTED]";
  }
}
