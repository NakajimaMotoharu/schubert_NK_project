package dev.codex.schubert.nk.batch.monitoring;

import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.Condition;
import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.Event;
import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.Service;
import dev.codex.schubert.nk.batch.monitoring.ContinuousConditionWindow.State;
import java.time.Duration;
import java.util.Objects;
import java.util.Optional;
import java.util.OptionalDouble;

/**
 * Supplied filesystem samples only, never an actual collector, source or control authority.
 * NK-OPS-001/P018-09; MON005..013; UI252; SS351 §7/10; PG-D524/TIMEDFS001..006.
 */
public final class TimedFilesystemMonitor {
  public record Evaluation(boolean suppliedValuePresent, Optional<Event> event) {
    public Evaluation {
      Objects.requireNonNull(event, "alert transition");
    }
  }

  private final Object lock = new Object();
  private final AlertThresholds thresholds = new AlertThresholds();
  private final ContinuousConditionWindow warning = new ContinuousConditionWindow();
  private final ContinuousConditionWindow critical = new ContinuousConditionWindow();
  private final AlertLifecycle lifecycle;
  private Optional<Duration> lastElapsed = Optional.empty();

  public TimedFilesystemMonitor(Service service) {
    lifecycle = new AlertLifecycle(Condition.FILESYSTEM, service);
  }

  /** Missing is explicit; a missing/gapped sequence must not close an existing alert. */
  public Evaluation observe(
      OptionalDouble percent, boolean consecutive, ObservationContext context) {
    Objects.requireNonNull(percent, "supplied filesystem value");
    Objects.requireNonNull(context, "observation context");
    if (percent.isPresent())
      thresholds.filesystem(percent.orElseThrow(), Duration.ZERO, Duration.ZERO);
    Duration elapsed = context.elapsed();
    synchronized (lock) {
      if (lastElapsed.isPresent() && elapsed.compareTo(lastElapsed.orElseThrow()) < 0)
        throw new IllegalArgumentException("invalid monitoring sequence");
      lastElapsed = Optional.of(elapsed);
      if (percent.isEmpty()) {
        warning.observe(State.UNKNOWN, elapsed, consecutive);
        critical.observe(State.UNKNOWN, elapsed, consecutive);
        lifecycle.interruptContinuity(elapsed);
        return new Evaluation(false, lifecycle.snapshot());
      }
      if (!consecutive) lifecycle.interruptContinuity(elapsed);
      double value = percent.orElseThrow();
      boolean aboveWarning = AlertThresholds.filesystemAboveWarning(value);
      Duration above80 =
          warning
              .observe(aboveWarning ? State.VIOLATING : State.NORMAL, elapsed, consecutive)
              .orElseThrow();
      Duration above90 =
          critical
              .observe(value >= 90 ? State.VIOLATING : State.NORMAL, elapsed, consecutive)
              .orElseThrow();
      return new Evaluation(
          true,
          lifecycle.observeWindowed(
              thresholds.filesystem(value, above80, above90), aboveWarning, context));
    }
  }

  public Optional<Event> snapshot() {
    synchronized (lock) {
      return lifecycle.snapshot();
    }
  }
}
