package dev.codex.schubert.nk.batch.monitoring;

import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.CauseClearance;
import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.Event;
import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.Service;
import java.nio.file.FileStore;
import java.util.Optional;

/**
 * One health-input-to-alert path; no scheduler, path ownership, control action or resource close.
 * NK-OPS-001/P018-09; RD171/UI252/SS351; PG-D529/FSINPUT008..010/spec1582.
 */
public final class FilesystemHealthMonitor {
  private final MonitoringPoller<TimedFilesystemMonitor.Evaluation> poller =
      new MonitoringPoller<>();
  private final FilesystemHealthObservation source;
  private final TimedFilesystemMonitor monitor;

  public FilesystemHealthMonitor(FileStore store, Service service) {
    source = new FilesystemHealthObservation(store);
    monitor = new TimedFilesystemMonitor(service);
  }

  /** Only the outer owner establishes actual source/cause/time continuity and polling deadlines. */
  public TimedFilesystemMonitor.Evaluation observe(
      boolean consecutive, ObservationContext context) {
    return poller.observe(
        consecutive, context, (continuous, at) -> monitor.observe(source.read(), continuous, at));
  }

  /** Capture time and input in one serialized poll; a failed clock never implies continuity. */
  public TimedFilesystemMonitor.Evaluation observeNow(
      boolean consecutive, CauseClearance clearance, MonitoringObservationClock clock) {
    return poller.observeNow(
        consecutive,
        clearance,
        clock,
        (continuous, at) -> monitor.observe(source.read(), continuous, at));
  }

  public Optional<Event> snapshot() {
    return monitor.snapshot();
  }
}
