package dev.codex.schubert.nk.batch.file;

import static dev.codex.schubert.nk.batch.file.EnvironmentInodePolicy.require;
import static dev.codex.schubert.nk.batch.file.EnvironmentInodePolicy.unavailable;

import dev.codex.schubert.nk.batch.backup.BackupFileDigest;
import dev.codex.schubert.nk.batch.backup.BackupManifest;
import dev.codex.schubert.nk.batch.file.EnvironmentInodePolicy.Metadata;
import dev.codex.schubert.nk.storage.InodeSecurityCalls;
import dev.codex.schubert.nk.storage.OwnedTransferDirectory;
import dev.codex.schubert.nk.storage.ResourceScope;
import dev.codex.schubert.nk.storage.StorageIoException;
import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.channels.FileChannel;
import java.nio.channels.SeekableByteChannel;
import java.nio.file.DirectoryIteratorException;
import java.nio.file.DirectoryStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.nio.file.attribute.FileTime;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.Arrays;
import java.util.HashMap;
import java.util.HashSet;
import java.util.HexFormat;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import java.util.function.LongSupplier;
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;

/**
 * Read-only agreement with trusted claims, not backup creation/authentication/DB success.
 * NK-BAT-001/BAK/BKO/UI251/SS341 6.5/343 5.3; SSC059/PG166; BAT194..209.
 */
@NullMarked
public final class BackupArtifactVerifier {
  private static final String MANIFEST = "MANIFEST.json";
  private static final List<String> NAMES =
      List.of(MANIFEST, "schubert_nk.dump", "config.tar", "credentials.tar.age");
  private static final Set<String> REQUIRED = Set.copyOf(NAMES);
  private static final long DEADLINE = 1_800_000_000_000L;
  private final Object lock = new Object();
  private final OwnedTransferDirectory root;
  private final InodeSecurityCalls security;
  private final long uid;
  private final long gid;
  private final Io io;
  private final Digests digests;
  private final LongSupplier clock;

  interface Io {
    @Nullable Map<String, Object> attributes(Path held) throws IOException;

    @Nullable SeekableByteChannel open(Path held) throws IOException;

    @Nullable DirectoryStream<Path> openNames(Path held) throws IOException;
  }

  @FunctionalInterface
  interface Digests {
    MessageDigest create() throws NoSuchAlgorithmException;
  }

  public BackupArtifactVerifier(
      OwnedTransferDirectory root, InodeSecurityCalls security, long uid, long gid) {
    this(root, security, uid, gid, new NioIo(), System::nanoTime);
  }

  BackupArtifactVerifier(
      OwnedTransferDirectory root,
      InodeSecurityCalls security,
      long uid,
      long gid,
      Io io,
      LongSupplier clock) {
    this(root, security, uid, gid, io, () -> MessageDigest.getInstance("SHA-256"), clock);
  }

  BackupArtifactVerifier(
      OwnedTransferDirectory root,
      InodeSecurityCalls security,
      long uid,
      long gid,
      Io io,
      Digests digests,
      LongSupplier clock) {
    this.root = Objects.requireNonNull(root, "backup root");
    this.security = Objects.requireNonNull(security, "inode security");
    this.io = Objects.requireNonNull(io, "backup IO");
    this.digests = Objects.requireNonNull(digests, "backup digest");
    this.clock = Objects.requireNonNull(clock, "backup clock");
    if (uid < 1 || uid > 0xffffffffL || gid < 1 || gid > 0xffffffffL)
      throw new IllegalArgumentException("invalid backup owner");
    this.uid = uid;
    this.gid = gid;
  }

  public BackupFileDigest verify(BackupManifest expected) throws StorageIoException {
    Objects.requireNonNull(expected, "trusted manifest");
    synchronized (lock) {
      long started = clock.getAsLong();
      byte[] buffer = new byte[65536];
      byte[] canonical = BackupManifestCodec.encode(expected);
      try {
        guard(started);
        require(security.effectiveUid() == 0);
        Metadata parent = directory(root, started);
        guard(started);
        var child = root.openExistingChild(expected.directoryName());
        BackupFileDigest result =
            ResourceScope.use(
                child::close,
                () -> {
                  Metadata initial = directory(child, started);
                  require(initial.device() == parent.device());
                  names(child, started);
                  Map<String, FileClaim> claims =
                      Map.of(
                          MANIFEST,
                          new FileClaim(canonical.length, "", 0, 0),
                          "schubert_nk.dump",
                          new FileClaim(expected.dump().size(), expected.dump().sha256(), uid, gid),
                          "config.tar",
                          new FileClaim(
                              expected.configuration().size(),
                              expected.configuration().sha256(),
                              0,
                              0),
                          "credentials.tar.age",
                          new FileClaim(
                              expected.credentials().size(),
                              expected.credentials().sha256(),
                              0,
                              0));
                  Map<String, Metadata> snapshots = new HashMap<>();
                  Map<String, BackupFileDigest> observed = new HashMap<>();
                  for (String name : NAMES) {
                    FileClaim claim = Objects.requireNonNull(claims.get(name));
                    guard(started);
                    child.atExistingEntryHandle(
                        name,
                        held -> {
                          Metadata before =
                              capture(held, false, claim.uid(), claim.gid(), claim.size(), started);
                          require(before.device() == initial.device());
                          snapshots.put(name, before);
                          observed.put(name, read(held, name, claim, canonical, buffer, started));
                          require(
                              before.equals(
                                  capture(
                                      held,
                                      false,
                                      claim.uid(),
                                      claim.gid(),
                                      claim.size(),
                                      started)));
                          return Boolean.TRUE;
                        });
                    guard(started);
                  }
                  for (String name : NAMES) {
                    FileClaim claim = Objects.requireNonNull(claims.get(name));
                    guard(started);
                    child.atExistingEntryHandle(
                        name,
                        held -> {
                          require(
                              Objects.requireNonNull(snapshots.get(name))
                                  .equals(
                                      capture(
                                          held,
                                          false,
                                          claim.uid(),
                                          claim.gid(),
                                          claim.size(),
                                          started)));
                          return Boolean.TRUE;
                        });
                    guard(started);
                  }
                  names(child, started);
                  require(initial.equals(directory(child, started)));
                  guard(started);
                  var rebound = root.openExistingChild(expected.directoryName());
                  ResourceScope.use(
                      rebound::close,
                      () -> {
                        require(initial.equals(directory(rebound, started)));
                        return Boolean.TRUE;
                      });
                  guard(started);
                  return Objects.requireNonNull(observed.get(MANIFEST));
                });
        guard(started);
        require(parent.equals(directory(root, started)));
        require(security.effectiveUid() == 0);
        guard(started);
        return result;
      } catch (IOException | DirectoryIteratorException | UnsupportedOperationException failure) {
        throw unavailable();
      } finally {
        Arrays.fill(buffer, (byte) 0);
        Arrays.fill(canonical, (byte) 0);
      }
    }
  }

