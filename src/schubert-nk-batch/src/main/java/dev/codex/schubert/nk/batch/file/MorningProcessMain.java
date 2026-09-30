package dev.codex.schubert.nk.batch.file;

import dev.codex.schubert.nk.batch.platform.BackupUnitTermination;
import dev.codex.schubert.nk.batch.platform.MorningBackupUnitCycle;
import dev.codex.schubert.nk.batch.platform.MorningParentBudget;
import dev.codex.schubert.nk.batch.platform.RootStartupContext;
import dev.codex.schubert.nk.batch.platform.StopGateException;
import dev.codex.schubert.nk.storage.*;
import edu.umd.cs.findbugs.annotations.SuppressFBWarnings;
import edu.umd.cs.findbugs.annotations.SuppressMatchType;
import java.io.IOException;
import java.nio.file.Path;
import java.util.Objects;
import java.util.Optional;
import java.util.UUID;
import org.jspecify.annotations.NullMarked;

/**
 * External same-owner Morning→Backup wiring. Actual artifacts/DB are completed and request/marker
 * retired only after full termination and original/current proof. S2/S3 are not assembled yet:
 * partial valid invocations still exit30, never0/10. A fresh normal worker failure is recorded and
 * safely retired, but subsequent cleanup/issuer remains incomplete. UNKNOWN is retained under the
 * outer oneshot budget; no unexecuted phase is invented as FAILED. No raw diagnostic is printed.
 * NK-OPS-001; OPS009/UI251/SS341/343/SSC100-102; PG339; PT-OPS-MMAIN001-007.
 */
@NullMarked
public final class MorningProcessMain {
  @FunctionalInterface
  interface Admission {
    void verify(MorningParentBudget budget) throws IOException;
  }

  @FunctionalInterface
  interface ResumeAdmission {
    void verify(MorningParentBudget budget, UUID runId) throws IOException;
  }

  private MorningProcessMain() {}

  public static void main(String[] args) {
    System.exit(
        run(
            args,
            MorningProcessMain::executeBackup,
            (budget, runId) -> executeBackup(budget, Optional.of(runId))));
  }

  private static void executeBackup(MorningParentBudget budget) throws IOException {
    executeBackup(budget, Optional.empty());
  }

  private static void executeBackup(MorningParentBudget entryBudget, Optional<UUID> runId)
      throws IOException {
    var entryRoot = RootStartupContext.create();
    var entrySnapshot = entryRoot.capture(RootStartupContext.Service.MORNING);
    var budget =
        MorningParentBudget.borrow(
            entryRoot.maintenanceDeadline(entrySnapshot, entryBudget.deadlineNanos()));
    MorningBackupStage.VerifiedEpochWork<MorningBackupUnitCycle.Outcome> work =
        (state, database, epoch, request, begins, part, original, completion) -> {
          var root = RootStartupContext.create();
          var snapshot = root.capture(RootStartupContext.Service.MORNING);
          var requests = openRequests();
          return ResourceScope.use(
              requests::close,
              () -> {
                var files = new BackupWorkerRequestFiles(requests, LinuxInodeSecurity.create());
                EnvironmentInodePolicy.require(files.read().equals(request));
                var terminal = BackupUnitTermination.create(root, snapshot);
                var backupCycle = MorningBackupUnitCycle.create(root, snapshot, budget);
                var backupOutcome =
                    backupCycle.execute(
                        () -> {
                          budget.requireWithin();
                          root.recheck(snapshot);
                          original.verify();
                          database.recheckConsistent(state.activation().run());
                          var startup = openCurrent();
                          ResourceScope.use(
                              startup::close,
                              () -> {
                                EnvironmentInodePolicy.require(
                                    new StartupPermitFiles(startup, LinuxInodeSecurity.create())
                                        .current()
                                        .equals(epoch));
                                return Boolean.TRUE;
                              });
                          EnvironmentInodePolicy.require(
                              files.read().equals(request) && terminal.quiescent().isPresent());
                          budget.requireWithin();
                          root.recheck(snapshot);
                          original.verify();
                          files.retire(request);
                          budget.requireWithin();
                          root.recheck(snapshot);
                          original.verify();
                        },
                        outcome -> {
                          budget.requireWithin();
                          root.recheck(snapshot);
                          original.verify();
                          if (request.verification().isPresent()
                              && outcome != MorningBackupUnitCycle.Outcome.SUCCESS)
                            throw new IOException("Prior backup verification unavailable");
                          completeObservedBackup(
                              outcome, begins, database, java.time.Clock.systemUTC(), completion);
                          budget.requireWithin();
                          root.recheck(snapshot);
                          original.verify();
                        });
                if (backupOutcome == MorningBackupUnitCycle.Outcome.SUCCESS) {
                  MorningCleanupExecution.execute(
                      root,
                      snapshot,
                      budget,
                      state,
                      database,
                      epoch,
                      original,
                      completion.verifiedManifest());
                } else if (backupOutcome == MorningBackupUnitCycle.Outcome.FAILED) {
                  MorningCleanupExecution.executeFailed(
                      root,
                      snapshot,
                      budget,
                      state,
                      database,
                      epoch,
                      original,
                      begins,
                      backupCycle.completedReceipt());
                }
                var broker =
                    MorningBrokerExecution.execute(
                        root, snapshot, budget, state, database, epoch, original);
                MorningExpiryExecution.execute(
                    root, snapshot, budget, state, database, epoch, original, broker);
                return backupOutcome;
              });
        };
    if (runId.isPresent()) {
      MorningBackupStage.resumeVerifiedEpoch(budget, runId.orElseThrow(), work);
    } else {
      MorningBackupStage.freshVerifiedEpoch(budget, work);
    }
  }

