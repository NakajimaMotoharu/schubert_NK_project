package dev.codex.schubert.nk.batch.repository;

import java.time.Instant;
import java.util.Objects;
import org.jspecify.annotations.NullMarked;

/**
 * Terminal metadata for exactly one activation, never proof that the parent gates ran. NK-BAT-001;
 * OPS-009/UI251/SS331/341/343 6.13; SSC-055/PG-D-156; PT-BAT-038..045.
 */
@NullMarked
public record MaintenanceCompletion(
    MaintenanceActivation activation, Instant endedAt, Outcome outcome) {
  public enum Outcome {
    SUCCESS(0),
    WARNING(10);

    private final int processExitCode;

    Outcome(int exitCode) {
      this.processExitCode = exitCode;
    }

    public int exitCode() {
      return processExitCode;
    }
  }

  public MaintenanceCompletion {
    Objects.requireNonNull(activation, "activation");
    Objects.requireNonNull(endedAt, "completion time");
    Objects.requireNonNull(outcome, "completion outcome");
    if (endedAt.isBefore(activation.run().cutoff())
        || endedAt.isAfter(Instant.parse("9999-12-31T23:59:59.999999Z"))
        || endedAt.getNano() % 1000 != 0)
      throw new IllegalArgumentException("invalid maintenance completion time");
  }

  @Override
  public String toString() {
    return "MaintenanceCompletion[identity/time=<redacted>]";
  }
}
