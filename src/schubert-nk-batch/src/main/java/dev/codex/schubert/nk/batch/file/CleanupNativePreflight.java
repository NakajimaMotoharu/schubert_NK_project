package dev.codex.schubert.nk.batch.file;

import dev.codex.schubert.nk.batch.backup.BackupManifest;
import dev.codex.schubert.nk.batch.platform.RootReleaseAdmission;
import dev.codex.schubert.nk.batch.platform.RootStartupContext;
import dev.codex.schubert.nk.batch.repository.CleanupDatabaseSession;
import dev.codex.schubert.nk.bootstrap.FixedServiceIdentity;
import dev.codex.schubert.nk.storage.*;
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
  private CleanupNativePreflight() {}

  @SuppressFBWarnings(
      value = "DMI_HARDCODED_ABSOLUTE_FILENAME",
      matchType = SuppressMatchType.EXACT,
      justification = "SS343/SSC104 fixed private Cleanup namespace and backup root; NCLEAN")
  static BackupManifest verify() throws IOException {
    RootStartupContext context = RootStartupContext.create();
    var snapshot = context.capture(RootStartupContext.Service.CLEANUP);
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
    var credentials = OwnedTransferDirectory.open(calls, credentialPath);
    BackupManifest result =
        ResourceScope.use(
            credentials::close,
            () -> {
              var reader = new RootBatchCredentialReader(credentials, security);
              var identity = new FixedServiceIdentity().resolveBackup();
              var backup = openBackup(calls);
              return ResourceScope.use(
                  backup::close,
                  () -> {
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
                                MaintenanceRunFiles.create()
                                    .execute(session -> session.observeCleanup(request)),
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
    return result;
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
