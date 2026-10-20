package dev.codex.schubert.nk.protocol.transport;

import java.util.Objects;

/**
 * A receiver must stop rather than reuse a transaction whose rollback did not return normally. The
 * original failure and rollback failure retain their identities; neither provider text nor a
 * throwable-graph search is needed to classify this internal outcome.
 *
 * <p>NK-MSG-001; RD MQ008/010; UI231; SS321 section 7/352; PG-D441; PT-JMS-UNC005..008.
 */
public final class UnconfirmedJmsRollbackException extends IllegalStateException {
  public UnconfirmedJmsRollbackException(Throwable primary, Throwable rollbackFailure) {
    super("JMS receiver rollback unconfirmed", Objects.requireNonNull(primary, "primary failure"));
    Objects.requireNonNull(rollbackFailure, "rollback failure");
    if (rollbackFailure != primary) {
      addSuppressed(rollbackFailure);
    }
  }
}
