package dev.codex.schubert.nk.batch.repository;

import java.util.Objects;
import org.jspecify.annotations.NullMarked;

/**
 * NK-BAT-001; OPS009/DAT009/UI251/SS331 3.13/341 7.3; SSC049/PG162; BAT114..121. A bounded DB
 * observation, not proof of fresh child termination or parent exclusion.
 */
@NullMarked
public record InspectionSummary(BatchRun run, CleanupCounts counts, boolean complete) {
  public InspectionSummary {
    Objects.requireNonNull(run, "fixed run");
    Objects.requireNonNull(counts, "inspection counts");
  }

  @Override
  public String toString() {
    return "InspectionSummary[observation=<redacted>]";
  }
}
