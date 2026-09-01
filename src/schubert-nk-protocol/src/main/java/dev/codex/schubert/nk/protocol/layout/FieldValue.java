package dev.codex.schubert.nk.protocol.layout;

import java.util.Objects;

/** Typed value of one X/N/B payload field. Text rendering is always redacted. */
public sealed interface FieldValue
    permits FieldValue.Text, FieldValue.Numeric, FieldValue.Flag, FieldValue.Unset {

  record Text(String value) implements FieldValue {
    public Text {
      Objects.requireNonNull(value, "value");
    }

    @Override
    public String toString() {
      return "Text[redacted,length=" + value.length() + ']';
    }
  }

  record Numeric(long value) implements FieldValue {}

  record Flag(boolean value) implements FieldValue {}

  enum Unset implements FieldValue {
    INSTANCE
  }
}
