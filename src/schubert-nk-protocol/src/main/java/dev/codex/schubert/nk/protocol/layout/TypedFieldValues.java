package dev.codex.schubert.nk.protocol.layout;

import java.util.Objects;
import java.util.Optional;

/** Type-safe bridge used by generated named records; it never infers component order. */
public final class TypedFieldValues {
  private TypedFieldValues() {}

  public static FieldValue.Text requiredText(FieldValueSet fields, String name) {
    FieldValue value = require(fields, name);
    if (value instanceof FieldValue.Text text) {
      return text;
    }
    throw wrongType(name);
  }

  public static FieldValue.Numeric requiredNumeric(FieldValueSet fields, String name) {
    FieldValue value = require(fields, name);
    if (value instanceof FieldValue.Numeric numeric) {
      return numeric;
    }
    throw wrongType(name);
  }

  public static FieldValue.Flag requiredFlag(FieldValueSet fields, String name) {
    FieldValue value = require(fields, name);
    if (value instanceof FieldValue.Flag flag) {
      return flag;
    }
    throw wrongType(name);
  }

  public static Optional<FieldValue.Text> optionalText(FieldValueSet fields, String name) {
    FieldValue value = require(fields, name);
    if (value == FieldValue.Unset.INSTANCE) {
      return Optional.empty();
    }
    if (value instanceof FieldValue.Text text) {
      return Optional.of(text);
    }
    throw wrongType(name);
  }

  public static FieldValue orUnset(Optional<FieldValue.Text> value) {
    Objects.requireNonNull(value, "value");
    return value.<FieldValue>map(text -> text).orElse(FieldValue.Unset.INSTANCE);
  }

  public static void requireEmpty(FieldValueSet fields) {
    Objects.requireNonNull(fields, "fields");
    if (fields.size() != 0) {
      throw new LayoutValidationException("empty data record contains fields");
    }
  }

  private static FieldValue require(FieldValueSet fields, String name) {
    Objects.requireNonNull(fields, "fields");
    Objects.requireNonNull(name, "name");
    return fields.getOrUnset(name);
  }

  private static LayoutValidationException wrongType(String name) {
    return new LayoutValidationException("typed field has the wrong value kind: " + name);
  }
}
