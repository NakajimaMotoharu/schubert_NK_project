package dev.codex.schubert.nk.protocol.file;

import java.util.Objects;

/** Root-independent MEDIA1024 values. Textual output redacts path/name/hash. */
public final class MediaDescriptor {
  private final MediaType mediaType;
  private final String logicalId;
  private final String storageRelativePath;
  private final String fileName;
  private final long byteLength;
  private final String sha256;
  private final String mimeType;
  private final ContentDisposition disposition;

  public MediaDescriptor(
      MediaType mediaType,
      String logicalId,
      String storageRelativePath,
      String fileName,
      long byteLength,
      String sha256,
      String mimeType,
      ContentDisposition disposition) {
    this.mediaType = Objects.requireNonNull(mediaType, "mediaType");
    this.logicalId = Objects.requireNonNull(logicalId, "logicalId");
    this.storageRelativePath = Objects.requireNonNull(storageRelativePath, "storageRelativePath");
    this.fileName = Objects.requireNonNull(fileName, "fileName");
    this.byteLength = byteLength;
    this.sha256 = Objects.requireNonNull(sha256, "sha256");
    this.mimeType = Objects.requireNonNull(mimeType, "mimeType");
    this.disposition = Objects.requireNonNull(disposition, "disposition");
    MediaDescriptorValidator.validate(this);
  }

  public MediaType mediaType() {
    return mediaType;
  }

  public String logicalId() {
    return logicalId;
  }

  /** Validated wire value; never expose it to Browser, HTML, HTTP header, metric, or log. */
  public String storageRelativePath() {
    return storageRelativePath;
  }

  /** Validated metadata for a later RFC 5987 encoder; never concatenate it into a header. */
  public String fileName() {
    return fileName;
  }

  public long byteLength() {
    return byteLength;
  }

  public String sha256() {
    return sha256;
  }

  public String mimeType() {
    return mimeType;
  }

  public ContentDisposition disposition() {
    return disposition;
  }

  @Override
  public String toString() {
    return "MediaDescriptor[mediaType="
        + mediaType
        + ", logicalId=REDACTED, storageRelativePath=REDACTED, fileName=REDACTED, byteLength="
        + byteLength
        + ", sha256=REDACTED, mimeType="
        + mimeType
        + ", disposition="
        + disposition
        + ']';
  }
}
