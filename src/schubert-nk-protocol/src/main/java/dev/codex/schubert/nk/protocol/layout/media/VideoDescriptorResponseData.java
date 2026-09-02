package dev.codex.schubert.nk.protocol.layout.media;

import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadData;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;
import dev.codex.schubert.nk.protocol.layout.semantic.DisplayPath;
import dev.codex.schubert.nk.protocol.layout.semantic.RelativePath;
import dev.codex.schubert.nk.protocol.layout.semantic.Sha256Hex;
import java.util.Map;
import java.util.Objects;

/** Generated named wire record. Trace: SS 323; layouts VIDRSP01. */
public record VideoDescriptorResponseData(String mediaLogicalId,
    RelativePath storageRelativePath,
    String fileName,
    long fileByteLength,
    Sha256Hex sha256,
    String mimeType,
    String contentDisposition,
    String title,
    String category,
    DisplayPath displayPath) implements PayloadData {
  public VideoDescriptorResponseData {
    Objects.requireNonNull(mediaLogicalId, "mediaLogicalId");
    Objects.requireNonNull(storageRelativePath, "storageRelativePath");
    Objects.requireNonNull(fileName, "fileName");
    Objects.requireNonNull(sha256, "sha256");
    Objects.requireNonNull(mimeType, "mimeType");
    Objects.requireNonNull(contentDisposition, "contentDisposition");
    Objects.requireNonNull(title, "title");
    Objects.requireNonNull(category, "category");
    Objects.requireNonNull(displayPath, "displayPath");
  }

  public static VideoDescriptorResponseData from(FieldValueSet fields) {
    return new VideoDescriptorResponseData(
        TypedFieldValues.requiredString(fields, "Media logical ID"),
        TypedFieldValues.requiredRelativePath(fields, "Storage relative path"),
        TypedFieldValues.requiredString(fields, "File name"),
        TypedFieldValues.requiredLong(fields, "File byte長"),
        TypedFieldValues.requiredSha256(fields, "SHA-256"),
        TypedFieldValues.requiredString(fields, "MIME type"),
        TypedFieldValues.requiredString(fields, "Content disposition"),
        TypedFieldValues.requiredString(fields, "Title"),
        TypedFieldValues.requiredString(fields, "Category"),
        TypedFieldValues.requiredDisplayPath(fields, "Display path"));
  }

  @Override
  public FieldValueSet fields() {
    return new FieldValueSet(
        Map.ofEntries(
            Map.entry("Media logical ID", TypedFieldValues.text(mediaLogicalId)),
            Map.entry("Storage relative path", TypedFieldValues.relativePath(storageRelativePath)),
            Map.entry("File name", TypedFieldValues.text(fileName)),
            Map.entry("File byte長", TypedFieldValues.numeric(fileByteLength)),
            Map.entry("SHA-256", TypedFieldValues.sha256(sha256)),
            Map.entry("MIME type", TypedFieldValues.text(mimeType)),
            Map.entry("Content disposition", TypedFieldValues.text(contentDisposition)),
            Map.entry("Title", TypedFieldValues.text(title)),
            Map.entry("Category", TypedFieldValues.text(category)),
            Map.entry("Display path", TypedFieldValues.displayPath(displayPath))));
  }

  @Override
  public String toString() {
    return "VideoDescriptorResponseData[REDACTED]";
  }
}
