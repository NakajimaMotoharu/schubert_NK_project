package dev.codex.schubert.nk.api.messaging.outbound;

import java.time.Instant;
import java.util.Objects;
import java.util.Optional;
import java.util.UUID;

/**
 * Immutable original QWK identity, never dispatch identity or provider exception text.
 * NK-MSG-002/NK-QST-001; ASY001/MQ008; UI242; SS312/321/324/331/SSC155; PT-QST-DLQ-MODEL/DB/JMS.
 * Worker samples UTC at PostgreSQL microsecond precision.
 */
public record OutboxDlqMetadata(
    UUID originalMessageId,
    String originalTransportId,
    int deliveryCount,
    String errorCode,
    Instant detectedAt) {
  public static final String RETRY_EXHAUSTED = "QUESTION_RETRY_EXHAUSTED";
  private static final Instant MINIMUM = Instant.parse("0001-01-01T00:00:00Z");
  private static final Instant MAXIMUM = Instant.parse("9999-12-31T23:59:59.999999Z");

  public OutboxDlqMetadata {
    Objects.requireNonNull(originalMessageId, "originalMessageId");
    Objects.requireNonNull(originalTransportId, "originalTransportId");
    Objects.requireNonNull(errorCode, "errorCode");
    Objects.requireNonNull(detectedAt, "detectedAt");
    if (originalTransportId.isBlank()
        || originalTransportId.length() > 128
        || originalTransportId.chars().anyMatch(c -> c < 0x20 || c > 0x7e))
      throw new IllegalArgumentException("DLQ transport identity is outside its bounded contract");
    if (deliveryCount < 1)
      throw new IllegalArgumentException("DLQ delivery count must be positive");
    if (!errorCode.equals(RETRY_EXHAUSTED))
      throw new IllegalArgumentException("DLQ business error code is unsupported");
    if (detectedAt.isBefore(MINIMUM)
        || detectedAt.isAfter(MAXIMUM)
        || detectedAt.getNano() % 1000 != 0)
      throw new IllegalArgumentException("DLQ detection time must be bounded UTC microseconds");
  }

  /** Log allowlist deliberately omits transport/message identifiers and detection details. */
  @Override
  public String toString() {
    return "OutboxDlqMetadata[<redacted>]";
  }

  static Optional<OutboxDlqMetadata> requireProfile(
      UUID dispatchId,
      OutboxDestination destination,
      String layout,
      String version,
      int length,
      Optional<OutboxDlqMetadata> metadata) {
    Objects.requireNonNull(metadata, "dlqMetadata");
    if ((destination == OutboxDestination.DLQ) != metadata.isPresent())
      throw new IllegalArgumentException("outbox destination and DLQ metadata disagree");
    if (metadata.isPresent()
        && (metadata.orElseThrow().originalMessageId().equals(dispatchId)
            || !layout.equals("QWKREQ01")
            || !version.equals("001")
            || length != 320))
      throw new IllegalArgumentException("DLQ dispatch profile is invalid");
    return metadata;
  }
}
