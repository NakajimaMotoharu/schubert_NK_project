package dev.codex.schubert.nk.api.security;

import java.net.InetAddress;
import java.util.Objects;
import java.util.Optional;

/**
 * Single caller-transaction snapshot; never bind from request input. NK-AUT-001; SS332 §5;
 * PT-AUT-003-D, BUG-020/YKT-017: retain immutable numeric literal, not a JDK address object.
 */
public record LockedLoginAttempt(
    String clientAddress, Optional<LoginAccount> account, LoginAttemptState ip) {
  public LockedLoginAttempt {
    Objects.requireNonNull(clientAddress, "clientAddress");
    Objects.requireNonNull(account, "account");
    Objects.requireNonNull(ip, "ip");
    if (ip.kind() != LoginAttemptKind.IP)
      throw new IllegalArgumentException("login IP state has incorrect kind");
    if (clientAddress.contains("%"))
      throw new IllegalArgumentException("login IP scope is invalid");
    try {
      clientAddress = InetAddress.ofLiteral(clientAddress).getHostAddress();
    } catch (IllegalArgumentException invalid) {
      throw new IllegalArgumentException("login IP literal is invalid");
    }
  }

  @Override
  public String toString() {
    return "LockedLoginAttempt[REDACTED]";
  }
}
