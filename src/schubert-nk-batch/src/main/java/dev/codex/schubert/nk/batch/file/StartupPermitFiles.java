package dev.codex.schubert.nk.batch.file;

import static dev.codex.schubert.nk.batch.file.EnvironmentInodePolicy.require;
import static dev.codex.schubert.nk.batch.file.EnvironmentInodePolicy.unavailable;

import dev.codex.schubert.nk.batch.file.EnvironmentInodePolicy.Snapshot;
import dev.codex.schubert.nk.batch.file.StartupPermitRecords.Epoch;
import dev.codex.schubert.nk.batch.file.StartupPermitRecords.Permit;
import dev.codex.schubert.nk.batch.file.StartupPermitRecords.State;
import dev.codex.schubert.nk.batch.repository.MaintenanceActivation;
import dev.codex.schubert.nk.storage.*;
import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.channels.SeekableByteChannel;
import java.nio.file.*;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.*;
import org.jspecify.annotations.*;

/**
 * NK-OPS-001; OPS009/UI251/SS343 SSC089; PG303; PT-OPS-PERMITFILE001..008. Borrowed authenticated
 * /run/schubert-nk/startup, root0700,tmpfs RW. Caller holds M/A and confirmed all fixed services
 * terminal for mutation; all original owners close before exec. No repair, fallback,
 * prerequisite-step claim, or child launch. Namespace admission is external.
 */
@NullMarked
public final class StartupPermitFiles {
  private static final String CURRENT = "epoch.current";
  private final Object stateLock = new Object();
  private final OwnedTransferDirectory root;
  private final InodeSecurityCalls security;
  private final Io io;
  private final EnvironmentInodePolicy policy;
  private final Parts parts;

  interface Io extends InspectorEnvironmentPublisher.Io {
    void replace(Path directory, String part, String current) throws IOException;

    MessageDigest digest() throws NoSuchAlgorithmException;
  }

  @FunctionalInterface
  interface Parts {
    UUID next();
  }

  public StartupPermitFiles(OwnedTransferDirectory root, InodeSecurityCalls security) {
    this(root, security, new NioIo(), UUID::randomUUID);
  }

  StartupPermitFiles(OwnedTransferDirectory root, InodeSecurityCalls security, Io io, Parts parts) {
    this.root = Objects.requireNonNull(root, "current namespace");
    this.security = Objects.requireNonNull(security, "security");
    this.io = Objects.requireNonNull(io, "IO");
    this.parts = Objects.requireNonNull(parts, "part IDs");
    policy = new EnvironmentInodePolicy(security, io);
  }

  /** Fresh epoch even on same-run resume; old permit is retained, never restored or accepted. */
  public Epoch invalidate(UUID boot, UUID epoch, MaintenanceActivation activation)
      throws StorageIoException {
    Epoch next = new Epoch(State.INVALID, boot, epoch, activation, Optional.empty());
    synchronized (stateLock) {
      try {
        Snapshot before = begin();
        Optional<Epoch> old = existingCurrent(before);
        require(old.isEmpty() || !old.orElseThrow().epoch().equals(epoch));
        replaceCurrent(next, before);
        finish(before);
        return next;
      } catch (IOException failure) {
        throw unavailable();
      }
    }
  }

  /** Caller has independently confirmed every required actual prestart step and current binding. */
  public Epoch issue(Epoch expected, Permit permit) throws StorageIoException {
    Objects.requireNonNull(expected, "expected epoch");
    Objects.requireNonNull(permit, "permit");
    synchronized (stateLock) {
      byte[] content = StartupPermitRecords.permit(permit);
      try {
        Snapshot before = begin();
        require(expected.state() == State.INVALID);
        require(expected.equals(current(before)));
        require(
            expected.boot().equals(permit.boot())
                && expected.epoch().equals(permit.epoch())
                && expected.activation().equals(permit.activation()));
        UUID part = parts.next();
        Snapshot original = writePart(part, content, before);
        String name = permit.epoch() + ".permit";
        root.publishAs(part, name);
        require(
            original.samePublishedFile(root.atExistingEntryHandle(name, p -> file(p, 1, before))));
        checkBytes(name, content, before);
        require(expected.equals(current(before)));
        String digest = HexFormat.of().formatHex(io.digest().digest(content));
        Epoch issued = expected.issued(digest);
        replaceCurrent(issued, before);
        require(permit.equals(readIssuedAt(before)));
        finish(before);
        return issued;
      } catch (IOException | NoSuchAlgorithmException failure) {
        throw unavailable();
      } finally {
        Arrays.fill(content, (byte) 0);
      }
    }
  }

  public Epoch current() throws StorageIoException {
    synchronized (stateLock) {
      try {
        Snapshot before = begin();
        Epoch result = current(before);
        finish(before);
        return result;
      } catch (IOException failure) {
        throw unavailable();
      }
    }
  }

  /**
   * Read-only: missing/corrupt/INVALID/old originals fail; never mutate to manufacture admission.
   */
  public Permit readIssued() throws StorageIoException {
    synchronized (stateLock) {
      try {
        Snapshot before = begin();
        Permit result = readIssuedAt(before);
        finish(before);
        return result;
      } catch (IOException failure) {
        throw unavailable();
      }
    }
  }

  private Permit readIssuedAt(Snapshot directory) throws IOException {
    Epoch before = current(directory);
    require(before.state() == State.ISSUED);
    byte[] bytes = read(before.epoch() + ".permit", directory);
    try {
      Permit result = StartupPermitRecords.verifyIssued(before, bytes);
      require(before.equals(current(directory)));
      return result;
    } finally {
      Arrays.fill(bytes, (byte) 0);
    }
  }

