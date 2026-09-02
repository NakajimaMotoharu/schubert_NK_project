package dev.codex.schubert.nk.protocol.layout;

import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.Objects;
import java.util.Set;

/** Immutable named field values for one data or record area. */
public final class FieldValueSet {
  private final Map<String, FieldValue> values;

  public FieldValueSet(Map<String, FieldValue> source) {
    Objects.requireNonNull(source, "source");
    LinkedHashMap<String, FieldValue> copy = new LinkedHashMap<>();
    for (Map.Entry<String, FieldValue> entry : source.entrySet()) {
      String name = Objects.requireNonNull(entry.getKey(), "field name");
      FieldValue value = Objects.requireNonNull(entry.getValue(), "field value");
      if (name.isBlank()) {
        throw new LayoutValidationException("field value name must not be blank");
      }
      copy.put(name, value);
    }
    values = Collections.unmodifiableMap(copy);
  }

  public static FieldValueSet empty() {
    return new FieldValueSet(Map.of());
  }

  public Set<String> names() {
    return values.keySet();
  }

  public FieldValue getOrUnset(String name) {
    Objects.requireNonNull(name, "name");
    return values.getOrDefault(name, FieldValue.Unset.INSTANCE);
  }

  public int size() {
    return values.size();
  }

  @Override
  public boolean equals(Object other) {
    return this == other
        || (other instanceof FieldValueSet that && values.equals(that.values));
  }

  @Override
  public int hashCode() {
    return values.hashCode();
  }

  @Override
  public String toString() {
    return "FieldValueSet[names=" + values.keySet() + ']';
  }
}
