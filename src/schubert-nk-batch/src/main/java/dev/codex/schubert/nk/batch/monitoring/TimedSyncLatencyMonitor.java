package dev.codex.schubert.nk.batch.monitoring;

import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.Condition;
import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.Event;
import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.Service;
import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.Severity;
import dev.codex.schubert.nk.batch.monitoring.ContinuousConditionWindow.State;
import java.time.Duration;
import java.util.Objects;
import java.util.Optional;
import java.util.OptionalDouble;

/**
 * Supplied p95 only, not a percentile calculator or real endpoint. RD171/UI252/SS351;
 * PG-D535/SYNCTIME001..008/spec1607.
 */
public final class TimedSyncLatencyMonitor {
  public record Evaluation(boolean suppliedValuePresent, Optional<Event> event) {
    public Evaluation {
      Objects.requireNonNull(event, "latency alert transition");
    }
  }

  private final Object lock = new Object();
  private final AlertThresholds thresholds = new AlertThresholds();
  private final ContinuousConditionWindow warning = new ContinuousConditionWindow();
  private final ContinuousConditionWindow critical = new ContinuousConditionWindow();
  private final AlertLifecycle lifecycle;
  private Optional<Duration> lastElapsed = Optional.empty();

  public TimedSyncLatencyMonitor(Service service) {
    lifecycle = new AlertLifecycle(Condition.SYNC_P95, service);
  }

  public Evaluation observe(
      OptionalDouble seconds, boolean consecutive, ObservationContext context) {
    Objects.requireNonNull(seconds, "supplied p95 seconds");
    Objects.requireNonNull(context, "observation context");
    if (seconds.isPresent())
      thresholds.syncP95(seconds.orElseThrow(), Duration.ZERO, Duration.ZERO);
    Duration elapsed = context.elapsed();
    synchronized (lock) {
      if (lastElapsed.isPresent() && elapsed.compareTo(lastElapsed.orElseThrow()) < 0)
        throw new IllegalArgumentException("invalid monitoring sequence");
      lastElapsed = Optional.of(elapsed);
      if (!consecutive || seconds.isEmpty()) lifecycle.interruptContinuity(elapsed);
      boolean aboveWarning =
          seconds.isPresent() && AlertThresholds.syncLatencyAboveWarning(seconds.orElseThrow());
      var above2 =
          warning.observe(
              seconds.isEmpty() ? State.UNKNOWN : aboveWarning ? State.VIOLATING : State.NORMAL,
              elapsed,
              consecutive);
      var above2Point5 =
          critical.observe(
              seconds.isEmpty()
                  ? State.UNKNOWN
                  : seconds.orElseThrow() > 2.5 ? State.VIOLATING : State.NORMAL,
              elapsed,
              consecutive);
      if (seconds.isEmpty()) return new Evaluation(false, lifecycle.snapshot());
      Severity level =
          thresholds.syncP95(
              seconds.orElseThrow(), above2.orElseThrow(), above2Point5.orElseThrow());
      return new Evaluation(true, lifecycle.observeWindowed(level, aboveWarning, context));
    }
  }

  public Optional<Event> snapshot() {
    synchronized (lock) {
      return lifecycle.snapshot();
    }
  }
}
