package dev.codex.schubert.nk.protocol.layout.media;

import dev.codex.schubert.nk.protocol.layout.FieldValue;
import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadData;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;
import java.util.Map;
import java.util.Objects;

/** Generated named wire record. Trace: SS 323; layouts MCTRSP01. */
public record MusicCategoryResponseData(FieldValue.Numeric totalCount) implements PayloadData {
  public MusicCategoryResponseData {
    Objects.requireNonNull(totalCount, "totalCount");
  }

  public static MusicCategoryResponseData from(FieldValueSet fields) {
    return new MusicCategoryResponseData(
        TypedFieldValues.requiredNumeric(fields, "Total count"));
  }

  @Override
  public FieldValueSet fields() {
    return new FieldValueSet(
        Map.ofEntries(
            Map.entry("Total count", totalCount)));
  }
}
