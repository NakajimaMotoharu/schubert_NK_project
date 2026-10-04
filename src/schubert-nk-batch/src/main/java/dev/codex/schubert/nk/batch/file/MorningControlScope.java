package dev.codex.schubert.nk.batch.file;

import dev.codex.schubert.nk.batch.file.StartupPermitRecords.Epoch;
import dev.codex.schubert.nk.batch.file.StartupPermitRecords.State;
import dev.codex.schubert.nk.batch.platform.MorningParentBudget;
import dev.codex.schubert.nk.batch.platform.MorningStopPass;
import dev.codex.schubert.nk.batch.platform.MorningUnitTerminals;
import dev.codex.schubert.nk.batch.platform.RootStartupContext;
import dev.codex.schubert.nk.batch.repository.MaintenanceRunState;
import dev.codex.schubert.nk.storage.LinuxFileLock;
import java.io.IOException;
import java.util.Objects;
import java.util.Optional;
import java.util.UUID;
import org.jspecify.annotations.NullMarked;

/**
 * Same-parent Morning M→dedicated DB/advisory→original→fixed-eight stop→A→fresh-eight boundary. The
 * supplied trusted work runs only after A's fresh observation and durable current INVALID and
 * retains callback-scoped DB backup/handoff capability inside M, A, DB and the original scope. This
 * does not prove clean Artemis journal, execute backup/Cleanup or issue a startup permit. An
 * unresolved stop-client must not return from MorningStopPass; handle-less UNKNOWN/hard-timeout
 * recovery remain unaccepted. NK-OPS-001; OPS009/UI251/253/SS341§3-7/343/SSC089/094/100-102/105;
 * PG341/343/344/346/378/PT-OPS-MCTRL001-018.
 */
@NullMarked
final class MorningControlScope {
  @FunctionalInterface
  interface Gate {
    void verify() throws IOException;
  }

  @FunctionalInterface
  interface Exclusive {
    <T> Optional<T> execute(LinuxFileLock.Operation<T> operation) throws IOException;
  }

  @FunctionalInterface
  interface StartupExclusive {
    <T> Optional<T> execute(LinuxFileLock.StartupOperation<T> operation) throws IOException;
  }

  @FunctionalInterface
  interface StopPass {
    void execute() throws IOException;
  }

  interface Original {
    <T> T execute(MorningNewRunAdmission.Continuation<T> continuation) throws IOException;
  }

  interface OwnedOriginal {
    <T> T execute(MorningNewRunAdmission.OwnedContinuation<T> continuation) throws IOException;
  }

  @FunctionalInterface
  interface Invalidation {
    void invalidate(MaintenanceRunState state) throws IOException;
  }

  @FunctionalInterface
  interface EpochInvalidation {
    Epoch invalidate(MaintenanceRunState state) throws IOException;
  }

  @FunctionalInterface
  interface OwnedEpochWork<T> {
    T execute(
        MaintenanceRunState state,
        dev.codex.schubert.nk.batch.repository.MorningDatabaseSession.Access database,
        Epoch epoch)
        throws IOException;
  }

  @FunctionalInterface
  interface VerifiedEpochWork<T> {
    T execute(
        MaintenanceRunState state,
        dev.codex.schubert.nk.batch.repository.MorningDatabaseSession.Access database,
        Epoch epoch,
        MorningNewRunAdmission.OriginalProof original,
        MorningUnitTerminals.Snapshot initialStop,
        MorningPermitPublication publication)
        throws IOException;
  }

  @FunctionalInterface
  interface Terminals {
    void requireAll() throws IOException;
  }

  @FunctionalInterface
  interface IntentClear {
    void requireClear() throws IOException;
  }

  private MorningControlScope() {}

  @FunctionalInterface
  private interface AfterPublication<T, R> {
    R execute(
        RootStartupContext root,
        RootStartupContext.Snapshot morning,
        MorningParentBudget budget,
        MaintenanceRunState state,
        dev.codex.schubert.nk.batch.repository.MorningDatabaseSession.Access database,
        MorningNewRunAdmission.OriginalProof original,
        Epoch issued,
        T result,
        java.util.function.Consumer<Gate> onOuterFailure)
        throws IOException;
  }

