package dev.codex.schubert.nk.protocol.layout.scenario;

import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadData;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;
import java.util.Map;

/** Generated named wire record. Trace: SS 323; layouts SPKRSP01. */
public record SpeakerListResponseData(long totalCount) implements PayloadData {
  public SpeakerListResponseData {
  }

  public static SpeakerListResponseData from(FieldValueSet fields) {
    return new SpeakerListResponseData(
        TypedFieldValues.requiredLong(fields, "Total count"));
  }

  @Override
  public FieldValueSet fields() {
    return new FieldValueSet(
        Map.ofEntries(
            Map.entry("Total count", TypedFieldValues.numeric(totalCount))));
  }

  @Override
  public String toString() {
    return "SpeakerListResponseData[REDACTED]";
  }
}
