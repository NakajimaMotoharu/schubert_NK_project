package dev.codex.schubert.nk.batch.file;

import static dev.codex.schubert.nk.batch.file.EnvironmentInodePolicy.require;
import static dev.codex.schubert.nk.batch.file.EnvironmentInodePolicy.unavailable;

import dev.codex.schubert.nk.batch.file.EnvironmentInodePolicy.Snapshot;
import dev.codex.schubert.nk.batch.platform.InspectorRunEnvironment;
import dev.codex.schubert.nk.batch.repository.BatchRun;
import dev.codex.schubert.nk.storage.InodeSecurityCalls;
import dev.codex.schubert.nk.storage.OwnedTransferDirectory;
import dev.codex.schubert.nk.storage.ResourceScope;
import dev.codex.schubert.nk.storage.StorageIoException;
import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.channels.FileChannel;
import java.nio.channels.SeekableByteChannel;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.util.Arrays;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;

/**
 * SSC063/PG171/BUG195/YKT154: explicit close precedence; 017049 compound PT supplement.
 * Borrowed-root run file publication only. NK-OPS-001; OPS-009/UI251/SS343 6.11; SSC-049; PG-D-154;
 * PT-OPS-PUB-001..012. Caller MUST hold the maintenance OS lock, admit the fixed namespace,
 * prohibit configuration changes and confirm child termination throughout each call. Never use this
 * helper's success to infer those conditions or the authoritative run/cutoff.
 */
@NullMarked
public final class InspectorEnvironmentPublisher {
  private static final String NAME = "inbox-inspector.env";
  private final Object stateLock = new Object();
  private final OwnedTransferDirectory root;
  private final InodeSecurityCalls security;
  private final Io io;
  private final EnvironmentInodePolicy policy;
  private final InspectorEnvironmentReader reader;

  interface Writer extends AutoCloseable {
    int write(ByteBuffer source) throws IOException;

    long size() throws IOException;

    void force() throws IOException;

    @Override
    void close() throws IOException;
  }

  interface Io extends InspectorEnvironmentReader.Io {
    @Nullable Writer openWriter(Path held) throws IOException;
  }

  public InspectorEnvironmentPublisher(OwnedTransferDirectory root, InodeSecurityCalls security) {
    this(root, security, new NioIo());
  }

  InspectorEnvironmentPublisher(OwnedTransferDirectory root, InodeSecurityCalls security, Io io) {
    this.root = Objects.requireNonNull(root, "environment root");
    this.security = Objects.requireNonNull(security, "inode security");
    this.io = Objects.requireNonNull(io, "environment IO");
    policy = new EnvironmentInodePolicy(security, io);
    // Only readRunAt is used: its runtime policy fixes GID=0, never the static configuration GID.
    reader = new InspectorEnvironmentReader(root, security, 1, io);
  }

  /**
   * Same-run reuse or new no-replace publication; failures retain any created or published file.
   */
  public void prepare(BatchRun run) throws StorageIoException {
    Objects.requireNonNull(run, "run");
    synchronized (stateLock) {
      begin();
      byte[] content = InspectorRunEnvironment.encode(run);
      try {
        Snapshot directory = directory();
        Optional<Snapshot> existing = probe(directory);
        Snapshot expected;
        if (existing.isPresent()) {
          expected = existing.orElseThrow();
          verifyBytes(run, NAME);
          root.atExistingEntryHandle(
              NAME,
              held -> {
                Snapshot before = file(held, 1, directory);
                require(expected.equals(before));
                forceExisting(held, content.length);
                require(before.equals(file(held, 1, directory)));
                return true;
              });
          root.sync();
        } else {
          expected =
              root.createPrivatePart(
                  run.id(),
                  held -> {
                    Snapshot before = file(held, 0, directory);
                    require(before.metadata().size() == 0);
                    writeNew(held, content);
                    Snapshot after = file(held, 1, directory);
                    require(before.sameIdentity(after));
                    require(after.metadata().size() == content.length);
                    return after;
                  });
          verifyBytes(run, run.id() + ".part");
          require(expected.equals(root.atPartHandle(run.id(), p -> file(p, 1, directory))));
          root.publishAs(run.id(), NAME);
        }
        Snapshot published = root.atExistingEntryHandle(NAME, p -> file(p, 1, directory));
        require(expected.samePublishedFile(published));
        verifyBytes(run, NAME);
        // BUG-152/YKT-118: the reader proves its own snapshot, not the original publication inode.
        // Only the original rename may change ctime; later readback must preserve it as well.
        require(published.equals(root.atExistingEntryHandle(NAME, p -> file(p, 1, directory))));
        finish(directory);
      } catch (IOException failure) {
        // Ownership scopes ended; IO/close diagnostics are not allowed across the parent boundary.
        throw unavailable();
      } finally {
        Arrays.fill(content, (byte) 0);
      }
    }
  }

