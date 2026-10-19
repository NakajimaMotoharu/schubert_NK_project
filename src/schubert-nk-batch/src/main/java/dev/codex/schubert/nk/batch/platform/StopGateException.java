package dev.codex.schubert.nk.batch.platform;

import java.util.Objects;
import org.jspecify.annotations.NullMarked;

/** Fixed diagnostic, never embeds command output. NK-OPS-001; SS341/343; PT-OPS-STOP-002..016. */
@NullMarked
public final class StopGateException extends RuntimeException {
  private static final long serialVersionUID = 1L;
  private final StopGateFailure failureReason;

  StopGateException(StopGateFailure reason) {
    super("application stop check failed");
    this.failureReason = Objects.requireNonNull(reason, "reason");
  }

  public StopGateFailure reason() {
    return failureReason;
  }
}
