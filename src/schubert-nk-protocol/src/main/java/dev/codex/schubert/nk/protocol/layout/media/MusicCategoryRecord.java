package dev.codex.schubert.nk.protocol.layout.media;

import dev.codex.schubert.nk.protocol.layout.FieldValue;
import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadRecord;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;
import java.util.Map;
import java.util.Objects;

/** Generated named wire record. Trace: SS 323; layouts MCTRSP01. */
public record MusicCategoryRecord(FieldValue.Text category,
    FieldValue.Numeric trackCount) implements PayloadRecord {
  public MusicCategoryRecord {
    Objects.requireNonNull(category, "category");
    Objects.requireNonNull(trackCount, "trackCount");
  }

  public static MusicCategoryRecord from(FieldValueSet fields) {
    return new MusicCategoryRecord(
        TypedFieldValues.requiredText(fields, "Category"),
        TypedFieldValues.requiredNumeric(fields, "Track件数"));
  }

  @Override
  public FieldValueSet fields() {
    return new FieldValueSet(
        Map.ofEntries(
            Map.entry("Category", category),
            Map.entry("Track件数", trackCount)));
  }
}
