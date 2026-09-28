package dev.codex.schubert.nk.batch.platform;

import java.io.IOException;
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

  private MorningUnitTerminals() {}

  public static void requireQuiescent(
      RootStartupContext context, RootStartupContext.Snapshot expected) throws IOException {
    Objects.requireNonNull(context, "Morning root context");
    Objects.requireNonNull(expected, "Morning root snapshot");
    if (expected.service() != RootStartupContext.Service.MORNING) throw unavailable();
    context.recheck(expected);
    requireQuiescent(
        unit -> MaintenanceUnitTermination.create(context, expected, unit).quiescent().isPresent());
    context.recheck(expected);
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
