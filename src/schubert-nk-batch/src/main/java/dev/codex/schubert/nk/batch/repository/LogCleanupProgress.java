package dev.codex.schubert.nk.batch.repository;

import java.util.Objects;
import org.jspecify.annotations.NullMarked;

/**
 * Borrowed-transaction observation, not confirmed commit. NK-BAT-001; DAT-009; UI251;
 * SS331§3.9/341§7; SSC-051; PG-D-137; PT-BAT-004/006/007/011.
 */
@NullMarked
public record LogCleanupProgress(BatchRun run, CleanupCounts counts, boolean complete) {
  public LogCleanupProgress {
    Objects.requireNonNull(run, "run");
    Objects.requireNonNull(counts, "counts");
  }
}
