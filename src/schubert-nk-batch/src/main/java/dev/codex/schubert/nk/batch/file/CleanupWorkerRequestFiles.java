package dev.codex.schubert.nk.batch.file;

import static dev.codex.schubert.nk.batch.file.EnvironmentInodePolicy.require;
import static dev.codex.schubert.nk.batch.file.EnvironmentInodePolicy.unavailable;

import dev.codex.schubert.nk.batch.file.EnvironmentInodePolicy.Snapshot;
import dev.codex.schubert.nk.batch.platform.CleanupWorkerRequest;
import dev.codex.schubert.nk.storage.*;
import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.file.Path;
import java.util.*;
import org.jspecify.annotations.NullMarked;

/**
 * Root-only Cleanup request source, not systemd's private credential copy or deletion authority.
 * NK-OPS-001/NK-BAT-001/OPS009/UI251/SS341/342/343/SSC104; PT-OPS-CREQFILE001..008. Parent
 * authenticates the fixed namespace, M/A, original run/activation and actual child Unit termination
 * before publication/retirement. No overwrite or repair of an existing request.
 */
@NullMarked
public final class CleanupWorkerRequestFiles {
  private final String name;
  private final int maximum;
  private final boolean expiry;
  private final Object lock = new Object();
  private final OwnedTransferDirectory root;
  private final InodeSecurityCalls security;
  private final InspectorEnvironmentPublisher.Io io;
  private final EnvironmentInodePolicy policy;

  public CleanupWorkerRequestFiles(OwnedTransferDirectory root, InodeSecurityCalls security) {
    this(root, security, new InspectorEnvironmentPublisher.NioIo());
  }

  CleanupWorkerRequestFiles(
      OwnedTransferDirectory root,
      InodeSecurityCalls security,
      InspectorEnvironmentPublisher.Io io) {
    this(root, security, io, false);
  }

  private CleanupWorkerRequestFiles(
      OwnedTransferDirectory root,
      InodeSecurityCalls security,
      InspectorEnvironmentPublisher.Io io,
      boolean expiry) {
    this.root = Objects.requireNonNull(root, "fixed request root");
    this.security = Objects.requireNonNull(security, "inode security");
    this.io = Objects.requireNonNull(io, "request IO");
    policy = new EnvironmentInodePolicy(security, io);
    this.expiry = expiry;
    name = expiry ? "expiry-request" : "cleanup-request";
    maximum =
        expiry ? CleanupWorkerRequest.Expiry.MAXIMUM_BYTES : CleanupWorkerRequest.MAXIMUM_BYTES;
  }

  public static CleanupWorkerRequestFiles forExpiry(
      OwnedTransferDirectory root, InodeSecurityCalls security) {
    return forExpiry(root, security, new InspectorEnvironmentPublisher.NioIo());
  }

  static CleanupWorkerRequestFiles forExpiry(
      OwnedTransferDirectory root,
      InodeSecurityCalls security,
      InspectorEnvironmentPublisher.Io io) {
    return new CleanupWorkerRequestFiles(root, security, io, true);
  }

  /** Any old request/part/unknown entry isolates the next Morning BEFORE DB/original/stop. */
  public void requireClear() throws StorageIoException {
    synchronized (lock) {
      Snapshot before = directory();
      root.atDirectory(
          held -> {
            try (var names = java.nio.file.Files.newDirectoryStream(held)) {
              require(!names.iterator().hasNext());
            } catch (java.nio.file.DirectoryIteratorException failure) {
              throw unavailable();
            }
            guard();
            return Boolean.TRUE;
          });
      require(before.equals(directory()));
    }
  }

  public void prepare(CleanupWorkerRequest request, UUID part) throws StorageIoException {
    Objects.requireNonNull(request, "root request");
    require(!expiry);
    prepareBytes(request.encode(), part);
  }

  public void prepareExpiry(CleanupWorkerRequest.Expiry request, UUID part)
      throws StorageIoException {
    Objects.requireNonNull(request, "root Expiry request");
    require(expiry);
    prepareBytes(request.encode(), part);
  }

  private void prepareBytes(byte[] content, UUID part) throws StorageIoException {
    Objects.requireNonNull(part, "new part");
    synchronized (lock) {
      try {
        Snapshot directory = directory();
        Snapshot written =
            root.createPrivatePart(
                part,
                held -> {
                  Snapshot empty = file(held, 0, directory);
                  require(empty.metadata().size() == 0);
                  write(held, content);
                  Snapshot result = file(held, 1, directory);
                  require(empty.sameIdentity(result) && result.metadata().size() == content.length);
                  verify(held, result, content);
                  return result;
                });
        require(written.equals(root.atPartHandle(part, p -> file(p, 1, directory))));
        root.publishAs(part, name);
        Snapshot published = root.atExistingEntryHandle(name, p -> file(p, 1, directory));
        require(written.samePublishedFile(published));
        root.atExistingEntryHandle(
            name,
            p -> {
              verify(p, published, content);
              return true;
            });
        require(published.equals(root.atExistingEntryHandle(name, p -> file(p, 1, directory))));
        require(directory.sameIdentity(directory()));
      } finally {
        Arrays.fill(content, (byte) 0);
      }
    }
  }

