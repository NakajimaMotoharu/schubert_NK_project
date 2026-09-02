package dev.codex.schubert.nk.protocol.codec;

import java.nio.charset.CharacterCodingException;

/** Sender-side field rejection. Trace: NK-PRO-002, SS 322 §11. */
public final class FieldEncodingException extends IllegalArgumentException {
  private static final long serialVersionUID = 1L;

  public FieldEncodingException(String message) {
    super(message);
  }

  public FieldEncodingException(String message, CharacterCodingException cause) {
    super(message, cause);
  }
}
