package dev.codex.schubert.nk.api.bootstrap;

import java.util.Objects;
import java.util.concurrent.TimeUnit;
import java.util.function.LongSupplier;

/**
 * NK-OPS-001/RD171/UI252/SS342351/1870/PG-D637: API-local first-stop notification budget. This
 * primitive clock owner creates no resource, worker, timeout override or permission. Caller
 * integration must begin it at the first stop notification and preserve parent/Unit deadlines. It
 * is not a measurement of systemd's earlier TERM delivery time or whole cleanup completion.
 */
final class ApiStopBudget {
  private static final long LIMIT_NANOS = TimeUnit.SECONDS.toNanos(60);
  private final Object lock = new Object();
  private final LongSupplier nanos;
  private boolean begun;
  private boolean expired;
  private long began;

  ApiStopBudget(LongSupplier nanos) {
    this.nanos = Objects.requireNonNull(nanos, "API stop monotonic clock");
  }

  /** One claim before reading time; a failed first clock cannot permit a later fresh deadline. */
  void begin() {
    synchronized (lock) {
      if (begun) return;
      begun = true;
      began = time();
    }
  }

  /** Pre-notification use is refused; expiry, reverse time and clock failure never revive. */
  long remainingNanos() {
    synchronized (lock) {
      if (!begun) throw new IllegalStateException("API stop budget not begun");
      if (expired) return 0;
      long elapsed = time() - began;
      if (elapsed < 0 || elapsed >= LIMIT_NANOS) {
        expired = true;
        return 0;
      }
      return LIMIT_NANOS - elapsed;
    }
  }

  private long time() {
    boolean returned = false;
    try {
      long value = nanos.getAsLong();
      returned = true;
      return value;
    } finally {
      // Preserve the original clock failure, including programming-contract NPE, never catch it
      // as a normal observation. A later caller sees only exhausted permission to wait.
      if (!returned) expired = true;
    }
  }
}
