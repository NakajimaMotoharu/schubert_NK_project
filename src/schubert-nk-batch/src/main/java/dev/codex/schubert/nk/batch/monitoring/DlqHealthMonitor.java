package dev.codex.schubert.nk.batch.monitoring;

import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.Condition;
import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.Event;
import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.Service;
import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.Severity;
import java.util.Objects;
import java.util.Optional;

/**
 * Current-entry DLQ health only, no browse/replay/delete/incident authority.
 * RD171/UI252/SS351;1689.
 */
public final class DlqHealthMonitor {
  /** Flags describe the current entries in this coherent sample, not historical incident status. */
  public record Observation(long messages, boolean increasing, boolean uninvestigated) {
    public Observation {
      if (messages < 0 || (messages == 0 && (increasing || uninvestigated)))
        throw new IllegalArgumentException("invalid DLQ observation");
    }
  }

  public record Evaluation(boolean observationPresent, Optional<Event> event) {
    public Evaluation {
      Objects.requireNonNull(event, "DLQ alert transition");
    }
  }

  private final MonitoringPoller<Evaluation> poller = new MonitoringPoller<>();
  private final AlertThresholds thresholds = new AlertThresholds();
  private final AlertLifecycle lifecycle;

  public DlqHealthMonitor(Service service) {
    lifecycle = new AlertLifecycle(Condition.DLQ, service);
  }

  /** Unknown samples do not establish normal; even known normal cannot auto-close DLQ alerts. */
  public Evaluation observe(
      Optional<Observation> observation, boolean consecutive, ObservationContext context) {
    Objects.requireNonNull(observation, "supplied DLQ observation");
    Observation value = observation.orElse(new Observation(0, false, false));
    Severity level = thresholds.dlq(value.messages(), value.increasing(), value.uninvestigated());
    return poller.observe(
        consecutive,
        context,
        (continuous, at) -> {
          if (!continuous || observation.isEmpty()) lifecycle.interruptContinuity(at.elapsed());
          Optional<Event> event =
              observation.isEmpty()
                  ? lifecycle.snapshot()
                  : lifecycle.observe(level, at.clearance(), at.at(), at.elapsed());
          return new Evaluation(observation.isPresent(), event);
        });
  }

  public Optional<Event> snapshot() {
    return lifecycle.snapshot();
  }
}
