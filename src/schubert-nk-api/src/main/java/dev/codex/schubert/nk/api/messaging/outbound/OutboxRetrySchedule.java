package dev.codex.schubert.nk.api.messaging.outbound;

import java.time.Duration;
import java.time.Instant;
import java.util.Objects;

/** SS 324 §8.3 application-level outbox retry schedule. */
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

  public Instant nextAttemptAt(Instant failedAt, int attemptCount) {
    Objects.requireNonNull(failedAt, "failedAt");
    return failedAt.plus(delayAfterFailure(attemptCount));
  }
}
