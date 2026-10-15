package dev.codex.schubert.nk.batch.file;

import dev.codex.schubert.nk.batch.platform.BackupWorkerRequest;
import dev.codex.schubert.nk.batch.platform.MorningParentBudget;
import dev.codex.schubert.nk.batch.platform.RootStartupContext;
import dev.codex.schubert.nk.batch.repository.MorningDatabaseSession;
import dev.codex.schubert.nk.storage.LinuxHostDirectoryCalls;
import dev.codex.schubert.nk.storage.LinuxInodeSecurity;
import dev.codex.schubert.nk.storage.OwnedTransferDirectory;
import dev.codex.schubert.nk.storage.ResourceScope;
import edu.umd.cs.findbugs.annotations.SuppressFBWarnings;
import edu.umd.cs.findbugs.annotations.SuppressMatchType;
import java.io.IOException;
import java.nio.file.Path;
import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.Objects;
import java.util.Optional;
import org.jspecify.annotations.NullMarked;

/**
 * SSC116/BUG350: retained root owner across genuine child verification, never a receipt producer.
 */
@NullMarked
final class MorningBackupReuse {
  @FunctionalInterface
  interface Continuation<T> {
    T execute(
        BackupWorkerRequest request,
        MorningDatabaseSession.BackupBegins current,
        MorningProcessMain.Archive completion)
        throws IOException;
  }

  private MorningBackupReuse() {}

  @SuppressFBWarnings(
      value = "DMI_HARDCODED_ABSOLUTE_FILENAME",
      matchType = SuppressMatchType.EXACT,
      justification = "SS343 fixed retained backup root; BRESUME-VM001 real native coverage")
  static <T> T execute(
      RootStartupContext context,
      RootStartupContext.Snapshot expected,
      MorningParentBudget budget,
      MorningDatabaseSession.Access database,
      MorningDatabaseSession.BackupBegins prior,
      Continuation<T> work)
      throws IOException {
    Objects.requireNonNull(context);
    Objects.requireNonNull(expected);
    Objects.requireNonNull(budget);
    Objects.requireNonNull(database);
    Objects.requireNonNull(prior);
    Objects.requireNonNull(work);
    budget.requireWithin();
    context.recheck(expected);
    var identity = new dev.codex.schubert.nk.bootstrap.FixedServiceIdentity().resolveBackup();
    var root =
        OwnedTransferDirectory.open(
            LinuxHostDirectoryCalls.create(), Path.of("/srv/schubert-nk/backup"));
    return ResourceScope.use(
        root::close,
        () -> {
          long started = System.nanoTime();
          var reader =
              new BackupManifestReader(
                  root, LinuxInodeSecurity.create(), identity.uid(), identity.gid());
          var verifier =
              new BackupArtifactVerifier(
                  root, LinuxInodeSecurity.create(), identity.uid(), identity.gid());
          String name =
              new BackupWorkerRequest(prior.database().run().id(), prior.database().startedAt())
                  .directoryName();
          var manifest = reader.read(name, prior.database(), prior.configuration());
          var held = verifier.verifyWithin(manifest, started);
          budget.requireWithin();
          context.recheck(expected);
          var current =
              database.beginResumeBackup(manifest, Instant.now().truncatedTo(ChronoUnit.MICROS));
          var request =
              new BackupWorkerRequest(
                  manifest.run().id(),
                  manifest.startedAt(),
                  Optional.of(
                      new BackupWorkerRequest.Verification(
                          held.manifest().sha256(),
                          manifest.dump().size(),
                          manifest.dump().sha256())));
          return Objects.requireNonNull(
              work.execute(
                  request,
                  current,
                  MorningProcessMain.archive(
                      () -> {
                        budget.requireWithin();
                        context.recheck(expected);
                        EnvironmentInodePolicy.require(
                            manifest.equals(
                                reader.read(name, prior.database(), prior.configuration())));
                        EnvironmentInodePolicy.require(
                            held.equals(verifier.verifyWithin(manifest, started)));
                        database.completeReusedBackup(
                            current, manifest, Instant.now().truncatedTo(ChronoUnit.MICROS));
                        budget.requireWithin();
                        context.recheck(expected);
                        return manifest;
                      })),
              "real reuse continuation");
        });
  }
}
