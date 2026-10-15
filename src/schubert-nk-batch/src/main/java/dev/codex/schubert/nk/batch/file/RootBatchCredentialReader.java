package dev.codex.schubert.nk.batch.file;

import static dev.codex.schubert.nk.batch.file.EnvironmentInodePolicy.require;

import dev.codex.schubert.nk.api.maintenance.InspectorDbCredential;
import dev.codex.schubert.nk.batch.file.EnvironmentInodePolicy.Metadata;
import dev.codex.schubert.nk.batch.platform.CleanupWorkerRequest;
import dev.codex.schubert.nk.storage.InodeSecurityCalls;
import dev.codex.schubert.nk.storage.OwnedTransferDirectory;
import dev.codex.schubert.nk.storage.ResourceScope;
import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.channels.SeekableByteChannel;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.util.Arrays;
import java.util.Map;
import java.util.Objects;
import org.jspecify.annotations.NullMarked;

/**
 * Borrowed fixed root Morning/Cleanup LoadCredential, never an ordinary service catalog extension.
 * Caller authenticates its own root Unit/boot and exact private credential namespace first.
 * NK-OPS-001/DAT009/OPS009/UI251/SS341/3436.15/SSC094104/PG311329; PT-OPS-RBCR001..012.
 */
@NullMarked
public final class RootBatchCredentialReader {
  interface Io {
    Map<String, Object> attributes(Path held) throws IOException;

    String filesystem(Path held) throws IOException;

    SeekableByteChannel open(Path held) throws IOException;
  }

  private final OwnedTransferDirectory root;
  private final InodeSecurityCalls security;
  private final Io io;

  public RootBatchCredentialReader(OwnedTransferDirectory root, InodeSecurityCalls security) {
    this(root, security, new NativeIo());
  }

  RootBatchCredentialReader(OwnedTransferDirectory root, InodeSecurityCalls security, Io io) {
    this.root = Objects.requireNonNull(root, "root credential directory");
    this.security = Objects.requireNonNull(security, "root credential security");
    this.io = Objects.requireNonNull(io, "root credential IO");
  }

  /** New password owner returned only after every read/close/inode observation succeeds. */
  public InspectorDbCredential read() throws IOException {
    return InspectorDbCredential.consume(readBytes("db-batch", 65536));
  }

  /** Fixed private copy only; canonical nonsecret correlation is not deletion authority. */
  public CleanupWorkerRequest readCleanupRequest() throws IOException {
    try {
      return CleanupWorkerRequest.consume(
          readBytes("cleanup-request", CleanupWorkerRequest.MAXIMUM_BYTES));
    } catch (IOException | IllegalArgumentException failure) {
      throw new IOException("root cleanup request unavailable");
    }
  }

  /** SSC124: closed success/FAILED data profile, never accepts an arbitrary kind/path. */
  public dev.codex.schubert.nk.batch.platform.CleanupProfile readCleanupProfile()
      throws IOException {
    try {
      return dev.codex.schubert.nk.batch.platform.CleanupProfile.consume(
          readBytes(
              "cleanup-request",
              dev.codex.schubert.nk.batch.platform.CleanupProfile.MAXIMUM_BYTES));
    } catch (IOException | IllegalArgumentException invalid) {
      throw new IOException("root cleanup profile unavailable");
    }
  }

  public CleanupWorkerRequest.Expiry readExpiryRequest() throws IOException {
    try {
      return CleanupWorkerRequest.Expiry.consume(
          readBytes("expiry-request", CleanupWorkerRequest.Expiry.MAXIMUM_BYTES));
    } catch (IllegalArgumentException invalid) {
      throw new IOException("root Expiry request unavailable");
    }
  }

  public dev.codex.schubert.nk.bootstrap.MaintenanceOwnerFrame readMaintenanceOwner()
      throws IOException {
    try {
      return dev.codex.schubert.nk.bootstrap.MaintenanceOwnerFrame.consume(
          readBytes(
              "maintenance-owner",
              dev.codex.schubert.nk.bootstrap.MaintenanceOwnerFrame.MAXIMUM_BYTES));
    } catch (IllegalArgumentException invalid) {
      throw new IOException("root maintenance owner unavailable");
    }
  }

  public InspectorDbCredential readMaintenanceMq() throws IOException {
    return InspectorDbCredential.consume(readBytes("mq-maintenance", 65536));
  }

  public InspectorDbCredential readOpsMq() throws IOException {
    return InspectorDbCredential.consume(readBytes("mq-ops", 65536));
  }

  private byte[] readBytes(String name, int maximum) throws IOException {
    byte[] material = new byte[maximum + 1];
    try {
      require(!Thread.currentThread().isInterrupted() && security.effectiveUid() == 0);
      Metadata directory = root.atDirectory(p -> inspect(p, true, maximum));
      int length =
          root.atExistingEntryHandle(
              name,
              p -> {
                Metadata before = inspect(p, false, maximum);
                require(before.device() == directory.device());
                var channel = Objects.requireNonNull(io.open(p), "root credential channel");
                int count =
                    ResourceScope.use(
                        channel::close,
                        () -> {
                          require(channel.size() == before.size());
                          ByteBuffer buffer = ByteBuffer.wrap(material);
                          while (buffer.hasRemaining()) {
                            int position = buffer.position();
                            int remaining = buffer.remaining();
                            int read = channel.read(buffer);
                            if (read == -1) break;
                            require(
                                read > 0
                                    && read <= remaining
                                    && buffer.position() == position + read);
                          }
                          require(
                              buffer.position() == before.size()
                                  && channel.size() == before.size());
                          return buffer.position();
                        });
                require(before.equals(inspect(p, false, maximum)));
                return count;
              });
      require(directory.equals(root.atDirectory(p -> inspect(p, true, maximum))));
      require(!Thread.currentThread().isInterrupted() && security.effectiveUid() == 0);
      return Arrays.copyOf(material, length);
    } finally {
      Arrays.fill(material, (byte) 0);
    }
  }

  private Metadata inspect(Path held, boolean directory, int maximum) throws IOException {
    Metadata m = EnvironmentInodePolicy.metadata(io.attributes(held));
    require(m.device() >= 0 && m.inode() > 0);
    require(m.mode() == (directory ? 0x4140 : 0x8100) && m.uid() == 0 && m.gid() == 0);
    require(
        directory
            ? m.links() >= 2 && m.size() >= 0
            : m.links() == 1 && m.size() >= 1 && m.size() <= maximum);
    byte[] acl = security.accessAcl(held, 44);
    require(acl != null && acl.length == 0 && security.readOnlyFilesystem(held));
    require("tmpfs".equals(io.filesystem(held)));
    return m;
  }

  static final class NativeIo implements Io {
    public Map<String, Object> attributes(Path held) throws IOException {
      return Files.readAttributes(
          held, "unix:mode,uid,gid,nlink,size,dev,ino,lastModifiedTime,ctime");
    }

    public SeekableByteChannel open(Path held) throws IOException {
      return Files.newByteChannel(held, StandardOpenOption.READ);
    }

    public String filesystem(Path held) throws IOException {
      return Files.getFileStore(held).type();
    }
  }
}