  private Optional<Epoch> existingCurrent(Snapshot directory) throws IOException {
    boolean[] entered = {false};
    try {
      root.atExistingEntryHandle(
          CURRENT,
          p -> {
            entered[0] = true;
            return file(p, 1, directory);
          });
      return Optional.of(current(directory));
    } catch (StorageIoException failure) {
      if (!entered[0] && failure.reason() == StorageIoException.Reason.MISSING)
        return Optional.empty();
      throw failure;
    }
  }

  private Epoch current(Snapshot directory) throws IOException {
    byte[] content = read(CURRENT, directory);
    try {
      return StartupPermitRecords.readEpoch(content);
    } finally {
      Arrays.fill(content, (byte) 0);
    }
  }

  private void replaceCurrent(Epoch value, Snapshot directory) throws IOException {
    byte[] content = StartupPermitRecords.epoch(value);
    try {
      UUID id = parts.next();
      Snapshot original = writePart(id, content, directory);
      root.atDirectory(
          p -> {
            io.replace(p, id + ".part", CURRENT);
            return Boolean.TRUE;
          });
      root.sync();
      require(
          original.samePublishedFile(
              root.atExistingEntryHandle(CURRENT, p -> file(p, 1, directory))));
      checkBytes(CURRENT, content, directory);
    } finally {
      Arrays.fill(content, (byte) 0);
    }
  }

  private Snapshot writePart(UUID id, byte[] content, Snapshot directory) throws IOException {
    return root.createPrivatePart(
        id,
        p -> {
          Snapshot before = file(p, 0, directory);
          require(before.metadata().size() == 0);
          var writer = io.openWriter(p);
          if (writer == null) throw unavailable();
          ResourceScope.use(
              writer::close,
              () -> {
                require(writer.size() == 0);
                ByteBuffer buffer = ByteBuffer.wrap(content);
                while (buffer.hasRemaining()) {
                  int position = buffer.position(),
                      remaining = buffer.remaining(),
                      count = writer.write(buffer);
                  require(count > 0 && count <= remaining && buffer.position() == position + count);
                }
                require(writer.size() == content.length);
                writer.force();
                require(writer.size() == content.length);
                return Boolean.TRUE;
              });
          Snapshot after = file(p, 1, directory);
          require(before.sameIdentity(after));
          return after;
        });
  }

  private void checkBytes(String name, byte[] expected, Snapshot directory) throws IOException {
    byte[] actual = read(name, directory);
    try {
      require(Arrays.equals(expected, actual));
    } finally {
      Arrays.fill(actual, (byte) 0);
    }
  }

  private byte[] read(String name, Snapshot directory) throws IOException {
    byte[] buffer = new byte[8193];
    try {
      Snapshot original =
          root.atExistingEntryHandle(
              name,
              p -> {
                Snapshot before = file(p, 1, directory);
                SeekableByteChannel reader = io.open(p);
                if (reader == null) throw unavailable();
                ResourceScope.use(
                    reader::close,
                    () -> {
                      require(reader.size() == before.metadata().size());
                      ByteBuffer bytes = ByteBuffer.wrap(buffer);
                      while (bytes.hasRemaining()) {
                        int position = bytes.position(),
                            remaining = bytes.remaining(),
                            count = reader.read(bytes);
                        if (count == -1) break;
                        require(
                            count > 0
                                && count <= remaining
                                && bytes.position() == position + count);
                      }
                      require(bytes.position() == before.metadata().size());
                      require(reader.size() == before.metadata().size());
                      return Boolean.TRUE;
                    });
                require(before.equals(file(p, 1, directory)));
                return before;
              });
      require(original.equals(root.atExistingEntryHandle(name, p -> file(p, 1, directory))));
      finish(directory);
      return Arrays.copyOf(buffer, (int) original.metadata().size());
    } finally {
      Arrays.fill(buffer, (byte) 0);
    }
  }

  private Snapshot begin() throws IOException {
    require(!Thread.currentThread().isInterrupted());
    require(security.effectiveUid() == 0);
    return directory();
  }

  private Snapshot directory() throws StorageIoException {
    return root.atDirectory(p -> policy.snapshot(p, true, true, 8192, 0, 0));
  }

  private Snapshot file(Path held, int minimum, Snapshot directory) throws IOException {
    Snapshot value = policy.snapshot(held, true, false, 8192, minimum, 0);
    require(value.metadata().device() == directory.metadata().device());
    return value;
  }

  private void finish(Snapshot before) throws IOException {
    require(before.sameIdentity(directory()));
    require(!Thread.currentThread().isInterrupted());
  }

  static final class NioIo implements Io {
    private final InspectorEnvironmentPublisher.NioIo delegate =
        new InspectorEnvironmentPublisher.NioIo();

    @Override
    public Map<String, Object> attributes(Path path) throws IOException {
      return delegate.attributes(path);
    }

    @Override
    public String filesystem(Path path) throws IOException {
      return delegate.filesystem(path);
    }

    @Override
    public SeekableByteChannel open(Path path) throws IOException {
      return delegate.open(path);
    }

    @Override
    public InspectorEnvironmentPublisher.Writer openWriter(Path path) throws IOException {
      return delegate.openWriter(path);
    }

    @Override
    public void replace(Path directory, String part, String current) throws IOException {
      // Retained directory and same filesystem only; unsupported atomic operation fails, no
      // fallback.
      Files.move(
          directory.resolve(part), directory.resolve(current), StandardCopyOption.ATOMIC_MOVE);
    }

    @Override
    public MessageDigest digest() throws NoSuchAlgorithmException {
      return MessageDigest.getInstance("SHA-256");
    }
  }
}
