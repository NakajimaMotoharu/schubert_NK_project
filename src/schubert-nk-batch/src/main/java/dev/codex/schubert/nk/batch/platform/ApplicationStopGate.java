package dev.codex.schubert.nk.batch.platform;

import java.util.Objects;
import org.jspecify.annotations.NullMarked;

/**
 * Read-only, fresh API/Web observations. Caller holds maintenance OS lock and prevents restarts;
 * this is neither a stop command nor a permanent lease. NK-OPS-001; OPS-009/AVL; UI251;
 * SS311/341/343; SSC-049/PG-D-148; PT-OPS-STOP-001..008.
 */
@NullMarked
public final class ApplicationStopGate {
  @FunctionalInterface
  interface StateSource {
    byte[] read(ApplicationUnit unit);
  }

  private final StateSource source;

  public static ApplicationStopGate create() {
    return new ApplicationStopGate(new SystemctlStateSource());
  }

  ApplicationStopGate(StateSource source) {
    this.source = Objects.requireNonNull(source, "state source");
  }

  /** Verify both units now; any failure prevents success and preserves interruption. No caching. */
  public void requireStopped() {
    for (var unit : ApplicationUnit.values()) {
      checkInterrupt();
      byte[] bytes = source.read(unit);
      checkInterrupt();
      UnitStateParser.requireStopped(unit, bytes);
    }
    checkInterrupt();
  }

  private static void checkInterrupt() {
    if (Thread.currentThread().isInterrupted())
      throw new StopGateException(StopGateFailure.INTERRUPTED);
  }
}
