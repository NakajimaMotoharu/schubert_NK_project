package dev.codex.schubert.nk.protocol.file;

import java.util.Objects;

/** MEDIA1024 I/A disposition. Trace: UI 235 §2. */
public enum ContentDisposition {
  INLINE('I'),
  ATTACHMENT('A');

  private final char wireValue;

  ContentDisposition(char wireValue) {
    this.wireValue = wireValue;
  }

  public char wireValue() {
    return wireValue;
  }

  public static ContentDisposition fromWire(String value) {
    Objects.requireNonNull(value, "value");
    return switch (value) {
      case "I" -> INLINE;
      case "A" -> ATTACHMENT;
      default -> throw new IllegalArgumentException("unknown content disposition");
    };
  }
}
