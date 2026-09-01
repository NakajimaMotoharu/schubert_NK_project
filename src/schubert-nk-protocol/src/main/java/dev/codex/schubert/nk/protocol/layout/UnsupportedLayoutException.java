package dev.codex.schubert.nk.protocol.layout;

/** Unknown layout ID/version. Trace: NK-PRO-001, SS 322 §11. */
public final class UnsupportedLayoutException extends IllegalArgumentException {
  private static final long serialVersionUID = 1L;

  public UnsupportedLayoutException(String message) {
    super(message);
  }
}
