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
 * partial valid invocations still exit30, never0/10. Known worker failure continuation remains
 * isolated under the outer oneshot budget; no unexecuted phase is invented as FAILED. No raw
 * diagnostic is printed. NK-OPS-001; OPS009/UI251/SS341/343/SSC100-102; PG339; PT-OPS-MMAIN001-007.
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

  private static void executeBackup(MorningParentBudget budget, Optional<UUID> runId)
      throws IOException {
    MorningBackupStage.VerifiedEpochWork<MorningBackupUnitCycle.Outcome> work =
        (state, database, epoch, request, begins, part, original) -> {
          var root = RootStartupContext.create();
          var snapshot = root.capture(RootStartupContext.Service.MORNING);
          var requests = openRequests();
          return ResourceScope.use(
              requests::close,
              () -> {
                var files = new BackupWorkerRequestFiles(requests, LinuxInodeSecurity.create());
                EnvironmentInodePolicy.require(files.read().equals(request));
                var terminal = BackupUnitTermination.create(root, snapshot);
                return MorningBackupUnitCycle.create(root, snapshot, budget)
                    .execute(
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
                          if (outcome != MorningBackupUnitCycle.Outcome.SUCCESS)
                            throw new IOException("Backup failure continuation unavailable");
                          budget.requireWithin();
                          root.recheck(snapshot);
                          original.verify();
                          new MorningBackupArtifacts(root, snapshot, budget)
                              .complete(request, begins, part, database);
                          budget.requireWithin();
                          root.recheck(snapshot);
                          original.verify();
                        });
              });
        };
    if (runId.isPresent()) {
      MorningBackupStage.resumeVerifiedEpoch(budget, runId.orElseThrow(), work);
    } else {
      MorningBackupStage.freshVerifiedEpoch(budget, work);
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
    var budget = MorningParentBudget.create();
    try {
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
