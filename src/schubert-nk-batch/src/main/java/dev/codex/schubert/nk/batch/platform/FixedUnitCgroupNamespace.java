package dev.codex.schubert.nk.batch.platform;

import dev.codex.schubert.nk.storage.DirectoryCalls;
import dev.codex.schubert.nk.storage.InodeSecurityCalls;
import dev.codex.schubert.nk.storage.ResourceScope;
import dev.codex.schubert.nk.storage.StorageIoException;
import java.io.IOException;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;

/**
 * Package-only genuine host cgroup namespace projection, not whole-process emptiness or authority.
 * NK-OPS-001/UI251/SS3415/343/SSC093100; BTERM001..008/MSTOP. Fixed enum leaf only. Narrow
 * extraction preserves all NOFOLLOW, ancestor identity, metadata, ACL and owner-close rules.
 */
@NullMarked
final class FixedUnitCgroupNamespace {
  private static final List<String> SEGMENTS = List.of("sys", "fs", "cgroup", "system.slice");

  @FunctionalInterface
  interface Context {
    void recheck() throws IOException;
  }

  interface Io {
    @Nullable Map<String, Object> attributes(Path held) throws IOException;

    @Nullable String filesystem(Path held) throws IOException;
  }

  private final Context context;
  private final DirectoryCalls host;
  private final InodeSecurityCalls security;
  private final Io io;

  FixedUnitCgroupNamespace(
      Context context, DirectoryCalls host, InodeSecurityCalls security, Io io) {
    this.context = Objects.requireNonNull(context, "root context");
    this.host = Objects.requireNonNull(host, "host view");
    this.security = Objects.requireNonNull(security, "inode security");
    this.io = Objects.requireNonNull(io, "inode IO");
  }

  void check() throws IOException {
    require(!Thread.currentThread().isInterrupted());
    context.recheck();
    require(security.effectiveUid() == 0);
    require(!Thread.currentThread().isInterrupted());
  }

  Snapshot observe(MaintenanceUnit unit) throws IOException {
    Objects.requireNonNull(unit, "fixed Unit");
    check();
    return ResourceScope.<Owner, Snapshot, StorageIoException>acquire(
        () -> new Owner(host),
        Owner::close,
        owner -> {
          var identities = new ArrayList<Identity>();
          int directory = owner.openRoot();
          identities.add(identity(directory, 0));
          for (int i = 0; i < SEGMENTS.size(); i++) {
            directory = owner.openDirectory(directory, SEGMENTS.get(i));
            identities.add(identity(directory, i + 1));
          }
          require(identities.get(1).device() == identities.get(2).device());
          require(identities.get(3).device() == identities.get(4).device());
          boolean present = true;
          int leaf = -1;
          try {
            leaf = owner.openDirectory(directory, unit.serviceName());
          } catch (StorageIoException failure) {
            if (failure.reason() != StorageIoException.Reason.MISSING) throw failure;
            present = false;
          }
          // BUG277/SSC308: only the open syscall's MISSING is absence; registration is primitive.
          if (present) {
            var child = identity(leaf, 4);
            require(child.device() == identities.get(4).device());
            identities.add(child);
          }
          for (int i = 0; i < identities.size(); i++) {
            require(identities.get(i).equals(identity(owner.descriptor(i), Math.min(i, 4))));
          }
          check();
          return new Snapshot(List.copyOf(identities), present);
        });
  }

  private Identity identity(int descriptor, int position) throws IOException {
    Path held = Path.of("/proc/self/fd/" + descriptor);
    var values = io.attributes(held);
    if (values == null
        || !(values.get("mode") instanceof Integer mode)
        || !(values.get("uid") instanceof Integer uid)
        || !(values.get("gid") instanceof Integer gid)
        || !(values.get("nlink") instanceof Integer links)
        || !(values.get("size") instanceof Long size)
        || !(values.get("dev") instanceof Long device)
        || !(values.get("ino") instanceof Long inode))
      throw new IOException("maintenance cgroup namespace unavailable");
    require((mode == 0x416d || mode == 0x41ed) && uid == 0 && gid == 0 && links >= 2 && size >= 0);
    require(device >= 0 && inode > 0);
    if (position > 0) require((position < 3 ? "sysfs" : "cgroup2").equals(io.filesystem(held)));
    require(security.accessAcl(held, 44).length == 0);
    return new Identity(mode, uid, gid, device, inode);
  }

  record Identity(int mode, int uid, int gid, long device, long inode) {}

  record Snapshot(List<Identity> identities, boolean present) {}

  private static void require(boolean valid) throws IOException {
    if (!valid) throw new IOException("maintenance cgroup namespace unavailable");
  }

  // SSC308/PT-OPS-CGROUPFD001-008: package-visible for independent primitive ownership tests.
  static final class Owner {
    private final DirectoryCalls calls;
    private final int[] descriptors = new int[6];
    private final boolean[] secondaryFailures = new boolean[6];
    private int count;
    private boolean closed;

    Owner(DirectoryCalls calls) {
      this.calls = Objects.requireNonNull(calls, "cgroup directory calls");
    }

    int openRoot() throws StorageIoException {
      guard();
      int descriptor = calls.openRoot();
      if (descriptor < 0) throw unavailable();
      for (int index = 0; index < count; index++)
        if (descriptors[index] == descriptor) throw unavailable();
      // PG-D802/2472: count changes before the write, as in the original post-increment.
      int ownedPosition = count;
      count++;
      descriptors[ownedPosition] = descriptor;
      return descriptor;
    }

    int openDirectory(int parent, String name) throws StorageIoException {
      Objects.requireNonNull(name, "cgroup directory segment");
      guard();
      boolean held = false;
      for (int index = 0; index < count; index++) if (descriptors[index] == parent) held = true;
      if (!held) throw unavailable();
      int descriptor = calls.openDirectory(parent, name);
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

    int descriptor(int position) {
      return descriptors[position];
    }

    void close() throws StorageIoException {
      if (closed) return;
      closed = true;
      for (int index = 0; index < count; index++) {
        try {
          calls.close(descriptors[index]);
        } catch (StorageIoException known) {
          throw closeAfterKnown(index + 1, known);
        } catch (RuntimeException | Error primary) {
          drain(index + 1);
          appendSecondary(primary);
          throw primary;
        }
      }
    }

    private StorageIoException closeAfterKnown(int remaining, StorageIoException primary) {
      boolean multiple = false;
      for (int index = remaining; index < count; index++) {
        try {
          calls.close(descriptors[index]);
        } catch (StorageIoException secondary) {
          multiple = true;
        } catch (RuntimeException | Error unknown) {
          drain(index + 1);
          appendSecondary(unknown);
          throw unknown;
        }
      }
      return new StorageIoException(
          !multiple && primary.getSuppressed().length == 0
              ? primary.reason()
              : StorageIoException.Reason.UNAVAILABLE);
    }

    private void drain(int remaining) {
      for (int index = remaining; index < count; index++) {
        try {
          calls.close(descriptors[index]);
        } catch (StorageIoException | RuntimeException | Error secondary) {
          secondaryFailures[index] = true;
        }
      }
    }

    private void appendSecondary(Throwable primary) {
      for (int index = 0; index < count; index++)
        if (secondaryFailures[index]) primary.addSuppressed(unavailable());
    }

    private static StorageIoException unavailable() {
      return new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
    }
  }
}
