package dev.codex.schubert.nk.api.error;

/**
 * Rollback/retry signal, never a successful reply. No provider message, cause or secret is
 * retained. NK-AUT-001/NK-MSG-002; MQ-006/008; UI231; SS311 section 8/312 section 12;
 * PT-AUT-TX-002/003.
 */
public final class TemporaryInfrastructureException extends RuntimeException {
  private static final long serialVersionUID = 1L;

  public TemporaryInfrastructureException() {
    super("request transaction is unavailable");
  }
}
