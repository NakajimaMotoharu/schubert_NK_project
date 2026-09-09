package dev.codex.schubert.nk.batch.repository;

/**
 * No JDBC text/cause/suppressed retained. NK-BAT-001; OPS-009; UI251; SS352; PG-D-137;
 * PT-BAT-010..015.
 */
public final class BatchRepositoryException extends RuntimeException {
  private static final long serialVersionUID = 1L;

  public BatchRepositoryException() {
    super("batch repository operation failed");
  }
}
