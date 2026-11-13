package dev.codex.schubert.nk.batch.file;

import static dev.codex.schubert.nk.batch.file.EnvironmentInodePolicy.require;

import dev.codex.schubert.nk.batch.platform.BackupUnitStartClient;
import dev.codex.schubert.nk.batch.platform.MaintenanceUnit;
import dev.codex.schubert.nk.batch.platform.MaintenanceUnitStopClient;
import dev.codex.schubert.nk.batch.platform.MaintenanceUnitTermination;
import dev.codex.schubert.nk.batch.platform.MorningCaddyReadiness;
import dev.codex.schubert.nk.batch.platform.MorningParentBudget;
import dev.codex.schubert.nk.batch.platform.MorningServiceReadiness;
import dev.codex.schubert.nk.batch.platform.RootStartupContext;
import dev.codex.schubert.nk.batch.repository.MaintenanceCompletion;
import dev.codex.schubert.nk.batch.repository.MaintenanceRunState;
import dev.codex.schubert.nk.batch.repository.MorningDatabaseSession;
import dev.codex.schubert.nk.bootstrap.FixedServiceIdentity;
import dev.codex.schubert.nk.bootstrap.MaintenanceOwnerFrame;
import dev.codex.schubert.nk.bootstrap.StartupReleaseManifest;
import dev.codex.schubert.nk.storage.LinuxDirectoryCalls;
import dev.codex.schubert.nk.storage.LinuxInodeSecurity;
import dev.codex.schubert.nk.storage.OwnedTransferDirectory;
import dev.codex.schubert.nk.storage.ResourceScope;
import dev.codex.schubert.nk.storage.ServiceConfigFiles;
import edu.umd.cs.findbugs.annotations.SuppressFBWarnings;
import edu.umd.cs.findbugs.annotations.SuppressMatchType;
import java.io.IOException;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import java.util.Objects;
import java.util.Optional;
import java.util.UUID;
import org.jspecify.annotations.NullMarked;

/** Normal A-after publication only, still the same M/DB/original owner. SSC137/PT297. */
@NullMarked
final class MorningStartupLaunchOwner {
  private MorningStartupLaunchOwner() {}

  @SuppressFBWarnings(
      value = "DMI_HARDCODED_ABSOLUTE_FILENAME",
      matchType = SuppressMatchType.EXACT,
      justification = "SS343/SSC137 fixed startup root; no caller path or arbitrary file")
  private static void prepare(
      RootStartupContext root,
      RootStartupContext.Snapshot morning,
      MorningParentBudget budget,
      MaintenanceRunState state,
      MorningDatabaseSession.Access database,
      MorningNewRunAdmission.OriginalProof original,
      StartupPermitRecords.Epoch issued)
      throws IOException {
    Objects.requireNonNull(root);
    Objects.requireNonNull(morning);
    Objects.requireNonNull(budget);
    Objects.requireNonNull(state);
    Objects.requireNonNull(database);
    Objects.requireNonNull(original);
    Objects.requireNonNull(issued);
    require(
        morning.service() == RootStartupContext.Service.MORNING
            && issued.state() == StartupPermitRecords.State.ISSUED
            && issued.activation().equals(state.activation()));
    budget.requireWithin();
    root.recheck(morning);
    original.verify();
    database.recheckConsistent(state.activation().run());
    var owner =
        new MaintenanceOwnerFrame(
            issued.boot(),
            state.activation().run().id(),
            state.activation().id(),
            state.activation().run().cutoff(),
            issued.epoch(),
            new MaintenanceOwnerFrame.Parent(
                morning.invocation(), morning.pid(), morning.startTicks()),
            Optional.empty(),
            budget.deadlineNanos());
    var calls = LinuxDirectoryCalls.create();
    Path startupPath = Path.of("/run/schubert-nk/startup");
    ResourceScope.acquire(
        () -> OwnedTransferDirectory.open(calls, startupPath),
        OwnedTransferDirectory::close,
        directory -> {
          var permits = new StartupPermitFiles(directory, LinuxInodeSecurity.create());
          require(issued.equals(permits.current()));
          permits.readIssued();
          var files = new StartupLaunchFiles(directory, LinuxInodeSecurity.create(), issued);
          files.prepareOwner(owner, UUID.randomUUID());
          require(owner.equals(files.readOwner()) && issued.equals(permits.current()));
          permits.readIssued();
          return Boolean.TRUE;
        });
    // Every namespace/entry owner is closed before this normal return; failure stays under M.
    budget.requireWithin();
    root.recheck(morning);
    original.verify();
    database.recheckConsistent(state.activation().run());
  }

