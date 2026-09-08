package dev.codex.schubert.nk.api.idempotency;

/** Outcome of the Inbox coordination step. */
public enum InboxExecutionStatus {
  EXECUTED,
  REPLAY,
  IN_PROGRESS
}
