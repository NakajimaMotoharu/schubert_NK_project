package dev.codex.schubert.nk.batch.monitoring;

import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.Condition;
import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.Event;
import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.Service;
import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.Severity;
import java.util.Objects;
import java.util.Optional;
import java.util.OptionalLong;

/** Supplied failure count only, no integrity probe/repair/retirement. RD171/UI252/SS351; 1687. */
public final class IntegrityHealthMonitor {
  public record Evaluation(boolean failureCountPresent, Optional<Event> event) {
    public Evaluation {
      Objects.requireNonNull(event, "integrity alert transition");
    }
  }

  private final MonitoringPoller<Evaluation> poller = new MonitoringPoller<>();
  private final AlertThresholds thresholds = new AlertThresholds();
  private final AlertLifecycle lifecycle;

  public IntegrityHealthMonitor(Service service) {
    lifecycle = new AlertLifecycle(Condition.INTEGRITY_CONFIG, service);
  }

  /**
   * Missing evidence is not normal, and even confirmed normal cannot auto-close protected alerts.
   */
  public Evaluation observe(
      OptionalLong failures, boolean consecutive, ObservationContext context) {
    Objects.requireNonNull(failures, "supplied integrity failure count");
    Severity level = thresholds.integrity(failures.orElse(0));
    return poller.observe(
        consecutive,
        context,
        (continuous, at) -> {
          if (!continuous || failures.isEmpty()) lifecycle.interruptContinuity(at.elapsed());
          Optional<Event> event =
              failures.isEmpty()
                  ? lifecycle.snapshot()
                  : lifecycle.observe(level, at.clearance(), at.at(), at.elapsed());
          return new Evaluation(failures.isPresent(), event);
        });
  }

  public Optional<Event> snapshot() {
    return lifecycle.snapshot();
  }
}
