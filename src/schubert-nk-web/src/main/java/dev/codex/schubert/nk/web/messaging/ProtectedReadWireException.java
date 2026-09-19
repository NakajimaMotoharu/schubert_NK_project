package dev.codex.schubert.nk.web.messaging;

import java.util.Objects;

/** NK-WEB001/NK-MED001/MQ/AUT/UI232,235/SS311,352/PG206/PT-WEB238..245. */
public final class ProtectedReadWireException extends RuntimeException {
  private static final long serialVersionUID = 1L;

  public enum Reason {
    INVALID_INPUT,
    INVALID_RESPONSE,
    UNAVAILABLE
  }

  private final Reason reason;

  public ProtectedReadWireException(Reason reason) {
    super("protected read exchange rejected", null, false, true);
    this.reason = Objects.requireNonNull(reason, "reason");
  }

  public Reason reason() {
    return reason;
  }
}
