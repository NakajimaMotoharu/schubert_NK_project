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
      if (dispatchValue0.equals("I")) {
        return INLINE;
      } else if (dispatchValue0.equals("A")) {
        return ATTACHMENT;
      } else {
        throw new IllegalArgumentException("unknown content disposition");
      }
    }
  }
}