  static dev.codex.schubert.nk.batch.repository.MaintenanceCompletion executeCompletedEpoch(
      MorningParentBudget budget,
      Optional<UUID> runId,
      VerifiedEpochWork<MorningCompletionEvidence> trustedWork)
      throws IOException {
    return executeVerifiedEpoch(
        budget, runId, trustedWork, MorningStartupLaunchOwner::publishCompleted);
  }

  /** Actual original owner remains nested inside the SAME M/A/DB/current callback. */
  static <T> T executeVerifiedEpoch(MorningParentBudget budget, VerifiedEpochWork<T> trustedWork)
      throws IOException {
    return executeVerifiedEpoch(budget, java.util.Optional.empty(), trustedWork);
  }

  static <T> T executeResumeVerifiedEpoch(
      MorningParentBudget budget, UUID runId, VerifiedEpochWork<T> trustedWork) throws IOException {
    return executeVerifiedEpoch(budget, java.util.Optional.of(runId), trustedWork);
  }

  private static <T> T executeVerifiedEpoch(
      MorningParentBudget budget, java.util.Optional<UUID> runId, VerifiedEpochWork<T> trustedWork)
      throws IOException {
    return executeVerifiedEpoch(
        budget,
        runId,
        trustedWork,
        (root, morning, parent, state, database, original, issued, result, onOuterFailure) -> {
          MorningStartupLaunchOwner.publish(
              root, morning, parent, state, database, original, issued);
          return result;
        });
  }

  private static <T, R> R executeVerifiedEpoch(
      MorningParentBudget budget,
      java.util.Optional<UUID> runId,
      VerifiedEpochWork<T> trustedWork,
      AfterPublication<T, R> completion)
      throws IOException {
    Objects.requireNonNull(budget, "parent Morning budget");
    Objects.requireNonNull(trustedWork, "verified original work");
    Objects.requireNonNull(runId);
    Objects.requireNonNull(completion);
    budget.requireWithin();
    var root = RootStartupContext.create();
    var snapshot = root.capture(RootStartupContext.Service.MORNING);
    // BUG391: after original/DB scope closure, only abort may use this owner, never issue/DB/proof.
    var publicationOwner =
        new java.util.concurrent.atomic.AtomicReference<MorningPermitPublication>();
    var graphOwner = new java.util.concurrent.atomic.AtomicReference<Gate>();
    Gate gate =
        () ->
            protectGraph(
                graphOwner,
                publicationOwner,
                () -> {
                  budget.requireWithin();
                  root.recheck(snapshot);
                  return Boolean.TRUE;
                });
    var maintenance = MaintenanceFileLock.create();
    var startup = StartupAdmissionFile.create();
    var initialStop =
        new java.util.concurrent.atomic.AtomicReference<MorningUnitTerminals.Snapshot>();
    try {
      return executeStopAndStartup(
          gate,
          maintenance::tryExclusive,
          () ->
              protectGraph(
                  graphOwner,
                  publicationOwner,
                  () -> {
                    try (var intent = BackupStartIntentFiles.create(root, snapshot)) {
                      intent.requireClear();
                    }
                    try (var intent = BackupStartIntentFiles.createPublication(root, snapshot)) {
                      intent.requireClear();
                    }
                    requireNoExpiryRequest(root, snapshot);
                    MorningNewRunAdmission.VerifiedContinuation<R> continuation =
                        (state, database, original) -> {
                          var publication =
                              MorningPermitPublication.create(
                                  root, snapshot, budget, state, database, original);
                          publicationOwner.set(publication);
                          try {
                            T result =
                                afterOriginal(
                                    gate,
                                    () -> MorningStopPass.create(root, snapshot, budget).execute(),
                                    startup::tryExclusive,
                                    () ->
                                        initialStop.set(
                                            MorningUnitTerminals.capture(root, snapshot)),
                                    () -> {
                                      Epoch epoch =
                                          MorningCurrentInvalidation.invalidate(
                                              root, snapshot, state);
                                      if (epoch.state() != State.INVALID
                                          || !epoch.activation().equals(state.activation()))
                                        throw unavailable();
                                      publication.bind(epoch);
                                      original.verify();
                                      return trustedWork.execute(
                                          state,
                                          database,
                                          epoch,
                                          original,
                                          Objects.requireNonNull(
                                              initialStop.get(), "actual A-after-stop set"),
                                          publication);
                                    });
                            gate.verify();
                            original.verify();
                            database.recheckConsistent(state.activation().run());
                            publication.commit();
                            return completion.execute(
                                root,
                                snapshot,
                                budget,
                                state,
                                database,
                                original,
                                publication.expected(),
                                result,
                                graphOwner::set);
                          } catch (IOException | RuntimeException | Error failure) {
                            publication.abort();
                            throw failure;
                          }
                        };
                    if (runId.isPresent()) {
                      return MorningResumeAdmission.create(root, snapshot)
                          .executeVerified(runId.orElseThrow(), continuation);
                    }
                    return MorningNewRunAdmission.create(root, snapshot)
                        .executeVerified(continuation);
                  }));
    } catch (IOException | RuntimeException | Error outerFailure) {
      // Post-completion M close uncertainty is not normal exit, nor proof M is still held.
      if (graphOwner.get() != null) MorningStartupLaunchOwner.retain();
      throw outerFailure;
    }
  }