  @FunctionalInterface
  interface Archive {
    void complete() throws IOException;

    default dev.codex.schubert.nk.batch.backup.BackupManifest verifiedManifest()
        throws IOException {
      throw new IOException("actual backup completion unavailable");
    }
  }

  @FunctionalInterface
  interface VerifiedArchive {
    dev.codex.schubert.nk.batch.backup.BackupManifest complete() throws IOException;
  }

  /** SSC119: retain the actual successful completion value only within the same owner callback. */
  static Archive archive(VerifiedArchive actual) {
    Objects.requireNonNull(actual, "actual archive operation");
    return new Archive() {
      private final long thread = Thread.currentThread().threadId();
      private boolean attempted;
      private Optional<dev.codex.schubert.nk.batch.backup.BackupManifest> manifest =
          Optional.empty();

      public void complete() throws IOException {
        if (attempted || Thread.currentThread().threadId() != thread)
          throw new IOException("actual backup completion unavailable");
        attempted = true;
        manifest =
            Optional.of(Objects.requireNonNull(actual.complete(), "actual verified manifest"));
      }

      public dev.codex.schubert.nk.batch.backup.BackupManifest verifiedManifest()
          throws IOException {
        if (Thread.currentThread().threadId() != thread || manifest.isEmpty())
          throw new IOException("actual backup completion unavailable");
        return manifest.orElseThrow();
      }
    };
  }

  /** SSC115: called only after a fresh normal worker result and explicit whole-Unit stop. */
  static void completeObservedBackup(
      MorningBackupUnitCycle.Outcome outcome,
      dev.codex.schubert.nk.batch.repository.MorningDatabaseSession.BackupBegins begins,
      dev.codex.schubert.nk.batch.repository.MorningDatabaseSession.Access database,
      java.time.Clock clock,
      Archive archive)
      throws IOException {
    Objects.requireNonNull(outcome, "actual terminal Backup outcome");
    Objects.requireNonNull(begins, "same-owner committed Backup begins");
    Objects.requireNonNull(database, "same-owner session capability");
    Objects.requireNonNull(clock, "actual UTC completion clock");
    Objects.requireNonNull(archive, "actual successful archive completion");
    if (outcome == MorningBackupUnitCycle.Outcome.SUCCESS) {
      archive.complete();
    } else {
      var ended =
          Objects.requireNonNull(clock.instant(), "actual failed content end")
              .truncatedTo(java.time.temporal.ChronoUnit.MICROS);
      if (ended.isBefore(begins.database().startedAt()))
        throw new IOException("Backup completion clock unavailable");
      var failed =
          new dev.codex.schubert.nk.batch.repository.BatchStepResult(
              dev.codex.schubert.nk.batch.repository.BatchStepResult.Status.FAILED,
              1,
              0,
              1,
              0,
              dev.codex.schubert.nk.batch.repository.BatchStepResult.Reason.COMMAND_FAILURE);
      database.failBackup(begins, ended, failed, failed);
    }
  }

  @SuppressFBWarnings(
      value = "DMI_HARDCODED_ABSOLUTE_FILENAME",
      matchType = SuppressMatchType.EXACT,
      justification = "SS343 fixed root-only request namespace")
  private static OwnedTransferDirectory openRequests() throws IOException {
    return OwnedTransferDirectory.open(
        LinuxDirectoryCalls.create(), Path.of("/run/schubert-nk/backup-request"));
  }

  @SuppressFBWarnings(
      value = "DMI_HARDCODED_ABSOLUTE_FILENAME",
      matchType = SuppressMatchType.EXACT,
      justification = "SS343 fixed root-only current namespace")
  private static OwnedTransferDirectory openCurrent() throws IOException {
    return OwnedTransferDirectory.open(
        LinuxDirectoryCalls.create(), Path.of("/run/schubert-nk/startup"));
  }

  static int run(String[] args, Admission admission) {
    return run(
        args,
        admission,
        (budget, runId) -> {
          throw new IOException("Resume admission unavailable");
        });
  }

  static int run(String[] args, Admission admission, ResumeAdmission resume) {
    Objects.requireNonNull(args, "Morning arguments");
    Objects.requireNonNull(admission, "fixed Morning admission");
    Objects.requireNonNull(resume, "fixed Morning resume admission");
    Optional<UUID> selected = Optional.empty();
    if (args.length != 0) {
      if (args.length != 2 || !"--resume".equals(args[0]) || args[1] == null) return 70;
      UUID runId;
      try {
        runId = UUID.fromString(args[1]);
      } catch (IllegalArgumentException invalid) {
        return 70;
      }
      if (runId.equals(new UUID(0, 0)) || !runId.toString().equals(args[1])) return 70;
      selected = Optional.of(runId);
    }
    try {
      var budget = MorningParentBudget.create();
      budget.requireWithin();
      if (selected.isPresent()) resume.verify(budget, selected.orElseThrow());
      else admission.verify(budget);
      budget.requireWithin();
      return 30;
    } catch (IOException | StopGateException known) {
      return 30;
    }
  }
}