  private Metadata directory(OwnedTransferDirectory directory, long started)
      throws StorageIoException {
    guard(started);
    Metadata value = directory.atDirectory(held -> capture(held, true, uid, gid, 0, started));
    guard(started);
    return value;
  }

  private Metadata capture(
      Path held, boolean directory, long owner, long group, long size, long started)
      throws IOException {
    guard(started);
    Metadata value = metadata(io.attributes(held));
    guard(started);
    require(
        value.mode() == (directory ? 040700 : 0100600)
            && value.uid() == owner
            && value.gid() == group);
    if (directory) require(value.links() >= 2 && value.size() >= 0);
    else require(value.links() == 1 && value.size() == size);
    guard(started);
    byte[] acl = security.accessAcl(held, 44);
    guard(started);
    require(acl != null && acl.length == 0);
    guard(started);
    require(!security.readOnlyFilesystem(held));
    guard(started);
    return value;
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

  private void names(OwnedTransferDirectory directory, long started) throws StorageIoException {
    guard(started);
    directory.atDirectory(
        held -> {
          guard(started);
          DirectoryStream<Path> stream = io.openNames(held);
          if (stream == null) throw unavailable();
          ResourceScope.use(
              stream,
              () -> {
                guard(started);
                Set<String> names = new HashSet<>();
                for (Path child : stream) {
                  guard(started);
                  require(child != null && held.equals(child.getParent()));
                  require(names.add(held.relativize(child).toString()) && names.size() <= 4);
                  guard(started);
                }
                require(names.equals(REQUIRED));
                guard(started);
                return Boolean.TRUE;
              });
          guard(started);
          return Boolean.TRUE;
        });
    guard(started);
  }

  private BackupFileDigest read(
      Path held, String name, FileClaim claim, byte[] canonical, byte[] bytes, long started)
      throws IOException, NoSuchAlgorithmException {
    guard(started);
    MessageDigest hash = Objects.requireNonNull(digests.create(), "backup digest");
    guard(started);
    SeekableByteChannel opened = io.open(held);
    if (opened == null) throw unavailable();
    return ResourceScope.use(
        opened,
        () -> {
          SeekableByteChannel channel = opened;
          guard(started);
          require(channel.size() == claim.size());
          guard(started);
          ByteBuffer buffer = ByteBuffer.wrap(bytes);
          long remaining = claim.size();
          while (remaining > 0) {
            guard(started);
            buffer.clear().limit((int) Math.min(remaining, bytes.length));
            int limit = buffer.limit();
            int read = channel.read(buffer);
            guard(started);
            require(read > 0 && read <= limit && buffer.position() == read);
            buffer.flip();
            if (name.equals(MANIFEST)) {
              int offset = (int) (claim.size() - remaining);
              for (int i = 0; i < read; i++) require(buffer.get(i) == canonical[offset + i]);
            }
            hash.update(buffer);
            guard(started);
            remaining -= read;
          }
          buffer.clear().limit(1);
          guard(started);
          require(channel.read(buffer) == -1 && buffer.position() == 0);
          guard(started);
          require(channel.size() == claim.size());
          guard(started);
          byte[] digest = hash.digest();
          require(digest != null && digest.length == 32);
          String actual = HexFormat.of().formatHex(digest);
          if (!name.equals(MANIFEST)) require(actual.equals(claim.hash()));
          guard(started);
          return new BackupFileDigest(claim.size(), actual);
        });
  }

  private void guard(long started) throws StorageIoException {
    if (Thread.currentThread().isInterrupted()) throw unavailable();
    long elapsed = clock.getAsLong() - started;
    // BUG186/YKT146: a final clock read must not hide a concurrently delivered interrupt.
    if (Thread.currentThread().isInterrupted()) throw unavailable();
    require(elapsed >= 0 && elapsed < DEADLINE);
  }

  private record FileClaim(long size, String hash, long uid, long gid) {}

  static final class NioIo implements Io {
    @Override
    public Map<String, Object> attributes(Path held) throws IOException {
      return Files.readAttributes(
          held, "unix:mode,uid,gid,nlink,size,dev,ino,lastModifiedTime,ctime");
    }

    @Override
    public SeekableByteChannel open(Path held) throws IOException {
      return FileChannel.open(held, StandardOpenOption.READ);
    }

    @Override
    public DirectoryStream<Path> openNames(Path held) throws IOException {
      return Files.newDirectoryStream(held);
    }
  }
}
