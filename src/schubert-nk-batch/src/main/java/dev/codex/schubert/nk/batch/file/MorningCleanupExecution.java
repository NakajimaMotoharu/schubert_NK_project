package dev.codex.schubert.nk.batch.file;

import static dev.codex.schubert.nk.batch.file.EnvironmentInodePolicy.require;

import dev.codex.schubert.nk.batch.backup.BackupManifest;
import dev.codex.schubert.nk.batch.platform.*;
import dev.codex.schubert.nk.batch.repository.*;
import dev.codex.schubert.nk.bootstrap.*;
import dev.codex.schubert.nk.storage.*;
import edu.umd.cs.findbugs.annotations.SuppressFBWarnings;
import edu.umd.cs.findbugs.annotations.SuppressMatchType;
import java.io.IOException;
import java.nio.file.Path;
import java.security.*;
import java.util.*;
import java.util.concurrent.atomic.AtomicReference;
import org.jspecify.annotations.NullMarked;

/** Same continuous Morning callback, no new M/A/DB owner. SS341/343 SSC119/CEXEC001. */
@NullMarked
final class MorningCleanupExecution {
  private MorningCleanupExecution() {}

  @SuppressFBWarnings(
      value = "DMI_HARDCODED_ABSOLUTE_FILENAME",
      matchType = SuppressMatchType.EXACT,
      justification = "SS343 fixed Cleanup source/current, no alternate run/Unit; CEXEC001")
  static CleanupTerminalRepository.Snapshot execute(
      RootStartupContext context,
      RootStartupContext.Snapshot expected,
      MorningParentBudget budget,
      MaintenanceRunState state,
      MorningDatabaseSession.Access database,
      StartupPermitRecords.Epoch epoch,
      MorningNewRunAdmission.OriginalProof original,
      BackupManifest actual)
      throws IOException {
    Objects.requireNonNull(context);
    Objects.requireNonNull(expected);
    Objects.requireNonNull(budget);
    Objects.requireNonNull(state);
    Objects.requireNonNull(database);
    Objects.requireNonNull(epoch);
    Objects.requireNonNull(original);
    Objects.requireNonNull(actual);
    require(
        expected.service() == RootStartupContext.Service.MORNING
            && state.activation().equals(epoch.activation())
            && epoch.state() == StartupPermitRecords.State.INVALID
            && actual.run().equals(state.activation().run())
            && expected.boot().equals(epoch.boot().toString()));
    Path currentPath = Path.of("/run/schubert-nk/startup");
    MaintenanceOwnerFrame.Guard parent =
        () -> {
          budget.requireWithin();
          context.recheck(expected);
          original.verify();
          var startup = OwnedTransferDirectory.open(LinuxDirectoryCalls.create(), currentPath);
          ResourceScope.use(
              startup::close,
              () -> {
                require(
                    new StartupPermitFiles(startup, LinuxInodeSecurity.create())
                        .current()
                        .equals(epoch));
                return Boolean.TRUE;
              });
          context.recheck(expected);
          original.verify();
          budget.requireWithin();
          return budget.remainingNanos();
        };
    parent.check();
    database.recheckConsistent(state.activation().run());
    var frame =
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
    var request =
        new CleanupWorkerRequest(
            actual.run().id(), state.activation().id(), actual.run().cutoff(), digest(actual));
    var directory =
        OwnedTransferDirectory.open(
            LinuxDirectoryCalls.create(), Path.of("/run/schubert-nk/cleanup-request"));
    return ResourceScope.use(
        directory::close,
        () -> {
          var security = LinuxInodeSecurity.create();
          var owners =
              CleanupWorkerRequestFiles.forOwner(
                  directory, security, CleanupWorkerRequestFiles.OwnerSource.PARENT);
          var requests = new CleanupWorkerRequestFiles(directory, security);
          requests.requireClear();
          parent.check();
          owners.prepareOwner(frame, UUID.randomUUID());
          requests.prepare(request, UUID.randomUUID());
          parent.check();
          var result = new AtomicReference<CleanupTerminalRepository.Snapshot>();
          var cycle =
              MorningBackupUnitCycle.create(
                  context, expected, budget, BackupUnitStartClient.Target.CLEANUP);
          var terminal =
              cycle.executeHandoff(
                  operation -> database.handoffCleanup(operation::execute),
                  receipt -> {
                    parent.check();
                    if (receipt.exitCode() == 30)
                      database.observeCleanupRejected(state.activation().run(), receipt, parent);
                    else
                      result.set(
                          database.observeCleanup(
                              state.activation().run(), receipt.exitCode(), parent));
                    parent.check();
                  },
                  () -> {
                    parent.check();
                    require(
                        MaintenanceUnitTermination.create(
                                context, expected, MaintenanceUnit.INSPECTOR)
                            .quiescent()
                            .isPresent());
                    requireInspectorEnvironmentClear();
                    requests.requireOwnedCycle();
                    require(owners.readOwner().equals(frame) && requests.read().equals(request));
                    requests.retire(request);
                    owners.retireOwner(frame);
                    parent.check();
                  });
          parent.check();
          if (terminal.exitCode() == 30) throw new IOException("Cleanup rejected");
          return Objects.requireNonNull(result.get(), "actual Cleanup readback");
        });
  }

  @SuppressFBWarnings(
      value = "DMI_HARDCODED_ABSOLUTE_FILENAME",
      matchType = SuppressMatchType.EXACT,
      justification = "SS343 fixed Inspector environment root, no alternate namespace; CEXEC004")
  private static void requireInspectorEnvironmentClear() throws IOException {
    var directory =
        OwnedTransferDirectory.open(
            LinuxDirectoryCalls.create(), Path.of("/run/schubert-nk/maintenance"));
    ResourceScope.use(
        directory::close,
        () -> {
          new InspectorEnvironmentPublisher(directory, LinuxInodeSecurity.create()).requireFresh();
          return Boolean.TRUE;
        });
  }

  private static String digest(BackupManifest actual) throws IOException {
    byte[] bytes = BackupManifestCodec.encode(actual);
    try {
      return HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(bytes));
    } catch (NoSuchAlgorithmException unavailable) {
      throw new IOException("backup binding unavailable");
    } finally {
      Arrays.fill(bytes, (byte) 0);
    }
  }
}
