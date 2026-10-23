package dev.codex.schubert.nk.batch.monitoring;

import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.Condition;
import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.Event;
import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.Service;
import dev.codex.schubert.nk.batch.monitoring.TransferMetricRecorder.Usage;
import io.micrometer.core.instrument.MeterRegistry;
import java.util.Objects;
import java.util.Optional;

/**
 * Supplied-count alert/metric connection only, not real collection or admission control.
 * RD171/UI252/SS341351; PG-D538/TRANSFERCONN001..008/spec1619.
 */
public final class TransferHealthMonitor {
  public record Evaluation(boolean suppliedValuePresent, Optional<Event> event) {
    public Evaluation {
      Objects.requireNonNull(event, "transfer alert transition");
    }
  }

  private final MonitoringPoller<Evaluation> poller = new MonitoringPoller<>();
  private final AlertThresholds thresholds = new AlertThresholds();
  private final AlertLifecycle lifecycle;
  private final TransferMetricRecorder metrics;

  public TransferHealthMonitor(MeterRegistry registry, String mode, Service service) {
    lifecycle = new AlertLifecycle(Condition.TRANSFER, service);
    metrics = new TransferMetricRecorder(registry, mode);
  }

  public Evaluation observe(
      Optional<Usage> supplied, boolean consecutive, ObservationContext context) {
    Objects.requireNonNull(supplied, "supplied transfer usage");
    return poller.observe(
        consecutive,
        context,
        (continuous, at) -> {
          if (!continuous || supplied.isEmpty()) lifecycle.interruptContinuity(at.elapsed());
          if (supplied.isEmpty()) {
            metrics.missing();
            return new Evaluation(false, lifecycle.snapshot());
          }
          Usage usage = supplied.orElseThrow();
          var event =
              lifecycle.observe(
                  thresholds.transfer(usage.totalBytes(), usage.totalFiles()),
                  at.clearance(),
                  at.at(),
                  at.elapsed());
          metrics.record(usage);
          return new Evaluation(true, event);
        });
  }

  public Optional<Event> snapshot() {
    return lifecycle.snapshot();
  }

  public Optional<Usage> observedUsage() {
    return metrics.snapshot();
  }

  public boolean detailedMetricsRequested() {
    return metrics.detailedMetricsRequested();
  }
}
