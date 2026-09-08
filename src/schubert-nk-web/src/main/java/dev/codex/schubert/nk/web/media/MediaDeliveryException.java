package dev.codex.schubert.nk.web.media;

import java.io.IOException;
import java.util.Objects;
import java.util.OptionalInt;

/** Safe delivery failure; never send another response after commit. SS333; PT-MED-026..032. */
public final class MediaDeliveryException extends IOException {
  private static final long serialVersionUID = 1L;

  public enum Reason {
    INVALID_DESCRIPTOR,
    BUSY,
    UNAVAILABLE
  }

  private final Reason reason;

  public MediaDeliveryException(Reason reason) {
    super("media delivery failed");
    this.reason = Objects.requireNonNull(reason, "reason");
  }

  public Reason reason() {
    return reason;
  }

  public int httpStatus() {
    return 503;
  }

  public OptionalInt retryAfterSeconds() {
    return reason == Reason.BUSY ? OptionalInt.of(1) : OptionalInt.empty();
  }
}
