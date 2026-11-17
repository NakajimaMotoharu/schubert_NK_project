package dev.codex.schubert.nk.batch.monitoring;

import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.CauseClearance;
import java.time.Duration;
import java.util.Objects;
import java.util.Optional;
import java.util.concurrent.locks.ReentrantLock;
import java.util.function.BiFunction;

/** Internal one-owner sequence/gap guard, not a scheduler or timeout/control authority. PG-D533. */
final class MonitoringPoller<R> {
  private final ReentrantLock lock = new ReentrantLock();
  private Optional<Duration> lastCompleted = Optional.empty();
  private boolean interrupted;

  R observe(
      boolean consecutive,
      ObservationContext context,
      BiFunction<Boolean, ObservationContext, R> action) {
    Objects.requireNonNull(context, "observation context");
    Objects.requireNonNull(action, "observation action");
    lock.lock();
    try {
      return observeLocked(consecutive, context, action);
    } finally {
      lock.unlock();
    }
  }

  R observeNow(
      boolean consecutive,
      CauseClearance clearance,
      MonitoringObservationClock clock,
      BiFunction<Boolean, ObservationContext, R> action) {
    Objects.requireNonNull(clearance, "cause clearance");
    Objects.requireNonNull(clock, "observation clock");
    Objects.requireNonNull(action, "observation action");
    lock.lock();
    try {
      final ObservationContext context;
      try {
        context = clock.context(clearance);
      } catch (RuntimeException | Error unavailableClock) {
        interrupted = true;
        throw unavailableClock;
      }
      return observeLocked(consecutive, context, action);
    } finally {
      lock.unlock();
    }
  }

  private R observeLocked(
      boolean consecutive,
      ObservationContext context,
      BiFunction<Boolean, ObservationContext, R> action) {
    if (lastCompleted.isPresent() && context.elapsed().compareTo(lastCompleted.orElseThrow()) < 0)
      throw new IllegalArgumentException("invalid monitoring sequence");
    try {
      R result =
          Objects.requireNonNull(
              action.apply(consecutive && !interrupted, context), "observation result");
      lastCompleted = Optional.of(context.elapsed());
      interrupted = false;
      return result;
    } catch (RuntimeException | Error unavailableObservation) {
      interrupted = true;
      throw unavailableObservation;
    }
  }
}
