package dev.codex.schubert.nk.batch.file;

import static dev.codex.schubert.nk.batch.file.EnvironmentInodePolicy.require;

import dev.codex.schubert.nk.batch.platform.*;
import dev.codex.schubert.nk.batch.repository.*;
import dev.codex.schubert.nk.bootstrap.*;
import dev.codex.schubert.nk.storage.*;
import edu.umd.cs.findbugs.annotations.*;
import java.io.IOException;
import java.nio.file.Path;
import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.*;
import java.util.concurrent.atomic.AtomicReference;
import org.jspecify.annotations.NullMarked;

/**
 * Genuine same-owner Broker→Expiry, separate one-shot advisory handoff after verified Cleanup.
 * NK-OPS-001/NK-BAT-001 OPS009/MQ/UI251/253 SS321/341§9/343 SSC125 EXPARENT001..005. Actual DB
 * begin/audit/receipt only; no invented after=0 or previous audit as current SKIP.
 */
@NullMarked
final class MorningExpiryExecution {
  private MorningExpiryExecution() {}

  @SuppressFBWarnings(
      value = "DMI_HARDCODED_ABSOLUTE_FILENAME",
      matchType = SuppressMatchType.EXACT,
      justification = "SS343 fixed same-owner expiry-request/current namespaces, no path selector")
  static MorningDatabaseSession.ExpiryObservation execute(
      RootStartupContext context,
      RootStartupContext.Snapshot expected,
      MorningParentBudget budget,
      MaintenanceRunState state,
      MorningDatabaseSession.Access database,
      StartupPermitRecords.Epoch epoch,
      MorningNewRunAdmission.OriginalProof original,
      MorningBrokerUnitCycle.Live broker)
      throws IOException {
    require(
        expected.service() == RootStartupContext.Service.MORNING
            && epoch.state() == StartupPermitRecords.State.INVALID
            && epoch.activation().equals(state.activation())
            && expected.boot().equals(epoch.boot().toString()));
    Path currentPath = Path.of("/run/schubert-nk/startup");
    Path requestsPath = Path.of("/run/schubert-nk/expiry-request");
    MaintenanceOwnerFrame.Guard parent =
        () -> {
          budget.requireWithin();
          context.recheck(expected);
          original.verify();
          var current = OwnedTransferDirectory.open(LinuxDirectoryCalls.create(), currentPath);
          ResourceScope.use(
              current::close,
              () -> {
                require(
                    new StartupPermitFiles(current, LinuxInodeSecurity.create())
                        .current()
                        .equals(epoch));
                return true;
              });
          // Broker's original guard reads parent DB; do not call it during advisory handoff.
          var probe = InspectorUnitProbe.forTarget(InspectorUnitSnapshot.Target.ARTEMIS);
          var before = probe.read();
          require(before.brokerRunningInvocation(broker.invocation()));
          var actor =
              new ChildStartupContext()
                  .verifyBroker(
                      epoch.boot(),
                      broker.invocation(),
                      new FixedServiceIdentity().resolveArtemis());
          require(before.running(actor.pid(), broker.invocation()) && before.matches(probe.read()));
          context.recheck(expected);
          original.verify();
          return budget.remainingNanos();
        };
    parent.check();
    database.recheckConsistent(state.activation().run());
    var owner =
        new MaintenanceOwnerFrame(
            epoch.boot(),
            state.activation().run().id(),
            state.activation().id(),
            state.activation().run().cutoff(),
            epoch.epoch(),
            new MaintenanceOwnerFrame.Parent(
                expected.invocation(), expected.pid(), expected.startTicks()),
            Optional.empty(),
            budget.deadlineNanos());
    var directory = OwnedTransferDirectory.open(LinuxDirectoryCalls.create(), requestsPath);
    return ResourceScope.use(
        directory::close,
        () -> {
          var security = LinuxInodeSecurity.create();
          var requests = CleanupWorkerRequestFiles.forExpiry(directory, security);
          var owners =
              CleanupWorkerRequestFiles.forOwner(
                  directory, security, CleanupWorkerRequestFiles.OwnerSource.PARENT);
          requests.requireClear();
          parent.check();
          var begins =
              database.beginExpiry(
                  state.activation().run(), Instant.now().truncatedTo(ChronoUnit.MICROS), parent);
          var handle = begins.current();
          var prior =
              begins
                  .prior()
                  .map(
                      value ->
                          new CleanupWorkerRequest.Expiry.PriorExpiry(
                              value.handle().id(),
                              value.handle().attempt(),
                              value.handle().startedAt(),
                              Objects.requireNonNull(value.audit().ended())));
          var request =
              new CleanupWorkerRequest.Expiry(
                  handle.run().id(),
                  state.activation().id(),
                  handle.run().cutoff(),
                  epoch.boot(),
                  epoch.epoch(),
                  broker.invocation(),
                  handle.id(),
                  handle.attempt(),
                  handle.startedAt(),
                  handle.skipped(),
                  prior);
          owners.prepareOwner(owner, UUID.randomUUID());
          requests.prepareExpiry(request, UUID.randomUUID());
          parent.check();
          var result = new AtomicReference<MorningDatabaseSession.ExpiryObservation>();
          var cycle =
              MorningBackupUnitCycle.create(
                  context, expected, budget, BackupUnitStartClient.Target.EXPIRY);
          var actual =
              cycle.executeHandoff(
                  work -> database.handoffExpiry(work::execute),
                  receipt -> {
                    parent.check();
                    result.set(database.observeExpiry(begins, receipt, parent));
                    parent.check();
                  },
                  () -> {
                    parent.check();
                    requests.requireExpiryOwnedCycle();
                    require(
                        owners.readOwner().equals(owner) && requests.readExpiry().equals(request));
                    requests.retireExpiry(request);
                    owners.retireOwner(owner);
                    parent.check();
                  });
          parent.check();
          if (actual.exitCode() == 30) throw new IOException("Expiry rejected");
          return Objects.requireNonNull(
              result.get(), "actual Expiry terminal/receipt/audit readback");
        });
  }
}