  static void publish(
      RootStartupContext root,
      RootStartupContext.Snapshot morning,
      MorningParentBudget budget,
      MaintenanceRunState state,
      MorningDatabaseSession.Access database,
      MorningNewRunAdmission.OriginalProof original,
      StartupPermitRecords.Epoch issued)
      throws IOException {
    prepare(root, morning, budget, state, database, original, issued);
    startPending(root, morning, budget, state, database, original, issued);
  }

  private record Started(
      MaintenanceUnit unit,
      MaintenanceUnitTermination termination,
      BackupUnitStartClient.Attempt attempt,
      MorningServiceReadiness readiness,
      ServiceConfigFiles.Service service,
      RootStartupContext.Snapshot captured) {}

  /** SSC237/PT-OPS-COMPLETION790001..004: literal phases, never provider data or authority. */
  enum CompletionPhase {
    CADDY_BEFORE,
    CADDY_AFTER,
    WEB_BEFORE,
    WEB_AFTER,
    API_HELD,
    API_BEFORE,
    API_AFTER,
    ALL_RETIRED,
    DONE_BEFORE,
    DONE_AFTER
  }

  static final class CompletionProgress {
    private final java.util.function.LongSupplier clock;
    private final java.util.function.Consumer<String> sink;
    private final long started;
    private CompletionPhase retainedPhase = CompletionPhase.CADDY_BEFORE;

    CompletionProgress(
        java.util.function.LongSupplier clock, java.util.function.Consumer<String> sink) {
      this.clock = Objects.requireNonNull(clock);
      this.sink = Objects.requireNonNull(sink);
      started = clock.getAsLong();
    }

    void phase(CompletionPhase next) {
      retainedPhase = Objects.requireNonNull(next);
      emit("VERIFY");
    }

    void failure(Throwable failure) {
      Objects.requireNonNull(failure);
      try {
        emit(
            failure instanceof IOException ? "IO" : failure instanceof Error ? "FATAL" : "RUNTIME");
      } catch (RuntimeException | Error diagnosticFailure) {
        // SSC326: best-effort diagnosis must return to the original owner's UNKNOWN retention.
      }
    }

    private void emit(String classification) {
      sink.accept(
          "event=morning.completion phase="
              + retainedPhase
              + " classification="
              + classification
              + " elapsedNanos="
              + (clock.getAsLong() - started));
    }
  }

  @FunctionalInterface
  interface CompletionRetirement {
    void retire(
        BackupUnitStartClient.RetirementGate before, BackupUnitStartClient.RetirementGate after)
        throws IOException;
  }

  @FunctionalInterface
  interface ApiRetained {
    void require(BackupUnitStartClient.RetirementGate gate) throws IOException;
  }

  static void retireCompleted(
      CompletionRetirement caddy,
      CompletionRetirement web,
      CompletionRetirement api,
      ApiRetained apiRetained,
      BackupUnitStartClient.RetirementGate pending,
      BackupUnitStartClient.RetirementGate retired,
      CompletionProgress progress)
      throws IOException {
    Objects.requireNonNull(caddy);
    Objects.requireNonNull(web);
    Objects.requireNonNull(api);
    Objects.requireNonNull(apiRetained);
    Objects.requireNonNull(pending);
    Objects.requireNonNull(retired);
    Objects.requireNonNull(progress);
    caddy.retire(
        completionGate(CompletionPhase.CADDY_BEFORE, pending, progress),
        completionGate(CompletionPhase.CADDY_AFTER, pending, progress));
    web.retire(
        completionGate(CompletionPhase.WEB_BEFORE, pending, progress),
        () -> {
          completionGate(CompletionPhase.WEB_AFTER, retired, progress).verify();
          apiRetained.require(completionGate(CompletionPhase.API_HELD, retired, progress));
        });
    api.retire(
        completionGate(CompletionPhase.API_BEFORE, retired, progress),
        completionGate(CompletionPhase.API_AFTER, retired, progress));
    completionGate(CompletionPhase.ALL_RETIRED, retired, progress).verify();
  }

