package dev.codex.schubert.nk.api.idempotency;

/** Terminal Inbox states that have a deterministic response. */
public enum InboxCompletionState {
  COMPLETED,
  ERROR
}
