package dev.codex.schubert.nk.protocol.layout.media;

import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadRecord;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;
import dev.codex.schubert.nk.protocol.layout.semantic.DisplayPath;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;

/** Generated named wire record. Trace: SS 323; layouts MTRRSP01. */
public record MusicTrackRecord(String trackId,
    String title,
    String category,
    String section,
    DisplayPath displayPath,
    long fileByteLength,
    Optional<String> pairKey,
    String pairRole,
    long displayOrder) implements PayloadRecord {
  public MusicTrackRecord {
    Objects.requireNonNull(trackId, "trackId");
    Objects.requireNonNull(title, "title");
    Objects.requireNonNull(category, "category");
    Objects.requireNonNull(section, "section");
    Objects.requireNonNull(displayPath, "displayPath");
    Objects.requireNonNull(pairKey, "pairKey");
    Objects.requireNonNull(pairRole, "pairRole");
  }

  public static MusicTrackRecord from(FieldValueSet fields) {
    return new MusicTrackRecord(
        TypedFieldValues.requiredString(fields, "Track ID"),
        TypedFieldValues.requiredString(fields, "Title"),
        TypedFieldValues.requiredString(fields, "Category"),
        TypedFieldValues.requiredString(fields, "Section"),
        TypedFieldValues.requiredDisplayPath(fields, "Display path"),
        TypedFieldValues.requiredLong(fields, "File byte長"),
        TypedFieldValues.optionalString(fields, "Pair key"),
        TypedFieldValues.requiredString(fields, "Pair role"),
        TypedFieldValues.requiredLong(fields, "Display order"));
  }

  @Override
  public FieldValueSet fields() {
    return new FieldValueSet(
        Map.ofEntries(
            Map.entry("Track ID", TypedFieldValues.text(trackId)),
            Map.entry("Title", TypedFieldValues.text(title)),
            Map.entry("Category", TypedFieldValues.text(category)),
            Map.entry("Section", TypedFieldValues.text(section)),
            Map.entry("Display path", TypedFieldValues.displayPath(displayPath)),
            Map.entry("File byte長", TypedFieldValues.numeric(fileByteLength)),
            Map.entry("Pair key", TypedFieldValues.optionalStringValue(pairKey)),
            Map.entry("Pair role", TypedFieldValues.text(pairRole)),
            Map.entry("Display order", TypedFieldValues.numeric(displayOrder))));
  }

  @Override
  public String toString() {
    return "MusicTrackRecord[REDACTED]";
  }
}
