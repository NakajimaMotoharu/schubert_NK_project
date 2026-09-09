package dev.codex.schubert.nk.batch.repository;

import java.util.Objects;
import org.jspecify.annotations.NullMarked;

/**
 * Uncommitted observation, never a process/OS-gate certificate. NK-BAT-001; DAT-009; UI251;
 * SS341§7; PG-D-137; PT-BAT-004/006/010.
 */
@NullMarked
public record CleanupChunk(CleanupCounts counts, CleanupReason reason) {
  public CleanupChunk {
    Objects.requireNonNull(counts, "counts");
    Objects.requireNonNull(reason, "reason");
    if (reason != CleanupReason.OK && counts.target() != 0)
      throw new IllegalArgumentException("rejected cleanup changed rows");
  }
}
