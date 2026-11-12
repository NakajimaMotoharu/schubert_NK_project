package dev.codex.schubert.nk.storage;

import java.io.IOException;
import java.util.Objects;

/** Bounded storage failure without physical paths/native messages. SS333; PT-SCN-008-F01/F02. */
public final class StorageIoException extends IOException {
  private static final long serialVersionUID = 1L;

  public enum Reason {
    COLLISION,
    MISSING,
    UNAVAILABLE
  }

  private final Reason failureReason;

  public StorageIoException(Reason reason) {
    super("transfer storage operation failed");
    this.failureReason = Objects.requireNonNull(reason, "reason");
  }

  public Reason reason() {
    return failureReason;
  }

  /** BUG2718/YKT2359: classify transient provider graphs before discarding diagnostics. */
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
    }
  }
}
