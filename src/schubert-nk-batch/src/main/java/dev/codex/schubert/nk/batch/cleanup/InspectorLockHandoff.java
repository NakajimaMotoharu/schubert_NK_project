package dev.codex.schubert.nk.batch.cleanup;

import java.io.IOException;
import java.sql.Connection;
import java.sql.SQLDataException;
import java.sql.SQLException;
import java.util.Objects;
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;

/**
 * Borrowed, single-owner parent connection. Caller continuously holds OS maintenance lock and
 * admits backup/run/stopped applications. Operation must synchronously confirm child termination,
 * never access the parent connection, and return no secrets. Dispose the connection on any failure.
 * NK-BAT-001; OPS-009; UI251; SS311/341§7.3; SSC-049/PG-D-150; PT-BAT-030..037.
 */
@NullMarked
public final class InspectorLockHandoff {
  private static final String HELD =
      "select exists(select 1 from pg_catalog.pg_locks where locktype='advisory'"
          + " and pid=pg_catalog.pg_backend_pid()"
          + " and database=(select oid from pg_catalog.pg_database where datname=pg_catalog.current_database())"
          + " and classid=0 and objid=71419602 and objsubid=1 and mode='ExclusiveLock' and granted) as value";

  private InspectorLockHandoff() {}

  @FunctionalInterface
  public interface Operation<T> {
    T execute() throws IOException;
  }

  public static <T> T execute(Connection parent, Operation<T> operation) {
    Objects.requireNonNull(parent, "parent connection");
    Objects.requireNonNull(operation, "synchronous operation");
    require(!Thread.currentThread().isInterrupted());
    try {
      ready(parent);
      require(scalar(parent, HELD));
      require(scalar(parent, "select pg_catalog.pg_advisory_unlock(71419602) as value"));
      require(!scalar(parent, HELD)); // Reentrant residual ownership must never start the child.
      T result;
      Throwable unknownCallback = null;
      try {
        result = Objects.requireNonNull(operation.execute(), "operation result");
      } catch (IOException failure) {
        throw new Failure();
      } catch (RuntimeException | Error failure) {
        unknownCallback = failure;
        throw failure;
      } finally {
        try {
          ready(parent);
          require(scalar(parent, "select pg_catalog.pg_try_advisory_lock(71419602) as value"));
          require(scalar(parent, HELD));
        } catch (SQLException | Failure failure) {
          // A fixed secondary must not replace an unknown callback or expose provider details.
          if (unknownCallback == null) throw new Failure();
          unknownCallback.addSuppressed(new Failure());
        }
      }
      require(!Thread.currentThread().isInterrupted());
      return result;
    } catch (SQLException failure) {
      // All JDBC resources have closed; no raw or suppressed provider diagnostics escape.
      throw new Failure();
    }
  }

  private static void ready(Connection parent) throws SQLException {
    require(parent.getAutoCommit() && !parent.isReadOnly());
  }

  private static boolean scalar(Connection parent, String sql) throws SQLException {
    try (var statement = parent.prepareStatement(sql)) {
      var checkedStatement = present(statement);
      checkedStatement.setQueryTimeout(5);
      try (var row = checkedStatement.executeQuery()) {
        var checkedRow = present(row);
        if (!checkedRow.next()) throw new SQLDataException("handoff result is missing");
        Boolean value = present(checkedRow.getObject("value", Boolean.class));
        if (checkedRow.next()) throw new SQLDataException("handoff result is ambiguous");
        return value;
      }
    }
  }

  private static <T> T present(@Nullable T value) throws SQLDataException {
    if (value == null) throw new SQLDataException("handoff result is missing");
    return value;
  }

  private static void require(boolean accepted) {
    if (!accepted) throw new Failure();
  }

  /** Fixed incomplete outcome; not the child's receipt, phase success or a recoverable lease. */
  public static final class Failure extends RuntimeException {
    private static final long serialVersionUID = 1L;

    private Failure() {
      super("maintenance lock handoff failed");
    }
  }
}
