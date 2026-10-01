package dev.codex.schubert.nk.batch.file;

import static dev.codex.schubert.nk.batch.file.EnvironmentInodePolicy.require;

import dev.codex.schubert.nk.batch.platform.*;
import dev.codex.schubert.nk.batch.repository.*;
import dev.codex.schubert.nk.bootstrap.MaintenanceOwnerFrame;
import dev.codex.schubert.nk.storage.*;
import edu.umd.cs.findbugs.annotations.SuppressFBWarnings;
import edu.umd.cs.findbugs.annotations.SuppressMatchType;
import java.io.IOException;
import java.nio.file.Path;
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

  /** Current S3 stage: true launch/ticket and cold failure, never a fake ready callback. */
  @SuppressFBWarnings(
      value = "DMI_HARDCODED_ABSOLUTE_FILENAME",
      matchType = SuppressMatchType.EXACT,
      justification = "SSC137 fixed startup source with actual root-generation binding")
  private static void startPending(
      RootStartupContext root,
      RootStartupContext.Snapshot morning,
      MorningParentBudget budget,
      MaintenanceRunState state,
      MorningDatabaseSession.Access database,
      MorningNewRunAdmission.OriginalProof original,
      StartupPermitRecords.Epoch issued)
      throws IOException {
    var service = ServiceConfigFiles.Service.API;
    var termination = MaintenanceUnitTermination.create(root, morning, MaintenanceUnit.API);
    require(termination.quiescentObservation().isPresent());
    budget.requireWithin();
    original.verify();
    database.recheckConsistent(state.activation().run());
    var starter = BackupUnitStartClient.createService(root, morning, service, issued, budget);
    var attempt = starter.start();
    // Any unresolved delivery retains M/DB/original and the durable marker to the outer deadline.
    if (attempt.status() != BackupUnitStartClient.Status.CLIENT_EXITED_ZERO) retain();
    boolean ticket = false;
    try {
      RootStartupContext.Snapshot child;
      while (true) {
        budget.requireWithin();
        original.verify();
        database.recheckConsistent(state.activation().run());
        try {
          child = root.captureServiceRoot(morning, RootStartupContext.Service.API);
          break;
        } catch (IOException notYetObserved) {
          pause();
        }
      }
      var directory =
          OwnedTransferDirectory.open(
              LinuxDirectoryCalls.create(), Path.of("/run/schubert-nk/startup"));
      var observedChild = child;
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
            require(
                observedChild.equals(
                    root.captureServiceRoot(morning, RootStartupContext.Service.API)));
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
            require(launch.equals(files.readLaunch(service)) && issued.equals(permits.current()));
            permits.readIssued();
            owner.parentsGuard().check();
            return Boolean.TRUE;
          });
      ticket = true;
      // Actual ordinary assembly still fails closed at 50. Maintain the live parent through it.
      while (!root.serviceGenerationExited(morning, observedChild)) {
        budget.requireWithin();
        original.verify();
        database.recheckConsistent(state.activation().run());
        pause();
      }
      var stopped = MaintenanceUnitStopClient.create(root, morning).stop(MaintenanceUnit.API);
      if (stopped.status() != MaintenanceUnitStopClient.Status.CLIENT_EXITED_ZERO) retain();
      while (termination.quiescentObservation().isEmpty()) {
        budget.requireWithin();
        original.verify();
        database.recheckConsistent(state.activation().run());
        pause();
      }
      try {
        attempt.preserveObservation();
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
        if (termination.quiescentObservation().isEmpty()) retain();
      } catch (IOException | RuntimeException | Error unknownTermination) {
        retain();
      }
      throw failure;
    }
    // No successful service receipt/readiness yet: keep intent and revoke permit under same M.
    throw new IOException("service startup not ready");
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