  /** Native S2 never reuses an old env/part, even if its canonical run happens to match. */
  public void requireFresh() throws StorageIoException {
    synchronized (stateLock) {
      begin();
      directory();
      root.atDirectory(
          path -> {
            try (var entries = java.nio.file.Files.newDirectoryStream(path)) {
              for (var entry : entries) {
                String name =
                    Objects.requireNonNull(entry.getFileName(), "fixed namespace leaf").toString();
                require(
                    !name.equals(NAME)
                        && !name.matches("[0-9a-f]{8}(-[0-9a-f]{4}){3}-[0-9a-f]{12}\\.part"));
              }
            }
            return true;
          });
      directory();
    }
  }

  public void prepareNew(BatchRun run) throws StorageIoException {
    Objects.requireNonNull(run, "run");
    synchronized (stateLock) {
      requireFresh();
      prepare(run);
    }
  }

  /** Caller has confirmed the child is terminal. A different run is never retired implicitly. */
  public void retire(BatchRun run) throws StorageIoException {
    Objects.requireNonNull(run, "run");
    synchronized (stateLock) {
      begin();
      try {
        Snapshot directory = directory();
        Optional<Snapshot> existing = probe(directory);
        if (existing.isPresent()) {
          verifyBytes(run, NAME);
          require(
              existing
                  .orElseThrow()
                  .equals(root.atExistingEntryHandle(NAME, p -> file(p, 1, directory))));
          root.unlinkEntry(NAME);
        }
        finish(directory);
      } catch (IOException failure) {
        throw unavailable();
      }
    }
  }

  private void begin() throws StorageIoException {
    require(!Thread.currentThread().isInterrupted());
    require(security.effectiveUid() == 0);
  }

  private Snapshot directory() throws StorageIoException {
    return root.atDirectory(p -> policy.snapshot(p, true, true, 110, 0, 0));
  }

  private Snapshot file(Path held, int minimum, Snapshot directory) throws IOException {
    Snapshot result = policy.snapshot(held, true, false, 110, minimum, 0);
    require(result.metadata().device() == directory.metadata().device());
    return result;
  }

  private Optional<Snapshot> probe(Snapshot directory) throws StorageIoException {
    boolean[] entered = {false};
    try {
      return Optional.of(
          root.atExistingEntryHandle(
              NAME,
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

  private void verifyBytes(BatchRun run, String name) throws StorageIoException {
    byte[] bytes = reader.readRunAt(run, name);
    Arrays.fill(bytes, (byte) 0);
  }

  private void finish(Snapshot before) throws StorageIoException {
    require(before.sameIdentity(directory()));
    require(!Thread.currentThread().isInterrupted());
  }

  private void writeNew(Path held, byte[] content) throws IOException {
    ByteBuffer buffer = ByteBuffer.wrap(content);
    ResourceScope.acquire(
        () -> {
          var writer = io.openWriter(held);
          if (writer == null) throw unavailable();
          return writer;
        },
        Writer::close,
        writer -> {
          require(writer.size() == 0);
          while (buffer.hasRemaining()) {
            int position = buffer.position();
            int remaining = buffer.remaining();
            int count = writer.write(buffer);
            require(count > 0 && count <= remaining && buffer.position() == position + count);
          }
          require(writer.size() == content.length);
          writer.force();

          return Boolean.TRUE;
        });
  }

  private void forceExisting(Path held, int expected) throws IOException {
    ResourceScope.acquire(
        () -> {
          var writer = io.openWriter(held);
          if (writer == null) throw unavailable();
          return writer;
        },
        Writer::close,
        writer -> {
          require(writer.size() == expected);
          writer.force();
          require(writer.size() == expected);

          return Boolean.TRUE;
        });
  }

  static final class NioIo implements Io {
    private final InspectorEnvironmentReader.NioIo readerIo =
        new InspectorEnvironmentReader.NioIo();

    @Override
    public Map<String, Object> attributes(Path held) throws IOException {
      return readerIo.attributes(held);
    }

    @Override
    public String filesystem(Path held) throws IOException {
      return readerIo.filesystem(held);
    }

    @Override
    public SeekableByteChannel open(Path held) throws IOException {
      return readerIo.open(held);
    }

    @Override
    public Writer openWriter(Path held) throws IOException {
      return new NioWriter(FileChannel.open(held, StandardOpenOption.WRITE));
    }
  }

  private static final class NioWriter implements Writer {
    private final FileChannel channel;

    private NioWriter(FileChannel channel) {
      this.channel = channel;
    }

    @Override
    public int write(ByteBuffer source) throws IOException {
      return channel.write(source);
    }

    @Override
    public long size() throws IOException {
      return channel.size();
    }

    @Override
    public void force() throws IOException {
      channel.force(true);
    }

    @Override
    public void close() throws IOException {
      channel.close();
    }
  }
}
