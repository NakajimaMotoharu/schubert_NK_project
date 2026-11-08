package dev.codex.schubert.nk.protocol.codec;

import java.nio.charset.CharacterCodingException;

/** NONPRODUCTION ORACLE FAULT: intentionally drops only the diagnostic cause. */
public final class FieldEncodingException extends IllegalArgumentException {
  private static final long serialVersionUID = 1L;

  public FieldEncodingException(String message) {
    super(message);
  }

  public FieldEncodingException(String message, CharacterCodingException ignoredCause) {
    super(message); // Intentional negative control, never installed into src or a release.
  }
}
