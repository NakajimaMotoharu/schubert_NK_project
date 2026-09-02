package dev.codex.schubert.nk.protocol.layout.media;

import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadData;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;
import java.util.Map;

/** Generated named wire record. Trace: SS 323; layouts MTRRSP01. */
public record MusicTrackResponseData(long totalCount) implements PayloadData {
  public MusicTrackResponseData {
    TypedFieldValues.requireUnsignedRange("totalCount", totalCount, 9);
  }

  public static MusicTrackResponseData from(FieldValueSet fields) {
    return new MusicTrackResponseData(
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
    return "MusicTrackResponseData[REDACTED]";
  }
}
