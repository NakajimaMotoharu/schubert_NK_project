package dev.codex.schubert.nk.api.application.question;

/** Closed expected provider failure; never provider text. NK-ASY-001; SS312§9; AWORK005. */
public final class AnswerBusinessException extends RuntimeException {
  private static final long serialVersionUID = 1L;

  public AnswerBusinessException() {
    super("answer could not be produced");
  }
}
