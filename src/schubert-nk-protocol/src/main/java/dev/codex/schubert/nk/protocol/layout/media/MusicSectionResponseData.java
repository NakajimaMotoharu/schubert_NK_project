package dev.codex.schubert.nk.protocol.layout.media;

import dev.codex.schubert.nk.protocol.layout.FieldValue;
import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadData;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;
import java.util.Map;
import java.util.Objects;

/** Generated named wire record. Trace: SS 323; layouts MCSRSP01. */
public record MusicSectionResponseData(FieldValue.Numeric totalCount) implements PayloadData {
  public MusicSectionResponseData {
    Objects.requireNonNull(totalCount, "totalCount");
  }

  public static MusicSectionResponseData from(FieldValueSet fields) {
    return new MusicSectionResponseData(
        TypedFieldValues.requiredNumeric(fields, "Total count"));
  }

  @Override
  public FieldValueSet fields() {
    return new FieldValueSet(
        Map.ofEntries(
            Map.entry("Total count", totalCount)));
  }
}
