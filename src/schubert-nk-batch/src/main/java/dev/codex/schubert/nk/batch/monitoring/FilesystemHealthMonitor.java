package dev.codex.schubert.nk.batch.monitoring;

import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.CauseClearance;
import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.Event;
import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.Service;
import java.nio.file.FileStore;
import java.util.Objects;
import java.util.Optional;
import java.util.OptionalDouble;

/**
 * One health-input-to-alert path; no scheduler, path ownership, control action or resource close.
 * NK-OPS-001/P018-09; RD171/UI252/SS351; PG-D529/FSINPUT008..010/spec1582.
 */
public final class FilesystemHealthMonitor {
  private final Object lock = new Object();
  private final FilesystemHealthObservation source;
  private final TimedFilesystemMonitor monitor;
  private boolean continuityInterrupted;

  public FilesystemHealthMonitor(FileStore store, Service service) {
    source = new FilesystemHealthObservation(store);
    monitor = new TimedFilesystemMonitor(service);
  }

  /** Only the outer owner establishes actual source/cause/time continuity and polling deadlines. */
  public TimedFilesystemMonitor.Evaluation observe(
      boolean consecutive, ObservationContext context) {
    Objects.requireNonNull(context, "observation context");
    synchronized (lock) {
      return observeLocked(consecutive, context);
    }
  }

  /** Capture time and input in one serialized poll; a failed clock never implies continuity. */
  public TimedFilesystemMonitor.Evaluation observeNow(
      boolean consecutive, CauseClearance clearance, MonitoringObservationClock clock) {
    Objects.requireNonNull(clearance, "cause clearance");
    Objects.requireNonNull(clock, "observation clock");
    synchronized (lock) {
      final ObservationContext context;
      try {
        context = clock.context(clearance);
      } catch (RuntimeException | Error unavailableClock) {
        continuityInterrupted = true;
        throw unavailableClock;
      }
      return observeLocked(consecutive, context);
    }
  }

  private TimedFilesystemMonitor.Evaluation observeLocked(
      boolean consecutive, ObservationContext context) {
    final OptionalDouble percent;
    try {
      percent = source.read();
    } catch (RuntimeException | Error unavailableInput) {
      continuityInterrupted = true;
      throw unavailableInput;
    }
    var result = monitor.observe(percent, consecutive && !continuityInterrupted, context);
    continuityInterrupted = false;
    return result;
  }

  public Optional<Event> snapshot() {
    return monitor.snapshot();
  }
}
