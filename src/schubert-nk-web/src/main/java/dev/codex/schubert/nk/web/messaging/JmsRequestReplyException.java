package dev.codex.schubert.nk.web.messaging;

import org.jspecify.annotations.Nullable;

/** Bounded non-secret Web temporary failure raised before an HTTP result is selected. */
public final class JmsRequestReplyException extends RuntimeException {
  private static final long serialVersionUID = 1L;

  private final Reason failureReason;

  JmsRequestReplyException(Reason reason, String message) {
    super(message);
    this.failureReason = java.util.Objects.requireNonNull(reason, "reason");
  }

  JmsRequestReplyException(Reason reason, String message, @Nullable Throwable cause) {
    super(message, cause);
    this.failureReason = java.util.Objects.requireNonNull(reason, "reason");
  }

  public Reason reason() {
    return failureReason;
  }

  public enum Reason {
    CAPACITY,
    TIMEOUT,
    INTERRUPTED
  }
}
