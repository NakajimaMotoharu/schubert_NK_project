package dev.codex.schubert.nk.batch.file;

import static dev.codex.schubert.nk.batch.file.EnvironmentInodePolicy.require;
import static dev.codex.schubert.nk.batch.file.EnvironmentInodePolicy.unavailable;

import dev.codex.schubert.nk.batch.backup.BackupFileDigest;
import dev.codex.schubert.nk.batch.backup.BackupManifest;
import dev.codex.schubert.nk.batch.file.EnvironmentInodePolicy.Metadata;
import dev.codex.schubert.nk.batch.platform.BackupWorkerRequest;
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
import java.util.Optional;
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
  private static final int FILE_TYPE_MASK = 0xf000;
  private static final int REGULAR_FILE_TYPE = 0x8000;

  private static final java.lang.String LITERAL_SCHUBERT_NK_DUMP = "schubert_nk.dump";

  private static final java.lang.String LITERAL_CONFIG_TAR = "config.tar";

  private static final java.lang.String LITERAL_CREDENTIALS_TAR_AGE = "credentials.tar.age";

  private static final String MANIFEST = "MANIFEST.json";
  private static final List<String> RETAINED_NAMES =
      List.of(MANIFEST, LITERAL_SCHUBERT_NK_DUMP, LITERAL_CONFIG_TAR, LITERAL_CREDENTIALS_TAR_AGE);
  private static final Set<String> REQUIRED = Set.copyOf(RETAINED_NAMES);
  private static final long DEADLINE = 1_800_000_000_000L;
  private final java.util.concurrent.locks.ReentrantLock lock =
      new java.util.concurrent.locks.ReentrantLock();
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

  /** Package-only durability on the same admitted, verified inode; SSC066/BAT258..273. */
  @FunctionalInterface
  interface Force {
    void apply(Path held, long expectedSize) throws IOException;
  }

  /** Internal immutable durability proof, never a public file capability. BUG204/YKT160. */
  record BundleSnapshot(
      BackupFileDigest manifest,
      Metadata directory,
      Map<String, Metadata> files,
      Map<String, BackupFileDigest> contents) {
    BundleSnapshot {
      Objects.requireNonNull(manifest, "manifest digest");
      Objects.requireNonNull(directory, "directory snapshot");
      files = Map.copyOf(files);
      contents = Map.copyOf(contents);
    }

    boolean samePublished(BundleSnapshot other) {
      // Role-fixed mode/uid/gid were checked in both captures; only directory ctime may change.
      return manifest.equals(other.manifest)
          && directory.device() == other.directory.device()
          && directory.inode() == other.directory.inode()
          && directory.links() == other.directory.links()
          && directory.size() == other.directory.size()
          && directory.modified().equals(other.directory.modified())
          && files.equals(other.files)
          && contents.equals(other.contents);
    }
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
    return verifyAt(expected, expected.directoryName(), null, null).manifest();
  }

  /**
   * Actual content observations only: caller still must publish/verify the manifest and DB pair.
   */
  public record PendingDigests(
      BackupFileDigest dump, BackupFileDigest configuration, BackupFileDigest credentials) {
    public PendingDigests {
      Objects.requireNonNull(dump, "observed dump");
      Objects.requireNonNull(configuration, "observed configuration");
      Objects.requireNonNull(credentials, "observed encrypted credentials");
    }
  }

  /** Fixed request-derived pending bundle, reusing the exact verifier inode/read policy. SSC110. */
  public PendingDigests observePending(BackupWorkerRequest request) throws StorageIoException {
    Objects.requireNonNull(request, "owned backup request");
    lock.lock();
    try {
      long started = clock.getAsLong();
      byte[] buffer = new byte[65536];
      var pendingNames =
          List.of(LITERAL_SCHUBERT_NK_DUMP, LITERAL_CONFIG_TAR, LITERAL_CREDENTIALS_TAR_AGE);
      try {
        require(security.effectiveUid() == 0);
        Metadata parent = directory(root, started);
        var result =
            ResourceScope.acquire(
                () -> root.openExistingChild(request.directoryName() + ".part"),
                OwnedTransferDirectory::close,
                child -> {
                  Metadata initial = directory(child, started);
                  require(initial.device() == parent.device());
                  names(child, started, Set.copyOf(pendingNames));
                  Map<String, Metadata> snapshots = new HashMap<>();
                  Map<String, BackupFileDigest> observed = new HashMap<>();
                  for (String name : pendingNames) {
                    guard(started);
                    child.atExistingEntryHandle(
                        name,
                        held -> {
                          guard(started);
                          Metadata value = metadata(io.attributes(held));
                          require(value.size() >= 0);
                          long owner = name.equals(LITERAL_SCHUBERT_NK_DUMP) ? uid : 0;
                          long group = name.equals(LITERAL_SCHUBERT_NK_DUMP) ? gid : 0;
                          var claim = new FileClaim(value.size(), "", owner, group);
                          Metadata before =
                              capture(held, false, owner, group, value.size(), started);
                          require(value.equals(before) && before.device() == initial.device());
                          snapshots.put(name, before);
                          observed.put(
                              name, read(held, name, claim, new byte[0], buffer, started, false));
                          require(
                              before.equals(
                                  capture(held, false, owner, group, value.size(), started)));
                          return Boolean.TRUE;
                        });
                  }
                  for (String name : pendingNames) {
                    child.atExistingEntryHandle(
                        name,
                        held -> {
                          Metadata before = Objects.requireNonNull(snapshots.get(name));
                          require(
                              before.equals(
                                  capture(
                                      held,
                                      false,
                                      before.uid(),
                                      before.gid(),
                                      before.size(),
                                      started)));
                          return Boolean.TRUE;
                        });
                  }
                  names(child, started, Set.copyOf(pendingNames));
                  require(initial.equals(directory(child, started)));
                  ResourceScope.acquire(
                      () -> root.openExistingChild(request.directoryName() + ".part"),
                      OwnedTransferDirectory::close,
                      rebound -> {
                        require(initial.equals(directory(rebound, started)));
                        return Boolean.TRUE;
                      });
                  return new PendingDigests(
                      Objects.requireNonNull(observed.get(LITERAL_SCHUBERT_NK_DUMP)),
                      Objects.requireNonNull(observed.get(LITERAL_CONFIG_TAR)),
                      Objects.requireNonNull(observed.get(LITERAL_CREDENTIALS_TAR_AGE)));
                });
        require(parent.equals(directory(root, started)) && security.effectiveUid() == 0);
        guard(started);
        return result;
      } catch (IOException | DirectoryIteratorException | UnsupportedOperationException failure) {
        throw unavailable();
      } finally {
        Arrays.fill(buffer, (byte) 0);
      }
    } finally {
      lock.unlock();
    }
  }

  BundleSnapshot verifyWithin(BackupManifest expected, long started) throws StorageIoException {
    Objects.requireNonNull(expected, "trusted manifest");
    return verifyAt(expected, expected.directoryName(), null, started);
  }

  /** Known digest disagreement only after all normal IO/close/identity checks have completed. */
  Optional<BundleSnapshot> inspectRetention(BackupManifest expected, long started)
      throws StorageIoException {
    Objects.requireNonNull(expected);
    if (!retentionSizesAgree(expected, started)) return Optional.empty();
    BundleSnapshot actual = verifyAt(expected, expected.directoryName(), null, started, false);
    return Objects.requireNonNull(actual.contents().get(LITERAL_SCHUBERT_NK_DUMP))
                .equals(expected.dump())
            && Objects.requireNonNull(actual.contents().get(LITERAL_CONFIG_TAR))
                .equals(expected.configuration())
            && Objects.requireNonNull(actual.contents().get(LITERAL_CREDENTIALS_TAR_AGE))
                .equals(expected.credentials())
        ? Optional.of(actual)
        : Optional.empty();
  }

  private boolean retentionSizesAgree(BackupManifest expected, long started)
      throws StorageIoException {
    byte[] canonical = BackupManifestCodec.encode(expected);
    try {
      require(security.effectiveUid() == 0);
      Metadata parent = directory(root, started);
      Map<String, Long> sizes =
          Map.of(
              MANIFEST,
              (long) canonical.length,
              LITERAL_SCHUBERT_NK_DUMP,
              expected.dump().size(),
              LITERAL_CONFIG_TAR,
              expected.configuration().size(),
              LITERAL_CREDENTIALS_TAR_AGE,
              expected.credentials().size());
      boolean same =
          ResourceScope.acquire(
              () -> root.openExistingChild(expected.directoryName()),
              OwnedTransferDirectory::close,
              child -> {
                Metadata initial = directory(child, started);
                require(initial.device() == parent.device());
                boolean matching = true;
                for (String name : RETAINED_NAMES) {
                  boolean actual =
                      child.atExistingEntryHandle(
                          name,
                          held -> {
                            guard(started);
                            Metadata raw = metadata(io.attributes(held));
                            require(
                                raw.size() >= 0
                                    && raw.device() == initial.device()
                                    && raw.inode() > 0);
                            if ((raw.mode() & FILE_TYPE_MASK) != REGULAR_FILE_TYPE) {
                              require(raw.equals(metadata(io.attributes(held))));
                              guard(started);
                              return false;
                            }
                            long fileUid = name.equals(LITERAL_SCHUBERT_NK_DUMP) ? uid : 0;
                            long fileGid = name.equals(LITERAL_SCHUBERT_NK_DUMP) ? gid : 0;
                            require(
                                raw.equals(
                                    capture(held, false, fileUid, fileGid, raw.size(), started)));
                            guard(started);
                            return raw.size() == Objects.requireNonNull(sizes.get(name));
                          });
                  matching &= actual;
                }
                require(initial.equals(directory(child, started)));
                return matching;
              });
      require(parent.equals(directory(root, started)));
      require(security.effectiveUid() == 0);
      guard(started);
      return same;
    } catch (IOException | DirectoryIteratorException | UnsupportedOperationException failure) {
      throw unavailable();
    } finally {
      Arrays.fill(canonical, (byte) 0);
    }
  }

  /** SSC133/ISSRET: fixed files, retained inode and empty-child removal, never recursive delete. */
  void removeRetained(
      BackupManifest expected,
      BundleSnapshot admitted,
      long started,
      dev.codex.schubert.nk.bootstrap.MaintenanceOwnerFrame.Guard owner)
      throws IOException {
    Objects.requireNonNull(expected);
    Objects.requireNonNull(admitted);
    Objects.requireNonNull(owner);
    lock.lock();
    try {
      owner.check();
      require(admitted.equals(verifyWithin(expected, started)));
      ResourceScope.acquire(
          () -> root.openExistingChild(expected.directoryName()),
          OwnedTransferDirectory::close,
          child -> {
            require(admitted.directory().equals(directory(child, started)));
            for (String name :
                List.of(
                    LITERAL_SCHUBERT_NK_DUMP,
                    LITERAL_CONFIG_TAR,
                    LITERAL_CREDENTIALS_TAR_AGE,
                    MANIFEST)) {
              owner.check();
              guard(started);
              Metadata original = Objects.requireNonNull(admitted.files().get(name));
              child.atExistingEntryHandle(
                  name,
                  held -> {
                    require(
                        original.equals(
                            capture(
                                held,
                                false,
                                original.uid(),
                                original.gid(),
                                original.size(),
                                started)));
                    return Boolean.TRUE;
                  });
              owner.check();
              require(sameDirectoryInode(admitted.directory(), directory(child, started)));
              child.unlinkEntry(name);
              guard(started);
            }
            owner.check();
            require(sameDirectoryInode(admitted.directory(), directory(child, started)));
            child.atDirectory(
                held -> {
                  return ResourceScope.acquire(
                      () -> {
                        var stream = io.openNames(held);
                        if (stream == null) throw unavailable();
                        return stream;
                      },
                      DirectoryStream::close,
                      stream -> {
                        guard(started);
                        require(!stream.iterator().hasNext());
                        guard(started);
                        return Boolean.TRUE;
                      });
                });
            ResourceScope.acquire(
                () -> root.openExistingChild(expected.directoryName()),
                OwnedTransferDirectory::close,
                rebound -> {
                  require(sameDirectoryInode(admitted.directory(), directory(rebound, started)));
                  return Boolean.TRUE;
                });
            owner.check();
            root.removeEmptyChild(expected.directoryName());
            guard(started);
            owner.check();
            return Boolean.TRUE;
          });
    } finally {
      lock.unlock();
    }
  }

  static boolean sameDirectoryInode(Metadata before, Metadata after) {
    return before.device() == after.device()
        && before.inode() == after.inode()
        && before.mode() == after.mode()
        && before.uid() == after.uid()
        && before.gid() == after.gid();
  }

  BundleSnapshot forcePending(BackupManifest expected, Force force, long started)
      throws StorageIoException {
    Objects.requireNonNull(expected, "trusted manifest");
    Objects.requireNonNull(force, "held inode force");
    return verifyAt(expected, expected.directoryName() + ".part", force, started);
  }

  private BundleSnapshot verifyAt(
      BackupManifest expected,
      String directoryName,
      @Nullable Force force,
      @Nullable Long suppliedStart)
      throws StorageIoException {
    return verifyAt(expected, directoryName, force, suppliedStart, true);
  }

  private BundleSnapshot verifyAt(
      BackupManifest expected,
      String directoryName,
      @Nullable Force force,
      @Nullable Long suppliedStart,
      boolean compareClaims)
      throws StorageIoException {
    lock.lock();
    try {
      long started = suppliedStart == null ? clock.getAsLong() : suppliedStart;
      byte[] buffer = new byte[65536];
      byte[] canonical = BackupManifestCodec.encode(expected);
      try {
        guard(started);
        require(security.effectiveUid() == 0);
        Metadata parent = directory(root, started);
        guard(started);
        BundleSnapshot result =
            ResourceScope.acquire(
                () -> root.openExistingChild(directoryName),
                OwnedTransferDirectory::close,
                child -> {
                  Metadata initial = directory(child, started);
                  require(initial.device() == parent.device());
                  names(child, started);
                  Map<String, FileClaim> claims =
                      Map.of(
                          MANIFEST,
                          new FileClaim(canonical.length, "", 0, 0),
                          LITERAL_SCHUBERT_NK_DUMP,
                          new FileClaim(expected.dump().size(), expected.dump().sha256(), uid, gid),
                          LITERAL_CONFIG_TAR,
                          new FileClaim(
                              expected.configuration().size(),
                              expected.configuration().sha256(),
                              0,
                              0),
                          LITERAL_CREDENTIALS_TAR_AGE,
                          new FileClaim(
                              expected.credentials().size(),
                              expected.credentials().sha256(),
                              0,
                              0));
                  Map<String, Metadata> snapshots = new HashMap<>();
                  Map<String, BackupFileDigest> observed = new HashMap<>();
                  for (String name : RETAINED_NAMES) {
                    FileClaim claim = Objects.requireNonNull(claims.get(name));
                    guard(started);
                    child.atExistingEntryHandle(
                        name,
                        held -> {
                          Metadata before =
                              capture(held, false, claim.uid(), claim.gid(), claim.size(), started);
                          require(before.device() == initial.device());
                          snapshots.put(name, before);
                          observed.put(
                              name,
                              read(held, name, claim, canonical, buffer, started, compareClaims));
                          if (force != null) {
                            guard(started);
                            force.apply(held, claim.size());
                            guard(started);
                          }
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
                  for (String name : RETAINED_NAMES) {
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
                  ResourceScope.acquire(
                      () -> root.openExistingChild(directoryName),
                      OwnedTransferDirectory::close,
                      rebound -> {
                        require(initial.equals(directory(rebound, started)));
                        return Boolean.TRUE;
                      });
                  guard(started);
                  if (force != null) {
                    child.sync();
                    guard(started);
                  }
                  return new BundleSnapshot(
                      Objects.requireNonNull(observed.get(MANIFEST)), initial, snapshots, observed);
                });
        guard(started);
        require(parent.equals(directory(root, started)));
        require(security.effectiveUid() == 0);
        guard(started);
        return result;
      } catch (IOException | DirectoryIteratorException | UnsupportedOperationException failure) {
        if (force != null && failure instanceof StorageIoException storage)
          throw new StorageIoException(storage.reason());
        throw unavailable();
      } finally {
        Arrays.fill(buffer, (byte) 0);
        Arrays.fill(canonical, (byte) 0);
      }
    } finally {
      lock.unlock();
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
        value.mode() == (directory ? 0x41c0 : 0x8180)
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
    names(directory, started, REQUIRED);
  }

  private void names(OwnedTransferDirectory directory, long started, Set<String> required)
      throws StorageIoException {
    guard(started);
    directory.atDirectory(
        held -> {
          guard(started);
          ResourceScope.acquire(
              () -> {
                DirectoryStream<Path> stream = io.openNames(held);
                if (stream == null) throw unavailable();
                return stream;
              },
              DirectoryStream::close,
              stream -> {
                guard(started);
                Set<String> names = new HashSet<>();
                for (Path child : stream) {
                  guard(started);
                  require(child != null && held.equals(child.getParent()));
                  require(names.add(held.relativize(child).toString()) && names.size() <= 4);
                  guard(started);
                }
                require(names.equals(required));
                guard(started);
                return Boolean.TRUE;
              });
          guard(started);
          return Boolean.TRUE;
        });
    guard(started);
  }

  private BackupFileDigest read(
      Path held,
      String name,
      FileClaim claim,
      byte[] canonical,
      byte[] bytes,
      long started,
      boolean compareClaims)
      throws IOException, NoSuchAlgorithmException {
    guard(started);
    MessageDigest hash = Objects.requireNonNull(digests.create(), "backup digest");
    guard(started);
    return ResourceScope.acquire(
        () -> {
          SeekableByteChannel opened = io.open(held);
          if (opened == null) throw unavailable();
          return opened;
        },
        SeekableByteChannel::close,
        opened -> {
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
          if (compareClaims && !name.equals(MANIFEST)) require(actual.equals(claim.hash()));
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
