package dev.codex.schubert.nk.web.logging;

import java.util.Objects;

/**
 * Safe error codes for the Web log projection alert; no event/key/provider detail is retained.
 *
 * <p>Trace: NK-MSG-002; RD MON-003; UI 252; SS 324 §9/352 §11.2; PT-IDEM-012/015.
 */
public final class WebLogPayloadException extends RuntimeException {
  private static final long serialVersionUID = 1L;

  public enum Reason {
    KEY_UNAVAILABLE,
    PAYLOAD_INVALID,
    CRYPTO_UNAVAILABLE
  }

  private final Reason reason;

  WebLogPayloadException(Reason reason) {
    super("web log encrypted payload rejected: " + Objects.requireNonNull(reason, "reason"));
    this.reason = reason;
  }

  public Reason reason() {
    return reason;
  }
}
