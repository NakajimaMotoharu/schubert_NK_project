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
    Metadata m = metadata(source.attributes(held));
    int mode = directory ? (runtime ? 040700 : 040750) : (runtime ? 0100600 : 0100640);
    require(m.mode() == mode && m.uid() == 0 && m.gid() == (runtime ? 0 : configGroup));
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

  private static Metadata metadata(@Nullable Map<String, Object> values) throws StorageIoException {
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
