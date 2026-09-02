package dev.codex.schubert.nk.protocol.layout.media;

import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadRecord;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;
import dev.codex.schubert.nk.protocol.layout.semantic.AnimationCategory;
import dev.codex.schubert.nk.protocol.layout.semantic.DisplayPath;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;

/** Generated named wire record. Trace: SS 323; layouts ANLRSP01. */
public record AnimationRecord(String videoId,
    String title,
    AnimationCategory category,
    DisplayPath displayPath,
    long fileByteLength,
    Optional<String> parentMainId,
    int displayOrder) implements PayloadRecord {
  public AnimationRecord {
    Objects.requireNonNull(videoId, "videoId");
    Objects.requireNonNull(title, "title");
    Objects.requireNonNull(category, "category");
    Objects.requireNonNull(displayPath, "displayPath");
    TypedFieldValues.requireUnsignedRange("fileByteLength", fileByteLength, 12);
    Objects.requireNonNull(parentMainId, "parentMainId");
    TypedFieldValues.requireUnsignedRange("displayOrder", displayOrder, 4);
  }

  public static AnimationRecord from(FieldValueSet fields) {
    return new AnimationRecord(
        TypedFieldValues.requiredString(fields, "Video ID"),
        TypedFieldValues.requiredString(fields, "Title"),
        TypedFieldValues.requiredEnum(fields, "Category", AnimationCategory.class),
        TypedFieldValues.requiredDisplayPath(fields, "Display path"),
        TypedFieldValues.requiredLong(fields, "File byte長"),
        TypedFieldValues.optionalString(fields, "Parent main ID"),
        TypedFieldValues.requiredInt(fields, "Display order"));
  }

  @Override
  public FieldValueSet fields() {
    return new FieldValueSet(
        Map.ofEntries(
            Map.entry("Video ID", TypedFieldValues.text(videoId)),
            Map.entry("Title", TypedFieldValues.text(title)),
            Map.entry("Category", TypedFieldValues.enumValue(category)),
            Map.entry("Display path", TypedFieldValues.displayPath(displayPath)),
            Map.entry("File byte長", TypedFieldValues.numeric(fileByteLength)),
            Map.entry("Parent main ID", TypedFieldValues.optionalStringValue(parentMainId)),
            Map.entry("Display order", TypedFieldValues.numeric(displayOrder))));
  }

  @Override
  public String toString() {
    return "AnimationRecord[REDACTED]";
  }
}
