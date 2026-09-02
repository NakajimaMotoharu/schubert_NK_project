package dev.codex.schubert.nk.protocol.layout.media;

import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadRecord;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;
import java.util.Map;
import java.util.Objects;

/** Generated named wire record. Trace: SS 323; layouts MCSRSP01. */
public record MusicSectionRecord(String section,
    int trackCount) implements PayloadRecord {
  public MusicSectionRecord {
    Objects.requireNonNull(section, "section");
  }

  public static MusicSectionRecord from(FieldValueSet fields) {
    return new MusicSectionRecord(
        TypedFieldValues.requiredString(fields, "Section"),
        TypedFieldValues.requiredInt(fields, "Track件数"));
  }

  @Override
  public FieldValueSet fields() {
    return new FieldValueSet(
        Map.ofEntries(
            Map.entry("Section", TypedFieldValues.text(section)),
            Map.entry("Track件数", TypedFieldValues.numeric(trackCount))));
  }

  @Override
  public String toString() {
    return "MusicSectionRecord[REDACTED]";
  }
}
