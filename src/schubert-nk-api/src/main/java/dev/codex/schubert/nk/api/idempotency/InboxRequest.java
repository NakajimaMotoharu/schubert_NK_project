package dev.codex.schubert.nk.api.idempotency;

import java.time.Instant;
import java.util.Objects;
import java.util.Optional;
import java.util.OptionalLong;
import java.util.Set;
import java.util.UUID;

/**
 * Validated identity and retention boundary for one API Inbox request.
 *
 * <p>Trace: NK-MSG-002, RD MQ-006..010/FUN-103..105, UI 241/242, SS 324 §5.
 */
public record InboxRequest(
    UUID messageId,
    UUID correlationId,
    OptionalLong ownerUserId,
    Optional<UUID> operationToken,
    CanonicalRequest canonicalRequest,
    Instant receivedAt,
    Instant expiresAt) {
  private static final long MAXIMUM_OWNER_ID = 999_999_999_999L;
  private static final Set<String> TOKEN_LAYOUTS =
      Set.of(
          "UCRREQ01",
          "USTREQ01",
          "URLREQ01",
          "UPWREQ01",
          "ULKREQ01",
          "QSBREQ01",
          "NTCREQ01",
          "QDLREQ01");

  public InboxRequest {
    Objects.requireNonNull(messageId, "messageId");
    Objects.requireNonNull(correlationId, "correlationId");
    Objects.requireNonNull(ownerUserId, "ownerUserId");
    Objects.requireNonNull(operationToken, "operationToken");
    Objects.requireNonNull(canonicalRequest, "canonicalRequest");
    Objects.requireNonNull(receivedAt, "receivedAt");
    Objects.requireNonNull(expiresAt, "expiresAt");
    boolean login = canonicalRequest.layoutId().equals("LGNREQ01");
    if (login == ownerUserId.isPresent()) {
      throw new IllegalArgumentException("owner scope does not match request layout");
    }
    if (ownerUserId.isPresent()
        && (ownerUserId.getAsLong() < 1 || ownerUserId.getAsLong() > MAXIMUM_OWNER_ID)) {
      throw new IllegalArgumentException("ownerUserId is outside N12");
    }
    String expectedScope = ownerUserId.isPresent() ? Long.toString(ownerUserId.getAsLong()) : "ANONYMOUS";
    if (!canonicalRequest.ownerScope().equals(expectedScope)) {
      throw new IllegalArgumentException("canonical owner scope does not match Inbox owner");
    }
    if (TOKEN_LAYOUTS.contains(canonicalRequest.layoutId()) != operationToken.isPresent()) {
      throw new IllegalArgumentException("operation token presence does not match request layout");
    }
    if (!receivedAt.isBefore(expiresAt)) {
      throw new IllegalArgumentException("Inbox expiry must be after receipt time");
    }
  }

  @Override
  public String toString() {
    return "InboxRequest[message/correlation/owner/token/request/time=<redacted>]";
  }
}
