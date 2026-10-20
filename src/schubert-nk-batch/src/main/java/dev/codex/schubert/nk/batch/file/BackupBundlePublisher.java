package dev.codex.schubert.nk.batch.file;

import static dev.codex.schubert.nk.batch.file.EnvironmentInodePolicy.require;
import static dev.codex.schubert.nk.batch.file.EnvironmentInodePolicy.unavailable;

import dev.codex.schubert.nk.batch.backup.BackupFileDigest;
import dev.codex.schubert.nk.batch.backup.BackupManifest;
import dev.codex.schubert.nk.batch.file.InspectorEnvironmentPublisher.Writer;
import dev.codex.schubert.nk.storage.InodeSecurityCalls;
import dev.codex.schubert.nk.storage.OwnedTransferDirectory;
import dev.codex.schubert.nk.storage.ResourceScope;
import dev.codex.schubert.nk.storage.StorageIoException;
import java.io.IOException;
import java.nio.channels.SeekableByteChannel;
import java.nio.file.DirectoryStream;
import java.nio.file.Path;
import java.security.MessageDigest;
import java.util.Map;
import java.util.Objects;
import java.util.function.LongSupplier;
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;

/**
 * Durable publication and final revalidation only; not archive generation, DB success or retention.
 * NK-BAT-001/BAK/BKO/OPS009/UI251/SS341 6.10/333 7.5/343; SSC066/PG177; BAT258..273. Caller retains
 * admitted root, continuous exclusion, stopped actors and trusted closed archives.
 */
@NullMarked
public final class BackupBundlePublisher {
  private static final long DEADLINE = 1_800_000_000_000L;
  private final java.util.concurrent.locks.ReentrantLock lock =
      new java.util.concurrent.locks.ReentrantLock();
  private final OwnedTransferDirectory root;
  private final BackupArtifactVerifier verifier;
  private final BackupManifestReader reader;
  private final Io io;
  private final LongSupplier clock;

  interface Io extends BackupArtifactVerifier.Io, BackupManifestReader.Io {
    @Nullable Writer openWriter(Path held) throws IOException;
  }

  public BackupBundlePublisher(
      OwnedTransferDirectory root, InodeSecurityCalls security, long uid, long gid) {
    this(root, security, uid, gid, new NioIo(), System::nanoTime);
  }

  BackupBundlePublisher(
      OwnedTransferDirectory root,
      InodeSecurityCalls security,
      long uid,
      long gid,
      Io io,
      LongSupplier clock) {
    this(root, security, uid, gid, io, clock, () -> MessageDigest.getInstance("SHA-256"));
  }

  BackupBundlePublisher(
      OwnedTransferDirectory root,
      InodeSecurityCalls security,
      long uid,
      long gid,
      Io io,
      LongSupplier clock,
      BackupArtifactVerifier.Digests digests) {
    this.root = Objects.requireNonNull(root, "backup root");
    this.io = Objects.requireNonNull(io, "bundle IO");
    this.clock = Objects.requireNonNull(clock, "bundle clock");
    verifier = new BackupArtifactVerifier(root, security, uid, gid, io, digests, clock);
    reader = new BackupManifestReader(root, security, uid, gid, io, clock);
  }

  /** All failures preserve the pending or published bundle; no implicit retry or DB commit. */
  public BackupFileDigest publish(BackupManifest trusted) throws StorageIoException {
    Objects.requireNonNull(trusted, "trusted manifest");
    lock.lock();
    try {
      long started = clock.getAsLong();
      guard(started);
      var before =
          verifier.forcePending(trusted, (held, size) -> force(held, size, started), started);
      guard(started);
      root.publishChild(trusted.directoryName() + ".part", trusted.directoryName());
      guard(started);
      BackupManifest actual =
          reader.readWithin(
              trusted.directoryName(),
              trusted.databaseStep(),
              trusted.configurationStep(),
              started);
      guard(started);
      require(trusted.equals(actual));
      var after = verifier.verifyWithin(actual, started);
      guard(started);
      require(before.samePublished(after));
      guard(started);
      return after.manifest();
    } finally {
      lock.unlock();
    }
  }

  private void force(Path held, long expected, long started) throws IOException {
    guard(started);
    ResourceScope.acquire(
        () -> {
          var writer = io.openWriter(held);
          if (writer == null) throw unavailable();
          return writer;
        },
        Writer::close,
        writer -> {
          guard(started);
          require(writer.size() == expected);
          guard(started);
          writer.force();
          guard(started);
          require(writer.size() == expected);
          guard(started);
          return Boolean.TRUE;
        });
    guard(started);
  }

  private void guard(long started) throws StorageIoException {
    if (Thread.currentThread().isInterrupted()) throw unavailable();
    long elapsed = clock.getAsLong() - started;
    if (Thread.currentThread().isInterrupted()) throw unavailable();
    require(elapsed >= 0 && elapsed < DEADLINE);
  }

  static final class NioIo implements Io {
    private final BackupArtifactVerifier.NioIo read = new BackupArtifactVerifier.NioIo();
    private final InspectorEnvironmentPublisher.NioIo write =
        new InspectorEnvironmentPublisher.NioIo();

    @Override
    public Map<String, Object> attributes(Path held) throws IOException {
      return read.attributes(held);
    }

    @Override
    public SeekableByteChannel open(Path held) throws IOException {
      return read.open(held);
    }

    @Override
    public DirectoryStream<Path> openNames(Path held) throws IOException {
      return read.openNames(held);
    }

    @Override
    public Writer openWriter(Path held) throws IOException {
      return write.openWriter(held);
    }
  }
}