  public CleanupWorkerRequest read() throws StorageIoException {
    require(!expiry);
    return CleanupWorkerRequest.consume(readBytes());
  }

  public CleanupWorkerRequest.Expiry readExpiry() throws StorageIoException {
    require(expiry);
    return CleanupWorkerRequest.Expiry.consume(readBytes());
  }

  private byte[] readBytes() throws StorageIoException {
    synchronized (lock) {
      byte[] bytes = new byte[maximum + 1];
      try {
        Snapshot directory = directory();
        Snapshot original =
            root.atExistingEntryHandle(
                name,
                p -> {
                  Snapshot before = file(p, 1, directory);
                  read(p, before.metadata().size(), bytes);
                  require(before.equals(file(p, 1, directory)));
                  return before;
                });
        require(original.equals(root.atExistingEntryHandle(name, p -> file(p, 1, directory))));
        require(directory.equals(directory()));
        return Arrays.copyOf(bytes, (int) original.metadata().size());
      } finally {
        Arrays.fill(bytes, (byte) 0);
      }
    }
  }

  /** Only after actual full Unit termination; source equality does not establish that condition. */
  public void retire(CleanupWorkerRequest expected) throws StorageIoException {
    Objects.requireNonNull(expected, "original request");
    require(!expiry);
    retireBytes(expected.encode());
  }

  public void retireExpiry(CleanupWorkerRequest.Expiry expected) throws StorageIoException {
    Objects.requireNonNull(expected, "original Expiry request");
    require(expiry);
    retireBytes(expected.encode());
  }

  private void retireBytes(byte[] expected) throws StorageIoException {
    synchronized (lock) {
      byte[] actual = new byte[0];
      try {
        Snapshot directory = directory();
        Snapshot before = root.atExistingEntryHandle(name, p -> file(p, 1, directory));
        actual = readBytes();
        require(Arrays.equals(expected, actual));
        require(before.equals(root.atExistingEntryHandle(name, p -> file(p, 1, directory))));
        root.unlinkEntry(name);
        root.sync();
        require(directory.sameIdentity(directory()));
      } finally {
        Arrays.fill(expected, (byte) 0);
        Arrays.fill(actual, (byte) 0);
      }
    }
  }

  private Snapshot directory() throws StorageIoException {
    guard();
    return root.atDirectory(p -> policy.snapshot(p, true, true, maximum, 0, 0));
  }

  private Snapshot file(Path held, int minimum, Snapshot directory) throws IOException {
    guard();
    Snapshot result = policy.snapshot(held, true, false, maximum, minimum, 0);
    require(result.metadata().device() == directory.metadata().device());
    return result;
  }

  private void guard() throws StorageIoException {
    require(!Thread.currentThread().isInterrupted());
    require(security.effectiveUid() == 0);
  }

  private void write(Path held, byte[] content) throws IOException {
    guard();
    var writer = io.openWriter(held);
    if (writer == null) throw unavailable();
    ResourceScope.use(
        writer::close,
        () -> {
          require(writer.size() == 0);
          ByteBuffer buffer = ByteBuffer.wrap(content);
          while (buffer.hasRemaining()) {
            guard();
            int position = buffer.position(), remaining = buffer.remaining();
            int n = writer.write(buffer);
            require(n > 0 && n <= remaining && buffer.position() == position + n);
          }
          require(writer.size() == content.length);
          writer.force();
          require(writer.size() == content.length);
          guard();
          return true;
        });
  }

  private void verify(Path held, Snapshot expected, byte[] content) throws IOException {
    byte[] buffer = new byte[content.length + 1];
    try {
      read(held, content.length, buffer);
      require(Arrays.equals(content, 0, content.length, buffer, 0, content.length));
      require(expected.equals(policy.snapshot(held, true, false, maximum, 1, 0)));
    } finally {
      Arrays.fill(buffer, (byte) 0);
    }
  }

  private void read(Path held, long length, byte[] bytes) throws IOException {
    guard();
    var channel = io.open(held);
    if (channel == null) throw unavailable();
    ResourceScope.use(
        channel,
        () -> {
          require(channel.size() == length);
          ByteBuffer buffer = ByteBuffer.wrap(bytes);
          buffer.limit((int) length);
          while (buffer.hasRemaining()) {
            guard();
            int position = buffer.position(), remaining = buffer.remaining();
            int n = channel.read(buffer);
            require(n > 0 && n <= remaining && buffer.position() == position + n);
          }
          buffer.limit(bytes.length);
          require(channel.read(buffer) == -1 && buffer.position() == length);
          require(channel.size() == length);
          guard();
          return true;
        });
  }
}
