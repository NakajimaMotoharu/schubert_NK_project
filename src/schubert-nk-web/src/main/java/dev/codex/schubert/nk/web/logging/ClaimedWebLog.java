package dev.codex.schubert.nk.web.logging;

import java.time.Instant;
import java.util.Objects;

/**
 * Immutable, encrypted Web-owned outbox lease; no business-schema data is accessible here.
 * Trace: NK-MSG-002; RD MON-003/MQ-008; UI 242; SS 324 section 9/331 section 9.3;
 * PT-IDEM-012.
 */
public record ClaimedWebLog(
    long id, WebLogPayloadIdentity identity, EncryptedWebLogPayload payload,
    int attemptCount, Instant nextAttemptAt, Instant createdAt,
    String leaseOwner, Instant leaseUntil) {
  public ClaimedWebLog {
    if (id < 1 || id > 999_999_999_999L) {
      throw new IllegalArgumentException("web log row ID is outside N12");
    }
    if (attemptCount < 0 || attemptCount > 100) {
      throw new IllegalArgumentException("web log attempt count is outside 0..100");
    }
    Objects.requireNonNull(identity, "identity");
    Objects.requireNonNull(payload, "payload");
    Objects.requireNonNull(nextAttemptAt, "nextAttemptAt");
    Objects.requireNonNull(createdAt, "createdAt");
    requireWorker(leaseOwner);
    Objects.requireNonNull(leaseUntil, "leaseUntil");
  }

  static String requireWorker(String worker) {
    Objects.requireNonNull(worker, "worker");
    if (!worker.matches("[A-Za-z0-9._-]{1,64}")) {
      throw new IllegalArgumentException("web log lease owner is invalid");
    }
    return worker;
  }

  @Override
  public String toString() {
    return "ClaimedWebLog[identity/payload/lease=<redacted>]";
  }
}
