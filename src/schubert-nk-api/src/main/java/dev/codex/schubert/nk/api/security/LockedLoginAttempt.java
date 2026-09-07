package dev.codex.schubert.nk.api.security;

import java.net.InetAddress;
import java.util.Objects;
import java.util.Optional;

/**
 * Single caller-transaction snapshot; never bind from request input. NK-AUT-001; SS332 §5;
 * PT-AUT-003-D.
 */
public record LockedLoginAttempt(
    InetAddress client, Optional<LoginAccount> account, LoginAttemptState ip) {
  public LockedLoginAttempt {
    Objects.requireNonNull(client, "client");
    Objects.requireNonNull(account, "account");
    Objects.requireNonNull(ip, "ip");
    if (ip.kind() != LoginAttemptKind.IP)
      throw new IllegalArgumentException("login IP state has incorrect kind");
  }

  @Override
  public String toString() {
    return "LockedLoginAttempt[REDACTED]";
  }
}
