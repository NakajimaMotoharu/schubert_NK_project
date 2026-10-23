package dev.codex.schubert.nk.batch.monitoring;

import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.CauseClearance;
import java.time.Duration;
import java.time.Instant;
import java.util.Objects;

/**
 * Immutable values, not proof of actual source/owner/cause clearance. NK-OPS-001/P018-09;
 * MON005..013; UI252; SS351; PG-D521/PT-OPS-MONPIPE-001.
 */
public record ObservationContext(CauseClearance clearance, Instant at, Duration elapsed) {
  public ObservationContext {
    Objects.requireNonNull(clearance, "cause clearance");
    Objects.requireNonNull(at, "observation time");
    Objects.requireNonNull(elapsed, "monotonic elapsed");
    if (elapsed.isNegative()) throw new IllegalArgumentException("invalid alert elapsed time");
  }
}
