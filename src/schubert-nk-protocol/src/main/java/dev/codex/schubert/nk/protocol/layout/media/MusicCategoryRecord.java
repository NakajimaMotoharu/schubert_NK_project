package dev.codex.schubert.nk.protocol.layout.media;

import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadRecord;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;
import java.util.Map;
import java.util.Objects;

/** Generated named wire record. Trace: SS 323; layouts MCTRSP01. */
public record MusicCategoryRecord(String category,
    int trackCount) implements PayloadRecord {
  public MusicCategoryRecord {
    Objects.requireNonNull(category, "category");
    TypedFieldValues.requireUnsignedRange("trackCount", trackCount, 6);
  }

  public static MusicCategoryRecord from(FieldValueSet fields) {
    return new MusicCategoryRecord(
        TypedFieldValues.requiredString(fields, "Category"),
        TypedFieldValues.requiredInt(fields, "Track件数"));
  }

  @Override
  public FieldValueSet fields() {
    return new FieldValueSet(
        Map.ofEntries(
            Map.entry("Category", TypedFieldValues.text(category)),
            Map.entry("Track件数", TypedFieldValues.numeric(trackCount))));
  }

  @Override
  public String toString() {
    return "MusicCategoryRecord[REDACTED]";
  }
}
