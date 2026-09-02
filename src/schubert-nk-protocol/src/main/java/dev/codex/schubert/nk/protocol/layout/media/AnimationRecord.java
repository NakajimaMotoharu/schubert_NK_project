package dev.codex.schubert.nk.protocol.layout.media;

import dev.codex.schubert.nk.protocol.layout.FieldValue;
import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadRecord;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;

/** Generated named wire record. Trace: SS 323; layouts ANLRSP01. */
public record AnimationRecord(FieldValue.Text videoId,
    FieldValue.Text title,
    FieldValue.Text category,
    FieldValue.Text displayPath,
    FieldValue.Numeric fileByteLength,
    Optional<FieldValue.Text> parentMainId,
    FieldValue.Numeric displayOrder) implements PayloadRecord {
  public AnimationRecord {
    Objects.requireNonNull(videoId, "videoId");
    Objects.requireNonNull(title, "title");
    Objects.requireNonNull(category, "category");
    Objects.requireNonNull(displayPath, "displayPath");
    Objects.requireNonNull(fileByteLength, "fileByteLength");
    Objects.requireNonNull(parentMainId, "parentMainId");
    Objects.requireNonNull(displayOrder, "displayOrder");
  }

  public static AnimationRecord from(FieldValueSet fields) {
    return new AnimationRecord(
        TypedFieldValues.requiredText(fields, "Video ID"),
        TypedFieldValues.requiredText(fields, "Title"),
        TypedFieldValues.requiredText(fields, "Category"),
        TypedFieldValues.requiredText(fields, "Display path"),
        TypedFieldValues.requiredNumeric(fields, "File byte長"),
        TypedFieldValues.optionalText(fields, "Parent main ID"),
        TypedFieldValues.requiredNumeric(fields, "Display order"));
  }

  @Override
  public FieldValueSet fields() {
    return new FieldValueSet(
        Map.ofEntries(
            Map.entry("Video ID", videoId),
            Map.entry("Title", title),
            Map.entry("Category", category),
            Map.entry("Display path", displayPath),
            Map.entry("File byte長", fileByteLength),
            Map.entry("Parent main ID", TypedFieldValues.orUnset(parentMainId)),
            Map.entry("Display order", displayOrder)));
  }
}
