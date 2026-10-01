package dev.codex.schubert.nk.batch.file;

import dev.codex.schubert.nk.storage.*;
import edu.umd.cs.findbugs.annotations.SuppressFBWarnings;
import edu.umd.cs.findbugs.annotations.SuppressMatchType;
import java.io.IOException;
import java.nio.file.*;
import java.util.*;
import org.jspecify.annotations.*;

/**
 * Root-only, read-only A admission in host and service mount views; never maintenance M.
 * NK-OPS-001; SYS-002/004,OPS-009; UI212/251; SS341/342/343; SSC086/087; PG294;
 * PT-OPS-ADMISSIONLOCK-001..008. Caller first authenticates kernel proc/PID1/system manager/boot
 * and its fixed Unit identity; rechecks that identity after A and before exec. This adapter does
 * not issue a permit or attest those identities. Trusted callback borrows A only until return or
 * same-PID native exec; all retained root/entry capabilities are CLOEXEC and never exported.
 */
@NullMarked
public final class StartupAdmissionFile {
  private final Path runtime;
  private final DirectoryCalls host;
  private final DirectoryCalls service;
  private final InodeSecurityCalls security;
  private final LinuxFileLock locks;
  private final Io io;

  interface Io {
    @Nullable
    Map<String, Object> attributes(Path held) throws IOException;

    @Nullable
    String filesystemType(Path held) throws IOException;
  }

  // Fixed /run, exact portability review only. No security/null/coverage exclusion.
  @SuppressFBWarnings(
      value = "DMI_HARDCODED_ABSOLUTE_FILENAME",
      matchType = SuppressMatchType.EXACT,
      justification = "SS341/343/SSC086 fixed /run A; PG294/PT-OPS-ADMISSIONLOCK-008")
  public static StartupAdmissionFile create() {
    return new StartupAdmissionFile(
        Path.of("/run"),
        LinuxHostDirectoryCalls.create(),
        LinuxDirectoryCalls.create(),
        LinuxInodeSecurity.create(),
        LinuxFileLock.create(),
        new NioIo());
  }

  StartupAdmissionFile(
      Path runtime,
      DirectoryCalls host,
      DirectoryCalls service,
      InodeSecurityCalls security,
      LinuxFileLock locks,
      Io io) {
    this.runtime = Objects.requireNonNull(runtime, "runtime");
    this.host = Objects.requireNonNull(host, "host view");
    this.service = Objects.requireNonNull(service, "service view");
    this.security = Objects.requireNonNull(security, "security");
    this.locks = Objects.requireNonNull(locks, "locks");
    this.io = Objects.requireNonNull(io, "io");
    if (!runtime.isAbsolute()
        || runtime.getNameCount() == 0
        || !runtime.equals(runtime.normalize()))
      throw new IllegalArgumentException("invalid startup runtime");
  }

  public <T> Optional<T> tryExclusive(LinuxFileLock.StartupOperation<T> operation)
      throws StorageIoException {
    Objects.requireNonNull(operation, "startup operation");
    return tryExclusiveObserved(admission -> operation.execute(admission.descriptor()));
  }

  /** Actual admitted held A identity, borrowed only while this owner's native OFD lock lives. */
  public record Admission(int descriptor, long device, long inode) {}

  @FunctionalInterface
  public interface AdmittedOperation<T> {
    T execute(Admission admission) throws IOException;
  }

  public <T> Optional<T> tryExclusiveObserved(AdmittedOperation<T> operation)
      throws StorageIoException {
    Objects.requireNonNull(operation, "startup operation");
    require(security.effectiveUid() == 0);
    try {
      return withView(
          host,
          true,
          (hostSnapshot, hostFile, hostOwner) ->
              withView(
                  service,
                  false,
                  (serviceSnapshot, serviceFile, serviceOwner) -> {
                    require(hostSnapshot.equals(serviceSnapshot));
                    return locks.tryExclusiveForStartup(
                        hostFile,
                        reserved -> {
                          verify(hostSnapshot);
                          // A fresh private-view open has a different OFD and must contend with
                          // host A.
                          require(locks.tryExclusive(serviceFile, () -> Boolean.TRUE).isEmpty());
                          // BUG265/YKT199: consume every root/entry observation owner before a
                          // callback may replace this root JVM. Only the A lock owner survives.
                          serviceOwner.close();
                          hostOwner.close();
                          T result =
                              operation.execute(
                                  new Admission(
                                      reserved,
                                      hostSnapshot.file().device(),
                                      hostSnapshot.file().inode()));
                          verify(hostSnapshot);
                          return result;
                        });
                  }));
    } catch (IOException failure) {
      throw unavailable();
    }
  }

