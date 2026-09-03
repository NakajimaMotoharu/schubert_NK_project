package dev.codex.schubert.nk.web.messaging;

/**
 * Signals that an invalid reply was durably isolated and the Web process must exit nonzero.
 *
 * <p>Trace: NK-MSG-001; RD MQ-008/MQ-010; UI 231/251; SS 321 section 7;
 * PT-JMS-006/009.
 */
public final class CommittedFatalReplyException extends RuntimeException {
  private static final long serialVersionUID = 1L;

  public CommittedFatalReplyException(Throwable cause) {
    super("invalid JMS reply was committed to the fatal DLQ", cause);
  }
}
