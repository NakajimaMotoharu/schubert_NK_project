package dev.codex.schubert.nk.web.revocation;

/** Fixed infrastructure diagnostic with no raw/provider cause. NK-WEB-002/QA050/RERUN005. */
public final class RevocationRetryException extends RuntimeException {
  private static final long serialVersionUID = 1L;

  RevocationRetryException() {
    super("retained revocation retry infrastructure unavailable");
  }
}
