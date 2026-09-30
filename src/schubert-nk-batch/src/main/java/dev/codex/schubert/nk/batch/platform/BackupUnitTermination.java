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

  @FunctionalInterface
  interface Context extends FixedUnitCgroupNamespace.Context {}

  interface Observations {
    InspectorUnitSnapshot read();

    byte[] placement();

    Optional<InspectorUnitSnapshot> quiescent();
  }

  interface Io extends FixedUnitCgroupNamespace.Io {}

  private final Object stateLock = new Object();
  private final Context context;
  private final Observations observations;
  private final DirectoryCalls host;
  private final InodeSecurityCalls security;
  private final Io io;
  private final BackupUnitStartClient.Target target;

  public static BackupUnitTermination create(
      RootStartupContext context, RootStartupContext.Snapshot expected) throws IOException {
    return create(context, expected, BackupUnitStartClient.Target.BACKUP);
  }

  public static BackupUnitTermination create(
      RootStartupContext context,
      RootStartupContext.Snapshot expected,
      BackupUnitStartClient.Target target)
      throws IOException {
    Objects.requireNonNull(context, "root context");
    Objects.requireNonNull(expected, "root identity");
    Objects.requireNonNull(target, "closed phase");
    require(expected.service() == RootStartupContext.Service.MORNING);
    context.recheck(expected);
    return new BackupUnitTermination(
        () -> context.recheck(expected),
        NativeObservations.forTarget(target),
        LinuxHostDirectoryCalls.create(),
        LinuxInodeSecurity.create(),
        new NioIo(),
        target);
  }

  BackupUnitTermination(
      Context context,
      Observations observations,
      DirectoryCalls host,
      InodeSecurityCalls security,
      Io io) {
    this(context, observations, host, security, io, BackupUnitStartClient.Target.BACKUP);
  }

  BackupUnitTermination(
      Context context,
      Observations observations,
      DirectoryCalls host,
      InodeSecurityCalls security,
      Io io,
      BackupUnitStartClient.Target target) {
    this.context = Objects.requireNonNull(context, "root context");
    this.observations = Objects.requireNonNull(observations, "fixed observations");
    this.host = Objects.requireNonNull(host, "host view");
    this.security = Objects.requireNonNull(security, "inode security");
    this.io = Objects.requireNonNull(io, "inode IO");
    this.target = Objects.requireNonNull(target, "closed phase");
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
        FixedUnitCgroupNamespace.Snapshot first = namespace();
        if (first.present()) {
          // SSC100/BUG308: a manager with no group cannot attest this present kernel tree.
          require(target.unit().controlGroup().equals(placement.get("ControlGroup")));
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

  private FixedUnitCgroupNamespace.Snapshot namespace() throws IOException {
    return new FixedUnitCgroupNamespace(context, host, security, io).observe(target.unit());
  }

  private Map<String, String> placement(byte[] bytes) throws IOException {
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
          target.unit().serviceName().equals(fields.get("Id"))
              && "system.slice".equals(fields.get("Slice"))
              && "no".equals(fields.get("Delegate")));
      String group = Objects.requireNonNull(fields.get("ControlGroup"), "fixed group field");
      require(group.isEmpty() || target.unit().controlGroup().equals(group));
      return Map.copyOf(fields);
    } finally {
      Arrays.fill(bytes, (byte) 0);
    }
  }

  private static void require(boolean valid) throws IOException {
    if (!valid) throw unavailable();
  }

  private static IOException unavailable() {
    return new IOException("backup termination unavailable");
  }

  static final class NativeObservations implements Observations {
    private final InspectorUnitProbe probe;
    private final InspectorUnitProbe.NativeReader reader;
    private final String unit;

    NativeObservations() {
      this(InspectorUnitProbe.NativeReader.forTarget(InspectorUnitSnapshot.Target.BACKUP));
    }

    static NativeObservations forTarget(BackupUnitStartClient.Target target) {
      Objects.requireNonNull(target, "closed phase");
      return new NativeObservations(
          InspectorUnitProbe.NativeReader.forTarget(target.observation()),
          InspectorUnitProbe.forTarget(target.observation()),
          target.unit().serviceName());
    }

    NativeObservations(InspectorUnitProbe.NativeReader reader) {
      this(reader, InspectorUnitProbe.forTarget(InspectorUnitSnapshot.Target.BACKUP));
    }

    NativeObservations(InspectorUnitProbe.NativeReader reader, InspectorUnitProbe probe) {
      this(reader, probe, UNIT);
    }

    private NativeObservations(
        InspectorUnitProbe.NativeReader reader, InspectorUnitProbe probe, String unit) {
      this.reader = Objects.requireNonNull(reader, "fixed reader");
      this.probe = Objects.requireNonNull(probe, "fixed backup probe");
      this.unit = Objects.requireNonNull(unit, "closed unit");
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
              unit),
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
