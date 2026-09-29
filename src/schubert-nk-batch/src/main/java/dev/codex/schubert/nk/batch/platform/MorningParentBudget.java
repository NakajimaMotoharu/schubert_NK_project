package dev.codex.schubert.nk.batch.platform;

import java.io.IOException;
import java.util.Objects;
import java.util.concurrent.TimeUnit;
import java.util.function.LongSupplier;
import org.jspecify.annotations.NullMarked;

/**
 * One monotonic 30-minute budget for the entire Morning parent, created once at external entry and
 * borrowed by every subsequent phase. A child phase must not restart this clock. systemd's
 * Type=oneshot TimeoutStartSec is an independent outer deadline; neither clock proves that a
 * possibly started Unit has terminated. NK-OPS-001; OPS009/BAK001; UI251; SS341/342/343;
 * SSC107/BUG322; PG366/PT-OPS-MBUDGET001..002.
 */
@NullMarked
public final class MorningParentBudget {
  private static final long LIMIT_NANOS = TimeUnit.MINUTES.toNanos(30);

  private final LongSupplier monotonic;
  private final long began;

  public static MorningParentBudget create() {
    return new MorningParentBudget(System::nanoTime);
  }

  MorningParentBudget(LongSupplier monotonic) {
    this.monotonic = Objects.requireNonNull(monotonic, "parent monotonic clock");
    this.began = monotonic.getAsLong();
  }

  /** At or beyond 30 minutes (or on an impossible backward observation), refuse further work. */
  public void requireWithin() throws IOException {
    remainingNanos();
  }

  /** Blocking tools borrow the parent's remaining time instead of starting a new deadline. */
  public long remainingNanos() throws IOException {
    long elapsed = monotonic.getAsLong() - began;
    if (elapsed < 0 || elapsed >= LIMIT_NANOS)
      throw new IOException("Morning parent budget unavailable");
    return LIMIT_NANOS - elapsed;
  }
}
