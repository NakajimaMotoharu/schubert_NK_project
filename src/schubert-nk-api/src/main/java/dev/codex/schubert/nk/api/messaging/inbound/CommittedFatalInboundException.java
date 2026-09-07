package dev.codex.schubert.nk.api.messaging.inbound;

/**
 * Signals that an invalid inbound message was durably isolated and API must exit nonzero.
 *
 * <p>Trace: NK-MSG-001; RD MQ-008/MQ-010; UI 231/251; SS 321 section 7; PT-JMS-006/009.
 */
public final class CommittedFatalInboundException extends RuntimeException {
  private static final long serialVersionUID = 1L;

  public CommittedFatalInboundException(Throwable cause) {
    super("invalid inbound JMS message was committed to the fatal DLQ", cause);
  }
}
