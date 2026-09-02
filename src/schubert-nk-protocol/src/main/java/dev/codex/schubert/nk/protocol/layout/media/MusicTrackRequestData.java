package dev.codex.schubert.nk.protocol.layout.media;

import dev.codex.schubert.nk.protocol.layout.FieldValue;
import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadData;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;
import java.util.Map;
import java.util.Objects;

/** Generated named wire record. Trace: SS 323; layouts MTRREQ01. */
public record MusicTrackRequestData(FieldValue.Text category,
    FieldValue.Text section) implements PayloadData {
  public MusicTrackRequestData {
    Objects.requireNonNull(category, "category");
    Objects.requireNonNull(section, "section");
  }

  public static MusicTrackRequestData from(FieldValueSet fields) {
    return new MusicTrackRequestData(
        TypedFieldValues.requiredText(fields, "Category"),
        TypedFieldValues.requiredText(fields, "Section"));
  }

  @Override
  public FieldValueSet fields() {
    return new FieldValueSet(
        Map.ofEntries(
            Map.entry("Category", category),
            Map.entry("Section", section)));
  }
}
