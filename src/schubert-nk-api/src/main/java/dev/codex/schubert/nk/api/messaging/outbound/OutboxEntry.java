package dev.codex.schubert.nk.api.messaging.outbound;

import java.time.Instant;
import java.util.Objects;
import java.util.Optional;
import java.util.UUID;

/** Immutable claimed application-outbox row with defensive wire-body ownership. */
public final class OutboxEntry {
  private static final long MAXIMUM_ID = 999_999_999_999L;

  private final long retainedId;
  private final UUID retainedMessageId;
  private final UUID retainedCorrelationId;
  private final OutboxDestination retainedDestination;
  private final String retainedLayoutId;
  private final String retainedLayoutVersion;
  private final byte[] retainedBody;
  private final int retainedAttemptCount;
  private final Instant retainedNextAttemptAt;
  private final Instant retainedCreatedAt;
  private final String retainedLeaseOwner;
  private final Instant retainedLeaseUntil;
  private final Optional<OutboxDlqMetadata> retainedDlqMetadata;

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
    this.retainedId = id;
    this.retainedMessageId = Objects.requireNonNull(messageId, "messageId");
    this.retainedCorrelationId = Objects.requireNonNull(correlationId, "correlationId");
    this.retainedDestination = Objects.requireNonNull(destination, "destination");
    this.retainedLayoutId = requireLayoutId(layoutId);
    this.retainedLayoutVersion = requireLayoutVersion(layoutVersion);
    Objects.requireNonNull(body, "body");
    if (body.length == 0) {
      throw new IllegalArgumentException("outbox body must not be empty");
    }
    this.retainedAttemptCount = attemptCount;
    this.retainedNextAttemptAt = Objects.requireNonNull(nextAttemptAt, "nextAttemptAt");
    this.retainedCreatedAt = Objects.requireNonNull(createdAt, "createdAt");
    this.retainedLeaseOwner = requireLeaseOwner(leaseOwner);
    this.retainedLeaseUntil = Objects.requireNonNull(leaseUntil, "leaseUntil");
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

  public long id() {
    return retainedId;
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

  public int attemptCount() {
    return retainedAttemptCount;
  }

  public Instant nextAttemptAt() {
    return retainedNextAttemptAt;
  }

  public Instant createdAt() {
    return retainedCreatedAt;
  }

  public String leaseOwner() {
    return retainedLeaseOwner;
  }

  public Instant leaseUntil() {
    return retainedLeaseUntil;
  }

  public Optional<OutboxDlqMetadata> dlqMetadata() {
    return retainedDlqMetadata;
  }

  @Override
  public String toString() {
    return "OutboxEntry[<redacted>]";
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
