package dev.codex.schubert.nk.batch.file;

import static dev.codex.schubert.nk.batch.file.EnvironmentInodePolicy.require;

import dev.codex.schubert.nk.batch.platform.*;
import dev.codex.schubert.nk.batch.repository.*;
import dev.codex.schubert.nk.bootstrap.FixedServiceIdentity;
import dev.codex.schubert.nk.bootstrap.MaintenanceOwnerFrame;
import dev.codex.schubert.nk.bootstrap.StartupReleaseManifest;
import dev.codex.schubert.nk.storage.*;
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
  static void publish(
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
    var directory =
        OwnedTransferDirectory.open(
            LinuxDirectoryCalls.create(), Path.of("/run/schubert-nk/startup"));
    ResourceScope.use(
        directory::close,
        () -> {
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
    startPending(root, morning, budget, state, database, original, issued);
  }

  private record Started(
      MaintenanceUnit unit,
      MaintenanceUnitTermination termination,
      BackupUnitStartClient.Attempt attempt,
      MorningServiceReadiness readiness) {}

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
    var started = new ArrayList<T>();
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
      var directory =
          OwnedTransferDirectory.open(
              LinuxDirectoryCalls.create(), Path.of("/run/schubert-nk/startup"));
      var observedChild = child;
      var information =
          ResourceScope.use(
              directory::close,
              () -> {
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
          return new Started(unit, termination, attempt, readiness);
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

  @SuppressFBWarnings(
      value = "DMI_HARDCODED_ABSOLUTE_FILENAME",
      matchType = SuppressMatchType.EXACT,
      justification = "SSC164 recheck only fixed same-epoch startup directory and launch")
  private static void verifyCurrentLaunch(
      RootStartupContext root,
      RootStartupContext.Snapshot morning,
      StartupPermitRecords.Epoch issued,
      ServiceConfigFiles.Service service,
      RootStartupContext.Snapshot captured)
      throws IOException {
    root.recheckServiceGeneration(morning, captured);
    var directory =
        OwnedTransferDirectory.open(
            LinuxDirectoryCalls.create(), Path.of("/run/schubert-nk/startup"));
    ResourceScope.use(
        directory::close,
        () -> {
          var security = LinuxInodeSecurity.create();
          var permits = new StartupPermitFiles(directory, security);
          require(issued.equals(permits.current()));
          permits.readIssued();
          var files = new StartupLaunchFiles(directory, security, issued);
          files.requireStartIntent(service);
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

  private static void retain() {
    for (; ; ) {
      java.util.concurrent.locks.LockSupport.parkNanos(
          java.util.concurrent.TimeUnit.SECONDS.toNanos(1));
      Thread.interrupted();
    }
  }
}
