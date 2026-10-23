package dev.codex.schubert.nk.batch.monitoring;

import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.CauseClearance;
import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.Event;
import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.Service;
import java.lang.management.MemoryMXBean;
import java.util.Optional;

/**
 * Borrowed heap input/time to one alert owner, no actual JVM control or provider admission.
 * NK-OPS-001/P018-09; RD171/UI252/SS351; PG-D533/HEAPCONN001..008/spec1599.
 */
public final class JvmHeapHealthMonitor {
  private final MonitoringPoller<TimedJvmHeapMonitor.Evaluation> poller = new MonitoringPoller<>();
  private final JvmHeapHealthObservation source;
  private final TimedJvmHeapMonitor monitor;

  public JvmHeapHealthMonitor(MemoryMXBean bean, Service service) {
    source = JvmHeapHealthObservation.from(bean);
    monitor = new TimedJvmHeapMonitor(service);
  }

  public TimedJvmHeapMonitor.Evaluation observe(
      boolean consecutive, boolean outOfMemoryReported, ObservationContext context) {
    return poller.observe(
        consecutive,
        context,
        (continuous, at) -> monitor.observe(source.read(), outOfMemoryReported, continuous, at));
  }

  public TimedJvmHeapMonitor.Evaluation observeNow(
      boolean consecutive,
      boolean outOfMemoryReported,
      CauseClearance clearance,
      MonitoringObservationClock clock) {
    return poller.observeNow(
        consecutive,
        clearance,
        clock,
        (continuous, at) -> monitor.observe(source.read(), outOfMemoryReported, continuous, at));
  }

  public Optional<Event> snapshot() {
    return monitor.snapshot();
  }
}
