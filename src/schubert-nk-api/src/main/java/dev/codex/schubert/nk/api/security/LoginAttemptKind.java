package dev.codex.schubert.nk.api.security;

/** Closed User/IP thresholds. NK-AUT-001; AUT-001; UI226 §4; SS314 §5; PT-AUT-003. */
public enum LoginAttemptKind {
  USER(5),
  IP(10);

  private final int failureThreshold;

  LoginAttemptKind(int threshold) {
    this.failureThreshold = threshold;
  }

  public int threshold() {
    return failureThreshold;
  }
}
