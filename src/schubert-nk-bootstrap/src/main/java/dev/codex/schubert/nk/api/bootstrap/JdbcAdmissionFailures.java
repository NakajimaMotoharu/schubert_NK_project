package dev.codex.schubert.nk.api.bootstrap;

import java.sql.SQLException;
import java.sql.SQLNonTransientConnectionException;
import java.util.Objects;
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;

/**
 * Fixed JDBC admission scopes only. SSC095/PG312/DBADMIT003/SCHEMA006. No provider text/self
 * suppression.
 */
@NullMarked
final class JdbcAdmissionFailures {
  private JdbcAdmissionFailures() {
    throw new AssertionError("static namespace");
  }

  static boolean replace(@Nullable Throwable primary, Throwable secondary) {
    beforeDiscard(primary, secondary);
    if (primary == null
        || (primary instanceof SQLException && !(secondary instanceof SQLException))) return true;
    if (!(primary instanceof SQLException))
      primary.addSuppressed(
          new SQLNonTransientConnectionException("database admission resource failure", "08001"));
    return false;
  }

  /** Classify only known SQL failures before discarding them; unknown primary identity stays. */
  static void beforeDiscard(@Nullable Throwable primary, Throwable secondary) {
    Objects.requireNonNull(secondary, "secondary failure");
    if (primary instanceof SQLException) JdbcFailureGraph.preserveFatal(primary);
    if ((primary == null || primary instanceof SQLException) && secondary instanceof SQLException)
      JdbcFailureGraph.preserveFatal(secondary);
  }
}
