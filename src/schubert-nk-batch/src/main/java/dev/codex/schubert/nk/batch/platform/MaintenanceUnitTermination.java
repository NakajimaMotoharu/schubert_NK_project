package dev.codex.schubert.nk.batch.platform;

import dev.codex.schubert.nk.storage.*;
import java.io.IOException;
import java.util.*;
import org.jspecify.annotations.NullMarked;

/**
 * Root parent's fixed whole-Unit observation, not stop execution, clean stop or startup authority.
 * NK-OPS-001/UI251/253/SS3415/343/SSC100; MSTOP/BTERM; BUG308/YKT241. Caller keeps continuous M/A
 * and forbids independent starts. Parent/client quarantine is separate.
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
        return Optional.of(before);
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
