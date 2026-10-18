package dev.codex.schubert.nk.batch.file;

import static dev.codex.schubert.nk.batch.file.EnvironmentInodePolicy.require;
import static dev.codex.schubert.nk.batch.file.EnvironmentInodePolicy.unavailable;

import dev.codex.schubert.nk.batch.file.EnvironmentInodePolicy.Snapshot;
import dev.codex.schubert.nk.batch.platform.BackupWorkerRequest;
import dev.codex.schubert.nk.storage.InodeSecurityCalls;
import dev.codex.schubert.nk.storage.OwnedTransferDirectory;
import dev.codex.schubert.nk.storage.ResourceScope;
import dev.codex.schubert.nk.storage.StorageIoException;
import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.channels.SeekableByteChannel;
import java.nio.file.Path;
import java.util.Arrays;
import java.util.Objects;
import java.util.UUID;
import org.jspecify.annotations.NullMarked;

/**
 * Root-only source request, not systemd's credential copy.
 * NK-OPS-001/BAK/UI251/SS3416.1/343/SSC092. Caller authenticates the fixed namespace, M/A, actual
 * original run/handles and full backup Unit termination before publication/retirement. No
 * overwrite/repair of an existing request.
 */
@NullMarked
public final class BackupWorkerRequestFiles {
  private static final String NAME = "backup-request";
  private final Object lock = new Object();
  private final OwnedTransferDirectory root;
  private final InodeSecurityCalls security;
  private final InspectorEnvironmentPublisher.Io io;
  private final EnvironmentInodePolicy policy;

  public BackupWorkerRequestFiles(OwnedTransferDirectory root, InodeSecurityCalls security) {
    this(root, security, new InspectorEnvironmentPublisher.NioIo());
  }

  BackupWorkerRequestFiles(
      OwnedTransferDirectory root,
      InodeSecurityCalls security,
      InspectorEnvironmentPublisher.Io io) {
    this.root = Objects.requireNonNull(root, "fixed request root");
    this.security = Objects.requireNonNull(security, "inode security");
    this.io = Objects.requireNonNull(io, "request IO");
    policy = new EnvironmentInodePolicy(security, io);
  }

