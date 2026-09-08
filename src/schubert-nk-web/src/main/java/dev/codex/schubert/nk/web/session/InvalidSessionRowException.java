package dev.codex.schubert.nk.web.session;

/**
 * A stored row cannot form the closed session model; caller may invalidate by its lookup hash.
 * NK-WEB-001; FUN-001/AUT-001..004; UI226; SS314 §7.2.4/331/352; SSC-041/PG-D-098/PT-WEB-037/041.
 * Retains no data/provider/SQL diagnostics.
 */
public final class InvalidSessionRowException extends SessionStoreException {
  private static final long serialVersionUID = 1L;
}
