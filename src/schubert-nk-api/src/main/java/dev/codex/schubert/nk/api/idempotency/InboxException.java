package dev.codex.schubert.nk.api.idempotency;

import java.sql.SQLException;
import java.util.Objects;

/** Bounded, non-sensitive Inbox coordination failure. */
public final class InboxException extends SQLException {
  private static final long serialVersionUID = 1L;

  public enum Reason {
    MESSAGE_ID_REUSE,
    OPERATION_TOKEN_REUSE,
    FINGERPRINT_KEY_UNAVAILABLE,
    STATE_CORRUPT,
    TRANSACTION_REQUIRED
  }

  private final Reason failureReason;

  InboxException(Reason reason, String message) {
    super(message, sqlState(reason));
    this.failureReason = Objects.requireNonNull(reason, "reason");
  }

  public Reason reason() {
    return failureReason;
  }

  private static String sqlState(Reason reason) {
    Objects.requireNonNull(reason, "reason");
    return switch (reason) {
      case MESSAGE_ID_REUSE, OPERATION_TOKEN_REUSE -> "23000";
      case FINGERPRINT_KEY_UNAVAILABLE -> "55000";
      case STATE_CORRUPT -> "XX000";
      case TRANSACTION_REQUIRED -> "25000";
    };
  }
}
