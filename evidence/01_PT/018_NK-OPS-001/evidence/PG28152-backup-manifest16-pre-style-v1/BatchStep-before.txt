package dev.codex.schubert.nk.batch.repository;

import org.jspecify.annotations.NullMarked;

/** Closed SS341 steps; NK-BAT-001/OPS009/UI251/SS331 8.3/SSC055/PG163; BAT130..137. */
@NullMarked
public enum BatchStep {
  BACKUP_DB(true),
  BACKUP_CONFIG(true),
  CLEAN_NOTIFICATION(false),
  CLEAN_QUESTION(false),
  CLEAN_SESSION(false),
  CLEAN_INBOX_OUTBOX(false),
  CLEAN_LOG(false),
  CLEAN_BATCH_RUN(false),
  CLEAN_TRANSFER(false),
  CLEAN_EXPIRY(false);

  private final boolean backupStep;

  BatchStep(boolean backup) {
    this.backupStep = backup;
  }

  public boolean backup() {
    return backupStep;
  }
}
