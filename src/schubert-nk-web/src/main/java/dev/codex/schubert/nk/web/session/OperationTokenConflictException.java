package dev.codex.schubert.nk.web.session;

/** QA049/SS314/TOKV207: explicit re-GET, never automatic UUID replacement or API submission. */
public final class OperationTokenConflictException extends IllegalStateException {
  private static final long serialVersionUID = 1L;

  public OperationTokenConflictException() {
    super("operation form is unavailable; get a new form explicitly");
  }

  public int httpStatus() {
    return 409;
  }
}
