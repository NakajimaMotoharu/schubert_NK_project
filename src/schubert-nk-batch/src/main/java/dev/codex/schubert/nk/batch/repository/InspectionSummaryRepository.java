package dev.codex.schubert.nk.batch.repository;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
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
          present(
              connection.prepareStatement(
                  "select inspected_count,deleted_count,protected_count,complete"
                      + " from schubert.maintenance_read_inbox_summary(?,?)"));
      @Nullable Throwable statementFailure = null;
      try {
        statement.setQueryTimeout(5);
        statement.setObject(1, run.id());
        statement.setObject(2, run.cutoff().atOffset(ZoneOffset.UTC));
        var row = present(statement.executeQuery());
        @Nullable Throwable rowFailure = null;
        try {
          if (row.next()) {
            long inspected = present(row.getObject("inspected_count", Long.class));
            long deleted = present(row.getObject("deleted_count", Long.class));
            long protectedCount = present(row.getObject("protected_count", Long.class));
            boolean complete = present(row.getObject("complete", Boolean.class));
            try {
              result =
                  Optional.of(
                      new InspectionSummary(
                          run, new CleanupCounts(inspected, deleted, protectedCount), complete));
            } catch (IllegalArgumentException invalidProjection) {
              throw new SQLDataException("inspection summary projection invalid");
            }
            require(!row.next());
          } else {
            result = Optional.empty();
          }
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
      // Owned resources have closed; no provider diagnostics/cause/suppressed escape.
      throw new BatchRepositoryException();
    }
  }

  // PG-D-1173: one policy Code point, reached from both normal and exceptional cleanup.
  private static void closeRow(ResultSet row, @Nullable Throwable primary) throws SQLException {
    try {
      row.close();
    } catch (SQLException | RuntimeException | Error secondary) {
      if (JdbcResourceFailures.replace(primary, secondary)) throw secondary;
    }
  }

  private static void closeStatement(PreparedStatement statement, @Nullable Throwable primary)
      throws SQLException {
    try {
      statement.close();
    } catch (SQLException | RuntimeException | Error secondary) {
      if (JdbcResourceFailures.replace(primary, secondary)) throw secondary;
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
