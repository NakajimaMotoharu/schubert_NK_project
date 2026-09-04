package dev.codex.schubert.nk.api.idempotency;

/** Result of verifying a stored operation fingerprint. Trace: NK-MSG-002, SS 324 §3.2. */
public enum FingerprintVerification {
  MATCH,
  MISMATCH,
  KEY_UNAVAILABLE
}
