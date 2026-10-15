package dev.codex.schubert.nk.batch.file;

import static dev.codex.schubert.nk.batch.file.EnvironmentInodePolicy.require;
import static dev.codex.schubert.nk.batch.file.EnvironmentInodePolicy.unavailable;

import dev.codex.schubert.nk.batch.file.EnvironmentInodePolicy.Metadata;
import dev.codex.schubert.nk.storage.InodeSecurityCalls;
import dev.codex.schubert.nk.storage.OwnedTransferDirectory;
import dev.codex.schubert.nk.storage.ResourceScope;
import dev.codex.schubert.nk.storage.StorageIoException;
import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.file.Path;
import java.util.Arrays;
import java.util.Objects;
import java.util.UUID;
import org.jspecify.annotations.NullMarked;

/**
 * NK-OPS-001; BAK/BKO/OPS009/UI251/SS341 6.1/3436.6; SSC090/091; PT-OPS-DBCP001..008. Borrowed,
 * independently admitted dedicated worker tmpfs root only. Caller authenticates fixed
 * Unit/NSS/namespace/output/parent M+A/whole budget and keeps every child terminal before returning
 * from Dump. Unknown-start isolation must NOT unwind this callback. No repair/overwrite/retry.
 */
@NullMarked
public final class BackupDatabaseCopy {
  @FunctionalInterface
  public interface Dump {
    void execute(Path heldPgpass) throws IOException;
  }

  private final Object lock = new Object();
  private final OwnedTransferDirectory root;
  private final InodeSecurityCalls security;
  private final InspectorEnvironmentPublisher.Io io;
  private final long uid;
  private final long gid;

  public BackupDatabaseCopy(
      OwnedTransferDirectory root, InodeSecurityCalls security, long uid, long gid) {
    this(root, security, uid, gid, new InspectorEnvironmentPublisher.NioIo());
  }

  BackupDatabaseCopy(
      OwnedTransferDirectory root,
      InodeSecurityCalls security,
      long uid,
      long gid,
      InspectorEnvironmentPublisher.Io io) {
    this.root = Objects.requireNonNull(root, "worker runtime root");
    this.security = Objects.requireNonNull(security, "inode security");
    this.io = Objects.requireNonNull(io, "copy IO");
    if (uid < 1 || uid > 0xffff_ffffL || gid < 1 || gid > 0xffff_ffffL)
      throw new IllegalArgumentException("invalid dedicated worker owner");
    this.uid = uid;
    this.gid = gid;
  }

  /** Consumes and clears raw bytes even on failure. Created material is retired only on success. */
  public void dump(byte[] raw, UUID part, Dump dump) throws StorageIoException {
    Objects.requireNonNull(raw, "owned pgpass bytes");
    synchronized (lock) {
      try {
        Objects.requireNonNull(part, "new material id");
        Objects.requireNonNull(dump, "fixed dump");
        require(raw.length >= 1 && raw.length <= 65536);
        guard();
        Metadata directory = directory();
        root.createPrivatePart(
            part,
            held -> {
              Metadata empty = capture(held, false);
              require(empty.device() == directory.device() && empty.size() == 0);
              write(held, raw, 0);
              Metadata written = capture(held, false);
              require(identity(empty, written) && written.size() == raw.length);
              bound(part, written);
              verify(held, written, raw);
              Arrays.fill(raw, (byte) 0);
              guard();
              dump.execute(held);
              guard();
              // Only all-terminal-positive return can authorize erasure. Unknown/IO preserves copy.
              require(written.equals(capture(held, false)));
              bound(part, written);
              write(held, raw, raw.length);
              Metadata erased = capture(held, false);
              require(identity(written, erased) && erased.size() == raw.length);
              verify(held, erased, raw);
              bound(part, erased);
              require(identity(directory, directory()));
              root.deletePart(part);
              root.sync();
              require(identity(directory, directory()));
              return Boolean.TRUE;
            });
        guard();
      } finally {
        Arrays.fill(raw, (byte) 0);
      }
    }
  }

  private void guard() throws StorageIoException {
    require(!Thread.currentThread().isInterrupted());
    require(security.effectiveUid() == uid);
  }

  private Metadata directory() throws StorageIoException {
    guard();
    return root.atDirectory(p -> capture(p, true));
  }

  private Metadata capture(Path held, boolean directory) throws IOException {
    guard();
    Metadata m = EnvironmentInodePolicy.metadata(io.attributes(held));
    require(m.mode() == (directory ? 040700 : 0100600) && m.uid() == uid && m.gid() == gid);
    if (directory) require(m.links() >= 2 && m.size() >= 0);
    else require(m.links() == 1 && m.size() >= 0 && m.size() <= 65536);
    byte[] acl = security.accessAcl(held, 44);
    require(acl != null && acl.length == 0);
    require("tmpfs".equals(io.filesystem(held)) && !security.readOnlyFilesystem(held));
    return m;
  }

  private static boolean identity(Metadata before, Metadata after) {
    return before.device() == after.device() && before.inode() == after.inode();
  }

  private void bound(UUID part, Metadata expected) throws StorageIoException {
    require(expected.equals(root.atPartHandle(part, p -> capture(p, false))));
  }

  private void write(Path held, byte[] bytes, int beforeSize) throws IOException {
    guard();
    var writer = io.openWriter(held);
    if (writer == null) throw unavailable();
    ResourceScope.use(
        writer::close,
        () -> {
          require(writer.size() == beforeSize);
          ByteBuffer buffer = ByteBuffer.wrap(bytes);
          while (buffer.hasRemaining()) {
            guard();
            int position = buffer.position();
            int remaining = buffer.remaining();
            int count = writer.write(buffer);
            require(count > 0 && count <= remaining && buffer.position() == position + count);
          }
          require(writer.size() == bytes.length);
          writer.force();
          require(writer.size() == bytes.length);
          guard();
          return Boolean.TRUE;
        });
  }

  private void verify(Path held, Metadata expected, byte[] bytes) throws IOException {
    byte[] readback = new byte[bytes.length + 1];
    try {
      var channel = io.open(held);
      if (channel == null) throw unavailable();
      ResourceScope.use(
          channel,
          () -> {
            require(channel.size() == bytes.length);
            ByteBuffer buffer = ByteBuffer.wrap(readback);
            buffer.limit(bytes.length);
            while (buffer.hasRemaining()) {
              guard();
              int position = buffer.position();
              int remaining = buffer.remaining();
              int count = channel.read(buffer);
              require(count > 0 && count <= remaining && buffer.position() == position + count);
            }
            require(Arrays.equals(bytes, 0, bytes.length, readback, 0, bytes.length));
            buffer.limit(readback.length);
            require(channel.read(buffer) == -1 && buffer.position() == bytes.length);
            require(channel.size() == bytes.length);
            return Boolean.TRUE;
          });
      require(expected.equals(capture(held, false)));
    } finally {
      Arrays.fill(readback, (byte) 0);
    }
  }
}
