package dev.codex.schubert.nk.batch.repository;

import java.util.Objects;
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;

/**
 * Fixed terminal counters and diagnostic allowlist. Protected skips are not silently failures.
 * NK-BAT-001/OPS009/UI251/SS331 8.3/341; SSC055/PG163; BAT130..137.
 */
@NullMarked
public record BatchStepResult(
    Status status, long target, long success, long failure, long bytes, Reason reason) {
  public enum Status {
    SUCCESS,
    WARNING,
    FAILED,
    SKIPPED
  }

  public enum Reason {
    NONE(null),
    ALREADY_SUCCESSFUL("step already successful for business date"),
    BACKUP_UNAVAILABLE("verified backup unavailable"),
    PROTECTED_RECORDS("protected records retained"),
    ABANDONED("previous same-run attempt abandoned"),
    DATABASE_FAILURE("batch database operation failed"),
    COMMAND_FAILURE("batch command failed"),
    SAFETY_FAILURE("batch safety check failed"),
    IO_FAILURE("batch file operation failed"),
    TIMEOUT("batch step deadline reached"),
    INTERRUPTED("batch step interrupted");

    private final @Nullable String diagnosticSummary;

    Reason(@Nullable String diagnosticSummary) {
      this.diagnosticSummary = diagnosticSummary;
    }

    public @Nullable String code() {
      return this == NONE ? null : name();
    }

    public @Nullable String summary() {
      return diagnosticSummary;
    }

    private boolean allows(Status status) {
      return switch (this) {
        case NONE -> status == Status.SUCCESS;
        case ALREADY_SUCCESSFUL, BACKUP_UNAVAILABLE -> status == Status.SKIPPED;
        case PROTECTED_RECORDS -> status == Status.WARNING;
        case ABANDONED -> status == Status.FAILED;
        default -> status == Status.WARNING || status == Status.FAILED;
      };
    }
  }

  public BatchStepResult {
    Objects.requireNonNull(status, "step status");
    Objects.requireNonNull(reason, "step reason");
    if (target < 0
        || success < 0
        || failure < 0
        || bytes < 0
        || !reason.allows(status)
        || (status == Status.SUCCESS && failure != 0)
        || (status == Status.SKIPPED
            && (target != 0 || success != 0 || failure != 0 || bytes != 0)))
      throw new IllegalArgumentException("invalid batch step result");
  }

  @Override
  public String toString() {
    return "BatchStepResult[observation=<redacted>]";
  }
}
