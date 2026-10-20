package dev.codex.schubert.nk.batch.file;

import static dev.codex.schubert.nk.batch.file.EnvironmentInodePolicy.require;
import static dev.codex.schubert.nk.batch.file.EnvironmentInodePolicy.unavailable;

import dev.codex.schubert.nk.batch.backup.BackupManifest;
import dev.codex.schubert.nk.batch.file.EnvironmentInodePolicy.Metadata;
import dev.codex.schubert.nk.batch.platform.CleanupWorkerRequest;
import dev.codex.schubert.nk.batch.repository.BatchRun;
import dev.codex.schubert.nk.batch.repository.BatchStepAttempt;
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
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
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
 * Root-owned claims at this observation, not generation, archive validation or DB success.
 * NK-BAT-001/BAK/BKO/OPS009/UI251/SS341 6.7/343 5.3; SSC062/PG169; BAT226..241. Caller retains
 * admitted backup root, OS exclusion and authoritative complete handles.
 */
@NullMarked
public final class BackupManifestReader {
  private static final String NAME = "MANIFEST.json";
  private static final long DEADLINE = 1_800_000_000_000L;
  private final java.util.concurrent.locks.ReentrantLock lock =
      new java.util.concurrent.locks.ReentrantLock();
  private final OwnedTransferDirectory root;
  private final InodeSecurityCalls security;
  private final long uid;
  private final long gid;
  private final Io io;
  private final LongSupplier clock;
  private final Digests digests;

  @FunctionalInterface
  interface Digests {
    MessageDigest create() throws NoSuchAlgorithmException;
  }

  interface Io {
    @Nullable Map<String, Object> attributes(Path held) throws IOException;

    @Nullable SeekableByteChannel open(Path held) throws IOException;

    @Nullable DirectoryStream<Path> openNames(Path held) throws IOException;
  }

  public BackupManifestReader(
      OwnedTransferDirectory root, InodeSecurityCalls security, long uid, long gid) {
    this(root, security, uid, gid, new NioIo(), System::nanoTime);
  }

  BackupManifestReader(
      OwnedTransferDirectory root,
      InodeSecurityCalls security,
      long uid,
      long gid,
      Io io,
      LongSupplier clock) {
    this(root, security, uid, gid, io, clock, () -> MessageDigest.getInstance("SHA-256"));
  }

  BackupManifestReader(
      OwnedTransferDirectory root,
      InodeSecurityCalls security,
      long uid,
      long gid,
      Io io,
      LongSupplier clock,
      Digests digests) {
    this.root = Objects.requireNonNull(root, "backup root");
    this.security = Objects.requireNonNull(security, "inode security");
    this.io = Objects.requireNonNull(io, "manifest IO");
    this.clock = Objects.requireNonNull(clock, "manifest clock");
    this.digests = Objects.requireNonNull(digests, "manifest digest provider");
    if (uid < 1 || uid > 0xffffffffL || gid < 1 || gid > 0xffffffffL)
      throw new IllegalArgumentException("invalid backup owner");
    this.uid = uid;
    this.gid = gid;
  }

  public BackupManifest read(String name, BatchStepAttempt database, BatchStepAttempt configuration)
      throws StorageIoException {
    Objects.requireNonNull(database, "database handle");
    Objects.requireNonNull(configuration, "configuration handle");
    BackupManifest result = readAt(name, null);
    require(
        result.databaseStep().equals(database) && result.configurationStep().equals(configuration));
    return result;
  }

  /** Same operation-wide monotonic budget supplied by the package publisher. SSC066/BAT258..273. */
  BackupManifest readWithin(
      String name, BatchStepAttempt database, BatchStepAttempt configuration, long started)
      throws StorageIoException {
    Objects.requireNonNull(database, "database handle");
    Objects.requireNonNull(configuration, "configuration handle");
    BackupManifest result = readAt(name, started);
    require(
        result.databaseStep().equals(database) && result.configurationStep().equals(configuration));
    return result;
  }

