package dev.codex.schubert.nk.protocol.layout.media;

import dev.codex.schubert.nk.protocol.layout.FieldValue;
import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadRecord;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;

/** Generated named wire record. Trace: SS 323; layouts MTRRSP01. */
public record MusicTrackRecord(FieldValue.Text trackId,
    FieldValue.Text title,
    FieldValue.Text category,
    FieldValue.Text section,
    FieldValue.Text displayPath,
    FieldValue.Numeric fileByteLength,
    Optional<FieldValue.Text> pairKey,
    FieldValue.Text pairRole,
    FieldValue.Numeric displayOrder) implements PayloadRecord {
  public MusicTrackRecord {
    Objects.requireNonNull(trackId, "trackId");
    Objects.requireNonNull(title, "title");
    Objects.requireNonNull(category, "category");
    Objects.requireNonNull(section, "section");
    Objects.requireNonNull(displayPath, "displayPath");
    Objects.requireNonNull(fileByteLength, "fileByteLength");
    Objects.requireNonNull(pairKey, "pairKey");
    Objects.requireNonNull(pairRole, "pairRole");
    Objects.requireNonNull(displayOrder, "displayOrder");
  }

  public static MusicTrackRecord from(FieldValueSet fields) {
    return new MusicTrackRecord(
        TypedFieldValues.requiredText(fields, "Track ID"),
        TypedFieldValues.requiredText(fields, "Title"),
        TypedFieldValues.requiredText(fields, "Category"),
        TypedFieldValues.requiredText(fields, "Section"),
        TypedFieldValues.requiredText(fields, "Display path"),
        TypedFieldValues.requiredNumeric(fields, "File byte長"),
        TypedFieldValues.optionalText(fields, "Pair key"),
        TypedFieldValues.requiredText(fields, "Pair role"),
        TypedFieldValues.requiredNumeric(fields, "Display order"));
  }

  @Override
  public FieldValueSet fields() {
    return new FieldValueSet(
        Map.ofEntries(
            Map.entry("Track ID", trackId),
            Map.entry("Title", title),
            Map.entry("Category", category),
            Map.entry("Section", section),
            Map.entry("Display path", displayPath),
            Map.entry("File byte長", fileByteLength),
            Map.entry("Pair key", TypedFieldValues.orUnset(pairKey)),
            Map.entry("Pair role", pairRole),
            Map.entry("Display order", displayOrder)));
  }
}
