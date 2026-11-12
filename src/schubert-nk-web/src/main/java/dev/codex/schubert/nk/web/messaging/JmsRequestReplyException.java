package dev.codex.schubert.nk.web.messaging;

import org.jspecify.annotations.Nullable;

/** Bounded non-secret Web temporary failure raised before an HTTP result is selected. */
public final class JmsRequestReplyException extends RuntimeException {
  private static final long serialVersionUID = 1L;

  private final Reason failureReason;

  JmsRequestReplyException(Reason reason, String message) {
    super(message);
    this.failureReason = java.util.Objects.requireNonNull(reason, "reason");
  }

  JmsRequestReplyException(Reason reason, String message, @Nullable Throwable cause) {
    super(message, cause);
    this.failureReason = java.util.Objects.requireNonNull(reason, "reason");
  }

  public Reason reason() {
    return failureReason;
  }

  public enum Reason {
    CAPACITY,
    TIMEOUT,
    INTERRUPTED
  }

  /** BUG2721/YKT2359: preserve fatal identity before a secret-free JMS catalog conversion. */
  public static void preserveFatal(Throwable failure) {
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
      // SSC328: next is last; direct Error and the existing cause/suppressed order stay fixed.
      if (candidate instanceof java.sql.SQLException sql) {
        java.sql.SQLException next = sql.getNextException();
        if (next != null) pending.add(next);
      }
      // JMSException keeps linkedException separately from Throwable.cause.
      if (candidate instanceof jakarta.jms.JMSException jms) {
        Exception linked = jms.getLinkedException();
        if (linked != null) pending.add(linked);
      }
    }
  }
}
