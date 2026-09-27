package dev.codex.schubert.nk.batch.file;

import static dev.codex.schubert.nk.batch.file.EnvironmentInodePolicy.require;

import dev.codex.schubert.nk.api.maintenance.InspectorDbCredential;
import dev.codex.schubert.nk.batch.file.EnvironmentInodePolicy.Metadata;
import dev.codex.schubert.nk.storage.*;
import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.channels.SeekableByteChannel;
import java.nio.file.*;
import java.util.*;
import org.jspecify.annotations.NullMarked;

/**
 * Borrowed, fixed root morning LoadCredential only; never an ordinary service catalog extension.
 * Caller authenticates root Unit/boot and exact credential namespace before supplying its owner.
 * NK-OPS-001/DAT009/OPS009/UI251/SS341/3436.15/SSC094/PG311; PT-OPS-RBCR001..008.
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
    byte[] material = new byte[65537];
    try {
      require(!Thread.currentThread().isInterrupted() && security.effectiveUid() == 0);
      Metadata directory = root.atDirectory(p -> inspect(p, true));
      int length =
          root.atExistingEntryHandle(
              "db-batch",
              p -> {
                Metadata before = inspect(p, false);
                require(before.device() == directory.device());
                var channel = Objects.requireNonNull(io.open(p), "root credential channel");
                int count =
                    ResourceScope.use(
                        channel::close,
                        () -> {
                          require(channel.size() == before.size());
                          ByteBuffer buffer = ByteBuffer.wrap(material);
                          while (buffer.hasRemaining()) {
                            int position = buffer.position(), remaining = buffer.remaining();
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
                require(before.equals(inspect(p, false)));
                return count;
              });
      require(directory.equals(root.atDirectory(p -> inspect(p, true))));
      require(!Thread.currentThread().isInterrupted() && security.effectiveUid() == 0);
      return InspectorDbCredential.consume(Arrays.copyOf(material, length));
    } finally {
      Arrays.fill(material, (byte) 0);
    }
  }

  private Metadata inspect(Path held, boolean directory) throws IOException {
    Metadata m = EnvironmentInodePolicy.metadata(io.attributes(held));
    require(m.device() >= 0 && m.inode() > 0);
    require(m.mode() == (directory ? 040500 : 0100400) && m.uid() == 0 && m.gid() == 0);
    require(
        directory
            ? m.links() >= 2 && m.size() >= 0
            : m.links() == 1 && m.size() >= 1 && m.size() <= 65536);
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
