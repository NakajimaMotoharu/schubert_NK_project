package dev.codex.schubert.nk.batch.repository;

import org.jspecify.annotations.NullMarked;

/**
 * Fixed SQL identifiers only. NK-BAT-001; DAT-009; UI251; SS331/332§11; PG-D-137;
 * PT-BAT-003/005/009.
 */
@NullMarked
public enum CleanupKind {
  NOTIFICATIONS("notifications", 1000),
  QUESTIONS("questions", 1000),
  SESSIONS("sessions", 1000),
  OUTBOX("message_stores", 1000),
  LOGS("logs", 10000),
  BATCH_RUNS("batch_runs", 1000),
  INBOX_PROGRESS("inbox_progress", 1000),
  LOG_PROGRESS("log_progress", 1000);
  private final String function;
  private final int maximumRows;

  CleanupKind(String suffix, int maximumRows) {
    this.function = "schubert.maintenance_cleanup_" + suffix;
    this.maximumRows = maximumRows;
  }

  public String function() {
    return function;
  }

  public int maximumRows() {
    return maximumRows;
  }
}
