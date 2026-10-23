package dev.codex.schubert.nk.batch.monitoring;

import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.Condition;
import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.Event;
import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.Service;
import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.Severity;
import java.util.Objects;
import java.util.Optional;
import java.util.OptionalLong;

/** Supplied Backup health only, no backup invocation/status discovery. RD171/UI252/SS351; 1683. */
public final class BackupHealthMonitor {
  /** Caller supplies one coherent scheduled-run/current-day observation, not inferred wall time. */
  public record Completion(boolean scheduledRunPassed, boolean todaySuccess) {}

  public record Evaluation(
      boolean completionPresent, boolean failureCountPresent, Optional<Event> event) {
    public Evaluation {
      Objects.requireNonNull(event, "backup alert transition");
    }
  }

  private final MonitoringPoller<Evaluation> poller = new MonitoringPoller<>();
  private final AlertThresholds thresholds = new AlertThresholds();
  private final AlertLifecycle lifecycle = new AlertLifecycle(Condition.BACKUP, Service.BATCH);

  /** Partial known abnormal evidence may alert, but only complete evidence can recover normally. */
  public Evaluation observe(
      Optional<Completion> completion,
      OptionalLong consecutiveFailures,
      boolean consecutive,
      ObservationContext context) {
    Objects.requireNonNull(completion, "supplied backup completion");
    Objects.requireNonNull(consecutiveFailures, "supplied backup consecutive failures");
    Completion status = completion.orElse(new Completion(false, false));
    Severity level =
        thresholds.backup(
            status.scheduledRunPassed(), status.todaySuccess(), consecutiveFailures.orElse(0));
    boolean complete = completion.isPresent() && consecutiveFailures.isPresent();
    return poller.observe(
        consecutive,
        context,
        (continuous, at) -> {
          if (!continuous || !complete) lifecycle.interruptContinuity(at.elapsed());
          Optional<Event> event =
              !complete && level == Severity.NORMAL
                  ? lifecycle.snapshot()
                  : lifecycle.observe(level, at.clearance(), at.at(), at.elapsed());
          return new Evaluation(completion.isPresent(), consecutiveFailures.isPresent(), event);
        });
  }

  public Optional<Event> snapshot() {
    return lifecycle.snapshot();
  }
}