  private static BackupUnitStartClient.RetirementGate completionGate(
      CompletionPhase phase,
      BackupUnitStartClient.RetirementGate proof,
      CompletionProgress progress) {
    return () -> {
      progress.phase(phase);
      proof.verify();
    };
  }

  /** Typed native completion only; callback stays under the same original/DB/M scopes. */
  static MaintenanceCompletion publishCompleted(
      RootStartupContext root,
      RootStartupContext.Snapshot morning,
      MorningParentBudget budget,
      MaintenanceRunState state,
      MorningDatabaseSession.Access database,
      MorningNewRunAdmission.OriginalProof original,
      StartupPermitRecords.Epoch issued,
      MorningCompletionEvidence evidence,
      java.util.function.Consumer<MorningControlScope.Gate> onOuterFailure)
      throws IOException {
    Objects.requireNonNull(evidence);
    Objects.requireNonNull(onOuterFailure);
    prepare(root, morning, budget, state, database, original, issued);
    var completed = new java.util.concurrent.atomic.AtomicReference<MaintenanceCompletion>();
    MorningStartupLaunchOwner.<Started>sequence(
        (service, earlier) ->
            startService(
                root, morning, budget, state, database, original, issued, service, earlier),
        started -> stopStarted(root, morning, budget, state, database, original, started),
        started -> {
          var caddy = MaintenanceUnitTermination.create(root, morning, MaintenanceUnit.CADDY);
          require(caddy.quiescentObservation().isPresent());
          BackupUnitStartClient.RetirementGate livePeer =
              () -> {
                budget.requireWithin();
                root.recheck(morning);
                original.verify();
                for (var service : started) {
                  verifyCurrentLaunch(root, morning, issued, service.service(), service.captured());
                  require(service.readiness().ready());
                }
                root.recheck(morning);
              };
          var liveChecks =
              new MorningCompletionChecks(
                  livePeer, () -> database.recheckConsistent(state.activation().run()));
          BackupUnitStartClient.RetirementGate live = liveChecks::verify;
          live.verify();
          BackupUnitStartClient.RetirementGate owner =
              () -> {
                budget.requireWithin();
                root.recheck(morning);
                original.verify();
                root.recheck(morning);
                budget.requireWithin();
              };
          String previousCaddy = MorningCaddyReadiness.coldInvocation(root, morning);
          // Fix once at the SAME preflight point, in the parent's Linux clock domain.
          long caddyRemainingFloor = caddyRemainingFloor(budget.remainingNanos());
          var attempt =
              BackupUnitStartClient.createCaddy(
                      root,
                      morning,
                      budget,
                      started.get(0).attempt(),
                      started.get(1).attempt(),
                      live,
                      owner,
                      previousCaddy)
                  .start();
          if (attempt.status() != BackupUnitStartClient.Status.CLIENT_EXITED_ZERO) retain();
          MorningCaddyReadiness proxy;
          try {
            while (true) {
              live.verify();
              require(budget.remainingNanos() > caddyRemainingFloor);
              try {
                proxy = MorningCaddyReadiness.create(root, morning, budget, previousCaddy);
                if (proxy.ready()) {
                  require(budget.remainingNanos() > caddyRemainingFloor);
                  break;
                }
              } catch (IOException notYetReady) {
                // Do not accept uncertainty; bounded failure stops the whole owned graph.
              }
              pause();
            }
          } catch (IOException | RuntimeException | Error failure) {
            stopOnly(root, morning, budget, MaintenanceUnit.CADDY, caddy);
            try {
              attempt.preserveObservation();
            } catch (IOException | RuntimeException | Error unknownClose) {
              retain();
            }
            throw failure;
          }
          var confirmedProxy = proxy;
          var pendingChecks =
              new MorningCompletionChecks(
                  () -> {
                    livePeer.verify();
                    require(confirmedProxy.ready());
                  },
                  () -> database.recheckConsistent(state.activation().run()));
          BackupUnitStartClient.RetirementGate retainedOwner =
              () -> {
                budget.requireWithin();
                root.recheck(morning);
                original.verifyRetained();
                root.recheck(morning);
                budget.requireWithin();
              };
          BackupUnitStartClient.RetirementGate pending =
              () -> {
                pendingChecks.verify();
                evidence.verify(
                    database,
                    java.time.Clock.systemUTC(),
                    pendingChecks.ownerGuard(budget::remainingNanos, retainedOwner),
                    original::referenceRun,
                    pendingChecks::verify);
                pendingChecks.verify();
              };
          BackupUnitStartClient.RetirementGate retiredPeer =
              () -> {
                budget.requireWithin();
                root.recheck(morning);
                original.verify();
                for (var service : started) {
                  verifyCurrentLaunch(
                      root, morning, issued, service.service(), service.captured(), false);
                  require(service.readiness().ready());
                }
                require(confirmedProxy.ready());
                root.recheck(morning);
              };
          var retiredChecks =
              new MorningCompletionChecks(
                  retiredPeer, () -> database.recheckConsistent(state.activation().run()));
          BackupUnitStartClient.RetirementGate afterRetirement =
              () -> {
                retiredChecks.verify();
                evidence.verify(
                    database,
                    java.time.Clock.systemUTC(),
                    retiredChecks.ownerGuard(budget::remainingNanos, retainedOwner),
                    original::referenceRun,
                    retiredChecks::verify);
                retiredChecks.verify();
              };
          // Registered BEFORE original/DB close; no expired DB/original capability is used there.
          var stopped = new java.util.concurrent.atomic.AtomicBoolean();
          onOuterFailure.accept(
              () -> {
                if (stopped.compareAndSet(false, true)) {
                  stopOnly(root, morning, budget, MaintenanceUnit.CADDY, caddy);
                  for (int i = started.size() - 1; i >= 0; i--)
                    stopOnly(
                        root, morning, budget, started.get(i).unit(), started.get(i).termination());
                }
              });
          var progress = new CompletionProgress(System::nanoTime, System.out::println);
          try {
            // Real Attempts invoke each before/after proof around their typed owned marker.
            retireCompleted(
                attempt::retireReadyAfter,
                started.get(1).attempt()::retireReadyAfter,
                started.get(0).attempt()::retireReadyAfter,
                started.get(0).attempt()::requireRetained,
                pending,
                afterRetirement,
                progress);
            completionGate(CompletionPhase.DONE_BEFORE, afterRetirement, progress).verify();
            var requested =
                state.completion().isPresent()
                    ? state.completion().orElseThrow()
                    : evidence.completion(state.activation(), java.time.Clock.systemUTC());
            require(original.complete(requested).equals(requested));
            completionGate(CompletionPhase.DONE_AFTER, afterRetirement, progress).verify();
            completed.set(requested);
          } catch (IOException | RuntimeException | Error uncertainCompletion) {
            // Half retirement, publication/readback or close unknown must not unwind the parent.
            progress.failure(uncertainCompletion);
            retain();
          }
        });
    return Objects.requireNonNull(completed.get());
  }

