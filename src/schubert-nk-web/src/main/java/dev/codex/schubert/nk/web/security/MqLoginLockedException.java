package dev.codex.schubert.nk.web.security;

import org.springframework.security.authentication.LockedException;

/**
 * Fixed lock outcome with only the approved bounded retry delay; no wire message/cause/context.
 * NK-WEB-001; FUN-001/AUT-001; UI226/234; SS314 §3.1; SSC-043/PG-D-102/PT-WEB-063/066.
 */
public final class MqLoginLockedException extends LockedException {
  private static final long serialVersionUID = 1L;
  private final int retryAfterSeconds;

  public MqLoginLockedException(int retryAfterSeconds) {
    super("login temporarily locked");
    if (retryAfterSeconds < 0 || retryAfterSeconds > 900)
      throw new IllegalArgumentException("login lock delay is outside 0..900");
    this.retryAfterSeconds = retryAfterSeconds;
  }

  public int retryAfterSeconds() {
    return retryAfterSeconds;
  }
}
