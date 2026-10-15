package dev.codex.schubert.nk.batch.cleanup;

import dev.codex.schubert.nk.batch.repository.BatchRun;
import dev.codex.schubert.nk.batch.repository.CleanupCounts;
import dev.codex.schubert.nk.batch.repository.InspectionSummary;
import dev.codex.schubert.nk.batch.repository.MaintenanceCompletion.Outcome;
import java.util.Objects;
import java.util.Optional;
import org.jspecify.annotations.NullMarked;

/**
 * Pure reconciliation only, never a fresh-child/OS/backup/step completion certificate. NK-BAT-001;
 * OPS009/DAT009/UI251/SS311/341 7.3; SSC049/PG162; BAT122..129.
 */
@NullMarked
public record InspectionAttempt(
    BatchRun run, CleanupCounts cumulative, CleanupCounts attempt, Outcome outcome) {
  public InspectionAttempt {
    Objects.requireNonNull(run, "fixed run");
    Objects.requireNonNull(cumulative, "cumulative counts");
    Objects.requireNonNull(attempt, "attempt counts");
    Objects.requireNonNull(outcome, "inspection outcome");
    require(attempt.target() <= cumulative.target());
    require(attempt.deleted() <= cumulative.deleted());
    require(attempt.skipped() <= cumulative.skipped());
    require(outcome == expectedOutcome(cumulative));
  }

  public static InspectionAttempt reconcile(
      BatchRun expectedRun,
      Optional<InspectionSummary> before,
      InspectionSummary after,
      int receipt) {
    Objects.requireNonNull(expectedRun, "fixed run");
    Objects.requireNonNull(before, "before observation");
    Objects.requireNonNull(after, "after observation");
    require(after.run().equals(expectedRun));
    require(after.complete());
    Outcome outcome = expectedOutcome(after.counts());
    require(receipt == outcome.exitCode());
    CleanupCounts baseline = new CleanupCounts(0, 0, 0);
    if (before.isPresent()) {
      InspectionSummary previous = before.get();
      require(previous.run().equals(expectedRun));
      baseline = previous.counts();
      if (previous.complete()) require(baseline.equals(after.counts()));
    }
    CleanupCounts cumulative = after.counts();
    require(cumulative.target() >= baseline.target());
    require(cumulative.deleted() >= baseline.deleted());
    require(cumulative.skipped() >= baseline.skipped());
    // Nonnegative monotone components cannot overflow these subtractions.
    var delta =
        new CleanupCounts(
            cumulative.target() - baseline.target(),
            cumulative.deleted() - baseline.deleted(),
            cumulative.skipped() - baseline.skipped());
    return new InspectionAttempt(expectedRun, cumulative, delta, outcome);
  }

  private static Outcome expectedOutcome(CleanupCounts counts) {
    return counts.skipped() == 0 ? Outcome.SUCCESS : Outcome.WARNING;
  }

  private static void require(boolean condition) {
    if (!condition) throw new IllegalArgumentException("inspection attempt mismatch");
  }

  @Override
  public String toString() {
    return "InspectionAttempt[observation=<redacted>]";
  }
}
