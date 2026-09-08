package dev.codex.schubert.nk.web.session;

/**
 * Fixed DB failure, without SQL/parameters/cause/suppressed resource diagnostics. NK-WEB-001;
 * FUN-001/AUT-001..004; UI226/242; SS314/331/352; SSC-040/PG-D-096/PT-WEB-024..031. Caller must
 * roll back the borrowed transaction.
 */
public sealed class SessionStoreException extends RuntimeException
    permits InvalidSessionRowException {
  private static final long serialVersionUID = 1L;

  public SessionStoreException() {
    super("session storage is unavailable");
  }
}
