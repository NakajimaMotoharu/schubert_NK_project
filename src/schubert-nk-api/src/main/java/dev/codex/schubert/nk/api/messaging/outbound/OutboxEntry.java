package dev.codex.schubert.nk.api.messaging.outbound;

import java.time.Instant;
import java.util.Objects;
import java.util.Optional;
import java.util.UUID;

/** Immutable claimed application-outbox row with defensive wire-body ownership. */
public final class OutboxEntry {
  private static final long MAXIMUM_ID = 999_999_999_999L;

  private final long id;
  private final UUID messageId;
  private final UUID correlationId;
  private final OutboxDestination destination;
  private final String layoutId;
  private final String layoutVersion;
  private final byte[] body;
  private final int attemptCount;
  private final Instant nextAttemptAt;
  private final Instant createdAt;
  private final String leaseOwner;
  private final Instant leaseUntil;
  private final Optional<OutboxDlqMetadata> dlqMetadata;

  public OutboxEntry(
      long id,
      UUID messageId,
      UUID correlationId,
      OutboxDestination destination,
      String layoutId,
      String layoutVersion,
      byte[] body,
      int attemptCount,
      Instant nextAttemptAt,
      Instant createdAt,
      String leaseOwner,
      Instant leaseUntil) {
    this(
        id,
        messageId,
        correlationId,
        destination,
        layoutId,
        layoutVersion,
        body,
        attemptCount,
        nextAttemptAt,
        createdAt,
        leaseOwner,
        leaseUntil,
        Optional.empty());
  }

  public OutboxEntry(
      long id,
      UUID messageId,
      UUID correlationId,
      OutboxDestination destination,
      String layoutId,
      String layoutVersion,
      byte[] body,
      int attemptCount,
      Instant nextAttemptAt,
      Instant createdAt,
      String leaseOwner,
      Instant leaseUntil,
      Optional<OutboxDlqMetadata> dlqMetadata) {
    if (id < 1 || id > MAXIMUM_ID) {
      throw new IllegalArgumentException("outbox id is outside N12");
    }
    if (attemptCount < 0 || attemptCount > 100) {
      throw new IllegalArgumentException("attemptCount must be between 0 and 100");
    }
    this.id = id;
    this.messageId = Objects.requireNonNull(messageId, "messageId");
    this.correlationId = Objects.requireNonNull(correlationId, "correlationId");
    this.destination = Objects.requireNonNull(destination, "destination");
    this.layoutId = requireLayoutId(layoutId);
    this.layoutVersion = requireLayoutVersion(layoutVersion);
    this.body = Objects.requireNonNull(body, "body").clone();
    if (body.length == 0) {
      throw new IllegalArgumentException("outbox body must not be empty");
    }
    this.attemptCount = attemptCount;
    this.nextAttemptAt = Objects.requireNonNull(nextAttemptAt, "nextAttemptAt");
    this.createdAt = Objects.requireNonNull(createdAt, "createdAt");
    this.leaseOwner = requireLeaseOwner(leaseOwner);
    this.leaseUntil = Objects.requireNonNull(leaseUntil, "leaseUntil");
    this.dlqMetadata =
        OutboxDlqMetadata.requireProfile(
            this.messageId,
            this.destination,
            this.layoutId,
            this.layoutVersion,
            this.body.length,
            dlqMetadata);
  }

  public long id() {
    return id;
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

  public int attemptCount() {
    return attemptCount;
  }

  public Instant nextAttemptAt() {
    return nextAttemptAt;
  }

  public Instant createdAt() {
    return createdAt;
  }

  public String leaseOwner() {
    return leaseOwner;
  }

  public Instant leaseUntil() {
    return leaseUntil;
  }

  public Optional<OutboxDlqMetadata> dlqMetadata() {
    return dlqMetadata;
  }

  @Override
  public String toString() {
    return "OutboxEntry[id=" + id + ", destination=" + destination + ", body=<redacted>]";
  }

  static String requireLayoutId(String value) {
    Objects.requireNonNull(value, "layoutId");
    if (!value.matches("[A-Z0-9]{8}")) {
      throw new IllegalArgumentException("layoutId must be eight upper-case alphanumeric bytes");
    }
    return value;
  }

  static String requireLayoutVersion(String value) {
    Objects.requireNonNull(value, "layoutVersion");
    if (!value.matches("[0-9]{3}")) {
      throw new IllegalArgumentException("layoutVersion must be three decimal digits");
    }
    return value;
  }

  static String requireLeaseOwner(String value) {
    Objects.requireNonNull(value, "leaseOwner");
    if (value.isBlank() || value.length() > 64) {
      throw new IllegalArgumentException("leaseOwner must contain 1 to 64 characters");
    }
    return value;
  }
}
