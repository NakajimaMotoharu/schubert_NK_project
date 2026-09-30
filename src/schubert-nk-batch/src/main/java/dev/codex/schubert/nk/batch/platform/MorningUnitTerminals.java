package dev.codex.schubert.nk.batch.platform;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.Objects;
import org.jspecify.annotations.NullMarked;

/**
 * Fresh fixed-eight whole-Unit/kernel termination check for the root Morning parent. A caller must
 * hold M, and after stop also A, through this observation and its next operation. Observation alone
 * is not stop execution, Artemis clean journal, backup success or startup permit authority.
 * NK-OPS-001; OPS009/UI251/SS341§5/343/SSC100; PG337/PT-OPS-MTERMS001-005.
 */
@NullMarked
public final class MorningUnitTerminals {
  @FunctionalInterface
  interface Observation {
    boolean quiescent(MaintenanceUnit unit) throws IOException;
  }

  @FunctionalInterface
  interface DetailedObservation {
    java.util.Optional<MaintenanceUnitTermination.Observation> read(MaintenanceUnit unit)
        throws IOException;
  }

  private MorningUnitTerminals() {}

  /** Actual A-after-stop observations, carried only by the verified native parent continuation. */
  public static final class Snapshot {
    private final RootStartupContext.Snapshot parent;
    private final List<MaintenanceUnitTermination.Observation> units;

    private Snapshot(
        RootStartupContext.Snapshot parent, List<MaintenanceUnitTermination.Observation> units) {
      this.parent = parent;
      this.units = List.copyOf(units);
    }

    public RootStartupContext.Snapshot parent() {
      return parent;
    }

    public List<MaintenanceUnitTermination.Observation> units() {
      return units;
    }

    @Override
    public String toString() {
      return "MorningStopSet[actual=<redacted>]";
    }
  }

  public static void requireQuiescent(
      RootStartupContext context, RootStartupContext.Snapshot expected) throws IOException {
    capture(context, expected);
  }

  public static Snapshot capture(RootStartupContext context, RootStartupContext.Snapshot expected)
      throws IOException {
    return capture(
        context,
        expected,
        unit -> MaintenanceUnitTermination.create(context, expected, unit).quiescentObservation());
  }

  static Snapshot capture(
      RootStartupContext context,
      RootStartupContext.Snapshot expected,
      DetailedObservation observer)
      throws IOException {
    Objects.requireNonNull(context, "Morning root context");
    Objects.requireNonNull(expected, "Morning root snapshot");
    Objects.requireNonNull(observer, "actual whole-Unit observations");
    if (expected.service() != RootStartupContext.Service.MORNING) throw unavailable();
    context.recheck(expected);
    var units = new ArrayList<MaintenanceUnitTermination.Observation>();
    requireQuiescent(
        unit -> {
          var actual = Objects.requireNonNull(observer.read(unit), "actual terminal observation");
          if (actual.isPresent() && actual.orElseThrow().manager().unit() != unit)
            throw unavailable();
          actual.ifPresent(units::add);
          return actual.isPresent();
        });
    context.recheck(expected);
    return new Snapshot(expected, units);
  }

  static void requireQuiescent(Observation observation) throws IOException {
    Objects.requireNonNull(observation, "fixed eight-Unit observation");
    try {
      for (MaintenanceUnit unit : MaintenanceUnit.values()) {
        if (Thread.currentThread().isInterrupted()) throw unavailable();
        if (!observation.quiescent(unit)) throw unavailable();
      }
      if (Thread.currentThread().isInterrupted()) throw unavailable();
    } catch (StopGateException known) {
      throw unavailable();
    }
  }

  private static IOException unavailable() {
    return new IOException("Morning whole-Unit termination unavailable");
  }
}
