package dev.codex.schubert.nk.batch.file;

import static dev.codex.schubert.nk.batch.file.EnvironmentInodePolicy.require;

import dev.codex.schubert.nk.batch.platform.BackupUnitTermination;
import dev.codex.schubert.nk.batch.platform.CleanupFailedBackupRequest;
import dev.codex.schubert.nk.batch.platform.CleanupWorkerRequest;
import dev.codex.schubert.nk.batch.platform.MaintenanceUnitTermination;
import dev.codex.schubert.nk.batch.platform.RootReleaseAdmission;
import dev.codex.schubert.nk.batch.platform.RootStartupContext;
import dev.codex.schubert.nk.batch.repository.BackupFailureSnapshot;
import dev.codex.schubert.nk.batch.repository.BatchRepositoryException;
import dev.codex.schubert.nk.batch.repository.BatchRun;
import dev.codex.schubert.nk.batch.repository.CleanupDatabaseSession;
import dev.codex.schubert.nk.batch.repository.MaintenanceActivation;
import dev.codex.schubert.nk.bootstrap.FixedServiceIdentity;
import dev.codex.schubert.nk.bootstrap.MaintenanceOwnerFrame;
import dev.codex.schubert.nk.storage.LinuxDirectoryCalls;
import dev.codex.schubert.nk.storage.LinuxHostDirectoryCalls;
import dev.codex.schubert.nk.storage.LinuxInodeSecurity;
import dev.codex.schubert.nk.storage.OwnedTransferDirectory;
import dev.codex.schubert.nk.storage.ResourceScope;
import dev.codex.schubert.nk.storage.ServiceCredentialLocation;
import dev.codex.schubert.nk.storage.StorageIoException;
import edu.umd.cs.findbugs.annotations.SuppressFBWarnings;
import edu.umd.cs.findbugs.annotations.SuppressMatchType;
import java.io.IOException;
import java.nio.file.Path;
import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.UUID;
import org.jspecify.annotations.NullMarked;

/**
 * Genuine Cleanup composition inside its own credential/backup/DB owners. No supplied path, role,
 * run, key or alternate success entry. NK-OPS-001/NK-BAT-001/OPS009/BAK001/DAT009/UI251/
 * SS341§7.3/343§6.17/SSC119; PT-OPS-CEXEC001/CINSPECT001..004.
 */
@NullMarked
final class CleanupNativeExecution {
  private CleanupNativeExecution() {}

