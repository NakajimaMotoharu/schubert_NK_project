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

  /** SS312/SSC329: classify transient JDBC graphs before discarding provider diagnostics. */
  public static void preserveFatal(Throwable failure) {
    var pending = new java.util.ArrayDeque<Throwable>();
    java.util.Set<Throwable> seen =
        java.util.Collections.newSetFromMap(new java.util.IdentityHashMap<>());
    pending.add(java.util.Objects.requireNonNull(failure, "failure"));
    while (!pending.isEmpty()) {
      Throwable candidate = pending.remove();
      if (!seen.add(candidate)) continue;
      if (candidate instanceof Error fatal) throw fatal;
      Throwable cause = candidate.getCause();
      if (cause != null) pending.add(cause);
      pending.addAll(java.util.Arrays.asList(candidate.getSuppressed()));
      if (candidate instanceof java.sql.SQLException sql) {
        java.sql.SQLException next = sql.getNextException();
        if (next != null) pending.add(next);
      }
    }
  }
}
