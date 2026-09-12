package dev.codex.schubert.nk.batch.file;

import dev.codex.schubert.nk.batch.platform.InspectorRunEnvironment;
import dev.codex.schubert.nk.batch.platform.InspectorStaticEnvironment;
import dev.codex.schubert.nk.batch.repository.BatchRun;
import dev.codex.schubert.nk.storage.InodeSecurityCalls;
import dev.codex.schubert.nk.storage.OwnedTransferDirectory;
import dev.codex.schubert.nk.storage.StorageIoException;
import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.channels.FileChannel;
import java.nio.channels.SeekableByteChannel;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.nio.file.attribute.FileTime;
import java.util.Arrays;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;

/**
 * Read-only, borrowed retained root; no path choice, repair, publication or child execution.
 * NK-OPS-001; OPS-009/UI251/SS311/343 6.9; SSC-049/PG-D-152; PT-OPS-EFILE-001..008. Caller owns the
 * fixed namespace, root lifetime, OS lock and trusted account-to-GID resolution.
 */
@NullMarked
public final class InspectorEnvironmentReader {
  private static final String NAME = "inbox-inspector.env";
  private static final Set<String> LOCAL = Set.of("ext2", "ext3", "ext4", "xfs", "btrfs", "tmpfs");
  private final OwnedTransferDirectory root;
  private final InodeSecurityCalls security;
  private final long configGroup;
  private final Io io;

  interface Io {
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
  }

  /** Returns caller-owned validated bytes, not a promise of future namespace stability. */
  public byte[] readStatic() throws StorageIoException {
    byte[] bytes = read(false);
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
    Objects.requireNonNull(run, "run");
    byte[] bytes = read(true);
    try {
      InspectorRunEnvironment.requireMatches(run, bytes);
      return bytes;
    } catch (IllegalArgumentException failure) {
      Arrays.fill(bytes, (byte) 0);
      throw failure;
    }
  }

  private byte[] read(boolean runtime) throws StorageIoException {
    require(!Thread.currentThread().isInterrupted());
    require(security.effectiveUid() == 0);
    int maximum = runtime ? 110 : InspectorStaticEnvironment.MAXIMUM_BYTES;
    byte[] bytes = new byte[maximum + 1];
    try {
      Snapshot directory = root.atDirectory(p -> snapshot(p, runtime, true, maximum));
      Snapshot original =
          root.atExistingEntryHandle(
              NAME,
              held -> {
                Snapshot before = snapshot(held, runtime, false, maximum);
                require(before.metadata().device() == directory.metadata().device());
                readFile(held, before.metadata().size(), bytes);
                require(before.equals(snapshot(held, runtime, false, maximum)));
                return before;
              });
      require(
          root.atExistingEntryHandle(
              NAME, p -> original.equals(snapshot(p, runtime, false, maximum))));
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
    try (var channel = io.open(held)) {
      if (channel == null) throw unavailable();
      require(channel.size() == expected);
      while (buffer.hasRemaining()) {
        int position = buffer.position(), remaining = buffer.remaining();
        int count = channel.read(buffer);
        if (count == -1) break;
        require(count > 0 && count <= remaining && buffer.position() == position + count);
      }
      require(buffer.position() == expected);
      require(channel.size() == expected);
    }
  }

  private Snapshot snapshot(Path held, boolean runtime, boolean directory, int maximum)
      throws IOException {
    Metadata m = metadata(io.attributes(held));
    int mode = directory ? (runtime ? 040700 : 040750) : (runtime ? 0100600 : 0100640);
    require(m.mode() == mode && m.uid() == 0 && m.gid() == (runtime ? 0 : configGroup));
    if (directory) require(m.links() >= 2 && m.size() >= 0);
    else require(m.links() == 1 && m.size() >= 1 && m.size() <= maximum);
    // Exact inode type/mode is established before any procfd-following xattr or filesystem call.
    byte[] acl = security.accessAcl(held, 44);
    require(acl != null && acl.length == 0);
    String filesystem = io.filesystem(held);
    if (filesystem == null) throw unavailable();
    boolean readonly = security.readOnlyFilesystem(held);
    if (runtime) require(filesystem.equals("tmpfs") && !readonly);
    else require(LOCAL.contains(filesystem));
    return new Snapshot(m, filesystem, readonly);
  }

  private static Metadata metadata(@Nullable Map<String, Object> values) throws StorageIoException {
    if (values == null
        || !(values.get("mode") instanceof Integer mode)
        || !(values.get("uid") instanceof Integer uid)
        || !(values.get("gid") instanceof Integer gid)
        || !(values.get("nlink") instanceof Integer links)
        || !(values.get("size") instanceof Long size)
        || !(values.get("dev") instanceof Long device)
        || !(values.get("ino") instanceof Long inode)
        || !(values.get("lastModifiedTime") instanceof FileTime modified)
        || !(values.get("ctime") instanceof FileTime changed)) throw unavailable();
    return new Metadata(
        mode,
        Integer.toUnsignedLong(uid),
        Integer.toUnsignedLong(gid),
        links,
        size,
        device,
        inode,
        modified,
        changed);
  }

  private static void require(boolean accepted) throws StorageIoException {
    if (!accepted) throw unavailable();
  }

  private static StorageIoException unavailable() {
    return new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
  }

  private record Metadata(
      int mode,
      long uid,
      long gid,
      int links,
      long size,
      long device,
      long inode,
      FileTime modified,
      FileTime changed) {}

  private record Snapshot(Metadata metadata, String filesystem, boolean readonly) {}

  static final class NioIo implements Io {
    @Override
    public Map<String, Object> attributes(Path held) throws IOException {
      return Files.readAttributes(
          held, "unix:mode,uid,gid,nlink,size,dev,ino,lastModifiedTime,ctime");
    }

    @Override
    public String filesystem(Path held) throws IOException {
      return Files.getFileStore(held).type();
    }

    @Override
    public SeekableByteChannel open(Path held) throws IOException {
      return FileChannel.open(held, StandardOpenOption.READ);
    }
  }
}
