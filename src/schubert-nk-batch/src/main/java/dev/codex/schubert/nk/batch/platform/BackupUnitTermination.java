package dev.codex.schubert.nk.batch.platform;

import dev.codex.schubert.nk.storage.*;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;
import org.jspecify.annotations.*;

/**
 * Root parent's fixed backup quiescence observation, never a success receipt or startup permit.
 * NK-OPS-001/SYS002/004/OPS009/BAK/BKO/UI251/SS3415/343; SSC093; BTERM001..008. Caller holds
 * continuous M/A, forbids independent start/restart/migration, and admits the fixed worker sandbox.
 * Context is authenticated before host view; every observation owner closes before return. Only the
 * fixed leaf's MISSING proves absence, not a bus or ancestor error.
 */
@NullMarked
public final class BackupUnitTermination {
  private static final String UNIT = "schubert-nk-backup.service";
  private static final String GROUP = "/system.slice/" + UNIT;
  private static final List<String> SEGMENTS = List.of("sys", "fs", "cgroup", "system.slice");

  @FunctionalInterface
  interface Context {
    void recheck() throws IOException;
  }

  interface Observations {
    InspectorUnitSnapshot read();

    byte[] placement();

    Optional<InspectorUnitSnapshot> quiescent();
  }

  interface Io {
    @Nullable
    Map<String, Object> attributes(Path held) throws IOException;

    @Nullable
    String filesystem(Path held) throws IOException;
  }

  private final Object stateLock = new Object();
  private final Context context;
  private final Observations observations;
  private final DirectoryCalls host;
  private final InodeSecurityCalls security;
  private final Io io;

  public static BackupUnitTermination create(
      RootStartupContext context, RootStartupContext.Snapshot expected) throws IOException {
    Objects.requireNonNull(context, "root context");
    Objects.requireNonNull(expected, "root identity");
    require(expected.service() == RootStartupContext.Service.MORNING);
    context.recheck(expected);
    return new BackupUnitTermination(
        () -> context.recheck(expected),
        new NativeObservations(),
        LinuxHostDirectoryCalls.create(),
        LinuxInodeSecurity.create(),
        new NioIo());
  }

  BackupUnitTermination(
      Context context,
      Observations observations,
      DirectoryCalls host,
      InodeSecurityCalls security,
      Io io) {
    this.context = Objects.requireNonNull(context, "root context");
    this.observations = Objects.requireNonNull(observations, "fixed observations");
    this.host = Objects.requireNonNull(host, "host view");
    this.security = Objects.requireNonNull(security, "inode security");
    this.io = Objects.requireNonNull(io, "inode IO");
  }

  public Optional<InspectorUnitSnapshot> quiescent() throws IOException {
    synchronized (stateLock) {
      try {
        check();
        var before = Objects.requireNonNull(observations.read(), "backup state");
        var placement = placement(observations.placement());
        if (!before.quiescent()) {
          check();
          return Optional.empty();
        }
        Namespace first = namespace();
        if (first.present()) {
          var all = Objects.requireNonNull(observations.quiescent(), "whole Unit observation");
          if (all.isEmpty() || !before.matches(all.orElseThrow())) {
            check();
            return Optional.empty();
          }
        }
        require(before.matches(Objects.requireNonNull(observations.read(), "backup state")));
        require(placement.equals(placement(observations.placement())));
        // Reopen the current host path; held old ancestors alone cannot attest namespace binding.
        require(first.equals(namespace()));
        require(before.matches(Objects.requireNonNull(observations.read(), "backup state")));
        require(placement.equals(placement(observations.placement())));
        check();
        return Optional.of(before);
      } catch (IOException failure) {
        throw unavailable();
      }
    }
  }

  private void check() throws IOException {
    require(!Thread.currentThread().isInterrupted());
    context.recheck();
    require(security.effectiveUid() == 0);
    require(!Thread.currentThread().isInterrupted());
  }

