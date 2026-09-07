package dev.codex.schubert.nk.api.messaging.outbound;

import java.time.Duration;
import java.time.Instant;
import java.util.Objects;

/** SS 324 §8.3 / SS 332 §7.2 retry base and bounded jitter; PT-IDEM-010, BUG-012. */
public enum OutboxRetrySchedule {
  INSTANCE;

  public Duration delayAfterFailure(int attemptCount) {
    if (attemptCount < 1 || attemptCount > 100) {
      throw new IllegalArgumentException("attemptCount must be between 1 and 100");
    }
    return switch (attemptCount) {
      case 1 -> Duration.ofSeconds(1);
      case 2 -> Duration.ofSeconds(5);
      case 3 -> Duration.ofSeconds(30);
      case 4 -> Duration.ofMinutes(1);
      default -> Duration.ofMinutes(5);
    };
  }

  /**
   * Schedules a failed attempt from its observed failure time using an injected jitter in permille.
   *
   * <p>The base delay is capped at 300 seconds before applying ±100 permille (±10%). Initial
   * receipt sends use their enqueue time directly; only failed attempts call this retry policy.
   */
  public Instant nextAttemptAt(Instant failedAt, int attemptCount, int jitterPermille) {
    Objects.requireNonNull(failedAt, "failedAt");
    if (jitterPermille < -100 || jitterPermille > 100) {
      throw new IllegalArgumentException("retry jitter must be between -100 and 100 permille");
    }
    long baseMillis = delayAfterFailure(attemptCount).toMillis();
    return failedAt.plusMillis(baseMillis + baseMillis * jitterPermille / 1_000);
  }
}
