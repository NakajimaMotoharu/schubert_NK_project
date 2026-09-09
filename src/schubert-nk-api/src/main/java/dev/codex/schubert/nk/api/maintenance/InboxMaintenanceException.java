package dev.codex.schubert.nk.api.maintenance;

/** Fixed failure, including uncertain commit; no provider cause or SQL values. SS341; PT037. */
public final class InboxMaintenanceException extends RuntimeException {
  private static final long serialVersionUID = 1L;

  InboxMaintenanceException() {
    super("Inbox maintenance did not complete; resume the same run");
  }
}
