package dev.codex.schubert.nk.batch.file;

import static dev.codex.schubert.nk.batch.file.EnvironmentInodePolicy.require;
import static dev.codex.schubert.nk.batch.file.EnvironmentInodePolicy.unavailable;

import dev.codex.schubert.nk.batch.backup.BackupManifest;
import dev.codex.schubert.nk.batch.file.EnvironmentInodePolicy.Metadata;
import dev.codex.schubert.nk.batch.repository.BatchStepAttempt;
import dev.codex.schubert.nk.storage.InodeSecurityCalls;
import dev.codex.schubert.nk.storage.OwnedTransferDirectory;
import dev.codex.schubert.nk.storage.ResourceScope;
import dev.codex.schubert.nk.storage.StorageIoException;
import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.channels.FileChannel;
import java.nio.channels.SeekableByteChannel;
import java.nio.file.*;
import java.nio.file.attribute.FileTime;
import java.util.*;
import java.util.function.LongSupplier;
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;

/**
 * Root-owned claims at this observation, not generation, archive validation or DB success.
 * NK-BAT-001/BAK/BKO/OPS009/UI251/SS341 6.7/343 5.3; SSC062/PG169; BAT226..241. Caller retains
 * admitted backup root, OS exclusion and authoritative complete handles.
 */
@NullMarked
public final class BackupManifestReader {
  private static final String NAME = "MANIFEST.json";
  private static final long DEADLINE = 1_800_000_000_000L;
  private final Object lock = new Object();
  private final OwnedTransferDirectory root;
  private final InodeSecurityCalls security;
  private final long uid, gid;
  private final Io io;
  private final LongSupplier clock;

  interface Io {
    @Nullable Map<String, Object> attributes(Path held) throws IOException;

    @Nullable SeekableByteChannel open(Path held) throws IOException;
  }

  public BackupManifestReader(
      OwnedTransferDirectory root, InodeSecurityCalls security, long uid, long gid) {
    this(root, security, uid, gid, new NioIo(), System::nanoTime);
  }

  BackupManifestReader(
      OwnedTransferDirectory root,
      InodeSecurityCalls security,
      long uid,
      long gid,
      Io io,
      LongSupplier clock) {
    this.root = Objects.requireNonNull(root, "backup root");
    this.security = Objects.requireNonNull(security, "inode security");
    this.io = Objects.requireNonNull(io, "manifest IO");
    this.clock = Objects.requireNonNull(clock, "manifest clock");
    if (uid < 1 || uid > 0xffffffffL || gid < 1 || gid > 0xffffffffL)
      throw new IllegalArgumentException("invalid backup owner");
    this.uid = uid;
    this.gid = gid;
  }

  public BackupManifest read(String name, BatchStepAttempt database, BatchStepAttempt configuration)
      throws StorageIoException {
    return readAt(name, database, configuration, null);
  }

  /** Same operation-wide monotonic budget supplied by the package publisher. SSC066/BAT258..273. */
  BackupManifest readWithin(
      String name, BatchStepAttempt database, BatchStepAttempt configuration, long started)
      throws StorageIoException {
    return readAt(name, database, configuration, started);
  }

  private BackupManifest readAt(
      String name,
      BatchStepAttempt database,
      BatchStepAttempt configuration,
      @Nullable Long suppliedStart)
      throws StorageIoException {
    Objects.requireNonNull(name, "backup directory name");
    Objects.requireNonNull(database, "database handle");
    Objects.requireNonNull(configuration, "configuration handle");
    require(
        name.length() == 52
            && name.matches(
                "[0-9]{8}-[0-9]{6}-[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"));
    synchronized (lock) {
      long started = suppliedStart == null ? clock.getAsLong() : suppliedStart;
      byte[] bytes = new byte[4097];
      try {
        guard(started);
        require(security.effectiveUid() == 0);
        guard(started);
        Metadata parent = directory(root, started);
        guard(started);
        var child = root.openExistingChild(name);
        Metadata original =
            ResourceScope.use(
                child::close,
                () -> {
                  Metadata initial = directory(child, started);
                  require(initial.device() == parent.device());
                  guard(started);
                  Metadata observed =
                      child.atExistingEntryHandle(
                          NAME,
                          held -> {
                            Metadata before = capture(held, false, started);
                            require(before.device() == initial.device());
                            readFile(held, before.size(), bytes, started);
                            require(before.equals(capture(held, false, started)));
                            return before;
                          });
                  guard(started);
                  require(
                      child.atExistingEntryHandle(
                          NAME, held -> observed.equals(capture(held, false, started))));
                  guard(started);
                  require(initial.equals(directory(child, started)));
                  guard(started);
                  var rebound = root.openExistingChild(name);
                  ResourceScope.use(
                      rebound::close,
                      () -> {
                        require(initial.equals(directory(rebound, started)));
                        return Boolean.TRUE;
                      });
                  guard(started);
                  return observed;
                });
        guard(started);
        require(parent.equals(directory(root, started)));
        BackupManifest result = decode(bytes, (int) original.size());
        require(
            result.directoryName().equals(name)
                && result.databaseStep().equals(database)
                && result.configurationStep().equals(configuration));
        guard(started);
        require(security.effectiveUid() == 0);
        guard(started);
        return result;
      } catch (IOException | DirectoryIteratorException | UnsupportedOperationException failure) {
        throw unavailable();
      } finally {
        Arrays.fill(bytes, (byte) 0);
      }
    }
  }

