package dev.codex.schubert.nk.batch.repository;

// PG-D-160/SSC056/BUG167/YKT128: SS332 JDBC4.2 UTC; existing Program/PT trace remains applicable.

import dev.codex.schubert.nk.storage.StorageIoException;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLDataException;
import java.sql.SQLException;
import java.util.Objects;
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;

/**
 * Borrowed single-owner parent connection; caller retains OS/DB exclusion through file mutation. No
 * lock acquisition, commit/rollback/close/config change, new connection or cached observation.
 * NK-BAT-001; DAT-009/OPS-009/UI251/SS311/331 3.12/332/343; SSC055/PG-D-159; PT-BAT-082..089.
 */
@NullMarked
public final class RunReferenceRepository {
  private final Connection connection;

  public RunReferenceRepository(Connection connection) {
    this.connection = Objects.requireNonNull(connection, "parent connection");
  }

  public RunReferences read(BatchRun run) {
    Objects.requireNonNull(run, "fixed run");
    try {
      require(!Thread.currentThread().isInterrupted());
      require(!connection.getAutoCommit());
      require(!connection.isReadOnly());
      require(connection.getTransactionIsolation() == Connection.TRANSACTION_READ_COMMITTED);
      RunReferences result;
      var statement =
          connection.prepareStatement(
              "select has_batch_history,has_inbox_progress,has_log_progress,identity_consistent"
                  + " from schubert.maintenance_read_run_references(?,?)");
      @Nullable Throwable statementFailure = null;
      try {
        var checked = present(statement);
        checked.setQueryTimeout(5);
        checked.setObject(1, run.id());
        checked.setObject(2, run.cutoff().atOffset(java.time.ZoneOffset.UTC));
        var row = checked.executeQuery();
        @Nullable Throwable rowFailure = null;
        try {
          var values = present(row);
          require(values.next());
          boolean history = present(values.getObject("has_batch_history", Boolean.class));
          boolean inbox = present(values.getObject("has_inbox_progress", Boolean.class));
          boolean log = present(values.getObject("has_log_progress", Boolean.class));
          boolean consistent = present(values.getObject("identity_consistent", Boolean.class));
          try {
            result = new RunReferences(history, inbox, log, consistent);
          } catch (IllegalArgumentException invalidProjection) {
            throw new SQLDataException("run reference projection invalid");
          }
          require(!values.next());
        } catch (SQLException | RuntimeException | Error failure) {
          rowFailure = failure;
          throw failure;
        } finally {
          closeRow(row, rowFailure);
        }
      } catch (SQLException | RuntimeException | Error failure) {
        statementFailure = failure;
        throw failure;
      } finally {
        closeStatement(statement, statementFailure);
      }
      require(!Thread.currentThread().isInterrupted());
      return result;
    } catch (SQLException failure) {
      StorageIoException.preserveFatal(failure);
      // All owned resources have closed. No raw/suppressed provider diagnostics escape.
      throw new BatchRepositoryException();
    }
  }

  // SSC448/BUG3126: one typed cleanup body, shared by normal and exceptional finally exits.
  private static void closeRow(@Nullable ResultSet row, @Nullable Throwable primary)
      throws SQLException {
    if (row != null)
      try {
        row.close();
      } catch (SQLException | RuntimeException | Error secondary) {
        if (JdbcResourceFailures.replace(primary, secondary)) throw secondary;
      }
  }

  private static void closeStatement(
      @Nullable PreparedStatement statement, @Nullable Throwable primary) throws SQLException {
    if (statement != null)
      try {
        statement.close();
      } catch (SQLException | RuntimeException | Error secondary) {
        if (JdbcResourceFailures.replace(primary, secondary)) throw secondary;
      }
  }

  private static void require(boolean condition) throws SQLDataException {
    if (!condition) throw new SQLDataException("run reference contract failed");
  }

  private static <T> T present(@Nullable T value) throws SQLDataException {
    if (value == null) throw new SQLDataException("run reference projection missing");
    return value;
  }
}
