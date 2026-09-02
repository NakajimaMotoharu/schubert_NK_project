package dev.codex.schubert.nk.protocol.layout.media;

import dev.codex.schubert.nk.protocol.layout.FieldValue;
import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadRecord;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;
import java.util.Map;
import java.util.Objects;

/** Generated named wire record. Trace: SS 323; layouts MCSRSP01. */
public record MusicSectionRecord(FieldValue.Text section,
    FieldValue.Numeric trackCount) implements PayloadRecord {
  public MusicSectionRecord {
    Objects.requireNonNull(section, "section");
    Objects.requireNonNull(trackCount, "trackCount");
  }

  public static MusicSectionRecord from(FieldValueSet fields) {
    return new MusicSectionRecord(
        TypedFieldValues.requiredText(fields, "Section"),
        TypedFieldValues.requiredNumeric(fields, "Track件数"));
  }

  @Override
  public FieldValueSet fields() {
    return new FieldValueSet(
        Map.ofEntries(
            Map.entry("Section", section),
            Map.entry("Track件数", trackCount)));
  }
}
