package dev.codex.schubert.nk.web.session;

import java.util.Objects;

/**
 * Closed failure reason, no parser/provider diagnostics or raw attributes retained. NK-WEB-001;
 * FUN-001/AUT-001..004; UI226/242; SS314/352; SSC-039/PG-D-095/PT-WEB-016..023. Repository/HTTP
 * owns invalidation and safe alerting.
 */
public final class SessionPayloadException extends RuntimeException {
  private static final long serialVersionUID = 1L;

  public enum Reason {
    PAYLOAD_INVALID,
    KEY_UNAVAILABLE,
    CRYPTO_UNAVAILABLE
  }

  private final Reason reason;

  SessionPayloadException(Reason reason) {
    super("session encrypted payload rejected: " + Objects.requireNonNull(reason, "reason"));
    this.reason = reason;
  }

  public Reason reason() {
    return reason;
  }
}
