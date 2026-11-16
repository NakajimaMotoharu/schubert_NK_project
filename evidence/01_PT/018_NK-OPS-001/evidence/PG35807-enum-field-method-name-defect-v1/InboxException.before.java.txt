package dev.codex.schubert.nk.api.idempotency;

import java.sql.SQLException;
import java.util.Objects;

/** Bounded, non-sensitive Inbox coordination failure. */
public final class InboxException extends SQLException {
  private static final long serialVersionUID = 1L;

  public enum Reason {
    MESSAGE_ID_REUSE("23000"),
    OPERATION_TOKEN_REUSE("23000"),
    FINGERPRINT_KEY_UNAVAILABLE("55000"),
    STATE_CORRUPT("XX000"),
    TRANSACTION_REQUIRED("25000");

    private final String sqlState;

    Reason(String sqlState) {
      this.sqlState = sqlState;
    }

    String sqlState() {
      return sqlState;
    }
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
    return Objects.requireNonNull(reason, "reason").sqlState();
  }
}
