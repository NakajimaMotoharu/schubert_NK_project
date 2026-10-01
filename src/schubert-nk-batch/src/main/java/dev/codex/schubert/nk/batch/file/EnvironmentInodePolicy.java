package dev.codex.schubert.nk.batch.file;

import dev.codex.schubert.nk.storage.InodeSecurityCalls;
import dev.codex.schubert.nk.storage.StorageIoException;
import java.io.IOException;
import java.nio.file.Path;
import java.nio.file.attribute.FileTime;
import java.util.Map;
import java.util.Set;
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;

/** Shared read/write admission; NK-OPS-001; OPS-009/UI251/SS343 6.9/6.11; EFILE/PUB PT. */
@NullMarked
final class EnvironmentInodePolicy {
  private static final Set<String> LOCAL = Set.of("ext2", "ext3", "ext4", "xfs", "btrfs", "tmpfs");
  private final InodeSecurityCalls security;
  private final Source source;

  interface Source {
    @Nullable Map<String, Object> attributes(Path held) throws IOException;

    @Nullable String filesystem(Path held) throws IOException;
  }

  // Package callers establish dependency invariants before constructing the shared policy.
  EnvironmentInodePolicy(InodeSecurityCalls security, Source source) {
    this.security = security;
    this.source = source;
  }

  Snapshot snapshot(
      Path held, boolean runtime, boolean directory, int maximum, int minimum, long configGroup)
      throws IOException {
    int mode = directory ? (runtime ? 040700 : 040750) : (runtime ? 0100600 : 0100640);
    return inspect(held, runtime, directory, mode, runtime ? 0 : configGroup, minimum, maximum);
  }

  /** Fixed /etc, /run and shared runtime ancestor: root:root0755, never created or repaired. */
  Snapshot ancestor(Path held, boolean runtime) throws IOException {
    return inspect(held, runtime, true, 040755, 0, 0, 0);
  }

  /** NK-BAT-001; SS343 6.14; PT-BAT-046..057. Never admit volatile or readonly records. */
  Snapshot durable(Path held, boolean directory, int minimum) throws IOException {
    Snapshot result =
        inspect(held, false, directory, directory ? 040700 : 0100600, 0, minimum, 204);
    require(!result.filesystem().equals("tmpfs") && !result.readonly());
    return result;
  }

  /** Shared durable ancestors retain 0755; NK-BAT-001/SS343 6.15/PT-BAT-070. */
  Snapshot durableAncestor(Path held) throws IOException {
    return durableAncestor(held, false);
  }

  /** SSC109: only paired native host admission may allow a private shared ancestor RO. */
  Snapshot durableAncestor(Path held, boolean allowPrivateReadonly) throws IOException {
    Snapshot result = inspect(held, false, true, 040755, 0, 0, 0);
    require(!result.filesystem().equals("tmpfs"));
    if (!allowPrivateReadonly) require(!result.readonly());
    return result;
  }

  private Snapshot inspect(
      Path held, boolean runtime, boolean directory, int mode, long group, int minimum, int maximum)
      throws IOException {
    return inspect(held, runtime, directory, mode, 0, group, minimum, maximum);
  }

  /** SSC126: read-only six-root inspection; never creates or repairs an admitted inode. */
  Snapshot roleDirectory(Path held, long uid, long gid, int permissions, boolean host)
      throws IOException {
    Snapshot result = inspect(held, false, true, 040000 | permissions, uid, gid, 0, 0);
    require(result.metadata().device() >= 0 && result.metadata().inode() > 0);
    if (host) require(!result.readonly());
    return result;
  }

  /** SSC137 host root credential source, deliberately distinct from LoadCredential tmpfs copies. */
  Snapshot hostCredentialSource(Path held, boolean directory, long group) throws IOException {
    Snapshot result =
        inspect(
            held,
            false,
            directory,
            directory ? 040700 : 0100600,
            0,
            directory ? 0 : group,
            directory ? 0 : 1,
            directory ? 0 : 65536);
    require(!result.readonly());
    return result;
  }

  private Snapshot inspect(
      Path held,
      boolean runtime,
      boolean directory,
      int mode,
      long uid,
      long group,
      int minimum,
      int maximum)
      throws IOException {
    Metadata m = metadata(source.attributes(held));
    require(m.mode() == mode && m.uid() == uid && m.gid() == group);
    if (directory) require(m.links() >= 2 && m.size() >= 0);
    else require(m.links() == 1 && m.size() >= minimum && m.size() <= maximum);
    byte[] acl = security.accessAcl(held, 44);
    require(acl != null && acl.length == 0);
    String filesystem = source.filesystem(held);
    if (filesystem == null) throw unavailable();
    boolean readonly = security.readOnlyFilesystem(held);
    if (runtime) require(filesystem.equals("tmpfs") && !readonly);
    else require(LOCAL.contains(filesystem));
    return new Snapshot(m, filesystem, readonly);
  }

  static Metadata metadata(@Nullable Map<String, Object> values) throws StorageIoException {
    if (values == null
        || !(values.get("mode") instanceof Integer mode)
        || !(values.get("uid") instanceof Integer uid)
        || !(values.get("gid") instanceof Integer gid)
        || !(values.get("nlink") instanceof Integer links)
        || !(values.get("size") instanceof Long size)
        || !(values.get("dev") instanceof Long device)
        || !(values.get("ino") instanceof Long inode)
        || !(values.get("lastModifiedTime") instanceof FileTime modified)
        || !(values.get("ctime") instanceof FileTime changed)) throw unavailable();
    return new Metadata(
        mode,
        Integer.toUnsignedLong(uid),
        Integer.toUnsignedLong(gid),
        links,
        size,
        device,
        inode,
        modified,
        changed);
  }

  static void require(boolean accepted) throws StorageIoException {
    if (!accepted) throw unavailable();
  }

  static StorageIoException unavailable() {
    return new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
  }

  record Metadata(
      int mode,
      long uid,
      long gid,
      int links,
      long size,
      long device,
      long inode,
      FileTime modified,
      FileTime changed) {}

  record Snapshot(Metadata metadata, String filesystem, boolean readonly) {
    /** Namespace content mutations may change directory size/times, never its admitted identity. */
    boolean sameIdentity(Snapshot other) {
      return metadata.mode() == other.metadata.mode()
          && metadata.uid() == other.metadata.uid()
          && metadata.gid() == other.metadata.gid()
          && metadata.links() == other.metadata.links()
          && metadata.device() == other.metadata.device()
          && metadata.inode() == other.metadata.inode()
          && filesystem.equals(other.filesystem)
          && readonly == other.readonly;
    }

    /** rename changes ctime; content size/mtime and identity still must be preserved. */
    boolean samePublishedFile(Snapshot other) {
      return sameIdentity(other)
          && metadata.size() == other.metadata.size()
          && metadata.modified().equals(other.metadata.modified());
    }
  }
}
