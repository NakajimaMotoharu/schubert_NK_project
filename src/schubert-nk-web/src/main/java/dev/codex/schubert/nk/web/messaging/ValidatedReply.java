package dev.codex.schubert.nk.web.messaging;

import java.util.Objects;
import java.util.UUID;

/**
 * Immutable reply transport result produced only after JMS and fixed-width validation.
 *
 * <p>Trace: NK-MSG-001; RD MQ-004/MQ-005; UI 231; SS 321 section 9; PT-JMS-005/008.
 */
public record ValidatedReply(UUID correlationId, byte[] body) {
  public ValidatedReply {
    Objects.requireNonNull(correlationId, "correlationId");
    Objects.requireNonNull(body, "body");
    body = body.clone();
  }

  @Override
  public byte[] body() {
    return body.clone();
  }

  @Override
  public String toString() {
    return "ValidatedReply[correlationId/body=<redacted>]";
  }
}
