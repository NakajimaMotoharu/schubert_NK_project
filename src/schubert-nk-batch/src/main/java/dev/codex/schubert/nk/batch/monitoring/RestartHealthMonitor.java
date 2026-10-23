package dev.codex.schubert.nk.batch.monitoring;

import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.Condition;
import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.Event;
import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.Service;
import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.Severity;
import java.util.Objects;
import java.util.Optional;
import java.util.OptionalLong;

/** Supplied restart health only, not systemd/history/control. RD171/UI252/SS351; 1685/BUG1668. */
public final class RestartHealthMonitor {
  public record Evaluation(
      boolean restartCountPresent, boolean rateLimitPresent, Optional<Event> event) {
    public Evaluation {
      Objects.requireNonNull(event, "restart alert transition");
    }
  }

  private final MonitoringPoller<Evaluation> poller = new MonitoringPoller<>();
  private final AlertThresholds thresholds = new AlertThresholds();
  private final AlertLifecycle lifecycle;

  public RestartHealthMonitor(Service service) {
    lifecycle = new AlertLifecycle(Condition.RESTART, service);
  }

  /** Count and rate-limit state are independent; incomplete evidence never establishes recovery. */
  public Evaluation observe(
      OptionalLong lastTenMinutes,
      Optional<Boolean> rateLimited,
      boolean consecutive,
      ObservationContext context) {
    Objects.requireNonNull(lastTenMinutes, "supplied restart count");
    Objects.requireNonNull(rateLimited, "supplied restart rate limit");
    Severity level = thresholds.restarts(lastTenMinutes.orElse(0), rateLimited.orElse(false));
    boolean complete = lastTenMinutes.isPresent() && rateLimited.isPresent();
    return poller.observe(
        consecutive,
        context,
        (continuous, at) -> {
          if (!continuous || !complete) lifecycle.interruptContinuity(at.elapsed());
          Optional<Event> event =
              !complete && level == Severity.NORMAL
                  ? lifecycle.snapshot()
                  : lifecycle.observe(level, at.clearance(), at.at(), at.elapsed());
          return new Evaluation(lastTenMinutes.isPresent(), rateLimited.isPresent(), event);
        });
  }

  public Optional<Event> snapshot() {
    return lifecycle.snapshot();
  }
}
