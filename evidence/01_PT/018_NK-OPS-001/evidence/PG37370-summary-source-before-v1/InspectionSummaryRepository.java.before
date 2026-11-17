package dev.codex.schubert.nk.batch.repository;

import java.sql.Connection;
import java.sql.SQLDataException;
import java.sql.SQLException;
import java.time.ZoneOffset;
import java.util.Objects;
import java.util.Optional;
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;

/**
 * Borrowed single-owner parent connection. No acquisition/commit/rollback/close/config mutation.
 * NK-BAT-001; OPS009/DAT009/UI251/SS311/331 3.13/332/341 7.3; SSC049/PG162; BAT114..121. UTC binds
 * preserve PG-D-160/SSC056/BUG167/YKT128; SQL checks only the present DB lock.
 */
@NullMarked
public final class InspectionSummaryRepository {
  private final Connection connection;

  public InspectionSummaryRepository(Connection connection) {
    this.connection = Objects.requireNonNull(connection, "parent connection");
  }

  public Optional<InspectionSummary> read(BatchRun run) {
    Objects.requireNonNull(run, "fixed run");
    try {
      require(!Thread.currentThread().isInterrupted());
      require(connection.getAutoCommit());
      require(!connection.isReadOnly());
      require(connection.getTransactionIsolation() == Connection.TRANSACTION_READ_COMMITTED);
      Optional<InspectionSummary> result;
      var statement =
          connection.prepareStatement(
              "select inspected_count,deleted_count,protected_count,complete"
                  + " from schubert.maintenance_read_inbox_summary(?,?)");
      @Nullable Throwable statementFailure = null;
      try {
        var checked = present(statement);
        checked.setQueryTimeout(5);
        checked.setObject(1, run.id());
        checked.setObject(2, run.cutoff().atOffset(ZoneOffset.UTC));
        var row = checked.executeQuery();
        @Nullable Throwable rowFailure = null;
        try {
          var values = present(row);
          if (values.next()) {
            long inspected = present(values.getObject("inspected_count", Long.class));
            long deleted = present(values.getObject("deleted_count", Long.class));
            long protectedCount = present(values.getObject("protected_count", Long.class));
            boolean complete = present(values.getObject("complete", Boolean.class));
            try {
              result =
                  Optional.of(
                      new InspectionSummary(
                          run, new CleanupCounts(inspected, deleted, protectedCount), complete));
            } catch (IllegalArgumentException invalidProjection) {
              throw new SQLDataException("inspection summary projection invalid");
            }
            require(!values.next());
          } else {
            result = Optional.empty();
          }
        } catch (SQLException | RuntimeException | Error failure) {
          rowFailure = failure;
          throw failure;
        } finally {
          if (row != null)
            try {
              row.close();
            } catch (SQLException | RuntimeException | Error secondary) {
              if (JdbcResourceFailures.replace(rowFailure, secondary)) throw secondary;
            }
        }
      } catch (SQLException | RuntimeException | Error failure) {
        statementFailure = failure;
        throw failure;
      } finally {
        if (statement != null)
          try {
            statement.close();
          } catch (SQLException | RuntimeException | Error secondary) {
            if (JdbcResourceFailures.replace(statementFailure, secondary)) throw secondary;
          }
      }
      require(!Thread.currentThread().isInterrupted());
      return result;
    } catch (SQLException failure) {
      // Owned resources have closed; no provider diagnostics/cause/suppressed escape.
      throw new BatchRepositoryException();
    }
  }

  private static void require(boolean condition) throws SQLDataException {
    if (!condition) throw new SQLDataException("inspection summary contract failed");
  }

  private static <T> T present(@Nullable T value) throws SQLDataException {
    if (value == null) throw new SQLDataException("inspection summary projection missing");
    return value;
  }
}
