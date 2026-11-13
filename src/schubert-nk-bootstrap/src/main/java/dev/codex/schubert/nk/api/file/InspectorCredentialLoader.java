package dev.codex.schubert.nk.api.file;

import dev.codex.schubert.nk.api.maintenance.InspectorAesCredential;
import dev.codex.schubert.nk.api.maintenance.InspectorCredentialAccess;
import dev.codex.schubert.nk.api.maintenance.InspectorDbCredential;
import dev.codex.schubert.nk.storage.InodeSecurityCalls;
import dev.codex.schubert.nk.storage.OwnedTransferDirectory;
import dev.codex.schubert.nk.storage.ServiceCredentialId;
import dev.codex.schubert.nk.storage.StorageIoException;
import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.channels.FileChannel;
import java.nio.channels.SeekableByteChannel;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.nio.file.attribute.FileTime;
import java.util.Arrays;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import java.util.OptionalInt;
import java.util.concurrent.atomic.AtomicBoolean;
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;

/**
 * Borrowed credential root; parse only after bounded file IO and owned entry close succeed.
 * NK-DAT-001; DAT-009/OPS-009/FIL-006; UI212/241/251; SS311/343 6.4; QA-046/SSC-049/PG-D-134;
 * PT-DB-INBOX-129..140. SSC-081/PG281 additionally reuses the same held-inode/ACL/bounded read path
 * for the fixed Web/API ServiceCredentialId catalog; no caller filename is accepted.
 */
@NullMarked
public final class InspectorCredentialLoader {
  interface Io {
    Map<String, Object> attributes(Path held) throws IOException;

    SeekableByteChannel openReadOnly(Path held) throws IOException;
  }

  private final OwnedTransferDirectory root;
  private final InodeSecurityCalls security;
  private final InspectorCredentialAccess policy;
  private final Io io;

  public InspectorCredentialLoader(OwnedTransferDirectory root, InodeSecurityCalls security) {
    this(root, security, new NioIo());
  }

  InspectorCredentialLoader(OwnedTransferDirectory root, InodeSecurityCalls security, Io io) {
    this.root = Objects.requireNonNull(root, "credential root");
    this.security = Objects.requireNonNull(security, "inode security");
    this.io = Objects.requireNonNull(io, "credential IO");
    policy = new InspectorCredentialAccess(security.effectiveUid());
  }

  /** Caller owns returned material and root; missing current or any IO/close failure is fatal. */
  public Optional<InspectorAesCredential> load(AesCredentialFile credential)
      throws InspectorCredentialException {
    Objects.requireNonNull(credential, "credential ID");
    byte[] buffer = new byte[70];
    try {
      Snapshot before = root.atDirectory(this::directory);
      OptionalInt length =
          readOptional(credential.fileName(), credential.optional(), buffer, false);
      require(before.equals(root.atDirectory(this::directory)));
      if (length.isEmpty()) return Optional.empty();
      return Optional.of(InspectorAesCredential.consume(Arrays.copyOf(buffer, length.getAsInt())));
    } catch (IOException | IllegalArgumentException | UnsupportedOperationException failure) {
      if (!(failure instanceof IOException)) StorageIoException.preserveFatal(failure);
      throw new InspectorCredentialException();
    } finally {
      Arrays.fill(buffer, (byte) 0);
    }
  }

  /** Fixed mandatory password file; caller owns returned material. SS343 6.6/PT193..208. */
  public InspectorDbCredential loadDatabasePassword() throws InspectorCredentialException {
    byte[] buffer = new byte[65537];
    try {
      Snapshot before = root.atDirectory(this::directory);
      int length = readOptional("db-inbox-inspector", false, buffer, true).orElseThrow();
      require(before.equals(root.atDirectory(this::directory)));
      return InspectorDbCredential.consume(Arrays.copyOf(buffer, length));
    } catch (IOException | IllegalArgumentException | UnsupportedOperationException failure) {
      if (!(failure instanceof IOException)) StorageIoException.preserveFatal(failure);
      throw new InspectorCredentialException();
    } finally {
      Arrays.fill(buffer, (byte) 0);
    }
  }

