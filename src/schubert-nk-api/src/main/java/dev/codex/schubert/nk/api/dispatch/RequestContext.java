package dev.codex.schubert.nk.api.dispatch;

import dev.codex.schubert.nk.api.security.AuthenticatedActor;
import java.time.Instant;
import java.util.Objects;
import java.util.Optional;
import java.util.UUID;

/**
 * Verified metadata supplied to a synchronous handler by its caller.
 *
 * <p>NK-MSG-001, MQ-003/MQ-006, UI232, SS311 §6.2 and SS312 §3.3, SSC-477, PT-JMS-HCTX001..004. The
 * caller supplies the actor only after the applicable authentication step.
 */
public record RequestContext(
    UUID messageId,
    UUID correlationId,
    Optional<UUID> requestId,
    Optional<AuthenticatedActor> actor,
    Instant receivedAt,
    int deliveryCount) {

  private static final int MINIMUM_DELIVERY_COUNT = 1;

  public RequestContext {
    Objects.requireNonNull(messageId, "message ID");
    Objects.requireNonNull(correlationId, "correlation ID");
    Objects.requireNonNull(requestId, "HTTP request ID");
    Objects.requireNonNull(actor, "authenticated actor");
    Objects.requireNonNull(receivedAt, "received timestamp");
    if (!messageId.equals(correlationId)) {
      throw new IllegalArgumentException("root request identity is inconsistent");
    }
    if (deliveryCount < MINIMUM_DELIVERY_COUNT) {
      throw new IllegalArgumentException("delivery count must be positive");
    }
  }

  @Override
  public String toString() {
    return "RequestContext[<redacted>]";
  }
}
