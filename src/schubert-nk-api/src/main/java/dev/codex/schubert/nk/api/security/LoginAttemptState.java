package dev.codex.schubert.nk.api.security;

import java.time.Duration;
import java.time.Instant;
import java.util.Objects;
import java.util.Optional;

/**
 * Immutable persisted login-window state; no clock reads or caller identity in this policy. Trace:
 * NK-AUT-001, AUT-001; UI226 §4; SS314 §5/332 §5.1; PT-AUT-003.
 */
public record LoginAttemptState(
    LoginAttemptKind kind,
    int failedCount,
    Optional<Instant> windowStartedAt,
    Optional<Instant> lockedUntil) {
  private static final Duration WINDOW = Duration.ofMinutes(15);

  public LoginAttemptState {
    Objects.requireNonNull(kind, "kind");
    Objects.requireNonNull(windowStartedAt, "windowStartedAt");
    Objects.requireNonNull(lockedUntil, "lockedUntil");
    if (failedCount < 0 || failedCount > kind.threshold()) {
      throw new IllegalArgumentException("login failure count is outside its threshold");
    }
    if (failedCount > 0 && windowStartedAt.isEmpty()) {
      throw new IllegalArgumentException("login failure window is missing");
    }
    if (lockedUntil.isPresent()) {
      if (failedCount != kind.threshold()) {
        throw new IllegalArgumentException("login lock requires the threshold count");
      }
      if (lockedUntil.orElseThrow().isBefore(windowStartedAt.orElseThrow())) {
        throw new IllegalArgumentException("login lock precedes its failure window");
      }
    }
  }

  public static LoginAttemptState empty(LoginAttemptKind kind) {
    return new LoginAttemptState(kind, 0, Optional.empty(), Optional.empty());
  }

  /** Lock is strict: its exact expiry instant permits another attempt. */
  public boolean isLocked(Instant now) {
    Objects.requireNonNull(now, "now");
    return lockedUntil.isPresent() && lockedUntil.orElseThrow().isAfter(now);
  }

  /** Ceil seconds, capped at SS314's 900; never truncates a still-active fractional second to 0. */
  public int retryAfterSeconds(Instant now) {
    if (!isLocked(now)) {
      return 0;
    }
    Duration remaining = Duration.between(now, lockedUntil.orElseThrow());
    long seconds = remaining.getSeconds() + (remaining.getNano() == 0 ? 0 : 1);
    return (int) Math.min(900, seconds);
  }

  /**
   * A locked request does not extend the lock or increment counters. A 15-minute window is
   * inclusive at its end for Current compatibility (SSC-009/BUG-021); lock expiry remains strict.
   */
  public LoginAttemptState afterFailure(Instant now) {
    if (isLocked(now)) {
      return this;
    }
    if (windowStartedAt.isPresent() && now.isBefore(windowStartedAt.orElseThrow())) {
      throw new IllegalArgumentException("login observation precedes its persisted failure window");
    }
    boolean sameWindow =
        windowStartedAt.isPresent() && !now.isAfter(windowStartedAt.orElseThrow().plus(WINDOW));
    int nextCount = sameWindow ? Math.min(kind.threshold(), failedCount + 1) : 1;
    Instant nextWindow = sameWindow ? windowStartedAt.orElseThrow() : now;
    Optional<Instant> nextLock =
        nextCount == kind.threshold() ? Optional.of(now.plus(WINDOW)) : Optional.empty();
    return new LoginAttemptState(kind, nextCount, Optional.of(nextWindow), nextLock);
  }

  /**
   * Success clears counters, window and lock; repositories map IP's NOT NULL window to current
   * time.
   */
  public LoginAttemptState afterSuccess() {
    return empty(kind);
  }
}