  /** Stop captured daemon graph before invalidation; callback uses no expired inner caps. */
  static <T> T protectGraph(
      java.util.concurrent.atomic.AtomicReference<Gate> graph,
      java.util.concurrent.atomic.AtomicReference<MorningPermitPublication> publication,
      LinuxFileLock.Operation<T> operation)
      throws IOException {
    Objects.requireNonNull(graph);
    return protectPublication(
        publication,
        () -> {
          try {
            return operation.execute();
          } catch (IOException | RuntimeException | Error failure) {
            var observer = graph.get();
            if (observer != null) observer.verify();
            throw failure;
          }
        });
  }

  /** BUG391: invoked under M; retained owner prevents this operation returning to M's close. */
  static <T> T protectPublication(
      java.util.concurrent.atomic.AtomicReference<MorningPermitPublication> owner,
      LinuxFileLock.Operation<T> operation)
      throws IOException {
    Objects.requireNonNull(owner);
    Objects.requireNonNull(operation);
    try {
      return operation.execute();
    } catch (IOException | RuntimeException | Error failure) {
      var publication = owner.get();
      if (publication != null) publication.abort();
      throw failure;
    }
  }

  static <T> T execute(MorningNewRunAdmission.Continuation<T> trustedWork) throws IOException {
    Objects.requireNonNull(trustedWork, "trusted Morning work");
    return executeOwned((state, ignored) -> trustedWork.execute(state));
  }

  static <T> T executeOwned(MorningNewRunAdmission.OwnedContinuation<T> trustedWork)
      throws IOException {
    Objects.requireNonNull(trustedWork, "owned trusted Morning work");
    var root = RootStartupContext.create();
    var snapshot = root.capture(RootStartupContext.Service.MORNING);
    return executeNativeOwned(
        root,
        snapshot,
        new OwnedOriginal() {
          @Override
          public <T> T execute(MorningNewRunAdmission.OwnedContinuation<T> continuation)
              throws IOException {
            // Fresh release/BOM admission and the dedicated DB owner are constructed only under M.
            return MorningNewRunAdmission.create(root, snapshot).executeOwned(continuation);
          }
        },
        trustedWork);
  }

  static <T> T executeOwnedEpoch(OwnedEpochWork<T> trustedWork) throws IOException {
    Objects.requireNonNull(trustedWork, "owned current-generation work");
    var root = RootStartupContext.create();
    var snapshot = root.capture(RootStartupContext.Service.MORNING);
    return executeNativeOwnedEpoch(
        root,
        snapshot,
        new OwnedOriginal() {
          @Override
          public <R> R execute(MorningNewRunAdmission.OwnedContinuation<R> continuation)
              throws IOException {
            return MorningNewRunAdmission.create(root, snapshot).executeOwned(continuation);
          }
        },
        trustedWork);
  }

  static <T> T executeResume(UUID runId, MorningNewRunAdmission.Continuation<T> trustedWork)
      throws IOException {
    Objects.requireNonNull(runId, "explicit resume run");
    Objects.requireNonNull(trustedWork, "trusted Morning work");
    return executeResumeOwned(runId, (state, ignored) -> trustedWork.execute(state));
  }

