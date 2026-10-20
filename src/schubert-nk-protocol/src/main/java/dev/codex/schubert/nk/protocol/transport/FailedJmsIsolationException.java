package dev.codex.schubert.nk.protocol.transport;

import dev.codex.schubert.nk.protocol.codec.PermanentProtocolException;
import java.util.Objects;

/**
 * Permanent wire isolation failed: do not ACK, retry business, or report committed isolation. The
 * caller must stop its receiver even when rollback returned normally. No provider text or throwable
 * graph search determines this phase; the isolation/rollback outcome and protocol remain available.
 *
 * <p>NK-MSG-001; RD MQ008/010; UI231; SS321§7/322§11/352; PG-D442; PT-JMS-ISO001..012.
 */
public final class FailedJmsIsolationException extends IllegalStateException {
  private static final long serialVersionUID = 1L;

  public FailedJmsIsolationException(
      Throwable primary, PermanentProtocolException protocolFailure) {
    super(
        "JMS permanent message isolation failed",
        Objects.requireNonNull(primary, "primary failure"));
    Objects.requireNonNull(protocolFailure, "protocol failure");
    if (protocolFailure != primary) {
      addSuppressed(protocolFailure);
    }
  }
}
