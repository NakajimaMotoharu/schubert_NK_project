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

  /** Data only: genuine current receipt and seven separate optional original references. SSC126. */
  record Completion(
      CleanupTerminalRepository.Snapshot terminal,
      BackupUnitReceiptGate.TerminalReceipt receipt,
      List<Optional<CleanupTerminalRepository.Entry>> references) {
    Completion {
      Objects.requireNonNull(terminal);
      Objects.requireNonNull(receipt);
      references = List.copyOf(references);
      if (receipt.target() != BackupUnitStartClient.Target.CLEANUP
          || receipt.exitCode() != terminal.exitCode()
          || references.size() != CleanupTerminalRepository.STEPS.size())
        throw new IllegalArgumentException("invalid actual Cleanup completion");
    }

    @Override
    public String toString() {
      return "CleanupCompletion[actual=<redacted>]";
    }
  }

  static Completion execute(
      RootStartupContext context,
      RootStartupContext.Snapshot expected,
      MorningParentBudget budget,
      MaintenanceRunState state,
      MorningDatabaseSession.Access database,
      StartupPermitRecords.Epoch epoch,
      MorningNewRunAdmission.OriginalProof original,
      BackupManifest actual)
      throws IOException {
    Objects.requireNonNull(actual);
    return execute(
        context,
        expected,
        budget,
        state,
        database,
        epoch,
        original,
        new CleanupWorkerRequest(
            actual.run().id(), state.activation().id(), actual.run().cutoff(), digest(actual)));
  }

  static Completion executeFailed(
      RootStartupContext context,
      RootStartupContext.Snapshot expected,
      MorningParentBudget budget,
      MaintenanceRunState state,
      MorningDatabaseSession.Access database,
      StartupPermitRecords.Epoch epoch,
      MorningNewRunAdmission.OriginalProof original,
      MorningDatabaseSession.BackupBegins begins,
      BackupUnitReceiptGate.TerminalReceipt actual)
      throws IOException {
    Objects.requireNonNull(actual);
    require(
        actual.target() == BackupUnitStartClient.Target.BACKUP
            && actual.exitCode() >= 1
            && actual.exitCode() <= 255);
    MaintenanceOwnerFrame.Guard base =
        () -> {
          budget.requireWithin();
          context.recheck(expected);
          original.verify();
          return budget.remainingNanos();
        };
    var failed = database.failedBackupSnapshot(begins, base);
    var request =
        new CleanupFailedBackupRequest(
            state.activation().run().id(),
            state.activation().id(),
            state.activation().run().cutoff(),
            epoch.boot(),
            epoch.epoch(),
            actual.invocation(),
            actual.startedMonotonic(),
            actual.endedMonotonic(),
            actual.exitCode(),
            failed);
    require(
        request.receiptMatches(
            BackupUnitTermination.create(context, expected)
                .quiescent()
                .orElseThrow(() -> new IOException("Backup failed receipt unavailable"))));
    return execute(context, expected, budget, state, database, epoch, original, request);
  }

  @SuppressFBWarnings(
      value = "DMI_HARDCODED_ABSOLUTE_FILENAME",
      matchType = SuppressMatchType.EXACT,
      justification = "SS343 fixed Cleanup namespace/current, same parent owner SSC124 CFLOW001")
  private static Completion execute(
      RootStartupContext context,
      RootStartupContext.Snapshot expected,
      MorningParentBudget budget,
      MaintenanceRunState state,
      MorningDatabaseSession.Access database,
      StartupPermitRecords.Epoch epoch,
      MorningNewRunAdmission.OriginalProof original,
      CleanupProfile request)
      throws IOException {
    Objects.requireNonNull(context);
    Objects.requireNonNull(expected);
    Objects.requireNonNull(budget);
    Objects.requireNonNull(state);
    Objects.requireNonNull(database);
    Objects.requireNonNull(epoch);
    Objects.requireNonNull(original);
    Objects.requireNonNull(request);
    require(
        expected.service() == RootStartupContext.Service.MORNING
            && state.activation().equals(epoch.activation())
            && epoch.state() == StartupPermitRecords.State.INVALID
            && request.run().equals(state.activation().run().id())
            && request.activation().equals(state.activation().id())
            && request.cutoff().equals(state.activation().run().cutoff())
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
          var requests =
              request instanceof CleanupFailedBackupRequest
                  ? CleanupWorkerRequestFiles.forFailure(directory, security)
                  : new CleanupWorkerRequestFiles(directory, security);
          requests.requireClear();
          parent.check();
          owners.prepareOwner(frame, UUID.randomUUID());
          switch (request) {
            case CleanupWorkerRequest success -> requests.prepare(success, UUID.randomUUID());
            case CleanupFailedBackupRequest failed ->
                requests.prepareFailure(failed, UUID.randomUUID());
          }
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
                          request instanceof CleanupFailedBackupRequest
                              ? database.observeCleanupBackupUnavailable(
                                  state.activation().run(), receipt.exitCode(), parent)
                              : database.observeCleanup(
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
                    require(owners.readOwner().equals(frame));
                    switch (request) {
                      case CleanupWorkerRequest success -> {
                        require(requests.read().equals(success));
                        requests.retire(success);
                      }
                      case CleanupFailedBackupRequest failed -> {
                        require(requests.readFailure().equals(failed));
                        require(
                            failed.receiptMatches(
                                BackupUnitTermination.create(context, expected)
                                    .quiescent()
                                    .orElseThrow(() -> new IOException("Backup receipt changed"))));
                        requests.retireFailure(failed);
                      }
                    }
                    owners.retireOwner(frame);
                    parent.check();
                  });
          parent.check();
          if (terminal.exitCode() == 30) throw new IOException("Cleanup rejected");
          var observed = Objects.requireNonNull(result.get(), "actual Cleanup readback");
          return new Completion(
              observed,
              cycle.completedReceipt(),
              database.cleanupReferences(observed, parent, original::referenceRun));
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
