package dev.codex.schubert.nk.batch.cleanup;

import dev.codex.schubert.nk.batch.repository.BatchStepAttempt;
import dev.codex.schubert.nk.batch.repository.CleanupCounts;
import dev.codex.schubert.nk.batch.repository.CleanupKind;
import dev.codex.schubert.nk.batch.repository.CleanupStepChunk;
import java.util.Objects;
import org.jspecify.annotations.NullMarked;

/**
 * Stored whole-step totals differ from this invocation's confirmed delta. Deferred FK is NOT END.
 * NK-BAT-001/OPS009/DAT009/UI251/SS331 3.14/332/341; SSC057/PG164; BAT154..161/170..177.
 */
@NullMarked
public record StepCleanupSummary(
    BatchStepAttempt attempt,
    CleanupKind kind,
    CleanupCounts before,
    CleanupCounts after,
    boolean deferred) {
  public StepCleanupSummary {
    CleanupStepChunk.requireMapping(attempt, kind);
    Objects.requireNonNull(before, "initial totals");
    Objects.requireNonNull(after, "stored totals");
    if (before.skipped() != 0
        || after.skipped() != 0
        || after.target() < before.target()
        || (deferred && kind != CleanupKind.QUESTIONS))
      throw new IllegalArgumentException("invalid step cleanup summary");
  }

  public CleanupCounts callCounts() {
    return new CleanupCounts(
        after.target() - before.target(), after.deleted() - before.deleted(), 0);
  }

  public boolean complete() {
    return !deferred;
  }

  @Override
  public String toString() {
    return "StepCleanupSummary[observation=<redacted>]";
  }
}
