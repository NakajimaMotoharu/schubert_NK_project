package dev.codex.schubert.nk.api.security;

/** Restricted internal audit only, never a user message. NK-AUT-001; SS314 §12/351; PT-AUT-004. */
public enum LoginAuditReason {
  SUCCEEDED,
  NO_ACCOUNT,
  DISABLED,
  PASSWORD_MISMATCH,
  PREEXISTING_LOCK
}
