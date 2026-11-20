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
 * Supplied pool values only, no JDBC/provider sampling or control. RD171/UI252/SS351;
 * PG-D534/DBTIME001..008/spec1603.
 */
public final class TimedDbPoolMonitor {
  public record Evaluation(boolean suppliedValuePresent, Optional<Event> event) {
    public Evaluation {
      Objects.requireNonNull(event, "pool alert transition");
    }
  }

  private final Object lock = new Object();
  private final AlertThresholds thresholds = new AlertThresholds();
  private final ContinuousConditionWindow warning = new ContinuousConditionWindow();
  private final AlertLifecycle lifecycle;
  private Optional<Duration> lastElapsed = Optional.empty();

  public TimedDbPoolMonitor(Service service) {
    lifecycle = new AlertLifecycle(Condition.DB_POOL, service);
  }

  /**
   * pending/timeouts must already be known current observations; unknown counts must not be
   * supplied as zero.
   */
  public Evaluation observe(
      OptionalDouble percent,
      long pending,
      long timeouts,
      boolean consecutive,
      ObservationContext context) {
    Objects.requireNonNull(percent, "supplied pool value");
    Objects.requireNonNull(context, "observation context");
    Severity immediate = thresholds.dbPool(percent.orElse(0), Duration.ZERO, pending, timeouts);
    Duration elapsed = context.elapsed();
    synchronized (lock) {
      if (lastElapsed.isPresent() && elapsed.compareTo(lastElapsed.orElseThrow()) < 0)
        throw new IllegalArgumentException("invalid monitoring sequence");
      lastElapsed = Optional.of(elapsed);
      if (!consecutive || percent.isEmpty()) lifecycle.interruptContinuity(elapsed);
      boolean aboveWarning =
          percent.isPresent() && AlertThresholds.dbPoolAboveWarning(percent.orElseThrow());
      var above80 =
          warning.observe(
              percent.isEmpty() ? State.UNKNOWN : aboveWarning ? State.VIOLATING : State.NORMAL,
              elapsed,
              consecutive);
      if (percent.isEmpty() && immediate != Severity.CRITICAL)
        return new Evaluation(false, lifecycle.snapshot());
      Severity level =
          immediate == Severity.CRITICAL
              ? Severity.CRITICAL
              : thresholds.dbPool(percent.orElseThrow(), above80.orElseThrow(), pending, timeouts);
      return new Evaluation(
          percent.isPresent(), lifecycle.observeWindowed(level, aboveWarning, context));
    }
  }

  public Optional<Event> snapshot() {
    synchronized (lock) {
      return lifecycle.snapshot();
    }
  }
}
