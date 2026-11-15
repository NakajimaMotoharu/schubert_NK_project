package dev.codex.schubert.nk.batch.repository;

import java.util.Objects;
import org.jspecify.annotations.NullMarked;

/**
 * Fixed SQL identifiers only. NK-BAT-001; DAT-009; UI251; SS331/332§11; PG-D-137;
 * PT-BAT-003/005/009.
 */
@NullMarked
public enum CleanupKind {
  NOTIFICATIONS("notifications", 1000, BatchStep.CLEAN_NOTIFICATION),
  QUESTIONS("questions", 1000, BatchStep.CLEAN_QUESTION),
  SESSIONS("sessions", 1000, BatchStep.CLEAN_SESSION),
  OUTBOX("message_stores", 1000, BatchStep.CLEAN_INBOX_OUTBOX),
  LOGS("logs", 10000, BatchStep.CLEAN_LOG),
  WEB_RECEIPTS("web_receipt_references", 1000, BatchStep.CLEAN_BATCH_RUN),
  BATCH_RUNS("batch_runs", 1000, BatchStep.CLEAN_BATCH_RUN),
  INBOX_PROGRESS("inbox_progress", 1000, BatchStep.CLEAN_BATCH_RUN),
  LOG_PROGRESS("log_progress", 1000, BatchStep.CLEAN_BATCH_RUN);
  private final String sqlFunction;
  private final int rowLimit;
  private final BatchStep parentStep;

  CleanupKind(String suffix, int maximumRows, BatchStep parentStep) {
    this.sqlFunction = "schubert.maintenance_cleanup_" + suffix;
    this.rowLimit = maximumRows;
    this.parentStep = Objects.requireNonNull(parentStep, "parent step");
  }

  public String function() {
    return sqlFunction;
  }

  public int maximumRows() {
    return rowLimit;
  }

  /**
   * Fixed parent step. LOGS uses its dedicated durable-cursor service, not V020. SS331
   * 3.14/332/341; SSC057/PG164; BAT154.
   */
  public BatchStep step() {
    return parentStep;
  }
}
