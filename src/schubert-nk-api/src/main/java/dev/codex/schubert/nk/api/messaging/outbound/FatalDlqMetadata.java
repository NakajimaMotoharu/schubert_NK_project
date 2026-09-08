package dev.codex.schubert.nk.api.messaging.outbound;

import java.time.Instant;
import java.util.Objects;

/** Bounded non-secret fatal-rejection metadata. Trace: NK-MSG-001; SS 321 §11. */
public record FatalDlqMetadata(String errorCode, DetectedBy detectedBy, Instant detectedAt) {
  public FatalDlqMetadata {
    Objects.requireNonNull(errorCode, "errorCode");
    Objects.requireNonNull(detectedBy, "detectedBy");
    Objects.requireNonNull(detectedAt, "detectedAt");
    if (!errorCode.matches("[A-Z][A-Z0-9_]{0,31}")) {
      throw new IllegalArgumentException("DLQ error code is invalid");
    }
  }

  public enum DetectedBy {
    API_SYNC,
    API_WORK,
    API_WEB_LOG,
    WEB_REPLY
  }
}
