package dev.codex.schubert.nk.web.revocation;

/** Closed non-sensitive persisted warning. NK-WEB-002/QA050/SS314331/RERUN004005. */
public enum RevocationFailureCode {
  SESSION_INVALID,
  API_REJECTED,
  INVALID_RESPONSE,
  UNAVAILABLE,
  KEY_UNAVAILABLE,
  PAYLOAD_INVALID,
  CRYPTO_UNAVAILABLE
}
