package dev.codex.schubert.nk.web.messaging;

import java.util.Objects;

/** NK-WEB-001/NK-SCN-001; UI232/234; SS311/321/352; PG-D-118/PT-WEB-166..173. */
public final class ScenarioWireException extends RuntimeException {
  private static final long serialVersionUID = 1L;

  public enum Reason {
    INVALID_INPUT,
    INVALID_RESPONSE,
    UNAVAILABLE
  }

  private final Reason reason;

  public ScenarioWireException(Reason reason) {
    super("scenario exchange rejected", null, false, true);
    this.reason = Objects.requireNonNull(reason, "reason");
  }

  public Reason reason() {
    return reason;
  }
}
