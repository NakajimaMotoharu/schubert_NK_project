package dev.codex.schubert.nk.web.security;

import java.net.InetAddress;
import java.util.Objects;

/**
 * Numeric text only, no session ID or other default WebAuthenticationDetails fields. Upstream must
 * separately establish Caddy trust. NK-WEB-001; FUN-001/AUT-001; UI226/234; SS314 §3.1/352;
 * SSC-043/PG-D-102/PT-WEB-063..067.
 */
public record LoginClientAddress(String value) {
  public LoginClientAddress {
    Objects.requireNonNull(value, "value");
    try {
      if (InetAddress.ofLiteral(value).getHostAddress().contains("%") || value.length() > 45)
        throw new IllegalArgumentException("invalid IP");
    } catch (IllegalArgumentException failure) {
      throw new IllegalArgumentException("login client address is invalid");
    }
  }

  @Override
  public String toString() {
    return "LoginClientAddress[REDACTED]";
  }
}