  /**
   * Fixed backup-only .pgpass source; caller owns/clears raw bytes, never a Web/API catalog entry.
   * NK-OPS-001/BAK/OPS009/UI251/SS341 6.1/343 6.6/SSC090/PG305/BACKCRED001..008. Caller
   * authenticates the dedicated Unit/root and stages private tmpfs0600 for libpq.
   */
  public byte[] readBackupPgpass() throws InspectorCredentialException {
    return readBackupMaterial("backup-pgpass", 65536);
  }

  /**
   * Fixed nonsecret backup-only request; caller consumes/clears and validates its canonical codec.
   */
  public byte[] readBackupRequest() throws InspectorCredentialException {
    // SSC116: closed NKBACKUP1 or NKBACKUPVERIFY1, consumed by the typed worker codec.
    return readBackupMaterial("backup-request", 400);
  }

  /** SSC119: fixed root-issued LoadCredential copy, never a key or startup permit. */
  public byte[] readMaintenanceOwner() throws InspectorCredentialException {
    return readBackupMaterial("maintenance-owner", 1024);
  }

  /** SSC188: dedicated bootstrap Unit only; not an ordinary API/Web credential catalog ID. */
  public InspectorDbCredential readBootstrapUsername() throws InspectorCredentialException {
    return consumeBootstrap(readBackupMaterial("bootstrap-admin-username", 256));
  }

  /** Fixed private input; creation policy is applied by BootstrapAdminService, not this decoder. */
  public InspectorDbCredential readBootstrapPassword() throws InspectorCredentialException {
    return consumeBootstrap(readBackupMaterial("bootstrap-admin-password", 65536));
  }

  private static InspectorDbCredential consumeBootstrap(byte[] owned)
      throws InspectorCredentialException {
    try {
      return InspectorDbCredential.consume(owned);
    } catch (IllegalArgumentException invalid) {
      throw new InspectorCredentialException();
    }
  }

  private byte[] readBackupMaterial(String name, int maximum) throws InspectorCredentialException {
    byte[] buffer = new byte[maximum + 1];
    try {
      Snapshot before = root.atDirectory(this::directory);
      int length =
          readOptional(name, false, buffer, true, before.metadata().device()).orElseThrow();
      require(length <= maximum);
      require(before.equals(root.atDirectory(this::directory)));
      return Arrays.copyOf(buffer, length);
    } catch (IOException | IllegalArgumentException | UnsupportedOperationException failure) {
      if (!(failure instanceof IOException)) StorageIoException.preserveFatal(failure);
      throw new InspectorCredentialException();
    } finally {
      Arrays.fill(buffer, (byte) 0);
    }
  }

  /** Fixed Web/API ID only; returned raw bytes are exclusively caller-owned and must be cleared. */
  byte[] readService(ServiceCredentialId credential) throws InspectorCredentialException {
    Objects.requireNonNull(credential, "service credential ID");
    boolean password = credential.kind() == ServiceCredentialId.Kind.PASSWORD;
    byte[] buffer = new byte[password ? 65537 : 70];
    try {
      Snapshot before = root.atDirectory(this::directory);
      int length =
          readOptional(credential.fileName(), false, buffer, password, before.metadata().device())
              .orElseThrow();
      require(before.equals(root.atDirectory(this::directory)));
      return Arrays.copyOf(buffer, length);
    } catch (IOException | IllegalArgumentException | UnsupportedOperationException failure) {
      if (!(failure instanceof IOException)) StorageIoException.preserveFatal(failure);
      throw new InspectorCredentialException();
    } finally {
      Arrays.fill(buffer, (byte) 0);
    }
  }

  private OptionalInt readOptional(
      String fileName, boolean optional, byte[] buffer, boolean database)
      throws StorageIoException {
    return readOptional(fileName, optional, buffer, database, -1);
  }

