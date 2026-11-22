package dev.codex.schubert.nk.batch.monitoring;

import java.time.Duration;
import java.util.Objects;
import java.util.Optional;
import org.jspecify.annotations.Nullable;

/**
 * Caller-declared sample continuity only, never actual observation or clock authority.
 * NK-OPS-001/P018-09; MON005..013; UI252; SS351 §7/10; PG-D523/1197/MONWINDOW001..008.
 */
public final class ContinuousConditionWindow {
  public enum State {
    VIOLATING,
    NORMAL,
    UNKNOWN
  }

  private final Object lock = new Object();
  private @Nullable Duration previous;
  private Optional<Duration> violationStart = Optional.empty();

  /** UNKNOWN is absent, NORMAL is zero; neither may preserve a preceding violation period. */
  public Optional<Duration> observe(State state, Duration elapsed, boolean consecutive) {
    Objects.requireNonNull(state, "observation state");
    Objects.requireNonNull(elapsed, "observation elapsed");
    synchronized (lock) {
      if (elapsed.isNegative() || (previous != null && elapsed.compareTo(previous) < 0))
        throw new IllegalArgumentException("invalid observation sequence");
      previous = elapsed;
      if (state != State.VIOLATING) {
        violationStart = Optional.empty();
        return state == State.NORMAL ? Optional.of(Duration.ZERO) : Optional.empty();
      }
      if (!consecutive || violationStart.isEmpty()) {
        violationStart = Optional.of(elapsed);
        return Optional.of(Duration.ZERO);
      }
      return Optional.of(elapsed.minus(violationStart.orElseThrow()));
    }
  }
}
