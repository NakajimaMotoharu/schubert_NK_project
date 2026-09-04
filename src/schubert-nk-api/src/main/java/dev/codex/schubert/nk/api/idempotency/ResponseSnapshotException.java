package dev.codex.schubert.nk.api.idempotency;

import java.util.Objects;

/**
 * Bounded response snapshot failure without plaintext or key material.
 *
 * <p>Trace: DAT-009, SS 324 §6/§15 and PT-IDEM-008.
 */
public final class ResponseSnapshotException extends RuntimeException {
  private static final long serialVersionUID = 1L;

  public enum Reason {
    KEY_UNAVAILABLE,
    SNAPSHOT_INVALID,
    CRYPTO_UNAVAILABLE
  }

  private final Reason reason;

  ResponseSnapshotException(Reason reason, String message) {
    super(message);
    this.reason = Objects.requireNonNull(reason, "reason");
  }

  ResponseSnapshotException(Reason reason, String message, Throwable cause) {
    super(message, cause);
    this.reason = Objects.requireNonNull(reason, "reason");
  }

  public Reason reason() {
    return reason;
  }
}
