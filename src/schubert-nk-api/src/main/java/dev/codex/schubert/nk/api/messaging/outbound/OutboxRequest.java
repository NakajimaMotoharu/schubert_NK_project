package dev.codex.schubert.nk.api.messaging.outbound;

import java.time.Instant;
import java.util.Objects;
import java.util.Optional;
import java.util.UUID;

/** Application-outbox INSERT request; identity is validated again before JMS send. */
public final class OutboxRequest {
  private final UUID retainedMessageId;
  private final UUID retainedCorrelationId;
  private final OutboxDestination retainedDestination;
  private final String retainedLayoutId;
  private final String retainedLayoutVersion;
  private final byte[] retainedBody;
  private final Instant retainedNextAttemptAt;
  private final Instant retainedCreatedAt;
  private final Optional<OutboxDlqMetadata> retainedDlqMetadata;

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
    this.retainedMessageId = Objects.requireNonNull(messageId, "messageId");
    this.retainedCorrelationId = Objects.requireNonNull(correlationId, "correlationId");
    this.retainedDestination = Objects.requireNonNull(destination, "destination");
    this.retainedLayoutId = OutboxEntry.requireLayoutId(layoutId);
    this.retainedLayoutVersion = OutboxEntry.requireLayoutVersion(layoutVersion);
    Objects.requireNonNull(body, "body");
    if (body.length == 0) {
      throw new IllegalArgumentException("outbox body must not be empty");
    }
    this.retainedNextAttemptAt = Objects.requireNonNull(nextAttemptAt, "nextAttemptAt");
    this.retainedCreatedAt = Objects.requireNonNull(createdAt, "createdAt");
    this.retainedDlqMetadata =
        OutboxDlqMetadata.requireProfile(
            this.retainedMessageId,
            this.retainedDestination,
            this.retainedLayoutId,
            this.retainedLayoutVersion,
            body.length,
            dlqMetadata);
    this.retainedBody = body.clone();
  }

  public UUID messageId() {
    return retainedMessageId;
  }

  public UUID correlationId() {
    return retainedCorrelationId;
  }

  public OutboxDestination destination() {
    return retainedDestination;
  }

  public String layoutId() {
    return retainedLayoutId;
  }

  public String layoutVersion() {
    return retainedLayoutVersion;
  }

  public byte[] body() {
    return retainedBody.clone();
  }

  public Instant nextAttemptAt() {
    return retainedNextAttemptAt;
  }

  public Instant createdAt() {
    return retainedCreatedAt;
  }

  public Optional<OutboxDlqMetadata> dlqMetadata() {
    return retainedDlqMetadata;
  }

  @Override
  public String toString() {
    return "OutboxRequest[<redacted>]";
  }
}
