package dev.codex.schubert.nk.protocol.file;

import java.util.Objects;

/** Root-independent MEDIA1024 values. Textual output redacts path/name/hash. */
public final class MediaDescriptor {
  private final MediaType retainedMediaType;
  private final String retainedLogicalId;
  private final String retainedStorageRelativePath;
  private final String retainedFileName;
  private final long retainedByteLength;
  private final String retainedSha256;
  private final String retainedMimeType;
  private final ContentDisposition retainedDisposition;

  public MediaDescriptor(
      MediaType mediaType,
      String logicalId,
      String storageRelativePath,
      String fileName,
      long byteLength,
      String sha256,
      String mimeType,
      ContentDisposition disposition) {
    this.retainedMediaType = Objects.requireNonNull(mediaType, "mediaType");
    this.retainedLogicalId = Objects.requireNonNull(logicalId, "logicalId");
    this.retainedStorageRelativePath =
        Objects.requireNonNull(storageRelativePath, "storageRelativePath");
    this.retainedFileName = Objects.requireNonNull(fileName, "fileName");
    this.retainedByteLength = byteLength;
    this.retainedSha256 = Objects.requireNonNull(sha256, "sha256");
    this.retainedMimeType = Objects.requireNonNull(mimeType, "mimeType");
    this.retainedDisposition = Objects.requireNonNull(disposition, "disposition");
    MediaDescriptorValidator.validate(this);
  }

  public MediaType mediaType() {
    return retainedMediaType;
  }

  public String logicalId() {
    return retainedLogicalId;
  }

  /** Validated wire value; never expose it to Browser, HTML, HTTP header, metric, or log. */
  public String storageRelativePath() {
    return retainedStorageRelativePath;
  }

  /** Validated metadata for a later RFC 5987 encoder; never concatenate it into a header. */
  public String fileName() {
    return retainedFileName;
  }

  public long byteLength() {
    return retainedByteLength;
  }

  public String sha256() {
    return retainedSha256;
  }

  public String mimeType() {
    return retainedMimeType;
  }

  public ContentDisposition disposition() {
    return retainedDisposition;
  }

  @Override
  public String toString() {
    return "MediaDescriptor[mediaType="
        + retainedMediaType
        + ", logicalId=REDACTED, storageRelativePath=REDACTED, fileName=REDACTED, byteLength="
        + retainedByteLength
        + ", sha256=REDACTED, mimeType="
        + retainedMimeType
        + ", disposition="
        + retainedDisposition
        + ']';
  }
}
