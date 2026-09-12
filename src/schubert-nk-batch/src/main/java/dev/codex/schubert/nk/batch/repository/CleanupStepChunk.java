package dev.codex.schubert.nk.batch.repository;

import java.util.Objects;
import java.util.Optional;
import org.jspecify.annotations.NullMarked;

/**
 * Uncommitted per-call deletion and explicitly known step totals. Not an OS/backup/whole-step
 * certificate. NK-BAT-001/OPS009/DAT009/UI251/SS331 3.14/332/341; SSC057/PG164; BAT154..169.
 */
@NullMarked
public record CleanupStepChunk(
    BatchStepAttempt attempt,
    CleanupKind kind,
    CleanupCounts counts,
    Optional<CleanupCounts> stepCounts,
    boolean complete,
    Reason reason) {
  public enum Reason {
    OK,
    LOCK_BUSY,
    BACKUP_GATE,
    FOREIGN_KEY_CONFLICT
  }

  public CleanupStepChunk {
    requireMapping(attempt, kind);
    Objects.requireNonNull(counts, "chunk counts");
    Objects.requireNonNull(stepCounts, "step counts");
    Objects.requireNonNull(reason, "chunk reason");
    boolean known = reason == Reason.OK || reason == Reason.FOREIGN_KEY_CONFLICT;
    if (counts.skipped() != 0
        || stepCounts.isPresent() != known
        || (reason != Reason.OK && counts.target() != 0)
        || complete != (reason == Reason.OK && counts.target() == 0)
        || (reason == Reason.FOREIGN_KEY_CONFLICT && kind != CleanupKind.QUESTIONS))
      throw new IllegalArgumentException("invalid step cleanup observation");
    if (stepCounts.isPresent()) {
      CleanupCounts total = stepCounts.orElseThrow();
      if (total.skipped() != 0 || total.target() < counts.target())
        throw new IllegalArgumentException("invalid step cleanup totals");
    }
  }

  public static void requireMapping(BatchStepAttempt attempt, CleanupKind kind) {
    Objects.requireNonNull(attempt, "step attempt");
    Objects.requireNonNull(kind, "cleanup kind");
    if (attempt.skipped() || kind == CleanupKind.LOGS || attempt.step() != kind.step())
      throw new IllegalArgumentException("invalid step cleanup mapping");
  }

  public Optional<CleanupCounts> beforeCounts() {
    return stepCounts.map(
        total ->
            new CleanupCounts(
                total.target() - counts.target(), total.deleted() - counts.deleted(), 0));
  }

  @Override
  public String toString() {
    return "CleanupStepChunk[observation=<redacted>]";
  }
}
