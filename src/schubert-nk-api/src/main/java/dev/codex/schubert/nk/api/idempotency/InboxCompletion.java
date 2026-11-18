package dev.codex.schubert.nk.api.idempotency;

import java.time.Instant;
import java.util.Objects;
import java.util.Optional;

/**
 * Deterministic handler result persisted for replay in the caller transaction.
 *
 * <p>Trace: NK-MSG-002, RD MQ-006..010, UI 241/242, SS 324 §6.
 */
public record InboxCompletion(
    InboxCompletionState state,
    InboxResultReference resultReference,
    String responseLayoutId,
    String responseVersion,
    Optional<EncryptedResponseSnapshot> responseSnapshot,
    Instant completedAt) {
  public InboxCompletion {
    Objects.requireNonNull(state, "state");
    Objects.requireNonNull(resultReference, "resultReference");
    Objects.requireNonNull(responseLayoutId, "responseLayoutId");
    Objects.requireNonNull(responseVersion, "responseVersion");
    Objects.requireNonNull(responseSnapshot, "responseSnapshot");
    Objects.requireNonNull(completedAt, "completedAt");
    if (!responseLayoutId.matches("[A-Z0-9]{8}")) {
      throw new IllegalArgumentException("responseLayoutId is invalid");
    }
    if (!responseVersion.matches("[0-9]{3}")) {
      throw new IllegalArgumentException("responseVersion is invalid");
    }
  }

  @Override
  public String toString() {
    return "InboxCompletion[<redacted>]";
  }
}
