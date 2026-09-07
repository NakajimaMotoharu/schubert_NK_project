package dev.codex.schubert.nk.api.idempotency;

import java.sql.Connection;
import java.sql.SQLException;

/** Business handler executed on the same JDBC transaction as the Inbox state transition. */
@FunctionalInterface
public interface InboxHandler {
  InboxCompletion handle(Connection connection) throws SQLException;
}