  static <T> T executeResumeOwned(
      UUID runId, MorningNewRunAdmission.OwnedContinuation<T> trustedWork) throws IOException {
    Objects.requireNonNull(runId, "explicit resume run");
    Objects.requireNonNull(trustedWork, "owned trusted Morning work");
    var root = RootStartupContext.create();
    var snapshot = root.capture(RootStartupContext.Service.MORNING);
    return executeNativeOwned(
        root,
        snapshot,
        new OwnedOriginal() {
          @Override
          public <T> T execute(MorningNewRunAdmission.OwnedContinuation<T> continuation)
              throws IOException {
            // No selection from DB or current permit: caller supplies exactly the original run ID.
            return MorningResumeAdmission.create(root, snapshot).executeOwned(runId, continuation);
          }
        },
        trustedWork);
  }

  static <T> T executeResumeOwnedEpoch(UUID runId, OwnedEpochWork<T> trustedWork)
      throws IOException {
    Objects.requireNonNull(runId, "explicit resume run");
    Objects.requireNonNull(trustedWork, "owned current-generation work");
    var root = RootStartupContext.create();
    var snapshot = root.capture(RootStartupContext.Service.MORNING);
    return executeNativeOwnedEpoch(
        root,
        snapshot,
        new OwnedOriginal() {
          @Override
          public <R> R execute(MorningNewRunAdmission.OwnedContinuation<R> continuation)
              throws IOException {
            return MorningResumeAdmission.create(root, snapshot).executeOwned(runId, continuation);
          }
        },
        trustedWork);
  }

  private static <T> T executeNativeOwned(
      RootStartupContext root,
      RootStartupContext.Snapshot snapshot,
      OwnedOriginal original,
      MorningNewRunAdmission.OwnedContinuation<T> trustedWork)
      throws IOException {
    return executeNativeOwnedEpoch(
        root,
        snapshot,
        original,
        (state, database, ignored) -> trustedWork.execute(state, database));
  }

  private static <T> T executeNativeOwnedEpoch(
      RootStartupContext root,
      RootStartupContext.Snapshot snapshot,
      OwnedOriginal original,
      OwnedEpochWork<T> trustedWork)
      throws IOException {
    var maintenance = MaintenanceFileLock.create();
    var startup = StartupAdmissionFile.create();
    return executeOwnedEpoch(
        () -> root.recheck(snapshot),
        maintenance::tryExclusive,
        withClearIntent(
            original,
            () -> {
              try (var intent = BackupStartIntentFiles.create(root, snapshot)) {
                intent.requireClear();
              }
              requireNoExpiryRequest(root, snapshot);
            }),
        () -> MorningStopPass.create(root, snapshot).execute(),
        startup::tryExclusive,
        () -> MorningUnitTerminals.requireQuiescent(root, snapshot),
        state -> MorningCurrentInvalidation.invalidate(root, snapshot, state),
        trustedWork);
  }

  static <T> T executeOwnedEpoch(
      Gate root,
      Exclusive maintenance,
      OwnedOriginal original,
      StopPass stop,
      StartupExclusive startup,
      Terminals terminals,
      EpochInvalidation invalidation,
      OwnedEpochWork<T> trustedWork)
      throws IOException {
    Objects.requireNonNull(original, "owned original");
    Objects.requireNonNull(stop, "fixed eight stop pass");
    Objects.requireNonNull(startup, "fixed A lock");
    Objects.requireNonNull(terminals, "fresh eight terminals");
    Objects.requireNonNull(invalidation, "durable current invalidation");
    Objects.requireNonNull(trustedWork, "owned current-generation work");
    return executeStopAndStartup(
        root,
        maintenance,
        () ->
            original.execute(
                (state, database) -> {
                  root.verify();
                  return afterOriginal(
                      root,
                      stop,
                      startup,
                      terminals,
                      () -> {
                        Epoch epoch =
                            Objects.requireNonNull(
                                invalidation.invalidate(state), "durable INVALID epoch");
                        // Epoch's constructor already makes INVALID imply an absent permit digest.
                        if (epoch.state() != State.INVALID
                            || !epoch.activation().equals(state.activation())) throw unavailable();
                        return trustedWork.execute(state, database, epoch);
                      });
                }));
  }

