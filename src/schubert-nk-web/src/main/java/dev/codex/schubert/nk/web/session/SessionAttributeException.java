package dev.codex.schubert.nk.web.session;

/** Closed schema violation; caller invalidates the session. NK-WEB-001; SS314; PT-WEB-011..014. */
public final class SessionAttributeException extends RuntimeException {
  private static final long serialVersionUID = 1L;

  public SessionAttributeException() {
    super("session attributes are invalid");
  }
}
