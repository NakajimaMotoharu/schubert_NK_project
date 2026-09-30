package dev.codex.schubert.nk.batch.file;

import dev.codex.schubert.nk.batch.platform.BackupWorkerRequest;
import dev.codex.schubert.nk.batch.platform.MorningParentBudget;
import dev.codex.schubert.nk.batch.platform.RootStartupContext;
import dev.codex.schubert.nk.batch.repository.MaintenanceRunState;
import dev.codex.schubert.nk.batch.repository.MorningDatabaseSession;
import java.io.IOException;
import java.time.Clock;
import java.util.Objects;
import java.util.UUID;
import org.jspecify.annotations.NullMarked;

/**
 * Production parent bridge from the continuously held M/A/original/DB scope to committed backup
 * begins and new-only request publication. The work callback remains within all owners and must
 * itself prove worker start/full termination, archives and later parent gates; this bridge alone
 * never marks a backup successful. NK-OPS-001; OPS009/BAK001/UI251/SS341§5-6/343§6.15;
 * SSC089/092/094/104/105; PG349/PT-OPS-MBSTAGE001-004.
 */
@NullMarked
final class MorningBackupStage {
  interface Scope {
    <T> T execute(MorningNewRunAdmission.OwnedContinuation<T> continuation) throws IOException;
  }

  interface EpochScope {
    <T> T execute(MorningControlScope.OwnedEpochWork<T> continuation) throws IOException;
  }

  @FunctionalInterface
  interface OwnedEpochWork<T> {
    T execute(
        MaintenanceRunState state,
        MorningDatabaseSession.Access database,
        StartupPermitRecords.Epoch epoch,
        BackupWorkerRequest request,
        MorningDatabaseSession.BackupBegins begins,
        UUID part)
        throws IOException;
  }

  @FunctionalInterface
  interface VerifiedEpochWork<T> {
    T execute(
        MaintenanceRunState state,
        MorningDatabaseSession.Access database,
        StartupPermitRecords.Epoch epoch,
        BackupWorkerRequest request,
        MorningDatabaseSession.BackupBegins begins,
        UUID part,
        MorningNewRunAdmission.OriginalProof original,
        MorningProcessMain.Archive completion)
        throws IOException;
  }

  @FunctionalInterface
  interface OwnedWork<T> {
    T execute(
        MaintenanceRunState state,
        MorningDatabaseSession.Access database,
        BackupWorkerRequest request,
        MorningDatabaseSession.BackupBegins begins,
        UUID part)
        throws IOException;
  }

  private MorningBackupStage() {}

  static <T> T freshVerifiedEpoch(MorningParentBudget budget, VerifiedEpochWork<T> work)
      throws IOException {
    return verifiedEpoch(budget, java.util.Optional.empty(), work);
  }

  static <T> T resumeVerifiedEpoch(
      MorningParentBudget budget, UUID runId, VerifiedEpochWork<T> work) throws IOException {
    return verifiedEpoch(budget, java.util.Optional.of(runId), work);
  }

  private static <T> T verifiedEpoch(
      MorningParentBudget budget, java.util.Optional<UUID> runId, VerifiedEpochWork<T> work)
      throws IOException {
    Objects.requireNonNull(budget, "parent Morning budget");
    Objects.requireNonNull(work, "verified backup work");
    budget.requireWithin();
    var root = RootStartupContext.create();
    var snapshot = root.capture(RootStartupContext.Service.MORNING);
    UUID part = UUID.randomUUID();
    MorningControlScope.VerifiedEpochWork<T> continuation =
        (state, database, epoch, original) -> {
          if (runId.isPresent()) {
            var prior =
                database.successfulBackup(
                    state.activation().run(),
                    java.time.Instant.now().truncatedTo(java.time.temporal.ChronoUnit.MICROS));
            if (prior.isPresent()) {
              return MorningBackupReuse.execute(
                  root,
                  snapshot,
                  budget,
                  database,
                  prior.orElseThrow(),
                  (request, begins, completion) -> {
                    original.verify();
                    budget.requireWithin();
                    MorningBackupRequestPublication.create(root, snapshot).publish(request, part);
                    T result =
                        work.execute(
                            state, database, epoch, request, begins, part, original, completion);
                    budget.requireWithin();
                    original.verify();
                    return result;
                  });
            }
          }
          java.util.Optional<BackupWorkerRequestFiles.ResumeProof> resumeProof =
              runId.isPresent()
                  ? java.util.Optional.of(database::requireAbandonedRequest)
                  : java.util.Optional.empty();
          var publisher = MorningBackupRequestPublication.create(root, snapshot, resumeProof);
          return MorningBackupPreparation.execute(
              state,
              database,
              Clock.systemUTC(),
              runId.isPresent(),
              publisher,
              part,
              (request, begins) -> {
                budget.requireWithin();
                original.verify();
                T result =
                    work.execute(
                        state,
                        database,
                        epoch,
                        request,
                        begins,
                        part,
                        original,
                        MorningProcessMain.archive(
                            () ->
                                new MorningBackupArtifacts(root, snapshot, budget)
                                    .complete(request, begins, part, database)));
                budget.requireWithin();
                original.verify();
                return result;
              });
        };
    if (runId.isPresent()) {
      return MorningControlScope.executeResumeVerifiedEpoch(
          budget, runId.orElseThrow(), continuation);
    }
    return MorningControlScope.executeVerifiedEpoch(budget, continuation);
  }

