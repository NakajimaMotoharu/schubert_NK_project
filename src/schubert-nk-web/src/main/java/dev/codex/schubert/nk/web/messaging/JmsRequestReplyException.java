package dev.codex.schubert.nk.web.messaging;

/** Bounded non-secret Web temporary failure raised before an HTTP result is selected. */
public final class JmsRequestReplyException extends RuntimeException {
  private static final long serialVersionUID = 1L;

  private final Reason reason;

  JmsRequestReplyException(Reason reason, String message) {
    super(message);
    this.reason = reason;
  }

  JmsRequestReplyException(Reason reason, String message, Throwable cause) {
    super(message, cause);
    this.reason = reason;
  }

  public Reason reason() {
    return reason;
  }

  public enum Reason {
    CAPACITY,
    TIMEOUT,
    INTERRUPTED
  }
}
