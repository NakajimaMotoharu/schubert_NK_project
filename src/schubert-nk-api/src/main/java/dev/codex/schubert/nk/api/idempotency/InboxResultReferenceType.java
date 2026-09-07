package dev.codex.schubert.nk.api.idempotency;

/** Allowlisted Inbox result reference types from the physical data design. */
public enum InboxResultReferenceType {
  NONE,
  AUTH_SESSION,
  USER,
  QUESTION,
  JOB,
  SCENARIO_FILE
}
