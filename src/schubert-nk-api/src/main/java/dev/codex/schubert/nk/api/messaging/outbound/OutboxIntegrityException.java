package dev.codex.schubert.nk.api.messaging.outbound;

/**
 * Deny-closed signal for an outbox row whose stored identity disagrees with its wire body.
 *
 * <p>The message is bounded and never contains the stored body or secret values. Trace: NK-MSG-002;
 * RD MQ-006/MQ-008; UI 242 section 8.2; SS 324 section 8.3.
 */
public final class OutboxIntegrityException extends RuntimeException {
  private static final long serialVersionUID = 1L;

  public OutboxIntegrityException(String message) {
    super(message);
  }

  public OutboxIntegrityException(String message, Throwable cause) {
    super(message, cause);
  }
}
