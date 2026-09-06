package dev.codex.schubert.nk.api.logging;

/** Retryable DB projection failure without SQL text/parameters. Trace: SS312/351, PT-IDEM-012. */
public final class LogProjectionDatabaseException extends RuntimeException {
  private static final long serialVersionUID = 1L;

  LogProjectionDatabaseException() {
    super("DB request log projection was not confirmed");
  }
}
