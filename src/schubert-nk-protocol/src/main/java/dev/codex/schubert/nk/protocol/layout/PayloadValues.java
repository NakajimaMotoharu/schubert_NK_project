package dev.codex.schubert.nk.protocol.layout;

import java.util.List;
import java.util.Objects;

/** Typed field values for one complete payload. */
public record PayloadValues(
    LayoutId layoutId, FieldValueSet data, List<FieldValueSet> records) {
  public PayloadValues {
    Objects.requireNonNull(layoutId, "layoutId");
    Objects.requireNonNull(data, "data");
    records = List.copyOf(records);
  }

  @Override
  public String toString() {
    return "PayloadValues[layoutId=" + layoutId + ", recordCount=" + records.size() + ']';
  }
}
