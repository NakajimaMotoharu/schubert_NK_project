package dev.codex.schubert.nk.batch.file;

import static dev.codex.schubert.nk.batch.file.EnvironmentInodePolicy.require;
import static dev.codex.schubert.nk.batch.file.EnvironmentInodePolicy.unavailable;

import dev.codex.schubert.nk.batch.file.EnvironmentInodePolicy.Snapshot;
import dev.codex.schubert.nk.storage.InodeSecurityCalls;
import dev.codex.schubert.nk.storage.OwnedTransferDirectory;
import dev.codex.schubert.nk.storage.ResourceScope;
import dev.codex.schubert.nk.storage.StorageIoException;
import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.file.Path;
import java.util.Arrays;
import java.util.Objects;
import java.util.Optional;
import java.util.UUID;
import java.util.regex.Pattern;
import org.jspecify.annotations.NullMarked;

/**
 * SSC063/PG171/BUG195/YKT154: explicit close precedence; 017049 compound PT supplement. Borrowed
 * private durable root, never a state-machine or OS-lock authority. NK-BAT-001;
 * OPS-009/UI251/SS311/343 6.14; SSC-055/PG-D-157; PT-BAT-046..057. Caller admits fixed namespace
 * and holds the maintenance OS flock across all related operations.
 */
@NullMarked
final class DurableRecordFiles {
  private static final Pattern NAME =
      Pattern.compile(
          "[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\\.(run|begin|done|plan|retire)");
  private final Object stateLock = new Object();
  private final OwnedTransferDirectory root;
  private final InodeSecurityCalls security;
  private final InspectorEnvironmentPublisher.Io io;
  private final EnvironmentInodePolicy policy;

  DurableRecordFiles(OwnedTransferDirectory root, InodeSecurityCalls security) {
    this(root, security, new InspectorEnvironmentPublisher.NioIo());
  }

  DurableRecordFiles(
      OwnedTransferDirectory root,
      InodeSecurityCalls security,
      InspectorEnvironmentPublisher.Io io) {
    this.root = Objects.requireNonNull(root, "record root");
    this.security = Objects.requireNonNull(security, "inode security");
    this.io = Objects.requireNonNull(io, "record IO");
    policy = new EnvironmentInodePolicy(security, io);
  }

  /** Caller-owned canonical bytes; only an initial entry-open MISSING means absence. */
  Optional<byte[]> read(String name) throws StorageIoException {
    name(name);
    synchronized (stateLock) {
      begin();
      byte[] buffer = new byte[205];
      try {
        Snapshot directory = directory();
        Optional<Snapshot> initial = probe(name, directory);
        if (initial.isEmpty()) {
          require(directory.equals(directory()));
          finish(directory);
          return Optional.empty();
        }
        Snapshot expected = initial.orElseThrow();
        readStable(name, expected, directory, buffer);
        byte[] result = Arrays.copyOf(buffer, (int) expected.metadata().size());
        content(name, result);
        require(directory.equals(directory()));
        finish(directory);
        return Optional.of(result);
      } catch (IOException failure) {
        throw unavailable();
      } finally {
        Arrays.fill(buffer, (byte) 0);
      }
    }
  }

  /** No overwrite or automatic partial-file recovery, including when publication is uncertain. */
  void publish(String name, byte[] bytes, UUID partId) throws StorageIoException {
    name(name);
    Objects.requireNonNull(bytes, "record bytes");
    Objects.requireNonNull(partId, "part identity");
    byte[] copy = bytes.clone();
    synchronized (stateLock) {
      try {
        content(name, copy);
        begin();
        Snapshot directory = directory();
        Optional<Snapshot> initial = probe(name, directory);
        Snapshot expected;
        if (initial.isPresent()) {
          expected = initial.orElseThrow();
          verify(name, expected, directory, copy);
          root.atExistingEntryHandle(
              name,
              held -> {
                require(expected.equals(file(held, 1, directory)));
                force(held, copy.length);
                require(expected.equals(file(held, 1, directory)));
                return true;
              });
          root.sync();
        } else {
          expected =
              root.createPrivatePart(
                  partId,
                  held -> {
                    Snapshot before = file(held, 0, directory);
                    require(before.metadata().size() == 0);
                    write(held, copy);
                    Snapshot after = file(held, 1, directory);
                    require(before.sameIdentity(after));
                    require(after.metadata().size() == copy.length);
                    return after;
                  });
          verify(partId + ".part", expected, directory, copy);
          require(expected.equals(root.atPartHandle(partId, p -> file(p, 1, directory))));
          root.publishAs(partId, name);
        }
        Snapshot published = root.atExistingEntryHandle(name, p -> file(p, 1, directory));
        require(expected.samePublishedFile(published));
        verify(name, published, directory, copy);
        require(published.equals(root.atExistingEntryHandle(name, p -> file(p, 1, directory))));
        finish(directory);
      } catch (IOException failure) {
        throw unavailable();
      } finally {
        Arrays.fill(copy, (byte) 0);
      }
    }
  }

