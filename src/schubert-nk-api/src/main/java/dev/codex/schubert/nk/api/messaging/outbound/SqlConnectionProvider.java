package dev.codex.schubert.nk.api.messaging.outbound;

import java.sql.Connection;
import java.sql.SQLException;

/** Process-composition boundary that opens one caller-owned JDBC connection. */
@FunctionalInterface
public interface SqlConnectionProvider {
  Connection open() throws SQLException;
}
