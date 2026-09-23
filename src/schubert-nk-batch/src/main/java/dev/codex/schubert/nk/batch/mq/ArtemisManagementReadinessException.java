package dev.codex.schubert.nk.batch.mq;

/** Redacted failure of the read-only broker-management startup gate. SS321 §13; PT-OPS-MQ-005. */
public final class ArtemisManagementReadinessException extends RuntimeException {
  private static final long serialVersionUID = 1L;

  public ArtemisManagementReadinessException() {
    super("Artemis effective broker configuration is unavailable");
  }
}
