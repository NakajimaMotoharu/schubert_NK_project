package dev.codex.schubert.nk.protocol.codec;

/** Sender-side whole-message invariant rejection. Trace: NK-PRO-002, SS 322 §11. */
public final class MessageEncodingException extends IllegalArgumentException {
  private static final long serialVersionUID = 1L;

  public MessageEncodingException(String message) {
    super(message);
  }

  public MessageEncodingException(String message, Throwable cause) {
    super(message, cause);
  }
}
