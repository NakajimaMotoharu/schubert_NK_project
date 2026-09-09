package dev.codex.schubert.nk.batch.cleanup;

/** NK-BAT-001; OPS-009; UI251; SS341§7/12; PG-D-138; PT-BAT-021..029. */
public enum CleanupStopReason {
  LOCK_BUSY,
  BACKUP_GATE,
  TIME_LIMIT,
  INTERRUPTED,
  DATABASE_FAILURE
}
