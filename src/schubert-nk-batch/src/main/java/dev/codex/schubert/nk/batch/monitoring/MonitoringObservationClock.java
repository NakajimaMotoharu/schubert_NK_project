package dev.codex.schubert.nk.batch.monitoring;

import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.CauseClearance;
import java.time.Clock;
import java.time.Duration;
import java.util.Objects;
import java.util.concurrent.locks.ReentrantLock;
import java.util.function.LongSupplier;

/**
 * Borrowed UTC and monotonic tick ports, not actual clock/owner or consecutive-sample proof.
 * NK-OPS-001/P018-09; RD171/UI252/SS351; PG-D530/OBSCLOCK001..008/spec1586.
 */
public final class MonitoringObservationClock {
  private final ReentrantLock lock = new ReentrantLock();
  private final Clock utc;
  private final LongSupplier ticks;
  private final long origin;
  private long last;

  /** Signed nanoTime origins are valid; one owner epoch must be shorter than 2^63 nanoseconds. */
  public MonitoringObservationClock(Clock utc, LongSupplier ticks) {
    this.utc = Objects.requireNonNull(utc, "observation UTC source");
    this.ticks = Objects.requireNonNull(ticks, "observation tick source");
    origin = ticks.getAsLong();
    last = origin;
  }

  /** Clock rollback is not fabricated away; only elapsed monotonic time controls alert periods. */
  public ObservationContext context(CauseClearance clearance) {
    Objects.requireNonNull(clearance, "cause clearance");
    lock.lock();
    try {
      long now = ticks.getAsLong();
      long elapsed = now - origin;
      if (now - last < 0 || elapsed < 0)
        throw new IllegalArgumentException("invalid monitoring clock sequence");
      var at = Objects.requireNonNull(utc.instant(), "observation instant");
      var context = new ObservationContext(clearance, at, Duration.ofNanos(elapsed));
      last = now;
      return context;
    } finally {
      lock.unlock();
    }
  }
}