  static <T> T freshEpoch(MorningParentBudget budget, OwnedEpochWork<T> work) throws IOException {
    Objects.requireNonNull(budget, "existing parent budget");
    Objects.requireNonNull(work, "same-generation backup work");
    budget.requireWithin();
    var root = RootStartupContext.create();
    var snapshot = root.capture(RootStartupContext.Service.MORNING);
    return executeOwnedEpoch(
        MorningControlScope::executeOwnedEpoch,
        MorningBackupRequestPublication.create(root, snapshot),
        Clock.systemUTC(),
        false,
        UUID.randomUUID(),
        (state, database, epoch, request, begins, part) -> {
          budget.requireWithin();
          T result = work.execute(state, database, epoch, request, begins, part);
          budget.requireWithin();
          return result;
        });
  }

  static <T> T executeOwnedEpoch(
      EpochScope scope,
      MorningBackupPreparation.Publisher publisher,
      Clock clock,
      boolean recoverAbandoned,
      UUID part,
      OwnedEpochWork<T> work)
      throws IOException {
    Objects.requireNonNull(scope, "same-generation Morning scope");
    Objects.requireNonNull(publisher, "root request publication");
    Objects.requireNonNull(clock, "UTC backup clock");
    Objects.requireNonNull(part, "new request part");
    Objects.requireNonNull(work, "same-generation backup work");
    return Objects.requireNonNull(
        scope.execute(
            (state, database, epoch) -> {
              Objects.requireNonNull(epoch, "owned INVALID epoch");
              if (epoch.state() != StartupPermitRecords.State.INVALID
                  || !epoch.activation().equals(state.activation()))
                throw new IOException("Morning backup generation unavailable");
              return MorningBackupPreparation.execute(
                  state,
                  database,
                  clock,
                  recoverAbandoned,
                  publisher,
                  part,
                  (request, begins) -> work.execute(state, database, epoch, request, begins, part));
            }),
        "Morning backup stage result");
  }

  static <T> T fresh(MorningBackupPreparation.Continuation<T> work) throws IOException {
    Objects.requireNonNull(work, "fresh backup work");
    var root = RootStartupContext.create();
    var snapshot = root.capture(RootStartupContext.Service.MORNING);
    return execute(
        MorningControlScope::executeOwned,
        MorningBackupRequestPublication.create(root, snapshot),
        Clock.systemUTC(),
        false,
        UUID.randomUUID(),
        work);
  }

  static <T> T resume(UUID runId, MorningBackupPreparation.Continuation<T> work)
      throws IOException {
    Objects.requireNonNull(runId, "explicit resume run");
    Objects.requireNonNull(work, "resume backup work");
    var root = RootStartupContext.create();
    var snapshot = root.capture(RootStartupContext.Service.MORNING);
    Scope scope =
        new Scope() {
          @Override
          public <R> R execute(MorningNewRunAdmission.OwnedContinuation<R> continuation)
              throws IOException {
            return MorningControlScope.executeResumeOwned(runId, continuation);
          }
        };
    return execute(
        scope,
        MorningBackupRequestPublication.create(root, snapshot),
        Clock.systemUTC(),
        true,
        UUID.randomUUID(),
        work);
  }

  static <T> T execute(
      Scope scope,
      MorningBackupPreparation.Publisher publisher,
      Clock clock,
      boolean recoverAbandoned,
      UUID part,
      MorningBackupPreparation.Continuation<T> work)
      throws IOException {
    Objects.requireNonNull(scope, "owned Morning control scope");
    Objects.requireNonNull(publisher, "root request publication");
    Objects.requireNonNull(clock, "UTC backup clock");
    Objects.requireNonNull(part, "new request part");
    Objects.requireNonNull(work, "same-owner backup work");
    return executeOwned(
        scope,
        publisher,
        clock,
        recoverAbandoned,
        part,
        (state, database, request, begins, ownedPart) -> work.execute(request, begins));
  }

  /**
   * Borrow all same-run owners only inside the supplied M/A/DB/original callback. The caller must
   * separately prove the current original and request before any possible Backup marker retirement.
   */
  static <T> T executeOwned(
      Scope scope,
      MorningBackupPreparation.Publisher publisher,
      Clock clock,
      boolean recoverAbandoned,
      UUID part,
      OwnedWork<T> work)
      throws IOException {
    Objects.requireNonNull(scope, "owned Morning control scope");
    Objects.requireNonNull(publisher, "root request publication");
    Objects.requireNonNull(clock, "UTC backup clock");
    Objects.requireNonNull(part, "new request part");
    Objects.requireNonNull(work, "same-owner backup work");
    return Objects.requireNonNull(
        scope.execute(
            (state, database) ->
                MorningBackupPreparation.execute(
                    state,
                    database,
                    clock,
                    recoverAbandoned,
                    publisher,
                    part,
                    (request, begins) -> work.execute(state, database, request, begins, part))),
        "Morning backup stage result");
  }
}