  private OptionalInt readOptional(
      String fileName, boolean optional, byte[] buffer, boolean database, long expectedDevice)
      throws StorageIoException {
    // Operation-local marker: missing after entry acquisition/inside IO/at close is not optional.
    var entered = new AtomicBoolean();
    try {
      int length =
          root.atExistingEntryHandle(
              fileName,
              held -> {
                entered.set(true);
                return readFile(held, buffer, database, expectedDevice);
              });
      return OptionalInt.of(length);
    } catch (StorageIoException failure) {
      if (failure.reason() == StorageIoException.Reason.MISSING && !entered.get() && optional) {
        StorageIoException.preserveFatal(failure);
        return OptionalInt.empty();
      }
      throw failure;
    }
  }

  private int readFile(Path held, byte[] bytes, boolean database, long expectedDevice)
      throws IOException {
    Snapshot before = file(held, database);
    if (expectedDevice >= 0) require(before.metadata().device() == expectedDevice);
    int expectedSize = (int) before.metadata().size();
    ByteBuffer buffer = ByteBuffer.wrap(bytes);
    try (var channel = io.openReadOnly(held)) {
      require(channel.size() == expectedSize);
      while (buffer.hasRemaining()) {
        int position = buffer.position();
        int remaining = buffer.remaining();
        int count = channel.read(buffer);
        if (count == -1) break;
        require(count > 0 && count <= remaining && buffer.position() == position + count);
      }
      require(buffer.position() == expectedSize);
      require(channel.size() == expectedSize);
    }
    require(before.equals(file(held, database)));
    return expectedSize;
  }

  private Snapshot directory(Path held) throws IOException {
    Metadata metadata = metadata(io.attributes(held));
    require((metadata.mode() & 0xf000) == 0x4000);
    boolean readonly = security.readOnlyFilesystem(held);
    policy.requireDirectory(
        metadata.mode(), metadata.uid(), metadata.links(), readonly, security.accessAcl(held, 44));
    return new Snapshot(metadata, readonly);
  }

  private Snapshot file(Path held, boolean database) throws IOException {
    Metadata metadata = metadata(io.attributes(held));
    // Must precede native path-following getxattr/statvfs and any content open on O_PATH symlinks.
    require((metadata.mode() & 0xf000) == 0x8000);
    boolean readonly = security.readOnlyFilesystem(held);
    if (database)
      policy.requireDatabaseFile(
          metadata.mode(),
          metadata.uid(),
          metadata.links(),
          metadata.size(),
          readonly,
          security.accessAcl(held, 44));
    else
      policy.requireAesFile(
          metadata.mode(),
          metadata.uid(),
          metadata.links(),
          metadata.size(),
          readonly,
          security.accessAcl(held, 44));
    return new Snapshot(metadata, readonly);
  }

  private static Metadata metadata(@Nullable Map<String, Object> attributes)
      throws InspectorCredentialException {
    if (attributes == null
        || !(attributes.get("mode") instanceof Integer mode)
        || !(attributes.get("uid") instanceof Integer uid)
        || !(attributes.get("gid") instanceof Integer gid)
        || !(attributes.get("nlink") instanceof Integer links)
        || !(attributes.get("size") instanceof Long size)
        || !(attributes.get("dev") instanceof Long device)
        || !(attributes.get("ino") instanceof Long inode)
        || !(attributes.get("lastModifiedTime") instanceof FileTime modified)
        || !(attributes.get("ctime") instanceof FileTime changed))
      throw new InspectorCredentialException();
    return new Metadata(
        mode, Integer.toUnsignedLong(uid), gid, links, size, device, inode, modified, changed);
  }

  private static void require(boolean accepted) throws InspectorCredentialException {
    if (!accepted) throw new InspectorCredentialException();
  }

  private record Metadata(
      int mode,
      long uid,
      int gid,
      int links,
      long size,
      long device,
      long inode,
      FileTime modified,
      FileTime changed) {}

  private record Snapshot(Metadata metadata, boolean readonly) {}

  static final class NioIo implements Io {
    @Override
    public Map<String, Object> attributes(Path held) throws IOException {
      return Files.readAttributes(
          held, "unix:mode,uid,gid,nlink,size,dev,ino,lastModifiedTime,ctime");
    }

    @Override
    public SeekableByteChannel openReadOnly(Path held) throws IOException {
      return FileChannel.open(held, StandardOpenOption.READ);
    }
  }
}
