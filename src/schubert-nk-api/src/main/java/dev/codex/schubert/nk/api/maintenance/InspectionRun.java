package dev.codex.schubert.nk.api.maintenance;

import java.time.Instant;
import java.util.Objects;
import java.util.UUID;
import org.jspecify.annotations.NullMarked;

/** Immutable cleanup cutoff, never recalculated during resume. SS341/PG-D-122; PT033..040. */
@NullMarked
public record InspectionRun(UUID id, Instant cutoff) {
  public InspectionRun {
    Objects.requireNonNull(id, "run ID");
    Objects.requireNonNull(cutoff, "cutoff");
    if (cutoff.isBefore(Instant.parse("0001-01-01T00:00:00Z"))
        || cutoff.isAfter(Instant.parse("9999-12-31T23:59:59.999999Z"))
        || cutoff.getNano() % 1000 != 0) {
      throw new IllegalArgumentException("inspection cutoff is outside the timestamp contract");
    }
  }

  @Override
  public String toString() {
    return "InspectionRun[identity/cutoff=<redacted>]";
  }
}