  @edu.umd.cs.findbugs.annotations.SuppressFBWarnings(
      value = "DMI_HARDCODED_ABSOLUTE_FILENAME",
      matchType = edu.umd.cs.findbugs.annotations.SuppressMatchType.EXACT,
      justification = "SS343/SSC111 fixed root-owned residue gate, before original/DB/stop under M")
  private static void requireNoExpiryRequest(
      RootStartupContext root, RootStartupContext.Snapshot expected) throws IOException {
    root.recheck(expected);
    try (var brokerIntent =
        BackupStartIntentFiles.create(
            root,
            expected,
            dev.codex.schubert.nk.batch.platform.BackupUnitStartClient.Target.BROKER)) {
      brokerIntent
          .requireClear(); // Under M, before old run/DB/stop: unknown daemon start stays isolated.
    }
    var startup =
        dev.codex.schubert.nk.storage.OwnedTransferDirectory.open(
            dev.codex.schubert.nk.storage.LinuxDirectoryCalls.create(),
            java.nio.file.Path.of("/run/schubert-nk/startup"));
    dev.codex.schubert.nk.storage.ResourceScope.use(
        startup::close,
        () -> {
          StartupLaunchFiles.requireNoServiceResidue(
              startup, dev.codex.schubert.nk.storage.LinuxInodeSecurity.create());
          return Boolean.TRUE;
        });
    var cleanup =
        dev.codex.schubert.nk.storage.OwnedTransferDirectory.open(
            dev.codex.schubert.nk.storage.LinuxDirectoryCalls.create(),
            java.nio.file.Path.of("/run/schubert-nk/cleanup-request"));
    dev.codex.schubert.nk.storage.ResourceScope.use(
        cleanup::close,
        () -> {
          new CleanupWorkerRequestFiles(
                  cleanup, dev.codex.schubert.nk.storage.LinuxInodeSecurity.create())
              .requireClear();
          return Boolean.TRUE;
        });
    root.recheck(expected);
    var directory =
        dev.codex.schubert.nk.storage.OwnedTransferDirectory.open(
            dev.codex.schubert.nk.storage.LinuxDirectoryCalls.create(),
            java.nio.file.Path.of("/run/schubert-nk/expiry-request"));
    dev.codex.schubert.nk.storage.ResourceScope.use(
        directory::close,
        () -> {
          CleanupWorkerRequestFiles.forExpiry(
                  directory, dev.codex.schubert.nk.storage.LinuxInodeSecurity.create())
              .requireClear();
          return Boolean.TRUE;
        });
    root.recheck(expected);
    var inspector =
        dev.codex.schubert.nk.storage.OwnedTransferDirectory.open(
            dev.codex.schubert.nk.storage.LinuxDirectoryCalls.create(),
            java.nio.file.Path.of("/run/schubert-nk/maintenance"));
    dev.codex.schubert.nk.storage.ResourceScope.use(
        inspector::close,
        () -> {
          new InspectorEnvironmentPublisher(
                  inspector, dev.codex.schubert.nk.storage.LinuxInodeSecurity.create())
              .requireFresh(); // Only Inspector env/UUID.part; sibling maintenance records are
          // retained.
          return Boolean.TRUE;
        });
    root.recheck(expected);
  }

  static OwnedOriginal withClearIntent(OwnedOriginal original, IntentClear intent) {
    Objects.requireNonNull(original, "dedicated DB/original owner");
    Objects.requireNonNull(intent, "same-boot start intent admission");
    return new OwnedOriginal() {
      @Override
      public <T> T execute(MorningNewRunAdmission.OwnedContinuation<T> continuation)
          throws IOException {
        // Called inside M: no DB/original mutation, fixed stop or new request precedes this gate.
        intent.requireClear();
        return original.execute(continuation);
      }
    };
  }

  static <T> T executeOwned(
      Gate root,
      Exclusive maintenance,
      OwnedOriginal original,
      StopPass stop,
      StartupExclusive startup,
      Terminals terminals,
      Invalidation invalidation,
      MorningNewRunAdmission.OwnedContinuation<T> trustedWork)
      throws IOException {
    Objects.requireNonNull(original, "owned original");
    Objects.requireNonNull(stop, "fixed eight stop pass");
    Objects.requireNonNull(startup, "fixed A lock");
    Objects.requireNonNull(terminals, "fresh eight terminals");
    Objects.requireNonNull(invalidation, "durable current invalidation");
    Objects.requireNonNull(trustedWork, "owned trusted work");
    return executeStopAndStartup(
        root,
        maintenance,
        () ->
            original.execute(
                (state, database) -> {
                  root.verify();
                  return afterOriginal(
                      root,
                      stop,
                      startup,
                      terminals,
                      () -> {
                        invalidation.invalidate(state);
                        return trustedWork.execute(state, database);
                      });
                }));
  }

