package dev.codex.schubert.nk.protocol.header;

import java.util.Objects;

/** Q/S/E wire message kind. Trace: NK-PRO-001, UI 232 §3, SS 322 §7. */
public enum MessageKind {
  REQUEST('Q'),
  RESPONSE('S'),
  EVENT('E');

  private final char encodedValue;

  MessageKind(char wireValue) {
    this.encodedValue = wireValue;
  }

  public char wireValue() {
    return encodedValue;
  }

  public static MessageKind fromWire(String value) {
    Objects.requireNonNull(value, "value");
    if (value.length() != 1) {
      throw new IllegalArgumentException("message kind must be exactly one byte");
    }
    return switch (value.charAt(0)) {
      case 'Q' -> REQUEST;
      case 'S' -> RESPONSE;
      case 'E' -> EVENT;
      default -> throw new IllegalArgumentException("unknown message kind");
    };
  }
}
