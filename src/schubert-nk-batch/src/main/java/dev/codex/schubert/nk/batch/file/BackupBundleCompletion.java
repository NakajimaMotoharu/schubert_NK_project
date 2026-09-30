package dev.codex.schubert.nk.batch.file;

import static dev.codex.schubert.nk.batch.file.EnvironmentInodePolicy.require;
import static dev.codex.schubert.nk.batch.file.EnvironmentInodePolicy.unavailable;

import dev.codex.schubert.nk.batch.backup.BackupCommitService;
import dev.codex.schubert.nk.batch.repository.BackupStepRepository;
import dev.codex.schubert.nk.batch.repository.BatchRepositoryException;
import dev.codex.schubert.nk.batch.repository.BatchStepAttempt;
import dev.codex.schubert.nk.storage.InodeSecurityCalls;
import dev.codex.schubert.nk.storage.OwnedTransferDirectory;
import dev.codex.schubert.nk.storage.StorageIoException;
import java.sql.Connection;
import java.sql.SQLException;
import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.Objects;
import java.util.function.LongSupplier;
import java.util.function.Supplier;
import org.jspecify.annotations.NullMarked;

/**
 * Root-authenticated files before atomic DB completion. Caller retains continuous OS exclusion,
 * stopped actors, authoritative handles and sole connection ownership; dispose connection on
 * failure. NK-BAT-001/BAK001..008/BKO001..008/OPS009/UI251/SS341 6.11/332/343; SSC067/PG184;
 * BAT274..281.
 */
@NullMarked
public final class BackupBundleCompletion {
  private static final long DEADLINE = 1_800_000_000_000L;
  private final Object lock = new Object();
  private final BackupManifestReader reader;
  private final BackupArtifactVerifier verifier;
  private final BackupCommitService commits;
  private final LongSupplier clock;
  private final Supplier<Instant> wall;

  public BackupBundleCompletion(
      OwnedTransferDirectory root, InodeSecurityCalls security, long uid, long gid) {
    this(
        new BackupManifestReader(root, security, uid, gid),
        new BackupArtifactVerifier(root, security, uid, gid),
        new BackupCommitService(),
        System::nanoTime,
        Instant::now);
  }

  BackupBundleCompletion(
      BackupManifestReader reader,
      BackupArtifactVerifier verifier,
      BackupCommitService commits,
      LongSupplier clock,
      Supplier<Instant> wall) {
    this.reader = Objects.requireNonNull(reader, "root manifest reader");
    this.verifier = Objects.requireNonNull(verifier, "backup artifact verifier");
    this.commits = Objects.requireNonNull(commits, "backup completion transaction");
    this.clock = Objects.requireNonNull(clock, "completion clock");
    this.wall = Objects.requireNonNull(wall, "completion wall clock");
  }

  public Instant complete(
      Connection parent, String name, BatchStepAttempt database, BatchStepAttempt configuration)
      throws StorageIoException {
    Objects.requireNonNull(parent, "parent connection");
    Objects.requireNonNull(name, "backup directory name");
    Objects.requireNonNull(database, "database handle");
    Objects.requireNonNull(configuration, "configuration handle");
    synchronized (lock) {
      long started = clock.getAsLong();
      guard(started);
      var manifest = reader.readWithin(name, database, configuration, started);
      guard(started);
      verifier.verifyWithin(manifest, started);
      guard(started);
      Instant ended =
          Objects.requireNonNull(wall.get(), "completion observation")
              .truncatedTo(ChronoUnit.MICROS);
      guard(started);
      Instant stored = commits.complete(parent, manifest, ended);
      // Read in a new transaction on the SAME owner connection after commit. A failure here
      // does not undo the committed pair: the caller must dispose/isolate, never claim SUCCESS.
      try {
        parent.setAutoCommit(false);
        if (!new BackupStepRepository(parent)
            .inspect(manifest, ended)
            .equals(java.util.Optional.of(stored))) throw new BatchRepositoryException();
        parent.rollback(); // Readback only; never a rollback claim for the prior write commit.
        parent.setAutoCommit(true);
      } catch (SQLException failure) {
        throw new BatchRepositoryException();
      }
      // This can fail after commit. Never claim rollback; a retry must revalidate the files.
      guard(started);
      return stored;
    }
  }

  private void guard(long started) throws StorageIoException {
    if (Thread.currentThread().isInterrupted()) throw unavailable();
    long elapsed = clock.getAsLong() - started;
    if (Thread.currentThread().isInterrupted()) throw unavailable();
    require(elapsed >= 0 && elapsed < DEADLINE);
  }
}
