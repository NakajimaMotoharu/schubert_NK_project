package dev.codex.schubert.nk.batch.repository;

import java.time.Instant;
import java.util.Objects;
import java.util.UUID;
import org.jspecify.annotations.NullMarked;

/** NK-BAT-001; OPS-009; UI251; SS341§3/7; PG-D-137; PT-BAT-001. */
@NullMarked
public record BatchRun(UUID id, Instant cutoff) {
  public BatchRun {
    Objects.requireNonNull(id, "run ID");
    Objects.requireNonNull(cutoff, "cutoff");
    if (cutoff.isBefore(Instant.parse("0001-01-01T00:00:00Z"))
        || cutoff.isAfter(Instant.parse("9999-12-31T23:59:59.999999Z"))
        || cutoff.getNano() % 1000 != 0)
      throw new IllegalArgumentException("batch cutoff is outside the timestamp contract");
  }

  @Override
  public String toString() {
    return "BatchRun[identity/cutoff=<redacted>]";
  }
}
