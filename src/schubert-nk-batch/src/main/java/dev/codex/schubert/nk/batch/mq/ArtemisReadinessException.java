package dev.codex.schubert.nk.batch.mq;

/** Redacted topology failure; provider diagnostics and management credentials never escape. */
public final class ArtemisReadinessException extends IllegalStateException {
  private static final long serialVersionUID = 1L;

  public ArtemisReadinessException() {
    super("Artemis effective Queue topology is unavailable");
  }
}
