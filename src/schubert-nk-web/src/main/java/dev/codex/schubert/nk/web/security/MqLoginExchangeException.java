package dev.codex.schubert.nk.web.security;

import java.util.Objects;

/**
 * Fixed Login boundary failure, never a bad-password response or provider diagnostic. NK-WEB-001;
 * FUN-001/AUT-001..004/MQ-004; UI226/234; SS314/352; PG-D-101/PT-WEB-054..059.
 */
public final class MqLoginExchangeException extends RuntimeException {
  private static final long serialVersionUID = 1L;

  public enum Reason {
    INVALID_INPUT,
    UNAVAILABLE
  }

  private final Reason failureReason;

  public MqLoginExchangeException(Reason reason) {
    super("login exchange rejected", null, false, true);
    this.failureReason = Objects.requireNonNull(reason, "reason");
  }

  public Reason reason() {
    return failureReason;
  }
}
