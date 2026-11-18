package dev.codex.schubert.nk.api.maintenance;

import java.util.Objects;
import java.util.Optional;
import org.jspecify.annotations.NullMarked;

/**
 * Run outcome, not a certificate for process/backup/key/OS gates. Failure progress is only the last
 * confirmed checkpoint, never an estimate of the latest DB state. NK-DAT-001; DAT-009/OPS-009;
 * UI251; SS324 12.7/341 7.3; QA-046/SSC-049/PG-D-130; PT-DB-INBOX-097..104.
 */
@NullMarked
public record InspectionExecution(Status status, Optional<InspectionProgress> lastConfirmed) {
  public enum Status {
    SUCCESS(0),
    WARNING(10),
    TIME_LIMIT(50),
    INTERRUPTED(50),
    STORAGE_FAILURE(50);

    private final int exitCode;

    Status(int exitCode) {
      this.exitCode = exitCode;
    }
  }

  public InspectionExecution {
    Objects.requireNonNull(status, "status");
    Objects.requireNonNull(lastConfirmed, "lastConfirmed");
    if (status == Status.SUCCESS || status == Status.WARNING) {
      InspectionProgress progress =
          lastConfirmed.orElseThrow(
              () ->
                  new IllegalArgumentException("completed execution requires confirmed progress"));
      if (!progress.complete() || (status == Status.SUCCESS) != (progress.protectedRows() == 0)) {
        throw new IllegalArgumentException("execution status does not match confirmed progress");
      }
    }
  }

  /**
   * Final resource closure and parent gates must also pass before a process uses this exit code.
   */
  public int exitCode() {
    return status.exitCode;
  }

  @Override
  public String toString() {
    return "InspectionExecution[status="
        + status
        + ", lastConfirmed="
        + lastConfirmed.map(InspectionProgress::toString).orElse("unavailable")
        + "]";
  }
}