  /** SSC186/PT-OPS-CADDYFENCE004: fixed 30s window, capped by the SAME parent deadline. */
  static long caddyRemainingFloor(long parentRemaining) throws IOException {
    if (parentRemaining <= 0 || parentRemaining > java.util.concurrent.TimeUnit.MINUTES.toNanos(30))
      throw new IOException("Caddy startup budget unavailable");
    return Math.max(0, parentRemaining - java.util.concurrent.TimeUnit.SECONDS.toNanos(30));
  }

  /** Whole Unit/kernel termination only, valid even after original/DB callbacks expire. */
  private static void stopOnly(
      RootStartupContext root,
      RootStartupContext.Snapshot morning,
      MorningParentBudget budget,
      MaintenanceUnit unit,
      MaintenanceUnitTermination termination) {
    try {
      if (termination.quiescentObservation().isEmpty()) {
        var stopped = MaintenanceUnitStopClient.create(root, morning).stop(unit);
        if (stopped.status() != MaintenanceUnitStopClient.Status.CLIENT_EXITED_ZERO) retain();
        while (termination.quiescentObservation().isEmpty()) {
          budget.requireWithin();
          root.recheck(morning);
          pause();
        }
      }
      budget.requireWithin();
      root.recheck(morning);
    } catch (IOException | RuntimeException | Error unknown) {
      retain();
    }
  }

