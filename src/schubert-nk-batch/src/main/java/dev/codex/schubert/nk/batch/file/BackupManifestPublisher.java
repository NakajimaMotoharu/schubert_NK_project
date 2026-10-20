package dev.codex.schubert.nk.batch.file;

import static dev.codex.schubert.nk.batch.file.EnvironmentInodePolicy.require;
import static dev.codex.schubert.nk.batch.file.EnvironmentInodePolicy.unavailable;

import dev.codex.schubert.nk.batch.backup.BackupManifest;
import dev.codex.schubert.nk.batch.file.EnvironmentInodePolicy.Metadata;
import dev.codex.schubert.nk.storage.InodeSecurityCalls;
import dev.codex.schubert.nk.storage.OwnedTransferDirectory;
import dev.codex.schubert.nk.storage.ResourceScope;
import dev.codex.schubert.nk.storage.StorageIoException;
import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.file.Path;
import java.nio.file.attribute.FileTime;
import java.util.Arrays;
import java.util.Map;
import java.util.Objects;
import java.util.UUID;
import java.util.function.LongSupplier;
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;

/**
 * New-only root claim publication, not archive generation or backup success. NK-BAT-001;
 * BAK/BKO/OPS009/UI251/SS341 6.8/343 5.3; SSC064/PG175; PT-BAT-242..257. Caller retains admitted
 * root, continuous OS exclusion, stopped actors and independently verified archive claims.
 */
@NullMarked
public final class BackupManifestPublisher {
  private static final String NAME = "MANIFEST.json";
  private static final long DEADLINE = 1_800_000_000_000L;
  private final java.util.concurrent.locks.ReentrantLock lock =
      new java.util.concurrent.locks.ReentrantLock();
  private final OwnedTransferDirectory root;
  private final InodeSecurityCalls security;
  private final long uid;
  private final long gid;
  private final InspectorEnvironmentPublisher.Io io;
  private final LongSupplier clock;

  public BackupManifestPublisher(
      OwnedTransferDirectory root, InodeSecurityCalls security, long uid, long gid) {
    this(root, security, uid, gid, new InspectorEnvironmentPublisher.NioIo(), System::nanoTime);
  }

