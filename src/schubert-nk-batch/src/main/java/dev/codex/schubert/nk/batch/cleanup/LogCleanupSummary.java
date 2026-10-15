package dev.codex.schubert.nk.batch.cleanup;

import dev.codex.schubert.nk.batch.repository.BatchRun;
import dev.codex.schubert.nk.batch.repository.CleanupCounts;
import dev.codex.schubert.nk.batch.repository.LogCleanupProgress;
import java.util.Objects;
import org.jspecify.annotations.NullMarked;

/**
 * Returned only after END/commit/restoration/owned-lock release. NK-BAT-001; DAT-009; UI251;
 * SS341§7.2; SSC-051; PG-D-138; PT-BAT-018..020/028.
 */
@NullMarked
public record LogCleanupSummary(BatchRun run, CleanupCounts before, LogCleanupProgress after) {
  public LogCleanupSummary {
    Objects.requireNonNull(run, "run");
    Objects.requireNonNull(before, "before");
    Objects.requireNonNull(after, "after");
    if (!run.equals(after.run())
        || !after.complete()
        || after.counts().target() < before.target()
        || after.counts().deleted() < before.deleted()
        || after.counts().skipped() < before.skipped())
      throw new IllegalArgumentException("log cleanup summary is inconsistent");
  }

  public CleanupCounts attemptCounts() {
    return new CleanupCounts(
        after.counts().target() - before.target(),
        after.counts().deleted() - before.deleted(),
        after.counts().skipped() - before.skipped());
  }

  public int exitCode() {
    return after.counts().skipped() > 0 ? 10 : 0;
  }

  @Override
  public String toString() {
    return "LogCleanupSummary[attempt="
        + attemptCounts()
        + ", cumulative="
        + after.counts()
        + ", exitCode="
        + exitCode()
        + "]";
  }
}
