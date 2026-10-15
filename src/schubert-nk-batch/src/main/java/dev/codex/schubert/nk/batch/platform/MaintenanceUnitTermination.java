package dev.codex.schubert.nk.batch.platform;

import dev.codex.schubert.nk.storage.LinuxHostDirectoryCalls;
import dev.codex.schubert.nk.storage.LinuxInodeSecurity;
import java.io.IOException;
import java.util.Arrays;
import java.util.List;
import java.util.Objects;
import java.util.Optional;
import org.jspecify.annotations.NullMarked;

/**
 * Fixed whole-Unit observation, not stop execution, clean stop or startup authority. Parent keeps
 * continuous M/A; child observes only WEB/API and cannot inherit the parent's lock authority.
 * NK-OPS-001/UI251/253/SS3415/343/SSC100104; MSTOP/BTERM; BUG308/YKT241; PG335.
 */
@NullMarked
public final class MaintenanceUnitTermination {
  interface Observations {
    MaintenanceStopSnapshot read() throws IOException;

    byte[] processes() throws IOException;
  }

  private final Object stateLock = new Object();
  private final FixedUnitCgroupNamespace.Context context;
  private final MaintenanceUnit unit;
  private final Observations observations;
  private final FixedUnitCgroupNamespace namespace;

  public static MaintenanceUnitTermination create(
      RootStartupContext context, RootStartupContext.Snapshot expected, MaintenanceUnit unit)
      throws IOException {
    Objects.requireNonNull(context, "root context");
    Objects.requireNonNull(expected, "root identity");
    Objects.requireNonNull(unit, "fixed Unit");
    require(expected.service() == RootStartupContext.Service.MORNING);
    context.recheck(expected);
    return nativeObserver(context, expected, unit);
  }

  /** Cleanup child may observe only the two application Units under its own fixed root actor. */
  public static MaintenanceUnitTermination createCleanup(
      RootStartupContext context, RootStartupContext.Snapshot expected, MaintenanceUnit unit)
      throws IOException {
    Objects.requireNonNull(context, "root context");
    Objects.requireNonNull(expected, "root identity");
    Objects.requireNonNull(unit, "fixed Unit");
    require(
        expected.service() == RootStartupContext.Service.CLEANUP
            && (unit == MaintenanceUnit.WEB || unit == MaintenanceUnit.API));
    context.recheck(expected);
    return nativeObserver(context, expected, unit);
  }

  private static MaintenanceUnitTermination nativeObserver(
      RootStartupContext context, RootStartupContext.Snapshot expected, MaintenanceUnit unit) {
    return new MaintenanceUnitTermination(
        () -> context.recheck(expected),
        unit,
        new NativeObservations(unit, new InspectorUnitProbe.NativeReader()),
        new FixedUnitCgroupNamespace(
            () -> context.recheck(expected),
            LinuxHostDirectoryCalls.create(),
            LinuxInodeSecurity.create(),
            new BackupUnitTermination.NioIo()));
  }

  MaintenanceUnitTermination(
      FixedUnitCgroupNamespace.Context context,
      MaintenanceUnit unit,
      Observations observations,
      FixedUnitCgroupNamespace namespace) {
    this.context = Objects.requireNonNull(context, "root context");
    this.unit = Objects.requireNonNull(unit, "fixed Unit");
    this.observations = Objects.requireNonNull(observations, "fixed observations");
    this.namespace = Objects.requireNonNull(namespace, "host namespace");
  }

  public Optional<MaintenanceStopSnapshot> quiescent() throws IOException {
    return quiescentObservation().map(Observation::manager);
  }

  /** SSC126: retained actual verified data; not a stop request or detached startup authority. */
  public record KernelDirectory(int mode, int uid, int gid, long device, long inode) {}

  public static final class Observation {
    private final MaintenanceStopSnapshot retainedManager;
    private final List<KernelDirectory> retainedDirectories;
    private final boolean present;

    private Observation(MaintenanceStopSnapshot manager, FixedUnitCgroupNamespace.Snapshot kernel) {
      this.retainedManager = manager;
      retainedDirectories =
          List.copyOf(
              kernel.identities().stream()
                  .map(i -> new KernelDirectory(i.mode(), i.uid(), i.gid(), i.device(), i.inode()))
                  .toList());
      present = kernel.present();
    }

    public MaintenanceStopSnapshot manager() {
      return retainedManager;
    }

    public List<KernelDirectory> directories() {
      return retainedDirectories;
    }

    public boolean leafPresent() {
      return present;
    }

    @Override
    public String toString() {
      return "MaintenanceTerminationObservation[actual=<redacted>]";
    }
  }

  public Optional<Observation> quiescentObservation() throws IOException {
    synchronized (stateLock) {
      try {
        check();
        var before = read();
        if (!before.quiescent()) {
          check();
          return Optional.empty();
        }
        var first = namespace.observe(unit);
        if (first.present()) {
          require(unit.controlGroup().equals(before.controlGroup()));
          byte[] processes =
              Objects.requireNonNull(observations.processes(), "whole Unit processes");
          boolean empty;
          try {
            empty =
                Arrays.equals(processes, new byte[] {'a', '(', 's', 'u', 's', ')', ' ', '0', '\n'});
          } finally {
            Arrays.fill(processes, (byte) 0);
          }
          if (!empty) {
            check();
            return Optional.empty();
          }
        }
        require(before.matches(read()));
        require(first.equals(namespace.observe(unit)));
        require(before.matches(read()));
        check();
        return Optional.of(new Observation(before, first));
      } catch (IOException failure) {
        throw unavailable();
      }
    }
  }

  private MaintenanceStopSnapshot read() throws IOException {
    check();
    var value = Objects.requireNonNull(observations.read(), "fixed Unit state");
    require(value.unit() == unit);
    return value;
  }

  private void check() throws IOException {
    require(!Thread.currentThread().isInterrupted());
    context.recheck();
    namespace.check();
  }

  private static void require(boolean valid) throws IOException {
    if (!valid) throw unavailable();
  }

  private static IOException unavailable() {
    return new IOException("maintenance termination unavailable");
  }

  static final class NativeObservations implements Observations {
    private final MaintenanceUnit unit;
    private final InspectorUnitProbe.NativeReader query;

    NativeObservations(MaintenanceUnit unit, InspectorUnitProbe.NativeReader query) {
      this.unit = Objects.requireNonNull(unit, "fixed Unit");
      this.query = Objects.requireNonNull(query, "fixed reader");
    }

    public MaintenanceStopSnapshot read() {
      byte[] bytes =
          query.execute(
              List.of(
                  "/usr/bin/systemctl",
                  "--system",
                  "--no-pager",
                  "--no-ask-password",
                  "show",
                  "--property=" + MaintenanceStopSnapshot.PROPERTIES,
                  unit.serviceName()),
              2048);
      try {
        return MaintenanceStopSnapshot.parse(unit, bytes);
      } finally {
        Arrays.fill(bytes, (byte) 0);
      }
    }

    public byte[] processes() {
      return query.execute(
          List.of(
              "/usr/bin/busctl",
              "--system",
              "--timeout=5s",
              "--no-pager",
              "call",
              "org.freedesktop.systemd1",
              "/org/freedesktop/systemd1",
              "org.freedesktop.systemd1.Manager",
              "GetUnitProcesses",
              "s",
              unit.serviceName()),
          9);
    }
  }
}
