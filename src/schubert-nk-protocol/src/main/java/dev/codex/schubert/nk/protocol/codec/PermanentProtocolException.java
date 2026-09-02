package dev.codex.schubert.nk.protocol.codec;

/** Receiver-side permanent wire rejection. Never includes body or field values. */
public final class PermanentProtocolException extends RuntimeException {
  private static final long serialVersionUID = 1L;

  public PermanentProtocolException(String message) {
    super(message);
  }

  public PermanentProtocolException(String message, Throwable cause) {
    super(message, cause);
  }
}
