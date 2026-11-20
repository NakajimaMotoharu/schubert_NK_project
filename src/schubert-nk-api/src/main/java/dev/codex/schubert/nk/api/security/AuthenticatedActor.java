package dev.codex.schubert.nk.api.security;

import dev.codex.schubert.nk.api.domain.Role;
import java.nio.charset.StandardCharsets;
import java.util.Objects;

/** Verified DB identity only; raw context is absent. NK-AUT-001; UI226; SS314 §6/9; PT-AUT-008. */
public record AuthenticatedActor(long userId, String username, Role role) {
  public AuthenticatedActor {
    Objects.requireNonNull(username, "username");
    Objects.requireNonNull(role, "role");
    if (userId < 1 || userId > 999_999_999_999L) {
      throw new IllegalArgumentException("actor ID is outside N12");
    }
    if (username.isEmpty()
        || !StandardCharsets.UTF_8.newEncoder().canEncode(username)
        || username.getBytes(StandardCharsets.UTF_8).length > 64) {
      throw new IllegalArgumentException("actor username length is invalid");
    }
  }

  @Override
  public String toString() {
    return "AuthenticatedActor[<redacted>]";
  }
}
