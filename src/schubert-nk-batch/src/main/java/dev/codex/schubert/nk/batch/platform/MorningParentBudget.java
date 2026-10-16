package dev.codex.schubert.nk.batch.platform;

import dev.codex.schubert.nk.storage.LinuxMonotonicClock;
import java.io.IOException;
import java.util.Objects;
import java.util.OptionalLong;
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
  private static final java.lang.String LITERAL_MORNING_PARENT_BUDGET_UNAVAILABLE =
      "Morning parent budget unavailable";

  private static final long LIMIT_NANOS = TimeUnit.MINUTES.toNanos(30);

  @FunctionalInterface
  private interface Clock {
    long read() throws IOException;
  }

  private final Clock monotonic;
  private final long began;
  private final OptionalLong borrowedDeadline;

  public static MorningParentBudget create() throws IOException {
    return new MorningParentBudget(LinuxMonotonicClock.create());
  }

  private MorningParentBudget(LinuxMonotonicClock clock) throws IOException {
    this(clock, OptionalLong.empty());
  }

  /** Same absolute Linux domain; the caller must independently authenticate the owner claim. */
  public static MorningParentBudget borrow(long deadline) throws IOException {
    if (deadline <= 0) throw new IOException(LITERAL_MORNING_PARENT_BUDGET_UNAVAILABLE);
    return new MorningParentBudget(LinuxMonotonicClock.create(), OptionalLong.of(deadline));
  }

  private MorningParentBudget(LinuxMonotonicClock clock, OptionalLong deadline) throws IOException {
    this.monotonic = clock::nowNanos;
    this.began = monotonic.read();
    this.borrowedDeadline = deadline;
    remainingNanos();
  }

  MorningParentBudget(LongSupplier monotonic) {
    Objects.requireNonNull(monotonic, "parent monotonic clock");
    this.monotonic = monotonic::getAsLong;
    this.began = monotonic.getAsLong();
    this.borrowedDeadline = OptionalLong.empty();
  }

  /** At or beyond 30 minutes (or on an impossible backward observation), refuse further work. */
  public void requireWithin() throws IOException {
    remainingNanos();
  }

  /** Blocking tools borrow the parent's remaining time instead of starting a new deadline. */
  public long remainingNanos() throws IOException {
    long now = monotonic.read();
    long elapsed = now - began;
    if (elapsed < 0 || elapsed >= LIMIT_NANOS)
      throw new IOException(LITERAL_MORNING_PARENT_BUDGET_UNAVAILABLE);
    if (borrowedDeadline.isPresent()) {
      long remaining = borrowedDeadline.getAsLong() - now;
      if (remaining <= 0 || remaining > LIMIT_NANOS)
        throw new IOException(LITERAL_MORNING_PARENT_BUDGET_UNAVAILABLE);
      return Math.min(LIMIT_NANOS - elapsed, remaining);
    }
    return LIMIT_NANOS - elapsed;
  }

  /** Same Linux clock domain for child claims; caller separately proves same boot and owner. */
  public long deadlineNanos() throws IOException {
    requireWithin();
    if (borrowedDeadline.isPresent()) return borrowedDeadline.getAsLong();
    try {
      return Math.addExact(began, LIMIT_NANOS);
    } catch (ArithmeticException overflow) {
      throw new IOException(LITERAL_MORNING_PARENT_BUDGET_UNAVAILABLE);
    }
  }
}