  /**
   * Selects untrusted claims by the fixed child's nonsecret digest. Caller must independently
   * verify all four files, both DB success rows and every root/Unit exclusion before DELETE.
   * NK-OPS-001/BAK001/OPS009/UI251/SS341/343/SSC104/PG331; PT-OPS-BMR017..024.
   */
  public BackupManifest findCleanupClaims(CleanupWorkerRequest request) throws StorageIoException {
    Objects.requireNonNull(request, "fixed cleanup request");
    lock.lock();
    try {
      long started = clock.getAsLong();
      try {
        guard(started);
        require(security.effectiveUid() == 0);
        Metadata parent = directory(root, started);
        List<String> first = names(started);
        BatchRun fixed = new BatchRun(request.run(), request.cutoff());
        List<String> matches = new ArrayList<>();
        for (String name : first) {
          guard(started);
          if (!name.endsWith("-" + request.run())) continue;
          require(
              name.length() == 52
                  && name.matches("[0-9]{8}-[0-9]{6}-[0-9a-f]{8}(-[0-9a-f]{4}){3}-[0-9a-f]{12}"));
          BackupManifest candidate = readAt(name, started);
          if (candidate.run().equals(fixed) && digest(candidate).equals(request.manifestSha256()))
            matches.add(name);
        }
        require(matches.size() == 1);
        BackupManifest fresh = readAt(matches.getFirst(), started);
        require(fresh.run().equals(fixed) && digest(fresh).equals(request.manifestSha256()));
        require(first.equals(names(started)) && parent.equals(directory(root, started)));
        guard(started);
        return fresh;
      } catch (IOException
          | DirectoryIteratorException
          | UnsupportedOperationException
          | NoSuchAlgorithmException failure) {
        throw unavailable();
      }
    } finally {
      lock.unlock();
    }
  }

  /** SSC133/ISSRET001..008: actual bounded names under the borrowed backup root. */
  List<String> retentionNames(long started) throws StorageIoException {
    lock.lock();
    try {
      require(security.effectiveUid() == 0);
      Metadata before = directory(root, started);
      List<String> result = names(started);
      require(before.equals(directory(root, started)));
      require(security.effectiveUid() == 0);
      guard(started);
      return result;
    } finally {
      lock.unlock();
    }
  }

  Metadata retentionRoot(long started) throws StorageIoException {
    require(security.effectiveUid() == 0);
    return directory(root, started);
  }

  boolean retentionDirectory(String name, long started) throws StorageIoException {
    guard(started);
    require(security.effectiveUid() == 0);
    return root.atExistingEntryHandle(
        name,
        held -> {
          Metadata before = metadata(io.attributes(held));
          guard(started);
          require(before.equals(metadata(io.attributes(held))));
          guard(started);
          return (before.mode() & 0xf000) == 0x4000;
        });
  }

  List<String> retentionFiles(String name, long started) throws StorageIoException {
    return ResourceScope.acquire(
        () -> root.openExistingChild(name),
        OwnedTransferDirectory::close,
        child -> {
          Metadata before = directory(child, started);
          List<String> result = names(child, started);
          require(before.equals(directory(child, started)));
          return result;
        });
  }

  /** Untrusted claim only; verifier and actual complete DB pair must separately agree. */
  Optional<BackupManifest> retentionClaim(String name, long started) throws StorageIoException {
    return readClaimAt(name, started, true);
  }

  private List<String> names(long started) throws StorageIoException {
    return names(root, started);
  }

  private List<String> names(OwnedTransferDirectory directory, long started)
      throws StorageIoException {
    guard(started);
    List<String> names =
        directory.atDirectory(
            held -> {
              return ResourceScope.acquire(
                  () -> {
                    DirectoryStream<Path> stream = io.openNames(held);
                    if (stream == null) throw unavailable();
                    return stream;
                  },
                  DirectoryStream::close,
                  stream -> {
                    Set<String> seen = new HashSet<>();
                    for (Path entry : stream) {
                      guard(started);
                      require(entry != null && held.equals(entry.getParent()));
                      require(seen.add(held.relativize(entry).toString()) && seen.size() <= 4096);
                    }
                    List<String> sorted = new ArrayList<>(seen);
                    Collections.sort(sorted);
                    guard(started);
                    return List.copyOf(sorted);
                  });
            });
    guard(started);
    return names;
  }

  private String digest(BackupManifest claim) throws NoSuchAlgorithmException {
    byte[] canonical = BackupManifestCodec.encode(claim);
    try {
      return HexFormat.of()
          .formatHex(Objects.requireNonNull(digests.create(), "manifest digest").digest(canonical));
    } finally {
      Arrays.fill(canonical, (byte) 0);
    }
  }

  private BackupManifest readAt(String name, @Nullable Long suppliedStart)
      throws StorageIoException {
    return readClaimAt(name, suppliedStart, false).orElseThrow(EnvironmentInodePolicy::unavailable);
  }

