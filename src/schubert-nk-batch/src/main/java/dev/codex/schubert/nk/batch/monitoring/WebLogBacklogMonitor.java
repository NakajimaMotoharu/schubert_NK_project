package dev.codex.schubert.nk.batch.monitoring;

import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.Condition;
import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.Event;
import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.Service;
import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.Severity;
import java.time.Duration;
import java.util.Objects;
import java.util.Optional;
import java.util.OptionalLong;

/** Supplied backlog evidence only; no broker/DB/controller. RD171/UI252/SS351; PG-D549/1672. */
public final class WebLogBacklogMonitor {
  public record Evaluation(boolean queuedPresent, boolean oldestPresent, Optional<Event> event) {
    public Evaluation {
      Objects.requireNonNull(event, "web log alert transition");
    }
  }

  private final MonitoringPoller<Evaluation> poller = new MonitoringPoller<>();
  private final AlertThresholds thresholds = new AlertThresholds();
  private final AlertLifecycle lifecycle = new AlertLifecycle(Condition.WEB_LOG, Service.WEB);

  /**
   * Known abnormal evidence may raise an alert; partial/unknown evidence can never establish normal
   * recovery. Source identity and any queue/outbox aggregation remain caller obligations.
   */
  public Evaluation observe(
      OptionalLong queued,
      Optional<Duration> oldest,
      boolean consecutive,
      ObservationContext context) {
    Objects.requireNonNull(queued, "supplied web log count");
    Objects.requireNonNull(oldest, "supplied web log age");
    Severity level = thresholds.webLog(queued.orElse(0), oldest.orElse(Duration.ZERO));
    boolean complete = queued.isPresent() && oldest.isPresent();
    return poller.observe(
        consecutive,
        context,
        (continuous, at) -> {
          if (!continuous || !complete) lifecycle.interruptContinuity(at.elapsed());
          Optional<Event> event =
              !complete && level == Severity.NORMAL
                  ? lifecycle.snapshot()
                  : lifecycle.observe(level, at.clearance(), at.at(), at.elapsed());
          return new Evaluation(queued.isPresent(), oldest.isPresent(), event);
        });
  }

  public Optional<Event> snapshot() {
    return lifecycle.snapshot();
  }
}
