package dev.codex.schubert.nk.batch.monitoring;

import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.Condition;
import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.Event;
import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.Service;
import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.Severity;
import java.util.Objects;
import java.util.Optional;
import java.util.OptionalLong;

/** Supplied backlog evidence only; no broker/DB/controller. RD171/UI252/SS351; PG-D550/1674. */
public final class AsyncQueueMonitor {
  public record Evaluation(boolean queuedPresent, boolean capacityPresent, Optional<Event> event) {
    public Evaluation {
      Objects.requireNonNull(event, "async queue alert transition");
    }
  }

  private final MonitoringPoller<Evaluation> poller = new MonitoringPoller<>();
  private final AlertThresholds thresholds = new AlertThresholds();
  private final AlertLifecycle lifecycle = new AlertLifecycle(Condition.ASYNC_QUEUE, Service.API);

  /**
   * Known abnormal evidence may raise an alert; partial/unknown evidence can never establish normal
   * recovery. Source identity and any count/capacity association remain caller obligations.
   */
  public Evaluation observe(
      OptionalLong queued, OptionalLong capacity, boolean consecutive, ObservationContext context) {
    Objects.requireNonNull(queued, "supplied async queue count");
    Objects.requireNonNull(capacity, "supplied async queue capacity");
    Severity level = thresholds.asyncQueue(queued.orElse(0), capacity.orElse(Long.MAX_VALUE));
    boolean complete = queued.isPresent() && capacity.isPresent();
    return poller.observe(
        consecutive,
        context,
        (continuous, at) -> {
          if (!continuous || !complete) lifecycle.interruptContinuity(at.elapsed());
          Optional<Event> event =
              !complete && level == Severity.NORMAL
                  ? lifecycle.snapshot()
                  : lifecycle.observe(level, at.clearance(), at.at(), at.elapsed());
          return new Evaluation(queued.isPresent(), capacity.isPresent(), event);
        });
  }

  public Optional<Event> snapshot() {
    return lifecycle.snapshot();
  }
}