  /** API ready then Web under the same parent. Later completion is not fabricated here. */
  private static void startPending(
      RootStartupContext root,
      RootStartupContext.Snapshot morning,
      MorningParentBudget budget,
      MaintenanceRunState state,
      MorningDatabaseSession.Access database,
      MorningNewRunAdmission.OriginalProof original,
      StartupPermitRecords.Epoch issued)
      throws IOException {
    MorningStartupLaunchOwner.<Started>sequence(
        (service, earlier) ->
            startService(
                root, morning, budget, state, database, original, issued, service, earlier),
        started -> stopStarted(root, morning, budget, state, database, original, started),
        started -> {
          // Caddy and the same held original completion capability are still mandatory.
          throw new IOException("startup pipeline incomplete");
        });
  }

  @FunctionalInterface
  interface Launch<T> {
    T execute(ServiceConfigFiles.Service service, List<T> earlier) throws IOException;
  }

  @FunctionalInterface
  interface Stop<T> {
    void execute(T started);
  }

  @FunctionalInterface
  interface Completion<T> {
    void execute(List<T> started) throws IOException;
  }

  /** Package-only deterministic ownership/ordering PT; no native or completion authority. */
  static <T> void sequence(Launch<T> launch, Stop<T> stop, Completion<T> completion)
      throws IOException {
    Objects.requireNonNull(launch);
    Objects.requireNonNull(stop);
    Objects.requireNonNull(completion);
    var started = new ArrayList<T>(2);
    try {
      started.add(
          Objects.requireNonNull(
              launch.execute(ServiceConfigFiles.Service.API, List.copyOf(started))));
      started.add(
          Objects.requireNonNull(
              launch.execute(ServiceConfigFiles.Service.WEB, List.copyOf(started))));
      completion.execute(List.copyOf(started));
    } catch (IOException | RuntimeException | Error failure) {
      for (int index = started.size() - 1; index >= 0; index--) stop.execute(started.get(index));
      throw failure;
    }
  }

  private static void stopStarted(
      RootStartupContext root,
      RootStartupContext.Snapshot morning,
      MorningParentBudget budget,
      MaintenanceRunState state,
      MorningDatabaseSession.Access database,
      MorningNewRunAdmission.OriginalProof original,
      Started started) {
    try {
      var stopped = MaintenanceUnitStopClient.create(root, morning).stop(started.unit());
      if (stopped.status() != MaintenanceUnitStopClient.Status.CLIENT_EXITED_ZERO) retain();
      while (started.termination().quiescentObservation().isEmpty()) {
        budget.requireWithin();
        original.verify();
        database.recheckConsistent(state.activation().run());
        pause();
      }
      started.attempt().preserveObservation();
      original.verify();
      database.recheckConsistent(state.activation().run());
      root.recheck(morning);
    } catch (IOException | RuntimeException | Error unknownTermination) {
      retain();
    }
  }

