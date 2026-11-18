package dev.codex.schubert.nk.api.bootstrap;

import dev.codex.schubert.nk.storage.StorageIoException;
import java.sql.SQLException;
import org.jspecify.annotations.NullMarked;

/** JDBC exception edge ownership for SS311/332, SSC-461, PG38600. */
@NullMarked
public interface JdbcFailureGraph {
  /** Preserve the first reachable original Error before a SQL diagnostic is discarded. */
  static void preserveFatal(Throwable failure) {
    StorageIoException.preserveFatal(
        failure,
        candidate -> candidate instanceof SQLException sql ? sql.getNextException() : null);
  }
}
