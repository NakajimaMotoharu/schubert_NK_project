package dev.codex.schubert.nk.web.bootstrap;

/** Redacted fail-closed startup result; provider messages and credential material never escape. */
public final class WebStartupException extends IllegalStateException {
  private static final long serialVersionUID = 1L;

  public WebStartupException(String component) {
    super(component + " is unavailable");
  }

  /** SS312/342/SSC330: module-local, non-I/O classification before startup redaction. */
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

  /** Temporary cleanup attachment only, without granting any new resource ownership. */
  public static void attachSecondary(Throwable primary, Throwable secondary) {
    java.util.Objects.requireNonNull(primary, "primary");
    java.util.Objects.requireNonNull(secondary, "secondary");
    if (primary != secondary) {
      primary.addSuppressed(secondary);
      if (primary.getSuppressed().length == 0) {
        preserveFatal(primary);
        preserveFatal(secondary);
      }
    }
  }
}
