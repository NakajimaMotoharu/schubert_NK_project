package dev.codex.schubert.nk.api.database;

import java.sql.SQLException;
import java.util.Objects;
import org.jspecify.annotations.Nullable;

/**
 * Stateless owned JDBC cleanup, never a connection/transaction owner. NK-DAT-001/NK-AUT-001;
 * DAT-009/AUT-004; UI226/241; SS311/332/352/SSC424; PT-JDBC-CLEANUP001..005.
 */
public interface JdbcResourceCleanup {
  /** Close an already established, nonnull owned statement or result set. */
  @FunctionalInterface
  interface SqlClose {
    void run() throws SQLException;
  }

  /**
   * Close once with exactly Java TWR failure semantics. Null primary means a successful body.
   * Secondary failures are suppressed on the original primary; self-suppression retains the JDK
   * IllegalArgumentException and its cause. Null action violates the call contract.
   */
  static void close(@Nullable Throwable primary, SqlClose action) throws SQLException {
    Objects.requireNonNull(action, "action");
    try {
      action.run();
    } catch (SQLException | RuntimeException | Error failure) {
      if (primary == null) throw failure;
      primary.addSuppressed(failure);
    }
  }
}
