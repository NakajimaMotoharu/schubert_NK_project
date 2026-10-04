package dev.codex.schubert.nk.web.session;

/**
 * Fixed DB failure, without SQL/parameters/cause/suppressed resource diagnostics. NK-WEB-001;
 * FUN-001/AUT-001..004; UI226/242; SS314/331/352; SSC-040/PG-D-096/PT-WEB-024..031. Caller must
 * roll back the borrowed transaction.
 */
public sealed class SessionStoreException extends RuntimeException
    permits InvalidSessionRowException {
  private static final long serialVersionUID = 1L;

  public SessionStoreException() {
    super("session storage is unavailable");
  }

  /** BUG628/YKT445: inspect only transient failures, never retain provider text in this catalog. */
  static void preserveFatal(Throwable failure) {
    var pending = new java.util.ArrayDeque<Throwable>();
    java.util.Set<Throwable> seen =
        java.util.Collections.newSetFromMap(new java.util.IdentityHashMap<>());
    pending.add(failure);
    while (!pending.isEmpty()) {
      Throwable candidate = pending.remove();
      if (!seen.add(candidate)) continue;
      if (candidate instanceof Error fatal) throw fatal;
      Throwable cause = candidate.getCause();
      if (cause != null) pending.add(cause);
      pending.addAll(java.util.Arrays.asList(candidate.getSuppressed()));
    }
  }
}
