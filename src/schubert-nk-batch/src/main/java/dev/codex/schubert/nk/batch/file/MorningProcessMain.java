package dev.codex.schubert.nk.batch.file;

import dev.codex.schubert.nk.batch.platform.BackupUnitTermination;
import dev.codex.schubert.nk.batch.platform.MorningBackupUnitCycle;
import dev.codex.schubert.nk.batch.platform.MorningParentBudget;
import dev.codex.schubert.nk.batch.platform.RootStartupContext;
import dev.codex.schubert.nk.batch.platform.StopGateException;
import dev.codex.schubert.nk.storage.LinuxDirectoryCalls;
import dev.codex.schubert.nk.storage.LinuxInodeSecurity;
import dev.codex.schubert.nk.storage.OwnedTransferDirectory;
import dev.codex.schubert.nk.storage.ResourceScope;
import dev.codex.schubert.nk.storage.StorageIoException;
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
 * retired only after full termination and original/current proof. Typed native completion follows
 * actual cleanup/issuer, both ordinary services, Caddy and same held original DONE; only all outer
 * scopes' normal closure may return0/10. Legacy partial admissions still exit30. UNKNOWN retains
 * the outer oneshot budget; no unexecuted phase is invented as FAILED. No raw diagnostic is
 * printed. NK-OPS-001; OPS009/UI251/SS341/343/SSC100-102; PG339; PT-OPS-MMAIN001-007.
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

  private final CompletedAdmission nativeAdmission;
  private final java.util.function.IntConsumer termination;

  /** SSC299: the standard Java25 launcher always binds the native operation and OS exit. */
  public MorningProcessMain() {
    this(MorningProcessMain::executeCompletedBackup, System::exit);
  }

  /** Data/control-flow test ports only, never a configurable startup capability. */
  MorningProcessMain(
      CompletedAdmission nativeAdmission, java.util.function.IntConsumer termination) {
    this.nativeAdmission = Objects.requireNonNull(nativeAdmission, "native Morning operation");
    this.termination = Objects.requireNonNull(termination, "OS exit request");
  }

  @FunctionalInterface
  interface CompletedAdmission {
    dev.codex.schubert.nk.batch.repository.MaintenanceCompletion execute(
        MorningParentBudget budget, Optional<UUID> runId) throws IOException;
  }

  public void main(String[] args) {
    termination.accept(runCompleted(args, nativeAdmission));
  }

  private static dev.codex.schubert.nk.batch.repository.MaintenanceCompletion
      executeCompletedBackup(MorningParentBudget entryBudget, Optional<UUID> runId)
          throws IOException {
    var entryRoot = RootStartupContext.create();
    var entrySnapshot = entryRoot.capture(RootStartupContext.Service.MORNING);
    var budget =
        MorningParentBudget.borrow(
            entryRoot.maintenanceDeadline(entrySnapshot, entryBudget.deadlineNanos()));
    MorningBackupStage.VerifiedEpochWork<MorningCompletionEvidence> work =
        (state,
            database,
            epoch,
            request,
            begins,
            part,
            original,
            completion,
            initialStop,
            publication) -> {
          var root = RootStartupContext.create();
          var snapshot = root.capture(RootStartupContext.Service.MORNING);
          return ResourceScope.acquire(
              MorningProcessMain::openRequests,
              OwnedTransferDirectory::close,
              requests -> {
                var files = new BackupWorkerRequestFiles(requests, LinuxInodeSecurity.create());
                EnvironmentInodePolicy.require(files.read().equals(request));
                var terminal = BackupUnitTermination.create(root, snapshot);
                var backupCycle = MorningBackupUnitCycle.create(root, snapshot, budget);
                var configCompletion =
                    new java.util.concurrent.atomic.AtomicReference<MorningBackupCompletion>();
                var backupOutcome =
                    backupCycle.executeObserved(
                        () -> {
                          budget.requireWithin();
                          root.recheck(snapshot);
                          original.verify();
                          database.recheckConsistent(state.activation().run());
                          ResourceScope.acquire(
                              MorningProcessMain::openCurrent,
                              OwnedTransferDirectory::close,
                              startup -> {
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
                        (outcome, actualReceipt) -> {
                          budget.requireWithin();
                          root.recheck(snapshot);
                          original.verify();
                          if (request.verification().isPresent()
                              && outcome != MorningBackupUnitCycle.Outcome.SUCCESS)
                            throw new IOException("Prior backup verification unavailable");
                          EnvironmentInodePolicy.require(files.read().equals(request));
                          configCompletion.set(
                              MorningBackupCompletion.complete(
                                  outcome,
                                  actualReceipt,
                                  begins,
                                  database,
                                  java.time.Clock.systemUTC(),
                                  completion,
                                  snapshot.invocation(),
                                  () -> {
                                    budget.requireWithin();
                                    root.recheck(snapshot);
                                    original.verify();
                                    return budget.remainingNanos();
                                  }));
                          budget.requireWithin();
                          root.recheck(snapshot);
                          original.verify();
                        });
                var retentionMode =
                    backupOutcome == MorningBackupUnitCycle.Outcome.FAILED
                        ? MorningBackupRetention.Mode.FAILED
                        : begins.database().skipped()
                            ? MorningBackupRetention.Mode.REUSED_SUCCESS
                            : MorningBackupRetention.Mode.NEW_SUCCESS;
                var backupCompleted =
                    Objects.requireNonNull(
                        configCompletion.get(), "actual parent CONFIG completion");
                return MorningBackupRetention.use(
                    retentionMode,
                    backupOutcome == MorningBackupUnitCycle.Outcome.SUCCESS
                        ? Optional.of(completion.verifiedManifest())
                        : Optional.empty(),
                    database,
                    () -> {
                      budget.requireWithin();
                      root.recheck(snapshot);
                      original.verify();
                      return budget.remainingNanos();
                    },
                    retention -> {
                      MorningCleanupExecution.Completion cleanup;
                      if (backupOutcome == MorningBackupUnitCycle.Outcome.SUCCESS) {
                        cleanup =
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
                        cleanup =
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
                      } else throw new IOException("Actual Backup completion unavailable");
                      database.recheckConsistent(state.activation().run());
                      var previousBroker =
                          dev.codex.schubert.nk.batch.platform.MorningPreviousBroker.capture(
                              root, snapshot, budget, initialStop, original::verify);
                      database.recheckConsistent(state.activation().run());
                      var broker =
                          MorningBrokerExecution.execute(
                              root,
                              snapshot,
                              budget,
                              state,
                              database,
                              epoch,
                              original,
                              publication::expected,
                              previousBroker);
                      var expiry =
                          MorningExpiryExecution.execute(
                              root,
                              snapshot,
                              budget,
                              state,
                              database,
                              epoch,
                              original,
                              broker.live());
                      database.recheckConsistent(state.activation().run());
                      database.recheckExpiry(
                          expiry,
                          () -> {
                            budget.requireWithin();
                            root.recheck(snapshot);
                            original.verify();
                            broker.recheck();
                            return budget.remainingNanos();
                          });
                      database.recheckConsistent(state.activation().run());
                      var references =
                          database.cleanupReferences(
                              cleanup.terminal(),
                              () -> {
                                budget.requireWithin();
                                root.recheck(snapshot);
                                original.verify();
                                broker.recheck();
                                return budget.remainingNanos();
                              },
                              original::referenceRun);
                      EnvironmentInodePolicy.require(cleanup.references().equals(references));
                      database.recheckConsistent(state.activation().run());
                      budget.requireWithin();
                      original.verify();
                      var release =
                          dev.codex.schubert.nk.batch.platform.RootReleaseAdmission.create(
                              root, snapshot);
                      var configurations = release.inspectConfigurations();
                      var startupRoots =
                          MorningStartupRoots.create(root, snapshot, configurations.roots());
                      var actualRoots = startupRoots.capture();
                      budget.requireWithin();
                      original.verify();
                      release.recheckConfigurations(configurations);
                      startupRoots.recheck(actualRoots);
                      budget.requireWithin();
                      original.verify();
                      broker.recheck();
                      // SSC129: derive both gate frames from the owned live DB/BOM read, not
                      // constants or a second connection. Frames alone grant no startup authority.
                      dev.codex.schubert.nk.bootstrap.MaintenanceOwnerFrame.Guard issuerOwner =
                          () -> {
                            budget.requireWithin();
                            root.recheck(snapshot);
                            original.verify();
                            broker.recheck();
                            return budget.remainingNanos();
                          };
                      var actualDatabase = database.inspectPermitDatabase(issuerOwner);
                      var actualBroker = broker.observe();
                      var brokerFrame =
                          MorningGateEvidence.broker(
                              epoch,
                              snapshot.invocation(),
                              broker.invocation(),
                              actualBroker.values(),
                              actualBroker.journal());
                      var postgresFrame =
                          MorningGateEvidence.postgres(
                              epoch, snapshot.invocation(), broker.invocation(), actualDatabase);
                      var releaseFrame =
                          MorningGateEvidence.release(
                              epoch,
                              snapshot.invocation(),
                              broker.invocation(),
                              actualDatabase.release(),
                              configurations.apiSha256(),
                              configurations.webSha256());
                      previousBroker.recheck(broker.live());
                      var stopFrame =
                          MorningGateEvidence.stop(
                              epoch,
                              snapshot.invocation(),
                              broker.invocation(),
                              initialStop,
                              previousBroker);
                      retention.recheck();
                      backupCompleted.recheck();
                      var retentionFrame =
                          MorningGateEvidence.retention(
                              epoch,
                              snapshot.invocation(),
                              broker.invocation(),
                              retention.result());
                      var prestartFrame =
                          MorningPrestartEvidence.encode(
                              epoch,
                              broker.invocation(),
                              backupCompleted,
                              cleanup,
                              expiry,
                              retention.result().currentSha256,
                              java.util.Map.of(
                                  "POSTGRES",
                                  postgresFrame,
                                  "RELEASE_BOM",
                                  releaseFrame,
                                  "STOP_SET",
                                  stopFrame,
                                  "BROKER_OPS",
                                  brokerFrame,
                                  "BACKUP_RETENTION",
                                  retentionFrame));
                      release.recheckConfigurations(configurations);
                      startupRoots.recheck(actualRoots);
                      database.recheckPermitDatabase(actualDatabase, issuerOwner);
                      var permit =
                          new StartupPermitRecords.Permit(
                              epoch.boot(),
                              epoch.epoch(),
                              epoch.activation(),
                              broker.invocation(),
                              actualDatabase.release().contents().sha256(),
                              configurations.apiSha256(),
                              configurations.webSha256(),
                              actualRoots.sha256(epoch),
                              prestartDigest(prestartFrame));
                      StartupPermitFiles.IssueProof actualProof =
                          (phase, expectedCurrent) -> {
                            budget.requireWithin();
                            root.recheck(snapshot);
                            original.verify();
                            EnvironmentInodePolicy.require(
                                publication.expected().equals(expectedCurrent));
                            release.recheckConfigurations(configurations);
                            startupRoots.recheck(actualRoots);
                            database.recheckPermitDatabase(actualDatabase, issuerOwner);
                            backupCompleted.recheck();
                            backupCycle.recheckCompletedBackup();
                            cleanup.receipt().requireStillPresent();
                            expiry.receipt().requireStillPresent();
                            EnvironmentInodePolicy.require(
                                cleanup
                                    .references()
                                    .equals(
                                        database.cleanupReferences(
                                            cleanup.terminal(),
                                            issuerOwner,
                                            original::referenceRun)));
                            database.recheckExpiry(expiry, issuerOwner);
                            retention.recheck();
                            previousBroker.recheck(broker.live());
                            broker
                                .observe(); // mutable pressure/log size is independently validated,
                            // not frozen
                            EnvironmentInodePolicy.require(
                                broker.invocation().equals(permit.brokerInvocation()));
                            for (var unit :
                                java.util.List.of(
                                    dev.codex.schubert.nk.batch.platform.MaintenanceUnit.CADDY,
                                    dev.codex.schubert.nk.batch.platform.MaintenanceUnit.WEB,
                                    dev.codex.schubert.nk.batch.platform.MaintenanceUnit.API,
                                    dev.codex.schubert.nk.batch.platform.MaintenanceUnit.INSPECTOR))
                              EnvironmentInodePolicy.require(
                                  dev.codex.schubert.nk.batch.platform.MaintenanceUnitTermination
                                      .create(root, snapshot, unit)
                                      .quiescent()
                                      .isPresent());
                            budget.requireWithin();
                            root.recheck(snapshot);
                            original.verify();
                          };
                      var issued = publication.issue(permit, actualProof);
                      actualProof.verify(StartupPermitFiles.IssuePhase.AFTER_READBACK, issued);
                      return new MorningCompletionEvidence(
                          backupOutcome,
                          begins,
                          backupOutcome == MorningBackupUnitCycle.Outcome.SUCCESS
                              ? Optional.of(completion.verifiedManifest())
                              : Optional.empty(),
                          backupCompleted.rows(),
                          backupCompleted.receipt(),
                          backupCycle,
                          cleanup,
                          expiry);
                    });
              });
        };
    var completed = MorningBackupStage.completedEpoch(budget, runId, work);
    budget.requireWithin();
    entryRoot.recheck(entrySnapshot);
    return completed;
  }

  /** SSC108/136, BUG393: the permit binds SHA-256 of the complete canonical frame, not its text. */
  static String prestartDigest(String frame) throws IOException {
    return prestartDigest(frame, () -> java.security.MessageDigest.getInstance("SHA-256"));
  }

  static String prestartDigest(String frame, StartupPermitRecords.DigestFactory factory)
      throws IOException {
    var bytes = Objects.requireNonNull(frame).getBytes(java.nio.charset.StandardCharsets.US_ASCII);
    Objects.requireNonNull(factory);
    try {
      return java.util.HexFormat.of().formatHex(factory.create().digest(bytes));
    } catch (java.security.NoSuchAlgorithmException failure) {
      StorageIoException.preserveFatal(failure);
      throw new IOException("prestart digest unavailable");
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
    Objects.requireNonNull(admission, "fixed Morning admission");
    Objects.requireNonNull(resume, "fixed Morning resume admission");
    return runCompleted(
        args,
        (budget, selected) -> {
          if (selected.isPresent()) resume.verify(budget, selected.orElseThrow());
          else admission.verify(budget);
          throw new IOException("Morning partial admission incomplete");
        });
  }

  /** Native typed result arrives only after all original/DB/credential/M owners closed normally. */
  static int runCompleted(String[] args, CompletedAdmission admission) {
    Objects.requireNonNull(args, "Morning arguments");
    Objects.requireNonNull(admission, "completed Morning admission");
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
      var completed =
          Objects.requireNonNull(admission.execute(budget, selected), "actual completion");
      budget.requireWithin();
      return completed.outcome().exitCode();
    } catch (IOException
        | StopGateException
        | dev.codex.schubert.nk.batch.cleanup.CleanupStoppedException known) {
      if (!(known instanceof IOException)) StorageIoException.preserveFatal(known);
      return 30;
    }
  }
}
