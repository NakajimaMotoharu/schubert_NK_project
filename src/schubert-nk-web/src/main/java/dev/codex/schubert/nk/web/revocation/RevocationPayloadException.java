package dev.codex.schubert.nk.web.revocation;

import java.util.Objects;

/** No raw/provider cause retained. Keep row on any reason. NK-WEB-002/QA050/RERUN003. */
public final class RevocationPayloadException extends RuntimeException {
  private static final long serialVersionUID = 1L;

  public enum Reason {
    PAYLOAD_INVALID,
    KEY_UNAVAILABLE,
    CRYPTO_UNAVAILABLE
  }

  private final Reason reason;

  RevocationPayloadException(Reason reason) {
    super("revocation encrypted payload rejected: " + Objects.requireNonNull(reason, "reason"));
    this.reason = reason;
  }

  public Reason reason() {
    return reason;
  }
}
