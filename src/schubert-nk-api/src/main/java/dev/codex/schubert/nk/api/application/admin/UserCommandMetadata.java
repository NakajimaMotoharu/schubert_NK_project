package dev.codex.schubert.nk.api.application.admin;

import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.Objects;
import java.util.UUID;

/** One operation timestamp and wire trace, not raw token. NK-ADM-001; SS332/351; PT-ADM-021/023. */
public record UserCommandMetadata(UUID messageId, UUID correlationId, Instant at) {
  public UserCommandMetadata {
    Objects.requireNonNull(messageId, "messageId");
    Objects.requireNonNull(correlationId, "correlationId");
    at = Objects.requireNonNull(at, "at").truncatedTo(ChronoUnit.MICROS);
  }

  @Override
  public String toString() {
    return "UserCommandMetadata[REDACTED]";
  }
}
