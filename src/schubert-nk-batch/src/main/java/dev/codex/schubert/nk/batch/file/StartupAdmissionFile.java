package dev.codex.schubert.nk.batch.file;

import dev.codex.schubert.nk.storage.DirectoryCalls;
import dev.codex.schubert.nk.storage.InodeSecurityCalls;
import dev.codex.schubert.nk.storage.LinuxDirectoryCalls;
import dev.codex.schubert.nk.storage.LinuxFileLock;
import dev.codex.schubert.nk.storage.LinuxHostDirectoryCalls;
import dev.codex.schubert.nk.storage.LinuxInodeSecurity;
import dev.codex.schubert.nk.storage.ResourceScope;
import dev.codex.schubert.nk.storage.StorageIoException;
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
 * Root-only, read-only A admission in host and service mount views; never maintenance M.
 * NK-OPS-001; SYS-002/004,OPS-009; UI212/251; SS341/342/343; SSC086/087; PG294;
 * PT-OPS-ADMISSIONLOCK-001..008. Caller first authenticates kernel proc/PID1/system manager/boot
 * and its fixed Unit identity; rechecks that identity after A and before exec. This adapter does
 * not issue a permit or attest those identities. Trusted callback borrows A only until return or
 * same-PID native exec; all retained root/entry capabilities are CLOEXEC and never exported.
 */
@NullMarked
public final class StartupAdmissionFile {
  private static final int MINIMUM_PRIVATE_VIEW_CAPACITY = 1;

  private final Path runtime;
  private final DirectoryCalls host;
  private final DirectoryCalls service;
  private final InodeSecurityCalls security;
  private final LinuxFileLock locks;
  private final Io io;

  interface Io {
    @Nullable Map<String, Object> attributes(Path held) throws IOException;

    @Nullable String filesystemType(Path held) throws IOException;
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
    return ResourceScope.<ViewOwner, T, StorageIoException>acquire(
        () -> new ViewOwner(calls, Math.addExact(runtime.getNameCount(), 3)),
        ViewOwner::close,
        owner -> {
          int directory = owner.openRoot();
          for (Path segment : runtime)
            directory = owner.openDirectory(directory, segment.toString());
          Identity runIdentity = identity(held(directory), true, hostView);
          int app = owner.openDirectory(directory, "schubert-nk");
          Identity appIdentity = identity(held(app), true, hostView);
          require(runIdentity.device() == appIdentity.device());
          int entry = owner.openEntry(app, "startup-admission.lock");
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
    if (directory) require(mode == 0x41ed && links >= 2 && size >= 0);
    else require(mode == 0x8180 && links == 1 && size == 0);
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
  static final class ViewOwner {
    private final DirectoryCalls calls;
    private final int[] descriptors;
    private final boolean[] secondaryFailures;
    private int count;
    private boolean closed;

    ViewOwner(DirectoryCalls calls, int capacity) {
      this.calls = Objects.requireNonNull(calls, "view directory calls");
      if (capacity < MINIMUM_PRIVATE_VIEW_CAPACITY)
        throw new IllegalArgumentException("positive private view capacity");
      descriptors = new int[capacity];
      secondaryFailures = new boolean[capacity];
    }

    // SSC308/VIEWFD001-008: guard before native IO, then only primitive work on valid new FD.
    int openRoot() throws StorageIoException {
      guard();
      int descriptor = calls.openRoot();
      if (descriptor < 0) throw unavailable();
      for (int index = 0; index < count; index++)
        if (descriptors[index] == descriptor) throw unavailable();
      // PG-D802/2472: preserve the pre-increment index and update before the owned write.
      int ownedPosition = count;
      count++;
      descriptors[ownedPosition] = descriptor;
      return descriptor;
    }

    int openDirectory(int parent, String name) throws StorageIoException {
      Objects.requireNonNull(name, "view directory segment");
      guard();
      parent(parent);
      int descriptor = calls.openDirectory(parent, name);
      if (descriptor < 0) throw unavailable();
      for (int index = 0; index < count; index++)
        if (descriptors[index] == descriptor) throw unavailable();
      int ownedPosition = count;
      count++;
      descriptors[ownedPosition] = descriptor;
      return descriptor;
    }

    int openEntry(int parent, String name) throws StorageIoException {
      Objects.requireNonNull(name, "view entry name");
      guard();
      parent(parent);
      int descriptor = calls.openEntry(parent, name);
      if (descriptor < 0) throw unavailable();
      for (int index = 0; index < count; index++)
        if (descriptors[index] == descriptor) throw unavailable();
      int ownedPosition = count;
      count++;
      descriptors[ownedPosition] = descriptor;
      return descriptor;
    }

    private void guard() throws StorageIoException {
      if (closed || count == descriptors.length) throw unavailable();
    }

    private void parent(int descriptor) throws StorageIoException {
      for (int index = 0; index < count; index++) if (descriptors[index] == descriptor) return;
      throw unavailable();
    }

    void close() throws StorageIoException {
      if (closed) return;
      closed = true; // Consume all ownership once, even if a native close reports failure.
      for (int index = count - 1; index >= 0; index--) {
        try {
          calls.close(descriptors[index]);
        } catch (StorageIoException known) {
          throw closeAfterKnown(index - 1, known);
        } catch (RuntimeException | Error primary) {
          drain(index - 1);
          appendSecondary(primary);
          throw primary;
        }
      }
    }

    // Keep the original typed catch alive: the first unknown supersedes prior known IO only.
    private StorageIoException closeAfterKnown(int remaining, StorageIoException primary) {
      boolean multiple = false;
      for (int index = remaining; index >= 0; index--) {
        try {
          calls.close(descriptors[index]);
        } catch (StorageIoException secondary) {
          multiple = true;
        } catch (RuntimeException | Error unknown) {
          drain(index - 1);
          appendSecondary(unknown);
          throw unknown;
        }
      }
      // Every FD was attempted before this normalization can allocate or inspect suppression.
      return new StorageIoException(
          !multiple && primary.getSuppressed().length == 0
              ? primary.reason()
              : StorageIoException.Reason.UNAVAILABLE);
    }

    private void drain(int remaining) {
      for (int index = remaining; index >= 0; index--) {
        try {
          calls.close(descriptors[index]);
        } catch (StorageIoException | RuntimeException | Error secondary) {
          secondaryFailures[index] = true;
        }
      }
    }

    private void appendSecondary(Throwable primary) {
      for (int index = count - 1; index >= 0; index--)
        if (secondaryFailures[index]) primary.addSuppressed(unavailable());
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
