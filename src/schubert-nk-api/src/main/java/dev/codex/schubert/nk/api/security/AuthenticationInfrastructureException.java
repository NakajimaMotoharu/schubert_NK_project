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

  /** BUG622/YKT440/QA050: redact ordinary failures without losing fatal JDBC close failures. */
  static void preserveFatal(Throwable failure) {
    var pending = new java.util.ArrayDeque<Throwable>();
    var seen = new java.util.IdentityHashMap<Throwable, Boolean>();
    pending.add(failure);
    while (!pending.isEmpty()) {
      Throwable current = pending.removeFirst();
      if (seen.put(current, Boolean.TRUE) != null) continue;
      if (current instanceof Error fatal) throw fatal;
      for (Throwable closing : current.getSuppressed()) pending.addLast(closing);
    }
  }
}
