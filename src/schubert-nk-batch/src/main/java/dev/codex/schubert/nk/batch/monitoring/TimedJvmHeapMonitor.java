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
 * Supplied heap observations/reports only, never catches real OOM or grants process control.
 * NK-OPS-001/P018-09; RD171/UI252/SS351; PG-D532/HEAPTIME001..008/spec1595.
 */
public final class TimedJvmHeapMonitor {
  public record Evaluation(boolean suppliedValuePresent, Optional<Event> event) {
    public Evaluation {
      Objects.requireNonNull(event, "heap alert transition");
    }
  }

  private final Object lock = new Object();
  private final AlertThresholds thresholds = new AlertThresholds();
  private final ContinuousConditionWindow warning = new ContinuousConditionWindow();
  private final AlertLifecycle lifecycle;
  private Optional<Duration> lastElapsed = Optional.empty();

  public TimedJvmHeapMonitor(Service service) {
    lifecycle = new AlertLifecycle(Condition.JVM_HEAP, service);
  }

  /** Actual OOM termination belongs to the outer owner, not a boolean report or this kernel. */
  public Evaluation observe(
      OptionalDouble percent,
      boolean outOfMemoryReported,
      boolean consecutive,
      ObservationContext context) {
    Objects.requireNonNull(percent, "supplied heap value");
    Objects.requireNonNull(context, "observation context");
    if (percent.isPresent())
      thresholds.jvmHeap(percent.orElseThrow(), Duration.ZERO, outOfMemoryReported);
    Duration elapsed = context.elapsed();
    synchronized (lock) {
      if (lastElapsed.isPresent() && elapsed.compareTo(lastElapsed.orElseThrow()) < 0)
        throw new IllegalArgumentException("invalid monitoring sequence");
      lastElapsed = Optional.of(elapsed);
      if (!consecutive || percent.isEmpty()) lifecycle.interruptContinuity(elapsed);
      boolean aboveWarning =
          percent.isPresent() && AlertThresholds.heapAboveWarning(percent.orElseThrow());
      var above75 =
          warning.observe(
              percent.isEmpty() ? State.UNKNOWN : aboveWarning ? State.VIOLATING : State.NORMAL,
              elapsed,
              consecutive);
      if (percent.isEmpty() && !outOfMemoryReported)
        return new Evaluation(false, lifecycle.snapshot());
      Severity level =
          outOfMemoryReported
              ? Severity.CRITICAL
              : thresholds.jvmHeap(percent.orElseThrow(), above75.orElseThrow(), false);
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
