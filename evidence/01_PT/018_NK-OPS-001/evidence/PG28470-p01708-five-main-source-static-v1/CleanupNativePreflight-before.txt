package dev.codex.schubert.nk.batch.file;

import dev.codex.schubert.nk.batch.backup.BackupManifest;
import dev.codex.schubert.nk.batch.platform.MaintenanceUnit;
import dev.codex.schubert.nk.batch.platform.MaintenanceUnitTermination;
import dev.codex.schubert.nk.batch.platform.RootReleaseAdmission;
import dev.codex.schubert.nk.batch.platform.RootStartupContext;
import dev.codex.schubert.nk.batch.platform.StopGateException;
import dev.codex.schubert.nk.batch.repository.CleanupDatabaseSession;
import dev.codex.schubert.nk.bootstrap.FixedServiceIdentity;
import dev.codex.schubert.nk.storage.DirectoryCalls;
import dev.codex.schubert.nk.storage.LinuxDirectoryCalls;
import dev.codex.schubert.nk.storage.LinuxInodeSecurity;
import dev.codex.schubert.nk.storage.OwnedTransferDirectory;
import dev.codex.schubert.nk.storage.ResourceScope;
import dev.codex.schubert.nk.storage.ServiceCredentialLocation;
import edu.umd.cs.findbugs.annotations.SuppressFBWarnings;
import edu.umd.cs.findbugs.annotations.SuppressMatchType;
import java.io.IOException;
import java.nio.file.Path;
import java.time.Clock;
import org.jspecify.annotations.NullMarked;

/**
 * Native, read-only Cleanup child wiring. The returned manifest is an observation, never DELETE
 * authority. The root parent, terminal actors, transfer and 0/10 outcome remain separate gates.
 * NK-OPS-001/NK-BAT-001; OPS009/BAK001/UI251/SS341/343/SSC104/PG334; PT-OPS-NCLEAN001 onward.
 */
@NullMarked
final class CleanupNativePreflight {
  @FunctionalInterface
  interface StopObservation {
    boolean quiescent(MaintenanceUnit unit) throws IOException;
  }

  private CleanupNativePreflight() {}

  @SuppressFBWarnings(
      value = "DMI_HARDCODED_ABSOLUTE_FILENAME",
      matchType = SuppressMatchType.EXACT,
      justification = "SS343/SSC104 fixed private Cleanup namespace and backup root; NCLEAN")
  static BackupManifest verify() throws IOException {
    RootStartupContext context = RootStartupContext.create();
    var snapshot = context.capture(RootStartupContext.Service.CLEANUP);
    applicationsStopped(context, snapshot);
    RootReleaseAdmission release = RootReleaseAdmission.create(context, snapshot);
    Path credentialPath;
    try {
      credentialPath = ServiceCredentialLocation.read(System.getenv()).directory();
    } catch (IllegalArgumentException invalid) {
      throw unavailable();
    }
    if (!credentialPath.equals(Path.of("/run/credentials/schubert-nk-cleanup.service")))
      throw unavailable();

    var calls = LinuxDirectoryCalls.create();
    var security = LinuxInodeSecurity.create();
    BackupManifest result =
        ResourceScope.<OwnedTransferDirectory, BackupManifest, IOException>acquire(
            () -> OwnedTransferDirectory.open(calls, credentialPath),
            OwnedTransferDirectory::close,
            credentials -> {
              var reader = new RootBatchCredentialReader(credentials, security);
              var identity = new FixedServiceIdentity().resolveBackup();
              return ResourceScope.<OwnedTransferDirectory, BackupManifest, IOException>acquire(
                  () -> openBackup(calls),
                  OwnedTransferDirectory::close,
                  backup -> {
                    var admission =
                        new CleanupBackupAdmission(
                            new BackupManifestReader(
                                backup, security, identity.uid(), identity.gid()),
                            new BackupArtifactVerifier(
                                backup, security, identity.uid(), identity.gid()));
                    var database =
                        new CleanupDatabaseSession(
                            "jdbc:postgresql://127.0.0.1:5432/schubert_nk",
                            context,
                            snapshot,
                            release);
                    return new CleanupPreflight(
                            () -> context.recheck(snapshot),
                            reader::readCleanupRequest,
                            request ->
                                MaintenanceRunFiles.observeHost(
                                    context,
                                    snapshot,
                                    new dev.codex.schubert.nk.batch.repository
                                        .MaintenanceActivation(
                                        new dev.codex.schubert.nk.batch.repository.BatchRun(
                                            request.run(), request.cutoff()),
                                        request.activation())),
                            (request, observedAt) ->
                                database.execute(
                                    reader.read(),
                                    connection ->
                                        admission.verify(request, observedAt, connection)),
                            Clock.systemUTC())
                        .verify();
                  });
            });
    context.recheck(snapshot); // No result until every borrowed root/DB owner has closed.
    applicationsStopped(context, snapshot);
    return result;
  }

  private static void applicationsStopped(
      RootStartupContext context, RootStartupContext.Snapshot snapshot) throws IOException {
    requireApplicationsStopped(
        unit ->
            MaintenanceUnitTermination.createCleanup(context, snapshot, unit)
                .quiescent()
                .isPresent());
  }

  static void requireApplicationsStopped(StopObservation observation) throws IOException {
    java.util.Objects.requireNonNull(observation, "fixed child stop observation");
    try {
      for (MaintenanceUnit unit :
          new MaintenanceUnit[] {MaintenanceUnit.WEB, MaintenanceUnit.API}) {
        if (!observation.quiescent(unit)) throw unavailable();
      }
    } catch (StopGateException known) {
      throw unavailable();
    }
  }

  @SuppressFBWarnings(
      value = "DMI_HARDCODED_ABSOLUTE_FILENAME",
      matchType = SuppressMatchType.EXACT,
      justification = "SS343/SSC104 fixed backup root; caller may not choose an alternate path")
  private static OwnedTransferDirectory openBackup(DirectoryCalls calls) throws IOException {
    return OwnedTransferDirectory.open(calls, Path.of("/srv/schubert-nk/backup"));
  }

  private static IOException unavailable() {
    return new IOException("root cleanup preflight unavailable");
  }
}
