package dev.codex.schubert.nk.protocol.header;

import java.util.Objects;

/** S/A/I wire interaction kind. Trace: NK-PRO-001, UI 232 §3, SS 322 §7. */
public enum InteractionKind {
  SYNCHRONOUS('S'),
  ASYNC_ACCEPTANCE('A'),
  INTERNAL('I');

  private final char wireValue;

  InteractionKind(char wireValue) {
    this.wireValue = wireValue;
  }

  public char wireValue() {
    return wireValue;
  }

  public static InteractionKind fromWire(String value) {
    Objects.requireNonNull(value, "value");
    if (value.length() != 1) {
      throw new IllegalArgumentException("interaction kind must be exactly one byte");
    }
    return switch (value.charAt(0)) {
      case 'S' -> SYNCHRONOUS;
      case 'A' -> ASYNC_ACCEPTANCE;
      case 'I' -> INTERNAL;
      default -> throw new IllegalArgumentException("unknown interaction kind");
    };
  }
}
