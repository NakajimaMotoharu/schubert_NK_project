package dev.codex.schubert.nk.web.session;

import java.time.Instant;
import java.util.Objects;

/**
 * Immutable technical row, not an authenticated or unexpired session. NK-WEB-001/NK-AUT-001;
 * FUN-001/AUT-001..004; UI226/242; SS314 §7.2.3/331 §9.1/352; SSC-040/PG-D-096/PT-WEB-024..031.
 * Nonnull values; mirrors DDL time/TTL/version bounds.
 */
public record WebSessionRow(
    SessionPayloadIdentity identity,
    EncryptedSessionPayload payload,
    Instant lastAccessedAt,
    Instant expiresAt,
    int maxInactiveSeconds,
    long version) {
  public WebSessionRow {
    Objects.requireNonNull(identity, "identity");
    Objects.requireNonNull(payload, "payload");
    Objects.requireNonNull(lastAccessedAt, "lastAccessedAt");
    Objects.requireNonNull(expiresAt, "expiresAt");
    if (lastAccessedAt.getNano() % 1000 != 0
        || expiresAt.getNano() % 1000 != 0
        || lastAccessedAt.isBefore(identity.createdAt())
        || expiresAt.isBefore(lastAccessedAt)
        || maxInactiveSeconds < 1
        || maxInactiveSeconds > 28800)
      throw new IllegalArgumentException("session row metadata is invalid");
    requireVersion(version);
  }

  static void requireVersion(long version) {
    if (version < 0 || version > 999999999)
      throw new IllegalArgumentException("session row version is invalid");
  }

  @Override
  public String toString() {
    return "WebSessionRow[REDACTED]";
  }
}
