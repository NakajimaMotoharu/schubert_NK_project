package dev.codex.schubert.nk.batch.repository;

import org.jspecify.annotations.NullMarked;

/** NK-BAT-001; DAT-009; UI251; SS332§11/341§7; PG-D-137; PT-BAT-002/010/011. */
@NullMarked
public record CleanupCounts(long target, long deleted, long skipped) {
  public CleanupCounts {
    if (target < 0 || deleted < 0 || deleted > target || skipped < 0 || skipped != target - deleted)
      throw new IllegalArgumentException("cleanup counts are inconsistent");
  }
}
