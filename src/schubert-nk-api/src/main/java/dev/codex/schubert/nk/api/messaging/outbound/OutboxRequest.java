package dev.codex.schubert.nk.api.messaging.outbound;

import java.time.Instant;
import java.util.Objects;
import java.util.Optional;
import java.util.UUID;

/** Application-outbox INSERT request; identity is validated again before JMS send. */
public final class OutboxRequest {
  private final UUID messageId;
  private final UUID correlationId;
  private final OutboxDestination destination;
  private final String layoutId;
  private final String layoutVersion;
  private final byte[] body;
  private final Instant nextAttemptAt;
  private final Instant createdAt;
  private final Optional<OutboxDlqMetadata> dlqMetadata;

  public OutboxRequest(
      UUID messageId,
      UUID correlationId,
      OutboxDestination destination,
      String layoutId,
      String layoutVersion,
      byte[] body,
      Instant nextAttemptAt,
      Instant createdAt) {
    this(
        messageId,
        correlationId,
        destination,
        layoutId,
        layoutVersion,
        body,
        nextAttemptAt,
        createdAt,
        Optional.empty());
  }

  public OutboxRequest(
      UUID messageId,
      UUID correlationId,
      OutboxDestination destination,
      String layoutId,
      String layoutVersion,
      byte[] body,
      Instant nextAttemptAt,
      Instant createdAt,
      Optional<OutboxDlqMetadata> dlqMetadata) {
    this.messageId = Objects.requireNonNull(messageId, "messageId");
    this.correlationId = Objects.requireNonNull(correlationId, "correlationId");
    this.destination = Objects.requireNonNull(destination, "destination");
    this.layoutId = OutboxEntry.requireLayoutId(layoutId);
    this.layoutVersion = OutboxEntry.requireLayoutVersion(layoutVersion);
    this.body = Objects.requireNonNull(body, "body").clone();
    if (body.length == 0) {
      throw new IllegalArgumentException("outbox body must not be empty");
    }
    this.nextAttemptAt = Objects.requireNonNull(nextAttemptAt, "nextAttemptAt");
    this.createdAt = Objects.requireNonNull(createdAt, "createdAt");
    this.dlqMetadata =
        OutboxDlqMetadata.requireProfile(
            this.messageId,
            this.destination,
            this.layoutId,
            this.layoutVersion,
            this.body.length,
            dlqMetadata);
  }

  public UUID messageId() {
    return messageId;
  }

  public UUID correlationId() {
    return correlationId;
  }

  public OutboxDestination destination() {
    return destination;
  }

  public String layoutId() {
    return layoutId;
  }

  public String layoutVersion() {
    return layoutVersion;
  }

  public byte[] body() {
    return body.clone();
  }

  public Instant nextAttemptAt() {
    return nextAttemptAt;
  }

  public Instant createdAt() {
    return createdAt;
  }

  public Optional<OutboxDlqMetadata> dlqMetadata() {
    return dlqMetadata;
  }

  @Override
  public String toString() {
    return "OutboxRequest[destination=" + destination + ", body=<redacted>]";
  }
}