  private Metadata directory(OwnedTransferDirectory directory, long started)
      throws StorageIoException {
    guard(started);
    Metadata value = directory.atDirectory(held -> capture(held, true, started));
    guard(started);
    return value;
  }

  private Metadata capture(Path held, boolean directory, long started) throws IOException {
    guard(started);
    Metadata value = metadata(io.attributes(held));
    guard(started);
    require(
        value.mode() == (directory ? 040700 : 0100600)
            && value.uid() == (directory ? uid : 0)
            && value.gid() == (directory ? gid : 0));
    if (directory) require(value.links() >= 2 && value.size() >= 0);
    else require(value.links() == 1 && value.size() >= 1 && value.size() <= 4096);
    byte[] acl = security.accessAcl(held, 44);
    guard(started);
    require(acl != null && acl.length == 0);
    require(!security.readOnlyFilesystem(held));
    guard(started);
    return value;
  }

  private void readFile(Path held, long expected, byte[] bytes, long started) throws IOException {
    guard(started);
    SeekableByteChannel opened = io.open(held);
    if (opened == null) throw unavailable();
    ResourceScope.use(
        opened,
        () -> {
          guard(started);
          require(opened.size() == expected);
          guard(started);
          ByteBuffer buffer = ByteBuffer.wrap(bytes);
          buffer.limit((int) expected);
          while (buffer.hasRemaining()) {
            int position = buffer.position(), remaining = buffer.remaining();
            guard(started);
            int read = opened.read(buffer);
            guard(started);
            require(read > 0 && read <= remaining && buffer.position() == position + read);
          }
          buffer.limit((int) expected + 1);
          guard(started);
          require(opened.read(buffer) == -1 && buffer.position() == expected);
          guard(started);
          require(opened.size() == expected);
          guard(started);
          return Boolean.TRUE;
        });
    guard(started);
  }

  private static BackupManifest decode(byte[] bytes, int size) throws StorageIoException {
    byte[] content = Arrays.copyOf(bytes, size);
    try {
      return BackupManifestCodec.decode(content);
    } catch (IllegalArgumentException malformed) {
      throw unavailable();
    } finally {
      Arrays.fill(content, (byte) 0);
    }
  }

  private static Metadata metadata(@Nullable Map<String, Object> values) throws StorageIoException {
    if (values == null
        || !(values.get("mode") instanceof Integer mode)
        || !(values.get("uid") instanceof Integer owner)
        || !(values.get("gid") instanceof Integer group)
        || !(values.get("nlink") instanceof Integer links)
        || !(values.get("size") instanceof Long size)
        || !(values.get("dev") instanceof Long device)
        || !(values.get("ino") instanceof Long inode)
        || !(values.get("lastModifiedTime") instanceof FileTime modified)
        || !(values.get("ctime") instanceof FileTime changed)) throw unavailable();
    return new Metadata(
        mode,
        Integer.toUnsignedLong(owner),
        Integer.toUnsignedLong(group),
        links,
        size,
        device,
        inode,
        modified,
        changed);
  }

  private void guard(long started) throws StorageIoException {
    if (Thread.currentThread().isInterrupted()) throw unavailable();
    long elapsed = clock.getAsLong() - started;
    if (Thread.currentThread().isInterrupted()) throw unavailable();
    require(elapsed >= 0 && elapsed < DEADLINE);
  }

  static final class NioIo implements Io {
    @Override
    public Map<String, Object> attributes(Path held) throws IOException {
      return Files.readAttributes(
          held, "unix:mode,uid,gid,nlink,size,dev,ino,lastModifiedTime,ctime");
    }

    @Override
    public SeekableByteChannel open(Path held) throws IOException {
      return FileChannel.open(held, StandardOpenOption.READ);
    }
  }
}
