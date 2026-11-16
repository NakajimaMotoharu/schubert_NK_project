package dev.codex.schubert.nk.protocol.layout;

import java.util.Objects;

/** Explicit one-based field metadata. Trace: NK-PRO-001, SS 322 §2/§12. */
public record FieldDefinition<T>(
    FieldArea area,
    String name,
    int start,
    int end,
    int length,
    WireType wireType,
    Presence presence,
    Padding padding,
    Class<T> javaType,
    String semanticRule) {

  public FieldDefinition(
      FieldArea area,
      String name,
      int start,
      int length,
      WireType wireType,
      Presence presence,
      Padding padding,
      Class<T> javaType,
      String semanticRule) {
    this(
        area,
        name,
        start,
        checkedEnd(start, length),
        length,
        wireType,
        presence,
        padding,
        javaType,
        semanticRule);
  }

  public FieldDefinition {
    Objects.requireNonNull(area, "area");
    Objects.requireNonNull(name, "name");
    Objects.requireNonNull(wireType, "wireType");
    Objects.requireNonNull(presence, "presence");
    Objects.requireNonNull(padding, "padding");
    Objects.requireNonNull(javaType, "javaType");
    Objects.requireNonNull(semanticRule, "semanticRule");
    if (name.isBlank() || semanticRule.isBlank()) {
      throw new LayoutValidationException("field name and semantic rule must not be blank");
    }
    if (start < 1 || length < 1) {
      throw new LayoutValidationException("field start and length must be positive");
    }
    if (end != checkedEnd(start, length)) {
      throw new LayoutValidationException("field end does not match start and length");
    }
    final Padding expected = expectedPaddingFor(wireType);
    if (padding != expected) {
      throw new LayoutValidationException("padding does not match the wire type");
    }
  }

  private static Padding expectedPaddingFor(WireType wireType) {
    if (wireType == WireType.TEXT) {
      return Padding.SPACE_RIGHT;
    } else if (wireType == WireType.NUMERIC) {
      return Padding.ZERO_LEFT;
    } else {
      return Padding.NONE;
    }
  }

  private static int checkedEnd(int start, int length) {
    try {
      return Math.addExact(start, length - 1);
    } catch (ArithmeticException exception) {
      throw new LayoutValidationException("field end offset overflow", exception);
    }
  }
}
