package dev.codex.schubert.nk.api.security;

/** Maps to 0102; no existence/state/raw-context detail. NK-AUT-001; SS314 §6; PT-AUT-007. */
public final class AuthenticationContextException extends RuntimeException {
  private static final long serialVersionUID = 1L;

  AuthenticationContextException() {
    super("authentication context is not valid");
  }
}