  private Optional<BackupManifest> readClaimAt(
      String name, @Nullable Long suppliedStart, boolean permitKnownMalformed)
      throws StorageIoException {
    Objects.requireNonNull(name, "backup directory name");
    require(
        name.length() == 52
            && name.matches(
                "[0-9]{8}-[0-9]{6}-[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"));
    lock.lock();
    try {
      long started = suppliedStart == null ? clock.getAsLong() : suppliedStart;
      byte[] bytes = new byte[4097];
      try {
        guard(started);
        require(security.effectiveUid() == 0);
        guard(started);
        Metadata parent = directory(root, started);
        guard(started);
        Metadata original =
            ResourceScope.acquire(
                () -> root.openExistingChild(name),
                OwnedTransferDirectory::close,
                child -> {
                  Metadata initial = directory(child, started);
                  require(initial.device() == parent.device());
                  guard(started);
                  Metadata observed =
                      child.atExistingEntryHandle(
                          NAME,
                          held -> {
                            Metadata before = capture(held, false, started);
                            require(before.device() == initial.device());
                            readFile(held, before.size(), bytes, started);
                            require(before.equals(capture(held, false, started)));
                            return before;
                          });
                  guard(started);
                  require(
                      child.atExistingEntryHandle(
                          NAME, held -> observed.equals(capture(held, false, started))));
                  guard(started);
                  require(initial.equals(directory(child, started)));
                  guard(started);
                  ResourceScope.acquire(
                      () -> root.openExistingChild(name),
                      OwnedTransferDirectory::close,
                      rebound -> {
                        require(initial.equals(directory(rebound, started)));
                        return Boolean.TRUE;
                      });
                  guard(started);
                  return observed;
                });
        guard(started);
        require(parent.equals(directory(root, started)));
        Optional<BackupManifest> result = decode(bytes, (int) original.size());
        if (result.isPresent() && !result.orElseThrow().directoryName().equals(name))
          result = Optional.empty();
        require(permitKnownMalformed || result.isPresent());
        guard(started);
        require(security.effectiveUid() == 0);
        guard(started);
        return result;
      } catch (IOException | DirectoryIteratorException | UnsupportedOperationException failure) {
        throw unavailable();
      } finally {
        Arrays.fill(bytes, (byte) 0);
      }
    } finally {
      lock.unlock();
    }
  }

  private Metadata directory(OwnedTransferDirectory directory, long started)
      throws StorageIoException {
    guard(started);
    Metadata value = directory.atDirectory(held -> capture(held, true, started));
    guard(started);
    return value;
  }

  private Metadata capture(Path held, boolean directory, long started) throws IOException {
    guard(started);
    Metadata value = metadata(io.attributes(held));
    guard(started);
    require(
        value.mode() == (directory ? 0x41c0 : 0x8180)
            && value.uid() == (directory ? uid : 0)
            && value.gid() == (directory ? gid : 0));
    if (directory) require(value.links() >= 2 && value.size() >= 0);
    else require(value.links() == 1 && value.size() >= 1 && value.size() <= 4096);
    byte[] acl = security.accessAcl(held, 44);
    guard(started);
    require(acl != null && acl.length == 0);
    require(!security.readOnlyFilesystem(held));
    guard(started);
    return value;
  }

  private void readFile(Path held, long expected, byte[] bytes, long started) throws IOException {
    guard(started);
    ResourceScope.acquire(
        () -> {
          SeekableByteChannel opened = io.open(held);
          if (opened == null) throw unavailable();
          return opened;
        },
        SeekableByteChannel::close,
        opened -> {
          guard(started);
          require(opened.size() == expected);
          guard(started);
          ByteBuffer buffer = ByteBuffer.wrap(bytes);
          buffer.limit((int) expected);
          while (buffer.hasRemaining()) {
            int position = buffer.position();
            int remaining = buffer.remaining();
            guard(started);
            int read = opened.read(buffer);
            guard(started);
            require(read > 0 && read <= remaining && buffer.position() == position + read);
          }
          buffer.limit((int) expected + 1);
          guard(started);
          require(opened.read(buffer) == -1 && buffer.position() == expected);
          guard(started);
          require(opened.size() == expected);
          guard(started);
          return Boolean.TRUE;
        });
    guard(started);
  }

  private static Optional<BackupManifest> decode(byte[] bytes, int size) {
    byte[] content = Arrays.copyOf(bytes, size);
    try {
      return Optional.of(BackupManifestCodec.decode(content));
    } catch (IllegalArgumentException malformed) {
      return Optional.empty();
    } finally {
      Arrays.fill(content, (byte) 0);
    }
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

  private void guard(long started) throws StorageIoException {
    if (Thread.currentThread().isInterrupted()) throw unavailable();
    long elapsed = clock.getAsLong() - started;
    if (Thread.currentThread().isInterrupted()) throw unavailable();
    require(elapsed >= 0 && elapsed < DEADLINE);
  }

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
