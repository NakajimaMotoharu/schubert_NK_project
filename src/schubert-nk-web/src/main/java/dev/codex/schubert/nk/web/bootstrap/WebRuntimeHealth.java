package dev.codex.schubert.nk.web.bootstrap;

import java.util.function.BooleanSupplier;
import java.util.function.Predicate;
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;

/**
 * NK-WEB-002/NK-OPS-001; MON003; SS313342352; PG-D377; PT-OPS-NWEB-HEALTH001..004. Pure decision on
 * an owner's captured resources, not acquisition or a readiness override.
 */
@NullMarked
final class WebRuntimeHealth {
  private WebRuntimeHealth() {}

  /** PG-D378/WEB-REM001: exact existing captured-management conjunction. */
  static <T> boolean ready(@Nullable T management, Predicate<T> probe) {
    return management != null && probe.test(management);
  }

  static <R, L, V> boolean healthy(
      BooleanSupplier ownerStopping,
      BooleanSupplier stopping,
      BooleanSupplier terminal,
      @Nullable R replies,
      @Nullable L replay,
      @Nullable V retry,
      @Nullable Object http,
      Predicate<R> replyReady,
      Predicate<L> logRunning,
      Predicate<V> revokeRunning) {
    return !ownerStopping.getAsBoolean()
        && !stopping.getAsBoolean()
        && !terminal.getAsBoolean()
        && replies != null
        && replay != null
        && retry != null
        && http != null
        && replyReady.test(replies)
        && logRunning.test(replay)
        && revokeRunning.test(retry);
  }
}
