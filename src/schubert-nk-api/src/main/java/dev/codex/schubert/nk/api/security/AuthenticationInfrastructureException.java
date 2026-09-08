package dev.codex.schubert.nk.api.security;

/**
 * Maps to 9000; SQL parameters/provider messages are not retained. NK-AUT-001; SS314 §6;
 * PT-AUT-007.
 */
public final class AuthenticationInfrastructureException extends RuntimeException {
  private static final long serialVersionUID = 1L;

  AuthenticationInfrastructureException() {
    super("authentication storage is unavailable");
  }
}