  /** True launch/ticket and actual ordinary readiness; no Unit-active surrogate. SSC164. */
  @SuppressFBWarnings(
      value = "DMI_HARDCODED_ABSOLUTE_FILENAME",
      matchType = SuppressMatchType.EXACT,
      justification = "SSC137 fixed startup source with actual root-generation binding")
  private static Started startService(
      RootStartupContext root,
      RootStartupContext.Snapshot morning,
      MorningParentBudget budget,
      MaintenanceRunState state,
      MorningDatabaseSession.Access database,
      MorningNewRunAdmission.OriginalProof original,
      StartupPermitRecords.Epoch issued,
      ServiceConfigFiles.Service service,
      List<Started> earlier)
      throws IOException {
    var unit =
        service == ServiceConfigFiles.Service.API ? MaintenanceUnit.API : MaintenanceUnit.WEB;
    var target =
        service == ServiceConfigFiles.Service.API
            ? RootStartupContext.Service.API
            : RootStartupContext.Service.WEB;
    var termination = MaintenanceUnitTermination.create(root, morning, unit);
    require(termination.quiescentObservation().isPresent());
    budget.requireWithin();
    original.verify();
    database.recheckConsistent(state.activation().run());
    var starter = BackupUnitStartClient.createService(root, morning, service, issued, budget);
    var attempt = starter.start();
    // Any unresolved delivery retains M/DB/original and the durable marker to the outer deadline.
    if (attempt.status() != BackupUnitStartClient.Status.CLIENT_EXITED_ZERO) retain();
    boolean ticket = false;
    boolean observationClosed = false;
    try {
      RootStartupContext.Snapshot child;
      while (true) {
        budget.requireWithin();
        original.verify();
        database.recheckConsistent(state.activation().run());
        try {
          child = root.captureServiceRoot(morning, target);
          break;
        } catch (IOException notYetObserved) {
          pause();
        }
      }
      var calls = LinuxDirectoryCalls.create();
      Path startupPath = Path.of("/run/schubert-nk/startup");
      var observedChild = child;
      var information =
          ResourceScope.acquire(
              () -> OwnedTransferDirectory.open(calls, startupPath),
              OwnedTransferDirectory::close,
              directory -> {
                var security = LinuxInodeSecurity.create();
                var permits = new StartupPermitFiles(directory, security);
                require(issued.equals(permits.current()));
                permits.readIssued();
                var files = new StartupLaunchFiles(directory, security, issued);
                files.requireStartIntent(service);
                var owner = files.readOwner();
                owner.parentsGuard().check();
                require(observedChild.equals(root.captureServiceRoot(morning, target)));
                var launch =
                    new StartupLaunchRecord(
                        service,
                        issued.boot(),
                        issued.epoch(),
                        issued.permitDigest().orElseThrow(),
                        StartupLaunchRecord.sha256(owner.encode()),
                        new MaintenanceOwnerFrame.Parent(
                            observedChild.invocation(),
                            observedChild.pid(),
                            observedChild.startTicks()));
                files.prepareLaunch(launch, UUID.randomUUID());
                require(
                    launch.equals(files.readLaunch(service)) && issued.equals(permits.current()));
                var permit = permits.readIssued();
                owner.parentsGuard().check();
                var expected =
                    RootReleaseApprovalReader.create(root, morning)
                        .execute(
                            approval -> {
                              var manifest =
                                  StartupReleaseManifest.createHost(
                                      new FixedServiceIdentity().configurationGroup());
                              require(
                                  manifest
                                      .verify(approval)
                                      .sha256()
                                      .equals(permit.releaseDigest()));
                              return manifest.publicInformation(permit.releaseDigest());
                            });
                require(issued.equals(permits.current()) && permit.equals(permits.readIssued()));
                owner.parentsGuard().check();
                return expected;
              });
      ticket = true;
      var readiness = MorningServiceReadiness.create(root, morning, observedChild, information);
      var childBudget =
          MorningParentBudget.borrow(
              root.serviceGenerationDeadline(morning, observedChild, budget.deadlineNanos()));
      while (!root.serviceGenerationExited(morning, observedChild)) {
        budget.requireWithin();
        childBudget.requireWithin();
        original.verify();
        database.recheckConsistent(state.activation().run());
        for (var prior : earlier) require(prior.readiness().ready());
        boolean ready = false;
        try {
          ready = readiness.ready();
        } catch (java.net.ConnectException notYetListening) {
          // A fixed socket can appear before its HTTP acceptor. Never promote unknown IO.
        }
        if (ready) {
          childBudget.requireWithin();
          budget.requireWithin();
          original.verify();
          database.recheckConsistent(state.activation().run());
          verifyCurrentLaunch(root, morning, issued, service, observedChild);
          require(readiness.ready());
          return new Started(unit, termination, attempt, readiness, service, observedChild);
        }
        pause();
      }
      var stopped = MaintenanceUnitStopClient.create(root, morning).stop(unit);
      if (stopped.status() != MaintenanceUnitStopClient.Status.CLIENT_EXITED_ZERO) retain();
      while (termination.quiescentObservation().isEmpty()) {
        budget.requireWithin();
        original.verify();
        database.recheckConsistent(state.activation().run());
        pause();
      }
      try {
        attempt.preserveObservation();
        observationClosed = true;
      } catch (IOException | RuntimeException | Error unknownClose) {
        retain();
      }
      original.verify();
      database.recheckConsistent(state.activation().run());
      root.recheck(morning);
    } catch (IOException | RuntimeException | Error failure) {
      // No receipt/whole termination means an unwind could orphan a delivered Root/service.
      if (!ticket) retain();
      try {
        if (termination.quiescentObservation().isEmpty()) {
          var stopped = MaintenanceUnitStopClient.create(root, morning).stop(unit);
          if (stopped.status() != MaintenanceUnitStopClient.Status.CLIENT_EXITED_ZERO) retain();
          while (termination.quiescentObservation().isEmpty()) {
            budget.requireWithin();
            original.verify();
            database.recheckConsistent(state.activation().run());
            pause();
          }
        }
        if (!observationClosed) attempt.preserveObservation();
      } catch (IOException | RuntimeException | Error unknownTermination) {
        retain();
      }
      throw failure;
    }
    // No successful service receipt/readiness yet: keep intent and revoke permit under same M.
    throw new IOException("service startup not ready");
  }

