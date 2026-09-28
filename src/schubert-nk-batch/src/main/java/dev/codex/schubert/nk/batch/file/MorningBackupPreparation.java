package dev.codex.schubert.nk.batch.file;

import dev.codex.schubert.nk.batch.platform.BackupWorkerRequest;
import dev.codex.schubert.nk.batch.repository.BatchRun;
import dev.codex.schubert.nk.batch.repository.BatchStep;
import dev.codex.schubert.nk.batch.repository.BatchStepAttempt;
import dev.codex.schubert.nk.batch.repository.MaintenanceRunState;
import dev.codex.schubert.nk.batch.repository.MorningDatabaseSession;
import java.io.IOException;
import java.time.Clock;
import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.Objects;
import java.util.UUID;
import org.jspecify.annotations.NullMarked;

/**
 * Parent-only handoff from committed backup begins to one nonsecret worker request. The caller
 * retains M/A, the durable original and dedicated DB scope; this class neither starts a worker nor
 * asserts an archive or backup success. The request is never published before both DB begins have
 * committed and their handles match the original run. NK-OPS-001; OPS009/BAK001/UI251/SS331§8.3,
 * 341§6.1-6.2/343§6.15/SSC092/094/104; PG347/PT-OPS-MBPREP001-006.
 */
@NullMarked
final class MorningBackupPreparation {
  @FunctionalInterface
  interface Publisher {
    void publish(BackupWorkerRequest request, UUID part) throws IOException;
  }

  @FunctionalInterface
  interface Continuation<T> {
    T execute(BackupWorkerRequest request, MorningDatabaseSession.BackupBegins begins)
        throws IOException;
  }

  private MorningBackupPreparation() {}

  static <T> T execute(
      MaintenanceRunState state,
      MorningDatabaseSession.Access database,
      Clock clock,
      boolean recoverAbandoned,
      Publisher publisher,
      UUID part,
      Continuation<T> continuation)
      throws IOException {
    Objects.requireNonNull(state, "original run state");
    Objects.requireNonNull(database, "owned DB capability");
    Objects.requireNonNull(clock, "backup clock");
    Objects.requireNonNull(publisher, "new-only request publisher");
    Objects.requireNonNull(part, "new request part");
    Objects.requireNonNull(continuation, "same-run backup continuation");
    BatchRun run = state.activation().run();
    if (state.completion().isPresent() || part.equals(run.id()) || part.equals(new UUID(0, 0)))
      throw unavailable();
    Instant started =
        Objects.requireNonNull(clock.instant(), "backup content start")
            .truncatedTo(ChronoUnit.MICROS);
    if (started.isBefore(run.cutoff())) throw unavailable();
    // Validate the immutable request before a transaction can commit. The part is a separate
    // caller-owned new-only filename and never an arbitrary output path.
    BackupWorkerRequest request = new BackupWorkerRequest(run.id(), started);
    MorningDatabaseSession.BackupBegins begins =
        Objects.requireNonNull(
            database.beginBackup(run, started, recoverAbandoned), "committed backup begins");
    valid(begins.database(), BatchStep.BACKUP_DB, run, started);
    valid(begins.configuration(), BatchStep.BACKUP_CONFIG, run, started);
    if (begins.database().id() == begins.configuration().id()) throw unavailable();
    publisher.publish(request, part);
    return Objects.requireNonNull(continuation.execute(request, begins), "backup continuation");
  }

  private static void valid(BatchStepAttempt attempt, BatchStep step, BatchRun run, Instant now)
      throws IOException {
    if (!attempt.run().equals(run)
        || attempt.step() != step
        || attempt.skipped()
        || attempt.startedAt().isAfter(now)) throw unavailable();
  }

  private static IOException unavailable() {
    return new IOException("Morning backup preparation unavailable");
  }
}
