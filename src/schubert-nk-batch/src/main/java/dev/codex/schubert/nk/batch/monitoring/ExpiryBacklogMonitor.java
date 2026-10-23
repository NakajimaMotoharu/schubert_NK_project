package dev.codex.schubert.nk.batch.monitoring;

import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.Condition;
import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.Event;
import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.Service;
import java.util.Objects;
import java.util.Optional;
import java.util.OptionalLong;

/** Supplied count health kernel only, never a queue read/purge/control. PG-D551/1676; SS351. */
public final class ExpiryBacklogMonitor {
  public record Evaluation(boolean suppliedValuePresent, Optional<Event> event) {
    public Evaluation {
      Objects.requireNonNull(event, "expiry alert transition");
    }
  }

  private final MonitoringPoller<Evaluation> poller = new MonitoringPoller<>();
  private final AlertThresholds thresholds = new AlertThresholds();
  private final AlertLifecycle lifecycle = new AlertLifecycle(Condition.EXPIRY, Service.BROKER);

  public Evaluation observe(
      OptionalLong messages, boolean consecutive, ObservationContext context) {
    Objects.requireNonNull(messages, "supplied expiry count");
    var level = thresholds.expiry(messages.orElse(0));
    return poller.observe(
        consecutive,
        context,
        (continuous, at) -> {
          if (!continuous || messages.isEmpty()) lifecycle.interruptContinuity(at.elapsed());
          return new Evaluation(
              messages.isPresent(),
              messages.isEmpty()
                  ? lifecycle.snapshot()
                  : lifecycle.observe(level, at.clearance(), at.at(), at.elapsed()));
        });
  }

  public Optional<Event> snapshot() {
    return lifecycle.snapshot();
  }
}