  private Namespace namespace() throws IOException {
    check();
    var owner = new Owner(host);
    return ResourceScope.use(
        owner::close,
        () -> {
          var identities = new ArrayList<Identity>();
          int directory = owner.add(host.openRoot());
          identities.add(identity(directory, 0));
          for (int i = 0; i < SEGMENTS.size(); i++) {
            directory = owner.add(host.openDirectory(directory, SEGMENTS.get(i)));
            identities.add(identity(directory, i + 1));
          }
          require(identities.get(1).device() == identities.get(2).device());
          require(identities.get(3).device() == identities.get(4).device());
          boolean present = true;
          int leaf = -1;
          try {
            leaf = host.openDirectory(directory, UNIT);
          } catch (StorageIoException failure) {
            if (failure.reason() != StorageIoException.Reason.MISSING) throw failure;
            present = false;
          }
          // BUG277: only the open syscall's MISSING is absence. Register before any fallible IO.
          if (present) {
            owner.add(leaf);
            var child = identity(leaf, 4);
            require(child.device() == identities.get(4).device());
            identities.add(child);
          }
          for (int i = 0; i < identities.size(); i++) {
            require(identities.get(i).equals(identity(owner.descriptor(i), Math.min(i, 4))));
          }
          check();
          return new Namespace(List.copyOf(identities), present);
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
        || !(values.get("ino") instanceof Long inode)) throw unavailable();
    require((mode == 040555 || mode == 040755) && uid == 0 && gid == 0 && links >= 2 && size >= 0);
    require(device >= 0 && inode > 0);
    if (position > 0) require((position < 3 ? "sysfs" : "cgroup2").equals(io.filesystem(held)));
    require(security.accessAcl(held, 44).length == 0);
    return new Identity(mode, uid, gid, device, inode);
  }

  private static Map<String, String> placement(byte[] bytes) throws IOException {
    Objects.requireNonNull(bytes, "fixed placement");
    try {
      require(bytes.length > 0 && bytes.length <= 1024);
      for (byte b : bytes) require(b == 10 || (b >= 32 && b <= 126));
      String[] lines = new String(bytes, StandardCharsets.US_ASCII).split("\n", -1);
      require(lines.length == 5 && lines[4].isEmpty());
      var fields = new HashMap<String, String>();
      for (int i = 0; i < 4; i++) {
        int separator = lines[i].indexOf('=');
        require(separator > 0);
        require(
            fields.putIfAbsent(lines[i].substring(0, separator), lines[i].substring(separator + 1))
                == null);
      }
      require(fields.keySet().equals(Set.of("Id", "Slice", "Delegate", "ControlGroup")));
      require(
          UNIT.equals(fields.get("Id"))
              && "system.slice".equals(fields.get("Slice"))
              && "no".equals(fields.get("Delegate")));
      String group = Objects.requireNonNull(fields.get("ControlGroup"), "fixed group field");
      require(group.isEmpty() || GROUP.equals(group));
      return Map.copyOf(fields);
    } finally {
      Arrays.fill(bytes, (byte) 0);
    }
  }

  private record Identity(int mode, int uid, int gid, long device, long inode) {}

  private record Namespace(List<Identity> identities, boolean present) {}

  private static void require(boolean valid) throws IOException {
    if (!valid) throw unavailable();
  }

  private static IOException unavailable() {
    return new IOException("backup termination unavailable");
  }

  private static final class Owner {
    private final DirectoryCalls calls;
    private final int[] descriptors = new int[6];
    private int count;

    Owner(DirectoryCalls calls) {
      this.calls = calls;
    }

    int add(int descriptor) throws IOException {
      require(descriptor >= 0);
      descriptors[count++] = descriptor;
      return descriptor;
    }

    int descriptor(int position) {
      return descriptors[position];
    }

    void close() throws StorageIoException {
      closeFrom(count - 1);
    }

    private void closeFrom(int position) throws StorageIoException {
      if (position < 0) return;
      ResourceScope.use(
          () -> calls.close(descriptors[position]),
          () -> {
            closeFrom(position - 1);
            return Boolean.TRUE;
          });
    }
  }

  static final class NativeObservations implements Observations {
    private final InspectorUnitProbe probe;
    private final InspectorUnitProbe.NativeReader reader;

    NativeObservations() {
      this(InspectorUnitProbe.NativeReader.forTarget(InspectorUnitSnapshot.Target.BACKUP));
    }

    NativeObservations(InspectorUnitProbe.NativeReader reader) {
      this(reader, InspectorUnitProbe.forTarget(InspectorUnitSnapshot.Target.BACKUP));
    }

    NativeObservations(InspectorUnitProbe.NativeReader reader, InspectorUnitProbe probe) {
      this.reader = Objects.requireNonNull(reader, "fixed reader");
      this.probe = Objects.requireNonNull(probe, "fixed backup probe");
    }

    public InspectorUnitSnapshot read() {
      return probe.read();
    }

    public Optional<InspectorUnitSnapshot> quiescent() {
      return probe.quiescent();
    }

    public byte[] placement() {
      return reader.execute(
          List.of(
              "/usr/bin/systemctl",
              "--system",
              "--no-pager",
              "--no-ask-password",
              "show",
              "--property=Id,Slice,Delegate,ControlGroup",
              UNIT),
          1024);
    }
  }

  static final class NioIo implements Io {
    public Map<String, Object> attributes(Path held) throws IOException {
      return Files.readAttributes(held, "unix:mode,uid,gid,nlink,size,dev,ino");
    }

    public String filesystem(Path held) throws IOException {
      return Files.getFileStore(held).type();
    }
  }
}
