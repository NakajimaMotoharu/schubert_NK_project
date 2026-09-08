package dev.codex.schubert.nk.api.idempotency;

import java.util.Objects;
import java.util.UUID;

/**
 * Saved-row message identity paired with an Inbox outcome, not an authentication/crypto grant.
 * NK-MSG-002/NK-ADM-001; MQ-006..010; UI236/241/242; SS324 §6/352; SSC-033/PG-D-085;
 * PT-IDEM-B01..B04. Token replay must use this source ID for stored snapshot AAD.
 */
public record BoundInboxExecution(UUID sourceMessageId, InboxExecution execution) {
  public BoundInboxExecution {
    Objects.requireNonNull(sourceMessageId, "sourceMessageId");
    Objects.requireNonNull(execution, "execution");
  }

  @Override
  public String toString() {
    return "BoundInboxExecution[REDACTED]";
  }
}
