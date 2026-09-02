package dev.codex.schubert.nk.protocol.layout.media;

import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadData;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;
import java.util.Map;

/** Generated named wire record. Trace: SS 323; layouts ANLRSP01. */
public record AnimationListResponseData(int totalCount) implements PayloadData {
  public AnimationListResponseData {
  }

  public static AnimationListResponseData from(FieldValueSet fields) {
    return new AnimationListResponseData(
        TypedFieldValues.requiredInt(fields, "Total count"));
  }

  @Override
  public FieldValueSet fields() {
    return new FieldValueSet(
        Map.ofEntries(
            Map.entry("Total count", TypedFieldValues.numeric(totalCount))));
  }

  @Override
  public String toString() {
    return "AnimationListResponseData[REDACTED]";
  }
}
