package dev.codex.schubert.nk.batch.cleanup;

import java.util.Objects;
import org.jspecify.annotations.NullMarked;

/**
 * Fixed incomplete outcome; no JDBC cause or values. NK-BAT-001; OPS-009; UI251; SS352; PG-D-138;
 * PT-BAT-021..029.
 */
@NullMarked
public final class CleanupStoppedException extends RuntimeException {
  private static final long serialVersionUID = 1L;
  private final CleanupStopReason reason;

  public CleanupStoppedException(CleanupStopReason reason) {
    super("cleanup did not complete");
    this.reason = Objects.requireNonNull(reason, "reason");
  }

  public CleanupStopReason reason() {
    return reason;
  }
}
