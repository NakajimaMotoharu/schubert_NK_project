package dev.codex.schubert.nk.protocol.layout.media;

import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadData;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;
import dev.codex.schubert.nk.protocol.layout.semantic.AnimationListCategory;
import java.util.Map;
import java.util.Objects;

/** Generated named wire record. Trace: SS 323; layouts ANLREQ01. */
public record AnimationListRequestData(AnimationListCategory category) implements PayloadData {
  public AnimationListRequestData {
    Objects.requireNonNull(category, "category");
  }

  public static AnimationListRequestData from(FieldValueSet fields) {
    return new AnimationListRequestData(
        TypedFieldValues.requiredEnum(fields, "Category", AnimationListCategory.class));
  }

  @Override
  public FieldValueSet fields() {
    return new FieldValueSet(
        Map.ofEntries(
            Map.entry("Category", TypedFieldValues.enumValue(category))));
  }

  @Override
  public String toString() {
    return "AnimationListRequestData[REDACTED]";
  }
}
