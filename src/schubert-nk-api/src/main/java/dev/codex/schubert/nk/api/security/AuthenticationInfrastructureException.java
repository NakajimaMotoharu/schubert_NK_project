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

  /**
   * BUG622/1596; YKT440/1349; SS312314354/SSC329330: pure module-local reuse, preserving the
   * existing Auth suppressed-first classification without exposing provider diagnostics.
   */
  public static void preserveFatal(Throwable failure) {
    var pending = new java.util.ArrayDeque<Throwable>();
    var seen = new java.util.IdentityHashMap<Throwable, Boolean>();
    pending.add(failure);
    while (!pending.isEmpty()) {
      Throwable current = pending.removeFirst();
      if (seen.put(current, Boolean.TRUE) != null) continue;
      if (current instanceof Error fatal) throw fatal;
      for (Throwable closing : current.getSuppressed()) pending.addLast(closing);
      // SSC328: keep the existing suppressed priority, then inspect the other JDBC edges.
      Throwable cause = current.getCause();
      if (cause != null) pending.addLast(cause);
      if (current instanceof java.sql.SQLException sql) {
        java.sql.SQLException next = sql.getNextException();
        if (next != null) pending.addLast(next);
      }
    }
  }
}
