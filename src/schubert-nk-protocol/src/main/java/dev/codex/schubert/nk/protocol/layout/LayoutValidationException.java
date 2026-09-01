package dev.codex.schubert.nk.protocol.layout;

/** Invalid immutable protocol metadata. Trace: NK-PRO-001, SS 322 §2/§12. */
public final class LayoutValidationException extends IllegalArgumentException {
  private static final long serialVersionUID = 1L;

  public LayoutValidationException(String message) {
    super(message);
  }

  public LayoutValidationException(String message, ArithmeticException cause) {
    super(message, cause);
  }
}
