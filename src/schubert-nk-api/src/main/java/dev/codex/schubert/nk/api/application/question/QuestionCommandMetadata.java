package dev.codex.schubert.nk.api.application.question;

import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.Objects;
import java.util.UUID;

/** Wire trace and one UTC microsecond operation time. SS332/351; PG-D-331; PT-QRY028/NTF012. */
public record QuestionCommandMetadata(UUID messageId, UUID correlationId, Instant at) {
  public QuestionCommandMetadata {
    Objects.requireNonNull(messageId, "messageId");
    Objects.requireNonNull(correlationId, "correlationId");
    at = Objects.requireNonNull(at, "at").truncatedTo(ChronoUnit.MICROS);
    if (at.isBefore(Instant.parse("0001-01-01T00:00:00Z"))
        || at.isAfter(Instant.parse("9999-12-31T23:59:59.999999Z")))
      throw new IllegalArgumentException("command time is outside UTC range");
  }

  @Override
  public String toString() {
    return "QuestionCommandMetadata[REDACTED]";
  }
}
