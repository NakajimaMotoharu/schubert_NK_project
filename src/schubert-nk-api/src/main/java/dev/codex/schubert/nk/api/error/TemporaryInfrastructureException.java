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

  /** SS312/SSC329330: classify transient JDBC/JMS graphs before discarding provider diagnostics. */
  public static void preserveFatal(Throwable failure) {
    java.util.Objects.requireNonNull(failure, "failure");
    if (failure instanceof Error fatal) throw fatal;
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
      // SSC330: readiness can wrap a checked JMS provider graph inside a RuntimeException.
      if (candidate instanceof jakarta.jms.JMSException jms) {
        Exception linked = jms.getLinkedException();
        if (linked != null) pending.add(linked);
      }
      if (candidate instanceof java.sql.SQLException sql) {
        java.sql.SQLException next = sql.getNextException();
        if (next != null) pending.add(next);
      }
    }
  }

  /** Transient owner cleanup graph only; never attach this graph to a new catalog exception. */
  public static void attachSecondary(Throwable primary, Throwable secondary) {
    java.util.Objects.requireNonNull(primary, "primary");
    java.util.Objects.requireNonNull(secondary, "secondary");
    if (primary != secondary) {
      primary.addSuppressed(secondary);
      if (primary.getSuppressed().length == 0) {
        // Suppression-disabled provider failures cannot silently discard a secondary fatal.
        preserveFatal(primary);
        preserveFatal(secondary);
      }
    }
  }
}
