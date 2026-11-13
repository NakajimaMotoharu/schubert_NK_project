package dev.codex.schubert.nk.api.maintenance;

import dev.codex.schubert.nk.api.error.TemporaryInfrastructureException;
import dev.codex.schubert.nk.bootstrap.MaintenanceOwnerFrame;
import java.io.IOException;
import java.util.Objects;
import java.util.Optional;
import java.util.function.LongSupplier;
import org.jspecify.annotations.NullMarked;

/**
 * Single-worker bounded run, using the same immutable run/cutoff for every committed chunk. Keys
 * and providers must remain live until this call ends. No retry, resource ownership,
 * systemd/HTTP/JMS startup or process success declaration. NK-DAT-001; DAT-009/OPS-009/MQ-008;
 * UI251; SS324 12.7/341 7.3; QA-046/SSC-049/PG-D-130; PT-DB-INBOX-097..104.
 */
@NullMarked
public final class InspectionRunExecutor {
  private static final long TIME_LIMIT_NANOS = 1_800_000_000_000L;
  private final InboxCleanup cleanup;
  private final LongSupplier monotonicNanos;
  private final Optional<MaintenanceOwnerFrame.Guard> parentGuard;

  public InspectionRunExecutor(InboxCleanup cleanup, LongSupplier monotonicNanos) {
    this(cleanup, monotonicNanos, Optional.empty());
  }

  InspectionRunExecutor(
      InboxCleanup cleanup,
      LongSupplier monotonicNanos,
      Optional<MaintenanceOwnerFrame.Guard> parentGuard) {
    this.parentGuard = Objects.requireNonNull(parentGuard, "parent guard profile");
    this.cleanup = Objects.requireNonNull(cleanup, "cleanup");
    this.monotonicNanos = Objects.requireNonNull(monotonicNanos, "monotonicNanos");
  }

  public InspectionExecution run(InspectionRun run) {
    Objects.requireNonNull(run, "run");
    long started = monotonicNanos.getAsLong();
    Optional<InspectionProgress> last = Optional.empty();
    while (true) {
      var stop = stopReason(started);
      if (stop.isPresent()) return new InspectionExecution(stop.orElseThrow(), last);
      InspectionProgress progress;
      try {
        progress = cleanup.runChunk(run, 1000);
      } catch (InboxMaintenanceException failure) {
        return new InspectionExecution(InspectionExecution.Status.STORAGE_FAILURE, last);
      }
      last = Optional.of(progress);
      stop = stopReason(started);
      if (stop.isPresent()) return new InspectionExecution(stop.orElseThrow(), last);
      if (progress.complete()) {
        return new InspectionExecution(
            progress.protectedRows() == 0
                ? InspectionExecution.Status.SUCCESS
                : InspectionExecution.Status.WARNING,
            last);
      }
    }
  }

  private Optional<InspectionExecution.Status> stopReason(long started) {
    if (Thread.currentThread().isInterrupted())
      return Optional.of(InspectionExecution.Status.INTERRUPTED);
    if (parentGuard.isPresent())
      try {
        parentGuard.orElseThrow().check();
      } catch (IOException unavailable) {
        // BUG2826: preserve fatal graph identity before the ordinary fixed outcome.
        TemporaryInfrastructureException.preserveFatal(unavailable);
        return Optional.of(InspectionExecution.Status.TIME_LIMIT);
      }
    // Signed subtraction tolerates nanoTime's natural wrap; a negative delta is fail-closed.
    long elapsed = monotonicNanos.getAsLong() - started;
    // BUG186/YKT146: also observe interruption at the final clock boundary.
    if (Thread.currentThread().isInterrupted())
      return Optional.of(InspectionExecution.Status.INTERRUPTED);
    if (elapsed < 0 || elapsed >= TIME_LIMIT_NANOS)
      return Optional.of(InspectionExecution.Status.TIME_LIMIT);
    return Optional.empty();
  }
}
