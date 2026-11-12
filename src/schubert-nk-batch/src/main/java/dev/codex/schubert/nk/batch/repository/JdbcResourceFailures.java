package dev.codex.schubert.nk.batch.repository;

import dev.codex.schubert.nk.storage.StorageIoException;
import java.sql.SQLException;
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;

/**
 * Failure precedence only; callers close JDBC resources directly. NK-BAT-001/DAT009/OPS009/UI251;
 * SS332/SSC063/PG179/BUG195,206/YKT154,162; BAT087,121. Never owns a connection or transaction.
 */
@NullMarked
final class JdbcResourceFailures {
  private JdbcResourceFailures() {}

  static boolean replace(@Nullable Throwable primary, Throwable secondary) {
    if (primary == null
        || (primary instanceof SQLException && !(secondary instanceof SQLException))) return true;
    if (!(primary instanceof SQLException)) primary.addSuppressed(new BatchRepositoryException());
    else {
      StorageIoException.preserveFatal(primary);
      StorageIoException.preserveFatal(secondary);
    }
    return false;
  }
}
