package dev.codex.schubert.nk.web.revocation;

import java.time.Instant;
import java.util.Objects;
import java.util.UUID;
import org.jspecify.annotations.Nullable;

/** Immutable ciphertext/lease projection, no authority proof. NK-WEB-002/QA050/RERUN004005. */
public record ClaimedRevocation(
    RevocationPayloadIdentity identity,
    @Nullable EncryptedRevocationPayload payload,
    int attemptCount,
    @Nullable Instant expiresAt,
    UUID leaseOwner,
    Instant leaseUntil,
    String keyVersion) {
  public ClaimedRevocation {
    Objects.requireNonNull(identity, "revocation identity");
    EncryptedRevocationPayload.validateVersion(keyVersion);
    if (payload != null && !payload.keyVersion().equals(keyVersion))
      throw new IllegalArgumentException("claimed revocation key binding is invalid");
    Objects.requireNonNull(leaseOwner, "revocation lease");
    PendingRevocationRepository.microseconds(leaseUntil);
    if (attemptCount < 0 || attemptCount > 100 || !leaseUntil.isAfter(identity.requestedAt()))
      throw new IllegalArgumentException("claimed revocation metadata is invalid");
    if (expiresAt != null) {
      PendingRevocationRepository.microseconds(expiresAt);
      if (!expiresAt.isAfter(identity.requestedAt()))
        throw new IllegalArgumentException("known revocation expiry is invalid");
    }
  }

  @Override
  public String toString() {
    return "ClaimedRevocation[REDACTED]";
  }
}