  /**
   * Caller authorizes retirement; this method proves bytes/inode, not completion or GC eligibility.
   */
  void remove(String name, byte[] bytes) throws StorageIoException {
    name(name);
    Objects.requireNonNull(bytes, "record bytes");
    byte[] copy = bytes.clone();
    synchronized (stateLock) {
      try {
        content(name, copy);
        begin();
        Snapshot directory = directory();
        Optional<Snapshot> initial = probe(name, directory);
        if (initial.isPresent()) {
          Snapshot expected = initial.orElseThrow();
          verify(name, expected, directory, copy);
          require(expected.equals(root.atExistingEntryHandle(name, p -> file(p, 1, directory))));
          root.unlinkEntry(name);
        } else {
          // BUG-159: absence may follow unlink success plus a failed directory durability barrier.
          root.sync();
        }
        finish(directory);
      } catch (IOException failure) {
        throw unavailable();
      } finally {
        Arrays.fill(copy, (byte) 0);
      }
    }
  }

  private static void name(String name) {
    Objects.requireNonNull(name, "record name");
    if (!name.equals("active") && !NAME.matcher(name).matches())
      throw new IllegalArgumentException("record name is invalid");
  }

  private static void content(String name, byte[] bytes) throws IOException {
    if (name.equals("active")) {
      MaintenanceRecords.readActivation(bytes);
    } else if (name.endsWith(".run")) {
      require(name.equals(MaintenanceRecords.readAnchor(bytes).id() + ".run"));
    } else if (name.endsWith(".begin")) {
      require(name.equals(MaintenanceRecords.readActivation(bytes).id() + ".begin"));
    } else if (name.endsWith(".plan")) {
      require(name.equals(MaintenanceRecords.readCompletion(bytes).activation().id() + ".plan"));
    } else if (name.endsWith(".retire")) {
      require(name.equals(MaintenanceRecords.readRetirement(bytes).run().id() + ".retire"));
    } else {
      require(name.equals(MaintenanceRecords.readCompletion(bytes).activation().id() + ".done"));
    }
  }

  private void begin() throws StorageIoException {
    require(!Thread.currentThread().isInterrupted());
    require(security.effectiveUid() == 0);
  }

  private Snapshot directory() throws StorageIoException {
    return root.atDirectory(p -> policy.durable(p, true, 0));
  }

  private Snapshot file(Path held, int minimum, Snapshot directory) throws IOException {
    Snapshot result = policy.durable(held, false, minimum);
    require(result.metadata().device() == directory.metadata().device());
    return result;
  }

  private Optional<Snapshot> probe(String name, Snapshot directory) throws StorageIoException {
    boolean[] entered = {false};
    try {
      return Optional.of(
          root.atExistingEntryHandle(
              name,
              p -> {
                entered[0] = true;
                return file(p, 1, directory);
              }));
    } catch (StorageIoException failure) {
      if (!entered[0] && failure.reason() == StorageIoException.Reason.MISSING)
        return Optional.empty();
      throw failure;
    }
  }

  private void readStable(String name, Snapshot expected, Snapshot directory, byte[] buffer)
      throws StorageIoException {
    root.atExistingEntryHandle(
        name,
        held -> {
          require(expected.equals(file(held, 1, directory)));
          readFile(held, expected.metadata().size(), buffer);
          require(expected.equals(file(held, 1, directory)));
          return true;
        });
    require(expected.equals(root.atExistingEntryHandle(name, p -> file(p, 1, directory))));
  }

  private void verify(String name, Snapshot expected, Snapshot directory, byte[] bytes)
      throws StorageIoException {
    byte[] buffer = new byte[205];
    try {
      readStable(name, expected, directory, buffer);
      require(expected.metadata().size() == bytes.length);
      require(Arrays.equals(bytes, 0, bytes.length, buffer, 0, bytes.length));
    } finally {
      Arrays.fill(buffer, (byte) 0);
    }
  }

  private void readFile(Path held, long expected, byte[] bytes) throws IOException {
    ByteBuffer buffer = ByteBuffer.wrap(bytes);
    var channel = io.open(held);
    if (channel == null) throw unavailable();
    ResourceScope.use(
        channel::close,
        () -> {
          require(channel.size() == expected);
          while (buffer.hasRemaining()) {
            int position = buffer.position(), remaining = buffer.remaining();
            int count = channel.read(buffer);
            if (count == -1) break;
            require(count > 0 && count <= remaining && buffer.position() == position + count);
          }
          require(buffer.position() == expected);
          require(channel.size() == expected);

          return Boolean.TRUE;
        });
  }

  private void write(Path held, byte[] bytes) throws IOException {
    ByteBuffer buffer = ByteBuffer.wrap(bytes);
    var writer = io.openWriter(held);
    if (writer == null) throw unavailable();
    ResourceScope.use(
        writer::close,
        () -> {
          require(writer.size() == 0);
          while (buffer.hasRemaining()) {
            int position = buffer.position(), remaining = buffer.remaining();
            int count = writer.write(buffer);
            require(count > 0 && count <= remaining && buffer.position() == position + count);
          }
          require(writer.size() == bytes.length);
          writer.force();

          return Boolean.TRUE;
        });
  }

  private void force(Path held, int size) throws IOException {
    var writer = io.openWriter(held);
    if (writer == null) throw unavailable();
    ResourceScope.use(
        writer::close,
        () -> {
          require(writer.size() == size);
          writer.force();
          require(writer.size() == size);

          return Boolean.TRUE;
        });
  }

  private void finish(Snapshot directory) throws StorageIoException {
    require(directory.sameIdentity(directory()));
    require(!Thread.currentThread().isInterrupted());
  }
}