  static <T> T execute(
      Gate root,
      Exclusive maintenance,
      Original original,
      StopPass stop,
      StartupExclusive startup,
      Terminals terminals,
      Invalidation invalidation,
      MorningNewRunAdmission.Continuation<T> trustedWork)
      throws IOException {
    Objects.requireNonNull(invalidation, "durable current invalidation");
    Objects.requireNonNull(trustedWork, "same-run Morning work");
    return executeOriginal(
        root,
        maintenance,
        original,
        stop,
        startup,
        terminals,
        state -> {
          invalidation.invalidate(state);
          return trustedWork.execute(state);
        });
  }

  static <T> T execute(
      Gate root,
      Exclusive maintenance,
      Original original,
      StopPass stop,
      StartupExclusive startup,
      Terminals terminals,
      MorningNewRunAdmission.Continuation<T> trustedWork)
      throws IOException {
    // Isolated PG343 PT port. The native Production factory uses the invalidating overload.
    return executeOriginal(root, maintenance, original, stop, startup, terminals, trustedWork);
  }

  private static <T> T executeOriginal(
      Gate root,
      Exclusive maintenance,
      Original original,
      StopPass stop,
      StartupExclusive startup,
      Terminals terminals,
      MorningNewRunAdmission.Continuation<T> trustedWork)
      throws IOException {
    Objects.requireNonNull(original, "dedicated DB and durable original");
    Objects.requireNonNull(stop, "fixed eight stop pass");
    Objects.requireNonNull(startup, "fixed A lock");
    Objects.requireNonNull(terminals, "fresh eight terminals");
    Objects.requireNonNull(trustedWork, "same-run Morning work");
    return executeStopAndStartup(
        root,
        maintenance,
        () ->
            original.execute(
                state -> {
                  root.verify();
                  return afterOriginal(
                      root, stop, startup, terminals, () -> trustedWork.execute(state));
                }));
  }

  static <T> T execute(
      Gate root,
      Exclusive maintenance,
      StopPass stop,
      StartupExclusive startup,
      Terminals terminals,
      LinuxFileLock.Operation<T> trustedWork)
      throws IOException {
    // Isolated PT port for the PG341 stop/A boundary. The native factory above always uses the
    // original-owning overload; this overload alone is never a Production Morning entry.
    Objects.requireNonNull(stop, "fixed eight stop pass");
    Objects.requireNonNull(startup, "fixed A lock");
    Objects.requireNonNull(terminals, "fresh eight terminals");
    Objects.requireNonNull(trustedWork, "trusted Morning work");
    return executeStopAndStartup(
        root, maintenance, () -> afterOriginal(root, stop, startup, terminals, trustedWork));
  }

  private static <T> T executeStopAndStartup(
      Gate root, Exclusive maintenance, LinuxFileLock.Operation<T> afterMaintenance)
      throws IOException {
    Objects.requireNonNull(root, "Morning root gate");
    Objects.requireNonNull(maintenance, "fixed M lock");
    Objects.requireNonNull(afterMaintenance, "owned Morning work");
    root.verify();
    Optional<T> completed =
        maintenance.execute(
            () -> {
              root.verify();
              T result =
                  Objects.requireNonNull(afterMaintenance.execute(), "Morning M work result");
              root.verify();
              return result;
            });
    if (completed.isEmpty()) throw unavailable();
    root.verify();
    return completed.orElseThrow();
  }

  private static <T> T afterOriginal(
      Gate root,
      StopPass stop,
      StartupExclusive startup,
      Terminals terminals,
      LinuxFileLock.Operation<T> trustedWork)
      throws IOException {
    stop.execute();
    root.verify();
    Optional<T> afterStartup =
        startup.execute(
            borrowedDescriptor -> {
              // A's reserved descriptor stays owned by StartupAdmissionFile. It is never exported
              // to the work or used as a substitute for Unit proof.
              root.verify();
              terminals.requireAll();
              root.verify();
              T result = Objects.requireNonNull(trustedWork.execute(), "Morning work result");
              root.verify();
              return result;
            });
    if (afterStartup.isEmpty()) throw unavailable();
    return afterStartup.orElseThrow();
  }

  private static IOException unavailable() {
    return new IOException("Morning control scope unavailable");
  }
}