  BackupManifestPublisher(
      OwnedTransferDirectory root,
      InodeSecurityCalls security,
      long uid,
      long gid,
      InspectorEnvironmentPublisher.Io io,
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

  /** Failure preserves partial/published files; caller reconciles them, never this new-only API. */
  public void create(BackupManifest trusted, UUID partId) throws StorageIoException {
    Objects.requireNonNull(trusted, "trusted manifest");
    Objects.requireNonNull(partId, "part id");
    lock.lock();
    try {
      long started = clock.getAsLong();
      byte[] content = BackupManifestCodec.encode(trusted);
      byte[] readback = new byte[content.length + 1];
      try {
        guard(started);
        require(security.effectiveUid() == 0);
        guard(started);
        Metadata parent = directory(root, started);
        String name = trusted.directoryName() + ".part";
        guard(started);
        ResourceScope.acquire(
            () -> root.openExistingChild(name),
            OwnedTransferDirectory::close,
            child -> {
              Metadata initial = directory(child, started);
              require(initial.device() == parent.device());
              guard(started);
              Metadata written =
                  child.createPrivatePart(
                      partId,
                      held -> {
                        Metadata before = capture(held, false, started);
                        require(before.device() == initial.device() && before.size() == 0);
                        write(held, content, started);
                        Metadata after = capture(held, false, started);
                        require(identity(before, after));
                        require(after.size() == content.length);
                        return after;
                      });
              verify(child, partId + ".part", written, content, readback, started);
              guard(started);
              require(written.equals(child.atPartHandle(partId, p -> capture(p, false, started))));
              guard(started);
              child.publishAs(partId, NAME);
              guard(started);
              Metadata published =
                  child.atExistingEntryHandle(NAME, p -> capture(p, false, started));
              require(
                  identity(written, published)
                      && written.size() == published.size()
                      && written.modified().equals(published.modified()));
              verify(child, NAME, published, content, readback, started);
              guard(started);
              require(
                  published.equals(
                      child.atExistingEntryHandle(NAME, p -> capture(p, false, started))));
              Metadata finalChild = directory(child, started);
              require(identity(initial, finalChild));
              guard(started);
              ResourceScope.acquire(
                  () -> root.openExistingChild(name),
                  OwnedTransferDirectory::close,
                  rebound -> {
                    require(finalChild.equals(directory(rebound, started)));
                    return Boolean.TRUE;
                  });
              guard(started);
              return Boolean.TRUE;
            });
        guard(started);
        require(parent.equals(directory(root, started)));
        guard(started);
        require(security.effectiveUid() == 0);
        guard(started);
      } finally {
        Arrays.fill(content, (byte) 0);
        Arrays.fill(readback, (byte) 0);
      }
    } finally {
      lock.unlock();
    }
  }

  private void write(Path held, byte[] content, long started) throws IOException {
    guard(started);
    ResourceScope.acquire(
        () -> {
          var writer = io.openWriter(held);
          if (writer == null) throw unavailable();
          return writer;
        },
        InspectorEnvironmentPublisher.Writer::close,
        writer -> {
          guard(started);
          require(writer.size() == 0);
          guard(started);
          ByteBuffer buffer = ByteBuffer.wrap(content);
          while (buffer.hasRemaining()) {
            int position = buffer.position();
            int remaining = buffer.remaining();
            guard(started);
            int count = writer.write(buffer);
            guard(started);
            require(count > 0 && count <= remaining && buffer.position() == position + count);
          }
          require(writer.size() == content.length);
          guard(started);
          writer.force();
          guard(started);
          require(writer.size() == content.length);
          guard(started);
          return Boolean.TRUE;
        });
    guard(started);
  }

  private void verify(
      OwnedTransferDirectory child,
      String name,
      Metadata expected,
      byte[] content,
      byte[] readback,
      long started)
      throws StorageIoException {
    guard(started);
    child.atExistingEntryHandle(
        name,
        held -> {
          require(expected.equals(capture(held, false, started)));
          guard(started);
          ResourceScope.acquire(
              () -> {
                var channel = io.open(held);
                if (channel == null) throw unavailable();
                return channel;
              },
              java.nio.channels.SeekableByteChannel::close,
              channel -> {
                guard(started);
                require(channel.size() == content.length);
                guard(started);
                ByteBuffer buffer = ByteBuffer.wrap(readback);
                buffer.limit(content.length);
                while (buffer.hasRemaining()) {
                  int position = buffer.position();
                  int remaining = buffer.remaining();
                  guard(started);
                  int count = channel.read(buffer);
                  guard(started);
                  require(count > 0 && count <= remaining && buffer.position() == position + count);
                }
                require(Arrays.equals(content, 0, content.length, readback, 0, content.length));
                buffer.limit(readback.length);
                guard(started);
                require(channel.read(buffer) == -1 && buffer.position() == content.length);
                guard(started);
                require(channel.size() == content.length);
                guard(started);
                return Boolean.TRUE;
              });
          require(expected.equals(capture(held, false, started)));
          return Boolean.TRUE;
        });
    guard(started);
  }

  private Metadata directory(OwnedTransferDirectory directory, long started)
      throws StorageIoException {
    guard(started);
    Metadata result = directory.atDirectory(p -> capture(p, true, started));
    guard(started);
    return result;
  }

  private Metadata capture(Path held, boolean directory, long started) throws IOException {
    guard(started);
    Metadata value = metadata(io.attributes(held));
    guard(started);
    require(
        value.mode() == (directory ? 0x41c0 : 0x8180)
            && value.uid() == (directory ? uid : 0)
            && value.gid() == (directory ? gid : 0));
    if (directory) require(value.links() >= 2 && value.size() >= 0);
    else require(value.links() == 1 && value.size() >= 0 && value.size() <= 4096);
    byte[] acl = security.accessAcl(held, 44);
    guard(started);
    require(acl != null && acl.length == 0);
    require(!security.readOnlyFilesystem(held));
    guard(started);
    return value;
  }

  private static boolean identity(Metadata a, Metadata b) {
    // Both snapshots passed capture for the same role: mode/uid/gid and file nlink are fixed.
    return a.device() == b.device() && a.inode() == b.inode();
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
}
