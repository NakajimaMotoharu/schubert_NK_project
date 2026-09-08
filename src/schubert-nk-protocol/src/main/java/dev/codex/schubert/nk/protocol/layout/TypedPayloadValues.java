package dev.codex.schubert.nk.protocol.layout;

import java.util.List;
import java.util.Objects;

/** One payload represented by the named data/record types specified in SS 323. */
public record TypedPayloadValues(LayoutId layoutId, PayloadData data, List<PayloadRecord> records) {
  public TypedPayloadValues {
    Objects.requireNonNull(layoutId, "layoutId");
    Objects.requireNonNull(data, "data");
    records = List.copyOf(records);
  }

  @Override
  public String toString() {
    return "TypedPayloadValues[layoutId=" + layoutId + ", recordCount=" + records.size() + ']';
  }
}