  private static void verifyCurrentLaunch(
      RootStartupContext root,
      RootStartupContext.Snapshot morning,
      StartupPermitRecords.Epoch issued,
      ServiceConfigFiles.Service service,
      RootStartupContext.Snapshot captured)
      throws IOException {
    verifyCurrentLaunch(root, morning, issued, service, captured, true);
  }

  @SuppressFBWarnings(
      value = "DMI_HARDCODED_ABSOLUTE_FILENAME",
      matchType = SuppressMatchType.EXACT,
      justification =
          "SSC178 fixed same-epoch directory, permits intent-free verification only after retirement")
  private static void verifyCurrentLaunch(
      RootStartupContext root,
      RootStartupContext.Snapshot morning,
      StartupPermitRecords.Epoch issued,
      ServiceConfigFiles.Service service,
      RootStartupContext.Snapshot captured,
      boolean pending)
      throws IOException {
    root.recheckServiceGeneration(morning, captured);
    var calls = LinuxDirectoryCalls.create();
    Path startupPath = Path.of("/run/schubert-nk/startup");
    ResourceScope.acquire(
        () -> OwnedTransferDirectory.open(calls, startupPath),
        OwnedTransferDirectory::close,
        directory -> {
          var security = LinuxInodeSecurity.create();
          var permits = new StartupPermitFiles(directory, security);
          require(issued.equals(permits.current()));
          permits.readIssued();
          var files = new StartupLaunchFiles(directory, security, issued);
          if (pending) files.requireStartIntent(service);
          var owner = files.readOwner();
          owner.parentsGuard().check();
          var expected =
              new StartupLaunchRecord(
                  service,
                  issued.boot(),
                  issued.epoch(),
                  issued.permitDigest().orElseThrow(),
                  StartupLaunchRecord.sha256(owner.encode()),
                  new MaintenanceOwnerFrame.Parent(
                      captured.invocation(), captured.pid(), captured.startTicks()));
          require(expected.equals(files.readLaunch(service)) && issued.equals(permits.current()));
          permits.readIssued();
          owner.parentsGuard().check();
          return Boolean.TRUE;
        });
    root.recheckServiceGeneration(morning, captured);
  }

  private static void pause() throws IOException {
    try {
      Thread.sleep(25);
    } catch (InterruptedException interrupted) {
      Thread.currentThread().interrupt();
      throw new IOException("service startup unavailable");
    }
  }

  static void retain() {
    for (; ; ) {
      java.util.concurrent.locks.LockSupport.parkNanos(
          java.util.concurrent.TimeUnit.SECONDS.toNanos(1));
      Thread.interrupted();
    }
  }
}
