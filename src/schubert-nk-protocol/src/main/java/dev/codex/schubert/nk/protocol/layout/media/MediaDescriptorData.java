package dev.codex.schubert.nk.protocol.layout.media;

import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadData;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;
import dev.codex.schubert.nk.protocol.layout.semantic.ContentDisposition;
import dev.codex.schubert.nk.protocol.layout.semantic.MediaMimeType;
import dev.codex.schubert.nk.protocol.layout.semantic.RelativePath;
import dev.codex.schubert.nk.protocol.layout.semantic.Sha256Hex;
import java.util.Map;
import java.util.Objects;

/** Generated named wire record. Trace: SS 323; layouts AUDRSP01, MEDRSP01. */
public record MediaDescriptorData(String mediaLogicalId,
    RelativePath storageRelativePath,
    String fileName,
    long fileByteLength,
    Sha256Hex sha256,
    MediaMimeType mimeType,
    ContentDisposition contentDisposition) implements PayloadData {
  public MediaDescriptorData {
    Objects.requireNonNull(mediaLogicalId, "mediaLogicalId");
    Objects.requireNonNull(storageRelativePath, "storageRelativePath");
    Objects.requireNonNull(fileName, "fileName");
    TypedFieldValues.requireUnsignedRange("fileByteLength", fileByteLength, 12);
    Objects.requireNonNull(sha256, "sha256");
    Objects.requireNonNull(mimeType, "mimeType");
    Objects.requireNonNull(contentDisposition, "contentDisposition");
  }

  public static MediaDescriptorData from(FieldValueSet fields) {
    return new MediaDescriptorData(
        TypedFieldValues.requiredString(fields, "Media logical ID"),
        TypedFieldValues.requiredRelativePath(fields, "Storage relative path"),
        TypedFieldValues.requiredString(fields, "File name"),
        TypedFieldValues.requiredLong(fields, "File byte長"),
        TypedFieldValues.requiredSha256(fields, "SHA-256"),
        TypedFieldValues.requiredEnum(fields, "MIME type", MediaMimeType.class),
        TypedFieldValues.requiredEnum(fields, "Content disposition", ContentDisposition.class));
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
            Map.entry("MIME type", TypedFieldValues.enumValue(mimeType)),
            Map.entry("Content disposition", TypedFieldValues.enumValue(contentDisposition))));
  }

  @Override
  public String toString() {
    return "MediaDescriptorData[REDACTED]";
  }
}
