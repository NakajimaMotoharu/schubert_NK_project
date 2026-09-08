package dev.codex.schubert.nk.protocol.file;

import java.util.Objects;
import java.util.regex.Pattern;

/** Sanitized content metadata returned after a large-result write. */
public record LargeResultContent(int recordCount, long byteLength, String sha256) {
  private static final Pattern HASH = Pattern.compile("[0-9a-f]{64}");

  public LargeResultContent {
    Objects.requireNonNull(sha256, "sha256");
    if (recordCount < 1
        || recordCount > LargeResultDescriptor.MAXIMUM_RECORD_COUNT
        || byteLength != (long) LargeResultDescriptor.RECORD_LENGTH * recordCount
        || !HASH.matcher(sha256).matches()) {
      throw new IllegalArgumentException("large-result content metadata is invalid");
    }
  }
}
