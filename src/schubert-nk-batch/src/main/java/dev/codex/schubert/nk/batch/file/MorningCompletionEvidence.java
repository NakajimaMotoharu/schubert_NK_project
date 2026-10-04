package dev.codex.schubert.nk.batch.file;

import dev.codex.schubert.nk.batch.backup.BackupManifest;
import dev.codex.schubert.nk.batch.platform.BackupUnitReceiptGate;
import dev.codex.schubert.nk.batch.platform.MorningBackupUnitCycle;
import dev.codex.schubert.nk.batch.repository.*;
import dev.codex.schubert.nk.bootstrap.MaintenanceOwnerFrame;
import java.io.IOException;
import java.time.Clock;
import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.*;
import org.jspecify.annotations.NullMarked;

/** Immutable actual ten-step data, never closed retention/file authority. SS341/343 SSC178/318. */
@NullMarked
record MorningCompletionEvidence(
    MorningBackupUnitCycle.Outcome backupOutcome,
    MorningDatabaseSession.BackupBegins begins,
    Optional<BackupManifest> manifest,
    MorningDatabaseSession.BackupObservation backup,
    BackupUnitReceiptGate.TerminalReceipt backupReceipt,
    MorningCleanupExecution.Completion cleanup,
    MorningDatabaseSession.ExpiryObservation expiry) {
  MorningCompletionEvidence {
    Objects.requireNonNull(backupOutcome);
    Objects.requireNonNull(begins);
    Objects.requireNonNull(manifest);
    Objects.requireNonNull(backup);
    Objects.requireNonNull(backupReceipt);
    Objects.requireNonNull(cleanup);
    Objects.requireNonNull(expiry);
    var run = begins.database().run();
    if (!run.equals(begins.configuration().run())
        || !begins.database().equals(backup.current().get(0).attempt())
        || !begins.configuration().equals(backup.current().get(1).attempt())
        || backupReceipt.target()
            != dev.codex.schubert.nk.batch.platform.BackupUnitStartClient.Target.BACKUP
        || (backupOutcome == MorningBackupUnitCycle.Outcome.SUCCESS) != manifest.isPresent()
        || (backupOutcome == MorningBackupUnitCycle.Outcome.SUCCESS)
            != (backupReceipt.exitCode() == 0)) throw invalid();
    for (var row : backup.current()) {
      if (!run.equals(row.attempt().run())) throw invalid();
      if (backupOutcome == MorningBackupUnitCycle.Outcome.FAILED) {
        if (row.result().status() != BatchStepResult.Status.FAILED
            || row.result().reason() != BatchStepResult.Reason.COMMAND_FAILURE) throw invalid();
      } else if (row.result().status() != BatchStepResult.Status.SUCCESS
          && row.result().status() != BatchStepResult.Status.SKIPPED) throw invalid();
    }
    for (var row : cleanup.terminal().entries()) {
      if (!run.equals(row.attempt().run())) throw invalid();
      boolean unavailable = row.result().reason() == BatchStepResult.Reason.BACKUP_UNAVAILABLE;
      if (unavailable
          != (backupOutcome == MorningBackupUnitCycle.Outcome.FAILED
              && row.attempt().step() != BatchStep.CLEAN_TRANSFER)) throw invalid();
    }
    if (!run.equals(expiry.begins().current().run())
        || expiry.result().status() == BatchStepResult.Status.FAILED
        || expiry.receipt().exitCode()
            != (expiry.result().status() == BatchStepResult.Status.WARNING ? 10 : 0))
      throw invalid();
  }

  /** Reacquire complete DB rows/audit and fresh fixed receipt handles; never reuse closed files. */
  void verify(
      MorningDatabaseSession.Access database, Clock clock, MaintenanceOwnerFrame.Guard owner)
      throws IOException {
    Objects.requireNonNull(database);
    Objects.requireNonNull(clock);
    Objects.requireNonNull(owner);
    owner.check();
    var run = begins.database().run();
    database.recheckConsistent(run);
    if (!backup.equals(database.observeBackup(begins, manifest, now(clock), owner)))
      throw unavailable();
    var actual =
        backupOutcome == MorningBackupUnitCycle.Outcome.FAILED
            ? database.observeCleanupBackupUnavailable(run, cleanup.receipt().exitCode(), owner)
            : database.observeCleanup(run, cleanup.receipt().exitCode(), owner);
    if (!cleanup.terminal().equals(actual)
        || !cleanup.references().equals(database.cleanupReferences(actual, owner)))
      throw unavailable();
    database.recheckExpiry(expiry, owner);
    backupReceipt.requireStillPresent();
    cleanup.receipt().requireStillPresent();
    expiry.receipt().requireStillPresent();
    database.recheckConsistent(run);
    owner.check();
  }

  MaintenanceCompletion completion(MaintenanceActivation activation, Clock clock)
      throws IOException {
    Objects.requireNonNull(activation);
    Objects.requireNonNull(clock);
    if (!activation.run().equals(begins.database().run())) throw unavailable();
    var ended = now(clock);
    for (var row : backup.current()) if (ended.isBefore(row.ended())) throw unavailable();
    for (var row : cleanup.terminal().entries())
      if (ended.isBefore(row.endedAt())) throw unavailable();
    if (ended.isBefore(expiry.ended())) throw unavailable();
    boolean warning =
        backupOutcome == MorningBackupUnitCycle.Outcome.FAILED
            || cleanup.terminal().exitCode() == 10
            || expiry.result().status() == BatchStepResult.Status.WARNING;
    return new MaintenanceCompletion(
        activation,
        ended,
        warning ? MaintenanceCompletion.Outcome.WARNING : MaintenanceCompletion.Outcome.SUCCESS);
  }

  private static Instant now(Clock clock) {
    return Objects.requireNonNull(clock.instant()).truncatedTo(ChronoUnit.MICROS);
  }

  private static IllegalArgumentException invalid() {
    return new IllegalArgumentException("Morning completion evidence invalid");
  }

  private static IOException unavailable() {
    return new IOException("Morning completion evidence unavailable");
  }

  @Override
  public String toString() {
    return "MorningCompletionEvidence[actual=<redacted>]";
  }
}
