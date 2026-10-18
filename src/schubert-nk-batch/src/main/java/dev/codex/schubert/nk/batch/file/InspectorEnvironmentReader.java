package dev.codex.schubert.nk.batch.file;

import dev.codex.schubert.nk.batch.file.EnvironmentInodePolicy.Snapshot;
import dev.codex.schubert.nk.batch.platform.InspectorRunEnvironment;
import dev.codex.schubert.nk.batch.platform.InspectorStaticEnvironment;
import dev.codex.schubert.nk.batch.repository.BatchRun;
import dev.codex.schubert.nk.storage.InodeSecurityCalls;
import dev.codex.schubert.nk.storage.OwnedTransferDirectory;
import dev.codex.schubert.nk.storage.ResourceScope;
import dev.codex.schubert.nk.storage.StorageIoException;
import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.channels.FileChannel;
import java.nio.channels.SeekableByteChannel;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.util.Arrays;
import java.util.Map;
import java.util.Objects;
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;

/**
 * SSC063/PG171/BUG195/YKT154: explicit close precedence; 017049 compound PT supplement. Read-only,
 * borrowed retained root; no path choice, repair, publication or child execution. NK-OPS-001;
 * OPS-009/UI251/SS311/343 6.9; SSC-049/PG-D-152; PT-OPS-EFILE-001..008. Caller owns the fixed
 * namespace, root lifetime, OS lock and trusted account-to-GID resolution.
 */
@NullMarked
public final class InspectorEnvironmentReader {
  private static final String NAME = "inbox-inspector.env";
  private final OwnedTransferDirectory root;
  private final InodeSecurityCalls security;
  private final long configGroup;
  private final Io io;
  private final EnvironmentInodePolicy policy;

  interface Io extends EnvironmentInodePolicy.Source {
    @Nullable Map<String, Object> attributes(Path held) throws IOException;

    @Nullable String filesystem(Path held) throws IOException;

    @Nullable SeekableByteChannel open(Path held) throws IOException;
  }

  public InspectorEnvironmentReader(
      OwnedTransferDirectory root, InodeSecurityCalls security, long configGroup) {
    this(root, security, configGroup, new NioIo());
  }

  InspectorEnvironmentReader(
      OwnedTransferDirectory root, InodeSecurityCalls security, long configGroup, Io io) {
    this.root = Objects.requireNonNull(root, "environment root");
    this.security = Objects.requireNonNull(security, "inode security");
    this.io = Objects.requireNonNull(io, "environment IO");
    if (configGroup < 1 || configGroup > 0xffff_ffffL)
      throw new IllegalArgumentException("configuration group is invalid");
    this.configGroup = configGroup;
    this.policy = new EnvironmentInodePolicy(security, io);
  }

  /** Returns caller-owned validated bytes, not a promise of future namespace stability. */
  public byte[] readStatic() throws StorageIoException {
    byte[] bytes = read(false, NAME);
    try {
      InspectorStaticEnvironment.requireValid(bytes);
      return bytes;
    } catch (IllegalArgumentException failure) {
      Arrays.fill(bytes, (byte) 0);
      throw failure;
    }
  }

  /** Uses the caller's authoritative run; never chooses a new identity or cutoff. */
  public byte[] readRun(BatchRun run) throws StorageIoException {
    return readRunAt(run, NAME);
  }

  /** Package-only publisher readback of its admitted single-segment part or fixed target. */
  byte[] readRunAt(BatchRun run, String name) throws StorageIoException {
    Objects.requireNonNull(run, "run");
    byte[] bytes = read(true, name);
    try {
      InspectorRunEnvironment.requireMatches(run, bytes);
      return bytes;
    } catch (IllegalArgumentException failure) {
      Arrays.fill(bytes, (byte) 0);
      throw failure;
    }
  }

  private byte[] read(boolean runtime, String name) throws StorageIoException {
    require(!Thread.currentThread().isInterrupted());
    require(security.effectiveUid() == 0);
    int maximum = runtime ? 110 : InspectorStaticEnvironment.MAXIMUM_BYTES;
    byte[] bytes = new byte[maximum + 1];
    try {
      Snapshot directory = root.atDirectory(p -> snapshot(p, runtime, true, maximum));
      Snapshot original =
          root.atExistingEntryHandle(
              name,
              held -> {
                Snapshot before = snapshot(held, runtime, false, maximum);
                require(before.metadata().device() == directory.metadata().device());
                readFile(held, before.metadata().size(), bytes);
                require(before.equals(snapshot(held, runtime, false, maximum)));
                return before;
              });
      require(
          root.atExistingEntryHandle(
              name, p -> original.equals(snapshot(p, runtime, false, maximum))));
      require(directory.equals(root.atDirectory(p -> snapshot(p, runtime, true, maximum))));
      require(!Thread.currentThread().isInterrupted());
      return Arrays.copyOf(bytes, (int) original.metadata().size());
    } catch (IOException failure) {
      // All owned channel/entry scopes have ended; discard even compound suppressed diagnostics.
      throw unavailable();
    } finally {
      Arrays.fill(bytes, (byte) 0);
    }
  }

  private void readFile(Path held, long expected, byte[] bytes) throws IOException {
    ByteBuffer buffer = ByteBuffer.wrap(bytes);
    ResourceScope.acquire(
        () -> {
          var channel = io.open(held);
          if (channel == null) throw unavailable();
          return channel;
        },
        SeekableByteChannel::close,
        channel -> {
          require(channel.size() == expected);
          while (buffer.hasRemaining()) {
            int position = buffer.position();
            int remaining = buffer.remaining();
            int count = channel.read(buffer);
            if (count == -1) break;
            require(count > 0 && count <= remaining && buffer.position() == position + count);
          }
          require(buffer.position() == expected);
          require(channel.size() == expected);

          return Boolean.TRUE;
        });
  }

  private Snapshot snapshot(Path held, boolean runtime, boolean directory, int maximum)
      throws IOException {
    return policy.snapshot(held, runtime, directory, maximum, 1, configGroup);
  }

  private static void require(boolean accepted) throws StorageIoException {
    if (!accepted) throw unavailable();
  }

  private static StorageIoException unavailable() {
    return new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
  }

  static final class NioIo implements Io {
    private final dev.codex.schubert.nk.storage.LinuxFilesystemClassifier retainedFilesystem =
        dev.codex.schubert.nk.storage.LinuxFilesystemClassifier.create();

    @Override
    public Map<String, Object> attributes(Path held) throws IOException {
      return Files.readAttributes(
          held, "unix:mode,uid,gid,nlink,size,dev,ino,lastModifiedTime,ctime");
    }

    @Override
    public String filesystem(Path held) throws IOException {
      return retainedFilesystem.filesystem(held);
    }

    @Override
    public SeekableByteChannel open(Path held) throws IOException {
      return FileChannel.open(held, StandardOpenOption.READ);
    }
  }
}
