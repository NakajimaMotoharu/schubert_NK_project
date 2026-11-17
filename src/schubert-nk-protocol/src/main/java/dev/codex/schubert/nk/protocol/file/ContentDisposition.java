package dev.codex.schubert.nk.protocol.file;

import java.util.Objects;

/** MEDIA1024 I/A disposition. Trace: UI 235 §2. */
public enum ContentDisposition {
  INLINE('I'),
  ATTACHMENT('A');

  private final char encodedValue;

  ContentDisposition(char wireValue) {
    this.encodedValue = wireValue;
  }

  public char wireValue() {
    return encodedValue;
  }

  public static ContentDisposition fromWire(String value) {
    Objects.requireNonNull(value, "value");
    {
      final String dispatchValue0 = java.util.Objects.requireNonNull(value);
      if ("I".equals(dispatchValue0)) {
        return INLINE;
      } else if ("A".equals(dispatchValue0)) {
        return ATTACHMENT;
      } else {
        throw new IllegalArgumentException("unknown content disposition");
      }
    }
  }
}
