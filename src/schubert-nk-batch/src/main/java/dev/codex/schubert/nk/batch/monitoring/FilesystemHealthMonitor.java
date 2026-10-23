package dev.codex.schubert.nk.batch.monitoring;

import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.Event;
import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.Service;
import java.nio.file.FileStore;
import java.util.Objects;
import java.util.Optional;

/**
 * One health-input-to-alert path; no scheduler, path ownership, control action or resource close.
 * NK-OPS-001/P018-09; RD171/UI252/SS351; PG-D529/FSINPUT008..010/spec1582.
 */
public final class FilesystemHealthMonitor {
  private final Object lock = new Object();
  private final FilesystemHealthObservation source;
  private final TimedFilesystemMonitor monitor;

  public FilesystemHealthMonitor(FileStore store, Service service) {
    source = new FilesystemHealthObservation(store);
    monitor = new TimedFilesystemMonitor(service);
  }

  /** Only the outer owner establishes actual source/cause/time continuity and polling deadlines. */
  public TimedFilesystemMonitor.Evaluation observe(
      boolean consecutive, ObservationContext context) {
    Objects.requireNonNull(context, "observation context");
    synchronized (lock) {
      return monitor.observe(source.read(), consecutive, context);
    }
  }

  public Optional<Event> snapshot() {
    return monitor.snapshot();
  }
}
