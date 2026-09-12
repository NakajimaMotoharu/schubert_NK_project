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

  /**
   * Fixed parent step. LOGS uses its dedicated durable-cursor service, not V020. SS331
   * 3.14/332/341; SSC057/PG164; BAT154.
   */
  public BatchStep step() {
    return switch (this) {
      case NOTIFICATIONS -> BatchStep.CLEAN_NOTIFICATION;
      case QUESTIONS -> BatchStep.CLEAN_QUESTION;
      case SESSIONS -> BatchStep.CLEAN_SESSION;
      case OUTBOX -> BatchStep.CLEAN_INBOX_OUTBOX;
      case LOGS -> BatchStep.CLEAN_LOG;
      case BATCH_RUNS, INBOX_PROGRESS, LOG_PROGRESS -> BatchStep.CLEAN_BATCH_RUN;
    };
  }
}
