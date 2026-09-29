package dev.codex.schubert.nk.batch.file;

import dev.codex.schubert.nk.storage.*;
import edu.umd.cs.findbugs.annotations.SuppressFBWarnings;
import edu.umd.cs.findbugs.annotations.SuppressMatchType;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;

/**
 * Root controller's fixed local runtime admission and scoped OS lock. NK-OPS-001; OPS-009/AVL;
 * UI251; SS311/341/343; SSC-049/PG-D-147; PT-OPS-LOCK-001..008. Does not create, chmod or unlink.
 * App stop, backup verification, DB handoff and the trusted root's namespace stability remain
 * mandatory caller duties. No path/UID/command can be selected through the public factory.
 */
// PG172/SSC063, BUG195/YKT154; resource precedence and PT evidence/01_PT/017/050.
@NullMarked
public final class MaintenanceFileLock {
  private final Path runtime;
  private final DirectoryCalls directories;
  private final Optional<DirectoryCalls> host;
  private final InodeSecurityCalls security;
  private final LinuxFileLock lock;
  private final Io io;

  interface Io {
    @Nullable Map<String, Object> attributes(Path held) throws IOException;

    @Nullable String filesystemType(Path held) throws IOException;

    boolean readOnly(Path held) throws IOException;
  }

  // BUG-142/YKT-112; owner NK-OPS-001 PG. Re-review at PG gate or Linux/path/SS change.
  // Fixed /run is UI251's safety contract, not an accidental portable application filename.
  // Only this exact portability diagnostic is reviewed; no coverage/null/security exclusion.
  @SuppressFBWarnings(
      value = "DMI_HARDCODED_ABSOLUTE_FILENAME",
      matchType = SuppressMatchType.EXACT,
      justification = "UI251/SS341/343 require fixed Linux /run; PG-D-147/PT-OPS-LOCK-007")
  public static MaintenanceFileLock create() {
    return new MaintenanceFileLock(
        Path.of("/run"),
        LinuxDirectoryCalls.create(),
        LinuxInodeSecurity.create(),
        LinuxFileLock.create(),
        new NioIo(),
        Optional.of(LinuxHostDirectoryCalls.create()));
  }

  // Package-only fixture/fault seam; never expose these selections as runtime configuration.
  MaintenanceFileLock(
      Path runtime,
      DirectoryCalls directories,
      InodeSecurityCalls security,
      LinuxFileLock lock,
      Io io) {
    this(runtime, directories, security, lock, io, Optional.empty());
  }

  // SSC109/BUG327: host capability is observation-only; M is locked in the private view.
  MaintenanceFileLock(
      Path runtime,
      DirectoryCalls directories,
      InodeSecurityCalls security,
      LinuxFileLock lock,
      Io io,
      Optional<DirectoryCalls> host) {
    this.runtime = Objects.requireNonNull(runtime, "runtime");
    this.directories = Objects.requireNonNull(directories, "directories");
    this.security = Objects.requireNonNull(security, "security");
    this.lock = Objects.requireNonNull(lock, "lock");
    this.io = Objects.requireNonNull(io, "io");
    this.host = Objects.requireNonNull(host, "host view");
    if (!runtime.isAbsolute()
        || runtime.getNameCount() == 0
        || !runtime.equals(runtime.normalize()))
      throw new IllegalArgumentException("invalid maintenance runtime");
  }

  /**
   * Only contention returns empty (callback not invoked). Admission, IO or close failure throws a
   * fixed diagnostic without cause/suppressed data. Runtime programming failures escape after
   * resource closure. A callback must not export live native resources or capabilities.
   */
  public <T> Optional<T> tryExclusive(LinuxFileLock.Operation<T> operation)
      throws StorageIoException {
    Objects.requireNonNull(operation, "operation");
    require(security.effectiveUid() == 0);
    try {
      if (host.isPresent())
        return withView(
            host.orElseThrow(),
            true,
            (hostSnapshot, ignored) ->
                withView(
                    directories,
                    false,
                    (privateSnapshot, held) -> {
                      require(hostSnapshot.equals(privateSnapshot));
                      return underLock(privateSnapshot, held, operation);
                    }));
      return withView(directories, false, (expected, held) -> underLock(expected, held, operation));
    } catch (IOException failure) {
      // Every owned entry/root has already closed; never leak nested/suppressed physical paths.
      throw unavailable();
    }
  }