  @SuppressFBWarnings(
      value = "DMI_HARDCODED_ABSOLUTE_FILENAME",
      matchType = SuppressMatchType.EXACT,
      justification = "SS343 fixed Cleanup private copy, readonly host backup/current; CEXEC001")
  static int execute() throws IOException {
    var context = RootStartupContext.create();
    var expected = context.capture(RootStartupContext.Service.CLEANUP);
    var release = RootReleaseAdmission.create(context, expected);
    Path fixed = Path.of("/run/credentials/schubert-nk-cleanup.service");
    Path backupPath = Path.of("/srv/schubert-nk/backup");
    require(ServiceCredentialLocation.read(System.getenv()).directory().equals(fixed));
    var security = LinuxInodeSecurity.create();
    var credentialCalls = LinuxDirectoryCalls.create();
    return ResourceScope.<OwnedTransferDirectory, Integer, IOException>acquire(
        () -> OwnedTransferDirectory.open(credentialCalls, fixed),
        OwnedTransferDirectory::close,
        credentials -> {
          var reader = new RootBatchCredentialReader(credentials, security);
          var owner = reader.readMaintenanceOwner();
          require(
              owner.boot().equals(UUID.fromString(expected.boot())) && owner.cleanup().isEmpty());
          var parents = owner.parentsGuard();
          MaintenanceOwnerFrame.Guard environment =
              () -> {
                context.recheck(expected);
                parents.check();
                verifyOriginalAndCurrent(context, expected, owner);
                CleanupNativePreflight.requireApplicationsStopped(
                    unit ->
                        MaintenanceUnitTermination.createCleanup(context, expected, unit)
                            .quiescent()
                            .isPresent());
                context.recheck(expected);
                return parents.remainingNanos();
              };
          environment.check(); // Before batch password/backup/DB, never just a parsed claim.
          var profile = reader.readCleanupProfile();
          require(
              profile.run().equals(owner.run())
                  && profile.activation().equals(owner.activation())
                  && profile.cutoff().equals(owner.cutoff()));
          if (profile instanceof CleanupFailedBackupRequest failed) {
            require(failed.boot().equals(owner.boot()) && failed.epoch().equals(owner.epoch()));
            var termination = BackupUnitTermination.forCleanupFailedBackup(context, expected);
            MaintenanceOwnerFrame.Guard failedGuard =
                () -> {
                  environment.check();
                  require(
                      failed.receiptMatches(
                          termination
                              .quiescent()
                              .orElseThrow(
                                  () -> new IOException("Backup failed receipt unavailable"))));
                  require(
                      reader.readCleanupProfile().equals(failed)
                          && reader.readMaintenanceOwner().equals(owner));
                  return environment.remainingNanos();
                };
            failedGuard.check();
            var database =
                new CleanupDatabaseSession(
                    "jdbc:postgresql://127.0.0.1:5432/schubert_nk", context, expected, release);
            return database.execute(
                reader.read(),
                connection -> {
                  MaintenanceOwnerFrame.Guard mutation =
                      () -> {
                        failedGuard.check();
                        verifyFailedPair(connection, failed.failure(), failedGuard);
                        return failedGuard.remainingNanos();
                      };
                  mutation.check();
                  int result =
                      new CleanupMaintenanceWork(context, expected, owner, mutation)
                          .executeFailed(connection);
                  mutation.check();
                  return result;
                });
          }
          var request = (CleanupWorkerRequest) profile;
          var identity = new FixedServiceIdentity().resolveBackup();
          var backupCalls = LinuxHostDirectoryCalls.create();
          return ResourceScope.<OwnedTransferDirectory, Integer, IOException>acquire(
              () -> OwnedTransferDirectory.open(backupCalls, backupPath),
              OwnedTransferDirectory::close,
              backup -> {
                var manifests =
                    new BackupManifestReader(backup, security, identity.uid(), identity.gid());
                var artifacts =
                    new BackupArtifactVerifier(backup, security, identity.uid(), identity.gid());
                var database =
                    new CleanupDatabaseSession(
                        "jdbc:postgresql://127.0.0.1:5432/schubert_nk", context, expected, release);
                environment.check();
                return database.execute(
                    reader.read(),
                    connection -> {
                      var manifest =
                          new CleanupBackupAdmission(manifests, artifacts)
                              .verify(
                                  request,
                                  Instant.now().truncatedTo(ChronoUnit.MICROS),
                                  connection);
                      MaintenanceOwnerFrame.Guard mutation =
                          () -> {
                            environment.check();
                            require(manifests.findCleanupClaims(request).equals(manifest));
                            artifacts.verify(manifest);
                            require(
                                reader.readCleanupRequest().equals(request)
                                    && reader.readMaintenanceOwner().equals(owner));
                            return environment.remainingNanos();
                          };
                      mutation.check();
                      int result =
                          new CleanupMaintenanceWork(context, expected, owner, mutation)
                              .execute(connection);
                      mutation.check();
                      return result;
                    });
              });
        });
  }

  /** Borrowed active transactions are never configured/committed; standalone reads roll back. */
  private static void verifyFailedPair(
      java.sql.Connection connection,
      BackupFailureSnapshot failure,
      MaintenanceOwnerFrame.Guard base)
      throws IOException {
    try {
      boolean own = connection.getAutoCommit();
      if (own) connection.setAutoCommit(false);
      new dev.codex.schubert.nk.batch.cleanup.MaintenanceMutationGuard(base).bind(connection);
      failure.verifyLatest(connection, base);
      if (own) {
        connection.rollback();
        connection.setAutoCommit(true);
      }
      base.check();
    } catch (java.sql.SQLException | BatchRepositoryException known) {
      StorageIoException.preserveFatal(known);
      throw new IOException("failed Backup DB observation unavailable");
    }
  }

  /** Root's read-only host capability cannot publish, repair, retire or bypass private writes. */
  @SuppressFBWarnings(
      value = "DMI_HARDCODED_ABSOLUTE_FILENAME",
      matchType = SuppressMatchType.EXACT,
      justification =
          "SS343 fixed current INVALID host observation, never an ordinary child capability")
  private static void verifyOriginalAndCurrent(
      RootStartupContext context, RootStartupContext.Snapshot expected, MaintenanceOwnerFrame owner)
      throws IOException {
    var activation =
        new MaintenanceActivation(new BatchRun(owner.run(), owner.cutoff()), owner.activation());
    require(MaintenanceRunFiles.observeHost(context, expected, activation).equals(activation));
    var startupCalls = LinuxHostDirectoryCalls.create();
    Path startupPath = Path.of("/run/schubert-nk/startup");
    ResourceScope.<OwnedTransferDirectory, Boolean, IOException>acquire(
        () -> OwnedTransferDirectory.open(startupCalls, startupPath),
        OwnedTransferDirectory::close,
        startup -> {
          var current = new StartupPermitFiles(startup, LinuxInodeSecurity.create()).current();
          require(
              current.state() == StartupPermitRecords.State.INVALID
                  && current.boot().equals(owner.boot())
                  && current.epoch().equals(owner.epoch())
                  && current.activation().equals(activation));
          context.recheck(expected);
          return Boolean.TRUE;
        });
  }
}
