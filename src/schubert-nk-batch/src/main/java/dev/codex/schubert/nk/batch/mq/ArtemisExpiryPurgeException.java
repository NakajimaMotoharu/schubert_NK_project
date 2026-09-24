package dev.codex.schubert.nk.batch.mq;

/** No provider detail or selector value crosses the maintenance failure boundary. SS321/341. */
public final class ArtemisExpiryPurgeException extends RuntimeException {
  private static final long serialVersionUID = 1L;

  public ArtemisExpiryPurgeException() {
    super("Artemis Expiry cleanup did not complete");
  }
}
