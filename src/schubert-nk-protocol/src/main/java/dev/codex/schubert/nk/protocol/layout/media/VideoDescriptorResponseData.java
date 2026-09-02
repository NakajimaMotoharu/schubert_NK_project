package dev.codex.schubert.nk.protocol.layout.media;

import dev.codex.schubert.nk.protocol.layout.FieldValue;
import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadData;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;
import java.util.Map;
import java.util.Objects;

/** Generated named wire record. Trace: SS 323; layouts VIDRSP01. */
public record VideoDescriptorResponseData(FieldValue.Text mediaLogicalId,
    FieldValue.Text storageRelativePath,
    FieldValue.Text fileName,
    FieldValue.Numeric fileByteLength,
    FieldValue.Text sha256,
    FieldValue.Text mimeType,
    FieldValue.Text contentDisposition,
    FieldValue.Text title,
    FieldValue.Text category,
    FieldValue.Text displayPath) implements PayloadData {
  public VideoDescriptorResponseData {
    Objects.requireNonNull(mediaLogicalId, "mediaLogicalId");
    Objects.requireNonNull(storageRelativePath, "storageRelativePath");
    Objects.requireNonNull(fileName, "fileName");
    Objects.requireNonNull(fileByteLength, "fileByteLength");
    Objects.requireNonNull(sha256, "sha256");
    Objects.requireNonNull(mimeType, "mimeType");
    Objects.requireNonNull(contentDisposition, "contentDisposition");
    Objects.requireNonNull(title, "title");
    Objects.requireNonNull(category, "category");
    Objects.requireNonNull(displayPath, "displayPath");
  }

  public static VideoDescriptorResponseData from(FieldValueSet fields) {
    return new VideoDescriptorResponseData(
        TypedFieldValues.requiredText(fields, "Media logical ID"),
        TypedFieldValues.requiredText(fields, "Storage relative path"),
        TypedFieldValues.requiredText(fields, "File name"),
        TypedFieldValues.requiredNumeric(fields, "File byte長"),
        TypedFieldValues.requiredText(fields, "SHA-256"),
        TypedFieldValues.requiredText(fields, "MIME type"),
        TypedFieldValues.requiredText(fields, "Content disposition"),
        TypedFieldValues.requiredText(fields, "Title"),
        TypedFieldValues.requiredText(fields, "Category"),
        TypedFieldValues.requiredText(fields, "Display path"));
  }

  @Override
  public FieldValueSet fields() {
    return new FieldValueSet(
        Map.ofEntries(
            Map.entry("Media logical ID", mediaLogicalId),
            Map.entry("Storage relative path", storageRelativePath),
            Map.entry("File name", fileName),
            Map.entry("File byte長", fileByteLength),
            Map.entry("SHA-256", sha256),
            Map.entry("MIME type", mimeType),
            Map.entry("Content disposition", contentDisposition),
            Map.entry("Title", title),
            Map.entry("Category", category),
            Map.entry("Display path", displayPath)));
  }
}
