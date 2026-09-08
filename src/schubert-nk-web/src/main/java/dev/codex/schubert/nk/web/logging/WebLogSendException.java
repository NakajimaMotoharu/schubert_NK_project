package dev.codex.schubert.nk.web.logging;

/** Bounded Web log send failure; trace NK-MSG-002, SS 324 section 9, PT-IDEM-012. */
public final class WebLogSendException extends Exception {
  private static final long serialVersionUID = 1L;

  public WebLogSendException(String message) {
    super(message);
  }

  public WebLogSendException(String message, Throwable cause) {
    super(message, cause);
  }
}