  private <T> Optional<T> underLock(
      Snapshot expected, Path held, LinuxFileLock.Operation<T> operation) throws IOException {
    return lock.tryExclusive(
        held,
        () -> {
          verifyCurrent(expected);
          T result = operation.execute();
          verifyCurrent(expected);
          return result;
        });
  }

  private <T> T withView(DirectoryCalls calls, boolean hostView, ViewOperation<T> operation)
      throws IOException {
    var run = OwnedTransferDirectory.open(calls, runtime);
    return ResourceScope.use(
        run::close,
        () -> {
          Identity runIdentity = run.atDirectory(p -> directory(p, hostView || host.isEmpty()));
          {
            var app = run.openExistingChild("schubert-nk");
            return ResourceScope.use(
                app::close,
                () -> {
                  Identity appIdentity = app.atDirectory(p -> directory(p, true));
                  require(runIdentity.device() == appIdentity.device());
                  return app.atExistingEntryHandle(
                      "maintenance.lock",
                      held -> {
                        Identity fileIdentity = file(held);
                        require(appIdentity.device() == fileIdentity.device());
                        var expected = new Snapshot(runIdentity, appIdentity, fileIdentity);
                        return operation.execute(expected, held);
                      });
                });
          }
        });
  }

  private void verifyCurrent(Snapshot expected) throws IOException {
    if (host.isPresent())
      withView(
          host.orElseThrow(),
          true,
          (actual, held) -> {
            require(expected.equals(actual));
            return Boolean.TRUE;
          });
    withView(
        directories,
        false,
        (actual, held) -> {
          require(expected.equals(actual));
          return Boolean.TRUE;
        });
  }

  private Identity directory(Path held, boolean requireWritable) throws IOException {
    Metadata m = metadata(io.attributes(held));
    require(m.mode() == 040755 && m.links() >= 2 && m.size() >= 0);
    return identity(held, m, requireWritable);
  }

  private Identity file(Path held) throws IOException {
    Metadata m = metadata(io.attributes(held));
    // Validate retained inode's exact type before any path-following FS or xattr operation.
    require(m.mode() == 0100600 && m.links() == 1 && m.size() == 0);
    return identity(held, m, true);
  }

  private Identity identity(Path held, Metadata m, boolean requireWritable) throws IOException {
    require(m.uid() == 0 && m.gid() == 0);
    require("tmpfs".equals(io.filesystemType(held)));
    if (requireWritable) require(!io.readOnly(held));
    require(security.accessAcl(held, 44).length == 0);
    // Directory size/link count may change when legitimate sibling services create their files;
    // they are validated, but identity includes only stable ownership/type/permission/dev/inode.
    return new Identity(m.mode(), m.uid(), m.gid(), m.device(), m.inode());
  }

  private static Metadata metadata(@Nullable Map<String, Object> values) throws StorageIoException {
    if (values == null
        || !(values.get("mode") instanceof Integer mode)
        || !(values.get("uid") instanceof Integer uid)
        || !(values.get("gid") instanceof Integer gid)
        || !(values.get("nlink") instanceof Integer links)
        || !(values.get("size") instanceof Long size)
        || !(values.get("dev") instanceof Long device)
        || !(values.get("ino") instanceof Long inode)) throw unavailable();
    return new Metadata(mode, uid, gid, links, size, device, inode);
  }

  private static void require(boolean accepted) throws StorageIoException {
    if (!accepted) throw unavailable();
  }

  private static StorageIoException unavailable() {
    return new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
  }

  private record Metadata(
      int mode, int uid, int gid, int links, long size, long device, long inode) {}

  private record Identity(int mode, int uid, int gid, long device, long inode) {}

  private record Snapshot(Identity run, Identity app, Identity file) {}

  @FunctionalInterface
  private interface ViewOperation<T> {
    T execute(Snapshot snapshot, Path heldFile) throws IOException;
  }

  static final class NioIo implements Io {
    @Override
    public Map<String, Object> attributes(Path held) throws IOException {
      return Files.readAttributes(held, "unix:mode,uid,gid,nlink,size,dev,ino");
    }

    @Override
    public String filesystemType(Path held) throws IOException {
      return Files.getFileStore(held).type();
    }

    @Override
    public boolean readOnly(Path held) throws IOException {
      return LinuxInodeSecurity.create().readOnlyFilesystem(held);
    }
  }
}