  public void prepare(BackupWorkerRequest request, UUID part) throws StorageIoException {
    Objects.requireNonNull(request, "root request");
    Objects.requireNonNull(part, "new part");
    synchronized (lock) {
      byte[] content = request.encode();
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
        root.publishAs(part, NAME);
        Snapshot published = root.atExistingEntryHandle(NAME, p -> file(p, 1, directory));
        require(written.samePublishedFile(published));
        root.atExistingEntryHandle(
            NAME,
            p -> {
              verify(p, published, content);
              return true;
            });
        require(published.equals(root.atExistingEntryHandle(NAME, p -> file(p, 1, directory))));
        require(directory.sameIdentity(directory()));
      } finally {
        Arrays.fill(content, (byte) 0);
      }
    }
  }

  /** SSC113: caller must hold explicit same-run M/A/original/current/full-terminal proof. */
  public void prepareResume(BackupWorkerRequest expected, UUID part) throws StorageIoException {
    Objects.requireNonNull(expected, "same original request");
    Objects.requireNonNull(part, "new request part");
    synchronized (lock) {
      Snapshot before = directory();
      BackupWorkerRequest previous;
      try {
        previous = read();
      } catch (StorageIoException missing) {
        if (missing.reason() != StorageIoException.Reason.MISSING) throw missing;
        require(before.equals(directory()));
        prepare(expected, part);
        return;
      }
      require(expected.equals(previous) && expected.equals(read()));
      require(before.equals(directory()));
    }
  }

  @FunctionalInterface
  public interface ResumeProof {
    void verify(BackupWorkerRequest previous) throws java.io.IOException;
  }

  /**
   * SSC114: new real content start; only a same-owner actual DB proof may retire the old request.
   */
  public void prepareResumeReplacement(BackupWorkerRequest expected, UUID part, ResumeProof proof)
      throws java.io.IOException {
    Objects.requireNonNull(expected, "new real backup request");
    Objects.requireNonNull(part, "new-only request part");
    Objects.requireNonNull(proof, "same-owner abandoned DB pair proof");
    synchronized (lock) {
      Snapshot before = directory();
      BackupWorkerRequest previous;
      try {
        previous = read();
      } catch (StorageIoException missing) {
        if (missing.reason() != StorageIoException.Reason.MISSING) throw missing;
        require(before.equals(directory()));
        prepare(expected, part);
        return;
      }
      if (expected.equals(previous)) {
        prepareResume(expected, part);
        return;
      }
      require(
          expected.run().equals(previous.run()) && previous.started().isBefore(expected.started()));
      proof.verify(previous);
      require(previous.equals(read()) && before.equals(directory()));
      retire(previous);
      prepare(expected, part);
    }
  }

  public BackupWorkerRequest read() throws StorageIoException {
    synchronized (lock) {
      byte[] bytes = new byte[BackupWorkerRequest.MAXIMUM_BYTES + 1];
      try {
        Snapshot directory = directory();
        Snapshot original =
            root.atExistingEntryHandle(
                NAME,
                p -> {
                  Snapshot before = file(p, 1, directory);
                  read(p, before.metadata().size(), bytes);
                  require(before.equals(file(p, 1, directory)));
                  return before;
                });
        require(original.equals(root.atExistingEntryHandle(NAME, p -> file(p, 1, directory))));
        require(directory.equals(directory()));
        return BackupWorkerRequest.consume(Arrays.copyOf(bytes, (int) original.metadata().size()));
      } finally {
        Arrays.fill(bytes, (byte) 0);
      }
    }
  }

  /** Only after actual full Unit termination; source equality does not establish that condition. */
  public void retire(BackupWorkerRequest expected) throws StorageIoException {
    Objects.requireNonNull(expected, "original request");
    synchronized (lock) {
      Snapshot directory = directory();
      Snapshot before = root.atExistingEntryHandle(NAME, p -> file(p, 1, directory));
      require(expected.equals(read()));
      require(before.equals(root.atExistingEntryHandle(NAME, p -> file(p, 1, directory))));
      root.unlinkEntry(NAME);
      root.sync();
      require(directory.sameIdentity(directory()));
    }
  }

  private Snapshot directory() throws StorageIoException {
    guard();
    return root.atDirectory(
        p -> policy.snapshot(p, true, true, BackupWorkerRequest.MAXIMUM_BYTES, 0, 0));
  }

  private Snapshot file(Path held, int minimum, Snapshot directory) throws IOException {
    guard();
    Snapshot result =
        policy.snapshot(held, true, false, BackupWorkerRequest.MAXIMUM_BYTES, minimum, 0);
    require(result.metadata().device() == directory.metadata().device());
    return result;
  }

  private void guard() throws StorageIoException {
    require(!Thread.currentThread().isInterrupted());
    require(security.effectiveUid() == 0);
  }

  private void write(Path held, byte[] content) throws IOException {
    guard();
    ResourceScope.acquire(
        () -> {
          var writer = io.openWriter(held);
          if (writer == null) throw unavailable();
          return writer;
        },
        InspectorEnvironmentPublisher.Writer::close,
        writer -> {
          require(writer.size() == 0);
          ByteBuffer buffer = ByteBuffer.wrap(content);
          while (buffer.hasRemaining()) {
            guard();
            int position = buffer.position();
            int remaining = buffer.remaining();
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
      require(
          expected.equals(
              policy.snapshot(held, true, false, BackupWorkerRequest.MAXIMUM_BYTES, 1, 0)));
    } finally {
      Arrays.fill(buffer, (byte) 0);
    }
  }

  private void read(Path held, long length, byte[] bytes) throws IOException {
    guard();
    ResourceScope.acquire(
        () -> {
          var channel = io.open(held);
          if (channel == null) throw unavailable();
          return channel;
        },
        SeekableByteChannel::close,
        channel -> {
          require(channel.size() == length);
          ByteBuffer buffer = ByteBuffer.wrap(bytes);
          buffer.limit((int) length);
          while (buffer.hasRemaining()) {
            guard();
            int position = buffer.position();
            int remaining = buffer.remaining();
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
