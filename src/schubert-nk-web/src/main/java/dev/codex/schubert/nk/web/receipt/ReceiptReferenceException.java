package dev.codex.schubert.nk.web.receipt;

/** Fixed diagnostic, never SQL/provider/message/locator data. QA048/SS331§9.4; RCPT002/005. */
public final class ReceiptReferenceException extends RuntimeException {
  private static final long serialVersionUID = 1L;

  public ReceiptReferenceException() {
    super("receipt reference unavailable");
  }
}