  private <T> T withView(DirectoryCalls calls, boolean hostView, ViewOperation<T> operation)
      throws IOException {
    var owner = new ViewOwner(calls);
    return ResourceScope.use(
        owner::close,
        () -> {
          int directory = owner.add(calls.openRoot());
          for (Path segment : runtime)
            directory = owner.add(calls.openDirectory(directory, segment.toString()));
          Identity runIdentity = identity(held(directory), true, hostView);
          int app = owner.add(calls.openDirectory(directory, "schubert-nk"));
          Identity appIdentity = identity(held(app), true, hostView);
          require(runIdentity.device() == appIdentity.device());
          int entry = owner.add(calls.openEntry(app, "startup-admission.lock"));
          Path file = held(entry);
          Identity fileIdentity = identity(file, false, hostView);
          require(appIdentity.device() == fileIdentity.device());
          return operation.execute(
              new Snapshot(runIdentity, appIdentity, fileIdentity), file, owner);
        });
  }

  private void verify(Snapshot expected) throws IOException {
    withView(
        host,
        true,
        (actual, held, owner) -> {
          require(expected.equals(actual));
          return Boolean.TRUE;
        });
    withView(
        service,
        false,
        (actual, held, owner) -> {
          require(expected.equals(actual));
          return Boolean.TRUE;
        });
  }

  private Identity identity(Path held, boolean directory, boolean hostView) throws IOException {
    Map<String, Object> values = io.attributes(held);
    if (values == null
        || !(values.get("mode") instanceof Integer mode)
        || !(values.get("uid") instanceof Integer uid)
        || !(values.get("gid") instanceof Integer gid)
        || !(values.get("nlink") instanceof Integer links)
        || !(values.get("size") instanceof Long size)
        || !(values.get("dev") instanceof Long device)
        || !(values.get("ino") instanceof Long inode)) throw unavailable();
    if (directory) require(mode == 040755 && links >= 2 && size >= 0);
    else require(mode == 0100600 && links == 1 && size == 0);
    require(uid == 0 && gid == 0);
    require("tmpfs".equals(io.filesystemType(held)));
    // Current retained host flags, never Java canonical FileStore.isReadOnly(). Private A may be
    // RO.
    if (hostView) require(!security.readOnlyFilesystem(held));
    require(security.accessAcl(held, 44).length == 0);
    return new Identity(mode, uid, gid, device, inode);
  }

  private static void require(boolean valid) throws StorageIoException {
    if (!valid) throw unavailable();
  }

  private static StorageIoException unavailable() {
    return new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
  }

  @FunctionalInterface
  private interface ViewOperation<T> {
    T execute(Snapshot snapshot, Path heldFile, ViewOwner owner) throws IOException;
  }

  private static Path held(int descriptor) {
    return Path.of("/proc/self/fd/" + descriptor);
  }

  /** Private root observation owner only, not a general exported file capability. */
  private static final class ViewOwner {
    private final DirectoryCalls calls;
    private final List<Integer> descriptors = new ArrayList<>();
    private boolean closed;

    ViewOwner(DirectoryCalls calls) {
      this.calls = calls;
    }

    int add(int descriptor) throws StorageIoException {
      require(descriptor >= 0);
      descriptors.add(descriptor);
      return descriptor;
    }

    void close() throws StorageIoException {
      if (closed) return;
      closed = true; // Consume all ownership once, even if a native close reports failure.
      closeFrom(0);
    }

    private void closeFrom(int position) throws StorageIoException {
      if (position == descriptors.size()) return;
      ResourceScope.use(
          () -> calls.close(descriptors.get(position)),
          () -> {
            closeFrom(position + 1);
            return Boolean.TRUE;
          });
    }
  }

  private record Identity(int mode, int uid, int gid, long device, long inode) {}

  private record Snapshot(Identity run, Identity app, Identity file) {}

  static final class NioIo implements Io {
    @Override
    public Map<String, Object> attributes(Path held) throws IOException {
      return Files.readAttributes(held, "unix:mode,uid,gid,nlink,size,dev,ino");
    }

    @Override
    public String filesystemType(Path held) throws IOException {
      return Files.getFileStore(held).type();
    }
  }
}
